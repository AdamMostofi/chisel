"""Rate limiter — chiseled version. Same behavior, less ceremony."""

import threading
import time
from functools import wraps

def rate_limit(calls=10, per=60):
    lock = threading.Lock()
    timestamps = []
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal timestamps
            with lock:
                now = time.time()
                timestamps = [t for t in timestamps if t > now - per]
                if len(timestamps) >= calls:
                    raise Exception("rate limit exceeded")
                timestamps.append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
