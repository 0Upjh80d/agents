import pytest
from httpx import AsyncClient
from requests import Response
from schemas.vaccine import VaccineCriteriaResponse, VaccineResponse


@pytest.mark.asyncio
async def test_authorized_user_get_vaccine_recommendations(
    authorized_client: AsyncClient,
):
    res: Response = await authorized_client.get("/vaccines/recommendations")

    data = res.json()
    available_vaccines = [VaccineResponse(**vaccine) for vaccine in data]

    # authorized_client is Male, 35 years old (see conftest.py)
    for vaccine in available_vaccines:
        assert vaccine.name == "Influenza (INF)"

        # we should only criteria based on user's eligibility
        # see conftest.py for Influenza vaccine criterias
        assert len(vaccine.vaccine_criterias) == 1

        for criteria in vaccine.vaccine_criterias:

            assert isinstance(criteria, VaccineCriteriaResponse)
            assert criteria.age_criteria in ["18-64 years"]
            assert criteria.gender_criteria in ["None", "M", "F"]

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
