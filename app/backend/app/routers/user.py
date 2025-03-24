from auth.oauth2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.database import get_db
from models.models import User
from schemas.user import UserResponse, UserUpdate, UserUpdateResponse
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/users", tags=["User"])


@router.get("", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    stmt = select(User).filter_by(id=current_user.id)

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user id {current_user.id} not found.",
        )

    return user


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=UserUpdateResponse)
async def update_user(
    id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update this user.",
        )

    result = await db.execute(select(User).filter_by(id=id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found.",
        )

    for key, value in user_update.model_dump().items():
        setattr(user, key, value)

    user.updated_at = func.now()

    db.add(user)
    # Flush inserts the object so it gets an ID, etc.
    await db.flush()
    # Refresh loads up-to-date data (like auto-generated IDs)
    await db.refresh(user)
    # Finally commit the transaction
    await db.commit()

    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
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
