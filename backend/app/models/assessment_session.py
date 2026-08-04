from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AssessmentSession(Base):
    """Table name is `assessment_sessions` — the Phase-1 promotion of the
    original `assessments` fixture table, so every later phase (which FKs
    everything to a session) has a stable anchor from day one. The API path
    stays `/assessments/...` unchanged; this is a persistence-layer rename
    only, invisible to the frontend.
    """

    __tablename__ = "assessment_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, default="reviewing")
    diagnosis: Mapped[str] = mapped_column(String, default="")
    confidence: Mapped[int] = mapped_column(Integer, default=0)
    diagnosis_action: Mapped[str | None] = mapped_column(String)
    version: Mapped[int] = mapped_column(Integer, default=1)
    # Populated by POST /assessments/{id}/diagnosis/generate (Claude-backed).
    # Null until first generated — insights_service falls back to a fixture
    # summary in that case, so GET /insights never 404s on a fresh assessment.
    insight_summary: Mapped[str | None] = mapped_column(Text)
    insight_tags: Mapped[list | None] = mapped_column(JSON)
