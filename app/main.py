from contextlib import asynccontextmanager

from core.config import get_settings
from core.database import engine
from fastapi import FastAPI

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

app = FastAPI(lifespan=lifespan)
