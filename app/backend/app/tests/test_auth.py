import jwt
import pytest
from core.config import settings
from httpx import AsyncClient
from requests import Response
from schemas.oauth2 import Token
from schemas.user import UserCreateResponse

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


@pytest.mark.asyncio
async def test_successful_create_user(async_client: AsyncClient):
    res: Response = await async_client.post(
        "/signup",
        json={
            "nric": "S9999999J",
            "first_name": "john",
            "last_name": "doe",
            "email": "john.doe@example.com",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "postal_code": "545078",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    new_user = UserCreateResponse(**res.json())
    assert res.status_code == 201
    assert new_user.email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_unsuccessful_create_existing_user(
    async_client: AsyncClient, test_user: tuple[dict, dict]
):
    res: Response = await async_client.post(
        "/signup",
        json={
            "nric": "S9999999J",
            "first_name": "john",
            "last_name": "doe",
            "email": "john.doe@example.com",
            "date_of_birth": "1990-01-01",
            "gender": "M",
            "postal_code": "545078",
            "password": "password123",
            "password_confirm": "password123",
        },
    )

    assert res.status_code == 409
    assert res.json().get("detail") == "User with email or NRIC already exists."


@pytest.mark.asyncio
async def test_successful_login(
    async_client: AsyncClient, test_user: tuple[dict, dict]
):
    res: Response = await async_client.post(
        "/login",
        data={
            "username": test_user[0]["email"],
            "password": test_user[0]["password"],
        },
    )

    data = res.json()

    token = Token(**data)
    payload = jwt.decode(
        token.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    id = payload.get("user_id")

    assert res.status_code == 200
    assert id == test_user[0]["id"]
    assert token.token_type == "bearer"
    assert data.get("detail") == "Login successful."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, password, expected_status, expected_detail",
    [
        (
            "john.doe@example.com",
            "wrongpassword",
            401,
            "Incorrect username or password.",
        ),
        (
            "userdoesnotexist@example.com",
            "password123",
            401,
            "Incorrect username or password.",
        ),
    ],
)
async def test_unsuccessful_login(
    async_client: AsyncClient,
    test_user: tuple[dict, dict],
    email: str,
    password: str,
    expected_status: int,
    expected_detail: str,
):
    res: Response = await async_client.post(
        "/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert res.status_code == expected_status
    assert res.json().get("detail") == expected_detail
