import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
from fastapi.testclient import TestClient

from hospital_patient_tracker import app
from auth import SECRET_KEY, ALGORITHM


client = TestClient(app, raise_server_exceptions=False)


def ensure_test_user():
    client.post(
        "/signup",
        json={
            "username": "testuser_week5",
            "password": "testpassword"
        }
    )


def get_test_token():
    """
    Create a valid JWT directly instead of calling /login.

    This avoids triggering the login rate limiter
    during unrelated tests.
    """
    payload = {
        "sub": "testuser_week5",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ---------------------------------------------------------
# Authentication tests
# ---------------------------------------------------------

def test_password_hashing():
    from auth import hash_password, verify_password

    password = "testpassword"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_signup():
    username = "testuser_week5_unique"

    response = client.post(
        "/signup",
        json={
            "username": username,
            "password": "testpassword"
        }
    )

    assert response.status_code in [201, 400]


def test_duplicate_signup():
    import uuid

    username = f"duplicate_week5_{uuid.uuid4().hex[:8]}"

    first_response = client.post(
        "/signup",
        json={
            "username": username,
            "password": "testpassword"
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/signup",
        json={
            "username": username,
            "password": "testpassword"
        }
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Username already exists"

def test_login():
    ensure_test_user()

    response = client.post(
        "/login",
        json={
            "username": "testuser_week5",
            "password": "testpassword"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_invalid_login():
    ensure_test_user()

    response = client.post(
        "/login",
        json={
            "username": "testuser_week5",
            "password": "wrongpassword"
        }
    )

    assert response.status_code in [401, 429]


def test_nonexistent_user_login():
    response = client.post(
        "/login",
        json={
            "username": "user_that_does_not_exist",
            "password": "wrongpassword"
        }
    )

    assert response.status_code in [401, 429]


def test_protected_endpoint_without_token():
    response = client.get("/patients/")

    assert response.status_code == 401


def test_protected_endpoint_with_token():
    token = get_test_token()

    response = client.get(
        "/patients/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_invalid_token():
    response = client.get(
        "/patients/",
        headers={
            "Authorization": "Bearer this-is-not-a-valid-token"
        }
    )

    assert response.status_code == 401


def test_expired_token():
    expired_payload = {
        "sub": "testuser_week5",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }

    expired_token = jwt.encode(
        expired_payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    response = client.get(
        "/patients/",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"


def test_login_rate_limiting():
    responses = []

    for _ in range(6):
        response = client.post(
            "/login",
            json={
                "username": "testuser_week5",
                "password": "wrongpassword"
            }
        )

        responses.append(response.status_code)

    assert 429 in responses


def test_request_does_not_log_sensitive_data(caplog):
    sensitive_value = "SECRET-PASSWORD-123"

    with caplog.at_level(logging.INFO):
        client.post(
            "/login",
            json={
                "username": "testuser_week5",
                "password": sensitive_value
            }
        )

    assert sensitive_value not in caplog.text


# ---------------------------------------------------------
# Patient validation / edge cases
# ---------------------------------------------------------

def test_patient_validation_invalid_age():
    token = get_test_token()

    response = client.post(
        "/patients/",
        json={
            "patient_id": "P001",
            "name": "Test Patient",
            "age": 150,
            "email": "test@example.com",
            "number": "08012345678",
            "gender": "M",
            "condition": "Test"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 422


def test_patient_validation_invalid_phone():
    token = get_test_token()

    response = client.post(
        "/patients/",
        json={
            "patient_id": "P002",
            "name": "Test Patient",
            "age": 30,
            "email": "test@example.com",
            "number": "12345",
            "gender": "M",
            "condition": "Test"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 422


def test_patient_validation_invalid_gender():
    token = get_test_token()

    response = client.post(
        "/patients/",
        json={
            "patient_id": "P003",
            "name": "Test Patient",
            "age": 30,
            "email": "test@example.com",
            "number": "08012345678",
            "gender": "X",
            "condition": "Test"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 422


def test_nonexistent_patient():
    token = get_test_token()

    response = client.get(
        "/patients/DOES-NOT-EXIST",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


# ---------------------------------------------------------
# Mocking
# ---------------------------------------------------------

def test_database_failure_is_handled():
    token = get_test_token()

    with patch(
        "hospital_patient_tracker.SessionLocal"
    ) as mock_session:

        mock_db = mock_session.return_value
        mock_db.query.side_effect = Exception(
            "Database connection failed"
        )

        response = client.get(
            "/patients/",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 500
        assert response.json()["detail"] == (
            "An internal server error occurred."
        )


def test_global_exception_handler_does_not_leak_error_details():
    token = get_test_token()

    with patch(
        "hospital_patient_tracker.SessionLocal"
    ) as mock_session:

        mock_db = mock_session.return_value
        mock_db.query.side_effect = Exception(
            "SECRET DATABASE PASSWORD"
        )

        response = client.get(
            "/patients/",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 500
        assert "SECRET DATABASE PASSWORD" not in response.text
        assert response.json()["detail"] == (
            "An internal server error occurred."
        )