from fastapi import APIRouter, Depends, HTTPException
from ...core.session import session_store
from ...domain.models import ChatRequest, ChatResponse
from ...services.sales_agent import SalesAgent
from ...core.llm import get_llm_client
from ...infrastructure.repositories import (
    load_products,
    load_customers,
    load_inventory,
    load_offers,
)
from ...services.inventory_agent import InventoryAgent
from ...services.loyalty_agent import LoyaltyAgent
from ...services.payment_agent import PaymentAgent
from ...services.fulfillment_agent import FulfillmentAgent

router = APIRouter(prefix="/chat", tags=["chat"])

_products = load_products()
_customers = load_customers()
_inventory = load_inventory()
_offers = load_offers()

_inventory_agent = InventoryAgent(_inventory)
_loyalty_agent = LoyaltyAgent()
_payment_agent = PaymentAgent()
_fulfillment_agent = FulfillmentAgent()


def get_sales_agent() -> SalesAgent:
    llm = get_llm_client()
    return SalesAgent(
        llm=llm,
        products=_products,
        customers=_customers,
        inventory_agent=_inventory_agent,
        loyalty_agent=_loyalty_agent,
        payment_agent=_payment_agent,
        fulfillment_agent=_fulfillment_agent,
    )


@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    agent: SalesAgent = Depends(get_sales_agent),
) -> ChatResponse:
    if req.customer_id not in _customers:
        raise HTTPException(status_code=404, detail="Customer not found")

    state = session_store.get(req.session_id)
    res = await agent.handle(req, state)
    session_store.set(req.session_id, res.state)
    return res
