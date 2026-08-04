from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int | None] = mapped_column(Integer)
    gender: Mapped[str | None] = mapped_column(String)
    occupation_sport: Mapped[str | None] = mapped_column(String)
    chief_complaint: Mapped[str | None] = mapped_column(String)
    duration: Mapped[str | None] = mapped_column(String)
    pain_score: Mapped[str | None] = mapped_column(String)
    aggravating: Mapped[str | None] = mapped_column(String)
    relieving: Mapped[str | None] = mapped_column(String)
    previous_injuries: Mapped[str | None] = mapped_column(String)
    clinical_summary: Mapped[str] = mapped_column(Text, default="")
    doctors_notes_count: Mapped[int] = mapped_column(Integer, default=0)
