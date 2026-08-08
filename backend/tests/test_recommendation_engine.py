"""Tests for ClaudeRecommendationEngine's prompt construction — proves both
rules files (assessment + recommendation) are threaded into the Claude
call. Mocks the Anthropic client itself, same pattern as
test_working_diagnosis_engine.py.
"""

from app.services.engines import recommendation_engine as engine_module
from app.services.engines.base import RecommendedTest, TestRecommendationBatch


class _FakeMessages:
    def __init__(self, result: TestRecommendationBatch):
        self._result = result
        self.calls: list[dict] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)

        class _Response:
            parsed_output = self._result

        return _Response()


class _FakeClient:
    def __init__(self, result: TestRecommendationBatch):
        self.messages = _FakeMessages(result)


def test_recommend_includes_both_rules_files_in_system_prompt(monkeypatch):
    fake_result = TestRecommendationBatch(
        tests=[
            RecommendedTest(
                test_name="Hip Internal Rotation",
                summary="Anterior pelvic tilt with suspected hip restriction",
                why_recommended="Checks whether hip restriction contributes to the anterior knee pain pattern.",
                confidence=82,
            )
        ],
    )
    fake_client = _FakeClient(fake_result)
    monkeypatch.setattr(engine_module, "get_anthropic_client", lambda: fake_client)

    engine = engine_module.ClaudeRecommendationEngine()
    result = engine.recommend(
        patient_summary="p",
        clinical_summary="c",
        doctor_notes=["note one"],
        findings=[{"tag": "GAIT", "label": "Pelvis Shift Right/Left", "selected": True}],
        logged_tests=[{"type": "joint", "name": "Single leg bridge", "result": "Weak on right"}],
    )

    assert result is fake_result
    assert len(fake_client.messages.calls) == 1
    call = fake_client.messages.calls[0]
    system_blocks = call["system"]
    assert len(system_blocks) == 3

    assessment_block, recommendation_block, task_block = system_blocks
    assert "Assessment Rules" in assessment_block["text"]
    assert engine_module.ASSESSMENT_RULES_PREAMBLE in assessment_block["text"]
    assert assessment_block["cache_control"] == {"type": "ephemeral"}

    assert "Assessment Recommendation Rules" in recommendation_block["text"]
    assert engine_module.RECOMMENDATION_RULES_PREAMBLE in recommendation_block["text"]
    assert recommendation_block["cache_control"] == {"type": "ephemeral"}

    assert task_block["text"] == engine_module.SYSTEM_PROMPT
    assert task_block["cache_control"] == {"type": "ephemeral"}

    user_content = call["messages"][0]["content"]
    assert "note one" in user_content
    assert "Pelvis Shift Right/Left" in user_content
    assert "confirmed finding" in user_content
    assert "Single leg bridge" in user_content
