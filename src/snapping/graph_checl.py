import osmnx as ox
G = ox.load_graphml("/home/nathan/Downloads/RunningApp/data/osm_cache/amsterdam_east_master.graphml")
_, gdf_edges = ox.graph_to_gdfs(G)

print(gdf_edges.geometry.head())
