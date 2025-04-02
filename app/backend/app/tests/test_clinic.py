import pytest
from httpx import AsyncClient
from requests import Response
from schemas.clinic import ClinicResponse, ClinicType


@pytest.mark.asyncio
@pytest.mark.parametrize("clinic_limit", [1, 2])
async def test_authorized_user_get_nearest_polyclinic(
    authorized_client: AsyncClient,
    clinic_limit: int,
):
    params = {"clinic_type": "polyclinic", "clinic_limit": clinic_limit}
    res: Response = await authorized_client.get("/clinic/nearest", params=params)

    assert res.status_code == 200
    assert len(res.json()) == clinic_limit

    polyclinics = [ClinicResponse(**record) for record in res.json()]

    for polyclinic in polyclinics:
        assert polyclinic.type == ClinicType.POLYCLINIC


@pytest.mark.asyncio
@pytest.mark.parametrize("clinic_limit", [1, 2])
async def test_authorized_user_get_nearest_gp(
    authorized_client: AsyncClient,
    clinic_limit: int,
):
    params = {"clinic_type": "gp", "clinic_limit": clinic_limit}
    res: Response = await authorized_client.get("/clinic/nearest", params=params)

    assert res.status_code == 200
    assert len(res.json()) == clinic_limit

    gps = [ClinicResponse(**record) for record in res.json()]

    for gp in gps:
        assert gp.type == ClinicType.GENERAL_PRACTIONER


@pytest.mark.asyncio
@pytest.mark.parametrize("clinic_limit", [1, 2])
async def test_authorized_user_get_nearest_clinic(
    authorized_client: AsyncClient,
    clinic_limit: int,
):
    params = {"clinic_limit": clinic_limit}
    res: Response = await authorized_client.get("/clinic/nearest", params=params)

    assert res.status_code == 200
    assert len(res.json()) == clinic_limit


@pytest.mark.asyncio
async def test_unauthorized_user_get_nearest_clinic(async_client: AsyncClient):
    res: Response = await async_client.get("/clinic/nearest")
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"
