"""test_integration.py
===================
Integration tests verifying multi-step operational flows end-to-end.

Flow:
  1. A fan creates a session (POST /users/session)
  2. The fan reports a medical incident (POST /incidents)
  3. The backend uses A* pathfinder logic to auto-dispatch the best staff member
     (e.g., medical staff near the gate) and increments their workload
  4. The admin checks the dashboard and staff listing to confirm workload/incident status
  5. The organizer broadcasts an emergency announcement to the medical team (POST /admin/announcements)
  6. The dispatched staff member queries notifications to receive the dispatch instruction
"""

from unittest.mock import patch
from app.models.models import StaffModel, IncidentModel, NotificationModel

MOCK_MEDICAL_CLASSIFICATION = {
    "type": "medical",
    "priority": "high",
    "severity": "high"
}


@patch("app.services.llm_service.LLMService.classify_incident_ai", return_value=MOCK_MEDICAL_CLASSIFICATION)
def test_full_incident_response_integration_flow(mock_classify, client, db_session):
    """Verifies end-to-end flow from reporting to dispatch and notifications."""
    try:
        db_session.query(StaffModel).delete()
        medical_staff = StaffModel(
            staff_id="staff_med_1",
            name="Dr. Sarah",
            role="medical",
            location="gate_a",
            status="available",
            workload=0
        )
        volunteer_staff = StaffModel(
            staff_id="staff_vol_1",
            name="John Doe",
            role="volunteer",
            location="gate_c",
            status="available",
            workload=0
        )
        db_session.add_all([medical_staff, volunteer_staff])
        db_session.commit()

        session_resp = client.post("/api/v1/users/session")
        assert session_resp.status_code == 200
        user_id = session_resp.json()["user_id"]

        incident_resp = client.post(
            "/api/v1/incidents",
            json={
                "type": "medical",
                "location": "gate_a",
                "description": "A spectator has passed out at Gate A",
                "severity": "high",
                "reporter_id": user_id
            }
        )
        assert incident_resp.status_code == 200
        inc_data = incident_resp.json()
        assert inc_data["status"] == "DISPATCHED"
        assert inc_data["assigned_staff"] == "staff_med_1"

        staff_resp = client.get("/api/v1/admin/staff")
        assert staff_resp.status_code == 200
        staff_list = staff_resp.json()["staff"]

        sarah_profile = next(s for s in staff_list if s["staff_id"] == "staff_med_1")
        assert sarah_profile["status"] == "busy"
        assert sarah_profile["workload"] == 1

        announce_resp = client.post(
            "/api/v1/admin/announcements",
            json={
                "message": "Clear corridor for emergency dispatch",
                "priority": "emergency",
                "target_roles": ["medical"]
            }
        )
        assert announce_resp.status_code == 200
        assert announce_resp.json()["sent_count"] == 1

        notif_resp = client.get("/api/v1/notifications/user_staff_med_1")
        assert notif_resp.status_code == 200
        notifs = notif_resp.json()["notifications"]

        assert len(notifs) > 0
        emergency_notif = next(n for n in notifs if "emergency" in n["priority"])
        assert "Clear corridor" in emergency_notif["message"]

    finally:
        db_session.query(StaffModel).delete()
        db_session.query(IncidentModel).delete()
        db_session.query(NotificationModel).delete()
        db_session.commit()
