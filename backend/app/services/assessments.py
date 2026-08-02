import uuid

from app.schemas.assessment import Assessment, AssessmentUpdate, DiagnosisUpdate
from app.services.store import ASSESSMENTS, PATIENTS, AssessmentRecord


def _to_schema(record: AssessmentRecord) -> Assessment:
    return Assessment(
        id=record.id,
        patient_id=record.patient_id,
        status=record.status,
        diagnosis=record.diagnosis,
        confidence=record.confidence,
        diagnosis_action=record.diagnosis_action,
        version=record.version,
    )


def list_assessments_for_patient(patient_id: str) -> list[Assessment]:
    return [_to_schema(a) for a in ASSESSMENTS.values() if a.patient_id == patient_id]


def get_assessment(assessment_id: str) -> Assessment | None:
    record = ASSESSMENTS.get(assessment_id)
    return _to_schema(record) if record else None


def create_assessment(patient_id: str) -> Assessment | None:
    if patient_id not in PATIENTS:
        return None
    assessment_id = f"assessment-{uuid.uuid4().hex[:8]}"
    record = AssessmentRecord(id=assessment_id, patient_id=patient_id)
    ASSESSMENTS[assessment_id] = record
    return _to_schema(record)


def update_assessment(assessment_id: str, data: AssessmentUpdate) -> Assessment | None:
    record = ASSESSMENTS.get(assessment_id)
    if not record:
        return None
    if data.status is not None:
        record.status = data.status
        record.version += 1
    return _to_schema(record)


def update_diagnosis(assessment_id: str, data: DiagnosisUpdate) -> Assessment | None:
    record = ASSESSMENTS.get(assessment_id)
    if not record:
        return None
    if data.diagnosis is not None:
        record.diagnosis = data.diagnosis
    if data.action is not None:
        record.diagnosis_action = data.action
    record.version += 1
    return _to_schema(record)
