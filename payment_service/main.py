from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from common.middleware import LoggingMiddleware
from .factories import PaymentProviderFactory

app = FastAPI(title="Payment Service")
app.add_middleware(LoggingMiddleware)


class PaymentRequest(BaseModel):
    user_id: str
    amount: float
    method: str


class PaymentResult(BaseModel):
    success: bool


@app.post("/charge", response_model=PaymentResult)
def charge(req: PaymentRequest):
    try:
        provider = PaymentProviderFactory.create(req.method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ok = provider.charge(req.user_id, req.amount)
    return PaymentResult(success=ok)
