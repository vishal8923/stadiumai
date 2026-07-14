from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.schemas import TranslateRequest, TranslateResponse
from app.dependencies import get_db, general_rate_limit
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/v1", tags=["translate"])

@router.post("/translate", response_model=TranslateResponse, dependencies=[general_rate_limit])
def translate_assistance_text(request: TranslateRequest, db: Session = Depends(get_db)):
    """
    Translates fan queries or staff directives with cultural context using Google Gemini.
    Requires GEMINI_API_KEY - returns HTTP 503 if the key is missing or invalid.
    """
    llm = LLMService(db)
    result = llm.translate_text(
        text=request.text,
        target_lang=request.target_lang,
        source_lang=request.source_lang,
        context=request.context
    )
    
    return TranslateResponse(
        translated_text=result.get("translated_text", ""),
        pronunciation_guide=result.get("pronunciation_guide"),
        cultural_note=result.get("cultural_note"),
        detected_source_lang=result.get("detected_source_lang")
    )
