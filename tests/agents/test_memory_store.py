"""Tests for ``agents/memory/store.py::absorb_meeting_evidence`` (Task 9.8).

The composite-store half of the persistent post-meeting belief path
(DESIGN.md §6.3 Rules 3 + 5, §4.6; audit gp-1 recall): one meeting's
public evidence is folded into the SAME ``AgentMemory.beliefs`` the next
meeting's suspicion graph and §6.6 rendered memory are built from, so an
accusation bump carries forward across meetings and decays between them.
The pure rule math is pinned in ``tests/agents/test_beliefs.py``; this
file pins the store-level wiring -- in-place persistence, the privileged
self-channel guards (own id + role-gated teammates, the 9.3 channel), and
the fail-loud precondition.
"""

from __future__ import annotations

from typing import Any

import pytest

from agents.memory.beliefs import (
    ACCUSATION_SUSPICION_DELTA,
    CORROBORATION_SUSPICION_DELTA,
    MEETING_SUSPICION_DECAY_RATE,
)
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import (
    AgentMemory,
    absorb_meeting_evidence,
    render_for_prompt,
)

_DEFAULT_SUSPICION = 0.5
# The §4.6 eject gate (DESIGN.md §4.6: max suspicion < 0.6 -> MUST-SKIP).
_EJECT_GATE = 0.60


def _self_state_event(
    *,
    tick: int,
    agent_id: str,
    role: str = "CREWMATE",
    room: str = "CAFETERIA",
    fellow_impostor_ids: tuple[str, ...] | None = None,
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "agent_id": agent_id,
        "room": room,
        "role": role,
        "pending_task_id": None,
    }
    if fellow_impostor_ids is not None:
        payload["fellow_impostor_ids"] = fellow_impostor_ids
    return EpisodicEvent(
        tick=tick,
        type="self_state",
        payload=payload,
        provenance="observed",
    )


def _saw_player_event(
    *, tick: int, player_id: str, room: str = "CAFETERIA"
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_player",
        payload={"player_id": player_id, "room": room, "action": None},
        provenance="observed",
    )


def _memory_for(
    *,
    agent_id: str = "p-1",
    role: str = "CREWMATE",
    fellow_impostor_ids: tuple[str, ...] | None = None,
    roster_sightings: tuple[str, ...] = ("p-2", "p-3", "p-4", "p-5"),
) -> AgentMemory:
    """An ``AgentMemory`` whose perception has run once (self_state recorded).

    ``roster_sightings`` records one tick-0 ``saw_player`` row per id --
    the production co-spawn shape (every player sees the full roster in
    the spawn room on the first perception tick), which is what makes the
    Task 10.2 fold filter (:func:`_known_roster_ids`) a no-op on
    real-player evidence in these tests.
    """

    memory = AgentMemory()
    memory.episodic.append(
        _self_state_event(
            tick=0,
            agent_id=agent_id,
            role=role,
            fellow_impostor_ids=fellow_impostor_ids,
        )
    )
    for player_id in roster_sightings:
        memory.episodic.append(_saw_player_event(tick=0, player_id=player_id))
    return memory


class TestAbsorbMeetingEvidencePersistence:
    def test_accusation_bump_persists_in_the_owned_belief_state(self) -> None:
        memory = _memory_for()

        absorb_meeting_evidence(memory, accused=("p-5",))

        # In place: the bump landed on the composite's own BeliefState,
        # not on a throwaway copy (the vote-time contradiction-lift
        # anti-pattern this task replaces).
        assert memory.beliefs.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert memory.beliefs.view("p-5").suspicion < _EJECT_GATE

    def test_accusations_persist_and_accumulate_across_meetings(self) -> None:
        # The contract's persistence pin: meeting 1's bump is still there
        # when meeting 2's fold runs on the same store, so the second
        # consecutive accusation reaches the inclusive 0.60 gate.
        memory = _memory_for()

        absorb_meeting_evidence(memory, accused=("p-5",))
        between_meetings = memory.beliefs.view("p-5").suspicion
        absorb_meeting_evidence(memory, accused=("p-5",))

        assert between_meetings == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert memory.beliefs.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + 2 * ACCUSATION_SUSPICION_DELTA
        )
        assert memory.beliefs.view("p-5").suspicion >= _EJECT_GATE

    def test_unreinforced_bump_decays_across_quiet_meetings(self) -> None:
        memory = _memory_for()
        bumped = _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA

        absorb_meeting_evidence(memory, accused=("p-5",))
        absorb_meeting_evidence(memory, accused=())

        assert memory.beliefs.view("p-5").suspicion == pytest.approx(
            bumped + (_DEFAULT_SUSPICION - bumped) * MEETING_SUSPICION_DECAY_RATE
        )

    def test_corroboration_lowers_persisted_suspicion(self) -> None:
        memory = _memory_for()

        absorb_meeting_evidence(memory, accused=("p-5",))
        absorb_meeting_evidence(memory, accused=(), corroborated=("p-5",))

        assert memory.beliefs.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION
            + ACCUSATION_SUSPICION_DELTA
            - CORROBORATION_SUSPICION_DELTA
        )

    def test_persisted_bump_renders_into_the_next_memory_view(self) -> None:
        # The point of persistence: the §6.6 view the NEXT meeting's
        # prompts are built from carries the accumulated score.
        memory = _memory_for()

        absorb_meeting_evidence(memory, accused=("p-5",))
        absorb_meeting_evidence(memory, accused=("p-5",))

        view = render_for_prompt(memory)
        assert "## Your current beliefs:" in view
        assert "p-5: suspicion 0.60" in view


class TestAbsorbMeetingEvidenceGuards:
    def test_impostor_accrues_no_bump_against_fellow_impostor(self) -> None:
        # The 7.12/9.3 teammate firewall on the accumulator (DESIGN.md
        # §4.7): teammate identity rides the same privileged self_state
        # channel the render guard reads, so an accused teammate adds no
        # row while a non-teammate accused in the same meeting does.
        memory = _memory_for(
            agent_id="p-1", role="IMPOSTOR", fellow_impostor_ids=("p-2",)
        )

        absorb_meeting_evidence(memory, accused=("p-2", "p-5"))

        assert "p-2" not in memory.beliefs.known_players()
        assert memory.beliefs.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )

    def test_teammate_guard_is_role_gated_to_impostor(self) -> None:
        # Defensive mirror of the render guard's role gate: a crewmate
        # whose self_state somehow carried fellow ids must NOT acquire a
        # teammate shield -- the listed player is bumped like anyone else.
        memory = _memory_for(
            agent_id="p-1", role="CREWMATE", fellow_impostor_ids=("p-2",)
        )

        absorb_meeting_evidence(memory, accused=("p-2",))

        assert memory.beliefs.view("p-2").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )

    def test_own_id_never_materialises_a_self_row(self) -> None:
        # A self-accusation in the transcript bumps everyone else's view
        # of the speaker; the speaker's own store holds no self row.
        memory = _memory_for(agent_id="p-1")

        absorb_meeting_evidence(memory, accused=("p-1",), corroborated=("p-1",))

        assert memory.beliefs.known_players() == ()

    def test_absorb_before_perception_fails_loud(self) -> None:
        # No self_state -> the self-subject guard cannot run; a meeting
        # before perception is a wiring bug (mirrors render_for_prompt).
        with pytest.raises(ValueError, match="perception must run"):
            absorb_meeting_evidence(AgentMemory(), accused=("p-5",))

    def test_absorb_without_agent_id_fails_loud(self) -> None:
        # A pre-9.3-shaped self_state payload (no ``agent_id``) carries a
        # role but not the recipient's own id; the fold must not guess.
        memory = AgentMemory()
        memory.episodic.append(
            EpisodicEvent(
                tick=0,
                type="self_state",
                payload={
                    "room": "CAFETERIA",
                    "role": "CREWMATE",
                    "pending_task_id": None,
                },
                provenance="observed",
            )
        )

        with pytest.raises(ValueError, match="agent_id"):
            absorb_meeting_evidence(memory, accused=("p-5",))


class TestRosterFilteredFoldAndRender:
    """Task 10.2 (DESIGN.md §6.3, §6.6; audit gp-6 C-C-8, H-H-6).

    The agents-side defense-in-depth behind the meeting-layer chokepoint:
    the post-meeting fold and the §6.6 belief rows are filtered to the
    agent's engine-witnessed player-id set, so a hallucinated structural
    id (a game id, a turn id, a free-text phrase) neither materialises a
    persistent belief row nor renders into any prompt surface -- even if
    a future claim type slips one past the meeting layer.
    """

    def test_garbage_subjects_never_materialise_belief_rows(self) -> None:
        # The audit's three garbage shapes, one per evidence channel: a
        # game id accused, a turn id corroborated (seed 12 m0's shape),
        # a free-text phrase contradicted. None may grow a row; the
        # roster subjects folded alongside them land normally.
        memory = _memory_for()

        absorb_meeting_evidence(
            memory,
            accused=("headless-seed-9", "p-5"),
            corroborated=("headless-seed-12:meeting-0:turn-0", "p-3"),
            contradicted=("p-2 dead",),
        )

        assert set(memory.beliefs.known_players()) == {"p-3", "p-5"}
        assert memory.beliefs.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert memory.beliefs.view("p-3").suspicion == pytest.approx(
            _DEFAULT_SUSPICION - CORROBORATION_SUSPICION_DELTA
        )

    def test_seed12_garbage_row_shape_cannot_reach_any_prompt_surface(self) -> None:
        # The seed-12 m2 shape end-to-end: m0's fold corroborated the
        # turn id "headless-seed-12:meeting-0:turn-0", materialising a
        # 0.45 row that decayed to 0.46 and rendered inside m2's vote
        # prompts (both the §6.6 beliefs block and the suspicion-graph
        # block snapshot ``beliefs.known_players()``). Under the filter
        # the row never exists, so NO snapshot of this store -- the §6.6
        # render here, ``suspicion_graph_for_meeting`` in the
        # orchestrator -- can carry it into a vote prompt.
        memory = _memory_for()

        absorb_meeting_evidence(
            memory,
            accused=(),
            corroborated=("headless-seed-12:meeting-0:turn-0", "p-4"),
        )
        absorb_meeting_evidence(memory, accused=())  # the quiet decay round

        assert "headless-seed-12:meeting-0:turn-0" not in memory.beliefs.known_players()
        view = render_for_prompt(memory)
        assert "headless-seed-12" not in view
        assert "p-4: suspicion" in view

    def test_render_filters_a_pre_polluted_store_to_roster_rows(self) -> None:
        # The render-side backstop is independent of the fold: a garbage
        # row already in the store (written before this task, or by a
        # hypothetical future write path the fold filter does not cover)
        # still cannot render -- roster rows are untouched.
        memory = _memory_for()
        memory.beliefs.adjust_suspicion(
            "headless-seed-12:meeting-0:turn-0", delta=-0.04
        )
        memory.beliefs.adjust_suspicion("p-5", delta=0.2)

        view = render_for_prompt(memory)

        assert "headless-seed-12" not in view
        assert "- p-5: suspicion 0.70" in view

    def test_dead_roster_player_rows_still_render(self) -> None:
        # "Roster ids" means the GAME roster, living and dead: the agent
        # witnessed p-5 at spawn, so a belief row about the now-dead p-5
        # (their body discovered later) keeps rendering -- liveness is
        # the meeting chokepoint's rule, never the render filter's.
        memory = _memory_for(roster_sightings=("p-5",))
        memory.episodic.append(
            EpisodicEvent(
                tick=7,
                type="saw_body",
                payload={"body_id": "body-p-5-7", "victim_id": "p-5", "room": "MEDBAY"},
                provenance="observed",
            )
        )
        memory.beliefs.adjust_suspicion("p-5", delta=0.2)

        assert "- p-5: suspicion 0.70" in render_for_prompt(memory)

    def test_render_without_self_channel_is_unfiltered(self) -> None:
        # Pre-9.3 fixture shape (no ``agent_id`` on self_state): the
        # roster is underivable, so the filter is inert and the render is
        # byte-identical to today -- the same degradation contract as the
        # 9.3 self-subject guard. Production is never in this state
        # (perception records the id every tick).
        memory = AgentMemory()
        memory.episodic.append(
            EpisodicEvent(
                tick=0,
                type="self_state",
                payload={
                    "room": "CAFETERIA",
                    "role": "CREWMATE",
                    "pending_task_id": None,
                },
                provenance="observed",
            )
        )
        memory.beliefs.adjust_suspicion("not-a-roster-id", delta=0.2)

        assert "- not-a-roster-id: suspicion 0.70" in render_for_prompt(memory)
