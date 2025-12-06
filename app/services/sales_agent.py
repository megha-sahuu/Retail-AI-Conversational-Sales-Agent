from typing import Dict, Any, List

from loguru import logger

from ..domain.models import ChatRequest, ChatResponse, Product, CustomerProfile
from ..core.llm import LLMClient, Message
from .recommendation_agent import RecommendationAgent
from .inventory_agent import InventoryAgent
from .loyalty_agent import LoyaltyAgent
from .payment_agent import PaymentAgent
from .fulfillment_agent import FulfillmentAgent


class SalesAgent:
    """
    Main orchestrator agent handling:
    - recommendations
    - stock checks
    - reservations
    - payments
    - fallback conversation
    """

    def __init__(
        self,
        llm: LLMClient,
        products: List[Product],
        customers: Dict[str, CustomerProfile],
        inventory_agent: InventoryAgent,
        loyalty_agent: LoyaltyAgent,
        payment_agent: PaymentAgent,
        fulfillment_agent: FulfillmentAgent,
    ):
        self.llm = llm
        self.products = products
        self.customers = customers
        self.inventory_agent = inventory_agent
        self.loyalty_agent = loyalty_agent
        self.payment_agent = payment_agent
        self.fulfillment_agent = fulfillment_agent

    # ======================================================================
    # MAIN HANDLER
    # ======================================================================

    async def handle(self, req: ChatRequest, session_state: Dict[str, Any]) -> ChatResponse:
        logger.info(f"Handling message from {req.customer_id} on {req.channel}: {req.message!r}")

        customer = self.customers[req.customer_id]
        state: Dict[str, Any] = dict(session_state)
        text = req.message.strip()
        text_lower = text.lower()

        # ------------------------------------------------------------------
        # 1) PAYMENT STAGE (user already chose product, now picking method)
        # ------------------------------------------------------------------
        if state.get("payment_stage") == "awaiting_method":
            reply = self._handle_payment_method_step(text_lower, customer, state)
            return ChatResponse(
                session_id=req.session_id,
                channel=req.channel,
                agent_reply=reply,
                state=state,
            )

        # ------------------------------------------------------------------
        # 1B) FULFILLMENT CHOICE AFTER SUCCESSFUL PAYMENT
        # ------------------------------------------------------------------
        if state.get("payment_stage") == "done":
            # User is now choosing between home delivery / store pickup
            if "home" in text_lower or "deliver" in text_lower or "delivery" in text_lower:
                state["fulfillment_choice"] = "home_delivery"
                state["payment_stage"] = None
                reply = (
                    "Great! Your order will be delivered to your registered address.\n"
                    "You'll receive tracking details shortly."
                )
            elif "store" in text_lower or "pickup" in text_lower or "pick up" in text_lower:
                state["fulfillment_choice"] = "store_pickup"
                state["payment_stage"] = None
                last_payment = state.get("last_payment") or {}
                txn = last_payment.get("transaction_id", "your transaction ID")
                reply = (
                    "Got it! Your order will be ready for in-store pickup.\n"
                    f"Please show {txn} at the counter when you visit the store."
                )
            else:
                # Still in 'done' stage but user said something else
                reply = "Would you prefer *home delivery* or *store pickup*?"

            return ChatResponse(
                session_id=req.session_id,
                channel=req.channel,
                agent_reply=reply,
                state=state,
            )

        # ------------------------------------------------------------------
        # 2) RECOMMENDATION (LLM assisted)
        # ------------------------------------------------------------------
        keywords_for_reco = ["suggest", "recommend", "show", "find", "looking for"]
        product_terms = ["shirt", "short", "dress", "jeans", "tshirt", "kurta"]

        mentions_product = any(term in text_lower for term in product_terms)
        budget = self._extract_budget(text_lower)
        mentions_budget = budget is not None

        if (
            any(word in text_lower for word in keywords_for_reco)
            or mentions_product
            or mentions_budget
        ):
            rec_agent = RecommendationAgent(self.products, self.llm)
            recs = await rec_agent.recommend(req.message, customer, budget)

            # ensure consistent order based on price (low → high)
            sorted_recs = sorted(recs, key=lambda p: p.price)

            state["last_recommendations"] = [p.sku for p in sorted_recs]

            if not recs:
                reply = (
                    "I couldn't find options in that range. "
                    "Want me to suggest something slightly above your budget?"
                )
            else:
                names = ", ".join(f"{p.name} (₹{p.price:.0f})" for p in recs)
                reply = (
                    f"I found these options for you: {names}. "
                    "Would you like me to check availability for any of them?"
                )

            return ChatResponse(
                session_id=req.session_id,
                channel=req.channel,
                agent_reply=reply,
                state=state,
            )

        # ------------------------------------------------------------------
        # 3) INVENTORY CHECK (supports “first/second/third/fourth… availability”)
        # ------------------------------------------------------------------
        if "availability" in text_lower or "in stock" in text_lower:
            index = self._extract_item_index(text_lower)
            recs = state.get("last_recommendations", [])

            if index is not None:
                # User said: "first availability", "fourth availability", etc.
                if not recs or index >= len(recs):
                    return ChatResponse(
                        session_id=req.session_id,
                        channel=req.channel,
                        agent_reply="I only have a few options. Please pick from the ones I suggested.",
                        state=state,
                    )
                sku = recs[index]
            else:
                # Generic availability → pick best from state
                try:
                    sku = self._pick_sku_from_state(state)
                except ValueError as e:
                    return ChatResponse(
                        session_id=req.session_id,
                        channel=req.channel,
                        agent_reply=str(e),
                        state=state,
                    )

            record = self.inventory_agent.first_available_store(sku)

            if record:
                state["reserved_candidate_sku"] = sku
                state["reserved_store"] = record.store_id
                reply = (
                    f"Good news! SKU {sku} is available at store {record.store_id}. "
                    "Should I reserve it for try-on or proceed to payment?"
                )
            else:
                reply = "It seems out of stock right now. Want me to suggest something similar?"

            return ChatResponse(
                session_id=req.session_id,
                channel=req.channel,
                agent_reply=reply,
                state=state,
            )

        # ------------------------------------------------------------------
        # 4) RESERVE IN STORE
        # ------------------------------------------------------------------
        if "reserve" in text_lower:
            try:
                sku = state.get("reserved_candidate_sku") or self._pick_sku_from_state(state)
            except ValueError as e:
                return ChatResponse(
                    session_id=req.session_id,
                    channel=req.channel,
                    agent_reply=str(e),
                    state=state,
                )

            record = self.inventory_agent.first_available_store(sku)

            if record:
                result = self.fulfillment_agent.reserve_in_store(record)
                state["last_reservation"] = {"sku": sku, "store_id": record.store_id}
                reply = f"{result.message} You can pay here or at the store."
            else:
                reply = "I tried to reserve it but it looks out of stock now."

            return ChatResponse(
                session_id=req.session_id,
                channel=req.channel,
                agent_reply=reply,
                state=state,
            )

        # ------------------------------------------------------------------
        # 5) PAYMENT FLOW START (“proceed to payment”, “checkout”, etc.)
        # ------------------------------------------------------------------
        payment_start_keywords = [
            "proceed to payment",
            "checkout",
            "check out",
            "buy this",
            "buy it",
            "buy now",
            "pay now",
            "proceed to pay",
            "pay here",
        ]
        if any(k in text_lower for k in payment_start_keywords) or (
            "payment" in text_lower and not state.get("payment_stage")
        ):
            try:
                reply = self._start_payment_flow(customer, state)
            except ValueError as e:
                return ChatResponse(
                    session_id=req.session_id,
                    channel=req.channel,
                    agent_reply=str(e),
                    state=state,
                )
            return ChatResponse(
                session_id=req.session_id,
                channel=req.channel,
                agent_reply=reply,
                state=state,
            )

        # ------------------------------------------------------------------
        # 6) FALLBACK TO LLM FOR GENERAL CHAT
        # ------------------------------------------------------------------
        history_raw = state.get("history", [])
        history = [Message(**m) for m in history_raw]
        history.append(Message(role="user", content=req.message))

        response = await self.llm.chat(history)

        history.append(Message(role="assistant", content=response))
        state["history"] = [m.model_dump() for m in history]

        return ChatResponse(
            session_id=req.session_id,
            channel=req.channel,
            agent_reply=response,
            state=state,
        )

    # ======================================================================
    # INTERNAL HELPERS
    # ======================================================================

    def _extract_item_index(self, text_lower: str) -> int | None:
        """
        Detect phrases like:
        - 'first availability'
        - 'second one'
        - 'fourth option'
        and return 0-based index.
        """
        mapping = {
            "first": 0, "1st": 0, "one": 0,
            "second": 1, "2nd": 1, "two": 1,
            "third": 2, "3rd": 2, "three": 2,
            "fourth": 3, "4th": 3, "four": 3,
            "fifth": 4, "5th": 4, "five": 4,
        }

        for word, idx in mapping.items():
            if word in text_lower:
                return idx
        return None

    def _start_payment_flow(self, customer: CustomerProfile, state: Dict[str, Any]) -> str:
        """
        Compute price, apply loyalty discount, and move into 'awaiting_method' stage.
        """
        sku = self._pick_sku_from_state(state)
        product = next(p for p in self.products if p.sku == sku)

        discount = self.loyalty_agent.calculate_discount(customer, product.price)
        final_amount = max(product.price - discount, 0)

        state["payment_stage"] = "awaiting_method"
        state["payment_context"] = {
            "sku": sku,
            "base_price": product.price,
            "discount": discount,
            "amount_due": final_amount,
        }

        return (
            f"Great, let's proceed to payment for **{product.name}**.\n"
            f"- MRP: ₹{product.price:.0f}\n"
            f"- Loyalty Savings: ₹{discount:.0f}\n"
            f"- Amount to Pay: ₹{final_amount:.0f}\n\n"
            "How would you like to pay?\n"
            "1) UPI\n"
            "2) Saved card\n"
            "3) Card\n"
            "4) Pay in store"
        )

    def _handle_payment_method_step(
        self,
        text_lower: str,
        customer: CustomerProfile,
        state: Dict[str, Any],
    ) -> str:
        """
        Step where user chooses payment method.
        """
        ctx = state.get("payment_context") or {}
        if not ctx:
            state["payment_stage"] = None
            return "Payment context missing. Please say 'proceed to payment' again."

        method = self._detect_payment_method(text_lower)
        if not method:
            return "Please choose a valid option: 1) UPI  2) Saved Card  3) Card  4) Pay in Store."

        amount = float(ctx["amount_due"])
        payment = self.payment_agent.charge(amount, method=method)

        if payment.success:
            state["payment_stage"] = "done"
            state["last_payment"] = {
                "sku": ctx["sku"],
                "amount": amount,
                "method": method,
                "transaction_id": payment.transaction_id,
            }
            return (
                f"Payment successful! Transaction ID: {payment.transaction_id}.\n"
                "Would you prefer home delivery or store pickup?"
            )

        state["payment_stage"] = "awaiting_method"
        return f"Payment failed: {payment.failure_reason}. Try another method."

    @staticmethod
    def _detect_payment_method(text: str) -> str | None:
        text = text.replace(")", "").strip().lower()

        if text == "1" or "upi" in text:
            return "upi"
        if text == "2" or "saved card" in text:
            return "saved_card"
        if text == "3" or "card" in text or "credit" in text or "debit" in text:
            return "card"
        if text == "4" or "store" in text:
            return "pay_in_store"

        return None

    @staticmethod
    def _extract_budget(text: str) -> float | None:
        """
        Very simple budget extractor: first 3–6 digit number.
        """
        import re

        m = re.search(r"(\d{3,6})", text)
        return float(m.group(1)) if m else None

    def _pick_sku_from_state(self, state: Dict[str, Any]) -> str:
        """
        Safely choose a SKU from conversation context.
        Raises ValueError with a friendly message if nothing is available.
        """

        # 1) If user explicitly selected / reserved something
        if "reserved_candidate_sku" in state:
            return state["reserved_candidate_sku"]

        # 2) Otherwise take from last recommendations
        recs = state.get("last_recommendations") or []
        if not recs:
            raise ValueError(
                "No recommendations available yet. Try something like 'show outfits under 3000' first."
            )

        # 3) Prefer the first product that actually has stock
        for sku in recs:
            if self.inventory_agent.first_available_store(sku):
                return sku

        # 4) If none in stock, fallback to the first recommendation
        return recs[0]
