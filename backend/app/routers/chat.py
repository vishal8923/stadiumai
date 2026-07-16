"""API endpoint for the GenAI conversational assistant concierge."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schemas import ChatRequest, ChatResponse
from app.dependencies import get_db, chat_rate_limit
from app.services.llm_service import LLMService
from typing import Annotated

router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponse, dependencies=[chat_rate_limit])
def chat_concierge(request: ChatRequest, db: Annotated[Session, Depends(get_db)]):
    """Main GenAI concierge endpoint. Uses Google Gemini API.
    Returns HTTP 503 if GEMINI_API_KEY is not configured or is invalid.
    """
    user_id = request.user_id or "anonymous_user"

    # Initialize and call LLM Service
    llm = LLMService(db)

    # Execute the request (real Gemini)
    return llm.execute_chat(
        user_id=user_id,
        message=request.message,
        location=request.location,
        accessibility_mode=request.accessibility_mode or False,
    )

