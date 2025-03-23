from fastapi import APIRouter, Depends, HTTPException, status
from models.database import get_db
from models.models import Polyclinic, Vaccine, VaccineStock
from schemas.stock import StockResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("", status_code=status.HTTP_200_OK, response_model=StockResponse)
async def get_vaccine_stock(
    vaccine_name: str,
    polyclinic_name: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(VaccineStock)
        .join(VaccineStock.vaccine)
        .join(VaccineStock.polyclinic)
        .filter(Vaccine.name == vaccine_name, Polyclinic.name == polyclinic_name)
    )
    result = await db.execute(stmt)
    stock = result.scalars().first()

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vaccine stock not found for {vaccine_name} at {polyclinic_name}.",
        )

    return stock
