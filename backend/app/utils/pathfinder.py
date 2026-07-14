import math
import heapq
from typing import List, Dict, Tuple, Optional, Any
from app.data.stadium_graph import STADIUM_NODES, STADIUM_EDGES

def euclidean_distance(node1_id: str, node2_id: str) -> float:
    n1 = STADIUM_NODES.get(node1_id)
    n2 = STADIUM_NODES.get(node2_id)
    if not n1 or not n2:
        return 0.0
    return math.sqrt((n1["x"] - n2["x"])**2 + (n1["y"] - n2["y"])**2)

def get_crowd_penalty_multiplier(density: float) -> float:
    """
    Returns penalty percentage (e.g., 0.2 for 20% increase) based on crowd density.
    Crowd penalty: +20% per crowd level (medium, high, critical).
    Levels:
      - Low (density < 0.3): 0%
      - Medium (0.3 <= density < 0.7): +20% (0.2)
      - High (0.7 <= density < 0.9): +40% (0.4)
      - Critical (density >= 0.9): +60% (0.6)
    """
    if density >= 0.9:
        return 0.6
    elif density >= 0.7:
        return 0.4
    elif density >= 0.3:
        return 0.2
    return 0.0

def get_crowd_score_label(density: float) -> str:
    if density >= 0.9:
        return "Critical"
    elif density >= 0.7:
        return "High"
    elif density >= 0.3:
        return "Medium"
    return "Low"

def find_path(
    from_node: str,
    to_node: str,
    accessibility_mode: bool = False,
    avoid_crowds: bool = False,
    crowd_levels: Dict[str, float] = None, # zone_id -> density (0.0 to 1.0)
    ignored_edges: set = None
) -> Optional[Dict[str, Any]]:
    """
    Finds path between two nodes using A*.
    Returns a dict with:
      - route: list of node IDs
      - estimated_time_minutes: int
      - distance_meters: int
      - crowd_score: str
    """
    if from_node not in STADIUM_NODES or to_node not in STADIUM_NODES:
        return None
        
    if crowd_levels is None:
        crowd_levels = {}
    if ignored_edges is None:
        ignored_edges = set()

    # Build adjacency list
    adj = {node_id: [] for node_id in STADIUM_NODES}
    for edge in STADIUM_EDGES:
        f = edge["from_node"]
        t = edge["to_node"]
        
        # Check if edge is ignored
        if (f, t) in ignored_edges or (t, f) in ignored_edges:
            continue
            
        dist = edge["distance"]
        acc = edge["accessible"]
        zone = edge["crowd_multiplier_zone"]
        
        if accessibility_mode and not acc:
            continue
            
        adj[f].append((t, dist, acc, zone))

    # A* initialization
    g_score = {node_id: float('inf') for node_id in STADIUM_NODES}
    g_score[from_node] = 0.0
    
    dist_accum = {node_id: 0.0 for node_id in STADIUM_NODES}
    parents = {}
    
    pq = [(euclidean_distance(from_node, to_node), from_node)]
    visited = set()

    while pq:
        _, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        visited.add(current)

        if current == to_node:
            # Reconstruct route
            route = []
            curr = to_node
            while curr in parents:
                route.append(curr)
                curr = parents[curr]
            route.append(from_node)
            route.reverse()
            
            # Estimate actual distance and average crowd level
            distance = dist_accum[to_node]
            
            # Compute path crowd penalties and average density
            densities = []
            for i in range(len(route) - 1):
                n1, n2 = route[i], route[i+1]
                # Find matching edge zone
                zone = f"zone_{n1}"
                for edge in STADIUM_EDGES:
                    if (edge["from_node"] == n1 and edge["to_node"] == n2) or (edge["from_node"] == n2 and edge["to_node"] == n1):
                        zone = edge["crowd_multiplier_zone"]
                        break
                densities.append(crowd_levels.get(zone, 0.15))
            
            avg_density = sum(densities) / len(densities) if densities else 0.15
            crowd_score_label = get_crowd_score_label(avg_density)
            
            # Calculate time according to formula:
            # speed = 1.4 m/s
            # crowd penalty: +20% per level above low
            # accessibility penalty: +10% if accessibility_mode and elevator is used
            speed = 1.4
            crowd_penalty = get_crowd_penalty_multiplier(avg_density)
            
            # Check if any elevator was used in route
            has_elevator = any(STADIUM_NODES[node]["type"] == "elevator" for node in route)
            acc_penalty = 0.10 if (accessibility_mode and has_elevator) else 0.0
            
            # Time in seconds
            time_sec = (distance / speed) * (1.0 + crowd_penalty + acc_penalty)
            time_min = max(1, int(round(time_sec / 60.0)))
            
            return {
                "route": route,
                "estimated_time_minutes": time_min,
                "distance_meters": int(round(distance)),
                "crowd_score": crowd_score_label
            }

        for neighbor, dist, acc, zone in adj[current]:
            if neighbor in visited:
                continue
                
            # Weight calculation for routing choices (avoid crowds, accessibility, etc.)
            crowd_density = crowd_levels.get(zone, 0.15)
            crowd_mult = 1.0
            if avoid_crowds:
                # Add extra routing penalty for dense zones
                crowd_mult += get_crowd_penalty_multiplier(crowd_density) * 2.0  # double weight penalty for routing away

            acc_penalty = 1.0
            if accessibility_mode and STADIUM_NODES[neighbor]["type"] == "elevator":
                acc_penalty = 1.1
                
            weight = dist * crowd_mult * acc_penalty
            
            tentative_g = g_score[current] + weight
            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                dist_accum[neighbor] = dist_accum[current] + dist
                parents[neighbor] = current
                f_score = tentative_g + euclidean_distance(neighbor, to_node)
                heapq.heappush(pq, (f_score, neighbor))

    return None

def get_route_with_alternatives(
    from_node: str,
    to_node: str,
    accessibility_mode: bool = False,
    avoid_crowds: bool = False,
    crowd_levels: Dict[str, float] = None
) -> Optional[Dict[str, Any]]:
    """
    Computes primary route and up to 2 alternative routes by temporarily removing key links.
    """
    if crowd_levels is None:
        crowd_levels = {}
        
    primary = find_path(from_node, to_node, accessibility_mode, avoid_crowds, crowd_levels)
    if not primary:
        return None

    # Let's generate up to 2 alternative routes
    alternatives = []
    primary_route = primary["route"]
    
    # Try removing different segments along the path to find deviations
    if len(primary_route) > 3:
        # We can remove the middle edge
        mid_idx = len(primary_route) // 2
        edge_to_remove = (primary_route[mid_idx], primary_route[mid_idx+1])
        
        alt_res = find_path(
            from_node, to_node, accessibility_mode, avoid_crowds, crowd_levels,
            ignored_edges={edge_to_remove}
        )
        if alt_res and alt_res["route"] != primary_route:
            alternatives.append(alt_res)
            
        # Try removing another edge (e.g. closer to end) if we need a second alternative
        if len(primary_route) > 5:
            edge_to_remove_2 = (primary_route[-3], primary_route[-2])
            alt_res_2 = find_path(
                from_node, to_node, accessibility_mode, avoid_crowds, crowd_levels,
                ignored_edges={edge_to_remove_2, edge_to_remove}
            )
            if alt_res_2 and alt_res_2["route"] != primary_route and alt_res_2["route"] not in [a["route"] for a in alternatives]:
                alternatives.append(alt_res_2)

    # Format output consistent with API contract
    formatted_alternatives = []
    for alt in alternatives:
        formatted_alternatives.append({
            "route": alt["route"],
            "estimated_time_minutes": alt["estimated_time_minutes"],
            "distance_meters": alt["distance_meters"],
            "crowd_score": alt["crowd_score"]
        })

    # Accessibility notes
    accessibility_notes = None
    if accessibility_mode:
        has_elevator = any(STADIUM_NODES[n]["type"] == "elevator" for n in primary_route)
        if has_elevator:
            accessibility_notes = "Route uses elevators. Expect small delay for elevator wait times."
        else:
            accessibility_notes = "Accessible route via ground floor level concourse corridors."

    return {
        "route": primary["route"],
        "estimated_time_minutes": primary["estimated_time_minutes"],
        "distance_meters": primary["distance_meters"],
        "crowd_score": primary["crowd_score"],
        "alternative_routes": formatted_alternatives,
        "accessibility_notes": accessibility_notes
    }
