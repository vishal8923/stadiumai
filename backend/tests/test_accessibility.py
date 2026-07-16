"""test_accessibility.py
=====================
Tests for the /api/v1/accessibility/{service_type} endpoint.

Coverage:
  - Happy path: known service types return structured response
  - Edge case: unknown service type falls back to global list, then 404 if DB empty
  - Input edge cases: empty string, very long type name
  - Schema validation: all required fields present in response

The DB is seeded via the app startup event (seed_database), so accessibility
services (elevator, ramp, restroom, etc.) are present for happy-path tests.
"""



def test_accessibility_elevator_returns_200(client):
    """GET /accessibility/elevator should return 200 with services list and nearest field."""
    response = client.get("/api/v1/accessibility/elevator")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "nearest" in data
    assert "wait_time_minutes" in data
    assert isinstance(data["services"], list)
    assert len(data["services"]) > 0


def test_accessibility_response_schema(client):
    """Each service item must contain the expected fields."""
    response = client.get("/api/v1/accessibility/elevator")
    assert response.status_code == 200
    data = response.json()
    for item in data["services"]:
        assert "id" in item
        assert "service_type" in item
        assert "location" in item
        assert "status" in item
        assert "wait_time_minutes" in item


def test_accessibility_wheelchair_rental(client):
    """wheelchair_rental type should return a valid response."""
    response = client.get("/api/v1/accessibility/wheelchair_rental")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert "services" in response.json()


def test_accessibility_nearest_is_operational_priority(client):
    """The 'nearest' item should preferably be operational."""
    response = client.get("/api/v1/accessibility/elevator")
    if response.status_code == 200:
        data = response.json()
        nearest = data["nearest"]
        operational = [s for s in data["services"] if s["status"] == "operational"]
        if operational:
            assert nearest["status"] == "operational"


def test_accessibility_unknown_type_returns_fallback_or_404(client):
    """Unknown service type should fall back to all services or return 404."""
    response = client.get("/api/v1/accessibility/nonexistent_service_xyz")
    assert response.status_code in [200, 404]


def test_accessibility_empty_string_type(client):
    """Empty string path param is treated as a type value -- should return a result or 404."""
    response = client.get("/api/v1/accessibility/ ")
    assert response.status_code in [200, 404]


def test_accessibility_very_long_type_name(client):
    """Extremely long service type names should not crash the server."""
    long_type = "a" * 500
    response = client.get(f"/api/v1/accessibility/{long_type}")
    assert response.status_code in [200, 404]


def test_accessibility_ramp_type(client):
    """Ramp is a valid seeded service type."""
    response = client.get("/api/v1/accessibility/ramp")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "services" in data
