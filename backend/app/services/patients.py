import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientField, PatientSummary, PatientUpdate


def _age_gender(record: Patient) -> str:
    parts = [str(record.age)] if record.age is not None else []
    if record.gender:
        parts.append(record.gender)
    return " · ".join(parts)


def _to_summary(record: Patient) -> PatientSummary:
    fields = [
        PatientField(label="Name", value=record.name),
        PatientField(label="Age / Gender", value=_age_gender(record)),
        PatientField(label="Occupation / Sport", value=record.occupation_sport or ""),
        PatientField(label="Chief complaint", value=record.chief_complaint or ""),
        PatientField(label="Duration", value=record.duration or ""),
        PatientField(label="Pain score", value=record.pain_score or ""),
        PatientField(label="Aggravating", value=record.aggravating or ""),
        PatientField(label="Relieving", value=record.relieving or ""),
        PatientField(label="Previous injuries", value=record.previous_injuries or ""),
    ]
    return PatientSummary(
        id=record.id,
        name=record.name,
        fields=fields,
        clinical_summary=record.clinical_summary,
        doctors_notes_count=record.doctors_notes_count,
    )


def list_patients(db: Session) -> list[PatientSummary]:
    records = db.scalars(select(Patient)).all()
    return [_to_summary(record) for record in records]


def get_patient(db: Session, patient_id: str) -> PatientSummary | None:
    record = db.get(Patient, patient_id)
    return _to_summary(record) if record else None


def create_patient(db: Session, data: PatientCreate) -> PatientSummary:
    patient_id = f"patient-{uuid.uuid4().hex[:8]}"
    record = Patient(
        id=patient_id,
        name=data.name,
        age=data.age,
        gender=data.gender,
        occupation_sport=data.occupation_sport,
        chief_complaint=data.chief_complaint,
        duration=data.duration,
        pain_score=data.pain_score,
        aggravating=data.aggravating,
        relieving=data.relieving,
        previous_injuries=data.previous_injuries,
        clinical_summary=data.clinical_summary,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_summary(record)


def update_patient(db: Session, patient_id: str, data: PatientUpdate) -> PatientSummary | None:
    record = db.get(Patient, patient_id)
    if not record:
        return None
    for field_name, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field_name, value)
    db.commit()
    db.refresh(record)
    return _to_summary(record)
