from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.backend.app.auth.password import verify_password
from app.backend.app.core.config import settings
from app.backend.app.models.database import get_db
from app.backend.app.models.models import User
from app.backend.app.schemas.oauth2 import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(
    request: Request,
    data: dict,
    refresh: bool = False,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"refresh": refresh})
    to_encode.update({"exp": expire})
    SECRET_KEY = request.app.state.secret_key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(
    request: Request,
    token: str,
    credentials_exception: Exception,
) -> TokenData:
    try:
        SECRET_KEY = request.app.state.secret_key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        refresh = payload.get("refresh")
        if id is None or refresh:
            raise credentials_exception

        token_data = TokenData(id=id)

    except InvalidTokenError:
        raise credentials_exception

    return token_data


async def authenticate_user(
    user_credentials: OAuth2PasswordRequestForm, db: AsyncSession = Depends(get_db)
) -> User | bool:
    stmt = select(User).filter_by(email=user_credentials.username)

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        return False
    if not verify_password(user_credentials.password, user.password):
        return False
    return user


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(request, token, credentials_exception)

    stmt = select(User).filter_by(id=str(token_data.id))

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with user id {str(token_data.id)} not found.",
        )

    return user
