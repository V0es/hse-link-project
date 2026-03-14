from datetime import datetime

from fastapi import HTTPException, status

from app.auth.base_repo import AbstractUserRepository
from app.auth.models import User
from app.cache.base_repo import AbstractCacheRepository
from app.core.config import get_settings
from app.links.base_repo import AbstractLinkRepository
from app.links.models import Link
from app.links.schemas import LinkCreate
from app.links.utils import generate_slug

settings = get_settings()


class LinkServive:
    def __init__(
        self,
        link_repo: AbstractLinkRepository,
        user_repo: AbstractUserRepository,
        cache_repo: AbstractCacheRepository,
    ) -> None:
        self.link_repo = link_repo
        self.user_repo = user_repo
        self.cache_repo = cache_repo

        self.link_prefix = settings.cache.link_prefix
        self.clicks_prefix = settings.cache.clicks_prefix

    async def create_short_link(self, link_schema: LinkCreate, user: User | None):
        if link_schema.slug:
            slug_exists = await self.link_repo.get_by_slug(link_schema.slug)
            if slug_exists:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, detail="Alias already exists"
                )
        else:
            link_schema.slug = generate_slug()

        if user:
            user_exists = await self.user_repo.get_by_id(user.id)
            if not user_exists:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

        link = Link(**link_schema.model_dump(), user=user)

        created_link = await self.link_repo.create(link)

        return LinkCreate.model_validate(created_link)

    async def get_original_link(self, slug: str) -> str:
        cache_key = f"{self.link_prefix}:{slug}"
        clicks_key = f"{self.clicks_prefix}:{slug}"

        long_url = await self.cache_repo.get(cache_key)

        if not long_url:
            link = await self.link_repo.get_by_slug(slug)

            if not link:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
                )

            if link.expires_at and link.expires_at < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_410_GONE, detail="Link has expired"
                )

            long_url = link.long_url

            await self.cache_repo.set(cache_key, long_url, ttl=3600)

        await self.cache_repo.increment_clicks(clicks_key)

        return long_url
