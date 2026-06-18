"""Shared types and errors for map/routing providers (no provider imports here)."""

from __future__ import annotations

from dataclasses import dataclass

METERS_PER_MILE = 1609.344


@dataclass
class Place:
    """A geocoded location."""

    label: str
    lat: float
    lng: float

    def as_dict(self) -> dict:
        return {"label": self.label, "lat": self.lat, "lng": self.lng}


@dataclass
class RouteResult:
    """A routed path: full polyline plus per-leg and total distances (miles)."""

    geometry: list[list[float]]  # [[lng, lat], ...]
    leg_distances_miles: list[float]
    total_distance_miles: float


class MapProviderError(Exception):
    """Base class for map/routing failures."""


class LocationNotFound(MapProviderError):
    """A user-supplied location could not be geocoded (maps to HTTP 400)."""


class UpstreamServiceError(MapProviderError):
    """The routing/geocoding provider failed or is misconfigured (maps to HTTP 502)."""
