from datetime import datetime

from pydantic import BaseModel
from schemas.base import BookingSlotBase
from schemas.polyclinic import PolyclinicResponse
from schemas.vaccine import VaccineResponse


class ScheduleSlotRequest(BaseModel):
    user_id: int
    booking_slot_id: int


class CancelSlotRequest(BaseModel):
    vaccine_record_id: int


class BookingSlotResponse(BookingSlotBase):
    id: int
    datetime: datetime
    polyclinic: PolyclinicResponse
    vaccine: VaccineResponse

    class Config:
        from_attributes = True


class AvailableSlotResponse(BaseModel):
    id: int
    datetime: datetime
    vaccine_id: int
    polyclinic: PolyclinicResponse

    class Config:
        from_attributes = True
