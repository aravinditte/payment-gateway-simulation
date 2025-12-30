from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_merchant
from app.db.models.merchant import Merchant
from app.db.session import get_db_session
from app.schemas.refund import RefundCreateRequest
from app.services.refund_service import RefundService

router = APIRouter()


@router.post("")
async def create_refund(
    request: RefundCreateRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Issues a refund for a captured payment.
    """
    return await RefundService.create_refund(
        db=db,
        merchant=merchant,
        request=request,
        idempotency_key=idempotency_key,
    )
