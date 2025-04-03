from typing import List
from uuid import UUID

from pydantic import BaseModel


class VaccineCriteriaResponse(BaseModel):
    age_criteria: str
    gender_criteria: str
    health_condition_criteria: str
    doses_required: int
    frequency: str

    class Config:
        from_attributes = True


class VaccineResponse(BaseModel):
    id: UUID
    name: str
    vaccine_criterias: List[VaccineCriteriaResponse]

    class Config:
        from_attributes = True
