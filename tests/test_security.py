"""Tests for security utilities."""

from app.core.security import (
    generate_api_key,
    generate_webhook_secret,
    sign_payload,
    verify_signature,
)


def test_generate_api_key():
    """Test API key generation."""
    api_key, api_secret = generate_api_key()

    assert api_key.startswith("pk_")
    assert len(api_key) > 10
    assert len(api_secret) > 10


def test_generate_webhook_secret():
    """Test webhook secret generation."""
    secret = generate_webhook_secret()

    assert len(secret) > 10
    assert isinstance(secret, str)


def test_sign_payload():
    """Test payload signing."""
    payload = '{"id": "123", "amount": 10000}'
    secret = "test-secret"

    signature = sign_payload(payload, secret)

    assert len(signature) == 64  # SHA-256 hex is 64 chars
    assert isinstance(signature, str)


def test_verify_signature_success():
    """Test successful signature verification."""
    payload = '{"id": "123", "amount": 10000}'
    secret = "test-secret"

    signature = sign_payload(payload, secret)
    is_valid = verify_signature(payload, signature, secret)

    assert is_valid is True


def test_verify_signature_failure():
    """Test signature verification failure."""
    payload = '{"id": "123", "amount": 10000}'
    secret = "test-secret"

    signature = sign_payload(payload, secret)
    is_valid = verify_signature(payload, "invalid-signature", secret)

    assert is_valid is False
