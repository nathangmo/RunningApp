# src/core/snapping_fast.py

import numpy as np
import osmnx as ox

from shapely.geometry import (
    Point as ShapelyPoint,
    LineString,
    MultiLineString,
    GeometryCollection,
    LinearRing
)
from shapely.strtree import STRtree
from shapely.ops import linemerge

from src.core.preprocessing import haversine_m


# -------------------------------------------------------------------
# STRtree Builder
# -------------------------------------------------------------------

def build_strtree(G):
    """
    Build an STRtree index of all OSM edge geometries.
    Returns (gdf_edges, tree, geoms) where:
      geoms is a Python list of geometries that the tree references.
    This avoids the Shapely behaviour where passing a numpy array causes
    nearest() to return an integer index instead of the geometry.
    """
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

    # MUST be a Python list, not numpy array
    geoms = list(gdf_edges.geometry)

    tree = STRtree(geoms)
    return gdf_edges, tree, geoms


# -------------------------------------------------------------------
# Geometry Sanitization
# -------------------------------------------------------------------

def _force_linestring(geom):
    """
    Convert arbitrary Shapely geometry to a LineString if possible.

    Supported inputs:
      - LineString             -> returned unchanged
      - MultiLineString        -> merged or use longest segment
      - GeometryCollection     -> longest contained LineString
      - LinearRing             -> convert to LineString
      - Unsupported            -> return None
    """
    if geom is None:
        return None

    # Already valid
    if isinstance(geom, LineString):
        return geom

    # MultiLineString → merge or pick longest
    if isinstance(geom, MultiLineString):
        merged = linemerge(geom)
        if isinstance(merged, LineString):
            return merged
        if isinstance(merged, MultiLineString):
            if len(merged.geoms) == 0:
                return None
            return max(merged.geoms, key=lambda g: g.length)
        return None

    # GeometryCollection → choose longest LineString
    if isinstance(geom, GeometryCollection):
        line_parts = [g for g in geom.geoms if isinstance(g, LineString)]
        if not line_parts:
            return None
        return max(line_parts, key=lambda g: g.length)

    # LinearRing → convert to LineString
    if isinstance(geom, LinearRing):
        return LineString(list(geom.coords))

    # Unsupported: Polygon, Point, None
    return None


# -------------------------------------------------------------------
# Snapping
# -------------------------------------------------------------------

def snap_points_fast(G, points):
    """
    Snap a list of (lat, lon) points to the nearest OSM edge geometry.

    This version is fully robust:
        - builds STRtree from Python list (correct .nearest() behaviour)
        - handles MultiLineString, GeometryCollection, LinearRing
        - falls back to nearest node if geometry unusable
        - never crashes on OSM data inconsistencies
    """
    gdf_edges, tree, geoms = build_strtree(G)
    snapped = []

    for lat, lon in points:
        p = ShapelyPoint(lon, lat)

        # nearest() should return a geometry, but STRtree quirks exist
        geom = tree.nearest(p)

        # If Shapely returns an integer index into geoms (bug in numpy-based trees)
        if isinstance(geom, (int, np.integer)):
            geom = geoms[int(geom)]

        # Convert to a clean LineString
        ls = _force_linestring(geom)

        # If no usable geometry → fallback to nearest node
        if ls is None or ls.length == 0:
            node = ox.distance.nearest_nodes(G, lon, lat)
            node_data = G.nodes[node]
            snapped_lat = node_data["y"]
            snapped_lon = node_data["x"]
            err = haversine_m(lat, lon, snapped_lat, snapped_lon)

            snapped.append({
                "snapped_lat": snapped_lat,
                "snapped_lon": snapped_lon,
                "geom": None,
                "error_meters": float(err),
            })
            continue

        # Safe projection
        proj = ls.project(p)
        projection = ls.interpolate(proj)

        snapped_lat = projection.y
        snapped_lon = projection.x

        err = haversine_m(lat, lon, snapped_lat, snapped_lon)

        snapped.append({
            "snapped_lat": snapped_lat,
            "snapped_lon": snapped_lon,
            "geom": ls,
            "error_meters": float(err),
        })

    return snapped
