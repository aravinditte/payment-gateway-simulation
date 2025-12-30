import pytest
from decimal import Decimal

from app.services.merchant_service import MerchantService
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreateRequest


@pytest.mark.asyncio
async def test_full_payment_creation_flow(db_session):
    merchant, api_key = await MerchantService.create_merchant(
        db=db_session,
        name="Test Merchant",
        email="merchant@test.com",
    )

    request = PaymentCreateRequest(
        amount=Decimal("500.00"),
        currency="JPY",
        simulation="success",
    )

    payment = await PaymentService.create_payment(
        db=db_session,
        merchant=merchant,
        request=request,
        idempotency_key="idem-key-1",
    )

    assert payment.amount == Decimal("500.00")
    assert payment.currency == "JPY"
    assert payment.status == "CREATED"


@pytest.mark.asyncio
async def test_payment_idempotency(db_session):
    merchant, _ = await MerchantService.create_merchant(
        db=db_session,
        name="Idem Merchant",
        email="idem@test.com",
    )

    request = PaymentCreateRequest(
        amount=Decimal("1000.00"),
        currency="JPY",
    )

    p1 = await PaymentService.create_payment(
        db=db_session,
        merchant=merchant,
        request=request,
        idempotency_key="idem-123",
    )

    p2 = await PaymentService.create_payment(
        db=db_session,
        merchant=merchant,
        request=request,
        idempotency_key="idem-123",
    )

    assert p1.id == p2.id
