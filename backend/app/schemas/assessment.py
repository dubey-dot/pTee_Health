from typing import Literal

from app.schemas.base import CamelModel

AssessmentStatus = Literal["reviewing", "completed"]
DiagnosisAction = Literal["agree", "update", "fully-change"]


class Assessment(CamelModel):
    id: str
    patient_id: str
    status: AssessmentStatus
    diagnosis: str
    confidence: int
    diagnosis_action: DiagnosisAction | None = None
    version: int


class AssessmentUpdate(CamelModel):
    status: AssessmentStatus | None = None


class DiagnosisUpdate(CamelModel):
    action: DiagnosisAction | None = None
    diagnosis: str | None = None
