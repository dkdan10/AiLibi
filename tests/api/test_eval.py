"""Endpoint tests for the eval routes (DESIGN.md §11.3, §11.4).

Covers ``/eval/cost-summary`` (Task 4.x) and ``/eval/tournament-report``
(Task 5.7): the latter serves the latest ``tournament-eval-report.json`` from
the configured eval dir (200), or 404 when none exists. The report fixture is
assembled exactly as the real artifact is — via
:func:`eval.meeting_quality.build_tournament_eval_report` over a hand-built
:class:`~eval.report_schema.TournamentReport` — so the test exercises the real
schema rather than a parallel hand-written JSON blob.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.replay_loader import ReplayLoader, get_replay_loader
from eval.meeting_quality import TournamentEvalReport, build_tournament_eval_report
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    TournamentReport,
)
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


# ---------------------------------------------------------------------------
# /eval/tournament-report (Task 5.7, DESIGN.md §11.3)
# ---------------------------------------------------------------------------


def _sample_eval_report() -> TournamentEvalReport:
    """A minimal-but-valid TournamentEvalReport for endpoint tests.

    Two no-meeting games (one crew win, one impostor win — the latter with a
    ``None`` final_tick to cover the partial/non-decisive shape) carrying
    distinct per-game cost, so the served body exercises the balance summary
    and the cost dashboard. The four metric blocks fall out of
    :func:`build_tournament_eval_report` (the empty case for no-meeting games),
    exactly as the production artifact is assembled.
    """

    games = (
        GameReport(
            game_id="headless-seed-0",
            seed=0,
            winner="CREWMATES",
            reason="CREWMATE_TASKS",
            final_tick=42,
            roles={"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
            replay_ref="replay-seed-0.jsonl",
            meetings=(),
            failed_calls=(),
            prompt_versions={"meeting": "v1"},
            cost=GameCostSummary(
                total_cost_usd=0.10,
                total_input_tokens=100,
                total_output_tokens=20,
                by_model={"claude-sonnet": 0.10},
            ),
        ),
        GameReport(
            game_id="headless-seed-1",
            seed=1,
            winner="IMPOSTORS",
            reason="IMPOSTOR_PARITY",
            final_tick=None,
            roles={"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
            replay_ref="replay-seed-1.jsonl",
            meetings=(),
            failed_calls=(),
            prompt_versions={"meeting": "v1"},
            cost=GameCostSummary(
                total_cost_usd=0.05,
                total_input_tokens=50,
                total_output_tokens=10,
                by_model={"claude-haiku": 0.05},
            ),
        ),
    )
    return build_tournament_eval_report(
        TournamentReport(
            format_version=CURRENT_FORMAT_VERSION, games=games, seeds_used=(0, 1)
        )
    )


def test_tournament_report_present_returns_200(tmp_path: Path) -> None:
    eval_report = _sample_eval_report()
    (tmp_path / "tournament-eval-report.json").write_text(
        eval_report.model_dump_json(), encoding="utf-8"
    )

    with _client(tmp_path) as client:
        response = client.get("/eval/tournament-report")

    assert response.status_code == 200
    body = response.json()
    # Served faithfully: the body round-trips back into an equal model.
    assert TournamentEvalReport.model_validate(body) == eval_report
    # Balance summary inputs: per-game winners, including the IMPOSTORS win.
    assert [g["winner"] for g in body["report"]["games"]] == [
        "CREWMATES",
        "IMPOSTORS",
    ]
    # Cost dashboard: each game's spend counted once → 0.10 + 0.05.
    assert body["cost_dashboard"]["total_cost_usd"] == pytest.approx(0.15)
    # A nullable metric field is served as JSON null, never 0 / NaN (the
    # no-impostor-ejection case), so the dashboard can render "n/a".
    assert body["vote_correctness"]["vote_correctness_rate"] is None


def test_tournament_report_absent_returns_404(tmp_path: Path) -> None:
    with _client(tmp_path / "empty") as client:
        response = client.get("/eval/tournament-report")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Committed 4p/1i report loads against the current model (Task 7.11)
# ---------------------------------------------------------------------------
#
# The eval model is frozen/``extra="forbid"``, so a committed report missing a
# now-required field would 500 at ``GET /eval/tournament-report`` at runtime
# while the tmp_path route tests above stay green (the runtime break 7.3
# documented). These two tests load the REAL committed 4p/1i report through the
# runtime paths — the loader and the HTTP route — so a stale committed report
# fails the suite here instead of only in production.

_COMMITTED_SAMPLES_DIR = Path(__file__).resolve().parents[2] / "replays" / "samples"


def test_committed_4p1i_report_validates_against_current_model() -> None:
    report = ReplayLoader(replay_dir=_COMMITTED_SAMPLES_DIR).tournament_report()
    assert isinstance(report, TournamentEvalReport)
    # The regenerated committed report carries every Task 7.11 field.
    # ejection_accuracy is None iff the set has no ejections (the field's own
    # validator). The Task 10.17 Wave-2 re-record keeps the flat 4p/1i set
    # ejecting and every ejection correct (the 9.11 Wave-1 set had a single
    # impostor ejection): the committed ground truth is now four ejections,
    # all impostors (accuracy 1.0; small-n flag set below).
    assert report.vote_correctness.total_ejections == 4
    assert report.vote_correctness.ejection_accuracy == 1.0
    assert report.vote_correctness.impostor_ejections == 4
    assert report.vote_correctness.crewmate_ejections == 0
    assert report.vote_correctness.vote_correctness_rate == pytest.approx(0.75)
    assert report.vote_correctness.vote_correctness_small_n is True
    assert report.vote_correctness.contradictions_flagged_but_ignored == 2
    assert isinstance(report.accusation_calibration.vote_ballot_low_power, bool)
    assert (
        report.meeting_rate.skipped_meetings + report.meeting_rate.ejected_meetings
        == report.meeting_rate.meetings_total
    )


def test_committed_4p1i_report_serves_via_route() -> None:
    with _client(_COMMITTED_SAMPLES_DIR) as client:
        response = client.get("/eval/tournament-report")
    assert response.status_code == 200
    body = response.json()
    assert "ejection_accuracy" in body["vote_correctness"]
    assert "skipped_meetings" in body["meeting_rate"]
    assert "vote_ballot_low_power" in body["accusation_calibration"]
