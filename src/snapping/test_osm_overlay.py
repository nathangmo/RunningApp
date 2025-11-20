import json
import streamlit as st
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(ROOT)

from src.snapping.preprocess_gps import preprocess_points
from src.snapping.resample_gps import resample_polyline
from src.snapping.visual_debug import create_debug_map


# SELECT ACTIVITY
activity_id = 15998885224
path = f"src/data/streams/{activity_id}.json"

from src.snapping.graph_loader import load_graph

G = load_graph(use_master=True)


with open(path, "r") as f:
    streams = json.load(f)

latlng = streams["latlng"]["data"]
time = streams.get("time", {}).get("data", None)

# STEP 1. Preprocess
clean = preprocess_points(latlng, time)

# STEP 2. Resample
clean_tuples = [(p[0], p[1]) for p in clean]
resampled = resample_polyline(clean_tuples, spacing_m=5.0)

# STEP 3. Load OSM graph
lats = [p[0] for p in resampled]
lons = [p[1] for p in resampled]
# G = load_graph_around_route(lats, lons, dist_m=1500)

# STEP 4. Visualize
deck = create_debug_map(G, clean_tuples, resampled)

st.title("OSM Overlay Debug")
st.pydeck_chart(deck)
