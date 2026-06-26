"""Tests for reported-testimony ingest + render (Task 13.5.2).

The content twin of ``tests/agents/test_memory_store.py``: where that file pins
the SCALAR meeting fold, this one pins the CONTENT fold
(``agents/memory/store.py::absorb_reported_testimony`` + the
``render_for_prompt`` reported branch + the alibi-map render). The 2026-06-25
memory diagnosis (workflow ``wg54kfoxy``) root -- "social info is a scalar, not
content" -- is exactly what this lever fixes: public testimony becomes
``provenance="reported"`` episodic content, self-framed as unverified, strictly
below first-hand salience, and the dead ``alibi_map`` is finally populated.
"""

from __future__ import annotations

from typing import Any

import pytest

from agents.memory.episodic import EpisodicEvent
from agents.memory.store import (
    AgentMemory,
    absorb_meeting_evidence,
    absorb_reported_testimony,
    render_for_prompt,
)
from agents.memory.store import (
    # Aliased so pytest does not collect the ``testimony_…`` import as a test
    # (its name starts with "test").
    testimony_as_content_enabled as _flag_enabled,
)
from agents.perception import EVENT_REPORTED_TESTIMONY, PROVENANCE_REPORTED
from meetings.manager import derive_reported_testimony
from meetings.schemas import (
    AccusationClaim,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ReportedStatement,
    SawPlayerObservation,
    VoteBallot,
)


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
        tick=tick, type="self_state", payload=payload, provenance="observed"
    )


def _saw_player_event(
    *, tick: int, player_id: str, room: str = "CAFETERIA", action: str | None = None
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_player",
        payload={"player_id": player_id, "room": room, "action": action},
        provenance="observed",
    )


def _memory_for(
    *,
    agent_id: str = "p-1",
    role: str = "CREWMATE",
    fellow_impostor_ids: tuple[str, ...] | None = None,
    roster_sightings: tuple[str, ...] = ("p-2", "p-3", "p-4", "p-5"),
    self_tick: int = 0,
) -> AgentMemory:
    """An ``AgentMemory`` whose perception has run once (self_state + roster)."""

    memory = AgentMemory()
    memory.episodic.append(
        _self_state_event(
            tick=self_tick,
            agent_id=agent_id,
            role=role,
            fellow_impostor_ids=fellow_impostor_ids,
        )
    )
    for player_id in roster_sightings:
        memory.episodic.append(_saw_player_event(tick=self_tick, player_id=player_id))
    return memory


def _reported_rows(memory: AgentMemory) -> tuple[EpisodicEvent, ...]:
    return tuple(
        event
        for event in memory.episodic.recent(since_tick=0)
        if event.type == EVENT_REPORTED_TESTIMONY
    )


class TestAbsorbReportedTestimony:
    def test_appends_reported_rows_for_other_speakers(self) -> None:
        memory = _memory_for(agent_id="p-1", self_tick=20)
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="saw_player",
                    subject="p-5",
                    from_tick=12,
                    to_tick=12,
                    room="ELECTRICAL",
                ),
            ),
        )

        rows = _reported_rows(memory)
        assert len(rows) == 1
        row = rows[0]
        assert row.provenance == PROVENANCE_REPORTED
        # Meeting-boundary tick: last self_state tick + 1.
        assert row.tick == 21
        assert row.payload["speaker"] == "p-3"
        assert row.payload["subject"] == "p-5"

    def test_own_statements_are_skipped(self) -> None:
        memory = _memory_for(agent_id="p-1")
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-1",  # the recipient's OWN statement
                    kind="accusation",
                    subject="p-5",
                ),
                ReportedStatement(
                    speaker="p-2",
                    kind="accusation",
                    subject="p-5",
                ),
            ),
        )

        rows = _reported_rows(memory)
        assert [row.payload["speaker"] for row in rows] == ["p-2"]

    def test_alibi_map_is_wired(self) -> None:
        memory = _memory_for(agent_id="p-1")
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="alibi",
                    subject="p-2",
                    from_tick=10,
                    to_tick=14,
                    room="MEDBAY",
                ),
            ),
        )

        belief = memory.beliefs.view("p-2")
        assert len(belief.alibis) == 1
        alibi = belief.alibis[0]
        assert alibi.player_id == "p-2"
        assert alibi.room == "MEDBAY"
        assert alibi.tick == 10
        assert alibi.source == "p-3"

    def test_reported_content_is_not_teammate_firewalled(self) -> None:
        # An impostor (p-1, teammate p-2) records a PUBLIC statement that
        # incriminates its own teammate p-2: reported CONTENT is a faithful
        # record of public speech (owner decision), unlike the SCALAR firewall.
        memory = _memory_for(
            agent_id="p-1", role="IMPOSTOR", fellow_impostor_ids=("p-2",)
        )
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="saw_player",
                    subject="p-2",
                    from_tick=9,
                    to_tick=9,
                    room="ELECTRICAL",
                ),
            ),
        )

        rows = _reported_rows(memory)
        assert [row.payload["subject"] for row in rows] == ["p-2"]

    def test_roster_only_drops_unknown_ids(self) -> None:
        memory = _memory_for(agent_id="p-1")
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(speaker="p-3", kind="accusation", subject="ghost-99"),
                ReportedStatement(speaker="ghost-9", kind="accusation", subject="p-2"),
                ReportedStatement(speaker="p-3", kind="accusation", subject="p-2"),
            ),
        )

        rows = _reported_rows(memory)
        assert len(rows) == 1
        assert rows[0].payload["speaker"] == "p-3"
        assert rows[0].payload["subject"] == "p-2"

    def test_is_deterministic_across_repeats(self) -> None:
        statements = (
            ReportedStatement(
                speaker="p-3",
                kind="saw_player",
                subject="p-5",
                from_tick=12,
                to_tick=12,
                room="ELECTRICAL",
            ),
            ReportedStatement(speaker="p-2", kind="accusation", subject="p-4"),
        )
        first = _memory_for(agent_id="p-1")
        second = _memory_for(agent_id="p-1")
        absorb_reported_testimony(first, statements=statements)
        absorb_reported_testimony(second, statements=statements)

        rows_first = [row.payload for row in _reported_rows(first)]
        rows_second = [row.payload for row in _reported_rows(second)]
        assert rows_first == rows_second

    def test_without_self_state_fails_loud(self) -> None:
        with pytest.raises(ValueError):
            absorb_reported_testimony(
                AgentMemory(),
                statements=(
                    ReportedStatement(speaker="p-2", kind="accusation", subject="p-3"),
                ),
            )

    def test_runs_after_scalar_fold_without_breaking_tick_order(self) -> None:
        # The orchestrator runs the scalar fold (appends a meeting-boundary
        # marker at last_tick + 1) and THEN the content fold at the same tick;
        # the episodic store's non-decreasing-tick invariant must hold.
        memory = _memory_for(agent_id="p-1", self_tick=30)
        absorb_meeting_evidence(memory, accused=("p-5",))
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(speaker="p-3", kind="accusation", subject="p-5"),
            ),
        )

        rows = _reported_rows(memory)
        assert rows[0].tick == 31


class TestReportedTestimonyRender:
    def test_reported_line_is_self_framed_unverified(self) -> None:
        memory = _memory_for(agent_id="p-1")
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="saw_player",
                    subject="p-5",
                    from_tick=12,
                    to_tick=12,
                    room="ELECTRICAL",
                ),
            ),
        )

        view = render_for_prompt(memory)
        assert "CLAIM by p-3 (unverified): saw p-5 in ELECTRICAL @ tick 12" in view
        assert "[meeting]" in view

    def test_each_kind_renders(self) -> None:
        memory = _memory_for(agent_id="p-1")
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-2",
                    kind="alibi",
                    subject="p-3",
                    from_tick=10,
                    to_tick=14,
                    room="MEDBAY",
                ),
                ReportedStatement(speaker="p-2", kind="accusation", subject="p-4"),
                ReportedStatement(
                    speaker="p-2",
                    kind="corroboration",
                    subject="p-5",
                    from_tick=11,
                    to_tick=11,
                ),
            ),
        )

        view = render_for_prompt(memory)
        assert "p-3 was in MEDBAY during ticks 10-14" in view
        assert "accused p-4" in view
        assert "backed p-5's account @ tick 11" in view

    def test_alibi_view_renders(self) -> None:
        memory = _memory_for(agent_id="p-1")
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="alibi",
                    subject="p-2",
                    from_tick=10,
                    to_tick=14,
                    room="MEDBAY",
                ),
            ),
        )

        view = render_for_prompt(memory)
        assert "alibi: in MEDBAY at tick 10 per p-3" in view

    def test_budget_tight_render_drops_reported_before_first_hand(self) -> None:
        # First-hand sightings (salience 50) and a reported claim (salience 25)
        # compete under a shrinking budget. Because reported is strictly below
        # first-hand, the FIRST budget at which the reported line disappears must
        # still carry every first-hand sighting -- reported is shed first.
        sightings = ("p-2", "p-3", "p-4", "p-5")
        memory = _memory_for(agent_id="p-1", roster_sightings=sightings)
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="saw_player",
                    subject="p-2",
                    from_tick=4,
                    to_tick=4,
                    room="ELECTRICAL",
                ),
            ),
        )

        full_budget = 1500
        full = render_for_prompt(memory, token_budget=full_budget)
        assert all(f"You saw {pid}" in full for pid in sightings)
        assert "CLAIM by p-3" in full

        # Walk the budget down; the first level that sheds the reported line must
        # still retain all first-hand sightings.
        for budget in range(full_budget, 20, -1):
            tight = render_for_prompt(memory, token_budget=budget)
            if "CLAIM by p-3" not in tight:
                assert all(f"You saw {pid}" in tight for pid in sightings)
                break
        else:  # pragma: no cover - defensive
            raise AssertionError("reported line never dropped as budget shrank")

    def test_flag_off_render_carries_no_reported_or_alibi_artifacts(self) -> None:
        # With the flag OFF the content fold is never called, so a memory built
        # exactly as pre-task renders with no reported / alibi artifacts -- the
        # byte-identity boundary (the full guarantee is verify_samples.sh).
        memory = _memory_for(agent_id="p-1")
        absorb_meeting_evidence(memory, accused=("p-5",))

        view = render_for_prompt(memory)
        assert "CLAIM by" not in view
        assert "alibi:" not in view

    def test_reported_rows_carry_no_role(self) -> None:
        # Reported content is PUBLIC transcript speech; it carries no role
        # (the leak suite invariant), asserted on both payload and render.
        memory = _memory_for(agent_id="p-1")
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="saw_player",
                    subject="p-5",
                    from_tick=12,
                    to_tick=12,
                    room="ELECTRICAL",
                ),
            ),
        )

        for row in _reported_rows(memory):
            assert "role" not in row.payload
            assert "IMPOSTOR" not in str(row.payload)
            assert "CREWMATE" not in str(row.payload)
        view = render_for_prompt(memory)
        claim_lines = [line for line in view.splitlines() if "CLAIM by" in line]
        assert claim_lines
        for line in claim_lines:
            assert "IMPOSTOR" not in line
            assert "CREWMATE" not in line


class TestTestimonyFlag:
    def test_default_is_off(self) -> None:
        assert _flag_enabled(env={}) is False

    def test_unrecognised_values_are_off(self) -> None:
        assert _flag_enabled(env={"AILIBI_TESTIMONY_AS_CONTENT": ""}) is False
        assert _flag_enabled(env={"AILIBI_TESTIMONY_AS_CONTENT": "maybe"}) is False

    def test_truthy_values_are_on(self) -> None:
        for value in ("1", "true", "TRUE", "yes", "on", "On"):
            assert _flag_enabled(env={"AILIBI_TESTIMONY_AS_CONTENT": value}) is True


class TestReviewFixes:
    """PR #198 review fixes: the self-subject finding + Codex P2 comments."""

    def test_self_subject_alibi_is_not_recorded_as_belief_row(self) -> None:
        # A reported alibi ABOUT the recipient (p-1) keeps the episodic CONTENT row
        # but must NOT materialise a self belief/alibi row -- belief rows are about
        # OTHERS and the scalar fold excludes own_id.
        memory = _memory_for(agent_id="p-1", self_tick=4)
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="alibi",
                    subject="p-1",  # the recipient itself
                    from_tick=10,
                    to_tick=12,
                    room="MEDBAY",
                ),
            ),
        )
        assert len(_reported_rows(memory)) == 1  # content row kept
        assert "p-1" not in memory.beliefs.known_players()  # no self belief row
        assert not memory.beliefs.view("p-1").alibis
        assert "p-1: alibi" not in render_for_prompt(memory)

    def test_co_present_companions_render_and_are_roster_gated(self) -> None:
        # A sighting's co_present companions are public "who was with whom"
        # evidence -- carried, roster-gated, and rendered "(with …)".
        memory = _memory_for(agent_id="p-1", self_tick=5)  # known roster p-1..p-5
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="saw_player",
                    subject="p-2",
                    from_tick=8,
                    to_tick=8,
                    room="MEDBAY",
                    co_present=("p-5", "ghost-9", "p-4"),  # ghost-9 not in roster
                ),
            ),
        )
        assert _reported_rows(memory)[0].payload["co_present"] == ["p-4", "p-5"]
        rendered = render_for_prompt(memory)
        assert "(with p-4, p-5)" in rendered
        assert "ghost-9" not in rendered

    def test_rendered_alibis_are_capped_per_subject(self) -> None:
        # The non-elastic §6.6 belief block must not grow unbounded -- only the
        # most-recent few alibis per subject render.
        memory = _memory_for(agent_id="p-1", self_tick=0)
        absorb_reported_testimony(
            memory,
            statements=tuple(
                ReportedStatement(
                    speaker="p-3",
                    kind="alibi",
                    subject="p-2",
                    from_tick=t,
                    to_tick=t,
                    room=f"ROOM{t}",
                )
                for t in (10, 11, 12, 13, 14)
            ),
        )
        rendered = render_for_prompt(memory)
        assert "at tick 14 per p-3" in rendered
        assert "at tick 12 per p-3" in rendered
        assert "at tick 11 per p-3" not in rendered
        assert "at tick 10 per p-3" not in rendered

    def test_derive_then_ingest_round_trip_per_living_agent(self) -> None:
        # Integration across the manager->store boundary (the two halves the
        # orchestrator + replay loops wire per living agent): a meeting where p-3
        # publicly reports seeing the dead victim p-5 and accuses p-2.
        result = MeetingResult(
            meeting_id="m1",
            triggered_by="p-1",
            trigger_tick=10,
            outcome="SKIPPED",
            ejected_player_id=None,
            ballots=tuple(
                VoteBallot(
                    voter=v,
                    target="SKIP",
                    confidence=0.5,
                    primary_reason_id=None,
                    rationale_text="x",
                )
                for v in ("p-1", "p-2", "p-3", "p-4")  # p-5 dead: not a voter
            ),
            transcript=MeetingTranscript(
                turns=(
                    MeetingTurn(
                        turn_id="m1:turn-0",
                        turn_index=0,
                        speaker="p-3",
                        turn_kind="opening",
                        reply_to=None,
                        observations=(
                            SawPlayerObservation(
                                type="saw_player",
                                tick=8,
                                subject="p-5",
                                room="MEDBAY",
                            ),
                        ),
                        claims=(
                            AccusationClaim(
                                type="accusation",
                                against="p-2",
                                confidence=0.7,
                                reason="r",
                            ),
                        ),
                        free_text="...",
                    ),
                )
            ),
        )
        statements = derive_reported_testimony(result)

        # A non-speaking listener (p-1, whose known roster includes the dead p-5)
        # records p-3's public testimony about BOTH subjects.
        listener = _memory_for(agent_id="p-1", self_tick=9)
        absorb_reported_testimony(listener, statements=statements)
        assert {r.payload["subject"] for r in _reported_rows(listener)} == {
            "p-5",
            "p-2",
        }

        # The speaker p-3 never re-records its own statements.
        speaker = _memory_for(agent_id="p-3", self_tick=9)
        absorb_reported_testimony(speaker, statements=statements)
        assert _reported_rows(speaker) == ()
