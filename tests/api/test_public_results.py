"""Public outcomes are reconstructed; editorial prose binds to exact recordings."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import api.public_results as public
from api.main import ENV_REPLAY_DIR, create_app
from api.replay_loader import ReplayLoader
from api.schemas import AgentMemoryView, PublicResultsView
from tests.orchestrator.test_replay_integrity import (
    completed_recording as completed_recording,
)

SAMPLES = Path(__file__).resolve().parents[2] / "replays/samples"


@pytest.fixture(scope="module")
def canonical_summary() -> PublicResultsView:
    return public.build_public_results(ReplayLoader(SAMPLES / "9p2i"))


def test_current_summary_is_bounded_and_source_checked(
    canonical_summary: PublicResultsView,
) -> None:
    r = canonical_summary
    assert (r.games, r.completed, r.crew_wins, r.impostor_wins, r.task_wins) == (
        50,
        50,
        35,
        15,
        0,
    )
    assert (r.meetings, r.ejections, r.impostor_ejections, r.innocent_ejections) == (
        151,
        95,
        82,
        13,
    )
    assert (
        r.proof_backed_ejections,
        r.proof_backed_correct,
        r.proof_free_ejections,
        r.proof_free_correct,
    ) == (68, 68, 27, 14)
    assert [c.classification for c in r.cases] == [
        "supported",
        "unsupported",
        "unresolved",
    ]
    assert (r.recorded_from, r.recorded_until) == ("2026-08-30", "2026-08-30")
    assert r.source_url and "5006a32f" in r.source_url
    assert len(r.model_dump_json().encode()) < public.MAX_PUBLIC_RESULTS_BYTES
    assert r.reported_cost_usd == 0 and r.input_tokens > 0


@pytest.mark.parametrize("mutation", ["winner", "tick", "order"])
def test_corrupt_recording_cannot_publish_results(
    completed_recording: Path,
    tmp_path: Path,
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = [json.loads(line) for line in completed_recording.read_text().splitlines()]
    if mutation == "winner":
        rows[-1]["winner"] = "IMPOSTORS"
    elif mutation == "tick":
        rows[0]["tick"] = 9000
    else:
        rows[0], rows[1] = rows[1], rows[0]
    destination = tmp_path / completed_recording.name
    destination.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    with pytest.raises(ValueError):
        public.build_public_results(ReplayLoader(tmp_path))
    monkeypatch.setenv(ENV_REPLAY_DIR, str(tmp_path))
    with TestClient(create_app(), raise_server_exceptions=False) as client:
        assert client.get("/eval/summary").status_code >= 400


def test_analysis_override_never_certifies_public_results(
    completed_recording: Path,
) -> None:
    with pytest.raises(ValueError, match="strict substrate"):
        public.build_public_results(
            ReplayLoader(completed_recording.parent, allow_substrate_mismatch=True)
        )


def test_changed_source_suppresses_editorial_prose_and_pinned_set_url(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "9p2i"
    destination.mkdir()
    shutil.copyfile(SAMPLES / "9p2i/roster.json", destination / "roster.json")
    source = SAMPLES / "9p2i/replay-seed-23.jsonl"
    shutil.copyfile(source, destination / source.name)
    # Valid JSON/replay with a different byte identity cannot keep the old prose.
    with (destination / source.name).open("a") as stream:
        stream.write("\n")
    r = public.build_public_results(ReplayLoader(destination))
    assert r.games == r.completed == 1
    assert not r.cases and r.source_url is None
    assert r.recorded_from is None


def test_summary_budget_gate_bites(
    completed_recording: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(public, "MAX_PUBLIC_RESULTS_BYTES", 1)
    with pytest.raises(ValueError, match="50 KiB"):
        public.build_public_results(ReplayLoader(completed_recording.parent))


def test_partial_recording_retains_reported_spend_without_a_win(
    completed_recording: Path, tmp_path: Path
) -> None:
    rows = [json.loads(line) for line in completed_recording.read_text().splitlines()]
    end = next(
        i for i, row in enumerate(rows) if "llm_calls" in row and "ballots" in row
    )
    rows = rows[: end + 1]
    assert rows[-1]["llm_calls"]
    rows[-1]["llm_calls"][0]["cost_usd"] = 0.25
    destination = tmp_path / completed_recording.name
    destination.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    result = public.build_public_results(ReplayLoader(tmp_path))
    assert (result.games, result.completed, result.unfinished) == (1, 0, 1)
    assert result.crew_wins == result.impostor_wins == 0
    assert result.reported_cost_usd == 0.25


def test_a_changed_case_projection_cannot_keep_its_prose(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    loader = ReplayLoader(SAMPLES / "9p2i")
    original = loader.get_meeting_memory

    def altered(game_id: str, meeting_id: str, agent_id: str) -> AgentMemoryView:
        memory = original(game_id, meeting_id, agent_id)
        if (game_id, meeting_id, agent_id) == (
            "headless-seed-46",
            "headless-seed-46:meeting-3",
            "p-3",
        ):
            return memory.model_copy(update={"observation_references": ()})
        return memory

    monkeypatch.setattr(loader, "get_meeting_memory", altered)
    with pytest.raises(ValueError, match="Curated case"):
        public.build_public_results(loader)
