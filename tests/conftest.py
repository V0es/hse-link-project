import asyncio
import base64

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from app.auth.repository import SQLUserRepository
from app.common.deps import get_cache_repo, get_user_repo
from app.core.config import get_settings
from app.core.database import Base
from app.links.deps import get_link_repository
from app.links.repository import SQLLinkRepository
from app.main import app
from tests.repos.memory_cache import MemoryCacheRepository

settings = get_settings()


def basic_auth_headers(username: str, password: str):
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    assert "sqlite" in settings.test.db_url
    engine = create_async_engine(settings.test.db_url)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database(async_engine: AsyncEngine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine: AsyncEngine):
    async with async_engine.connect() as conn:
        trans = await conn.begin()

        session = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )()

        nested = await conn.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(sess, transaction):
            nonlocal nested
            if not nested.is_active and conn.sync_connection:
                nested = conn.sync_connection.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture
def test_app():
    from app.main import create_app

    return create_app()


@pytest_asyncio.fixture
async def app_with_overrides(test_app, db_session):

    async def get_fake_user_repo() -> SQLUserRepository:
        return SQLUserRepository(db_session)

    async def get_fake_link_repo() -> SQLLinkRepository:
        return SQLLinkRepository(db_session)

    async def get_fake_cache_repo() -> MemoryCacheRepository:
        return MemoryCacheRepository()

    test_app.dependency_overrides[get_link_repository] = get_fake_link_repo
    test_app.dependency_overrides[get_user_repo] = get_fake_user_repo
    test_app.dependency_overrides[get_cache_repo] = get_fake_cache_repo

    yield test_app

    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_with_overrides):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_overrides), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient):
    # 1. Регистрируем пользователя
    await client.post("/auth/register", headers=basic_auth_headers("test", "123"))

    # 2. Логинимся
    login_resp = await client.post(
        "/auth/login", headers=basic_auth_headers("test", "123")
    )

    # 3. Берем куку из заголовка set-cookie
    token = login_resp.cookies.get("access_token")
    if token:
        client.cookies.set("access_token", token)

    return client
