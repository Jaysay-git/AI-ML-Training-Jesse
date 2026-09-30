import logging
import time
import uuid
from pathlib import Path

import joblib
import pandas as pd

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from database import SessionLocal
from models import Patient, User
from schemas import (
    PatientCreate,
    UserCreate,
    PredictionRequest,
    PatientExtractionRequest,
    PatientExtractionResponse,
    UploadResponse,
    DocumentSearchResponse,
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)

from llm_service import extract_patient_information

from ingestion import ingest_document, generate_embedding
from vector_store import collection


app = FastAPI(
    title="Hospital Patient Tracker & AI Assistant",
    description=(
        "Hospital Patient Tracker with authentication, "
        "ML-based risk prediction, AI patient information extraction, "
        "and RAG document search."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# ML MODEL
# ---------------------------------------------------------

model = joblib.load("hospital_risk_model.joblib")


# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------

logger = logging.getLogger("hospital_api")

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


# ---------------------------------------------------------
# REQUEST LOGGING MIDDLEWARE
# ---------------------------------------------------------

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
        duration,
    )

    response.headers["X-Request-ID"] = request_id

    return response


# ---------------------------------------------------------
# RATE LIMITING
# ---------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# ---------------------------------------------------------
# GLOBAL ERROR HANDLER
# ---------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred."
        },
    )


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    return verify_access_token(token)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Hospital Patient Tracker & AI Assistant is running"
    }


# ---------------------------------------------------------
# USER AUTHENTICATION
# ---------------------------------------------------------

@app.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
)
def signup(user: UserCreate):
    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.username == user.username)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists",
            )

        hashed_password = hash_password(user.password)

        db_user = User(
            username=user.username,
            password_hash=hashed_password,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {
            "message": "User created successfully",
            "username": db_user.username,
        }

    finally:
        db.close()


@app.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    user: UserCreate,
):
    db = SessionLocal()

    try:
        db_user = (
            db.query(User)
            .filter(User.username == user.username)
            .first()
        )

        if db_user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        if not verify_password(
            user.password,
            db_user.password_hash,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        access_token = create_access_token(
            db_user.username
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    finally:
        db.close()


# ---------------------------------------------------------
# PATIENT ENDPOINTS
# ---------------------------------------------------------

@app.post(
    "/patients/",
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient: PatientCreate,
    current_user: str = Depends(get_current_user),
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
            condition=patient.condition,
        )

        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)

        return db_patient

    finally:
        db.close()


@app.get("/patients/")
def get_patients(
    current_user: str = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        return db.query(Patient).all()

    finally:
        db.close()


@app.get("/patients/{patient_id}")
def get_patient(
    patient_id: str,
    current_user: str = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        patient = (
            db.query(Patient)
            .filter(Patient.patient_id == patient_id)
            .first()
        )

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found",
            )

        return patient

    finally:
        db.close()


@app.put("/patients/{patient_id}")
def update_patient(
    patient_id: str,
    updated_patient: PatientCreate,
    current_user: str = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        patient = (
            db.query(Patient)
            .filter(Patient.patient_id == patient_id)
            .first()
        )

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found",
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
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: str,
    current_user: str = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        patient = (
            db.query(Patient)
            .filter(Patient.patient_id == patient_id)
            .first()
        )

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found",
            )

        db.delete(patient)
        db.commit()

    finally:
        db.close()


# ---------------------------------------------------------
# ML RISK PREDICTION
# ---------------------------------------------------------

@app.post("/predict")
def predict(data: PredictionRequest):
    input_data = pd.DataFrame(
        [data.model_dump()]
    )

    prediction = model.predict(input_data)[0]

    probability = model.predict_proba(
        input_data
    )[0][1]

    return {
        "high_risk": int(prediction),
        "probability": round(
            float(probability),
            4,
        ),
    }


# ---------------------------------------------------------
# AI PATIENT INFORMATION EXTRACTION
# ---------------------------------------------------------

@app.post(
    "/patients/extract",
    response_model=PatientExtractionResponse,
)
def extract_patient(
    request: PatientExtractionRequest,
    current_user: str = Depends(get_current_user),
):
    try:
        extracted = extract_patient_information(
            request.text
        )

        db = SessionLocal()

        try:
            query = db.query(Patient)

            if extracted.name:
                query = query.filter(
                    Patient.name.ilike(
                        f"%{extracted.name}%"
                    )
                )

            if extracted.age is not None:
                query = query.filter(
                    Patient.age == extracted.age
                )

            if extracted.gender:
                gender = (
                    extracted.gender
                    .strip()
                    .lower()
                )

                if gender in ["m", "male"]:
                    query = query.filter(
                        Patient.gender == "M"
                    )

                elif gender in ["f", "female"]:
                    query = query.filter(
                        Patient.gender == "F"
                    )

            patients = query.all()

            if len(patients) == 0:
                raise HTTPException(
                    status_code=404,
                    detail="No matching patient found.",
                )

            if len(patients) > 1:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Multiple patients match the "
                        "provided information. Please "
                        "provide more identifying "
                        "information."
                    ),
                )

            patient = patients[0]

            return {
                "patient": {
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "age": patient.age,
                    "email": patient.email,
                    "number": patient.number,
                    "gender": patient.gender,
                    "condition": patient.condition,
                },
                "new_information": {
                    "symptoms": extracted.symptoms,
                    "temperature": extracted.temperature,
                },
            }

        finally:
            db.close()

    except RuntimeError as exc:
        error_message = str(exc)

        if "timed out" in error_message.lower():
            raise HTTPException(
                status_code=504,
                detail=error_message,
            )

        raise HTTPException(
            status_code=503,
            detail=error_message,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# ---------------------------------------------------------
# DOCUMENT UPLOAD
# ---------------------------------------------------------

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


@app.post(
    "/documents/upload",
    response_model=UploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
):
    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are allowed.",
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=(
                "File is too large. "
                "Maximum size is 5 MB."
            ),
        )

    safe_filename = Path(
        file.filename or "uploaded_file"
    ).name

    file_path = UPLOAD_DIR / safe_filename

    file_path.write_bytes(contents)

    return UploadResponse(
        filename=safe_filename,
        size_bytes=len(contents),
        message="Document uploaded successfully.",
    )


# ---------------------------------------------------------
# DOCUMENT INGESTION
# ---------------------------------------------------------

@app.post("/documents/ingest")
def ingest_uploaded_document(
    filename: str,
    strategy: str = "paragraph",
):
    if strategy not in ["paragraph", "fixed"]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Strategy must be either "
                "'paragraph' or 'fixed'."
            ),
        )

    safe_filename = Path(filename).name
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    try:
        ingest_document(
            file_path=file_path,
            strategy=strategy,
        )

        return {
            "filename": safe_filename,
            "strategy": strategy,
            "message": "Document ingested successfully.",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ---------------------------------------------------------
# DOCUMENT SEMANTIC SEARCH
# ---------------------------------------------------------


@app.post(
    "/documents/search",
    response_model=DocumentSearchResponse,
)
def search_documents(
    query: str,
    n_results: int = 3,
    strategy: str | None = None,
):
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    if n_results < 1 or n_results > 10:
        raise HTTPException(
            status_code=400,
            detail="n_results must be between 1 and 10.",
        )

    if strategy is not None and strategy not in ["paragraph", "fixed"]:
        raise HTTPException(
            status_code=400,
            detail="strategy must be 'paragraph' or 'fixed'.",
        )

    query_embedding = generate_embedding(query)

    where_filter = None

    if strategy is not None:
        where_filter = {
            "chunking_strategy": strategy
        }

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted_results = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        formatted_results.append(
            {
                "text": document,
                "filename": metadata.get(
                    "filename",
                    "",
                ),
                "chunk_index": metadata.get(
                    "chunk_index",
                    0,
                ),
                "source": metadata.get(
                    "source",
                    "",
                ),
                "chunking_strategy": metadata.get(
                    "chunking_strategy",
                    "",
                ),
                "pages": metadata.get(
                    "pages",
                    "",
                ),
                "distance": float(distance),
            }
        )

    return {
        "query": query,
        "strategy": strategy,
        "results": formatted_results,
    }

