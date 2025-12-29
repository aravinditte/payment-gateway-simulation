"""Rate limiting service."""

from datetime import datetime, timedelta
from typing import Optional


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float) -> None:
        """Initialize rate limiter.

        Args:
            capacity: Maximum tokens
            refill_rate: Tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = datetime.utcnow()

    def _refill(self) -> None:
        """Refill tokens based on time elapsed."""
        now = datetime.utcnow()
        time_passed = (now - self.last_refill).total_seconds()
        self.tokens = min(
            self.capacity,
            self.tokens + time_passed * self.refill_rate,
        )
        self.last_refill = now

    def allow(self, tokens: int = 1) -> bool:
        """Check if request should be allowed.

        Args:
            tokens: Number of tokens to consume

        Returns:
            bool: True if allowed, False if rate limit exceeded
        """
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
