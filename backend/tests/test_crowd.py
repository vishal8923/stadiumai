import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_zone_density():
    # gate_a exists in stadium_graph.py
    response = client.get("/api/v1/crowd/density/gate_a")
    assert response.status_code == 200
    data = response.json()
    assert "zone_id" in data
    assert data["zone_id"] == "gate_a"
    assert "current_density" in data

def test_get_stadium_overview():
    response = client.get("/api/v1/crowd/density")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
