import time
from typing import Dict, Tuple

from fastapi import Depends, Request

from app.core.config import get_settings
from app.core.exceptions import RateLimitExceededError

settings = get_settings()


# -------------------------------------------------
# Fixed Window Rate Limiter (In-Memory)
# -------------------------------------------------
class FixedWindowRateLimiter:
    """
    Simple fixed-window rate limiter.

    Keyed by (api_key, window_start).
    Suitable for local dev, simulators, and single-node services.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        # key -> (count, window_start_timestamp)
        self._store: Dict[str, Tuple[int, int]] = {}

    def _current_window(self) -> int:
        return int(time.time()) // self.window_seconds

    def allow_request(self, key: str) -> None:
        """
        Checks whether a request is allowed.
        Raises RateLimitExceededError if limit is exceeded.
        """
        window = self._current_window()
        store_key = f"{key}:{window}"

        if store_key not in self._store:
            self._store[store_key] = (1, window)
            return

        count, _ = self._store[store_key]

        if count >= self.max_requests:
            raise RateLimitExceededError(
                f"Rate limit exceeded: {self.max_requests} requests per "
                f"{self.window_seconds} seconds"
            )

        self._store[store_key] = (count + 1, window)


# -------------------------------------------------
# Singleton Limiter Instance
# -------------------------------------------------
_rate_limiter = FixedWindowRateLimiter(
    max_requests=settings.RATE_LIMIT_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
)


# -------------------------------------------------
# FastAPI Dependency
# -------------------------------------------------
async def rate_limit_dependency(
    request: Request,
) -> None:
    """
    FastAPI dependency enforcing rate limits per API key.

    Uses API key if available, otherwise falls back to client IP.
    """
    api_key = request.headers.get(settings.API_KEY_HEADER)
    identifier = api_key or request.client.host

    _rate_limiter.allow_request(identifier)
