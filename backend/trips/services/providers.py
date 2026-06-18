"""Map-provider abstraction + factory.

The rest of the app depends only on the ``MapProvider`` protocol, so swapping
OpenRouteService for another provider (Mapbox, OSRM, ...) is a localized change.
"""

from __future__ import annotations

from typing import Protocol

from django.conf import settings

from .base import Place, RouteResult, UpstreamServiceError
from .geocoding import ors_geocode
from .routing import ors_route


class MapProvider(Protocol):
    """Geocoding + routing capability used by the trip planner."""

    def geocode(self, text: str) -> Place: ...

    def route(self, coordinates: list[tuple[float, float]]) -> RouteResult: ...


class ORSProvider:
    """OpenRouteService-backed provider (truck profile ``driving-hgv``)."""

    def __init__(self, api_key: str, base_url: str, profile: str, timeout: float) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._profile = profile
        self._timeout = timeout

    def geocode(self, text: str) -> Place:
        return ors_geocode(text, self._api_key, self._base_url, self._timeout)

    def route(self, coordinates: list[tuple[float, float]]) -> RouteResult:
        return ors_route(coordinates, self._api_key, self._base_url, self._profile, self._timeout)


def get_map_provider() -> MapProvider:
    """Build the configured map provider from Django settings."""
    provider = settings.MAP_PROVIDER
    if provider == "openrouteservice":
        if not settings.ORS_API_KEY:
            raise UpstreamServiceError("ORS_API_KEY is not configured on the server.")
        return ORSProvider(
            api_key=settings.ORS_API_KEY,
            base_url=settings.ORS_BASE_URL,
            profile="driving-hgv",
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
    raise UpstreamServiceError(f"Unknown MAP_PROVIDER '{provider}'.")
