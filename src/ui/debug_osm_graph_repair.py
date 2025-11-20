import streamlit as st
import pydeck as pdk
import os
import sys
import osmnx as ox
from shapely.geometry import LineString

# Project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.graph_loader import load_graph
from src.core.preprocessing import haversine_m


# -------------------------------------------------------
# Helper to add an edge
# -------------------------------------------------------
def add_edge(G, u, v, x_u, y_u, x_v, y_v):
    geom = LineString([(x_u, y_u), (x_v, y_v)])
    length = haversine_m(y_u, x_u, y_v, x_v)

    G.add_edge(u, v, geometry=geom, length=length)
    G.add_edge(v, u, geometry=geom, length=length)
    return G


# -------------------------------------------------------
# Session state
# -------------------------------------------------------
if "G" not in st.session_state:
    st.session_state.G = load_graph(use_master=True)

if "selected_node_1" not in st.session_state:
    st.session_state.selected_node_1 = None

if "selected_node_2" not in st.session_state:
    st.session_state.selected_node_2 = None


# -------------------------------------------------------
# Build map layers
# -------------------------------------------------------
G = st.session_state.G

gdf_nodes, gdf_edges = ox.graph_to_gdfs(
    G, nodes=True, edges=True, fill_edge_geometry=True
)

# Node list
node_data = [
    {"lon": row["x"], "lat": row["y"], "id": int(idx)}
    for idx, row in gdf_nodes.iterrows()
]

# Edge list
paths = []
for geom in gdf_edges.geometry:
    if geom is None or geom.is_empty:
        continue
    xs, ys = geom.xy
    paths.append({"path": [[float(lon), float(lat)] for lon, lat in zip(xs, ys)]})


node_layer = pdk.Layer(
    "ScatterplotLayer",
    data=node_data,
    get_position=["lon", "lat"],
    get_fill_color=[255, 0, 0],
    get_radius=5,
    pickable=True,
)

edge_layer = pdk.Layer(
    "PathLayer",
    data=paths,
    get_path="path",
    get_color=[120, 120, 120],
    width_scale=2,
    width_min_pixels=1,
)

view_state = pdk.ViewState(
    latitude=float(gdf_nodes["y"].mean()),
    longitude=float(gdf_nodes["x"].mean()),
    zoom=14,
)

deck = pdk.Deck(
    layers=[edge_layer, node_layer],
    initial_view_state=view_state,
    tooltip={"html": "<b>Node ID:</b> {id}"}
)


st.title("OSM Graph Repair Tool (Simple Mode)")

st.pydeck_chart(deck)


# -------------------------------------------------------
# Manual node selection
# -------------------------------------------------------
with st.expander("Select nodes manually"):
    st.write("Hover on the map to read the Node ID in the tooltip.")

    node_id_manual = st.text_input("Enter Node ID")

    if st.button("Select Node 1"):
        try:
            st.session_state.selected_node_1 = int(node_id_manual)
            st.success(f"Selected Node 1: {st.session_state.selected_node_1}")
        except:
            st.error("Invalid node ID")

    if st.button("Select Node 2"):
        try:
            st.session_state.selected_node_2 = int(node_id_manual)
            st.success(f"Selected Node 2: {st.session_state.selected_node_2}")
        except:
            st.error("Invalid node ID")


# -------------------------------------------------------
# Add edge
# -------------------------------------------------------
u = st.session_state.selected_node_1
v = st.session_state.selected_node_2

if u is not None and v is not None:
    if st.button("Add Edge"):
        try:
            x_u = float(gdf_nodes.loc[u].x)
            y_u = float(gdf_nodes.loc[u].y)
            x_v = float(gdf_nodes.loc[v].x)
            y_v = float(gdf_nodes.loc[v].y)

            st.session_state.G = add_edge(G, u, v, x_u, y_u, x_v, y_v)
            st.success(f"Added edge between {u} and {v}")

        except Exception as e:
            st.error(str(e))


# -------------------------------------------------------
# Export graph
# -------------------------------------------------------
if st.button("Export repaired graph"):
    out_path = os.path.join(PROJECT_ROOT, "data/osm_cache/repaired_graph.graphml")
    ox.save_graphml(st.session_state.G, out_path)
    st.success(f"Saved repaired graph to: {out_path}")
