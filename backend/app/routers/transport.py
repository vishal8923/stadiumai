from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.schemas import TransportResponse
from app.dependencies import get_db, general_rate_limit
from app.services.transport_service import TransportService
from typing import Annotated

router = APIRouter(prefix="/api/v1", tags=["transport"])

@router.get("/transport", response_model=TransportResponse, dependencies=[general_rate_limit])
def get_transit_options(
    location: Annotated[str, Query(description="Starting gate or zone in/around stadium")],
    destination: Annotated[str | None, Query(description="End point (e.g. Parking Lot B, Downtown)")] = None,
    mode: Annotated[str | None, Query(description="Transport mode (Metro, Shuttle, Bus, Taxi)")] = None,
    db: Session = Depends(get_db),
):
    """Get transportation options with ETAs, recommendations, and traffic levels.
    Non-AI, works normally even if Gemini is disabled.
    """
    service = TransportService(db)
    return service.get_options(location=location, destination=destination, mode=mode)
