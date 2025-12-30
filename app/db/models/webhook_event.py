import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class WebhookEvent(Base):
    """
    Represents a webhook delivery attempt.
    Used for retries, auditing, and observability.
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
    merchant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # -------------------------------------------------
    # Webhook Metadata
    # -------------------------------------------------
    event_type = Column(
        String(64),
        nullable=False,
        comment="Event name (payment.succeeded, payment.failed, etc.)",
    )

    payload = Column(
        String,
        nullable=False,
        comment="JSON payload sent to merchant",
    )

    target_url = Column(
        String(2048),
        nullable=False,
        comment="Webhook destination URL",
    )

    # -------------------------------------------------
    # Delivery State
    # -------------------------------------------------
    attempt_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of delivery attempts",
    )

    last_status_code = Column(
        Integer,
        nullable=True,
        comment="Last HTTP response code",
    )

    delivered = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether webhook was successfully delivered",
    )

    # -------------------------------------------------
    # Audit Fields
    # -------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    last_attempt_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )


# -------------------------------------------------
# Indexes
# -------------------------------------------------
Index(
    "idx_webhook_events_delivery_state",
    WebhookEvent.delivered,
    WebhookEvent.attempt_count,
)
