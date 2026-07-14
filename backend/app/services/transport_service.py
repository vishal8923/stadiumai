from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status
from app.models.models import TransportModel
from app.models.schemas import TransportResponse, TransportOption

class TransportService:
    def __init__(self, db: Session):
        self.db = db

    def get_options(self, location: str, destination: Optional[str] = None, mode: Optional[str] = None) -> TransportResponse:
        """
        Retrieves transport options based on location, destination, and mode.
        """
        query = self.db.query(TransportModel)
        
        # Apply filters if provided
        # Since we use mock data, we match location loosely or return all options starting near the gates
        if location:
            # Check if location matches a gate, e.g. gate_a -> match gate or "Stadium"
            query = query.filter(
                (TransportModel.location.ilike(f"%{location}%")) | 
                (TransportModel.location.ilike("%stadium%"))
            )
            
        if destination:
            query = query.filter(TransportModel.destination.ilike(f"%{destination}%"))
            
        if mode:
            query = query.filter(TransportModel.mode.ilike(f"%{mode}%"))

        options = query.all()

        # If no options found, return all available options as a fallback
        if not options:
            options = self.db.query(TransportModel).all()

        if not options:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No transport options found for the specified route."
            )

        # Convert to Pydantic objects
        option_list = []
        for opt in options:
            option_list.append(
                TransportOption(
                    id=opt.id,
                    mode=opt.mode,
                    destination=opt.destination,
                    eta_minutes=opt.eta_minutes,
                    recommendation_score=opt.recommendation_score,
                    details=opt.details
                )
            )

        # Sort options by recommendation score descending
        option_list.sort(key=lambda x: -x.recommendation_score)

        # Best recommendation is the top scored option
        recommendation = option_list[0]
        
        # Determine average traffic level
        traffic_levels = [o.traffic_level for o in options]
        if "heavy" in traffic_levels:
            traffic_level = "heavy"
        elif "moderate" in traffic_levels:
            traffic_level = "moderate"
        else:
            traffic_level = "light"

        return TransportResponse(
            options=option_list,
            recommendation=recommendation,
            traffic_level=traffic_level
        )
