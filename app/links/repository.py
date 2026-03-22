from datetime import datetime, timedelta
from typing import Iterable, override

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.links.base_repo import AbstractLinkRepository
from app.links.models import Link


class SQLLinkRepository(AbstractLinkRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @override
    async def get_by_id(self, id: int) -> Link | None:
        stmt = select(Link).where(Link.id == id)
        link = await self.session.execute(stmt)

        return link.scalar_one_or_none()

    @override
    async def get_by_long_url(self, long_url: str) -> Iterable[Link]:
        stmt = select(Link).where(Link.long_url == long_url)
        link = await self.session.execute(stmt)

        return link.scalars().all()

    @override
    async def create(self, link: Link) -> Link:
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    @override
    async def get_by_slug(self, slug: str) -> Link | None:
        stmt = select(Link).where(Link.slug == slug)
        link = await self.session.execute(stmt)

        return link.scalar_one_or_none()

    @override
    async def increment_redirects(self, slug: str, amount: int) -> None:
        stmt = (
            update(Link)
            .where(Link.slug == slug)
            .values(redirects=Link.redirects + amount, last_used_at=datetime.now())
        )
        await self.session.execute(stmt)
        await self.session.commit()

    @override
    async def delete_by_slug(self, slug: str) -> Link:
        stmt = delete(Link).where(Link.slug == slug).returning(Link)
        deleted = await self.session.execute(stmt)
        await self.session.commit()
        return deleted.scalar_one()

    @override
    async def update_long_url(self, slug: str, new_long_url: str) -> Link:
        stmt = (
            update(Link)
            .where(Link.slug == slug)
            .values(long_url=new_long_url)
            .returning(Link)
        )
        updated = await self.session.execute(stmt)
        await self.session.commit()
        return updated.scalar_one()

    @override
    async def flush_unused_links(self, days: int) -> Iterable[str]:
        due_date = datetime.now() - timedelta(days=days)
        stmt = delete(Link).where(Link.last_used_at < due_date).returning(Link.slug)

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.scalars()

    @override
    async def update_stats(
        self, slug: str, redirects: int, last_used: datetime | None
    ) -> Link | None:
        stmt = (
            update(Link)
            .where(Link.slug == slug)
            .values(redirects=Link.redirects + redirects, last_used_at=last_used)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
