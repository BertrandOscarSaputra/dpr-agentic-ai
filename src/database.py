"""PostgreSQL connection & SQLAlchemy ORM setup.

Engine and session are created lazily to avoid import-time failures
when the database is not available (e.g., during testing without a live DB).
"""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create the SQLAlchemy engine (cached singleton)."""
    return create_engine(
        settings.database_url_resolved,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DEBUG,
    )


def get_session_factory() -> sessionmaker[Session]:
    """Create a session factory bound to the engine."""
    return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
