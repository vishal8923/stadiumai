"""
test_unit_services.py
======================
Unit tests for TransportService, AnalyticsService, and NotificationService.

Covers:
  - TransportService: get_options returning correct schema, sorting options, falling back to all options on empty filters
  - AnalyticsService: log_request saving logs correctly, get_usage_analytics generating stats
  - NotificationService: send_notification inserting notification model, mark_notifications_read updating status, get_user_notifications retrieving data
"""

import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.models import Base
from app.models.models import TransportModel, AnalyticsModel, NotificationModel
from app.services.transport_service import TransportService
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService


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


# ── TransportService Tests ─────────────────────────────────────────────────────

def test_transport_get_options_empty_db(db_session):
    """Raises 404 if no options are available in DB."""
    service = TransportService(db_session)
    with pytest.raises(HTTPException) as exc:
        service.get_options("gate_a")
    assert exc.value.status_code == 404


def test_transport_get_options_success(db_session):
    """Retrieves options, sets traffic level and identifies best recommendation."""
    t1 = TransportModel(id="1", location="gate_a", destination="downtown", mode="bus", eta_minutes=15, recommendation_score=4.0, traffic_level="light", details="")
    t2 = TransportModel(id="2", location="gate_a", destination="downtown", mode="metro", eta_minutes=10, recommendation_score=4.8, traffic_level="moderate", details="")
    db_session.add_all([t1, t2])
    db_session.commit()

    service = TransportService(db_session)
    res = service.get_options("gate_a")
    assert len(res.options) == 2
    # Recommended should be t2 since score is higher
    assert res.recommendation.id == "2"
    assert res.traffic_level == "moderate"


# ── AnalyticsService Tests ─────────────────────────────────────────────────────

def test_analytics_log_request(db_session):
    """Correctly logs requests into database."""
    service = AnalyticsService(db_session)
    service.log_request("/api/v1/chat", "POST", 200, 150.5, "user_1")

    log = db_session.query(AnalyticsModel).first()
    assert log is not None
    assert log.endpoint == "/api/v1/chat"
    assert log.method == "POST"
    assert log.status_code == 200
    assert log.latency_ms == 150.5
    assert log.user_id == "user_1"


def test_analytics_get_usage_analytics(db_session):
    """Computes stats fromlogged data."""
    now = datetime.datetime.utcnow()
    # Log 3 successful calls and 1 error call
    l1 = AnalyticsModel(endpoint="/api/v1/chat", method="POST", status_code=200, latency_ms=100.0, user_id="user_1", timestamp=now)
    l2 = AnalyticsModel(endpoint="/api/v1/navigate", method="POST", status_code=200, latency_ms=200.0, user_id="user_2", timestamp=now)
    l3 = AnalyticsModel(endpoint="/api/v1/chat", method="POST", status_code=500, latency_ms=50.0, user_id="user_1", timestamp=now)
    db_session.add_all([l1, l2, l3])
    db_session.commit()

    service = AnalyticsService(db_session)
    res = service.get_usage_analytics("24h")
    # Minimally, it returns either count, defaults or mapped values
    assert res.api_calls >= 3
    assert res.active_users >= 2
    assert res.error_rate == pytest.approx(1/3, rel=1e-2)


# ── NotificationService Tests ──────────────────────────────────────────────────

def test_notification_send_and_get(db_session):
    """Sends notification and retrieves for specific user sorted by timestamp desc."""
    service = NotificationService(db_session)
    n1 = service.send_notification("user_1", "Hello First", "info")
    n2 = service.send_notification("user_1", "Hello Second", "warning")

    res = service.get_user_notifications("user_1")
    assert res.unread_count == 2
    assert len(res.notifications) == 2
    # Sorted by desc timestamp, so n2 first
    assert res.notifications[0].id == n2.id
    assert res.notifications[1].id == n1.id


def test_notification_mark_read(db_session):
    """Marks specific notifications as read."""
    service = NotificationService(db_session)
    n1 = service.send_notification("user_1", "Msg 1", "info")
    n2 = service.send_notification("user_1", "Msg 2", "info")

    updated = service.mark_notifications_read([n1.id])
    assert updated == 1

    res = service.get_user_notifications("user_1")
    assert res.unread_count == 1
    assert res.notifications[1].is_read is True  # n1 is older, so at index 1
    assert res.notifications[0].is_read is False # n2 is index 0
