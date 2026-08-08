from app.schemas.base import CamelModel


class RecommendedTest(CamelModel):
    test_name: str
    summary: str
    why_recommended: str
    confidence: int


class TestRecommendationBatch(CamelModel):
    tests: list[RecommendedTest] = []
    no_recommendation_reason: str | None = None
