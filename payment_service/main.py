from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common.config import get_oop_enabled
from common.middleware import LoggingMiddleware, install_logging_middleware

app = FastAPI(title="Payment Service")

oop_enabled = get_oop_enabled(default=True)
if oop_enabled:
    app.add_middleware(LoggingMiddleware)
else:
    install_logging_middleware(app)


class PaymentRequest(BaseModel):
    user_id: str
    amount: float
    method: str


class PaymentResult(BaseModel):
    success: bool


# ---- Procedural payment handlers (no Factory/providers) ----
def _charge_credit_card(user_id: str, amount: float) -> bool:
    # keep minimal work for benchmarking
    return True


def _charge_paypal(user_id: str, amount: float) -> bool:
    return True


_PROCEDURAL_DISPATCH = {
    "credit_card": _charge_credit_card,
    "paypal": _charge_paypal,
}


@app.post("/charge", response_model=PaymentResult)
def charge(req: PaymentRequest):
    if oop_enabled:
        # OOP/Factory Method path
        from .factories import PaymentProviderFactory
        try:
            provider = PaymentProviderFactory.create(req.method)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        ok = provider.charge(req.user_id, req.amount)
        return PaymentResult(success=ok)

    # Procedural path
    fn = _PROCEDURAL_DISPATCH.get(req.method)
    if fn is None:
        raise HTTPException(status_code=400, detail=f"Unsupported payment method: {req.method}")
    return PaymentResult(success=bool(fn(req.user_id, req.amount)))
