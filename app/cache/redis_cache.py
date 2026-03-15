from typing import AsyncGenerator, override

from redis.asyncio import Redis

from app.cache.base_repo import AbstractCacheRepository
from app.core.config import get_settings

settings = get_settings()


class RedisCacheRepository(AbstractCacheRepository):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.ttl = settings.cache.ttl

    @override
    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        ttl = ttl or self.ttl
        return await self.redis.set(key, value, ttl)

    @override
    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    @override
    async def delete(self, *keys: str) -> str | None:
        return await self.redis.delete(*keys)

    @override
    async def increment(self, key: str, amount: int = 1) -> None:
        await self.redis.incrby(key, amount)

    @override
    async def get_keys(self, pattern: str, count: int = 10) -> AsyncGenerator[str]:
        async for key in self.redis.scan_iter(pattern):
            yield key
