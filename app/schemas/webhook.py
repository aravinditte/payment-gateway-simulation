from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class WebhookEventResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    payment_id: UUID | None
    event_type: str
    delivered: bool
    attempt_count: int
    last_status_code: int | None
    created_at: datetime
    last_attempt_at: datetime | None

    class Config:
        from_attributes = True
