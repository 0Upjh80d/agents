from uuid import UUID

from pydantic import BaseModel
from schemas.address import AddressResponse


class PolyclinicResponse(BaseModel):
    id: UUID
    name: str
    address: AddressResponse

    class Config:
        from_attributes = True
