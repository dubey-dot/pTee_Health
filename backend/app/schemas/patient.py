from app.schemas.base import CamelModel


class PatientField(CamelModel):
    label: str
    value: str


class PatientSummary(CamelModel):
    id: str
    name: str
    fields: list[PatientField]
    clinical_summary: str
    doctors_notes_count: int = 0


class PatientCreate(CamelModel):
    name: str
    age: int | None = None
    gender: str | None = None
    occupation_sport: str | None = None
    chief_complaint: str | None = None
    duration: str | None = None
    pain_score: str | None = None
    aggravating: str | None = None
    relieving: str | None = None
    previous_injuries: str | None = None
    clinical_summary: str = ""


class PatientUpdate(CamelModel):
    name: str | None = None
    age: int | None = None
    gender: str | None = None
    occupation_sport: str | None = None
    chief_complaint: str | None = None
    duration: str | None = None
    pain_score: str | None = None
    aggravating: str | None = None
    relieving: str | None = None
    previous_injuries: str | None = None
    clinical_summary: str | None = None
    doctors_notes_count: int | None = None
