from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schemas import NotificationResponse, MarkReadRequest, MarkReadResponse
from app.dependencies import get_db, general_rate_limit
from app.services.notification_service import NotificationService
from typing import Annotated

router = APIRouter(prefix="/api/v1", tags=["notifications"])

@router.get("/notifications/{user_id}", response_model=NotificationResponse, dependencies=[general_rate_limit])
def get_user_notifications_endpoint(user_id: str, db: Annotated[Session, Depends(get_db)]):
    """Retrieves list of priority push notifications sent to a specific user or staff session.
    Non-AI, works normally even if Gemini is disabled.
    """
    service = NotificationService(db)
    return service.get_user_notifications(user_id)

@router.post("/notifications/mark-read", response_model=MarkReadResponse, dependencies=[general_rate_limit])
def mark_user_notifications_read(request: MarkReadRequest, db: Annotated[Session, Depends(get_db)]):
    """Marks selected notifications as read.
    Non-AI, works normally even if Gemini is disabled.
    """
    service = NotificationService(db)
    updated_count = service.mark_notifications_read(request.notification_ids)
    return MarkReadResponse(updated_count=updated_count)
