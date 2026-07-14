import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# We import the required schemas
from app.models.schemas import Action, RouteResponse, CrowdAlert, ChatResponse, AlternativeRoute
from app.models.models import ConversationModel, UserModel
from app.data.stadium_graph import STADIUM_NODES

logger = logging.getLogger("stadium_ai")

# Check on startup (lazy warning only, no API calls)
def check_gemini_configured() -> bool:
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", "").strip()
    if not api_key:
        logger.warning("WARNING: GEMINI_API_KEY is not configured. AI features will return HTTP 503.")
        return False
    if not model_name:
        logger.warning("WARNING: GEMINI_MODEL is not configured. AI features will return HTTP 503.")
        return False
    return True

# Initialize the startup check warning
check_gemini_configured()

class LLMService:
    def __init__(self, db: Session):
        self.db = db

    def _get_api_client(self) -> Tuple[Any, str]:
        """
        Dynamically loads the API key and model name, initializes and returns the Gemini client and model name.
        Throws HTTP 503 if API key or model name is missing.
        """
        load_dotenv(override=True)
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model_name = os.getenv("GEMINI_MODEL", "").strip()

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini API key is not configured. AI features are disabled."
            )
        if not model_name:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini model (GEMINI_MODEL) is not configured in the environment."
            )

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai, model_name
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to initialize Gemini API client: {str(e)}"
            )

    def translate_text(self, text: str, target_lang: str, source_lang: Optional[str] = None, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Translates text with cultural context using the real Gemini API.
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

        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )
            response = model.generate_content([system_prompt, user_content])
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Gemini API translation error: {str(e)}"
            )

    def classify_incident_ai(self, description: str) -> Dict[str, Any]:
        """
        Classifies reported incident using Gemini API.
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

        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json"
                }
            )
            response = model.generate_content([system_prompt, f"Incident report: '{description}'"])
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Gemini API incident classification error: {str(e)}"
            )

    def execute_chat(self, user_id: str, message: str, location: Optional[str] = None, accessibility_mode: bool = False) -> ChatResponse:
        """
        Orchestrates AI chat concierge session using the real Gemini API.
        Handles conversation memory from SQLite DB and runs tools (function calling).
        """
        genai, model_name = self._get_api_client()

        # Step 1: Gather Conversation History from DB
        history = self.db.query(ConversationModel).filter(
            ConversationModel.user_id == user_id
        ).order_by(ConversationModel.timestamp.desc()).limit(20).all()
        history.reverse()

        # Step 2: System prompt setup
        system_instructions = (
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

        # Build list of prompt messages
        chat_contents = []
        chat_contents.append({"role": "user", "parts": [system_instructions]})
        chat_contents.append({"role": "model", "parts": ["Understood. I will act as StadiumAI and output JSON responses based on these instructions."] })

        for h in history:
            chat_contents.append({"role": "user" if h.role == "user" else "model", "parts": [h.message]})

        # Add current user prompt
        current_prompt = f"User Location: {location or 'unknown'}\nAccessibility Mode Enabled: {accessibility_mode}\nMessage: {message}"
        chat_contents.append({"role": "user", "parts": [current_prompt]})

        # Define tools in python
        # We define local schemas and execution mappings
        context_store = {
            "route_response": None,
            "crowd_alert": None,
            "actions": []
        }

        # Local tool functions to declare to Gemini
        # We write helper function definitions matching what Gemini expects
        # 1. get_directions
        def get_directions(from_location: str, to_location: str) -> str:
            """
            Calculate the optimal path/directions between two points in the stadium.
            Args:
                from_location: Starting node ID (e.g. gate_a, sec_5)
                to_location: Ending node ID (e.g. food_court_north, sec_10)
            """
            from app.services.navigation_service import NavigationService
            nav = NavigationService(self.db)
            try:
                res = nav.calculate_route(from_location, to_location, accessibility_mode, True)
                context_store["route_response"] = res
                return json.dumps(res)
            except Exception as e:
                return f"Error computing directions: {str(e)}"

        # 2. get_crowd_density
        def get_crowd_density(zone_id: str) -> str:
            """
            Get the current crowd density level and safety risk for a zone in the stadium.
            Args:
                zone_id: The zone or gate ID (e.g. zone_gate_a, zone_concourse_1)
            """
            from app.services.crowd_service import CrowdService
            crowd = CrowdService(self.db)
            try:
                res = crowd.get_zone_density(zone_id)
                # Keep record of crowd alerts
                if res.level in ["high", "critical"]:
                    context_store["crowd_alert"] = CrowdAlert(
                        zone_id=res.zone_id,
                        density=res.current_density,
                        level=res.level,
                        message=f"High crowd levels detected in {res.zone_id}. Avoid this area if possible."
                    )
                return json.dumps(res.dict())
            except Exception as e:
                return f"Error retrieving crowd density: {str(e)}"

        # 3. get_transport_options
        def get_transport_options(location: str, destination: Optional[str] = None, mode: Optional[str] = None) -> str:
            """
            Get transport options, departure times, traffic levels, and recommended modes.
            Args:
                location: Current location or stadium gate
                destination: Where the user wants to go (optional)
                mode: Transport mode (bus, metro, shuttle, taxi) (optional)
            """
            from app.services.transport_service import TransportService
            ts = TransportService(self.db)
            try:
                res = ts.get_options(location, destination, mode)
                context_store["actions"].append(Action(type="transport", payload=res.dict()))
                return json.dumps(res.dict())
            except Exception as e:
                return f"Error checking transport options: {str(e)}"

        # 4. classify_waste
        def classify_waste(item_description: str, location: Optional[str] = None) -> str:
            """
            Classifies waste item as recycling, compost, or landfill and locates nearest bin.
            Args:
                item_description: Name of item to discard (e.g. plastic cup, banana peel)
                location: User's current location (optional)
            """
            # Rule-based lookup or simple sustainability helper
            # We can handle sustainability waste lookup directly
            # Let's import sustainability router waste classification
            from app.routers.sustainability import classify_waste_item
            try:
                res = classify_waste_item(item_description, location)
                context_store["actions"].append(Action(type="sustainability", payload=res.dict()))
                return json.dumps(res.dict())
            except Exception as e:
                return f"Error classifying waste: {str(e)}"

        # 5. create_incident
        def create_incident(type: str, location: str, description: str, severity: str = "medium") -> str:
            """
            Reports an active security, medical, or fire incident to stadium dispatchers.
            Args:
                type: medical, fire, security, lost_person, infrastructure
                location: location of incident
                description: details about what happened
                severity: low, medium, high, critical
            """
            from app.services.incident_service import IncidentService
            iserv = IncidentService(self.db)
            try:
                res = iserv.report_incident(type, location, description, severity, user_id)
                context_store["actions"].append(Action(type="incident_reported", payload=res.dict()))
                return json.dumps(res.dict())
            except Exception as e:
                return f"Error submitting incident: {str(e)}"

        # 6. get_accessibility_info
        def get_accessibility_info(service_type: str) -> str:
            """
            Get details and wait times for accessible units (elevators, restrooms, companion aid).
            Args:
                service_type: elevator, ramp, restroom, hearing_loop, wheelchair_rental
            """
            from app.routers.accessibility import get_accessibility_services_endpoint
            try:
                res = get_accessibility_services_endpoint(service_type, self.db)
                context_store["actions"].append(Action(type="accessibility", payload=res.dict()))
                return json.dumps(res.dict())
            except Exception as e:
                return f"Error retrieving accessibility: {str(e)}"

        # 7. get_match_info
        def get_match_info(match_id: str = "current") -> str:
            """
            Get match score, status, timelines, or stats.
            Args:
                match_id: ID of the match, or 'current' for the active live match
            """
            from app.routers.match import get_match_details, get_current_live_match
            try:
                if match_id == "current":
                    res = get_current_live_match(self.db)
                else:
                    res = get_match_details(match_id, self.db)
                context_store["actions"].append(Action(type="match_stats", payload=res.dict()))
                return json.dumps(res.dict())
            except Exception as e:
                return f"Error checking match details: {str(e)}"

        # List of python functions passed as tools to Gemini
        registered_tools = [
            get_directions,
            get_crowd_density,
            get_transport_options,
            classify_waste,
            create_incident,
            get_accessibility_info,
            get_match_info
        ]

        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                tools=registered_tools,
                generation_config={
                    "temperature": 0.5,
                    "response_mime_type": "application/json"
                }
            )

            # Generate response
            # Gemini chat session or simple content generation loop to support tool execution
            chat = model.start_chat(enable_automatic_function_calling=True)
            
            # Send message to model
            response = chat.send_message(current_prompt)
            
            # Parse response
            raw_text = response.text.strip()
            parsed = json.loads(raw_text)
            
            response_text = parsed.get("response_text", "I'm sorry, I encountered an issue parsing the response.")
            action_type = parsed.get("action_type", "none")
            action_payload = parsed.get("action_payload", {})

            # If action was returned by JSON, add it to action list if not already captured
            if action_type != "none" and not context_store["actions"]:
                context_store["actions"].append(Action(type=action_type, payload=action_payload))

            # Build final response
            chat_response = ChatResponse(
                response_text=response_text,
                actions=context_store["actions"],
                route=context_store["route_response"],
                crowd_alert=context_store["crowd_alert"],
                from_agent=True
            )

            # Store conversations in Database
            user_msg = ConversationModel(
                user_id=user_id,
                role="user",
                message=message,
                timestamp=None # default utcnow
            )
            ai_msg = ConversationModel(
                user_id=user_id,
                role="assistant",
                message=response_text,
                intent=action_type,
                actions=json.dumps([a.dict() for a in chat_response.actions]),
                timestamp=None # default utcnow
            )
            self.db.add(user_msg)
            self.db.add(ai_msg)
            self.db.commit()

            return chat_response

        except Exception as e:
            # Rollback db session just in case it got dirty
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Gemini API chat session error: {str(e)}"
            )
