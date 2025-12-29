"""Domain enumerations."""

from enum import Enum


class PaymentStatus(str, Enum):
    """Payment lifecycle states."""

    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentStatusTransition(str, Enum):
    """Valid payment status transitions."""

    CREATED_TO_AUTHORIZED = "CREATED->AUTHORIZED"
    AUTHORIZED_TO_CAPTURED = "AUTHORIZED->CAPTURED"
    AUTHORIZED_TO_FAILED = "AUTHORIZED->FAILED"
    CREATED_TO_FAILED = "CREATED->FAILED"
    CAPTURED_TO_REFUNDED = "CAPTURED->REFUNDED"


class WebhookEventType(str, Enum):
    """Webhook event types."""

    PAYMENT_CREATED = "payment.created"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"


class WebhookStatus(str, Enum):
    """Webhook delivery status."""

    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class SimulationType(str, Enum):
    """Simulation types for testing various scenarios."""

    SUCCESS = "success"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    NETWORK_TIMEOUT = "network_timeout"
    FRAUD_DETECTED = "fraud_detected"
    BANK_ERROR = "bank_error"
