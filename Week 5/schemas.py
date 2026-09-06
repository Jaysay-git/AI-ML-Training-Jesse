from pydantic import BaseModel, EmailStr, Field, field_validator


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

class UserCreate(BaseModel):
    username: str
    password: str