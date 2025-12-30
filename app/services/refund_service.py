from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundError,
    PaymentStateError,
    IdempotencyConflictError,
)
from app.db.models.refund import Refund
from app.db.models.idempotency import IdempotencyKey
from app.repositories.payment_repository import PaymentRepository
from app.repositories.refund_repository import RefundRepository
from app.repositories.idempotency_repository import IdempotencyRepository
from app.services.webhook_service import WebhookService


class RefundService:
    """
    Handles refund business logic.
    """

    @classmethod
    async def create_refund(
        cls,
        *,
        db: AsyncSession,
        merchant,
        request,
        idempotency_key: str,
    ) -> Refund:
        payment = await PaymentRepository.get_by_id(
            db, request.payment_id, merchant.id
        )
        if not payment:
            raise NotFoundError("Payment not found")

        if payment.status != "CAPTURED":
            raise PaymentStateError(
                "Only captured payments can be refunded"
            )

        existing = await RefundRepository.get_by_idempotency_key(
            db, payment.id, idempotency_key
        )
        if existing:
            return existing

        refund = Refund(
            payment_id=payment.id,
            merchant_id=merchant.id,
            amount=Decimal(request.amount),
            currency=payment.currency,
            reason=request.reason,
            status="processed",
            idempotency_key=idempotency_key,
        )

        await RefundRepository.create(db, refund)

        payment.status = "REFUNDED"

        await WebhookService.emit_event(
            db=db,
            merchant=merchant,
            event_type="payment.refunded",
            payload={
                "payment_id": str(payment.id),
                "refund_id": str(refund.id),
            },
        )

        return refund
