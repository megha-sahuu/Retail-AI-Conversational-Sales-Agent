from dataclasses import dataclass
from ..domain.models import InventoryRecord


@dataclass
class FulfillmentResult:
    success: bool
    message: str


class FulfillmentAgent:
    """
    Handles fulfillment actions like reserve-in-store or delivery booking.
    For the prototype we just simulate a successful reservation.
    """

    def reserve_in_store(self, record: InventoryRecord) -> FulfillmentResult:
        # In a real system, this would call OMS / POS or logistics API.
        return FulfillmentResult(
            success=True,
            message=f"Item reserved at store {record.store_id}. Pickup valid for 24 hours.",
        )

    # You could later add:
    # def schedule_delivery(...): ...
