from fastapi import FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Patient
from schemas import PatientCreate

app = FastAPI()



@app.post("/patients/", status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate):
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
def get_patients():
    db = SessionLocal()

    try:
        return db.query(Patient).all()

    finally:
        db.close()


@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
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
    updated_patient: PatientCreate
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
def delete_patient(patient_id: str):
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
