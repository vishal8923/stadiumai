import uuid
import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import UserModel, ConversationModel
from app.models.schemas import UserSessionResponse, UserHistoryResponse, ConversationItem, Action
from app.dependencies import get_db, general_rate_limit

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/session", response_model=UserSessionResponse, dependencies=[general_rate_limit])
def create_user_session(db: Session = Depends(get_db)):
    """
    Creates an anonymous fan user session in the database.
    Non-AI, works normally even if Gemini is disabled.
    """
    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    created_at = datetime.datetime.utcnow()
    
    user = UserModel(
        user_id=user_id,
        created_at=created_at,
        role="fan",
        language="en",
        accessibility_mode=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserSessionResponse(
        user_id=user.user_id,
        created_at=user.created_at.isoformat()
    )

@router.get("/{user_id}/history", response_model=UserHistoryResponse, dependencies=[general_rate_limit])
def get_user_chat_history(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieves previous chat message logs and intents for a specific user session.
    Non-AI, works normally even if Gemini is disabled.
    """
    # Verify user exists
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User session '{user_id}' not found."
        )

    conversations = db.query(ConversationModel).filter(
        ConversationModel.user_id == user_id
    ).order_by(ConversationModel.timestamp.asc()).all()

    items = []
    for c in conversations:
        actions_list = []
        if c.actions:
            try:
                raw_actions = json.loads(c.actions)
                for act in raw_actions:
                    actions_list.append(
                        Action(type=act.get("type", ""), payload=act.get("payload", {}))
                    )
            except Exception:
                pass
                
        items.append(
            ConversationItem(
                role=c.role,
                message=c.message,
                intent=c.intent,
                actions=actions_list,
                timestamp=c.timestamp.isoformat()
            )
        )

    return UserHistoryResponse(
        conversations=items,
        total=len(items)
    )
