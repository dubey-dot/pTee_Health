import uuid

from app.schemas.finding import Finding, FindingCreate, FindingDetail, FindingUpdate
from app.services.store import ASSESSMENTS, FINDINGS, FindingRecord, bump_assessment_version


def _to_schema(record: FindingRecord) -> Finding:
    detail = FindingDetail(**record.detail) if record.detail else None
    return Finding(
        id=record.id,
        assessment_id=record.assessment_id,
        tag=record.tag,
        label=record.label,
        selected=record.selected,
        detail=detail,
    )


def list_findings(assessment_id: str) -> list[Finding]:
    records = [f for f in FINDINGS.values() if f.assessment_id == assessment_id]
    records.sort(key=lambda f: f.order)
    return [_to_schema(f) for f in records]


def create_finding(assessment_id: str, data: FindingCreate) -> Finding | None:
    if assessment_id not in ASSESSMENTS:
        return None
    finding_id = f"finding-{uuid.uuid4().hex[:8]}"
    order = sum(1 for f in FINDINGS.values() if f.assessment_id == assessment_id)
    record = FindingRecord(
        id=finding_id,
        assessment_id=assessment_id,
        tag=data.tag,
        label=data.label,
        selected=data.selected,
        detail=data.detail.model_dump() if data.detail else None,
        order=order,
    )
    FINDINGS[finding_id] = record
    bump_assessment_version(assessment_id)
    return _to_schema(record)


def update_finding(finding_id: str, data: FindingUpdate) -> Finding | None:
    record = FINDINGS.get(finding_id)
    if not record:
        return None
    record.label = data.label
    bump_assessment_version(record.assessment_id)
    return _to_schema(record)


def delete_finding(finding_id: str) -> bool:
    record = FINDINGS.pop(finding_id, None)
    if record:
        bump_assessment_version(record.assessment_id)
    return record is not None
