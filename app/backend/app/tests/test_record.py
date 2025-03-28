import pytest
from httpx import AsyncClient
from requests import Response
from schemas.record import VaccineRecordResponse


@pytest.mark.asyncio
async def test_authorized_user_no_vaccination_records(
    authorized_client: AsyncClient,
):
    res: Response = await authorized_client.get("/records")

    assert res.status_code == 404
    assert res.json().get("detail") == "No records found."


@pytest.mark.asyncio
async def test_authorized_user_get_vaccination_records(
    authorized_client_for_vaccine_records: AsyncClient,
):
    res: Response = await authorized_client_for_vaccine_records.get("/records")

    data = res.json()
    records = [VaccineRecordResponse(**record) for record in data]

    for record in records:
        assert (
            str(record.user_id)
            == authorized_client_for_vaccine_records.headers["user_id"]
        )
        # .value for Enum to get string
        assert record.status.value in ["booked", "completed"]

    assert res.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id",
    [
        # See data.sql for the available records
        "b6732344-bc30-4401-9a69-b91e28273b8d",
        "invalid-id",
    ],
)
async def test_authorized_user_invalid_vaccination_record(
    authorized_client: AsyncClient, id: str
):
    res: Response = await authorized_client.get(f"/records/{id}")

    assert res.status_code == 404
    assert res.json().get("detail") == f"Record with record id {id} not found."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id",
    [
        # See data.sql for the available records
        "b6732344-bc30-4401-9a69-b91e28273b8d",
        "7eb3a1a2-dd8c-4cd7-84d5-cd5621ab4fc1",
    ],
)
async def test_authorized_user_get_vaccination_record(
    authorized_client_for_vaccine_records: AsyncClient, id: str
):
    res: Response = await authorized_client_for_vaccine_records.get(f"/records/{id}")

    record = VaccineRecordResponse(**res.json())

    assert (
        str(record.user_id) == authorized_client_for_vaccine_records.headers["user_id"]
    )
    # .value for Enum to get string
    assert record.status.value in ["booked", "completed"]

    assert res.status_code == 200


@pytest.mark.asyncio
async def test_unauthorized_user_get_vaccination_records(async_client: AsyncClient):
    res: Response = await async_client.get("/records")
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"


@pytest.mark.asyncio
async def test_unauthorized_user_get_vaccination_record(async_client: AsyncClient):
    res: Response = await async_client.get("/records/some-id")
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"
