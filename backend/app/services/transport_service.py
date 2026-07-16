from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import TransportModel
from app.models.schemas import TransportResponse, TransportOption

class TransportService:
    def __init__(self, db: Session):
        self.db = db

    def get_options(self, location: str, destination: str | None = None, mode: str | None = None) -> TransportResponse:
        query = self.db.query(TransportModel)

        if location:
            query = query.filter(
                (TransportModel.location.ilike(f"%{location}%"))
                | (TransportModel.location.ilike("%stadium%")),
            )

        if destination:
            query = query.filter(TransportModel.destination.ilike(f"%{destination}%"))

        if mode:
            query = query.filter(TransportModel.mode.ilike(f"%{mode}%"))

        options = query.all()

        if not options:
            options = self.db.query(TransportModel).all()

        if not options:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No transport options found for the specified route.",
            )

        option_list = [
            TransportOption(
                id=opt.id,
                mode=opt.mode,
                destination=opt.destination,
                eta_minutes=opt.eta_minutes,
                recommendation_score=opt.recommendation_score,
                details=opt.details,
            )
            for opt in options
        ]

        option_list.sort(key=lambda x: -x.recommendation_score)

        recommendation = option_list[0]
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
            traffic_level=traffic_level,
        )
