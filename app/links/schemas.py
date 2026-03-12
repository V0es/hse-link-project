from pydantic import BaseModel


class LinkCreate(BaseModel):
    slug: str
    long_url: str
    user_id: int | None
