from datetime import datetime

from openai import BaseModel
from pydantic import EmailStr
from schemas.base import UserBase


class UserResponse(UserBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str
    password_confirm: str


class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
