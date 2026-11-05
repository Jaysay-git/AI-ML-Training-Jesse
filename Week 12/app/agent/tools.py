
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import Commodity, Location, Price
from app.services.analytics_service import (
    compare_prices as compare_prices_service,
    calculate_price_changes as calculate_price_changes_service,
)


def lookup_commodity(
    db: Session,
    commodity_name: str,
    recorded_at: date | None = None,
    city: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    commodity = db.scalar(
        select(Commodity).where(
            func.lower(Commodity.name) == commodity_name.strip().lower()
        )
    )

    if commodity is None:
        return {
            "found": False,
            "message": f"Commodity '{commodity_name}' was not found.",
        }

    query = (
        select(
            Commodity.name.label("commodity"),
            Commodity.category,
            Commodity.unit,
            Location.city,
            Location.state,
            Price.price,
            Price.recorded_at,
            Price.data_source,
        )
        .join(Price, Price.commodity_id == Commodity.id)
        .join(Location, Price.location_id == Location.id)
        .where(Commodity.id == commodity.id)
    )

    # Exact-date lookup takes priority.
    if recorded_at is not None:
        query = query.where(Price.recorded_at == recorded_at)

    # Monthly or custom date-range lookup.
    elif start_date is not None and end_date is not None:
        query = query.where(
            Price.recorded_at >= start_date,
            Price.recorded_at <= end_date,
        )

    # If no date is supplied, retrieve the latest available date.
    elif start_date is None and end_date is None:
        latest_date = (
            select(func.max(Price.recorded_at))
            .where(Price.commodity_id == commodity.id)
            .scalar_subquery()
        )
        query = query.where(Price.recorded_at == latest_date)

    # Optional city filter.
    if city is not None:
        query = query.where(
            func.lower(Location.city) == city.strip().lower()
        )

    query = query.order_by(
        Price.recorded_at.desc(),
        Location.city,
    )

    results = db.execute(query).all()

    return {
        "found": bool(results),
        "commodity": commodity.name,
        "category": commodity.category,
        "unit": commodity.unit,
        "records": [
            {
                "city": row.city,
                "state": row.state,
                "price": float(row.price),
                "recorded_at": row.recorded_at.isoformat(),
                "data_source": row.data_source,
            }
            for row in results
        ],
        "message": (
            "Price records retrieved successfully."
            if results
            else "No price records matched the requested filters."
        ),
    }


def compare_prices(
    db: Session,
    commodity_name: str,
    recorded_at: date,
):
    commodity = db.scalar(
        select(Commodity).where(
            func.lower(Commodity.name) == commodity_name.strip().lower()
        )
    )

    if commodity is None:
        return {
            "found": False,
            "message": f"Commodity '{commodity_name}' was not found.",
            "records": [],
        }

    results = compare_prices_service(
        db,
        commodity.id,
        recorded_at,
    )

    return {
        "found": bool(results),
        "commodity": commodity.name,
        "recorded_at": recorded_at.isoformat(),
        "records": [
            {
                "city": row["city"],
                "state": row["state"],
                "price": row["price"],
                "unit": row["unit"],
                "data_source": "See individual price records for source attribution.",
            }
            for row in results
        ],
        "message": (
            "Price comparison retrieved successfully."
            if results
            else "No matching price records were found for that date."
        ),
    }


def calculate_price_change(
    db: Session,
    commodity_name: str,
    start_date: date,
    end_date: date,
):
    commodity = db.scalar(
        select(Commodity).where(
            func.lower(Commodity.name) == commodity_name.strip().lower()
        )
    )

    if commodity is None:
        return {
            "found": False,
            "message": f"Commodity '{commodity_name}' was not found.",
            "records": [],
        }

    if start_date >= end_date:
        return {
            "found": False,
            "message": "The end date must be later than the start date.",
            "records": [],
        }

    results = calculate_price_changes_service(
        db,
        commodity.id,
        start_date,
        end_date,
    )

    return {
        "found": bool(results),
        "commodity": commodity.name,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "records": results,
        "message": (
            "Price changes calculated successfully."
            if results
            else "No matching records were found for both dates."
        ),
    }
