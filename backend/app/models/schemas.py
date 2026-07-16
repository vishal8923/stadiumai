from pydantic import BaseModel
from typing import Any

# Common Models
class Action(BaseModel):
    type: str
    payload: dict[str, Any]

class AlternativeRoute(BaseModel):
    route: list[str]
    estimated_time_minutes: int
    distance_meters: int
    crowd_score: str

class RouteResponse(BaseModel):
    route: list[str]
    estimated_time_minutes: int
    distance_meters: int
    crowd_score: str
    alternative_routes: list[AlternativeRoute]
    accessibility_notes: str | None = None

class CrowdAlert(BaseModel):
    zone_id: str
    density: float
    level: str
    message: str

# 1. Chat
class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None
    language: str | None = None
    location: str | None = None
    accessibility_mode: bool | None = False

class ChatResponse(BaseModel):
    response_text: str
    actions: list[Action] = []
    route: RouteResponse | None = None
    crowd_alert: CrowdAlert | None = None
    from_agent: bool = False

# 2. Navigation
class NavigateRequest(BaseModel):
    from_location: str
    to_location: str
    accessibility_mode: bool | None = False
    avoid_crowds: bool | None = False



# 3. Crowd Zone
class CrowdZoneResponse(BaseModel):
    zone_id: str
    current_density: float
    level: str
    prediction_5min: str
    prediction_15min: str
    risk_level: str
    suggested_alternative: str | None = None
    trend: str

class CrowdAllResponse(BaseModel):
    zones: list[CrowdZoneResponse]
    timestamp: str

# 4. Translation
class TranslateRequest(BaseModel):
    text: str
    source_lang: str | None = None
    target_lang: str
    context: str | None = None

class TranslateResponse(BaseModel):
    translated_text: str
    pronunciation_guide: str | None = None
    cultural_note: str | None = None
    detected_source_lang: str | None = None

# 5. Incidents
class IncidentRequest(BaseModel):
    type: str
    location: str
    description: str
    severity: str | None = "medium"
    reporter_id: str | None = None

class IncidentResponse(BaseModel):
    incident_id: str
    priority: str
    response_time_minutes: int
    status: str
    assigned_staff: str | None = None

class IncidentDetailResponse(BaseModel):
    id: str
    type: str
    location: str
    severity: str
    description: str
    status: str
    response_time_minutes: int
    assigned_staff: str
    created_at: str
    resolved_at: str | None = None

# 6. Transport
class TransportOption(BaseModel):
    id: str
    mode: str
    destination: str
    eta_minutes: int
    recommendation_score: float
    details: str | None = None

class TransportResponse(BaseModel):
    options: list[TransportOption]
    recommendation: TransportOption
    traffic_level: str

# 7. Match Info
class MatchEvent(BaseModel):
    minute: int
    event_type: str
    player: str | None = None
    team: str | None = None
    detail: str | None = None

class MatchStats(BaseModel):
    possession_a: int
    possession_b: int
    shots_a: int
    shots_b: int
    fouls_a: int
    fouls_b: int

class MatchResponse(BaseModel):
    id: str
    team_a: str
    team_b: str
    score_a: int
    score_b: int
    status: str
    stadium: str
    kickoff_time: str
    timeline: list[MatchEvent]
    stats: MatchStats

# 8. Sustainability Waste
class WasteRequest(BaseModel):
    item_description: str
    location: str | None = None

class WasteResponse(BaseModel):
    item_type: str
    bin_type: str
    bin_location: str
    environmental_impact: str
    disposal_tip: str

# 9. Accessibility
class AccessibilityServiceItem(BaseModel):
    id: str
    service_type: str
    location: str
    status: str
    wait_time_minutes: int

class AccessibilityResponse(BaseModel):
    services: list[AccessibilityServiceItem]
    nearest: AccessibilityServiceItem
    wait_time_minutes: int

# 10. Users Session
class UserSessionResponse(BaseModel):
    user_id: str
    created_at: str

# 11. Conversation History
class ConversationItem(BaseModel):
    role: str
    message: str
    intent: str | None = None
    actions: list[Action] = []
    timestamp: str

class UserHistoryResponse(BaseModel):
    conversations: list[ConversationItem]
    total: int

# 12. Notifications
class NotificationItem(BaseModel):
    id: str
    message: str
    priority: str
    is_read: bool
    timestamp: str

class NotificationResponse(BaseModel):
    notifications: list[NotificationItem]
    unread_count: int

class MarkReadRequest(BaseModel):
    notification_ids: list[str]

class MarkReadResponse(BaseModel):
    updated_count: int

# 13. Admin Dashboard
class AlertItem(BaseModel):
    id: str
    title: str
    message: str
    severity: str
    timestamp: str

class AdminDashboardResponse(BaseModel):
    active_incidents: int
    crowd_level: str
    ai_queries_today: int
    avg_response_time: float
    staff_online: int
    alerts: list[AlertItem]

# 14. Admin Incidents
class AdminIncidentListResponse(BaseModel):
    incidents: list[IncidentDetailResponse]
    total: int
    page: int
    pages: int

class IncidentUpdateRequest(BaseModel):
    status: str | None = None
    assigned_staff: str | None = None
    notes: str | None = None
    priority: str | None = None

class IncidentUpdateResponse(BaseModel):
    id: str
    status: str
    assigned_staff: str
    updated_at: str

# 15. Admin Crowd Analytics
class TrendPoint(BaseModel):
    time: str
    density: float

class PeakTime(BaseModel):
    time: str
    density: float
    zone: str

class CrowdPrediction(BaseModel):
    zone: str
    time_15min: str
    expected_density: float

class ZoneBreakdown(BaseModel):
    zone: str
    density: float
    status: str

class AdminCrowdAnalyticsResponse(BaseModel):
    trends: list[TrendPoint]
    peak_times: list[PeakTime]
    predictions: list[CrowdPrediction]
    zone_breakdown: list[ZoneBreakdown]

# 16. Admin Staff
class StaffMember(BaseModel):
    staff_id: str
    name: str
    role: str
    location: str
    status: str
    workload: int

class AdminStaffResponse(BaseModel):
    staff: list[StaffMember]
    total: int
    available: int
    busy: int

# 17. Admin Announcements
class AnnouncementRequest(BaseModel):
    message: str
    zones: list[str] | None = None
    priority: str
    target_roles: list[str] | None = None

class AnnouncementResponse(BaseModel):
    announcement_id: str
    sent_count: int
    timestamp: str

# 18. Admin Usage Analytics
class FeatureStat(BaseModel):
    feature: str
    count: int

class AdminUsageResponse(BaseModel):
    api_calls: int
    active_users: int
    popular_features: list[FeatureStat]
    error_rate: float
    avg_latency: float

# 19. Health Response
class HealthResponse(BaseModel):
    status: str
    uptime: float
    version: str
    timestamp: str

class DBHealthResponse(BaseModel):
    status: str
    connection_pool: int
    latency_ms: float

class AIHealthResponse(BaseModel):
    status: str
    provider: str
    last_response_time_ms: float
    quota_remaining: int | None = None
