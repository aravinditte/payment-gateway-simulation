import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class IdempotencyKey(Base):
    """
    Tracks idempotency keys to guarantee request safety.

    Used for:
    - Payments
    - Refunds
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
    # Ownership
    # -------------------------------------------------
    merchant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    key = Column(
        String(255),
        nullable=False,
        comment="Idempotency key provided by client",
    )

    request_hash = Column(
        String(255),
        nullable=False,
        comment="Hash of request payload for consistency validation",
    )

    response_snapshot = Column(
        String,
        nullable=True,
        comment="Stored response for replay",
    )

    # -------------------------------------------------
    # Audit
    # -------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )


# -------------------------------------------------
# Constraints
# -------------------------------------------------
Index(
    "uq_idempotency_merchant_key",
    IdempotencyKey.merchant_id,
    IdempotencyKey.key,
    unique=True,
)
