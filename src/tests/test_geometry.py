import osmnx as ox
from shapely.geometry import Polygon

north = 52.390
south = 52.340
east  = 4.990
west  = 4.870

polygon = Polygon([
    (west, north),
    (east, north),
    (east, south),
    (west, south),
    (west, north),
])

G = ox.graph_from_polygon(
    polygon,
    network_type="walk",
    simplify=True,
)

gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(G, nodes=True, edges=True)

print(gdf_edges.head())
print("Geometry exists:", gdf_edges.geometry.notnull().any())
