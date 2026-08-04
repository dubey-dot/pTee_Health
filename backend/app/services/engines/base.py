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
