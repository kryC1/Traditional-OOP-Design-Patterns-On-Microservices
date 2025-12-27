from fastapi import FastAPI
from pydantic import BaseModel

from common.config import get_oop_enabled
from common.middleware import LoggingMiddleware, install_logging_middleware

app = FastAPI(title="Notification Service")

# Middleware selection
if get_oop_enabled(default=True):
    app.add_middleware(LoggingMiddleware)
else:
    install_logging_middleware(app)


class OrderCreatedEvent(BaseModel):
    order_id: str
    user_id: str


@app.post("/order-created")
def order_created(event: OrderCreatedEvent):
    # Minimal side effect for benchmarking
    print(f"[Notification] Order created: order_id={event.order_id}, user={event.user_id}")
    return {"status": "ok"}
