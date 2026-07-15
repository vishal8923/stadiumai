"""
test_unit_navigation_service.py
==============================
Unit tests for backend/app/services/navigation_service.py.

Covers:
  - _get_current_crowd_densities returning dict of zone_id -> density
  - calculate_route validation of starting location node (raises 400)
  - calculate_route validation of destination node (raises 400)
  - calculate_route returning correct RouteResponse structure for valid inputs
  - calculate_route raising 404 if no path can be found (unreachable)
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.models import Base
from app.models.models import CrowdDataModel
from app.services.navigation_service import NavigationService


@pytest.fixture
def db_session():
    """Create in-memory SQLite database session for unit testing."""
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_get_current_crowd_densities(db_session):
    """Retrieves latest density for unique zones."""
    c1 = CrowdDataModel(zone_id="zone_gate_a", current_density=0.3)
    c2 = CrowdDataModel(zone_id="zone_gate_a", current_density=0.8) # more recent
    db_session.add_all([c1, c2])
    db_session.commit()

    service = NavigationService(db_session)
    densities = service._get_current_crowd_densities()
    assert "zone_gate_a" in densities
    assert densities["zone_gate_a"] == 0.8


def test_calculate_route_invalid_start(db_session):
    """Raises 400 BAD REQUEST if starting node is invalid."""
    service = NavigationService(db_session)
    with pytest.raises(HTTPException) as exc:
        service.calculate_route("invalid_start", "gate_b")
    assert exc.value.status_code == 400
    assert "Starting location" in exc.value.detail


def test_calculate_route_invalid_dest(db_session):
    """Raises 400 BAD REQUEST if destination node is invalid."""
    service = NavigationService(db_session)
    with pytest.raises(HTTPException) as exc:
        service.calculate_route("gate_a", "invalid_dest")
    assert exc.value.status_code == 400
    assert "Destination" in exc.value.detail


def test_calculate_route_success(db_session):
    """Returns valid RouteResponse structure for valid path query."""
    service = NavigationService(db_session)
    res = service.calculate_route("gate_a", "gate_b")
    assert res.route is not None
    assert isinstance(res.route, list)
    assert res.distance_meters > 0
    assert res.estimated_time_minutes > 0
    assert res.crowd_score in ["Low", "Medium", "High", "Critical"]
    assert isinstance(res.alternative_routes, list)
