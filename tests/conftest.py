"""Shared pytest fixtures for API tests"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient instance for testing the FastAPI app"""
    return TestClient(app)
