"""Generates the Insights panel content for an assessment.

`assessment_sessions.insight_summary` / `.insight_tags` are populated by
`services/assessments.py::generate_diagnosis` (the Claude-backed combined
diagnosis + confidence + insights call). Until that's been run at least once
for a given assessment, those columns are null and this falls back to a
fixture summary — so GET /insights never 404s or returns empty content on a
freshly created assessment.
"""

from sqlalchemy.orm import Session

from app.models.assessment_session import AssessmentSession
from app.schemas.insight import InsightTag, Insights

_FIXTURE_SUMMARY = (
    "No AI-generated insights yet — click \"Working diagnosis\" and generate "
    "one, or log findings first so there's something to reason about."
)
_FIXTURE_TAGS: list[InsightTag] = []


def get_insights(db: Session, assessment_id: str) -> Insights | None:
    record = db.get(AssessmentSession, assessment_id)
    if record is None:
        return None

    if record.insight_summary is not None:
        return Insights(
            assessment_id=assessment_id,
            summary=record.insight_summary,
            tags=[InsightTag(**tag) for tag in (record.insight_tags or [])],
        )

    return Insights(assessment_id=assessment_id, summary=_FIXTURE_SUMMARY, tags=_FIXTURE_TAGS)
