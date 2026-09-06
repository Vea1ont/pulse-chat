import asyncio
from contextlib import asynccontextmanager

from consumer import chat_cache_invalidation
from database import Base, engine
from fastapi import FastAPI
from models import Chat, ChatMember, Message  # noqa: F401


@asynccontextmanager  # 1. Делаю функцию менеджером старта/паузы
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:  # 2. Открываю соединение с БД
        await conn.run_sync(
            Base.metadata.create_all
        )  # 3. Создаю все таблицы, о которых Base знает
    chat_invalid = asyncio.create_task(chat_cache_invalidation())
    yield
    chat_invalid.cancel()
