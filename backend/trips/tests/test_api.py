"""Integration tests for the API view with OpenRouteService mocked (offline)."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

import pytest
import responses
from rest_framework.test import APIClient

BASE = "https://api.openrouteservice.org"
GEOCODE_URL = f"{BASE}/geocode/search"
ROUTE_URL = f"{BASE}/v2/directions/driving-hgv/geojson"

_COORDS = {"chicago": [-87.63, 41.88], "dallas": [-96.80, 32.78], "angeles": [-118.24, 34.05]}


def _geocode_callback(request):
    text = parse_qs(urlparse(request.url).query)["text"][0].lower()
    lng, lat = next((v for k, v in _COORDS.items() if k in text), [-90.0, 40.0])
    body = {
        "features": [
            {"geometry": {"coordinates": [lng, lat]}, "properties": {"label": text.title()}}
        ]
    }
    return (200, {}, json.dumps(body))


def _route_body(leg1_m=1126540.8, leg2_m=1287475.2):  # 700 mi + 800 mi
    return {
        "features": [
            {
                "geometry": {"coordinates": [[-87.6, 41.9], [-96.8, 32.8], [-118.2, 34.0]]},
                "properties": {
                    "segments": [
                        {"distance": leg1_m, "duration": 1},
                        {"distance": leg2_m, "duration": 1},
                    ],
                    "summary": {"distance": leg1_m + leg2_m, "duration": 2},
                },
            }
        ]
    }


def _mock_ors(route_status=200):
    responses.add_callback(
        responses.GET, GEOCODE_URL, callback=_geocode_callback, content_type="application/json"
    )
    responses.add(responses.POST, ROUTE_URL, json=_route_body(), status=route_status)


VALID_PAYLOAD = {
    "current_location": "Chicago, IL",
    "pickup_location": "Dallas, TX",
    "dropoff_location": "Los Angeles, CA",
    "current_cycle_used": 0,
}


@pytest.fixture(autouse=True)
def _reset_throttle():
    # AnonRateThrottle counts live in the cache; reset between tests for isolation.
    from django.core.cache import cache

    cache.clear()
    yield


@pytest.fixture
def api(settings):
    settings.ORS_API_KEY = "test-key"
    settings.MAP_PROVIDER = "openrouteservice"
    return APIClient()


def test_health(api):
    resp = api.get("/api/health/")
    assert resp.status_code == 200 and resp.json() == {"status": "ok"}


@responses.activate
def test_plan_trip_happy_path(api):
    _mock_ors()
    resp = api.post("/api/plan-trip/", VALID_PAYLOAD, format="json")
    assert resp.status_code == 200
    data = resp.json()
    assert set(data) == {"inputs", "geocoded", "route", "summary", "stops", "days"}
    assert data["summary"]["total_distance_miles"] == 1500.0
    assert data["summary"]["num_fuel_stops"] == 1
    assert data["days"], "expected at least one daily log"
    for day in data["days"]:
        assert abs(sum(day["totals"].values()) - 24.0) < 0.05


@responses.activate
def test_invalid_input_returns_400(api):
    _mock_ors()
    resp = api.post("/api/plan-trip/", {"current_location": "Chicago"}, format="json")
    assert resp.status_code == 400
    assert "pickup_location" in resp.json()


@responses.activate
def test_cycle_out_of_range_returns_400(api):
    _mock_ors()
    payload = {**VALID_PAYLOAD, "current_cycle_used": 80}
    resp = api.post("/api/plan-trip/", payload, format="json")
    assert resp.status_code == 400


@responses.activate
def test_nan_cycle_returns_400_not_500(api):
    _mock_ors()
    payload = {**VALID_PAYLOAD, "current_cycle_used": "nan"}
    resp = api.post("/api/plan-trip/", payload, format="json")
    assert resp.status_code == 400


@responses.activate
def test_unknown_location_returns_400(api):
    responses.add(responses.GET, GEOCODE_URL, json={"features": []}, status=200)
    resp = api.post("/api/plan-trip/", VALID_PAYLOAD, format="json")
    assert resp.status_code == 400
    assert "error" in resp.json()


@responses.activate
def test_upstream_failure_returns_502(api):
    _mock_ors(route_status=500)
    resp = api.post("/api/plan-trip/", VALID_PAYLOAD, format="json")
    assert resp.status_code == 502
    assert "error" in resp.json()


@responses.activate
def test_router_returning_too_many_legs_is_502(api):
    responses.add_callback(
        responses.GET, GEOCODE_URL, callback=_geocode_callback, content_type="application/json"
    )
    body = {
        "features": [
            {
                "geometry": {"coordinates": [[0, 0], [1, 1]]},
                "properties": {
                    "segments": [{"distance": 1000}, {"distance": 1000}, {"distance": 1000}],
                    "summary": {"distance": 3000},
                },
            }
        ]
    }
    responses.add(responses.POST, ROUTE_URL, json=body, status=200)
    resp = api.post("/api/plan-trip/", VALID_PAYLOAD, format="json")
    assert resp.status_code == 502


def test_missing_api_key_returns_502(api, settings):
    settings.ORS_API_KEY = ""
    resp = api.post("/api/plan-trip/", VALID_PAYLOAD, format="json")
    assert resp.status_code == 502
