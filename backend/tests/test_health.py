"""Tests for health check endpoints."""


def test_system_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime" in data


def test_db_health(client):
    response = client.get("/api/v1/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_ai_health(client):
    response = client.get("/api/v1/health/ai")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unconfigured"
