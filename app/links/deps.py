from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import SQLUserRepository
from app.cache.redis_cache import RedisCacheRepository
from app.common.deps import get_cache_repo, get_user_repo
from app.core.database import get_session
from app.links.repository import SQLLinkRepository
from app.links.service import LinkServive


async def get_link_repository(
    session: AsyncSession = Depends(get_session),
) -> SQLLinkRepository:
    return SQLLinkRepository(session)


async def get_link_service(
    link_repo: SQLLinkRepository = Depends(get_link_repository),
    user_repo: SQLUserRepository = Depends(get_user_repo),
    cache_repo: RedisCacheRepository = Depends(get_cache_repo),
) -> LinkServive:
    return LinkServive(link_repo, user_repo, cache_repo)
