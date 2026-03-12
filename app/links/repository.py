from sqlalchemy.ext.asyncio import AsyncSession

from app.links.base_repo import AbstractLinkRepository


class SQLLinkRepository(AbstractLinkRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
