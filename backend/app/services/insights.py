"""Generates the Insights panel content for an assessment.

Fixture-backed for Phase 2. This is the seam Phase 4 swaps: retrieval over
findings/tests + an LLM call replaces the hardcoded response below, but the
return shape (and therefore the route and frontend contract) doesn't change.
"""

from app.schemas.insight import InsightTag, Insights
from app.services.store import ASSESSMENTS


def get_insights(assessment_id: str) -> Insights | None:
    if assessment_id not in ASSESSMENTS:
        return None
    return Insights(
        assessment_id=assessment_id,
        summary=(
            "Biceps Femoris: Quad — weak. Next, Pelvis Shift Right/Left. A lateral "
            "pelvic shift changes hip loading and frontal-plane control."
        ),
        tags=[InsightTag(label="Biceps Femoris — Quad — weak", meta="8 recorded")],
    )
