from pydantic import BaseModel, EmailStr, HttpUrl
from uuid import UUID
from datetime import datetime


class MerchantResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    webhook_url: HttpUrl | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
