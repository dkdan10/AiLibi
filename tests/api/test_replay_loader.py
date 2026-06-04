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
from pathlib import Path

import pytest

from api import replay_loader
from api.replay_loader import ReplayLoader, ReplayStateMismatchError, RosterConfig
from api.schemas import (
    FoundBodyObsView,
    KillEventView,
    MeetingTriggeredEventView,
    ReportBodyEventView,
)
from engine.world import load_canonical_map
from llm.fake_provider import FakeProvider
from observation.service import ObservationService
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import LLMCallRecord, ReplayLogEntry, read_all_entries
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state
from tests.api.fixtures.sample_replay import (
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

    # ticks[0] is the synthesized tick=-1 "Start" frame (Finding 1); the
    # recorded ticks (0, 1, 2) follow it.
    assert [tick.tick for tick in replay.ticks] == [-1, 0, 1, 2]
    assert len(replay.meetings) == 1
    meeting = replay.meetings[0]
    assert meeting.meeting_id == expected.meeting_id
    assert meeting.tick == 1
    assert meeting.trigger_kind == "body"
    assert meeting.outcome == "SKIPPED"
    assert meeting.total_cost_usd == pytest.approx(expected.total_cost_usd)
    assert {report.agent_id for report in meeting.reports} == set(
        expected.living_agents
    )
    assert replay.metadata.winner == "CREWMATES"
    # total_ticks counts only recorded ReplayEntrys; the synthesized initial
    # entry is extra, so ticks has exactly one more element than total_ticks.
    assert replay.metadata.total_ticks == 3
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
    write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    replay = loader.load_replay("headless-seed-0")

    # Select by tick number, not array index: ticks[0] is the synthesized
    # tick=-1 "Start" frame, so the recorded ticks are offset by one.
    tick0 = next(t for t in replay.ticks if t.tick == 0)
    tick1 = next(t for t in replay.ticks if t.tick == 1)

    kill_events = [e for e in tick0.events if isinstance(e, KillEventView)]
    assert len(kill_events) == 1
    assert kill_events[0].victim_id == "p-1"

    tick1_types = {type(e) for e in tick1.events}
    assert MeetingTriggeredEventView in tick1_types
    assert ReportBodyEventView in tick1_types


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
    # Synthesized "Start" (tick=-1) precedes the two recorded ticks.
    assert [tick.tick for tick in replay.ticks] == [-1, 0, 1]
    # The tick timeline still surfaces the meeting_triggered event (tick 1)...
    tick1 = next(t for t in replay.ticks if t.tick == 1)
    assert any(
        isinstance(event, MeetingTriggeredEventView) and event.meeting_id == meeting_id
        for event in tick1.events
    )
    # ...but memory for the unresolved meeting is not exposed.
    with pytest.raises(KeyError):
        loader.get_meeting_memory("headless-seed-0", meeting_id, "p-2")


def test_unknown_game_raises_file_not_found(loader: ReplayLoader) -> None:
    with pytest.raises(FileNotFoundError):
        loader.load_replay("headless-seed-404")


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
    assert memory.tick == 1
    assert memory.role == "CREWMATE"
    assert memory.tasks_assigned == 1
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
    # The corruption is recorded, not silently swallowed.
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("replay-seed-1.jsonl" in r.getMessage() for r in warnings)


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


def test_multi_impostor_memory_walk_holds_firewall(
    tmp_path: Path, multi_impostor_replay_bytes: bytes
) -> None:
    # The first multi-impostor reconstruction also drives the collect_memory walk:
    # get_meeting_memory rebuilds every per-tick packet through ObservationService,
    # which is where 7.2's impostor-only fellow_impostor_ids is populated. Confirm
    # that rebuild path is reachable on multi-impostor data and an impostor's
    # memory resolves (the crew-empty invariant itself is guarded by 7.2's leak
    # property sweep over the same service).
    (tmp_path / "replay-seed-0.jsonl").write_bytes(multi_impostor_replay_bytes)
    _write_roster(tmp_path, num_players=7, num_impostors=2, tasks_per_crewmate=2)
    loader = ReplayLoader(replay_dir=tmp_path)

    replay = loader.load_replay("headless-seed-0")
    assert replay.meetings  # the hermetic 7p/2i seed-0 game resolves a meeting
    meeting_id = replay.meetings[0].meeting_id
    impostor = next(p.agent_id for p in replay.players if p.role == "IMPOSTOR")
    memory = loader.get_meeting_memory("headless-seed-0", meeting_id, impostor)
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


# -- committed 7p/2i meeting-heavy set (Task 7.8) -----------------------------
#
# Unlike the hermetic Task 7.4 fixtures above (tmp_path, no committed data), the
# two tests below point the loader at the COMMITTED replays/samples/7p2i/ set and
# reconstruct it. This is the CI-enforced determinism gate for the committed
# multi-impostor set: check.sh runs `uv run pytest` but does NOT invoke
# scripts/verify_samples.sh, so without a pytest test the committed 7p/2i set's
# byte-identical reconstruction would be unguarded in CI. It pairs with the flat
# 4p/1i set's coverage in tests/scripts/test_verify_samples.py
# (test_clean_sample_verifies), so BOTH committed sets are CI-gated.

_COMMITTED_7P2I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "7p2i"
)

# The Wave 0 exit-gate floor (DESIGN.md §11.4; tasks/phase-7-plan.md "Wave 0 exit
# criteria"): >= 30 RESOLVED meetings over the committed denominator. Pinned in CI
# so a future engine change can never silently drop the committed set below the
# enablement gate without failing here.
_GATE_MIN_RESOLVED_MEETINGS = 30

# The committed 7p/2i set is exactly 50 replays, seeds 0-49. Pinned so the
# reconstruction gate below verifies the WHOLE set rather than just "enough" of
# it: a deleted seed shrinks the on-disk glob, and a corrupted one is silently
# dropped by list_replays() (CorruptedFileError -> WARNING), either of which
# would otherwise still clear the >=30 meeting floor while leaving committed
# seeds un-reconstructed.
_COMMITTED_7P2I_SEED_COUNT = 50


def _committed_7p2i_seeds() -> list[int]:
    return sorted(
        int(p.stem.rsplit("-", 1)[1])
        for p in _COMMITTED_7P2I_DIR.glob("replay-seed-*.jsonl")
    )


@pytest.mark.skip(
    reason=(
        "Task 8.1 per-player task re-key (DESIGN.md §3.2) changes "
        "_serialize_world_state, so every committed game's per-tick state_hash "
        "changes and the committed 7p/2i bytes no longer reconstruct. Re-recorded "
        "and re-enabled in Task 8.12 (combined re-record)."
    )
)
def test_committed_7p2i_set_reconstructs_byte_identically() -> None:
    # Every committed 7p/2i replay reconstructs byte-identically under the current
    # engine: load_replay re-seeds from the committed roster.json (7p/2i + 2
    # tasks/crewmate) and raises ReplayStateMismatchError on ANY per-tick
    # state_hash drift. num_impostors / tasks_per_crewmate are not recoverable from
    # the action stream, so this only reconstructs because the committed descriptor
    # is correct — making this both the determinism gate and a roster.json check.
    assert replay_loader._load_roster_config(_COMMITTED_7P2I_DIR) == RosterConfig(
        num_players=7, num_impostors=2, tasks_per_crewmate=2
    )
    # Pin the committed shape BEFORE the load loop. The meeting floor below is a
    # count of resolved meetings, NOT a count of replays — reusing it as the
    # replay-count check let a thinned/corrupted checkout pass: list_replays()
    # silently skips a corrupted file and the glob misses a deleted one, so as
    # long as >=30 readable files remained, the loop would never reconstruct the
    # missing seeds despite this test's contract that EVERY committed replay does.
    expected_seeds = list(range(_COMMITTED_7P2I_SEED_COUNT))
    assert _committed_7p2i_seeds() == expected_seeds  # no deleted seed on disk

    loader = ReplayLoader(replay_dir=_COMMITTED_7P2I_DIR)
    metas = loader.list_replays()
    # A corrupted file is dropped from the listing, so an exact-count match (not a
    # floor) is what proves the whole committed set is readable before we load it.
    assert len(metas) == _COMMITTED_7P2I_SEED_COUNT

    resolved_meetings = 0
    for meta in metas:
        replay = loader.load_replay(meta.game_id)  # raises on determinism drift
        assert {p.agent_id for p in replay.players} == {f"p-{n}" for n in range(1, 8)}
        assert sum(1 for p in replay.players if p.role == "IMPOSTOR") == 2
        resolved_meetings += len(replay.meetings)

    # The whole point of the meeting-heavy set: the Stage-A enablement gate's
    # resolved-meeting floor is committed and CI-enforced, not just asserted once
    # at generation time.
    assert resolved_meetings >= _GATE_MIN_RESOLVED_MEETINGS


def test_committed_7p2i_set_holds_crew_firewall(tmp_path: Path) -> None:
    # End-to-end firewall coverage (7.2's crew-empty invariant) on the REAL
    # committed multi-impostor roster — the coverage the 7.2 contract defers to
    # this task. The single-impostor 4p/1i fixtures cannot surface a crew-tuple
    # misroute (every fellow_impostor_ids is () there regardless), so this re-seeds
    # each committed seed at the recorded roster and confirms ObservationService
    # gives every crewmate-recipient an empty fellow_impostor_ids while each
    # impostor sees exactly the OTHER impostor (self excluded). The invariant is a
    # pure function of roles, so the seeded initial state exercises it directly.
    roster = replay_loader._load_roster_config(_COMMITTED_7P2I_DIR)
    assert roster is not None
    game_map = load_canonical_map()
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )
    seeds = _committed_7p2i_seeds()
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
