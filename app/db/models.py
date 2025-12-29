"""SQLAlchemy ORM models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    String,
    Text,
    DateTime,
    Numeric,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentStatus, WebhookEventType, WebhookStatus
from app.db.base import Base


class Merchant(Base):
    """Merchant entity for payment gateway users."""

    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    webhook_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    api_keys: Mapped[list["APIKey"]] = relationship(
        "APIKey", back_populates="merchant", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="merchant", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_merchant_email", "email"),)


class APIKey(Base):
    """API key for merchant authentication."""

    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"))
    api_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    api_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="api_keys")

    __table_args__ = (
        Index("idx_api_key_merchant", "merchant_id"),
        Index("idx_api_key_key", "api_key"),
        UniqueConstraint("merchant_id", "api_key", name="uq_merchant_api_key"),
    )


class Payment(Base):
    """Payment record."""

    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"))
    amount: Mapped[int] = mapped_column(nullable=False)  # Amount in paise/cents
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[PaymentStatus] = mapped_column(
        String(50), default=PaymentStatus.CREATED, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    authorized_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="payments")
    refunds: Mapped[list["Refund"]] = relationship(
        "Refund", back_populates="payment", cascade="all, delete-orphan"
    )
    webhook_events: Mapped[list["WebhookEvent"]] = relationship(
        "WebhookEvent", back_populates="payment", cascade="all, delete-orphan"
    )
    idempotency_key: Mapped[Optional["IdempotencyKey"]] = relationship(
        "IdempotencyKey", back_populates="payment", uselist=False
    )

    __table_args__ = (
        Index("idx_payment_merchant", "merchant_id"),
        Index("idx_payment_status", "status"),
        Index("idx_payment_created", "created_at"),
    )


class Refund(Base):
    """Refund record."""

    __tablename__ = "refunds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payment_id: Mapped[str] = mapped_column(String(36), ForeignKey("payments.id"))
    amount: Mapped[int] = mapped_column(nullable=False)  # Amount in paise/cents
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    payment: Mapped["Payment"] = relationship("Payment", back_populates="refunds")

    __table_args__ = (
        Index("idx_refund_payment", "payment_id"),
        Index("idx_refund_created", "created_at"),
    )


class WebhookEvent(Base):
    """Webhook event record."""

    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payment_id: Mapped[str] = mapped_column(String(36), ForeignKey("payments.id"))
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"))
    event_type: Mapped[WebhookEventType] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[WebhookStatus] = mapped_column(
        String(50), default=WebhookStatus.PENDING, nullable=False
    )
    delivery_attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    payment: Mapped["Payment"] = relationship("Payment", back_populates="webhook_events")

    __table_args__ = (
        Index("idx_webhook_payment", "payment_id"),
        Index("idx_webhook_merchant", "merchant_id"),
        Index("idx_webhook_status", "status"),
        Index("idx_webhook_next_retry", "next_retry_at"),
    )


class IdempotencyKey(Base):
    """Idempotency key for duplicate request prevention."""

    __tablename__ = "idempotency_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"))
    payment_id: Mapped[str] = mapped_column(String(36), ForeignKey("payments.id"))
    response_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    payment: Mapped["Payment"] = relationship("Payment", back_populates="idempotency_key")

    __table_args__ = (
        Index("idx_idempotency_key", "idempotency_key"),
        Index("idx_idempotency_merchant", "merchant_id"),
        Index("idx_idempotency_expires", "expires_at"),
    )
