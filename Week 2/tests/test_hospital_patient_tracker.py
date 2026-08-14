from fastapi.testclient import TestClient
from hospital_patient_tracker import app

client = TestClient(app)

def test_create_patient():
    response = client.post(
        "/patients/",
        json={
            "patient_id": "TEST-001",
            "name": "Test Patient",
            "age": 30,
            "email": "test@gmail.com",
            "number": "08123456789",
            "gender": "M",
            "condition": "Malaria"
        }
    )

    assert response.status_code == 201
    assert response.json()["patient_id"] == "TEST-001"


def test_get_all_patients():
    response = client.get("/patients/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_patient():
    response = client.get("/patients/TEST-001")

    assert response.status_code == 200
    assert response.json()["patient_id"] == "TEST-001"


def test_update_patient():
    response = client.put(
        "/patients/TEST-001",
        json={
            "patient_id": "TEST-001",
            "name": "Updated Patient",
            "age": 35,
            "email": "updated@gmail.com",
            "number": "08111111111",
            "gender": "M",
            "condition": "Hypertension"
        }
    )

    print(response.json())

    assert response.status_code == 200


def test_delete_patient():
    response = client.delete("/patients/TEST-001")

    assert response.status_code == 204

def test_get_nonexistent_patient():
    response = client.get("/patients/DOES-NOT-EXIST")

    assert response.status_code == 404

def test_update_nonexistent_patient():
    response = client.put(
        "/patients/DOES-NOT-EXIST",
        json={
            "patient_id": "DOES-NOT-EXIST",
            "name": "Nobody",
            "age": 30,
            "email": "nobody@gmail.com",
            "number": "08122222222",
            "gender": "M",
            "condition": "Malaria"
        }
    )

    assert response.status_code == 404


def test_delete_nonexistent_patient():
    response = client.delete("/patients/DOES-NOT-EXIST")

    assert response.status_code == 404


def test_invalid_email():
    response = client.post(
        "/patients/",
        json={
            "patient_id": "TEST-002",
            "name": "Invalid Email",
            "age": 30,
            "email": "not-an-email",
            "number": "08123456789",
            "gender": "M",
            "condition": "Malaria"
        }
    )

    assert response.status_code == 422


def test_invalid_phone_letters():
    response = client.post(
        "/patients/",
        json={
            "patient_id": "TEST-003",
            "name": "Invalid Phone",
            "age": 30,
            "email": "test3@gmail.com",
            "number": "08123ABCDE9",
            "gender": "M",
            "condition": "Malaria"
        }
    )

    assert response.status_code == 422


def test_invalid_phone_length():
    response = client.post(
        "/patients/",
        json={
            "patient_id": "TEST-004",
            "name": "Invalid Phone",
            "age": 30,
            "email": "test4@gmail.com",
            "number": "0812345678",
            "gender": "M",
            "condition": "Malaria"
        }
    )

    assert response.status_code == 422


def test_invalid_age():
    response = client.post(
        "/patients/",
        json={
            "patient_id": "TEST-005",
            "name": "Invalid Age",
            "age": -5,
            "email": "test5@gmail.com",
            "number": "08123456789",
            "gender": "M",
            "condition": "Malaria"
        }
    )

    assert response.status_code == 422


def test_invalid_gender():
    response = client.post(
        "/patients/",
        json={
            "patient_id": "TEST-006",
            "name": "Invalid Gender",
            "age": 30,
            "email": "test6@gmail.com",
            "number": "08123456789",
            "gender": "X",
            "condition": "Malaria"
        }
    )

    assert response.status_code == 422