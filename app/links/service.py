from datetime import datetime

from fastapi import HTTPException, status

from app.auth.base_repo import AbstractUserRepository
from app.auth.exceptions import UserNotFoundException
from app.auth.models import User
from app.cache.base_repo import AbstractCacheRepository
from app.core.config import get_settings
from app.links.base_repo import AbstractLinkRepository
from app.links.exceptions import SlugAlreadyExistsException
from app.links.models import Link
from app.links.schemas import LinkCreate, LinkSchema, LinkStats, LinkUpdate
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
        self.last_used_prefix = settings.cache.last_used_prefix

    def cache_key(self, slug: str) -> str:
        return f"{self.link_prefix}:{slug}"

    def clicks_key(self, slug: str) -> str:
        return f"{self.clicks_prefix}:{slug}"

    def last_used_key(self, slug: str) -> str:
        return f"{self.last_used_prefix}:{slug}"

    async def create_short_link(
        self, link_schema: LinkCreate, user: User | None
    ) -> LinkSchema:
        if link_schema.slug:
            slug_exists = await self.link_repo.get_by_slug(link_schema.slug)
            if slug_exists:
                raise SlugAlreadyExistsException
        else:
            link_schema.slug = generate_slug()

        if user:
            user_exists = await self.user_repo.get_by_id(user.id)
            if not user_exists:
                raise UserNotFoundException

        link = Link(**link_schema.model_dump(), user=user)

        created_link = await self.link_repo.create(link)

        return LinkSchema.model_validate(created_link)

    async def get_original_link(self, slug: str) -> str:

        long_url = await self.cache_repo.get(self.cache_key(slug))

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

            await self.cache_repo.set(self.cache_key(slug), long_url)

        await self.cache_repo.increment(self.clicks_key(slug))
        await self.cache_repo.set(self.last_used_key(slug), datetime.now().isoformat())

        return long_url

    async def delete_link(self, slug: str, user: User) -> LinkSchema:
        link = await self.link_repo.get_by_slug(slug)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Alias does not exist"
            )

        if not link.user == user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )

        deleted = await self.link_repo.delete_by_slug(slug)
        await self.cache_repo.delete(self.cache_key(slug), self.clicks_key(slug))
        return LinkSchema.model_validate(deleted)

    async def update_link(self, update_schema: LinkUpdate, user: User) -> LinkSchema:
        link = await self.link_repo.get_by_slug(update_schema.slug)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Alias not found"
            )

        if not link.user == user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only registered users can update their links",
            )

        updated = await self.link_repo.update_long_url(
            slug=update_schema.slug, new_long_url=update_schema.new_long_url
        )

        await self.cache_repo.set(
            self.cache_key(update_schema.slug), update_schema.new_long_url
        )

        return LinkSchema.model_validate(updated)

    async def get_link_stats(self, slug: str, user: User) -> LinkStats:
        link = await self.link_repo.get_by_slug(slug)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
            )

        if not link.user == user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )

        redis_clicks = await self.cache_repo.get(self.cache_key(slug))
        redis_clicks = int(redis_clicks) if redis_clicks else 0

        total_clicks = link.redirects + redis_clicks

        redis_last_used_at = await self.cache_repo.get(self.last_used_key(slug))

        last_used_at = (
            datetime.fromisoformat(redis_last_used_at)
            if redis_last_used_at
            else link.last_used_at
        )

        return LinkStats(
            long_url=link.long_url,
            created_at=link.created_at,
            redirects=total_clicks,
            last_used_at=last_used_at,
        )
