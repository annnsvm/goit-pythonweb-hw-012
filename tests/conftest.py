import asyncio
import pickle
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import create_access_token
from src.services.utils.hash_helper import HashHelper

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "id": 7,
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "777333",
    "avatar": "https://twitter.com/gravatar",
    "role": "user",
    "refresh_token": "refresh_token",
}

test_admin_user = User(
    id=7,
    username="deadpool",
    email="deadpool@example.com",
    avatar="https://twitter.com/gravatar",
    role="admin",
    confirmed="True",
    refresh_token="refresh_token",
)


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = HashHelper().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                confirmed=True,
                avatar="<https://twitter.com/gravatar>",
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["username"]})
    return token


@pytest.fixture(autouse=True)
def mock_redis_user():
    with patch("src.services.auth.redis.from_url") as mock_redis:
        mock_instance = mock_redis.return_value
        # mock_instance.get.return_value = None
        mock_instance.get.return_value = pickle.dumps(test_admin_user)
        mock_instance.set = AsyncMock()
        mock_instance.expire = AsyncMock()

        yield