"""In-memory fixture store for Phase 2.

Stands in for a real database until Phase 3. Seeded with the same data that
used to be hardcoded as frontend component defaults, so wiring the frontend
to these endpoints is behavior-neutral. Swapping this for SQLAlchemy models
in Phase 3 only touches this module and the services that use it — the
schemas and routes are unaffected.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PatientRecord:
    id: str
    name: str
    age: int | None
    gender: str | None
    occupation_sport: str | None
    chief_complaint: str | None
    duration: str | None
    pain_score: str | None
    aggravating: str | None
    relieving: str | None
    previous_injuries: str | None
    clinical_summary: str
    doctors_notes_count: int = 0


@dataclass
class AssessmentRecord:
    id: str
    patient_id: str
    status: str = "reviewing"
    diagnosis: str = ""
    confidence: int = 0
    diagnosis_action: str | None = None
    version: int = 1


@dataclass
class FindingRecord:
    id: str
    assessment_id: str
    tag: str
    label: str
    selected: bool = False
    detail: dict | None = None
    order: int = 0


@dataclass
class TestRecord:
    id: str
    assessment_id: str
    type: str
    name: str
    result: str = ""


PATIENTS: dict[str, PatientRecord] = {}
ASSESSMENTS: dict[str, AssessmentRecord] = {}
FINDINGS: dict[str, FindingRecord] = {}
TESTS: dict[str, TestRecord] = {}


def bump_assessment_version(assessment_id: str) -> None:
    assessment = ASSESSMENTS.get(assessment_id)
    if assessment:
        assessment.version += 1


def seed() -> None:
    if PATIENTS:
        return

    patient = PatientRecord(
        id="patient-1",
        name="Ankita Sharma",
        age=32,
        gender="Female",
        occupation_sport="a software engineer and i · runner",
        chief_complaint="Right anterior knee pain",
        duration="3 months",
        pain_score="",
        aggravating="stairs, squatting, better with rest, ice",
        relieving="rest, ice",
        previous_injuries="",
        clinical_summary=(
            "Presenting with right anterior knee pain for 3 months. Findings so far "
            "involve Pelvis, Hip, Ankle, with pelvis anterior; hip restricted; ankle "
            "limited. Muscle picture: Glute Med (overactive), Tfl (overactive), Quad "
            "(weak), Hamstring (weak)."
        ),
        doctors_notes_count=0,
    )
    PATIENTS[patient.id] = patient

    assessment = AssessmentRecord(
        id="assessment-1",
        patient_id=patient.id,
        status="completed",
        diagnosis="Load-related right anterior knee pain",
        confidence=64,
        diagnosis_action="agree",
        version=1,
    )
    ASSESSMENTS[assessment.id] = assessment

    findings = [
        FindingRecord(
            id="pelvis-shift",
            assessment_id=assessment.id,
            tag="GAIT",
            label="Pelvis Shift Right/Left",
            selected=True,
            detail={
                "question": "Is the pelvis shifted to one side over the feet?",
                "bullets": [
                    "Shift right / left",
                    "Weight distribution",
                    "Lateral trunk lean",
                    "Frontal-plane symmetry",
                ],
            },
            order=0,
        ),
        FindingRecord(
            id="pelvis-rotation",
            assessment_id=assessment.id,
            tag="JOINT",
            label="Pelvis Rotation Right/Left",
            order=1,
        ),
        FindingRecord(
            id="ribcage-position",
            assessment_id=assessment.id,
            tag="JOINT",
            label="Ribcage Position",
            order=2,
        ),
        FindingRecord(
            id="neck-position",
            assessment_id=assessment.id,
            tag="JOINT",
            label="Neck Position",
            order=3,
        ),
        FindingRecord(
            id="spinal-position",
            assessment_id=assessment.id,
            tag="JOINT",
            label="Spinal Position",
            order=4,
        ),
    ]
    for finding in findings:
        FINDINGS[finding.id] = finding


seed()
