"""Public outcomes are reconstructed; editorial prose binds to exact recordings."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import api.public_results as public
from api.main import ENV_REPLAY_DIR, create_app
from api.replay_loader import ReplayLoader
from api.schemas import AgentMemoryView, PublicResultsView, ReplayView
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


@pytest.fixture
def summary_recording(completed_recording: Path, tmp_path: Path) -> Path:
    destination = tmp_path / completed_recording.name
    shutil.copyfile(completed_recording, destination)
    roster = completed_recording.parent / "roster.json"
    if roster.exists():
        shutil.copyfile(roster, tmp_path / roster.name)
    return destination


def test_public_summary_reuses_walks_and_clear_cache_revalidates() -> None:
    # The real set exceeds the loader's sixteen-entry playback cache.
    loader = ReplayLoader(SAMPLES / "9p2i")
    with patch.object(loader, "_walk", wraps=loader._walk) as walk:
        first = public.build_public_results(loader)
        initial_walks = walk.call_count
        assert initial_walks > 0
        assert public.build_public_results(loader) == first
        assert walk.call_count == initial_walks
        loader.clear_cache()
        assert public.build_public_results(loader) == first
        assert walk.call_count > initial_walks


def test_warm_summary_refuses_same_mtime_corruption_and_recovers(
    summary_recording: Path,
) -> None:
    completed_recording = summary_recording
    loader = ReplayLoader(completed_recording.parent)
    first = public.build_public_results(loader)
    original = completed_recording.read_bytes()
    stamp = completed_recording.stat()
    rows = [json.loads(line) for line in original.splitlines()]
    rows[-1]["winner"] = (
        "IMPOSTORS" if rows[-1]["winner"] == "CREWMATES" else "CREWMATES"
    )
    completed_recording.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    os.utime(completed_recording, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    with pytest.raises(ValueError, match="invalid or unverified"):
        public.build_public_results(loader)
    completed_recording.write_bytes(original)
    os.utime(completed_recording, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    assert public.build_public_results(loader) == first


def test_warm_summary_refreshes_manifest_provenance(summary_recording: Path) -> None:
    completed_recording = summary_recording
    loader = ReplayLoader(completed_recording.parent)
    first = public.build_public_results(loader)
    manifest = completed_recording.parent / "MANIFEST.md"
    seed = int(completed_recording.stem.removeprefix("replay-seed-"))
    manifest.write_text(
        f"| seed | refreshed_at |\n| --- | --- |\n| {seed} | 2026-09-06 |\n"
    )
    refreshed = public.build_public_results(loader)
    assert refreshed.source_fingerprint != first.source_fingerprint
    assert refreshed.recorded_from == refreshed.recorded_until == "2026-09-06"
    assert refreshed.games == first.games


def test_warm_summary_rechecks_ambient_substrate(
    summary_recording: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    loader = ReplayLoader(summary_recording.parent)
    public.build_public_results(loader)
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1")
    with pytest.raises(ValueError, match="invalid or unverified"):
        public.build_public_results(loader)


def test_warm_summary_rechecks_same_mtime_roster(summary_recording: Path) -> None:
    roster = summary_recording.parent / "roster.json"
    roster.write_text(
        json.dumps({"num_players": 7, "num_impostors": 1, "tasks_per_crewmate": 1})
    )
    loader = ReplayLoader(summary_recording.parent)
    public.build_public_results(loader)
    stamp = roster.stat()
    roster.write_text(
        json.dumps({"num_players": 7, "num_impostors": 2, "tasks_per_crewmate": 1})
    )
    os.utime(roster, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    with pytest.raises(ValueError, match="invalid or unverified"):
        public.build_public_results(loader)


@pytest.mark.parametrize("changed", ["source", "substrate"])
def test_generation_drift_is_refused_and_not_cached(
    summary_recording: Path, monkeypatch: pytest.MonkeyPatch, changed: str
) -> None:
    loader = ReplayLoader(summary_recording.parent)
    original = loader.load_replay
    altered = False

    def load(game_id: str, *, include_llm_bodies: bool = True) -> ReplayView:
        nonlocal altered
        result = original(game_id, include_llm_bodies=include_llm_bodies)
        if not altered:
            altered = True
            if changed == "source":
                with summary_recording.open("ab") as stream:
                    stream.write(b"\n")
            else:
                monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1")
        return result

    monkeypatch.setattr(loader, "load_replay", load)
    with pytest.raises(ValueError, match="changed during public-results"):
        public.build_public_results(loader)
    assert loader._public_results_cache is None


def test_public_results_cache_is_scoped_to_its_loader(summary_recording: Path) -> None:
    first_loader = ReplayLoader(summary_recording.parent)
    first = public.build_public_results(first_loader)
    second_loader = ReplayLoader(summary_recording.parent)
    with patch.object(second_loader, "_walk", wraps=second_loader._walk) as walk:
        assert public.build_public_results(second_loader) == first
        assert walk.call_count > 0
