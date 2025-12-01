from pydantic import BaseModel
from typing import List


class OrderItem(BaseModel):
    product_id: str
    quantity: int


class CreateOrderRequest(BaseModel):
    user_id: str
    items: List[OrderItem]
    payment_method: str  # "credit_card", "paypal", etc.


class OrderResponse(BaseModel):
    order_id: str
    status: str
    total_amount: float
