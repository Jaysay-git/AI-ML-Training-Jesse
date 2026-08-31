# Week 4 — Authentication & Security

This week adds authentication and security features to the Hospital Patient Tracker API.

## Features

* User signup with password hashing
* JWT-based login
* Protected patient endpoints
* Login rate limiting
* Safe centralized error handling
* Request logging with request IDs and latency
* Automated authentication tests

## Environment Setup

Create a `.env` file inside the `Week 4` directory:

```env
JWT_SECRET_KEY=your-secret-key-here
```

The `JWT_SECRET_KEY` is used to sign and verify JWT access tokens.

For local development, use a strong, randomly generated secret. Do not commit the `.env` file or expose the secret in source code.

## Running Tests

From the `Week 4` directory:

```bash
python -m pytest tests
```

All authentication tests should pass before submitting changes.

## Authentication Flow

1. A user signs up with a username and password.
2. The password is hashed before being stored in the database.
3. The user logs in with their credentials.
4. The API creates a JWT access token.
5. The client sends the token when accessing protected patient endpoints.
6. The API verifies the token before allowing access.
7. Invalid or missing tokens result in an authentication error.

## Protected Endpoints

The patient endpoints require a valid JWT:

* `GET /patients/`
* `GET /patients/{patient_id}`
* `POST /patients/`
* `PUT /patients/{patient_id}`
* `DELETE /patients/{patient_id}`

Signup and login remain publicly accessible so users can authenticate before accessing protected resources.
