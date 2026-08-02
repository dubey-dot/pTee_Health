from fastapi import Header


def get_current_user(authorization: str | None = Header(default=None)) -> None:
    """No-op until Phase 5 auth lands.

    Wired into every /api/v1 route now (see api/v1/router.py) so enforcing
    auth later only means changing this function's body, not every route
    signature.
    """
    return None
