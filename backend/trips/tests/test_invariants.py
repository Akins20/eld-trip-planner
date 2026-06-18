"""Property/invariant tests - group G. The master compliance re-validation."""

from __future__ import annotations

import pytest

from trips.hos.constants import MINUTES_PER_DAY, Status
from trips.hos.segments import validate_compliance

from ._helpers import run_days

# (leg1_mi, leg2_mi, cycle_hours, start_hour)
SCENARIOS = [
    (60, 40, 0, 8),
    (700, 800, 0, 8),
    (800, 1200, 0, 6),
    (1200, 1800, 0, 23),
    (300, 300, 68, 8),
    (200, 200, 70, 12),
    (200, 200, 75, 0),
    (500, 100, 40, 17),
    (0, 0, 0, 8),
    (1234, 766, 55, 21),
]


@pytest.mark.parametrize("d1,d2,cu,hh", SCENARIOS)
def test_timeline_is_compliant(d1, d2, cu, hh):
    sim, _ = run_days(d1, d2, cycle_hours=cu)
    assert validate_compliance(sim.segments) == []


@pytest.mark.parametrize("d1,d2,cu,hh", SCENARIOS)
def test_timeline_is_contiguous(d1, d2, cu, hh):
    sim, _ = run_days(d1, d2, cycle_hours=cu)
    segs = sim.segments
    assert segs[0].start_min == 0
    for prev, nxt in zip(segs, segs[1:], strict=False):
        assert nxt.start_min == prev.end_min
        assert nxt.end_min > nxt.start_min
    total = sum(s.duration_min for s in segs)
    assert total == segs[-1].end_min


@pytest.mark.parametrize("d1,d2,cu,hh", SCENARIOS)
def test_daily_totals_and_conservation(d1, d2, cu, hh):
    from datetime import datetime

    start = datetime(2026, 6, 18, hh, 0)
    sim, days = run_days(d1, d2, cycle_hours=cu, start=start)
    for day in days:
        assert sum(day.totals.values()) == MINUTES_PER_DAY
    drive_days = sum(d.totals[Status.DRIVING] for d in days)
    drive_sim = sum(s.duration_min for s in sim.segments if s.status == Status.DRIVING)
    assert drive_days == drive_sim
    assert abs(sum(d.miles for d in days) - sim.total_miles) < 0.05
