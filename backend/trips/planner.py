"""Trip-planning orchestrator: geocode -> route -> simulate -> split -> format.

This is the only module the API view calls. It wires the map provider (network) to
the pure HOS engine (computation); each step is a single call, keeping the view thin.
"""

from __future__ import annotations

from datetime import datetime

from .hos.constants import MINUTES_PER_HOUR
from .hos.day_splitter import split_days
from .hos.formatters import format_plan
from .hos.geo import assign_stop_coordinates, downsample_polyline
from .hos.segments import Leg
from .hos.simulator import simulate
from .services.base import UpstreamServiceError
from .services.providers import get_map_provider


def build_trip_plan(
    current_location: str,
    pickup_location: str,
    dropoff_location: str,
    current_cycle_used: float,
    start_dt: datetime,
    avg_speed_mph: float,
) -> dict:
    """Resolve locations, route the trip, run the HOS simulation, and format output."""
    provider = get_map_provider()
    current = provider.geocode(current_location)
    pickup = provider.geocode(pickup_location)
    dropoff = provider.geocode(dropoff_location)

    coordinates = [
        (current.lng, current.lat),
        (pickup.lng, pickup.lat),
        (dropoff.lng, dropoff.lat),
    ]
    route = provider.route(coordinates)
    leg_miles = list(route.leg_distances_miles)
    if len(leg_miles) > 2:  # 3 waypoints must yield <=2 legs; fail loud if not
        raise UpstreamServiceError("Router returned an unexpected number of legs.")
    leg1, leg2 = (leg_miles + [0.0, 0.0])[:2]

    legs = [
        Leg(current.label, pickup.label, leg1, "to_pickup"),
        Leg(pickup.label, dropoff.label, leg2, "to_dropoff"),
    ]
    sim = simulate(legs, round(current_cycle_used * MINUTES_PER_HOUR), avg_speed_mph)
    # Thin the polyline once, then place stops on that same line so every marker
    # lands exactly on the route that the client draws.
    geometry = downsample_polyline(route.geometry)
    assign_stop_coordinates(sim.stops, geometry, sim.total_miles)
    days = split_days(sim.segments, sim.stops, start_dt)

    geocoded = {
        "current": current.as_dict(),
        "pickup": pickup.as_dict(),
        "dropoff": dropoff.as_dict(),
    }
    inputs = {
        "current_location": current_location,
        "pickup_location": pickup_location,
        "dropoff_location": dropoff_location,
        "current_cycle_used": current_cycle_used,
        "start_datetime": start_dt.isoformat(),
    }
    return format_plan(inputs, geocoded, geometry, [leg1, leg2], sim, days, start_dt)
