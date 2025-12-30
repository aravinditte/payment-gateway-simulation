import pytest
from decimal import Decimal
from uuid import uuid4

from app.domain.payment import PaymentDomain
from app.domain.enums import PaymentStatus


def test_payment_valid_state_transitions():
    payment = PaymentDomain(
        id=uuid4(),
        merchant_id=uuid4(),
        amount=Decimal("100.00"),
        currency="JPY",
        status=PaymentStatus.CREATED,
    )

    payment.authorize()
    assert payment.status == PaymentStatus.AUTHORIZED

    payment.capture()
    assert payment.status == PaymentStatus.CAPTURED


def test_invalid_capture_raises_error():
    payment = PaymentDomain(
        id=uuid4(),
        merchant_id=uuid4(),
        amount=Decimal("100.00"),
        currency="JPY",
        status=PaymentStatus.CREATED,
    )

    with pytest.raises(ValueError):
        payment.capture()
