from datetime import datetime, timedelta

import pytest


@pytest.mark.asyncio
@pytest.mark.functional
async def test_redirect_success(client):
    payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    }
    create = await client.post("/links/shorten", json=payload)
    print(create.json())
    slug = create.json()["slug"]

    response = await client.get(f"/links/{slug}", follow_redirects=False)

    assert response.status_code in (301, 307)
    assert response.headers["location"] == "https://google.com"


@pytest.mark.asyncio
@pytest.mark.functional
async def test_redirect_not_found(client):
    response = await client.get("/links/unknown", follow_redirects=False)

    assert response.status_code == 404
