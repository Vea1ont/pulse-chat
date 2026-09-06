from contextlib import asynccontextmanager

from database import Base, engine
from events import producer
from fastapi import FastAPI
from models import Profile, User  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await producer.start()
    yield
    await producer.stop()
