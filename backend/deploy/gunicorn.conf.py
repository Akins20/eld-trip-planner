"""Gunicorn configuration for the ELD Trip Planner API (managed by systemd)."""

import os

bind = os.getenv("GUNICORN_BIND", "unix:/run/eld-backend/gunicorn.sock")
workers = int(os.getenv("GUNICORN_WORKERS", "3"))
worker_class = "sync"
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
graceful_timeout = 30
keepalive = 5

# Log to stdout/stderr so journald captures everything.
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOGLEVEL", "info")
