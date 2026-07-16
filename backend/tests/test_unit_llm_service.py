"""Unit tests for LLMService: chat, translation, incident classification, and tool methods."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


# ── check_gemini_configured ──────────────────────────────────────────────


class TestCheckGeminiConfigured:
    """Tests for the startup configuration check function."""

    @patch("app.services.llm_service.settings")
    def test_returns_true_when_configured(self, mock_settings: MagicMock) -> None:
        from app.services.llm_service import check_gemini_configured

        mock_settings.GEMINI_API_KEY = "  fake-key  "
        mock_settings.GEMINI_MODEL = "  gemini-pro  "
        assert check_gemini_configured() is True

    @patch("app.services.llm_service.settings")
    def test_returns_false_when_api_key_empty(self, mock_settings: MagicMock) -> None:
        from app.services.llm_service import check_gemini_configured

        mock_settings.GEMINI_API_KEY = ""
        mock_settings.GEMINI_MODEL = "gemini-pro"
        assert check_gemini_configured() is False

    @patch("app.services.llm_service.settings")
    def test_returns_false_when_model_empty(self, mock_settings: MagicMock) -> None:
        from app.services.llm_service import check_gemini_configured

        mock_settings.GEMINI_API_KEY = "key"
        mock_settings.GEMINI_MODEL = ""
        assert check_gemini_configured() is False


# ── _get_api_client ──────────────────────────────────────────────────────


class TestGetApiClient:
    """Tests for _get_api_client: validates config checks and import handling."""

    def _make_service(self, db: MagicMock | None = None):
        from app.services.llm_service import LLMService

        return LLMService(db or MagicMock())

    @patch("app.services.llm_service.settings")
    def test_raises_503_when_api_key_missing(self, mock_settings: MagicMock) -> None:
        from fastapi import HTTPException

        mock_settings.GEMINI_API_KEY = ""
        mock_settings.GEMINI_MODEL = "gemini-pro"
        svc = self._make_service()
        with pytest.raises(HTTPException) as exc_info:
            svc._get_api_client()
        assert exc_info.value.status_code == 503
        assert "not configured" in exc_info.value.detail.lower()

    @patch("app.services.llm_service.settings")
    def test_raises_503_when_model_missing(self, mock_settings: MagicMock) -> None:
        from fastapi import HTTPException

        mock_settings.GEMINI_API_KEY = "key"
        mock_settings.GEMINI_MODEL = "  "
        svc = self._make_service()
        with pytest.raises(HTTPException) as exc_info:
            svc._get_api_client()
        assert exc_info.value.status_code == 503
        assert "GEMINI_MODEL" in exc_info.value.detail

    @patch("app.services.llm_service.settings")
    def test_raises_503_when_import_fails(self, mock_settings: MagicMock) -> None:
        from fastapi import HTTPException

        mock_settings.GEMINI_API_KEY = "key"
        mock_settings.GEMINI_MODEL = "model"
        svc = self._make_service()

        with patch.dict("sys.modules", {"google.generativeai": None}):
            with pytest.raises(HTTPException) as exc_info:
                svc._get_api_client()
        assert exc_info.value.status_code == 503
        assert "Failed to initialize" in exc_info.value.detail

    @patch("app.services.llm_service.settings")
    def test_returns_genai_and_model(self, mock_settings: MagicMock) -> None:
        mock_settings.GEMINI_API_KEY = "key"
        mock_settings.GEMINI_MODEL = "gemini-pro"
        svc = self._make_service()

        mock_genai = MagicMock()
        with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
            genai, model_name = svc._get_api_client()
        assert genai is mock_genai
        assert model_name == "gemini-pro"
        mock_genai.configure.assert_called_once_with(api_key="key")


# ── _load_conversation_history ───────────────────────────────────────────


class TestLoadConversationHistory:
    """Tests for conversation history loading."""

    def test_empty_history(self) -> None:
        from app.services.llm_service import LLMService

        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        svc = LLMService(db)
        result = svc._load_conversation_history("usr_abc")
        assert result == []

    def test_reversed_chronological_order(self) -> None:
        from app.services.llm_service import LLMService

        entry_old = SimpleNamespace(role="user", message="old")
        entry_new = SimpleNamespace(role="assistant", message="new")
        # DB returns desc order, but service reverses it
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            entry_new,
            entry_old,
        ]
        svc = LLMService(db)
        result = svc._load_conversation_history("usr_abc")
        assert result[0].message == "old"
        assert result[1].message == "new"


# ── _build_system_instructions ───────────────────────────────────────────


class TestBuildSystemInstructions:
    """Tests for system prompt generation."""

    def test_returns_nonempty_string_with_rules(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        instructions = svc._build_system_instructions()
        assert isinstance(instructions, str)
        assert len(instructions) > 100
        assert "StadiumAI" in instructions
        assert "get_directions" in instructions
        assert "get_crowd_density" in instructions
        assert "create_incident" in instructions


# ── _build_chat_contents ─────────────────────────────────────────────────


class TestBuildChatContents:
    """Tests for building the Gemini message array."""

    def test_structure_starts_with_system_and_model(self) -> None:
        from app.services.llm_service import LLMService

        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        svc = LLMService(db)
        contents = svc._build_chat_contents("usr_x", "hello", None, False)
        assert contents[0]["role"] == "user"
        assert contents[1]["role"] == "model"
        assert contents[-1]["role"] == "user"
        assert "hello" in contents[-1]["parts"][0]

    def test_includes_location_and_accessibility(self) -> None:
        from app.services.llm_service import LLMService

        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        svc = LLMService(db)
        contents = svc._build_chat_contents("usr_x", "hi", "gate_a", True)
        last = contents[-1]["parts"][0]
        assert "gate_a" in last
        assert "True" in last

    def test_history_entries_inserted_between_system_and_current(self) -> None:
        from app.services.llm_service import LLMService

        entry = SimpleNamespace(role="user", message="prior q")
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [entry]
        svc = LLMService(db)
        contents = svc._build_chat_contents("usr_x", "new q", None, False)
        # system(0), model(1), history(2), current(3)
        assert len(contents) == 4
        assert contents[2]["role"] == "user"
        assert contents[2]["parts"][0] == "prior q"


# ── _persist_conversation ────────────────────────────────────────────────


class TestPersistConversation:
    """Tests for saving conversation to the database."""

    def test_adds_two_messages_and_commits(self) -> None:
        from app.services.llm_service import LLMService
        from app.models.schemas import Action

        db = MagicMock()
        svc = LLMService(db)
        svc._persist_conversation(
            "usr_x", "user msg", "ai reply", "navigation",
            [Action(type="navigation", payload={"route": ["a"]})],
        )
        assert db.add.call_count == 2
        db.commit.assert_called_once()

    def test_stores_actions_json(self) -> None:
        from app.services.llm_service import LLMService
        from app.models.schemas import Action

        db = MagicMock()
        svc = LLMService(db)
        actions = [Action(type="transport", payload={"mode": "bus"})]
        svc._persist_conversation("usr_x", "q", "a", "transport", actions)
        ai_msg = db.add.call_args_list[1][0][0]
        assert ai_msg.intent == "transport"
        assert "bus" in ai_msg.actions


# ── _parse_chat_response ─────────────────────────────────────────────────


class TestParseChatResponse:
    """Tests for parsing Gemini raw JSON into ChatResponse."""

    def _make_ctx(self) -> dict:
        return {"route_response": None, "crowd_alert": None, "actions": []}

    def test_basic_response(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        raw = json.dumps({
            "response_text": "Hello!",
            "action_type": "none",
            "action_payload": {},
        })
        resp = svc._parse_chat_response(raw, self._make_ctx())
        assert resp.response_text == "Hello!"
        assert resp.actions == []
        assert resp.from_agent is True

    def test_response_with_action(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        ctx = self._make_ctx()
        raw = json.dumps({
            "response_text": "Here is your route",
            "action_type": "navigation",
            "action_payload": {"route": ["a", "b"]},
        })
        resp = svc._parse_chat_response(raw, ctx)
        assert resp.response_text == "Here is your route"
        assert len(resp.actions) == 1
        assert resp.actions[0].type == "navigation"

    def test_missing_keys_uses_defaults(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        resp = svc._parse_chat_response("{}", self._make_ctx())
        assert "issue parsing" in resp.response_text.lower()
        assert resp.actions == []

    def test_existing_actions_not_overwritten(self) -> None:
        from app.services.llm_service import LLMService
        from app.models.schemas import Action

        ctx = self._make_ctx()
        ctx["actions"] = [Action(type="crowd_alert", payload={})]
        svc = LLMService(MagicMock())
        raw = json.dumps({"response_text": "ok", "action_type": "navigation", "action_payload": {}})
        resp = svc._parse_chat_response(raw, ctx)
        assert len(resp.actions) == 1
        assert resp.actions[0].type == "crowd_alert"


# ── Tool methods ─────────────────────────────────────────────────────────


class TestToolGetDirections:
    """Tests for _tool_get_directions."""

    def test_returns_json_on_success(self) -> None:
        from app.services.llm_service import LLMService
        import app.services.navigation_service as nav_mod

        original = nav_mod.NavigationService
        mock_nav = MagicMock()
        mock_nav.calculate_route.return_value = {"route": ["gate_a", "sec_5"], "distance_meters": 200}
        nav_mod.NavigationService = lambda db: mock_nav
        try:
            db = MagicMock()
            svc = LLMService(db)
            result = svc._tool_get_directions("gate_a", "sec_5", False)
        finally:
            nav_mod.NavigationService = original

        data = json.loads(result)
        assert data["route"] == ["gate_a", "sec_5"]

    def test_returns_error_on_exception(self) -> None:
        from app.services.llm_service import LLMService
        import app.services.navigation_service as nav_mod

        original = nav_mod.NavigationService
        mock_nav = MagicMock()
        mock_nav.calculate_route.side_effect = ValueError("bad route")
        nav_mod.NavigationService = lambda db: mock_nav
        try:
            svc = LLMService(MagicMock())
            result = svc._tool_get_directions("x", "y", False)
        finally:
            nav_mod.NavigationService = original

        assert "Error" in result or "error" in result


class TestToolGetCrowdDensity:
    """Tests for _tool_get_crowd_density."""

    def test_returns_json_and_sets_alert(self) -> None:
        from app.services.llm_service import LLMService

        mock_crowd = MagicMock()
        mock_zone = SimpleNamespace(
            zone_id="gate_a",
            current_density=0.95,
            level="critical",
            model_dump=lambda: {"zone_id": "gate_a", "level": "critical"},
        )
        mock_crowd.get_zone_density.return_value = mock_zone
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        with patch("app.services.crowd_service.CrowdService", return_value=mock_crowd):
            svc = LLMService(MagicMock())
            svc._tool_get_crowd_density("gate_a", ctx)

        assert ctx["crowd_alert"] is not None
        assert ctx["crowd_alert"].level == "critical"

    def test_low_density_no_alert(self) -> None:
        from app.services.llm_service import LLMService

        mock_crowd = MagicMock()
        mock_zone = SimpleNamespace(
            zone_id="gate_b",
            current_density=0.2,
            level="low",
            model_dump=lambda: {"zone_id": "gate_b", "level": "low"},
        )
        mock_crowd.get_zone_density.return_value = mock_zone
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        with patch("app.services.crowd_service.CrowdService", return_value=mock_crowd):
            svc = LLMService(MagicMock())
            svc._tool_get_crowd_density("gate_b", ctx)

        assert ctx["crowd_alert"] is None


class TestToolGetTransportOptions:
    """Tests for _tool_get_transport_options."""

    def test_appends_action_on_success(self) -> None:
        from app.services.llm_service import LLMService

        mock_ts = MagicMock()
        mock_res = SimpleNamespace(model_dump=lambda: {"options": []})
        mock_ts.get_options.return_value = mock_res
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        with patch("app.services.transport_service.TransportService", return_value=mock_ts):
            svc = LLMService(MagicMock())
            svc._tool_get_transport_options("gate_a", "hotel_b", "bus", ctx)

        assert len(ctx["actions"]) == 1
        assert ctx["actions"][0].type == "transport"


class TestToolCreateIncident:
    """Tests for _tool_create_incident."""

    def test_appends_incident_action(self) -> None:
        from app.services.llm_service import LLMService

        mock_is = MagicMock()
        mock_inc = SimpleNamespace(model_dump=lambda: {"incident_id": "inc_1"})
        mock_is.report_incident.return_value = mock_inc
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        with patch("app.services.incident_service.IncidentService", return_value=mock_is):
            svc = LLMService(MagicMock())
            svc._tool_create_incident("medical", "gate_a", "man down", "high", "usr_x", ctx)

        assert len(ctx["actions"]) == 1
        assert ctx["actions"][0].type == "incident_reported"


class TestToolGetAccessibilityInfo:
    """Tests for _tool_get_accessibility_info."""

    def test_returns_services_json(self) -> None:
        from app.services.llm_service import LLMService

        mock_svc_model = SimpleNamespace(
            id="acc_1",
            service_type="elevator",
            location="gate_a",
            status="operational",
            wait_time_minutes=2,
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [mock_svc_model]
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        svc = LLMService(db)
        result = svc._tool_get_accessibility_info("elevator", ctx)
        data = json.loads(result)
        assert "services" in data or "nearest" in data

    def test_returns_error_when_no_services(self) -> None:
        from app.services.llm_service import LLMService

        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []
        db.query.return_value.all.return_value = []
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        svc = LLMService(db)
        result = svc._tool_get_accessibility_info("nonexistent", ctx)
        data = json.loads(result)
        assert "error" in data


class TestToolGetMatchInfo:
    """Tests for _tool_get_match_info."""

    def test_returns_match_json(self) -> None:
        from app.services.llm_service import LLMService

        mock_match = SimpleNamespace(
            id="m_1",
            team_a="Brazil",
            team_b="Argentina",
            score_a=2,
            score_b=1,
            status="live",
            stadium="Lusail",
            kickoff_time="2026-07-19T20:00",
            timeline=None,
            stats=None,
        )
        db = MagicMock()
        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_match
        query_mock.first.return_value = mock_match
        db.query.return_value = query_mock

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        svc = LLMService(db)
        result = svc._tool_get_match_info("current", ctx)
        data = json.loads(result)
        assert data["team_a"] == "Brazil"

    def test_returns_error_when_no_match(self) -> None:
        from app.services.llm_service import LLMService

        db = MagicMock()
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = None
        query_mock.first.return_value = None
        db.query.return_value = query_mock

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        svc = LLMService(db)
        result = svc._tool_get_match_info("current", ctx)
        data = json.loads(result)
        assert "error" in data


class TestToolClassifyWaste:
    """Tests for _tool_classify_waste."""

    def test_appends_sustainability_action(self) -> None:
        from app.services.llm_service import LLMService

        mock_res = SimpleNamespace(model_dump=lambda: {"type": "recycling"})
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        with patch("app.routers.sustainability.classify_waste_item", return_value=mock_res):
            svc = LLMService(MagicMock())
            svc._tool_classify_waste("plastic cup", "gate_a", ctx)

        assert len(ctx["actions"]) == 1
        assert ctx["actions"][0].type == "sustainability"

    def test_returns_error_on_exception(self) -> None:
        from app.services.llm_service import LLMService

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        with patch("app.routers.sustainability.classify_waste_item", side_effect=ValueError("service down")):
            svc = LLMService(MagicMock())
            result = svc._tool_classify_waste("cup", None, ctx)

        assert "Error" in result
        assert len(ctx["actions"]) == 0


class TestToolErrorPaths:
    """Tests for error paths in tool methods."""

    def test_crowd_density_error_path(self) -> None:
        from app.services.llm_service import LLMService
        from sqlalchemy.exc import SQLAlchemyError

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        with patch("app.services.crowd_service.CrowdService") as mock_cls:
            mock_cls.return_value.get_zone_density.side_effect = SQLAlchemyError("db down")
            svc = LLMService(MagicMock())
            result = svc._tool_get_crowd_density("gate_a", ctx)

        assert "Error" in result

    def test_transport_options_error_path(self) -> None:
        from app.services.llm_service import LLMService
        from sqlalchemy.exc import SQLAlchemyError

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        with patch("app.services.transport_service.TransportService") as mock_cls:
            mock_cls.return_value.get_options.side_effect = SQLAlchemyError("timeout")
            svc = LLMService(MagicMock())
            result = svc._tool_get_transport_options("gate_a", None, None, ctx)

        assert "Error" in result

    def test_incident_error_path(self) -> None:
        from app.services.llm_service import LLMService
        from sqlalchemy.exc import SQLAlchemyError

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        with patch("app.services.incident_service.IncidentService") as mock_cls:
            mock_cls.return_value.report_incident.side_effect = SQLAlchemyError("db error")
            svc = LLMService(MagicMock())
            result = svc._tool_create_incident("medical", "gate_a", "man down", "high", "usr_x", ctx)

        assert "Error" in result

    def test_accessibility_error_path(self) -> None:
        from app.services.llm_service import LLMService
        from sqlalchemy.exc import SQLAlchemyError

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        db = MagicMock()
        db.query.side_effect = SQLAlchemyError("db error")
        svc = LLMService(db)
        result = svc._tool_get_accessibility_info("elevator", ctx)

        assert "Error" in result

    def test_match_info_error_path(self) -> None:
        from app.services.llm_service import LLMService
        from sqlalchemy.exc import SQLAlchemyError

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        db = MagicMock()
        db.query.side_effect = SQLAlchemyError("db error")
        svc = LLMService(db)
        result = svc._tool_get_match_info("current", ctx)

        assert "Error" in result

    def test_match_info_by_specific_id(self) -> None:
        from app.services.llm_service import LLMService

        mock_match = SimpleNamespace(
            id="m_1",
            team_a="Brazil",
            team_b="Argentina",
            score_a=2,
            score_b=1,
            status="live",
            stadium="Lusail",
            kickoff_time="2026-07-19T20:00",
            timeline='[{"minute": 10, "event_type": "goal"}]',
            stats='{"possession_a": 60, "possession_b": 40, "shots_a": 5, "shots_b": 3, "fouls_a": 2, "fouls_b": 4}',
        )
        db = MagicMock()
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = mock_match
        db.query.return_value = query_mock

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        svc = LLMService(db)
        result = svc._tool_get_match_info("m_1", ctx)
        data = json.loads(result)
        assert data["id"] == "m_1"

    def test_match_info_invalid_timeline_json(self) -> None:
        from app.services.llm_service import LLMService

        mock_match = SimpleNamespace(
            id="m_1",
            team_a="Brazil",
            team_b="Argentina",
            score_a=2,
            score_b=1,
            status="live",
            stadium="Lusail",
            kickoff_time="2026-07-19T20:00",
            timeline="not-json",
            stats="not-json",
        )
        db = MagicMock()
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = mock_match
        db.query.return_value = query_mock

        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        svc = LLMService(db)
        result = svc._tool_get_match_info("current", ctx)
        data = json.loads(result)
        assert data["timeline"] == []
        assert data["stats"]["possession_a"] == 50

    def test_accessibility_no_operational_items(self) -> None:
        from app.services.llm_service import LLMService

        mock_svc_model = SimpleNamespace(
            id="acc_1",
            service_type="elevator",
            location="gate_a",
            status="maintenance",
            wait_time_minutes=0,
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [mock_svc_model]
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}

        svc = LLMService(db)
        result = svc._tool_get_accessibility_info("elevator", ctx)
        data = json.loads(result)
        assert "nearest" in data


# ── _register_tools ──────────────────────────────────────────────────────


class TestRegisterTools:
    """Tests for the tool registry."""

    def test_returns_seven_callables(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        tools = svc._register_tools(ctx, False, "usr_x")
        assert len(tools) == 7
        for t in tools:
            assert callable(t)

    def test_registered_tools_delegate_to_methods(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        tools = svc._register_tools(ctx, True, "usr_x")

        with patch("app.services.navigation_service.NavigationService") as nav_cls:
            nav_cls.return_value.calculate_route.return_value = {"route": ["a"]}
            result = tools[0]("gate_a", "sec_5")
            assert "route" in result

    def test_registered_crowd_density_tool(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        tools = svc._register_tools(ctx, False, "usr_x")

        with patch("app.services.crowd_service.CrowdService") as cls:
            mock_zone = SimpleNamespace(
                zone_id="g1", current_density=0.3, level="low",
                model_dump=lambda: {"zone_id": "g1", "level": "low"},
            )
            cls.return_value.get_zone_density.return_value = mock_zone
            result = tools[1]("g1")
            assert "low" in result

    def test_registered_transport_tool(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        tools = svc._register_tools(ctx, False, "usr_x")

        with patch("app.services.transport_service.TransportService") as cls:
            mock_res = SimpleNamespace(model_dump=lambda: {"options": []})
            cls.return_value.get_options.return_value = mock_res
            result = tools[2]("gate_a")
            assert "options" in result

    def test_registered_waste_tool(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        tools = svc._register_tools(ctx, False, "usr_x")

        with patch("app.routers.sustainability.classify_waste_item") as fn:
            fn.return_value = SimpleNamespace(model_dump=lambda: {"type": "recycling"})
            result = tools[3]("plastic cup")
            assert "recycling" in result

    def test_registered_incident_tool(self) -> None:
        from app.services.llm_service import LLMService

        svc = LLMService(MagicMock())
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        tools = svc._register_tools(ctx, False, "usr_x")

        with patch("app.services.incident_service.IncidentService") as cls:
            mock_inc = SimpleNamespace(model_dump=lambda: {"incident_id": "inc_1"})
            cls.return_value.report_incident.return_value = mock_inc
            result = tools[4]("medical", "gate_a", "man down", "high")
            assert "inc_1" in result

    def test_registered_accessibility_tool(self) -> None:
        from app.services.llm_service import LLMService

        mock_svc = SimpleNamespace(
            id="a1", service_type="elevator", location="g1",
            status="operational", wait_time_minutes=2,
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [mock_svc]
        svc = LLMService(db)
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        tools = svc._register_tools(ctx, False, "usr_x")

        result = tools[5]("elevator")
        assert "elevator" in result

    def test_registered_match_tool(self) -> None:
        from app.services.llm_service import LLMService

        mock_match = SimpleNamespace(
            id="m1", team_a="A", team_b="B", score_a=1, score_b=0,
            status="live", stadium="S", kickoff_time="2026-07-19T20:00",
            timeline=None, stats=None,
        )
        db = MagicMock()
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = mock_match
        db.query.return_value = query_mock
        svc = LLMService(db)
        ctx = {"route_response": None, "crowd_alert": None, "actions": []}
        tools = svc._register_tools(ctx, False, "usr_x")

        result = tools[6]("current")
        assert "m1" in result


# ── translate_text (mocked genai) ────────────────────────────────────────


class TestTranslateText:
    """Tests for translate_text with mocked Gemini API."""

    def test_success(self) -> None:
        from app.services.llm_service import LLMService

        mock_response = SimpleNamespace(text=json.dumps({
            "translated_text": "Hola",
            "pronunciation_guide": "OH-lah",
            "cultural_note": None,
            "detected_source_lang": "en",
        }))
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        svc = LLMService(MagicMock())
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "key"
            mock_settings.GEMINI_MODEL = "model"
            with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
                result = svc.translate_text("Hello", "es")

        assert result["translated_text"] == "Hola"

    def test_raises_503_on_failure(self) -> None:
        from app.services.llm_service import LLMService
        from fastapi import HTTPException

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = RuntimeError("API down")
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        svc = LLMService(MagicMock())
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "key"
            mock_settings.GEMINI_MODEL = "model"
            with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
                with pytest.raises(HTTPException) as exc_info:
                    svc.translate_text("Hello", "es")
                assert exc_info.value.status_code == 503

    def test_with_source_lang_and_context(self) -> None:
        from app.services.llm_service import LLMService

        mock_response = SimpleNamespace(text=json.dumps({
            "translated_text": "Hola amigo",
            "pronunciation_guide": None,
            "cultural_note": "Informal greeting",
            "detected_source_lang": "en",
        }))
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        svc = LLMService(MagicMock())
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "key"
            mock_settings.GEMINI_MODEL = "model"
            with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
                result = svc.translate_text("Hello friend", "es", source_lang="en", context="football stadium")

        assert result["translated_text"] == "Hola amigo"


# ── classify_incident_ai (mocked genai) ─────────────────────────────────


class TestClassifyIncidentAI:
    """Tests for classify_incident_ai with mocked Gemini API."""

    def test_success(self) -> None:
        from app.services.llm_service import LLMService

        mock_response = SimpleNamespace(text=json.dumps({
            "type": "security",
            "priority": "high",
            "severity": "high",
            "response_urgency": "immediate",
        }))
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        svc = LLMService(MagicMock())
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "key"
            mock_settings.GEMINI_MODEL = "model"
            with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
                result = svc.classify_incident_ai("Suspicious package")

        assert result["type"] == "security"
        assert result["priority"] == "high"

    def test_raises_503_on_failure(self) -> None:
        from app.services.llm_service import LLMService
        from fastapi import HTTPException

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = RuntimeError("quota exceeded")
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        svc = LLMService(MagicMock())
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "key"
            mock_settings.GEMINI_MODEL = "model"
            with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
                with pytest.raises(HTTPException) as exc_info:
                    svc.classify_incident_ai("Fire in the stands")
                assert exc_info.value.status_code == 503
                assert "failed after" in exc_info.value.detail.lower()


# ── execute_chat (mocked genai) ─────────────────────────────────────────


class TestExecuteChat:
    """Tests for execute_chat with mocked Gemini API."""

    def test_full_chat_flow(self) -> None:
        from app.services.llm_service import LLMService

        mock_response = SimpleNamespace(text=json.dumps({
            "response_text": "Welcome to the World Cup!",
            "action_type": "none",
            "action_payload": {},
        }))
        mock_model = MagicMock()
        mock_chat = MagicMock()
        mock_chat.send_message.return_value = mock_response
        mock_model.start_chat.return_value = mock_chat
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        db = MagicMock()
        # empty history
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        svc = LLMService(db)
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "key"
            mock_settings.GEMINI_MODEL = "model"
            with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
                result = svc.execute_chat("usr_x", "Hello!")

        assert result.response_text == "Welcome to the World Cup!"
        assert result.from_agent is True
        assert db.add.call_count == 2
        db.commit.assert_called_once()

    def test_chat_error_returns_503(self) -> None:
        from app.services.llm_service import LLMService
        from fastapi import HTTPException

        mock_model = MagicMock()
        mock_chat = MagicMock()
        mock_chat.send_message.side_effect = RuntimeError("timeout")
        mock_model.start_chat.return_value = mock_chat
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        svc = LLMService(db)
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "key"
            mock_settings.GEMINI_MODEL = "model"
            with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
                with pytest.raises(HTTPException) as exc_info:
                    svc.execute_chat("usr_x", "Hello!")
                assert exc_info.value.status_code == 503
                db.rollback.assert_called_once()
