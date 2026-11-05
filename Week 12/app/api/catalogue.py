from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models import Commodity, Location, User

router = APIRouter(
    tags=["Catalogue"],
)


@router.get("/commodities")
def get_commodities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    commodities = db.scalars(
        select(Commodity).order_by(Commodity.name)
    ).all()

    return [
        {
            "id": commodity.id,
            "name": commodity.name,
            "category": commodity.category,
            "unit": commodity.unit,
        }
        for commodity in commodities
    ]


@router.get("/locations")
def get_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    locations = db.scalars(
        select(Location).order_by(Location.city)
    ).all()

    return [
        {
            "id": location.id,
            "city": location.city,
            "state": location.state,
        }
        for location in locations
    ]
