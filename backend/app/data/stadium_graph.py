# Stadium Graph Layout for FIFA World Cup 2026

STADIUM_NODES = {
    # 8 Gates
    "gate_a": {"name": "Gate A (North)", "x": 0.0, "y": 100.0, "type": "gate", "level": 1},
    "gate_b": {"name": "Gate B (North-East)", "x": 70.7, "y": 70.7, "type": "gate", "level": 1},
    "gate_c": {"name": "Gate C (East)", "x": 100.0, "y": 0.0, "type": "gate", "level": 1},
    "gate_d": {"name": "Gate D (South-East)", "x": 70.7, "y": -70.7, "type": "gate", "level": 1},
    "gate_e": {"name": "Gate E (South)", "x": 0.0, "y": -100.0, "type": "gate", "level": 1},
    "gate_f": {"name": "Gate F (South-West)", "x": -70.7, "y": -70.7, "type": "gate", "level": 1},
    "gate_g": {"name": "Gate G (West)", "x": -100.0, "y": 0.0, "type": "gate", "level": 1},
    "gate_h": {"name": "Gate H (North-West)", "x": -70.7, "y": 70.7, "type": "gate", "level": 1},

    # 4 Concourses (Level 1 main hallways)
    "concourse_1": {"name": "Concourse 1 (North)", "x": 0.0, "y": 60.0, "type": "concourse", "level": 1},
    "concourse_2": {"name": "Concourse 2 (East)", "x": 60.0, "y": 0.0, "type": "concourse", "level": 1},
    "concourse_3": {"name": "Concourse 3 (South)", "x": 0.0, "y": -60.0, "type": "concourse", "level": 1},
    "concourse_4": {"name": "Concourse 4 (West)", "x": -60.0, "y": 0.0, "type": "concourse", "level": 1},

    # 6 Elevators (Connecting Levels 1, 2, 3, 4)
    "elevator_1": {"name": "Elevator 1", "x": 30.0, "y": 50.0, "type": "elevator", "level": 1},
    "elevator_2": {"name": "Elevator 2", "x": 50.0, "y": 30.0, "type": "elevator", "level": 1},
    "elevator_3": {"name": "Elevator 3", "x": 30.0, "y": -50.0, "type": "elevator", "level": 1},
    "elevator_4": {"name": "Elevator 4", "x": -30.0, "y": -50.0, "type": "elevator", "level": 1},
    "elevator_5": {"name": "Elevator 5", "x": -50.0, "y": 30.0, "type": "elevator", "level": 1},
    "elevator_6": {"name": "Elevator 6", "x": -30.0, "y": 50.0, "type": "elevator", "level": 1},

    # Seating Sections (Level 1: 1-8, Level 2: 9-16, Level 3: 17-24, Level 4: 25-32)
    "sec_1": {"name": "Section 1", "x": 15.0, "y": 37.0, "type": "section", "level": 1},
    "sec_2": {"name": "Section 2", "x": 37.0, "y": 15.0, "type": "section", "level": 1},
    "sec_3": {"name": "Section 3", "x": 37.0, "y": -15.0, "type": "section", "level": 1},
    "sec_4": {"name": "Section 4", "x": 15.0, "y": -37.0, "type": "section", "level": 1},
    "sec_5": {"name": "Section 5", "x": -15.0, "y": -37.0, "type": "section", "level": 1},
    "sec_6": {"name": "Section 6", "x": -37.0, "y": -15.0, "type": "section", "level": 1},
    "sec_7": {"name": "Section 7", "x": -37.0, "y": 15.0, "type": "section", "level": 1},
    "sec_8": {"name": "Section 8", "x": -15.0, "y": 37.0, "type": "section", "level": 1},

    "sec_9": {"name": "Section 9", "x": 17.0, "y": 42.0, "type": "section", "level": 2},
    "sec_10": {"name": "Section 10", "x": 42.0, "y": 17.0, "type": "section", "level": 2},
    "sec_11": {"name": "Section 11", "x": 42.0, "y": -17.0, "type": "section", "level": 2},
    "sec_12": {"name": "Section 12", "x": 17.0, "y": -42.0, "type": "section", "level": 2},
    "sec_13": {"name": "Section 13", "x": -17.0, "y": -42.0, "type": "section", "level": 2},
    "sec_14": {"name": "Section 14", "x": -42.0, "y": -17.0, "type": "section", "level": 2},
    "sec_15": {"name": "Section 15", "x": -42.0, "y": 17.0, "type": "section", "level": 2},
    "sec_16": {"name": "Section 16", "x": -17.0, "y": 42.0, "type": "section", "level": 2},

    "sec_17": {"name": "Section 17", "x": 20.0, "y": 48.0, "type": "section", "level": 3},
    "sec_18": {"name": "Section 18", "x": 48.0, "y": 20.0, "type": "section", "level": 3},
    "sec_19": {"name": "Section 19", "x": 48.0, "y": -20.0, "type": "section", "level": 3},
    "sec_20": {"name": "Section 20", "x": 20.0, "y": -48.0, "type": "section", "level": 3},
    "sec_21": {"name": "Section 21", "x": -20.0, "y": -48.0, "type": "section", "level": 3},
    "sec_22": {"name": "Section 22", "x": -48.0, "y": -20.0, "type": "section", "level": 3},
    "sec_23": {"name": "Section 23", "x": -48.0, "y": 20.0, "type": "section", "level": 3},
    "sec_24": {"name": "Section 24", "x": -20.0, "y": 48.0, "type": "section", "level": 3},

    "sec_25": {"name": "Section 25", "x": 22.0, "y": 53.0, "type": "section", "level": 4},
    "sec_26": {"name": "Section 26", "x": 53.0, "y": 22.0, "type": "section", "level": 4},
    "sec_27": {"name": "Section 27", "x": 53.0, "y": -22.0, "type": "section", "level": 4},
    "sec_28": {"name": "Section 28", "x": 22.0, "y": -53.0, "type": "section", "level": 4},
    "sec_29": {"name": "Section 29", "x": -22.0, "y": -53.0, "type": "section", "level": 4},
    "sec_30": {"name": "Section 30", "x": -53.0, "y": -22.0, "type": "section", "level": 4},
    "sec_31": {"name": "Section 31", "x": -53.0, "y": 22.0, "type": "section", "level": 4},
    "sec_32": {"name": "Section 32", "x": -22.0, "y": 53.0, "type": "section", "level": 4},

    # Amenities
    "food_court_north": {"name": "Food Court North", "x": 0.0, "y": 55.0, "type": "amenity", "level": 1},
    "food_court_south": {"name": "Food Court South", "x": 0.0, "y": -55.0, "type": "amenity", "level": 1},
    "food_court_east": {"name": "Food Court East", "x": 55.0, "y": 0.0, "type": "amenity", "level": 1},
    "food_court_west": {"name": "Food Court West", "x": -55.0, "y": 0.0, "type": "amenity", "level": 1},

    "washroom_north": {"name": "Washrooms North", "x": 15.0, "y": 55.0, "type": "amenity", "level": 1},
    "washroom_south": {"name": "Washrooms South", "x": -15.0, "y": -55.0, "type": "amenity", "level": 1},

    "medical_station_1": {"name": "Medical Station 1", "x": 40.0, "y": 40.0, "type": "amenity", "level": 1},
    "medical_station_2": {"name": "Medical Station 2", "x": -40.0, "y": -40.0, "type": "amenity", "level": 1},

    "info_desk_1": {"name": "Info Desk 1", "x": 20.0, "y": 20.0, "type": "amenity", "level": 1},
    "info_desk_2": {"name": "Info Desk 2", "x": -20.0, "y": -20.0, "type": "amenity", "level": 1},

    "merchandise_1": {"name": "Merchandise Shop 1", "x": 45.0, "y": -45.0, "type": "amenity", "level": 1},
    "merchandise_2": {"name": "Merchandise Shop 2", "x": -45.0, "y": 45.0, "type": "amenity", "level": 1},
}

# Bidirectional edges to connect the entire graph
STADIUM_EDGES = []

def _add_edge(n1, n2, distance, *, accessible=True, zone=None):
    STADIUM_EDGES.append({
        "from_node": n1,
        "to_node": n2,
        "distance": distance,
        "accessible": accessible,
        "crowd_multiplier_zone": zone or f"zone_{n1}",
    })
    STADIUM_EDGES.append({
        "from_node": n2,
        "to_node": n1,
        "distance": distance,
        "accessible": accessible,
        "crowd_multiplier_zone": zone or f"zone_{n2}",
    })

# Connect Gates to Concourses (Level 1)
_add_edge("gate_a", "concourse_1", 40.0, accessible=True, zone="zone_gate_a")
_add_edge("gate_b", "concourse_1", 45.0, accessible=True, zone="zone_gate_b")
_add_edge("gate_b", "concourse_2", 45.0, accessible=True, zone="zone_gate_b")
_add_edge("gate_c", "concourse_2", 40.0, accessible=True, zone="zone_gate_c")
_add_edge("gate_d", "concourse_2", 45.0, accessible=True, zone="zone_gate_d")
_add_edge("gate_d", "concourse_3", 45.0, accessible=True, zone="zone_gate_d")
_add_edge("gate_e", "concourse_3", 40.0, accessible=True, zone="zone_gate_e")
_add_edge("gate_f", "concourse_3", 45.0, accessible=True, zone="zone_gate_f")
_add_edge("gate_f", "concourse_4", 45.0, accessible=True, zone="zone_gate_f")
_add_edge("gate_g", "concourse_4", 40.0, accessible=True, zone="zone_gate_g")
_add_edge("gate_h", "concourse_4", 45.0, accessible=True, zone="zone_gate_h")
_add_edge("gate_h", "concourse_1", 45.0, accessible=True, zone="zone_gate_h")

# Connect Concourses in a loop (Level 1)
_add_edge("concourse_1", "concourse_2", 84.8, accessible=True, zone="zone_concourse_1")
_add_edge("concourse_2", "concourse_3", 84.8, accessible=True, zone="zone_concourse_2")
_add_edge("concourse_3", "concourse_4", 84.8, accessible=True, zone="zone_concourse_3")
_add_edge("concourse_4", "concourse_1", 84.8, accessible=True, zone="zone_concourse_4")

# Connect Concourses to Level 1 Elevators and Amenities
_add_edge("concourse_1", "food_court_north", 10.0, accessible=True, zone="zone_amenities_north")
_add_edge("concourse_1", "washroom_north", 15.0, accessible=True, zone="zone_amenities_north")
_add_edge("concourse_1", "elevator_1", 31.6, accessible=True, zone="zone_concourse_1")
_add_edge("concourse_1", "elevator_6", 31.6, accessible=True, zone="zone_concourse_1")

_add_edge("concourse_2", "food_court_east", 10.0, accessible=True, zone="zone_amenities_east")
_add_edge("concourse_2", "medical_station_1", 28.2, accessible=True, zone="zone_amenities_east")
_add_edge("concourse_2", "elevator_2", 31.6, accessible=True, zone="zone_concourse_2")
_add_edge("concourse_2", "elevator_3", 58.3, accessible=True, zone="zone_concourse_2")

_add_edge("concourse_3", "food_court_south", 10.0, accessible=True, zone="zone_amenities_south")
_add_edge("concourse_3", "washroom_south", 15.0, accessible=True, zone="zone_amenities_south")
_add_edge("concourse_3", "elevator_3", 31.6, accessible=True, zone="zone_concourse_3")
_add_edge("concourse_3", "elevator_4", 31.6, accessible=True, zone="zone_concourse_3")

_add_edge("concourse_4", "food_court_west", 10.0, accessible=True, zone="zone_amenities_west")
_add_edge("concourse_4", "medical_station_2", 28.2, accessible=True, zone="zone_amenities_west")
_add_edge("concourse_4", "elevator_5", 31.6, accessible=True, zone="zone_concourse_4")
_add_edge("concourse_4", "elevator_4", 58.3, accessible=True, zone="zone_concourse_4")

# Additional Level 1 Amenities and Seating Links
_add_edge("concourse_1", "sec_1", 25.0, accessible=False, zone="zone_seating_l1")  # Seating sections have steps, not accessible by default
_add_edge("concourse_1", "sec_8", 25.0, accessible=False, zone="zone_seating_l1")
_add_edge("concourse_2", "sec_2", 25.0, accessible=False, zone="zone_seating_l1")
_add_edge("concourse_2", "sec_3", 25.0, accessible=False, zone="zone_seating_l1")
_add_edge("concourse_3", "sec_4", 25.0, accessible=False, zone="zone_seating_l1")
_add_edge("concourse_3", "sec_5", 25.0, accessible=False, zone="zone_seating_l1")
_add_edge("concourse_4", "sec_6", 25.0, accessible=False, zone="zone_seating_l1")
_add_edge("concourse_4", "sec_7", 25.0, accessible=False, zone="zone_seating_l1")

# Connect Level 1 Seating Sections in a loop
_add_edge("sec_1", "sec_2", 31.1, accessible=False, zone="zone_seating_l1")
_add_edge("sec_2", "sec_3", 30.0, accessible=False, zone="zone_seating_l1")
_add_edge("sec_3", "sec_4", 31.1, accessible=False, zone="zone_seating_l1")
_add_edge("sec_4", "sec_5", 30.0, accessible=False, zone="zone_seating_l1")
_add_edge("sec_5", "sec_6", 31.1, accessible=False, zone="zone_seating_l1")
_add_edge("sec_6", "sec_7", 30.0, accessible=False, zone="zone_seating_l1")
_add_edge("sec_7", "sec_8", 31.1, accessible=False, zone="zone_seating_l1")
_add_edge("sec_8", "sec_1", 30.0, accessible=False, zone="zone_seating_l1")

# Connect Elevators to Seating Levels (Stairs & Elevator accessibility paths)
# Elevator nodes act as vertical transport hubs.
# On Level 2, 3, 4, the elevator node name represents the level-specific lobby.
# For pathfinding, we connect elevator hubs to adjacent sections of each level.
# In a real stadium, elevators are accessible, while stairs are not.
# We'll connect elevator nodes on Level 1 to section nodes on Level 2, 3, 4 via stairs (non-accessible)
# and via elevator-only links (accessible).

# Level 2 Seating loop (sec_9 to sec_16)
_add_edge("sec_9", "sec_10", 35.0, accessible=False, zone="zone_seating_l2")
_add_edge("sec_10", "sec_11", 34.0, accessible=False, zone="zone_seating_l2")
_add_edge("sec_11", "sec_12", 35.0, accessible=False, zone="zone_seating_l2")
_add_edge("sec_12", "sec_13", 34.0, accessible=False, zone="zone_seating_l2")
_add_edge("sec_13", "sec_14", 35.0, accessible=False, zone="zone_seating_l2")
_add_edge("sec_14", "sec_15", 34.0, accessible=False, zone="zone_seating_l2")
_add_edge("sec_15", "sec_16", 35.0, accessible=False, zone="zone_seating_l2")
_add_edge("sec_16", "sec_9", 34.0, accessible=False, zone="zone_seating_l2")

# Level 3 Seating loop (sec_17 to sec_24)
_add_edge("sec_17", "sec_18", 40.0, accessible=False, zone="zone_seating_l3")
_add_edge("sec_18", "sec_19", 40.0, accessible=False, zone="zone_seating_l3")
_add_edge("sec_19", "sec_20", 40.0, accessible=False, zone="zone_seating_l3")
_add_edge("sec_20", "sec_21", 40.0, accessible=False, zone="zone_seating_l3")
_add_edge("sec_21", "sec_22", 40.0, accessible=False, zone="zone_seating_l3")
_add_edge("sec_22", "sec_23", 40.0, accessible=False, zone="zone_seating_l3")
_add_edge("sec_23", "sec_24", 40.0, accessible=False, zone="zone_seating_l3")
_add_edge("sec_24", "sec_17", 40.0, accessible=False, zone="zone_seating_l3")

# Level 4 Seating loop (sec_25 to sec_32)
_add_edge("sec_25", "sec_26", 45.0, accessible=False, zone="zone_seating_l4")
_add_edge("sec_26", "sec_27", 44.0, accessible=False, zone="zone_seating_l4")
_add_edge("sec_27", "sec_28", 45.0, accessible=False, zone="zone_seating_l4")
_add_edge("sec_28", "sec_29", 44.0, accessible=False, zone="zone_seating_l4")
_add_edge("sec_29", "sec_30", 45.0, accessible=False, zone="zone_seating_l4")
_add_edge("sec_30", "sec_31", 44.0, accessible=False, zone="zone_seating_l4")
_add_edge("sec_31", "sec_32", 45.0, accessible=False, zone="zone_seating_l4")
_add_edge("sec_32", "sec_25", 44.0, accessible=False, zone="zone_seating_l4")

# Connect Elevators to appropriate sections on higher levels (Accessible elevator links)
# Elevator 1 & 6 serve north sections (Level 2: 9,16; Level 3: 17,24; Level 4: 25,32)
# Elevator 2 serves east sections (Level 2: 10,11; Level 3: 18,19; Level 4: 26,27)
# Elevator 3 serves south/east sections
# Elevator 4 serves south/west sections
# Elevator 5 serves west sections

# Level 2 connections
_add_edge("elevator_1", "sec_9", 15.0, accessible=True, zone="zone_seating_l2")
_add_edge("elevator_1", "sec_16", 15.0, accessible=True, zone="zone_seating_l2")
_add_edge("elevator_2", "sec_10", 15.0, accessible=True, zone="zone_seating_l2")
_add_edge("elevator_3", "sec_11", 15.0, accessible=True, zone="zone_seating_l2")
_add_edge("elevator_3", "sec_12", 15.0, accessible=True, zone="zone_seating_l2")
_add_edge("elevator_4", "sec_13", 15.0, accessible=True, zone="zone_seating_l2")
_add_edge("elevator_5", "sec_14", 15.0, accessible=True, zone="zone_seating_l2")
_add_edge("elevator_5", "sec_15", 15.0, accessible=True, zone="zone_seating_l2")
_add_edge("elevator_6", "sec_16", 15.0, accessible=True, zone="zone_seating_l2")

# Level 3 connections
_add_edge("elevator_1", "sec_17", 20.0, accessible=True, zone="zone_seating_l3")
_add_edge("elevator_1", "sec_24", 20.0, accessible=True, zone="zone_seating_l3")
_add_edge("elevator_2", "sec_18", 20.0, accessible=True, zone="zone_seating_l3")
_add_edge("elevator_3", "sec_19", 20.0, accessible=True, zone="zone_seating_l3")
_add_edge("elevator_3", "sec_20", 20.0, accessible=True, zone="zone_seating_l3")
_add_edge("elevator_4", "sec_21", 20.0, accessible=True, zone="zone_seating_l3")
_add_edge("elevator_5", "sec_22", 20.0, accessible=True, zone="zone_seating_l3")
_add_edge("elevator_5", "sec_23", 20.0, accessible=True, zone="zone_seating_l3")
_add_edge("elevator_6", "sec_24", 20.0, accessible=True, zone="zone_seating_l3")

# Level 4 connections
_add_edge("elevator_1", "sec_25", 25.0, accessible=True, zone="zone_seating_l4")
_add_edge("elevator_1", "sec_32", 25.0, accessible=True, zone="zone_seating_l4")
_add_edge("elevator_2", "sec_26", 25.0, accessible=True, zone="zone_seating_l4")
_add_edge("elevator_3", "sec_27", 25.0, accessible=True, zone="zone_seating_l4")
_add_edge("elevator_3", "sec_28", 25.0, accessible=True, zone="zone_seating_l4")
_add_edge("elevator_4", "sec_29", 25.0, accessible=True, zone="zone_seating_l4")
_add_edge("elevator_5", "sec_30", 25.0, accessible=True, zone="zone_seating_l4")
_add_edge("elevator_5", "sec_31", 25.0, accessible=True, zone="zone_seating_l4")
_add_edge("elevator_6", "sec_32", 25.0, accessible=True, zone="zone_seating_l4")

# Info Desk connections (Level 1)
_add_edge("info_desk_1", "sec_1", 20.0, accessible=True, zone="zone_amenities_north")
_add_edge("info_desk_1", "sec_2", 20.0, accessible=True, zone="zone_amenities_north")
_add_edge("info_desk_2", "sec_5", 20.0, accessible=True, zone="zone_amenities_south")
_add_edge("info_desk_2", "sec_6", 20.0, accessible=True, zone="zone_amenities_south")

# Merchandise connections (Level 1)
_add_edge("merchandise_1", "sec_3", 15.0, accessible=True, zone="zone_amenities_east")
_add_edge("merchandise_2", "sec_7", 15.0, accessible=True, zone="zone_amenities_west")
