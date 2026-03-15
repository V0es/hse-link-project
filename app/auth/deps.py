from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from jwt import InvalidTokenError

from app.auth.schemas import TokenPayload, UserSchema
from app.auth.utils import decode_jwt

CredsDep = Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]


async def get_user_creds(credentials: CredsDep) -> UserSchema:
    username, password = credentials.username, credentials.password
    user = UserSchema(username=username, password=password)

    return user


async def get_access_token(request: Request) -> TokenPayload | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = decode_jwt(token)
        return TokenPayload(**payload)
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
