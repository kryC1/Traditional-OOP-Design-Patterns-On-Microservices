import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Decorator-like middleware that wraps each request to log and measure latency.
    Demonstrates Decorator pattern at HTTP layer.
    """

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        print(f"{request.method} {request.url.path} -> {response.status_code} "
              f"in {duration_ms:.2f} ms")
        return response
