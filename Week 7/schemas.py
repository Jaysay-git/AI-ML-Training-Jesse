from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

class UserCreate(BaseModel):
    username: str
    password: str


# --------------------------------------------------
# PATIENT CRUD
# --------------------------------------------------

class PatientCreate(BaseModel):
    patient_id: str
    name: str
    age: int = Field(ge=0, le=120)
    email: EmailStr
    number: str
    gender: str
    condition: str

    @field_validator("number")
    @classmethod
    def validate_phone_number(cls, value):
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")

        if len(value) != 11:
            raise ValueError("Phone number must be exactly 11 digits")

        if not value.startswith("0"):
            raise ValueError("Phone number must start with 0")

        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):
        if value not in ["M", "F"]:
            raise ValueError("Gender must be M or F")

        return value


# --------------------------------------------------
# ML PREDICTION
# --------------------------------------------------

class PredictionRequest(BaseModel):
    age: int
    gender: str
    temperature: float
    heart_rate: int
    oxygen_saturation: float
    previous_admissions: int
    symptom_count: int
    chronic_condition: int


# --------------------------------------------------
# LLM PATIENT EXTRACTION
# --------------------------------------------------

class PatientExtractionRequest(BaseModel):
    text: str


class ExtractedPatientInfo(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    symptoms: list[str] = Field(default_factory=list)
    temperature: Optional[float] = None


class PatientRecordResponse(BaseModel):
    patient_id: str
    name: str
    age: int
    email: str
    number: str
    gender: str
    condition: str


class NewPatientInformation(BaseModel):
    symptoms: list[str] = Field(default_factory=list)
    temperature: Optional[float] = None


class PatientExtractionResponse(BaseModel):
    patient: PatientRecordResponse
    new_information: NewPatientInformation