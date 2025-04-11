from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.backend.app.schemas.address import AddressResponse
from app.backend.app.schemas.base import UserBase
from app.backend.app.schemas.clinic import ClinicResponse


class UserResponse(UserBase):
    address: AddressResponse | None
    enrolled_clinic: ClinicResponse | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    postal_code: str
    password: str
    password_confirm: str


class UserUpdate(UserBase):
    postal_code: str
    enrolled_clinic_postal_code: str


class UserCreateResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateResponse(BaseModel):
    id: UUID
    email: EmailStr
    updated_at: datetime

    class Config:
        from_attributes = True
