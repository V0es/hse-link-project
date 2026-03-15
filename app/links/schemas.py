from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LinkCreate(BaseModel):
    model_config = ConfigDict(validate_by_alias=True)
    long_url: str
    expires_at: datetime
    slug: str | None = Field(None, alias="custom_alias")


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
