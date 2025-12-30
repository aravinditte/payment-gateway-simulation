"""Payment endpoints."""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.dependencies import get_current_merchant
from app.db.engine import get_db
from app.db.models import APIKey, Merchant
from app.schemas.payment import (
    CapturePaymentRequest,
    CreatePaymentRequest,
    PaymentResponse,
    RefundPaymentRequest,
    RefundResponse,
)
from app.services.exceptions import PaymentGatewayException
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    request: CreatePaymentRequest,
    idempotency_key: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_db),
    merchant_data: tuple[Merchant, APIKey] = Depends(get_current_merchant),
) -> PaymentResponse:
    """Create new payment.

    Args:
        request: Create payment request
        idempotency_key: Optional idempotency key
        session: Database session
        merchant_data: Current merchant

    Returns:
        PaymentResponse: Created payment

    Raises:
        HTTPException: If creation fails
    """
    merchant, _ = merchant_data
    service = PaymentService(session)

    try:
        payment, _ = await service.create_payment(
            merchant=merchant,
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            customer_email=request.customer_email,
            customer_phone=request.customer_phone,
            custom_metadata=request.custom_metadata,
            idempotency_key=idempotency_key,
            simulate=request.simulate,
        )
        return PaymentResponse.from_orm(payment)
    except PaymentGatewayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    session: AsyncSession = Depends(get_db),
    merchant_data: tuple[Merchant, APIKey] = Depends(get_current_merchant),
) -> PaymentResponse:
    """Get payment details.

    Args:
        payment_id: Payment ID
        session: Database session
        merchant_data: Current merchant

    Returns:
        PaymentResponse: Payment details

    Raises:
        HTTPException: If payment not found
    """
    merchant, _ = merchant_data
    service = PaymentService(session)

    try:
        payment = await service.get_payment(merchant.id, payment_id)
        return PaymentResponse.from_orm(payment)
    except PaymentGatewayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{payment_id}/capture",
    response_model=PaymentResponse,
)
async def capture_payment(
    payment_id: str,
    request: CapturePaymentRequest,
    session: AsyncSession = Depends(get_db),
    merchant_data: tuple[Merchant, APIKey] = Depends(get_current_merchant),
) -> PaymentResponse:
    """Capture authorized payment.

    Args:
        payment_id: Payment ID
        request: Capture request
        session: Database session
        merchant_data: Current merchant

    Returns:
        PaymentResponse: Captured payment

    Raises:
        HTTPException: If capture fails
    """
    merchant, _ = merchant_data
    service = PaymentService(session)

    try:
        payment = await service.capture_payment(merchant.id, payment_id)
        return PaymentResponse.from_orm(payment)
    except PaymentGatewayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{payment_id}/refund",
    response_model=RefundResponse,
)
async def refund_payment(
    payment_id: str,
    request: RefundPaymentRequest,
    session: AsyncSession = Depends(get_db),
    merchant_data: tuple[Merchant, APIKey] = Depends(get_current_merchant),
) -> RefundResponse:
    """Refund captured payment.

    Args:
        payment_id: Payment ID
        request: Refund request
        session: Database session
        merchant_data: Current merchant

    Returns:
        RefundResponse: Refund details

    Raises:
        HTTPException: If refund fails
    """
    merchant, _ = merchant_data
    service = PaymentService(session)

    try:
        refund = await service.refund_payment(
            merchant.id,
            payment_id,
            amount=request.amount,
            reason=request.reason,
        )
        return RefundResponse.from_orm(refund)
    except PaymentGatewayException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
