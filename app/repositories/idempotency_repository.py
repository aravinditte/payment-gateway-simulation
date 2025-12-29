"""Idempotency key repository."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IdempotencyKey
from app.db.repository import BaseRepository


class IdempotencyKeyRepository(BaseRepository[IdempotencyKey]):
    """Repository for idempotency key operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize idempotency key repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session, IdempotencyKey)

    async def get_by_key(self, idempotency_key: str) -> Optional[IdempotencyKey]:
        """Get idempotency key record.

        Args:
            idempotency_key: Idempotency key string

        Returns:
            Optional[IdempotencyKey]: Idempotency key record or None
        """
        stmt = select(IdempotencyKey).where(
            IdempotencyKey.idempotency_key == idempotency_key
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
