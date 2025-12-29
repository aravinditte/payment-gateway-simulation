"""FastAPI dependencies."""

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.db.models import APIKey, Merchant
from app.services.auth_service import AuthService
from app.services.exceptions import AuthenticationError


async def get_current_merchant(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_db),
) -> tuple[Merchant, APIKey]:
    """Get current merchant from authorization header.

    Args:
        authorization: Authorization header
        session: Database session

        Returns:
            tuple[Merchant, APIKey]: (merchant, api_key)

        Raises:
            AuthenticationError: If authentication fails
    """
    auth_service = AuthService(session)
    return await auth_service.authenticate_request(authorization)
