from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.idempotency import IdempotencyKey


class IdempotencyRepository:
    """
    Repository for idempotency key tracking and replay protection.
    """

    @classmethod
    async def get(
        cls,
        db: AsyncSession,
        merchant_id,
        key: str,
    ) -> Optional[IdempotencyKey]:
        stmt = select(IdempotencyKey).where(
            IdempotencyKey.merchant_id == merchant_id,
            IdempotencyKey.key == key,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        record: IdempotencyKey,
    ) -> IdempotencyKey:
        db.add(record)
        await db.flush()
        return record
