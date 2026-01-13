from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class OrderItemPublic(BaseModel):
    product_id: int
    name: Optional[str] = None
    quantity: int
    unit_price: float


class OrderPublic(BaseModel):
    id_key: int
    date: Optional[datetime] = None
    total: Optional[float] = None
    status: Optional[str] = None
    items: List[OrderItemPublic] = []
