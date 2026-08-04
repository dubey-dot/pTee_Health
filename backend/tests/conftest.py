"""Shared pytest fixtures.

Runs against a real Postgres database (a dedicated `..._test` database on
the same server docker-compose.yml brings up for local dev) — not SQLite,
not mocks — per the plan's "database tests against a real instance" policy.
Each test runs inside its own transaction that's rolled back afterward, so
tests are isolated from each other without needing to recreate the schema
per test.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_db
from app.db.base import Base
from app.main import app

_TEST_DB_NAME = "ptee_health_test"


def _test_database_url() -> str:
    base_url = get_settings().database_url.rsplit("/", 1)[0]
    return f"{base_url}/{_TEST_DB_NAME}"


def _ensure_test_database_exists() -> None:
    base_url = get_settings().database_url.rsplit("/", 1)[0]
    admin_engine = create_engine(f"{base_url}/postgres", isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": _TEST_DB_NAME}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{_TEST_DB_NAME}"'))
    admin_engine.dispose()


@pytest.fixture(scope="session")
def engine():
    _ensure_test_database_exists()
    eng = create_engine(_test_database_url())
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


def _seed(session: Session) -> None:
    session.execute(
        text(
            """
            INSERT INTO patients (
                id, name, age, gender, occupation_sport, chief_complaint, duration,
                pain_score, aggravating, relieving, previous_injuries, clinical_summary,
                doctors_notes_count
            ) VALUES (
                'patient-1', 'Ankita Sharma', 32, 'Female',
                'a software engineer and i · runner', 'Right anterior knee pain',
                '3 months', '', 'stairs, squatting, better with rest, ice', 'rest, ice',
                '', 'Presenting with right anterior knee pain for 3 months.', 0
            )
            """
        )
    )
    session.execute(
        text(
            """
            INSERT INTO assessment_sessions (
                id, patient_id, status, diagnosis, confidence, diagnosis_action, version
            ) VALUES (
                'assessment-1', 'patient-1', 'completed',
                'Load-related right anterior knee pain', 64, 'agree', 1
            )
            """
        )
    )
    session.execute(
        text(
            """
            INSERT INTO findings (id, assessment_id, tag, label, selected, detail, "order")
            VALUES ('pelvis-shift', 'assessment-1', 'GAIT', 'Pelvis Shift Right/Left', true, NULL, 0)
            """
        )
    )
    session.commit()


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    # `create_savepoint` mode: the session's own commits (which the service
    # layer calls freely, e.g. `db.commit()` after each write) end/restart a
    # SAVEPOINT rather than the outer transaction, so `transaction.rollback()`
    # below always undoes everything a test did, including the seed data.
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    _seed(session)
    session.commit()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
