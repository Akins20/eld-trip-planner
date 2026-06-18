"""Formatter tests - engine objects render to the documented API shape."""

from __future__ import annotations

from trips.hos.day_splitter import split_days
from trips.hos.formatters import format_plan
from trips.hos.geo import assign_stop_coordinates

from ._helpers import START, run_sim

# Chicago -> Dallas -> Los Angeles, as [lng, lat] (ORS order).
GEOMETRY = [[-87.63, 41.88], [-96.80, 32.78], [-118.24, 34.05]]
GEOCODED = {
    "current": {"label": "Chicago, IL", "lat": 41.88, "lng": -87.63},
    "pickup": {"label": "Dallas, TX", "lat": 32.78, "lng": -96.80},
    "dropoff": {"label": "Los Angeles, CA", "lat": 34.05, "lng": -118.24},
}


def _build():
    sim = run_sim(700, 800)
    assign_stop_coordinates(sim.stops, GEOMETRY, sim.total_miles)
    days = split_days(sim.segments, sim.stops, START)
    return format_plan({"current_cycle_used": 0}, GEOCODED, GEOMETRY, [700, 800], sim, days, START)


def test_top_level_shape():
    out = _build()
    assert set(out) == {"inputs", "geocoded", "route", "summary", "stops", "days"}


def test_geometry_is_lat_lng_for_leaflet():
    out = _build()
    assert out["route"]["geometry"][0] == [41.88, -87.63]  # flipped from [lng, lat]


def test_summary_counts_and_distance():
    out = _build()
    summary = out["summary"]
    assert summary["num_days"] == len(out["days"])
    assert summary["total_distance_miles"] == 1500.0
    assert summary["num_fuel_stops"] == 1


def test_each_day_totals_sum_to_24_hours():
    out = _build()
    for day in out["days"]:
        assert abs(sum(day["totals"].values()) - 24.0) < 0.05
        for seg in day["segments"]:
            assert 0.0 <= seg["start_hour"] <= seg["end_hour"] <= 24.0


def test_stops_have_coordinates_and_clock_labels():
    out = _build()
    assert out["stops"], "expected at least the start stop"
    for stop in out["stops"]:
        assert stop["lat"] is not None and stop["lng"] is not None
        assert stop["start_label"].startswith("Day ")
