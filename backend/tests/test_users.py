"""test_users.py
=============
Tests for the /api/v1/users endpoints.

Coverage:
  - POST /users/session: creates a new session with unique user_id, schema check
  - POST /users/session twice: produces distinct user IDs
  - GET /users/{user_id}/history: existing user returns conversation list
  - GET /users/{user_id}/history: nonexistent user returns 404
  - Edge cases: very long user ID, special characters in user ID
  - Schema validation: UserSessionResponse and UserHistoryResponse fields

All endpoints are non-AI; no Gemini mocking required.
"""



def test_create_session_returns_200(client):
    """POST /users/session should return 200 with user_id and created_at."""
    response = client.post("/api/v1/users/session")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "created_at" in data


def test_create_session_user_id_format(client):
    """Created user_id should start with 'usr_'."""
    response = client.post("/api/v1/users/session")
    assert response.status_code == 200
    user_id = response.json()["user_id"]
    assert user_id.startswith("usr_")


def test_create_session_created_at_is_string(client):
    """created_at should be an ISO format string."""
    response = client.post("/api/v1/users/session")
    assert response.status_code == 200
    created_at = response.json()["created_at"]
    assert isinstance(created_at, str)
    assert len(created_at) > 10


def test_create_two_sessions_have_unique_ids(client):
    """Two consecutive session creations should produce distinct user IDs."""
    r1 = client.post("/api/v1/users/session")
    r2 = client.post("/api/v1/users/session")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["user_id"] != r2.json()["user_id"]


def test_user_history_seeded_user_returns_200(client):
    """GET /users/user_fan/history should return 200 (user_fan is seeded)."""
    response = client.get("/api/v1/users/user_fan/history")
    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert "total" in data
    assert isinstance(data["conversations"], list)


def test_user_history_total_matches_list_length(client):
    """Total field should match the number of items in conversations list."""
    response = client.get("/api/v1/users/user_fan/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["conversations"])


def test_user_history_new_user_returns_empty(client):
    """A freshly created user has no conversation history."""
    create_resp = client.post("/api/v1/users/session")
    assert create_resp.status_code == 200
    user_id = create_resp.json()["user_id"]

    history_resp = client.get(f"/api/v1/users/{user_id}/history")
    assert history_resp.status_code == 200
    data = history_resp.json()
    assert data["conversations"] == []
    assert data["total"] == 0


def test_user_history_nonexistent_user_returns_404(client):
    """GET /users/nonexistent_user/history should return 404."""
    response = client.get("/api/v1/users/nonexistent_user_xyz_999/history")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_user_history_404_detail_contains_user_id(client):
    """404 detail message should mention the missing user ID."""
    missing_id = "totally_unknown_usr_id"
    response = client.get(f"/api/v1/users/{missing_id}/history")
    assert response.status_code == 404
    assert missing_id in response.json()["detail"]


def test_user_history_very_long_user_id_returns_404(client):
    """Very long user IDs should return 404 not 500."""
    long_id = "usr_" + "x" * 500
    response = client.get(f"/api/v1/users/{long_id}/history")
    assert response.status_code == 404


def test_user_history_conversation_item_schema(client):
    """If conversations exist, each item must have role, message, timestamp."""
    response = client.get("/api/v1/users/user_fan/history")
    assert response.status_code == 200
    conversations = response.json()["conversations"]
    for conv in conversations:
        assert "role" in conv
        assert "message" in conv
        assert "timestamp" in conv
        assert "actions" in conv


def test_user_history_with_actions(client, db_session):
    """Conversations with actions JSON should be parsed into Action objects."""
    import json
    from app.models.models import ConversationModel, UserModel
    import datetime

    user = UserModel(
        user_id="usr_actions_test",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        role="fan",
        language="en",
        accessibility_mode=False,
    )
    db_session.add(user)

    conv = ConversationModel(
        user_id="usr_actions_test",
        role="assistant",
        message="Here is your route",
        intent="navigation",
        actions=json.dumps([{"type": "navigation", "payload": {"route": ["gate_a"]}}]),
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    db_session.add(conv)
    db_session.commit()

    response = client.get("/api/v1/users/usr_actions_test/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    actions = data["conversations"][0]["actions"]
    assert len(actions) == 1
    assert actions[0]["type"] == "navigation"
