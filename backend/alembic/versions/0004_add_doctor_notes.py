"""add doctor_notes table

Backs POST/GET /assessments/{id}/notes — the Doctor's Notes section on the
Assessment screen, supporting both typed and voice-dictated (transcribed
client-side) notes, one row per note, scoped to its assessment session.

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "doctor_notes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "assessment_id", sa.String(), sa.ForeignKey("assessment_sessions.id"), nullable=False
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(), nullable=False, server_default="typed"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True
        ),
    )
    op.create_index("ix_doctor_notes_assessment_id", "doctor_notes", ["assessment_id"])


def downgrade() -> None:
    op.drop_table("doctor_notes")
