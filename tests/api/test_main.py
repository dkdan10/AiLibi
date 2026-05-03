from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from api.main import HealthResponse, app, health


def test_app_imports_and_registers_health_route() -> None:
    assert isinstance(app, FastAPI)
    route_paths = {getattr(route, "path", None) for route in app.routes}
    assert "/health" in route_paths
    assert health() == HealthResponse(status="ok", service="ailibi-api")


def test_docker_compose_declares_api_service() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "api:" in compose
    assert "uv" in compose
    assert "uvicorn" in compose
    assert "api.main:app" in compose
    assert "${AILIBI_API_PORT:-8000}:8000" in compose
