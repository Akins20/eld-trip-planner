"""HOS simulator unit tests - groups A-E of the test matrix."""

from __future__ import annotations

from trips.hos.constants import Status
from trips.hos.segments import validate_compliance

from ._helpers import count_kind, driving_minutes, first_stop_min, run_sim


def _driving_segments(sim):
    return [s for s in sim.segments if s.status == Status.DRIVING]


# --- Group A: single-day, no special events --------------------------------
def test_short_trip_has_no_special_stops():
    sim = run_sim(60, 40)
    for kind in ("fuel", "break", "rest", "restart"):
        assert count_kind(sim, kind) == 0
    assert len(_driving_segments(sim)) == 2  # one continuous drive per leg
    on_duty = sum(s.duration_min for s in sim.segments if s.status == Status.ON_DUTY)
    assert on_duty == 120  # 1h pickup + 1h dropoff
    assert validate_compliance(sim.segments) == []


def test_driving_split_by_pickup_avoids_break():
    # 300 + 200 mi: each leg is < 8 h, and the pickup resets the break clock.
    sim = run_sim(300, 200)
    assert count_kind(sim, "break") == 0


# --- Group B: 30-minute break boundary -------------------------------------
def test_break_inserted_after_8h_driving():
    sim = run_sim(500, 100)  # leg 0 is ~9.1 h of continuous driving
    assert count_kind(sim, "break") == 1
    brk = first_stop_min(sim, "break")
    drove_before = sum(
        s.duration_min for s in sim.segments if s.status == Status.DRIVING and s.end_min <= brk
    )
    assert drove_before == 8 * 60  # break lands exactly at the 8-hour mark


def test_no_break_when_leg_ends_exactly_at_8h():
    # 440 mi == exactly 8.0 h driving; arrival (pickup) wins the tie, no break.
    sim = run_sim(440, 100)
    assert count_kind(sim, "break") == 0
    assert validate_compliance(sim.segments) == []


def test_coincident_fuel_and_break_collapse_to_one_stop():
    # At 125 mph, 1,000 mi == 8.0 h: fuel and break fall together -> single stop.
    sim = run_sim(1100, 0, speed=125.0)
    assert count_kind(sim, "fuel") == 1
    assert count_kind(sim, "break") == 0  # the on-duty fuel stop satisfies the break


# --- Group C: fuel placement -----------------------------------------------
def test_one_fuel_stop_on_1500_mile_trip():
    sim = run_sim(700, 800)
    assert count_kind(sim, "fuel") == 1


def test_two_fuel_stops_on_2100_mile_trip():
    sim = run_sim(900, 1200)
    assert count_kind(sim, "fuel") == 2


def test_no_fuel_when_dropoff_lands_on_fuel_mark():
    sim = run_sim(700, 300)  # dropoff at exactly mile 1,000 == final arrival
    assert count_kind(sim, "fuel") == 0


# --- Group D: 11-hour limit and 10-hour reset ------------------------------
def test_rest_inserted_after_11h_driving():
    sim = run_sim(700, 0)  # ~12.7 h of driving in one leg
    assert count_kind(sim, "rest") == 1
    assert count_kind(sim, "break") == 1  # break at 8 h precedes the 11 h reset
    assert validate_compliance(sim.segments) == []


def test_long_trip_takes_multiple_rests():
    sim = run_sim(800, 1200)  # 2,000 mi
    assert count_kind(sim, "rest") >= 3
    assert validate_compliance(sim.segments) == []


# --- Group E: 70-hour cycle and 34-hour restart ----------------------------
def test_restart_when_cycle_exhausted_midtrip():
    sim = run_sim(300, 300, cycle_hours=68)
    assert count_kind(sim, "restart") == 1
    assert validate_compliance(sim.segments) == []


def test_restart_at_start_when_cycle_full():
    sim = run_sim(200, 200, cycle_hours=70)
    assert count_kind(sim, "restart") == 1
    assert sim.segments[0].status == Status.OFF
    assert sim.segments[0].duration_min == 34 * 60  # the trip opens with a 34h restart


def test_over_limit_cycle_is_graceful():
    sim = run_sim(200, 200, cycle_hours=75)
    assert count_kind(sim, "restart") == 1
    assert driving_minutes(sim) > 0
    assert validate_compliance(sim.segments) == []


def test_negative_cycle_treated_as_zero():
    sim = run_sim(200, 200, cycle_hours=-5)
    assert count_kind(sim, "restart") == 0
    assert validate_compliance(sim.segments) == []
