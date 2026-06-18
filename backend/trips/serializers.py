"""Request validation for the trip-planning API."""

from __future__ import annotations

import math

from rest_framework import serializers


class PlanTripSerializer(serializers.Serializer):
    """Validates the four trip inputs (plus an optional start time)."""

    current_location = serializers.CharField(max_length=200, trim_whitespace=True)
    pickup_location = serializers.CharField(max_length=200, trim_whitespace=True)
    dropoff_location = serializers.CharField(max_length=200, trim_whitespace=True)
    current_cycle_used = serializers.FloatField(min_value=0, max_value=70)
    start_datetime = serializers.DateTimeField(required=False, allow_null=True)

    def validate_current_cycle_used(self, value: float) -> float:
        # NaN slips past min/max (all comparisons are False); reject non-finite values.
        if not math.isfinite(value):
            raise serializers.ValidationError("Must be a finite number between 0 and 70.")
        return value
