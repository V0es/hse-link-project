from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from jwt import InvalidTokenError

from app.auth.schemas import TokenPayload, UserSchema
from app.auth.utils import decode_jwt

CredsDep = Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]


async def get_user_creds(credentials: CredsDep) -> UserSchema:
    username, password = credentials.username, credentials.password
    user = UserSchema(username=username, password=password)

    return user


async def get_access_token(
    access_token: Annotated[str | None, Cookie()] = None,
) -> TokenPayload | None:
    if not access_token:
        return None
    try:
        payload = decode_jwt(access_token)
        return TokenPayload(**payload)
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
