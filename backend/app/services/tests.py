import uuid

from app.schemas.test import LoggedTest, LoggedTestCreate
from app.services.store import ASSESSMENTS, TESTS, TestRecord, bump_assessment_version


def _to_schema(record: TestRecord) -> LoggedTest:
    return LoggedTest(
        id=record.id,
        assessment_id=record.assessment_id,
        type=record.type,
        name=record.name,
        result=record.result,
    )


def list_tests(assessment_id: str) -> list[LoggedTest]:
    return [_to_schema(t) for t in TESTS.values() if t.assessment_id == assessment_id]


def create_test(assessment_id: str, data: LoggedTestCreate) -> LoggedTest | None:
    if assessment_id not in ASSESSMENTS:
        return None
    test_id = f"test-{uuid.uuid4().hex[:8]}"
    record = TestRecord(
        id=test_id,
        assessment_id=assessment_id,
        type=data.type,
        name=data.name,
        result=data.result,
    )
    TESTS[test_id] = record
    bump_assessment_version(assessment_id)
    return _to_schema(record)
