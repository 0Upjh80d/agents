import pytest
from httpx import AsyncClient
from requests import Response
from schemas.vaccine import VaccineResponse


@pytest.mark.asyncio
async def test_authorized_user_get_vaccine_recommendations(
    authorized_client: AsyncClient,
):
    res: Response = await authorized_client.get("/vaccines/recommendations")

    data = res.json()
    available_vaccines = [VaccineResponse(**vaccine) for vaccine in data]

    for vaccine in available_vaccines:
        assert vaccine.age_criteria in [
            "18+ years old",
            "65+ years old",
            "18-26 years old",
            "27-64 years old",
            # Additional criteria
        ]
        assert vaccine.gender_criteria in ["None", "M", "F"]
        assert (
            vaccine.name == "Influenza (INF)"
        )  # authorized_client is Male, 35 years old (see conftest.py)

    assert res.status_code == 200
    assert len(data) == len(available_vaccines)


@pytest.mark.asyncio
async def test_authorized_user_get_no_vaccine_recommendations(
    authorized_client_for_no_vaccine_recommendations: AsyncClient,
):
    res: Response = await authorized_client_for_no_vaccine_recommendations.get(
        "/vaccines/recommendations"
    )

    assert res.status_code == 404
    # authorized_client_for_no_vaccine_recommendations is Female, 17 years old (see conftest.py)
    # See data.sql for the available vaccines
    assert res.json().get("detail") == "No vaccine recommendations."


@pytest.mark.asyncio
async def test_unauthorized_user_get_vaccine_recommendations(async_client: AsyncClient):
    res: Response = await async_client.get("/vaccines/recommendations")

    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"
