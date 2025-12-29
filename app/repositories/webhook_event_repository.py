"""Webhook event repository."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WebhookStatus
from app.db.models import WebhookEvent
from app.db.repository import BaseRepository


class WebhookEventRepository(BaseRepository[WebhookEvent]):
    """Repository for webhook event operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize webhook event repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session, WebhookEvent)

    async def get_failed_webhooks(self, limit: int = 100) -> list[WebhookEvent]:
        """Get failed webhooks pending retry.

        Args:
            limit: Maximum records

        Returns:
            list[WebhookEvent]: List of failed webhooks
        """
        stmt = (
            select(WebhookEvent)
            .where(WebhookEvent.status == WebhookStatus.FAILED)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_payment_id(self, payment_id: str) -> list[WebhookEvent]:
        """Get webhook events for payment.

        Args:
            payment_id: Payment ID

        Returns:
            list[WebhookEvent]: List of webhook events
        """
        stmt = select(WebhookEvent).where(WebhookEvent.payment_id == payment_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
