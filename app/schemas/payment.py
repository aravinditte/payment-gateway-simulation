"""Payment request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    """Create payment request."""

    amount: int = Field(..., gt=0, description="Amount in paise/cents")
    currency: str = Field(default="INR", description="Currency code")
    description: Optional[str] = Field(None, description="Payment description")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_phone: Optional[str] = Field(None, description="Customer phone")
    metadata: Optional[dict] = Field(None, description="Custom metadata")
    simulate: Optional[str] = Field(
        None,
        description="Simulation type (success, insufficient_funds, network_timeout, fraud_detected, bank_error)",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "amount": 10000,
                "currency": "INR",
                "description": "Order #123",
                "customer_email": "user@example.com",
                "metadata": {"order_id": "123", "customer_id": "456"},
            }
        }


class PaymentResponse(BaseModel):
    """Payment response."""

    id: str
    amount: int
    currency: str
    status: str
    description: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    metadata: Optional[dict] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    authorized_at: Optional[datetime] = None
    captured_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class CapturePaymentRequest(BaseModel):
    """Capture payment request."""

    pass


class RefundPaymentRequest(BaseModel):
    """Refund payment request."""

    amount: Optional[int] = Field(None, gt=0, description="Refund amount (None = full)")
    reason: Optional[str] = Field(None, description="Refund reason")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "amount": 5000,
                "reason": "Customer requested",
            }
        }


class RefundResponse(BaseModel):
    """Refund response."""

    id: str
    payment_id: str
    amount: int
    reason: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
