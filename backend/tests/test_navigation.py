"""Tests for the navigation /api/v1/navigate endpoint."""


def test_calculate_route_valid(client):
    response = client.post(
        "/api/v1/navigate",
        json={"from_location": "gate_a", "to_location": "gate_b"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "route" in data
    assert "distance_meters" in data


def test_calculate_route_invalid_location(client):
    response = client.post(
        "/api/v1/navigate",
        json={"from_location": "unknown", "to_location": "gate_b"}
    )
    assert response.status_code in [400, 404, 500]


def test_route_with_accessibility(client):
    response = client.post(
        "/api/v1/navigate",
        json={"from_location": "gate_a", "to_location": "gate_b", "accessibility_mode": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert "route" in data
