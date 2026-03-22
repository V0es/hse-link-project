from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.auth.deps import get_user_creds
from app.auth.repository import SQLUserRepository
from app.auth.schemas import UserSchema
from app.auth.utils import encode_jwt, verify_password
from app.common.deps import get_user_repo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_creds: UserSchema = Depends(get_user_creds),
    user_repo: SQLUserRepository = Depends(get_user_repo),
) -> dict[str, str]:
    user = await user_repo.get_by_username(user_creds.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    await user_repo.create(user_creds)
    return {"message": "Registered successfully"}


@router.post("/login")
async def login(
    response: Response,
    user_creds: UserSchema = Depends(get_user_creds),
    user_repo: SQLUserRepository = Depends(get_user_repo),
) -> dict[str, str]:
    user = await user_repo.get_by_username(user_creds.username)
    if not user or not verify_password(user_creds.password, user.password_hash):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Incorrect credentials")
    token = encode_jwt({"username": user_creds.username})

    response.set_cookie("access_token", token, httponly=True, secure=False)
    return {"message": "Logged in successfully"}
