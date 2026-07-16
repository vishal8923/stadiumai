import uuid
import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import IncidentModel, StaffModel
from app.models.schemas import IncidentResponse, IncidentDetailResponse
from app.services.llm_service import LLMService
from app.utils.pathfinder import find_path

class IncidentService:
    def __init__(self, db: Session):
        self.db = db

    def report_incident(
        self,
        type_param: str,
        location: str,
        description: str,
        severity_param: str,
        reporter_id: str | None = None,
    ) -> IncidentResponse:
        llm = LLMService(self.db)
        try:
            classification = llm.classify_incident_ai(description)
        except HTTPException:
            raise
        except (ValueError, TypeError, RuntimeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini AI classification failed. Please try again later.",
            ) from exc

        ai_type = classification.get("type", type_param)
        ai_priority = classification.get("priority", "medium")
        ai_severity = classification.get("severity", severity_param)

        incident_id = f"inc_{uuid.uuid4().hex[:8]}"

        incident = IncidentModel(
            incident_id=incident_id,
            type=ai_type,
            location=location,
            description=description,
            severity=ai_severity,
            priority=ai_priority,
            status="REPORTED",
            reporter_id=reporter_id,
            assigned_staff=None,
            response_time_minutes=0,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )

        assigned_staff_id, eta = self._dispatch_staff(ai_type, location)

        if assigned_staff_id:
            incident.assigned_staff = assigned_staff_id
            incident.status = "DISPATCHED"
            incident.response_time_minutes = eta

        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        return IncidentResponse(
            incident_id=incident.incident_id,
            priority=incident.priority,
            response_time_minutes=incident.response_time_minutes,
            status=incident.status,
            assigned_staff=incident.assigned_staff,
        )

    def get_incident(self, incident_id: str) -> IncidentDetailResponse:
        incident = self.db.query(IncidentModel).filter(
            IncidentModel.incident_id == incident_id,
        ).first()

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        return IncidentDetailResponse(
            id=incident.incident_id,
            type=incident.type,
            location=incident.location,
            severity=incident.severity,
            description=incident.description,
            status=incident.status,
            response_time_minutes=incident.response_time_minutes,
            assigned_staff=incident.assigned_staff or "None",
            created_at=incident.created_at.isoformat(),
            resolved_at=incident.resolved_at.isoformat() if incident.resolved_at else None,
        )

    def _dispatch_staff(self, incident_type: str, location: str) -> tuple[str | None, int]:
        staff_members = self.db.query(StaffModel).filter(
            StaffModel.status != "offline",
        ).all()

        if not staff_members:
            return None, 0

        best_staff = None
        min_score = float("inf")
        best_eta = 0

        role_map = {
            "medical": "medical",
            "fire": "security",
            "security": "security",
            "lost_person": "volunteer",
            "infrastructure": "logistics",
        }
        desired_role = role_map.get(incident_type, "volunteer")

        for staff in staff_members:
            role_score = 0 if staff.role == desired_role else 100
            workload_score = staff.workload * 50
            distance = 100.0
            path_res = find_path(staff.location, location)
            if path_res:
                distance = float(path_res["distance_meters"])
            distance_score = distance
            total_score = role_score + workload_score + distance_score

            if total_score < min_score:
                min_score = total_score
                best_staff = staff
                best_eta = round((distance / 1.4) / 60.0) + 2

        if best_staff:
            best_staff.workload += 1
            best_staff.status = "busy"
            self.db.commit()
            return best_staff.staff_id, best_eta

        return None, 0
