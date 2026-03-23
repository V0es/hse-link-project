from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.auth.exceptions import UserNotFoundException
from app.auth.models import User
from app.common.deps import get_current_user
from app.links.deps import get_link_service
from app.links.exceptions import SlugAlreadyExistsException
from app.links.schemas import LinkCreate, LinkSchema, LinkStats, LinkUpdate
from app.links.service import LinkServive

router = APIRouter(prefix="/links")


@router.post("/shorten", response_model=LinkCreate, status_code=status.HTTP_201_CREATED)
async def create_short_link(
    link: LinkCreate = Body(),
    link_service: LinkServive = Depends(get_link_service),
    user: User | None = Depends(get_current_user),
) -> LinkSchema:
    """
    Create short link
    """
    try:
        created_link = await link_service.create_short_link(link, user)
    except SlugAlreadyExistsException:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Alias already exists")

    except UserNotFoundException:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return created_link


@router.get("/{short_code}")
async def redirect_to_original_link(
    short_code: str, link_service: LinkServive = Depends(get_link_service)
) -> RedirectResponse:
    """
    Redirect
    """
    original_url = await link_service.get_original_link(short_code)
    return RedirectResponse(original_url)


@router.delete("/{short_code}", status_code=status.HTTP_200_OK)
async def delete_link(
    short_code: str,
    user: User | None = Depends(get_current_user),
    link_service: LinkServive = Depends(get_link_service),
) -> dict[str, str]:
    """
    Delete short link
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    await link_service.delete_link(slug=short_code, user=user)

    return {"message": "link deleted successfully"}


@router.put("/{short_code}", status_code=status.HTTP_200_OK, response_model=LinkSchema)
async def update_link(
    update_schema: LinkUpdate = Body(),
    user: User | None = Depends(get_current_user),
    link_service: LinkServive = Depends(get_link_service),
) -> LinkSchema:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only registered users can update their links",
        )
    updated = await link_service.update_link(update_schema=update_schema, user=user)

    return updated


@router.get("/{short_code}/stats", status_code=status.HTTP_200_OK)
async def get_stats(
    short_code: str,
    link_service: LinkServive = Depends(get_link_service),
    user: User | None = Depends(get_current_user),
) -> LinkStats:
    """Show stats"""
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    link_stats = await link_service.get_link_stats(short_code, user)
    return link_stats
