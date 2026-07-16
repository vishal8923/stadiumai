"""API endpoints for accessible infrastructure mapping and wait times."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import AccessibilityServiceModel
from app.models.schemas import AccessibilityResponse, AccessibilityServiceItem
from app.dependencies import get_db, general_rate_limit
from typing import Annotated

router = APIRouter(prefix="/api/v1", tags=["accessibility"])

@router.get("/accessibility/{service_type}", response_model=AccessibilityResponse, dependencies=[general_rate_limit])
def get_accessibility_services_endpoint(service_type: str, db: Annotated[Session, Depends(get_db)]):
    """Get operational availability and locations of accessible infrastructure (elevators, restrooms, ramps, wheelchair rentals).
    Non-AI, works normally even if Gemini is disabled.
    """
    # Query database for units matching type
    services = db.query(AccessibilityServiceModel).filter(
        AccessibilityServiceModel.service_type == service_type,
    ).all()

    if not services:
        # Fallback to general lookup
        services = db.query(AccessibilityServiceModel).all()

    if not services:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Accessibility service type '{service_type}' not found.",
        )

    service_items = []
    for s in services:
        service_items.append(
            AccessibilityServiceItem(
                id=s.id,
                service_type=s.service_type,
                location=s.location,
                status=s.status,
                wait_time_minutes=s.wait_time_minutes,
            ),
        )

    # Prioritize operational units with minimal wait times
    operational_units = [item for item in service_items if item.status == "operational"]
    operational_units.sort(key=lambda x: x.wait_time_minutes)

    if operational_units:
        nearest = operational_units[0]
        wait_time = nearest.wait_time_minutes
    else:
        # Fallback if no operational units are present
        nearest = service_items[0]
        wait_time = 0

    return AccessibilityResponse(
        services=service_items,
        nearest=nearest,
        wait_time_minutes=wait_time,
    )
