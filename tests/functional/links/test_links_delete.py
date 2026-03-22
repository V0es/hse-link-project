from datetime import datetime, timedelta

import pytest


@pytest.mark.asyncio
@pytest.mark.functional
async def test_delete_requires_auth(client):
    response = await client.delete("/links/test")

    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.functional
async def test_delete_success(auth_client):
    payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    }
    create = await auth_client.post(
        "/links/shorten",
        json=payload,
    )

    slug = create.json()["slug"]
    response = await auth_client.delete(f"/links/{slug}")
    print(f"resp_json:{response.json()}")
    assert response.status_code == 200
