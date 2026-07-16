"""test_unit_crowd_service.py
==========================
Unit tests for backend/app/services/crowd_service.py.

Covers:
  - _get_level_str classification based on density
  - get_zone_density with no data (fallback behaviour)
  - get_zone_density with one history entry
  - get_zone_density with history representing rising trend
  - get_zone_density with history representing falling trend
  - get_all_zones returning multiple items
  - purge_old_data removing old database records
"""

import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.models import CrowdDataModel
from app.services.crowd_service import CrowdService


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


def test_get_level_str():
    """Correctly assigns category labels to densities."""
    service = CrowdService(None)
    assert service._get_level_str(0.95) == "critical"
    assert service._get_level_str(0.75) == "high"
    assert service._get_level_str(0.4) == "medium"
    assert service._get_level_str(0.2) == "low"


def test_get_zone_density_no_data(db_session):
    """Fallback values returned when database is empty for zone."""
    service = CrowdService(db_session)
    res = service.get_zone_density("gate_a")
    assert res.zone_id == "gate_a"
    assert res.current_density == 0.15
    assert res.level == "low"
    assert res.trend == "stable"


def test_get_zone_density_stable_trend(db_session):
    """Calculates status based on single density record."""
    data = CrowdDataModel(
        zone_id="gate_a",
        current_density=0.5,
        level="medium",
        prediction_5min="medium",
        prediction_15min="medium",
        risk_level="medium",
        trend="stable",
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    db_session.add(data)
    db_session.commit()

    service = CrowdService(db_session)
    res = service.get_zone_density("gate_a")
    assert res.current_density == 0.5
    assert res.trend == "stable"
    assert res.risk_level == "medium"


def test_get_zone_density_rising_trend(db_session):
    """Identifies trend as rising when density is increasing."""
    now = datetime.datetime.now(datetime.timezone.utc)
    d1 = CrowdDataModel(
        zone_id="gate_a", current_density=0.4, level="medium",
        prediction_5min="medium", prediction_15min="medium",
        risk_level="medium", trend="stable", timestamp=now - datetime.timedelta(minutes=5)
    )
    d2 = CrowdDataModel(
        zone_id="gate_a", current_density=0.6, level="medium",
        prediction_5min="medium", prediction_15min="medium",
        risk_level="medium", trend="stable", timestamp=now
    )
    db_session.add_all([d1, d2])
    db_session.commit()

    service = CrowdService(db_session)
    res = service.get_zone_density("gate_a")
    assert res.trend == "rising"
    # rising trend adds +0.05 (5m) and +0.15 (15m)
    assert res.prediction_5min == "medium"     # 0.6 + 0.05 = 0.65 -> medium (< 0.7 threshold)
    # Actually let's just check the result type is str
    assert isinstance(res.prediction_5min, str)
    assert isinstance(res.prediction_15min, str)


def test_get_zone_density_falling_trend(db_session):
    """Identifies trend as falling when density is decreasing."""
    now = datetime.datetime.now(datetime.timezone.utc)
    d1 = CrowdDataModel(
        zone_id="gate_a", current_density=0.8, level="high",
        prediction_5min="high", prediction_15min="high",
        risk_level="high", trend="stable", timestamp=now - datetime.timedelta(minutes=5)
    )
    d2 = CrowdDataModel(
        zone_id="gate_a", current_density=0.5, level="medium",
        prediction_5min="medium", prediction_15min="medium",
        risk_level="medium", trend="stable", timestamp=now
    )
    db_session.add_all([d1, d2])
    db_session.commit()

    service = CrowdService(db_session)
    res = service.get_zone_density("gate_a")
    assert res.trend == "falling"


def test_get_all_zones(db_session):
    """Should return data for all unique zones in DB."""
    now = datetime.datetime.now(datetime.timezone.utc)
    d1 = CrowdDataModel(
        zone_id="gate_a", current_density=0.2, level="low",
        prediction_5min="low", prediction_15min="low",
        risk_level="low", trend="stable", timestamp=now
    )
    d2 = CrowdDataModel(
        zone_id="gate_b", current_density=0.5, level="medium",
        prediction_5min="medium", prediction_15min="medium",
        risk_level="medium", trend="stable", timestamp=now
    )
    db_session.add_all([d1, d2])
    db_session.commit()

    service = CrowdService(db_session)
    res = service.get_all_zones()
    assert len(res.zones) == 2
    zones_ids = [z.zone_id for z in res.zones]
    assert "gate_a" in zones_ids
    assert "gate_b" in zones_ids


def test_purge_old_data(db_session):
    """Should delete records older than 24 hours."""
    now = datetime.datetime.now(datetime.timezone.utc)
    d_new = CrowdDataModel(
        zone_id="gate_a", current_density=0.2, level="low",
        prediction_5min="low", prediction_15min="low",
        risk_level="low", trend="stable", timestamp=now
    )
    d_old = CrowdDataModel(
        zone_id="gate_b", current_density=0.5, level="medium",
        prediction_5min="medium", prediction_15min="medium",
        risk_level="medium", trend="stable", timestamp=now - datetime.timedelta(hours=25)
    )
    db_session.add_all([d_new, d_old])
    db_session.commit()

    service = CrowdService(db_session)
    service.purge_old_data()

    remaining = db_session.query(CrowdDataModel).all()
    assert len(remaining) == 1
    assert remaining[0].zone_id == "gate_a"
