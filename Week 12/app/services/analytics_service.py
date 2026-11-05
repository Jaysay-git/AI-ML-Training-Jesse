from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import Commodity, Location, Price


def get_overview(db: Session):
    total_commodities = db.scalar(
        select(func.count()).select_from(Commodity)
    )

    total_locations = db.scalar(
        select(func.count()).select_from(Location)
    )

    total_price_records = db.scalar(
        select(func.count()).select_from(Price)
    )

    latest_recorded_date = db.scalar(
        select(func.max(Price.recorded_at))
    )

    return {
        "total_commodities": total_commodities or 0,
        "total_locations": total_locations or 0,
        "total_price_records": total_price_records or 0,
        "latest_recorded_date": latest_recorded_date,
        "data_note": "Dataset contains simulated prices.",
    }

def compare_prices(
    db: Session,
    commodity_id: int,
    recorded_at,
):
    query = (
        select(
            Commodity.name.label("commodity"),
            Commodity.unit,
            Location.city,
            Location.state,
            Price.price,
            Price.recorded_at,
        )
        .join(Price, Price.commodity_id == Commodity.id)
        .join(Location, Price.location_id == Location.id)
        .where(
            Price.commodity_id == commodity_id,
            Price.recorded_at == recorded_at,
        )
        .order_by(Location.city)
    )

    results = db.execute(query).all()

    return [
        {
            "commodity": row.commodity,
            "unit": row.unit,
            "city": row.city,
            "state": row.state,
            "price": float(row.price),
            "recorded_at": row.recorded_at,
        }
        for row in results
    ]

def calculate_price_changes(
    db: Session,
    commodity_id: int,
    start_date,
    end_date,
):
    start_query = select(Price).where(
        Price.commodity_id == commodity_id,
        Price.recorded_at == start_date,
    )

    end_query = select(Price).where(
        Price.commodity_id == commodity_id,
        Price.recorded_at == end_date,
    )

    start_prices = {
        price.location_id: price
        for price in db.scalars(start_query).all()
    }

    end_prices = {
        price.location_id: price
        for price in db.scalars(end_query).all()
    }

    results = []

    for location_id, end_price in end_prices.items():
        start_price = start_prices.get(location_id)

        if start_price is None:
            continue

        difference = end_price.price - start_price.price

        percentage_change = (
            (difference / start_price.price) * 100
        )

        location = db.get(Location, location_id)

        results.append({
            "city": location.city,
            "commodity_id": commodity_id,
            "start_date": start_date,
            "end_date": end_date,
            "start_price": float(start_price.price),
            "end_price": float(end_price.price),
            "difference": float(difference),
            "percentage_change": round(
                float(percentage_change), 2
            ),
        })

    return results