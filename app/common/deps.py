from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_access_token
from app.auth.models import User
from app.auth.repository import SQLUserRepository
from app.auth.schemas import TokenPayload
from app.cache.redis_cache import RedisCacheRepository
from app.core.database import get_session
from app.links.repository import SQLLinkRepository


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


async def get_cache_repo(redis: Redis = Depends(get_redis)) -> RedisCacheRepository:
    return RedisCacheRepository(redis)


async def get_user_repo(
    session: AsyncSession = Depends(get_session),
) -> SQLUserRepository:
    return SQLUserRepository(session)


async def get_link_repo(
    session: AsyncSession = Depends(get_session),
) -> SQLLinkRepository:
    return SQLLinkRepository(session)


async def get_current_user(
    token: TokenPayload | None = Depends(get_access_token),
    user_repo: SQLUserRepository = Depends(get_user_repo),
) -> User | None:
    if not token:
        return None

    user = await user_repo.get_by_username(token.username)
    return user
