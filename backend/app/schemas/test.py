from typing import Literal

from app.schemas.base import CamelModel

TestType = Literal["joint", "muscle", "gait"]


class LoggedTest(CamelModel):
    id: str
    assessment_id: str
    type: TestType
    name: str
    result: str = ""


class LoggedTestCreate(CamelModel):
    type: TestType
    name: str
    result: str = ""
