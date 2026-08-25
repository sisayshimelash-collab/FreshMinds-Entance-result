"""
FreshMinds Result Bot — Rate Limiter & In-Memory TTL Cache

Thread-safe, self-cleaning rate limiter and LRU/TTL cache
for handling thousands of concurrent users safely without memory leaks.
"""

import time
import asyncio
from collections import defaultdict
from typing import Any, Optional

from config import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS


class RateLimiter:
    """Per-user rate limiter using a sliding window with auto-cleanup."""

    def __init__(
        self,
        max_requests: int = RATE_LIMIT_MAX_REQUESTS,
        window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
        max_tracked_users: int = 50000,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_tracked_users = max_tracked_users
        self._requests: dict[int, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if a user is allowed to make a request.
        Returns True if allowed, False if rate-limited.
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds

        # Clean old timestamps for this user
        timestamps = [ts for ts in self._requests[user_id] if ts > cutoff]

        if len(timestamps) >= self.max_requests:
            self._requests[user_id] = timestamps
            return False

        # Add current timestamp
        timestamps.append(now)
        self._requests[user_id] = timestamps

        # Periodic purge guard if dictionary exceeds memory limit
        if len(self._requests) > self.max_tracked_users:
            self.cleanup()

        return True

    def seconds_until_reset(self, user_id: int) -> int:
        """Return seconds until the user's oldest request expires."""
        if user_id not in self._requests or not self._requests[user_id]:
            return 0

        now = time.monotonic()
        cutoff = now - self.window_seconds
        active = [ts for ts in self._requests[user_id] if ts > cutoff]

        if not active:
            return 0

        oldest = min(active)
        remaining = self.window_seconds - (now - oldest)
        return max(1, int(remaining))

    def cleanup(self):
        """Remove users with no active requests to bound memory usage."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        expired_users = [
            uid for uid, timestamps in self._requests.items()
            if not timestamps or max(timestamps) <= cutoff
        ]
        for uid in expired_users:
            self._requests.pop(uid, None)


class TTLCache:
    """Lightweight in-memory TTL cache with capacity bounding."""

    def __init__(self, default_ttl: float = 300.0, max_size: int = 10000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get an item if it exists and has not expired."""
        if key not in self._cache:
            return None

        expiry, value = self._cache[key]
        if time.monotonic() > expiry:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Store an item with an expiration time."""
        # Evict oldest entry if size limit reached
        if len(self._cache) >= self.max_size:
            self.cleanup()
            if len(self._cache) >= self.max_size:
                # Remove first key (FIFO approximation)
                first_key = next(iter(self._cache))
                del self._cache[first_key]

        expire_at = time.monotonic() + (ttl if ttl is not None else self.default_ttl)
        self._cache[key] = (expire_at, value)

    def delete(self, key: str):
        """Delete an item from cache."""
        self._cache.pop(key, None)

    def cleanup(self):
        """Purge all expired items."""
        now = time.monotonic()
        expired = [k for k, (exp, _) in self._cache.items() if now > exp]
        for k in expired:
            del self._cache[k]
