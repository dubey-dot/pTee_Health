from app.schemas.base import CamelModel
from app.schemas.test import TestType


class RecommendedTest(CamelModel):
    test_name: str
    test_type: TestType
    summary: str
    why_recommended: str


class TestRecommendationBatch(CamelModel):
    tests: list[RecommendedTest] = []
    no_recommendation_reason: str | None = None
