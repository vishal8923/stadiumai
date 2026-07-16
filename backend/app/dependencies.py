"""Shared FastAPI dependencies for rate limiting and database sessions."""
import time
from collections import defaultdict
from fastapi import Depends, Request, HTTPException, status
from app.config import settings
from app.models.database import get_db  # noqa: F401

# In-memory store: { "client_ip:path": [timestamp1, timestamp2, ...] }
rate_limit_store: dict[str, list[float]] = defaultdict(list)


def rate_limiter(limit_per_minute: int):
    """Create an in-memory per-IP-per-route rate limiter dependency.

    Uses a deque-like approach: on each request we only need to check the
    oldest timestamp, not re-scan the entire list.  Old entries are lazily
    pruned when the list exceeds 2x the limit.

    Args:
        limit_per_minute: Maximum number of requests allowed per minute per IP+path.

    Returns:
        A FastAPI dependency callable.

    """

    def dependency(request: Request) -> None:
        limit = limit_per_minute or settings.RATE_LIMIT_PER_MINUTE
        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"

        now = time.time()
        timestamps = rate_limit_store[key]

        # Fast path: if under limit, just append
        if len(timestamps) < limit:
            timestamps.append(now)
            return

        # At capacity: check if the oldest entry has expired
        if now - timestamps[0] >= 60:
            # Oldest entry is outside the window — drop it and others that expired
            cutoff = now - 60
            # Find first non-expired index (usually 0 or 1)
            idx = 0
            while idx < len(timestamps) and timestamps[idx] <= cutoff:
                idx += 1
            rate_limit_store[key] = timestamps[idx:]
            rate_limit_store[key].append(now)
            return

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )

    return dependency


general_rate_limit = Depends(rate_limiter(100))
chat_rate_limit = Depends(rate_limiter(20))
navigation_rate_limit = Depends(rate_limiter(50))
incident_rate_limit = Depends(rate_limiter(10))
