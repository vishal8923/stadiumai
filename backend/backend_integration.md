# StadiumAI - Backend Integration Document

This document provides a comprehensive guide for frontend developers and client-side integration agents to interface with the **StadiumAI Backend Service**. This API powers the Operations & Fan Experience GenAI Concierge Service for the FIFA World Cup 2026.

---

## 1. Project Overview

- **Backend Framework**: FastAPI (v0.110.0)
- **Runtime**: Python 3.11
- **Package Manager**: `pip` (dependency tracking via `requirements.txt`)
- **Server Gateway**: Uvicorn (v0.28.0)
- **Database Layer**: SQLite (`stadium_ai.db`) accessed via SQLAlchemy (v2.0.28) ORM.

### Project Structure

```text
stadiumai/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point & configuration registry
│   ├── config.py               # Settings management via Pydantic BaseSettings
│   ├── dependencies.py         # Shared rate-limiting & database dependencies
│   ├── data/                   # Mock generators, graph database configuration, static datasets
│   │   ├── stadium_graph.py    # Stadium topological layout & nodes
│   │   └── mock_generators.py  # Seeding data on startup
│   ├── models/                 # Database & schema definitions
│   │   ├── database.py         # SQLAlchemy connection engine
│   │   ├── models.py           # Database entity tables
│   │   └── schemas.py          # Pydantic validation schemas
│   ├── routers/                # API router handlers
│   │   ├── accessibility.py    # Ramps, elevators, wait times
│   │   ├── admin.py            # Administrative panel, staff workloads, stats
│   │   ├── chat.py             # GenAI assistant chat concierge
│   │   ├── crowd.py            # Live crowd densities & forecasts
│   │   ├── incidents.py        # Safety & medical incident submissions
│   │   ├── match.py            # Live score tracking and timeline stats
│   │   ├── navigation.py       # Custom A* pathfinding routes
│   │   ├── notifications.py    # Push notification queues
│   │   ├── sustainability.py   # Eco-waste classification
│   │   ├── translate.py        # Google Gemini translator
│   │   ├── transport.py        # Metro, shuttle, taxi schedules
│   │   └── users.py            # Anonymous fan session initiation
│   └── services/               # Underlying business logic
│       ├── analytics_service.py
│       ├── crowd_service.py
│       ├── incident_service.py
│       ├── llm_service.py       # Google Gemini client & tool configurations
│       ├── navigation_service.py
│       ├── notification_service.py
│       ├── rag_service.py       # Static document query retrieval (RAG)
│       └── transport_service.py
├── tests/                      # Automated test suite
├── Dockerfile                  # Slim production container config
├── docker-compose.yml          # Container orchestration template
└── requirements.txt            # Dependency listings
```

---

## 2. Server Configuration

- **Development Base URL**: `http://localhost:8000`
- **Production Base URL**: Configured via production domain mapping (e.g., `https://api.stadiumai.world`)
- **API Version**: `1.0.0`
- **API Prefix**: `/api/v1`

---

## 3. Authentication & Session Management

The backend uses a **stateful, anonymous fan session-based architecture**. It does *not* require traditional passwords, registration workflows, JWT tokens, access tokens, refresh tokens, or token-based logout endpoints.

### Session Lifecycle

1. **Session Creation**: The client initiates an anonymous fan session by calling `POST /api/v1/users/session`.
2. **Session Identification**: The server returns a persistent plain-text session identifier (`user_id`) in the format `usr_<hex_string>`.
3. **Session Persistence**: The `user_id` must be stored by the frontend in `localStorage` or memory.
4. **Authorization Header**: For all stateful requests (chat, notifications, history, reporting), the frontend must pass this session ID in the request header:
   ```http
   X-User-ID: usr_a1b2c3d4
   ```
   *Alternative:* If headers are restricted, endpoints accept the user ID via query parameters (`?user_id=usr_a1b2c3d4`) or request bodies.
5. **Session Expiration**: Sessions are persistent in the database. There is no active token expiration.
6. **Logout**: To terminate the session, the frontend simply clears the stored `user_id` local token.

### Protected Access

There are no route-level authorization guards for normal fan routes. Administrative endpoints (`/api/v1/admin/*`) are designed for operations staff. Rate limiting is applied universally based on client IP.

---

## 4. API Response Standard

All endpoints return standardized JSON objects.

### Standard Success Response

Returned directly as defined by the endpoint's Pydantic model. For example:
```json
{
  "status": "ok"
}
```

### Standard Error Response

All validation, missing credentials, and server issues return a consistent error body:
```json
{
  "detail": "Description of the error."
}
```

### FastAPI Schema Validation Error (422 Unprocessable Entity)

If input validation fails, FastAPI returns a detailed location and description array:
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Rate Limiting HTTP Status

When a client exceeds the request rate threshold, the server returns an **HTTP 429 Too Many Requests** error:
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## 5. API Documentation

### 5.1 System & Health Endpoints

---

#### 1. System Health
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/health`
- **Description**: Returns the server uptime, build version, and UTC timestamp.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**: None
- **Query Parameters**: None
- **Request Body**: None
- **Validation Rules**: None
- **Example Request**:
  ```http
  GET /api/v1/health HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "status": "ok",
    "uptime": 1254.32,
    "version": "1.0.0",
    "timestamp": "2026-07-12T12:35:10.123456"
  }
  ```

---

#### 2. Database Connection Health
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/health/db`
- **Description**: Verifies live connection to SQLite database and logs query latency.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**: None
- **Query Parameters**: None
- **Request Body**: None
- **Validation Rules**: None
- **Example Request**:
  ```http
  GET /api/v1/health/db HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "status": "healthy",
    "connection_pool": 1,
    "latency_ms": 1.45
  }
  ```
- **Example Error Response**:
  - **Status Code**: `500 Internal Server Error`
  ```json
  {
    "detail": "Database health check failed: connection timeout"
  }
  ```

---

#### 3. AI Service Health Check
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/health/ai`
- **Description**: Checks configuration state of Google Gemini API variables.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**: None
- **Query Parameters**: None
- **Request Body**: None
- **Validation Rules**: None
- **Example Request**:
  ```http
  GET /api/v1/health/ai HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "status": "configured",
    "provider": "Google Gemini",
    "model": "gemini-3.5-flash",
    "last_response_time_ms": 0.0,
    "quota_remaining": null
  }
  ```

---

### 5.2 User Session Endpoints

---

#### 4. Create User Session
- **HTTP Method**: `POST`
- **Full Path**: `/api/v1/users/session`
- **Description**: Registers a new anonymous fan session in the database.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path/Query Parameters**: None
- **Request Body**: None
- **Validation Rules**: Rate limit of 100 requests per minute.
- **Example Request**:
  ```http
  POST /api/v1/users/session HTTP/1.1
  Host: localhost:8000
  Content-Length: 0
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "user_id": "usr_a1b2c3d4",
    "created_at": "2026-07-12T12:35:10.123456"
  }
  ```

---

#### 5. Retrieve User Chat History
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/users/{user_id}/history`
- **Description**: Fetches past chat transcripts, actions, and classified intents for a session.
- **Authentication Required**: Yes (Session validation)
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**:
  - `user_id`: String (Target session code)
- **Query Parameters**: None
- **Request Body**: None
- **Validation Rules**: Returns 404 if the session ID does not exist in the database. Rate limit: 100 req/min.
- **Example Request**:
  ```http
  GET /api/v1/users/usr_a1b2c3d4/history HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "conversations": [
      {
        "role": "user",
        "message": "Where is the nearest waste bin?",
        "intent": null,
        "actions": [],
        "timestamp": "2026-07-12T12:30:00"
      },
      {
        "role": "assistant",
        "message": "The nearest bin is a Recycling Bin (Blue) located near Concourse 1.",
        "intent": "sustainability",
        "actions": [
          {
            "type": "sustainability",
            "payload": {
              "item_type": "Recyclable (Plastic/Metal)",
              "bin_type": "Recycling Bin (Blue)",
              "bin_location": "Next to washrooms in Concourse 1",
              "environmental_impact": "Saves energy and redirects plastics away from landfills.",
              "disposal_tip": "Empty any liquid before recycling."
            }
          }
        ],
        "timestamp": "2026-07-12T12:30:02"
      }
    ],
    "total": 2
  }
  ```
- **Example Error Response**:
  - **Status Code**: `404 Not Found`
  ```json
  {
    "detail": "User session 'usr_nonexistent' not found."
  }
  ```

---

### 5.3 Concierge & AI Endpoints

---

#### 6. GenAI Concierge Chat
- **HTTP Method**: `POST`
- **Full Path**: `/api/v1/chat`
- **Description**: Main conversational concierge routing queries to Google Gemini. Auto-executes functional tools based on intent.
- **Authentication Required**: No (Optional `user_id` in body)
- **Headers**:
  - `Content-Type: application/json`
- **Path/Query Parameters**: None
- **Request Body Schema**:
  - `message`: String (Required)
  - `user_id`: String (Optional, defaults to `"anonymous_user"`)
  - `language`: String (Optional)
  - `location`: String (Optional, e.g., `"gate_a"`)
  - `accessibility_mode`: Boolean (Optional, defaults to `false`)
- **Validation Rules**: Message cannot be empty. Rate limit: 20 requests per minute.
- **Example Request**:
  ```json
  {
    "message": "Show me directions to Sec 10 avoiding crowd density",
    "user_id": "usr_a1b2c3d4",
    "location": "gate_a",
    "accessibility_mode": false
  }
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "response_text": "I have mapped a route from Gate A to Section 10 for you. It avoids the crowded bottlenecks near Gate B.",
    "actions": [
      {
        "type": "navigation",
        "payload": {
          "route": ["gate_a", "sec_1", "sec_10"],
          "estimated_time_minutes": 4,
          "distance_meters": 320,
          "crowd_score": "low"
        }
      }
    ],
    "route": {
      "route": ["gate_a", "sec_1", "sec_10"],
      "estimated_time_minutes": 4,
      "distance_meters": 320,
      "crowd_score": "low",
      "alternative_routes": [],
      "accessibility_notes": null
    },
    "crowd_alert": null,
    "from_agent": true
  }
  ```
- **Example Error Response**:
  - **Status Code**: `503 Service Unavailable` (If Gemini key is disabled or not set)
  ```json
  {
    "detail": "Gemini API key is not configured. AI features are disabled."
  }
  ```

---

#### 7. Language Translation
- **HTTP Method**: `POST`
- **Full Path**: `/api/v1/translate`
- **Description**: Translates queries and announcements with localized cultural context using Google Gemini.
- **Authentication Required**: No
- **Headers**:
  - `Content-Type: application/json`
- **Path/Query Parameters**: None
- **Request Body Schema**:
  - `text`: String (Required)
  - `source_lang`: String (Optional, auto-detected if empty)
  - `target_lang`: String (Required)
  - `context`: String (Optional, e.g., `"concourse directions"`)
- **Validation Rules**: Input text must be provided. Rate limit: 100 req/min.
- **Example Request**:
  ```json
  {
    "text": "Where is the kickoff point?",
    "target_lang": "es",
    "context": "stadium football match"
  }
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "translated_text": "¿Dónde se realiza el saque inicial?",
    "pronunciation_guide": "Dohn-deh seh rah-ah-leeth-ah el sah-oo-keh ee-nee-thyahl",
    "cultural_note": "Kickoff translates literally as 'saque inicial' in professional match broadcasts.",
    "detected_source_lang": "en"
  }
  ```

---

#### 8. Submit Incident Report
- **HTTP Method**: `POST`
- **Full Path**: `/api/v1/incidents`
- **Description**: Reports safety, infrastructure, or medical concerns. Uses Gemini AI to auto-classify priority levels and dispatch staff.
- **Authentication Required**: No
- **Headers**:
  - `Content-Type: application/json`
- **Path/Query Parameters**: None
- **Request Body Schema**:
  - `type`: String (Required, e.g., `"medical"`, `"fire"`, `"security"`, `"lost_person"`, `"infrastructure"`)
  - `location`: String (Required, e.g., `"Section 12"`)
  - `description`: String (Required)
  - `severity`: String (Optional, defaults to `"medium"`)
  - `reporter_id`: String (Optional)
- **Validation Rules**: Priority is auto-derived by AI analysis of the description field. Rate limit: 10 req/min.
- **Example Request**:
  ```json
  {
    "type": "medical",
    "location": "Concourse 2",
    "description": "An elderly fan has collapsed and appears to be unconscious near the hot dog stand.",
    "severity": "high",
    "reporter_id": "usr_a1b2c3d4"
  }
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "incident_id": "inc_2a8b9c10",
    "priority": "critical",
    "response_time_minutes": 3,
    "status": "DISPATCHED",
    "assigned_staff": "stf_medical_01"
  }
  ```
- **Example Error Response**:
  - **Status Code**: `503 Service Unavailable`
  ```json
  {
    "detail": "Gemini API incident classification error: Service connection timed out."
  }
  ```

---

### 5.4 Stadium Services

---

#### 9. A* Navigation Pathfinding
- **HTTP Method**: `POST`
- **Full Path**: `/api/v1/navigate`
- **Description**: Computes step-by-step pathfinding using rule-based topological graph navigation (Non-AI).
- **Authentication Required**: No
- **Headers**:
  - `Content-Type: application/json`
- **Path/Query Parameters**: None
- **Request Body Schema**:
  - `from_location`: String (Required, start node)
  - `to_location`: String (Required, end node)
  - `accessibility_mode`: Boolean (Optional, defaults to `false`)
  - `avoid_crowds`: Boolean (Optional, defaults to `false`)
- **Validation Rules**: Locations must match registered node IDs. Rate limit: 50 req/min.
- **Example Request**:
  ```json
  {
    "from_location": "gate_a",
    "to_location": "sec_10",
    "accessibility_mode": true,
    "avoid_crowds": true
  }
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "route": ["gate_a", "elevator_1", "sec_10"],
    "estimated_time_minutes": 6,
    "distance_meters": 410,
    "crowd_score": "low",
    "alternative_routes": [],
    "accessibility_notes": "Route maps via Elevator 1 to avoid concourse stairs."
  }
  ```

---

#### 10. Live Crowd Heatmap Overlay
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/crowd/all`
- **Description**: Retrieves real-time crowd density parameters across all stadium zones.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**: None
- **Query Parameters**: None
- **Request Body**: None
- **Validation Rules**: None. Rate limit: 100 req/min.
- **Example Request**:
  ```http
  GET /api/v1/crowd/all HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "zones": [
      {
        "zone_id": "zone_gate_a",
        "current_density": 0.35,
        "level": "medium",
        "prediction_5min": "medium",
        "prediction_15min": "high",
        "risk_level": "low",
        "suggested_alternative": null,
        "trend": "rising"
      },
      {
        "zone_id": "zone_gate_b",
        "current_density": 0.85,
        "level": "high",
        "prediction_5min": "high",
        "prediction_15min": "critical",
        "risk_level": "high",
        "suggested_alternative": "gate_d",
        "trend": "rising"
      }
    ],
    "timestamp": "2026-07-12T12:35:10.123456"
  }
  ```

---

#### 11. Zone Specific Crowd Status
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/crowd/{zone_id}`
- **Description**: Detailed status metrics for a single zone.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**:
  - `zone_id`: String (e.g., `"zone_gate_b"`)
- **Query Parameters**: None
- **Request Body**: None
- **Validation Rules**: None
- **Example Request**:
  ```http
  GET /api/v1/crowd/zone_gate_b HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "zone_id": "zone_gate_b",
    "current_density": 0.85,
    "level": "high",
    "prediction_5min": "high",
    "prediction_15min": "critical",
    "risk_level": "high",
    "suggested_alternative": "gate_d",
    "trend": "rising"
  }
  ```

---

#### 12. Fetch Single Incident Details
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/incidents/{incident_id}`
- **Description**: Fetches database records for a reported incident (Non-AI).
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**:
  - `incident_id`: String (e.g., `"inc_2a8b9c10"`)
- **Query Parameters**: None
- **Request Body**: None
- **Validation Rules**: Throws 404 if incident does not exist.
- **Example Request**:
  ```http
  GET /api/v1/incidents/inc_2a8b9c10 HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "id": "inc_2a8b9c10",
    "type": "medical",
    "location": "Concourse 2",
    "severity": "high",
    "description": "An elderly fan collapsed near the hot dog stand.",
    "status": "DISPATCHED",
    "response_time_minutes": 3,
    "assigned_staff": "stf_medical_01",
    "created_at": "2026-07-12T12:35:10.123456",
    "resolved_at": null
  }
  ```

---

#### 13. Transit Options
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/transport`
- **Description**: Queries transit departures, routes, recommendations, and localized traffic index.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**: None
- **Query Parameters**:
  - `location`: String (Required, starting location)
  - `destination`: String (Optional)
  - `mode`: String (Optional, e.g., `"Metro"`, `"Shuttle"`, `"Bus"`, `"Taxi"`)
- **Validation Rules**: Location parameter must be supplied.
- **Example Request**:
  ```http
  GET /api/v1/transport?location=gate_a&mode=Metro HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "options": [
      {
        "id": "tr_metro_01",
        "mode": "Metro",
        "destination": "Downtown Transit Center",
        "eta_minutes": 8,
        "recommendation_score": 9.2,
        "details": "Line 1 operating normal frequency. Platform access via East Gate."
      }
    ],
    "recommendation": {
      "id": "tr_metro_01",
      "mode": "Metro",
      "destination": "Downtown Transit Center",
      "eta_minutes": 8,
      "recommendation_score": 9.2,
      "details": "Line 1 operating normal frequency."
    },
    "traffic_level": "moderate"
  }
  ```

---

#### 14. Live Match Info
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/match/current`
- **Description**: Returns live scores, stats, and real-time events for the active match.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path/Query Parameters**: None
- **Request Body**: None
- **Example Request**:
  ```http
  GET /api/v1/match/current HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "id": "match_live_01",
    "team_a": "USA",
    "team_b": "England",
    "score_a": 1,
    "score_b": 0,
    "status": "live",
    "stadium": "MetLife Stadium",
    "kickoff_time": "19:00",
    "timeline": [
      {
        "minute": 34,
        "event_type": "goal",
        "player": "Christian Pulisic",
        "team": "USA",
        "detail": "Assisted by Weston McKennie"
      }
    ],
    "stats": {
      "possession_a": 48,
      "possession_b": 52,
      "shots_a": 6,
      "shots_b": 4,
      "fouls_a": 10,
      "fouls_b": 8
    }
  }
  ```

---

#### 15. Historical Match Details
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/match/{match_id}`
- **Description**: Fetches stats and events for a specific match ID.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**:
  - `match_id`: String (e.g., `"match_live_01"`)
- **Query Parameters**: None
- **Request Body**: None
- **Example Request**:
  ```http
  GET /api/v1/match/match_live_01 HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  - *(Same response schema as `/match/current`)*

---

#### 16. Eco Waste Classification
- **HTTP Method**: `POST`
- **Full Path**: `/api/v1/sustainability/waste`
- **Description**: Static lookup that returns recycling, composting, or landfill guides for discarded items.
- **Authentication Required**: No
- **Headers**:
  - `Content-Type: application/json`
- **Path/Query Parameters**:
  - `location`: String (Optional fallback location)
- **Request Body Schema**:
  - `item_description`: String (Required, e.g., `"banana peel"`)
  - `location`: String (Optional, current user coordinates or zone)
- **Example Request**:
  ```json
  {
    "item_description": "banana peel",
    "location": "gate_a"
  }
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "item_type": "Organic Waste",
    "bin_type": "Compost Bin (Green)",
    "bin_location": "Nearest Compost Bin (Green) is located near gate_a on the main concourse corridor.",
    "environmental_impact": "Converts organic food waste into rich nutrient compost, lowering methane emissions.",
    "disposal_tip": "Remove plastic cutlery or foil wrappers before disposing of food scraps."
  }
  ```

---

#### 17. Operational Accessibility Infrastructure
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/accessibility/{service_type}`
- **Description**: Returns operational availability, location, and wait times of elevators, ramps, and wheelchairs.
- **Authentication Required**: No
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**:
  - `service_type`: String (Must be one of: `elevator`, `ramp`, `restroom`, `hearing_loop`, `wheelchair_rental`)
- **Query Parameters**: None
- **Request Body**: None
- **Example Request**:
  ```http
  GET /api/v1/accessibility/elevator HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "services": [
      {
        "id": "acc_elv_01",
        "service_type": "elevator",
        "location": "Concourse Section 10",
        "status": "operational",
        "wait_time_minutes": 2
      }
    ],
    "nearest": {
      "id": "acc_elv_01",
      "service_type": "elevator",
      "location": "Concourse Section 10",
      "status": "operational",
      "wait_time_minutes": 2
    },
    "wait_time_minutes": 2
  }
  ```

---

#### 18. Retrieve Priority User Notifications
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/notifications/{user_id}`
- **Description**: Fetches emergency, priority, or staff alerts queue for a specific session code.
- **Authentication Required**: Yes
- **Headers**:
  - `Accept: application/json`
- **Path Parameters**:
  - `user_id`: String (Target user ID)
- **Example Request**:
  ```http
  GET /api/v1/notifications/usr_a1b2c3d4 HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "notifications": [
      {
        "id": "notif_01",
        "message": "Crowd bottleneck at Gate B. Use Gate D instead.",
        "priority": "warning",
        "is_read": false,
        "timestamp": "2026-07-12T12:35:10"
      }
    ],
    "unread_count": 1
  }
  ```

---

#### 19. Mark Notifications as Read
- **HTTP Method**: `POST`
- **Full Path**: `/api/v1/notifications/mark-read`
- **Description**: Updates list of targeted notifications as read.
- **Authentication Required**: Yes
- **Headers**:
  - `Content-Type: application/json`
- **Request Body Schema**:
  - `notification_ids`: List of Strings (Required)
- **Example Request**:
  ```json
  {
    "notification_ids": ["notif_01"]
  }
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "updated_count": 1
  }
  ```

---

### 5.5 Administrative Endpoints (Operations Staff Only)

---

#### 20. Admin Dashboard Overview
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/admin/dashboard`
- **Description**: Operations dashboard reporting unresolved incidents, overall crowd indicators, active staff count, and system notices.
- **Authentication Required**: No
- **Example Request**:
  ```http
  GET /api/v1/admin/dashboard HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "active_incidents": 3,
    "crowd_level": "High",
    "ai_queries_today": 320,
    "avg_response_time": 4.5,
    "staff_online": 18,
    "alerts": [
      {
        "id": "alert_1",
        "title": "Crowd Congestion",
        "message": "Heavy bottleneck building up at Gate B.",
        "severity": "warning",
        "timestamp": "2026-07-12T12:35:10.123456"
      }
    ]
  }
  ```

---

#### 21. Paginated Administrative Incident List
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/admin/incidents`
- **Description**: Returns a paginated list of incidents filtered by status, type, or priority.
- **Authentication Required**: No
- **Query Parameters**:
  - `status`: String (Optional, e.g., `"REPORTED"`, `"DISPATCHED"`, `"RESOLVED"`, `"CLOSED"`)
  - `type`: String (Optional, e.g., `"medical"`, `"fire"`, `"security"`)
  - `priority`: String (Optional, e.g., `"low"`, `"medium"`, `"high"`, `"critical"`)
  - `page`: Integer (Optional, default `1`, minimum `1`)
  - `limit`: Integer (Optional, default `10`, minimum `1`)
- **Example Request**:
  ```http
  GET /api/v1/admin/incidents?status=REPORTED&page=1&limit=5 HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "incidents": [
      {
        "id": "inc_2a8b9c10",
        "type": "medical",
        "location": "Concourse 2",
        "severity": "high",
        "description": "An elderly fan collapsed near the hot dog stand.",
        "status": "REPORTED",
        "response_time_minutes": 0,
        "assigned_staff": "None",
        "created_at": "2026-07-12T12:35:10",
        "resolved_at": null
      }
    ],
    "total": 1,
    "page": 1,
    "pages": 1
  }
  ```

---

#### 22. Update Incident Records
- **HTTP Method**: `PATCH`
- **Full Path**: `/api/v1/admin/incidents/{incident_id}`
- **Description**: Modifies status indicators, notes, priority levels, or assigns dispatch staff members.
- **Authentication Required**: No
- **Path Parameters**:
  - `incident_id`: String (Target incident)
- **Request Body Schema**:
  - `status`: String (Optional)
  - `assigned_staff`: String (Optional, Staff Member ID)
  - `notes`: String (Optional)
  - `priority`: String (Optional)
- **Example Request**:
  ```json
  {
    "status": "RESOLVED",
    "assigned_staff": "stf_medical_01"
  }
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "id": "inc_2a8b9c10",
    "status": "RESOLVED",
    "assigned_staff": "stf_medical_01",
    "updated_at": "2026-07-12T12:35:10.123456"
  }
  ```

---

#### 23. Detailed Crowd Analytics Metrics
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/admin/crowd/analytics`
- **Description**: Returns 10-minute density trends, predicted congestion slots, and live zones breakdown.
- **Authentication Required**: No
- **Query Parameters**:
  - `zone`: String (Optional)
- **Example Request**:
  ```http
  GET /api/v1/admin/crowd/analytics HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "trends": [
      {
        "time": "12:10",
        "density": 0.45
      }
    ],
    "peak_times": [
      {
        "time": "18:30",
        "density": 0.85,
        "zone": "zone_gate_b"
      }
    ],
    "predictions": [
      {
        "zone": "zone_gate_a",
        "time_15min": "12:50",
        "expected_density": 0.68
      }
    ],
    "zone_breakdown": [
      {
        "zone": "zone_gate_a",
        "density": 0.65,
        "status": "medium"
      }
    ]
  }
  ```

---

#### 24. Live Staff Workloads Listing
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/admin/staff`
- **Description**: Queries operational team statuses, workloads, and coordination coordinates.
- **Authentication Required**: No
- **Example Request**:
  ```http
  GET /api/v1/admin/staff HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "staff": [
      {
        "staff_id": "stf_medical_01",
        "name": "Dr. Sarah Jenkins",
        "role": "medical",
        "location": "Medical Post 1",
        "status": "available",
        "workload": 0
      }
    ],
    "total": 1,
    "available": 1,
    "busy": 0
  }
  ```

---

#### 25. Broadcast General Announcement
- **HTTP Method**: `POST`
- **Full Path**: `/api/v1/admin/announcements`
- **Description**: Triggers push notifications to staff subsets, volunteers, or zones.
- **Authentication Required**: No
- **Request Body Schema**:
  - `message`: String (Required)
  - `zones`: List of Strings (Optional)
  - `priority`: String (Required, e.g., `"info"`, `"warning"`, `"emergency"`)
  - `target_roles`: List of Strings (Optional, e.g., `["medical", "security"]`)
- **Example Request**:
  ```json
  {
    "message": "Emergency dispatch alert. Fire alarm testing starting on Level 2 in 10 minutes.",
    "priority": "emergency",
    "target_roles": ["security"]
  }
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "announcement_id": "ann_e7f3d9b0",
    "sent_count": 4,
    "timestamp": "2026-07-12T12:35:10.123456"
  }
  ```

---

#### 26. API Analytics Logs
- **HTTP Method**: `GET`
- **Full Path**: `/api/v1/admin/analytics/usage`
- **Description**: Tracks endpoint usage, latencies, and transaction volumes.
- **Authentication Required**: No
- **Query Parameters**:
  - `period`: String (Optional, select from: `1h`, `24h`, `7d`, `30d`. Defaults to `24h`)
- **Example Request**:
  ```http
  GET /api/v1/admin/analytics/usage?period=24h HTTP/1.1
  Host: localhost:8000
  ```
- **Example Success Response**:
  - **Status Code**: `200 OK`
  ```json
  {
    "api_calls": 420,
    "active_users": 65,
    "popular_features": [
      {
        "feature": "AI Chat Assistant",
        "count": 210
      }
    ],
    "error_rate": 0.015,
    "avg_latency": 132.4
  }
  ```

---

## 6. Google Gemini AI Integrations

The backend acts as the sole orchestrator for Gemini APIs.
- **Gemini is handled entirely on the backend.**
- **The frontend must never request a Gemini API key.**
- **The frontend must never call the Google Gemini API directly.**

### AI Endpoints Overview

| Endpoint | Purpose | Request Body Schema | Streaming Support | History / Persistence |
|---|---|---|---|---|
| `POST /api/v1/chat` | GenAI Concierge Chat Assistant. Resolves routes, stats, alerts. | `ChatRequest` (see schema below) | **No** (Synchronous API responses only) | Recorded directly in SQLite `conversations` table. Retrieve via `/users/{user_id}/history`. |
| `POST /api/v1/translate` | Translation with cultural context. | `TranslateRequest` | **No** | None |
| `POST /api/v1/incidents` | Classification of incident severity and type. | `IncidentRequest` | **No** | Saved in SQLite `incidents` table. |

### Chat Request & Response Details

#### Request Format (`ChatRequest`)
- `message` (String, Required): User query.
- `user_id` (String, Optional): Maps history logs to session.
- `language` (String, Optional): Explicit locale overrides.
- `location` (String, Optional): Sets starting coordinate node.
- `accessibility_mode` (Boolean, Optional): Enables step-free paths.

#### Response Format (`ChatResponse`)
- `response_text` (String): AI message.
- `actions` (Array): Declared functional operations triggered by AI tool calling.
- `route` (Object, Optional): Standard path metrics (if navigation was requested).
- `crowd_alert` (Object, Optional): Critical alerts if density surpasses 80%.

**Streaming Support**: Not currently supported. Responses block until fully generated by Gemini and the backend tools.
**Image/File Uploads**: Not supported on any AI endpoints.

---

## 7. File Upload APIs & WebSockets

### File Uploads
- **Status**: **Not Implemented / Not Available**.
- There are no endpoints for file or media uploads in the backend.

### WebSockets
- **Status**: **Not Implemented / Not Available**.
- All data exchanges use standard REST HTTP methods (polling models can be set up by the client on endpoints like `/crowd/all` if needed).

---

## 8. Environment Variables Required By Frontend

To configure the frontend client properly, define only the API base URL:

```env
# URL path to the FastAPI backend gateway
REACT_APP_API_BASE_URL=http://localhost:8000
# OR if using Vite:
VITE_API_BASE_URL=http://localhost:8000
# OR if using Next.js:
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

> [!IMPORTANT]
> **Never** expose `GEMINI_API_KEY` on the frontend environment files.

---

## 9. CORS (Cross-Origin Resource Sharing)

- **Configured Origin Rules**: Allowed origins are loaded dynamically from the `.env` variable `CORS_ORIGINS`.
- **Default (Dev)**: `*` (allows all origins, including localhost clients).
- **Production recommendation**: Restrict to the specific frontend build domain (e.g., `CORS_ORIGINS=https://stadiumai.world`).
- **Allowed Methods/Headers**: `["*"]` (allowing all standard HTTP headers and HTTP verbs).
- **Credentials Support**: Configured to `True` to allow cookies and request headers (like session user codes).

---

## 10. Swagger / OpenAPI 3.0.0 Specification

The following is the complete, production-ready OpenAPI 3.0.0 specification for the backend service. It can be saved as `openapi.yaml` to generate client libraries or display interactive docs.

```yaml
openapi: 3.0.0
info:
  title: StadiumAI Backend API
  description: Operations & Fan Experience GenAI Concierge Service for FIFA World Cup 2026
  version: 1.0.0
servers:
  - url: http://localhost:8000
    description: Local Development Server
paths:
  /api/v1/health:
    get:
      tags:
        - system
      summary: System Health
      description: Returns uptime, version, and timestamp.
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
  /api/v1/health/db:
    get:
      tags:
        - system
      summary: Database Health
      description: Verifies database query connection and latency.
      responses:
        '200':
          description: Database is connected
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DBHealthResponse'
        '500':
          description: DB connection error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/health/ai:
    get:
      tags:
        - system
      summary: AI Health
      description: Checks if the Gemini API key is configured.
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AIHealthResponse'
  /api/v1/users/session:
    post:
      tags:
        - users
      summary: Create Session
      description: Registers an anonymous session in the database.
      responses:
        '200':
          description: Session created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserSessionResponse'
  /api/v1/users/{user_id}/history:
    get:
      tags:
        - users
      summary: Session Chat History
      description: Fetches all messages and actions associated with a user session.
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: History retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserHistoryResponse'
        '404':
          description: Session not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/chat:
    post:
      tags:
        - chat
      summary: Chat Concierge
      description: Primary GenAI endpoint executing commands and responding via Gemini.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        '200':
          description: Concierge response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
        '503':
          description: Gemini disabled
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/navigate:
    post:
      tags:
        - navigation
      summary: Navigation Router
      description: Custom A* pathfinding route between two stadium checkpoints.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NavigateRequest'
      responses:
        '200':
          description: Navigation route computed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RouteResponse'
  /api/v1/crowd/all:
    get:
      tags:
        - crowd
      summary: Live Crowd Data
      description: Returns current densities and predictions for all concourses and gates.
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CrowdAllResponse'
  /api/v1/crowd/{zone_id}:
    get:
      tags:
        - crowd
      summary: Zone Crowd Details
      description: Fetches densities, predictions, and exit warnings for a specific zone.
      parameters:
        - name: zone_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CrowdZoneResponse'
  /api/v1/incidents:
    post:
      tags:
        - incidents
      summary: Report Incident
      description: Reports a safety issue and triggers dispatcher allocations.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IncidentRequest'
      responses:
        '200':
          description: Incident registered
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IncidentResponse'
        '503':
          description: Gemini classification error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/incidents/{incident_id}:
    get:
      tags:
        - incidents
      summary: Incident Details
      description: Fetches details for a single reported incident.
      parameters:
        - name: incident_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IncidentDetailResponse'
        '404':
          description: Incident not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/translate:
    post:
      tags:
        - translate
      summary: Translate Query
      description: Multilingual translation wrapper using Gemini with contextual parameters.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TranslateRequest'
      responses:
        '200':
          description: Translated text
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TranslateResponse'
        '503':
          description: Gemini error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/transport:
    get:
      tags:
        - transport
      summary: Transit Schedule
      description: Retrieves transit ETA schedules, scores, and traffic levels.
      parameters:
        - name: location
          in: query
          required: true
          schema:
            type: string
        - name: destination
          in: query
          required: false
          schema:
            type: string
        - name: mode
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: Transit schedules list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TransportResponse'
        '404':
          description: No options found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/match/current:
    get:
      tags:
        - match
      summary: Live Match Stats
      description: Returns live match score timelines and match statistics.
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MatchResponse'
        '404':
          description: No match scheduled
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/match/{match_id}:
    get:
      tags:
        - match
      summary: Historical Match Details
      description: Retrieves score statistics for a match by its unique identifier.
      parameters:
        - name: match_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MatchResponse'
        '404':
          description: Match not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/sustainability/waste:
    post:
      tags:
        - sustainability
      summary: Waste Classification
      description: Evaluates optimal disposal bins and impact details for waste.
      parameters:
        - name: location
          in: query
          required: false
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WasteRequest'
      responses:
        '200':
          description: Disposal guidelines
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WasteResponse'
  /api/v1/accessibility/{service_type}:
    get:
      tags:
        - accessibility
      summary: Accessibility Assets
      description: Checks functional availability of elevators, companion assets, and restrooms.
      parameters:
        - name: service_type
          in: path
          required: true
          schema:
            type: string
            enum: [elevator, ramp, restroom, hearing_loop, wheelchair_rental]
      responses:
        '200':
          description: Assets status listing
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AccessibilityResponse'
        '404':
          description: Asset type not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/notifications/{user_id}:
    get:
      tags:
        - notifications
      summary: Get Alerts Queue
      description: Fetches unread notifications for a user session.
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Notifications listed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotificationResponse'
  /api/v1/notifications/mark-read:
    post:
      tags:
        - notifications
      summary: Mark Notifications Read
      description: Marks selected notification IDs as read.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MarkReadRequest'
      responses:
        '200':
          description: Status updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MarkReadResponse'
  /api/v1/admin/dashboard:
    get:
      tags:
        - admin
      summary: Admin Metrics
      description: Get active incidents count, general crowd status, and online staff numbers.
      responses:
        '200':
          description: Operational statistics
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AdminDashboardResponse'
  /api/v1/admin/incidents:
    get:
      tags:
        - admin
      summary: List Logged Incidents
      description: Paginated and filtered overview of reported operations concerns.
      parameters:
        - name: status
          in: query
          required: false
          schema:
            type: string
        - name: type
          in: query
          required: false
          schema:
            type: string
        - name: priority
          in: query
          required: false
          schema:
            type: string
        - name: page
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            default: 10
      responses:
        '200':
          description: Paginated incident listing
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AdminIncidentListResponse'
  /api/v1/admin/incidents/{incident_id}:
    patch:
      tags:
        - admin
      summary: Update Incident Dispatch
      description: Change status, severity priority, or allocate staff coordinators to an incident.
      parameters:
        - name: incident_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IncidentUpdateRequest'
      responses:
        '200':
          description: Incident values modified
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IncidentUpdateResponse'
        '404':
          description: Incident ID not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
  /api/v1/admin/crowd/analytics:
    get:
      tags:
        - admin
      summary: Heavy Crowd Trends
      description: Detailed concourse density trends and prediction indexes.
      parameters:
        - name: zone
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: Analytics dashboard metrics
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AdminCrowdAnalyticsResponse'
  /api/v1/admin/staff:
    get:
      tags:
        - admin
      summary: Online Staff Roster
      description: Operational roster listing active workloads and status details.
      responses:
        '200':
          description: Staff details response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AdminStaffResponse'
  /api/v1/admin/announcements:
    post:
      tags:
        - admin
      summary: Broadcast Announcements
      description: Dispatches notices to specific zones or roles.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AnnouncementRequest'
      responses:
        '200':
          description: Broadcast complete
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnnouncementResponse'
  /api/v1/admin/analytics/usage:
    get:
      tags:
        - admin
      summary: Admin API Logs
      description: Tracks endpoint usage, latencies, and transaction volumes.
      parameters:
        - name: period
          in: query
          required: false
          schema:
            type: string
            default: 24h
      responses:
        '200':
          description: Usage statistics payload
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AdminUsageResponse'

components:
  schemas:
    HealthResponse:
      type: object
      properties:
        status:
          type: string
        uptime:
          type: number
        version:
          type: string
        timestamp:
          type: string
    DBHealthResponse:
      type: object
      properties:
        status:
          type: string
        connection_pool:
          type: integer
        latency_ms:
          type: number
    AIHealthResponse:
      type: object
      properties:
        status:
          type: string
        provider:
          type: string
        model:
          type: string
        last_response_time_ms:
          type: number
        quota_remaining:
          type: integer
          nullable: true
    ErrorResponse:
      type: object
      properties:
        detail:
          type: string
    UserSessionResponse:
      type: object
      properties:
        user_id:
          type: string
        created_at:
          type: string
    Action:
      type: object
      properties:
        type:
          type: string
        payload:
          type: object
    ConversationItem:
      type: object
      properties:
        role:
          type: string
        message:
          type: string
        intent:
          type: string
          nullable: true
        actions:
          type: array
          items:
            $ref: '#/components/schemas/Action'
        timestamp:
          type: string
    UserHistoryResponse:
      type: object
      properties:
        conversations:
          type: array
          items:
            $ref: '#/components/schemas/ConversationItem'
        total:
          type: integer
    ChatRequest:
      type: object
      required:
        - message
      properties:
        message:
          type: string
        user_id:
          type: string
          nullable: true
        language:
          type: string
          nullable: true
        location:
          type: string
          nullable: true
        accessibility_mode:
          type: boolean
          default: false
    AlternativeRoute:
      type: object
      properties:
        route:
          type: array
          items:
            type: string
        estimated_time_minutes:
          type: integer
        distance_meters:
          type: integer
        crowd_score:
          type: string
    RouteResponse:
      type: object
      properties:
        route:
          type: array
          items:
            type: string
        estimated_time_minutes:
          type: integer
        distance_meters:
          type: integer
        crowd_score:
          type: string
        alternative_routes:
          type: array
          items:
            $ref: '#/components/schemas/AlternativeRoute'
        accessibility_notes:
          type: string
          nullable: true
    CrowdAlert:
      type: object
      properties:
        zone_id:
          type: string
        density:
          type: number
        level:
          type: string
        message:
          type: string
    ChatResponse:
      type: object
      properties:
        response_text:
          type: string
        actions:
          type: array
          items:
            $ref: '#/components/schemas/Action'
        route:
          $ref: '#/components/schemas/RouteResponse'
          nullable: true
        crowd_alert:
          $ref: '#/components/schemas/CrowdAlert'
          nullable: true
        from_agent:
          type: boolean
    NavigateRequest:
      type: object
      required:
        - from_location
        - to_location
      properties:
        from_location:
          type: string
        to_location:
          type: string
        accessibility_mode:
          type: boolean
          default: false
        avoid_crowds:
          type: boolean
          default: false
    CrowdZoneResponse:
      type: object
      properties:
        zone_id:
          type: string
        current_density:
          type: number
        level:
          type: string
        prediction_5min:
          type: string
        prediction_15min:
          type: string
        risk_level:
          type: string
        suggested_alternative:
          type: string
          nullable: true
        trend:
          type: string
    CrowdAllResponse:
      type: object
      properties:
        zones:
          type: array
          items:
            $ref: '#/components/schemas/CrowdZoneResponse'
        timestamp:
          type: string
    IncidentRequest:
      type: object
      required:
        - type
        - location
        - description
      properties:
        type:
          type: string
        location:
          type: string
        description:
          type: string
        severity:
          type: string
          default: medium
        reporter_id:
          type: string
          nullable: true
    IncidentResponse:
      type: object
      properties:
        incident_id:
          type: string
        priority:
          type: string
        response_time_minutes:
          type: integer
        status:
          type: string
        assigned_staff:
          type: string
          nullable: true
    IncidentDetailResponse:
      type: object
      properties:
        id:
          type: string
        type:
          type: string
        location:
          type: string
        severity:
          type: string
        description:
          type: string
        status:
          type: string
        response_time_minutes:
          type: integer
        assigned_staff:
          type: string
        created_at:
          type: string
        resolved_at:
          type: string
          nullable: true
    TranslateRequest:
      type: object
      required:
        - text
        - target_lang
      properties:
        text:
          type: string
        source_lang:
          type: string
          nullable: true
        target_lang:
          type: string
        context:
          type: string
          nullable: true
    TranslateResponse:
      type: object
      properties:
        translated_text:
          type: string
        pronunciation_guide:
          type: string
          nullable: true
        cultural_note:
          type: string
          nullable: true
        detected_source_lang:
          type: string
          nullable: true
    TransportOption:
      type: object
      properties:
        id:
          type: string
        mode:
          type: string
        destination:
          type: string
        eta_minutes:
          type: integer
        recommendation_score:
          type: number
        details:
          type: string
          nullable: true
    TransportResponse:
      type: object
      properties:
        options:
          type: array
          items:
            $ref: '#/components/schemas/TransportOption'
        recommendation:
          $ref: '#/components/schemas/TransportOption'
        traffic_level:
          type: string
    MatchEvent:
      type: object
      properties:
        minute:
          type: integer
        event_type:
          type: string
        player:
          type: string
          nullable: true
        team:
          type: string
          nullable: true
        detail:
          type: string
          nullable: true
    MatchStats:
      type: object
      properties:
        possession_a:
          type: integer
        possession_b:
          type: integer
        shots_a:
          type: integer
        shots_b:
          type: integer
        fouls_a:
          type: integer
        fouls_b:
          type: integer
    MatchResponse:
      type: object
      properties:
        id:
          type: string
        team_a:
          type: string
        team_b:
          type: string
        score_a:
          type: integer
        score_b:
          type: integer
        status:
          type: string
        stadium:
          type: string
        kickoff_time:
          type: string
        timeline:
          type: array
          items:
            $ref: '#/components/schemas/MatchEvent'
        stats:
          $ref: '#/components/schemas/MatchStats'
    WasteRequest:
      type: object
      required:
        - item_description
      properties:
        item_description:
          type: string
        location:
          type: string
          nullable: true
    WasteResponse:
      type: object
      properties:
        item_type:
          type: string
        bin_type:
          type: string
        bin_location:
          type: string
        environmental_impact:
          type: string
        disposal_tip:
          type: string
    AccessibilityServiceItem:
      type: object
      properties:
        id:
          type: string
        service_type:
          type: string
        location:
          type: string
        status:
          type: string
        wait_time_minutes:
          type: integer
    AccessibilityResponse:
      type: object
      properties:
        services:
          type: array
          items:
            $ref: '#/components/schemas/AccessibilityServiceItem'
        nearest:
          $ref: '#/components/schemas/AccessibilityServiceItem'
        wait_time_minutes:
          type: integer
    NotificationItem:
      type: object
      properties:
        id:
          type: string
        message:
          type: string
        priority:
          type: string
        is_read:
          type: boolean
        timestamp:
          type: string
    NotificationResponse:
      type: object
      properties:
        notifications:
          type: array
          items:
            $ref: '#/components/schemas/NotificationItem'
        unread_count:
          type: integer
    MarkReadRequest:
      type: object
      required:
        - notification_ids
      properties:
        notification_ids:
          type: array
          items:
            type: string
    MarkReadResponse:
      type: object
      properties:
        updated_count:
          type: integer
    AlertItem:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        message:
          type: string
        severity:
          type: string
        timestamp:
          type: string
    AdminDashboardResponse:
      type: object
      properties:
        active_incidents:
          type: integer
        crowd_level:
          type: string
        ai_queries_today:
          type: integer
        avg_response_time:
          type: number
        staff_online:
          type: integer
        alerts:
          type: array
          items:
            $ref: '#/components/schemas/AlertItem'
    AdminIncidentListResponse:
      type: object
      properties:
        incidents:
          type: array
          items:
            $ref: '#/components/schemas/IncidentDetailResponse'
        total:
          type: integer
        page:
          type: integer
        pages:
          type: integer
    IncidentUpdateRequest:
      type: object
      properties:
        status:
          type: string
          nullable: true
        assigned_staff:
          type: string
          nullable: true
        notes:
          type: string
          nullable: true
        priority:
          type: string
          nullable: true
    IncidentUpdateResponse:
      type: object
      properties:
        id:
          type: string
        status:
          type: string
        assigned_staff:
          type: string
        updated_at:
          type: string
    TrendPoint:
      type: object
      properties:
        time:
          type: string
        density:
          type: number
    PeakTime:
      type: object
      properties:
        time:
          type: string
        density:
          type: number
        zone:
          type: string
    CrowdPrediction:
      type: object
      properties:
        zone:
          type: string
        time_15min:
          type: string
        expected_density:
          type: number
    ZoneBreakdown:
      type: object
      properties:
        zone:
          type: string
        density:
          type: number
        status:
          type: string
    AdminCrowdAnalyticsResponse:
      type: object
      properties:
        trends:
          type: array
          items:
            $ref: '#/components/schemas/TrendPoint'
        peak_times:
          type: array
          items:
            $ref: '#/components/schemas/PeakTime'
        predictions:
          type: array
          items:
            $ref: '#/components/schemas/CrowdPrediction'
        zone_breakdown:
          type: array
          items:
            $ref: '#/components/schemas/ZoneBreakdown'
    StaffMember:
      type: object
      properties:
        staff_id:
          type: string
        name:
          type: string
        role:
          type: string
        location:
          type: string
        status:
          type: string
        workload:
          type: integer
    AdminStaffResponse:
      type: object
      properties:
        staff:
          type: array
          items:
            $ref: '#/components/schemas/StaffMember'
        total:
          type: integer
        available:
          type: integer
        busy:
          type: integer
    AnnouncementRequest:
      type: object
      required:
        - message
        - priority
      properties:
        message:
          type: string
        zones:
          type: array
          items:
            type: string
          nullable: true
        priority:
          type: string
        target_roles:
          type: array
          items:
            type: string
          nullable: true
    AnnouncementResponse:
      type: object
      properties:
        announcement_id:
          type: string
        sent_count:
          type: integer
        timestamp:
          type: string
    FeatureStat:
      type: object
      properties:
        feature:
          type: string
        count:
          type: integer
    AdminUsageResponse:
      type: object
      properties:
        api_calls:
          type: integer
        active_users:
          type: integer
        popular_features:
          type: array
          items:
            $ref: '#/components/schemas/FeatureStat'
        error_rate:
          type: number
        avg_latency:
          type: number
