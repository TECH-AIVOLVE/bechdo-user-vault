
from functools import wraps
from fastapi import HTTPException, Request, status
import time
import asyncio
from src.config import settings

# Simple in-memory rate limiting store
# For production, use Redis or similar
rate_limit_store = {}

def rate_limited():
    """Rate limit decorator for API endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the IP from the request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
                    
            if not request and "request" in kwargs:
                request = kwargs["request"]
                
            if request:
                ip = request.client.host
            else:
                ip = "unknown"
                
            # Generate a key based on the function and IP
            key = f"{func.__name__}:{ip}"
            
            current_time = time.time()
            
            # Initialize or clean up old entries
            if key not in rate_limit_store or current_time - rate_limit_store[key]["start"] > settings.RATE_LIMIT_PERIOD_SECONDS:
                rate_limit_store[key] = {
                    "count": 0,
                    "start": current_time
                }
                
            # Increment count
            rate_limit_store[key]["count"] += 1
            
            # Check if rate limit exceeded
            if rate_limit_store[key]["count"] > settings.RATE_LIMIT_ATTEMPTS:
                time_passed = current_time - rate_limit_store[key]["start"]
                wait_time = settings.RATE_LIMIT_PERIOD_SECONDS - time_passed
                
                if wait_time > 0:
                    # Add jitter to prevent time-based attacks
                    wait_time = wait_time + (wait_time * 0.1)
                    
                    # For very sensitive endpoints, uncomment to add delay
                    # await asyncio.sleep(wait_time)
                    
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {int(wait_time)} seconds.",
                        headers={"Retry-After": str(int(wait_time))}
                    )
                    
            return await func(*args, **kwargs)
        return wrapper
    return decorator
