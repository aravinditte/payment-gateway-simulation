"""Webhook service for event management and delivery."""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WebhookEventType, WebhookStatus
from app.core.security import sign_payload
from app.db.models import Payment, WebhookEvent
from app.repositories.webhook_event_repository import WebhookEventRepository


class WebhookService:
    """Service for webhook event management."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session
        """
        self.webhook_repo = WebhookEventRepository(session)
        self.session = session

    async def create_event(
        self,
        payment_id: str,
        merchant_id: str,
        event_type: WebhookEventType,
        payment: Payment,
    ) -> WebhookEvent:
        """Create webhook event.

        Args:
            payment_id: Payment ID
            merchant_id: Merchant ID
            event_type: Event type
            payment: Payment object

        Returns:
            WebhookEvent: Created webhook event
        """
        payload = {
            "event": event_type.value,
            "payment": {
                "id": payment.id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "description": payment.description,
                "customer_email": payment.customer_email,
                "metadata": payment.metadata,
                "created_at": payment.created_at.isoformat(),
                "updated_at": payment.updated_at.isoformat(),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        if payment.error_code:
            payload["error"] = {
                "code": payment.error_code,
                "message": payment.error_message,
            }

        webhook_event = await self.webhook_repo.create(
            id=str(uuid.uuid4()),
            payment_id=payment_id,
            merchant_id=merchant_id,
            event_type=event_type,
            payload=payload,
            status=WebhookStatus.PENDING,
        )
        await self.webhook_repo.commit()

        return webhook_event

    async def deliver_webhook(
        self,
        webhook_event: WebhookEvent,
        webhook_url: str,
        webhook_secret: str,
    ) -> bool:
        """Deliver webhook to merchant.

        Args:
            webhook_event: Webhook event
            webhook_url: Merchant webhook URL
            webhook_secret: Secret for signing

        Returns:
            bool: True if delivery successful
        """
        payload_json = json.dumps(webhook_event.payload)
        signature = sign_payload(payload_json, webhook_secret)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-ID": webhook_event.id,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    webhook_url,
                    content=payload_json,
                    headers=headers,
                )
                response.raise_for_status()
                return True
        except Exception as e:
            return False

    async def retry_failed_webhooks(
        self,
        max_retries: int = 5,
        retry_delay: int = 5,
    ) -> None:
        """Retry failed webhook deliveries.

        Args:
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
        """
        # This would be called by a background task
        pass
