from pydantic import BaseModel


class PolyclinicResponse(BaseModel):
    id: int
    name: str
    address: str

    class Config:
        from_attributes = True
