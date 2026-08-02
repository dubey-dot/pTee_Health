from app.schemas.base import CamelModel


class InsightTag(CamelModel):
    label: str
    meta: str


class Insights(CamelModel):
    assessment_id: str
    summary: str
    tags: list[InsightTag]
