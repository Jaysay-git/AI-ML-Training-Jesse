
from io import BytesIO
from uuid import uuid4

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.database.connection import SessionLocal
from app.database.models import Price


client = TestClient(app)


@pytest.fixture(scope="module")
def authenticated_user():
    email = f"import-test-{uuid4().hex}@example.com"
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
    headers = {"Authorization": f"Bearer {token}"}

    yield headers

    # Remove this test user's imported records and account.
    from app.database.models import User

    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))

        if user:
            db.execute(
                Price.__table__.delete().where(
                    Price.created_by == user.id
                )
            )
            db.delete(user)
            db.commit()
    finally:
        db.close()


def test_csv_import_preview(authenticated_user):
    csv_content = (
        "commodity,location,price,recorded_at\n"
        "Rice,Lagos,4500,2026-11-05\n"
    )

    response = client.post(
        "/prices/import/preview",
        headers=authenticated_user,
        files={
            "file": (
                "prices.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result["valid_rows"]) == 1
    assert len(result["invalid_rows"]) == 0
    assert len(result["duplicate_rows"]) == 0


def test_excel_import_preview(authenticated_user):
    dataframe = pd.DataFrame([
        {
            "commodity": "Beans",
            "location": "Ibadan",
            "price": 3200,
            "recorded_at": "2026-11-06",
        }
    ])

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False)

    response = client.post(
        "/prices/import/preview",
        headers=authenticated_user,
        files={
            "file": (
                "prices.xlsx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result["valid_rows"]) == 1
    assert len(result["invalid_rows"]) == 0


def test_confirm_csv_import(authenticated_user):
    csv_content = (
        "commodity,location,price,recorded_at\n"
        "Garri,Abuja,1800,2026-11-07\n"
    )

    response = client.post(
        "/prices/import/confirm",
        headers=authenticated_user,
        files={
            "file": (
                "confirm.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "success"
    assert result["imported_count"] == 1

    db = SessionLocal()
    try:
        imported = db.scalar(
            select(Price).where(
                Price.recorded_at == "2026-11-07"
            )
        )

        assert imported is not None
        assert imported.data_source == "USER_SUBMITTED"
        assert imported.created_by is not None
    finally:
        db.close()


def test_duplicate_import_is_detected(authenticated_user):
    csv_content = (
        "commodity,location,price,recorded_at\n"
        "Garri,Abuja,1800,2026-11-07\n"
    )

    response = client.post(
        "/prices/import/preview",
        headers=authenticated_user,
        files={
            "file": (
                "duplicate.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result["valid_rows"]) == 0
    assert len(result["duplicate_rows"]) == 1


def test_invalid_rows_are_reported(authenticated_user):
    csv_content = (
        "commodity,location,price,recorded_at\n"
        "Unknown Commodity,Lagos,4500,2026-11-08\n"
        "Rice,Lagos,-500,2026-11-09\n"
    )

    response = client.post(
        "/prices/import/preview",
        headers=authenticated_user,
        files={
            "file": (
                "invalid.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result["valid_rows"]) == 0
    assert len(result["invalid_rows"]) == 2
