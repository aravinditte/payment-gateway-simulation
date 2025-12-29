"""Tests for payment service."""

import pytest
import uuid
from datetime import datetime

from app.core.enums import PaymentStatus
from app.db.models import Merchant, Payment
from app.services.payment_service import PaymentService
from app.services.exceptions import ValidationError, ConflictError


@pytest.mark.asyncio
async def test_create_payment_success(test_db, test_merchant):
    """Test successful payment creation."""
    async with test_db() as session:
        service = PaymentService(session)
        merchant = test_merchant["merchant"]

        payment, response = await service.create_payment(
            merchant=merchant,
            amount=10000,
            currency="INR",
            description="Test payment",
            customer_email="customer@test.com",
        )

        assert payment.id
        assert payment.amount == 10000
        assert payment.currency == "INR"
        assert payment.status == PaymentStatus.CAPTURED
        assert payment.merchant_id == merchant.id
        assert response["status"] == PaymentStatus.CAPTURED


@pytest.mark.asyncio
async def test_create_payment_invalid_amount(test_db, test_merchant):
    """Test payment creation with invalid amount."""
    async with test_db() as session:
        service = PaymentService(session)
        merchant = test_merchant["merchant"]

        with pytest.raises(ValidationError):
            await service.create_payment(
                merchant=merchant,
                amount=-100,
            )


@pytest.mark.asyncio
async def test_create_payment_idempotency(test_db, test_merchant):
    """Test idempotent payment creation."""
    async with test_db() as session:
        service = PaymentService(session)
        merchant = test_merchant["merchant"]
        idempotency_key = str(uuid.uuid4())

        payment1, _ = await service.create_payment(
            merchant=merchant,
            amount=10000,
            idempotency_key=idempotency_key,
        )

        payment2, _ = await service.create_payment(
            merchant=merchant,
            amount=10000,
            idempotency_key=idempotency_key,
        )

        assert payment1.id == payment2.id


@pytest.mark.asyncio
async def test_get_payment_success(test_db, test_merchant):
    """Test getting payment."""
    async with test_db() as session:
        service = PaymentService(session)
        merchant = test_merchant["merchant"]

        payment, _ = await service.create_payment(
            merchant=merchant,
            amount=10000,
        )

        fetched_payment = await service.get_payment(
            merchant_id=merchant.id,
            payment_id=payment.id,
        )

        assert fetched_payment.id == payment.id


@pytest.mark.asyncio
async def test_get_payment_not_found(test_db, test_merchant):
    """Test getting non-existent payment."""
    async with test_db() as session:
        service = PaymentService(session)
        merchant = test_merchant["merchant"]

        with pytest.raises(Exception):
            await service.get_payment(
                merchant_id=merchant.id,
                payment_id="nonexistent",
            )


@pytest.mark.asyncio
async def test_refund_payment_success(test_db, test_merchant):
    """Test successful refund."""
    async with test_db() as session:
        service = PaymentService(session)
        merchant = test_merchant["merchant"]

        payment, _ = await service.create_payment(
            merchant=merchant,
            amount=10000,
        )

        refund = await service.refund_payment(
            merchant_id=merchant.id,
            payment_id=payment.id,
            amount=5000,
            reason="Customer requested",
        )

        assert refund.amount == 5000
        assert refund.payment_id == payment.id


@pytest.mark.asyncio
async def test_refund_payment_exceeds_amount(test_db, test_merchant):
    """Test refund with amount exceeding payment."""
    async with test_db() as session:
        service = PaymentService(session)
        merchant = test_merchant["merchant"]

        payment, _ = await service.create_payment(
            merchant=merchant,
            amount=10000,
        )

        with pytest.raises(ValidationError):
            await service.refund_payment(
                merchant_id=merchant.id,
                payment_id=payment.id,
                amount=20000,
            )
