import json
import httpx
import time
import hmac
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.webhook_event import WebhookEvent

settings = get_settings()


class WebhookService:
    """
    Responsible for emitting webhook events.
    """

    @staticmethod
    def _sign_payload(payload: str, secret: str) -> str:
        timestamp = int(time.time())
        signed = f"{timestamp}.{payload}".encode("utf-8")
        signature = hmac.new(
            secret.encode("utf-8"),
            signed,
            hashlib.sha256,
        ).hexdigest()
        return f"t={timestamp},v1={signature}"

    @classmethod
    async def emit_event(
        cls,
        *,
        db: AsyncSession,
        merchant,
        event_type: str,
        payload: dict,
    ) -> None:
        if not merchant.webhook_url:
            return

        body = json.dumps(
            {
                "type": event_type,
                "data": payload,
            }
        )

        signature = cls._sign_payload(body, merchant.webhook_secret)

        event = WebhookEvent(
            merchant_id=merchant.id,
            event_type=event_type,
            payload=body,
            target_url=merchant.webhook_url,
            attempt_count=1,
        )
        db.add(event)

        async with httpx.AsyncClient(timeout=5) as client:
            try:
                response = await client.post(
                    merchant.webhook_url,
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        settings.WEBHOOK_SIGNATURE_HEADER: signature,
                    },
                )
                event.last_status_code = response.status_code
                event.delivered = response.status_code < 300
            except Exception:
                event.last_status_code = None
                event.delivered = False
