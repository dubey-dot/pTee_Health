from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.finding import Finding, FindingCreate, FindingUpdate
from app.services import findings as findings_service

router = APIRouter()


@router.get("/assessments/{assessment_id}/findings", response_model=list[Finding])
def list_findings(assessment_id: str, db: Session = Depends(get_db)) -> list[Finding]:
    return findings_service.list_findings(db, assessment_id)


@router.post("/assessments/{assessment_id}/findings", response_model=Finding, status_code=201)
def create_finding(
    assessment_id: str, data: FindingCreate, db: Session = Depends(get_db)
) -> Finding:
    finding = findings_service.create_finding(db, assessment_id, data)
    if not finding:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return finding


@router.patch("/findings/{finding_id}", response_model=Finding)
def update_finding(
    finding_id: str, data: FindingUpdate, db: Session = Depends(get_db)
) -> Finding:
    finding = findings_service.update_finding(db, finding_id, data)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.delete("/findings/{finding_id}", status_code=204)
def delete_finding(finding_id: str, db: Session = Depends(get_db)) -> Response:
    deleted = findings_service.delete_finding(db, finding_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Finding not found")
    return Response(status_code=204)
