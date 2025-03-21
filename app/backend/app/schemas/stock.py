from pydantic import BaseModel


class StockResponse(BaseModel):
    stock_quantity: int

    class Config:
        from_attributes = True
