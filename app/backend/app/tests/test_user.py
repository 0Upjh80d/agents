from datetime import datetime

import pytest
from httpx import AsyncClient
from requests import Response
from schemas.user import UserResponse, UserUpdateResponse


@pytest.mark.asyncio
async def test_authorized_user_get_user(
    authorized_client: AsyncClient, test_user: tuple[dict, dict]
):
    res: Response = await authorized_client.get("/users")

    user = UserResponse(**res.json())

    assert res.status_code == 200
    assert user.nric == test_user[1]["nric"]
    assert user.first_name == test_user[1]["first_name"].capitalize()
    assert user.last_name == test_user[1]["last_name"].capitalize()
    assert user.email == test_user[1]["email"]
    assert (
        user.date_of_birth
        == datetime.strptime(test_user[1]["date_of_birth"], "%Y-%m-%d").date()
    )  # convert string to date
    assert user.gender.value == test_user[1]["gender"]  # convert Enum to string
    assert user.address.postal_code == test_user[1]["postal_code"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_email, update_postal_code, expected_address, expected_long, expected_lat",
    [
        (
            "updated.email@example.com",
            "768898",
            "2 YISHUN AVENUE 9 NATIONAL HEALTHCARE GROUP POLYCLINICS (YISHUN POLYCLINIC) SINGAPORE 768898",
            103.839190698939,
            1.43035851992416,
        ),
        (
            "updated.email@example.com",
            "569666",
            "21 ANG MO KIO CENTRAL 2 ANG MO KIO POLYCLINIC SINGAPORE 569666",
            103.845677779279,
            1.3743245905856,
        ),
    ],
)
async def test_authorized_user_update_user(
    authorized_client: AsyncClient,
    test_user: tuple[dict, dict],
    update_email: str,
    update_postal_code: str,
    expected_address: str,
    expected_long: float,
    expected_lat: float,
):
    res: Response = await authorized_client.put(
        "/users",
        json={
            "nric": test_user[1]["nric"],
            "first_name": test_user[1]["first_name"],
            "last_name": test_user[1]["last_name"],
            "email": update_email,
            "date_of_birth": test_user[1]["date_of_birth"],
            "gender": test_user[1]["gender"],
            "postal_code": test_user[1]["postal_code"],
            "enrolled_clinic_postal_code": update_postal_code,
        },
    )

    updated_user = UserUpdateResponse(**res.json())

    assert res.status_code == 200
    assert updated_user.email == update_email

    res: Response = await authorized_client.get("/users")

    user = UserResponse(**res.json())

    assert res.status_code == 200
    assert user.enrolled_clinic.address.postal_code == update_postal_code
    assert user.enrolled_clinic.address.address == expected_address
    assert user.enrolled_clinic.address.longitude == round(expected_long, 6)
    assert user.enrolled_clinic.address.latitude == round(expected_lat, 6)


@pytest.mark.asyncio
async def test_unauthorized_user_get_user(async_client: AsyncClient):
    res: Response = await async_client.get("/users")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthorized_user_update_user(async_client: AsyncClient):
    res: Response = await async_client.put("/users")
    assert res.status_code == 401
