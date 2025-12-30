from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.payment import Payment


class PaymentRepository:
    """
    Data access layer for Payment entities.
    """

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        payment: Payment,
    ) -> Payment:
        db.add(payment)
        await db.flush()
        return payment

    @classmethod
    async def get_by_id(
        cls,
        db: AsyncSession,
        payment_id,
        merchant_id,
    ) -> Optional[Payment]:
        stmt = select(Payment).where(
            Payment.id == payment_id,
            Payment.merchant_id == merchant_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_idempotency_key(
        cls,
        db: AsyncSession,
        merchant_id,
        idempotency_key: str,
    ) -> Optional[Payment]:
        stmt = select(Payment).where(
            Payment.merchant_id == merchant_id,
            Payment.idempotency_key == idempotency_key,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def list_by_merchant(
        cls,
        db: AsyncSession,
        merchant_id,
        limit: int = 50,
    ) -> List[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.merchant_id == merchant_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
