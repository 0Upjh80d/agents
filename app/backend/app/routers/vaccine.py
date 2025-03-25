from datetime import datetime

from auth.oauth2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from models.database import get_db
from models.models import User, Vaccine
from schemas.vaccine import VaccineResponse
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/vaccines", tags=["Vaccine"])


@router.get(
    "/recommendations",
    status_code=status.HTTP_200_OK,
    response_model=list[VaccineResponse],
)
async def get_vaccine_recommendations_for_user(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user_age = (datetime.today().date() - current_user.date_of_birth).days // 365

    age_filters = or_(
        Vaccine.age_criteria.is_(None),
        and_(Vaccine.age_criteria == "18+ years old", user_age >= 18),
        and_(Vaccine.age_criteria == "65+ years old", user_age >= 65),
        and_(Vaccine.age_criteria == "18-26 years old", 18 <= user_age <= 26),
        and_(Vaccine.age_criteria == "27-64 years old", 27 <= user_age <= 64),
    )

    gender_filters = or_(
        Vaccine.gender_criteria.is_("None"),
        Vaccine.gender_criteria == current_user.gender,
    )

    stmt = select(Vaccine).filter(age_filters, gender_filters)

    result = await db.execute(stmt)
    available_vaccines = result.scalars().all()

    if not available_vaccines:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No vaccine recommendations."
        )

    return available_vaccines
