import hashlib
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundError,
    PaymentStateError,
    IdempotencyConflictError,
)
from app.db.models.payment import Payment
from app.db.models.idempotency import IdempotencyKey
from app.repositories.payment_repository import PaymentRepository
from app.repositories.idempotency_repository import IdempotencyRepository
from app.services.webhook_service import WebhookService


class PaymentService:
    """
    Handles payment lifecycle and business rules.
    """

    @staticmethod
    def _hash_request(payload: dict) -> str:
        return hashlib.sha256(
            str(sorted(payload.items())).encode("utf-8")
        ).hexdigest()

    @classmethod
    async def create_payment(
        cls,
        *,
        db: AsyncSession,
        merchant,
        request,
        idempotency_key: str,
    ) -> Payment:
        # -------------------------------------------------
        # Idempotency check
        # -------------------------------------------------
        existing = await PaymentRepository.get_by_idempotency_key(
            db, merchant.id, idempotency_key
        )
        if existing:
            return existing

        payload_hash = cls._hash_request(request.model_dump())

        idempotency_record = await IdempotencyRepository.get(
            db, merchant.id, idempotency_key
        )
        if idempotency_record:
            if idempotency_record.request_hash != payload_hash:
                raise IdempotencyConflictError(
                    "Idempotency key reused with different payload"
                )

        # -------------------------------------------------
        # Create payment
        # -------------------------------------------------
        payment = Payment(
            merchant_id=merchant.id,
            amount=Decimal(request.amount),
            currency=request.currency,
            status="CREATED",
            idempotency_key=idempotency_key,
            external_reference=request.external_reference,
            simulation_scenario=request.simulation,
        )

        await PaymentRepository.create(db, payment)

        # Store idempotency record
        await IdempotencyRepository.create(
            db,
            IdempotencyKey(
                merchant_id=merchant.id,
                key=idempotency_key,
                request_hash=payload_hash,
                response_snapshot=str(payment.id),
            ),
        )

        # Emit webhook
        await WebhookService.emit_event(
            db=db,
            merchant=merchant,
            event_type="payment.created",
            payload={
                "payment_id": str(payment.id),
                "status": payment.status,
            },
        )

        return payment

    @classmethod
    async def get_payment(
        cls,
        *,
        db: AsyncSession,
        merchant,
        payment_id: str,
    ) -> Payment:
        payment = await PaymentRepository.get_by_id(
            db, payment_id, merchant.id
        )
        if not payment:
            raise NotFoundError("Payment not found")
        return payment

    @classmethod
    async def capture_payment(
        cls,
        *,
        db: AsyncSession,
        merchant,
        payment_id: str,
    ) -> Payment:
        payment = await cls.get_payment(
            db=db, merchant=merchant, payment_id=payment_id
        )

        if payment.status != "AUTHORIZED":
            raise PaymentStateError(
                "Only authorized payments can be captured"
            )

        payment.status = "CAPTURED"
        payment.updated_at = datetime.utcnow()

        await WebhookService.emit_event(
            db=db,
            merchant=merchant,
            event_type="payment.succeeded",
            payload={
                "payment_id": str(payment.id),
                "status": payment.status,
            },
        )

        return payment
