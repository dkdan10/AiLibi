"""A public regroup, as the agent's rendered memory states it.

Under ``meeting_reset = "hub_with_grace"`` the live loop writes one
``public_regroup`` row into every living memory at each non-terminal meeting's
close (``orchestrator.replay.fold_public_regroup``), on the default evidence
path as well as under evidence version 2; version 1 writes none. Every render
change below keys on that row, so a memory without it renders exactly as
before:

* the meetings block announces the regroup (the notice);
* on the default evidence path, the co-presence rows the regroup produced fold
  into one line, as the spawn group does, when none of them carries a movement
  note; a subject last seen at the regroup after a sighting elsewhere carries
  one, and then each row stays its own. Version 2 folds neither group and
  renders each sighting on its own row;
* the self-location route states the regroup as its own step;
* a task completion detected on the regroup's tick is placed where the task was
  done, not in the meeting room.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Final

import pytest

import orchestrator.replay as replay_module
from agents.memory.episodic import EpisodicEvent
from agents.memory.evidence_context import ingest_public_regroup
from agents.memory.store import AgentMemory, render_for_prompt
from api.replay_loader import ReplayLoader
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from tests._helpers.scripted_meeting import record_game

#: Every player of a 9-player game; ``p-1`` is the observer.
PLAYERS: Final[tuple[str, ...]] = tuple(f"p-{index}" for index in range(1, 10))
OBSERVER: Final[str] = "p-1"
OTHERS: Final[tuple[str, ...]] = PLAYERS[1:]
#: A meeting held at tick 5 resumed play at tick 6.
REGROUP: Final[int] = 6
BUDGET: Final[int] = 100_000
NOTICE: Final[str] = (
    f"Public regroup at the start of tick {REGROUP}: living players were placed in "
    "CAFETERIA; this was not a walking journey."
)
TRAIL_STEP: Final[str] = (
    f"public regroup at the start of t{REGROUP}, placed in CAFETERIA "
    "(not a walking journey)"
)


def _self_state(
    tick: int, room: str, *, owned: tuple[str, ...] | None = None
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "room": room,
        "role": "CREWMATE",
        "pending_task_id": None,
        "agent_id": OBSERVER,
        "fellow_impostor_ids": (),
    }
    if owned is not None:
        payload["owned_task_ids"] = owned
    return EpisodicEvent(
        tick=tick,
        type="self_state",
        payload=payload,
        provenance="observed",
        observation_id=f"{OBSERVER}:{tick}:0",
    )


def _saw(tick: int, subject: str, room: str, seq: int) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_player",
        payload={"player_id": subject, "room": room, "action": None},
        provenance="observed",
        observation_id=f"{OBSERVER}:{tick}:{seq}",
    )


def _regroup_row(
    tick: int = REGROUP, room: str = "CAFETERIA", players: tuple[str, ...] = PLAYERS
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="public_regroup",
        payload={"room": room, "player_ids": tuple(sorted(players))},
        provenance="public",
    )


def _memory(
    *,
    regroup: bool,
    unseen_at_regroup: tuple[str, ...] = (),
    unseen_after_regroup: tuple[str, ...] = (),
    room_before: str = "LABS",
    version: int | None = None,
    row_room: str = "CAFETERIA",
    row_players: tuple[str, ...] = PLAYERS,
) -> AgentMemory:
    """Spawn together, split up, a meeting at tick 5, everyone gathered at 6.

    ``p-2`` is seen in ``room_before`` at ticks 1-5. A movement note lands on a
    subject's latest sighting only, when the agent saw it in another room
    before, and the fold takes no group whose regroup-tick row carries one
    (``agents.memory.store._spawn_group_indices``). So each subject is seen once
    more after the regroup: no tick-6 row is then a latest sighting and the
    regroup group folds. A subject in ``unseen_after_regroup`` is not seen
    again, so its tick-6 row is its latest sighting; for ``p-2`` after a stay in
    another room that row carries the note, and the group renders row by row.
    """

    memory = AgentMemory(evidence_reasoning_version=version)  # type: ignore[arg-type]
    events: list[EpisodicEvent] = [_self_state(0, "CAFETERIA")]
    events += [
        _saw(0, subject, "CAFETERIA", seq) for seq, subject in enumerate(OTHERS, 1)
    ]
    for tick in range(1, REGROUP):
        events.append(_self_state(tick, room_before))
        events.append(_saw(tick, "p-2", room_before, 1))
    if regroup:
        events.append(_regroup_row(room=row_room, players=row_players))
    events.append(_self_state(REGROUP, "CAFETERIA"))
    events += [
        _saw(REGROUP, subject, "CAFETERIA", seq)
        for seq, subject in enumerate(OTHERS, 1)
        if subject not in unseen_at_regroup
    ]
    events.append(_self_state(REGROUP + 1, "UPPER_HALL"))
    events += [
        _saw(REGROUP + 1, subject, "ADMIN" if index % 2 else "UPPER_HALL", index)
        for index, subject in enumerate(OTHERS, 1)
        if subject not in unseen_after_regroup
    ]
    for event in events:
        memory.episodic.append(event)
    return memory


def _render(memory: AgentMemory) -> str:
    return render_for_prompt(memory, token_budget=BUDGET)


def _regroup_tick_rows(view: str) -> list[str]:
    return [line for line in view.splitlines() if f"[tick {REGROUP}]" in line]


# --------------------------------------------------------------------------- #
# The notice                                                                  #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("version", [None, 2])
def test_the_regroup_row_is_ingested_on_the_default_path_and_under_version_2(
    version: int | None,
) -> None:
    memory = AgentMemory(evidence_reasoning_version=version)  # type: ignore[arg-type]
    ingest_public_regroup(memory, tick=REGROUP, room="CAFETERIA", player_ids=PLAYERS)
    rows = [row for row in memory.episodic.recent(since_tick=0)]
    assert [(row.type, row.tick, row.provenance) for row in rows] == [
        ("public_regroup", REGROUP, "public")
    ]


def test_version_1_ingests_no_regroup_row() -> None:
    memory = AgentMemory(evidence_reasoning_version=1)
    ingest_public_regroup(memory, tick=REGROUP, room="CAFETERIA", player_ids=PLAYERS)
    assert memory.episodic.recent(since_tick=0) == ()


def test_the_default_path_renders_the_notice_whenever_the_row_exists() -> None:
    assert NOTICE in _render(_memory(regroup=True)).splitlines()[3]
    assert "Public regroup" not in _render(_memory(regroup=False))


def test_version_1_renders_no_notice_even_beside_a_row() -> None:
    assert "Public regroup" not in _render(_memory(regroup=True, version=1))


def test_only_a_public_row_is_an_announced_regroup() -> None:
    # The same row written as something the agent observed is not the public
    # announcement: no notice, no fold, no route step.
    memory = _memory(regroup=False)
    public = _regroup_row()
    forged = EpisodicEvent(
        tick=public.tick,
        type=public.type,
        payload=public.payload,
        provenance="observed",
    )
    rebuilt = AgentMemory()
    for event in memory.episodic.recent(since_tick=0):
        if event.tick == REGROUP and event.type == "self_state":
            rebuilt.episodic.append(forged)
        rebuilt.episodic.append(event)
    assert _render(rebuilt) == _render(memory)


def test_a_malformed_public_row_is_refused() -> None:
    memory = _memory(regroup=False)
    memory.episodic.append(
        EpisodicEvent(
            tick=REGROUP + 5,
            type="public_regroup",
            payload={"room": "CAFETERIA"},
            provenance="public",
        )
    )
    with pytest.raises(ValueError, match="public regroup row is malformed"):
        _render(memory)


@pytest.mark.parametrize(
    "payload",
    [
        {"room": "CAFETERIA"},
        {"room": 7, "player_ids": ("p-1", "p-2")},
        {"room": "CAFETERIA", "player_ids": "p-1"},
        {"room": "CAFETERIA", "player_ids": frozenset({"p-1"})},
    ],
)
def test_the_malformed_row_refusal_quotes_the_payload_it_read(
    payload: dict[str, Any],
) -> None:
    memory = _memory(regroup=False)
    memory.episodic.append(
        EpisodicEvent(
            tick=REGROUP + 5,
            type="public_regroup",
            payload=payload,
            provenance="public",
        )
    )
    with pytest.raises(ValueError) as refused:
        _render(memory)
    assert str(refused.value) == f"public regroup row is malformed: {payload!r}"


def test_a_public_row_listing_its_players_reads_as_the_tuple_row_does() -> None:
    # The row's contract is a room and a list of player ids; the one writer
    # stores a tuple, and a row holding a list renders the same notice, fold and
    # route step.
    tupled = _memory(regroup=True)
    listed = AgentMemory()
    for event in tupled.episodic.recent(since_tick=0):
        if event.type == "public_regroup":
            event = EpisodicEvent(
                tick=event.tick,
                type=event.type,
                payload={
                    "room": event.payload["room"],
                    "player_ids": list(event.payload["player_ids"]),
                },
                provenance=event.provenance,
            )
        listed.episodic.append(event)
    view = _render(listed)
    assert NOTICE in view
    assert view == _render(tupled)


# --------------------------------------------------------------------------- #
# The fold and the trail                                                      #
# --------------------------------------------------------------------------- #


def test_a_nine_player_regroup_folds_eight_rows_into_one_line() -> None:
    with_row = _regroup_tick_rows(_render(_memory(regroup=True)))
    without_row = _regroup_tick_rows(_render(_memory(regroup=False)))
    assert len(without_row) == len(OTHERS) == 8
    assert with_row == [
        f"- [obs {OBSERVER}:{REGROUP}:1] [tick {REGROUP}] After the public regroup "
        f"you saw every other living player in CAFETERIA: {', '.join(OTHERS)}."
    ]


def test_a_subject_last_seen_at_the_regroup_after_a_walk_leaves_every_row() -> None:
    # The fold's strength, beside the folded case above: p-2 was seen in LABS
    # before the meeting and not again after the regroup, so its tick-6 row is
    # its latest sighting and carries the movement note. The group then renders
    # row by row, the note on p-2's row, with the notice and the route step and
    # no fold line; the rows are the ones rendered without the public row.
    view = _render(_memory(regroup=True, unseen_after_regroup=("p-2",)))
    rows = _regroup_tick_rows(view)
    assert len(rows) == len(OTHERS) == 8
    assert "After the public regroup" not in view
    assert f"- {NOTICE}" in view.splitlines()
    assert TRAIL_STEP in _trail(view)
    (noted,) = [row for row in rows if "moved from" in row]
    assert "You saw p-2 in CAFETERIA" in noted
    assert noted.endswith(" (moved from LABS, last seen there at tick 5).")
    assert rows == _regroup_tick_rows(
        _render(_memory(regroup=False, unseen_after_regroup=("p-2",)))
    )


def test_a_subject_never_seen_elsewhere_leaves_the_fold_whole() -> None:
    # The note needs a room change: p-9 is never seen away from the meeting
    # room before the regroup, so its tick-6 row stays bare even as its latest
    # sighting, and the group still folds.
    rows = _regroup_tick_rows(
        _render(_memory(regroup=True, unseen_after_regroup=("p-9",)))
    )
    assert rows == [
        f"- [obs {OBSERVER}:{REGROUP}:1] [tick {REGROUP}] After the public regroup "
        f"you saw every other living player in CAFETERIA: {', '.join(OTHERS)}."
    ]


def test_a_partial_view_of_the_regroup_keeps_its_rows() -> None:
    view = _render(_memory(regroup=True, unseen_at_regroup=("p-9",)))
    rows = _regroup_tick_rows(view)
    assert len(rows) == len(OTHERS) - 1
    assert not any("every other living player" in row for row in rows)


def test_the_fold_expects_the_players_the_row_gathered_not_the_known_roster() -> None:
    # p-9 died before the meeting: the row gathers eight players, so the seven
    # others the observer saw at the regroup fold into one line.
    memory = _memory(
        regroup=True,
        unseen_at_regroup=("p-9",),
        row_players=tuple(player for player in PLAYERS if player != "p-9"),
    )
    rows = _regroup_tick_rows(_render(memory))
    assert rows == [
        f"- [obs {OBSERVER}:{REGROUP}:1] [tick {REGROUP}] After the public regroup "
        f"you saw every other living player in CAFETERIA: {', '.join(p for p in OTHERS if p != 'p-9')}."
    ]


def test_the_fold_reads_the_rows_room() -> None:
    # The same group of rows under a row naming another room is not the fact
    # the fold states, so it keeps its rows.
    memory = _memory(regroup=True, row_room="ADMIN")
    assert len(_regroup_tick_rows(_render(memory))) == len(OTHERS)


def _trail(view: str) -> str:
    (line,) = [line for line in view.splitlines() if line.startswith("- Your route")]
    return line


def test_the_route_states_the_regroup_as_its_own_step() -> None:
    assert f"LABS t1-5 -> {TRAIL_STEP} -> CAFETERIA t6 -> UPPER_HALL t7" in _trail(
        _render(_memory(regroup=True))
    )
    assert "LABS t1-5 -> CAFETERIA t6 -> UPPER_HALL t7" in _trail(
        _render(_memory(regroup=False))
    )


def test_the_notice_and_the_route_step_read_the_rows_room() -> None:
    view = _render(_memory(regroup=True, row_room="ADMIN"))
    assert NOTICE.replace("CAFETERIA", "ADMIN") in view
    assert TRAIL_STEP.replace("CAFETERIA", "ADMIN") in _trail(view)


def test_the_regroup_breaks_a_stay_in_the_meeting_room_too() -> None:
    assert f"CAFETERIA t0-5 -> {TRAIL_STEP} -> CAFETERIA t6" in _trail(
        _render(_memory(regroup=True, room_before="CAFETERIA"))
    )
    assert "CAFETERIA t0-6" in _trail(
        _render(_memory(regroup=False, room_before="CAFETERIA"))
    )


def test_under_version_2_the_regroup_sightings_keep_their_own_rows() -> None:
    # Version 2 renders every sighting on its own row, at spawn and after a
    # regroup alike: the row brings the notice and the route step, no fold line.
    with_row = _render(_memory(regroup=True, version=2))
    without_row = _render(_memory(regroup=False, version=2))
    assert f"- {NOTICE}" in with_row.splitlines()
    assert TRAIL_STEP in _trail(with_row)
    assert "After the public regroup" not in with_row
    assert "You saw every other player in" not in with_row
    # Version 2 dates a sighting "[tick 6, timing unspecified]".
    stamp = re.compile(rf"\[tick {REGROUP}[,\]]")
    rows = [line for line in with_row.splitlines() if stamp.search(line)]
    assert rows == [line for line in without_row.splitlines() if stamp.search(line)]
    assert sorted(re.findall(r"You saw (p-\d) in CAFETERIA", "\n".join(rows))) == [
        *OTHERS
    ]


@pytest.mark.parametrize(
    ("version", "folds"), [(None, True), (1, True), (2, False)], ids=str
)
def test_only_version_2_leaves_the_spawn_group_unfolded(
    version: int | None, folds: bool
) -> None:
    # The fold the regroup reuses runs on every path but version 2, whose
    # observations carry no sighting key to fold on.
    view = _render(_memory(regroup=False, version=version))
    assert ("You saw every other player in CAFETERIA" in view) is folds


def test_the_row_changes_only_the_notice_the_fold_and_the_route() -> None:
    with_row = _render(_memory(regroup=True)).splitlines()
    without_row = _render(_memory(regroup=False)).splitlines()
    added = [line for line in with_row if line not in without_row]
    removed = [line for line in without_row if line not in with_row]
    fold = (
        f"- [obs {OBSERVER}:{REGROUP}:1] [tick {REGROUP}] After the public regroup "
        f"you saw every other living player in CAFETERIA: {', '.join(OTHERS)}."
    )
    assert sorted(added) == sorted(
        ["## Meetings so far:", f"- {NOTICE}", fold, _trail("\n".join(with_row))]
    )
    assert sorted(removed) == sorted(
        [*_regroup_tick_rows("\n".join(without_row)), _trail("\n".join(without_row))]
    )


# --------------------------------------------------------------------------- #
# Own-completion placement                                                    #
# --------------------------------------------------------------------------- #


def _completion_memory(*, regroup: bool, resume_room: str) -> AgentMemory:
    """``p-1`` finishes analyze_specimen in LABS on the trigger tick (5)."""

    memory = AgentMemory()
    rows = [
        _self_state(4, "LABS", owned=("analyze_specimen",)),
        _self_state(5, "LABS", owned=("analyze_specimen",)),
    ]
    if regroup:
        rows.append(_regroup_row())
    rows.append(_self_state(REGROUP, resume_room, owned=()))
    for row in rows:
        memory.episodic.append(row)
    return memory


def _completion_line(view: str) -> str:
    (line,) = [line for line in view.splitlines() if "You completed" in line]
    return line


def test_a_trigger_tick_completion_is_placed_where_it_was_done() -> None:
    view = _render(_completion_memory(regroup=True, resume_room="CAFETERIA"))
    assert _completion_line(view).endswith(
        f"[tick {REGROUP}] You completed analyze_specimen (you were in LABS)."
    )


def test_without_the_row_the_completion_takes_the_resume_room() -> None:
    view = _render(_completion_memory(regroup=False, resume_room="CAFETERIA"))
    assert _completion_line(view).endswith("(you were in CAFETERIA).")


def test_an_ordinary_resume_places_the_completion_as_before() -> None:
    view = _render(_completion_memory(regroup=False, resume_room="LABS"))
    assert _completion_line(view) == (
        f"- [obs {OBSERVER}:{REGROUP}:0] [tick {REGROUP}] You completed "
        "analyze_specimen (you were in LABS)."
    )


# --------------------------------------------------------------------------- #
# End to end: the default-path notice, live and reconstructed                 #
# --------------------------------------------------------------------------- #

_SEED: Final[int] = 1000
_RESET: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    meeting_reset="hub_with_grace"
)


@pytest.fixture(scope="module")
def reset_game(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return record_game(
        tmp_path_factory.mktemp("reset") / "9p2i", seed=_SEED, config=_RESET
    )


@pytest.fixture(scope="module")
def preserve_game(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return record_game(
        tmp_path_factory.mktemp("preserve") / "9p2i", seed=_SEED, config=None
    )


def _second_meeting(path: Path) -> MeetingReplayEntry:
    meetings = [
        row for row in read_all_entries(path) if isinstance(row, MeetingReplayEntry)
    ]
    assert len(meetings) >= 2
    return meetings[1]


def _loader_memory(path: Path, meeting: MeetingReplayEntry) -> str:
    view = ReplayLoader(path.parent).get_meeting_memory(
        f"headless-seed-{_SEED}", meeting.meeting_id, meeting.triggered_by
    )
    return view.rendered_memory_text


def _opener_prompts(meeting: MeetingReplayEntry) -> list[str]:
    return [
        call.prompt
        for call in meeting.llm_calls
        if call.agent_id == meeting.triggered_by
    ]


def _first_resume_tick(path: Path) -> int:
    meetings = [
        row for row in read_all_entries(path) if isinstance(row, MeetingReplayEntry)
    ]
    return meetings[0].tick + 1


def test_the_second_meeting_carries_the_notice_live_and_reconstructed(
    reset_game: Path,
) -> None:
    meeting = _second_meeting(reset_game)
    notice = re.escape(
        f"Public regroup at the start of tick {_first_resume_tick(reset_game)}:"
    )
    text = _loader_memory(reset_game, meeting)
    assert re.search(notice, text)
    prompts = _opener_prompts(meeting)
    assert prompts and all(re.search(notice, prompt) for prompt in prompts)
    assert any(text in prompt for prompt in prompts)


def test_without_the_folds_ingestion_the_reconstruction_loses_the_notice(
    reset_game: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The fold every reconstruction shares writes the row through
    # ``fold_public_regroup``; removing that one call leaves the loader without
    # the notice while the live prompt still has it.
    monkeypatch.setattr(replay_module, "fold_public_regroup", lambda *a, **k: None)
    meeting = _second_meeting(reset_game)
    text = _loader_memory(reset_game, meeting)
    assert "Public regroup" not in text
    assert not any(text in prompt for prompt in _opener_prompts(meeting))


def test_the_preserve_game_renders_no_notice(preserve_game: Path) -> None:
    meeting = _second_meeting(preserve_game)
    assert "Public regroup" not in _loader_memory(preserve_game, meeting)
    assert not any("Public regroup" in call.prompt for call in meeting.llm_calls)
