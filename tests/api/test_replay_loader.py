"""Unit tests for :class:`api.replay_loader.ReplayLoader` (DESIGN.md §7, §11.4).

The fixtures write real replays via ``orchestrator.replay.ReplayLog`` (see
``tests/api/fixtures/sample_replay.py``), so these tests exercise engine
playback against ground truth: every reconstructed ``state_hash`` must match
the recorded one, or :class:`ReplayStateMismatchError` is raised.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Literal, get_args

import pytest
from fastapi.testclient import TestClient

# Task 8.7 reshaped ``MeetingTranscript`` to the ordered ``turns`` list and
# removed ``ReportDocument`` / ``Statement`` from ``meetings.schemas``; Task 8.10
# re-pointed the api replay-loader views (``api/replay_loader.py`` /
# ``api/schemas.py``) and the shared meeting-replay fixture
# (``tests/api/fixtures/sample_replay.py``) onto the turn shape, so this module
# imports cleanly again (the mid-stack ImportError shim is no longer needed). The
# committed-set meeting reconstruction stays skipped per-test until Task 8.12
# re-records it (idempotent with Task 8.1's state_hash-driven skip).
from api import replay_loader
from api.main import create_app
from api.replay_loader import (
    _TURN_PREFIX_MARKERS,  # noqa: PLC2701
    _turn_view,  # noqa: PLC2701
    EmptyReplayError,
    ReplayDispositionMismatchError,
    ReplayLoader,
    ReplayStateMismatchError,
    ReplaySubstrateMismatchError,
    RosterConfig,
    get_replay_loader,
)
from api.schemas import (
    CurrentAction,
    ReplayView,
    FoundBodyObsView,
    KillEventView,
    MeetingTriggeredEventView,
    ReportBodyEventView,
    SawMoveObservationView,
    TurnAnnotationLabel,
)
from meetings.manager import (
    EMERGENCY_BODY_STRIP_MARKER,
    INVALID_ACCUSATION_TARGET_MARKER,
    OPENING_UNSURE_DEGRADE_MARKER,
)
from meetings.schemas import (
    BallotTargetRewriteReason,
    MeetingTurn,
    VoteBallot,
    SawMoveObservation,
    TurnAnnotation,
    TurnAnnotationKind,
)
from engine.actions import Action
from engine.entities import BodyState, PlayerState, TaskState
from engine.events import ActionRejectedEvent
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from llm.fake_provider import FakeProvider
from observation.service import ObservationService
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    MeetingReplayEntry,
    ReplayEntry,
    ReplayLogEntry,
    _stable_json,  # noqa: PLC2701
    classify_action_dispositions,
    read_all_entries,
    substrate_flag_snapshot,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state
from tests.api.fixtures.sample_replay import (
    MeetingReplayExpectations,
    corrupt_tick_hash,
    strip_llm_call_agent_ids,
    write_meeting_replay,
    write_partial_replay,
    write_roster_replay,
    write_sample_replay,
    write_unresolved_meeting_replay,
)


@pytest.fixture
def loader(tmp_path: Path) -> ReplayLoader:
    return ReplayLoader(replay_dir=tmp_path)


def test_load_replay_reconstructs_ticks_meetings_and_winner(
    tmp_path: Path, loader: ReplayLoader
) -> None:
    expected = write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)

    replay = loader.load_replay("headless-seed-0")

    # ticks[0] is the synthesized tick=-1 "Start" frame (Finding 1); the recorded
    # ticks (0 .. total_ticks-1) follow it. The round-start cooldown (DESIGN.md
    # §3.4) delays the opening kill, so the fixture is longer than the pre-gp-1
    # 3-tick game — assert against the values the fixture reports rather than
    # magic numbers.
    assert [tick.tick for tick in replay.ticks] == [-1, *range(expected.total_ticks)]
    assert len(replay.meetings) == 1
    meeting = replay.meetings[0]
    assert meeting.meeting_id == expected.meeting_id
    assert meeting.tick == expected.meeting_tick
    assert meeting.trigger_kind == "body"
    assert meeting.outcome == "SKIPPED"
    assert meeting.total_cost_usd == pytest.approx(expected.total_cost_usd)
    # The reactive chain (DESIGN.md §5.2) is one ordered ``turns`` list: the
    # fixture's meeting is a single opening turn by the reporter (unsure, so the
    # chain terminates at once). Every living agent still casts a ballot.
    assert [turn.speaker for turn in meeting.turns] == [expected.reporter]
    assert meeting.turns[0].turn_kind == "opening"
    assert {ballot.voter for ballot in meeting.ballots} == set(expected.living_agents)
    assert replay.metadata.winner == "CREWMATES"
    # total_ticks counts only recorded ReplayEntrys; the synthesized initial
    # entry is extra, so ticks has exactly one more element than total_ticks.
    assert replay.metadata.total_ticks == expected.total_ticks
    assert len(replay.ticks) == replay.metadata.total_ticks + 1
    assert replay.metadata.meeting_count == 1
    assert {player.agent_id for player in replay.players} == {
        "p-1",
        "p-2",
        "p-3",
        "p-4",
    }
    assert replay.map.rooms  # canonical map geometry is populated


def test_initial_state_tick_is_synthesized_at_spawn(
    tmp_path: Path, loader: ReplayLoader
) -> None:
    # Finding 1 (DESIGN.md §3.1, §11.4): record_tick snapshots post-advance_tick
    # state, so the recorded tick 0 no longer shows the pre-action spawn. The
    # loader prepends a synthesized tick=-1 "Start" frame with every player
    # alive in the canonical map's spawn room (CAFETERIA).
    write_sample_replay(tmp_path / "replay-seed-22.jsonl", seed=22, ticks=3)

    replay = loader.load_replay("headless-seed-22")

    start = replay.ticks[0]
    assert start.tick == -1
    assert len(start.agent_states) == 4
    for agent in start.agent_states:
        assert agent.is_alive is True
        assert agent.room_id == "CAFETERIA"
        assert agent.is_venting is False
        assert agent.current_action == "IDLE"
    assert start.tasks_completed_total == 0
    assert start.tasks_required_total > 0
    assert start.events == ()
    assert start.sabotage_active == ()
    # total_ticks counts recorded entries only; the synthesized frame is extra.
    assert len(replay.ticks) == replay.metadata.total_ticks + 1


def test_tick_event_projection(tmp_path: Path, loader: ReplayLoader) -> None:
    expected = write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    replay = loader.load_replay("headless-seed-0")

    # The round-start cooldown (DESIGN.md §3.4) delays the opening kill: it lands
    # on the tick before the report/meeting. Select by tick number, not array
    # index (ticks[0] is the synthesized tick=-1 "Start" frame).
    kill_tick = next(t for t in replay.ticks if t.tick == expected.meeting_tick - 1)
    meeting_tick = next(t for t in replay.ticks if t.tick == expected.meeting_tick)

    kill_events = [e for e in kill_tick.events if isinstance(e, KillEventView)]
    assert len(kill_events) == 1
    assert kill_events[0].victim_id == expected.victim

    meeting_tick_types = {type(e) for e in meeting_tick.events}
    assert MeetingTriggeredEventView in meeting_tick_types
    assert ReportBodyEventView in meeting_tick_types


def test_dead_player_and_impostor_tick_state(
    tmp_path: Path, loader: ReplayLoader
) -> None:
    write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    replay = loader.load_replay("headless-seed-0")

    final_states = {s.agent_id: s for s in replay.ticks[-1].agent_states}
    victim = final_states["p-1"]
    assert victim.is_alive is False
    assert victim.room_id is None

    impostor = final_states["p-3"]  # seed 0 impostor
    assert impostor.task_progress is None  # impostors never carry task progress


def test_list_replays_sorted_and_skips_non_matching(tmp_path: Path) -> None:
    write_sample_replay(tmp_path / "replay-seed-2.jsonl", seed=2)
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / "replay-seed-foo.jsonl").write_text("ignore", encoding="utf-8")

    loader = ReplayLoader(replay_dir=tmp_path)
    metas = loader.list_replays()

    assert [meta.seed for meta in metas] == [0, 2]
    assert [meta.game_id for meta in metas] == [
        "headless-seed-0",
        "headless-seed-2",
    ]


def test_list_replays_empty_dir_returns_empty(tmp_path: Path) -> None:
    loader = ReplayLoader(replay_dir=tmp_path / "does-not-exist")
    assert loader.list_replays() == []


def test_state_hash_mismatch_raises_with_bad_tick(tmp_path: Path) -> None:
    path = tmp_path / "replay-seed-0.jsonl"
    write_sample_replay(path, seed=0, ticks=3)
    corrupt_tick_hash(path, tick=1)

    loader = ReplayLoader(replay_dir=tmp_path)
    with pytest.raises(ReplayStateMismatchError) as exc_info:
        loader.load_replay("headless-seed-0")
    assert exc_info.value.tick == 1
    assert exc_info.value.game_id == "headless-seed-0"


def test_partial_replay_has_no_winner_but_intact_timeline(tmp_path: Path) -> None:
    write_partial_replay(tmp_path / "replay-seed-7.jsonl", seed=7, ticks=4)
    loader = ReplayLoader(replay_dir=tmp_path)

    replay = loader.load_replay("headless-seed-7")
    assert replay.metadata.winner is None
    assert replay.metadata.winner_reason is None
    # Synthesized "Start" (tick=-1) precedes the recorded ticks.
    assert [tick.tick for tick in replay.ticks] == [-1, 0, 1, 2, 3]


def test_unresolved_meeting_is_not_exposed_via_memory(tmp_path: Path) -> None:
    # A meeting that opened but never resolved (crash mid-meeting) has no
    # MeetingReplayEntry, so it is absent from `replay.meetings`; memory for it
    # must be absent too, so /meetings/{id} and /memory/{id} agree (both 404).
    meeting_id = write_unresolved_meeting_replay(
        tmp_path / "replay-seed-0.jsonl", seed=0
    )
    loader = ReplayLoader(replay_dir=tmp_path)

    replay = loader.load_replay("headless-seed-0")
    assert replay.meetings == ()
    assert replay.metadata.winner is None
    # The round-start cooldown (DESIGN.md §3.4) delays the opening kill, so the
    # meeting opens at ``kill_cooldown_ticks + 1`` (the fixture no-ops out the
    # cooldown, kills, then reports). Synthesized "Start" (tick=-1) precedes the
    # recorded ticks.
    meeting_tick = load_canonical_map().kill_cooldown_ticks + 1
    assert [tick.tick for tick in replay.ticks] == [-1, *range(meeting_tick + 1)]
    # The tick timeline still surfaces the meeting_triggered event...
    tick_meeting = next(t for t in replay.ticks if t.tick == meeting_tick)
    assert any(
        isinstance(event, MeetingTriggeredEventView) and event.meeting_id == meeting_id
        for event in tick_meeting.events
    )
    # ...but memory for the unresolved meeting is not exposed.
    with pytest.raises(KeyError):
        loader.get_meeting_memory("headless-seed-0", meeting_id, "p-2")


def test_unknown_game_raises_file_not_found(loader: ReplayLoader) -> None:
    with pytest.raises(FileNotFoundError):
        loader.load_replay("headless-seed-404")


def test_aborted_call_summary_preserves_spend_without_resolving_meeting(
    tmp_path: Path,
) -> None:
    path = tmp_path / "replay-seed-0.jsonl"
    meeting_id = write_unresolved_meeting_replay(path, seed=0)
    entry = AbortedMeetingReplayEntry(
        game_id="headless-seed-0",
        meeting_id=meeting_id,
        tick=load_canonical_map().kill_cooldown_ticks + 1,
        llm_calls=(
            LLMCallRecord(
                call_kind="meeting",
                model="paid-model",
                prompt="saved prompt",
                response_text="saved response",
                input_tokens=10,
                output_tokens=2,
                cost_usd=0.06,
                agent_id="p-2",
            ),
        ),
        prompt_versions={"opening": "opening.v1"},
        error_type="RuntimeError",
        error_message="transport stopped",
    )
    with path.open("a", encoding="utf-8") as stream:
        stream.write(entry.model_dump_json() + "\n")
    loader = ReplayLoader(replay_dir=tmp_path)

    replay = loader.load_replay("headless-seed-0")

    assert replay.metadata.total_cost_usd == pytest.approx(0.06)
    assert replay.metadata.prompt_versions == {"opening": "opening.v1"}
    assert replay.metadata.meeting_count == 0
    assert replay.metadata.winner is None
    assert replay.finale is None
    assert replay.meetings == ()
    assert replay.failed_calls == ()
    assert loader.list_replays()[0].total_cost_usd == pytest.approx(0.06)
    assert loader.cost_summary().total_cost_usd == pytest.approx(0.06)
    assert "saved prompt" not in replay.model_dump_json()
    with pytest.raises(KeyError):
        loader.get_meeting_memory("headless-seed-0", meeting_id, "p-2")


def test_lru_cache_returns_same_instance_until_cleared(tmp_path: Path) -> None:
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    loader = ReplayLoader(replay_dir=tmp_path)

    first = loader.load_replay("headless-seed-0")
    second = loader.load_replay("headless-seed-0")
    assert first is second  # cache hit shortcuts engine playback

    loader.clear_cache()
    third = loader.load_replay("headless-seed-0")
    assert third is not first
    assert third == first  # value-equal frozen DTO


def test_get_meeting_memory_fields(tmp_path: Path) -> None:
    expected = write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    loader = ReplayLoader(replay_dir=tmp_path)
    reporter = expected.reporter

    memory = loader.get_meeting_memory("headless-seed-0", expected.meeting_id, reporter)

    assert memory.agent_id == reporter
    assert memory.tick == expected.meeting_tick
    assert memory.role == "CREWMATE"
    # Task 13.12 flipped the canonical default to ``redistribute``: the fixture's
    # kill re-keys the victim's incomplete task to the surviving reporter, so the
    # reconstructed memory view shows 2 assigned tasks (was 1 under the old drop
    # default — the dropped task is now inherited, not deleted).
    assert memory.tasks_assigned == 2
    assert memory.rendered_memory_text.startswith("## Your role: CREWMATE")
    # Observations are projected from the reconstructed episodic memory (the
    # same store rendered_memory_text draws from): the reporter saw the body, so
    # a found_body observation is present, ordered ahead of any sightings.
    assert any(isinstance(o, FoundBodyObsView) for o in memory.observations)
    assert isinstance(memory.observations[0], FoundBodyObsView)
    # The fixture's contradiction lists the reporter as a subject.
    assert len(memory.open_contradictions) == 1


def test_dead_player_memory_is_retrievable(tmp_path: Path) -> None:
    # A player who died before the meeting is a known agent; ThoughtStream must
    # still be able to inspect their (frozen-at-death) memory.
    expected = write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    loader = ReplayLoader(replay_dir=tmp_path)

    memory = loader.get_meeting_memory(
        "headless-seed-0", expected.meeting_id, expected.victim
    )
    assert memory.agent_id == expected.victim
    assert memory.rendered_memory_text.startswith("## Your role:")


def test_non_default_roster_is_inferred_from_actions(tmp_path: Path) -> None:
    # The replay format doesn't persist num_players; the loader recovers it from
    # the action stream so a non-default-roster replay loads without a 500.
    write_roster_replay(tmp_path / "replay-seed-0.jsonl", seed=0, num_players=6)
    loader = ReplayLoader(replay_dir=tmp_path)

    replay = loader.load_replay("headless-seed-0")
    assert {player.agent_id for player in replay.players} == {
        f"p-{n}" for n in range(1, 7)
    }


def test_zero_padded_filename_is_fetchable_by_advertised_game_id(
    tmp_path: Path,
) -> None:
    # list_replays advertises a zero-padded file as game_id=headless-seed-1;
    # load_replay must resolve the same file rather than 404.
    write_sample_replay(tmp_path / "replay-seed-01.jsonl", seed=1)
    loader = ReplayLoader(replay_dir=tmp_path)

    (meta,) = loader.list_replays()
    assert meta.game_id == "headless-seed-1"
    assert loader.load_replay(meta.game_id).metadata.game_id == "headless-seed-1"


def test_directory_matching_glob_is_skipped(tmp_path: Path) -> None:
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    (tmp_path / "replay-seed-7.jsonl").mkdir()  # directory, not a replay file
    loader = ReplayLoader(replay_dir=tmp_path)

    assert [meta.seed for meta in loader.list_replays()] == [0]


def test_duplicate_seed_files_are_deduped_deterministically(tmp_path: Path) -> None:
    # Two filenames map to seed 1 (canonical + zero-padded). The seed must be
    # advertised once and resolve to the same file regardless of glob order.
    write_sample_replay(tmp_path / "replay-seed-1.jsonl", seed=1)
    write_sample_replay(tmp_path / "replay-seed-01.jsonl", seed=1)
    loader = ReplayLoader(replay_dir=tmp_path)

    metas = loader.list_replays()
    assert [meta.game_id for meta in metas] == ["headless-seed-1"]  # unique
    # Fetchable, and the resolved file is stable across calls (deterministic).
    assert loader.load_replay("headless-seed-1").metadata.game_id == "headless-seed-1"


def test_get_meeting_memory_unknown_meeting_and_agent(tmp_path: Path) -> None:
    expected = write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    loader = ReplayLoader(replay_dir=tmp_path)

    with pytest.raises(KeyError):
        loader.get_meeting_memory("headless-seed-0", "headless-seed-0:meeting-9", "p-2")
    with pytest.raises(KeyError):
        loader.get_meeting_memory("headless-seed-0", expected.meeting_id, "p-999")
    with pytest.raises(FileNotFoundError):
        loader.get_meeting_memory("headless-seed-404", "x", "p-2")


def test_cost_summary_aggregates_across_replays(tmp_path: Path) -> None:
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    meeting = write_meeting_replay(tmp_path / "replay-seed-1.jsonl", seed=1)
    loader = ReplayLoader(replay_dir=tmp_path)

    summary = loader.cost_summary()
    assert summary.total_replays == 2
    assert summary.total_cost_usd == pytest.approx(meeting.total_cost_usd)
    assert summary.max_cost_per_replay == pytest.approx(meeting.total_cost_usd)
    assert summary.mean_cost_per_replay == pytest.approx(meeting.total_cost_usd / 2)
    # Both replays record a CREWMATES win.
    assert summary.decisive_split == {"CREWMATES": 1.0, "IMPOSTORS": 0.0}


def test_cost_summary_empty_dir_is_zeroed(tmp_path: Path) -> None:
    loader = ReplayLoader(replay_dir=tmp_path / "empty")
    summary = loader.cost_summary()
    assert summary.total_replays == 0
    assert summary.total_cost_usd == 0.0
    assert summary.mean_cost_per_replay == 0.0
    assert summary.max_cost_per_replay == 0.0
    assert summary.decisive_split == {}


def test_llm_call_agent_id_round_trips_to_dto(tmp_path: Path) -> None:
    # Task 4.7: a recorded LLMCallRecord.agent_id survives the full pipeline
    # (JSONL -> loader -> DTO) and surfaces on LLMCallView.agent_id.
    custom_calls = (
        LLMCallRecord(
            call_kind="meeting",
            model="fake-model",
            prompt="## Your role: CREWMATE\nEmit one ReportDocument.",
            response_text='{"ok": true}',
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.01,
            agent_id="p-2",
        ),
    )
    write_meeting_replay(
        tmp_path / "replay-seed-0.jsonl", seed=0, llm_calls=custom_calls
    )
    loader = ReplayLoader(replay_dir=tmp_path)

    meeting = loader.load_replay("headless-seed-0").meetings[0]
    assert [call.agent_id for call in meeting.llm_calls] == ["p-2"]


def test_llm_call_agent_id_is_none_for_pre_4_7_replay(tmp_path: Path) -> None:
    # A replay written before the agent_id field existed has no agent_id key on
    # its LLM-call records; the loader must surface agent_id=None, not crash.
    path = tmp_path / "replay-seed-0.jsonl"
    write_meeting_replay(path, seed=0)
    strip_llm_call_agent_ids(path)
    loader = ReplayLoader(replay_dir=tmp_path)

    meeting = loader.load_replay("headless-seed-0").meetings[0]
    assert meeting.llm_calls  # the fixture wrote LLM calls
    assert all(call.agent_id is None for call in meeting.llm_calls)


# -- efficiency / pagination / resilience (Task 6.6) --------------------------


def _count_reads(monkeypatch: pytest.MonkeyPatch) -> dict[Path, int]:
    """Spy on ``read_all_entries``; return a live ``{path: read_count}`` map."""

    reads: dict[Path, int] = {}
    real = read_all_entries  # original, captured before the module attr is swapped

    def counting(path: Path) -> tuple[ReplayLogEntry, ...]:
        reads[Path(path)] = reads.get(Path(path), 0) + 1
        return real(path)

    monkeypatch.setattr(replay_loader, "read_all_entries", counting)
    return reads


def _bump_mtime(path: Path, *, by_ns: int = 2_000_000_000) -> None:
    """Advance ``path``'s mtime so a cache key folding mtime changes for sure.

    Guards the rewrite-invalidation tests against coarse filesystem timestamp
    resolution, where a fast unlink+rewrite could reuse the previous mtime.
    """

    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + by_ns))


def test_cost_summary_reads_each_file_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # G-G-2: cost AND decisive outcome come from one read_all_entries per file,
    # not the pre-6.6 two passes (compute_cost_usd + read_game_outcome).
    write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    write_meeting_replay(tmp_path / "replay-seed-1.jsonl", seed=1)
    loader = ReplayLoader(replay_dir=tmp_path)

    reads = _count_reads(monkeypatch)
    loader.cost_summary()

    assert reads == {
        tmp_path / "replay-seed-0.jsonl": 1,
        tmp_path / "replay-seed-1.jsonl": 1,
    }


def test_list_replays_reads_each_file_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # G-G-2: the metadata path folds its former double read into one per file.
    write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    write_sample_replay(tmp_path / "replay-seed-1.jsonl", seed=1)
    loader = ReplayLoader(replay_dir=tmp_path)

    reads = _count_reads(monkeypatch)
    loader.list_replays()

    assert reads == {
        tmp_path / "replay-seed-0.jsonl": 1,
        tmp_path / "replay-seed-1.jsonl": 1,
    }


def test_metadata_summary_is_memoized_across_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # H-H-2: a per-file (path, mtime) cache means a second listing re-parses
    # nothing while the files are unchanged.
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    loader = ReplayLoader(replay_dir=tmp_path)

    reads = _count_reads(monkeypatch)
    loader.list_replays()
    loader.list_replays()

    assert reads == {tmp_path / "replay-seed-0.jsonl": 1}  # second call cached


def test_in_place_rewrite_is_not_served_stale(tmp_path: Path) -> None:
    # H-H-2: an in-place refresh (same path, new bytes, new mtime) must miss both
    # the metadata-summary cache and the engine-playback cache.
    path = tmp_path / "replay-seed-0.jsonl"
    write_sample_replay(path, seed=0, ticks=3)
    loader = ReplayLoader(replay_dir=tmp_path)

    assert loader.list_replays()[0].total_ticks == 3
    assert loader.load_replay("headless-seed-0").metadata.total_ticks == 3

    # Rewrite the same path with a longer game (ReplayLog refuses to overwrite,
    # so remove first), then bump mtime to guarantee a new cache key regardless
    # of filesystem timestamp resolution.
    path.unlink()
    write_sample_replay(path, seed=0, ticks=5)
    _bump_mtime(path)

    assert loader.list_replays()[0].total_ticks == 5
    assert loader.load_replay("headless-seed-0").metadata.total_ticks == 5


def test_list_replays_pagination_bounds(tmp_path: Path) -> None:
    # G-G-3: limit/offset slice the seed-sorted path list before building views.
    for seed in range(5):
        write_sample_replay(tmp_path / f"replay-seed-{seed}.jsonl", seed=seed)
    loader = ReplayLoader(replay_dir=tmp_path)

    # Absent params preserve the original "every replay" behavior.
    assert [m.seed for m in loader.list_replays()] == [0, 1, 2, 3, 4]
    assert [m.seed for m in loader.list_replays(limit=2)] == [0, 1]
    assert [m.seed for m in loader.list_replays(offset=3)] == [3, 4]
    assert [m.seed for m in loader.list_replays(limit=2, offset=1)] == [1, 2]
    assert loader.list_replays(limit=0) == []
    assert loader.list_replays(offset=99) == []
    # A limit past the end clamps to what remains.
    assert [m.seed for m in loader.list_replays(limit=10, offset=3)] == [3, 4]


def test_list_replays_skips_corrupted_file_and_logs(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    # K-K-8 (backend half): one corrupted replay must not 500 the whole picker.
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    write_sample_replay(tmp_path / "replay-seed-2.jsonl", seed=2)
    bad = tmp_path / "replay-seed-1.jsonl"
    write_sample_replay(bad, seed=1)
    # Doubled-write corruption (duplicate ticks) — the pattern read_all_entries
    # rejects with CorruptedFileError (Task 4.16).
    bad.write_text(bad.read_text(encoding="utf-8") * 2, encoding="utf-8")
    loader = ReplayLoader(replay_dir=tmp_path)

    with caplog.at_level(logging.WARNING, logger="api.replay_loader"):
        metas = loader.list_replays()

    # Healthy replays still list; the corrupted one is excluded, not a 500.
    assert [m.seed for m in metas] == [0, 2]
    # The corruption is recorded, not silently swallowed, and names its class so
    # an operator can tell a doubled write from the other skip reasons.
    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    (message,) = [m for m in warnings if "replay-seed-1.jsonl" in m]
    assert "doubled write" in message


# -- corrupt / empty replay resilience (Task 20.4) ----------------------------
#
# The listing and the cost summary must degrade per file, not per directory: a
# truncated write, a zero-byte file and a schema-invalid row each take out only
# themselves. A DIRECT fetch of the same game id keeps failing loud, so the skip
# is degradation on the collection view and never silence on the item view.

_TRUNCATION_BYTES = 40


def _write_broken_replay_dir(tmp_path: Path) -> MeetingReplayExpectations:
    """Populate ``tmp_path`` with two healthy replays and three broken ones.

    Seeds 0 and 1 are healthy (seed 1 is the meeting fixture, the only replay
    carrying LLM cost, and its expectations are returned). Seed 2 is truncated
    mid-line — what a Ctrl-C'd or OOM-killed tournament leaves, since the runner
    writes incrementally; seed 3 is zero-byte; seed 4 carries a row whose
    ``tick`` is a string. All three are corruptions of genuine ``ReplayLog``
    output rather than hand-authored blobs, so they match what a broken run
    actually produces.
    """

    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    expected = write_meeting_replay(tmp_path / "replay-seed-1.jsonl", seed=1)

    truncated = tmp_path / "replay-seed-2.jsonl"
    write_sample_replay(truncated, seed=2)
    truncated.write_bytes(truncated.read_bytes()[:-_TRUNCATION_BYTES])

    (tmp_path / "replay-seed-3.jsonl").write_bytes(b"")

    invalid = tmp_path / "replay-seed-4.jsonl"
    write_sample_replay(invalid, seed=4)
    rows = invalid.read_text(encoding="utf-8").splitlines()
    rows[0] = json.dumps({**json.loads(rows[0]), "tick": "not-an-int"})
    invalid.write_text("\n".join(rows) + "\n", encoding="utf-8")

    return expected


def _broken_dir_client(
    replay_dir: Path, *, raise_server_exceptions: bool = True
) -> TestClient:
    test_app = create_app()
    loader = ReplayLoader(replay_dir=replay_dir)
    test_app.dependency_overrides[get_replay_loader] = lambda: loader
    return TestClient(test_app, raise_server_exceptions=raise_server_exceptions)


def test_broken_fixtures_are_broken_at_the_reader(tmp_path: Path) -> None:
    # The three fixtures must really be broken at the reader — two unreadable,
    # one yielding no entries at all — otherwise the resilience assertions below
    # would be passing against healthy files.
    _write_broken_replay_dir(tmp_path)

    with pytest.raises(ValueError):  # truncated last line -> invalid JSON
        read_all_entries(tmp_path / "replay-seed-2.jsonl")
    assert read_all_entries(tmp_path / "replay-seed-3.jsonl") == ()
    with pytest.raises(ValueError):  # "tick": "not-an-int" -> ValidationError
        read_all_entries(tmp_path / "replay-seed-4.jsonl")


def test_list_replays_survives_truncated_empty_and_invalid_files(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    # C-5: only the doubled-write shape was tolerated before; a truncated write,
    # a zero-byte file or a schema-invalid row 500'd the whole picker.
    _write_broken_replay_dir(tmp_path)
    loader = ReplayLoader(replay_dir=tmp_path)

    with caplog.at_level(logging.WARNING, logger="api.replay_loader"):
        metas = loader.list_replays()

    assert [m.seed for m in metas] == [0, 1]

    warnings = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 3  # nothing swallowed, and nothing logged twice

    def _sole_warning(filename: str) -> str:
        (message,) = [m for m in warnings if filename in m]
        return message

    # Each skipped file names its own path and its failure class.
    assert "unparseable row" in _sole_warning("replay-seed-2.jsonl")
    assert "no replay records" in _sole_warning("replay-seed-3.jsonl")
    assert "unparseable row" in _sole_warning("replay-seed-4.jsonl")


def test_cost_summary_survives_and_excludes_broken_files(tmp_path: Path) -> None:
    # The eval dashboard degrades with the picker, and the mean is a mean over
    # the games actually reduced — a skipped file must not dilute it.
    expected = _write_broken_replay_dir(tmp_path)
    loader = ReplayLoader(replay_dir=tmp_path)

    summary = loader.cost_summary()

    assert summary.total_replays == 2  # not 5
    assert summary.total_cost_usd == pytest.approx(expected.total_cost_usd)
    assert summary.max_cost_per_replay == pytest.approx(expected.total_cost_usd)
    assert summary.mean_cost_per_replay == pytest.approx(expected.total_cost_usd / 2)
    assert summary.decisive_split == {"CREWMATES": 1.0, "IMPOSTORS": 0.0}


def test_broken_replay_dir_still_serves_200_over_http(tmp_path: Path) -> None:
    # Both collection endpoints returned 500 for this directory before C-5.
    expected = _write_broken_replay_dir(tmp_path)

    with _broken_dir_client(tmp_path) as client:
        listing = client.get("/replays")
        costs = client.get("/eval/cost-summary")

    assert listing.status_code == 200
    assert [item["seed"] for item in listing.json()] == [0, 1]
    assert costs.status_code == 200
    assert costs.json()["total_replays"] == 2
    assert costs.json()["mean_cost_per_replay"] == pytest.approx(
        expected.total_cost_usd / 2
    )


def test_direct_fetch_of_a_broken_replay_still_fails_loud(tmp_path: Path) -> None:
    # The listing's skip is degradation, never silence: fetching a skipped game
    # id raises out of the loader (a 500 through the route) rather than serving a
    # half-written game — including the no-record file, which must not be
    # synthesized into a 0-tick game.
    _write_broken_replay_dir(tmp_path)
    loader = ReplayLoader(replay_dir=tmp_path)

    with pytest.raises(ValueError):
        loader.load_replay("headless-seed-2")
    with pytest.raises(EmptyReplayError):
        loader.load_replay("headless-seed-3")
    with pytest.raises(ValueError):
        loader.load_replay("headless-seed-4")

    with _broken_dir_client(tmp_path, raise_server_exceptions=False) as client:
        assert client.get("/replays/headless-seed-1").status_code == 200
        assert client.get("/replays/headless-seed-2").status_code == 500
        assert client.get("/replays/headless-seed-3").status_code == 500


def test_blank_line_only_replay_is_never_served_as_a_zero_tick_game(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    # A file of blank lines contributes no records for the same reason a
    # zero-byte one does, and is treated identically on every path.
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    (tmp_path / "replay-seed-1.jsonl").write_text("\n\n\n", encoding="utf-8")
    loader = ReplayLoader(replay_dir=tmp_path)

    with caplog.at_level(logging.WARNING, logger="api.replay_loader"):
        metas = loader.list_replays()

    assert [m.seed for m in metas] == [0]
    assert loader.cost_summary().total_replays == 1
    assert any(
        "replay-seed-1.jsonl" in r.getMessage()
        and "no replay records" in r.getMessage()
        for r in caplog.records
    )
    with pytest.raises(EmptyReplayError):
        loader.load_replay("headless-seed-1")


# -- roster-aware loader / two-committed-set layout (Task 7.4) -----------------
#
# Hermetic, FAKE-provider only: a tiny multi-impostor game is generated in
# tmp_path and reconstructed through the loader's per-set roster mechanism. No
# real-provider spend and NO committed replays/samples/ data — Task 7.5 commits
# the real 7p/2i set; this proves the plumbing on the canonical 7p/2i + 2-task
# roster.

_MI_NUM_PLAYERS = 7
_MI_NUM_IMPOSTORS = 2
_MI_TASKS_PER_CREWMATE = 2


def _run_multi_impostor_game(replay_path: Path, *, seed: int = 0) -> None:
    """Run a hermetic 7p/2i + 2-task game on the FAKE provider into ``replay_path``.

    Mirrors the canonical Phase 7 roster (Task 7.5's committed set) so the
    loader's roster-aware re-seed is exercised against a real multi-impostor
    replay. The fake provider is deterministic and never spends.
    """

    HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=replay_path,
        num_players=_MI_NUM_PLAYERS,
        num_impostors=_MI_NUM_IMPOSTORS,
        tasks_per_crewmate=_MI_TASKS_PER_CREWMATE,
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
        scheduler=TickScheduler(max_ticks=300),
    ).run()


def _write_roster(
    directory: Path,
    *,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
) -> None:
    (directory / "roster.json").write_text(
        json.dumps(
            {
                "num_players": num_players,
                "num_impostors": num_impostors,
                "tasks_per_crewmate": tasks_per_crewmate,
            }
        ),
        encoding="utf-8",
    )


@pytest.fixture(scope="module")
def multi_impostor_replay_bytes(tmp_path_factory: pytest.TempPathFactory) -> bytes:
    """Bytes of a hermetic 7p/2i replay, generated once for the module.

    Generating the replay once and replaying its bytes into each test's tmp_path
    (with a per-test ``roster.json``) keeps the suite fast while exercising the
    same recorded multi-impostor game under several descriptors.
    """

    src = tmp_path_factory.mktemp("multi-impostor-src") / "replay-seed-0.jsonl"
    _run_multi_impostor_game(src, seed=0)
    return src.read_bytes()


def test_multi_impostor_replay_reconstructs_with_matching_roster(
    tmp_path: Path, multi_impostor_replay_bytes: bytes
) -> None:
    # (a) A descriptor naming the recorded roster re-seeds 2 impostors + 2
    # tasks/crewmate, so engine playback reconstructs byte-identically (every
    # per-tick state_hash matches; no ReplayStateMismatchError).
    (tmp_path / "replay-seed-0.jsonl").write_bytes(multi_impostor_replay_bytes)
    _write_roster(tmp_path, num_players=7, num_impostors=2, tasks_per_crewmate=2)
    loader = ReplayLoader(replay_dir=tmp_path)

    replay = loader.load_replay("headless-seed-0")
    assert {p.agent_id for p in replay.players} == {f"p-{n}" for n in range(1, 8)}
    # The descriptor's num_impostors took effect — the flat default (1) would
    # have mismatched on tick 0.
    assert sum(1 for p in replay.players if p.role == "IMPOSTOR") == 2


# A hermetic 7p/2i seed that still resolves a meeting under the round-start
# cooldown (DESIGN.md §3.4). Seed 0 (used by ``multi_impostor_replay_bytes``
# above, which only needs roster reconstruction) now ends as a crew task-win with
# no meeting once the opening kill is cooldown-delayed, so the memory-walk test
# uses its own meeting-bearing seed instead of the shared fixture.
_MI_MEETING_SEED = 1


def test_serving_a_disposition_bearing_recording_changes_no_label(
    tmp_path: Path,
) -> None:
    """End-to-end: the recorded field and the event derivation serve one timeline.

    The recorder now stamps ``action_dispositions`` on every tick row. Serving
    the same game with the key stripped — the shape all 300 committed replays
    carry — must produce a byte-identical tick timeline, which is what keeps
    every committed spectator number pinned across the migration.
    """

    with_field = tmp_path / "with-field"
    without_field = tmp_path / "without-field"
    with_field.mkdir()
    without_field.mkdir()
    recorded = with_field / f"replay-seed-{_MI_MEETING_SEED}.jsonl"
    _run_multi_impostor_game(recorded, seed=_MI_MEETING_SEED)
    for directory in (with_field, without_field):
        _write_roster(directory, num_players=7, num_impostors=2, tasks_per_crewmate=2)

    lines = recorded.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines]
    assert any(
        "discarded_by_meeting" in row.get("action_dispositions", [])
        for row in rows
        if row["kind"] == "tick"
    ), "the fixture must exercise the class the field exists to record"
    (without_field / recorded.name).write_text(
        "\n".join(
            _stable_json({k: v for k, v in row.items() if k != "action_dispositions"})
            for row in rows
        )
        + "\n",
        encoding="utf-8",
    )

    game_id = f"headless-seed-{_MI_MEETING_SEED}"
    served = ReplayLoader(replay_dir=with_field).load_replay(game_id)
    derived = ReplayLoader(replay_dir=without_field).load_replay(game_id)

    assert [tick.model_dump() for tick in served.ticks] == [
        tick.model_dump() for tick in derived.ticks
    ]


def test_a_doctored_disposition_tuple_is_refused_before_it_is_served(
    tmp_path: Path,
) -> None:
    """The served tuple is verified against the walk that just produced it.

    The state hash cannot vouch for a disposition — a discarded action was
    never applied, so a row that relabels one ``applied`` still reconstructs
    byte-identically while moving that agent's served ``current_action`` off
    ``BLOCKED``. The loader re-derives and refuses.
    """

    doctored_dir = tmp_path / "doctored"
    doctored_dir.mkdir()
    recorded = doctored_dir / f"replay-seed-{_MI_MEETING_SEED}.jsonl"
    _run_multi_impostor_game(recorded, seed=_MI_MEETING_SEED)
    _write_roster(doctored_dir, num_players=7, num_impostors=2, tasks_per_crewmate=2)

    rows = [
        json.loads(line) for line in recorded.read_text(encoding="utf-8").splitlines()
    ]
    doctored_tick: int | None = None
    for row in rows:
        if row["kind"] != "tick":
            continue
        if "discarded_by_meeting" not in row.get("action_dispositions", []):
            continue
        doctored_tick = row["tick"]
        row["action_dispositions"] = [
            "applied" if value == "discarded_by_meeting" else value
            for value in row["action_dispositions"]
        ]
        break
    assert doctored_tick is not None, "the fixture must carry a discarded action"
    recorded.write_text(
        "\n".join(_stable_json(row) for row in rows) + "\n", encoding="utf-8"
    )

    with pytest.raises(ReplayDispositionMismatchError) as excinfo:
        ReplayLoader(replay_dir=doctored_dir).load_replay(
            f"headless-seed-{_MI_MEETING_SEED}"
        )

    assert excinfo.value.tick == doctored_tick
    assert "discarded_by_meeting" in excinfo.value.actual
    assert "discarded_by_meeting" not in excinfo.value.expected
    # The app-level handler that turns a divergent reconstruction into a
    # 500-with-tick covers this kind too.
    assert isinstance(excinfo.value, ReplayStateMismatchError)


def test_the_served_ballot_schema_publishes_every_field_in_both_modes() -> None:
    """The OpenAPI component a generated client reads keeps the ballot contract.

    ``VoteBallot`` carries a custom ``model_serializer``, which collapses the
    SERIALIZATION-mode schema — the one FastAPI publishes — to a bare object
    unless the model strips the serializer from the core schema it hands the
    generator. Reverting that hook drops every property here.
    """

    component = create_app().openapi()["components"]["schemas"]["VoteBallot"]

    assert set(component["properties"]) == set(VoteBallot.model_fields)
    assert component.get("additionalProperties") is not True
    for field in ("guard_redirected_from", "guard_rewrite_reason", "target", "voter"):
        assert field in component["properties"]


def test_multi_impostor_memory_walk_holds_firewall(tmp_path: Path) -> None:
    # The multi-impostor reconstruction also drives the collect_memory walk:
    # get_meeting_memory rebuilds every per-tick packet through ObservationService,
    # which is where 7.2's impostor-only fellow_impostor_ids is populated. Confirm
    # that rebuild path is reachable on multi-impostor data and an impostor's
    # memory resolves (the crew-empty invariant itself is guarded by 7.2's leak
    # property sweep over the same service).
    game_id = f"headless-seed-{_MI_MEETING_SEED}"
    _run_multi_impostor_game(
        tmp_path / f"replay-seed-{_MI_MEETING_SEED}.jsonl", seed=_MI_MEETING_SEED
    )
    _write_roster(tmp_path, num_players=7, num_impostors=2, tasks_per_crewmate=2)
    loader = ReplayLoader(replay_dir=tmp_path)

    replay = loader.load_replay(game_id)
    assert replay.meetings  # the hermetic 7p/2i game resolves a meeting
    meeting_id = replay.meetings[0].meeting_id
    impostor = next(p.agent_id for p in replay.players if p.role == "IMPOSTOR")
    memory = loader.get_meeting_memory(game_id, meeting_id, impostor)
    assert memory.agent_id == impostor
    assert memory.role == "IMPOSTOR"


@pytest.mark.parametrize(
    "wrong",
    [
        {"num_players": 7, "num_impostors": 1, "tasks_per_crewmate": 2},
        {"num_players": 7, "num_impostors": 2, "tasks_per_crewmate": 1},
    ],
)
def test_wrong_roster_descriptor_raises_state_mismatch(
    tmp_path: Path, multi_impostor_replay_bytes: bytes, wrong: dict[str, int]
) -> None:
    # (b) The descriptor is load-bearing: naming the wrong num_impostors OR the
    # wrong tasks_per_crewmate re-seeds different roles/tasks, so the per-tick
    # state_hash check fails loud rather than serving a wrongly-reconstructed game.
    (tmp_path / "replay-seed-0.jsonl").write_bytes(multi_impostor_replay_bytes)
    _write_roster(tmp_path, **wrong)
    loader = ReplayLoader(replay_dir=tmp_path)

    with pytest.raises(ReplayStateMismatchError):
        loader.load_replay("headless-seed-0")


def test_multi_impostor_replay_without_descriptor_fails_loud(
    tmp_path: Path, multi_impostor_replay_bytes: bytes
) -> None:
    # A multi-impostor replay placed in a flat dir with NO roster.json defaults to
    # 4p/1i and therefore cannot reconstruct — it fails loud rather than silently
    # re-seeding the wrong roster. This is precisely why the descriptor exists.
    (tmp_path / "replay-seed-0.jsonl").write_bytes(multi_impostor_replay_bytes)
    loader = ReplayLoader(replay_dir=tmp_path)

    with pytest.raises(ReplayStateMismatchError):
        loader.load_replay("headless-seed-0")


def test_flat_directory_without_descriptor_defaults_to_4p1i(tmp_path: Path) -> None:
    # (c) A flat dir with no roster.json keeps the MVP 4p/1i default verbatim: a
    # genuine 4p/1i replay reconstructs byte-identically (1 impostor, 4 players),
    # exactly as before Task 7.4 — the committed-baseline path is unchanged.
    write_sample_replay(tmp_path / "replay-seed-0.jsonl", seed=0, ticks=3)
    loader = ReplayLoader(replay_dir=tmp_path)

    replay = loader.load_replay("headless-seed-0")
    assert {p.agent_id for p in replay.players} == {f"p-{n}" for n in range(1, 5)}
    assert sum(1 for p in replay.players if p.role == "IMPOSTOR") == 1


def test_load_roster_config_absent_returns_none(tmp_path: Path) -> None:
    # The ONLY defaulting path: no descriptor present -> None -> 4p/1i re-seed.
    assert replay_loader._load_roster_config(tmp_path) is None


def test_load_roster_config_parses_valid_descriptor(tmp_path: Path) -> None:
    _write_roster(tmp_path, num_players=7, num_impostors=2, tasks_per_crewmate=2)
    assert replay_loader._load_roster_config(tmp_path) == RosterConfig(
        num_players=7, num_impostors=2, tasks_per_crewmate=2
    )


@pytest.mark.parametrize(
    "payload",
    [
        '{"num_players": 7, "num_impostors": 2}',  # missing tasks_per_crewmate
        # unexpected key
        '{"num_players": 7, "num_impostors": 2, "tasks_per_crewmate": 2, "x": 1}',
        '{"num_players": "7", "num_impostors": 2, "tasks_per_crewmate": 2}',  # type
        '{"num_players": 7.0, "num_impostors": 2, "tasks_per_crewmate": 2}',  # float
        '{"num_players": 7, "num_impostors": 0, "tasks_per_crewmate": 2}',  # non-positive
        '{"num_players": 7, "num_impostors": true, "tasks_per_crewmate": 2}',  # bool
        "[7, 2, 2]",  # not a JSON object
        "not valid json",  # malformed JSON
    ],
)
def test_load_roster_config_malformed_fails_loud(tmp_path: Path, payload: str) -> None:
    # A present-but-malformed descriptor raises rather than falling back to the
    # 4p/1i default (AGENTS.md "no silent fallbacks").
    (tmp_path / "roster.json").write_text(payload, encoding="utf-8")
    with pytest.raises(ValueError):
        replay_loader._load_roster_config(tmp_path)


def test_load_roster_config_non_file_is_malformed(tmp_path: Path) -> None:
    # A roster.json that exists but is NOT a regular file (e.g. a directory from a
    # bad checkout) is present-but-malformed: fail loud, don't silently default to
    # 4p/1i.
    (tmp_path / "roster.json").mkdir()
    with pytest.raises(ValueError):
        replay_loader._load_roster_config(tmp_path)


def test_roster_descriptor_added_after_construction_is_picked_up(
    tmp_path: Path, multi_impostor_replay_bytes: bytes
) -> None:
    # The roster is read per-walk (not cached at construction): adding the correct
    # descriptor to an already-constructed loader lets a multi-impostor set
    # reconstruct without re-creating the loader.
    (tmp_path / "replay-seed-0.jsonl").write_bytes(multi_impostor_replay_bytes)
    loader = ReplayLoader(replay_dir=tmp_path)
    # No descriptor yet -> flat 4p/1i default -> the 7p/2i replay can't reconstruct.
    with pytest.raises(ReplayStateMismatchError):
        loader.load_replay("headless-seed-0")

    _write_roster(tmp_path, num_players=7, num_impostors=2, tasks_per_crewmate=2)

    replay = loader.load_replay("headless-seed-0")
    assert sum(1 for p in replay.players if p.role == "IMPOSTOR") == 2


def test_roster_descriptor_change_in_place_is_not_served_stale(
    tmp_path: Path, multi_impostor_replay_bytes: bytes
) -> None:
    # H-H-2 parity for the sidecar: the roster.json mtime is folded into the
    # reconstruction cache key, so an in-place descriptor rewrite on an
    # already-constructed loader invalidates the cached walk rather than serving
    # the stale roster. Start with the correct descriptor (cached success), then
    # rewrite it wrong in place + bump its mtime; the SAME loader must re-seed
    # with the new (wrong) roster and fail loud — not return the cached success.
    (tmp_path / "replay-seed-0.jsonl").write_bytes(multi_impostor_replay_bytes)
    _write_roster(tmp_path, num_players=7, num_impostors=2, tasks_per_crewmate=2)
    loader = ReplayLoader(replay_dir=tmp_path)

    loader.load_replay("headless-seed-0")  # caches a successful reconstruction

    # Replay file untouched; only the sidecar changes (+ mtime bump to beat coarse
    # filesystem timestamp resolution).
    _write_roster(tmp_path, num_players=7, num_impostors=1, tasks_per_crewmate=2)
    _bump_mtime(tmp_path / "roster.json")

    with pytest.raises(ReplayStateMismatchError):
        loader.load_replay("headless-seed-0")


# -- committed 9p/2i meeting-heavy set (Tasks 7.8, 8.12) ----------------------
#
# Unlike the hermetic Task 7.4 fixtures above (tmp_path, no committed data), the
# two tests below point the loader at the COMMITTED replays/samples/9p2i/ set and
# reconstruct it. This is the CI-enforced determinism gate for the committed
# multi-impostor set: check.sh runs `uv run pytest` but does NOT invoke
# scripts/verify_samples.sh, so without a pytest test the committed 9p/2i set's
# byte-identical reconstruction would be unguarded in CI. It pairs with the flat
# 4p/1i set's coverage in tests/scripts/test_verify_samples.py
# (test_clean_sample_verifies), so BOTH committed sets are CI-gated.

_COMMITTED_9P2I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)

# The Wave 0 exit-gate floor (DESIGN.md §11.4; tasks/phase-7-plan.md "Wave 0 exit
# criteria"): >= 30 RESOLVED meetings over the committed denominator. Pinned in CI
# so a future engine change can never silently drop the committed set below the
# enablement gate without failing here.
_GATE_MIN_RESOLVED_MEETINGS = 30

# The committed 9p/2i set is exactly 50 replays, seeds 0-49. Pinned so the
# reconstruction gate below verifies the WHOLE set rather than just "enough" of
# it: a deleted seed shrinks the on-disk glob, and a corrupted one is silently
# dropped by list_replays() (CorruptedFileError -> WARNING), either of which
# would otherwise still clear the >=30 meeting floor while leaving committed
# seeds un-reconstructed.
_COMMITTED_9P2I_SEED_COUNT = 50


def _committed_9p2i_seeds() -> list[int]:
    return sorted(
        int(p.stem.rsplit("-", 1)[1])
        for p in _COMMITTED_9P2I_DIR.glob("replay-seed-*.jsonl")
    )


def test_committed_9p2i_set_reconstructs_byte_identically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Every committed 9p/2i replay reconstructs byte-identically under the current
    # engine: load_replay re-seeds from the committed roster.json (9p/2i + 2
    # tasks/crewmate) and raises ReplayStateMismatchError on ANY per-tick
    # state_hash drift. num_impostors / tasks_per_crewmate are not recoverable from
    # the action stream, so this only reconstructs because the committed descriptor
    # is correct — making this both the determinism gate and a roster.json check.
    #
    # The committed set was re-recorded on the Featherless / Qwen/Qwen3-32B
    # substrate (Task 14.12 baseline 2) with all four Phase-13.5 levers ON PLUS
    # the Task-14.10 evidence_quality_lift lever ON, stamped on each game_over
    # record. Every lever is unconditional (the 13.5 four since Task 14.9, the
    # 14.10 lever since the 14.12 close follow-up), so the committed set
    # reconstructs under a genuinely BARE environment — no AILIBI_* export.
    _delete_ailibi_env(monkeypatch)
    assert replay_loader._load_roster_config(_COMMITTED_9P2I_DIR) == RosterConfig(
        num_players=9, num_impostors=2, tasks_per_crewmate=2
    )
    # Pin the committed shape BEFORE the load loop. The meeting floor below is a
    # count of resolved meetings, NOT a count of replays — reusing it as the
    # replay-count check let a thinned/corrupted checkout pass: list_replays()
    # silently skips a corrupted file and the glob misses a deleted one, so as
    # long as >=30 readable files remained, the loop would never reconstruct the
    # missing seeds despite this test's contract that EVERY committed replay does.
    expected_seeds = list(range(_COMMITTED_9P2I_SEED_COUNT))
    assert _committed_9p2i_seeds() == expected_seeds  # no deleted seed on disk

    loader = ReplayLoader(replay_dir=_COMMITTED_9P2I_DIR)
    metas = loader.list_replays()
    # A corrupted file is dropped from the listing, so an exact-count match (not a
    # floor) is what proves the whole committed set is readable before we load it.
    assert len(metas) == _COMMITTED_9P2I_SEED_COUNT

    resolved_meetings = 0
    for meta in metas:
        replay = loader.load_replay(meta.game_id)  # raises on determinism drift
        assert {p.agent_id for p in replay.players} == {f"p-{n}" for n in range(1, 10)}
        assert sum(1 for p in replay.players if p.role == "IMPOSTOR") == 2
        resolved_meetings += len(replay.meetings)

    # The whole point of the meeting-heavy set: the Stage-A enablement gate's
    # resolved-meeting floor is committed and CI-enforced, not just asserted once
    # at generation time.
    assert resolved_meetings >= _GATE_MIN_RESOLVED_MEETINGS


def test_committed_9p2i_set_holds_crew_firewall(tmp_path: Path) -> None:
    # End-to-end firewall coverage (7.2's crew-empty invariant) on the REAL
    # committed multi-impostor roster — the coverage the 7.2 contract defers to
    # this task. The single-impostor 4p/1i fixtures cannot surface a crew-tuple
    # misroute (every fellow_impostor_ids is () there regardless), so this re-seeds
    # each committed seed at the recorded roster and confirms ObservationService
    # gives every crewmate-recipient an empty fellow_impostor_ids while each
    # impostor sees exactly the OTHER impostor (self excluded). The invariant is a
    # pure function of roles, so the seeded initial state exercises it directly.
    roster = replay_loader._load_roster_config(_COMMITTED_9P2I_DIR)
    assert roster is not None
    game_map = load_canonical_map()
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )
    seeds = _committed_9p2i_seeds()
    assert seeds  # the committed set is non-empty
    for seed in seeds:
        state = seed_initial_state(
            seed=seed,
            game_map=game_map,
            num_players=roster.num_players,
            num_impostors=roster.num_impostors,
            tasks_per_crewmate=roster.tasks_per_crewmate,
        )
        impostor_ids = {pid for pid, p in state.players.items() if p.role == "IMPOSTOR"}
        assert len(impostor_ids) == roster.num_impostors
        for pid in state.players:
            packet = service.build_packet(
                world_state=state, agent_id=pid, engine_events=()
            )
            if state.players[pid].role == "CREWMATE":
                assert packet.self_state.fellow_impostor_ids == ()
            else:
                assert set(packet.self_state.fellow_impostor_ids) == impostor_ids - {
                    pid
                }


# -- Task 14.7: the loader HONORS the stamped substrate-flag config -----------
#
# A re-record stamps its substrate-lever config onto the game_over record. The
# loader's memory reconstruction re-derives under the active substrate (the
# four Phase-13.5 levers unconditionally ON since Task 14.9 — no env reads), so
# it refuses to reconstruct a replay stamped with a DIFFERENT lever config (no
# silent cross-substrate replay); with the gates retired that means a legacy
# stamp recording a lever OFF. An unstamped (legacy) replay is never checked,
# so the committed final-9B baseline reconstructs unchanged. NO env vars are
# needed anywhere — the committed flags-ON baseline serves under a BARE
# environment (the Task-14.9 acceptance bar).

# Built from the live substrate snapshot so the fully-ON stamp tracks exactly the
# lever set the loader's guard compares against and can never drift again. Task
# 15.7 GRADUATED reporter_exculpation to always-on, so the snapshot is now SIX
# keys (testimony_as_content, witnessed_kill_evidence, movement_perception,
# unfreeze_memory, evidence_quality_lift, reporter_exculpation), all True — every
# lever is unconditional, so the ambient snapshot IS the fully-ON stamp.
_ALL_FLAGS_ON = dict(substrate_flag_snapshot())
# A legacy stamp this build can no longer reproduce: the movement lever
# recorded OFF (its OFF derivation was deleted by Task 14.9).
_LEGACY_MOVEMENT_OFF = {**_ALL_FLAGS_ON, "movement_perception": False}
# A legacy stamp recording the (now unconditional) evidence_quality_lift OFF —
# equally unreproducible on this build (retired at the 14.12 close).
_LEGACY_EVIDENCE_QUALITY_LIFT_OFF = {**_ALL_FLAGS_ON, "evidence_quality_lift": False}


def _delete_ailibi_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip every ``AILIBI_*`` var so the test runs under a genuinely bare env."""

    for var in list(os.environ):
        if var.startswith("AILIBI_"):
            monkeypatch.delenv(var, raising=False)


def test_assert_substrate_matches_skips_unstamped_replay() -> None:
    # An unstamped game_over (the committed final-9B baseline) is never checked.
    entries = [
        GameEndReplayEntry(game_id="g", tick=1, winner="CREWMATES", reason="TASKS")
    ]
    replay_loader._assert_substrate_matches("g", entries)  # no raise


def test_assert_substrate_matches_passes_for_all_on_stamp_under_bare_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The committed baseline's all-ON stamp matches the unconditional substrate
    # with NO env vars set — reconstruction needs no AILIBI_* export.
    _delete_ailibi_env(monkeypatch)
    entries = [
        GameEndReplayEntry(
            game_id="g",
            tick=1,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags=_ALL_FLAGS_ON,
        )
    ]
    replay_loader._assert_substrate_matches("g", entries)  # no raise


def test_assert_substrate_matches_raises_on_legacy_off_stamp() -> None:
    # A legacy stamp recording a lever OFF names the divergent lever and the
    # Task-14.9 retirement (there is no env remediation any more — the OFF
    # derivation no longer exists in this build).
    entries = [
        GameEndReplayEntry(
            game_id="g",
            tick=1,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags=_LEGACY_MOVEMENT_OFF,
        )
    ]
    with pytest.raises(ReplaySubstrateMismatchError) as excinfo:
        replay_loader._assert_substrate_matches("g", entries)
    message = str(excinfo.value)
    assert "movement_perception" in message
    assert "14.9" in message
    assert "AILIBI_" not in message


def test_assert_substrate_matches_raises_on_legacy_evidence_quality_lift_off_stamp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Task 14.12 close: the evidence_quality_lift lever is now RETIRED to
    # unconditional (like the four 13.5 levers), so a legacy stamp recording it
    # OFF is a cross-substrate replay this build cannot reproduce. It fails loud,
    # names the lever and the retirement, and offers NO env remediation (the OFF
    # derivation no longer exists) — the same mode as the retired 13.5 levers.
    _delete_ailibi_env(monkeypatch)
    entries = [
        GameEndReplayEntry(
            game_id="g",
            tick=1,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags=_LEGACY_EVIDENCE_QUALITY_LIFT_OFF,
        )
    ]
    with pytest.raises(ReplaySubstrateMismatchError) as excinfo:
        replay_loader._assert_substrate_matches("g", entries)
    message = str(excinfo.value)
    assert "evidence_quality_lift" in message
    assert "Retired" in message
    assert "14.12" in message


def _stamp_committed_9p2i_seed(dst: Path, seed: int, flags: dict[str, bool]) -> str:
    """Copy a committed 9p2i replay into ``dst`` with ``flags`` stamped on its
    game_over record (tick/meeting bytes verbatim, so the state_hash chain is
    unchanged). Returns the replay's game_id."""

    dst.mkdir(parents=True, exist_ok=True)
    (dst / "roster.json").write_text(
        (_COMMITTED_9P2I_DIR / "roster.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    src = _COMMITTED_9P2I_DIR / f"replay-seed-{seed}.jsonl"
    out: list[str] = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("kind") == "game_over":
            record["substrate_flags"] = flags
            line = json.dumps(record, sort_keys=True, separators=(",", ":"))
        out.append(line)
    (dst / f"replay-seed-{seed}.jsonl").write_text(
        "\n".join(out) + "\n", encoding="utf-8"
    )
    return f"headless-seed-{seed}"


def test_stamped_replay_reconstructs_under_bare_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An all-ON recording reconstructs with NO env vars set: the stamp matches
    # the unconditional substrate. The state hash is substrate-independent, so
    # the tick/meeting bytes (verbatim) still reconstruct.
    game_id = _stamp_committed_9p2i_seed(tmp_path, 0, dict(_ALL_FLAGS_ON))
    _delete_ailibi_env(monkeypatch)
    loader = ReplayLoader(replay_dir=tmp_path)
    replay = loader.load_replay(game_id)  # no raise — reconstructs
    assert {p.agent_id for p in replay.players} == {f"p-{n}" for n in range(1, 10)}


def test_committed_baseline_serves_under_bare_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Pins the Task-14.9 spectator fix (the ``run_spectator.sh`` 500 reported
    # 2026-07-01), now covering baseline 2: the committed 9p2i baseline is stamped
    # all-ON (the four 13.5 levers + the Task-14.10 evidence_quality_lift lever),
    # and the launcher exports no AILIBI_* vars. Every one of those levers is
    # unconditional (the 13.5 four since 14.9, the 14.10 lever since the 14.12
    # close follow-up), so the loader serves the committed set under a genuinely
    # bare environment.
    if not _COMMITTED_9P2I_DIR.is_dir():
        pytest.skip("committed 9p2i sample set not present")
    _delete_ailibi_env(monkeypatch)
    loader = ReplayLoader(replay_dir=_COMMITTED_9P2I_DIR)
    replay = loader.load_replay("headless-seed-0")  # no raise — serves bare
    assert {p.agent_id for p in replay.players} == {f"p-{n}" for n in range(1, 10)}


def test_legacy_off_stamped_replay_fails_loud(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A recording stamped with a lever OFF (a pre-14.9 flag-OFF/ablation
    # artifact) fails loud — this build's unconditional substrate cannot
    # faithfully re-derive it (no silent cross-substrate replay).
    game_id = _stamp_committed_9p2i_seed(tmp_path, 0, dict(_LEGACY_MOVEMENT_OFF))
    _delete_ailibi_env(monkeypatch)
    loader = ReplayLoader(replay_dir=tmp_path)
    with pytest.raises(ReplaySubstrateMismatchError):
        loader.load_replay(game_id)


# -- Task 14.8: the ANALYSIS-ONLY substrate-mismatch override ------------------
#
# The 14.8 per-lever ablation deliberately re-derived the stamped all-ON
# baseline under toggled levers, which the Task-14.7 guard otherwise
# (correctly) refuses. ``allow_substrate_mismatch`` (default OFF) remains the
# explicit opt-in for reconstructing a mismatch-stamped replay — since Task
# 14.9 that means a legacy stamp recording a lever OFF (the OFF derivation
# itself no longer exists, so the override reconstructs it under the
# unconditional all-ON substrate, logged, never silent). The former
# env-flip-between-loads cache test is DELETED with rationale: with the four
# gates retired the ambient snapshot is constant, so no env flip can change the
# derivation; the ``_substrate_cache_key`` machinery stays for the next
# toggleable lever (14.10) to exercise.


def test_assert_substrate_matches_default_still_raises_on_mismatch() -> None:
    # The override's DEFAULT position changes nothing: a mismatch-stamped
    # replay still fails loud (the Task-14.7 guard behavior).
    entries = [
        GameEndReplayEntry(
            game_id="g",
            tick=1,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags=_LEGACY_MOVEMENT_OFF,
        )
    ]
    with pytest.raises(ReplaySubstrateMismatchError):
        replay_loader._assert_substrate_matches(
            "g", entries, allow_substrate_mismatch=False
        )


def test_assert_substrate_matches_override_permits_deliberate_mismatch(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # ``allow_substrate_mismatch=True`` permits the deliberate re-derivation an
    # analysis pass needs — and is logged at WARNING, never silent.
    entries = [
        GameEndReplayEntry(
            game_id="g",
            tick=1,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags=_LEGACY_MOVEMENT_OFF,
        )
    ]
    with caplog.at_level(logging.WARNING, logger="api.replay_loader"):
        replay_loader._assert_substrate_matches(
            "g", entries, allow_substrate_mismatch=True
        )  # no raise
    assert any("Deliberate substrate mismatch" in rec.message for rec in caplog.records)


def test_loader_override_reconstructs_legacy_off_stamped_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The analysis entry: a legacy OFF-stamped recording reconstructs when (and
    # only when) the loader is constructed with the analysis-only override. The
    # per-tick state hash is substrate-independent, so the walk still verifies;
    # the memory re-derivation runs under the unconditional all-ON substrate.
    game_id = _stamp_committed_9p2i_seed(tmp_path, 0, dict(_LEGACY_MOVEMENT_OFF))
    _delete_ailibi_env(monkeypatch)
    loader = ReplayLoader(replay_dir=tmp_path, allow_substrate_mismatch=True)
    replay = loader.load_replay(game_id)  # no raise — deliberate mismatch
    assert {p.agent_id for p in replay.players} == {f"p-{n}" for n in range(1, 10)}


def test_loader_default_still_refuses_mismatch_after_override_landed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The default-constructed loader (the serving/verify path) is unchanged by
    # the 14.8 override: an OFF-stamped recording is still refused loud.
    game_id = _stamp_committed_9p2i_seed(tmp_path, 0, dict(_LEGACY_MOVEMENT_OFF))
    _delete_ailibi_env(monkeypatch)
    loader = ReplayLoader(replay_dir=tmp_path)
    with pytest.raises(ReplaySubstrateMismatchError):
        loader.load_replay(game_id)


def test_override_loader_is_silent_when_substrate_matches_stamp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # The override only PERMITS a mismatch — it does not manufacture one. For
    # an all-ON stamp (matching the unconditional substrate) the guard passes
    # normally and NO deliberate-mismatch warning is emitted (the WARNING is
    # scoped to an actual mismatch).
    game_id = _stamp_committed_9p2i_seed(tmp_path, 0, dict(_ALL_FLAGS_ON))
    _delete_ailibi_env(monkeypatch)
    loader = ReplayLoader(replay_dir=tmp_path, allow_substrate_mismatch=True)
    with caplog.at_level(logging.WARNING, logger="api.replay_loader"):
        loader.load_replay(game_id)  # no raise
    assert not any(
        "Deliberate substrate mismatch" in rec.message for rec in caplog.records
    )


# -- current_action fidelity: the recorded intent, never an inherited label ----
#
# ``current_action`` used to be read off the actor's ``last_action`` — the last
# action the engine ACCEPTED — so a rejected or never-attempted intent left the
# previous tick's label standing, and four whole classes of behaviour rendered as
# something they were not. The tests below pin the replacement: the label is a
# function of THIS tick's recorded intent and its outcome
# (``api.replay_loader._current_action``).


def _fidelity_state() -> WorldState:
    """A minimal PLAY state in ADMIN: one impostor, two crewmates, one body.

    ``p-2`` owns the only task instance, so ``p-3`` (the impostor) submitting
    ``do_task`` for that map task is exactly the fake task the engine rejects and
    a co-located crewmate witnesses as work.
    """

    def player(
        pid: str,
        role: Literal["CREWMATE", "IMPOSTOR"],
        position: tuple[float, float],
    ) -> PlayerState:
        return PlayerState(
            id=pid,
            role=role,
            alive=True,
            room="ADMIN",
            position=position,
            last_action=None,
            in_vent=False,
        )

    return WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players={
            "p-1": player("p-1", "CREWMATE", (0.0, 0.0)),
            "p-2": player("p-2", "CREWMATE", (1.0, 0.0)),
            "p-3": player("p-3", "IMPOSTOR", (2.0, 0.0)),
        },
        bodies={
            "body-p-9-0": BodyState(
                id="body-p-9-0",
                player_id="p-9",
                room="ADMIN",
                position=(3.0, 0.0),
                killed_by="p-3",
                discovered_by=None,
            )
        },
        tasks={
            "p-2:swipe_card": TaskState(
                id="p-2:swipe_card",
                owner="p-2",
                map_task_id="swipe_card",
                room="ADMIN",
                progress=0,
                required_ticks=1,
                completed=False,
            )
        },
        sabotage=None,
        cooldowns={"p-3": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
    )


def _label_from_last_action(last_action: Action | None) -> str:
    """The derivation this task replaced: the label read off ``last_action``.

    Reproduced here — and nowhere in production — so the gate can prove it bites.
    If the projection is ever reverted to reading the last ACCEPTED action, the
    assertion comparing the two derivations fails instead of passing silently.
    """

    if last_action is None:
        return "IDLE"
    return {
        "move": "MOVING",
        "do_task": "TASK",
        "kill": "KILL",
        "vent": "VENT",
        "report": "REPORT",
        "emergency": "REPORT",
        "sabotage": "SABOTAGE",
        "repair_sabotage": "TASK",
    }.get(last_action.type, "IDLE")


def test_impostor_fake_task_reads_pretend_task_not_the_stale_label() -> None:
    game_map = load_canonical_map()
    # Tick 1: the impostor moves (to its own room, which the engine accepts), so
    # its ``last_action`` is a move when the bluff lands on the next tick.
    moved, _ = advance_tick(
        _fidelity_state(),
        replay_loader._deserialize_actions(
            [{"type": "move", "actor": "p-3", "payload": {"to_room": "ADMIN"}}]
        ),
        game_map=game_map,
    )
    assert moved.players["p-3"].last_action is not None

    # Tick 2: the impostor submits ``do_task``. It owns no instance of the map
    # task, so the engine rejects it and never updates ``last_action``.
    fake_task = replay_loader._deserialize_actions(
        [{"type": "do_task", "actor": "p-3", "payload": {"task_id": "swipe_card"}}]
    )
    after, events = advance_tick(moved, fake_task, game_map=game_map)
    assert any(
        isinstance(event, ActionRejectedEvent) and event.actor == "p-3"
        for event in events
    )

    intents = replay_loader._tick_intents(fake_task, events)
    assert replay_loader._current_action(intents, "p-3", "IMPOSTOR") == "PRETEND_TASK"

    # The gate bites: the label the replaced derivation produces here is a
    # DIFFERENT one, so reverting the projection fails this test.
    stale = _label_from_last_action(after.players["p-3"].last_action)
    assert stale == "MOVING"
    assert stale != replay_loader._current_action(intents, "p-3", "IMPOSTOR")


def test_meeting_freezes_later_intents_into_blocked() -> None:
    # ``advance_tick`` returns the moment a handler flips the phase to MEETING,
    # so every action positioned after the trigger's was never attempted. Those
    # agents did not idle and did not move — the tick foreclosed them.
    game_map = load_canonical_map()
    actions = replay_loader._deserialize_actions(
        [
            {"type": "move", "actor": "p-1", "payload": {"to_room": "ADMIN"}},
            {"type": "report", "actor": "p-2", "payload": {"body_id": "body-p-9-0"}},
            {"type": "do_task", "actor": "p-3", "payload": {"task_id": "swipe_card"}},
        ]
    )
    state, events = advance_tick(_fidelity_state(), actions, game_map=game_map)
    assert state.phase == "MEETING"

    intents = replay_loader._tick_intents(actions, events)
    # Before the trigger: judged on its merits.
    assert replay_loader._current_action(intents, "p-1", "CREWMATE") == "MOVING"
    # The trigger itself.
    assert replay_loader._current_action(intents, "p-2", "CREWMATE") == "REPORT"
    # After it: never attempted. BLOCKED outranks PRETEND_TASK — the impostor's
    # fake task did not happen at all on this tick.
    assert replay_loader._current_action(intents, "p-3", "IMPOSTOR") == "BLOCKED"


def test_recorded_dispositions_and_the_event_derivation_agree() -> None:
    """The migration is a no-op on behaviour: both paths build one ``_TickIntents``.

    ``_tick_intents`` prefers the row's recorded ``action_dispositions`` and
    falls back to re-deriving the cutoff from the ``MeetingTriggered`` event,
    so the served ``CurrentAction`` labels are the same either way — which is
    what lets every committed cell stay pinned across the change.
    """

    game_map = load_canonical_map()
    actions = replay_loader._deserialize_actions(
        [
            {"type": "move", "actor": "p-1", "payload": {"to_room": "ADMIN"}},
            {"type": "report", "actor": "p-2", "payload": {"body_id": "body-p-9-0"}},
            {"type": "do_task", "actor": "p-3", "payload": {"task_id": "swipe_card"}},
        ]
    )
    state, events = advance_tick(_fidelity_state(), actions, game_map=game_map)
    assert state.phase == "MEETING"
    recorded = classify_action_dispositions(actions, events)
    assert "discarded_by_meeting" in recorded

    derived = replay_loader._tick_intents(actions, events)
    read_off = replay_loader._tick_intents(actions, events, recorded)

    assert read_off == derived
    assert read_off.preempted == frozenset({"p-3"})

    # The gate bites: a row claiming nothing was discarded lands on a DIFFERENT
    # intents object, so the preference is real rather than decorative.
    doctored = replay_loader._tick_intents(
        actions, events, tuple("applied" for _ in recorded)
    )
    assert doctored.preempted == frozenset()


def test_the_killed_victim_arm_survives_the_recorded_path() -> None:
    # The kill lands before the victim's own action is reached, so the engine
    # REFUSES that action for being dead — a rejection that says nothing about
    # what the agent tried to do. Nothing marks it `discarded_by_meeting`, so
    # the KILL arm (which reads events) is what preempts it, on both paths.
    game_map = load_canonical_map()
    actions = replay_loader._deserialize_actions(
        [
            {"type": "kill", "actor": "p-3", "payload": {"target": "p-1"}},
            {"type": "move", "actor": "p-1", "payload": {"to_room": "UPPER_HALL"}},
        ]
    )
    _state, events = advance_tick(_fidelity_state(), actions, game_map=game_map)
    recorded = classify_action_dispositions(actions, events)
    assert recorded == ("applied", "rejected")

    read_off = replay_loader._tick_intents(actions, events, recorded)
    assert read_off == replay_loader._tick_intents(actions, events)
    assert read_off.preempted == frozenset({"p-1"})


def test_the_target_rewrite_labels_are_the_five_typed_reasons() -> None:
    """The display class is DERIVED from the recorded union, not restated.

    Pinning the five keeps the contract explicit: a sixth reason added to
    ``BallotTargetRewriteReason`` reaches the finale recap automatically, and a
    citation-only label never does.
    """

    assert replay_loader._TARGET_REWRITE_LABELS == frozenset(
        {
            "parse_default",
            "invalid_target",
            "teammate_coerced",
            "under_gate_redirect",
            "uncited_coerced",
        }
    )
    assert replay_loader._TARGET_REWRITE_LABELS == frozenset(
        get_args(BallotTargetRewriteReason)
    )
    assert "invalid_reason_id" not in replay_loader._TARGET_REWRITE_LABELS
    assert "invalid_observation_id" not in replay_loader._TARGET_REWRITE_LABELS


def test_agent_with_no_recorded_intent_reads_idle() -> None:
    # The inheritance channel, closed: an agent that submitted nothing this tick
    # (a dead agent, the synthesized Start frame) has no label to carry forward,
    # however busy it was a tick ago.
    game_map = load_canonical_map()
    state, events = advance_tick(
        _fidelity_state(),
        replay_loader._deserialize_actions(
            [{"type": "move", "actor": "p-1", "payload": {"to_room": "ADMIN"}}]
        ),
        game_map=game_map,
    )
    assert _label_from_last_action(state.players["p-1"].last_action) == "MOVING"

    no_intents = replay_loader._tick_intents([], ())
    assert replay_loader._current_action(no_intents, "p-1", "CREWMATE") == "IDLE"


@dataclass(frozen=True)
class _ActionCensus:
    """Every recorded intent in a committed set, by the label it renders."""

    #: intent kind -> label -> count. Impostor ``do_task`` is counted apart from
    #: a crewmate's: it is the fake task, and it is the class that used to lie.
    by_intent: Mapping[str, Mapping[str, int]]
    #: Labels on agent-ticks where that actor submitted nothing at all.
    without_intent: Mapping[str, int]
    #: Every non-null ``visibility.visible_players[].action`` seen in the walk —
    #: the As-agent fog's OWN action channel, counted to keep it distinguishable
    #: from the omniscient label.
    fog_actions: Mapping[str, int]


@cache
def _committed_9p2i_action_census() -> _ActionCensus:
    """Fold the committed 9p2i set once, cross-referencing intents to labels.

    Re-derives nothing: it reads each replay's recorded ``actions`` rows and the
    ``current_action`` the loader projected for that actor on that tick, so the
    counts below are a property of the committed bytes and the served DTO.
    """

    loader = ReplayLoader(replay_dir=_COMMITTED_9P2I_DIR)
    by_intent: dict[str, Counter[str]] = defaultdict(Counter)
    without_intent: Counter[str] = Counter()
    fog_actions: Counter[str] = Counter()
    for meta in loader.list_replays():
        replay = loader.load_replay(meta.game_id)
        role = {player.agent_id: player.role for player in replay.players}
        labels = {
            tick.tick: {
                agent.agent_id: agent.current_action for agent in tick.agent_states
            }
            for tick in replay.ticks
        }
        for tick_view in replay.ticks:
            for agent in tick_view.agent_states:
                if agent.visibility is None:
                    continue
                for seen in agent.visibility.visible_players:
                    if seen.action is not None:
                        fog_actions[seen.action] += 1
        recorded: dict[int, dict[str, str]] = {}
        path = _COMMITTED_9P2I_DIR / f"replay-seed-{meta.seed}.jsonl"
        for entry in read_all_entries(path):
            if isinstance(entry, ReplayEntry):
                recorded[entry.tick] = {
                    str(raw["actor"]): str(raw["type"]) for raw in entry.actions
                }
        for tick, per_agent in labels.items():
            intents = recorded.get(tick, {})
            for agent_id, label in per_agent.items():
                kind = intents.get(agent_id)
                if kind is None:
                    without_intent[label] += 1
                    continue
                if kind == "do_task" and role[agent_id] == "IMPOSTOR":
                    kind = "impostor_do_task"
                by_intent[kind][label] += 1
    return _ActionCensus(
        by_intent={kind: dict(counts) for kind, counts in by_intent.items()},
        without_intent=dict(without_intent),
        fog_actions=dict(fog_actions),
    )


def test_committed_9p2i_fake_tasks_emergencies_and_repairs_are_named() -> None:
    # The A-track census (audits/review-2026-08-19/A/s2-movement-positions.md
    # §"BUG — B3") measured what the stale label cost over the committed sets;
    # these are the same three intent classes, recomputed here from the same
    # bytes under the fixed projection.
    census = _committed_9p2i_action_census()

    fake_tasks = census.by_intent["impostor_do_task"]
    assert sum(fake_tasks.values()) == 373  # was 370
    # Not one of them still renders as a stale label.
    assert fake_tasks.get("IDLE", 0) == 0
    assert fake_tasks.get("MOVING", 0) == 0
    assert fake_tasks.get("TASK", 0) == 0
    # The 8 that read BLOCKED share a tick with an earlier meeting trigger, so
    # the engine never attempted them at all.
    assert fake_tasks["PRETEND_TASK"] == 365  # was 360
    assert fake_tasks["BLOCKED"] == 8  # was 10

    # 12 emergency intents: 10 pressed the button, 2 were foreclosed or refused.
    assert census.by_intent["emergency"] == {"EMERGENCY": 10, "BLOCKED": 2}  # was 8/2
    # 38 repair intents: 26 landed.
    # was {"REPAIR": 16, "BLOCKED": 8}
    assert census.by_intent["repair_sabotage"] == {"REPAIR": 26, "BLOCKED": 12}


def test_committed_9p2i_labels_never_outlive_their_tick() -> None:
    # The structural claim, checked over 50 games: a label describes the intent
    # recorded for that actor on that tick, so it can name only an outcome that
    # intent could have — and an agent that submitted nothing reads IDLE, whatever
    # it was doing a tick earlier.
    census = _committed_9p2i_action_census()
    reachable = {
        "move": {"MOVING", "BLOCKED"},
        "do_task": {"TASK", "BLOCKED"},
        "impostor_do_task": {"PRETEND_TASK", "BLOCKED"},
        "kill": {"KILL", "BLOCKED"},
        "vent": {"VENT", "BLOCKED"},
        "report": {"REPORT", "BLOCKED"},
        "emergency": {"EMERGENCY", "BLOCKED"},
        "sabotage": {"SABOTAGE", "BLOCKED"},
        "repair_sabotage": {"REPAIR", "BLOCKED"},
        "wait": {"IDLE", "BLOCKED"},
    }
    assert set(census.by_intent) == set(reachable)
    for kind, counts in census.by_intent.items():
        assert set(counts) <= reachable[kind], kind
    assert set(census.without_intent) == {"IDLE"}


def test_fog_action_channel_keeps_its_own_vocabulary() -> None:
    # The firewall question PRETEND_TASK raises: can an As-agent perspective
    # reach it? No — the fog reads a DIFFERENT field. ``current_action`` is the
    # omniscient spectator's label for the SELECTED agent's own token, and every
    # other token under fog reads ``visibility.visible_players[].action``, whose
    # vocabulary is disjoint from it. A co-located crewmate still witnesses the
    # impostor's fake task, as ``"task"`` — which is exactly what it looks like
    # from outside, and is the point of the bluff.
    census = _committed_9p2i_action_census()
    assert set(census.fog_actions) <= {"kill", "vent", "task"}
    assert census.fog_actions["task"] > 0
    assert not set(census.fog_actions) & set(get_args(CurrentAction))


# ---------------------------------------------------------------------------
# Turn annotations: both recorded shapes, one chip vocabulary
# ---------------------------------------------------------------------------


_COMMITTED_4P1I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "4p1i"
)

# The five audit markers' static heads, derived from the loader's own table.
_TURN_MARKER_HEADS: tuple[str, ...] = tuple(
    marker.partition("{")[0] for _label, marker in _TURN_PREFIX_MARKERS
)


def _turn(free_text: str, **overrides: object) -> MeetingTurn:
    return MeetingTurn(
        turn_id="m-1:turn-0",
        turn_index=0,
        speaker="p-1",
        turn_kind="opening",
        reply_to=None,
        free_text=free_text,
        **overrides,  # type: ignore[arg-type]
    )


def test_turn_annotation_vocabulary_is_single_sourced() -> None:
    # The loader's chip labels, the meeting-layer kinds and the DTO's literal are
    # ONE vocabulary: a new kind cannot reach the wire without a label to render.
    labels = tuple(label for label, _marker in _TURN_PREFIX_MARKERS)
    assert set(labels) == set(get_args(TurnAnnotationKind))
    assert set(labels) == set(get_args(TurnAnnotationLabel))
    assert len(labels) == len(set(labels))


def test_legacy_spliced_markers_become_chips_and_leave_free_text() -> None:
    # A turn recorded before the lever: the markers sit in free_text, stacked
    # front-to-back. The loader lifts every one out as a label.
    spliced = (
        OPENING_UNSURE_DEGRADE_MARKER
        + EMERGENCY_BODY_STRIP_MARKER
        + INVALID_ACCUSATION_TARGET_MARKER.format(target="imp-2")
        + "I am not sure who did it."
    )
    view = _turn_view(_turn(spliced))

    # Labels come back in the order the markers were spliced, not table order.
    assert view.annotations == (
        "opening_degraded_unsure",
        "fabricated_opening",
        "invalid_accusation_target",
    )
    assert view.free_text == "I am not sure who did it."
    assert view.fabricated_opening is True


def test_a_marker_payload_containing_the_marker_tail_still_strips_exactly() -> None:
    # The repr-aware pattern (not a naive scan for the tail) is why a
    # hallucinated target that literally contains "dropped] " cannot swallow the
    # speaker's words.
    view = _turn_view(
        _turn(
            INVALID_ACCUSATION_TARGET_MARKER.format(target="x dropped] y")
            + "the real sentence"
        )
    )
    assert view.annotations == ("invalid_accusation_target",)
    assert view.free_text == "the real sentence"


def test_structured_annotations_become_the_same_chips() -> None:
    # The same facts recorded the new way: free_text is untouched and the labels
    # match the legacy projection above.
    view = _turn_view(
        _turn(
            "I am not sure who did it.",
            annotations=(
                TurnAnnotation(kind="opening_degraded_unsure"),
                TurnAnnotation(kind="fabricated_opening"),
                TurnAnnotation(kind="invalid_accusation_target", original="imp-2"),
            ),
        )
    )

    assert view.annotations == (
        "opening_degraded_unsure",
        "fabricated_opening",
        "invalid_accusation_target",
    )
    assert view.free_text == "I am not sure who did it."
    assert view.fabricated_opening is True


def test_a_clean_turn_carries_no_chips() -> None:
    view = _turn_view(_turn("p-3 was with me in Reactor."))
    assert view.annotations == ()
    assert view.fabricated_opening is False
    assert view.free_text == "p-3 was with me in Reactor."


def test_saw_move_observation_reaches_the_spectator() -> None:
    # The first recorded saw_move turn must render, not raise: the movement
    # shape parses unconditionally, so it can appear before its lever's record.
    view = _turn_view(
        _turn(
            "p-3 left Reactor for Admin.",
            observations=(
                SawMoveObservation(
                    type="saw_move",
                    tick=12,
                    subject="p-3",
                    from_room="REACTOR",
                    to_room="ADMIN",
                ),
            ),
        )
    )

    assert view.observations == (
        SawMoveObservationView(
            type="saw_move",
            tick=12,
            subject="p-3",
            from_room="REACTOR",
            to_room="ADMIN",
        ),
    )


def test_a_committed_meeting_line_re_serializes_byte_identically() -> None:
    # OFF-path identity at the bytes: the additive annotations field is elided
    # when empty, so a committed line round-trips through the model unchanged.
    # The perturbation below shows the comparison bites.
    path = _COMMITTED_9P2I_DIR / "replay-seed-0.jsonl"
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("kind") == "meeting"
    ]
    assert lines, "seed 0 must carry a recorded meeting"
    for line in lines:
        entry = MeetingReplayEntry.model_validate_json(line)
        assert _stable_json(entry.model_dump(mode="json")) == line

    poisoned = MeetingReplayEntry.model_validate_json(lines[0])
    turns = poisoned.transcript.turns
    poisoned = poisoned.model_copy(
        update={
            "transcript": poisoned.transcript.model_copy(
                update={
                    "turns": (
                        turns[0].model_copy(
                            update={
                                "annotations": (
                                    TurnAnnotation(kind="fabricated_opening"),
                                )
                            }
                        ),
                        *turns[1:],
                    )
                }
            )
        }
    )
    assert _stable_json(poisoned.model_dump(mode="json")) != lines[0]


def test_committed_turn_marker_census_and_zero_served_leak() -> None:
    """The committed-bytes counterfactual for the two samples sets.

    The four RATE cells (marker-bearing turns and contaminated prompts per set)
    are pinned in ``tests/eval/test_evidence_honesty.py::
    test_i8_marker_contamination_pins``; what is pinned here is the KIND split
    behind them, plus the property that matters at the wire: no raw marker
    substring survives into a served ``TurnView.free_text``. Every one of these
    turns carries a structured annotation instead once the lever is adopted.
    """

    # Baseline 6 read (971, 53, {invalid_accusation_target: 53}) and (117, 0, {}).
    # The marked count collapsed to TWO: the structured-turn-marker channel is
    # unconditional now, so the guards record annotations instead of splicing
    # prose, and the accusation guard itself fires far less on the v4 openings.
    # was (871, 1, {invalid_accusation_target: 1}) and (120, 0, {}).
    expected = {
        _COMMITTED_9P2I_DIR: (869, 2, {"invalid_accusation_target": 2}),
        _COMMITTED_4P1I_DIR: (117, 0, {}),
    }
    for directory, (
        expected_turns,
        expected_marked,
        expected_kinds,
    ) in expected.items():
        turns = marked = 0
        kinds: Counter[str] = Counter()
        for path in sorted(directory.glob("replay-seed-*.jsonl")):
            for entry in read_all_entries(path):
                if not isinstance(entry, MeetingReplayEntry):
                    continue
                for turn in entry.transcript.turns:
                    turns += 1
                    view = _turn_view(turn)
                    if view.annotations:
                        marked += 1
                    kinds.update(view.annotations)
                    for head in _TURN_MARKER_HEADS:
                        assert head not in view.free_text, turn.turn_id
        assert (turns, marked) == (expected_turns, expected_marked), directory
        assert dict(kinds) == expected_kinds, directory


# --------------------------------------------------------------------------- #
# The meeting-outcome fold: the reconstruction seam a lever-ON record needs     #
# --------------------------------------------------------------------------- #

# One committed 9p2i seed that resolves three meetings, so a served memory
# snapshot at the SECOND meeting must already carry the FIRST meeting's outcome.
_MULTI_MEETING_SEED = 0
_MEETINGS_HEADER = "## Meetings so far:"


def _meetings_block(rendered: str) -> str:
    """The ``## Meetings so far:`` block of a rendered memory ("" when absent)."""

    if _MEETINGS_HEADER not in rendered:
        return ""
    tail = rendered.split(_MEETINGS_HEADER, 1)[1]
    lines: list[str] = []
    for line in tail.splitlines():
        if line.startswith("## "):
            break
        if line.strip():
            lines.append(line)
    return "\n".join(lines)


def _expected_meetings_block(replay: ReplayView, upto: int) -> str:
    """Render the meeting-history block from the SERVED replay DTO alone.

    Built independently of the loader's fold: the announced outcome of each
    resolved meeting before ``upto`` is read off the served ``MeetingView``
    (ejection, tally) and the served roster (the confirm-ejects role, the
    impostor count), the resume tick is the meeting tick + 1 (DESIGN.md §3.1,
    "returns control to tick t+1"), and the rows are pushed through the store's
    own ``record_meeting_outcome`` / ``render_for_prompt``. A loader that folded a
    wrong tick, tally or role would not reproduce these bytes.
    """

    from agents.memory.store import (  # noqa: PLC2701
        AgentMemory,
        _meeting_history_lines,
        record_meeting_outcome,
    )

    role_by_id = {player.agent_id: player.role for player in replay.players}
    impostors = sum(1 for role in role_by_id.values() if role == "IMPOSTOR")
    memory = AgentMemory()
    for meeting in replay.meetings[:upto]:
        ejected = meeting.ejected_player_id
        record_meeting_outcome(
            memory,
            end_tick=meeting.tick + 1,
            ejected_id=ejected,
            revealed_role=None if ejected is None else role_by_id[ejected],
            votes_for_ejected=(
                0
                if ejected is None
                else sum(1 for b in meeting.ballots if b.target == ejected)
            ),
            skip_votes=sum(1 for b in meeting.ballots if b.target == "SKIP"),
            roster_impostor_count=impostors,
        )
    # The view assembler bullets each line; the block renderer supplies the text.
    return "\n".join(
        f"- {line}" for line in _meeting_history_lines(memory.meeting_history)
    )


def test_meeting_outcome_memory_on_reconstruction_matches_the_store_render(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The lever-ON reconstruction the adopting record depends on: with
    # meeting_outcome_memory exported, a recording stamped for that substrate
    # reconstructs, and the memory the loader SERVES at the second meeting carries
    # the first meeting's announced outcome -- byte-for-byte what the store
    # renders for a memory folded from the served facts alone. Without the fold in
    # the walk the block is empty and this comparison fails.
    _delete_ailibi_env(monkeypatch)
    monkeypatch.setenv("AILIBI_MEETING_OUTCOME_MEMORY", "1")
    game_id = _stamp_committed_9p2i_seed(
        tmp_path, _MULTI_MEETING_SEED, substrate_flag_snapshot()
    )
    loader = ReplayLoader(replay_dir=tmp_path)
    replay = loader.load_replay(game_id)
    assert len(replay.meetings) >= 2

    second = replay.meetings[1]
    voter = second.ballots[0].voter  # a voter is alive at the meeting it votes in
    view = loader.get_meeting_memory(game_id, second.meeting_id, voter)

    expected = _expected_meetings_block(replay, upto=1)
    assert expected != ""
    assert _meetings_block(view.rendered_memory_text) == expected


def test_the_meeting_outcome_channel_reaches_the_served_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The channel is UNCONDITIONAL since the baseline-7 record, so the served
    # memory for a second meeting carries the FIRST meeting's announced outcome
    # -- with no AILIBI_* export in the process at all. (Baseline 6 rendered
    # nothing here, which is what made the fold measurement-neutral then.)
    _delete_ailibi_env(monkeypatch)
    loader = ReplayLoader(replay_dir=_COMMITTED_9P2I_DIR)
    replay = loader.load_replay(f"headless-seed-{_MULTI_MEETING_SEED}")
    assert len(replay.meetings) >= 2
    second = replay.meetings[1]
    voter = second.ballots[0].voter
    view = loader.get_meeting_memory(
        f"headless-seed-{_MULTI_MEETING_SEED}", second.meeting_id, voter
    )
    assert _MEETINGS_HEADER in view.rendered_memory_text


# -- the stamp's OTHER direction: a key this build's registry does not have ----
#
# The substrate registry is append-only, so a stamp from an OLDER build is a
# strict subset of this build's keys and compares clean. A stamp from a NEWER
# build carries a lever this one never registered — a substrate nothing here can
# reproduce or even name — and the guard used to iterate only the BUILD's keys,
# so it saw an empty diff and reconstructed silently.

_UNKNOWN_LEVER_STAMP = {**_ALL_FLAGS_ON, "a_lever_from_the_future": True}


def test_assert_substrate_matches_raises_on_a_key_this_build_does_not_know(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The finding's exact repro: the live snapshot plus ONE unknown key. Every
    # key this build knows agrees, so the old build-keys-only diff was empty.
    _delete_ailibi_env(monkeypatch)
    entries = [
        GameEndReplayEntry(
            game_id="g",
            tick=1,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags=_UNKNOWN_LEVER_STAMP,
        )
    ]

    with pytest.raises(ReplaySubstrateMismatchError) as excinfo:
        replay_loader._assert_substrate_matches("g", entries)

    message = str(excinfo.value)
    assert "a_lever_from_the_future" in message
    assert "BEHIND" in message  # the hint names WHICH build can read it
    assert excinfo.value.unknown == ["a_lever_from_the_future"]
    assert excinfo.value.differing == []


def test_the_paired_known_lever_flip_still_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The half that already worked, kept beside the new one so the pair reads
    # as one contract: a lever this build KNOWS, recorded the other way.
    _delete_ailibi_env(monkeypatch)
    entries = [
        GameEndReplayEntry(
            game_id="g",
            tick=1,
            winner="CREWMATES",
            reason="TASKS",
            substrate_flags={**_ALL_FLAGS_ON, "impostor_roll_call": True},
        )
    ]

    with pytest.raises(ReplaySubstrateMismatchError) as excinfo:
        replay_loader._assert_substrate_matches("g", entries)

    assert excinfo.value.differing == ["impostor_roll_call"]
    assert excinfo.value.unknown == []


def _mixed_substrate_set(tmp_path: Path, *, seed: int) -> Path:
    """The WHOLE committed 9p2i set, with ONE game_over restamped off-substrate.

    The whole set, not one file: a directory holding a single replay fails its
    own tick-0 state hash, so a one-file fixture would prove nothing about the
    substrate path — it would fail for an unrelated reason. Returns the PARENT
    of the set subdir, which is what :func:`api.main.create_app` takes.
    """

    parent = tmp_path / "samples"
    set_dir = parent / "9p2i"
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
    return parent


def test_listing_drops_a_substrate_mismatched_replay_but_cost_still_counts_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # The asymmetry, pinned so it is a decision rather than a discovery. The
    # picker promises a replay it can OPEN, so a recording this build cannot
    # reconstruct is dropped and logged. The cost summary promises what the run
    # SPENT, and cost/winner/ticks are read straight off the bytes with no
    # reconstruction — so a mismatched game is a real game that really cost that
    # much, and dropping it would understate the total.
    _delete_ailibi_env(monkeypatch)
    parent = _mixed_substrate_set(tmp_path, seed=0)
    loader = ReplayLoader(replay_dir=parent / "9p2i")

    with caplog.at_level(logging.WARNING):
        listed = loader.list_replays()
    summary = loader.cost_summary()

    assert "headless-seed-0" not in {view.game_id for view in listed}
    assert len(listed) == summary.total_replays - 1
    assert any("substrate mismatch" in record.message for record in caplog.records)
    # And the drop is not a blanket one: every other seed still lists.
    assert len(listed) == len(list((parent / "9p2i").glob("replay-seed-*.jsonl"))) - 1


def test_the_analysis_override_still_lists_a_mismatched_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The Task-14.8 ablation loader deliberately reads across substrates, so the
    # listing guard must honor the same override the reconstruction guard does —
    # otherwise the ablation could not even find the games it exists to compare.
    _delete_ailibi_env(monkeypatch)
    parent = _mixed_substrate_set(tmp_path, seed=0)
    loader = ReplayLoader(replay_dir=parent / "9p2i", allow_substrate_mismatch=True)

    listed = loader.list_replays()

    assert "headless-seed-0" in {view.game_id for view in listed}
