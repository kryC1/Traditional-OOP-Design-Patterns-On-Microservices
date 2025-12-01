from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from common.middleware import LoggingMiddleware

app = FastAPI(title="Inventory Service")
app.add_middleware(LoggingMiddleware)


class Item(BaseModel):
    product_id: str
    quantity: int


class InventoryCheckRequest(BaseModel):
    items: List[Item]


class InventoryCheckResponse(BaseModel):
    ok: bool
    total_amount: float


# hard-coded price table for demo
PRICES = {
    "p1": 10.0,
    "p2": 20.0,
    "p3": 5.0,
}


@app.post("/check", response_model=InventoryCheckResponse)
def check_inventory(req: InventoryCheckRequest):
    total = 0.0
    for item in req.items:
        price = PRICES.get(item.product_id, 0.0)
        total += price * item.quantity
    # always "in stock" for the demo
    return InventoryCheckResponse(ok=True, total_amount=total)
