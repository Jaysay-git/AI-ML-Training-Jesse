from fastapi import FastAPI, HTTPException, status, Body 
from pydantic import BaseModel, EmailStr, Field, field_validator

app = FastAPI()

class Patient(BaseModel):
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


patients = []

@app.post("/details/")
def create_patient(
    patient_id: str,
    name: str,
    age: int,
    email: str,
    number: str,
    gender: str,
    condition: str
):
    patient = Patient(
        patient_id=patient_id,
        name=name,
        age=age,
        email=email,
        number=number,
        gender=gender,
        condition=condition
    )

    patients.append(patient)
    return patients

@app.get("/patients/")
def get_patients():
    return patients

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    for patient in patients:
        if patient.patient_id == patient_id:
            return patient

    raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )



@app.put("/patients/{patient_id}")
def update_patient(
    patient_id: str,
    updated_patient: Patient = Body(...)
):
    for i, patient in enumerate(patients):
        if patient.patient_id == patient_id:
            patients[i] = updated_patient
            return updated_patient

    raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )

@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: str):
    for i, patient in enumerate(patients):
        if patient.patient_id == patient_id:
            patients.pop(i)
            return
    raise HTTPException(
    status_code=404,
    detail="Patient not found"
)



@app.post("/patients/", status_code=status.HTTP_201_CREATED)
def create_patient(patient: Patient):
    patients.append(patient)
    return patient

