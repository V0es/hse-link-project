from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import SQLUserRepository
from app.auth.schemas import UserSchema
from app.auth.utils import hash_password
from app.core.database import get_session

CredsDep = Annotated[HTTPBasicCredentials, Depends(HTTPBasic)]


async def get_user_repo(
    session: AsyncSession = Depends(get_session),
) -> SQLUserRepository:
    return SQLUserRepository(session)


async def get_user_creds(credentials: CredsDep) -> UserSchema:
    username, password = credentials.username, credentials.password
    user = UserSchema(username=username, password_hash=hash_password(password))

    return user
