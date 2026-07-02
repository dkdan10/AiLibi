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
    SUBSTRATE_FLAG_KEYS,
    FailedCallReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    ReplayEntry,
    ReplayLog,
    compute_cost_usd,
    read_all_entries,
    read_failed_call_entries,
    read_game_outcome,
    read_substrate_flags,
    substrate_flag_snapshot,
)
from tests._helpers.world_state import scripted_initial_world_state

# The committed 9p2i sample set the gp-4 audit measured; read-only here (the
# re-record itself is Task 9.11).
_COMMITTED_9P2I_REPLAYS = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)


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


class TestSubstrateFlagStamp:
    """The Task-14.7 substrate-flag stamp on the game_over record.

    A replay self-describes which Phase-13.5 levers generated it. Since Task
    14.9 the four levers are unconditionally ON (their env gates are retired),
    so the snapshot is constant all-True regardless of the environment and
    every new recording stamps the full snapshot — matching the committed
    14.7 flags-ON baseline. The stamp machinery stays generic: a future
    toggleable lever (14.10) registers its key + resolver in
    ``orchestrator.replay`` and rides the same snapshot/stamp/guard path.
    """

    def test_substrate_flag_snapshot_is_unconditionally_all_on(self) -> None:
        # The retired levers report True under ANY env — a bare mapping, an
        # explicit legacy "0", or the legacy all-ON export all read identically.
        all_on = dict.fromkeys(SUBSTRATE_FLAG_KEYS, True)
        assert substrate_flag_snapshot({}) == all_on
        assert substrate_flag_snapshot() == all_on
        assert substrate_flag_snapshot({"AILIBI_TESTIMONY_AS_CONTENT": "0"}) == all_on
        assert set(SUBSTRATE_FLAG_KEYS) == {
            "testimony_as_content",
            "witnessed_kill_evidence",
            "movement_perception",
            "unfreeze_memory",
        }

    def test_every_recording_stamps_the_full_snapshot(self, tmp_path: Path) -> None:
        # No env vars needed: recording under a bare environment stamps all
        # four levers ON, consistent with the committed 14.7 baseline.
        path = tmp_path / "on.jsonl"
        ReplayLog(path, game_id="g-on").record_game_end(
            winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=41
        )
        entry = read_all_entries(path)[0]
        assert isinstance(entry, GameEndReplayEntry)
        assert entry.substrate_flags == {
            "testimony_as_content": True,
            "witnessed_kill_evidence": True,
            "movement_perception": True,
            "unfreeze_memory": True,
        }
        assert read_substrate_flags(path) == dict(entry.substrate_flags)

    def test_legacy_game_over_without_stamp_deserializes(self) -> None:
        # A pre-14.7 game_over record (no substrate_flags key) still validates,
        # with the field defaulting to None — so committed replays reconstruct
        # unchanged.
        entry = GameEndReplayEntry.model_validate(
            {
                "kind": "game_over",
                "game_id": "legacy",
                "tick": 7,
                "winner": "CREWMATES",
                "reason": "TASKS",
            }
        )
        assert entry.substrate_flags is None


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
        # A non-vote failed call carries no §4.6 verdict (Task 10.12).
        assert entry.rendered_vote_max is None

    def test_defaulted_vote_persists_rendered_max(self, tmp_path: Path) -> None:
        # Task 10.12 (audit H-H-2): a defaulted VOTE row carries the rendered
        # §4.6 max so the offline verdict reconstruction can classify it.
        path = tmp_path / "failed.jsonl"
        log = ReplayLog(path, game_id="g-5")

        log.record_failed_call(
            meeting_id="g-5:meeting-2",
            tick=80,
            model="(deadline_default)",
            prompt_length=0,
            raw_response="",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            error_type="deadline_default",
            error_message="vote defaulted (validation); p-1 submitted no ballot",
            rendered_vote_max=0.65,
        )

        entry = read_failed_call_entries(path)[0]
        assert entry.rendered_vote_max == 0.65

    def test_legacy_failed_call_without_field_tolerates_absence(self) -> None:
        # Backward-compat pin (Task 10.12): every committed single-era replay
        # predates ``rendered_vote_max``, so a row WITHOUT the key must still
        # load (default ``None``) -- the reader tolerates its absence and the
        # bytes reconstruct unchanged.
        legacy = {
            "kind": "failed_call",
            "game_id": "g-9",
            "meeting_id": "g-9:meeting-0",
            "tick": 40,
            "model": "(deadline_default)",
            "prompt_length": 0,
            "raw_response": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "error_type": "deadline_default",
            "error_message": "vote defaulted (validation); p-1 submitted no ballot",
        }

        entry = FailedCallReplayEntry.model_validate(legacy)

        assert entry.rendered_vote_max is None

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


class TestFailedCallSingleWriteGuard:
    """Byte-identical failed-call rows write once (Task 9.10, audit gp-4).

    The lived incident (MECH-B-1): a deterministic provider (seeded local
    model, fixed prompt) regenerates the SAME failing response on the in-turn
    retry, so a single defaulted opening surfaced the same burned generation
    twice and seeds 8/36/39 each persisted a duplicate ``failed_call`` row —
    double-counting 5,969 input / 6,144 output tokens and inflating
    ``total_failed_calls`` 4→7. ``record_failed_call`` now drops a row that is
    byte-identical (the FULL frozen entry) to one this log already wrote.
    Distinct rows — including zero-spend ``deadline_default`` visibility
    markers that share the zero ``(model, raw_response, input_tokens,
    output_tokens)`` tuple but name different participants in
    ``error_message`` — still each record once.
    """

    @staticmethod
    def _record_seed_shape_row(
        log: ReplayLog,
        *,
        model: str = "Qwen/Qwen3-32B",
        raw_response: str = '{\n  "turn_id": "t",\n  "turn_index": 0,\n  "speaker": "p-2"',
        input_tokens: int = 1984,
        output_tokens: int = 2048,
        error_message: str = (
            "opening turn (turn 0) defaulted (validation); p-2 submitted no "
            "turn [ValidationError: EOF while parsing a string]"
        ),
    ) -> None:
        # Field values mirror the committed seed-8 duplicate (meeting-1,
        # tick 14) — the audited double-count shape.
        log.record_failed_call(
            meeting_id="headless-seed-8:meeting-1",
            tick=14,
            model=model,
            prompt_length=6627,
            raw_response=raw_response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=0.0,
            error_type="deadline_default",
            error_message=error_message,
        )

    def test_byte_identical_retry_row_records_exactly_once(
        self, tmp_path: Path
    ) -> None:
        # The seed-8/36/39 shape: the opening's single retry burned a
        # byte-identical generation, so the defaulted turn issues the same
        # write twice; exactly one row may land.
        path = tmp_path / "dedup.jsonl"
        with ReplayLog(path, game_id="headless-seed-8") as log:
            self._record_seed_shape_row(log)
            self._record_seed_shape_row(log)

        failed = read_failed_call_entries(path)
        assert len(failed) == 1
        # The spend is counted once, not doubled.
        assert sum(f.input_tokens for f in failed) == 1984
        assert sum(f.output_tokens for f in failed) == 2048

    def test_distinct_failures_in_one_meeting_each_record_once(
        self, tmp_path: Path
    ) -> None:
        # Two genuinely different burned generations in the same meeting
        # (different raw response / spend) are NOT duplicates.
        path = tmp_path / "distinct.jsonl"
        with ReplayLog(path, game_id="headless-seed-8") as log:
            self._record_seed_shape_row(log)
            self._record_seed_shape_row(
                log,
                raw_response='{\n  "turn_id": "t",\n  "claims": [',
                output_tokens=903,
            )

        failed = read_failed_call_entries(path)
        assert len(failed) == 2
        assert sum(f.output_tokens for f in failed) == 2048 + 903

    def test_zero_spend_markers_for_different_defaults_each_record_once(
        self, tmp_path: Path
    ) -> None:
        # Two zero-spend visibility markers (a defaulted turn and a defaulted
        # vote) share the zero (model, raw_response, tokens) tuple and differ
        # only in error_message; deduping on the FULL row keeps both visible.
        path = tmp_path / "markers.jsonl"
        with ReplayLog(path, game_id="g-1") as log:
            for message in (
                "reply turn (turn 2) defaulted (deadline); p-2 submitted no turn",
                "vote defaulted (deadline); p-3 submitted no ballot",
            ):
                log.record_failed_call(
                    meeting_id="g-1:meeting-0",
                    tick=30,
                    model="(deadline_default)",
                    prompt_length=0,
                    raw_response="",
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    error_type="deadline_default",
                    error_message=message,
                )

        assert len(read_failed_call_entries(path)) == 2

    def test_guard_is_per_log_not_per_process(self, tmp_path: Path) -> None:
        # The same failure shape in a DIFFERENT game's log is a different
        # burned call and must still record.
        with ReplayLog(tmp_path / "a.jsonl", game_id="g-a") as log:
            self._record_seed_shape_row(log)
        with ReplayLog(tmp_path / "b.jsonl", game_id="g-b") as log:
            self._record_seed_shape_row(log)

        assert len(read_failed_call_entries(tmp_path / "a.jsonl")) == 1
        assert len(read_failed_call_entries(tmp_path / "b.jsonl")) == 1

    def test_committed_9p2i_rows_rerecord_to_their_distinct_set(
        self, tmp_path: Path
    ) -> None:
        # Offline confirmation against the committed 9p2i set: re-recording
        # each replay's failed-call rows through the guarded chokepoint yields
        # exactly its distinct rows in order. On the Qwen/Qwen3-32B qwen3_32b.v3
        # re-record the committed bytes carry no duplicate failed-call shapes —
        # every seed's rows are already distinct, so clean bytes re-record to
        # themselves (including the rendered_vote_max carried on vote defaults,
        # e.g. seeds 21/34/36).
        sample_files = sorted(_COMMITTED_9P2I_REPLAYS.glob("replay-seed-*.jsonl"))
        assert sample_files, f"no committed replays under {_COMMITTED_9P2I_REPLAYS}"
        for sample in sample_files:
            originals = read_failed_call_entries(sample)
            if not originals:
                continue
            distinct = list(dict.fromkeys(originals))
            rerecord_path = tmp_path / sample.name
            with ReplayLog(rerecord_path, game_id=originals[0].game_id) as log:
                for entry in originals:
                    log.record_failed_call(
                        meeting_id=entry.meeting_id,
                        tick=entry.tick,
                        model=entry.model,
                        prompt_length=entry.prompt_length,
                        raw_response=entry.raw_response,
                        input_tokens=entry.input_tokens,
                        output_tokens=entry.output_tokens,
                        cost_usd=entry.cost_usd,
                        error_type=entry.error_type,
                        error_message=entry.error_message,
                        rendered_vote_max=entry.rendered_vote_max,
                    )
            assert list(read_failed_call_entries(rerecord_path)) == distinct


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
