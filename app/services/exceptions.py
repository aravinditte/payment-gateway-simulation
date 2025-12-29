"""Custom exceptions for service layer."""


class PaymentGatewayException(Exception):
    """Base exception for payment gateway."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        """Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(PaymentGatewayException):
    """Authentication error."""

    def __init__(self, message: str = "Invalid API key") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=401)


class ValidationError(PaymentGatewayException):
    """Validation error."""

    def __init__(self, message: str = "Validation failed") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=400)


class NotFoundError(PaymentGatewayException):
    """Resource not found error."""

    def __init__(self, message: str = "Resource not found") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=404)


class ConflictError(PaymentGatewayException):
    """Conflict error (e.g., invalid state transition)."""

    def __init__(self, message: str = "Conflict") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=409)


class PaymentError(PaymentGatewayException):
    """Payment processing error."""

    def __init__(self, message: str = "Payment processing failed") -> None:
        """Initialize exception.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=402)
