"""Pytest fixtures shared across all test modules."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture()
def client() -> TestClient:
    """Create a FastAPI test client."""
    return TestClient(app)
