from fastapi import FastAPI, HTTPException
import httpx

from common.models import CreateOrderRequest, OrderResponse
from common.config import get_oop_enabled
from common.middleware import LoggingMiddleware, install_logging_middleware

ORDER_SERVICE_URL = "http://localhost:8001"


def create_app() -> FastAPI:
    oop_enabled = get_oop_enabled(default=True)

    app = FastAPI(title="API Gateway")

    # Middleware: OOP vs procedural
    if oop_enabled:
        app.add_middleware(LoggingMiddleware)
    else:
        install_logging_middleware(app)

    if oop_enabled:
        # ---- OOP/Strategy version (your existing design) ----
        from abc import ABC, abstractmethod

        class RoutingStrategy(ABC):
            @abstractmethod
            async def route_order(self, req: CreateOrderRequest) -> OrderResponse:
                ...

        class SimpleRoutingStrategy(RoutingStrategy):
            async def route_order(self, req: CreateOrderRequest) -> OrderResponse:
                async with httpx.AsyncClient() as client:
                    r = await client.post(f"{ORDER_SERVICE_URL}/orders", json=req.model_dump(), timeout=5.0)
                r.raise_for_status()
                return OrderResponse(**r.json())

        current_strategy: RoutingStrategy = SimpleRoutingStrategy()

        @app.post("/checkout", response_model=OrderResponse)
        async def checkout(req: CreateOrderRequest):
            try:
                return await current_strategy.route_order(req)
            except httpx.HTTPError as e:
                raise HTTPException(status_code=502, detail=str(e))

    else:
        # ---- Procedural version (no Strategy classes) ----
        @app.post("/checkout", response_model=OrderResponse)
        async def checkout(req: CreateOrderRequest):
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.post(
                        f"{ORDER_SERVICE_URL}/orders",
                        json=req.model_dump(),
                        timeout=5.0,
                    )
                r.raise_for_status()
                return OrderResponse(**r.json())
            except httpx.HTTPError as e:
                raise HTTPException(status_code=502, detail=str(e))

    return app


app = create_app()
