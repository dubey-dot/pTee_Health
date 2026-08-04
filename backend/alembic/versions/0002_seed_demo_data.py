"""seed demo data — patient-1 / assessment-1 / 5 findings

Reproduces the same fixture data that used to live in the in-memory
store.py, so this migration is behavior-neutral for anyone running the app
locally against a fresh database.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

patients = sa.table(
    "patients",
    sa.column("id", sa.String),
    sa.column("name", sa.String),
    sa.column("age", sa.Integer),
    sa.column("gender", sa.String),
    sa.column("occupation_sport", sa.String),
    sa.column("chief_complaint", sa.String),
    sa.column("duration", sa.String),
    sa.column("pain_score", sa.String),
    sa.column("aggravating", sa.String),
    sa.column("relieving", sa.String),
    sa.column("previous_injuries", sa.String),
    sa.column("clinical_summary", sa.Text),
    sa.column("doctors_notes_count", sa.Integer),
)

assessment_sessions = sa.table(
    "assessment_sessions",
    sa.column("id", sa.String),
    sa.column("patient_id", sa.String),
    sa.column("status", sa.String),
    sa.column("diagnosis", sa.String),
    sa.column("confidence", sa.Integer),
    sa.column("diagnosis_action", sa.String),
    sa.column("version", sa.Integer),
)

findings = sa.table(
    "findings",
    sa.column("id", sa.String),
    sa.column("assessment_id", sa.String),
    sa.column("tag", sa.String),
    sa.column("label", sa.String),
    sa.column("selected", sa.Boolean),
    sa.column("detail", sa.JSON),
    sa.column("order", sa.Integer),
)


def upgrade() -> None:
    op.bulk_insert(
        patients,
        [
            {
                "id": "patient-1",
                "name": "Ankita Sharma",
                "age": 32,
                "gender": "Female",
                "occupation_sport": "a software engineer and i · runner",
                "chief_complaint": "Right anterior knee pain",
                "duration": "3 months",
                "pain_score": "",
                "aggravating": "stairs, squatting, better with rest, ice",
                "relieving": "rest, ice",
                "previous_injuries": "",
                "clinical_summary": (
                    "Presenting with right anterior knee pain for 3 months. Findings so far "
                    "involve Pelvis, Hip, Ankle, with pelvis anterior; hip restricted; ankle "
                    "limited. Muscle picture: Glute Med (overactive), Tfl (overactive), Quad "
                    "(weak), Hamstring (weak)."
                ),
                "doctors_notes_count": 0,
            }
        ],
    )

    op.bulk_insert(
        assessment_sessions,
        [
            {
                "id": "assessment-1",
                "patient_id": "patient-1",
                "status": "completed",
                "diagnosis": "Load-related right anterior knee pain",
                "confidence": 64,
                "diagnosis_action": "agree",
                "version": 1,
            }
        ],
    )

    op.bulk_insert(
        findings,
        [
            {
                "id": "pelvis-shift",
                "assessment_id": "assessment-1",
                "tag": "GAIT",
                "label": "Pelvis Shift Right/Left",
                "selected": True,
                "detail": {
                    "question": "Is the pelvis shifted to one side over the feet?",
                    "bullets": [
                        "Shift right / left",
                        "Weight distribution",
                        "Lateral trunk lean",
                        "Frontal-plane symmetry",
                    ],
                },
                "order": 0,
            },
            {
                "id": "pelvis-rotation",
                "assessment_id": "assessment-1",
                "tag": "JOINT",
                "label": "Pelvis Rotation Right/Left",
                "selected": False,
                "detail": None,
                "order": 1,
            },
            {
                "id": "ribcage-position",
                "assessment_id": "assessment-1",
                "tag": "JOINT",
                "label": "Ribcage Position",
                "selected": False,
                "detail": None,
                "order": 2,
            },
            {
                "id": "neck-position",
                "assessment_id": "assessment-1",
                "tag": "JOINT",
                "label": "Neck Position",
                "selected": False,
                "detail": None,
                "order": 3,
            },
            {
                "id": "spinal-position",
                "assessment_id": "assessment-1",
                "tag": "JOINT",
                "label": "Spinal Position",
                "selected": False,
                "detail": None,
                "order": 4,
            },
        ],
    )


def downgrade() -> None:
    op.execute(findings.delete().where(findings.c.assessment_id == "assessment-1"))
    op.execute(assessment_sessions.delete().where(assessment_sessions.c.id == "assessment-1"))
    op.execute(patients.delete().where(patients.c.id == "patient-1"))
