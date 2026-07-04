"""Rate limiter — no-skill version. Full decorator class."""

import threading
import time
from functools import wraps


class RateLimitExceeded(Exception):
    """Raised when the rate limit is exceeded."""
    pass


class RateLimiter:
    """Limits the number of function calls per time window."""

    def __init__(self, calls=10, per=60):
        self.calls = calls
        self.per = per
        self._lock = threading.Lock()
        self._timestamps = []

    def acquire(self):
        """Try to acquire a slot. Raises RateLimitExceeded if over limit."""
        with self._lock:
            now = time.time()
            cutoff = now - self.per
            self._timestamps = [t for t in self._timestamps if t > cutoff]
            if len(self._timestamps) >= self.calls:
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {self.calls} calls per {self.per}s"
                )
            self._timestamps.append(now)
            return True

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            self.acquire()
            return fn(*args, **kwargs)
        return wrapper


def rate_limit(calls=10, per=60):
    """Decorator factory for rate limiting."""
    limiter = RateLimiter(calls, per)
    return limiter
