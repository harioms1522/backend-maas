import asyncio
import time
from fastapi import Depends, HTTPException, status
from typing import Dict, Tuple

from app.api.v1.endpoints.helpers import get_api_key

class InMemoryRateLimiterOnAPIKey:
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.cache: Dict[str, Tuple[int, int]] = {}
        self.lock = asyncio.Lock()

    async def __call__(self, api_key: str = Depends(get_api_key)):
        current_minute = int(time.time() // self.window_seconds)
        print(f"Rate limiter check for API key: {api_key}, current minute: {current_minute}", time.time())
        async with self.lock:
            if api_key in self.cache:
                saved_minute, count = self.cache[api_key]
                if saved_minute == current_minute:
                    if count >= self.requests_per_minute:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute allowed."
                        )
                    self.cache[api_key] = (current_minute, count + 1)
                else:
                    self.cache[api_key] = (current_minute, 1)
            else:
                self.cache[api_key] = (current_minute, 1)