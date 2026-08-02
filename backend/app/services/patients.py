import uuid

from app.schemas.patient import PatientCreate, PatientField, PatientSummary, PatientUpdate
from app.services.store import PATIENTS, PatientRecord


def _age_gender(record: PatientRecord) -> str:
    parts = [str(record.age)] if record.age is not None else []
    if record.gender:
        parts.append(record.gender)
    return " · ".join(parts)


def _to_summary(record: PatientRecord) -> PatientSummary:
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


def list_patients() -> list[PatientSummary]:
    return [_to_summary(record) for record in PATIENTS.values()]


def get_patient(patient_id: str) -> PatientSummary | None:
    record = PATIENTS.get(patient_id)
    return _to_summary(record) if record else None


def create_patient(data: PatientCreate) -> PatientSummary:
    patient_id = f"patient-{uuid.uuid4().hex[:8]}"
    record = PatientRecord(
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
    PATIENTS[patient_id] = record
    return _to_summary(record)


def update_patient(patient_id: str, data: PatientUpdate) -> PatientSummary | None:
    record = PATIENTS.get(patient_id)
    if not record:
        return None
    for field_name, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field_name, value)
    return _to_summary(record)
