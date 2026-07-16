"""SQLAlchemy ORM models for StadiumAI database tables."""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.models.database import Base


class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String, default="fan")
    language = Column(String, default="en")
    accessibility_mode = Column(Boolean, default=False)
    ticket_info = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<UserModel(user_id='{self.user_id}', role='{self.role}')>"


class ConversationModel(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    role = Column(String)
    message = Column(String)
    intent = Column(String, nullable=True)
    actions = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ConversationModel(id={self.id}, user_id='{self.user_id}', role='{self.role}')>"


class IncidentModel(Base):
    __tablename__ = "incidents"
    incident_id = Column(String, primary_key=True, index=True)
    type = Column(String)
    location = Column(String)
    description = Column(String)
    severity = Column(String, default="medium")
    priority = Column(String, default="medium")
    status = Column(String, default="REPORTED")
    reporter_id = Column(String, nullable=True)
    assigned_staff = Column(String, nullable=True)
    response_time_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<IncidentModel(incident_id='{self.incident_id}', type='{self.type}', status='{self.status}')>"


class RouteModel(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_location = Column(String)
    to_location = Column(String)
    accessibility_mode = Column(Boolean, default=False)
    avoid_crowds = Column(Boolean, default=False)
    route_nodes = Column(String)
    estimated_time_minutes = Column(Integer)
    distance_meters = Column(Integer)
    crowd_score = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RouteModel(id={self.id}, from='{self.from_location}', to='{self.to_location}')>"


class CrowdDataModel(Base):
    __tablename__ = "crowd_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    zone_id = Column(String, index=True)
    current_density = Column(Float)
    level = Column(String)
    prediction_5min = Column(String)
    prediction_15min = Column(String)
    risk_level = Column(String)
    suggested_alternative = Column(String, nullable=True)
    trend = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<CrowdDataModel(zone_id='{self.zone_id}', density={self.current_density}, level='{self.level}')>"


class KnowledgeItemModel(Base):
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String)
    question_or_keyword = Column(String)
    content = Column(String)

    def __repr__(self) -> str:
        return f"<KnowledgeItemModel(id={self.id}, category='{self.category}')>"


class MatchModel(Base):
    __tablename__ = "matches"
    id = Column(String, primary_key=True, index=True)
    team_a = Column(String)
    team_b = Column(String)
    score_a = Column(Integer, default=0)
    score_b = Column(Integer, default=0)
    status = Column(String)
    stadium = Column(String)
    kickoff_time = Column(String)
    timeline = Column(String)
    stats = Column(String)

    def __repr__(self) -> str:
        return f"<MatchModel(id='{self.id}', {self.team_a} vs {self.team_b}, status='{self.status}')>"


class TransportModel(Base):
    __tablename__ = "transport"
    id = Column(String, primary_key=True, index=True)
    location = Column(String)
    destination = Column(String)
    mode = Column(String)
    eta_minutes = Column(Integer)
    recommendation_score = Column(Float)
    traffic_level = Column(String)
    details = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<TransportModel(id='{self.id}', mode='{self.mode}', location='{self.location}')>"


class AccessibilityServiceModel(Base):
    __tablename__ = "accessibility_services"
    id = Column(String, primary_key=True, index=True)
    service_type = Column(String)
    location = Column(String)
    status = Column(String)
    wait_time_minutes = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<AccessibilityServiceModel(id='{self.id}', type='{self.service_type}', status='{self.status}')>"


class NotificationModel(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    message = Column(String)
    priority = Column(String, default="info")
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<NotificationModel(id='{self.id}', user_id='{self.user_id}', priority='{self.priority}')>"


class StaffModel(Base):
    __tablename__ = "staff"
    staff_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    location = Column(String)
    status = Column(String, default="available")
    workload = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<StaffModel(staff_id='{self.staff_id}', name='{self.name}', role='{self.role}')>"


class AnalyticsModel(Base):
    __tablename__ = "analytics"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    endpoint = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    latency_ms = Column(Float)
    user_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<AnalyticsModel(endpoint='{self.endpoint}', status_code={self.status_code})>"
