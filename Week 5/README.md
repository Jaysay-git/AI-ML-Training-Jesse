# Week 5 — Testing, Docker & Deployment

This week extends the Hospital Patient Tracker API with a meaningful automated test suite, Docker containerization, and secure environment variable management.

## Features

* User signup with password hashing
* JWT-based login
* Protected patient endpoints
* Login rate limiting
* Safe centralized error handling
* Request logging with request IDs and latency
* Automated authentication and API tests
* Edge-case and validation testing
* Mocked database failure testing
* Dockerized FastAPI application
* PostgreSQL container using Docker Compose
* Environment-based configuration for secrets

## Environment Setup

Create a `.env` file inside the `Week 5` directory:

```env
JWT_SECRET_KEY=your-secret-key-here
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-database-password
POSTGRES_DB=hospital_patients
```

The `JWT_SECRET_KEY` is used to sign and verify JWT access tokens.

The PostgreSQL variables are used to configure the database connection.

For local development, use strong, randomly generated secrets. Do not commit the `.env` file or expose secrets in source code.

The `.env` file is excluded from Git using `.gitignore`.

## Running Tests

From the `Week 5` directory, activate the virtual environment and run:

```bash
python -m pytest
```

The test suite contains 18 automated tests covering authentication, validation, protected endpoints, rate limiting, error handling, and database failure scenarios.

### Test Coverage

The tests include:

* Password hashing and verification
* Successful user signup
* Duplicate username handling
* Successful login
* Invalid login credentials
* Login with a nonexistent user
* Accessing protected endpoints without authentication
* Accessing protected endpoints with a valid JWT
* Invalid JWT handling
* Expired JWT handling
* Login rate limiting
* Preventing sensitive information from appearing in logs
* Invalid patient age
* Invalid phone number
* Invalid gender
* Requesting a nonexistent patient
* Mocked database failure
* Global exception handling without exposing internal error details

All tests currently pass.

## Authentication Flow

1. A user signs up with a username and password.
2. The password is hashed before being stored in the database.
3. The user logs in with their credentials.
4. The API creates a JWT access token.
5. The client sends the token when accessing protected patient endpoints.
6. The API verifies the token before allowing access.
7. Invalid or missing tokens result in an authentication error.

## Protected Endpoints

The following patient endpoints require a valid JWT:

* `GET /patients/`
* `GET /patients/{patient_id}`
* `POST /patients/`
* `PUT /patients/{patient_id}`
* `DELETE /patients/{patient_id}`

Signup and login remain publicly accessible so users can authenticate before accessing protected resources.

## Docker

The application is containerized using Docker.

The project contains:

* `Dockerfile` — builds the FastAPI application image.
* `docker-compose.yml` — runs the API and PostgreSQL services together.
* `.env` — stores environment-specific configuration and secrets.

### Build and Start the Application

Run:

```bash
docker compose up --build
```

This starts:

* **API** — FastAPI application running on port `8000`
* **Database** — PostgreSQL running on port `5433`

The API documentation can be accessed at:

```text
http://localhost:8000/docs
```

### Stop the Containers

```bash
docker compose down
```

## Docker Services

The application uses two services:

### API

The API service builds the FastAPI application from the project's `Dockerfile`.

The container runs Uvicorn and exposes port `8000`.

### PostgreSQL

The database service uses the official PostgreSQL Docker image.

Docker Compose provides the database credentials and connection information through environment variables.

The API connects to PostgreSQL using the Docker Compose service name rather than `localhost`.

## Secrets Management

Sensitive configuration is stored outside the application source code.

The `.env` file contains environment-specific values such as:

* JWT secret key
* PostgreSQL username
* PostgreSQL password
* PostgreSQL database name

The `.env` file is listed in `.gitignore` so it is not committed to the repository.

In a production environment, secrets should be stored using a dedicated secrets-management system rather than committed to source control.

## Error Handling and Logging

The API includes centralized exception handling to prevent internal implementation details from being exposed to clients.

Requests are logged with:

* Request ID
* HTTP method
* Request path
* Response status
* Request latency

Sensitive information such as passwords and authentication secrets is not included in request logs.

## Deployment

The application is containerized and structured to support deployment to a container platform such as Azure Container Apps.

The Azure deployment step was not completed as part of the current Week 5 implementation.
