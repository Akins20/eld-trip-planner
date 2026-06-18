"""Day-splitter unit tests - group F (multi-day + midnight handling)."""

from __future__ import annotations

from datetime import datetime

from trips.hos.constants import MINUTES_PER_DAY, Status

from ._helpers import run_days


def test_multiday_each_day_sums_to_1440():
    sim, days = run_days(800, 1200)  # 2,000 mi
    assert len(days) >= 3
    for day in days:
        assert sum(day.totals.values()) == MINUTES_PER_DAY


def test_segment_crossing_midnight_is_split_with_apportioned_mileage():
    start = datetime(2026, 6, 18, 23, 0)  # depart 23:00 -> drive crosses midnight
    sim, days = run_days(100, 0, start=start)
    assert len(days) == 2
    assert days[0].totals[Status.DRIVING] > 0
    assert days[1].totals[Status.DRIVING] > 0
    drive_days = sum(d.totals[Status.DRIVING] for d in days)
    drive_sim = sum(s.duration_min for s in sim.segments if s.status == Status.DRIVING)
    assert drive_days == drive_sim
    assert abs(sum(d.miles for d in days) - sim.total_miles) < 0.01


def test_full_off_duty_day_inside_restart_still_emitted():
    # Cycle full at start -> 34h restart; a whole calendar day falls inside it.
    sim, days = run_days(200, 200, cycle_hours=70, start=datetime(2026, 6, 18, 20, 0))
    assert any(day.totals[Status.OFF] == MINUTES_PER_DAY for day in days)
    for day in days:
        assert sum(day.totals.values()) == MINUTES_PER_DAY
