from typing import List, Tuple
from src.core.preprocessing import haversine_m, Point


def cumulative_distances(points: List[Point]) -> List[float]:
    if not points:
        return []

    dists = [0.0]
    total = 0.0
    for i in range(1, len(points)):
        lat1, lon1 = points[i - 1]
        lat2, lon2 = points[i]
        seg = haversine_m(lat1, lon1, lat2, lon2)
        total += seg
        dists.append(total)
    return dists


def interpolate_point(p1: Point, p2: Point, t: float) -> Point:
    return (
        p1[0] + t * (p2[0] - p1[0]),
        p1[1] + t * (p2[1] - p1[1])
    )


def resample_polyline(points: List[Point], spacing_m: float = 5.0) -> List[Point]:
    if not points:
        return []

    if len(points) == 1:
        return points

    cum = cumulative_distances(points)
    total_len = cum[-1]

    if total_len < spacing_m:
        return [points[0], points[-1]]

    num_samples = int(total_len // spacing_m)

    target_dists = [i * spacing_m for i in range(num_samples + 1)]
    resampled: List[Point] = []

    idx = 0
    for td in target_dists:
        while idx < len(cum) - 1 and cum[idx + 1] < td:
            idx += 1

        if idx == len(cum) - 1:
            resampled.append(points[-1])
            continue

        d0 = cum[idx]
        d1 = cum[idx + 1]
        t = 0.0 if d1 == d0 else (td - d0) / (d1 - d0)

        resampled.append(interpolate_point(points[idx], points[idx + 1], t))

    return resampled
