from datetime import datetime

from auth.oauth2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from models.database import get_db
from models.models import User, Vaccine, VaccineCriteria
from schemas.vaccine import VaccineResponse
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import contains_eager

router = APIRouter(prefix="/vaccines", tags=["Vaccine"])


@router.get(
    "/recommendations",
    status_code=status.HTTP_200_OK,
    response_model=list[VaccineResponse],
)
async def get_vaccine_recommendations_for_user(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):

    user_age_years = (datetime.today().date() - current_user.date_of_birth).days // 365

    user_age_months = (datetime.today().date() - current_user.date_of_birth).days // 30

    age_filters = or_(
        VaccineCriteria.age_criteria.is_(None),
        and_(VaccineCriteria.age_criteria == "0 months", user_age_months == 0),
        and_(VaccineCriteria.age_criteria == "2 months", user_age_months == 2),
        and_(VaccineCriteria.age_criteria == "4 months", user_age_months == 4),
        and_(VaccineCriteria.age_criteria == "6 months", user_age_months == 6),
        and_(VaccineCriteria.age_criteria == "12 months", user_age_months == 12),
        and_(VaccineCriteria.age_criteria == "15 months", user_age_months == 15),
        and_(VaccineCriteria.age_criteria == "18 months", user_age_months == 18),
        and_(VaccineCriteria.age_criteria == "6-59 months", 6 <= user_age_months <= 59),
        and_(VaccineCriteria.age_criteria == "10-11 years", 10 <= user_age_years <= 11),
        and_(VaccineCriteria.age_criteria == "12-13 years", 12 <= user_age_years <= 13),
        and_(VaccineCriteria.age_criteria == "13-14 years", 13 <= user_age_years <= 14),
        and_(VaccineCriteria.age_criteria == "2-17 years", 2 <= user_age_years <= 17),
        and_(VaccineCriteria.age_criteria == "5-17 years", 5 <= user_age_years <= 17),
        and_(VaccineCriteria.age_criteria == "18+ years", user_age_years >= 18),
        and_(VaccineCriteria.age_criteria == "18-26 years", 18 <= user_age_years <= 26),
        and_(VaccineCriteria.age_criteria == "18-64 years", 18 <= user_age_years <= 64),
        and_(VaccineCriteria.age_criteria == "65+ years", user_age_years >= 65),
    )

    gender_filters = or_(
        VaccineCriteria.gender_criteria.is_("None"),
        VaccineCriteria.gender_criteria == current_user.gender,
    )

    stmt = (
        select(Vaccine)
        .join(Vaccine.vaccine_criterias)
        .options(contains_eager(Vaccine.vaccine_criterias))
        .filter(age_filters, gender_filters)
    )

    result = await db.execute(stmt)
    available_vaccines = result.scalars().unique()

    if not available_vaccines:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No vaccine recommendations."
        )

    return available_vaccines
