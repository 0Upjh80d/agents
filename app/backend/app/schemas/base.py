from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr


class Gender(str, Enum):
    Male = "Male"
    Female = "Female"


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: date
    gender: Gender


class BookingSlotBase(BaseModel):
    id: int
    polyclinic_id: int
    vaccine_id: int
    datetime: datetime
