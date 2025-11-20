# src/ui/activity_inspector.py

import sys
import os
import json

import streamlit as st
import pydeck as pdk
import osmnx as ox

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.graph_loader import load_graph
from src.core.graph_cropper import crop_graph_edges
from src.core.run_path import RunPath

DATA_ROOT = os.path.join(PROJECT_ROOT, "src", "data")
STREAMS_DIR = os.path.join(DATA_ROOT, "streams")
ACTIVITIES_PATH = os.path.join(DATA_ROOT, "all_activities.json")


def compute_bbox(G):
    lats = [data["y"] for _, data in G.nodes(data=True)]
    lons = [data["x"] for _, data in G.nodes(data=True)]
    return min(lats), max(lats), min(lons), max(lons)


@st.cache_resource
def get_graph():
    return load_graph(use_master=True)


@st.cache_data
def load_activities():
    with open(ACTIVITIES_PATH, "r") as f:
        acts = json.load(f)
    return [a for a in acts if a.get("type") == "Run"]


@st.cache_data
def load_streams(activity_id):
    with open(os.path.join(STREAMS_DIR, f"{activity_id}.json"), "r") as f:
        return json.load(f)


def main():
    st.title("Activity Inspector")

    G = get_graph()
    lat_min, lat_max, lon_min, lon_max = compute_bbox(G)

    activities = load_activities()

    labels = [
        f"{a.get('start_date_local','')[:10]} | {a.get('distance',0)/1000:.1f} km | {a.get('name','')}"
        for a in activities
    ]
    label_to_act = dict(zip(labels, activities))

    selected = st.selectbox("Select a run", labels)
    act = label_to_act[selected]
    streams = load_streams(act["id"])

    latlng = streams["latlng"]["data"]
    lats = [p[0] for p in latlng]
    lons = [p[1] for p in latlng]

    inside_lat = (min(lats) >= lat_min) and (max(lats) <= lat_max)
    inside_lon = (min(lons) >= lon_min) and (max(lons) <= lon_max)
    if not (inside_lat and inside_lon):
        st.error("Outside graph area.")
        st.stop()

    run_path = RunPath.from_streams(G, streams)

    raw_df = run_path.to_raw_dataframe()
    snapped_df = run_path.to_snapped_dataframe()

    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G, nodes=True, edges=True)
    cropped_edges = crop_graph_edges(gdf_edges, latlng)

    edge_points = []
    for geom in cropped_edges.geometry:
        if geom is None or geom.geom_type != "LineString":
            continue
        xs, ys = geom.xy
        for la, lo in zip(ys, xs):
            edge_points.append({"lat": la, "lon": lo})

    edge_layer = pdk.Layer("ScatterplotLayer", edge_points,
                           get_position=["lon", "lat"],
                           get_radius=4, get_color=[160, 160, 160])

    raw_layer = pdk.Layer("ScatterplotLayer", raw_df,
                          get_position=["lon", "lat"],
                          get_radius=6, get_color=[0, 0, 255])

    snapped_layer = pdk.Layer("ScatterplotLayer", snapped_df,
                              get_position=["lon", "lat"],
                              get_radius=4, get_color=[255, 0, 0])

    mid = raw_df.iloc[len(raw_df)//2]
    view = pdk.ViewState(latitude=mid["lat"], longitude=mid["lon"], zoom=14)

    st.pydeck_chart(pdk.Deck(
        layers=[edge_layer, raw_layer, snapped_layer],
        initial_view_state=view,
        map_style="mapbox://styles/mapbox/light-v9"
    ))


if __name__ == "__main__":
    main()
