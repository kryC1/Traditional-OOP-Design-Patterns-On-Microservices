from dataclasses import dataclass
from typing import List
from common.models import OrderItem, CreateOrderRequest, OrderResponse
import httpx
import uuid


@dataclass
class CheckoutContext:
    request: CreateOrderRequest
    total_amount: float = 0.0
    inventory_ok: bool = False
    payment_ok: bool = False
    order_id: str | None = None


class CheckoutBuilder:
    """
    Builder pattern: step-by-step assembly of a checkout workflow
    involving multiple services (inventory, payment, notification).
    """

    def __init__(self, inventory_url: str, payment_url: str, notify_url: str):
        self.inventory_url = inventory_url
        self.payment_url = payment_url
        self.notify_url = notify_url

    async def check_inventory(self, ctx: CheckoutContext) -> "CheckoutBuilder":
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.inventory_url}/check",
                json={"items": [item.dict() for item in ctx.request.items]},
                timeout=5.0,
            )
            resp.raise_for_status()
            data = resp.json()
        ctx.inventory_ok = data["ok"]
        ctx.total_amount = data["total_amount"]
        return self

    async def process_payment(self, ctx: CheckoutContext) -> "CheckoutBuilder":
        if not ctx.inventory_ok:
            return self
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.payment_url}/charge",
                json={
                    "user_id": ctx.request.user_id,
                    "amount": ctx.total_amount,
                    "method": ctx.request.payment_method,
                },
                timeout=5.0,
            )
            resp.raise_for_status()
            data = resp.json()
        ctx.payment_ok = data["success"]
        return self

    async def finalize_order(self, ctx: CheckoutContext) -> "CheckoutBuilder":
        if not (ctx.inventory_ok and ctx.payment_ok):
            return self
        ctx.order_id = str(uuid.uuid4())
        # notify service about new order
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.notify_url}/order-created",
                json={"order_id": ctx.order_id, "user_id": ctx.request.user_id},
                timeout=5.0,
            )
        return self

    def build_response(self, ctx: CheckoutContext) -> OrderResponse:
        status = "FAILED"
        if ctx.inventory_ok and ctx.payment_ok and ctx.order_id:
            status = "COMPLETED"
        return OrderResponse(
            order_id=ctx.order_id or "N/A",
            status=status,
            total_amount=ctx.total_amount,
        )
