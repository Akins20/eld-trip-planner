"""Engine data models + an INDEPENDENT compliance validator.

``validate_compliance`` re-walks an emitted timeline and re-derives the HOS clocks
from scratch, asserting every limit. It deliberately does not share code with the
simulator, so it grades the simulator's output instead of trusting it (test T28).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .constants import (
    BREAK_DRIVE_LIMIT_MIN,
    BREAK_MIN,
    CYCLE_LIMIT_MIN,
    DRIVE_LIMIT_MIN,
    RESET_MIN,
    RESTART_MIN,
    WINDOW_LIMIT_MIN,
    Status,
)


@dataclass
class Leg:
    """One driving leg of the trip (current->pickup, then pickup->dropoff)."""

    from_label: str
    to_label: str
    distance_miles: float
    kind: str  # "to_pickup" | "to_dropoff"


@dataclass
class Segment:
    """A contiguous duty-status interval, in minutes since trip start."""

    status: Status
    start_min: int
    end_min: int
    miles: float = 0.0
    note: str = ""

    @property
    def duration_min(self) -> int:
        return self.end_min - self.start_min


@dataclass
class Stop:
    """A point event placed on the map and the trip timeline."""

    kind: str
    label: str
    start_min: int
    end_min: int
    mile_marker: float
    lat: float | None = None
    lng: float | None = None


@dataclass
class Remark:
    """A location/notes annotation drawn under the log grid at a duty change."""

    minute: int  # day-relative minute (0..1440)
    location: str
    note: str = ""


@dataclass
class SimResult:
    """Raw output of the simulator before day-splitting/formatting."""

    segments: list[Segment] = field(default_factory=list)
    stops: list[Stop] = field(default_factory=list)
    total_miles: float = 0.0
    cycle_used_start_min: int = 0
    cycle_used_end_min: int = 0


def validate_compliance(segments: list[Segment]) -> list[str]:
    """Return a list of human-readable HOS/conservation violations (empty == valid)."""
    violations: list[str] = []
    if not segments:
        return ["timeline is empty"]

    # Conservation: contiguous, positive-length, starts at zero.
    if segments[0].start_min != 0:
        violations.append(f"timeline must start at minute 0, got {segments[0].start_min}")
    for i, seg in enumerate(segments):
        if seg.end_min <= seg.start_min:
            violations.append(
                f"segment {i} has non-positive duration ({seg.start_min}->{seg.end_min})"
            )
        if i > 0 and seg.start_min != segments[i - 1].end_min:
            violations.append(
                f"gap/overlap between segment {i - 1} and {i}: "
                f"{segments[i - 1].end_min} != {seg.start_min}"
            )

    # Re-derive the clocks independently and re-check every driving segment.
    drive_since_reset = 0
    since_break = 0
    cycle = 0
    window_start = 0

    for i, seg in enumerate(segments):
        d = seg.duration_min
        if seg.status == Status.DRIVING:
            drive_since_reset += d
            since_break += d
            cycle += d
            window_elapsed = seg.end_min - window_start
            if drive_since_reset > DRIVE_LIMIT_MIN:
                violations.append(f"seg {i}: 11h driving exceeded ({drive_since_reset} min)")
            if window_elapsed > WINDOW_LIMIT_MIN:
                violations.append(f"seg {i}: 14h window exceeded ({window_elapsed} min)")
            if since_break > BREAK_DRIVE_LIMIT_MIN:
                violations.append(f"seg {i}: drove >8h without a 30-min break ({since_break} min)")
            if cycle > CYCLE_LIMIT_MIN:
                violations.append(f"seg {i}: 70h cycle exceeded ({cycle} min)")
        elif seg.status == Status.ON_DUTY:
            cycle += d
            if d >= BREAK_MIN:
                since_break = 0
        else:  # OFF or SLEEPER - never counts toward the cycle
            if d >= RESTART_MIN:
                drive_since_reset = since_break = cycle = 0
                window_start = seg.end_min
            elif d >= RESET_MIN:
                drive_since_reset = since_break = 0
                window_start = seg.end_min
            elif d >= BREAK_MIN:
                since_break = 0

    return violations
