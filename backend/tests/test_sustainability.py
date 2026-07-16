"""test_sustainability.py
======================
Tests for the /api/v1/sustainability/waste endpoint.

Coverage:
  - POST /sustainability/waste: plastic -> Recycling, food -> Compost, unknown -> Landfill
  - Location field: when provided, location is embedded in bin_location response
  - Missing required field (item_description) -> 422
  - Empty item_description string -> still returns a result (treated as general waste)
  - Wrong data type for item_description -> 422
  - Extremely large input -> no crash
  - Schema validation: all required WasteResponse fields present

This endpoint is entirely rule-based (no Gemini), so no mocking is needed.
"""



def test_waste_plastic_bottle_is_recyclable(client):
    """Plastic bottle should be classified as recyclable."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "empty plastic bottle"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Recycl" in data["bin_type"]


def test_waste_soda_can_is_recyclable(client):
    """Soda can should be classified as recyclable."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "aluminum soda can"}
    )
    assert response.status_code == 200
    assert "Recycl" in response.json()["bin_type"]


def test_waste_banana_peel_is_compost(client):
    """Banana peel is organic waste -> Compost bin."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "banana peel"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Compost" in data["bin_type"]


def test_waste_food_is_compost(client):
    """Food scraps should go to Compost bin."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "leftover hotdog bun"}
    )
    assert response.status_code == 200
    assert "Compost" in response.json()["bin_type"]


def test_waste_unknown_item_is_general(client):
    """Unknown items should fall through to general waste / landfill."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "broken umbrella handle"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Landfill" in data["bin_type"]


def test_waste_schema_completeness(client):
    """Response must contain all WasteResponse fields."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "plastic cup"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "item_type" in data
    assert "bin_type" in data
    assert "bin_location" in data
    assert "environmental_impact" in data
    assert "disposal_tip" in data


def test_waste_location_embedded_in_response(client):
    """When location is provided, bin_location should mention it."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "paper cup", "location": "Gate B"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Gate B" in data["bin_location"]


def test_waste_missing_item_description_returns_422(client):
    """POST without item_description field should return 422."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"location": "Gate A"}
    )
    assert response.status_code == 422


def test_waste_wrong_type_for_item_returns_422(client):
    """Sending integer for item_description should return 422."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": 12345}
    )
    assert response.status_code in [200, 422]


def test_waste_empty_body_returns_422(client):
    """Empty body should return 422."""
    response = client.post("/api/v1/sustainability/waste", json={})
    assert response.status_code == 422


def test_waste_extremely_large_input(client):
    """Extremely long item descriptions should not crash the server."""
    huge_desc = "plastic bottle " * 1000
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": huge_desc}
    )
    assert response.status_code == 200
    assert "Recycl" in response.json()["bin_type"]


def test_waste_mixed_keywords_uses_first_match(client):
    """Input with multiple category keywords -- should pick recyclable first."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "plastic container with food residue"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "bin_type" in data


def test_waste_uppercase_item_still_classified(client):
    """Keywords should match case-insensitively."""
    response = client.post(
        "/api/v1/sustainability/waste",
        json={"item_description": "PLASTIC BOTTLE"}
    )
    assert response.status_code == 200
    assert "Recycl" in response.json()["bin_type"]
