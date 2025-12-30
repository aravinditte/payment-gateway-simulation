from enum import Enum


class PaymentStatus(str, Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class RefundStatus(str, Enum):
    PROCESSED = "processed"
    FAILED = "failed"


class SimulationScenario(str, Enum):
    SUCCESS = "success"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    NETWORK_TIMEOUT = "network_timeout"
    FRAUD_DETECTED = "fraud_detected"
    BANK_ERROR = "bank_error"


class WebhookEventType(str, Enum):
    PAYMENT_CREATED = "payment.created"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"
