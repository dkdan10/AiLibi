"""Unit coverage for the replay-log records and fail-loud guards.

These exercise the additive replay records introduced by Task 3.19 and the
fail-loud / doubled-file guards added by Task 4.16 (DESIGN.md §11.4):

* ``record_game_end`` / ``read_game_outcome`` — persist and recover the
  decisive game outcome so win-rate is evaluable from any replay log,
  including a partial tournament that crashed mid-run (finding 3).
* ``record_failed_call`` — persist the cost + partial response of an LLM
  call that aborted a meeting on schema-validation failure, so per-meeting
  cost is auditable even for the crashed meeting (finding 2), and is folded
  into ``compute_cost_usd``.
* ``ReplayLog.__init__`` fail-loud on an existing path (write side) and
  ``read_all_entries`` doubled-file detection (read side) — Task 4.16
  guards against the silent run-over-run concatenation that broke the
  loader's dedup in Phase 4 UX prep.

Pure replay-layer tests: no full game loop, no LLM call.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from orchestrator.replay import (
    FailedCallReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    ReplayEntry,
    ReplayLog,
    compute_cost_usd,
    read_all_entries,
    read_failed_call_entries,
    read_game_outcome,
)
from tests._helpers.world_state import scripted_initial_world_state


class TestGameEndRecording:
    def test_record_game_end_round_trips_via_read_game_outcome(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "outcome.jsonl"
        log = ReplayLog(path, game_id="g-1")

        log.record_game_end(winner="CREWMATES", reason="all_tasks_complete")

        assert read_game_outcome(path) == "CREWMATES"

    def test_game_end_entry_persists_winner_reason_and_tick(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "outcome.jsonl"
        log = ReplayLog(path, game_id="g-1")

        log.record_game_end(winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=412)

        entries = read_all_entries(path)
        assert len(entries) == 1
        entry = entries[0]
        assert isinstance(entry, GameEndReplayEntry)
        assert entry.kind == "game_over"
        assert entry.game_id == "g-1"
        assert entry.winner == "IMPOSTORS"
        assert entry.reason == "IMPOSTOR_PARITY"
        assert entry.tick == 412

    def test_read_game_outcome_returns_none_when_no_game_end_row(
        self, tmp_path: Path
    ) -> None:
        # A partial replay from a run that crashed mid-meeting: a failed-call
        # row is present but the game outcome was never decided.
        path = tmp_path / "partial.jsonl"
        log = ReplayLog(path, game_id="g-2")
        log.record_failed_call(
            meeting_id="g-2:meeting-0",
            tick=99,
            model="claude-sonnet-4-6",
            prompt_length=10,
            raw_response="I need to think...",
            input_tokens=1,
            output_tokens=1,
            cost_usd=0.0,
            error_type="ValidationError",
            error_message="boom",
        )

        assert read_game_outcome(path) is None

    def test_read_game_outcome_returns_none_for_empty_replay(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "empty.jsonl"
        path.write_text("", encoding="utf-8")

        assert read_game_outcome(path) is None

    def test_read_game_outcome_raises_on_doubled_game_over(
        self, tmp_path: Path
    ) -> None:
        # A game writes exactly one game-end row. Two ``game_over`` rows mean
        # two games' records were concatenated into one file (the Phase 4
        # doubled-write). ``read_game_outcome`` routes through
        # ``read_all_entries``, so it now fails loud (Task 4.16) instead of
        # silently returning the last winner.
        path = tmp_path / "multi.jsonl"
        log = ReplayLog(path, game_id="g-3")
        log.record_game_end(winner="CREWMATES", reason="CREWMATE_TASKS")
        log.record_game_end(winner="IMPOSTORS", reason="IMPOSTOR_PARITY")

        with pytest.raises(ReplayLog.CorruptedFileError):
            read_game_outcome(path)

    def test_record_game_end_accepts_none_winner_as_undecided(
        self, tmp_path: Path
    ) -> None:
        # winner=None encodes a drawn / unfinished game; the engine never
        # produces one, but the field allows it and it reads back as None.
        path = tmp_path / "draw.jsonl"
        log = ReplayLog(path, game_id="g-4")
        log.record_game_end(winner=None, reason="unfinished")

        assert read_game_outcome(path) is None


class TestFailedCallRecording:
    def test_record_failed_call_round_trips(self, tmp_path: Path) -> None:
        path = tmp_path / "failed.jsonl"
        log = ReplayLog(path, game_id="g-5")

        log.record_failed_call(
            meeting_id="g-5:meeting-0",
            tick=410,
            model="claude-sonnet-4-6",
            prompt_length=2048,
            raw_response='{"agent_id": "p-3"',
            input_tokens=1500,
            output_tokens=900,
            cost_usd=0.018,
            error_type="ValidationError",
            error_message="1 validation error for ReportDocument",
        )

        failed = read_failed_call_entries(path)
        assert len(failed) == 1
        entry = failed[0]
        assert isinstance(entry, FailedCallReplayEntry)
        assert entry.kind == "failed_call"
        assert entry.game_id == "g-5"
        assert entry.meeting_id == "g-5:meeting-0"
        assert entry.tick == 410
        assert entry.model == "claude-sonnet-4-6"
        assert entry.prompt_length == 2048
        assert entry.raw_response == '{"agent_id": "p-3"'
        assert entry.input_tokens == 1500
        assert entry.output_tokens == 900
        assert entry.cost_usd == 0.018
        assert entry.error_type == "ValidationError"
        assert entry.error_message == "1 validation error for ReportDocument"

    def test_compute_cost_usd_folds_in_failed_call_cost(self, tmp_path: Path) -> None:
        # The crashing call's spend must not be silently dropped from the
        # canonical per-game cost reduction (Task 3.19 finding 2).
        path = tmp_path / "cost.jsonl"
        log = ReplayLog(path, game_id="g-6")
        log.record_failed_call(
            meeting_id="g-6:meeting-0",
            tick=200,
            model="claude-sonnet-4-6",
            prompt_length=1000,
            raw_response="...",
            input_tokens=500,
            output_tokens=300,
            cost_usd=0.0075,
            error_type="ValidationError",
            error_message="boom",
        )

        assert compute_cost_usd(path) == 0.0075

    def test_compute_cost_usd_is_zero_for_game_end_only_replay(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "no-cost.jsonl"
        ReplayLog(path, game_id="g-7").record_game_end(
            winner="CREWMATES", reason="CREWMATE_TASKS"
        )

        assert compute_cost_usd(path) == 0.0


class TestLLMCallRecordAgentId:
    """``LLMCallRecord.agent_id`` per-call attribution (Task 4.7, §5, §11.4)."""

    def test_agent_id_round_trips_through_jsonl(self) -> None:
        record = LLMCallRecord(
            call_kind="meeting",
            model="claude-test",
            prompt="## Your role: CREWMATE",
            response_text='{"ok": true}',
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.01,
            agent_id="p-2",
        )

        restored = LLMCallRecord.model_validate_json(record.model_dump_json())

        assert restored == record
        assert restored.agent_id == "p-2"

    def test_missing_agent_id_defaults_to_none(self) -> None:
        # A replay JSONL written before this field existed has no agent_id
        # key. ``extra="forbid"`` rejects unknown fields but still permits a
        # missing optional one, so old replays load with agent_id=None.
        legacy_line = (
            '{"call_kind": "meeting", "model": "claude-test", "prompt": "p", '
            '"response_text": "r", "input_tokens": 1, "output_tokens": 1, '
            '"cost_usd": 0.0}'
        )

        record = LLMCallRecord.model_validate_json(legacy_line)

        assert record.agent_id is None


class TestWriteSideFailLoud:
    """``ReplayLog.__init__`` refuses an existing path unless ``force=True``.

    Write-side guard for Task 4.16 (DESIGN.md §11.4): re-using a replay path
    used to silently append a second game's rows, doubling the file.
    """

    def test_constructing_against_existing_file_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "replay.jsonl"
        state = scripted_initial_world_state(seed=1)
        ReplayLog(path, game_id="g-1").record_tick(0, [], state)

        with pytest.raises(ReplayLog.AlreadyExistsError) as excinfo:
            ReplayLog(path, game_id="g-1")

        assert str(path) in str(excinfo.value)

    def test_already_exists_error_is_a_file_exists_error(self, tmp_path: Path) -> None:
        # Subclassing FileExistsError lets callers that only catch the stdlib
        # type still intercept the fail-loud.
        path = tmp_path / "replay.jsonl"
        ReplayLog(path, game_id="g-1").record_game_end(
            winner="CREWMATES", reason="done"
        )

        with pytest.raises(FileExistsError):
            ReplayLog(path, game_id="g-1")

    def test_force_true_truncates_previous_content(self, tmp_path: Path) -> None:
        path = tmp_path / "replay.jsonl"
        state = scripted_initial_world_state(seed=1)
        ReplayLog(path, game_id="g-old").record_tick(0, [], state)

        # force=True deletes the old file before recording, so the previous
        # game's rows are gone and no doubled-write can happen. Nothing is on
        # disk until the next append.
        reopened = ReplayLog(path, game_id="g-new", force=True)
        assert not path.exists()

        reopened.record_tick(0, [], state)
        entries = read_all_entries(path)
        assert len(entries) == 1
        entry = entries[0]
        assert isinstance(entry, ReplayEntry)
        assert entry.game_id == "g-new"
        assert entry.tick == 0

    def test_constructing_against_fresh_path_succeeds(self, tmp_path: Path) -> None:
        # The common case: a brand-new path needs no force.
        path = tmp_path / "fresh.jsonl"
        ReplayLog(path, game_id="g-1").record_game_end(
            winner="CREWMATES", reason="done"
        )

        assert read_game_outcome(path) == "CREWMATES"


class TestReadSideDoubledFileDetection:
    """``read_all_entries`` fails loud on the doubled-file pattern (Task 4.16).

    The lived incident: two tournament runs against the same ``--output-dir``
    concatenated per-seed JSONLs. A doubled file has overlapping ``tick``
    values and/or two ``game_over`` rows.
    """

    def test_duplicate_tick_raises_naming_path_and_tick(self, tmp_path: Path) -> None:
        path = tmp_path / "doubled-ticks.jsonl"
        tick_row = (
            '{"kind":"tick","game_id":"g-1","tick":0,"actions":[],'
            '"state_hash":"deadbeef"}'
        )
        path.write_text(f"{tick_row}\n{tick_row}\n", encoding="utf-8")

        with pytest.raises(ReplayLog.CorruptedFileError) as excinfo:
            read_all_entries(path)

        message = str(excinfo.value)
        assert "Duplicate tick 0" in message
        assert str(path) in message

    def test_two_game_over_rows_raise_naming_path(self, tmp_path: Path) -> None:
        path = tmp_path / "doubled-overs.jsonl"
        over_row = (
            '{"kind":"game_over","game_id":"g-1","winner":"CREWMATES","reason":"done"}'
        )
        path.write_text(f"{over_row}\n{over_row}\n", encoding="utf-8")

        with pytest.raises(ReplayLog.CorruptedFileError) as excinfo:
            read_all_entries(path)

        message = str(excinfo.value)
        assert "game_over" in message
        assert str(path) in message

    def test_clean_single_game_reads_without_raising(self, tmp_path: Path) -> None:
        # A normal game — strictly increasing ticks, exactly one game_over —
        # is unaffected by the doubled-file detection.
        path = tmp_path / "clean.jsonl"
        state = scripted_initial_world_state(seed=1)
        log = ReplayLog(path, game_id="g-1")
        log.record_tick(0, [], state)
        log.record_tick(1, [], state)
        log.record_game_end(winner="CREWMATES", reason="done")

        entries = read_all_entries(path)

        assert len(entries) == 3
