from fastapi import FastAPI
from pydantic import BaseModel
from common.middleware import LoggingMiddleware

app = FastAPI(title="Notification Service")
app.add_middleware(LoggingMiddleware)


class OrderCreatedEvent(BaseModel):
    order_id: str
    user_id: str


@app.post("/order-created")
def order_created(event: OrderCreatedEvent):
    # In real life: send email, push notification, etc.
    print(f"[Notification] Order created: order_id={event.order_id}, user={event.user_id}")
    return {"status": "ok"}
