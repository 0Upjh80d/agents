from datetime import datetime

from pydantic import BaseModel


class VaccineRecordResponse(BaseModel):
    id: int
    user_id: int
    booking_slot_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
