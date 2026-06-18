"""OpenRouteService directions - waypoints -> polyline + per-leg distances."""

from __future__ import annotations

import logging

import requests

from .base import METERS_PER_MILE, RouteResult, UpstreamServiceError

logger = logging.getLogger(__name__)


def ors_route(
    coordinates: list[tuple[float, float]],
    api_key: str,
    base_url: str,
    profile: str,
    timeout: float,
) -> RouteResult:
    """Route through ``coordinates`` ((lng, lat) order) via ORS GeoJSON directions."""
    url = f"{base_url}/v2/directions/{profile}/geojson"
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    # Keep per-leg `segments` (needed for leg distances) but skip step text and
    # simplify the line for a smaller payload and faster map rendering.
    body = {
        "coordinates": [[lng, lat] for lng, lat in coordinates],
        "instructions": True,
        "instructions_format": "text",
        "geometry_simplify": True,
    }
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise UpstreamServiceError(f"Routing request failed: {exc}") from exc

    if resp.status_code != 200:
        # Log the provider body server-side; do not leak it to the client.
        logger.warning("ORS routing HTTP %s: %s", resp.status_code, resp.text[:300])
        raise UpstreamServiceError(f"Routing provider returned HTTP {resp.status_code}.")

    features = (resp.json() or {}).get("features") or []
    if not features:
        raise UpstreamServiceError("Routing returned no route for the given locations.")

    try:
        feature = features[0]
        geometry = feature["geometry"]["coordinates"]
        segments = feature["properties"]["segments"]
        leg_miles = [seg["distance"] / METERS_PER_MILE for seg in segments]
        total_miles = feature["properties"]["summary"]["distance"] / METERS_PER_MILE
    except (KeyError, TypeError, IndexError, ValueError) as exc:
        logger.warning("Malformed ORS routing response: %s", exc)
        raise UpstreamServiceError("Routing provider returned a malformed response.") from exc

    return RouteResult(
        geometry=geometry, leg_distances_miles=leg_miles, total_distance_miles=total_miles
    )
