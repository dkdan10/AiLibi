"""Route registration tests (DESIGN.md §7).

Task 4.1 only registers endpoints with ``501`` placeholder bodies, so these
tests assert each endpoint is *registered* (returns 501, not 404), the root
and unknown-path behavior, and that the OpenAPI schema reflects the documented
DTOs. Endpoint *bodies* are covered in 4.2.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.main import app, create_app

# Each registered GET endpoint, with sample path params filled in.
_ENDPOINTS: tuple[str, ...] = (
    "/replays",
    "/replays/headless-seed-0",
    "/replays/headless-seed-0/ticks/0",
    "/replays/headless-seed-0/meetings/m1",
    "/replays/headless-seed-0/meetings/m1/memory/p1",
    "/eval/cost-summary",
)

# DTOs that must surface in the generated OpenAPI components.
_EXPECTED_OPENAPI_SCHEMAS: tuple[str, ...] = (
    "ReplayMetadataView",
    "ReplayView",
    "TickView",
    "MeetingView",
    "AgentMemoryView",
    "EvalCostSummaryView",
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_create_app_returns_fresh_instances() -> None:
    first = create_app()
    second = create_app()
    assert first is not second


def test_root_returns_service_info(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "ailibi-api"}


@pytest.mark.parametrize("path", _ENDPOINTS)
def test_endpoint_is_registered_with_501(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 501, (
        f"{path} should be registered (501), not missing (got {response.status_code})"
    )
    assert response.json()["detail"] == "Not implemented in 4.1; lands in 4.2"


def test_unknown_path_returns_404(client: TestClient) -> None:
    assert client.get("/does-not-exist").status_code == 404


def test_tick_path_param_is_typed_int(client: TestClient) -> None:
    # A non-integer tick fails path validation (422) rather than reaching the
    # handler — confirms the {tick} converter is an int.
    assert client.get("/replays/headless-seed-0/ticks/not-an-int").status_code == 422


def test_openapi_schema_lists_expected_dtos(client: TestClient) -> None:
    spec: dict[str, Any] = client.get("/openapi.json").json()
    schemas = spec["components"]["schemas"]
    for name in _EXPECTED_OPENAPI_SCHEMAS:
        assert name in schemas, f"{name} missing from OpenAPI components"


def test_openapi_paths_cover_every_endpoint(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert "/replays" in paths
    assert "/replays/{game_id}" in paths
    assert "/replays/{game_id}/ticks/{tick}" in paths
    assert "/replays/{game_id}/meetings/{meeting_id}" in paths
    assert "/replays/{game_id}/meetings/{meeting_id}/memory/{agent_id}" in paths
    assert "/eval/cost-summary" in paths
