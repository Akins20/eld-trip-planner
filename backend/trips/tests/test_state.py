"""SimState clock + unit-conversion tests."""

from __future__ import annotations

from trips.hos.state import SimState, miles_for_minutes, minutes_for_miles


def test_minutes_for_miles_handles_non_positive():
    assert minutes_for_miles(0, 55) == 0
    assert minutes_for_miles(-5, 55) == 0


def test_conversions_are_consistent():
    assert minutes_for_miles(55, 55) == 60
    assert miles_for_minutes(60, 55) == 55.0


def test_fresh_state_budgets():
    s = SimState()
    assert s.drive_remaining() == 11 * 60
    assert s.window_remaining() == 14 * 60
    assert s.break_remaining() == 8 * 60
    assert s.cycle_remaining() == 70 * 60


def test_reset_clears_daily_clocks_but_not_cycle():
    s = SimState(drive_since_reset=600, since_break=400, cycle_used=1000, current_min=600)
    s.apply_reset()
    assert s.drive_since_reset == 0
    assert s.since_break == 0
    assert s.window_remaining() == 14 * 60
    assert s.cycle_used == 1000  # a 10h reset never touches the 70h cycle


def test_restart_clears_everything():
    s = SimState(drive_since_reset=600, since_break=400, cycle_used=4000, current_min=600)
    s.apply_restart()
    assert s.cycle_used == 0
    assert s.drive_since_reset == 0
