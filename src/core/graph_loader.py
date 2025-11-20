import os
import osmnx as ox
import numpy as np
from src.core.graph_repair import repair_graph

# Compute absolute project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

MASTER_GRAPH_PATH = os.path.join(
    PROJECT_ROOT,
    "data/osm_cache/amsterdam_east_master_dense_repaired.graphml"
)


def load_master_graph():
    """
    Load the pre-downloaded OSM graph for Amsterdam East.
    """
    print("DEBUG: Attempting to load master graph…")
    print(f"DEBUG: __file__         = {__file__}")
    print(f"DEBUG: PROJECT_ROOT     = {PROJECT_ROOT}")
    print(f"DEBUG: MASTER_GRAPH_PATH = {MASTER_GRAPH_PATH}")
    print(f"DEBUG: Path exists?      = {os.path.exists(MASTER_GRAPH_PATH)}")

    if not os.path.exists(MASTER_GRAPH_PATH):
        raise FileNotFoundError(
            f"Master graph not found at: {MASTER_GRAPH_PATH}"
        )

    print("DEBUG: Loading graphml…")
    G = ox.load_graphml(MASTER_GRAPH_PATH)
    print("DEBUG: Graph loaded successfully.")

    # Note: NO repair here
    return G


def load_graph_legacy(latitudes, longitudes, dist_m=1500):
    ox.settings.use_cache = True
    ox.settings.cache_folder = os.path.join(PROJECT_ROOT, "data/osm_cache")

    center_lat = round(float(np.mean(latitudes)), 4)
    center_lon = round(float(np.mean(longitudes)), 4)

    return ox.graph_from_point(
        (center_lat, center_lon),
        dist=dist_m,
        network_type="walk",
        simplify=True
    )


def load_graph(use_master=True):
    """
    Main entry point for loading a graph.
    Repairs missing connectors automatically.
    """
    if use_master:
        G = ox.load_graphml(MASTER_GRAPH_PATH)
    else:
        G = ox.graph_from_place("Amsterdam, NL", network_type="walk")

    # Single place where repair happens
    G = repair_graph(G, max_gap_m=30)
    print("DEBUG: Graph repaired successfully.")

    return G
