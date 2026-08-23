# Hospital Patient Tracker API

A RESTful CRUD API built with FastAPI for managing hospital patient records.

In Week 3, the API was migrated from in-memory storage to a PostgreSQL database using SQLAlchemy ORM and Alembic migrations. PostgreSQL runs in Docker using Docker Compose.

The API supports creating, retrieving, updating, and deleting patient records while validating patient information such as age, email, phone number, and gender.

## Features

* Create a patient record
* Retrieve all patient records
* Retrieve a patient by patient ID
* Update a patient record
* Delete a patient record
* Persist patient data in PostgreSQL
* Use SQLAlchemy ORM for database operations
* Use Alembic for database migrations
* Validate patient age
* Validate email addresses
* Validate phone numbers
* Validate gender
* Return meaningful HTTP status codes
* Return meaningful error messages
* Automated tests using pytest

## Technologies Used

* Python
* FastAPI
* Uvicorn
* Pydantic
* Email Validator
* SQLAlchemy
* Psycopg
* PostgreSQL
* Docker
* Docker Compose
* Alembic
* Pytest
* HTTPX

## Project Structure

```text
Week 3/
│
├── alembic/
│   ├── versions/
│   │   └── f36855e27fb9_create_patients_table.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── tests/
│   └── test_hospital_patient_tracker.py
│
├── alembic.ini
├── database.py
├── docker-compose.yml
├── hospital_patient_tracker.py
├── models.py
├── schemas.py
├── requirements.txt
└── README.md
```

## Database Architecture

The application uses PostgreSQL as its database.

Docker Compose runs the PostgreSQL database in a container, while SQLAlchemy is used by the FastAPI application to communicate with the database.

The main database components are:

### `database.py`

Contains the SQLAlchemy database configuration, including the database engine, session configuration, and declarative base.

### `models.py`

Contains the SQLAlchemy ORM models used to represent database tables.

### `schemas.py`

Contains the Pydantic schemas used to validate incoming API data.

### `alembic/`

Contains the Alembic configuration and database migration files used to create and update the database schema.

## Docker and PostgreSQL

PostgreSQL is run using Docker Compose.

Start the PostgreSQL container with:

```bash
docker compose up -d
```

To check that the container is running:

```bash
docker ps
```

To stop the PostgreSQL container:

```bash
docker compose down
```

## Installation

### 1. Clone the repository

Clone the GitHub repository to your computer:

```bash
git clone https://github.com/Jaysay-git/AI-ML-Training-Jesse.git
```

### 2. Navigate to the Week 3 project

```bash
cd AI-ML-Training-Jesse
cd "Week 3"
```

### 3. Activate the virtual environment

If using the `jaysay` virtual environment:

```powershell
jaysay\Scripts\activate
```

### 4. Install the required dependencies

```bash
py -m pip install -r requirements.txt
```

## Database Migrations

Alembic is used to manage changes to the PostgreSQL database schema.

### Apply migrations

Run:

```bash
py -m alembic upgrade head
```

This applies the latest migration to the database.

### Check the current migration

```bash
py -m alembic current
```

### View migration history

```bash
py -m alembic history
```

## Running the API

First, make sure the PostgreSQL Docker container is running:

```bash
docker compose up -d
```

Then start the FastAPI application using Uvicorn:

```bash
py -m uvicorn hospital_patient_tracker:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically provides interactive API documentation.

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI can be used to test the API endpoints.

## API Endpoints

| Method | Endpoint                 | Description           |
| ------ | ------------------------ | --------------------- |
| POST   | `/patients/`             | Create a patient      |
| GET    | `/patients/`             | Retrieve all patients |
| GET    | `/patients/{patient_id}` | Retrieve a patient    |
| PUT    | `/patients/{patient_id}` | Update a patient      |
| DELETE | `/patients/{patient_id}` | Delete a patient      |

## Validation

The API validates patient information before accepting requests.

### Age

Patient age must be between 0 and 120.

### Email

Patient email addresses must be valid email addresses.

### Phone Number

Phone numbers must contain only numeric characters, contain 11 digits, and follow the required Nigerian phone number format.

### Gender

Only the accepted gender values are allowed.

Invalid input returns:

```text
422 Unprocessable Entity
```

with details describing the validation error.

## HTTP Status Codes

The API uses meaningful HTTP status codes:

| Status Code | Meaning                      |
| ----------- | ---------------------------- |
| 200         | Request successful           |
| 201         | Patient successfully created |
| 204         | Patient successfully deleted |
| 404         | Patient not found            |
| 422         | Invalid input                |

## Running Tests

The project includes automated tests using pytest.

From the Week 3 project directory, run:

```powershell
py -m pytest tests
```

The tests cover the main CRUD operations and validation behavior of the API.

## Example Patient

Example patient data:

```json
{
    "patient_id": "TEST-001",
    "name": "John Doe",
    "age": 35,
    "email": "john@example.com",
    "number": "08123456789",
    "gender": "M",
    "condition": "Hypertension"
}
```

## Error Handling

The API returns appropriate errors when:

* A patient does not exist
* An invalid email is provided
* An invalid phone number is provided
* An invalid gender is provided
* An invalid age is provided

## Database Persistence

Unlike the Week 2 implementation, which stored patient records in memory, the Week 3 implementation persists patient records in PostgreSQL.

This means patient data remains stored in the database instead of being lost when the API application restarts.

SQLAlchemy handles communication between the FastAPI application and PostgreSQL, while Alembic manages database schema migrations.
