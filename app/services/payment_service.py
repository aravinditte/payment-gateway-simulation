"""Payment service for payment operations."""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PaymentStatus, SimulationType, WebhookEventType
from app.db.models import APIKey, IdempotencyKey, Merchant, Payment, Refund
from app.repositories.idempotency_repository import IdempotencyKeyRepository
from app.repositories.payment_repository import PaymentRepository
from app.services.exceptions import ConflictError, NotFoundError, ValidationError
from app.services.webhook_service import WebhookService


class PaymentService:
    """Service for payment operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: Database session
        """
        self.payment_repo = PaymentRepository(session)
        self.idempotency_repo = IdempotencyKeyRepository(session)
        self.webhook_service = WebhookService(session)
        self.session = session

    async def create_payment(
        self,
        merchant: Merchant,
        amount: int,
        currency: str = "INR",
        description: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        metadata: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
        simulate: Optional[str] = None,
    ) -> tuple[Payment, dict]:
        """Create payment.

        Args:
            merchant: Merchant
            amount: Amount in paise/cents
            currency: Currency code
            description: Payment description
            customer_email: Customer email
            customer_phone: Customer phone
            metadata: Custom metadata
            idempotency_key: Idempotency key
            simulate: Simulation type

        Returns:
            tuple[Payment, dict]: (payment, response_data)

        Raises:
            ValidationError: If validation fails
        """
        # Check idempotency
        if idempotency_key:
            existing_key = await self.idempotency_repo.get_by_key(idempotency_key)
            if existing_key:
                return await self.payment_repo.get_by_id(existing_key.payment_id), existing_key.response_data  # type: ignore

        # Validate amount
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")

        # Create payment
        payment = await self.payment_repo.create(
            id=str(uuid.uuid4()),
            merchant_id=merchant.id,
            amount=amount,
            currency=currency,
            description=description,
            customer_email=customer_email,
            customer_phone=customer_phone,
            metadata=metadata or {},
            status=PaymentStatus.CREATED,
        )

        # Simulate payment if requested
        response_data = {"id": payment.id, "status": payment.status}

        if simulate:
            payment, event_type = await self._simulate_payment(
                payment, SimulationType(simulate)
            )
            response_data["simulated"] = True
            response_data["simulation_type"] = simulate
        else:
            # Auto-authorize and capture for successful payments
            payment.status = PaymentStatus.AUTHORIZED
            payment.authorized_at = datetime.utcnow()
            payment.status = PaymentStatus.CAPTURED
            payment.captured_at = datetime.utcnow()
            event_type = WebhookEventType.PAYMENT_SUCCEEDED

        await self.payment_repo.update(payment, status=payment.status)
        await self.payment_repo.commit()

        # Create idempotency key
        if idempotency_key:
            await self.idempotency_repo.create(
                id=str(uuid.uuid4()),
                idempotency_key=idempotency_key,
                merchant_id=merchant.id,
                payment_id=payment.id,
                response_data=response_data,
                expires_at=datetime.utcnow() + timedelta(hours=24),
            )
            await self.idempotency_repo.commit()

        # Create webhook event
        await self.webhook_service.create_event(
            payment_id=payment.id,
            merchant_id=merchant.id,
            event_type=event_type,
            payment=payment,
        )

        response_data["status"] = payment.status
        response_data["created_at"] = payment.created_at.isoformat()
        return payment, response_data

    async def get_payment(self, merchant_id: str, payment_id: str) -> Payment:
        """Get payment.

        Args:
            merchant_id: Merchant ID
            payment_id: Payment ID

        Returns:
            Payment: Payment

        Raises:
            NotFoundError: If payment not found
        """
        payment = await self.payment_repo.get_by_merchant_and_payment_id(
            merchant_id, payment_id
        )
        if not payment:
            raise NotFoundError(f"Payment {payment_id} not found")
        return payment

    async def capture_payment(self, merchant_id: str, payment_id: str) -> Payment:
        """Capture payment.

        Args:
            merchant_id: Merchant ID
            payment_id: Payment ID

        Returns:
            Payment: Captured payment

        Raises:
            NotFoundError: If payment not found
            ConflictError: If payment status is invalid
        """
        payment = await self.get_payment(merchant_id, payment_id)

        if payment.status != PaymentStatus.AUTHORIZED:
            raise ConflictError(
                f"Cannot capture payment in {payment.status} state. Expected: AUTHORIZED"
            )

        payment.status = PaymentStatus.CAPTURED
        payment.captured_at = datetime.utcnow()
        await self.payment_repo.update(payment, status=payment.status, captured_at=payment.captured_at)
        await self.payment_repo.commit()

        # Create webhook event
        await self.webhook_service.create_event(
            payment_id=payment.id,
            merchant_id=merchant_id,
            event_type=WebhookEventType.PAYMENT_SUCCEEDED,
            payment=payment,
        )

        return payment

    async def refund_payment(
        self, merchant_id: str, payment_id: str, amount: Optional[int] = None, reason: Optional[str] = None
    ) -> Refund:
        """Refund payment.

        Args:
            merchant_id: Merchant ID
            payment_id: Payment ID
            amount: Amount to refund (None = full amount)
            reason: Refund reason

        Returns:
            Refund: Refund record

        Raises:
            NotFoundError: If payment not found
            ConflictError: If payment cannot be refunded
        """
        payment = await self.get_payment(merchant_id, payment_id)

        if payment.status != PaymentStatus.CAPTURED:
            raise ConflictError(
                f"Cannot refund payment in {payment.status} state. Expected: CAPTURED"
            )

        refund_amount = amount or payment.amount

        if refund_amount > payment.amount:
            raise ValidationError(f"Refund amount cannot exceed payment amount")

        # Create refund record
        refund = Refund(
            id=str(uuid.uuid4()),
            payment_id=payment.id,
            amount=refund_amount,
            reason=reason,
            status="COMPLETED",
        )
        self.session.add(refund)

        # Update payment status
        if refund_amount == payment.amount:
            payment.status = PaymentStatus.REFUNDED
            await self.payment_repo.update(payment, status=payment.status)

        await self.session.flush()
        await self.session.commit()

        # Create webhook event
        await self.webhook_service.create_event(
            payment_id=payment.id,
            merchant_id=merchant_id,
            event_type=WebhookEventType.PAYMENT_REFUNDED,
            payment=payment,
        )

        return refund

    async def _simulate_payment(
        self, payment: Payment, simulation: SimulationType
    ) -> tuple[Payment, WebhookEventType]:
        """Simulate payment with various scenarios.

        Args:
            payment: Payment to simulate
            simulation: Simulation type

        Returns:
            tuple[Payment, WebhookEventType]: (updated_payment, event_type)
        """
        if simulation == SimulationType.SUCCESS:
            payment.status = PaymentStatus.AUTHORIZED
            payment.authorized_at = datetime.utcnow()
            payment.status = PaymentStatus.CAPTURED
            payment.captured_at = datetime.utcnow()
            return payment, WebhookEventType.PAYMENT_SUCCEEDED

        elif simulation == SimulationType.INSUFFICIENT_FUNDS:
            payment.status = PaymentStatus.FAILED
            payment.error_code = "INSUFFICIENT_FUNDS"
            payment.error_message = "Insufficient funds in account"
            return payment, WebhookEventType.PAYMENT_FAILED

        elif simulation == SimulationType.NETWORK_TIMEOUT:
            payment.status = PaymentStatus.FAILED
            payment.error_code = "NETWORK_TIMEOUT"
            payment.error_message = "Payment gateway timeout"
            return payment, WebhookEventType.PAYMENT_FAILED

        elif simulation == SimulationType.FRAUD_DETECTED:
            payment.status = PaymentStatus.FAILED
            payment.error_code = "FRAUD_DETECTED"
            payment.error_message = "Transaction flagged as fraudulent"
            return payment, WebhookEventType.PAYMENT_FAILED

        elif simulation == SimulationType.BANK_ERROR:
            payment.status = PaymentStatus.FAILED
            payment.error_code = "BANK_ERROR"
            payment.error_message = "Bank rejected the transaction"
            return payment, WebhookEventType.PAYMENT_FAILED

        return payment, WebhookEventType.PAYMENT_CREATED
