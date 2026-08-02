from fastapi import APIRouter, HTTPException

from app.schemas.insight import Insights
from app.services import insights as insights_service

router = APIRouter()


@router.get("/assessments/{assessment_id}/insights", response_model=Insights)
def get_insights(assessment_id: str) -> Insights:
    insights = insights_service.get_insights(assessment_id)
    if not insights:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return insights
