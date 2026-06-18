"""Unit tests for the ORS service wrappers' error handling."""

from __future__ import annotations

import pytest
import requests
import responses

from trips.services.base import LocationNotFound, UpstreamServiceError
from trips.services.geocoding import ors_geocode
from trips.services.routing import ors_route

BASE = "https://api.openrouteservice.org"
GEOCODE = f"{BASE}/geocode/search"
ROUTE = f"{BASE}/v2/directions/driving-hgv/geojson"


@responses.activate
def test_geocode_success_parses_label_and_coords():
    body = {
        "features": [
            {"geometry": {"coordinates": [-87.6, 41.9]}, "properties": {"label": "Chicago, IL"}}
        ]
    }
    responses.add(responses.GET, GEOCODE, json=body, status=200)
    place = ors_geocode("Chicago", "k", BASE, 5)
    assert place.label == "Chicago, IL" and place.lat == 41.9 and place.lng == -87.6


@responses.activate
def test_geocode_no_results_raises_location_not_found():
    responses.add(responses.GET, GEOCODE, json={"features": []}, status=200)
    with pytest.raises(LocationNotFound):
        ors_geocode("nowhere-xyz", "k", BASE, 5)


@responses.activate
def test_geocode_http_error_raises_upstream():
    responses.add(responses.GET, GEOCODE, json={}, status=503)
    with pytest.raises(UpstreamServiceError):
        ors_geocode("x", "k", BASE, 5)


@responses.activate
def test_geocode_network_error_raises_upstream():
    responses.add(responses.GET, GEOCODE, body=requests.ConnectionError("boom"))
    with pytest.raises(UpstreamServiceError):
        ors_geocode("x", "k", BASE, 5)


@responses.activate
def test_route_success_converts_meters_to_miles():
    body = {
        "features": [
            {
                "geometry": {"coordinates": [[0, 0], [1, 1]]},
                "properties": {
                    "segments": [{"distance": 1609.344}, {"distance": 3218.688}],
                    "summary": {"distance": 4828.032},
                },
            }
        ]
    }
    responses.add(responses.POST, ROUTE, json=body, status=200)
    result = ors_route([(0, 0), (1, 1), (2, 2)], "k", BASE, "driving-hgv", 5)
    assert result.leg_distances_miles == [1.0, 2.0]
    assert round(result.total_distance_miles, 1) == 3.0


@responses.activate
def test_route_http_error_raises_upstream():
    responses.add(responses.POST, ROUTE, json={}, status=500)
    with pytest.raises(UpstreamServiceError):
        ors_route([(0, 0), (1, 1)], "k", BASE, "driving-hgv", 5)


@responses.activate
def test_route_no_features_raises_upstream():
    responses.add(responses.POST, ROUTE, json={"features": []}, status=200)
    with pytest.raises(UpstreamServiceError):
        ors_route([(0, 0), (1, 1)], "k", BASE, "driving-hgv", 5)


@responses.activate
def test_route_malformed_feature_raises_upstream():
    # 200 OK but the feature is missing `summary` -> wrapped as UpstreamServiceError, not a 500.
    body = {"features": [{"geometry": {"coordinates": [[0, 0]]}, "properties": {"segments": []}}]}
    responses.add(responses.POST, ROUTE, json=body, status=200)
    with pytest.raises(UpstreamServiceError):
        ors_route([(0, 0), (1, 1)], "k", BASE, "driving-hgv", 5)


@responses.activate
def test_geocode_feature_without_coordinates_raises_not_found():
    body = {"features": [{"geometry": None, "properties": {"label": "x"}}]}
    responses.add(responses.GET, GEOCODE, json=body, status=200)
    with pytest.raises(LocationNotFound):
        ors_geocode("x", "k", BASE, 5)


@responses.activate
def test_route_network_error_raises_upstream():
    responses.add(responses.POST, ROUTE, body=requests.ConnectionError("boom"))
    with pytest.raises(UpstreamServiceError):
        ors_route([(0, 0), (1, 1)], "k", BASE, "driving-hgv", 5)
