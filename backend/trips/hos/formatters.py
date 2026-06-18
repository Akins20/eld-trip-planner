"""Turn engine objects into the JSON-serializable API response (presentation only)."""

from __future__ import annotations

from datetime import datetime, timedelta

from .constants import (
    CYCLE_LIMIT_MIN,
    KIND_BREAK,
    KIND_FUEL,
    KIND_REST,
    KIND_RESTART,
    MINUTES_PER_DAY,
    MINUTES_PER_HOUR,
    Status,
)
from .day_splitter import DailyLog
from .segments import SimResult


def _h(minutes: float) -> float:
    """Minutes -> hours, rounded to 2 decimals for display."""
    return round(minutes / MINUTES_PER_HOUR, 2)


def _clock(start_dt: datetime, minute: int) -> str:
    """Absolute ``"Day N HH:MM"`` label for a trip-relative minute."""
    offset0 = start_dt.hour * MINUTES_PER_HOUR + start_dt.minute
    g = offset0 + minute
    day, tod = g // MINUTES_PER_DAY + 1, g % MINUTES_PER_DAY
    return f"Day {day} {tod // 60:02d}:{tod % 60:02d}"


def _totals_by_status(sim: SimResult) -> dict[Status, int]:
    totals = {s: 0 for s in Status}
    for seg in sim.segments:
        totals[seg.status] += seg.duration_min
    return totals


def _summary(sim: SimResult, days: list[DailyLog], start_dt: datetime) -> dict:
    totals = _totals_by_status(sim)
    drive = totals[Status.DRIVING]
    on_duty_nd = totals[Status.ON_DUTY]
    end_min = sim.segments[-1].end_min if sim.segments else 0
    kinds = [s.kind for s in sim.stops]
    return {
        "total_distance_miles": round(sim.total_miles, 1),
        "total_drive_hours": _h(drive),
        "total_on_duty_not_driving_hours": _h(on_duty_nd),
        "total_on_duty_hours": _h(drive + on_duty_nd),
        "total_off_duty_hours": _h(totals[Status.OFF]),
        "total_sleeper_hours": _h(totals[Status.SLEEPER]),
        "total_duration_hours": _h(end_min),
        "num_days": len(days),
        "num_fuel_stops": kinds.count(KIND_FUEL),
        "num_breaks": kinds.count(KIND_BREAK),
        "num_rests": kinds.count(KIND_REST),
        "num_restarts": kinds.count(KIND_RESTART),
        "cycle_used_start_hours": _h(sim.cycle_used_start_min),
        "cycle_used_end_hours": _h(sim.cycle_used_end_min),
        "cycle_hours_remaining_end": _h(max(0, CYCLE_LIMIT_MIN - sim.cycle_used_end_min)),
        "start_datetime": start_dt.isoformat(),
        "end_datetime": (start_dt + timedelta(minutes=end_min)).isoformat(),
    }


def _day_dict(day: DailyLog) -> dict:
    return {
        "day_number": day.day_number,
        "date": day.date.isoformat(),
        "miles": round(day.miles, 1),
        "totals": {status.value: _h(minutes) for status, minutes in day.totals.items()},
        "segments": [
            {
                "status": seg.status.value,
                "start_hour": round(seg.start_min / MINUTES_PER_HOUR, 4),
                "end_hour": round(seg.end_min / MINUTES_PER_HOUR, 4),
                "miles": round(seg.miles, 1),
                "note": seg.note,
            }
            for seg in day.segments
        ],
        "remarks": [
            {"hour": round(r.minute / MINUTES_PER_HOUR, 4), "location": r.location, "kind": r.note}
            for r in day.remarks
        ],
    }


def format_plan(
    inputs: dict,
    geocoded: dict,
    geometry: list[list[float]],
    leg_distances: list[float],
    sim: SimResult,
    days: list[DailyLog],
    start_dt: datetime,
) -> dict:
    """Assemble the complete ``/api/plan-trip/`` response payload."""
    labels = [
        geocoded["current"]["label"],
        geocoded["pickup"]["label"],
        geocoded["dropoff"]["label"],
    ]
    summary = _summary(sim, days, start_dt)
    return {
        "inputs": inputs,
        "geocoded": geocoded,
        "route": {
            "total_distance_miles": round(sim.total_miles, 1),
            "total_drive_hours": summary["total_drive_hours"],
            "geometry": [[lat, lng] for lng, lat in geometry],  # [lat, lng] for Leaflet
            "legs": [
                {"from": labels[i], "to": labels[i + 1], "distance_miles": round(d, 1)}
                for i, d in enumerate(leg_distances)
            ],
        },
        "summary": summary,
        "stops": [
            {
                "kind": s.kind,
                "label": s.label,
                "start_min": s.start_min,
                "start_label": _clock(start_dt, s.start_min),
                "duration_hours": _h(s.end_min - s.start_min),
                "mile_marker": round(s.mile_marker, 1),
                "lat": s.lat,
                "lng": s.lng,
            }
            for s in sim.stops
        ],
        "days": [_day_dict(day) for day in days],
    }
