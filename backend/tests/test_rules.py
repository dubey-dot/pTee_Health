import pytest

from app.services.engines import rules as rules_module


def test_load_assessment_rules_returns_file_contents():
    text = rules_module.load_assessment_rules()
    assert "Assessment Rules" in text
    assert text == text.strip()  # no leading/trailing whitespace


def test_load_assessment_rules_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(rules_module, "RULES_PATH", tmp_path / "does-not-exist.md")

    with pytest.raises(RuntimeError, match="Assessment rules file not found"):
        rules_module.load_assessment_rules()


def test_load_recommendation_rules_returns_file_contents():
    text = rules_module.load_recommendation_rules()
    assert "Assessment Recommendation Rules" in text
    assert text == text.strip()


def test_load_recommendation_rules_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(rules_module, "RECOMMENDATION_RULES_PATH", tmp_path / "does-not-exist.md")

    with pytest.raises(RuntimeError, match="Recommendation rules file not found"):
        rules_module.load_recommendation_rules()
