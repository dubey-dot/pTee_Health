from pathlib import Path

RULES_PATH = Path(__file__).parent / "assessment_rules.md"


def load_assessment_rules() -> str:
    """Reads the standing assessment rules Claude must follow before
    generating a working diagnosis, kept in a separate Markdown file so
    they can be edited without touching any engine/Python code.

    Read fresh on every call (deliberately not cached) so an edit to
    assessment_rules.md takes effect on the very next "Generate with AI"
    call — no backend restart required, unlike ANTHROPIC_API_KEY which is
    cached via Settings.
    """
    if not RULES_PATH.exists():
        raise RuntimeError(
            f"Assessment rules file not found at {RULES_PATH} — restore "
            "assessment_rules.md (see services/engines/rules.py)."
        )
    return RULES_PATH.read_text(encoding="utf-8").strip()
