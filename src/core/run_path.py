# src/core/run_path.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any

import osmnx as ox

from src.core.preprocessing import preprocess_points, haversine_m, Point
from src.core.snapping_fast import snap_points_fast


@dataclass
class RunPathStats:
    """Basic statistics for a processed run."""
    num_raw_points: int
    num_clean_points: int
    num_snapped_points: int
    num_nodes: int
    total_distance_m: float
    avg_spacing_m: Optional[float]


class RunPath:
    """
    Standardized representation of a single running activity on top of an OSM graph.

    This wraps:
      - raw GPS points
      - cleaned points (duplicates + speed spikes removed)
      - snapped points (projected to nearest OSM edges)
      - corresponding graph nodes (nearest node on each edge)
      - basic statistics such as total distance
    """

    def __init__(
        self,
        G,
        latlng: List[Point],
        times: Optional[List[float]] = None,
    ) -> None:
        """
        Parameters
        ----------
        G : networkx.MultiDiGraph
            OSM graph loaded via graph_loader.load_graph.
        latlng : list[(lat, lon)]
            Raw GPS coordinates from Strava streams, in (lat, lon) order.
        times : list[float] or None
            Optional time stream (seconds) aligned with latlng, for speed spike removal.
        """
        if not latlng:
            raise ValueError("RunPath requires at least one GPS point.")

        self.G = G

        # 1. Raw points
        self.raw_points: List[Point] = [(p[0], p[1]) for p in latlng]

        # 2. Clean points (remove duplicates, speed spikes)
        self.clean_points: List[Point] = preprocess_points(latlng, times)

        # 3. Snap to OSM edges (using your fast STRtree-based snapping)
        self.snapped_records: List[Dict[str, Any]] = snap_points_fast(G, self.clean_points)

        # 4. Extract snapped coordinates
        self.snapped_points: List[Point] = [
            (rec["snapped_lat"], rec["snapped_lon"]) for rec in self.snapped_records
        ]

        # 5. Map snapped points to nearest graph nodes
        self.node_sequence: List[int] = self._compute_node_sequence()

        if not self.node_sequence:
            raise RuntimeError("Failed to compute a node sequence for this run.")

        self.start_node: int = self.node_sequence[0]
        self.end_node: int = self.node_sequence[-1]

        # 6. Basic stats
        self.stats: RunPathStats = self._compute_stats()

    # ------------------------------------------------------------------
    # Core internal methods
    # ------------------------------------------------------------------

    def _compute_node_sequence(self) -> List[int]:
        """
        For each snapped point, find the nearest edge, then pick the closest of its
        two endpoint nodes (u or v). Returns a deduplicated node sequence.
        """
        G = self.G
        nodes: List[int] = []

        for lat, lon in self.snapped_points:
            # ox.distance.nearest_edges expects (x=lon, y=lat)
            u, v, key = ox.distance.nearest_edges(G, lon, lat)

            node_u = G.nodes[u]
            node_v = G.nodes[v]

            d_u = haversine_m(lat, lon, node_u["y"], node_u["x"])
            d_v = haversine_m(lat, lon, node_v["y"], node_v["x"])

            closest_node = u if d_u <= d_v else v
            nodes.append(closest_node)

        # Remove consecutive duplicates to obtain a simplified node sequence
        simplified: List[int] = []
        for nid in nodes:
            if not simplified or simplified[-1] != nid:
                simplified.append(nid)

        return simplified

    def _compute_stats(self) -> RunPathStats:
        """Compute simple statistics based on snapped points."""
        total_dist = self._total_distance_m(self.snapped_points)

        if len(self.snapped_points) > 1:
            avg_spacing = total_dist / (len(self.snapped_points) - 1)
        else:
            avg_spacing = None

        return RunPathStats(
            num_raw_points=len(self.raw_points),
            num_clean_points=len(self.clean_points),
            num_snapped_points=len(self.snapped_points),
            num_nodes=len(self.node_sequence),
            total_distance_m=total_dist,
            avg_spacing_m=avg_spacing,
        )

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    @staticmethod
    def _total_distance_m(points: List[Point]) -> float:
        """Sum haversine distance along a polyline."""
        if len(points) < 2:
            return 0.0

        total = 0.0
        for (lat1, lon1), (lat2, lon2) in zip(points[:-1], points[1:]):
            total += haversine_m(lat1, lon1, lat2, lon2)
        return total

    def to_dict(self) -> Dict[str, Any]:
        """Lightweight serialization of the run path."""
        return {
            "start_node": self.start_node,
            "end_node": self.end_node,
            "node_sequence": self.node_sequence,
            "stats": self.stats.__dict__,
        }

    def to_snapped_dataframe(self):
        """Return a pandas DataFrame of snapped points for mapping."""
        import pandas as pd

        lat = [p[0] for p in self.snapped_points]
        lon = [p[1] for p in self.snapped_points]

        return pd.DataFrame({"lat": lat, "lon": lon})

    def to_raw_dataframe(self):
        """Return a pandas DataFrame of raw points for mapping."""
        import pandas as pd

        lat = [p[0] for p in self.raw_points]
        lon = [p[1] for p in self.raw_points]

        return pd.DataFrame({"lat": lat, "lon": lon})

    # ------------------------------------------------------------------
    # Class helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_streams(
        cls,
        G,
        streams: Dict[str, Any],
    ) -> "RunPath":
        """
        Construct a RunPath directly from Strava streams JSON.

        Expects:
          streams["latlng"]["data"]  -> list of [lat, lon]
          streams["time"]["data"]    -> list of timestamps (optional)
        """
        if "latlng" not in streams:
            raise ValueError("Streams dict does not contain 'latlng' data.")

        latlng = streams["latlng"]["data"]

        times = None
        if "time" in streams and "data" in streams["time"]:
            times = streams["time"]["data"]

        return cls(G, latlng, times=times)
