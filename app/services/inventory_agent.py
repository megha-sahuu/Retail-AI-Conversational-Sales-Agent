from typing import List, Optional
from ..domain.models import InventoryRecord


class InventoryAgent:
    def __init__(self, records: List[InventoryRecord]):
        self._records = records

    def first_available_store(self, sku: str) -> Optional[InventoryRecord]:
        for record in self._records:
            if record.sku == sku and record.quantity > 0:
                return record
        return None
