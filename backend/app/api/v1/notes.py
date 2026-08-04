from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.note import DoctorNote, DoctorNoteCreate
from app.services import notes as notes_service

router = APIRouter()


@router.get("/assessments/{assessment_id}/notes", response_model=list[DoctorNote])
def list_notes(assessment_id: str, db: Session = Depends(get_db)) -> list[DoctorNote]:
    return notes_service.list_notes(db, assessment_id)


@router.post("/assessments/{assessment_id}/notes", response_model=DoctorNote, status_code=201)
def create_note(
    assessment_id: str, data: DoctorNoteCreate, db: Session = Depends(get_db)
) -> DoctorNote:
    note = notes_service.create_note(db, assessment_id, data)
    if not note:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return note
