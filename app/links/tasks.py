import asyncio

from app.core.celery_app import celery_app
from app.core.database import get_session
from app.links.repository import SQLLinkRepository


@celery_app.task(name="increment_clicks")
def increment_clicks(slug: str):
    async def increment(slug: str):
        async with get_session() as session:
            repo = SQLLinkRepository(session)
            await repo.increment_redirects(slug)

    asyncio.run(increment(slug))
