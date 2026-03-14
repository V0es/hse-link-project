from datetime import datetime
from typing import Iterable

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.links.base_repo import AbstractLinkRepository
from app.links.models import Link


class SQLLinkRepository(AbstractLinkRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_long_url(self, long_url: str) -> Iterable[Link]:
        stmt = select(Link).where(Link.long_url == long_url)
        link = await self.session.execute(stmt)

        return link.scalars().all()

    async def create(self, link: Link) -> Link:
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def get_by_slug(self, slug: str) -> Link | None:
        stmt = select(Link).where(Link.slug == slug)
        link = await self.session.execute(stmt)

        return link.scalar_one_or_none()

    async def increment_redirects(self, slug: str) -> None:
        stmt = (
            update(Link)
            .where(Link.slug == slug)
            .values(redirects=Link.redirects + 1, last_redirection=datetime.now())
        )
        await self.session.execute(stmt)
        await self.session.commit()
