"""Shared builders for the HOS engine test suite."""

from __future__ import annotations

from datetime import datetime

from trips.hos.constants import KIND_BREAK, KIND_FUEL, KIND_REST, KIND_RESTART, Status
from trips.hos.day_splitter import DailyLog, split_days
from trips.hos.segments import Leg, SimResult
from trips.hos.simulator import simulate

SPEED = 55.0
START = datetime(2026, 6, 18, 8, 0)


def make_legs(d1: float, d2: float) -> list[Leg]:
    return [
        Leg("Chicago, IL", "Dallas, TX", d1, "to_pickup"),
        Leg("Dallas, TX", "Los Angeles, CA", d2, "to_dropoff"),
    ]


def run_sim(d1: float, d2: float, cycle_hours: float = 0.0, speed: float = SPEED) -> SimResult:
    return simulate(make_legs(d1, d2), round(cycle_hours * 60), speed)


def run_days(
    d1: float, d2: float, cycle_hours: float = 0.0, start: datetime = START, speed: float = SPEED
) -> tuple[SimResult, list[DailyLog]]:
    sim = run_sim(d1, d2, cycle_hours, speed)
    return sim, split_days(sim.segments, sim.stops, start)


def count_kind(sim: SimResult, kind: str) -> int:
    return sum(1 for s in sim.stops if s.kind == kind)


def driving_minutes(sim: SimResult) -> int:
    return sum(s.duration_min for s in sim.segments if s.status == Status.DRIVING)


def first_stop_min(sim: SimResult, kind: str) -> int | None:
    for s in sim.stops:
        if s.kind == kind:
            return s.start_min
    return None


# convenience re-exports for tests
KINDS = {"fuel": KIND_FUEL, "break": KIND_BREAK, "rest": KIND_REST, "restart": KIND_RESTART}
