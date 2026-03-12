from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.auth.models import User


class Link(Base):
    slug: Mapped[str] = mapped_column(unique=True)
    long_url: Mapped[str] = mapped_column()
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)
    user: Mapped[User | None] = relationship(back_populates="links")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    expires_at: Mapped[DateTime | None] = mapped_column(DateTime, default=None)
