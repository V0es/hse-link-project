from abc import ABC, abstractmethod
from typing import AsyncGenerator


class AbstractCacheRepository(ABC):
    @abstractmethod
    async def set(self, key: str, value: str, ttl: int | None = None) -> None: ...
    @abstractmethod
    async def get(self, key: str) -> str | None: ...
    @abstractmethod
    async def delete(self, *keys: str) -> str | None: ...
    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> None: ...
    @abstractmethod
    async def get_keys(
        self, pattern: str, count: int | None = None
    ) -> AsyncGenerator[str]: ...
