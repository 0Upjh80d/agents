from schemas.base import UserBase


class UserResponse(UserBase):

    class Config:
        from_attributes = True
