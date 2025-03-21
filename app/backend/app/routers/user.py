from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from models.database import get_db
from models.models import BookingSlot, User, Vaccine, VaccineRecord
from schemas.record import VaccineRecordResponse
from schemas.user import UserResponse
from schemas.vaccine import VaccineResponse
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(id=id)

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user id {id} not found.",
        )

    return user


@router.get(
    "/records/{id}",
    status_code=status.HTTP_200_OK,
    response_model=list[VaccineRecordResponse],
)
async def get_user_vaccination_records(id: int, db: AsyncSession = Depends(get_db)):
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
        .filter(User.id == id)
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
    "/recommend/{id}",
    status_code=status.HTTP_200_OK,
    response_model=list[VaccineResponse],
)
async def get_vaccine_recommendations_for_user(
    id: int, db: AsyncSession = Depends(get_db)
):
    stmt = select(User).filter_by(id=id)

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user id {id} not found.",
        )

    user_age = (datetime.today().date() - user.date_of_birth).days // 365

    age_filters = or_(
        Vaccine.age_criteria.is_(None),
        and_(Vaccine.age_criteria == "18+ years old", user_age >= 18),
        and_(Vaccine.age_criteria == "65+ years old", user_age >= 65),
        and_(Vaccine.age_criteria == "18-26 years old", 18 <= user_age <= 26),
        and_(Vaccine.age_criteria == "27-64 years old", 27 <= user_age <= 64),
    )

    gender_filters = or_(
        Vaccine.gender_criteria.is_("None"),
        and_(Vaccine.gender_criteria == "Female", user.gender == "F"),
        and_(Vaccine.gender_criteria == "Male", user.gender == "M"),
    )

    stmt = select(Vaccine).filter(age_filters, gender_filters)

    result = await db.execute(stmt)
    available_vaccines = result.scalars().all()

    if not available_vaccines:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No vaccine recommendations."
        )

    return available_vaccines
