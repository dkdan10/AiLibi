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
    ContradictionRef,
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
    pending_task_id: str | None = None,
    owned_task_ids: tuple[str, ...] | None = None,
    fellow_impostor_ids: tuple[str, ...] | None = None,
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "agent_id": agent_id,
        "room": room,
        "role": role,
        "pending_task_id": pending_task_id,
    }
    if owned_task_ids is not None:
        payload["owned_task_ids"] = owned_task_ids
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

        # The STORED belief carries the full accumulated score (two accusations,
        # 0.5 + 0.05 + 0.05 = 0.60) -- persistence is a fold-level fact.
        assert memory.beliefs.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + 2 * ACCUSATION_SUSPICION_DELTA
        )

        view = render_for_prompt(memory)
        assert "## Your current beliefs:" in view
        # The RENDER clamps it one notch to 0.59: the accumulated 0.60 is entirely
        # SOFT (two accusation bumps, no hard/grounded component), so the Task-16.4
        # J1 hard-evidence render gate -- unconditional since the Task-16.17 close --
        # renders a soft-only at-or-over-gate row one display notch below the §4.6
        # eject gate. The stored scalar above is untouched; only the read-site clamps.
        assert "p-5: suspicion 0.59" in view


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
    the post-meeting fold (inputs filtered, pre-existing non-roster rows
    purged) and both §6.6 sections (belief rows and open-contradiction
    lines) are filtered to the agent's engine-witnessed player-id set, so
    a hallucinated structural id (a game id, a turn id, a free-text
    phrase) neither materialises a persistent belief row, nor survives a
    fold, nor renders into any prompt surface -- even if a future claim
    type slips one past the meeting layer.
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

    def test_render_filters_non_roster_contradiction_lines_too(self) -> None:
        # Both §6.6 sections are covered (Codex review, PR #140): an
        # inconsistency recorded on a garbage row cannot surface through
        # "## Open contradictions" either -- while one recorded on a
        # roster row renders as before.
        memory = _memory_for()
        memory.beliefs.record_contradiction(
            "headless-seed-12:meeting-0:turn-0",
            ContradictionRef(
                summary="phantom subject headless-seed-12:meeting-0:turn-0 conflict",
                left_ref="alibi:garbage",
                right_ref="sighting:garbage",
            ),
        )
        memory.beliefs.record_contradiction(
            "p-5",
            ContradictionRef(
                summary="p-5 alibi conflict around tick 7",
                left_ref="alibi:p-5",
                right_ref="sighting:p-3:p-5",
            ),
        )

        view = render_for_prompt(memory)

        assert "headless-seed-12" not in view
        assert "- p-5 alibi conflict around tick 7" in view

    def test_pre_polluted_store_self_heals_at_the_first_fold(self) -> None:
        # The fold's output-side purge (Codex review, PR #140): a garbage
        # row that somehow predates the filters is DELETED from the store
        # by the next post-meeting fold -- so every downstream snapshot,
        # including the vote prompt's suspicion graph
        # (``suspicion_graph_for_meeting`` iterates ``known_players()``),
        # carries roster ids only from that fold onward.
        memory = _memory_for()
        memory.beliefs.adjust_suspicion(
            "headless-seed-12:meeting-0:turn-0", delta=-0.04
        )

        absorb_meeting_evidence(memory, accused=("p-5",))

        assert memory.beliefs.known_players() == ("p-5",)

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


class TestImpostorPretendTaskCompletionGate:
    """The completion inference is crewmate-only (Task 10.14; Codex review,
    PR #155). An IMPOSTOR's ``pending_task_id`` is a fabricated blend target that
    rotates across a per-seat set and never completes, so a change in it must NOT
    render a "You completed ..." observation — else the blend would manufacture a
    ``completed_task`` alibi and corrupt the meeting/eval evidence. The crewmate
    path (a real pending change IS a completion) is unchanged.
    """

    def test_impostor_pending_change_mints_no_completed_task(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=0,
                agent_id="p-3",
                role="IMPOSTOR",
                pending_task_id="align_engine_output",
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=6,
                agent_id="p-3",
                role="IMPOSTOR",
                pending_task_id="analyze_specimen",
            )
        )

        view = render_for_prompt(memory)

        assert "You completed" not in view

    def test_a_crewmate_completion_leaves_the_owned_set_and_renders(self) -> None:
        # The completion is minted from the tasks that LEAVE the owned set, so
        # the crew fixture carries one (baseline 6 inferred it from the changed
        # pending id alone, which a redistributed instance could fake).
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=0,
                agent_id="p-1",
                role="CREWMATE",
                pending_task_id="swipe_card",
                owned_task_ids=("submit_scan", "swipe_card"),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=6,
                agent_id="p-1",
                role="CREWMATE",
                pending_task_id="submit_scan",
                owned_task_ids=("submit_scan",),
            )
        )

        view = render_for_prompt(memory)

        assert "You completed swipe_card" in view


def _own_kill_event(*, tick: int, victim_id: str, room: str) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="own_kill",
        payload={"victim_id": victim_id, "room": room},
        provenance="observed",
    )


def _saw_body_event(
    *, tick: int, body_id: str, victim_id: str, room: str
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_body",
        payload={"body_id": body_id, "victim_id": victim_id, "room": room},
        provenance="observed",
    )


class TestOwnKillRender:
    """The killer's own kill renders as a privileged self-channel line and
    suppresses the self-victim "discovered body" line (Task 11.3, DESIGN.md
    §1.3, §6.2; experiments/lab/report-memory-fix-probe.md). The engine excludes
    a killer from its own kill's witnesses, so the body it made would otherwise
    surface only through the ordinary ``saw_body`` channel as a discovery -- the
    killer narrating finding the body it created. Legibility only: the
    memory-fix probe falsified this as a survival/deflection lever.
    """

    def test_killer_memory_shows_kill_line_not_self_victim_body(self) -> None:
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", role="IMPOSTOR")
        )
        # The kill the impostor committed this tick (privileged self channel).
        memory.episodic.append(_own_kill_event(tick=4, victim_id="p-2", room="REACTOR"))
        # The body it made surfaces through the ordinary saw_body channel -- it
        # must be suppressed in favour of the kill line above.
        memory.episodic.append(
            _saw_body_event(
                tick=4, body_id="body-p-2-4", victim_id="p-2", room="REACTOR"
            )
        )

        view = render_for_prompt(memory)

        assert "[tick 4] You (IMPOSTOR) killed p-2 in REACTOR." in view
        assert "You discovered p-2's body" not in view

    def test_other_bodies_still_render_for_the_killer(self) -> None:
        # Only the killer's OWN victim is suppressed; a body it genuinely
        # stumbles on (made by someone else) renders normally.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", role="IMPOSTOR")
        )
        memory.episodic.append(_own_kill_event(tick=4, victim_id="p-2", room="REACTOR"))
        memory.episodic.append(
            _saw_body_event(
                tick=4, body_id="body-p-2-4", victim_id="p-2", room="REACTOR"
            )
        )
        memory.episodic.append(
            _saw_body_event(
                tick=6, body_id="body-p-9-6", victim_id="p-9", room="STORAGE"
            )
        )

        view = render_for_prompt(memory)

        assert "You (IMPOSTOR) killed p-2 in REACTOR." in view
        assert "You discovered p-2's body" not in view
        assert "[tick 6] You discovered p-9's body in STORAGE." in view

    def test_self_victim_suppression_survives_body_appended_before_kill(
        self,
    ) -> None:
        # Append order independence (the up-front victim collection): even when
        # the self-victim saw_body row precedes the own_kill row, the discovery
        # line is suppressed and the kill line renders.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", role="IMPOSTOR")
        )
        memory.episodic.append(
            _saw_body_event(
                tick=4, body_id="body-p-2-4", victim_id="p-2", room="REACTOR"
            )
        )
        memory.episodic.append(_own_kill_event(tick=4, victim_id="p-2", room="REACTOR"))

        view = render_for_prompt(memory)

        assert "You (IMPOSTOR) killed p-2 in REACTOR." in view
        assert "You discovered p-2's body" not in view


def _saw_player_in(
    *, tick: int, player_id: str, room: str, action: str | None = None
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_player",
        payload={"player_id": player_id, "room": room, "action": action},
        provenance="observed",
    )


class TestSameRoomCoPresenceRender:
    """Task 13.9 co-presence: each ordinary sighting line names the OTHER subjects
    the observer saw in the same room on the same tick -- a pure render of the
    episodic ``saw_player`` log so the model states reliable co-presence (the
    two-source material the inferential detector needs). The §4.7 suppressions are
    mirrored, so a self-subject or a teammate-at-a-kill-window is never named.
    """

    def test_co_present_sightings_name_the_other_companions(self) -> None:
        # One tick, one room, three subjects -> each line lists the other two
        # (sorted). A single tick has no consecutive pair, so no transition fires
        # and the lines isolate the co-presence suffix.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        for player_id in ("p-2", "p-3", "p-4"):
            memory.episodic.append(
                _saw_player_in(tick=3, player_id=player_id, room="STORAGE")
            )

        view = render_for_prompt(memory)

        assert "[tick 3] You saw p-2 in STORAGE (with p-3, p-4)." in view
        assert "[tick 3] You saw p-3 in STORAGE (with p-2, p-4)." in view
        assert "[tick 3] You saw p-4 in STORAGE (with p-2, p-3)." in view

    def test_solitary_sighting_has_no_companion_suffix(self) -> None:
        # A lone sighting renders byte-identically to the pre-13.9 output.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-2", room="STORAGE"))

        view = render_for_prompt(memory)

        assert "[tick 3] You saw p-2 in STORAGE." in view
        assert "(with" not in view

    def test_co_presence_is_scoped_to_one_tick_and_room(self) -> None:
        # Subjects seen in the same room but on DIFFERENT ticks are not companions.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-2", room="STORAGE"))
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-3", room="ADMIN"))

        view = render_for_prompt(memory)

        # Same tick, DIFFERENT room -> not co-present.
        assert "[tick 3] You saw p-2 in STORAGE." in view
        assert "[tick 3] You saw p-3 in ADMIN." in view
        assert "(with" not in view

    def test_co_presence_carries_through_an_active_task_sighting(self) -> None:
        # The "with …" suffix also rides the active-action sighting line (the
        # observed-activity stamp): "You saw p-2 task in STORAGE (with p-3)."
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(
            _saw_player_in(tick=3, player_id="p-2", room="STORAGE", action="task")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-3", room="STORAGE"))

        view = render_for_prompt(memory)

        assert "[tick 3] You saw p-2 task in STORAGE (with p-3)." in view

    def test_self_subject_is_never_named_as_a_companion(self) -> None:
        # Defensive (the service never lists the recipient in its own
        # visible_players): a stray self-subject sighting is dropped from both the
        # sighting line and every companion list.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-1", room="STORAGE"))
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-2", room="STORAGE"))

        view = render_for_prompt(memory)

        assert "You saw p-1" not in view
        assert "[tick 3] You saw p-2 in STORAGE." in view
        assert "(with" not in view

    def test_impostor_co_presence_excludes_a_teammate_at_a_kill_window(self) -> None:
        # The §4.7 own-goal guard reaches co-presence too: an impostor observer's
        # fellow seen at a body's room/tick is suppressed from the sighting AND
        # from any companion list, so the impostor's testimony never places the
        # teammate at the scene -- not even via "with …".
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=4,
                agent_id="p-1",
                role="IMPOSTOR",
                room="REACTOR",
                fellow_impostor_ids=("p-2",),
            )
        )
        memory.episodic.append(_saw_player_in(tick=4, player_id="p-2", room="REACTOR"))
        memory.episodic.append(_saw_player_in(tick=4, player_id="p-3", room="REACTOR"))
        memory.episodic.append(
            _saw_body_event(
                tick=4, body_id="body-p-9-4", victim_id="p-9", room="REACTOR"
            )
        )

        view = render_for_prompt(memory)

        assert "You saw p-2" not in view
        assert "(with p-2" not in view
        assert "[tick 4] You saw p-3 in REACTOR." in view


class TestWithinVisionTransitionRender:
    """Task 13.9 within-vision transitions: entry/exit at the observer's OWN room,
    from consecutive ``saw_player`` deltas while the observer is stationary. The
    observer never sees the adjacent origin/destination (room-only), so the full
    trajectory only emerges when meeting testimony is combined.
    """

    def test_entered_and_left_are_rendered_at_the_observer_room(self) -> None:
        # Observer stationary in STORAGE across ticks 3-5; p-2 absent at 3, present
        # at 4 (entered), absent at 5 (left).
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=4, player_id="p-2", room="STORAGE"))
        memory.episodic.append(
            _self_state_event(tick=5, agent_id="p-1", room="STORAGE")
        )

        view = render_for_prompt(memory)

        assert "[tick 4] p-2 entered STORAGE." in view
        assert "[tick 5] p-2 left STORAGE." in view
        assert "[tick 4] You saw p-2 in STORAGE." in view

    def test_observer_movement_does_not_fabricate_a_transition(self) -> None:
        # p-2 "disappears" only because the OBSERVER left STORAGE, not because p-2
        # moved -- no transition may be attributed across the observer's own move.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-2", room="STORAGE"))
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", room="ENGINEERING")
        )

        view = render_for_prompt(memory)

        assert "left" not in view
        assert "entered" not in view

    def test_a_tick_gap_breaks_the_transition_delta(self) -> None:
        # Non-adjacent ticks (e.g. across a meeting) cannot be a clean delta.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-2", room="STORAGE"))
        memory.episodic.append(
            _self_state_event(tick=7, agent_id="p-1", room="STORAGE")
        )

        view = render_for_prompt(memory)

        assert "left" not in view
        assert "entered" not in view

    def test_co_presence_and_transitions_render_together(self) -> None:
        # A combined scene: at tick 4 the observer sees p-2 and p-3 together
        # (co-presence), and across tick 3->4 both entered the observer's room.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=4, player_id="p-2", room="STORAGE"))
        memory.episodic.append(_saw_player_in(tick=4, player_id="p-3", room="STORAGE"))

        view = render_for_prompt(memory)

        assert "[tick 4] You saw p-2 in STORAGE (with p-3)." in view
        assert "[tick 4] You saw p-3 in STORAGE (with p-2)." in view
        assert "[tick 4] p-2 entered STORAGE." in view
        assert "[tick 4] p-3 entered STORAGE." in view

    def test_transition_excludes_a_teammate_at_a_kill_window(self) -> None:
        # The §4.7 guard reaches transitions too: a fellow impostor at a body's
        # room/tick produces no entered/left line in the impostor's own memory.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(
                tick=3,
                agent_id="p-1",
                role="IMPOSTOR",
                room="REACTOR",
                fellow_impostor_ids=("p-2",),
            )
        )
        memory.episodic.append(
            _self_state_event(
                tick=4,
                agent_id="p-1",
                role="IMPOSTOR",
                room="REACTOR",
                fellow_impostor_ids=("p-2",),
            )
        )
        memory.episodic.append(_saw_player_in(tick=4, player_id="p-2", room="REACTOR"))
        memory.episodic.append(
            _saw_body_event(
                tick=4, body_id="body-p-9-4", victim_id="p-9", room="REACTOR"
            )
        )

        view = render_for_prompt(memory)

        assert "p-2 entered" not in view
        assert "p-2 left" not in view

    def test_a_kill_in_the_room_does_not_render_a_false_left(self) -> None:
        # Codex review: a subject seen at N but gone at N+1 because it was KILLED
        # in the observer's room (dead -> dropped from visible_players, body now
        # visible) did NOT leave. The "left" must be suppressed -- the body
        # discovery is the truthful testimony and a false departure would corrupt
        # path reconstruction. The observer stays put in STORAGE across 3->4.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-2", room="STORAGE"))
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(
            _saw_body_event(
                tick=4, body_id="body-p-2-4", victim_id="p-2", room="STORAGE"
            )
        )

        view = render_for_prompt(memory)

        assert "p-2 left STORAGE" not in view
        assert "[tick 4] You discovered p-2's body in STORAGE." in view

    def test_a_departure_still_renders_when_the_body_is_elsewhere(self) -> None:
        # The kill-in-place guard is room-scoped: a subject who genuinely LEFT the
        # observer's room (and whose body, if any, is in a room the observer cannot
        # see) still yields a truthful "left". Here p-2 leaves STORAGE at tick 4
        # with no body visible in STORAGE, so the departure renders.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-2", room="STORAGE"))
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", room="STORAGE")
        )

        view = render_for_prompt(memory)

        assert "[tick 4] p-2 left STORAGE." in view

    def test_no_transition_is_inferred_across_a_meeting_boundary(self) -> None:
        # Codex review: a player ejected/removed at a meeting vanishes with no body
        # and no gameplay movement, and gameplay resumes ADJACENT to the pre-meeting
        # tick (apply_meeting_result: working.tick + 1), so the tick-gap guard
        # cannot see the boundary. absorb_meeting_evidence -- the per-living-agent
        # post-meeting hook the live orchestrator AND the replay loader both call --
        # records the boundary at the resume tick, and no delta across it becomes a
        # transition. The observer stays in STORAGE across the boundary.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=3, player_id="p-2", room="STORAGE"))
        # A meeting concludes (p-2 is ejected). Records the boundary at tick 4.
        absorb_meeting_evidence(memory, accused=("p-2",))
        # Gameplay resumes at tick 4: observer still in STORAGE, p-2 gone (ejected,
        # no body) -- a removal, not a departure.
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", room="STORAGE")
        )

        view = render_for_prompt(memory)

        assert "p-2 left STORAGE" not in view
        assert "p-2 entered" not in view

    def test_transitions_resume_after_a_meeting_boundary(self) -> None:
        # The boundary guard is narrow: only the pair that SPANS the meeting is
        # skipped. A genuine departure on a later, non-spanning pair still renders.
        memory = AgentMemory()
        memory.episodic.append(
            _self_state_event(tick=3, agent_id="p-1", room="STORAGE")
        )
        absorb_meeting_evidence(memory, accused=())  # boundary recorded at tick 4
        memory.episodic.append(
            _self_state_event(tick=4, agent_id="p-1", room="STORAGE")
        )
        memory.episodic.append(_saw_player_in(tick=4, player_id="p-3", room="STORAGE"))
        memory.episodic.append(
            _self_state_event(tick=5, agent_id="p-1", room="STORAGE")
        )

        view = render_for_prompt(memory)

        # The (4, 5) pair does not span the boundary (which sits at tick 4).
        assert "[tick 5] p-3 left STORAGE." in view


def _byte_fixture_memory() -> AgentMemory:
    """A fixed store exercising the render's channels: roster, movement, a body.

    Deterministic and hand-built — no RNG, no replay walk — so the rendered
    Markdown below is a constant a reader can diff, not a number to re-derive.
    """

    memory = _memory_for()
    memory.episodic.append(
        _self_state_event(
            tick=3, agent_id="p-1", room="ELECTRICAL", pending_task_id="swipe_card"
        )
    )
    memory.episodic.append(
        _saw_player_event(tick=3, player_id="p-2", room="ELECTRICAL")
    )
    memory.episodic.append(_self_state_event(tick=5, agent_id="p-1", room="ELECTRICAL"))
    memory.episodic.append(
        _saw_body_event(tick=5, body_id="b-1", victim_id="p-3", room="ELECTRICAL")
    )
    absorb_meeting_evidence(memory, accused=("p-2",))
    return memory


# The bytes :func:`_byte_fixture_memory` renders to. Committed, not recomputed:
# an expected value derived at assert time from the code under test would agree
# with any change it made.
_EXPECTED_FIXTURE_RENDER = """\
## Your role: CREWMATE

## Where you were:
- Your route (t = tick): CAFETERIA t0 -> (no record) -> ELECTRICAL t3 -> (no record) -> ELECTRICAL t5

## Recent observations (most salient first):
- [tick 5] You discovered p-3's body in ELECTRICAL.
- [tick 3] You saw p-2 in ELECTRICAL (moved from CAFETERIA, last seen there at tick 0).
- [tick 0] You saw every other player in CAFETERIA: p-2, p-3, p-4, p-5.

## Your current beliefs:
- p-2: suspicion 0.55
"""


class TestRenderIsByteIdenticalOverAFixture:
    """The §6.6 rendered view is untouched by how ``recent()`` finds its window.

    ``render_for_prompt`` reads the episodic log through ``recent(since_tick=0)``
    a dozen times per call; the window is now bisected and its whole-log answer
    cached. This is the render-side proof that nothing about the prompt bytes
    moved with it (the recorded-replay proof is scripts/verify_samples.sh).
    """

    def test_render_matches_the_committed_bytes(self) -> None:
        assert render_for_prompt(_byte_fixture_memory()) == _EXPECTED_FIXTURE_RENDER

    def test_the_committed_bytes_discriminate(self) -> None:
        # The constant is a gate, not decoration: one more observed row in the
        # fixture store must break it.
        memory = _byte_fixture_memory()
        memory.episodic.append(
            _saw_player_event(tick=6, player_id="p-4", room="ELECTRICAL")
        )
        assert render_for_prompt(memory) != _EXPECTED_FIXTURE_RENDER

    def test_repeated_renders_of_one_store_are_stable(self) -> None:
        # The cached whole-log tuple is shared across reads within one render
        # and across renders; neither may make the second call differ.
        memory = _byte_fixture_memory()
        assert render_for_prompt(memory) == render_for_prompt(memory)
