from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.backend.app.auth.oauth2 import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
)
from app.backend.app.auth.password import hash_password, verify_password
from app.backend.app.models.database import get_db
from app.backend.app.models.models import Address, User
from app.backend.app.schemas.oauth2 import Token
from app.backend.app.schemas.user import UserCreate, UserCreateResponse

router = APIRouter(tags=["Authentication"])


@router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserCreateResponse
)
async def signup(
    request: Request, user: UserCreate, db: AsyncSession = Depends(get_db)
):

    stmt = select(User).filter(or_(User.email == user.email, User.nric == user.nric))

    result = await db.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email or NRIC already exists.",
        )

    if user.password != user.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and password confirmation do not match.",
        )

    stmt = select(Address).filter_by(postal_code=user.postal_code)

    result = await db.execute(stmt)
    address = result.scalars().first()

    # Hash the password
    hashed_password = hash_password(user.password)
    # Set password to hashed password
    user.password = hashed_password

    data = user.model_dump()
    if address:
        data["address"] = address
    data.pop("postal_code", None)
    data.pop("password_confirm", None)  # Don't raise error if it's not there

    new_user = User(**data)

    # If valid, set request.state.user_id
    request.state.user_id = new_user.id

    # Create the user in the database
    db.add(new_user)
    # Flush inserts the object so it gets an ID, etc.
    await db.flush()
    # Refresh loads up-to-date data (like auto-generated IDs)
    await db.refresh(new_user)
    # Finally commit the transaction
    await db.commit()

    return new_user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(user_credentials, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If valid, set request.state.user_id
    request.state.user_id = user.id

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Create access token
    access_token = create_access_token(
        request,
        data={
            "user_id": user.id
        },  # TODO: Add a specific set of permissions to a JWT token
        expires_delta=access_token_expires,
    )
    # TODO: Create refresh token

    # Return access token
    return JSONResponse(
        content={
            "detail": "Login successful.",
            "access_token": access_token,
            # "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )
