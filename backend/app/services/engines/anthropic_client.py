from functools import lru_cache

import anthropic

from app.core.config import get_settings


@lru_cache
def get_anthropic_client() -> anthropic.Anthropic:
    """Shared client, constructed once. Reads ANTHROPIC_API_KEY from Settings
    (backend/.env or the real environment) — never hardcode a key here.

    Checked explicitly rather than left to the SDK: with no key at all, the
    SDK raises a bare TypeError at request-build time (not an
    anthropic.APIStatusError/APIConnectionError), which would otherwise slip
    past the API layer's error handling as an unhandled 500 instead of a
    clear 502.
    """
    api_key = get_settings().anthropic_api_key
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not configured — set it in backend/.env "
            "(see backend/.env.example) to enable AI-generated diagnosis/insights."
        )
    return anthropic.Anthropic(api_key=api_key)
