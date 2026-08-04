from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.patient import PatientCreate, PatientSummary, PatientUpdate
from app.services import patients as patients_service

router = APIRouter()


@router.get("/patients", response_model=list[PatientSummary])
def list_patients(db: Session = Depends(get_db)) -> list[PatientSummary]:
    return patients_service.list_patients(db)


@router.post("/patients", response_model=PatientSummary, status_code=201)
def create_patient(data: PatientCreate, db: Session = Depends(get_db)) -> PatientSummary:
    return patients_service.create_patient(db, data)


@router.get("/patients/{patient_id}", response_model=PatientSummary)
def get_patient(patient_id: str, db: Session = Depends(get_db)) -> PatientSummary:
    patient = patients_service.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/patients/{patient_id}", response_model=PatientSummary)
def update_patient(
    patient_id: str, data: PatientUpdate, db: Session = Depends(get_db)
) -> PatientSummary:
    patient = patients_service.update_patient(db, patient_id, data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
