from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base
from models import User, Profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield