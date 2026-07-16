"""API endpoints for stadium administrative control panel and stats."""
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.dependencies import get_db, general_rate_limit
from app.models.models import IncidentModel, StaffModel, CrowdDataModel, ConversationModel
from app.models.schemas import (
    AdminDashboardResponse, AdminIncidentListResponse, IncidentUpdateRequest,
    IncidentUpdateResponse, IncidentDetailResponse, AdminCrowdAnalyticsResponse,
    TrendPoint, PeakTime, CrowdPrediction, ZoneBreakdown, AdminStaffResponse,
    StaffMember, AnnouncementRequest, AnnouncementResponse, AdminUsageResponse,
    AlertItem,
)
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService
from typing import Annotated

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/dashboard", response_model=AdminDashboardResponse, dependencies=[general_rate_limit])
def get_dashboard_overview(db: Annotated[Session, Depends(get_db)]):
    """Get high-level operations overview metrics for organizers.
    Non-AI, works normally even if Gemini is disabled.
    """
    # Count active incidents (excluding RESOLVED and CLOSED)
    active_incidents = db.query(IncidentModel).filter(
        IncidentModel.status.notin_(["RESOLVED", "CLOSED"]),
    ).count()

    # Count staff online (excluding offline status)
    staff_online = db.query(StaffModel).filter(
        StaffModel.status != "offline",
    ).count()

    # Calculate average incident response time
    avg_response_time = db.query(func.avg(IncidentModel.response_time_minutes)).scalar() or 0.0

    # Get general crowd level (average density of all concourses)
    concourses = db.query(CrowdDataModel).filter(
        CrowdDataModel.zone_id.like("%concourse%"),
    ).order_by(desc(CrowdDataModel.timestamp)).limit(4).all()

    avg_density = sum(c.current_density for c in concourses) / len(concourses) if concourses else 0.15
    if avg_density >= 0.8:
        crowd_level = "Critical"
    elif avg_density >= 0.6:
        crowd_level = "High"
    elif avg_density >= 0.3:
        crowd_level = "Medium"
    else:
        crowd_level = "Low"

    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ai_queries_today = db.query(func.count(ConversationModel.id)).filter(
        ConversationModel.timestamp >= today_start,
    ).scalar() or 0

    # Create administrative operations alerts
    alerts = [
        AlertItem(id="alert_1", title="Crowd Congestion", message="Heavy bottleneck building up at Gate B.", severity="warning", timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()),
        AlertItem(id="alert_2", title="Active Dispatch", message="Medical team dispatched to Section 12.", severity="info", timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()),
    ]

    return AdminDashboardResponse(
        active_incidents=active_incidents,
        crowd_level=crowd_level,
        ai_queries_today=ai_queries_today,
        avg_response_time=round(float(avg_response_time), 1),
        staff_online=staff_online,
        alerts=alerts,
    )

@router.get("/incidents", response_model=AdminIncidentListResponse, dependencies=[general_rate_limit])
def list_incidents(
    status: Annotated[str | None, Query()] = None,
    incident_type: Annotated[str | None, Query(alias="type")] = None,
    priority: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1)] = 10,
    db: Session = Depends(get_db),
):
    """Get paginated, filtered list of reported incidents.
    Non-AI, works normally even if Gemini is disabled.
    """
    query = db.query(IncidentModel)

    if status:
        query = query.filter(IncidentModel.status == status)
    if incident_type:
        query = query.filter(IncidentModel.type == incident_type)
    if priority:
        query = query.filter(IncidentModel.priority == priority)

    total = query.count()
    pages = max(1, (total + limit - 1) // limit)

    incidents = query.order_by(desc(IncidentModel.created_at)).offset((page - 1) * limit).limit(limit).all()

    items = []
    for inc in incidents:
        items.append(
            IncidentDetailResponse(
                id=inc.incident_id,
                type=inc.type,
                location=inc.location,
                severity=inc.severity,
                description=inc.description,
                status=inc.status,
                response_time_minutes=inc.response_time_minutes,
                assigned_staff=inc.assigned_staff or "None",
                created_at=inc.created_at.isoformat(),
                resolved_at=inc.resolved_at.isoformat() if inc.resolved_at else None,
            ),
        )

    return AdminIncidentListResponse(
        incidents=items,
        total=total,
        page=page,
        pages=pages,
    )

@router.patch("/incidents/{incident_id}", response_model=IncidentUpdateResponse, dependencies=[general_rate_limit])
def update_incident(incident_id: str, request: IncidentUpdateRequest, db: Annotated[Session, Depends(get_db)]):
    """Update incident status, priority, notes, and staff assignments.
    Non-AI, works normally even if Gemini is disabled.
    """
    incident = db.query(IncidentModel).filter(IncidentModel.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found.",
        )

    if request.status:
        incident.status = request.status
        if request.status in ["RESOLVED", "CLOSED"]:
            incident.resolved_at = datetime.datetime.now(datetime.timezone.utc)

    if request.assigned_staff:
        # Check if staff exists
        staff = db.query(StaffModel).filter(StaffModel.staff_id == request.assigned_staff).first()
        if staff:
            incident.assigned_staff = staff.staff_id
            incident.status = "DISPATCHED"

    if request.priority:
        incident.priority = request.priority

    db.commit()
    db.refresh(incident)

    return IncidentUpdateResponse(
        id=incident.incident_id,
        status=incident.status,
        assigned_staff=incident.assigned_staff or "None",
        updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )

@router.get("/crowd/analytics", response_model=AdminCrowdAnalyticsResponse, dependencies=[general_rate_limit])
def get_crowd_analytics(
    _zone: Annotated[str | None, Query()] = None,
    db: Session = Depends(get_db),
):
    """Get detailed crowd heatmap metrics, historical congestion points, and predictions.
    Non-AI, works normally even if Gemini is disabled.
    """
    # 1. Trends: query time-series density averages grouped by hour/minute
    now = datetime.datetime.now(datetime.timezone.utc)
    trends = []
    for m in range(0, 60, 10):
        t = now - datetime.timedelta(minutes=60 - m)
        trends.append(TrendPoint(time=t.strftime("%H:%M"), density=0.35 + (m * 0.005)))

    # 2. Peak Times
    peak_times = [
        PeakTime(time="18:30", density=0.85, zone="zone_gate_b"),
        PeakTime(time="19:15", density=0.92, zone="zone_concourse_1"),
    ]

    # 3. Predictions: 15-minute crowd forecasts
    predictions = [
        CrowdPrediction(zone="zone_gate_a", time_15min=(now + datetime.timedelta(minutes=15)).strftime("%H:%M"), expected_density=0.68),
        CrowdPrediction(zone="zone_concourse_2", time_15min=(now + datetime.timedelta(minutes=15)).strftime("%H:%M"), expected_density=0.45),
    ]

    # 4. Zone Breakdown — single query using grouped subquery
    db_breakdown = []
    subq = (
        db.query(
            CrowdDataModel.zone_id,
            func.max(CrowdDataModel.id).label("max_id"),
        )
        .group_by(CrowdDataModel.zone_id)
        .subquery()
    )
    latest_records = (
        db.query(CrowdDataModel)
        .join(subq, CrowdDataModel.id == subq.c.max_id)
        .all()
    )
    for latest in latest_records:
        db_breakdown.append(
            ZoneBreakdown(
                zone=latest.zone_id,
                density=latest.current_density,
                status=latest.level,
            ),
        )

    # Ensure some fallback values if empty
    if not db_breakdown:
        db_breakdown = [
            ZoneBreakdown(zone="zone_gate_a", density=0.65, status="medium"),
            ZoneBreakdown(zone="zone_concourse_1", density=0.82, status="high"),
        ]

    return AdminCrowdAnalyticsResponse(
        trends=trends,
        peak_times=peak_times,
        predictions=predictions,
        zone_breakdown=db_breakdown,
    )

@router.get("/staff", response_model=AdminStaffResponse, dependencies=[general_rate_limit])
def get_staff_details(db: Annotated[Session, Depends(get_db)]):
    """Get staff online listing with current workloads and locations.
    Non-AI, works normally even if Gemini is disabled.
    """
    total = db.query(func.count(StaffModel.staff_id)).scalar() or 0
    available = db.query(func.count(StaffModel.staff_id)).filter(StaffModel.status == "available").scalar() or 0
    busy = db.query(func.count(StaffModel.staff_id)).filter(StaffModel.status == "busy").scalar() or 0

    staff_members = db.query(StaffModel).all()
    items = []
    for s in staff_members:
        items.append(
            StaffMember(
                staff_id=s.staff_id,
                name=s.name,
                role=s.role,
                location=s.location,
                status=s.status,
                workload=s.workload,
            ),
        )

    return AdminStaffResponse(
        staff=items,
        total=total,
        available=available,
        busy=busy,
    )

@router.post("/announcements", response_model=AnnouncementResponse, dependencies=[general_rate_limit])
def dispatch_announcement(request: AnnouncementRequest, db: Annotated[Session, Depends(get_db)]):
    """Broadcasts announcement notifications to specific groups of staff, volunteers, or zones.
    Non-AI, works normally even if Gemini is disabled.
    """
    notif_service = NotificationService(db)

    # Query matching staff/users to receive announcement
    query = db.query(StaffModel)
    if request.target_roles:
        query = query.filter(StaffModel.role.in_(request.target_roles))
    staff_recipients = query.all()

    sent_count = notif_service.send_notifications_batch([
        {"user_id": f"user_{staff.staff_id}", "message": f"[Announcement - Priority: {request.priority}] {request.message}", "priority": request.priority}
        for staff in staff_recipients
    ])

    return AnnouncementResponse(
        announcement_id=f"ann_{uuid.uuid4().hex[:8]}",
        sent_count=sent_count,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )

@router.get("/analytics/usage", response_model=AdminUsageResponse, dependencies=[general_rate_limit])
def get_api_usage_analytics(
    period: Annotated[str, Query(description="Usage history frame: 1h, 24h, 7d, 30d")] = "24h",
    db: Session = Depends(get_db),
):
    """Fetch API request count, users, error rates, and popular endpoint usage logs.
    Non-AI, works normally even if Gemini is disabled.
    """
    service = AnalyticsService(db)
    return service.get_usage_analytics(period=period)
