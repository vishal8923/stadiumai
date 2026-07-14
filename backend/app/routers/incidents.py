from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.schemas import IncidentRequest, IncidentResponse, IncidentDetailResponse
from app.dependencies import get_db, incident_rate_limit, general_rate_limit
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/api/v1", tags=["incidents"])

@router.post("/incidents", response_model=IncidentResponse, dependencies=[incident_rate_limit])
def report_new_incident(request: IncidentRequest, db: Session = Depends(get_db)):
    """
    Submits a new security or medical incident report.
    This uses Gemini AI auto-classification of priority and type.
    Requires GEMINI_API_KEY - returns HTTP 503 Service Unavailable if it's missing or invalid.
    """
    service = IncidentService(db)
    response = service.report_incident(
        type_param=request.type,
        location=request.location,
        description=request.description,
        severity_param=request.severity or "medium",
        reporter_id=request.reporter_id
    )
    return response

@router.get("/incidents/{incident_id}", response_model=IncidentDetailResponse, dependencies=[general_rate_limit])
def get_incident_details(incident_id: str, db: Session = Depends(get_db)):
    """
    Gets detailed information of a reported incident.
    Non-AI, works normally even if Gemini is disabled.
    """
    service = IncidentService(db)
    return service.get_incident(incident_id)
