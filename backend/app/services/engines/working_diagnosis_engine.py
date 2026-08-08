from app.services.engines.anthropic_client import get_anthropic_client
from app.services.engines.base import GeneratedAssessment
from app.services.engines.rules import ASSESSMENT_RULES_PREAMBLE, load_assessment_rules

SYSTEM_PROMPT = (
    "In addition to the assessment rules above, you are a clinical reasoning "
    "assistant supporting physiotherapists during a patient assessment. Given "
    "the patient's intake summary and the findings recorded so far, produce: "
    "a single working diagnosis, a confidence percentage (0-100) reflecting "
    "how well the current findings support it, a short clinical reasoning "
    "summary explaining that confidence, and 1-3 short insight tags "
    "highlighting the most clinically significant finding(s) recorded so "
    "far. Be conservative — confidence should rise only as corroborating "
    "findings accumulate, and should stay low (well under 50) when few "
    "findings are recorded yet."
)


class ClaudeWorkingDiagnosisEngine:
    """Real implementation of the WorkingDiagnosisEngine seam, backed by
    Claude Opus 5 with structured outputs (the response IS the validated
    schema — no free-text parsing). Requires ANTHROPIC_API_KEY; raises
    anthropic.APIError subclasses on failure, which the calling service
    (`services/assessments.py::generate_diagnosis`) turns into a 502.
    """

    def generate(
        self, *, patient_summary: str, clinical_summary: str, findings: list[dict]
    ) -> GeneratedAssessment:
        client = get_anthropic_client()
        findings_text = (
            "\n".join(f"- [{f['tag']}] {f['label']}" for f in findings)
            or "(no findings recorded yet)"
        )

        rules_text = load_assessment_rules()

        response = client.messages.parse(
            model="claude-opus-5",
            max_tokens=4096,
            output_config={"effort": "high"},
            system=[
                {
                    "type": "text",
                    "text": f"{ASSESSMENT_RULES_PREAMBLE}\n\n{rules_text}",
                    # Changes only when assessment_rules.md is edited —
                    # cached separately from SYSTEM_PROMPT below so either
                    # can change without invalidating the other's cache.
                    "cache_control": {"type": "ephemeral"},
                },
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    # Identical on every call — cheap prompt-caching win.
                    "cache_control": {"type": "ephemeral"},
                },
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Patient summary: {patient_summary or '(none provided)'}\n\n"
                        f"Clinical summary: {clinical_summary or '(none provided)'}\n\n"
                        f"Findings recorded so far:\n{findings_text}"
                    ),
                }
            ],
            output_format=GeneratedAssessment,
        )
        if response.parsed_output is None:
            raise ValueError("Claude response did not match the expected schema")
        return response.parsed_output
