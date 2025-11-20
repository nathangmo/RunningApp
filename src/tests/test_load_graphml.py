import osmnx as ox
from osmnx import convert

G = ox.io.load_graphml("/home/nathan/Downloads/RunningApp/data/osm_cache/amsterdam_east_master.graphml")

print("nodes:", len(G.nodes))
print("edges:", len(G.edges))

gdf_nodes, gdf_edges = convert.graph_to_gdfs(G, nodes=True, edges=True)

print(gdf_edges.head(10))
print("Number of non-null geometries:", gdf_edges.geometry.notnull().sum())
