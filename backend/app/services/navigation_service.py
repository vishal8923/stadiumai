from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from app.models.models import CrowdDataModel
from app.models.schemas import RouteResponse, AlternativeRoute
from app.utils.pathfinder import get_route_with_alternatives
from app.data.stadium_graph import STADIUM_NODES

class NavigationService:
    def __init__(self, db: Session):
        self.db = db

    def _get_current_crowd_densities(self) -> Dict[str, float]:
        """
        Fetch latest crowd densities for all zones to use for path weights.
        """
        # Get unique zones
        zone_ids = [z[0] for z in self.db.query(CrowdDataModel.zone_id).distinct().all()]
        
        crowd_levels = {}
        for zid in zone_ids:
            latest = self.db.query(CrowdDataModel).filter(
                CrowdDataModel.zone_id == zid
            ).order_by(desc(CrowdDataModel.timestamp)).first()
            if latest:
                crowd_levels[zid] = latest.current_density
                
        return crowd_levels

    def calculate_route(
        self,
        from_location: str,
        to_location: str,
        accessibility_mode: bool = False,
        avoid_crowds: bool = False
    ) -> RouteResponse:
        """
        Calculate routing using A* pathfinding.
        """
        # Validate locations exist in the graph
        if from_location not in STADIUM_NODES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Starting location '{from_location}' is not a valid node in the stadium graph."
            )
        if to_location not in STADIUM_NODES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Destination '{to_location}' is not a valid node in the stadium graph."
            )

        # Get crowd data
        crowd_levels = self._get_current_crowd_densities()

        # Run pathfinding
        route_info = get_route_with_alternatives(
            from_node=from_location,
            to_node=to_location,
            accessibility_mode=accessibility_mode,
            avoid_crowds=avoid_crowds,
            crowd_levels=crowd_levels
        )

        if not route_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No route found between '{from_location}' and '{to_location}'."
            )

        alt_routes = []
        for alt in route_info.get("alternative_routes", []):
            alt_routes.append(
                AlternativeRoute(
                    route=alt["route"],
                    estimated_time_minutes=alt["estimated_time_minutes"],
                    distance_meters=alt["distance_meters"],
                    crowd_score=alt["crowd_score"]
                )
            )

        return RouteResponse(
            route=route_info["route"],
            estimated_time_minutes=route_info["estimated_time_minutes"],
            distance_meters=route_info["distance_meters"],
            crowd_score=route_info["crowd_score"],
            alternative_routes=alt_routes,
            accessibility_notes=route_info.get("accessibility_notes")
        )
