import hmac
import hashlib
import time
from typing import Optional

from fastapi import Header, Depends

from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    WebhookSignatureError,
)

settings = get_settings()


# -------------------------------------------------
# API Key Authentication
# -------------------------------------------------
async def verify_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> str:
    """
    Verifies that an API key is present and valid.

    Actual merchant lookup is performed in the service/repository layer.
    This function only enforces presence and basic format.
    """
    if not x_api_key:
        raise AuthenticationError("Missing API key")

    # Basic sanity check (length / format)
    if len(x_api_key) < 20:
        raise AuthenticationError("Invalid API key format")

    return x_api_key


# -------------------------------------------------
# HMAC Signature Utilities
# -------------------------------------------------
def _compute_hmac_signature(secret: str, payload: bytes) -> str:
    """
    Computes HMAC SHA-256 signature for a given payload.
    """
    return hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()


def _constant_time_compare(val1: str, val2: str) -> bool:
    """
    Prevents timing attacks when comparing signatures.
    """
    return hmac.compare_digest(val1, val2)


# -------------------------------------------------
# Webhook Signature Verification
# -------------------------------------------------
def verify_webhook_signature(
    *,
    payload: bytes,
    signature_header: Optional[str],
    secret: str,
    tolerance_seconds: int = 300,
) -> None:
    """
    Verifies webhook HMAC signature and timestamp tolerance.

    Expected header format:
        t=timestamp,v1=signature
    """
    if not signature_header:
        raise WebhookSignatureError("Missing webhook signature header")

    try:
        parts = dict(
            item.split("=", 1) for item in signature_header.split(",")
        )
        timestamp = int(parts["t"])
        received_signature = parts["v1"]
    except Exception:
        raise WebhookSignatureError("Malformed webhook signature header")

    # Replay attack protection
    current_time = int(time.time())
    if abs(current_time - timestamp) > tolerance_seconds:
        raise WebhookSignatureError("Webhook timestamp outside tolerance window")

    signed_payload = f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8")
    expected_signature = _compute_hmac_signature(secret, signed_payload)

    if not _constant_time_compare(expected_signature, received_signature):
        raise WebhookSignatureError("Invalid webhook signature")


# -------------------------------------------------
# Dependency Helpers
# -------------------------------------------------
def api_key_dependency():
    """
    FastAPI dependency wrapper for API key verification.
    """
    return Depends(verify_api_key)
