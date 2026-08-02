from fastapi import APIRouter, HTTPException

from app.schemas.patient import PatientCreate, PatientSummary, PatientUpdate
from app.services import patients as patients_service

router = APIRouter()


@router.get("/patients", response_model=list[PatientSummary])
def list_patients() -> list[PatientSummary]:
    return patients_service.list_patients()


@router.post("/patients", response_model=PatientSummary, status_code=201)
def create_patient(data: PatientCreate) -> PatientSummary:
    return patients_service.create_patient(data)


@router.get("/patients/{patient_id}", response_model=PatientSummary)
def get_patient(patient_id: str) -> PatientSummary:
    patient = patients_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/patients/{patient_id}", response_model=PatientSummary)
def update_patient(patient_id: str, data: PatientUpdate) -> PatientSummary:
    patient = patients_service.update_patient(patient_id, data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
