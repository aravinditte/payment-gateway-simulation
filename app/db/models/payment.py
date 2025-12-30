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


class Payment(Base):
    """
    Represents a payment transaction initiated by a merchant.

    This model tracks the full lifecycle of a payment:
    CREATED → AUTHORIZED → CAPTURED → FAILED / REFUNDED
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
    # Merchant Relationship
    # -------------------------------------------------
    merchant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    merchant = relationship(
        "Merchant",
        backref="payments",
        lazy="joined",
    )

    # -------------------------------------------------
    # Payment Identity
    # -------------------------------------------------
    external_reference = Column(
        String(255),
        nullable=True,
        comment="Client-side reference ID (optional)",
    )

    idempotency_key = Column(
        String(255),
        nullable=False,
        comment="Idempotency key used for safe retries",
    )

    # -------------------------------------------------
    # Amount & Currency
    # -------------------------------------------------
    amount = Column(
        Numeric(precision=18, scale=2),
        nullable=False,
        comment="Payment amount in smallest currency unit",
    )

    currency = Column(
        String(3),
        nullable=False,
        comment="ISO 4217 currency code",
    )

    # -------------------------------------------------
    # Payment State
    # -------------------------------------------------
    status = Column(
        String(32),
        nullable=False,
        index=True,
        comment="Current payment status",
    )

    failure_code = Column(
        String(64),
        nullable=True,
        comment="Failure reason code (if failed)",
    )

    failure_message = Column(
        String(255),
        nullable=True,
        comment="Human-readable failure message",
    )

    # -------------------------------------------------
    # Simulation Controls
    # -------------------------------------------------
    simulation_scenario = Column(
        String(64),
        nullable=True,
        comment="Simulation scenario (success, timeout, fraud, etc.)",
    )

    # -------------------------------------------------
    # Audit Fields
    # -------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Payment creation timestamp",
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last status update timestamp",
    )


# -------------------------------------------------
# Indexes & Constraints
# -------------------------------------------------
Index(
    "uq_payments_merchant_id_idempotency_key",
    Payment.merchant_id,
    Payment.idempotency_key,
    unique=True,
)

Index(
    "idx_payments_merchant_status",
    Payment.merchant_id,
    Payment.status,
)
