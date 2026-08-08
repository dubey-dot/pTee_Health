from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assessment_session import AssessmentSession
from app.models.doctor_note import DoctorNote as DoctorNoteModel
from app.models.legacy_finding import Finding as FindingModel
from app.models.legacy_test import LoggedTest as LoggedTestModel
from app.models.patient import Patient
from app.schemas.recommendation import RecommendedTest, TestRecommendationBatch
from app.services.engines.base import RecommendationEngine
from app.services.engines.recommendation_engine import ClaudeRecommendationEngine


def _to_schema(result) -> TestRecommendationBatch:
    return TestRecommendationBatch(
        tests=[
            RecommendedTest(
                test_name=test.test_name,
                test_type=test.test_type,
                summary=test.summary,
                why_recommended=test.why_recommended,
            )
            for test in result.tests
        ],
        no_recommendation_reason=result.no_recommendation_reason,
    )


def get_recommendations(
    db: Session, assessment_id: str, engine: RecommendationEngine | None = None
) -> TestRecommendationBatch | None:
    """Advisory only — reads current state and asks the engine for a
    ranked batch of tests to consider, but writes nothing to the database
    itself. Deleting a suggestion is client-side only (see
    RecommendedTestsPanel); completing one calls the existing
    POST /assessments/{id}/tests to persist the doctor's findings for
    real. Regenerated fresh on every call from whatever findings/tests/
    notes exist at that moment.
    """
    record = db.get(AssessmentSession, assessment_id)
    if record is None:
        return None

    patient = db.get(Patient, record.patient_id)
    findings = db.scalars(
        select(FindingModel).where(FindingModel.assessment_id == assessment_id)
    ).all()
    logged_tests = db.scalars(
        select(LoggedTestModel).where(LoggedTestModel.assessment_id == assessment_id)
    ).all()
    notes = db.scalars(
        select(DoctorNoteModel).where(DoctorNoteModel.assessment_id == assessment_id)
    ).all()

    result = (engine or ClaudeRecommendationEngine()).recommend(
        patient_summary=patient.chief_complaint if patient else "",
        clinical_summary=patient.clinical_summary if patient else "",
        doctor_notes=[n.content for n in notes],
        findings=[{"tag": f.tag, "label": f.label, "selected": f.selected} for f in findings],
        logged_tests=[{"type": t.type, "name": t.name, "result": t.result} for t in logged_tests],
    )
    return _to_schema(result)
