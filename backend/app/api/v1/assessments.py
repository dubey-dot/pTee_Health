from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.assessment import Assessment, AssessmentUpdate
from app.services import assessments as assessments_service

router = APIRouter()


@router.get("/patients/{patient_id}/assessments", response_model=list[Assessment])
def list_assessments(patient_id: str, db: Session = Depends(get_db)) -> list[Assessment]:
    return assessments_service.list_assessments_for_patient(db, patient_id)


@router.post("/patients/{patient_id}/assessments", response_model=Assessment, status_code=201)
def create_assessment(patient_id: str, db: Session = Depends(get_db)) -> Assessment:
    assessment = assessments_service.create_assessment(db, patient_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Patient not found")
    return assessment


@router.get("/assessments/{assessment_id}", response_model=Assessment)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)) -> Assessment:
    assessment = assessments_service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.patch("/assessments/{assessment_id}", response_model=Assessment)
def update_assessment(
    assessment_id: str, data: AssessmentUpdate, db: Session = Depends(get_db)
) -> Assessment:
    assessment = assessments_service.update_assessment(db, assessment_id, data)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment
