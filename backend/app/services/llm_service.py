"""LLM service for Gemini AI integration: chat, translation, and incident classification."""

from __future__ import annotations

import json
import time
import logging
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.schemas import (
    Action,
    AccessibilityResponse,
    AccessibilityServiceItem,
    ChatResponse,
    CrowdAlert,
    MatchResponse,
    WasteRequest,
)
from app.models.models import AccessibilityServiceModel, ConversationModel, MatchModel

logger = logging.getLogger("stadium_ai")

MAX_RETRIES = 2
RETRY_BACKOFF = 1.0
GEMINI_TIMEOUT = 30


def check_gemini_configured() -> bool:
    """Check if Gemini API key and model are configured; log warnings if missing."""
    api_key = settings.GEMINI_API_KEY.strip()
    model_name = settings.GEMINI_MODEL.strip()
    if not api_key:
        logger.warning("WARNING: GEMINI_API_KEY is not configured. AI features will return HTTP 503.")
        return False
    if not model_name:
        logger.warning("WARNING: GEMINI_MODEL is not configured. AI features will return HTTP 503.")
        return False
    return True


check_gemini_configured()


class LLMService:
    """Service layer for Google Gemini AI chat, translation, and incident classification.

    Encapsulates all Gemini interactions:
    - execute_chat: full conversational concierge with tool calling
    - translate_text: multilingual translation with cultural context
    - classify_incident_ai: incident report classification

    Each public method returns structured Pydantic models or dicts ready for serialisation.
    """

    def __init__(self, db: Session) -> None:
        """Initialise the service with a database session.

        Args:
            db: Active SQLAlchemy database session.
        """
        self.db = db

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call_gemini_with_retry(
        self,
        genai: Any,
        model_name: str,
        contents: list[Any],
        *,
        temperature: float = 0.5,
        max_retries: int = MAX_RETRIES,
    ) -> tuple[Any, float]:
        """Call Gemini with automatic retry on transient failures.

        Args:
            genai: The configured google.generativeai module.
            model_name: The Gemini model identifier.
            contents: The content list to send.
            temperature: Sampling temperature.
            max_retries: Maximum number of attempts.

        Returns:
            Tuple of (response_object, latency_ms).

        Raises:
            HTTPException 503: If all retries are exhausted.
        """
        import google.generativeai as genai_mod

        model = genai_mod.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": temperature,
                "response_mime_type": "application/json",
            },
        )

        last_error: Exception | None = None
        for attempt in range(max_retries):
            start = time.time()
            try:
                response = model.generate_content(contents)
                latency_ms = (time.time() - start) * 1000
                logger.info(
                    "gemini.call success model=%s attempt=%d latency=%.1fms",
                    model_name,
                    attempt + 1,
                    latency_ms,
                )
                return response, latency_ms
            except Exception as exc:
                latency_ms = (time.time() - start) * 1000
                last_error = exc
                logger.warning(
                    "gemini.call failed model=%s attempt=%d/%d latency=%.1fms error=%s",
                    model_name,
                    attempt + 1,
                    max_retries,
                    latency_ms,
                    exc,
                )
                if attempt < max_retries - 1:
                    time.sleep(RETRY_BACKOFF * (attempt + 1))

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Gemini API failed after {max_retries} attempts: {last_error!s}",
        ) from last_error

    def _get_api_client(self) -> tuple[Any, str]:
        """Dynamically load the API key / model name and return a (genai, model_name) tuple.

        Raises HTTP 503 if the API key or model name is missing or if initialisation fails.
        """
        api_key = settings.GEMINI_API_KEY.strip()
        model_name = settings.GEMINI_MODEL.strip()

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini API key is not configured. AI features are disabled.",
            )
        if not model_name:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini model (GEMINI_MODEL) is not configured in the environment.",
            )

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            return genai, model_name
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to initialize Gemini API client: {exc!s}",
            ) from exc

    def _load_conversation_history(self, user_id: str) -> list[ConversationModel]:
        """Retrieve the last 20 conversation entries for the given user, ordered chronologically.

        Args:
            user_id: Unique user identifier.

        Returns:
            List of ConversationModel rows in chronological order.
        """
        history: list[ConversationModel] = (
            self.db.query(ConversationModel)
            .filter(ConversationModel.user_id == user_id)
            .order_by(ConversationModel.timestamp.desc())
            .limit(20)
            .all()
        )
        history.reverse()
        return history

    def _build_system_instructions(self) -> str:
        """Return the system-level instructions prompt for the StadiumAI concierge.

        Returns:
            A string containing the system prompt with tool-use rules.
        """
        return (
            "You are StadiumAI, the official AI concierge for FIFA World Cup 2026. "
            "You have real-time access to stadium operations data, crowd analytics, navigation systems, and multilingual capabilities.\n"
            "Your personality is helpful, energetic, and culturally aware. Speak in the user's language.\n"
            "RULES:\n"
            "1. Keep responses concise (max 3 sentences) for mobile readability.\n"
            "2. When asked for directions or navigation, use get_directions.\n"
            "3. When asked about crowd density or traffic, use get_crowd_density.\n"
            "4. When asked about match stats or live score, use get_match_info.\n"
            "5. If a safety incident is reported, use create_incident.\n"
            "6. For waste disposal, use classify_waste.\n"
            "7. If they need accessibility services, use get_accessibility_info.\n"
            "8. Combine navigation + crowd data to recommend food or exits.\n"
            "IMPORTANT: Return output strictly as a JSON object containing the keys:\n"
            "- response_text (string explanation for the user)\n"
            "- action_type (string corresponding to action taken: 'navigation', 'incident_reported', 'transport', 'sustainability', 'crowd_alert', 'match_stats', 'none')\n"
            "- action_payload (dict containing metadata returned by function calls)\n"
        )

    def _build_chat_contents(
        self,
        user_id: str,
        message: str,
        location: str | None,
        accessibility_mode: bool,
    ) -> list[dict[str, Any]]:
        """Construct the message array sent to Gemini.

        Args:
            user_id: Current user identifier.
            message: The user's latest text message.
            location: Optional location string.
            accessibility_mode: Whether accessibility mode is active.

        Returns:
            A list of dicts with ``role`` and ``parts`` keys for the Gemini API.
        """
        contents: list[dict[str, Any]] = [
            {"role": "user", "parts": [self._build_system_instructions()]},
            {
                "role": "model",
                "parts": ["Understood. I will act as StadiumAI and output JSON responses based on these instructions."],
            },
        ]

        for entry in self._load_conversation_history(user_id):
            role = "user" if entry.role == "user" else "model"
            contents.append({"role": role, "parts": [entry.message]})

        current_prompt = (
            f"User Location: {location or 'unknown'}\n"
            f"Accessibility Mode Enabled: {accessibility_mode}\n"
            f"Message: {message}"
        )
        contents.append({"role": "user", "parts": [current_prompt]})
        return contents

    def _persist_conversation(
        self,
        user_id: str,
        user_message: str,
        response_text: str,
        action_type: str,
        actions: list[Action],
    ) -> None:
        """Save the user message and AI response to the conversation history table.

        Args:
            user_id: Current user identifier.
            user_message: The original user message text.
            response_text: The AI response text.
            action_type: The action type returned by Gemini.
            actions: Full list of Action objects captured during the turn.
        """
        user_entry = ConversationModel(
            user_id=user_id,
            role="user",
            message=user_message,
            timestamp=None,
        )
        ai_entry = ConversationModel(
            user_id=user_id,
            role="assistant",
            message=response_text,
            intent=action_type,
            actions=json.dumps([a.model_dump() for a in actions]),
            timestamp=None,
        )
        self.db.add(user_entry)
        self.db.add(ai_entry)
        self.db.commit()

    def _parse_chat_response(
        self,
        raw_text: str,
        context_store: dict[str, Any],
    ) -> ChatResponse:
        """Parse the raw JSON from Gemini into a structured ChatResponse.

        Args:
            raw_text: Raw response text from Gemini.
            context_store: Mutable dict holding route, crowd_alert, and actions collected
                           during tool execution.

        Returns:
            A populated ChatResponse ready for serialisation.
        """
        parsed = json.loads(raw_text)
        response_text: str = parsed.get(
            "response_text",
            "I'm sorry, I encountered an issue parsing the response.",
        )
        action_type: str = parsed.get("action_type", "none")
        action_payload: dict[str, Any] = parsed.get("action_payload", {})

        if action_type != "none" and not context_store["actions"]:
            context_store["actions"].append(Action(type=action_type, payload=action_payload))

        return ChatResponse(
            response_text=response_text,
            actions=context_store["actions"],
            route=context_store["route_response"],
            crowd_alert=context_store["crowd_alert"],
            from_agent=True,
        )

    # ------------------------------------------------------------------
    # Tool implementations (called by Gemini via function calling)
    # ------------------------------------------------------------------

    def _tool_get_directions(
        self,
        from_location: str,
        to_location: str,
        accessibility_mode: bool,
    ) -> str:
        """Calculate the optimal path/directions between two points in the stadium.

        Args:
            from_location: Starting node ID (e.g. gate_a, sec_5).
            to_location: Ending node ID (e.g. food_court_north, sec_10).
            accessibility_mode: Whether to prefer accessible routes.

        Returns:
            JSON string of the route result.
        """
        from app.services.navigation_service import NavigationService

        nav = NavigationService(self.db)
        try:
            res = nav.calculate_route(from_location, to_location, accessibility_mode, True)
            return json.dumps(res)
        except (TypeError, ValueError, SQLAlchemyError) as exc:
            return f"Error computing directions: {exc!s}"

    def _tool_get_crowd_density(
        self,
        zone_id: str,
        context_store: dict[str, Any],
    ) -> str:
        """Get the current crowd density level and safety risk for a zone.

        Args:
            zone_id: The zone or gate ID (e.g. zone_gate_a, zone_concourse_1).
            context_store: Mutable context dict for side-effects (crowd alerts).

        Returns:
            JSON string of the crowd density result.
        """
        from app.services.crowd_service import CrowdService

        crowd = CrowdService(self.db)
        try:
            res = crowd.get_zone_density(zone_id)
            if res.level in {"high", "critical"}:
                context_store["crowd_alert"] = CrowdAlert(
                    zone_id=res.zone_id,
                    density=res.current_density,
                    level=res.level,
                    message=f"High crowd levels detected in {res.zone_id}. Avoid this area if possible.",
                )
            return json.dumps(res.model_dump())
        except (TypeError, ValueError, SQLAlchemyError) as exc:
            return f"Error retrieving crowd density: {exc!s}"

    def _tool_get_transport_options(
        self,
        location: str,
        destination: str | None,
        mode: str | None,
        context_store: dict[str, Any],
    ) -> str:
        """Get transport options, departure times, traffic levels, and recommended modes.

        Args:
            location: Current location or stadium gate.
            destination: Where the user wants to go (optional).
            mode: Transport mode (bus, metro, shuttle, taxi) (optional).
            context_store: Mutable context dict for side-effects (action list).

        Returns:
            JSON string of transport options.
        """
        from app.services.transport_service import TransportService

        ts = TransportService(self.db)
        try:
            res = ts.get_options(location, destination, mode)
            context_store["actions"].append(Action(type="transport", payload=res.model_dump()))
            return json.dumps(res.model_dump())
        except (TypeError, ValueError, SQLAlchemyError) as exc:
            return f"Error checking transport options: {exc!s}"

    def _tool_classify_waste(
        self,
        item_description: str,
        location: str | None,
        context_store: dict[str, Any],
    ) -> str:
        """Classify waste item as recycling, compost, or landfill and locate nearest bin.

        Args:
            item_description: Name of item to discard (e.g. plastic cup, banana peel).
            location: User's current location (optional).
            context_store: Mutable context dict for side-effects (action list).

        Returns:
            JSON string of waste classification result.
        """
        from app.routers.sustainability import classify_waste_item

        try:
            req = WasteRequest(item_description=item_description, location=location)
            res = classify_waste_item(req, location)
            context_store["actions"].append(Action(type="sustainability", payload=res.model_dump()))
            return json.dumps(res.model_dump())
        except (TypeError, ValueError, SQLAlchemyError) as exc:
            return f"Error classifying waste: {exc!s}"

    def _tool_create_incident(
        self,
        incident_type: str,
        location: str,
        description: str,
        severity: str,
        user_id: str,
        context_store: dict[str, Any],
    ) -> str:
        """Report an active security, medical, or fire incident to stadium dispatchers.

        Args:
            incident_type: medical, fire, security, lost_person, infrastructure.
            location: Location of incident.
            description: Details about what happened.
            severity: low, medium, high, critical.
            user_id: Reporting user identifier.
            context_store: Mutable context dict for side-effects (action list).

        Returns:
            JSON string of incident creation result.
        """
        from app.services.incident_service import IncidentService

        iserv = IncidentService(self.db)
        try:
            res = iserv.report_incident(incident_type, location, description, severity, user_id)
            context_store["actions"].append(Action(type="incident_reported", payload=res.model_dump()))
            return json.dumps(res.model_dump())
        except (TypeError, ValueError, SQLAlchemyError) as exc:
            return f"Error submitting incident: {exc!s}"

    def _tool_get_accessibility_info(
        self,
        service_type: str,
        context_store: dict[str, Any],
    ) -> str:
        """Get details and wait times for accessible units (elevators, restrooms, companion aid).

        Args:
            service_type: elevator, ramp, restroom, hearing_loop, wheelchair_rental.
            context_store: Mutable context dict for side-effects (action list).

        Returns:
            JSON string of accessibility service information.
        """
        try:
            services: list[AccessibilityServiceModel] = (
                self.db.query(AccessibilityServiceModel)
                .filter(AccessibilityServiceModel.service_type == service_type)
                .all()
            )
            if not services:
                services = self.db.query(AccessibilityServiceModel).all()
            if not services:
                return json.dumps({"error": f"Service type '{service_type}' not found"})

            items = [
                AccessibilityServiceItem(
                    id=s.id,
                    service_type=s.service_type,
                    location=s.location,
                    status=s.status,
                    wait_time_minutes=s.wait_time_minutes,
                )
                for s in services
            ]
            operational = sorted(
                [i for i in items if i.status == "operational"],
                key=lambda x: x.wait_time_minutes,
            )
            nearest = operational[0] if operational else items[0]
            wait_time = nearest.wait_time_minutes if operational else 0

            result = AccessibilityResponse(services=items, nearest=nearest, wait_time_minutes=wait_time)
            context_store["actions"].append(Action(type="accessibility", payload=result.model_dump()))
            return json.dumps(result.model_dump())
        except (TypeError, ValueError, SQLAlchemyError) as exc:
            return f"Error retrieving accessibility: {exc!s}"

    def _tool_get_match_info(
        self,
        match_id: str,
        context_store: dict[str, Any],
    ) -> str:
        """Get match score, status, timelines, or stats.

        Args:
            match_id: ID of the match, or 'current' for the active live match.
            context_store: Mutable context dict for side-effects (action list).

        Returns:
            JSON string of match information.
        """
        try:
            if match_id == "current":
                match = self.db.query(MatchModel).filter(MatchModel.status == "live").first()
                if not match:
                    match = self.db.query(MatchModel).first()
            else:
                match = self.db.query(MatchModel).filter(MatchModel.id == match_id).first()

            if not match:
                return json.dumps({"error": "No match found"})

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

            result = MatchResponse(
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
            context_store["actions"].append(Action(type="match_stats", payload=result.model_dump()))
            return json.dumps(result.model_dump())
        except (TypeError, ValueError, SQLAlchemyError) as exc:
            return f"Error checking match details: {exc!s}"

    # ------------------------------------------------------------------
    # Tool registry
    # ------------------------------------------------------------------

    def _register_tools(
        self,
        context_store: dict[str, Any],
        accessibility_mode: bool,
        user_id: str,
    ) -> list[Any]:
        """Build and return the list of callable tool functions for Gemini function calling.

        Each tool wraps a ``_tool_*`` method with the correct closure over context_store
        and other runtime parameters so Gemini can call them transparently.

        Args:
            context_store: Shared mutable dict for side-effects during tool execution.
            accessibility_mode: Whether accessibility mode is active (passed to navigation).
            user_id: Current user identifier (passed to incident reporting).

        Returns:
            A list of callables suitable as ``tools`` for ``GenerativeModel``.
        """

        def get_directions(from_location: str, to_location: str) -> str:
            return self._tool_get_directions(from_location, to_location, accessibility_mode)

        def get_crowd_density(zone_id: str) -> str:
            return self._tool_get_crowd_density(zone_id, context_store)

        def get_transport_options(location: str, destination: str | None = None, mode: str | None = None) -> str:
            return self._tool_get_transport_options(location, destination, mode, context_store)

        def classify_waste(item_description: str, location: str | None = None) -> str:
            return self._tool_classify_waste(item_description, location, context_store)

        def create_incident(type: str, location: str, description: str, severity: str = "medium") -> str:
            return self._tool_create_incident(type, location, description, severity, user_id, context_store)

        def get_accessibility_info(service_type: str) -> str:
            return self._tool_get_accessibility_info(service_type, context_store)

        def get_match_info(match_id: str = "current") -> str:
            return self._tool_get_match_info(match_id, context_store)

        return [
            get_directions,
            get_crowd_density,
            get_transport_options,
            classify_waste,
            create_incident,
            get_accessibility_info,
            get_match_info,
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def translate_text(
        self,
        text: str,
        target_lang: str,
        source_lang: str | None = None,
        context: str | None = None,
    ) -> dict[str, Any]:
        """Translate text with cultural context using the real Gemini API.

        Args:
            text: The source text to translate.
            target_lang: Target language code (e.g. 'es', 'fr').
            source_lang: Optional source language hint.
            context: Optional context/setting for the translation.

        Returns:
            A dict with keys ``translated_text``, ``pronunciation_guide``,
            ``cultural_note``, and ``detected_source_lang``.

        Raises:
            HTTPException 503: If the Gemini API call fails after retries.
        """
        genai, model_name = self._get_api_client()

        system_prompt = (
            "You are a professional multilingual translator for the FIFA World Cup 2026. "
            "Translate the input text accurately to the target language. "
            "You must return the output STRICTLY as a JSON object with these keys:\n"
            "- translated_text (string)\n"
            "- pronunciation_guide (string or null)\n"
            "- cultural_note (string or null, e.g. football slang, local customs if applicable)\n"
            "- detected_source_lang (string)\n\n"
            "Do not include any markdown fences or explanations outside the JSON."
        )

        user_content = f"Text to translate: '{text}'\nTarget Language: {target_lang}"
        if source_lang:
            user_content += f"\nSource Language (implied): {source_lang}"
        if context:
            user_content += f"\nContext/Setting: {context}"

        response, _latency = self._call_gemini_with_retry(
            genai, model_name, [system_prompt, user_content], temperature=0.3,
        )
        return json.loads(response.text.strip())

    def classify_incident_ai(self, description: str) -> dict[str, Any]:
        """Classify a reported incident using the Gemini API.

        Args:
            description: Free-text description of the incident.

        Returns:
            A dict with keys ``type``, ``priority``, ``severity``, and ``response_urgency``.

        Raises:
            HTTPException 503: If the Gemini API call fails after retries.
        """
        genai, model_name = self._get_api_client()

        system_prompt = (
            "You are an AI dispatcher for FIFA World Cup 2026 stadium security. "
            "Analyze the incident report description and return a JSON object with these fields:\n"
            "- type (one of: 'medical', 'fire', 'security', 'lost_person', 'infrastructure')\n"
            "- priority (one of: 'low', 'medium', 'high', 'critical')\n"
            "- severity (one of: 'low', 'medium', 'high', 'critical')\n"
            "- response_urgency (string description)\n\n"
            "Do not include any explanation outside the JSON."
        )

        response, _latency = self._call_gemini_with_retry(
            genai, model_name,
            [system_prompt, f"Incident report: '{description}'"],
            temperature=0.2,
        )
        return json.loads(response.text.strip())

    def execute_chat(
        self,
        user_id: str,
        message: str,
        location: str | None = None,
        accessibility_mode: bool = False,
    ) -> ChatResponse:
        """Orchestrate an AI chat concierge session using the Gemini API.

        Loads conversation history from the database, builds a prompt with tool
        definitions, calls Gemini (which may invoke zero or more tools), and persists
        both the user message and AI response.

        Args:
            user_id: Unique user identifier.
            message: The user's current chat message.
            location: Optional current location within the stadium.
            accessibility_mode: Whether the user has requested accessibility features.

        Returns:
            A ChatResponse containing the AI response text, any tool-generated
            actions, route data, and crowd alerts.

        Raises:
            HTTPException 503: If the Gemini API call or response parsing fails.
        """
        genai, model_name = self._get_api_client()

        context_store: dict[str, Any] = {
            "route_response": None,
            "crowd_alert": None,
            "actions": [],
        }

        chat_contents = self._build_chat_contents(user_id, message, location, accessibility_mode)
        registered_tools = self._register_tools(context_store, accessibility_mode, user_id)

        import google.generativeai as genai_mod

        model = genai_mod.GenerativeModel(
            model_name=model_name,
            tools=registered_tools,
            generation_config={
                "temperature": 0.5,
                "response_mime_type": "application/json",
            },
        )

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                chat = model.start_chat(enable_automatic_function_calling=True)
                start = time.time()
                response = chat.send_message(chat_contents[-1]["parts"][0])
                latency_ms = (time.time() - start) * 1000

                logger.info(
                    "gemini.chat success model=%s attempt=%d latency=%.1fms",
                    model_name,
                    attempt + 1,
                    latency_ms,
                )

                raw_text = response.text.strip()
                chat_response = self._parse_chat_response(raw_text, context_store)

                self._persist_conversation(
                    user_id=user_id,
                    user_message=message,
                    response_text=chat_response.response_text,
                    action_type=chat_response.actions[0].type if chat_response.actions else "none",
                    actions=chat_response.actions,
                )

                return chat_response

            except Exception as exc:
                latency_ms = (time.time() - start) * 1000 if 'start' in dir() else 0
                last_error = exc
                logger.warning(
                    "gemini.chat failed model=%s attempt=%d/%d latency=%.1fms error=%s",
                    model_name,
                    attempt + 1,
                    MAX_RETRIES,
                    latency_ms,
                    exc,
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF * (attempt + 1))

        self.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Gemini API chat session failed after {MAX_RETRIES} attempts: {last_error!s}",
        ) from last_error
