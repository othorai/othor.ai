import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        
    def _cleanup_old_requests(self, key: str, window_seconds: int):
        """Remove requests older than the window."""
        current_time = time.time()
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if current_time - req_time < window_seconds
        ]
    
    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is within rate limit."""
        self._cleanup_old_requests(key, window_seconds)
        
        if len(self.requests[key]) >= max_requests:
            return False
            
        self.requests[key].append(time.time())
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Rate limiting decorator."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get client identifier (you might want to customize this)
            client_id = kwargs.get('authorization', 'anonymous')
            if isinstance(client_id, str) and client_id.startswith('Bearer '):
                client_id = client_id[7:]  # Remove 'Bearer ' prefix
            
            key = f"{func.__name__}:{client_id}"
            
            if not rate_limiter.check_rate_limit(key, max_requests, window_seconds):
                logger.warning(f"Rate limit exceeded for {key}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Please try again in {window_seconds} seconds."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator