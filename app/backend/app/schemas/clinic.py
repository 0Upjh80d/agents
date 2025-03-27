from enum import Enum
from uuid import UUID

from pydantic import BaseModel
from schemas.address import AddressResponse


class ClinicType(Enum):
    POLYCLINIC = "polyclinic"
    GENERAL_PRACTIONER = "gp"


class PolyclinicResponse(BaseModel):
    id: UUID
    name: str
    address: AddressResponse

    class Config:
        from_attributes = True


class ClinicResponse(BaseModel):
    name: str
    type: ClinicType
    address: AddressResponse

    class Config:
        from_attributes = True
