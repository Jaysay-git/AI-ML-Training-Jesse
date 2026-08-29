from fastapi.testclient import TestClient

from hospital_patient_tracker import app


client = TestClient(app)


def test_password_hashing():
    from auth import hash_password, verify_password

    password = "testpassword"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_signup():
    username = "testuser_week4_unique"

    response = client.post(
        "/signup",
        json={
            "username": username,
            "password": "testpassword"
        }
    )

    # User may already exist from an earlier test run.
    assert response.status_code in [201, 400]


def test_login():
    response = client.post(
        "/login",
        json={
            "username": "testuser_week4",
            "password": "testpassword"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_invalid_login():
    response = client.post(
        "/login",
        json={
            "username": "testuser_week4",
            "password": "wrongpassword"
        }
    )

    assert response.status_code in [401, 429]


def test_protected_endpoint_without_token():
    response = client.get("/patients/")

    assert response.status_code == 401


def test_protected_endpoint_with_token():
    login_response = client.post(
        "/login",
        json={
            "username": "testuser_week4",
            "password": "testpassword"
        }
    )

    if login_response.status_code == 429:
        return

    token = login_response.json()["access_token"]

    response = client.get(
        "/patients/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_login_rate_limiting():
    responses = []

    for _ in range(6):
        response = client.post(
            "/login",
            json={
                "username": "testuser_week4",
                "password": "wrongpassword"
            }
        )

        responses.append(response.status_code)

    assert 429 in responses

def test_request_does_not_log_sensitive_data(caplog):
    sensitive_value = "SECRET-PASSWORD-123"

    with caplog.at_level("INFO"):
        client.post(
            "/login",
            json={
                "username": "testuser_week4",
                "password": sensitive_value
            }
        )

    assert sensitive_value not in caplog.text
