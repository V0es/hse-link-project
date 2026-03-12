from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import get_settings
from core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


settings = get_settings()

app = FastAPI(lifespan=lifespan)
