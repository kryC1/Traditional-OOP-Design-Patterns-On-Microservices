from abc import ABC, abstractmethod
from fastapi import FastAPI
from fastapi import HTTPException
from common.middleware import LoggingMiddleware
from common.models import CreateOrderRequest, OrderResponse
import httpx

app = FastAPI(title="API Gateway")
app.add_middleware(LoggingMiddleware)

ORDER_SERVICE_URL = "http://localhost:8001"


# --- Strategy pattern for routing/policy selection ---

class RoutingStrategy(ABC):
    @abstractmethod
    async def route_order(self, req: CreateOrderRequest) -> OrderResponse:
        ...


class SimpleRoutingStrategy(RoutingStrategy):
    async def route_order(self, req: CreateOrderRequest) -> OrderResponse:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{ORDER_SERVICE_URL}/orders", json=req.dict(), timeout=5.0)
        r.raise_for_status()
        return OrderResponse(**r.json())


class FailingFastStrategy(RoutingStrategy):
    """
    Example of a strategy that refuses requests if some condition is met
    (e.g., we detected high latency, circuit open, etc.)
    """

    async def route_order(self, req: CreateOrderRequest) -> OrderResponse:
        # For demo, we'll just pass through; later you can add latency checks, etc.
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{ORDER_SERVICE_URL}/orders", json=req.dict(), timeout=5.0)
        r.raise_for_status()
        return OrderResponse(**r.json())


# You can change this at runtime or via env variable to simulate different strategies
current_strategy: RoutingStrategy = SimpleRoutingStrategy()


@app.post("/checkout", response_model=OrderResponse)
async def checkout(req: CreateOrderRequest):
    try:
        return await current_strategy.route_order(req)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))
