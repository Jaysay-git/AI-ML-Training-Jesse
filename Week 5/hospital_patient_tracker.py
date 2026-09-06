import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from database import SessionLocal
from models import Patient, User
from schemas import PatientCreate, UserCreate
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token
)

app = FastAPI()

logger = logging.getLogger("hospital_api")
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    logger.info(
        "request_id=%s method=%s path=%s status=%s latency=%.4fs",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration
    )

    response.headers["X-Request-ID"] = request_id

    return response

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred."
        }
    )

security = HTTPBearer()
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    return verify_access_token(token)

@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate):
    db = SessionLocal()

    try:
        existing_user = db.query(User).filter(
            User.username == user.username
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        hashed_password = hash_password(user.password)

        db_user = User(
            username=user.username,
            password_hash=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {
            "message": "User created successfully",
            "username": db_user.username
        }

    finally:
        db.close()

@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user: UserCreate):
    db = SessionLocal()

    try:
        db_user = db.query(User).filter(
            User.username == user.username
        ).first()

        if db_user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        if not verify_password(
            user.password,
            db_user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        access_token = create_access_token(db_user.username)

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    finally:
        db.close()

@app.post("/patients/", status_code=status.HTTP_201_CREATED)
def create_patient(
    patient: PatientCreate,
    current_user: str = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        db_patient = Patient(
            patient_id=patient.patient_id,
            name=patient.name,
            age=patient.age,
            email=patient.email,
            number=patient.number,
            gender=patient.gender,
            condition=patient.condition
        )

        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)

        return db_patient

    finally:
        db.close()

@app.get("/patients/")
def get_patients(current_user: str = Depends(get_current_user)):
    db = SessionLocal()

    try:
        return db.query(Patient).all()

    finally:
        db.close()


@app.get("/patients/{patient_id}")
def get_patient(
    patient_id: str,
    current_user: str = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )

        return patient

    finally:
        db.close()

@app.put("/patients/{patient_id}")
def update_patient(
    patient_id: str,
    updated_patient: PatientCreate,
    current_user: str = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )

        patient.name = updated_patient.name
        patient.age = updated_patient.age
        patient.email = updated_patient.email
        patient.number = updated_patient.number
        patient.gender = updated_patient.gender
        patient.condition = updated_patient.condition

        db.commit()
        db.refresh(patient)

        return patient

    finally:
        db.close()


@app.delete(
    "/patients/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_patient(
    patient_id: str,
    current_user: str = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )

        db.delete(patient)
        db.commit()

    finally:
        db.close()
