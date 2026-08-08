from pathlib import Path

RULES_PATH = Path(__file__).parent / "assessment_rules.md"
RECOMMENDATION_RULES_PATH = Path(__file__).parent / "recommendation_rules.md"

ASSESSMENT_RULES_PREAMBLE = (
    "The following ASSESSMENT RULES are standing instructions for this "
    "practice. Read and follow them before doing anything else in this "
    "conversation — they take precedence over the task instructions below."
)

RECOMMENDATION_RULES_PREAMBLE = (
    "The following ASSESSMENT RECOMMENDATION RULES govern how you must "
    "select and format the next recommended test. Follow them exactly, in "
    "addition to (not instead of) the assessment rules above."
)


def _read(path: Path, label: str) -> str:
    if not path.exists():
        raise RuntimeError(
            f"{label} file not found at {path} — restore it (see services/engines/rules.py)."
        )
    return path.read_text(encoding="utf-8").strip()


def load_assessment_rules() -> str:
    """Reads the standing assessment rules Claude must follow before
    generating a working diagnosis, kept in a separate Markdown file so
    they can be edited without touching any engine/Python code.

    Read fresh on every call (deliberately not cached) so an edit to
    assessment_rules.md takes effect on the very next "Generate with AI"
    call — no backend restart required, unlike ANTHROPIC_API_KEY which is
    cached via Settings.
    """
    return _read(RULES_PATH, "Assessment rules")


def load_recommendation_rules() -> str:
    """Same contract as load_assessment_rules(), for the rules governing
    the "what test should the clinician perform next" recommendation
    engine (services/engines/recommendation_engine.py).
    """
    return _read(RECOMMENDATION_RULES_PATH, "Recommendation rules")
