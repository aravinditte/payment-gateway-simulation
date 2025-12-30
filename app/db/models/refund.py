import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Refund(Base):
    """
    Represents a refund issued against a captured payment.
    """

    # -------------------------------------------------
    # Primary Key
    # -------------------------------------------------
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # -------------------------------------------------
    # Relationships
    # -------------------------------------------------
    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    payment = relationship(
        "Payment",
        backref="refunds",
        lazy="joined",
    )

    merchant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # -------------------------------------------------
    # Refund Details
    # -------------------------------------------------
    amount = Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        comment="Refund amount",
    )

    currency = Column(
        String(3),
        nullable=False,
        comment="ISO 4217 currency code",
    )

    reason = Column(
        String(255),
        nullable=True,
        comment="Refund reason (optional)",
    )

    status = Column(
        String(32),
        nullable=False,
        comment="Refund status (processed, failed)",
    )

    # -------------------------------------------------
    # Idempotency
    # -------------------------------------------------
    idempotency_key = Column(
        String(255),
        nullable=False,
        comment="Idempotency key for refund requests",
    )

    # -------------------------------------------------
    # Audit Fields
    # -------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )


# -------------------------------------------------
# Indexes & Constraints
# -------------------------------------------------
Index(
    "uq_refunds_payment_id_idempotency_key",
    Refund.payment_id,
    Refund.idempotency_key,
    unique=True,
)

Index(
    "idx_refunds_merchant_created_at",
    Refund.merchant_id,
    Refund.created_at,
)
