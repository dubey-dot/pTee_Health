from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.test import LoggedTest, LoggedTestCreate
from app.services import tests as tests_service

router = APIRouter()


@router.get("/assessments/{assessment_id}/tests", response_model=list[LoggedTest])
def list_tests(assessment_id: str, db: Session = Depends(get_db)) -> list[LoggedTest]:
    return tests_service.list_tests(db, assessment_id)


@router.post("/assessments/{assessment_id}/tests", response_model=LoggedTest, status_code=201)
def create_test(
    assessment_id: str, data: LoggedTestCreate, db: Session = Depends(get_db)
) -> LoggedTest:
    test = tests_service.create_test(db, assessment_id, data)
    if not test:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return test
