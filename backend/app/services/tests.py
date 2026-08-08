import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assessment_session import AssessmentSession
from app.models.legacy_test import LoggedTest as LoggedTestModel
from app.schemas.test import LoggedTest, LoggedTestCreate, LoggedTestUpdate


def _to_schema(record: LoggedTestModel) -> LoggedTest:
    return LoggedTest(
        id=record.id,
        assessment_id=record.assessment_id,
        type=record.type,
        name=record.name,
        result=record.result,
    )


def list_tests(db: Session, assessment_id: str) -> list[LoggedTest]:
    records = db.scalars(
        select(LoggedTestModel).where(LoggedTestModel.assessment_id == assessment_id)
    ).all()
    return [_to_schema(t) for t in records]


def create_test(db: Session, assessment_id: str, data: LoggedTestCreate) -> LoggedTest | None:
    assessment = db.get(AssessmentSession, assessment_id)
    if assessment is None:
        return None
    test_id = f"test-{uuid.uuid4().hex[:8]}"
    record = LoggedTestModel(
        id=test_id,
        assessment_id=assessment_id,
        type=data.type,
        name=data.name,
        result=data.result,
    )
    db.add(record)
    assessment.version += 1
    db.commit()
    db.refresh(record)
    return _to_schema(record)


def update_test(db: Session, test_id: str, data: LoggedTestUpdate) -> LoggedTest | None:
    record = db.get(LoggedTestModel, test_id)
    if not record:
        return None
    record.result = data.result
    assessment = db.get(AssessmentSession, record.assessment_id)
    if assessment:
        assessment.version += 1
    db.commit()
    db.refresh(record)
    return _to_schema(record)
