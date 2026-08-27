from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.main import HealthResponse, app, create_app, health
from api.replay_loader import ReplayLoader, get_replay_loader
from orchestrator.replay import (
    fsm_default_tactical_policy_stamp,
    substrate_flag_snapshot,
)

_COMMITTED_9P2I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)
#: A stamp naming a lever this build's registry does not have — the shape a
#: recording made by a NEWER build carries. Nothing here can reproduce it.
_UNKNOWN_LEVER_STAMP = {
    **substrate_flag_snapshot(env={}),
    "a_lever_from_the_future": True,
}


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


# -- the provenance refusals reach HTTP as the 500 their docstrings promise ----
#
# All three replay-provenance errors promise "HTTP 500 with the offending game id
# in the response body". Only the state one had a handler, so the substrate
# error's carefully-built remediation text was constructed and discarded, leaving
# a bare `Internal Server Error` in a text/plain body.


def _delete_ailibi_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip every ``AILIBI_*`` var so the served substrate is the bare slate."""

    for var in list(os.environ):
        if var.startswith("AILIBI_"):
            monkeypatch.delenv(var, raising=False)


def _mixed_substrate_set(tmp_path: Path, *, seed: int) -> Path:
    """The WHOLE committed 9p2i set with ONE game_over restamped off-substrate.

    The whole set, not one file: a directory holding a single replay fails its
    own tick-0 state hash, so a one-file fixture would 500 for an unrelated
    reason and prove nothing about the substrate path.
    """

    set_dir = tmp_path / "samples" / "9p2i"
    shutil.copytree(_COMMITTED_9P2I_DIR, set_dir)
    path = set_dir / f"replay-seed-{seed}.jsonl"
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("kind") == "game_over":
            record["substrate_flags"] = dict(_UNKNOWN_LEVER_STAMP)
            line = json.dumps(record, sort_keys=True, separators=(",", ":"))
        out.append(line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return set_dir


def test_substrate_mismatch_serves_a_500_naming_the_game_and_the_divergence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _delete_ailibi_env(monkeypatch)
    set_dir = _mixed_substrate_set(tmp_path, seed=0)
    test_app = create_app(replay_dir=set_dir.parent)
    test_app.dependency_overrides[get_replay_loader] = lambda: ReplayLoader(
        replay_dir=set_dir
    )

    with TestClient(test_app, raise_server_exceptions=False) as client:
        response = client.get("/replays/headless-seed-0")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["game_id"] == "headless-seed-0"
    assert body["unknown_levers"] == ["a_lever_from_the_future"]
    assert body["differing_levers"] == []
    assert "a_lever_from_the_future" in body["detail"]


def test_policy_mismatch_serves_a_500_naming_the_game_and_the_divergence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # This error is unreachable from HTTP on a normally-served set:
    # ``SetLoaderRegistry._build_loader`` constructs every served loader bare, so
    # ``expected_tactical_policy`` is never set by the serving path. The claim is
    # made by a caller, so the test makes one — via the same dependency override
    # the loader tests use — rather than pretending the guard is live.
    _delete_ailibi_env(monkeypatch)
    set_dir = tmp_path / "samples" / "9p2i"
    shutil.copytree(_COMMITTED_9P2I_DIR, set_dir)
    learned_claim = fsm_default_tactical_policy_stamp().model_copy(
        update={"policy_id": "learned-mover-v1"}
    )
    test_app = create_app(replay_dir=set_dir.parent)
    test_app.dependency_overrides[get_replay_loader] = lambda: ReplayLoader(
        replay_dir=set_dir, expected_tactical_policy=learned_claim
    )

    with TestClient(test_app, raise_server_exceptions=False) as client:
        response = client.get("/replays/headless-seed-0")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["game_id"] == "headless-seed-0"
    assert body["differing_fields"] == ["policy_id"]
    assert "learned-mover-v1" in body["detail"]


def test_every_replay_mismatch_error_has_a_registered_handler() -> None:
    # The defect was a promise without a registration. The table IS the promise
    # now, so pin that the app registers every entry — a fourth error added to
    # the table without a registration, or a registration dropped, fails here.
    # (The state entry's own 500-with-tick body is pinned end to end by
    # tests/api/test_replays.py::test_get_replay_state_mismatch_returns_500.)
    from api.main import _REPLAY_MISMATCH_HANDLERS  # noqa: PLC2701

    registered = set(create_app().exception_handlers)

    assert {error_type for error_type, _ in _REPLAY_MISMATCH_HANDLERS} <= registered
