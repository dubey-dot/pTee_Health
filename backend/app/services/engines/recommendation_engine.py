from app.services.engines.anthropic_client import get_anthropic_client
from app.services.engines.base import TestRecommendationBatch
from app.services.engines.rules import (
    ASSESSMENT_RULES_PREAMBLE,
    RECOMMENDATION_RULES_PREAMBLE,
    load_assessment_rules,
    load_recommendation_rules,
)

SYSTEM_PROMPT = (
    "In addition to the assessment rules and recommendation rules above, "
    "you are a clinical reasoning assistant recommending a ranked batch of "
    "up to 4 assessments for a physiotherapist to consider next during a "
    "patient assessment. Given the patient's intake summary, doctor's "
    "notes, findings recorded so far, and tests already logged, decide "
    "which further tests would meaningfully increase confidence in a "
    "working diagnosis. Never recommend a test that has already been "
    "logged. Rank tests highest-value first. Classify each recommended "
    "test's test_type as exactly one of \"joint\", \"muscle\", or \"gait\" "
    "— the same categories used for manually-logged tests elsewhere in "
    "this app, since accepting a recommendation creates a real logged "
    "test of that type. Do not invent a confidence score for individual "
    "tests — only the overall working-diagnosis confidence matters here, "
    "and it is not part of this call's output. If no further tests would "
    "meaningfully help — either because the working-diagnosis confidence "
    "is already sufficient or because the remaining gap can't be closed "
    "by more testing — return an empty tests list and explain why in "
    "no_recommendation_reason."
)


class ClaudeRecommendationEngine:
    """Real implementation of the RecommendationEngine seam, backed by
    Claude Opus 5 with structured outputs. Requires ANTHROPIC_API_KEY;
    raises anthropic.APIError subclasses on failure, which the calling
    service (`services/recommendations.py`) lets propagate into a 502.
    """

    def recommend(
        self,
        *,
        patient_summary: str,
        clinical_summary: str,
        doctor_notes: list[str],
        findings: list[dict],
        logged_tests: list[dict],
    ) -> TestRecommendationBatch:
        client = get_anthropic_client()

        findings_text = (
            "\n".join(
                f"- [{f['tag']}] {f['label']}"
                + (" (confirmed finding)" if f.get("selected") else " (not yet confirmed)")
                for f in findings
            )
            or "(no findings recorded yet)"
        )
        tests_text = (
            "\n".join(f"- {t['type']}: {t['name']} — result: {t['result'] or '(no result recorded)'}" for t in logged_tests)
            or "(no tests logged yet)"
        )
        notes_text = "\n".join(f"- {n}" for n in doctor_notes) or "(no doctor's notes recorded yet)"

        response = client.messages.parse(
            model="claude-opus-5",
            max_tokens=4096,
            output_config={"effort": "high"},
            system=[
                {
                    "type": "text",
                    "text": f"{ASSESSMENT_RULES_PREAMBLE}\n\n{load_assessment_rules()}",
                    "cache_control": {"type": "ephemeral"},
                },
                {
                    "type": "text",
                    "text": f"{RECOMMENDATION_RULES_PREAMBLE}\n\n{load_recommendation_rules()}",
                    "cache_control": {"type": "ephemeral"},
                },
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                },
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Patient summary: {patient_summary or '(none provided)'}\n\n"
                        f"Clinical summary: {clinical_summary or '(none provided)'}\n\n"
                        f"Doctor's notes:\n{notes_text}\n\n"
                        f"Findings recorded so far:\n{findings_text}\n\n"
                        f"Tests already logged:\n{tests_text}"
                    ),
                }
            ],
            output_format=TestRecommendationBatch,
        )
        if response.parsed_output is None:
            raise ValueError("Claude response did not match the expected schema")
        return response.parsed_output
