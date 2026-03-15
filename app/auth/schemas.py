from datetime import datetime

from pydantic import BaseModel


class UserSchema(BaseModel):
    username: str
    password: str


class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenPayload(BaseModel):
    username: str
    iat: datetime
    exp: datetime | None = None
