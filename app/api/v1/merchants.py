from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_merchant
from app.db.models.merchant import Merchant
from app.db.session import get_db_session

router = APIRouter()


@router.get("/me")
async def get_merchant_profile(
    merchant: Merchant = Depends(get_current_merchant),
):
    """
    Returns authenticated merchant profile.
    """
    return {
        "id": merchant.id,
        "name": merchant.name,
        "email": merchant.email,
        "webhook_url": merchant.webhook_url,
        "is_active": merchant.is_active,
        "created_at": merchant.created_at,
    }
