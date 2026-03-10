from fastapi import APIRouter

router = APIRouter(prefix="/links")


@router.post("/shorten")
def create_short_link():
    """
    Create short link
    """
    pass


@router.get("/{short_code}")
def redirect_to_original_link(short_code: str):
    """
    Redirect
    """
    pass


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


@router.post("/shorten")
def create_link(custom_alias: str):
    """
    Create link
    """
