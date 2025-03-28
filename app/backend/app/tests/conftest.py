from pathlib import Path

import jwt
import pytest_asyncio
from auth.oauth2 import create_access_token
from core.config import settings
from httpx import ASGITransport, AsyncClient
from main import app
from models.database import Base, get_db
from requests import Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Database connection (existing SQLite file)
DATABASE_URL = "sqlite+aiosqlite:///../../../data/test_vaccination_db.sqlite"

engine = create_async_engine(DATABASE_URL, echo=False)

# Session creation
TestingAsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db():
    """
    Drop and recreate all tables before each test, then populate them with data.
    """
    async with engine.begin() as conn:
        # 1) Drop & create tables
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        # 2) Load seed data from SQL script (optional)
        sql_file = Path("../../../data/data.sql")
        if not sql_file.exists():
            raise FileNotFoundError("data.sql not found")

        script = sql_file.read_text()

        # Split statements on semicolons, strip whitespace, and execute each
        for statement in script.split(";"):
            stmt = statement.strip()
            if stmt:
                await conn.execute(text(stmt))

    # The fixture yields here, so tests can run with the fresh, seeded DB
    yield

    # Optionally drop all tables again after each test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session(init_test_db) -> AsyncSession:  # type: ignore
    """
    Return a new database session for each test function,
    using the test engine.
    """
    async with TestingAsyncSessionLocal() as db:
        # async with db.begin():
        yield db


@pytest_asyncio.fixture
async def override_get_db_fixture(session: AsyncSession):
    """
    Override FastAPI's get_db so that it yields our test session
    instead of creating a brand new one from the real DB.
    """

    async def _override_get_db():
        yield session

    app.dependency_overrides[get_db] = _override_get_db
    yield  # tests will run after this
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(override_get_db_fixture) -> AsyncClient:  # type: ignore
    """
    Return an HTTPX AsyncClient that points to our FastAPI app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_user(async_client: AsyncClient) -> tuple[dict, dict]:
    user_data = {
        "nric": "S9999999J",
        "first_name": "john",
        "last_name": "doe",
        "email": "john.doe@example.com",
        "date_of_birth": "1990-01-01",  # 35 years old
        "gender": "M",
        "postal_code": "545078",
        "password": "password123",
        "password_confirm": "password123",
    }

    res: Response = await async_client.post(
        "/signup",
        json=user_data,
    )

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user, user_data


@pytest_asyncio.fixture
async def token(test_user: tuple[dict, dict]) -> str:
    return create_access_token({"user_id": test_user[0]["id"]})


@pytest_asyncio.fixture
async def authorized_client(async_client: AsyncClient, token: str) -> AsyncClient:
    async_client.headers = {**async_client.headers, "Authorization": f"Bearer {token}"}

    return async_client


@pytest_asyncio.fixture
async def authorized_client_for_no_vaccine_recommendations(async_client: AsyncClient):
    user_data = {"username": "jane.doe@example.com", "password": "password123"}
    res: Response = await async_client.post(
        "/login",
        data=user_data,
    )

    assert res.status_code == 200

    token = res.json().get("access_token")

    async_client.headers = {
        **async_client.headers,
        "Authorization": f"Bearer {token}",
    }

    return async_client


@pytest_asyncio.fixture
async def authorized_client_for_vaccine_records(async_client: AsyncClient):
    user_data = {"username": "test.user@example.com", "password": "testpassword123"}
    res: Response = await async_client.post(
        "/login",
        data=user_data,
    )

    assert res.status_code == 200

    token = res.json().get("access_token")

    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")

    async_client.headers = {
        **async_client.headers,
        "user_id": str(id),
        "Authorization": f"Bearer {token}",
    }

    return async_client
