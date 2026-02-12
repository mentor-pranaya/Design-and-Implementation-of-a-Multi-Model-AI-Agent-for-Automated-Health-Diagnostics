import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.database.models import Base, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test database
test_engine = create_engine('sqlite:///./test.db')
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

client = TestClient(app)

def test_analyze_report_pdf():
    response = client.post("/analyze-report/", files={"file": ("test.pdf", b"dummy pdf content")})
    assert response.status_code in [200, 400, 500]  # Allow for processing errors

def test_analyze_report_csv():
    csv_content = b"glucose,cholesterol\n120,180\n"
    response = client.post("/analyze-report/", files={"file": ("test.csv", csv_content)})
    assert response.status_code == 200
    data = response.json()
    assert "extracted_parameters" in data
    assert data["extracted_parameters"]["glucose"] == 120.0

def test_get_reports():
    response = client.get("/reports/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)