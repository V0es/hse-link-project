from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_link_stats_unauthorized(client: AsyncClient):
    stats_resp = await client.get("/links/test/stats")

    assert stats_resp.status_code == 403


@pytest.mark.asyncio
async def test_link_stats_authorized_not_found(auth_client: AsyncClient):
    resp = await auth_client.get("/links/test/stats")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_link_stats_authorized_success(auth_client: AsyncClient):
    create_payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    }

    create_resp = await auth_client.post(
        "/links/shorten",
        json=create_payload,
    )

    slug = create_resp.json()["slug"]

    stats_resp = await auth_client.get(f"/links/{slug}/stats")

    assert stats_resp.status_code == 200
