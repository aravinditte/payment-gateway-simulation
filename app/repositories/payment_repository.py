"""Payment repository."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PaymentStatus
from app.db.models import Payment
from app.db.repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository for payment operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize payment repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session, Payment)

    async def get_by_merchant_and_payment_id(
        self, merchant_id: str, payment_id: str
    ) -> Optional[Payment]:
        """Get payment by merchant and payment ID.

        Args:
            merchant_id: Merchant ID
            payment_id: Payment ID

        Returns:
            Optional[Payment]: Payment or None
        """
        stmt = select(Payment).where(
            Payment.id == payment_id,
            Payment.merchant_id == merchant_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_status(
        self, status: PaymentStatus, limit: int = 100
    ) -> list[Payment]:
        """Get payments by status.

        Args:
            status: Payment status
            limit: Maximum records

        Returns:
            list[Payment]: List of payments
        """
        stmt = select(Payment).where(Payment.status == status).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
