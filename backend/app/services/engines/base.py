from typing import Protocol

from pydantic import BaseModel, Field


class GeneratedInsightTag(BaseModel):
    label: str
    meta: str


class GeneratedAssessment(BaseModel):
    """Structured-output shape for the combined working-diagnosis +
    confidence + insights generation call. One LLM call, one schema —
    cheaper and more internally consistent than three separate round trips
    reasoning over the same findings.
    """

    diagnosis: str
    confidence: int = Field(ge=0, le=100)
    reasoning: str
    insight_summary: str
    insight_tags: list[GeneratedInsightTag]


class WorkingDiagnosisEngine(Protocol):
    """The AI seam. `services/assessments.py` only ever calls this
    interface — never a concrete engine class — so swapping the model,
    prompt, or provider later never touches the calling service or the API
    route above it.
    """

    def generate(
        self,
        *,
        patient_summary: str,
        clinical_summary: str,
        findings: list[dict],
    ) -> GeneratedAssessment: ...


class RecommendedTest(BaseModel):
    """One recommended assessment within a batch, in the shape required by
    recommendation_rules.md Rule 3."""

    test_name: str
    # Short, always-visible line — the clinical pattern/signal driving the
    # recommendation (e.g. "Upper trapezius dominance, suspected
    # cervicogenic headache"). Not the full reasoning — see why_recommended.
    summary: str
    # Fuller reasoning shown only when the doctor expands "Why this test" —
    # what the test is/does, why it's recommended, and which specific
    # intake/finding/note signals triggered it.
    why_recommended: str
    # How confident the engine is that *this specific test* is worth
    # doing — independent of the overall working-diagnosis confidence.
    confidence: int = Field(ge=0, le=100)


class TestRecommendationBatch(BaseModel):
    """Root structured-output shape for the recommendation engine — a
    ranked batch (Rule 1), not a single test. `tests` is empty when no
    further tests are worth recommending (confidence is already
    sufficient, or the remaining gap can't be closed by more testing);
    `no_recommendation_reason` explains why in that case.
    """

    tests: list[RecommendedTest] = []
    no_recommendation_reason: str | None = None


class RecommendationEngine(Protocol):
    """The AI seam for "what should the clinician test next" — mirrors
    WorkingDiagnosisEngine's swappable-behind-a-Protocol pattern.
    """

    def recommend(
        self,
        *,
        patient_summary: str,
        clinical_summary: str,
        doctor_notes: list[str],
        findings: list[dict],
        logged_tests: list[dict],
    ) -> TestRecommendationBatch: ...
