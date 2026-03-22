from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.base_repo import AbstractUserRepository
from app.auth.models import User
from app.auth.schemas import UserSchema
from app.auth.utils import hash_password


class SQLUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @override
    async def get_by_id(self, id: int) -> User | None:
        stmt = select(User).where(User.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @override
    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @override
    async def create(self, user_schema: UserSchema) -> User:
        user_schema.password = hash_password(user_schema.password)
        user_to_create = User(
            username=user_schema.username, password_hash=user_schema.password
        )
        self.session.add(user_to_create)

        await self.session.commit()
        await self.session.refresh(user_to_create)

        return user_to_create
