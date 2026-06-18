"""The simulation clock state - integer-minute HOS counters and their mutations.

All time is integer minutes. Mileage is float (route distances). Centralizing every
mutation here keeps the simulator readable and the arithmetic auditable.
"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    BREAK_DRIVE_LIMIT_MIN,
    BREAK_MIN,
    CYCLE_LIMIT_MIN,
    DRIVE_LIMIT_MIN,
    FUEL_INTERVAL_MILES,
    MINUTES_PER_HOUR,
    RESET_MIN,
    RESTART_MIN,
    WINDOW_LIMIT_MIN,
)


def minutes_for_miles(miles: float, speed_mph: float) -> int:
    """Driving minutes to cover ``miles`` at ``speed_mph`` (rounded to the minute)."""
    if miles <= 0:
        return 0
    return round(miles / speed_mph * MINUTES_PER_HOUR)


def miles_for_minutes(minutes: int, speed_mph: float) -> float:
    """Miles covered by driving ``minutes`` at ``speed_mph``."""
    return minutes / MINUTES_PER_HOUR * speed_mph


@dataclass
class SimState:
    """Live HOS clocks during a trip simulation (minutes since trip start)."""

    current_min: int = 0
    window_start_min: int = 0
    drive_since_reset: int = 0
    since_break: int = 0
    cycle_used: int = 0
    miles_to_next_fuel: float = FUEL_INTERVAL_MILES
    total_miles: float = 0.0

    # --- Remaining budgets (minutes) before each limit binds ---
    def drive_remaining(self) -> int:
        return DRIVE_LIMIT_MIN - self.drive_since_reset

    def window_remaining(self) -> int:
        return WINDOW_LIMIT_MIN - (self.current_min - self.window_start_min)

    def break_remaining(self) -> int:
        return BREAK_DRIVE_LIMIT_MIN - self.since_break

    def cycle_remaining(self) -> int:
        return CYCLE_LIMIT_MIN - self.cycle_used

    # --- Mutations (each corresponds to one emitted segment) ---
    def apply_drive(self, minutes: int, miles: float) -> None:
        self.current_min += minutes
        self.drive_since_reset += minutes
        self.since_break += minutes
        self.cycle_used += minutes
        self.total_miles += miles
        self.miles_to_next_fuel -= miles

    def apply_on_duty(self, minutes: int) -> None:
        """On-duty, not driving (pickup/dropoff/fuel): counts toward the cycle."""
        self.current_min += minutes
        self.cycle_used += minutes
        if minutes >= BREAK_MIN:
            self.since_break = 0

    def apply_off_break(self, minutes: int) -> None:
        """A short off-duty break: consumes the 14h window but not the cycle."""
        self.current_min += minutes
        if minutes >= BREAK_MIN:
            self.since_break = 0

    def apply_reset(self) -> None:
        """10 consecutive hours off (sleeper): restart the 11h and 14h clocks."""
        self.current_min += RESET_MIN
        self.drive_since_reset = 0
        self.since_break = 0
        self.window_start_min = self.current_min

    def apply_restart(self) -> None:
        """34 consecutive hours off: also reset the 70h cycle (superset of a reset)."""
        self.current_min += RESTART_MIN
        self.drive_since_reset = 0
        self.since_break = 0
        self.cycle_used = 0
        self.window_start_min = self.current_min

    def refuel(self) -> None:
        self.miles_to_next_fuel = FUEL_INTERVAL_MILES
