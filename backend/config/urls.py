"""Root URL configuration. All endpoints live under ``/api/`` (see trips.urls)."""

from django.urls import include, path

urlpatterns = [
    path("api/", include("trips.urls")),
]
