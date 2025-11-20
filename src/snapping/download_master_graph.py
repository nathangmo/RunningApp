import osmnx as ox
from shapely.geometry import Polygon

def download_master_graph_bbox():
    north = 52.390
    south = 52.340
    east  = 4.990
    west  = 4.870

    poly = Polygon([
        (west, north),
        (east, north),
        (east, south),
        (west, south),
        (west, north),
    ])

    G = ox.graph.graph_from_polygon(
        poly,
        network_type="walk",
        simplify=False,
    )

    ox.io.save_graphml(G, "data/osm_cache/amsterdam_east_master_dense.graphml")

    print("DONE:", len(G.nodes()), "nodes,", len(G.edges()), "edges")

if __name__ == "__main__":
    download_master_graph_bbox()
