from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database.url, echo=True, pool_size=5, max_overflow=10
)

sessionmaker = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
