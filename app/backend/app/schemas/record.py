from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class Status(Enum):
    BOOKED = "booked"
    COMPLETED = "completed"


class VaccineRecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    booking_slot_id: UUID
    status: Status
    created_at: datetime

    class Config:
        from_attributes = True
