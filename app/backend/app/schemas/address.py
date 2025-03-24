from pydantic import BaseModel


class AddressResponse(BaseModel):
    postal_code: str
    address: str
    longitude: float
    latitude: float
