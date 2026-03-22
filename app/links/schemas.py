from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LinkCreate(BaseModel):
    long_url: str
    expires_at: datetime
    slug: str | None = None


class LinkUpdate(BaseModel):
    slug: str
    new_long_url: str


class LinkSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    long_url: str
    created_at: datetime
    expires_at: datetime


class LinkStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    long_url: str
    created_at: datetime
    redirects: int
    last_used_at: datetime | None
