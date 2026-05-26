"""Endpoint tests for the replay routes (DESIGN.md §7, §11.4).

Supersedes the body coverage that ``tests/api/test_routes.py`` (Task 4.1) held
when the handlers returned ``501``. Drives the populated routes through
FastAPI's ``TestClient`` with a :class:`ReplayLoader` pointed at a temp replay
dir (injected via ``dependency_overrides``), and keeps the route-registration /
OpenAPI smoke checks that remain valid after the bodies landed.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.main import app, create_app
from api.replay_loader import ReplayLoader, get_replay_loader
from tests.api.fixtures.sample_replay import (
    corrupt_tick_hash,
    write_meeting_replay,
    write_sample_replay,
)


@pytest.fixture
def replay_dir(tmp_path: Path) -> Path:
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0, ticks=3)
    write_meeting_replay(tmp_path / "replay-seed-1.jsonl", seed=1)
    return tmp_path


@pytest.fixture
def client(replay_dir: Path) -> Iterator[TestClient]:
    test_app = create_app()
    loader = ReplayLoader(replay_dir=replay_dir)
    test_app.dependency_overrides[get_replay_loader] = lambda: loader
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def empty_client(tmp_path: Path) -> Iterator[TestClient]:
    test_app = create_app()
    loader = ReplayLoader(replay_dir=tmp_path / "empty")
    test_app.dependency_overrides[get_replay_loader] = lambda: loader
    with TestClient(test_app) as test_client:
        yield test_client


# -- GET /replays --------------------------------------------------------


def test_list_replays_returns_metadata_sorted_by_seed(client: TestClient) -> None:
    response = client.get("/replays")
    assert response.status_code == 200
    body = response.json()
    assert [item["seed"] for item in body] == [0, 1]
    assert body[0]["game_id"] == "headless-seed-0"


def test_list_replays_empty_dir_returns_empty_list(empty_client: TestClient) -> None:
    response = empty_client.get("/replays")
    assert response.status_code == 200
    assert response.json() == []


# -- GET /replays/{game_id} ---------------------------------------------


def test_get_replay_returns_full_view(client: TestClient) -> None:
    response = client.get("/replays/headless-seed-1")
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["game_id"] == "headless-seed-1"
    assert len(body["ticks"]) == 3
    assert len(body["meetings"]) == 1


def test_get_replay_unknown_game_returns_404(client: TestClient) -> None:
    response = client.get("/replays/headless-seed-999")
    assert response.status_code == 404
    assert response.json()["detail"] == "replay not found: headless-seed-999"


def test_get_replay_state_mismatch_returns_500(tmp_path: Path) -> None:
    path = tmp_path / "replay-seed-0.jsonl"
    write_sample_replay(path, seed=0, ticks=3)
    corrupt_tick_hash(path, tick=2)

    test_app = create_app()
    loader = ReplayLoader(replay_dir=tmp_path)
    test_app.dependency_overrides[get_replay_loader] = lambda: loader
    with TestClient(test_app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/replays/headless-seed-0")

    assert response.status_code == 500
    body = response.json()
    assert body["tick"] == 2
    assert body["game_id"] == "headless-seed-0"
    assert "mismatch" in body["detail"]


# -- GET /replays/{game_id}/ticks/{tick} --------------------------------


def test_get_tick_returns_tick_view(client: TestClient) -> None:
    response = client.get("/replays/headless-seed-1/ticks/1")
    assert response.status_code == 200
    body = response.json()
    assert body["tick"] == 1
    assert any(event["type"] == "meeting_triggered" for event in body["events"])


def test_get_tick_out_of_range_returns_404(client: TestClient) -> None:
    assert client.get("/replays/headless-seed-1/ticks/99").status_code == 404


def test_get_tick_unknown_game_returns_404(client: TestClient) -> None:
    assert client.get("/replays/headless-seed-999/ticks/0").status_code == 404


# -- GET /replays/{game_id}/meetings/{meeting_id} -----------------------


def test_get_meeting_returns_meeting_view(client: TestClient) -> None:
    response = client.get("/replays/headless-seed-1/meetings/headless-seed-1:meeting-0")
    assert response.status_code == 200
    body = response.json()
    assert body["meeting_id"] == "headless-seed-1:meeting-0"
    assert body["trigger_kind"] == "body"
    assert body["outcome"] == "SKIPPED"


def test_get_meeting_unknown_returns_404(client: TestClient) -> None:
    response = client.get("/replays/headless-seed-1/meetings/nope")
    assert response.status_code == 404


# -- GET .../meetings/{meeting_id}/memory/{agent_id} --------------------


def test_get_meeting_memory_returns_view(client: TestClient) -> None:
    # seed 1 impostor is p-4; the reporter is the second crewmate.
    meeting = "headless-seed-1:meeting-0"
    response = client.get(f"/replays/headless-seed-1/meetings/{meeting}/memory/p-2")
    assert response.status_code == 200
    body = response.json()
    assert body["agent_id"] == "p-2"
    assert body["tick"] == 1
    assert body["rendered_memory_text"].startswith("## Your role:")


def test_get_meeting_memory_unknown_agent_returns_404(client: TestClient) -> None:
    meeting = "headless-seed-1:meeting-0"
    response = client.get(f"/replays/headless-seed-1/meetings/{meeting}/memory/p-999")
    assert response.status_code == 404


def test_get_meeting_memory_unknown_meeting_returns_404(client: TestClient) -> None:
    response = client.get("/replays/headless-seed-1/meetings/missing/memory/p-2")
    assert response.status_code == 404


def test_get_meeting_memory_unknown_game_returns_404(client: TestClient) -> None:
    response = client.get("/replays/headless-seed-999/meetings/m/memory/p-2")
    assert response.status_code == 404


# -- registration / OpenAPI smoke (migrated from Task 4.1 test_routes) ---

_EXPECTED_OPENAPI_SCHEMAS: tuple[str, ...] = (
    "ReplayMetadataView",
    "ReplayView",
    "TickView",
    "MeetingView",
    "AgentMemoryView",
    "EvalCostSummaryView",
)


def test_create_app_returns_fresh_instances() -> None:
    assert create_app() is not create_app()


def test_root_returns_service_info() -> None:
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "ailibi-api"}


def test_unknown_path_returns_404() -> None:
    with TestClient(app) as client:
        assert client.get("/does-not-exist").status_code == 404


def test_tick_path_param_is_typed_int(client: TestClient) -> None:
    # A non-integer tick fails path validation (422) before reaching the handler.
    assert client.get("/replays/headless-seed-1/ticks/not-an-int").status_code == 422


def test_openapi_lists_expected_dtos_and_paths() -> None:
    with TestClient(app) as client:
        spec: dict[str, Any] = client.get("/openapi.json").json()
    schemas = spec["components"]["schemas"]
    for name in _EXPECTED_OPENAPI_SCHEMAS:
        assert name in schemas, f"{name} missing from OpenAPI components"
    paths = spec["paths"]
    assert "/replays" in paths
    assert "/replays/{game_id}" in paths
    assert "/replays/{game_id}/ticks/{tick}" in paths
    assert "/replays/{game_id}/meetings/{meeting_id}" in paths
    assert "/replays/{game_id}/meetings/{meeting_id}/memory/{agent_id}" in paths
    assert "/eval/cost-summary" in paths
