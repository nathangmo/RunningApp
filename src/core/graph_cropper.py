from shapely.geometry import box

def crop_graph_edges(gdf_edges, latlng, margin_deg=0.002):
    """
    Crop OSM edges to a small region around the run.
    margin_deg ~ 0.002 deg ≈ 200 meters.
    """

    lats = [p[0] for p in latlng]
    lons = [p[1] for p in latlng]

    min_lat = min(lats) - margin_deg
    max_lat = max(lats) + margin_deg
    min_lon = min(lons) - margin_deg
    max_lon = max(lons) + margin_deg

    bbox = box(min_lon, min_lat, max_lon, max_lat)

    cropped = gdf_edges[gdf_edges.geometry.intersects(bbox)]
    return cropped
