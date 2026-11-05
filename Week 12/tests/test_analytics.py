import pytest
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.database.connection import SessionLocal
from app.database.models import User, Commodity

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_headers():
    email = f"analytics-{uuid4().hex}@example.com"
    password = "TestPassword123!"

    signup = client.post(
        "/auth/signup",
        json={"email": email, "password": password},
    )
    assert signup.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    yield {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    try:
        user = db.scalar(
            select(User).where(User.email == email)
        )
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def test_analytics_overview(auth_headers):
    response = client.get(
        "/analytics/overview",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_commodities"] == 12
    assert data["total_locations"] == 3
    assert data["total_price_records"] == 432
    assert data["data_note"] == "Dataset contains simulated prices."


def test_compare_prices(auth_headers):
    db = SessionLocal()
    try:
        rice = db.scalar(
            select(Commodity).where(Commodity.name == "Rice")
        )
        assert rice is not None
        commodity_id = rice.id
    finally:
        db.close()

    response = client.get(
        "/analytics/compare",
        params={
            "commodity_id": commodity_id,
            "recorded_at": "2025-12-01",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["commodity"] == "Rice"
    assert len(data["results"]) == 3

    cities = {row["city"] for row in data["results"]}
    assert cities == {"Lagos", "Ibadan", "Abuja"}


def test_calculate_price_changes(auth_headers):
    db = SessionLocal()
    try:
        rice = db.scalar(
            select(Commodity).where(Commodity.name == "Rice")
        )
        assert rice is not None
        commodity_id = rice.id
    finally:
        db.close()

    response = client.get(
        "/analytics/changes",
        params={
            "commodity_id": commodity_id,
            "start_date": "2025-01-01",
            "end_date": "2025-12-01",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert len(results) == 3

    for row in results:
        expected_change = (
            (row["end_price"] - row["start_price"])
            / row["start_price"]
        ) * 100

        assert row["percentage_change"] == round(
            expected_change, 2
        )
