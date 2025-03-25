from datetime import datetime, timezone

from auth.oauth2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.database import get_db
from models.models import Address, Clinic, User
from schemas.user import UserResponse, UserUpdate, UserUpdateResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/users", tags=["User"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def get_user(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(User)
        .outerjoin(Address, onclause=Address.id == User.address_id)
        .outerjoin(Clinic, onclause=Clinic.id == User.enrolled_clinic_id)
        .options(
            selectinload(User.address),
            selectinload(User.enrolled_clinic).selectinload(Clinic.address),
        )
        .filter(User.id == str(current_user.id))
    )

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user id {current_user.id} not found.",
        )

    return user


@router.put("", status_code=status.HTTP_200_OK, response_model=UserUpdateResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).filter_by(id=current_user.id)

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {current_user.id} not found.",
        )

    # Step 1: Get the address, if available
    stmt = select(Address).filter_by(postal_code=user_update.postal_code)

    result = await db.execute(stmt)
    address = result.scalars().first()

    # Step 2: Get the address of the enrolled clinic, if available
    stmt = (
        select(Clinic)
        .join(Address)
        .filter(Address.postal_code == user_update.enrolled_clinic_postal_code)
    )

    result = await db.execute(stmt)
    clinic = result.scalars().first()

    address_id = address.id if address else None
    clinic_id = clinic.id if clinic else None

    data = user_update.model_dump()
    for key, value in data.items():
        if key == "postal_code":
            setattr(user, "address_id", address_id)
        elif key == "enrolled_clinic_postal_code":
            setattr(user, "enrolled_clinic_id", clinic_id)
        elif hasattr(user, key):
            setattr(user, key, value)

    user.updated_at = datetime.now(timezone.utc)

    db.add(user)
    # Flush inserts the object so it gets an ID, etc.
    await db.flush()
    # Refresh loads up-to-date data (like auto-generated IDs)
    await db.refresh(user)
    # Finally commit the transaction
    await db.commit()

    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(id=id)

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user id {id} not found.",
        )

    # Delete the user in the database
    await db.delete(user)
    # Finally commit the transaction
    await db.commit()

    return JSONResponse(content={"detail": "User successfully deleted."})
