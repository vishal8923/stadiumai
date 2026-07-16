"""test_notifications.py
=====================
Tests for the /api/v1/notifications endpoints.

Coverage:
  - GET /notifications/{user_id}: existing user returns list, unknown user returns empty list
  - POST /notifications/mark-read: valid IDs update count, empty list returns 0,
    missing notification_ids field returns 422
  - Edge cases: very long user ID, wrong data type for notification_ids
  - Schema validation: all fields present in NotificationResponse

All endpoints are non-AI (no Gemini mocking required).
"""

from app.services.notification_service import NotificationService


def test_notifications_known_user_returns_200(client):
    """GET /notifications/user_fan should return 200 with list structure."""
    response = client.get("/api/v1/notifications/user_fan")
    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data
    assert "unread_count" in data
    assert isinstance(data["notifications"], list)


def test_notifications_unknown_user_returns_empty(client):
    """GET /notifications/unknown_user returns 200 with empty notifications list."""
    response = client.get("/api/v1/notifications/completely_unknown_user_xyz")
    assert response.status_code == 200
    data = response.json()
    assert data["notifications"] == []
    assert data["unread_count"] == 0


def test_notifications_unread_count_nonnegative(client):
    """unread_count should always be >= 0."""
    response = client.get("/api/v1/notifications/user_fan")
    assert response.status_code == 200
    assert response.json()["unread_count"] >= 0


def test_notifications_item_schema(client, db_session):
    """Each notification item should have required fields."""
    svc = NotificationService(db_session)
    svc.send_notification(user_id="user_fan", message="Test notification", priority="info")
    db_session.commit()

    response = client.get("/api/v1/notifications/user_fan")
    assert response.status_code == 200
    notifications = response.json()["notifications"]
    if notifications:
        item = notifications[0]
        assert "id" in item
        assert "message" in item
        assert "priority" in item
        assert "is_read" in item
        assert "timestamp" in item


def test_notifications_very_long_user_id(client):
    """Very long user IDs should not crash the server."""
    long_id = "u" * 500
    response = client.get(f"/api/v1/notifications/{long_id}")
    assert response.status_code == 200
    assert response.json()["notifications"] == []


def test_mark_read_valid_ids(client, db_session):
    """POST mark-read with valid notification IDs returns 200 with updated_count."""
    svc = NotificationService(db_session)
    notif = svc.send_notification(user_id="user_fan", message="Mark this read", priority="info")
    db_session.commit()
    notif_id = notif.id

    response = client.post(
        "/api/v1/notifications/mark-read",
        json={"notification_ids": [notif_id]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "updated_count" in data
    assert data["updated_count"] >= 1


def test_mark_read_empty_list_returns_zero(client):
    """POST mark-read with empty list should return 200 with updated_count=0."""
    response = client.post(
        "/api/v1/notifications/mark-read",
        json={"notification_ids": []}
    )
    assert response.status_code == 200
    assert response.json()["updated_count"] == 0


def test_mark_read_nonexistent_ids_returns_zero(client):
    """Nonexistent notification IDs should result in updated_count=0."""
    response = client.post(
        "/api/v1/notifications/mark-read",
        json={"notification_ids": ["nonexistent_notif_id_xyz"]}
    )
    assert response.status_code == 200
    assert response.json()["updated_count"] == 0


def test_mark_read_missing_notification_ids_returns_422(client):
    """POST without required 'notification_ids' field should return 422."""
    response = client.post("/api/v1/notifications/mark-read", json={})
    assert response.status_code == 422


def test_mark_read_wrong_type_returns_422(client):
    """notification_ids must be a list — sending a string should return 422."""
    response = client.post(
        "/api/v1/notifications/mark-read",
        json={"notification_ids": "not_a_list"}
    )
    assert response.status_code == 422


def test_mark_read_null_ids_returns_422(client):
    """notification_ids: null should return 422."""
    response = client.post(
        "/api/v1/notifications/mark-read",
        json={"notification_ids": None}
    )
    assert response.status_code == 422
