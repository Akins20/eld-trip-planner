"""Place stops on the route polyline by cumulative mileage (for map markers).

Stops are located by the mileage at which the simulator inserted them. Because the
returned geometry is a simplified polyline whose summed length may differ slightly
from the routing API's reported distance, we map a stop's mileage to a *fraction* of
the trip and read the point at that fraction of the polyline length. Endpoints snap
exactly to the first/last coordinate.
"""

from __future__ import annotations

import bisect
import math

from .constants import MAX_GEOMETRY_POINTS
from .segments import Stop

_EARTH_RADIUS_MILES = 3958.7613


def downsample_polyline(points: list, max_points: int = MAX_GEOMETRY_POINTS) -> list:
    """Evenly thin a polyline to at most ``max_points``, always keeping the endpoints."""
    count = len(points)
    if count <= max_points:
        return points
    step = count / max_points
    thinned = [points[int(i * step)] for i in range(max_points)]
    thinned[-1] = points[-1]
    return thinned


def haversine_miles(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    """Great-circle distance between two ``[lng, lat]`` points, in miles."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * _EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


def cumulative_miles(coords: list[list[float]]) -> list[float]:
    """Cumulative distance (miles) at each ``[lng, lat]`` vertex of the polyline."""
    cum = [0.0]
    for (lng1, lat1), (lng2, lat2) in zip(coords, coords[1:], strict=False):
        cum.append(cum[-1] + haversine_miles(lng1, lat1, lng2, lat2))
    return cum


def point_at_fraction(
    coords: list[list[float]], cum: list[float], fraction: float
) -> tuple[float, float]:
    """Return the ``(lat, lng)`` at ``fraction`` (0..1) of the polyline length."""
    if not coords:
        return (0.0, 0.0)
    total = cum[-1]
    if total <= 0 or fraction <= 0:
        return (coords[0][1], coords[0][0])
    if fraction >= 1:
        return (coords[-1][1], coords[-1][0])
    target = fraction * total
    for i in range(1, len(cum)):
        if cum[i] >= target:
            span = cum[i] - cum[i - 1] or 1.0
            t = (target - cum[i - 1]) / span
            lng = coords[i - 1][0] + t * (coords[i][0] - coords[i - 1][0])
            lat = coords[i - 1][1] + t * (coords[i][1] - coords[i - 1][1])
            return (lat, lng)
    return (coords[-1][1], coords[-1][0])


def _nearest_vertex(cum: list[float], target: float) -> int:
    """Index of the polyline vertex whose cumulative distance is closest to ``target``."""
    i = bisect.bisect_left(cum, target)
    if i <= 0:
        return 0
    if i >= len(cum):
        return len(cum) - 1
    return i if (cum[i] - target) < (target - cum[i - 1]) else i - 1


def assign_stop_coordinates(
    stops: list[Stop], coords: list[list[float]], total_route_miles: float
) -> None:
    """Snap each stop to the nearest polyline vertex.

    Markers sit exactly on a vertex of the same thinned polyline the client draws
    (with line simplification disabled), so every marker lands precisely on the route.
    """
    if not coords:
        return
    cum = cumulative_miles(coords)
    total_poly = cum[-1]
    for stop in stops:
        fraction = stop.mile_marker / total_route_miles if total_route_miles > 0 else 0.0
        fraction = min(max(fraction, 0.0), 1.0)
        idx = _nearest_vertex(cum, fraction * total_poly)
        stop.lat, stop.lng = coords[idx][1], coords[idx][0]
