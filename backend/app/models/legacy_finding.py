from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_sessions.id"), nullable=False, index=True
    )
    tag: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, default=False)
    detail: Mapped[dict | None] = mapped_column(JSON)
    order: Mapped[int] = mapped_column(Integer, default=0)
