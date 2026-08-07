"""Tests for ClaudeWorkingDiagnosisEngine's prompt construction — proves the
assessment rules file is actually threaded into the Claude call, not just
that rules.py can load it in isolation. Mocks the Anthropic client itself
(no real network call), since nothing else in this suite calls the real API.
"""

from app.services.engines import working_diagnosis_engine as engine_module
from app.services.engines.base import GeneratedAssessment, GeneratedInsightTag


class _FakeMessages:
    def __init__(self, result: GeneratedAssessment):
        self._result = result
        self.calls: list[dict] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)

        class _Response:
            parsed_output = self._result

        return _Response()


class _FakeClient:
    def __init__(self, result: GeneratedAssessment):
        self.messages = _FakeMessages(result)


def test_generate_includes_assessment_rules_in_system_prompt(monkeypatch):
    fake_result = GeneratedAssessment(
        diagnosis="x",
        confidence=10,
        reasoning="y",
        insight_summary="z",
        insight_tags=[GeneratedInsightTag(label="a", meta="b")],
    )
    fake_client = _FakeClient(fake_result)
    monkeypatch.setattr(engine_module, "get_anthropic_client", lambda: fake_client)

    engine = engine_module.ClaudeWorkingDiagnosisEngine()
    result = engine.generate(patient_summary="p", clinical_summary="c", findings=[])

    assert result is fake_result
    assert len(fake_client.messages.calls) == 1
    system_blocks = fake_client.messages.calls[0]["system"]
    assert len(system_blocks) == 2

    rules_block, task_block = system_blocks
    assert "Assessment Rules" in rules_block["text"]
    assert engine_module.RULES_PREAMBLE in rules_block["text"]
    assert rules_block["cache_control"] == {"type": "ephemeral"}
    assert task_block["text"] == engine_module.SYSTEM_PROMPT
    assert task_block["cache_control"] == {"type": "ephemeral"}
