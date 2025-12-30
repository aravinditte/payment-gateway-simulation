from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_merchant
from app.core.rate_limiter import rate_limit_dependency
from app.db.models.merchant import Merchant
from app.db.session import get_db_session
from app.schemas.payment import PaymentCreateRequest
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post(
    "",
    dependencies=[Depends(rate_limit_dependency)],
)
async def create_payment(
    request: PaymentCreateRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Creates a new payment.
    """
    payment = await PaymentService.create_payment(
        db=db,
        merchant=merchant,
        request=request,
        idempotency_key=idempotency_key,
    )

    return payment


@router.get("/{payment_id}")
async def get_payment(
    payment_id: str,
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves a payment by ID.
    """
    return await PaymentService.get_payment(
        db=db,
        merchant=merchant,
        payment_id=payment_id,
    )


@router.post("/{payment_id}/capture")
async def capture_payment(
    payment_id: str,
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Captures an authorized payment.
    """
    return await PaymentService.capture_payment(
        db=db,
        merchant=merchant,
        payment_id=payment_id,
    )
