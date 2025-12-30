from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal


# -----------------------------
# Requests
# -----------------------------
class PaymentCreateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    external_reference: str | None = None
    simulation: str | None = Field(
        None,
        description="Simulation scenario: success, timeout, fraud, etc.",
    )


# -----------------------------
# Responses
# -----------------------------
class PaymentResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    amount: Decimal
    currency: str
    status: str
    failure_code: str | None
    failure_message: str | None
    simulation_scenario: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
