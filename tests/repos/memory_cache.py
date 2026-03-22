from typing import Any, AsyncGenerator, override

from app.cache.base_repo import AbstractCacheRepository


class MemoryCacheRepository(AbstractCacheRepository):
    def __init__(self) -> None:
        self.cache: dict[str, Any] = {}

    @override
    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self.cache[key] = value

    @override
    async def get(self, key: str) -> str | None:
        return self.cache.get(key)

    @override
    async def delete(self, *keys: str) -> str | None:
        for key in keys:
            self.cache.pop(key, "NF")

    @override
    async def increment(self, key: str, amount: int = 1) -> None:
        self.cache[key] = self.cache.get(key, 0) + amount

    @override
    async def get_keys(
        self, pattern: str, count: int | None = None
    ) -> AsyncGenerator[str, None]:
        pattern = pattern.replace("*", "")
        valid_keys = [key for key in self.cache.keys() if key.startswith(pattern)]

        for key in valid_keys:
            yield key
