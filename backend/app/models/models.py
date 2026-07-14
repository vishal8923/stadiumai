from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.models.database import Base

class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String, default="fan")  # fan, volunteer, staff, organizer
    language = Column(String, default="en")
    accessibility_mode = Column(Boolean, default=False)
    ticket_info = Column(String, nullable=True)

class ConversationModel(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    role = Column(String)  # user, assistant
    message = Column(String)
    intent = Column(String, nullable=True)
    actions = Column(String, nullable=True)  # JSON-serialized list of Action
    timestamp = Column(DateTime, default=datetime.utcnow)

class IncidentModel(Base):
    __tablename__ = "incidents"
    incident_id = Column(String, primary_key=True, index=True)
    type = Column(String)  # medical, fire, security, lost_person, infrastructure
    location = Column(String)
    description = Column(String)
    severity = Column(String, default="medium")  # low, medium, high, critical
    priority = Column(String, default="medium")  # low, medium, high, critical
    status = Column(String, default="REPORTED")  # REPORTED, DISPATCHED, RESOLVED, CLOSED
    reporter_id = Column(String, nullable=True)
    assigned_staff = Column(String, nullable=True)  # Name or ID of assigned staff
    response_time_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class RouteModel(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_location = Column(String)
    to_location = Column(String)
    accessibility_mode = Column(Boolean, default=False)
    avoid_crowds = Column(Boolean, default=False)
    route_nodes = Column(String)  # JSON-serialized list of node IDs
    estimated_time_minutes = Column(Integer)
    distance_meters = Column(Integer)
    crowd_score = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CrowdDataModel(Base):
    __tablename__ = "crowd_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    zone_id = Column(String, index=True)
    current_density = Column(Float)  # 0.0 to 1.0
    level = Column(String)  # low, medium, high, critical
    prediction_5min = Column(String)
    prediction_15min = Column(String)
    risk_level = Column(String)
    suggested_alternative = Column(String, nullable=True)
    trend = Column(String)  # rising, falling, stable
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class KnowledgeItemModel(Base):
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String)  # faq, policies, food_menus, transport, emergency, accessibility
    question_or_keyword = Column(String)
    content = Column(String)

class MatchModel(Base):
    __tablename__ = "matches"
    id = Column(String, primary_key=True, index=True)
    team_a = Column(String)
    team_b = Column(String)
    score_a = Column(Integer, default=0)
    score_b = Column(Integer, default=0)
    status = Column(String)  # scheduled, live, completed
    stadium = Column(String)
    kickoff_time = Column(String)
    timeline = Column(String)  # JSON-serialized list of MatchEvent
    stats = Column(String)  # JSON-serialized MatchStats

class TransportModel(Base):
    __tablename__ = "transport"
    id = Column(String, primary_key=True, index=True)
    location = Column(String)
    destination = Column(String)
    mode = Column(String)  # bus, metro, shuttle, taxi, walking
    eta_minutes = Column(Integer)
    recommendation_score = Column(Float)
    traffic_level = Column(String)  # light, moderate, heavy
    details = Column(String, nullable=True)

class AccessibilityServiceModel(Base):
    __tablename__ = "accessibility_services"
    id = Column(String, primary_key=True, index=True)
    service_type = Column(String)  # elevator, ramp, restroom, hearing_loop, wheelchair_rental
    location = Column(String)
    status = Column(String)  # operational, maintenance, offline
    wait_time_minutes = Column(Integer, default=0)

class NotificationModel(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    message = Column(String)
    priority = Column(String, default="info")  # info, warning, emergency
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class StaffModel(Base):
    __tablename__ = "staff"
    staff_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)  # medical, security, volunteer, logistics
    location = Column(String)
    status = Column(String, default="available")  # available, busy, offline
    workload = Column(Integer, default=0)  # number of active incidents assigned

class AnalyticsModel(Base):
    __tablename__ = "analytics"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    endpoint = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    latency_ms = Column(Float)
    user_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
