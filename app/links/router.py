from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from app.auth.deps import get_current_user
from app.auth.models import User
from app.links.deps import get_link_service
from app.links.schemas import LinkCreate
from app.links.service import LinkServive

router = APIRouter(prefix="/links")


@router.post("/shorten", response_model=LinkCreate, status_code=status.HTTP_201_CREATED)
async def create_short_link(
    link: LinkCreate,
    link_service: LinkServive = Depends(get_link_service),
    user: User | None = Depends(get_current_user),
) -> LinkCreate:
    """
    Create short link
    """
    created_link = await link_service.create_short_link(link, user)
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


@router.delete("/{short_code}")
def delete_link(short_code: str):
    """
    Delete short link
    """
    pass


@router.put("/{short_code}")
def update_link(short_code: str):
    """
    Update link
    """
    pass


@router.get("/{short_code}/stats")
def get_stats(short_code: str):
    """Show stats"""
    pass


@router.post("/shorten")
def create_link(custom_alias: str):
    """
    Create link
    """
    pass
