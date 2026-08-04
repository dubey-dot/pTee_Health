import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assessment_session import AssessmentSession
from app.models.doctor_note import DoctorNote as DoctorNoteModel
from app.schemas.note import DoctorNote, DoctorNoteCreate


def _to_schema(record: DoctorNoteModel) -> DoctorNote:
    return DoctorNote(
        id=record.id,
        assessment_id=record.assessment_id,
        content=record.content,
        source=record.source,
        created_at=record.created_at,
    )


def list_notes(db: Session, assessment_id: str) -> list[DoctorNote]:
    records = db.scalars(
        select(DoctorNoteModel)
        .where(DoctorNoteModel.assessment_id == assessment_id)
        .order_by(DoctorNoteModel.created_at)
    ).all()
    return [_to_schema(n) for n in records]


def create_note(db: Session, assessment_id: str, data: DoctorNoteCreate) -> DoctorNote | None:
    assessment = db.get(AssessmentSession, assessment_id)
    if assessment is None:
        return None
    note_id = f"note-{uuid.uuid4().hex[:8]}"
    record = DoctorNoteModel(
        id=note_id,
        assessment_id=assessment_id,
        content=data.content,
        source=data.source,
    )
    db.add(record)
    assessment.version += 1
    db.commit()
    db.refresh(record)
    return _to_schema(record)
