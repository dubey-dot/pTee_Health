"""initial schema — patients, assessment_sessions, findings, logged_tests

Revision ID: 0001
Revises:
Create Date: 2026-08-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("occupation_sport", sa.String(), nullable=True),
        sa.Column("chief_complaint", sa.String(), nullable=True),
        sa.Column("duration", sa.String(), nullable=True),
        sa.Column("pain_score", sa.String(), nullable=True),
        sa.Column("aggravating", sa.String(), nullable=True),
        sa.Column("relieving", sa.String(), nullable=True),
        sa.Column("previous_injuries", sa.String(), nullable=True),
        sa.Column("clinical_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("doctors_notes_count", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "assessment_sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("patient_id", sa.String(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="reviewing"),
        sa.Column("diagnosis", sa.String(), nullable=False, server_default=""),
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("diagnosis_action", sa.String(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_assessment_sessions_patient_id", "assessment_sessions", ["patient_id"])

    op.create_table(
        "findings",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "assessment_id", sa.String(), sa.ForeignKey("assessment_sessions.id"), nullable=False
        ),
        sa.Column("tag", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_findings_assessment_id", "findings", ["assessment_id"])

    op.create_table(
        "logged_tests",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "assessment_id", sa.String(), sa.ForeignKey("assessment_sessions.id"), nullable=False
        ),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("result", sa.String(), nullable=False, server_default=""),
    )
    op.create_index("ix_logged_tests_assessment_id", "logged_tests", ["assessment_id"])


def downgrade() -> None:
    op.drop_table("logged_tests")
    op.drop_table("findings")
    op.drop_table("assessment_sessions")
    op.drop_table("patients")
