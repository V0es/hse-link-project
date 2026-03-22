from datetime import datetime, timedelta

import pytest


@pytest.mark.asyncio
@pytest.mark.functional
async def test_link_create_unauthorized_random_slug(client):
    payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    }
    response = await client.post("/links/shorten", json=payload)

    assert response.status_code == 201
    assert "slug" in response.json()


@pytest.mark.asyncio
@pytest.mark.functional
async def test_link_create_authorized_random_slug(auth_client):
    payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
    }
    response = await auth_client.post("/links/shorten", json=payload)

    assert response.status_code == 201
    assert "slug" in response.json()


@pytest.mark.asyncio
@pytest.mark.functional
async def test_link_create_unauthorized_custom_slug(client):
    payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
        "slug": "test",
    }
    response = await client.post("/links/shorten", json=payload)

    assert response.status_code == 201
    assert "slug" in response.json()
    assert response.json().get("slug") == "test"


@pytest.mark.asyncio
@pytest.mark.functional
async def test_link_create_authorized_custom_slug(auth_client):
    payload = {
        "long_url": "https://google.com",
        "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
        "slug": "test",
    }
    response = await auth_client.post("/links/shorten", json=payload)

    assert response.status_code == 201
    assert "slug" in response.json()

    assert response.json().get("slug") == "test"
