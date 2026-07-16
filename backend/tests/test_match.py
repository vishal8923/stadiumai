"""test_match.py
=============
Tests for the /api/v1/match endpoints.

Coverage:
  - GET /match/current: live match schema, fallback when no live match
  - GET /match/{match_id}: valid ID (200), nonexistent ID (404)
  - Schema fields: team_a, team_b, status, score, timeline, stats all present
  - Edge cases: special characters in match ID, very long ID

The DB is pre-seeded with a live match (Argentina vs Mexico) and a scheduled
match, so /match/current should always return a result in tests.
"""



def test_match_current_returns_200(client):
    """GET /match/current should return 200 with the live or most recent match."""
    response = client.get("/api/v1/match/current")
    assert response.status_code == 200


def test_match_current_schema(client):
    """Response must include all MatchResponse schema fields."""
    response = client.get("/api/v1/match/current")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "team_a" in data
    assert "team_b" in data
    assert "score_a" in data
    assert "score_b" in data
    assert "status" in data
    assert "stadium" in data
    assert "kickoff_time" in data
    assert "timeline" in data
    assert "stats" in data


def test_match_current_stats_structure(client):
    """Match stats should contain possession and shots fields."""
    response = client.get("/api/v1/match/current")
    assert response.status_code == 200
    stats = response.json()["stats"]
    assert "possession_a" in stats
    assert "possession_b" in stats
    assert "shots_a" in stats
    assert "shots_b" in stats


def test_match_current_timeline_is_list(client):
    """Timeline must be a list."""
    response = client.get("/api/v1/match/current")
    assert response.status_code == 200
    assert isinstance(response.json()["timeline"], list)


def test_match_current_status_valid(client):
    """Status must be one of: scheduled, live, completed."""
    response = client.get("/api/v1/match/current")
    assert response.status_code == 200
    assert response.json()["status"] in ["scheduled", "live", "completed"]


def test_match_by_id_live_match(client):
    """GET /match/match_live should return 200 (seeded live match)."""
    response = client.get("/api/v1/match/match_live")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "match_live"


def test_match_by_id_scheduled_match(client):
    """GET /match/match_scheduled should return 200 (seeded scheduled match)."""
    response = client.get("/api/v1/match/match_scheduled")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "match_scheduled"


def test_match_by_id_not_found_returns_404(client):
    """GET /match/nonexistent_match_id should return 404."""
    response = client.get("/api/v1/match/nonexistent_match_xyz_123")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_match_by_id_error_message_contains_id(client):
    """404 detail should mention the missing match ID."""
    missing_id = "totally_unknown_match"
    response = client.get(f"/api/v1/match/{missing_id}")
    assert response.status_code == 404
    assert missing_id in response.json()["detail"]


def test_match_by_id_very_long_id(client):
    """Extremely long match IDs should return 404 not 500."""
    long_id = "m" * 500
    response = client.get(f"/api/v1/match/{long_id}")
    assert response.status_code == 404


def test_match_by_id_special_characters(client):
    """Special characters in match ID should not crash the server."""
    response = client.get("/api/v1/match/match%20with%20spaces")
    assert response.status_code in [200, 404]


def test_match_map_with_invalid_timeline_json(db_session):
    """map_match_to_response should handle invalid JSON in timeline gracefully."""
    from app.models.models import MatchModel
    from app.routers.match import map_match_to_response

    match = MatchModel(
        id="match_bad_json",
        team_a="Team A",
        team_b="Team B",
        score_a=0,
        score_b=0,
        status="scheduled",
        stadium="Test Stadium",
        kickoff_time="2026-07-20T20:00",
        timeline="not-valid-json{{{",
        stats="also-not-valid-json",
    )
    db_session.add(match)
    db_session.commit()

    response = map_match_to_response(match)
    assert response.timeline == []
    assert response.stats.possession_a == 50


def test_match_current_no_match_returns_404(client, db_session):
    """GET /match/current should return 404 when no matches exist at all."""
    from app.models.models import MatchModel

    db_session.query(MatchModel).delete()
    db_session.commit()

    response = client.get("/api/v1/match/current")
    assert response.status_code == 404
    assert "No match" in response.json()["detail"]
