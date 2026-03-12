from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import get_user_creds, get_user_repo
from app.auth.repository import SQLUserRepository
from app.auth.schemas import UserSchema

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_creds: UserSchema = Depends(get_user_creds),
    user_repo: SQLUserRepository = Depends(get_user_repo),
):
    user = await user_repo.get_by_username(user_creds.username)
    if user:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    await user_repo.create(user_creds)
    return {"message": "Registered successfully"}
