import osmnx as ox
G = ox.load_graphml("data/osm_cache/amsterdam_east_master.graphml")
print(len(G.nodes()), len(G.edges()))
