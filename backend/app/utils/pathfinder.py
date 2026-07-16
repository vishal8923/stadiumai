import math
import heapq
from typing import Any
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from app.data.stadium_graph import STADIUM_NODES, STADIUM_EDGES

pathfinding_cache = TTLCache(maxsize=100, ttl=60)

def pathfinding_key(from_node: str, to_node: str, *, accessibility_mode: bool = False, avoid_crowds: bool = False, crowd_levels: dict[str, float] | None = None):
    crowd_tuple = tuple(sorted(crowd_levels.items())) if crowd_levels else ()
    return hashkey(from_node, to_node, accessibility_mode, avoid_crowds, crowd_tuple)

def euclidean_distance(node1_id: str, node2_id: str) -> float:
    n1 = STADIUM_NODES.get(node1_id)
    n2 = STADIUM_NODES.get(node2_id)
    if not n1 or not n2:
        return 0.0
    return math.sqrt((n1["x"] - n2["x"])**2 + (n1["y"] - n2["y"])**2)

def get_crowd_penalty_multiplier(density: float) -> float:
    if density >= 0.9:
        return 0.6
    if density >= 0.7:
        return 0.4
    if density >= 0.3:
        return 0.2
    return 0.0

def get_crowd_score_label(density: float) -> str:
    if density >= 0.9:
        return "Critical"
    if density >= 0.7:
        return "High"
    if density >= 0.3:
        return "Medium"
    return "Low"

def _build_adjacency_list(
    accessibility_mode: bool,  # noqa: FBT001
    ignored_edges: set,
) -> dict[str, list]:
    adj = {node_id: [] for node_id in STADIUM_NODES}
    for edge in STADIUM_EDGES:
        f = edge["from_node"]
        t = edge["to_node"]
        if (f, t) in ignored_edges or (t, f) in ignored_edges:
            continue
        dist = edge["distance"]
        acc = edge["accessible"]
        zone = edge["crowd_multiplier_zone"]
        if accessibility_mode and not acc:
            continue
        adj[f].append((t, dist, acc, zone))
    return adj

def _reconstruct_path_result(
    to_node: str,
    from_node: str,
    parents: dict,
    dist_accum: dict,
    *,
    accessibility_mode: bool,
    crowd_levels: dict[str, float],
) -> dict[str, Any]:
    route = []
    curr = to_node
    while curr in parents:
        route.append(curr)
        curr = parents[curr]
    route.append(from_node)
    route.reverse()

    distance = dist_accum[to_node]
    densities = []
    for i in range(len(route) - 1):
        n1, n2 = route[i], route[i + 1]
        zone = f"zone_{n1}"
        for edge in STADIUM_EDGES:
            if (edge["from_node"] == n1 and edge["to_node"] == n2) or (edge["from_node"] == n2 and edge["to_node"] == n1):
                zone = edge["crowd_multiplier_zone"]
                break
        densities.append(crowd_levels.get(zone, 0.15))

    avg_density = sum(densities) / len(densities) if densities else 0.15
    crowd_score_label = get_crowd_score_label(avg_density)
    speed = 1.4
    crowd_penalty = get_crowd_penalty_multiplier(avg_density)
    has_elevator = any(STADIUM_NODES[node]["type"] == "elevator" for node in route)
    acc_penalty = 0.10 if (accessibility_mode and has_elevator) else 0.0
    time_sec = (distance / speed) * (1.0 + crowd_penalty + acc_penalty)
    time_min = max(1, round(time_sec / 60.0))

    return {
        "route": route,
        "estimated_time_minutes": time_min,
        "distance_meters": round(distance),
        "crowd_score": crowd_score_label,
    }

def _process_neighbor(
    current: str,
    neighbor: str,
    dist: float,
    zone: str,
    g_score: dict,
    dist_accum: dict,
    parents: dict,
    pq: list,
    to_node: str,
    *,
    avoid_crowds: bool,
    accessibility_mode: bool,
    crowd_levels: dict[str, float],
    visited: set,
):
    if neighbor in visited:
        return
    crowd_density = crowd_levels.get(zone, 0.15)
    crowd_mult = 1.0
    if avoid_crowds:
        crowd_mult += get_crowd_penalty_multiplier(crowd_density) * 2.0
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

def find_path(
    from_node: str,
    to_node: str,
    *,
    accessibility_mode: bool = False,
    avoid_crowds: bool = False,
    crowd_levels: dict[str, float] | None = None,
    ignored_edges: set | None = None,
) -> dict[str, Any] | None:
    if from_node not in STADIUM_NODES or to_node not in STADIUM_NODES:
        return None
    if crowd_levels is None:
        crowd_levels = {}
    if ignored_edges is None:
        ignored_edges = set()

    adj = _build_adjacency_list(accessibility_mode, ignored_edges)

    g_score = dict.fromkeys(STADIUM_NODES, float("inf"))
    g_score[from_node] = 0.0
    dist_accum = dict.fromkeys(STADIUM_NODES, 0.0)
    parents = {}
    pq = [(euclidean_distance(from_node, to_node), from_node)]
    visited = set()

    while pq:
        _, current = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)

        if current == to_node:
            return _reconstruct_path_result(to_node, from_node, parents, dist_accum, accessibility_mode=accessibility_mode, crowd_levels=crowd_levels)

        for neighbor, dist, _acc, zone in adj[current]:
            _process_neighbor(
                current, neighbor, dist, zone,
                g_score, dist_accum, parents, pq, to_node,
                avoid_crowds=avoid_crowds, accessibility_mode=accessibility_mode,
                crowd_levels=crowd_levels, visited=visited,
            )

    return None

def _generate_alternatives(
    from_node: str,
    to_node: str,
    accessibility_mode: bool,  # noqa: FBT001
    avoid_crowds: bool,  # noqa: FBT001
    crowd_levels: dict[str, float],
    primary_route: list[str],
) -> list[dict[str, Any]]:
    alternatives = []
    if len(primary_route) > 3:
        mid_idx = len(primary_route) // 2
        edge_to_remove = (primary_route[mid_idx], primary_route[mid_idx + 1])
        alt_res = find_path(
            from_node, to_node,
            accessibility_mode=accessibility_mode,
            avoid_crowds=avoid_crowds,
            crowd_levels=crowd_levels,
            ignored_edges={edge_to_remove},
        )
        if alt_res and alt_res["route"] != primary_route:
            alternatives.append(alt_res)
        if len(primary_route) > 5:
            edge_to_remove_2 = (primary_route[-3], primary_route[-2])
            alt_res_2 = find_path(
                from_node, to_node,
                accessibility_mode=accessibility_mode,
                avoid_crowds=avoid_crowds,
                crowd_levels=crowd_levels,
                ignored_edges={edge_to_remove_2, edge_to_remove},
            )
            if alt_res_2 and alt_res_2["route"] != primary_route and alt_res_2["route"] not in [a["route"] for a in alternatives]:
                alternatives.append(alt_res_2)
    return alternatives

@cached(cache=pathfinding_cache, key=pathfinding_key)
def get_route_with_alternatives(
    from_node: str,
    to_node: str,
    *,
    accessibility_mode: bool = False,
    avoid_crowds: bool = False,
    crowd_levels: dict[str, float] | None = None,
) -> dict[str, Any] | None:
    if crowd_levels is None:
        crowd_levels = {}

    primary = find_path(from_node, to_node, accessibility_mode=accessibility_mode, avoid_crowds=avoid_crowds, crowd_levels=crowd_levels)
    if not primary:
        return None

    primary_route = primary["route"]
    alternatives = _generate_alternatives(from_node, to_node, accessibility_mode, avoid_crowds, crowd_levels, primary_route)

    formatted_alternatives = [
        {
            "route": alt["route"],
            "estimated_time_minutes": alt["estimated_time_minutes"],
            "distance_meters": alt["distance_meters"],
            "crowd_score": alt["crowd_score"],
        }
        for alt in alternatives
    ]

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
        "accessibility_notes": accessibility_notes,
    }
