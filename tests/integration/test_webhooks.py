import pytest
from decimal import Decimal

from app.services.merchant_service import MerchantService
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreateRequest
from app.db.models.webhook_event import WebhookEvent
from sqlalchemy import select


@pytest.mark.asyncio
async def test_webhook_event_created(db_session):
    merchant, _ = await MerchantService.create_merchant(
        db=db_session,
        name="Webhook Merchant",
        email="webhook@test.com",
        webhook_url="https://example.com/webhook",
    )

    request = PaymentCreateRequest(
        amount=Decimal("300.00"),
        currency="JPY",
    )

    await PaymentService.create_payment(
        db=db_session,
        merchant=merchant,
        request=request,
        idempotency_key="wh-1",
    )

    stmt = select(WebhookEvent).where(
        WebhookEvent.merchant_id == merchant.id
    )
    result = await db_session.execute(stmt)
    events = result.scalars().all()

    assert len(events) == 1
    assert events[0].event_type == "payment.created"
