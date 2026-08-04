import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.assessment_session import AssessmentSession
from app.models.legacy_finding import Finding as FindingModel
from app.schemas.finding import Finding, FindingCreate, FindingDetail, FindingUpdate


def _to_schema(record: FindingModel) -> Finding:
    detail = FindingDetail(**record.detail) if record.detail else None
    return Finding(
        id=record.id,
        assessment_id=record.assessment_id,
        tag=record.tag,
        label=record.label,
        selected=record.selected,
        detail=detail,
    )


def list_findings(db: Session, assessment_id: str) -> list[Finding]:
    records = db.scalars(
        select(FindingModel)
        .where(FindingModel.assessment_id == assessment_id)
        .order_by(FindingModel.order)
    ).all()
    return [_to_schema(f) for f in records]


def create_finding(db: Session, assessment_id: str, data: FindingCreate) -> Finding | None:
    if db.get(AssessmentSession, assessment_id) is None:
        return None
    finding_id = f"finding-{uuid.uuid4().hex[:8]}"
    order = db.scalar(
        select(func.count())
        .select_from(FindingModel)
        .where(FindingModel.assessment_id == assessment_id)
    )
    record = FindingModel(
        id=finding_id,
        assessment_id=assessment_id,
        tag=data.tag,
        label=data.label,
        selected=data.selected,
        detail=data.detail.model_dump() if data.detail else None,
        order=order,
    )
    db.add(record)
    _bump_assessment_version(db, assessment_id)
    db.commit()
    db.refresh(record)
    return _to_schema(record)


def update_finding(db: Session, finding_id: str, data: FindingUpdate) -> Finding | None:
    record = db.get(FindingModel, finding_id)
    if not record:
        return None
    record.label = data.label
    _bump_assessment_version(db, record.assessment_id)
    db.commit()
    db.refresh(record)
    return _to_schema(record)


def delete_finding(db: Session, finding_id: str) -> bool:
    record = db.get(FindingModel, finding_id)
    if not record:
        return False
    assessment_id = record.assessment_id
    db.delete(record)
    _bump_assessment_version(db, assessment_id)
    db.commit()
    return True


def _bump_assessment_version(db: Session, assessment_id: str) -> None:
    assessment = db.get(AssessmentSession, assessment_id)
    if assessment:
        assessment.version += 1
