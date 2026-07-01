import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://vealont:pulsechat@postgres:5432/pulse_chat_db")

# Движок — одно соединение с БД на весь процесс
engine = create_async_engine(DATABASE_URL)

# Фабрика сессий — каждый запрос получает свою сессию
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Базовый класс для всех SQLAlchemy-моделей
class Base(DeclarativeBase):
    pass


# Dependency для FastAPI — даёт сессию на время запроса и закрывает после
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
