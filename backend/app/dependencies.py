import time
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from typing import Generator
from app.config import settings
from app.models.database import get_db

# In-memory rate limit store: { "client_ip:path": [timestamp1, timestamp2, ...] }
rate_limit_store = defaultdict(list)

def rate_limiter(limit_per_minute: int):
    """
    A simple in-memory rate limiter dependency.
    """
    def dependency(request: Request):
        # Fallback to rate limit in settings if not configured
        limit = limit_per_minute or settings.RATE_LIMIT_PER_MINUTE
        client_ip = request.client.host if request.client else "unknown"
        # We limit based on IP and route path
        key = f"{client_ip}:{request.url.path}"
        
        now = time.time()
        # Clean up timestamps older than 60 seconds
        rate_limit_store[key] = [t for t in rate_limit_store[key] if now - t < 60]
        
        if len(rate_limit_store[key]) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        rate_limit_store[key].append(now)
    return dependency

# Specific rate limit dependencies based on API contract:
# - General API: 100 requests/minute
# - AI Chat: 20 requests/minute
# - Navigation: 50 requests/minute
# - Incident report: 10 requests/minute

general_rate_limit = Depends(rate_limiter(100))
chat_rate_limit = Depends(rate_limiter(20))
navigation_rate_limit = Depends(rate_limiter(50))
incident_rate_limit = Depends(rate_limiter(10))
