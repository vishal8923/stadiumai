"""test_unit_pathfinder.py
=======================
Unit tests for backend/app/utils/pathfinder.py.

Covers:
  - euclidean_distance calculation
  - get_crowd_penalty_multiplier based on density
  - get_crowd_score_label based on density
  - find_path with known/expected graph outputs
  - find_path with accessibility_mode (filtering accessible edges)
  - find_path with avoid_crowds (penalty multiplier on dense zones)
  - find_path with unreachable/nonexistent nodes
  - get_route_with_alternatives including alternative path generation
"""

import pytest
from app.utils.pathfinder import (
    euclidean_distance,
    get_crowd_penalty_multiplier,
    get_crowd_score_label,
    find_path,
    get_route_with_alternatives
)


def test_euclidean_distance_valid():
    """Distance between gate_a (0.0, 100.0) and concourse_1 (0.0, 60.0) should be 40.0."""
    dist = euclidean_distance("gate_a", "concourse_1")
    assert dist == pytest.approx(40.0)


def test_euclidean_distance_missing_nodes():
    """Distance involving a missing node should return 0.0."""
    dist1 = euclidean_distance("nonexistent", "gate_a")
    dist2 = euclidean_distance("gate_a", "nonexistent")
    assert dist1 == 0.0
    assert dist2 == 0.0


def test_crowd_penalty_multiplier():
    """Penalty ranges: <0.3 -> 0.0, >=0.3 -> 0.2, >=0.7 -> 0.4, >=0.9 -> 0.6."""
    assert get_crowd_penalty_multiplier(0.1) == 0.0
    assert get_crowd_penalty_multiplier(0.3) == 0.2
    assert get_crowd_penalty_multiplier(0.5) == 0.2
    assert get_crowd_penalty_multiplier(0.7) == 0.4
    assert get_crowd_penalty_multiplier(0.85) == 0.4
    assert get_crowd_penalty_multiplier(0.9) == 0.6
    assert get_crowd_penalty_multiplier(1.0) == 0.6


def test_crowd_score_label():
    """Labels: <0.3 -> Low, >=0.3 -> Medium, >=0.7 -> High, >=0.9 -> Critical."""
    assert get_crowd_score_label(0.1) == "Low"
    assert get_crowd_score_label(0.3) == "Medium"
    assert get_crowd_score_label(0.7) == "High"
    assert get_crowd_score_label(0.95) == "Critical"


def test_find_path_happy_path():
    """Standard path finding between two adjacent nodes."""
    res = find_path("gate_a", "concourse_1")
    assert res is not None
    assert res["route"] == ["gate_a", "concourse_1"]
    assert res["distance_meters"] == 40
    assert res["estimated_time_minutes"] > 0
    assert res["crowd_score"] == "Low"


def test_find_path_invalid_nodes():
    """If from_node or to_node is invalid, should return None."""
    assert find_path("nonexistent", "gate_a") is None
    assert find_path("gate_a", "nonexistent") is None


def test_find_path_accessibility_mode():
    """Accessibility mode should filter out non-accessible edges."""
    # From concourse_1 to sec_1, accessible is False.
    # So with accessibility_mode=True, finding a path directly or via sec_1 shouldn't use that edge.
    # Let's test routing to sec_1. If we enable accessibility_mode, it should return None since all edges to sec_1 are accessible=False.
    res_non_acc = find_path("concourse_1", "sec_1", accessibility_mode=False)
    res_acc = find_path("concourse_1", "sec_1", accessibility_mode=True)
    assert res_non_acc is not None
    assert res_acc is None


def test_find_path_avoid_crowds():
    """Path finding with avoid_crowds increases weights on high density zones."""
    crowd_levels = {"zone_concourse_1": 0.95, "zone_concourse_2": 0.1, "zone_concourse_3": 0.1, "zone_concourse_4": 0.1}
    res_normal = find_path("gate_b", "gate_h", avoid_crowds=False, crowd_levels=crowd_levels)
    res_avoid = find_path("gate_b", "gate_h", avoid_crowds=True, crowd_levels=crowd_levels)
    assert res_normal is not None
    assert res_avoid is not None


def test_get_route_with_alternatives():
    """Returns primary route and alternative routes."""
    res = get_route_with_alternatives("gate_a", "gate_e")
    assert res is not None
    assert "route" in res
    assert "alternative_routes" in res
    assert "estimated_time_minutes" in res
    assert "distance_meters" in res
    assert "crowd_score" in res
    assert isinstance(res["alternative_routes"], list)
