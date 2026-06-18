"""Split a flat trip timeline into per-calendar-day ELD logs.

The timeline (minutes since trip start) is mapped onto the home-terminal calendar,
padded with off-duty before departure and after arrival, then sliced at each
midnight. A segment that straddles midnight is split and its mileage apportioned by
time. Every day's four status totals are guaranteed to sum to 1,440 minutes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from .constants import MINUTES_PER_DAY, MINUTES_PER_HOUR, Status
from .segments import Remark, Segment, Stop


@dataclass
class DailyLog:
    """One calendar day of duty-status data ready to draw on a log sheet."""

    day_number: int
    date: date
    segments: list[Segment]  # day-relative minutes within [0, 1440]
    totals: dict[Status, int]  # minutes per status; sums to 1,440
    miles: float = 0.0
    remarks: list[Remark] = field(default_factory=list)


def _global_timeline(segments: list[Segment], offset0: int, span_end: int) -> list[Segment]:
    """Trip segments shifted onto the calendar grid, padded off-duty at both ends."""
    out: list[Segment] = []
    if offset0 > 0:
        out.append(Segment(Status.OFF, 0, offset0, note="off duty"))
    for seg in segments:
        out.append(
            Segment(seg.status, offset0 + seg.start_min, offset0 + seg.end_min, seg.miles, seg.note)
        )
    trip_end = offset0 + (segments[-1].end_min if segments else 0)
    if trip_end < span_end:
        out.append(Segment(Status.OFF, trip_end, span_end, note="off duty"))
    return out


def _merge(day_segments: list[Segment]) -> list[Segment]:
    """Collapse consecutive same-status intervals into single log lines."""
    merged: list[Segment] = []
    for seg in day_segments:
        if merged and merged[-1].status == seg.status:
            merged[-1].end_min = seg.end_min
            merged[-1].miles += seg.miles
            merged[-1].note = merged[-1].note or seg.note
        else:
            merged.append(Segment(seg.status, seg.start_min, seg.end_min, seg.miles, seg.note))
    return merged


def split_days(segments: list[Segment], stops: list[Stop], start_dt: datetime) -> list[DailyLog]:
    """Convert the raw timeline into a list of per-day :class:`DailyLog` objects."""
    end_min = segments[-1].end_min if segments else 0
    offset0 = start_dt.hour * MINUTES_PER_HOUR + start_dt.minute
    total_grid = offset0 + end_min
    num_days = max(1, -(-total_grid // MINUTES_PER_DAY))  # ceil division
    span_end = num_days * MINUTES_PER_DAY
    timeline = _global_timeline(segments, offset0, span_end)

    days: list[DailyLog] = []
    for d in range(num_days):
        lo, hi = d * MINUTES_PER_DAY, (d + 1) * MINUTES_PER_DAY
        raw: list[Segment] = []
        for seg in timeline:
            i_start, i_end = max(seg.start_min, lo), min(seg.end_min, hi)
            if i_end <= i_start:
                continue
            frac = (i_end - i_start) / (seg.end_min - seg.start_min)
            raw.append(Segment(seg.status, i_start - lo, i_end - lo, seg.miles * frac, seg.note))
        day_segments = _merge(raw)

        totals = {s: 0 for s in Status}
        for seg in day_segments:
            totals[seg.status] += seg.duration_min
        miles = sum(seg.miles for seg in day_segments if seg.status == Status.DRIVING)

        remarks = [
            Remark(stop.start_min + offset0 - lo, stop.label, stop.kind)
            for stop in stops
            if lo <= stop.start_min + offset0 < hi
        ]
        days.append(
            DailyLog(
                d + 1, (start_dt + timedelta(days=d)).date(), day_segments, totals, miles, remarks
            )
        )
    return days
