from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.auth.models import User


class Link(Base):
    slug: Mapped[str] = mapped_column(String(), unique=True, index=True)
    long_url: Mapped[str] = mapped_column()
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), default=None)
    user: Mapped["User | None"] = relationship("User", back_populates="links")
    redirects: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
