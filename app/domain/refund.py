from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from app.domain.enums import RefundStatus


@dataclass
class RefundDomain:
    """
    Pure refund domain object.
    """

    id: UUID
    payment_id: UUID
    merchant_id: UUID
    amount: Decimal
    currency: str
    status: RefundStatus
    created_at: datetime | None = None

    def mark_failed(self) -> None:
        self.status = RefundStatus.FAILED

    def mark_processed(self) -> None:
        self.status = RefundStatus.PROCESSED
