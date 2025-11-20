import streamlit as st
import pydeck as pdk
import osmnx as ox
from shapely.geometry import LineString
from shapely.ops import linemerge
import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.graph_loader import load_graph
from src.streamlit_map_click import map_click


def normalize_geom(geom):
    if geom is None or geom.is_empty:
        return None

    if geom.geom_type == "LineString":
        return geom

    if geom.geom_type == "MultiLineString":
        # choose the longest segment
        parts = list(geom.geoms)
        if len(parts) == 0:
            return None
        return max(parts, key=lambda g: g.length)

    return None


def main():
    st.title("OSM Graph Debug Viewer")

    G = load_graph(use_master=True)
    st.write("Graph loaded")

    gdf_nodes, gdf_edges = ox.convert.graph_to_gdfs(
        G, nodes=True, edges=True, fill_edge_geometry=True
    )
    # Debug: print graph bounding box
    xs = gdf_nodes["x"].values
    ys = gdf_nodes["y"].values

    st.write("Graph bounds:")
    st.write("min_lon:", float(xs.min()))
    st.write("max_lon:", float(xs.max()))
    st.write("min_lat:", float(ys.min()))
    st.write("max_lat:", float(ys.max()))

    gdf_edges["geometry"] = gdf_edges.geometry.apply(normalize_geom)
    lines = gdf_edges[gdf_edges.geometry.notna()]

    st.write("Valid geometries:", len(lines))

    # Build PathLayer data
    paths = []
    for geom in lines.geometry:
        if geom is None or geom.is_empty:
            continue

        xs, ys = geom.xy
        path = [[float(lon), float(lat)] for lon, lat in zip(xs, ys)]
        paths.append({"path": path})

    st.write("Paths to draw:", len(paths))

    # Build node layer
    # node_data = [
    #     {"lon": row["x"], "lat": row["y"]}
    #     for _, row in gdf_nodes.iterrows()
    # ]
    node_data = [
        {"lon": row["x"], "lat": row["y"], "id": int(idx)}
        for idx, row in gdf_nodes.iterrows()
    ]

    node_layer = pdk.Layer(
        "ScatterplotLayer",
        data=node_data,
        get_position=["lon", "lat"],
        get_fill_color=[255, 0, 0],
        get_radius=3,
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

    # Center on average coordinates
    lat_center = gdf_nodes["y"].mean()
    lon_center = gdf_nodes["x"].mean()

    view_state = pdk.ViewState(
        longitude=lon_center,
        latitude=lat_center,
        zoom=13,
        pitch=0,
    )

    deck = pdk.Deck(
        layers=[edge_layer, node_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={
            "html": "<b>Node ID:</b> {id}<br><b>Lat:</b> {lat}<br><b>Lon:</b> {lon}",
            "style": {"color": "white"}
        }
    )


    # Convert deck to JSON
    deck_json = deck.to_json()

    clicked = map_click(deck_json=deck_json, key="osm_click_map")

    st.write("Click event:", clicked)

    if "first_node" not in st.session_state:
        st.session_state.first_node = None

    if clicked is not None:
        node_id = clicked["data"]["id"]

        if st.session_state.first_node is None:
            st.session_state.first_node = node_id
            st.success(f"First node selected: {node_id}")

        else:
            a = st.session_state.first_node
            b = node_id
            st.session_state.first_node = None

            # Add edge to graph
            if not G.has_edge(a, b):
                G.add_edge(a, b)
                G.add_edge(b, a)

            # Save repaired graph
            ox.save_graphml(G, "data/osm_cache/amsterdam_east_repaired.graphml")

            st.success(f"Added repaired edge between {a} and {b}")


if __name__ == "__main__":
    main()
