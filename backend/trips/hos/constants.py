"""FMCSA Hours-of-Service rule constants - the single source of truth.

Property-carrying driver, 70-hour/8-day cycle, no adverse driving conditions.
All durations are in **integer minutes** so the simulator's arithmetic is exact
and the "daily totals sum to 1440 minutes" invariant is provable, not approximate.
"""

from __future__ import annotations

from enum import StrEnum


class Status(StrEnum):
    """The four duty statuses drawn on an ELD daily log grid."""

    OFF = "off_duty"
    SLEEPER = "sleeper"
    DRIVING = "driving"
    ON_DUTY = "on_duty"


# Statuses that count against the 70-hour cycle (on-duty time).
ON_DUTY_STATUSES: frozenset[Status] = frozenset({Status.DRIVING, Status.ON_DUTY})

# --- FMCSA limits (minutes) ---
DRIVE_LIMIT_MIN = 11 * 60  # 11-hour driving limit
WINDOW_LIMIT_MIN = 14 * 60  # 14-hour on-duty driving window
BREAK_DRIVE_LIMIT_MIN = 8 * 60  # 30-min break required after 8 cumulative driving hours
CYCLE_LIMIT_MIN = 70 * 60  # 70-hour / 8-day on-duty limit
RESET_MIN = 10 * 60  # 10 consecutive hours off resets the 11/14 clocks
RESTART_MIN = 34 * 60  # 34 consecutive hours off resets the 70-hour cycle

# --- Activity durations (minutes) ---
PICKUP_MIN = 60  # 1 hour on-duty at pickup (assessment assumption)
DROPOFF_MIN = 60  # 1 hour on-duty at dropoff (assessment assumption)
FUEL_MIN = 30  # on-duty fueling stop; >= BREAK_MIN so it also satisfies a 30-min break
BREAK_MIN = 30  # 30-minute off-duty break

# --- Fueling ---
FUEL_INTERVAL_MILES = 1000.0  # fuel at least once every 1,000 miles

# --- Defaults / tolerances ---
DEFAULT_AVG_SPEED_MPH = 55.0
EPS_MILES = 1e-6
MINUTES_PER_HOUR = 60
MINUTES_PER_DAY = 1440
# Cap on route polyline points sent to the client. Stops are placed on this same
# thinned line so every marker lands exactly on the drawn route.
MAX_GEOMETRY_POINTS = 1500

# --- Stop kinds (point events for the map + timeline) ---
KIND_START = "start"
KIND_PICKUP = "pickup"
KIND_DROPOFF = "dropoff"
KIND_FUEL = "fuel"
KIND_BREAK = "break"
KIND_REST = "rest"  # 10-hour reset (sleeper berth)
KIND_RESTART = "restart"  # 34-hour cycle restart (off duty)
