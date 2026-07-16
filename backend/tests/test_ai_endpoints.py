"""test_ai_endpoints.py
====================
Integration/mock tests for endpoints relying on the Gemini AI layer:
  - POST /api/v1/chat/
  - POST /api/v1/translate/
  - POST /api/v1/incidents/

All calls to the LLMService (using Google Gemini API) are fully mocked out
to prevent network calls, ensure tests run fast and deterministically, and
prevent dependency on actual API quota.
"""

from unittest.mock import patch


@patch("app.services.llm_service.LLMService.execute_chat")
def test_chat_happy_path_mocked(mock_execute_chat, client):
    """POST /chat/ with mocked success response from LLMService."""
    from app.models.schemas import ChatResponse
    mock_execute_chat.return_value = ChatResponse(
        response_text="Hello! How can I help you at the World Cup today?",
        actions=[],
        route=None,
        crowd_alert=None,
        from_agent=True
    )

    response = client.post(
        "/api/v1/chat/",
        json={
            "message": "Hello",
            "user_id": "user_fan",
            "language": "en"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["response_text"] == "Hello! How can I help you at the World Cup today?"
    assert data["from_agent"] is True
    mock_execute_chat.assert_called_once()


@patch("app.services.llm_service.LLMService.execute_chat")
def test_chat_llm_service_error_graceful(mock_execute_chat, client):
    """POST /chat/ handles unexpected LLM timeout/error by returning 503 instead of crashing."""
    from fastapi import HTTPException
    mock_execute_chat.side_effect = HTTPException(status_code=503, detail="Gemini API chat session error: timeout")

    response = client.post("/api/v1/chat/", json={"message": "Help"})
    assert response.status_code == 503
    assert "timeout" in response.json()["detail"]


@patch("app.services.llm_service.LLMService.translate_text")
def test_translate_happy_path_mocked(mock_translate_text, client):
    """POST /translate/ with mocked success response."""
    mock_translate_text.return_value = {
        "translated_text": "Hola",
        "pronunciation_guide": "OH-lah",
        "cultural_note": "Common friendly greeting",
        "detected_source_lang": "en"
    }

    response = client.post(
        "/api/v1/translate/",
        json={
            "text": "Hello",
            "target_lang": "es"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["translated_text"] == "Hola"
    assert data["pronunciation_guide"] == "OH-lah"
    mock_translate_text.assert_called_once()


@patch("app.services.llm_service.LLMService.translate_text")
def test_translate_llm_service_error_graceful(mock_translate_text, client):
    """POST /translate/ handles translation exceptions by returning 503."""
    from fastapi import HTTPException
    mock_translate_text.side_effect = HTTPException(status_code=503, detail="Gemini API translation error: offline")

    response = client.post(
        "/api/v1/translate/",
        json={
            "text": "Hello",
            "target_lang": "es"
        }
    )
    assert response.status_code == 503
    assert "offline" in response.json()["detail"]


@patch("app.services.llm_service.LLMService.classify_incident_ai")
def test_incident_classification_happy_path_mocked(mock_classify, client):
    """POST /incidents/ with mocked AI classification."""
    mock_classify.return_value = {
        "type": "security",
        "priority": "high",
        "severity": "high"
    }

    response = client.post(
        "/api/v1/incidents/",
        json={
            "type": "security",
            "location": "gate_b",
            "description": "Suspicious luggage left at security screening",
            "severity": "medium",
            "user_id": "user_fan"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"].startswith("inc_")
    assert data["priority"] == "high"
    mock_classify.assert_called_once()


@patch("app.services.llm_service.LLMService.classify_incident_ai")
def test_incident_classification_llm_error_graceful(mock_classify, client):
    """POST /incidents/ handles classification failure by returning 503."""
    from fastapi import HTTPException
    mock_classify.side_effect = HTTPException(status_code=503, detail="Gemini API classification error: quota exceeded")

    response = client.post(
        "/api/v1/incidents/",
        json={
            "type": "medical",
            "location": "gate_a",
            "description": "Heart attack simulation"
        }
    )
    assert response.status_code == 503
    assert "quota exceeded" in response.json()["detail"]
