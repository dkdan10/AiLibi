"""Unit tests for :class:`api.replay_loader.ReplayLoader` (DESIGN.md §7, §11.4).

The fixtures write real replays via ``orchestrator.replay.ReplayLog`` (see
``tests/api/fixtures/sample_replay.py``), so these tests exercise engine
playback against ground truth: every reconstructed ``state_hash`` must match
the recorded one, or :class:`ReplayStateMismatchError` is raised.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from api.replay_loader import ReplayLoader, ReplayStateMismatchError
from api.schemas import (
    FoundBodyObsView,
    KillEventView,
    MeetingTriggeredEventView,
    ReportBodyEventView,
)
from tests.api.fixtures.sample_replay import (
    corrupt_tick_hash,
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

    assert [tick.tick for tick in replay.ticks] == [0, 1, 2]
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
    assert replay.metadata.total_ticks == 3
    assert replay.metadata.meeting_count == 1
    assert {player.agent_id for player in replay.players} == {
        "p-1",
        "p-2",
        "p-3",
        "p-4",
    }
    assert replay.map.rooms  # canonical map geometry is populated


def test_tick_event_projection(tmp_path: Path, loader: ReplayLoader) -> None:
    write_meeting_replay(tmp_path / "replay-seed-0.jsonl", seed=0)
    replay = loader.load_replay("headless-seed-0")

    kill_events = [e for e in replay.ticks[0].events if isinstance(e, KillEventView)]
    assert len(kill_events) == 1
    assert kill_events[0].victim_id == "p-1"

    tick1_types = {type(e) for e in replay.ticks[1].events}
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
    assert [tick.tick for tick in replay.ticks] == [0, 1, 2, 3]


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
    assert [tick.tick for tick in replay.ticks] == [0, 1]
    # The tick timeline still surfaces the meeting_triggered event...
    assert any(
        isinstance(event, MeetingTriggeredEventView) and event.meeting_id == meeting_id
        for event in replay.ticks[1].events
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
