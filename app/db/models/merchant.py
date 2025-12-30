import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Merchant(Base):
    """
    Represents a merchant (API consumer) using the payment gateway.

    A merchant owns:
    - API keys
    - Webhook configuration
    - Payments and refunds
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
    # Merchant Identity
    # -------------------------------------------------
    name = Column(
        String(255),
        nullable=False,
        comment="Merchant display name",
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Primary contact email",
    )

    # -------------------------------------------------
    # API & Security
    # -------------------------------------------------
    api_key_hash = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Hashed API key for authentication",
    )

    webhook_secret = Column(
        String(255),
        nullable=False,
        comment="Secret used to sign webhook payloads",
    )

    webhook_url = Column(
        String(2048),
        nullable=True,
        comment="Webhook endpoint configured by merchant",
    )

    # -------------------------------------------------
    # Status Flags
    # -------------------------------------------------
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the merchant is active",
    )

    # -------------------------------------------------
    # Audit Fields
    # -------------------------------------------------
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Record creation timestamp",
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update timestamp",
    )


# -------------------------------------------------
# Indexes
# -------------------------------------------------
Index("idx_merchants_api_key_hash", Merchant.api_key_hash)
