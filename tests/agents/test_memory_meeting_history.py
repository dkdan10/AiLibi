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
import json
from pathlib import Path
from typing import Final

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
from agents.tactical.features import TacticalFeatureEncoder, TacticalFeatureEncoderV3
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.world import load_canonical_map
from eval.leak_scan import assert_memory_render_role_disclosure_is_entitled
from observation.packet import (
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import TacticalAgent
from tests._helpers.committed import (
    CORPUS_4P1I,
    CORPUS_9P2I,
    SAMPLES_4P1I,
    SAMPLES_9P2I,
)

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


def test_meeting_outcome_carries_exactly_the_announced_facts() -> None:
    # Provenance pin: a recorded row carries EXACTLY the facts the table heard
    # announced and nothing else — no engine-private state can ride in through a
    # widened dataclass. Each name below is a public announcement:
    #
    #   end_tick             the tick gameplay resumed at
    #   ejected_id           who the tally removed
    #   revealed_role        the confirm-ejects announcement for THAT player
    #   votes_for_ejected    the announced tally
    #   skip_votes           the announced tally
    #   roster_impostor_count  the impostor count stated at game start
    field_names = tuple(field.name for field in dataclasses.fields(MeetingOutcome))
    assert field_names == (
        "end_tick",
        "ejected_id",
        "revealed_role",
        "votes_for_ejected",
        "skip_votes",
        "roster_impostor_count",
    )

    memory = AgentMemory()
    record_meeting_outcome(
        memory,
        end_tick=12,
        ejected_id="p-8",
        revealed_role="IMPOSTOR",
        votes_for_ejected=5,
        skip_votes=2,
        roster_impostor_count=2,
    )
    (row,) = memory.meeting_history.outcomes
    assert row.end_tick == 12
    assert row.ejected_id == "p-8"
    assert row.revealed_role == "IMPOSTOR"
    assert row.votes_for_ejected == 5
    assert row.skip_votes == 2
    assert row.roster_impostor_count == 2


def test_a_skipped_meeting_may_not_carry_a_revealed_role() -> None:
    # The disclosure is the EJECTION's, so a row that reveals a role without
    # ejecting anyone is a wiring bug, not a state to normalise away.
    memory = AgentMemory()
    with pytest.raises(ValueError, match="skipped meeting reveals no role"):
        record_meeting_outcome(
            memory, end_tick=4, ejected_id=None, revealed_role="CREWMATE"
        )


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


def test_render_for_prompt_reads_the_meeting_history_channel() -> None:
    memory = _render_memory()
    before = render_for_prompt(memory)
    record_meeting_outcome(memory, end_tick=5, ejected_id="p-2")
    record_meeting_outcome(memory, end_tick=9, ejected_id=None)
    after = render_for_prompt(memory)
    # Populating the channel adds the block: one line per concluded meeting.
    assert before != after
    assert "## Meetings so far:" not in before
    assert "- Meeting 1 (tick 5): p-2 EJECTED." in after
    assert "- Meeting 2 (tick 9): no ejection." in after


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


# ---------------------------------------------------------------------------- #
# The lever resolver
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# OFF-path byte identity
# ---------------------------------------------------------------------------- #


def _announced(memory: AgentMemory) -> None:
    """Fold two meetings carrying the full announcement payload."""

    record_meeting_outcome(
        memory,
        end_tick=14,
        ejected_id="p-2",
        revealed_role="IMPOSTOR",
        votes_for_ejected=7,
        skip_votes=1,
        roster_impostor_count=2,
    )
    record_meeting_outcome(
        memory,
        end_tick=27,
        ejected_id=None,
        votes_for_ejected=0,
        skip_votes=6,
        roster_impostor_count=2,
    )


def test_the_announced_fields_reach_the_render() -> None:
    # A memory whose outcomes carry the announced role and the tally renders MORE
    # than one holding the two-field fold alone: the extra fields are read, not
    # merely stored.
    two_field = _render_memory()
    record_meeting_outcome(two_field, end_tick=14, ejected_id="p-2")
    record_meeting_outcome(two_field, end_tick=27, ejected_id=None)
    announced = _render_memory()
    _announced(announced)

    lean = render_for_prompt(two_field)
    full = render_for_prompt(announced)

    assert lean != full
    assert "- Meeting 1 (tick 14): p-2 EJECTED." in lean
    assert (
        "- Meeting 1 (tick 14): p-2 EJECTED 7-1 — p-2 was an IMPOSTOR. "
        "1 impostor remains." in full
    )


# ---------------------------------------------------------------------------- #
# The rendered block, line for line
# ---------------------------------------------------------------------------- #


def _meetings_block(render: str) -> list[str]:
    """The ``## Meetings so far:`` bullet lines, in rendered order."""

    lines = render.splitlines()
    start = lines.index("## Meetings so far:")
    block: list[str] = []
    for line in lines[start + 1 :]:
        if not line.startswith("- "):
            break
        block.append(line[2:])
    return block


def test_on_path_renders_an_ejected_impostor_a_crewmate_and_a_skip() -> None:
    memory = _render_memory()
    record_meeting_outcome(
        memory,
        end_tick=14,
        ejected_id="p-2",
        revealed_role="CREWMATE",
        votes_for_ejected=6,
        skip_votes=2,
        roster_impostor_count=2,
    )
    record_meeting_outcome(
        memory,
        end_tick=27,
        ejected_id=None,
        votes_for_ejected=0,
        skip_votes=6,
        roster_impostor_count=2,
    )
    record_meeting_outcome(
        memory,
        end_tick=41,
        ejected_id="p-5",
        revealed_role="IMPOSTOR",
        votes_for_ejected=4,
        skip_votes=0,
        roster_impostor_count=2,
    )

    render = render_for_prompt(
        memory,
    )

    assert _meetings_block(render) == [
        "Meeting 1 (tick 14): p-2 EJECTED 6-2 — p-2 was a CREWMATE. 2 impostors remain.",
        "Meeting 2 (tick 27): no ejection (6 skip). 2 impostors remain.",
        "Meeting 3 (tick 41): p-5 EJECTED 4-0 — p-5 was an IMPOSTOR. 1 impostor remains.",
    ]


def test_the_block_sits_above_the_observations_and_below_the_role_line() -> None:
    memory = _render_memory()
    _announced(memory)
    lines = render_for_prompt(
        memory,
    ).splitlines()
    assert lines[0].startswith("## Your role:")
    assert lines.index("## Meetings so far:") < lines.index(
        "## Recent observations (most salient first):"
    )


def test_the_block_survives_a_budget_that_sheds_every_observation() -> None:
    # Non-elastic by construction: the record of what a meeting decided is what
    # stops a long game re-prosecuting a closed case, so a budget tight enough to
    # drop every sighting must still carry it.
    memory = _render_memory()
    _announced(memory)
    full = render_for_prompt(
        memory,
    )
    tight = render_for_prompt(
        memory,
        token_budget=60,
    )
    assert "## Recent observations (most salient first):" in full
    assert "## Recent observations (most salient first):" not in tight
    assert _meetings_block(tight) == _meetings_block(full)


# ---------------------------------------------------------------------------- #
# The impostors-remaining arithmetic
# ---------------------------------------------------------------------------- #


def test_impostors_remaining_counts_down_only_on_a_confirmed_impostor() -> None:
    # A two-impostor game: the first ejection is wrong, the second is right.
    history = MeetingHistory()
    history.record(
        end_tick=10,
        ejected_id="p-3",
        revealed_role="CREWMATE",
        votes_for_ejected=5,
        skip_votes=1,
        roster_impostor_count=2,
    )
    history.record(
        end_tick=20,
        ejected_id=None,
        votes_for_ejected=0,
        skip_votes=5,
        roster_impostor_count=2,
    )
    history.record(
        end_tick=30,
        ejected_id="p-7",
        revealed_role="IMPOSTOR",
        votes_for_ejected=4,
        skip_votes=0,
        roster_impostor_count=2,
    )

    assert history.impostors_remaining_after(0) == 2
    assert history.impostors_remaining_after(1) == 2
    assert history.impostors_remaining_after(2) == 1


def test_impostors_remaining_is_underivable_without_the_roster_count() -> None:
    history = MeetingHistory()
    history.record(end_tick=6, ejected_id="p-4")
    assert history.impostors_remaining_after(0) is None
    with pytest.raises(IndexError):
        history.impostors_remaining_after(1)


def test_a_kill_never_moves_the_impostors_remaining_count() -> None:
    # Kills reach memory through perception, never through this channel; the
    # count is a pure function of what the table CONFIRMED by ejection.
    memory = _render_memory()
    memory.episodic.append(
        EpisodicEvent(
            tick=4,
            type="saw_body",
            payload={"body_id": "b-1", "victim_id": "p-9", "room": "CAFETERIA"},
            provenance="observed",
        )
    )
    record_meeting_outcome(
        memory,
        end_tick=14,
        ejected_id=None,
        votes_for_ejected=0,
        skip_votes=5,
        roster_impostor_count=1,
    )
    assert _meetings_block(
        render_for_prompt(
            memory,
        )
    ) == ["Meeting 1 (tick 14): no ejection (5 skip). 1 impostor remains."]


# ---------------------------------------------------------------------------- #
# The disclosure is entitled, and the scanner says so
# ---------------------------------------------------------------------------- #


def test_no_role_appears_before_its_ejection_tick() -> None:
    memory = _render_memory()
    # Rendered BEFORE the meeting concludes: nothing has been folded, so the
    # block is absent and the render names no other player's role at all.
    before = render_for_prompt(
        memory,
    )
    assert "## Meetings so far:" not in before
    assert_memory_render_role_disclosure_is_entitled(
        before, ejection_ticks={}, render_tick=9
    )

    record_meeting_outcome(
        memory,
        end_tick=14,
        ejected_id="p-2",
        revealed_role="IMPOSTOR",
        votes_for_ejected=7,
        skip_votes=1,
        roster_impostor_count=2,
    )
    after = render_for_prompt(
        memory,
    )
    assert "p-2 was an IMPOSTOR" in after
    assert_memory_render_role_disclosure_is_entitled(
        after, ejection_ticks={"p-2": 14}, render_tick=14
    )
    # The SAME render dated before the ejection is a leak, and the gate bites.
    with pytest.raises(AssertionError, match="before their ejection"):
        assert_memory_render_role_disclosure_is_entitled(
            after, ejection_ticks={"p-2": 14}, render_tick=13
        )


# ---------------------------------------------------------------------------- #
# The v3 encoder is untouched
# ---------------------------------------------------------------------------- #


def test_v3_encode_is_inert_to_the_announcement_fields() -> None:
    encoder = TacticalFeatureEncoderV3()
    public_map = _canonical_public_map()
    packet, memory = _encode_fixture(public_map)
    record_meeting_outcome(memory, end_tick=5, ejected_id="p-2")
    record_meeting_outcome(memory, end_tick=9, ejected_id=None)
    two_field = encoder.encode(packet, public_map, memory)

    _packet, announced_memory = _encode_fixture(public_map)
    record_meeting_outcome(
        announced_memory,
        end_tick=5,
        ejected_id="p-2",
        revealed_role="IMPOSTOR",
        votes_for_ejected=6,
        skip_votes=1,
        roster_impostor_count=2,
    )
    record_meeting_outcome(
        announced_memory,
        end_tick=9,
        ejected_id=None,
        votes_for_ejected=0,
        skip_votes=4,
        roster_impostor_count=2,
    )
    announced = encoder.encode(packet, public_map, announced_memory)

    # Not one feature byte moves, and the segment is still exactly three floats.
    assert announced == two_field
    segments = {
        segment.name: segment.size for segment in encoder.feature_layout(public_map)
    }
    assert segments["meeting_history_scalars"] == 3


# ---------------------------------------------------------------------------- #
# The committed-bytes counterfactual
# ---------------------------------------------------------------------------- #

#: What the block would have cost and bought over the four committed sets, keyed
#: by set: (rendered memories, renders that would gain a prior-ejection line,
#: those following at least one IMPOSTOR reveal, those following at least one
#: CREWMATE reveal, ``saw_vent`` observations naming an already-ejected player).
#:
#: A "rendered memory" is one (agent, meeting) pair with at least one recorded
#: LLM call — an agent renders its memory once per meeting and several calls
#: read it. The IMPOSTOR and CREWMATE columns OVERLAP by construction: a render
#: after two ejections of different outcomes counts in both.
#:
#: Both 4p1i sets read zero on the ejection columns and that is the true number,
#: not a gap: a 4p/1i game ends at its first ejection, so no meeting ever follows
#: one.
#:
#: Re-measured on the current bytes (the baseline-7 rows were
#: 120/0/0/0/0, 871/415/410/31/14, 132/0/0/0/0 and 2479/1196/1148/106/45; the
#: baseline-6 rows were 117/0/0/0/0, 971/475/409/139/68, 120/0/0/0/0 and
#: 2726/1324/1187/282/232). The ``saw_vent`` columns keep falling — 14 -> 8 and
#: 45 -> 44 — because the meeting-outcome channel renders the ejection, so a
#: witness has far less occasion to name an already-ejected player.
_COUNTERFACTUAL_CENSUS: Final[dict[str, tuple[int, int, int, int, int]]] = {
    "samples/4p1i": (117, 0, 0, 0, 0),  # was (120, 0, 0, 0, 0)
    "samples/9p2i": (869, 411, 406, 24, 8),  # was (871, 415, 410, 31, 14)
    "ml_corpus/4p1i": (129, 0, 0, 0, 0),  # was (132, 0, 0, 0, 0)
    "ml_corpus/9p2i": (2516, 1186, 1160, 78, 44),  # was (2479, 1196, 1148, 106, 45)
}


def _census_for(sample_dir: Path) -> tuple[int, int, int, int, int]:
    """Re-derive one committed set's counterfactual from its recorded bytes.

    Roles are firewalled out of the replay JSONL, so they are re-derived from the
    seeds through :func:`eval.validity.roles_by_seed` — the deterministic
    re-seeding route the committed report itself takes.
    """

    from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    renders = gained = after_impostor = after_crewmate = stale_vents = 0
    for seed in seeds_on_disk(sample_dir):
        seed_roles = roles[seed]
        ejected_so_far: list[str] = []
        replay = sample_dir / f"replay-seed-{seed}.jsonl"
        for line in replay.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record.get("kind") != "meeting":
                continue
            rendering_agents = {
                call["agent_id"] for call in record.get("llm_calls", ())
            }
            renders += len(rendering_agents)
            prior = [seed_roles[player] for player in ejected_so_far]
            if prior:
                gained += len(rendering_agents)
                if "IMPOSTOR" in prior:
                    after_impostor += len(rendering_agents)
                if "CREWMATE" in prior:
                    after_crewmate += len(rendering_agents)
            for turn in record.get("transcript", {}).get("turns", ()):
                for observation in turn.get("observations", ()):
                    if observation.get("type") != "saw_vent":
                        continue
                    if observation.get("subject") in ejected_so_far:
                        stale_vents += 1
            ejected = record.get("ejected_player_id")
            if ejected is not None:
                ejected_so_far.append(ejected)
    return renders, gained, after_impostor, after_crewmate, stale_vents


@pytest.mark.slow
@pytest.mark.parametrize("set_name", sorted(_COUNTERFACTUAL_CENSUS))
def test_committed_bytes_counterfactual_is_what_the_record_is_judged_against(
    set_name: str,
) -> None:
    sample_dir = {
        "samples/4p1i": SAMPLES_4P1I,
        "samples/9p2i": SAMPLES_9P2I,
        "ml_corpus/4p1i": CORPUS_4P1I,
        "ml_corpus/9p2i": CORPUS_9P2I,
    }[set_name]
    assert _census_for(sample_dir) == _COUNTERFACTUAL_CENSUS[set_name]


@pytest.mark.slow
def test_the_census_totals_reproduce_the_review_counts() -> None:
    renders = sum(row[0] for row in _COUNTERFACTUAL_CENSUS.values())
    gained = sum(row[1] for row in _COUNTERFACTUAL_CENSUS.values())
    stale_vents = sum(row[4] for row in _COUNTERFACTUAL_CENSUS.values())
    assert (renders, gained) == (3631, 1597)  # was (3602, 1611)
    # The re-litigation denominator, re-measured on the baseline-7 bytes: the
    # meeting-outcome channel renders the ejection, so a witness has far less
    # occasion to name an already-ejected player (baseline 6: 300).
    assert stale_vents == 52  # was 59
