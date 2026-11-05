from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PriceCreate(BaseModel):
    commodity_id: int = Field(gt=0)
    location_id: int = Field(gt=0)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    recorded_at: date


class PriceUpdate(BaseModel):
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    recorded_at: date | None = None


class PriceResponse(BaseModel):
    id: int
    commodity_id: int
    location_id: int
    price: Decimal
    recorded_at: date
    data_source: str
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
