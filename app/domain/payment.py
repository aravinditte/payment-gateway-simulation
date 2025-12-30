from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from app.domain.enums import PaymentStatus, SimulationScenario


@dataclass
class PaymentDomain:
    """
    Pure payment domain object.
    Encapsulates payment state transitions.
    """

    id: UUID
    merchant_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    simulation: SimulationScenario | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # -----------------------------------------
    # State Transitions
    # -----------------------------------------
    def authorize(self) -> None:
        if self.status != PaymentStatus.CREATED:
            raise ValueError("Only CREATED payments can be authorized")
        self.status = PaymentStatus.AUTHORIZED

    def capture(self) -> None:
        if self.status != PaymentStatus.AUTHORIZED:
            raise ValueError("Only AUTHORIZED payments can be captured")
        self.status = PaymentStatus.CAPTURED

    def fail(self, reason: str | None = None) -> None:
        if self.status in {PaymentStatus.CAPTURED, PaymentStatus.REFUNDED}:
            raise ValueError("Captured or refunded payments cannot be failed")
        self.status = PaymentStatus.FAILED

    def refund(self) -> None:
        if self.status != PaymentStatus.CAPTURED:
            raise ValueError("Only CAPTURED payments can be refunded")
        self.status = PaymentStatus.REFUNDED
