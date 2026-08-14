# Hospital Patient Tracker API

A RESTful CRUD API built with FastAPI for managing hospital patient records.

The API allows users to create, retrieve, update, and delete patient records. It also includes input validation for patient information such as age, email, phone number, and gender.

## Features

- Create a patient record
- Retrieve all patient records
- Retrieve a patient by patient ID
- Update a patient record
- Delete a patient record
- Validate patient age
- Validate email addresses
- Validate phone numbers
- Validate gender
- Return meaningful HTTP status codes
- Return meaningful error messages
- Automated tests using pytest

## Technologies Used

- Python
- FastAPI
- Pydantic
- Uvicorn
- Pytest

## Project Structure

```text
ASSIGNMENT WEEK 2 AI-ML/
│
├── Main_hospital_patient_tracker.py
├── requirements.txt
├── README.md
│
└── tests/
    └── test_hospital_patient_tracker.py