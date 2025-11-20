import sys, os
import json
import streamlit as st
import pydeck as pdk
import osmnx as ox
from shapely.geometry import Point, LineString

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.graph_loader import load_graph



def main():

    st.title("Minimal Map Debugger")

    activity_id = "15998885224"
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "streams",
            f"{activity_id}.json",
        )
    )

    st.write(f"Loading activity from:\n{path}")

    with open(path, "r") as f:
        streams = json.load(f)

    latlng = streams["latlng"]["data"]
    gps_df = [{"lat": p[0], "lon": p[1]} for p in latlng]

    # Load master graph
    G = load_graph(use_master=True)

    # Convert edges to scatterable points for visualization
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

    from src.core.graph_cropper import crop_graph_edges

    cropped_edges = crop_graph_edges(gdf_edges, latlng, margin_deg=0.003)

    edge_points = []
    for geom in cropped_edges.geometry:
        if geom is None:
            continue
        if geom.geom_type == "LineString":
            xs, ys = geom.xy
            for la, lo in zip(ys, xs):
                edge_points.append({"lat": la, "lon": lo})

    # Build pydeck layers
    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=edge_points,
            get_position=["lon", "lat"],
            get_radius=5,
            get_color=[100, 100, 100],
        ),
        pdk.Layer(
            "ScatterplotLayer",
            data=gps_df,
            get_position=["lon", "lat"],
            get_radius=7,
            get_color=[0, 0, 255],
        ),
    ]

    # Center the map on the midpoint of your run
    mid = gps_df[len(gps_df)//2]
    view = pdk.ViewState(
        latitude=mid["lat"],
        longitude=mid["lon"],
        zoom=14,
    )

    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view))


if __name__ == "__main__":
    main()
