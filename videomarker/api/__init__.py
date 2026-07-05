"""VideoMarker REST API — FastAPI-based server for video processing."""

from videomarker.api.server import create_app, app

__all__ = ["create_app", "app", "get_settings"]

