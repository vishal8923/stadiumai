from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Common Models
class Action(BaseModel):
    type: str
    payload: Dict[str, Any]

class AlternativeRoute(BaseModel):
    route: List[str]
    estimated_time_minutes: int
    distance_meters: int
    crowd_score: str

class RouteResponse(BaseModel):
    route: List[str]
    estimated_time_minutes: int
    distance_meters: int
    crowd_score: str
    alternative_routes: List[AlternativeRoute]
    accessibility_notes: Optional[str] = None

class CrowdAlert(BaseModel):
    zone_id: str
    density: float
    level: str
    message: str

# 1. Chat
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    language: Optional[str] = None
    location: Optional[str] = None
    accessibility_mode: Optional[bool] = False

class ChatResponse(BaseModel):
    response_text: str
    actions: List[Action] = []
    route: Optional[RouteResponse] = None
    crowd_alert: Optional[CrowdAlert] = None
    from_agent: bool = False

# 2. Navigation
class NavigateRequest(BaseModel):
    from_location: str
    to_location: str
    accessibility_mode: Optional[bool] = False
    avoid_crowds: Optional[bool] = False

# 3. Crowd Zone
class CrowdZoneResponse(BaseModel):
    zone_id: str
    current_density: float
    level: str
    prediction_5min: str
    prediction_15min: str
    risk_level: str
    suggested_alternative: Optional[str] = None
    trend: str

class CrowdAllResponse(BaseModel):
    zones: List[CrowdZoneResponse]
    timestamp: str

# 4. Translation
class TranslateRequest(BaseModel):
    text: str
    source_lang: Optional[str] = None
    target_lang: str
    context: Optional[str] = None

class TranslateResponse(BaseModel):
    translated_text: str
    pronunciation_guide: Optional[str] = None
    cultural_note: Optional[str] = None
    detected_source_lang: Optional[str] = None

# 5. Incidents
class IncidentRequest(BaseModel):
    type: str
    location: str
    description: str
    severity: Optional[str] = "medium"
    reporter_id: Optional[str] = None

class IncidentResponse(BaseModel):
    incident_id: str
    priority: str
    response_time_minutes: int
    status: str
    assigned_staff: Optional[str] = None

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
    resolved_at: Optional[str] = None

# 6. Transport
class TransportOption(BaseModel):
    id: str
    mode: str
    destination: str
    eta_minutes: int
    recommendation_score: float
    details: Optional[str] = None

class TransportResponse(BaseModel):
    options: List[TransportOption]
    recommendation: TransportOption
    traffic_level: str

# 7. Match Info
class MatchEvent(BaseModel):
    minute: int
    event_type: str
    player: Optional[str] = None
    team: Optional[str] = None
    detail: Optional[str] = None

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
    timeline: List[MatchEvent]
    stats: MatchStats

# 8. Sustainability Waste
class WasteRequest(BaseModel):
    item_description: str
    location: Optional[str] = None

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
    services: List[AccessibilityServiceItem]
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
    intent: Optional[str] = None
    actions: List[Action] = []
    timestamp: str

class UserHistoryResponse(BaseModel):
    conversations: List[ConversationItem]
    total: int

# 12. Notifications
class NotificationItem(BaseModel):
    id: str
    message: str
    priority: str
    is_read: bool
    timestamp: str

class NotificationResponse(BaseModel):
    notifications: List[NotificationItem]
    unread_count: int

class MarkReadRequest(BaseModel):
    notification_ids: List[str]

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
    alerts: List[AlertItem]

# 14. Admin Incidents
class AdminIncidentListResponse(BaseModel):
    incidents: List[IncidentDetailResponse]
    total: int
    page: int
    pages: int

class IncidentUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_staff: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None

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
    trends: List[TrendPoint]
    peak_times: List[PeakTime]
    predictions: List[CrowdPrediction]
    zone_breakdown: List[ZoneBreakdown]

# 16. Admin Staff
class StaffMember(BaseModel):
    staff_id: str
    name: str
    role: str
    location: str
    status: str
    workload: int

class AdminStaffResponse(BaseModel):
    staff: List[StaffMember]
    total: int
    available: int
    busy: int

# 17. Admin Announcements
class AnnouncementRequest(BaseModel):
    message: str
    zones: Optional[List[str]] = None
    priority: str
    target_roles: Optional[List[str]] = None

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
    popular_features: List[FeatureStat]
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
    quota_remaining: Optional[int] = None
