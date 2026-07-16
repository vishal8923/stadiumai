import uuid
import json
import datetime
from contextlib import suppress
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.models.models import UserModel, ConversationModel
from app.models.schemas import UserSessionResponse, UserHistoryResponse, ConversationItem, Action
from app.dependencies import get_db, general_rate_limit
from typing import Annotated

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/session", response_model=UserSessionResponse, dependencies=[general_rate_limit])
def create_user_session(db: Annotated[Session, Depends(get_db)]):
    """Creates an anonymous fan user session in the database.
    Non-AI, works normally even if Gemini is disabled.
    """
    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    created_at = datetime.datetime.now(datetime.timezone.utc)

    user = UserModel(
        user_id=user_id,
        created_at=created_at,
        role="fan",
        language="en",
        accessibility_mode=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserSessionResponse(
        user_id=user.user_id,
        created_at=user.created_at.isoformat(),
    )

@router.get("/{user_id}/history", response_model=UserHistoryResponse, dependencies=[general_rate_limit])
def get_user_chat_history(
    db: Annotated[Session, Depends(get_db)],
    user_id: str,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Retrieves previous chat message logs and intents for a specific user session.
    Non-AI, works normally even if Gemini is disabled.
    """
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User session '{user_id}' not found.",
        )

    conversations = db.query(ConversationModel).filter(
        ConversationModel.user_id == user_id,
    ).order_by(ConversationModel.timestamp.asc()).offset(offset).limit(limit).all()

    items = []
    for c in conversations:
        actions_list = []
        if c.actions:
            with suppress(json.JSONDecodeError, TypeError):
                raw_actions = json.loads(c.actions)
                for act in raw_actions:
                    actions_list.append(
                        Action(type=act.get("type", ""), payload=act.get("payload", {})),
                    )

        items.append(
            ConversationItem(
                role=c.role,
                message=c.message,
                intent=c.intent,
                actions=actions_list,
                timestamp=c.timestamp.isoformat(),
            ),
        )

    return UserHistoryResponse(
        conversations=items,
        total=len(items),
    )
