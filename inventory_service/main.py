from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from common.config import get_oop_enabled
from common.middleware import LoggingMiddleware, install_logging_middleware

app = FastAPI(title="Inventory Service")

# Middleware selection
if get_oop_enabled(default=True):
    app.add_middleware(LoggingMiddleware)
else:
    install_logging_middleware(app)


class Item(BaseModel):
    product_id: str
    quantity: int


class InventoryCheckRequest(BaseModel):
    items: List[Item]


class InventoryCheckResponse(BaseModel):
    ok: bool
    total_amount: float


# Hard-coded price table
PRICES = {
    "p1": 10.0,
    "p2": 20.0,
    "p3": 5.0,
}


@app.post("/check", response_model=InventoryCheckResponse)
def check_inventory(req: InventoryCheckRequest):
    total = 0.0
    for item in req.items:
        total += PRICES.get(item.product_id, 0.0) * item.quantity

    return InventoryCheckResponse(ok=True, total_amount=total)
