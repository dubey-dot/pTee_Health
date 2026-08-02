from fastapi import APIRouter, HTTPException

from app.schemas.test import LoggedTest, LoggedTestCreate
from app.services import tests as tests_service

router = APIRouter()


@router.get("/assessments/{assessment_id}/tests", response_model=list[LoggedTest])
def list_tests(assessment_id: str) -> list[LoggedTest]:
    return tests_service.list_tests(assessment_id)


@router.post("/assessments/{assessment_id}/tests", response_model=LoggedTest, status_code=201)
def create_test(assessment_id: str, data: LoggedTestCreate) -> LoggedTest:
    test = tests_service.create_test(assessment_id, data)
    if not test:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return test
