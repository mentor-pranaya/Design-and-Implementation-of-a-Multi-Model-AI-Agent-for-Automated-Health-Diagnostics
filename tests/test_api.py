"""Integration tests for FastAPI backend."""

import json
import pytest
from fastapi.testclient import TestClient

from api.main import app, UPLOAD_DIR


client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Health Report AI Backend"


def test_analyze_missing_file():
    """Test analyze endpoint without file."""
    response = client.post("/analyze", data={})
    assert response.status_code == 422


def test_analyze_invalid_file_format(tmp_path):
    """Test analyze endpoint with invalid file format."""
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("test data")

    with open(invalid_file, "rb") as f:
        response = client.post(
            "/analyze",
            files={"file": ("test.txt", f, "text/plain")},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "error"
    assert "Invalid file format" in result["message"]


def test_upload_dir_created():
    """Test that upload directory is created."""
    assert UPLOAD_DIR  # Should exist or be created on app startup


def test_api_endpoints_exist():
    """Test that all expected endpoints are available."""
    response = client.get("/")
    data = response.json()
    assert "health" in data["endpoints"]
    assert "analyze" in data["endpoints"]
    assert "batch_analyze" in data["endpoints"]


def test_analyze_response_structure(tmp_path):
    """Test that analyze endpoint returns proper response structure."""
    json_file = tmp_path / "test_report.json"
    json_file.write_text(json.dumps({"test": "data"}))

    with open(json_file, "rb") as f:
        response = client.post(
            "/analyze",
            files={"file": ("test_report.json", f, "application/json")},
        )

    assert response.status_code == 200
    result = response.json()
    assert "status" in result
    assert "message" in result
    assert result["status"] in ("success", "error")


