import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.models.webhook_event import WebhookEvent
from app.db.models.merchant import Merchant
from app.workers.webhook_dispatcher import WebhookDispatcher

settings = get_settings()
logger = get_logger(__name__)


class WebhookRetryScheduler:
    """
    Periodically retries failed webhook deliveries using exponential backoff.
    """

    @classmethod
    async def run_once(cls, db: AsyncSession) -> None:
        """
        Runs a single retry cycle.
        """
        stmt = select(WebhookEvent).where(
            WebhookEvent.delivered.is_(False),
            WebhookEvent.attempt_count < settings.WEBHOOK_MAX_RETRIES,
        )

        result = await db.execute(stmt)
        events = result.scalars().all()

        if not events:
            return

        logger.info(
            "webhook_retry_cycle_started",
            extra={"pending_events": len(events)},
        )

        for event in events:
            # Simple exponential backoff
            backoff_seconds = (
                settings.WEBHOOK_RETRY_BACKOFF_SECONDS
                * (2 ** (event.attempt_count - 1))
            )

            await asyncio.sleep(backoff_seconds)

            merchant = await db.get(Merchant, event.merchant_id)
            if not merchant:
                continue

            await WebhookDispatcher.dispatch(
                db=db,
                event=event,
                webhook_secret=merchant.webhook_secret,
            )

    @classmethod
    async def run_forever(cls, db: AsyncSession, interval_seconds: int = 10) -> None:
        """
        Continuously runs retry cycles.
        Intended for background worker process.
        """
        logger.info("webhook_retry_scheduler_started")

        while True:
            try:
                await cls.run_once(db)
            except Exception as exc:
                logger.exception(
                    "webhook_retry_scheduler_error",
                    extra={"error": str(exc)},
                )

            await asyncio.sleep(interval_seconds)
