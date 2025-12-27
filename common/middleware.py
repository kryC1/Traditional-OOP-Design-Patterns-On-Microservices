import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000.0
        # Consider disabling prints for benchmark runs
        print(f"{request.method} {request.url.path} -> {response.status_code} in {duration_ms:.2f} ms")
        return response


def install_logging_middleware(app: FastAPI) -> None:
    """
    Procedural (non-class) middleware registration.
    This avoids the explicit Decorator-pattern narrative in code.
    """
    @app.middleware("http")
    async def _timing_middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000.0
        # Consider disabling prints for benchmark runs
        print(f"{request.method} {request.url.path} -> {response.status_code} in {duration_ms:.2f} ms")
        return response
