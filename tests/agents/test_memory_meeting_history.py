"""Tests for the Task-18.22 meeting-history memory channel.

The meeting-history channel is the fourth :class:`AgentMemory` component: an
append-only log of concluded-meeting outcomes (resume tick + the announced
ejection) fed EXCLUSIVELY from the public ``note_meeting_concluded`` hook
payload and consumed ONLY by the v3 tactical feature encoder. This file pins the
carrier's semantics (record / partition / the non-decreasing-``end_tick``
guards), the :func:`record_meeting_outcome` fold and the store's additive
fourth field, the REAL :class:`~orchestrator.game.TacticalAgent` hook fold for
BOTH roles (an impostor has no emergency tracker, yet the fold must still run),
the firewall provenance angle named in the task DoD (``working.py`` imports no
engine/numpy/torch, and a recorded row carries exactly the two hook-payload
fields), and the inertness invariants that keep encoder-v2 bytes and every
rendered prompt byte identical before vs after the channel is populated.
"""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import pytest

from agents.memory.beliefs import BeliefState
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import (
    AgentMemory,
    record_meeting_outcome,
    render_for_prompt,
)
from agents.memory.working import MeetingHistory, MeetingOutcome, WorkingMemory
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.features import TacticalFeatureEncoder
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.world import load_canonical_map
from observation.packet import (
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import TacticalAgent

_WORKING_PY = Path("agents/memory/working.py")


# ---------------------------------------------------------------------------- #
# MeetingHistory carrier semantics
# ---------------------------------------------------------------------------- #


def test_record_appends_outcomes_in_order() -> None:
    history = MeetingHistory()
    assert len(history) == 0
    # ``tuple(...)`` narrows only the temporary, keeping ``history.outcomes``
    # unnarrowed for the non-empty comparison below (mypy len-narrowing would
    # otherwise pin it to ``tuple[()]``).
    assert tuple(history.outcomes) == ()

    history.record(end_tick=4, ejected_id="p-3")
    history.record(end_tick=9, ejected_id=None)

    assert len(history) == 2
    assert history.outcomes == (
        MeetingOutcome(end_tick=4, ejected_id="p-3"),
        MeetingOutcome(end_tick=9, ejected_id=None),
    )
    # ``outcomes`` is an immutable snapshot, not the backing list.
    assert isinstance(history.outcomes, tuple)


def test_ejection_and_skip_counts_partition_the_log() -> None:
    history = MeetingHistory()
    history.record(end_tick=1, ejected_id="p-2")
    history.record(end_tick=2, ejected_id=None)
    history.record(end_tick=3, ejected_id="p-5")
    history.record(end_tick=4, ejected_id=None)

    # The two counts partition every recorded row (ejection XOR skip).
    assert history.ejection_count() == 2
    assert history.skip_count() == 2
    assert history.ejection_count() + history.skip_count() == len(history)


def test_record_rejects_negative_end_tick() -> None:
    history = MeetingHistory()
    with pytest.raises(ValueError, match="non-negative"):
        history.record(end_tick=-1, ejected_id=None)


def test_record_rejects_decreasing_end_tick() -> None:
    history = MeetingHistory()
    history.record(end_tick=10, ejected_id="p-2")
    with pytest.raises(ValueError, match="non-decreasing"):
        history.record(end_tick=9, ejected_id=None)


def test_record_accepts_equal_end_tick() -> None:
    # A repeated fold of the same resume tick must NOT raise (mirrors the
    # WorkingMemory.record_sighting equal-tick allowance).
    history = MeetingHistory()
    history.record(end_tick=7, ejected_id="p-2")
    history.record(end_tick=7, ejected_id=None)
    assert len(history) == 2
    assert history.ejection_count() == 1
    assert history.skip_count() == 1


# ---------------------------------------------------------------------------- #
# record_meeting_outcome fold + the additive AgentMemory field
# ---------------------------------------------------------------------------- #


def test_record_meeting_outcome_appends_to_memory_channel() -> None:
    memory = AgentMemory()
    record_meeting_outcome(memory, end_tick=6, ejected_id="p-4")
    record_meeting_outcome(memory, end_tick=11, ejected_id=None)

    assert memory.meeting_history.outcomes == (
        MeetingOutcome(end_tick=6, ejected_id="p-4"),
        MeetingOutcome(end_tick=11, ejected_id=None),
    )
    assert memory.meeting_history.ejection_count() == 1
    assert memory.meeting_history.skip_count() == 1


def test_default_agent_memory_channel_is_empty() -> None:
    memory = AgentMemory()
    assert isinstance(memory.meeting_history, MeetingHistory)
    assert len(memory.meeting_history) == 0


def test_three_field_agent_memory_construction_still_works() -> None:
    # Every pre-18.22 three-field construction keeps working and gets an empty
    # channel from the field's default factory.
    memory = AgentMemory(
        episodic=MemoryStore(),
        working=WorkingMemory(),
        beliefs=BeliefState(),
    )
    assert isinstance(memory.meeting_history, MeetingHistory)
    assert len(memory.meeting_history) == 0
    # The fold still lands on the default-constructed channel.
    record_meeting_outcome(memory, end_tick=3, ejected_id="p-2")
    assert len(memory.meeting_history) == 1


# ---------------------------------------------------------------------------- #
# The REAL TacticalAgent hook fold — both roles
# ---------------------------------------------------------------------------- #


def _self_state_event(*, tick: int, room: str) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="self_state",
        payload={"room": room, "pending_task_id": None},
        provenance="observed",
    )


def test_hook_fold_populates_channel_for_crewmate() -> None:
    agent = TacticalAgent(
        agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"), role="CREWMATE"
    )
    # The crewmate carries an emergency tracker whose meeting-end bookkeeping
    # re-samples the over-gate baseline; it needs a self_state to read.
    agent.memory.episodic.append(_self_state_event(tick=8, room="CAFETERIA"))

    agent.note_meeting_concluded(
        end_tick=9, dead_ids=("p-9",), emergency_caller_id="p-1", ejected_id="p-9"
    )

    # The fold ran alongside the tracker: the channel carries the payload verbatim.
    assert agent.memory.meeting_history.outcomes == (
        MeetingOutcome(end_tick=9, ejected_id="p-9"),
    )


def test_hook_fold_populates_channel_for_impostor_without_tracker() -> None:
    agent = TacticalAgent(
        agent_id="p-1", policy=ImpostorPolicy(agent_id="p-1"), role="IMPOSTOR"
    )
    # An impostor has NO emergency tracker; the meeting-history fold must run
    # anyway (the v3 encoder is impostor-side).
    assert agent._emergency_tracker is None

    agent.note_meeting_concluded(
        end_tick=13, dead_ids=(), emergency_caller_id=None, ejected_id="p-4"
    )

    assert agent.memory.meeting_history.outcomes == (
        MeetingOutcome(end_tick=13, ejected_id="p-4"),
    )


def test_hook_fold_omitted_ejected_id_defaults_to_skip_row() -> None:
    agent = TacticalAgent(
        agent_id="p-1", policy=ImpostorPolicy(agent_id="p-1"), role="IMPOSTOR"
    )
    # The keyword defaults to None — every existing direct caller records a SKIP
    # row (the meeting tallied no ejection).
    agent.note_meeting_concluded(end_tick=7, dead_ids=(), emergency_caller_id=None)

    assert agent.memory.meeting_history.outcomes == (
        MeetingOutcome(end_tick=7, ejected_id=None),
    )
    assert agent.memory.meeting_history.skip_count() == 1


# ---------------------------------------------------------------------------- #
# Firewall-legality (the leak-style provenance angle)
# ---------------------------------------------------------------------------- #

_FORBIDDEN_WORKING_IMPORTS = frozenset({"engine", "numpy", "torch"})


def _imported_top_level_modules(source: str) -> set[str]:
    """The top-level module names imported by ``source`` (AST, not substring).

    Mirrors the ``tests/test_firewall.py`` scan idiom: walk every ``Import`` /
    ``ImportFrom`` node and reduce each to its root package, so a docstring that
    merely NAMES a banned module never false-positives.
    """

    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module is not None:
                roots.add(node.module.split(".", 1)[0])
    return roots


def test_working_module_has_no_engine_numpy_or_torch_import() -> None:
    # The channel lives in agents/memory/working.py, which must stay firewall- and
    # pure-Python-clean (no engine/, no numpy/torch) exactly like the rest of
    # agents/ — the meeting-history carrier introduces no new dependency.
    imported = _imported_top_level_modules(_WORKING_PY.read_text(encoding="utf-8"))
    assert imported & _FORBIDDEN_WORKING_IMPORTS == set()


def test_meeting_outcome_carries_exactly_the_hook_payload_fields() -> None:
    # Provenance pin: a recorded row carries EXACTLY the two public hook-payload
    # fields (resume tick + announced ejection) and nothing else — no engine-
    # private state can ride in through a widened dataclass.
    field_names = tuple(field.name for field in dataclasses.fields(MeetingOutcome))
    assert field_names == ("end_tick", "ejected_id")

    memory = AgentMemory()
    record_meeting_outcome(memory, end_tick=12, ejected_id="p-8")
    (row,) = memory.meeting_history.outcomes
    assert row.end_tick == 12
    assert row.ejected_id == "p-8"


# ---------------------------------------------------------------------------- #
# Inertness pins — encoder-v2 + prompt byte-safety
# ---------------------------------------------------------------------------- #


def _canonical_public_map() -> PublicMapView:
    return public_map_from_engine_map(load_canonical_map())


def _render_memory() -> AgentMemory:
    """A hand-built memory render_for_prompt accepts (a self_state + a belief)."""

    memory = AgentMemory()
    memory.episodic.append(
        EpisodicEvent(
            tick=3,
            type="self_state",
            payload={
                "agent_id": "p-1",
                "room": "CAFETERIA",
                "role": "CREWMATE",
                "pending_task_id": None,
            },
            provenance="observed",
        )
    )
    memory.episodic.append(
        EpisodicEvent(
            tick=3,
            type="saw_player",
            payload={"player_id": "p-2", "room": "CAFETERIA", "action": None},
            provenance="observed",
        )
    )
    memory.beliefs.seed_player("p-2", suspicion=0.7, trust=0.3)
    return memory


def test_render_for_prompt_is_inert_to_meeting_history() -> None:
    memory = _render_memory()
    before = render_for_prompt(memory)
    record_meeting_outcome(memory, end_tick=5, ejected_id="p-2")
    record_meeting_outcome(memory, end_tick=9, ejected_id=None)
    after = render_for_prompt(memory)
    # Populating the meeting-history channel changes ZERO prompt bytes.
    assert before == after


def _encode_fixture(public_map: PublicMapView) -> tuple[ObservationPacket, AgentMemory]:
    rooms = sorted(public_map.room_ids)
    packet = ObservationPacket(
        tick=10,
        agent_id="p-1",
        self_state=SelfView(
            room=rooms[0],
            role="IMPOSTOR",
            pending_task_id=None,
            fellow_impostor_ids=("p-9",),
        ),
        visible_players=(PlayerView(id="p-2", room=rooms[0], action=None),),
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=1,
            tasks_total=10,
            task_completion_percent=0.1,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=0,
    )
    beliefs = BeliefState()
    beliefs.seed_player("p-2", suspicion=0.65, trust=0.4)
    memory = AgentMemory(beliefs=beliefs)
    memory.episodic.append(
        EpisodicEvent(
            tick=8,
            type="saw_player",
            payload={"player_id": "p-2", "room": rooms[0]},
            provenance="observed",
        )
    )
    return packet, memory


def test_v2_encode_is_inert_to_meeting_history() -> None:
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    packet, memory = _encode_fixture(public_map)
    before = encoder.encode(packet, public_map, memory)
    record_meeting_outcome(memory, end_tick=5, ejected_id="p-2")
    record_meeting_outcome(memory, end_tick=9, ejected_id=None)
    after = encoder.encode(packet, public_map, memory)
    # The v2 encoder never reads the meeting-history channel — byte-identical.
    assert before == after
