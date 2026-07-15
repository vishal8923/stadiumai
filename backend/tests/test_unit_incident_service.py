"""
test_unit_incident_service.py
=============================
Unit tests for backend/app/services/incident_service.py.

Covers:
  - _dispatch_staff with empty/no available staff (returns None, 0)
  - _dispatch_staff selecting role-matched staff member
  - _dispatch_staff preferring lower workload staff
  - report_incident with mocked AI classification mapping inputs to DB
  - get_incident successfully returning IncidentDetailResponse
  - get_incident raising 404 for missing records
"""

import pytest
import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.models import Base
from app.models.models import IncidentModel, StaffModel
from app.services.incident_service import IncidentService


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


def test_dispatch_staff_no_staff(db_session):
    """Returns None, 0 if no staff members are online in DB."""
    service = IncidentService(db_session)
    staff_id, eta = service._dispatch_staff("medical", "gate_a")
    assert staff_id is None
    assert eta == 0


def test_dispatch_staff_role_match(db_session):
    """Selects medical staff for medical incident, security for fire/security, etc."""
    s1 = StaffModel(staff_id="st_1", name="Alice", role="volunteer", location="gate_a", status="available", workload=0)
    s2 = StaffModel(staff_id="st_2", name="Bob", role="medical", location="gate_b", status="available", workload=0)
    db_session.add_all([s1, s2])
    db_session.commit()

    service = IncidentService(db_session)
    staff_id, eta = service._dispatch_staff("medical", "gate_b")
    assert staff_id == "st_2"
    assert eta > 0
    # Bob should be set to busy and workload incremented
    db_session.refresh(s2)
    assert s2.status == "busy"
    assert s2.workload == 1


def test_dispatch_staff_workload_preference(db_session):
    """Prefers a staff member with lower workload if multiple are available."""
    # Both are security and near Gate A
    s1 = StaffModel(staff_id="st_1", name="Alice", role="security", location="gate_a", status="available", workload=2)
    s2 = StaffModel(staff_id="st_2", name="Bob", role="security", location="gate_a", status="available", workload=0)
    db_session.add_all([s1, s2])
    db_session.commit()

    service = IncidentService(db_session)
    staff_id, eta = service._dispatch_staff("security", "gate_a")
    assert staff_id == "st_2"


@patch("app.services.llm_service.LLMService.classify_incident_ai")
def test_report_incident_success(mock_classify, db_session):
    """Creates incident, dispatches staff, saves to DB successfully."""
    # Setup mock classification
    mock_classify.return_value = {
        "type": "medical",
        "priority": "critical",
        "severity": "critical"
    }

    # Seed staff member to dispatch
    staff = StaffModel(staff_id="st_1", name="Doctor", role="medical", location="gate_a", status="available", workload=0)
    db_session.add(staff)
    db_session.commit()

    service = IncidentService(db_session)
    res = service.report_incident(
        type_param="unknown",
        location="gate_a",
        description="Fan collapsed at gate A",
        severity_param="low",
        reporter_id="user_1"
    )

    assert res.incident_id.startswith("inc_")
    assert res.priority == "critical"
    assert res.status == "DISPATCHED"
    assert res.assigned_staff == "st_1"

    # Check database save
    db_inc = db_session.query(IncidentModel).filter(IncidentModel.incident_id == res.incident_id).first()
    assert db_inc is not None
    assert db_inc.description == "Fan collapsed at gate A"


def test_get_incident_success(db_session):
    """Fetches details of a single incident."""
    inc = IncidentModel(
        incident_id="inc_test", type="security", location="gate_c",
        description="Intruder on field", severity="high", priority="high",
        status="REPORTED", reporter_id="user_2", created_at=datetime.datetime.utcnow()
    )
    db_session.add(inc)
    db_session.commit()

    service = IncidentService(db_session)
    res = service.get_incident("inc_test")
    assert res.id == "inc_test"
    assert res.location == "gate_c"
    assert res.assigned_staff == "None"


def test_get_incident_not_found(db_session):
    """Raises 404 error if incident does not exist."""
    service = IncidentService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_incident("nonexistent")
    assert exc_info.value.status_code == 404
