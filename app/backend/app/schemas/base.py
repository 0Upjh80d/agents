from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: date
    gender: str


class BookingSlotBase(BaseModel):
    id: int
    polyclinic_id: int
    vaccine_id: int
    datetime: datetime
