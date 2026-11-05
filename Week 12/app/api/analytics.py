
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models import Commodity, User
from app.services.analytics_service import (
    get_overview,
    compare_prices,
    calculate_price_changes,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_overview(db)


@router.get("/compare")
def analytics_compare(
    commodity_id: int = Query(gt=0),
    recorded_at: date = Query(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    commodity = db.get(Commodity, commodity_id)

    if commodity is None:
        raise HTTPException(
            status_code=404,
            detail="Commodity not found",
        )

    results = compare_prices(
        db,
        commodity_id,
        recorded_at,
    )

    return {
        "commodity": commodity.name,
        "recorded_at": recorded_at,
        "results": results,
    }


@router.get("/changes")
def analytics_changes(
    commodity_id: int = Query(gt=0),
    start_date: date = Query(),
    end_date: date = Query(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date",
        )

    commodity = db.get(Commodity, commodity_id)

    if commodity is None:
        raise HTTPException(
            status_code=404,
            detail="Commodity not found",
        )

    results = calculate_price_changes(
        db,
        commodity_id,
        start_date,
        end_date,
    )

    return {
        "commodity": commodity.name,
        "start_date": start_date,
        "end_date": end_date,
        "results": results,
    }
