import hmac
import hashlib
import time
from typing import Tuple


def generate_hmac_signature(
    *,
    payload: str,
    secret: str,
) -> Tuple[int, str]:
    """
    Generates a timestamped HMAC SHA-256 signature.

    Returns:
        (timestamp, signature)
    """
    timestamp = int(time.time())
    message = f"{timestamp}.{payload}".encode("utf-8")

    signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=message,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return timestamp, signature


def constant_time_compare(a: str, b: str) -> bool:
    """
    Performs constant-time string comparison.
    Prevents timing attacks.
    """
    return hmac.compare_digest(a, b)
