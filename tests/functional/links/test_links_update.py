from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.functional
async def test_link_update_unauthorized(client: AsyncClient):
    payload = {
        "slug": "test",
        "new_long_url": "https://google.com",
    }
    update_resp = await client.put(
        "/links/update",
        json=payload,
    )

    assert update_resp.status_code == 401


@pytest.mark.asyncio
@pytest.mark.functional
async def test_link_update_authorized_not_found(auth_client: AsyncClient):
    create_payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    }

    await auth_client.post(
        "/links/shorten",
        json=create_payload,
    )

    update_payload = {
        "new_long_url": "https://example.com",
        "slug": "test",
    }

    update_resp = await auth_client.put(
        "/links/test",
        json=update_payload,
    )

    assert update_resp.status_code == 404


@pytest.mark.asyncio
@pytest.mark.functional
async def test_link_update_authorized_success(auth_client: AsyncClient):
    create_payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    }

    create_resp = await auth_client.post(
        "/links/shorten",
        json=create_payload,
    )

    slug = create_resp.json()["slug"]

    update_payload = {
        "new_long_url": "https://example.com",
        "slug": slug,
    }

    update_resp = await auth_client.put(
        f"/links/{slug}",
        json=update_payload,
    )

    assert update_resp.status_code == 200

    redir_resp = await auth_client.get(f"/links/{slug}", follow_redirects=True)

    assert redir_resp.url == "https://example.com"
