from uuid import UUID

from pydantic import BaseModel
from schemas.base import BookingSlotBase
from schemas.vaccine import VaccineResponse


class ScheduleSlotRequest(BaseModel):
    booking_slot_id: UUID


class CancelSlotRequest(BaseModel):
    vaccine_record_id: UUID


class BookingSlotResponse(BookingSlotBase):
    vaccine: VaccineResponse

    class Config:
        from_attributes = True


class RescheduleSlotRequest(BaseModel):
    vaccine_record_id: UUID
    new_slot_id: UUID


class AvailableSlotResponse(BookingSlotBase):
    vaccine_id: UUID

    class Config:
        from_attributes = True
