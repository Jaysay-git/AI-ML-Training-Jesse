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

```

## Installation

1. Clone the repository

Clone the GitHub repository to your computer:
git clone https://github.com/Jaysay-git/AI-ML-Training-Jesse.git

2. Navigate to the Week 2 project
cd AI-ML-Training-Jesse
cd "Week 2"

3. Install the required dependencies
pip install -r requirements.txt

## Running the API
Start the FastAPI development server using Uvicorn:
uvicorn Main_hospital_patient_tracker:app --reload

The API will be available at:
http://127.0.0.1:8000

## API Documentation
FastAPI automatically provides interactive API documentation.

After starting the server, open:
http://127.0.0.1:8000/docs

You can use the Swagger UI to test the API endpoints.


API Endpoints

Method	    Endpoint	                Description

POST	    /details/	                Create a patient

GET	        /patients/	                Retrieve all patients

GET	        /patients/{patient_id}	    Retrieve a patient

PUT	        /patients/{patient_id}	    Update a patient

DELETE	    /patients/{patient_id}	    Delete a patient


Validation

The API validates patient information before accepting requests.

Age

Patient age must be between 0 and 120.

Email

Patient email addresses must be valid email addresses.

Phone Number

Phone numbers must contain only valid numeric characters and must meet the required length.

Gender

Only accepted gender values are allowed.

Invalid input returns:

422 Unprocessable Entity

with details describing the validation error.


HTTP Status Codes

The API uses meaningful HTTP status codes:
| Status Code | Meaning                      |
| ----------- | ---------------------------- |
| 200         | Request successful           |
| 201         | Patient successfully created |
| 204         | Patient successfully deleted |
| 404         | Patient not found            |
| 422         | Invalid input                |

Running Tests

The project includes automated tests using pytest.

From the Week 2 project directory, run:
python -m pytest

A successful test run should show:
13 passed

Example Patient

Example patient data:

{

    "patient_id": "TEST-001",

    "name": "John Doe",

    "age": 35,

    "email": "john@example.com",

    "number": "08123456789",

    "gender": "M",

    "condition": "Hypertension"

}

Error Handling

The API returns appropriate errors when:

A patient does not exist

An invalid email is provided

An invalid phone number is provided

An invalid gender is provided

An invalid age is provided