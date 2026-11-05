import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.database.connection import SessionLocal
from app.database.models import User

client = TestClient(app)


@pytest.fixture(scope="module")
def test_user_email():
    email = f"testuser-{uuid4().hex}@example.com"

    yield email

    # Clean up the test account after all tests finish
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


def test_signup(test_user_email):
    response = client.post(
        "/auth/signup",
        json={
            "email": test_user_email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == test_user_email
    assert response.json()["role"] == "user"
    assert "password_hash" not in response.json()


def test_duplicate_signup(test_user_email):
    response = client.post(
        "/auth/signup",
        json={
            "email": test_user_email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 409


def test_login(test_user_email):
    response = client.post(
        "/auth/login",
        json={
            "email": test_user_email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


def test_invalid_login(test_user_email):
    response = client.post(
        "/auth/login",
        json={
            "email": test_user_email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_current_user_with_token(test_user_email):
    login_response = client.post(
        "/auth/login",
        json={
            "email": test_user_email,
            "password": "TestPassword123!",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == test_user_email
    assert response.json()["role"] == "user"


def test_current_user_without_token():
    response = client.get("/auth/me")

    assert response.status_code == 401