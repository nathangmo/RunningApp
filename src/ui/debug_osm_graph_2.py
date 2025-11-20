import sys
import os
import streamlit as st
import pydeck as pdk
import osmnx as ox
from osmnx import convert

# Make sure project root is on path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.graph_loader import load_graph


def main():
    st.title("OSM Graph Geometry Debugger")

    # Load graph
    G = load_graph(use_master=True)
    st.write("Graph loaded")

    # Convert to GeoDataFrames
    gdf_nodes, gdf_edges = convert.graph_to_gdfs(G, nodes=True, edges=True)
    st.write("Nodes:", len(gdf_nodes))
    st.write("Edges:", len(gdf_edges))

    # ----------------------------------------------------------------------
    # 1) DEFINE CROPPING BOUNDING BOX (your coordinates + margin)
    # ----------------------------------------------------------------------
    # Input coordinates: 52°22'13.6"N 4°56'25.0"E
    # Converted:
    # lat = 52.370444
    # lon = 4.940278

    center_lat = 52.370444
    center_lon = 4.940278

    margin = 0.05    # approx ~1.6 km margin on each side

    min_lat = center_lat - margin
    max_lat = center_lat + margin
    min_lon = center_lon - margin
    max_lon = center_lon + margin

    st.subheader("Cropping area")
    st.write("lat range:", (min_lat, max_lat))
    st.write("lon range:", (min_lon, max_lon))

    cropped_edges = gdf_edges[
        (gdf_edges.geometry.bounds.miny >= min_lat) &
        (gdf_edges.geometry.bounds.maxy <= max_lat) &
        (gdf_edges.geometry.bounds.minx >= min_lon) &
        (gdf_edges.geometry.bounds.maxx <= max_lon)
    ]

    st.write("Cropped edges:", len(cropped_edges))

    # ----------------------------------------------------------------------
    # 2) Build paths from cropped geometries
    # ----------------------------------------------------------------------

    paths = []
    for geom in cropped_edges.geometry:
        if geom is None or geom.is_empty:
            continue

        if geom.geom_type == "LineString":
            xs, ys = geom.xy
            path = [[float(lon), float(lat)] for lon, lat in zip(xs, ys)]
            paths.append({"path": path})

        elif geom.geom_type == "MultiLineString":
            for part in geom.geoms:
                xs, ys = part.xy
                path = [[float(lon), float(lat)] for lon, lat in zip(xs, ys)]
                paths.append({"path": path})

    st.write("Rendered path count:", len(paths))

    # ----------------------------------------------------------------------
    # 3) Build PathLayer
    # ----------------------------------------------------------------------

    edge_layer = pdk.Layer(
        "PathLayer",
        data=paths,
        get_path="path",
        get_color=[0, 100, 200],
        width_scale=2,
        width_min_pixels=1,
        pickable=False,
    )

    view = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=14,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[edge_layer],
            initial_view_state=view,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        )
    )


if __name__ == "__main__":
    main()
