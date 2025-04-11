from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.backend.app.auth.oauth2 import get_current_user
from app.backend.app.models.database import get_db
from app.backend.app.models.models import BookingSlot, User, VaccineRecord
from app.backend.app.schemas.record import VaccineRecordResponse

router = APIRouter(prefix="/records", tags=["Record"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[VaccineRecordResponse],
)
async def get_user_vaccination_records(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # If valid, set request.state.user_id
    request.state.user_id = current_user.id

    stmt = (
        select(VaccineRecord)
        .join(User, onclause=VaccineRecord.user_id == User.id)
        .join(BookingSlot, onclause=VaccineRecord.booking_slot_id == BookingSlot.id)
        .options(
            selectinload(VaccineRecord.booking_slot).selectinload(BookingSlot.vaccine),
            selectinload(VaccineRecord.booking_slot).selectinload(
                BookingSlot.polyclinic
            ),
        )
        .filter(User.id == current_user.id)
        .order_by(BookingSlot.datetime.desc())
    )

    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No records found."
        )

    return records


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=VaccineRecordResponse,
)
async def get_user_vaccination_record(
    request: Request,
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # If valid, set request.state.user_id
    request.state.user_id = current_user.id

    stmt = (
        select(VaccineRecord)
        .join(BookingSlot)
        .options(
            selectinload(VaccineRecord.booking_slot).selectinload(BookingSlot.vaccine),
            selectinload(VaccineRecord.booking_slot).selectinload(
                BookingSlot.polyclinic
            ),
        )
        .filter(VaccineRecord.id == id, VaccineRecord.user_id == current_user.id)
    )

    result = await db.execute(stmt)
    record = result.scalars().first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with record id {id} not found.",
        )

    return record
