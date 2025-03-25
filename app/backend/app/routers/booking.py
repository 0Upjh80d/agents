from datetime import datetime

from auth.oauth2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.database import get_db
from models.models import BookingSlot, Clinic, User, Vaccine, VaccineRecord
from schemas.booking import (
    AvailableSlotResponse,
    BookingSlotResponse,
    ScheduleSlotRequest,
)
from schemas.record import VaccineRecordResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/bookings", tags=["Booking"])


@router.get(
    "/available",
    status_code=status.HTTP_200_OK,
    response_model=list[AvailableSlotResponse],
)
async def get_available_booking_slots(
    vaccine_name: str,
    polyclinic_limit: int = 3,
    timeslot_limit: int = 1,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Step 1: Create a query to exclude already-booked slots
    booked_slots_subquery = select(VaccineRecord.booking_slot_id)

    # Step 2: Select booking slots NOT in VaccineRecord table
    stmt = (
        select(BookingSlot)
        .join(BookingSlot.vaccine)
        .join(BookingSlot.polyclinic)
        .options(selectinload(BookingSlot.polyclinic).selectinload(Clinic.address))
        .where(
            Vaccine.name == vaccine_name,
            BookingSlot.datetime
            >= datetime(2025, 3, 10),  # TODO: Hardcoded for development
            BookingSlot.id.notin_(booked_slots_subquery),
        )
        .order_by(BookingSlot.datetime.asc())
    )

    result = await db.execute(stmt)
    slots = result.scalars().all()

    if not slots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No available slots for {vaccine_name}.",
        )

    # Step 3: Group results by polyclinic (up to polyclinic_limit), each with up to timeslot_limit slots
    from collections import defaultdict

    polyclinic_slot_count = defaultdict(int)
    final_slots = []

    for slot in slots:
        # If number of recommended polyclinics exceeds the limit and polyclinic already exists inside,
        # we should still proceed with the logic to check if the recommended number of timeslots
        # for the polyclinic have exceeded the limit or not
        if (
            len(polyclinic_slot_count) >= polyclinic_limit
            and slot.polyclinic_id not in polyclinic_slot_count
        ):
            continue  # skip if we have reached the polyclinic limit and this polyclinic isn't counted yet

        # Check if recommended timeslots exceeded the limit for the recommended polyclinic
        if polyclinic_slot_count[slot.polyclinic_id] < timeslot_limit:
            final_slots.append(slot)
            polyclinic_slot_count[slot.polyclinic_id] += 1

    return final_slots


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=BookingSlotResponse,
)
async def get_booking_slot(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(BookingSlot)
        .options(
            selectinload(BookingSlot.polyclinic).selectinload(Clinic.address),
            selectinload(BookingSlot.vaccine),
        )
        .filter_by(id=id)
    )

    result = await db.execute(stmt)
    slot = result.scalars().first()

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slot with booking id {id} not found.",
        )

    return slot


@router.post(
    "/schedule",
    status_code=status.HTTP_201_CREATED,
    response_model=VaccineRecordResponse,
)
async def schedule_vaccination_slot(
    request: ScheduleSlotRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Step 1: Check if the booking slot already exists and isn't booked
    booking_slot_query = await db.execute(
        select(BookingSlot).where(BookingSlot.id == str(request.booking_slot_id))
    )
    booking_slot = booking_slot_query.scalar_one_or_none()

    if not booking_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking slot with slot id {str(request.booking_slot_id)} not found.",
        )

    # Step 2: Ensure this slot hasn't already been booked
    booked_result = await db.execute(
        select(VaccineRecord).where(
            VaccineRecord.booking_slot_id == str(request.booking_slot_id)
        )
    )
    existing_record = booked_result.scalar_one_or_none()

    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Slot already booked."
        )

    # Step 3: Create new VaccineRecord
    new_vaccine_record = VaccineRecord(
        user_id=current_user.id,
        booking_slot_id=str(request.booking_slot_id),
        status="booked",
    )

    # Step 4: Create the record in the database
    db.add(new_vaccine_record)
    # Flush inserts the object so it gets an ID, etc.
    await db.flush()
    # Refresh loads up-to-date data (like auto-generated IDs)
    await db.refresh(new_vaccine_record)
    # Finally commit the transaction
    await db.commit()

    return new_vaccine_record


@router.delete(
    "/cancel/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_vaccination_slot(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Step 1: Check if the VaccineRecord exists
    vaccine_record_query = await db.execute(
        select(VaccineRecord).where(VaccineRecord.id == record_id)
    )
    vaccine_record = vaccine_record_query.scalar_one_or_none()

    if not vaccine_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vaccine record with id {record_id} not found.",
        )

    # Step 2: Validate that the current user owns this VaccineRecord
    if vaccine_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to cancel this vaccination slot.",
        )

    # Step 3: Only allow deletion if status is 'booked'
    if vaccine_record.status != "booked":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel slot with status '{vaccine_record.status}'.",
        )

    # Step 3: Delete the record from the database
    await db.delete(vaccine_record)
    # Finally commit the transaction
    await db.commit()

    return JSONResponse(content={"detail": "Vaccination slot successfully cancelled."})
