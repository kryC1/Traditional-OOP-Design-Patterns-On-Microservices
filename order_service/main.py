from fastapi import FastAPI
from common.middleware import LoggingMiddleware
from common.models import CreateOrderRequest, OrderResponse
from .builder import CheckoutBuilder, CheckoutContext

ORDER_INVENTORY_URL = "http://localhost:8003"
ORDER_PAYMENT_URL = "http://localhost:8002"
ORDER_NOTIFICATION_URL = "http://localhost:8004"

app = FastAPI(title="Order Service")
app.add_middleware(LoggingMiddleware)


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
