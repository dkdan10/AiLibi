"""Endpoint tests for the eval cost-summary route (DESIGN.md §11.4)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.replay_loader import ReplayLoader, get_replay_loader
from tests.api.fixtures.sample_replay import write_meeting_replay, write_sample_replay


def _client(replay_dir: Path) -> TestClient:
    test_app = create_app()
    loader = ReplayLoader(replay_dir=replay_dir)
    test_app.dependency_overrides[get_replay_loader] = lambda: loader
    return TestClient(test_app)


@pytest.fixture
def populated_client(tmp_path: Path) -> Iterator[TestClient]:
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    write_meeting_replay(tmp_path / "replay-seed-1.jsonl", seed=1)
    with _client(tmp_path) as client:
        yield client


def test_cost_summary_aggregates(populated_client: TestClient) -> None:
    response = populated_client.get("/eval/cost-summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_replays"] == 2
    assert body["total_cost_usd"] == pytest.approx(0.03)
    assert body["max_cost_per_replay"] == pytest.approx(0.03)
    assert body["mean_cost_per_replay"] == pytest.approx(0.015)
    assert body["decisive_split"] == {"CREWMATES": 1.0, "IMPOSTORS": 0.0}


def test_cost_summary_empty_dir_returns_zeros(tmp_path: Path) -> None:
    with _client(tmp_path / "empty") as client:
        response = client.get("/eval/cost-summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_replays"] == 0
    assert body["total_cost_usd"] == 0.0
    assert body["mean_cost_per_replay"] == 0.0
    assert body["max_cost_per_replay"] == 0.0
    assert body["decisive_split"] == {}
