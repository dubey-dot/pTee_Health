import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assessment_session import AssessmentSession
from app.models.patient import Patient
from app.schemas.assessment import Assessment, AssessmentUpdate, DiagnosisUpdate


def _to_schema(record: AssessmentSession) -> Assessment:
    return Assessment(
        id=record.id,
        patient_id=record.patient_id,
        status=record.status,
        diagnosis=record.diagnosis,
        confidence=record.confidence,
        diagnosis_action=record.diagnosis_action,
        version=record.version,
    )


def list_assessments_for_patient(db: Session, patient_id: str) -> list[Assessment]:
    records = db.scalars(
        select(AssessmentSession).where(AssessmentSession.patient_id == patient_id)
    ).all()
    return [_to_schema(a) for a in records]


def get_assessment(db: Session, assessment_id: str) -> Assessment | None:
    record = db.get(AssessmentSession, assessment_id)
    return _to_schema(record) if record else None


def create_assessment(db: Session, patient_id: str) -> Assessment | None:
    if db.get(Patient, patient_id) is None:
        return None
    assessment_id = f"assessment-{uuid.uuid4().hex[:8]}"
    record = AssessmentSession(id=assessment_id, patient_id=patient_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_schema(record)


def update_assessment(db: Session, assessment_id: str, data: AssessmentUpdate) -> Assessment | None:
    record = db.get(AssessmentSession, assessment_id)
    if not record:
        return None
    if data.status is not None:
        record.status = data.status
        record.version += 1
    db.commit()
    db.refresh(record)
    return _to_schema(record)


def update_diagnosis(db: Session, assessment_id: str, data: DiagnosisUpdate) -> Assessment | None:
    record = db.get(AssessmentSession, assessment_id)
    if not record:
        return None
    if data.diagnosis is not None:
        record.diagnosis = data.diagnosis
    if data.action is not None:
        record.diagnosis_action = data.action
    record.version += 1
    db.commit()
    db.refresh(record)
    return _to_schema(record)
