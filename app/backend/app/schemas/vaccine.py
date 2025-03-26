from uuid import UUID

from pydantic import BaseModel


class VaccineResponse(BaseModel):
    id: UUID
    name: str
    price: float
    doses_required: int
    age_criteria: str
    gender_criteria: str

    class Config:
        from_attributes = True
