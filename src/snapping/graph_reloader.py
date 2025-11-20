import osmnx as ox

G = ox.graph_from_bbox(
    north=52.38,
    south=52.35,
    east=4.95,
    west=4.88,
    network_type="walk"
)

G = ox.add_edge_geometries(G)
ox.save_graphml("amsterdam_east_small.graphml")


