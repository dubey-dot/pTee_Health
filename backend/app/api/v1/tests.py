from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.test import LoggedTest, LoggedTestCreate, LoggedTestUpdate
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


@router.patch("/tests/{test_id}", response_model=LoggedTest)
def update_test(test_id: str, data: LoggedTestUpdate, db: Session = Depends(get_db)) -> LoggedTest:
    test = tests_service.update_test(db, test_id, data)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test
