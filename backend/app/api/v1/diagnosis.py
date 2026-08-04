from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.assessment import Assessment, DiagnosisUpdate
from app.services import assessments as assessments_service

router = APIRouter()


@router.get("/assessments/{assessment_id}/diagnosis", response_model=Assessment)
def get_diagnosis(assessment_id: str, db: Session = Depends(get_db)) -> Assessment:
    assessment = assessments_service.get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.patch("/assessments/{assessment_id}/diagnosis", response_model=Assessment)
def update_diagnosis(
    assessment_id: str, data: DiagnosisUpdate, db: Session = Depends(get_db)
) -> Assessment:
    assessment = assessments_service.update_diagnosis(db, assessment_id, data)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment
