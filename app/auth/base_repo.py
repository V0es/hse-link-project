from abc import ABC

from app.auth.models import User
from app.auth.schemas import UserSchema


class AbstractUserRepository(ABC):
    async def get_by_id(self, id: int) -> User | None: ...
    async def get_by_username(self, username: str) -> User | None: ...
    async def create(self, user_schema: UserSchema) -> User: ...
