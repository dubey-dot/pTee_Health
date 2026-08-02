from app.schemas.base import CamelModel


class FindingDetail(CamelModel):
    question: str
    bullets: list[str]


class Finding(CamelModel):
    id: str
    assessment_id: str
    tag: str
    label: str
    selected: bool = False
    detail: FindingDetail | None = None


class FindingCreate(CamelModel):
    tag: str
    label: str
    selected: bool = False
    detail: FindingDetail | None = None


class FindingUpdate(CamelModel):
    label: str
