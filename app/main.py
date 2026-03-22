from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api_router import api_router
from app.core.config import get_settings
from app.core.database import engine
from app.core.redis import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await get_redis(
        host=settings.cache.host, port=settings.cache.port, db_num=settings.cache.db_num
    )
    yield
    await engine.dispose()
    await app.state.redis.close()


settings = get_settings()


def create_app() -> FastAPI:

    app = FastAPI(lifespan=lifespan)
    app.include_router(api_router)

    return app


app = create_app()
