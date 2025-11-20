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

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

GRAPH_PATH_IN  = os.path.join(PROJECT_ROOT, "data/osm_cache/amsterdam_east_master_dense.graphml")
GRAPH_PATH_OUT = os.path.join(PROJECT_ROOT, "data/osm_cache/amsterdam_east_master_dense_repaired.graphml")

# Target location of the known gap
TARGET_LAT = 52.368954
TARGET_LON = 4.9372609


# -------------------------------------------------------------------
# Helper: Find nearest OSM nodes
# -------------------------------------------------------------------

def nearest_nodes_k(G, lon, lat, k=5):
    gdf_nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
    xs = gdf_nodes.x.values
    ys = gdf_nodes.y.values

    d = (xs - lon)**2 + (ys - lat)**2
    idxs = np.argsort(d)[:k]
    return gdf_nodes.iloc[idxs]


# -------------------------------------------------------------------
# Helper: Insert missing edge
# -------------------------------------------------------------------

def add_edge_between_nodes(G, u, v, x_u, y_u, x_v, y_v):
    geom = LineString([(x_u, y_u), (x_v, y_v)])
    length = haversine_m(y_u, x_u, y_v, x_v)

    G.add_edge(u, v, geometry=geom, length=length)
    G.add_edge(v, u, geometry=geom, length=length)

    return G


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():
    print("Loading graph:", GRAPH_PATH_IN)
    G = ox.load_graphml(GRAPH_PATH_IN)
    print("Graph loaded.")

    print("\nNearest nodes to:", TARGET_LAT, TARGET_LON)
    nearest = nearest_nodes_k(G, TARGET_LON, TARGET_LAT, k=5)
    print(nearest[["y", "x"]])
    print("\nNode IDs:")
    print(nearest.index.values)

    print("\nPick TWO node IDs above that should be connected.")
    u = int(input("Enter first node ID: ").strip())
    v = int(input("Enter second node ID: ").strip())

    gdf_nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)

    x_u = float(gdf_nodes.loc[u].x)
    y_u = float(gdf_nodes.loc[u].y)
    x_v = float(gdf_nodes.loc[v].x)
    y_v = float(gdf_nodes.loc[v].y)

    G = add_edge_between_nodes(G, u, v, x_u, y_u, x_v, y_v)

    print("\nSaving repaired graph to:", GRAPH_PATH_OUT)
    ox.save_graphml(G, GRAPH_PATH_OUT)
    print("Done.")


if __name__ == "__main__":
    main()
