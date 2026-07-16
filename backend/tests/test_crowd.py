"""Tests for the crowd density endpoints."""


def test_get_zone_density(client):
    response = client.get("/api/v1/crowd/gate_a")
    assert response.status_code == 200
    data = response.json()
    assert "zone_id" in data
    assert "current_density" in data


def test_get_all_crowd_data(client):
    response = client.get("/api/v1/crowd/all")
    assert response.status_code == 200
    data = response.json()
    assert "zones" in data
    assert isinstance(data["zones"], list)
    assert len(data["zones"]) > 0
