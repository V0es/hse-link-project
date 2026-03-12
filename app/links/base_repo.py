from abc import ABC

from app.links.models import Link
from app.links.schemas import LinkCreate


class AbstractLinkRepository(ABC):
    async def get_by_id(self, id: int) -> Link: ...
    async def get_by_long_url(self, long_url: str) -> Link: ...
    async def create(self, link_schema: LinkCreate) -> Link: ...
