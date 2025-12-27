from fastapi import FastAPI
import httpx
import uuid

from common.config import get_oop_enabled
from common.middleware import LoggingMiddleware, install_logging_middleware
from common.models import CreateOrderRequest, OrderResponse

ORDER_INVENTORY_URL = "http://localhost:8003"
ORDER_PAYMENT_URL = "http://localhost:8002"
ORDER_NOTIFICATION_URL = "http://localhost:8004"


def create_app() -> FastAPI:
    oop_enabled = get_oop_enabled(default=True)

    app = FastAPI(title="Order Service")

    if oop_enabled:
        app.add_middleware(LoggingMiddleware)
    else:
        install_logging_middleware(app)

    if oop_enabled:
        # ---- OOP/Builder version (your existing code) ----
        from .builder import CheckoutBuilder, CheckoutContext

        @app.post("/orders", response_model=OrderResponse)
        async def create_order(req: CreateOrderRequest):
            ctx = CheckoutContext(request=req)
            builder = CheckoutBuilder(
                inventory_url=ORDER_INVENTORY_URL,
                payment_url=ORDER_PAYMENT_URL,
                notify_url=ORDER_NOTIFICATION_URL,
            )
            await builder.check_inventory(ctx)
            await builder.process_payment(ctx)
            await builder.finalize_order(ctx)
            return builder.build_response(ctx)

    else:
        # ---- Procedural version (single function orchestration) ----
        @app.post("/orders", response_model=OrderResponse)
        async def create_order(req: CreateOrderRequest):
            async with httpx.AsyncClient() as client:
                # Step 1: inventory
                inv = await client.post(
                    f"{ORDER_INVENTORY_URL}/check",
                    json={"items": [it.model_dump() for it in req.items]},
                    timeout=5.0,
                )
                inv.raise_for_status()
                inv_data = inv.json()
                inventory_ok = bool(inv_data.get("ok", False))
                total_amount = float(inv_data.get("total_amount", 0.0))

                if not inventory_ok:
                    return OrderResponse(order_id="N/A", status="FAILED", total_amount=total_amount)

                # Step 2: payment
                pay = await client.post(
                    f"{ORDER_PAYMENT_URL}/charge",
                    json={"user_id": req.user_id, "amount": total_amount, "method": req.payment_method},
                    timeout=5.0,
                )
                pay.raise_for_status()
                pay_ok = bool(pay.json().get("success", False))

                if not pay_ok:
                    return OrderResponse(order_id="N/A", status="FAILED", total_amount=total_amount)

                # Step 3: finalize + notify
                order_id = str(uuid.uuid4())
                await client.post(
                    f"{ORDER_NOTIFICATION_URL}/order-created",
                    json={"order_id": order_id, "user_id": req.user_id},
                    timeout=5.0,
                )

                return OrderResponse(order_id=order_id, status="COMPLETED", total_amount=total_amount)

    return app


app = create_app()
