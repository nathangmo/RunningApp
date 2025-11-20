import sys
import os

# Ensure project root is on path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import osmnx as ox
import numpy as np
from shapely.geometry import LineString
from src.core.preprocessing import haversine_m


GRAPH_PATH_IN  = os.path.join(PROJECT_ROOT, "data/osm_cache/amsterdam_east_master_dense.graphml")
GRAPH_PATH_OUT = os.path.join(PROJECT_ROOT, "data/osm_cache/amsterdam_east_master_dense_repaired.graphml")


# ---------------------------------------------------------
# Helper: add edge
# ---------------------------------------------------------

def add_edge_between_nodes(G, u, v, x_u, y_u, x_v, y_v):
    geom = LineString([(x_u, y_u), (x_v, y_v)])
    length = haversine_m(y_u, x_u, y_v, x_v)

    G.add_edge(u, v, geometry=geom, length=length)
    G.add_edge(v, u, geometry=geom, length=length)
    return G


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print("Loading graph:", GRAPH_PATH_IN)
    G = ox.load_graphml(GRAPH_PATH_IN)
    print("Graph loaded.")
    print("Current edges:", len(G.edges()))

    gdf_nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)

    print("\nInteractive edge adding mode.")
    print("Type 'done' to stop and save.")
    print("Type 'show' to list all edges added so far.")
    print("----------------------------------------------------")

    added_edges = []

    while True:
        cmd = input("\nEnter first node ID (or 'done'): ").strip()

        if cmd.lower() == "done":
            break
        if cmd.lower() == "show":
            print("\nEdges added this session:")
            for (u, v) in added_edges:
                print(f"{u} <-> {v}")
            continue

        try:
            u = int(cmd)
        except:
            print("Invalid integer.")
            continue

        v_str = input("Enter second node ID: ").strip()
        try:
            v = int(v_str)
        except:
            print("Invalid integer.")
            continue

        if u not in gdf_nodes.index or v not in gdf_nodes.index:
            print("One of the node IDs is not in the graph.")
            continue

        x_u = float(gdf_nodes.loc[u].x)
        y_u = float(gdf_nodes.loc[u].y)
        x_v = float(gdf_nodes.loc[v].x)
        y_v = float(gdf_nodes.loc[v].y)

        G = add_edge_between_nodes(G, u, v, x_u, y_u, x_v, y_v)
        added_edges.append((u, v))

        print(f"Added edge: {u} <-> {v}")
        print("Total edges now:", len(G.edges()))

    # Save
    print("\nSaving repaired graph to:", GRAPH_PATH_OUT)
    ox.save_graphml(G, GRAPH_PATH_OUT)
    print("Done. Added", len(added_edges), "edges.")


if __name__ == "__main__":
    main()
