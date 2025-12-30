from typing import Optional


class AppException(Exception):
    """
    Base application exception.

    All domain-level and service-level errors should inherit from this class.
    These exceptions are converted into HTTP responses in main.py.
    """

    def __init__(
        self,
        *,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[dict] = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(message)


# -------------------------------------------------
# Authentication & Authorization
# -------------------------------------------------
class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status_code=401,
            error_code="AUTHENTICATION_FAILED",
            message=message,
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            status_code=403,
            error_code="ACCESS_FORBIDDEN",
            message=message,
        )


# -------------------------------------------------
# Request & Validation Errors
# -------------------------------------------------
class BadRequestError(AppException):
    def __init__(self, message: str = "Invalid request"):
        super().__init__(
            status_code=400,
            error_code="BAD_REQUEST",
            message=message,
        )


class IdempotencyConflictError(AppException):
    def __init__(self, message: str = "Duplicate request"):
        super().__init__(
            status_code=409,
            error_code="IDEMPOTENCY_CONFLICT",
            message=message,
        )


# -------------------------------------------------
# Resource Errors
# -------------------------------------------------
class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            status_code=404,
            error_code="NOT_FOUND",
            message=message,
        )


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            status_code=409,
            error_code="CONFLICT",
            message=message,
        )


# -------------------------------------------------
# Payment Domain Errors
# -------------------------------------------------
class PaymentStateError(AppException):
    def __init__(self, message: str = "Invalid payment state transition"):
        super().__init__(
            status_code=422,
            error_code="INVALID_PAYMENT_STATE",
            message=message,
        )


class PaymentFailedError(AppException):
    def __init__(self, message: str = "Payment failed"):
        super().__init__(
            status_code=402,
            error_code="PAYMENT_FAILED",
            message=message,
        )


# -------------------------------------------------
# Webhook Errors
# -------------------------------------------------
class WebhookSignatureError(AppException):
    def __init__(self, message: str = "Invalid webhook signature"):
        super().__init__(
            status_code=400,
            error_code="INVALID_WEBHOOK_SIGNATURE",
            message=message,
        )


class WebhookDeliveryError(AppException):
    def __init__(self, message: str = "Webhook delivery failed"):
        super().__init__(
            status_code=502,
            error_code="WEBHOOK_DELIVERY_FAILED",
            message=message,
        )


# -------------------------------------------------
# System Errors
# -------------------------------------------------
class RateLimitExceededError(AppException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            message=message,
        )
