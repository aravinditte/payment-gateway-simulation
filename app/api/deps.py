from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_api_key
from app.core.exceptions import AuthenticationError
from app.db.session import get_db_session
from app.repositories.merchant_repository import MerchantRepository
from app.db.models.merchant import Merchant


async def get_current_merchant(
    api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db_session),
) -> Merchant:
    """
    Resolves the authenticated merchant from API key.
    """
    merchant = await MerchantRepository.get_by_api_key(db, api_key)

    if not merchant or not merchant.is_active:
        raise AuthenticationError("Invalid or inactive API key")

    return merchant
