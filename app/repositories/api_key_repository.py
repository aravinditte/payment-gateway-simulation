"""API key repository."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import APIKey
from app.db.repository import BaseRepository


class APIKeyRepository(BaseRepository[APIKey]):
    """Repository for API key operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize API key repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session, APIKey)

    async def get_by_api_key(self, api_key: str) -> Optional[APIKey]:
        """Get API key record by API key.

        Args:
            api_key: API key string

        Returns:
            Optional[APIKey]: API key record or None
        """
        stmt = select(APIKey).where(
            APIKey.api_key == api_key,
            APIKey.is_active == True,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_merchant_id(self, merchant_id: str) -> list[APIKey]:
        """Get all API keys for merchant.

        Args:
            merchant_id: Merchant ID

        Returns:
            list[APIKey]: List of API keys
        """
        stmt = select(APIKey).where(APIKey.merchant_id == merchant_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
