import pytest

from tests.conftest import basic_auth_headers


@pytest.mark.asyncio
@pytest.mark.functional
async def test_register(client):
    response = await client.post(
        "/auth/register", headers=basic_auth_headers("test", "123")
    )

    assert response.status_code == 201


@pytest.mark.asyncio
@pytest.mark.functional
async def test_duplicate_register(client):
    credentials = basic_auth_headers("test", "123")
    await client.post("/auth/register", headers=credentials)

    response = await client.post("/auth/register", headers=credentials)

    assert response.status_code == 409


@pytest.mark.asyncio
@pytest.mark.functional
async def test_login_success(client):
    credentials = basic_auth_headers("test", "123")
    await client.post("/auth/register", headers=credentials)

    response = await client.post("/auth/login", headers=credentials)

    assert response.status_code == 200
    assert "access_token" in response.cookies


@pytest.mark.asyncio
@pytest.mark.functional
async def test_login_wrong_credentials(client):
    true_credentials = basic_auth_headers("test", "123")
    wrong_username_credentials = basic_auth_headers("test1", "123")
    wrong_password_credentials = basic_auth_headers("test", "1231")
    await client.post("/auth/register", headers=true_credentials)

    response = await client.post("/auth/login", headers=wrong_username_credentials)
    assert response.status_code == 403

    response = await client.post("/auth/login", headers=wrong_password_credentials)
    assert response.status_code == 403
