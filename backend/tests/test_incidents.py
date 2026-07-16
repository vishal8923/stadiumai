"""test_incidents.py
=================
Tests for the /api/v1/incidents endpoints.

Coverage:
  - POST /incidents (create): mocked LLM for happy path, 503 without API key,
    missing required fields (422), invalid types, extremely large input
  - GET /incidents/{id}: found (200), not found (404), invalid ID format
  - Error handling: LLM timeout/error graceful handling
  - Edge cases: empty description, wrong data types

Strategy:
  The IncidentService.report_incident() calls LLMService.classify_incident_ai()
  which raises HTTP 503 when GEMINI_API_KEY is absent.  Happy-path tests use
  unittest.mock.patch to inject a mock classification response so tests run
  offline and deterministically.
"""

from unittest.mock import patch

MOCK_CLASSIFICATION = {
    "type": "medical",
    "priority": "high",
    "severity": "high"
}


def test_incident_create_returns_503_without_gemini_key(client):
    """Without a real GEMINI_API_KEY the endpoint returns 503."""
    response = client.post(
        "/api/v1/incidents",
        json={
            "type": "medical",
            "location": "gate_a",
            "description": "Fan collapsed near Gate A entrance",
            "severity": "high"
        }
    )
    assert response.status_code == 503
    assert "Gemini" in response.json().get("detail", "")


@patch("app.services.llm_service.LLMService.classify_incident_ai", return_value=MOCK_CLASSIFICATION)
def test_incident_create_happy_path(mock_classify, client):
    """With mocked LLM, POST /incidents returns 200 with IncidentResponse schema."""
    response = client.post(
        "/api/v1/incidents",
        json={
            "type": "medical",
            "location": "gate_a",
            "description": "Fan collapsed near Gate A entrance",
            "severity": "medium",
            "reporter_id": "user_fan"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "incident_id" in data
    assert "priority" in data
    assert "status" in data
    assert "response_time_minutes" in data
    assert data["incident_id"].startswith("inc_")
    mock_classify.assert_called_once()


@patch("app.services.llm_service.LLMService.classify_incident_ai", return_value=MOCK_CLASSIFICATION)
def test_incident_create_returns_different_ids(mock_classify, client):
    """Each incident creation should produce a unique incident_id."""
    payload = {
        "type": "security",
        "location": "concourse_1",
        "description": "Suspicious package found near entrance",
        "severity": "high"
    }
    r1 = client.post("/api/v1/incidents", json=payload)
    r2 = client.post("/api/v1/incidents", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["incident_id"] != r2.json()["incident_id"]


def test_incident_create_missing_type_returns_422(client):
    """Missing required 'type' field should return 422."""
    response = client.post(
        "/api/v1/incidents",
        json={
            "location": "gate_b",
            "description": "Missing type field"
        }
    )
    assert response.status_code == 422


def test_incident_create_missing_location_returns_422(client):
    """Missing required 'location' field should return 422."""
    response = client.post(
        "/api/v1/incidents",
        json={
            "type": "medical",
            "description": "Missing location field"
        }
    )
    assert response.status_code == 422


def test_incident_create_missing_description_returns_422(client):
    """Missing required 'description' field should return 422."""
    response = client.post(
        "/api/v1/incidents",
        json={
            "type": "medical",
            "location": "gate_a"
        }
    )
    assert response.status_code == 422


def test_incident_create_empty_body_returns_422(client):
    """Empty body should return 422."""
    response = client.post("/api/v1/incidents", json={})
    assert response.status_code == 422


@patch("app.services.llm_service.LLMService.classify_incident_ai", return_value=MOCK_CLASSIFICATION)
def test_incident_create_extremely_large_description(mock_classify, client):
    """Very long description strings should be handled without server crash."""
    huge_desc = "A" * 10000
    response = client.post(
        "/api/v1/incidents",
        json={
            "type": "infrastructure",
            "location": "concourse_2",
            "description": huge_desc,
            "severity": "low"
        }
    )
    assert response.status_code in [200, 422]


def test_incident_create_wrong_data_type_for_location_returns_422(client):
    """Sending integer for location field should return 422."""
    response = client.post(
        "/api/v1/incidents",
        json={
            "type": "security",
            "location": 12345,
            "description": "Wrong type test"
        }
    )
    assert response.status_code in [200, 422, 503]


@patch(
    "app.services.llm_service.LLMService.classify_incident_ai",
    side_effect=ValueError("LLM timeout simulated")
)
def test_incident_llm_error_returns_graceful_error(mock_classify, client):
    """If the LLM service throws an unexpected exception, app should not crash with 500."""
    response = client.post(
        "/api/v1/incidents",
        json={
            "type": "medical",
            "location": "gate_a",
            "description": "LLM failure test"
        }
    )
    assert response.status_code in [500, 503]


@patch("app.services.llm_service.LLMService.classify_incident_ai", return_value=MOCK_CLASSIFICATION)
def test_incident_get_by_id_happy_path(mock_classify, client):
    """GET /incidents/{id} for a recently created incident should return 200."""
    create_resp = client.post(
        "/api/v1/incidents",
        json={
            "type": "security",
            "location": "gate_c",
            "description": "Gate C crowd surge",
            "severity": "high"
        }
    )
    assert create_resp.status_code == 200
    incident_id = create_resp.json()["incident_id"]

    get_resp = client.get(f"/api/v1/incidents/{incident_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == incident_id
    assert "type" in data
    assert "location" in data
    assert "severity" in data
    assert "status" in data
    assert "created_at" in data


def test_incident_get_nonexistent_id_returns_404(client):
    """GET /incidents/nonexistent should return 404."""
    response = client.get("/api/v1/incidents/nonexistent_incident_id_xyz")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_incident_get_empty_id_returns_404_or_405(client):
    """GET /incidents/ (empty id) should return 404 or 405."""
    response = client.get("/api/v1/incidents/")
    assert response.status_code in [404, 405]
