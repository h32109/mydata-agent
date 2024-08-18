import asyncio
from typing import Any
from functools import wraps


class InMemoryCache:
    def __init__(self):
        self.cache = {}

    async def get(self, key: str) -> Any:
        return self.cache.get(key)

    async def set(self, key: str, value: Any, expiration: int = 3600):
        self.cache[key] = value
        asyncio.create_task(self._expire(key, expiration))

    async def _expire(self, key: str, expiration: int):
        await asyncio.sleep(expiration)
        self.cache.pop(key, None)


cache = InMemoryCache()


def cached(expiration: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            result = await cache.get(key)
            if result is None:
                result = await func(*args, **kwargs)
                await cache.set(key, result, expiration)
            return result

        return wrapper

    return decorator
