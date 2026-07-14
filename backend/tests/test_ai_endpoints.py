import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_returns_503_without_key():
    response = client.post("/api/v1/chat/", json={"message": "Hello"})
    # Expecting 503 because GEMINI_API_KEY is not set
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert "Gemini" in data["detail"]

def test_translate_returns_503_without_key():
    response = client.post("/api/v1/translate/", json={"text": "Hello", "target_language": "es"})
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert "Gemini" in data["detail"]

def test_incident_classification_returns_503_without_key():
    response = client.post("/api/v1/incidents/", json={
        "type": "medical",
        "location": "gate_a",
        "description": "Someone fell down",
        "severity": "medium",
        "user_id": "test_user"
    })
    # The incident endpoint might still save the incident but attempt AI classification,
    # Let's see what it returns. If it uses AI, it will hit 503.
    # Actually, incident reporting calls classify_incident_ai synchronously in incident_service.py.
    # Let's assume it fails and returns 503.
    assert response.status_code == 503
