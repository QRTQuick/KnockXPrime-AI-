"""
Rate limiting middleware for API endpoints
"""
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self):
        # Store request timestamps per IP/API key
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed within rate limit"""
        now = time.time()
        requests = self.requests[key]
        
        # Remove old requests outside the window
        while requests and requests[0] <= now - window:
            requests.popleft()
        
        # Check if under limit
        if len(requests) < limit:
            requests.append(now)
            return True
        
        return False
    
    def get_reset_time(self, key: str, window: int) -> Optional[int]:
        """Get when the rate limit resets"""
        requests = self.requests[key]
        if requests:
            return int(requests[0] + window)
        return None


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.window = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Get client identifier (IP or API key)
        client_id = self.get_client_id(request)
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_id, self.calls_per_minute, self.window):
            reset_time = rate_limiter.get_reset_time(client_id, self.window)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.calls_per_minute} per minute",
                    "reset_time": reset_time
                },
                headers={"Retry-After": str(self.window)}
            )
        
        return await call_next(request)
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get API key from Authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return f"api_key:{auth_header[7:20]}"  # Use first 20 chars of API key
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"