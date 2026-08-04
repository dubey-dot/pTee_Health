from datetime import datetime
from typing import Literal

from app.schemas.base import CamelModel

NoteSource = Literal["typed", "voice"]


class DoctorNote(CamelModel):
    id: str
    assessment_id: str
    content: str
    source: NoteSource
    created_at: datetime


class DoctorNoteCreate(CamelModel):
    content: str
    source: NoteSource = "typed"
