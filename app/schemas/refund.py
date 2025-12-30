from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal


# -----------------------------
# Requests
# -----------------------------
class RefundCreateRequest(BaseModel):
    payment_id: UUID
    amount: Decimal = Field(..., gt=0)
    reason: str | None = None


# -----------------------------
# Responses
# -----------------------------
class RefundResponse(BaseModel):
    id: UUID
    payment_id: UUID
    merchant_id: UUID
    amount: Decimal
    currency: str
    status: str
    reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True
