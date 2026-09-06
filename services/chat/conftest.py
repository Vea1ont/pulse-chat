import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from database import DATABASE_URL, Base, get_db
from main import app
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# тестовый движок БЕЗ пула — соединения не переживают запрос
TEST_DATABASE_URL = DATABASE_URL.replace("/pulse_chat_db", "/pulse_chat_test_db")
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        yield session


# подменяем настоящий get_db на тестовый во всём приложении
app.dependency_overrides[get_db] = override_get_db


async def _reset_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def prepare_database():
    asyncio.run(_reset_tables())
    yield


@pytest.fixture(autouse=True)
def mock_valkey():
    with (
        patch("routers.chats.valkey") as valkey_mock_a,
        patch("security.valkey") as valkey_mock_b,
    ):
        valkey_mock_a.get = AsyncMock(return_value=None)  # кэш всегда пустой
        valkey_mock_a.set = AsyncMock()  # запись в кэш - пустышка
        valkey_mock_a.keys = AsyncMock(return_value=[])  # ключей для инвалидации нет
        valkey_mock_a.delete = AsyncMock()  # удаление - пустышка
        valkey_mock_a.exists = AsyncMock(return_value=0)

        valkey_mock_b.exists = AsyncMock(return_value=0)
        yield valkey_mock_a, valkey_mock_b
