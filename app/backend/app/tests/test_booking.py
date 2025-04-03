import pytest
from httpx import AsyncClient
from requests import Response
from schemas.booking import BookingSlotResponse
from schemas.record import VaccineRecordResponse


# ============================================================================
# Get all slots
# TODO: user without address (when staging merged)
# TODO: distance increasing (when staging merged)
# ============================================================================
@pytest.mark.asyncio
async def test_get_all_available_booking_slots(
    async_client: AsyncClient,
):
    params = {"vaccine_name": "Influenza (INF)"}
    res: Response = await async_client.get("/bookings/available", params=params)

    assert res.status_code == 200


# ============================================================================
# Get 1 valid slot
# ============================================================================
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "slot_id, expected_vaccine",
    [
        # See data.sql for the available records
        ("97ba51db-48d8-4873-b1ee-57a9b7f766f0", "Influenza (INF)"),
        ("21b89cd2-f99c-4113-bb46-5cc21d566b97", "Human Papillomavirus (HPV)"),
    ],
)
async def test_valid_booking_slot(
    async_client: AsyncClient, slot_id: str, expected_vaccine: str
):
    res: Response = await async_client.get(f"/bookings/{slot_id}")

    assert res.status_code == 200
    slot = BookingSlotResponse(**res.json())
    assert str(slot.id) == slot_id
    assert slot.vaccine.name == expected_vaccine


# ============================================================================
# Get 1 invalid slot
# ============================================================================
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "slot_id",
    [
        # See data.sql for the available records
        "b6732344-bc30-4401-9a69-b91e28273b8d",  # vaccine record id, hence invalid
        "invalid-id-2",
    ],
)
async def test_invalid_booking_slot(async_client: AsyncClient, slot_id: str):
    res: Response = await async_client.get(f"/bookings/{slot_id}")

    assert res.status_code == 404
    assert res.json().get("detail") == f"Slot with booking id {slot_id} not found."


# ============================================================================
# TODO: authorised user valid schedule
# ============================================================================
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "slot_id",
    [
        # See data.sql for the available records
        "213fa5e7-abbb-4e55-bccc-318db42ace81",
        "e7bbc307-ae75-4854-bd91-d6851ae085fd",
    ],
)
async def test_authorized_user_valid_schedule(
    authorized_client_for_scheduling: AsyncClient, slot_id: str
):
    json_body = {"booking_slot_id": slot_id}
    res: Response = await authorized_client_for_scheduling.post(
        "/bookings/schedule", json=json_body
    )

    assert res.status_code == 201

    booked_slot = VaccineRecordResponse(**res.json())
    assert str(booked_slot.booking_slot_id) == slot_id
    assert (
        str(booked_slot.user_id) == authorized_client_for_scheduling.headers["user_id"]
    )
    assert booked_slot.status.value == "booked"


# ============================================================================
# TODO: authorised user invalid schedule (booked alr or invalid id)
# ============================================================================
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "slot_id, expected_status_code, expected_error_message",
    [
        # Invalid UUID:
        (
            "97ba51db-48d8-4873-b1ee-57a9b7f766fa",
            404,
            "Booking slot with slot id 97ba51db-48d8-4873-b1ee-57a9b7f766fa not found.",
        ),
        # Valid ID, booked by other user:
        ("97ba51db-48d8-4873-b1ee-57a9b7f766f0", 400, "Slot already booked."),
        # Invalid ID, unprocessible entity:
        (
            "invalid-id-3",
            422,
            "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `i` at 1",
        ),
    ],
)
async def test_authorized_user_invalid_schedule(
    authorized_client_for_scheduling: AsyncClient,
    slot_id: str,
    expected_status_code: int,
    expected_error_message: str,
):
    json_body = {"booking_slot_id": slot_id}

    res: Response = await authorized_client_for_scheduling.post(
        "/bookings/schedule", json=json_body
    )

    assert res.status_code == expected_status_code

    error_response = res.json()

    # Error: 422 Unprocessable Entity
    if res.status_code == 422:
        error_messages = [error.get("msg") for error in error_response["detail"]]
        assert error_messages[0] == expected_error_message

    # Other Errors: 400, 404
    else:
        assert error_response.get("detail") == expected_error_message


# ============================================================================
# TODO: unauthorised user schedule
# ============================================================================
@pytest.mark.asyncio
async def test_unauthorized_user_schedule(async_client: AsyncClient):

    slot_id = "97ba51db-48d8-4873-b1ee-57a9b7f766f0"
    json_body = {"booking_slot_id": slot_id}
    res: Response = await async_client.post("/bookings/schedule", json=json_body)

    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"


# ============================================================================
# TODO: authorised user valid cancel
# ============================================================================
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "record_id",
    [
        # See data.sql for the available records
        "b6732344-bc30-4401-9a69-b91e28273b8d",
        # "7eb3a1a2-dd8c-4cd7-84d5-cd5621ab4fc1"
    ],
)
async def test_authorized_user_valid_cancel(
    authorized_client_for_vaccine_records: AsyncClient, record_id: str
):

    res = await authorized_client_for_vaccine_records.delete(
        f"/bookings/cancel/{record_id}"
    )

    assert res.status_code == 200
    assert res.json().get("detail") == "Vaccination slot successfully cancelled."


# ============================================================================
# TODO: authorised user invalid cancel
# ============================================================================
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "record_id, expected_status, expected_detail",
    [
        # Unauthorized - user doesn't have permission to cancel this record
        (
            "b6732344-bc30-4401-9a69-b91e28273b8d",
            401,
            "You are not authorized to cancel this vaccination slot.",
        ),
        # Not found - non-existent record
        (
            "7eb3a1a2-dd8c-4cd7-84d5-cd5621ab4fc2",
            404,
            "Vaccine record with id 7eb3a1a2-dd8c-4cd7-84d5-cd5621ab4fc2 not found.",
        ),
        ("invalid-id-4", 404, "Vaccine record with id invalid-id-4 not found."),
    ],
)
async def test_authorized_user_invalid_record_cancel(
    authorized_client_for_scheduling: AsyncClient,
    record_id: str,
    expected_status: int,
    expected_detail: str,
):
    # Send request to cancel the record
    res = await authorized_client_for_scheduling.delete(f"/bookings/cancel/{record_id}")

    # Assert the expected status code
    assert res.status_code == expected_status

    # Assert the error detail message
    assert res.json().get("detail") == expected_detail


# ============================================================================
# TODO: unauthorised user cancel
# ============================================================================
@pytest.mark.asyncio
async def test_unauthorized_user_cancel(async_client: AsyncClient):

    record_id = "b6732344-bc30-4401-9a69-b91e28273b8d"
    json_body = {"booking_slot_id": record_id}
    res: Response = await async_client.post("/bookings/schedule", json=json_body)

    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"


# ============================================================================
# TODO: authorised user valid reschedule
# ============================================================================
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "record_id, new_slot_id",
    [
        # See data.sql for the available records
        (
            "b6732344-bc30-4401-9a69-b91e28273b8d",
            "213fa5e7-abbb-4e55-bccc-318db42ace81",
        ),
    ],
)
async def test_authorized_user_valid_reschedule(
    authorized_client_for_vaccine_records: AsyncClient, record_id: str, new_slot_id: str
):
    json_body = {"vaccine_record_id": record_id, "new_slot_id": new_slot_id}
    res: Response = await authorized_client_for_vaccine_records.post(
        "/bookings/reschedule", json=json_body
    )

    assert res.status_code == 200

    rescheduled_slot = VaccineRecordResponse(**res.json())

    assert str(rescheduled_slot.id) == record_id
    assert str(rescheduled_slot.booking_slot_id) == new_slot_id
    assert rescheduled_slot.status.value == "booked"
    assert (
        str(rescheduled_slot.user_id)
        == authorized_client_for_vaccine_records.headers["user_id"]
    )


# ============================================================================
# TODO: authorised user invalid reschedule (reschule slot or new slot invalid)
# ============================================================================
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "record_id, new_slot_id, expected_status, expected_error_message",
    [
        # Not my record (belongs to another user)
        (
            "b6732344-bc30-4401-9a69-b91e28273b8d",  # Valid record, but belongs to another user
            "213fa5e7-abbb-4e55-bccc-318db42ace81",  # Valid slot id
            401,  # Unauthorized
            "You are not authorized to cancel this vaccination slot.",
        ),
        # My record, but slot already booked by someone else
        (
            "a6578d08-4e81-40ca-bc30-c9f2d01024aa",  # Valid record that belongs to user
            "97ba51db-48d8-4873-b1ee-57a9b7f766f0",  # Slot already booked
            400,
            "Slot already booked",
        ),
        # My record, but invalid slot id (doesn't exist)
        (
            "a6578d08-4e81-40ca-bc30-c9f2d01024aa",  # Valid record that belongs to user
            "00000000-0000-0000-0000-000000000000",  # Non-existent slot
            404,  # Not found
            "Booking slot with ID 00000000-0000-0000-0000-000000000000 not found.",
        ),
        # Invalid record id (doesn't exist)
        (
            "00000000-0000-0000-0000-000000000000",  # Non-existent record
            "213fa5e7-abbb-4e55-bccc-318db42ace81",  # Valid slot id
            404,  # Not found
            "Vaccine record with id 00000000-0000-0000-0000-000000000000 not found.",
        ),
    ],
)
async def test_authorized_user_invalid_reschedule(
    authorized_client_for_scheduling: AsyncClient,  # TODO: CHANGE CLEINT
    record_id: str,
    new_slot_id: str,
    expected_status: int,
    expected_error_message: str,
):
    json_body = {"vaccine_record_id": record_id, "new_slot_id": new_slot_id}

    res: Response = await authorized_client_for_scheduling.post(
        "/bookings/reschedule", json=json_body
    )

    # Assert status code
    assert res.status_code == expected_status

    # Assert error message
    response_data = res.json()
    assert "detail" in response_data
    assert expected_error_message in response_data["detail"]


# ============================================================================
# TODO: unauthorised user reschedule
# ============================================================================
@pytest.mark.asyncio
async def test_unauthorized_user_reschedule(async_client: AsyncClient):

    record_id = "b6732344-bc30-4401-9a69-b91e28273b8d"
    new_slot_id = "213fa5e7-abbb-4e55-bccc-318db42ace81"
    json_body = {"vaccine_record_id": record_id, "new_slot_id": new_slot_id}
    res: Response = await async_client.post("/bookings/reschedule", json=json_body)

    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"
