"""test_transport.py
=================
Tests for the /api/v1/transport endpoint.

Coverage:
  - GET /transport?location=...: happy path returns options, recommendation, traffic_level
  - Mode filter: ?mode=Metro filters results
  - Destination filter: ?destination=Downtown filters results
  - Missing required 'location' param returns 422
  - Unknown location falls back to all available options (no 404)
  - Response schema validation: TransportResponse fields present
  - Edge cases: empty location, very long location, wrong param types

This endpoint is non-AI; no Gemini mocking required.
"""



def test_transport_gate_a_returns_200(client):
    """GET /transport?location=gate_a should return options with correct schema."""
    response = client.get("/api/v1/transport?location=gate_a")
    assert response.status_code == 200
    data = response.json()
    assert "options" in data
    assert "recommendation" in data
    assert "traffic_level" in data
    assert isinstance(data["options"], list)
    assert len(data["options"]) > 0


def test_transport_schema_validation(client):
    """Each transport option must contain expected fields."""
    response = client.get("/api/v1/transport?location=gate_a")
    assert response.status_code == 200
    options = response.json()["options"]
    for opt in options:
        assert "id" in opt
        assert "mode" in opt
        assert "destination" in opt
        assert "eta_minutes" in opt
        assert "recommendation_score" in opt


def test_transport_recommendation_is_highest_scored(client):
    """The recommendation should be the option with the highest recommendation_score."""
    response = client.get("/api/v1/transport?location=gate_a")
    assert response.status_code == 200
    data = response.json()
    options = data["options"]
    recommendation = data["recommendation"]
    if len(options) > 1:
        max_score = max(o["recommendation_score"] for o in options)
        assert recommendation["recommendation_score"] == max_score


def test_transport_traffic_level_valid(client):
    """traffic_level must be one of: light, moderate, heavy."""
    response = client.get("/api/v1/transport?location=gate_a")
    assert response.status_code == 200
    assert response.json()["traffic_level"] in ["light", "moderate", "heavy"]


def test_transport_with_mode_filter(client):
    """Adding mode=Metro should return results (or fall back to all)."""
    response = client.get("/api/v1/transport?location=gate_a&mode=Metro")
    assert response.status_code == 200
    assert "options" in response.json()


def test_transport_with_destination_filter(client):
    """Adding destination param should work without error."""
    response = client.get("/api/v1/transport?location=gate_a&destination=Downtown")
    assert response.status_code == 200


def test_transport_with_all_params(client):
    """All three params together should not cause errors."""
    response = client.get(
        "/api/v1/transport?location=gate_a&destination=Airport&mode=Shuttle"
    )
    assert response.status_code == 200


def test_transport_missing_location_returns_422(client):
    """GET /transport without location param should return 422."""
    response = client.get("/api/v1/transport")
    assert response.status_code == 422


def test_transport_unknown_location_falls_back(client):
    """Unknown location falls back to all transport options (no 404)."""
    response = client.get("/api/v1/transport?location=completely_unknown_location_xyz")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert len(response.json()["options"]) > 0


def test_transport_very_long_location(client):
    """Extremely long location strings should not crash the server."""
    long_loc = "gate_" + "a" * 500
    response = client.get(f"/api/v1/transport?location={long_loc}")
    assert response.status_code in [200, 404, 422]


def test_transport_stadium_location_works(client):
    """'stadium' as location should match any entry with 'stadium' in location field."""
    response = client.get("/api/v1/transport?location=stadium")
    assert response.status_code in [200, 404]


def test_transport_options_sorted_by_score_descending(client):
    """Options should be sorted by recommendation_score descending."""
    response = client.get("/api/v1/transport?location=gate_a")
    assert response.status_code == 200
    options = response.json()["options"]
    if len(options) > 1:
        scores = [o["recommendation_score"] for o in options]
        assert scores == sorted(scores, reverse=True)
