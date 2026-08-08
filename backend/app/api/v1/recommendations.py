import anthropic
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.recommendation import TestRecommendationBatch
from app.services import recommendations as recommendations_service

router = APIRouter()


@router.post("/assessments/{assessment_id}/recommendations", response_model=TestRecommendationBatch)
def get_recommendations(assessment_id: str, db: Session = Depends(get_db)) -> TestRecommendationBatch:
    """Advisory only — does not persist anything or bump the assessment's
    version; the doctor logs the actual performed test separately via the
    existing findings/tests endpoints once it's done. 502 (not 500) on any
    Anthropic failure, same convention as /diagnosis/generate.
    """
    try:
        result = recommendations_service.get_recommendations(db, assessment_id)
    except (anthropic.APIStatusError, anthropic.APIConnectionError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=f"AI recommendation failed: {exc}") from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return result
