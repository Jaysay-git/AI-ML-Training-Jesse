from datetime import date

from sqlalchemy import select

from app.agent.agent import fallback_answer
from app.database.connection import SessionLocal
from app.database.models import Commodity, Location, Price


def test_rice_lookup_filters_by_city_and_month():
    db = SessionLocal()

    try:
        result = fallback_answer(
            db,
            "What is the price of rice in Lagos in December 2025?"
        )

        answer = result["answer"]

        assert result["fallback"] is True
        assert "lookup_commodity" in result["tools_used"]

        assert "Lagos, Lagos State" in answer
        assert "2,295.98" in answer
        assert "SIMULATED" in answer

        assert "Ibadan" not in answer
        assert "Abuja" not in answer

    finally:
        db.close()


def test_beans_lookup_finds_user_submitted_price_in_november_2026():
    db = SessionLocal()
    submitted_price = None

    try:
        beans = db.scalar(
            select(Commodity).where(Commodity.name == "Beans")
        )

        ibadan = db.scalar(
            select(Location).where(Location.city == "Ibadan")
        )

        assert beans is not None
        assert ibadan is not None

        submitted_price = Price(
            commodity_id=beans.id,
            location_id=ibadan.id,
            price=3200.00,
            recorded_at=date(2026, 11, 5),
            data_source="USER_SUBMITTED",
        )

        db.add(submitted_price)
        db.commit()

        result = fallback_answer(
            db,
            "What is the price of beans in Ibadan in November 2026?"
        )

        answer = result["answer"]

        assert result["fallback"] is True
        assert "lookup_commodity" in result["tools_used"]
        assert "Ibadan, Oyo State" in answer
        assert "3,200.00" in answer
        assert "USER_SUBMITTED" in answer
        assert "Lagos" not in answer
        assert "Abuja" not in answer

    finally:
        if submitted_price is not None:
            db.delete(submitted_price)
            db.commit()

        db.close()
