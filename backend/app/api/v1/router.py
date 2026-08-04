from fastapi import APIRouter, Depends

from app.api.v1 import assessments, diagnosis, findings, insights, notes, patients, tests
from app.core.deps import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])

router.include_router(patients.router, tags=["patients"])
router.include_router(assessments.router, tags=["assessments"])
router.include_router(findings.router, tags=["findings"])
router.include_router(diagnosis.router, tags=["diagnosis"])
router.include_router(tests.router, tags=["tests"])
router.include_router(insights.router, tags=["insights"])
router.include_router(notes.router, tags=["notes"])
