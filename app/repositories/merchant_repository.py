"""Merchant repository."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Merchant
from app.db.repository import BaseRepository


class MerchantRepository(BaseRepository[Merchant]):
    """Repository for merchant operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize merchant repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session, Merchant)

    async def get_by_email(self, email: str) -> Optional[Merchant]:
        """Get merchant by email.

        Args:
            email: Merchant email

        Returns:
            Optional[Merchant]: Merchant or None
        """
        stmt = select(Merchant).where(Merchant.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
