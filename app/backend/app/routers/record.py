from fastapi import APIRouter, Depends, HTTPException, status
from models.database import get_db
from models.models import BookingSlot, VaccineRecord
from schemas.record import VaccineRecordResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/records", tags=["Record"])


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=VaccineRecordResponse,
)
async def get_vaccine_record(id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(VaccineRecord)
        .join(BookingSlot)
        .options(
            selectinload(VaccineRecord.booking_slot).selectinload(BookingSlot.vaccine),
            selectinload(VaccineRecord.booking_slot).selectinload(
                BookingSlot.polyclinic
            ),
        )
        .filter(VaccineRecord.id == id)
    )

    result = await db.execute(stmt)
    record = result.scalars().first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with record id {id} not found.",
        )

    return record
