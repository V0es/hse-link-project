from redis.asyncio import Redis

from app.cache.base_repo import AbstractCacheRepository
from app.core.config import get_settings

settings = get_settings()


class RedisCacheRepository(AbstractCacheRepository):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        return await self.redis.set(key, value, ttl)

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def delete(self, key: str) -> str | None:
        return await self.redis.delete(key)

    async def increment(self, key: str, amount: int = 1) -> None:
        await self.redis.incrby(key, amount)
