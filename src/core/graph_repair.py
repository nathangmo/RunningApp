import numpy as np
from shapely.geometry import LineString
from shapely.strtree import STRtree
from pyproj import Transformer
from scipy.spatial import KDTree
import osmnx as ox
from src.core.preprocessing import haversine_m


def repair_graph(G, max_gap_m=30):

    gdf_nodes, gdf_edges = ox.convert.graph_to_gdfs(G, nodes=True, edges=True)

    # Filter strictly valid geometries
    valid_geoms = []
    for g in gdf_edges.geometry:
        if g is None:
            continue
        if not hasattr(g, "geom_type"):
            continue
        if g.is_empty:
            continue
        valid_geoms.append(g)

    # Build spatial index
    tree_edges = STRtree(valid_geoms)

    # Projection
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    xs = gdf_nodes["x"].values
    ys = gdf_nodes["y"].values
    px, py = transformer.transform(xs, ys)

    coords_m = np.column_stack([px, py])
    kd = KDTree(coords_m)

    close_pairs = kd.query_pairs(r=max_gap_m)

    to_add = []

    for i, j in close_pairs:
        node_u = gdf_nodes.index[i]
        node_v = gdf_nodes.index[j]

        if G.has_edge(node_u, node_v) or G.has_edge(node_v, node_u):
            continue

        cand = LineString([(xs[i], ys[i]), (xs[j], ys[j])])

        hits = tree_edges.query(cand)

        intersects = False
        for h in hits:
            if isinstance(h, (int, np.integer)):
                geom = valid_geoms[int(h)]
            else:
                geom = h

            if geom is None:
                continue
            if not hasattr(geom, "geom_type"):
                continue
            if geom.is_empty:
                continue

            if cand.intersects(geom):
                intersects = True
                break

        if intersects:
            continue

        to_add.append((node_u, node_v, cand))

    # Add edges
    for u, v, geom in to_add:
        lat_u = float(gdf_nodes.loc[u].y)
        lon_u = float(gdf_nodes.loc[u].x)
        lat_v = float(gdf_nodes.loc[v].y)
        lon_v = float(gdf_nodes.loc[v].x)

        length = haversine_m(lat_u, lon_u, lat_v, lon_v)

        G.add_edge(u, v, geometry=geom, length=length)
        G.add_edge(v, u, geometry=geom, length=length)

    return G
