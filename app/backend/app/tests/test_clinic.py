import pytest
from httpx import AsyncClient
from requests import Response
from schemas.clinic import ClinicResponse, ClinicType


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "clinic_type, clinic_limit",
    [("polyclinic", 1), ("polyclinic", 2), ("gp", 1), ("gp", 2), (None, 1), (None, 2)],
)
async def test_authorized_user_get_nearest(
    authorized_client: AsyncClient,
    clinic_type: str,
    clinic_limit: int,
):
    params = {"clinic_limit": clinic_limit}

    if clinic_type:
        params["clinic_type"] = clinic_type

    res: Response = await authorized_client.get("/clinics/nearest", params=params)

    assert res.status_code == 200
    assert len(res.json()) == clinic_limit

    clinics = [ClinicResponse(**record) for record in res.json()]

    for clinic in clinics:
        if clinic_type == ClinicType.POLYCLINIC.value:  # Get nearest polyclinic
            assert clinic.type == ClinicType.POLYCLINIC
        elif clinic_type == ClinicType.GENERAL_PRACTIONER.value:  # Get nearest GP
            assert clinic.type == ClinicType.GENERAL_PRACTIONER
        else:
            # If none, check that the type is either POLYCLINIC or GENERAL_PRACTIONER only
            assert clinic.type in {ClinicType.POLYCLINIC, ClinicType.GENERAL_PRACTIONER}


@pytest.mark.asyncio
async def test_unauthorized_user_get_nearest_clinic(async_client: AsyncClient):
    res: Response = await async_client.get("/clinics/nearest")
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"
