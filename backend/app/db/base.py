from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import every model module here so Alembic's autogenerate (and
# Base.metadata.create_all in tests) sees the full schema from this single
# import. Models themselves must not import this module back except for
# `Base` itself, to avoid circular imports.
from app.models import assessment_session, legacy_finding, legacy_test, patient  # noqa: E402,F401
