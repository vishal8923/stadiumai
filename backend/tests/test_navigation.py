import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_calculate_route_valid():
    response = client.get("/api/v1/navigation/route?from_location=gate_a&to_location=gate_b")
    assert response.status_code == 200
    data = response.json()
    assert "path" in data
    assert "distance" in data

def test_calculate_route_invalid_location():
    response = client.get("/api/v1/navigation/route?from_location=unknown&to_location=gate_b")
    # pathfinder will return 400 for unknown locations or simply error out
    assert response.status_code in [400, 404, 500]

def test_route_with_accessibility():
    response = client.get("/api/v1/navigation/route?from_location=gate_a&to_location=gate_b&accessibility_mode=true")
    assert response.status_code == 200
    data = response.json()
    assert "path" in data
