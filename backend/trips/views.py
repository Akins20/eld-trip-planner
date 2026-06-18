"""Thin DRF views. All business logic lives in ``trips.planner`` / ``trips.hos``."""

from __future__ import annotations

from datetime import datetime, time

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .planner import build_trip_plan
from .serializers import PlanTripSerializer
from .services.base import LocationNotFound, MapProviderError


def _default_start() -> datetime:
    """Default departure: 08:00 (home-terminal wall clock) on the current date."""
    return datetime.combine(datetime.now().date(), time(8, 0))


@api_view(["GET"])
def health(request: Request) -> Response:
    """Liveness probe for uptime checks and smoke tests."""
    return Response({"status": "ok"})


@api_view(["POST"])
def plan_trip(request: Request) -> Response:
    """Validate trip inputs, build the route + HOS plan, and return it as JSON."""
    serializer = PlanTripSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # -> HTTP 400 with field errors
    data = serializer.validated_data

    start_dt = data.get("start_datetime") or _default_start()
    if start_dt.tzinfo is not None:
        start_dt = start_dt.replace(tzinfo=None)  # treat as home-terminal local time

    try:
        plan = build_trip_plan(
            current_location=data["current_location"],
            pickup_location=data["pickup_location"],
            dropoff_location=data["dropoff_location"],
            current_cycle_used=data["current_cycle_used"],
            start_dt=start_dt,
            avg_speed_mph=settings.AVG_SPEED_MPH,
        )
    except LocationNotFound as exc:
        return Response({"error": str(exc)}, status=400)
    except MapProviderError as exc:
        return Response({"error": str(exc)}, status=502)
    except (ValueError, TypeError):
        # Defensive: malformed numeric input that slipped past validation -> 400, not 500.
        return Response({"error": "Could not process the trip inputs."}, status=400)
    return Response(plan)
