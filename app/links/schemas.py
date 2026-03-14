from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LinkCreate(BaseModel):
    model_config = ConfigDict(validate_by_alias=True)
    long_url: str
    expires_at: datetime
    slug: str | None = Field(None, alias="custom_alias")
