from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.insight import Insights
from app.services import insights as insights_service

router = APIRouter()


@router.get("/assessments/{assessment_id}/insights", response_model=Insights)
def get_insights(assessment_id: str, db: Session = Depends(get_db)) -> Insights:
    insights = insights_service.get_insights(db, assessment_id)
    if not insights:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return insights
