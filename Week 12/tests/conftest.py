
import pytest

from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

from app.database.connection import Base, SessionLocal
from app.database import models
from app.core.limiter import limiter

from scripts.seed_data import seed_database


@pytest.fixture(scope="session", autouse=True)
def isolated_test_database():
    """
    Give the entire test session its own in-memory SQLite database.
    """

    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=test_engine)
    SessionLocal.configure(bind=test_engine)

    seed_database()

    yield

    SessionLocal.configure(bind=None)
    test_engine.dispose()


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Prevent rate-limit counters from leaking between tests."""
    limiter.reset()
    yield
    limiter.reset()
