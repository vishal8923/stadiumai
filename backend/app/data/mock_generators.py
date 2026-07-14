import json
import os
import datetime
import random
from sqlalchemy.orm import Session
from app.models.models import (
    UserModel, MatchModel, TransportModel, AccessibilityServiceModel, 
    StaffModel, CrowdDataModel, KnowledgeItemModel
)
from app.data.stadium_graph import STADIUM_NODES

DATA_DIR = os.path.dirname(__file__)

def seed_database(db: Session):
    """
    Seeds database with initial datasets if they don't already exist.
    """
    # Check if database is already populated
    if db.query(UserModel).count() > 0:
        return

    print("Seeding database with mock FIFA World Cup 2026 data...")

    # 1. Seed Users
    roles = ["fan", "volunteer", "staff", "organizer"]
    langs = ["en", "es", "fr", "pt"]
    users = []
    
    # Predefined users for testing
    users.append(UserModel(user_id="user_fan", role="fan", language="en", accessibility_mode=False, ticket_info="Section 10, Row F"))
    users.append(UserModel(user_id="user_staff", role="staff", language="en", accessibility_mode=False, ticket_info=None))
    users.append(UserModel(user_id="user_volunteer", role="volunteer", language="es", accessibility_mode=False, ticket_info=None))
    users.append(UserModel(user_id="user_accessible", role="fan", language="fr", accessibility_mode=True, ticket_info="Section 2, Row A"))

    for i in range(1, 10):
        users.append(
            UserModel(
                user_id=f"user_{i}",
                role=random.choice(roles),
                language=random.choice(langs),
                accessibility_mode=random.choice([True, False, False, False]),
                ticket_info=f"Section {random.randint(1, 32)}, Row {random.choice(['A','B','C','D'])}"
            )
        )
    db.add_all(users)
    db.commit()

    # 2. Seed Matches
    # Live Match (Argentina vs Mexico)
    live_timeline = [
        {"minute": 12, "event_type": "goal", "player": "Lionel Messi", "team": "Argentina", "detail": "Assisted by Rodrigo De Paul"},
        {"minute": 28, "event_type": "yellow_card", "player": "Hirving Lozano", "team": "Mexico", "detail": "Tactical foul"},
        {"minute": 44, "event_type": "substitution", "player": "Alexis Vega", "team": "Mexico", "detail": "Tactical change"}
    ]
    live_stats = {
        "possession_a": 58, "possession_b": 42,
        "shots_a": 9, "shots_b": 5,
        "fouls_a": 7, "fouls_b": 11
    }
    match_live = MatchModel(
        id="match_live",
        team_a="Argentina",
        team_b="Mexico",
        score_a=1,
        score_b=0,
        status="live",
        stadium="FIFA Stadium (Dallas)",
        kickoff_time="Live Now",
        timeline=json.dumps(live_timeline),
        stats=json.dumps(live_stats)
    )

    # Scheduled Match (USA vs England)
    scheduled_stats = {
        "possession_a": 0, "possession_b": 0,
        "shots_a": 0, "shots_b": 0,
        "fouls_a": 0, "fouls_b": 0
    }
    match_sched = MatchModel(
        id="match_scheduled",
        team_a="USA",
        team_b="England",
        score_a=0,
        score_b=0,
        status="scheduled",
        stadium="FIFA Stadium (Dallas)",
        kickoff_time="Tomorrow, 19:00",
        timeline=json.dumps([]),
        stats=json.dumps(scheduled_stats)
    )
    db.add_all([match_live, match_sched])
    db.commit()

    # 3. Seed Transport
    transport_options = [
        TransportModel(id="trans_metro_red", location="Gate C (East)", destination="Downtown / City Center", mode="Metro", eta_minutes=4, recommendation_score=0.92, traffic_level="light", details="Red Line Metro runs every 3 mins post-match. Wheelchair accessible platforms."),
        TransportModel(id="trans_shuttle_b", location="Gate G (West)", destination="Parking Lot B", mode="Shuttle", eta_minutes=6, recommendation_score=0.85, traffic_level="moderate", details="Continuous loops starting 3 hours pre-match."),
        TransportModel(id="trans_bus_101", location="Gate A (North)", destination="Airport Express", mode="Bus", eta_minutes=12, recommendation_score=0.74, traffic_level="moderate", details="Bus Route 101 runs hourly."),
        TransportModel(id="trans_taxi_stand", location="Gate E (South)", destination="Hotel District", mode="Taxi", eta_minutes=8, recommendation_score=0.68, traffic_level="heavy", details="Taxi rank with dispatcher assist.")
    ]
    db.add_all(transport_options)
    db.commit()

    # 4. Seed Accessibility Services
    accessibility_services = [
        AccessibilityServiceModel(id="elevator_1", service_type="elevator", location="Elevator 1 Lobby (North)", status="operational", wait_time_minutes=3),
        AccessibilityServiceModel(id="elevator_2", service_type="elevator", location="Elevator 2 Lobby (East)", status="operational", wait_time_minutes=2),
        AccessibilityServiceModel(id="elevator_3", service_type="elevator", location="Elevator 3 Lobby (South-East)", status="maintenance", wait_time_minutes=0),
        AccessibilityServiceModel(id="elevator_4", service_type="elevator", location="Elevator 4 Lobby (South-West)", status="operational", wait_time_minutes=4),
        AccessibilityServiceModel(id="elevator_5", service_type="elevator", location="Elevator 5 Lobby (West)", status="operational", wait_time_minutes=1),
        AccessibilityServiceModel(id="elevator_6", service_type="elevator", location="Elevator 6 Lobby (North-West)", status="operational", wait_time_minutes=2),
        AccessibilityServiceModel(id="ramp_north", service_type="ramp", location="Gate A Entrance Ramp", status="operational", wait_time_minutes=0),
        AccessibilityServiceModel(id="restroom_l1", service_type="restroom", location="Concourse 1 (near Section 4)", status="operational", wait_time_minutes=2),
        AccessibilityServiceModel(id="restroom_l2", service_type="restroom", location="Concourse 2 (near Section 12)", status="operational", wait_time_minutes=1),
        AccessibilityServiceModel(id="rental_desk", service_type="wheelchair_rental", location="Info Desk 1 (Gate A)", status="operational", wait_time_minutes=5)
    ]
    db.add_all(accessibility_services)
    db.commit()

    # 5. Seed Staff
    staff_members = [
        StaffModel(staff_id="staff_1", name="Carlos (Medical)", role="medical", location="medical_station_1", status="available", workload=0),
        StaffModel(staff_id="staff_2", name="Elena (Medical)", role="medical", location="medical_station_2", status="available", workload=0),
        StaffModel(staff_id="staff_3", name="John (Security)", role="security", location="concourse_1", status="available", workload=0),
        StaffModel(staff_id="staff_4", name="Marcus (Security)", role="security", location="concourse_3", status="available", workload=0),
        StaffModel(staff_id="staff_5", name="Sofia (Volunteer)", role="volunteer", location="info_desk_1", status="available", workload=0),
        StaffModel(staff_id="staff_6", name="David (Logistics)", role="logistics", location="concourse_4", status="available", workload=0)
    ]
    db.add_all(staff_members)
    db.commit()

    # 6. Seed Crowd Data (Multiple time entries to demonstrate trends)
    now = datetime.datetime.utcnow()
    crowd_entries = []
    
    # We populate data for all stadium nodes as zones
    for zone in STADIUM_NODES.keys():
        zone_id = f"zone_{zone}"
        # Set realistic baseline density (T-30 mins pre-match: high gates/concourses, low sections)
        base_density = 0.15
        if "gate" in zone:
            base_density = random.uniform(0.5, 0.8)
        elif "concourse" in zone:
            base_density = random.uniform(0.3, 0.6)
        elif "sec" in zone:
            base_density = random.uniform(0.1, 0.3)

        # Write 3 history points per zone to populate trends
        for diff_min in [30, 15, 0]:
            density = base_density
            # Simulate a rising trend for sections, stable/falling for gates
            if "sec" in zone:
                density += (30 - diff_min) * 0.015
            elif "gate" in zone:
                density -= (30 - diff_min) * 0.008
                
            density = max(0.05, min(0.98, density))
            
            level = "low"
            if density >= 0.9:
                level = "critical"
            elif density >= 0.7:
                level = "high"
            elif density >= 0.3:
                level = "medium"

            crowd_entries.append(
                CrowdDataModel(
                    zone_id=zone_id,
                    current_density=density,
                    level=level,
                    prediction_5min=level,
                    prediction_15min=level,
                    risk_level="low",
                    suggested_alternative=None,
                    trend="stable",
                    timestamp=now - datetime.timedelta(minutes=diff_min)
                )
            )

    db.add_all(crowd_entries)
    db.commit()

    # 7. Seed Knowledge Items from JSON files
    json_files = {
        "faq": "faq.json",
        "policies": "policies.json",
        "food_menus": "food_menus.json",
        "transport": "transport.json",
        "emergency": "emergency.json",
        "accessibility": "accessibility.json"
    }

    for category, filename in json_files.items():
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    for item in items:
                        # Map keys to standard Category/Keyword/Content format
                        q_kw = ""
                        content_str = ""
                        
                        if "question" in item:
                            q_kw = item["question"]
                            content_str = item["answer"]
                        elif "policy" in item:
                            q_kw = item["policy"]
                            content_str = item["description"]
                        elif "name" in item:
                            q_kw = item["name"]
                            content_str = f"Location: {item.get('location','')}. Menu items: " + ", ".join([f"{m.get('item','')} (${m.get('price','')})" for m in item.get("menu", [])])
                        elif "scenario" in item:
                            q_kw = item["scenario"]
                            content_str = f"Protocol: {item.get('protocol','')}. Assembly: {item.get('assembly_point','')}"
                        elif "service_type" in item:
                            q_kw = item["service_type"]
                            content_str = f"Location: {item.get('location','')}. Details: {item.get('details','')}"
                        elif "route" in item:
                            q_kw = item["route"]
                            content_str = f"Mode: {item.get('mode','')}. Details: {item.get('schedule_details','')}"

                        db.add(
                            KnowledgeItemModel(
                                category=category,
                                question_or_keyword=q_kw,
                                content=content_str
                            )
                        )
                db.commit()
            except Exception as e:
                print(f"Error seeding {category}: {e}")
                
    print("Database seeding completed successfully!")
