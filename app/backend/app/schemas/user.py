from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr
from schemas.address import AddressResponse
from schemas.base import UserBase
from schemas.clinic import EnrolledClinicResponse


class UserResponse(UserBase):
    address: AddressResponse | None
    enrolled_clinic: EnrolledClinicResponse | None
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
