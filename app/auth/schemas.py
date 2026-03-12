from pydantic import BaseModel


class UserSchema(BaseModel):
    username: str
    password_hash: str


class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"
