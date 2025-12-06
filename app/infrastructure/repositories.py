from pathlib import Path
from typing import List, Dict
import json
from ..core.config import get_settings
from ..domain.models import Product, CustomerProfile, InventoryRecord, Offer

_settings = get_settings()
_data_dir = Path(_settings.data_dir)


def load_products() -> List[Product]:
    with open(_data_dir / "catalog.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Product(**p) for p in data]


def load_customers() -> Dict[str, CustomerProfile]:
    with open(_data_dir / "customers.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return {c["id"]: CustomerProfile(**c) for c in data}


def load_inventory() -> List[InventoryRecord]:
    with open(_data_dir / "inventory.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return [InventoryRecord(**r) for r in data]


def load_offers() -> List[Offer]:
    with open(_data_dir / "offers.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Offer(**o) for o in data]
