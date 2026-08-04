from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LoggedTest(Base):
    __tablename__ = "logged_tests"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    assessment_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_sessions.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[str] = mapped_column(String, default="")
