from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.schemas import NavigateRequest, RouteResponse
from app.dependencies import get_db, navigation_rate_limit
from app.services.navigation_service import NavigationService

router = APIRouter(prefix="/api/v1", tags=["navigation"])

@router.post("/navigate", response_model=RouteResponse, dependencies=[navigation_rate_limit])
def navigate_stadium(request: NavigateRequest, db: Session = Depends(get_db)):
    """
    Computes optimal pathfinding on the stadium layout using A* algorithm.
    Intentionally rule-based and non-AI, works normally even if Gemini is disabled.
    """
    service = NavigationService(db)
    response = service.calculate_route(
        from_location=request.from_location,
        to_location=request.to_location,
        accessibility_mode=request.accessibility_mode or False,
        avoid_crowds=request.avoid_crowds or False
    )
    return response
