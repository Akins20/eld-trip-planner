"""Geo interpolation tests - group H (stops snap onto the route polyline)."""

from __future__ import annotations

from trips.hos.geo import (
    assign_stop_coordinates,
    cumulative_miles,
    downsample_polyline,
    point_at_fraction,
)
from trips.hos.segments import Stop

# A simple polyline along the longitude axis at latitude 0: [lng, lat] pairs.
COORDS = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0]]


def _stop(mile: float) -> Stop:
    return Stop(kind="fuel", label="x", start_min=0, end_min=30, mile_marker=mile)


def test_endpoints_snap_exactly():
    cum = cumulative_miles(COORDS)
    total = cum[-1]
    stops = [_stop(0.0), _stop(total)]
    assign_stop_coordinates(stops, COORDS, total)
    assert stops[0].lat == 0.0 and stops[0].lng == 0.0  # mile 0 -> first vertex
    assert stops[1].lat == 0.0 and abs(stops[1].lng - 3.0) < 1e-9  # last vertex


def test_midpoint_snaps_to_a_vertex_on_the_line():
    cum = cumulative_miles(COORDS)
    total = cum[-1]
    stops = [_stop(total / 2)]
    assign_stop_coordinates(stops, COORDS, total)
    assert abs(stops[0].lat - 0.0) < 1e-9  # on the lat-0 drawn line
    assert stops[0].lng in (1.0, 2.0)  # snapped to a polyline vertex


def test_fraction_clamps_outside_range():
    cum = cumulative_miles(COORDS)
    assert point_at_fraction(COORDS, cum, -1.0) == (0.0, 0.0)
    assert point_at_fraction(COORDS, cum, 5.0) == (0.0, 3.0)


def test_cumulative_is_monotonic():
    cum = cumulative_miles(COORDS)
    assert cum[0] == 0.0
    assert all(b > a for a, b in zip(cum, cum[1:], strict=False))


def test_empty_coords_is_safe():
    stop = _stop(10.0)
    assign_stop_coordinates([stop], [], 100.0)  # no geometry -> no crash, no coords
    assert stop.lat is None and stop.lng is None
    assert point_at_fraction([], [], 0.5) == (0.0, 0.0)


def test_downsample_polyline_thins_and_keeps_endpoints():
    pts = [[i, i] for i in range(5000)]
    out = downsample_polyline(pts)
    assert len(out) == 1500
    assert out[0] == [0, 0] and out[-1] == [4999, 4999]


def test_downsample_polyline_noop_when_already_small():
    pts = [[0, 0], [1, 1], [2, 2]]
    assert downsample_polyline(pts) is pts


def test_stop_lands_on_a_drawn_segment():
    # A stop interpolated on the SAME polyline the client draws must lie on a segment.
    stop = _stop(110.0)
    assign_stop_coordinates([stop], COORDS, cumulative_miles(COORDS)[-1])
    assert abs(stop.lat - 0.0) < 1e-9  # on the lat-0 drawn line
