import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import MatchModel
from app.models.schemas import MatchResponse
from app.dependencies import get_db, general_rate_limit
from typing import Annotated

router = APIRouter(prefix="/api/v1", tags=["match"])

def map_match_to_response(match: MatchModel) -> MatchResponse:
    try:
        timeline = json.loads(match.timeline) if match.timeline else []
    except (json.JSONDecodeError, TypeError):
        timeline = []

    try:
        stats = json.loads(match.stats) if match.stats else {
            "possession_a": 50, "possession_b": 50,
            "shots_a": 0, "shots_b": 0,
            "fouls_a": 0, "fouls_b": 0,
        }
    except (json.JSONDecodeError, TypeError):
        stats = {
            "possession_a": 50, "possession_b": 50,
            "shots_a": 0, "shots_b": 0,
            "fouls_a": 0, "fouls_b": 0,
        }

    return MatchResponse(
        id=match.id,
        team_a=match.team_a,
        team_b=match.team_b,
        score_a=match.score_a,
        score_b=match.score_b,
        status=match.status,
        stadium=match.stadium,
        kickoff_time=match.kickoff_time,
        timeline=timeline,
        stats=stats,
    )

@router.get("/match/current", response_model=MatchResponse, dependencies=[general_rate_limit])
def get_current_live_match(db: Annotated[Session, Depends(get_db)]):
    """Get current live match timeline and statistics.
    Non-AI, works normally even if Gemini is disabled.
    """
    # Fetch live match (first match with status 'live')
    match = db.query(MatchModel).filter(MatchModel.status == "live").first()
    if not match:
        # Fallback to any match
        match = db.query(MatchModel).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No match is currently scheduled or live.",
        )
    return map_match_to_response(match)

@router.get("/match/{match_id}", response_model=MatchResponse, dependencies=[general_rate_limit])
def get_match_details(match_id: str, db: Annotated[Session, Depends(get_db)]):
    """Get stats and events list of a specific match by ID.
    Non-AI, works normally even if Gemini is disabled.
    """
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID '{match_id}' not found.",
        )
    return map_match_to_response(match)
