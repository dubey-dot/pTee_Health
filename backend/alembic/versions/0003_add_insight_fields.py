"""add insight_summary / insight_tags to assessment_sessions

Persists the output of POST /assessments/{id}/diagnosis/generate (the
Claude-backed working diagnosis + insights call) so a subsequent GET
/insights returns the generated content instead of always recomputing.

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("assessment_sessions", sa.Column("insight_summary", sa.Text(), nullable=True))
    op.add_column("assessment_sessions", sa.Column("insight_tags", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("assessment_sessions", "insight_tags")
    op.drop_column("assessment_sessions", "insight_summary")
