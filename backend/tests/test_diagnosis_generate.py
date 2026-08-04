"""Tests for POST /assessments/{id}/diagnosis/generate.

Mocks at the service boundary (services.assessments.generate_diagnosis's
`engine` parameter) rather than hitting the real Anthropic API — same
approach the module docstring on ClaudeWorkingDiagnosisEngine assumes tests
would take, and consistent with no other test in this suite making network
calls.
"""

import anthropic
import httpx

from app.services import assessments as assessments_service
from app.services.engines.base import GeneratedAssessment, GeneratedInsightTag


class _FakeEngine:
    def __init__(self, result: GeneratedAssessment | None = None, error: Exception | None = None):
        self._result = result
        self._error = error
        self.calls: list[dict] = []

    def generate(self, *, patient_summary, clinical_summary, findings):
        self.calls.append(
            {
                "patient_summary": patient_summary,
                "clinical_summary": clinical_summary,
                "findings": findings,
            }
        )
        if self._error:
            raise self._error
        return self._result


def _fake_result(**overrides) -> GeneratedAssessment:
    defaults = dict(
        diagnosis="Load-related right anterior knee pain",
        confidence=72,
        reasoning="Findings consistently point to a lateral pelvic shift.",
        insight_summary="Pelvis Shift Right/Left is the most significant finding so far.",
        insight_tags=[GeneratedInsightTag(label="Pelvis Shift Right/Left", meta="1 recorded")],
    )
    defaults.update(overrides)
    return GeneratedAssessment(**defaults)


def test_generate_diagnosis_service_persists_result(db_session):
    engine = _FakeEngine(result=_fake_result())
    updated = assessments_service.generate_diagnosis(db_session, "assessment-1", engine=engine)

    assert updated is not None
    assert updated.diagnosis == "Load-related right anterior knee pain"
    assert updated.confidence == 72
    assert updated.version == 2  # bumped from the seeded version=1

    # The engine was actually called with the seeded patient + finding data.
    assert len(engine.calls) == 1
    assert engine.calls[0]["patient_summary"] == "Right anterior knee pain"
    assert {"tag": "GAIT", "label": "Pelvis Shift Right/Left"} in engine.calls[0]["findings"]


def test_generate_diagnosis_persists_insights_for_later_get(db_session):
    engine = _FakeEngine(result=_fake_result())
    assessments_service.generate_diagnosis(db_session, "assessment-1", engine=engine)

    from app.services import insights as insights_service

    insights = insights_service.get_insights(db_session, "assessment-1")
    assert insights is not None
    assert insights.summary == "Pelvis Shift Right/Left is the most significant finding so far."
    assert insights.tags[0].label == "Pelvis Shift Right/Left"


def test_generate_diagnosis_not_found(db_session):
    engine = _FakeEngine(result=_fake_result())
    result = assessments_service.generate_diagnosis(db_session, "does-not-exist", engine=engine)
    assert result is None
    assert engine.calls == []  # never called the engine for a nonexistent assessment


def test_generate_diagnosis_endpoint_404(client):
    res = client.post("/api/v1/assessments/does-not-exist/diagnosis/generate")
    assert res.status_code == 404


def test_generate_diagnosis_endpoint_502_when_api_key_missing(client, monkeypatch):
    # No mocking of the engine itself — exercises the real
    # ClaudeWorkingDiagnosisEngine's missing-key guard, since this is the
    # actual first-run experience for anyone who hasn't set
    # ANTHROPIC_API_KEY yet (found via manual testing: without this guard,
    # the SDK raises a bare TypeError that becomes an unhandled 500).
    from app.services.engines import anthropic_client as anthropic_client_module

    class _EmptyKeySettings:
        anthropic_api_key = ""

    anthropic_client_module.get_anthropic_client.cache_clear()
    monkeypatch.setattr(anthropic_client_module, "get_settings", lambda: _EmptyKeySettings())

    res = client.post("/api/v1/assessments/assessment-1/diagnosis/generate")
    assert res.status_code == 502
    assert "ANTHROPIC_API_KEY" in res.json()["detail"]

    anthropic_client_module.get_anthropic_client.cache_clear()


def test_generate_diagnosis_endpoint_502_on_anthropic_failure(client, db_session, monkeypatch):
    def _raise(self, **kwargs):
        raise anthropic.APIConnectionError(
            request=httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        )

    monkeypatch.setattr(
        "app.services.engines.working_diagnosis_engine.ClaudeWorkingDiagnosisEngine.generate",
        _raise,
    )
    res = client.post("/api/v1/assessments/assessment-1/diagnosis/generate")
    assert res.status_code == 502

    # Existing diagnosis must survive a failed generation attempt untouched.
    still_there = client.get("/api/v1/assessments/assessment-1").json()
    assert still_there["diagnosis"] == "Load-related right anterior knee pain"
