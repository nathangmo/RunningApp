import streamlit as st
import pydeck as pdk
import osmnx as ox
from shapely.geometry import LineString
from shapely.ops import linemerge
import sys, os
from shapely.strtree import STRtree
from shapely.geometry import Point
import json

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RUN_JSON_PATH = os.path.join(PROJECT_ROOT, "src", "data", "streams", "15998885224.json")

st.write("Loading GPS file from:", RUN_JSON_PATH)
from src.core.graph_loader import load_graph

with open(RUN_JSON_PATH) as f:
    run = json.load(f)

def normalize_geom(geom):
    if geom is None or geom.is_empty:
        return None
    if geom.geom_type == "LineString":
        return geom
    if geom.geom_type == "MultiLineString":
        parts = list(geom.geoms)
        if len(parts) == 0:
            return None
        return max(parts, key=lambda g: g.length)
    return None

def build_edge_index(gdf_edges):
    geoms = [geom for geom in gdf_edges.geometry.tolist() if geom is not None]
    tree = STRtree(geoms)
    return tree, geoms

def snap_point(pt, tree, geoms):
    res = tree.nearest(pt)

    # Case 1: Shapely returns a geometry
    if hasattr(res, "interpolate"):
        geom = res

    # Case 2: Shapely returns an index (np.int64)
    else:
        geom = geoms[int(res)]

    snapped = geom.interpolate(geom.project(pt))
    return snapped

def snap_track(lat_list, lon_list, tree, geoms):
    snapped = []
    for lat, lon in zip(lat_list, lon_list):
        pt = Point(lon, lat)
        sp = snap_point(pt, tree, geoms)
        snapped.append((sp.y, sp.x))
    return snapped


def main():
    st.title("OSM Graph Debug Viewer")

    G = load_graph(use_master=True)
    st.write("Graph loaded")

    gdf_nodes, gdf_edges = ox.convert.graph_to_gdfs(
        G, nodes=True, edges=True, fill_edge_geometry=True
    )

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

    paths = []
    for geom in lines.geometry:
        if geom is None or geom.is_empty:
            continue
        xs, ys = geom.xy
        path = [[float(lon), float(lat)] for lon, lat in zip(xs, ys)]
        paths.append({"path": path})

    st.write("Paths to draw:", len(paths))

    node_data = [
        {"lon": row["x"], "lat": row["y"]}
        for _, row in gdf_nodes.iterrows()
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

    lat_center = gdf_nodes["y"].mean()
    lon_center = gdf_nodes["x"].mean()

    with open("/home/nathan/Downloads/RunningApp/src/data/streams/15998885224.json") as f:
        run = json.load(f)

    gps_pairs = run["latlng"]["data"]
    gps_lats = [p[0] for p in gps_pairs]
    gps_lons = [p[1] for p in gps_pairs]

    tree, geoms = build_edge_index(lines)
    snapped = snap_track(gps_lats, gps_lons, tree,geoms)

    original_points = [{"lon": lon, "lat": lat} for lat, lon in zip(gps_lats, gps_lons)]
    snapped_points = [{"lon": lon, "lat": lat} for lat, lon in snapped]

    original_layer = pdk.Layer(
        "ScatterplotLayer",
        data=original_points,
        get_position=["lon", "lat"],
        get_fill_color=[255, 0, 0],
        get_radius=3,
    )

    snapped_layer = pdk.Layer(
        "ScatterplotLayer",
        data=snapped_points,
        get_position=["lon", "lat"],
        get_fill_color=[0, 255, 0],
        get_radius=3,
    )

    view_state = pdk.ViewState(
        longitude=lon_center,
        latitude=lat_center,
        zoom=13,
        pitch=0,
    )

    deck = pdk.Deck(
        layers=[edge_layer, node_layer, original_layer, snapped_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    )

    st.pydeck_chart(deck)

if __name__ == "__main__":
    main()
