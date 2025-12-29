"""Security utilities for signature verification and key management."""

import hashlib
import hmac
import secrets
from typing import Tuple


def generate_api_key() -> Tuple[str, str]:
    """Generate a random API key for merchant authentication.

    Returns:
        Tuple[str, str]: (api_key, api_secret) - both needed for signing requests
    """
    api_key = f"pk_{secrets.token_urlsafe(32)}"
    api_secret = secrets.token_urlsafe(64)
    return api_key, api_secret


def generate_webhook_secret() -> str:
    """Generate a webhook signing secret.

    Returns:
        str: Webhook secret for HMAC signature verification
    """
    return secrets.token_urlsafe(64)


def sign_payload(payload: str, secret: str) -> str:
    """Generate HMAC SHA-256 signature for payload.

    Args:
        payload: JSON string or request body to sign
        secret: Secret key for signing

    Returns:
        str: Hex-encoded HMAC SHA-256 signature
    """
    signature = hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return signature


def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify HMAC SHA-256 signature.

    Args:
        payload: Original payload as string
        signature: Signature to verify
        secret: Secret key used for signing

    Returns:
        bool: True if signature is valid, False otherwise
    """
    expected_signature = sign_payload(payload, secret)
    return hmac.compare_digest(signature, expected_signature)
