"""The compliance validator must actually CATCH violations (it grades the engine)."""

from __future__ import annotations

from trips.hos.constants import Status
from trips.hos.segments import Segment, validate_compliance


def test_empty_timeline_is_flagged():
    assert validate_compliance([]) == ["timeline is empty"]


def test_detects_11h_driving_violation():
    segs = [Segment(Status.DRIVING, 0, 12 * 60, 660.0)]  # 12h straight
    violations = validate_compliance(segs)
    assert any("11h driving" in v for v in violations)


def test_detects_gap_in_timeline():
    segs = [Segment(Status.DRIVING, 0, 100, 90.0), Segment(Status.OFF, 200, 300)]
    assert any("gap/overlap" in v for v in validate_compliance(segs))


def test_detects_non_zero_start():
    assert any("start at minute 0" in v for v in validate_compliance([Segment(Status.OFF, 10, 20)]))


def test_detects_non_positive_duration():
    assert any("non-positive" in v for v in validate_compliance([Segment(Status.OFF, 0, 0)]))


def test_detects_70h_cycle_violation():
    segs = [
        Segment(Status.ON_DUTY, 0, 70 * 60),
        Segment(Status.DRIVING, 70 * 60, 70 * 60 + 60, 55.0),
    ]
    assert any("70h cycle" in v for v in validate_compliance(segs))


def test_reset_clears_clocks_so_long_trip_validates():
    # 8h drive, 10h sleeper reset, 8h drive -> 16h total driving, compliant because the
    # reset clears the 11h clock and each block is exactly at the 8h break limit.
    segs = [
        Segment(Status.DRIVING, 0, 8 * 60, 440.0),
        Segment(Status.SLEEPER, 8 * 60, 18 * 60),
        Segment(Status.DRIVING, 18 * 60, 26 * 60, 440.0),
    ]
    assert validate_compliance(segs) == []
