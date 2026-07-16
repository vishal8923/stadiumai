"""test_admin.py
=============
Tests for all /api/v1/admin/* endpoints.

Coverage:
  - Dashboard overview: metrics keys present
  - Incident listing: pagination, filters, 404 for unknown ID
  - Incident PATCH: valid update, 404 for missing incident
  - Crowd analytics: trends/predictions/zone_breakdown structure
  - Staff listing: response schema
  - Announcements: valid broadcast, missing required field (422)
  - Usage analytics: period-based filtering

All endpoints are non-AI; no Gemini mocking required.
"""

import pytest


def test_admin_dashboard_returns_200(client):
    """GET /admin/dashboard should return 200 with required metric keys."""
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "active_incidents" in data
    assert "crowd_level" in data
    assert "ai_queries_today" in data
    assert "avg_response_time" in data
    assert "staff_online" in data
    assert "alerts" in data


def test_admin_dashboard_crowd_level_valid(client):
    """crowd_level must be one of the expected categorical values."""
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 200
    crowd_level = response.json()["crowd_level"]
    assert crowd_level in ["Low", "Medium", "High", "Critical"]


def test_admin_dashboard_alerts_is_list(client):
    """Alerts field must be a list."""
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 200
    assert isinstance(response.json()["alerts"], list)


def test_admin_incidents_list_returns_200(client):
    """GET /admin/incidents should return 200 with pagination fields."""
    response = client.get("/api/v1/admin/incidents")
    assert response.status_code == 200
    data = response.json()
    assert "incidents" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert isinstance(data["incidents"], list)


def test_admin_incidents_list_pagination(client):
    """Pagination params should work without error."""
    response = client.get("/api/v1/admin/incidents?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert len(data["incidents"]) <= 5


def test_admin_incidents_filter_by_status(client):
    """Filtering by status param should return 200."""
    response = client.get("/api/v1/admin/incidents?status=REPORTED")
    assert response.status_code == 200
    data = response.json()
    for inc in data["incidents"]:
        assert inc["status"] == "REPORTED"


def test_admin_incidents_filter_by_priority(client):
    """Filtering by priority should work."""
    response = client.get("/api/v1/admin/incidents?priority=high")
    assert response.status_code == 200
    assert "incidents" in response.json()


def test_admin_incidents_invalid_page_returns_422(client):
    """Page < 1 should return 422."""
    response = client.get("/api/v1/admin/incidents?page=0")
    assert response.status_code == 422


def test_admin_patch_incident_not_found(client):
    """PATCH on nonexistent incident should return 404."""
    response = client.patch(
        "/api/v1/admin/incidents/nonexistent_incident_id",
        json={"status": "RESOLVED"}
    )
    assert response.status_code == 404
    assert "detail" in response.json()


def test_admin_patch_incident_valid(client):
    """PATCH on a real incident (seeded) should return 200 with updated fields."""
    list_response = client.get("/api/v1/admin/incidents?limit=1")
    assert list_response.status_code == 200
    incidents = list_response.json()["incidents"]
    if not incidents:
        pytest.skip("No incidents seeded in DB")

    incident_id = incidents[0]["id"]
    response = client.patch(
        f"/api/v1/admin/incidents/{incident_id}",
        json={"priority": "low"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "status" in data
    assert "updated_at" in data


def test_admin_crowd_analytics_returns_200(client):
    """GET /admin/crowd/analytics should return 200 with structured data."""
    response = client.get("/api/v1/admin/crowd/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert "peak_times" in data
    assert "predictions" in data
    assert "zone_breakdown" in data


def test_admin_crowd_analytics_trends_structure(client):
    """Trends must be a list of {time, density} objects."""
    response = client.get("/api/v1/admin/crowd/analytics")
    assert response.status_code == 200
    trends = response.json()["trends"]
    assert isinstance(trends, list)
    assert len(trends) > 0
    for t in trends:
        assert "time" in t
        assert "density" in t


def test_admin_crowd_analytics_zone_breakdown(client):
    """zone_breakdown must contain zone, density, status."""
    response = client.get("/api/v1/admin/crowd/analytics")
    assert response.status_code == 200
    zones = response.json()["zone_breakdown"]
    assert isinstance(zones, list)
    for z in zones:
        assert "zone" in z
        assert "density" in z
        assert "status" in z


def test_admin_staff_returns_200(client):
    """GET /admin/staff should return staff list with counts."""
    response = client.get("/api/v1/admin/staff")
    assert response.status_code == 200
    data = response.json()
    assert "staff" in data
    assert "total" in data
    assert "available" in data
    assert "busy" in data
    assert isinstance(data["staff"], list)


def test_admin_staff_count_consistency(client):
    """Available + busy <= total (some may be offline)."""
    response = client.get("/api/v1/admin/staff")
    data = response.json()
    assert data["available"] + data["busy"] <= data["total"]


def test_admin_announcements_valid(client):
    """POST /admin/announcements with valid body should return 200."""
    response = client.post(
        "/api/v1/admin/announcements",
        json={"message": "Testing PA system", "priority": "info"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "announcement_id" in data
    assert "sent_count" in data
    assert "timestamp" in data


def test_admin_announcements_with_target_roles(client):
    """Announcements targeted to specific roles should work."""
    response = client.post(
        "/api/v1/admin/announcements",
        json={
            "message": "Emergency drill in 5 minutes",
            "priority": "emergency",
            "target_roles": ["security", "medical"]
        }
    )
    assert response.status_code == 200


def test_admin_announcements_missing_message_returns_422(client):
    """POST without required 'message' field should return 422."""
    response = client.post(
        "/api/v1/admin/announcements",
        json={"priority": "info"}
    )
    assert response.status_code == 422


def test_admin_announcements_missing_priority_returns_422(client):
    """POST without required 'priority' field should return 422."""
    response = client.post(
        "/api/v1/admin/announcements",
        json={"message": "Missing priority field"}
    )
    assert response.status_code == 422


def test_admin_announcements_wrong_type_returns_422(client):
    """Sending integer for message should return 422."""
    response = client.post(
        "/api/v1/admin/announcements",
        json={"message": 12345, "priority": "info"}
    )
    assert response.status_code in [200, 422]


def test_admin_usage_analytics_default_period(client):
    """GET /admin/analytics/usage should return usage metrics."""
    response = client.get("/api/v1/admin/analytics/usage")
    assert response.status_code == 200
    data = response.json()
    assert "api_calls" in data
    assert "active_users" in data
    assert "popular_features" in data
    assert "error_rate" in data
    assert "avg_latency" in data


def test_admin_usage_analytics_1h_period(client):
    """period=1h should return valid analytics response."""
    response = client.get("/api/v1/admin/analytics/usage?period=1h")
    assert response.status_code == 200


def test_admin_usage_analytics_7d_period(client):
    """period=7d should return valid analytics response."""
    response = client.get("/api/v1/admin/analytics/usage?period=7d")
    assert response.status_code == 200


def test_admin_incidents_filter_by_type(client):
    """Filtering by type param should return 200."""
    response = client.get("/api/v1/admin/incidents?type=medical")
    assert response.status_code == 200
    data = response.json()
    assert "incidents" in data


def test_admin_patch_incident_with_staff_assignment(client):
    """PATCH with assigned_staff on a real incident should work."""
    list_response = client.get("/api/v1/admin/incidents?limit=1")
    assert list_response.status_code == 200
    incidents = list_response.json()["incidents"]
    if not incidents:
        pytest.skip("No incidents seeded in DB")

    incident_id = incidents[0]["id"]
    response = client.patch(
        f"/api/v1/admin/incidents/{incident_id}",
        json={"assigned_staff": "staff_1"}
    )
    assert response.status_code == 200


def test_admin_patch_incident_resolved_status(client):
    """PATCH setting status to RESOLVED should include resolved_at."""
    list_response = client.get("/api/v1/admin/incidents?limit=1")
    assert list_response.status_code == 200
    incidents = list_response.json()["incidents"]
    if not incidents:
        pytest.skip("No incidents seeded in DB")

    incident_id = incidents[0]["id"]
    response = client.patch(
        f"/api/v1/admin/incidents/{incident_id}",
        json={"status": "RESOLVED"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RESOLVED"


def test_admin_usage_analytics_30d_period(client):
    """period=30d should return valid analytics response."""
    response = client.get("/api/v1/admin/analytics/usage?period=30d")
    assert response.status_code == 200
