from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .enums import Channel


class Product(BaseModel):
    sku: str
    name: str
    category: str
    price: float
    attributes: Dict[str, Any] = Field(default_factory=dict)
    image_url: Optional[str] = None


class CustomerProfile(BaseModel):
    id: str
    name: str
    loyalty_tier: str
    loyalty_points: int
    preferences: List[str] = Field(default_factory=list)
    past_purchases: List[str] = Field(default_factory=list)
    default_channel: Channel = Channel.MOBILE_APP


class ChatRequest(BaseModel):
    session_id: str
    customer_id: str
    channel: Channel
    message: str


class ChatResponse(BaseModel):
    session_id: str
    channel: Channel
    agent_reply: str
    state: Dict[str, Any] = Field(default_factory=dict)


class InventoryRecord(BaseModel):
    sku: str
    store_id: str
    quantity: int


class Offer(BaseModel):
    id: str
    description: str
    percentage: float
    applicable_categories: List[str]
