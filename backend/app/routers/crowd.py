"""API endpoints for real-time crowd density heatmap and zone forecasts."""
import time
from contextlib import suppress
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schemas import CrowdZoneResponse, CrowdAllResponse
from app.dependencies import get_db, general_rate_limit
from app.services.crowd_service import CrowdService
from typing import Annotated

router = APIRouter(prefix="/api/v1", tags=["crowd"])

_last_purge_time: float = 0.0
_PURGE_INTERVAL: float = 600.0  # 10 minutes


@router.get("/crowd/all", response_model=CrowdAllResponse, dependencies=[general_rate_limit])
def get_all_crowd_data(db: Annotated[Session, Depends(get_db)]):
    """Get current crowd density and forecasts for all zones in the stadium.
    Used for Heatmap overlays. Purges stale data at most once per 10 minutes.
    """
    global _last_purge_time
    now = time.time()
    if now - _last_purge_time > _PURGE_INTERVAL:
        _last_purge_time = now
        with suppress(Exception):
            CrowdService(db).purge_old_data()
    return CrowdService(db).get_all_zones()


@router.get("/crowd/{zone_id}", response_model=CrowdZoneResponse, dependencies=[general_rate_limit])
def get_zone_crowd_data(zone_id: str, db: Annotated[Session, Depends(get_db)]):
    """Get detailed crowd density, risk level, predictions, and alternative exits/routes for a specific zone.
    """
    return CrowdService(db).get_zone_density(zone_id)
