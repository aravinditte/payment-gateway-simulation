from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.refund import Refund


class RefundRepository:
    """
    Data access layer for Refund entities.
    """

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        refund: Refund,
    ) -> Refund:
        db.add(refund)
        await db.flush()
        return refund

    @classmethod
    async def get_by_id(
        cls,
        db: AsyncSession,
        refund_id,
        merchant_id,
    ) -> Optional[Refund]:
        stmt = select(Refund).where(
            Refund.id == refund_id,
            Refund.merchant_id == merchant_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_idempotency_key(
        cls,
        db: AsyncSession,
        payment_id,
        idempotency_key: str,
    ) -> Optional[Refund]:
        stmt = select(Refund).where(
            Refund.payment_id == payment_id,
            Refund.idempotency_key == idempotency_key,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def list_by_payment(
        cls,
        db: AsyncSession,
        payment_id,
    ) -> List[Refund]:
        stmt = (
            select(Refund)
            .where(Refund.payment_id == payment_id)
            .order_by(Refund.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()
