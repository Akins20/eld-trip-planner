"""The HOS trip simulator - pure, deterministic, framework-agnostic.

Walks the trip leg-by-leg over an integer-minute clock, inserting fuel stops,
30-minute breaks, 10-hour resets, and 34-hour restarts exactly when FMCSA rules
require them, and emits a duty-status timeline plus point stops.

Constraint dispatch is structured as: (1) before each drive chunk, ensure the
driver may legally drive - inserting the largest applicable rest in priority order
restart > reset > break; (2) drive the largest chunk bounded by every limit, the
leg end, and the next fuel mark; (3) after the chunk, insert fuel if due. A >=30-min
on-duty fuel stop also clears the break counter, so a coincident fuel+break collapses
to a single stop.
"""

from __future__ import annotations

from .constants import (
    BREAK_MIN,
    DROPOFF_MIN,
    EPS_MILES,
    FUEL_MIN,
    KIND_BREAK,
    KIND_DROPOFF,
    KIND_FUEL,
    KIND_PICKUP,
    KIND_REST,
    KIND_RESTART,
    KIND_START,
    PICKUP_MIN,
    Status,
)
from .segments import Leg, Segment, SimResult, Stop
from .state import SimState, miles_for_minutes, minutes_for_miles


def simulate(
    legs: list[Leg],
    current_cycle_used_min: int,
    avg_speed_mph: float,
) -> SimResult:
    """Run the simulation and return the raw timeline (segments + stops)."""
    state = SimState(cycle_used=max(0, current_cycle_used_min))
    segments: list[Segment] = []
    stops: list[Stop] = []
    origin_label = legs[0].from_label if legs else "Origin"

    # --- segment/stop emitters (mutate state + record output together) ---
    def drive(minutes: int, miles: float) -> None:
        start = state.current_min
        state.apply_drive(minutes, miles)
        segments.append(Segment(Status.DRIVING, start, state.current_min, miles))

    def on_duty(minutes: int, kind: str, label: str) -> None:
        start, mile = state.current_min, state.total_miles
        state.apply_on_duty(minutes)
        segments.append(Segment(Status.ON_DUTY, start, state.current_min, note=label))
        stops.append(Stop(kind, label, start, state.current_min, mile))

    def fuel() -> None:
        start, mile = state.current_min, state.total_miles
        state.apply_on_duty(FUEL_MIN)
        state.refuel()
        label = f"Fuel stop (mi {mile:,.0f})"
        segments.append(Segment(Status.ON_DUTY, start, state.current_min, note=label))
        stops.append(Stop(KIND_FUEL, label, start, state.current_min, mile))

    def off_break() -> None:
        start, mile = state.current_min, state.total_miles
        state.apply_off_break(BREAK_MIN)
        segments.append(Segment(Status.OFF, start, state.current_min, note="30-min break"))
        stops.append(Stop(KIND_BREAK, "30-min break", start, state.current_min, mile))

    def rest() -> None:
        start, mile = state.current_min, state.total_miles
        state.apply_reset()
        segments.append(Segment(Status.SLEEPER, start, state.current_min, note="10-hr rest"))
        stops.append(Stop(KIND_REST, "10-hr rest", start, state.current_min, mile))

    def restart(label: str) -> None:
        start, mile = state.current_min, state.total_miles
        state.apply_restart()
        segments.append(Segment(Status.OFF, start, state.current_min, note=label))
        stops.append(Stop(KIND_RESTART, label, start, state.current_min, mile))

    def ensure_can_drive() -> None:
        """Insert the largest applicable rest until the driver may legally drive."""
        while True:
            if state.cycle_remaining() <= 0:
                restart("34-hr restart (70-hr cycle reached)")
            elif state.drive_remaining() <= 0 or state.window_remaining() <= 0:
                rest()
            elif state.break_remaining() <= 0:
                # Only break if there is window left to drive afterwards; else reset.
                off_break() if state.window_remaining() > BREAK_MIN else rest()
            else:
                return

    # --- precondition: an exhausted cycle means a restart before any driving ---
    if state.cycle_remaining() <= 0:
        restart("34-hr restart (cycle exhausted at start)")
    stops.append(Stop(KIND_START, f"Depart - {origin_label}", 0, 0, 0.0))

    # --- drive each leg, then perform its boundary activity ---
    for leg_index, leg in enumerate(legs):
        is_last_leg = leg_index == len(legs) - 1
        remaining = leg.distance_miles
        while remaining > EPS_MILES:
            if minutes_for_miles(remaining, avg_speed_mph) == 0:
                remaining = 0.0  # sub-minute remainder: treat as arrived
                break
            ensure_can_drive()
            leg_min = minutes_for_miles(remaining, avg_speed_mph)
            fuel_min = minutes_for_miles(state.miles_to_next_fuel, avg_speed_mph)
            chunk = min(
                state.drive_remaining(),
                state.window_remaining(),
                state.break_remaining(),
                state.cycle_remaining(),
                leg_min,
                fuel_min,
            )
            if chunk >= leg_min:  # leg finishes (wins ties - never an unneeded stop)
                minutes, miles = leg_min, remaining
            elif chunk == fuel_min:  # stop exactly on the 1,000-mile fuel mark
                minutes, miles = fuel_min, state.miles_to_next_fuel
            else:  # a duty/window/break/cycle limit binds: drive up to it
                minutes = chunk
                miles = miles_for_minutes(minutes, avg_speed_mph)
            drive(minutes, miles)
            remaining = max(0.0, remaining - miles)
            arrived_final = is_last_leg and remaining <= EPS_MILES
            if state.miles_to_next_fuel <= EPS_MILES and not arrived_final:
                fuel()

        if leg.kind == "to_pickup":
            on_duty(PICKUP_MIN, KIND_PICKUP, f"Pickup - {leg.to_label}")
        elif leg.kind == "to_dropoff":
            on_duty(DROPOFF_MIN, KIND_DROPOFF, f"Dropoff - {leg.to_label}")

    stops.sort(key=lambda s: (s.start_min, s.end_min))
    return SimResult(
        segments=segments,
        stops=stops,
        total_miles=state.total_miles,
        cycle_used_start_min=max(0, current_cycle_used_min),
        cycle_used_end_min=state.cycle_used,
    )
