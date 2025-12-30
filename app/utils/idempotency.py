import hashlib
from typing import Any


def hash_request_payload(payload: Any) -> str:
    """
    Generates a deterministic hash for a request payload.

    Used to verify idempotency key reuse with identical payloads.
    """
    normalized = str(payload)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
