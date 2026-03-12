from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password_hash: str
