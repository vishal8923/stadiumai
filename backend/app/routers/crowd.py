from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.schemas import CrowdZoneResponse, CrowdAllResponse
from app.dependencies import get_db, general_rate_limit
from app.services.crowd_service import CrowdService

router = APIRouter(prefix="/api/v1", tags=["crowd"])

@router.get("/crowd/all", response_model=CrowdAllResponse, dependencies=[general_rate_limit])
def get_all_crowd_data(db: Session = Depends(get_db)):
    """
    Get current crowd density and forecasts for all zones in the stadium.
    Used for Heatmap overlays.
    """
    service = CrowdService(db)
    # Purge old data while querying
    service.purge_old_data()
    return service.get_all_zones()

@router.get("/crowd/{zone_id}", response_model=CrowdZoneResponse, dependencies=[general_rate_limit])
def get_zone_crowd_data(zone_id: str, db: Session = Depends(get_db)):
    """
    Get detailed crowd density, risk level, predictions, and alternative exits/routes for a specific zone.
    """
    service = CrowdService(db)
    return service.get_zone_density(zone_id)
