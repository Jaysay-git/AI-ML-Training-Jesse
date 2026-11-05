from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Price


def create_price(db: Session, price_data: dict, user_id: int):
    price = Price(
        **price_data,
        data_source="USER_SUBMITTED",
        created_by=user_id,
    )

    db.add(price)
    db.commit()
    db.refresh(price)

    return price


def get_price(db: Session, price_id: int):
    return db.get(Price, price_id)


def list_prices(
    db: Session,
    commodity_id: int | None = None,
    location_id: int | None = None,
):
    query = select(Price)

    if commodity_id is not None:
        query = query.where(Price.commodity_id == commodity_id)

    if location_id is not None:
        query = query.where(Price.location_id == location_id)

    return db.scalars(
        query.order_by(Price.recorded_at.desc())
    ).all()


def update_price(
    db: Session,
    price: Price,
    update_data: dict,
    user_id: int,
):
    if price.created_by != user_id:
        return None

    for field, value in update_data.items():
        if value is not None:
            setattr(price, field, value)

    db.commit()
    db.refresh(price)

    return price


def delete_price(db: Session, price: Price, user_id: int):
    if price.created_by != user_id:
        return False

    db.delete(price)
    db.commit()

    return True
