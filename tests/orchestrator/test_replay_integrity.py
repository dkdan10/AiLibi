"""Reject altered chronology and outcomes in otherwise genuine recordings."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pytest
from pydantic import BaseModel

from agents.base import AgentInterface
from api.replay_loader import ReplayLoader
from engine.entities import PlayerId
from engine.world import WorldState, load_canonical_map
from eval.balance_eval import load_tournament_report
from llm.client import CallKind, LLMResponse
from llm.fake_provider import FakeProvider
from meetings.manager import MeetingTrigger
from meetings.schemas import MeetingResult, MeetingTranscript, VoteBallot
from orchestrator.game import (
    HeadlessGame,
    MeetingArtifacts,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import GameEndReplayEntry, MeetingReplayEntry, read_all_entries
from orchestrator.replay_integrity import ReplayIntegrityError
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

if TYPE_CHECKING:
    from _verify_samples import VerifyFailure


@pytest.fixture
def sample_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[Path], list[VerifyFailure]]:
    # Script modules use top-level names, matching mypy_path and scripts tests.
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    from _verify_samples import verify_samples

    return verify_samples


Mutation = Literal[
    "tick_label",
    "terminal_winner",
    "terminal_reason",
    "terminal_tick",
    "premature_terminal",
    "reordered_meetings",
    "orphan_meeting",
    "duplicate_meeting",
    "mixed_game_ids",
    "post_terminal_tick",
    "reticked_meeting",
    "missing_meeting",
    "meeting_pre_hash",
    "meeting_reporter",
]


def _game(
    path: Path, *, max_ticks: int = 200, fail_meeting: bool = False
) -> HeadlessGame:
    provider = _FailingProvider() if fail_meeting else FakeProvider()
    return HeadlessGame(
        seed=1,
        num_players=7,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=max_ticks),
        meeting_runner=build_default_meeting_runner(llm_client=provider),
    )


class _FailingProvider:
    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        raise RuntimeError("injected provider failure")


class _EjectImpostorRunner:
    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        target = next(
            pid
            for pid, player in state.players.items()
            if player.alive and player.role == "IMPOSTOR"
        )
        return MeetingArtifacts(
            result=MeetingResult(
                meeting_id=meeting_id,
                triggered_by=trigger.triggered_by,
                trigger_tick=trigger.trigger_tick,
                outcome="EJECTED",
                ejected_player_id=target,
                ballots=tuple(
                    VoteBallot(
                        voter=pid,
                        target=target if pid != target else "SKIP",
                        confidence=1.0,
                        primary_reason_id=None,
                        considered_alternatives=(),
                        rationale_text="scripted terminal vote",
                    )
                    for pid, player in state.players.items()
                    if player.alive
                ),
                transcript=MeetingTranscript(),
            ),
            llm_calls=(),
            prompt_versions={},
        )


@pytest.fixture(scope="module")
def completed_recording(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("integrity-source") / "replay-seed-1.jsonl"
    result = _game(path).run()
    assert result.final_state.phase == "GAME_OVER"
    assert result.outcome == "CREWMATES"
    entries = read_all_entries(path)
    assert sum(isinstance(entry, MeetingReplayEntry) for entry in entries) == 2
    assert isinstance(entries[-1], GameEndReplayEntry)
    return path


@pytest.fixture(scope="module")
def ejection_recording(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("integrity-ejection") / "replay-seed-1.jsonl"
    result = HeadlessGame(
        seed=1,
        num_players=7,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=200),
        meeting_runner=_EjectImpostorRunner(),
    ).run()
    assert result.final_state.phase == "GAME_OVER"
    assert result.outcome == "CREWMATES"
    terminal = read_all_entries(path)[-1]
    assert isinstance(terminal, GameEndReplayEntry)
    assert terminal.reason == "CREWMATE_EJECT"
    return path


def _rows(source: Path) -> list[dict[str, object]]:
    return [entry.model_dump(mode="json") for entry in read_all_entries(source)]


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _alter(source: Path, path: Path, mutation: Mutation) -> None:
    rows = _rows(source)
    meetings = [index for index, row in enumerate(rows) if row["kind"] == "meeting"]
    first, second = meetings
    if mutation == "tick_label":
        rows[0]["tick"] = 9999
    elif mutation == "terminal_winner":
        rows[-1]["winner"] = "IMPOSTORS"
    elif mutation == "terminal_reason":
        rows[-1]["reason"] = "IMPOSTOR_PARITY"
    elif mutation == "terminal_tick":
        rows[-1]["tick"] = 9999
    elif mutation == "premature_terminal":
        terminal = rows[-1]
        terminal["tick"] = 5
        rows = [*rows[:5], terminal]
    elif mutation == "reordered_meetings":
        rows[first], rows[second] = rows[second], rows[first]
    elif mutation == "orphan_meeting":
        orphan = dict(rows[first])
        orphan.update(tick=1, meeting_id="orphan")
        rows.insert(2, orphan)
    elif mutation == "duplicate_meeting":
        rows.insert(first + 1, dict(rows[first]))
    elif mutation == "mixed_game_ids":
        rows[2]["game_id"] = "another-game"
    elif mutation == "post_terminal_tick":
        extra = dict(rows[0])
        extra["tick"] = 9999
        rows.append(extra)
    elif mutation == "reticked_meeting":
        rows[first]["tick"] = 9
    elif mutation == "missing_meeting":
        rows.pop(first)
    elif mutation == "meeting_pre_hash":
        rows[first]["state_hash_before"] = "0" * 64
    elif mutation == "meeting_reporter":
        rows[first]["triggered_by"] = "another-reporter"
    else:
        raise AssertionError(f"unhandled mutation: {mutation}")
    _write(path, rows)


def test_genuine_completed_recording_reconstructs(
    completed_recording: Path, sample_verifier: Callable[[Path], list[VerifyFailure]]
) -> None:
    replay = ReplayLoader(completed_recording.parent).load_replay("headless-seed-1")
    assert replay.metadata.winner == "CREWMATES"
    assert replay.metadata.winner_reason == "CREWMATE_TASKS"
    assert len(replay.meetings) == 2
    assert sample_verifier(completed_recording.parent) == []


def test_forged_ballot_targets_cannot_keep_a_verified_ejection(
    ejection_recording: Path, tmp_path: Path
) -> None:
    rows = _rows(ejection_recording)
    original_hashes = tuple(
        (
            row.get("state_hash"),
            row.get("state_hash_before"),
            row.get("state_hash_after"),
        )
        for row in rows
    )
    meeting = next(row for row in rows if row["kind"] == "meeting")
    assert meeting["outcome"] == "EJECTED"
    ballots = meeting["ballots"]
    assert isinstance(ballots, list)
    for ballot in ballots:
        ballot["target"] = "SKIP"
    assert (
        tuple(
            (
                row.get("state_hash"),
                row.get("state_hash_before"),
                row.get("state_hash_after"),
            )
            for row in rows
        )
        == original_hashes
    )
    _write(tmp_path / ejection_recording.name, rows)
    with pytest.raises(ReplayIntegrityError, match="ballot_tally_mismatch"):
        ReplayLoader(tmp_path).load_replay("headless-seed-1")
    state = seed_initial_state(
        seed=1, game_map=load_canonical_map(), num_players=7, tasks_per_crewmate=1
    )
    with pytest.raises(ReplayIntegrityError, match="ballot_tally_mismatch"):
        load_tournament_report(
            tmp_path,
            roles_by_seed={
                1: {pid: player.role for pid, player in state.players.items()}
            },
        )


def test_legacy_terminal_without_optional_tick_remains_valid(
    completed_recording: Path, tmp_path: Path
) -> None:
    rows = _rows(completed_recording)
    del rows[-1]["tick"]
    _write(tmp_path / completed_recording.name, rows)
    replay = ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert replay.metadata.winner == "CREWMATES"


def test_meeting_ids_are_opaque_when_references_are_consistent(
    completed_recording: Path, tmp_path: Path
) -> None:
    rows = _rows(completed_recording)
    first = next(row for row in rows if row["kind"] == "meeting")
    old_id = first["meeting_id"]
    for row in rows:
        if row.get("meeting_id") == old_id:
            row["meeting_id"] = "external-meeting-key"
    _write(tmp_path / completed_recording.name, rows)
    replay = ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert replay.meetings[0].meeting_id == "external-meeting-key"


@pytest.mark.parametrize("fail_meeting", [False, True])
def test_genuine_unfinished_and_aborted_recordings_remain_valid(
    tmp_path: Path, fail_meeting: bool
) -> None:
    path = tmp_path / "replay-seed-1.jsonl"
    game = _game(path, max_ticks=200 if fail_meeting else 5, fail_meeting=fail_meeting)
    if fail_meeting:
        with pytest.raises(RuntimeError, match="injected provider failure"):
            game.run()
        assert any(entry.kind == "meeting_aborted" for entry in read_all_entries(path))
    else:
        assert game.run().outcome == "TICK_BUDGET_REACHED"
    replay = ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert replay.metadata.winner is None
    assert replay.metadata.total_ticks > 0
    assert not replay.meetings


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("tick_label", "tick_label_mismatch"),
        ("terminal_winner", "recorded_outcome_mismatch"),
        ("terminal_reason", "recorded_outcome_mismatch"),
        ("terminal_tick", "terminal_tick_mismatch"),
        ("premature_terminal", "recorded_outcome_mismatch"),
        ("reordered_meetings", "row_order"),
        ("orphan_meeting", "meeting_trigger_mismatch"),
        ("duplicate_meeting", "row_order"),
        ("mixed_game_ids", "row_order"),
        ("post_terminal_tick", "row_order"),
        ("reticked_meeting", "row_order"),
        ("missing_meeting", "row_order"),
        ("meeting_pre_hash", "meeting_pre_hash_mismatch"),
        ("meeting_reporter", "meeting_trigger_mismatch"),
    ],
)
def test_corrupted_recording_is_rejected(
    completed_recording: Path, tmp_path: Path, mutation: Mutation, expected_code: str
) -> None:
    _alter(completed_recording, tmp_path / completed_recording.name, mutation)
    with pytest.raises(ReplayIntegrityError) as excinfo:
        ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert excinfo.value.code == expected_code


def test_genuine_meeting_ejection_win_reconstructs(
    ejection_recording: Path, sample_verifier: Callable[[Path], list[VerifyFailure]]
) -> None:
    replay = ReplayLoader(ejection_recording.parent).load_replay("headless-seed-1")
    assert replay.metadata.winner == "CREWMATES"
    assert replay.metadata.winner_reason == "CREWMATE_EJECT"
    assert replay.meetings[-1].outcome == "EJECTED"
    assert sample_verifier(ejection_recording.parent) == []


@pytest.mark.parametrize(
    ("field", "value", "expected_code"),
    [
        ("winner", "IMPOSTORS", "recorded_outcome_mismatch"),
        ("reason", "CREWMATE_TASKS", "recorded_outcome_mismatch"),
        ("tick", 9999, "terminal_tick_mismatch"),
    ],
)
def test_meeting_ejection_terminal_metadata_is_verified(
    ejection_recording: Path,
    tmp_path: Path,
    field: str,
    value: str | int,
    expected_code: str,
) -> None:
    rows = _rows(ejection_recording)
    rows[-1][field] = value
    _write(tmp_path / ejection_recording.name, rows)
    with pytest.raises(ReplayIntegrityError) as excinfo:
        ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert excinfo.value.code == expected_code


@pytest.mark.parametrize("mutation", ["tick_label", "terminal_winner"])
def test_sample_verifier_rejects_corruption_that_keeps_all_state_hashes(
    completed_recording: Path,
    tmp_path: Path,
    mutation: Mutation,
    sample_verifier: Callable[[Path], list[VerifyFailure]],
) -> None:
    _alter(completed_recording, tmp_path / completed_recording.name, mutation)
    failures = sample_verifier(tmp_path)
    assert len(failures) == 1
    assert failures[0].game_id == "headless-seed-1"
