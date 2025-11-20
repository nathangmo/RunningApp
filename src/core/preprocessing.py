import math
from typing import List, Tuple

Point = Tuple[float, float]


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def remove_duplicates(points: List[Point]) -> List[Point]:
    if not points:
        return []
    cleaned = [points[0]]
    for p in points[1:]:
        if p != cleaned[-1]:
            cleaned.append(p)
    return cleaned


def remove_speed_spikes(points: List[Point], times: List[float], max_speed_m_s: float = 7.0) -> List[Point]:
    if len(points) != len(times):
        return points

    keep = [True] * len(points)

    for i in range(1, len(points)):
        lat1, lon1 = points[i - 1]
        lat2, lon2 = points[i]
        dt = times[i] - times[i - 1]
        if dt <= 0:
            continue

        dist = haversine_m(lat1, lon1, lat2, lon2)
        speed = dist / dt

        if speed > max_speed_m_s:
            keep[i] = False

    return [p for p, k in zip(points, keep) if k]


def preprocess_points(latlng: list, time_stream: list | None = None) -> list:
    points = [(p[0], p[1]) for p in latlng]

    points = remove_duplicates(points)

    if time_stream is not None:
        points = remove_speed_spikes(points, time_stream)

    return [(p[0], p[1]) for p in points]
