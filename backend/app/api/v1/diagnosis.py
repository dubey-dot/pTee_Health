import anthropic
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


@router.post("/assessments/{assessment_id}/diagnosis/generate", response_model=Assessment)
def generate_diagnosis(assessment_id: str, db: Session = Depends(get_db)) -> Assessment:
    """Runs the Claude-backed working-diagnosis engine and persists diagnosis,
    confidence, and insights in one call. 502 (not 500) on any Anthropic API
    failure — including a missing/invalid ANTHROPIC_API_KEY — since this is a
    real upstream-service failure, not a bug in this endpoint; the assessment's
    existing diagnosis/confidence are left untouched.
    """
    try:
        assessment = assessments_service.generate_diagnosis(db, assessment_id)
    except (anthropic.APIStatusError, anthropic.APIConnectionError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {exc}") from exc
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment
