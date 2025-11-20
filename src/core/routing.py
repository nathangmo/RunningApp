from typing import List

import osmnx as ox

from src.core.preprocessing import haversine_m, Point


def shortest_path(G, start_node: int, end_node: int, weight: str = "length") -> List[int]:
    """
    Thin wrapper around osmnx shortest path.
    Returns a list of node ids from start_node to end_node.
    """
    return ox.shortest_path(G, start_node, end_node, weight=weight)


def path_length_m(G, node_path: List[int]) -> float:
    """
    Approximate the length of a path by summing edge lengths.
    Falls back to haversine distance if no length attribute is present.
    """
    if len(node_path) < 2:
        return 0.0

    total = 0.0

    for u, v in zip(node_path[:-1], node_path[1:]):
        if G.has_edge(u, v):
            # take the first edge variant
            edge_data = next(iter(G[u][v].values()))
            length = edge_data.get("length", None)
            if length is not None:
                total += float(length)
                continue

        # fallback to haversine on node coordinates
        node_u = G.nodes[u]
        node_v = G.nodes[v]
        total += haversine_m(node_u["y"], node_u["x"], node_v["y"], node_v["x"])

    return total


def approximate_polyline_length(points: List[Point]) -> float:
    """
    Utility for computing length of a coordinate polyline without graph context.
    """
    if len(points) < 2:
        return 0.0

    total = 0.0
    for (lat1, lon1), (lat2, lon2) in zip(points[:-1], points[1:]):
        total += haversine_m(lat1, lon1, lat2, lon2)
    return total


def find_loop_extension_stub(
    G,
    start_node: int,
    end_node: int,
    base_distance_m: float,
    extra_distance_m: float,
    search_radius_m: float = 1000.0,
):
    """
    Placeholder for future loop extension logic.

    The intended behaviour is:
      given a base path from start_node to end_node with length base_distance_m,
      find a path that roughly adds extra_distance_m while starting near start_node
      and ending near end_node.

    For now this is just a stub, to be implemented later.
    """
    raise NotImplementedError("Loop extension logic not implemented yet.")
