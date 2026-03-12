from abc import ABC

from app.auth.models import User
from app.auth.schemas import UserCreate


class AbstractUserRepository(ABC):
    async def get_by_id(self, id: int) -> User: ...
    async def get_by_username(self, username: str) -> User: ...
    async def create(self, user: UserCreate) -> User: ...
