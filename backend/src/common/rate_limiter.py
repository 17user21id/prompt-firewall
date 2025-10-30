"""
Rate limiting utilities extracted from auth module.
"""

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from .auth_constants import AuthConstants


class RateLimiter:
    """Simple rate limiter for API endpoints."""

    def __init__(self):
        self.requests = {}  # tenant_id -> list of timestamps
        self.max_requests = AuthConstants.DEFAULT_MAX_REQUESTS  # per minute
        self.window_minutes = AuthConstants.DEFAULT_WINDOW_MINUTES

    def is_rate_limited(self, tenant_id: str) -> bool:
        """Check if tenant is rate limited."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=self.window_minutes)

        if tenant_id not in self.requests:
            self.requests[tenant_id] = []

        # Remove old requests
        self.requests[tenant_id] = [
            req_time for req_time in self.requests[tenant_id]
            if req_time > window_start
        ]

        # Check if limit exceeded
        if len(self.requests[tenant_id]) >= self.max_requests:
            return True

        # Add current request
        self.requests[tenant_id].append(now)
        return False


# Global rate limiter
rate_limiter = RateLimiter()


def check_rate_limit(tenant_id: str):
    """Check rate limit for a tenant."""
    if rate_limiter.is_rate_limited(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=AuthConstants.RATE_LIMIT_EXCEEDED
        )


