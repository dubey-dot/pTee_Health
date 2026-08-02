from fastapi import APIRouter, HTTPException

from app.schemas.assessment import Assessment, DiagnosisUpdate
from app.services import assessments as assessments_service

router = APIRouter()


@router.get("/assessments/{assessment_id}/diagnosis", response_model=Assessment)
def get_diagnosis(assessment_id: str) -> Assessment:
    assessment = assessments_service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.patch("/assessments/{assessment_id}/diagnosis", response_model=Assessment)
def update_diagnosis(assessment_id: str, data: DiagnosisUpdate) -> Assessment:
    assessment = assessments_service.update_diagnosis(assessment_id, data)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment
