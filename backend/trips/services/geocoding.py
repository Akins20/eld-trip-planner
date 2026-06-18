"""OpenRouteService geocoding (Pelias) - text location -> coordinates."""

from __future__ import annotations

import requests

from .base import LocationNotFound, Place, UpstreamServiceError


def ors_geocode(text: str, api_key: str, base_url: str, timeout: float) -> Place:
    """Geocode a free-text location to a :class:`Place` via ORS /geocode/search."""
    url = f"{base_url}/geocode/search"
    params = {"api_key": api_key, "text": text, "size": 1}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as exc:
        raise UpstreamServiceError(f"Geocoding request failed: {exc}") from exc

    if resp.status_code != 200:
        raise UpstreamServiceError(f"Geocoding returned HTTP {resp.status_code}")

    features = (resp.json() or {}).get("features") or []
    if not features:
        raise LocationNotFound(f"Could not find a location matching '{text}'.")

    feature = features[0]
    coords = ((feature or {}).get("geometry") or {}).get("coordinates") or []
    try:
        lng, lat = float(coords[0]), float(coords[1])
    except (IndexError, TypeError, ValueError) as exc:
        raise LocationNotFound(f"Could not find a usable location for '{text}'.") from exc
    label = feature.get("properties", {}).get("label") or text
    return Place(label=label, lat=lat, lng=lng)
