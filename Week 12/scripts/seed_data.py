import pandas as pd

from datetime import datetime
from sqlalchemy import select, func

from app.database.connection import SessionLocal
from app.database.models import User, Commodity, Location, Price


CSV_PATH = "data/raw/commodity_prices.csv"


def seed_database():
    df = pd.read_csv(CSV_PATH)
    db = SessionLocal()

    try:
        commodity_map = {}
        location_map = {}

        # Create commodities
        for _, row in df[
            ["commodity", "category", "unit"]
        ].drop_duplicates().iterrows():

            commodity = db.scalar(
                select(Commodity).where(
                    Commodity.name == row["commodity"]
                )
            )

            if not commodity:
                commodity = Commodity(
                    name=row["commodity"],
                    category=row["category"],
                    unit=row["unit"],
                )
                db.add(commodity)
                db.flush()

            commodity_map[row["commodity"]] = commodity.id

        # Create locations
        for _, row in df[
            ["location", "state"]
        ].drop_duplicates().iterrows():

            location = db.scalar(
                select(Location).where(
                    Location.city == row["location"],
                    Location.state == row["state"],
                )
            )

            if not location:
                location = Location(
                    city=row["location"],
                    state=row["state"],
                )
                db.add(location)
                db.flush()

            location_map[row["location"]] = location.id

        db.commit()

        # Insert price records without duplicating existing entries
        inserted = 0
        skipped = 0

        for _, row in df.iterrows():
            commodity_id = commodity_map[row["commodity"]]
            location_id = location_map[row["location"]]
            recorded_at = datetime.strptime(
                row["recorded_at"], "%Y-%m-%d"
            ).date()

            existing = db.scalar(
                select(Price).where(
                    Price.commodity_id == commodity_id,
                    Price.location_id == location_id,
                    Price.recorded_at == recorded_at,
                )
            )

            if existing:
                skipped += 1
                continue

            price_record = Price(
                commodity_id=commodity_id,
                location_id=location_id,
                price=row["price"],
                recorded_at=recorded_at,
                data_source=row["data_source"],
                created_by=None,
            )

            db.add(price_record)
            inserted += 1

        db.commit()

        print("Database seeding completed!")
        print(f"Commodities: {len(commodity_map)}")
        print(f"Locations: {len(location_map)}")
        print(f"Price records inserted: {inserted}")
        print(f"Existing records skipped: {skipped}")

        print("\nFinal database totals:")
        print(
            "Users:",
            db.scalar(select(func.count()).select_from(User))
        )
        print(
            "Commodities:",
            db.scalar(select(func.count()).select_from(Commodity))
        )
        print(
            "Locations:",
            db.scalar(select(func.count()).select_from(Location))
        )
        print(
            "Prices:",
            db.scalar(select(func.count()).select_from(Price))
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
