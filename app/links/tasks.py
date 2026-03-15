from datetime import datetime

from app.cache.redis_cache import RedisCacheRepository
from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.core.database import get_async_session
from app.core.redis import get_redis
from app.links.repository import SQLLinkRepository

settings = get_settings()


@celery_app.task(name="sync_stats")
async def sync_stats():
    async def sync():
        redis = await get_redis(
            settings.cache.host, settings.cache.port, settings.cache.db_num
        )
        cache_repo = RedisCacheRepository(redis)
        async with get_async_session() as session:
            link_repo = SQLLinkRepository(session)
            async for key in cache_repo.get_keys(f"{settings.cache.clicks_prefix}:*"):
                slug = key.split(":")[1]

                clicks = await cache_repo.get(key)
                last_used = await cache_repo.get(
                    f"{settings.cache.last_used_prefix}:{slug}"
                )

                if not clicks:
                    continue

                await link_repo.update_stats(
                    slug,
                    int(clicks),
                    datetime.fromisoformat(last_used) if last_used else None,
                )
                await cache_repo.delete(key)
                await cache_repo.delete(f"{settings.cache.last_used_prefix}:{slug}")

    await sync()


@celery_app.task(name="flush_abandoned_links")
async def flush_abandoned_links() -> None:
    async def flush():
        redis = await get_redis(
            settings.cache.host, settings.cache.port, settings.cache.db_num
        )
        cache_repo = RedisCacheRepository(redis)
        async with get_async_session() as session:
            link_repo = SQLLinkRepository(session)
            deleted_slugs = await link_repo.flush_unused_links(
                settings.app.link_unused_threshold_days
            )
        if deleted_slugs:
            await cache_repo.delete(
                *[f"{settings.cache.link_prefix}:{slug}" for slug in deleted_slugs]
            )

            await cache_repo.delete(
                *[f"{settings.cache.clicks_prefix}:{slug}" for slug in deleted_slugs]
            )

    await flush()
