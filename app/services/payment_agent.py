from pydantic import BaseModel
from typing import Optional
import random


class PaymentResult(BaseModel):
    """
    Simple result object returned by PaymentAgent. SalesAgent expects:
    - success (bool)
    - transaction_id (optional str)
    - failure_reason (optional str)
    """
    success: bool
    transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None


class PaymentAgent:
    """
    Mock payment processor used for the demo.
    No real money, no external APIs.

    charge(amount, method) returns a PaymentResult.

    Methods:
    - "upi"
    - "saved_card"
    - "card"
    - "pay_in_store"
    """

    def __init__(self) -> None:
        # You could inject config here if needed.
        pass

    def charge(self, amount: float, method: str) -> PaymentResult:
        """
        Simulate a payment.
        - pay_in_store: always 'success' (since user will pay at counter)
        - other methods: ~90% success, 10% failure for realism
        """
        method = method or ""
        method = method.lower().strip()

        # Always succeed for pay-in-store (no online payment)
        if method == "pay_in_store":
            return PaymentResult(
                success=True,
                transaction_id="PAY-IN-STORE",
            )

        # For UPI / saved_card / card, simulate gateway behavior
        success_probability = 0.9  # 90% success

        if random.random() < success_probability:
            txn_id = f"TXN-{random.randint(10000, 99999)}"
            return PaymentResult(
                success=True,
                transaction_id=txn_id,
            )

        # Simulated failure
        return PaymentResult(
            success=False,
            failure_reason="Payment gateway error. Please try another method.",
        )
