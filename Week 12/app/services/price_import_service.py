
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Commodity, Location, Price


REQUIRED_COLUMNS = {
    "commodity",
    "location",
    "price",
    "recorded_at",
}

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_ROWS = 1000


def read_spreadsheet(content: bytes, filename: str) -> pd.DataFrame:
    """Read an uploaded CSV or XLSX spreadsheet."""

    extension = Path(filename).suffix.lower()

    if extension not in {".csv", ".xlsx"}:
        raise ValueError("Only CSV and XLSX files are supported.")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File size must not exceed 5 MB.")

    try:
        if extension == ".csv":
            df = pd.read_csv(BytesIO(content))
        else:
            df = pd.read_excel(
                BytesIO(content),
                engine="openpyxl",
            )
    except Exception as error:
        raise ValueError(
            "Unable to read the spreadsheet. Check that it is valid."
        ) from error

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    df = df[list(REQUIRED_COLUMNS)].copy()
    df = df.dropna(how="all")

    if df.empty:
        raise ValueError("The spreadsheet contains no records.")

    if len(df) > MAX_ROWS:
        raise ValueError(
            f"A maximum of {MAX_ROWS} records can be imported at once."
        )

    return df


def parse_price_upload(
    db: Session,
    content: bytes,
    filename: str,
) -> dict:
    """Validate spreadsheet rows without saving anything."""

    df = read_spreadsheet(content, filename)

    commodities = db.scalars(select(Commodity)).all()
    locations = db.scalars(select(Location)).all()

    commodity_map = {
        item.name.strip().lower(): item
        for item in commodities
    }

    location_map = {
        item.city.strip().lower(): item
        for item in locations
    }

    existing_keys = set(
        db.execute(
            select(
                Price.commodity_id,
                Price.location_id,
                Price.recorded_at,
            )
        ).all()
    )

    seen_keys = set()

    valid_rows = []
    invalid_rows = []
    duplicate_rows = []

    for index, row in df.iterrows():
        row_number = index + 2
        errors = []

        commodity_name = str(row["commodity"]).strip()
        location_name = str(row["location"]).strip()

        commodity = commodity_map.get(commodity_name.lower())
        location = location_map.get(location_name.lower())

        if not commodity:
            errors.append(
                f"Unknown commodity: {commodity_name}"
            )

        if not location:
            errors.append(
                f"Unknown location: {location_name}"
            )

        try:
            raw_price = row["price"]

            if pd.isna(raw_price):
                raise ValueError

            price = Decimal(str(raw_price)).quantize(
                Decimal("0.01")
            )

            if not price.is_finite() or price <= 0:
                raise ValueError

            if price.adjusted() >= 10:
                raise ValueError

        except (InvalidOperation, ValueError, TypeError):
            price = None
            errors.append(
                "Price must be a positive number with "
                "no more than 10 integer digits."
            )

        try:
            raw_date = row["recorded_at"]

            if pd.isna(raw_date):
                raise ValueError

            if isinstance(raw_date, datetime):
                recorded_at = raw_date.date()
            elif isinstance(raw_date, date):
                recorded_at = raw_date
            else:
                recorded_at = date.fromisoformat(
                    str(raw_date).strip()[:10]
                )

        except (ValueError, TypeError):
            recorded_at = None
            errors.append(
                "Date must use YYYY-MM-DD format."
            )

        if errors:
            invalid_rows.append({
                "row": int(row_number),
                "errors": errors,
            })
            continue

        key = (
            commodity.id,
            location.id,
            recorded_at,
        )

        if key in existing_keys or key in seen_keys:
            duplicate_rows.append({
                "row": int(row_number),
                "commodity": commodity.name,
                "location": location.city,
                "recorded_at": recorded_at.isoformat(),
                "reason": (
                    "This commodity, location and date "
                    "combination already exists."
                ),
            })
            continue

        seen_keys.add(key)

        valid_rows.append({
            "row": int(row_number),
            "commodity_id": commodity.id,
            "commodity": commodity.name,
            "location_id": location.id,
            "location": location.city,
            "price": str(price),
            "recorded_at": recorded_at.isoformat(),
        })

    return {
        "total_rows": len(df),
        "valid_count": len(valid_rows),
        "invalid_count": len(invalid_rows),
        "duplicate_count": len(duplicate_rows),
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "duplicate_rows": duplicate_rows,
    }


def save_imported_prices(
    db: Session,
    valid_rows: list[dict],
    user_id: int,
) -> int:
    """Save validated rows as one transaction."""

    records = [
        Price(
            commodity_id=row["commodity_id"],
            location_id=row["location_id"],
            price=Decimal(row["price"]),
            recorded_at=date.fromisoformat(row["recorded_at"]),
            data_source="USER_SUBMITTED",
            created_by=user_id,
        )
        for row in valid_rows
    ]

    try:
        db.add_all(records)
        db.commit()

        return len(records)

    except Exception:
        db.rollback()
        raise
