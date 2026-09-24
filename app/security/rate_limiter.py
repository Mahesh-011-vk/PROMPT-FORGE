"""
PromptForge AI - In-Memory Token Bucket Rate Limiter.

Protects API endpoints against denial-of-service and brute force abuse.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass

from app.config.settings import settings


@dataclass
class TokenBucket:
    """Token bucket state for a single client."""

    capacity: float
    refill_rate: float  # tokens per second
    tokens: float
    last_update: float


class RateLimiter:
    """Sliding token bucket rate limiter for client requests."""

    def __init__(self, requests_per_minute: int | None = None):
        self.rpm = requests_per_minute or settings.RATE_LIMITS.USER
        self.refill_rate = self.rpm / 60.0
        self.buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=float(self.rpm),
                refill_rate=self.refill_rate,
                tokens=float(self.rpm),
                last_update=time.monotonic(),
            )
        )

    def is_allowed(self, client_id: str, cost: float = 1.0) -> tuple[bool, int]:
        """Check if client is permitted to make a request.

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.monotonic()
        bucket = self.buckets[client_id]

        # Calculate refilled tokens since last access
        elapsed = now - bucket.last_update
        bucket.last_update = now
        bucket.tokens = min(bucket.capacity, bucket.tokens + elapsed * bucket.refill_rate)

        if bucket.tokens >= cost:
            bucket.tokens -= cost
            return True, 0

        # Calculate time needed to replenish required tokens
        missing = cost - bucket.tokens
        retry_after = int(missing / bucket.refill_rate) + 1
        return False, max(1, retry_after)


rate_limiter = RateLimiter()
