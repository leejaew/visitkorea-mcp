"""
Async token bucket rate limiter for the VisitKorea MCP server.

Limits real upstream HTTP calls to data.go.kr to 10 per minute with a
burst capacity of 5. Cached responses bypass the limiter entirely — only
calls that actually hit the network consume a token.

Usage:
    from utils.rate_limiter import limiter
    await limiter.acquire()  # blocks until a token is available
"""
from __future__ import annotations

import asyncio
import time


class TokenBucket:
    """
    Async token bucket.

    Tokens refill at *rate* tokens/second up to *capacity*.
    Calling acquire() waits until a token is available, then consumes one.
    """

    def __init__(self, rate: float, capacity: float) -> None:
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock: asyncio.Lock | None = None

    def _get_lock(self) -> asyncio.Lock:
        # Lazily created so the object is safe to construct at module level
        # before any asyncio event loop is running.
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def acquire(self) -> None:
        async with self._get_lock():
            now = time.monotonic()
            self._tokens = min(
                self._capacity,
                self._tokens + (now - self._last) * self._rate,
            )
            self._last = now
            if self._tokens < 1:
                wait = (1.0 - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0


# Shared instance: 10 tokens/minute, burst of 5
limiter = TokenBucket(rate=10 / 60, capacity=5)
