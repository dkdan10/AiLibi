"""Bind failed-call identities to genuine meeting boundaries in the viewer."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pytest

from api.replay_loader import ReplayLoader
from api.schemas import MeetingTriggeredEventView
from engine.world import load_canonical_map
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    FailedCallReplayEntry,
    MeetingReplayEntry,
    ReplayLogEntry,
    read_all_entries,
)
from orchestrator.replay_integrity import ReplayIntegrityError
from orchestrator.scheduler import TickScheduler

Boundary = Literal["resolved", "aborted", "legacy_unresolved"]


@pytest.fixture(scope="module")
def recorded_rows(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[ReplayLogEntry, ...]:
    path = tmp_path_factory.mktemp("side-record-source") / "replay-seed-1.jsonl"
    game = HeadlessGame(
        seed=1,
        num_players=7,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=200),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
    )
    assert game.run().final_state.phase == "GAME_OVER"
    return read_all_entries(path)


def _boundary_rows(
    rows: tuple[ReplayLogEntry, ...], boundary: Boundary
) -> tuple[list[ReplayLogEntry], str, int]:
    meetings = [
        (index, row)
        for index, row in enumerate(rows)
        if isinstance(row, MeetingReplayEntry)
    ]
    assert len(meetings) == 2
    index, meeting = meetings[0 if boundary == "resolved" else 1]
    prefix = list(rows[: index + 1] if boundary == "resolved" else rows[:index])
    if boundary == "aborted":
        prefix.append(
            AbortedMeetingReplayEntry(
                game_id=meeting.game_id,
                meeting_id=meeting.meeting_id,
                tick=meeting.tick,
                llm_calls=(),
                prompt_versions=meeting.prompt_versions,
                error_type="RuntimeError",
                error_message="interrupted retry",
            )
        )
    return prefix, meeting.meeting_id, meeting.tick


def _failure(meeting_id: str, tick: int, call_id: str | None) -> FailedCallReplayEntry:
    return FailedCallReplayEntry(
        game_id="headless-seed-1",
        meeting_id=meeting_id,
        tick=tick,
        model="injected-model",
        prompt_length=5,
        raw_response="{}",
        input_tokens=10,
        output_tokens=2,
        cost_usd=0.25,
        error_type="ValidationError",
        error_message="invalid response",
        call_id=call_id,
    )


def _write(directory: Path, rows: list[ReplayLogEntry]) -> ReplayLoader:
    path = directory / "replay-seed-1.jsonl"
    path.write_text(
        "".join(
            row.model_dump_json(exclude={"call_id"}) + "\n"
            if isinstance(row, FailedCallReplayEntry) and row.call_id is None
            else row.model_dump_json() + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )
    return ReplayLoader(directory)


def test_failed_call_cannot_reuse_an_earlier_meeting_identity(
    recorded_rows: tuple[ReplayLogEntry, ...], tmp_path: Path
) -> None:
    rows, _, tick = _boundary_rows(recorded_rows, "legacy_unresolved")
    earlier = next(row for row in rows if isinstance(row, MeetingReplayEntry))
    rows.append(_failure(earlier.meeting_id, tick, "attempt-1"))
    loader = _write(tmp_path, rows)

    with pytest.raises(ReplayIntegrityError):
        loader.load_replay("headless-seed-1")
    assert loader.list_replays() == []


@pytest.mark.parametrize("different_content", [False, True])
def test_explicit_failed_call_identity_cannot_repeat(
    recorded_rows: tuple[ReplayLogEntry, ...],
    tmp_path: Path,
    different_content: bool,
) -> None:
    rows, meeting_id, tick = _boundary_rows(recorded_rows, "aborted")
    failure = _failure(meeting_id, tick, "attempt-1")
    duplicate = (
        failure.model_copy(update={"raw_response": "other response"})
        if different_content
        else failure
    )
    loader = _write(tmp_path, [*rows, failure, duplicate])

    with pytest.raises(ReplayIntegrityError):
        loader.load_replay("headless-seed-1")
    assert loader.list_replays() == []


@pytest.mark.parametrize("boundary", ["resolved", "aborted", "legacy_unresolved"])
def test_distinct_attempts_with_identical_content_remain_valid(
    recorded_rows: tuple[ReplayLogEntry, ...], tmp_path: Path, boundary: Boundary
) -> None:
    rows, meeting_id, tick = _boundary_rows(recorded_rows, boundary)
    rows.extend(_failure(meeting_id, tick, call_id) for call_id in ("one", "two"))
    loader = _write(tmp_path, rows)

    replay = loader.load_replay("headless-seed-1")

    assert len(replay.failed_calls) == 2
    assert replay.metadata.total_cost_usd == pytest.approx(0.50)
    assert replay.metadata.winner is None
    assert len(loader.list_replays()) == 1


def test_legacy_failed_call_without_attempt_identity_remains_valid(
    recorded_rows: tuple[ReplayLogEntry, ...], tmp_path: Path
) -> None:
    rows, meeting_id, tick = _boundary_rows(recorded_rows, "legacy_unresolved")
    loader = _write(tmp_path, [*rows, _failure(meeting_id, tick, None)])

    replay = loader.load_replay("headless-seed-1")

    assert len(replay.failed_calls) == 1
    assert replay.metadata.total_cost_usd == pytest.approx(0.25)
    assert replay.metadata.winner is None
    assert len(loader.list_replays()) == 1


@pytest.mark.parametrize("boundary", ["aborted", "legacy_unresolved"])
def test_partial_meeting_preserves_opaque_identity_in_trigger_event(
    recorded_rows: tuple[ReplayLogEntry, ...], tmp_path: Path, boundary: Boundary
) -> None:
    rows, _, tick = _boundary_rows(recorded_rows, boundary)
    meeting_id = "external-meeting-key"
    if boundary == "aborted":
        rows[-1] = rows[-1].model_copy(update={"meeting_id": meeting_id})
    rows.append(_failure(meeting_id, tick, "attempt-1"))
    loader = _write(tmp_path, rows)

    replay = loader.load_replay("headless-seed-1")

    triggers = [
        event
        for event in replay.ticks[-1].events
        if isinstance(event, MeetingTriggeredEventView)
    ]
    assert len(triggers) == 1
    assert triggers[0].meeting_id == replay.failed_calls[-1].meeting_id == meeting_id
    assert replay.metadata.winner is None


@pytest.mark.parametrize("boundary", ["resolved", "aborted", "legacy_unresolved"])
def test_empty_meeting_identity_is_rejected(
    recorded_rows: tuple[ReplayLogEntry, ...], tmp_path: Path, boundary: Boundary
) -> None:
    rows, _, tick = _boundary_rows(recorded_rows, boundary)
    if boundary != "legacy_unresolved":
        rows[-1] = rows[-1].model_copy(update={"meeting_id": ""})
    rows.append(_failure("", tick, "attempt-1"))
    loader = _write(tmp_path, rows)

    with pytest.raises(ReplayIntegrityError):
        loader.load_replay("headless-seed-1")
    assert loader.list_replays() == []
