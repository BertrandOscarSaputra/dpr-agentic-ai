"""Pytest fixtures shared across all test modules."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.database import get_db
from src.main import app


@pytest.fixture()
def mock_db() -> MagicMock:
    """Create a mock SQLAlchemy session."""
    session = MagicMock()
    return session


@pytest.fixture()
def client(mock_db: MagicMock) -> TestClient:
    """Create a FastAPI test client with mocked DB session."""
    app.dependency_overrides[get_db] = lambda: mock_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()
