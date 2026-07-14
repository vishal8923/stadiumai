import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_system_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime" in data

def test_db_health():
    response = client.get("/api/v1/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_ai_health():
    # Since GEMINI_API_KEY is not configured yet, it should return unconfigured
    response = client.get("/api/v1/health/ai")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unconfigured"
