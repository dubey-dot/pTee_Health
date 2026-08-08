"""Tests for POST /assessments/{id}/recommendations.

Mocks at the service boundary (services.recommendations.get_recommendations's
`engine` parameter) rather than hitting the real Anthropic API — same
approach as test_diagnosis_generate.py.
"""

import anthropic
import httpx

from app.services import recommendations as recommendations_service
from app.services.engines.base import RecommendedTest, TestRecommendationBatch


class _FakeEngine:
    def __init__(self, result: TestRecommendationBatch | None = None, error: Exception | None = None):
        self._result = result
        self._error = error
        self.calls: list[dict] = []

    def recommend(self, *, patient_summary, clinical_summary, doctor_notes, findings, logged_tests):
        self.calls.append(
            {
                "patient_summary": patient_summary,
                "clinical_summary": clinical_summary,
                "doctor_notes": doctor_notes,
                "findings": findings,
                "logged_tests": logged_tests,
            }
        )
        if self._error:
            raise self._error
        return self._result


def _fake_result(**overrides) -> TestRecommendationBatch:
    defaults = dict(
        tests=[
            RecommendedTest(
                test_name="Hip Internal Rotation",
                test_type="joint",
                summary="Anterior pelvic tilt with suspected hip restriction",
                why_recommended="Checks whether hip restriction is contributing.",
            )
        ],
        no_recommendation_reason=None,
    )
    defaults.update(overrides)
    return TestRecommendationBatch(**defaults)


def test_get_recommendations_service(db_session):
    engine = _FakeEngine(result=_fake_result())
    result = recommendations_service.get_recommendations(db_session, "assessment-1", engine=engine)

    assert result is not None
    assert len(result.tests) == 1
    assert result.tests[0].test_name == "Hip Internal Rotation"
    assert result.tests[0].test_type == "joint"

    assert len(engine.calls) == 1
    assert engine.calls[0]["patient_summary"] == "Right anterior knee pain"
    assert {"tag": "GAIT", "label": "Pelvis Shift Right/Left", "selected": True} in engine.calls[0]["findings"]


def test_get_recommendations_empty_batch(db_session):
    engine = _FakeEngine(
        result=_fake_result(tests=[], no_recommendation_reason="Confidence already sufficient.")
    )
    result = recommendations_service.get_recommendations(db_session, "assessment-1", engine=engine)

    assert result.tests == []
    assert result.no_recommendation_reason == "Confidence already sufficient."


def test_get_recommendations_not_found(db_session):
    engine = _FakeEngine(result=_fake_result())
    result = recommendations_service.get_recommendations(db_session, "does-not-exist", engine=engine)
    assert result is None
    assert engine.calls == []


def test_get_recommendations_does_not_bump_version(db_session, client):
    before = client.get("/api/v1/assessments/assessment-1").json()["version"]
    engine = _FakeEngine(result=_fake_result())
    recommendations_service.get_recommendations(db_session, "assessment-1", engine=engine)
    after = client.get("/api/v1/assessments/assessment-1").json()["version"]
    assert after == before  # advisory only, never mutates the assessment


def test_recommendations_endpoint_404(client):
    res = client.post("/api/v1/assessments/does-not-exist/recommendations")
    assert res.status_code == 404


def test_recommendations_endpoint_502_when_api_key_missing(client, monkeypatch):
    from app.services.engines import anthropic_client as anthropic_client_module

    class _EmptyKeySettings:
        anthropic_api_key = ""

    anthropic_client_module.get_anthropic_client.cache_clear()
    monkeypatch.setattr(anthropic_client_module, "get_settings", lambda: _EmptyKeySettings())

    res = client.post("/api/v1/assessments/assessment-1/recommendations")
    assert res.status_code == 502
    assert "ANTHROPIC_API_KEY" in res.json()["detail"]

    anthropic_client_module.get_anthropic_client.cache_clear()


def test_recommendations_endpoint_502_on_anthropic_failure(client, monkeypatch):
    def _raise(self, **kwargs):
        raise anthropic.APIConnectionError(
            request=httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        )

    monkeypatch.setattr(
        "app.services.engines.recommendation_engine.ClaudeRecommendationEngine.recommend",
        _raise,
    )
    res = client.post("/api/v1/assessments/assessment-1/recommendations")
    assert res.status_code == 502
