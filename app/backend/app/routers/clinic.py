from auth.oauth2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from models.database import get_db
from models.models import Address, Clinic, User
from schemas.clinic import ClinicResponse
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/clinic", tags=["Clinic"])


@router.get(
    "/polyclinic/nearest",
    status_code=status.HTTP_200_OK,
    response_model=list[ClinicResponse],
)
async def get_nearest_polyclinic(
    polyclinic_limit: int = 3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    user_address_stmt = (
        select(Address.longitude, Address.latitude)
        .join(User.address)
        .where(User.id == current_user.id)
    )

    result = await db.execute(user_address_stmt)
    user_longitude, user_latitude = result.first()

    # Calculate the distance using the Haversine formula
    haversine_distance = func.pow(
        func.radians(Address.latitude - user_latitude), 2
    ) + func.pow(func.radians(Address.longitude - user_longitude), 2)

    # Query to fetch clinics ordered by distance
    stmt = (
        select(Clinic)
        .join(Clinic.address)
        .options(selectinload(Clinic.address))
        .add_columns(haversine_distance.label("distance"))
        .where(Clinic.type == "polyclinic")
        .order_by("distance")
        .limit(polyclinic_limit)
    )

    result = await db.execute(stmt)
    polyclinics = result.scalars().all()

    if not polyclinics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No polyclinics found.",
        )

    return polyclinics


@router.get(
    "/gp/nearest", status_code=status.HTTP_200_OK, response_model=list[ClinicResponse]
)
async def get_nearest_gp(
    gp_limit: int = 3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    user_address_stmt = (
        select(Address.longitude, Address.latitude)
        .join(User.address)
        .where(User.id == current_user.id)
    )

    result = await db.execute(user_address_stmt)
    user_longitude, user_latitude = result.first()

    # Calculate the distance using the Haversine formula
    haversine_distance = func.pow(
        func.radians(Address.latitude - user_latitude), 2
    ) + func.pow(func.radians(Address.longitude - user_longitude), 2)

    # Query to fetch clinics ordered by distance
    stmt = (
        select(Clinic)
        .join(Clinic.address)
        .options(selectinload(Clinic.address))
        .add_columns(haversine_distance.label("distance"))
        .where(Clinic.type == "gp")
        .order_by("distance")
        .limit(gp_limit)
    )

    result = await db.execute(stmt)
    gps = result.scalars().all()

    if not gps:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No general practitioners found.",
        )

    return gps
