import httpx
import hmac
import hashlib
import time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.models.webhook_event import WebhookEvent

settings = get_settings()
logger = get_logger(__name__)


class WebhookDispatcher:
    """
    Responsible for delivering a single webhook event.
    """

    @staticmethod
    def _sign_payload(payload: str, secret: str) -> str:
        """
        Generates a timestamped HMAC SHA-256 signature.
        """
        timestamp = int(time.time())
        message = f"{timestamp}.{payload}".encode("utf-8")

        signature = hmac.new(
            secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()

        return f"t={timestamp},v1={signature}"

    @classmethod
    async def dispatch(
        cls,
        *,
        db: AsyncSession,
        event: WebhookEvent,
        webhook_secret: str,
    ) -> None:
        """
        Attempts to deliver a webhook event.
        """
        signature = cls._sign_payload(
            event.payload,
            webhook_secret,
        )

        async with httpx.AsyncClient(timeout=5) as client:
            try:
                response = await client.post(
                    event.target_url,
                    content=event.payload,
                    headers={
                        "Content-Type": "application/json",
                        settings.WEBHOOK_SIGNATURE_HEADER: signature,
                    },
                )

                event.attempt_count += 1
                event.last_status_code = response.status_code
                event.delivered = response.status_code < 300
                event.last_attempt_at = time.time()

                logger.info(
                    "webhook_dispatched",
                    extra={
                        "event_id": str(event.id),
                        "status_code": response.status_code,
                        "delivered": event.delivered,
                    },
                )

            except Exception as exc:
                event.attempt_count += 1
                event.delivered = False
                event.last_status_code = None
                event.last_attempt_at = time.time()

                logger.warning(
                    "webhook_dispatch_failed",
                    extra={
                        "event_id": str(event.id),
                        "error": str(exc),
                    },
                )

        db.add(event)
