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

import functools
import itertools
import tempfile
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final, NamedTuple

import pytest

import agents.memory.store as store
from agents.memory.beliefs import AlibiClaim as BeliefAlibiClaim
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    _MAX_RENDERED_ALIBIS,
    _MAX_RENDERED_ALIBIS_FROM_OTHERS,
    _build_observations,
    _estimate_tokens,
    _format_alibi_suffix,
    _latest_self_guard_fields,
    absorb_meeting_evidence,
    absorb_reported_testimony,
    render_for_prompt,
)
from agents.perception import EVENT_REPORTED_TESTIMONY, PROVENANCE_REPORTED
from engine.world import load_canonical_map
from eval.evidence_honesty import (
    _WALK_CONFIG,
    _fold_meeting_into_memories,
    _perceive_tick,
)
from eval.replay_walk import MeetingApplied, MeetingOpened, TickOpened, walk_replay
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from meetings.manager import derive_reported_testimony
from meetings.transcript import canonical_rooms
from observation.service import ObservationService
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    AlibiSegment,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ReportedStatement,
    SawKillObservation,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    VoteBallot,
    WhereaboutsClaim,
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
        # The tick-0 whole-roster group renders as ONE summary line naming every
        # subject (the coalesced render, unconditional since the baseline-7
        # record); baseline 6 rendered one "You saw p-N" line per subject.
        spawn = "- [tick 0] You saw every other player in CAFETERIA: "
        assert spawn + ", ".join(sightings) + "." in full
        assert "CLAIM by p-3" in full

        # Walk the budget down. The reported band outranks bare co-presence, so
        # the ORDER inverted: the level that sheds the first-hand row still
        # carries the reported line, and the reported line is the last standing.
        for budget in range(full_budget, 5, -1):
            tight = render_for_prompt(memory, token_budget=budget)
            if spawn not in tight:
                assert "CLAIM by p-3" in tight
                break
        else:  # pragma: no cover - defensive
            raise AssertionError("the first-hand row never dropped")

    def test_render_without_ingested_testimony_carries_no_reported_or_alibi_artifacts(
        self,
    ) -> None:
        # A memory into which no testimony was ever folded (e.g. a meeting with
        # no structured claims) renders with no reported / alibi artifacts --
        # the artifacts come only from absorb_reported_testimony's input, never
        # from the scalar fold. (Retargeted from the retired flag-OFF
        # byte-identity test; the lever is unconditional since Task 14.9.)
        memory = _memory_for(agent_id="p-1")
        absorb_meeting_evidence(memory, accused=("p-5",))
        absorb_reported_testimony(memory, statements=())

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


# ---------------------------------------------------------------------------- #
# Testimony as CONTENT: the vent body, the speaker, the meeting index
# ---------------------------------------------------------------------------- #

_VENT_SIGHTING: Final[ReportedStatement] = ReportedStatement(
    speaker="p-8",
    kind="saw_vent",
    subject="p-4",
    from_tick=11,
    to_tick=11,
    room="ENGINEERING",
)


def _memory_at_meeting(index: int) -> AgentMemory:
    """A listener's memory with ``index`` meeting boundaries already folded.

    ``absorb_reported_testimony`` counts the boundary markers
    ``absorb_meeting_evidence`` appends, so this is what the live orchestrator
    and the replay loader both hand it.
    """

    memory = _memory_for(
        agent_id="p-1",
        roster_sightings=("p-2", "p-3", "p-4", "p-5", "p-8"),
        self_tick=14,
    )
    for _ in range(index):
        memory.episodic.append(
            EpisodicEvent(
                tick=15,
                type="meeting_boundary",
                payload={},
                provenance="observed",
            )
        )
    return memory


def _testimony_lines(render: str) -> list[str]:
    return [line for line in render.splitlines() if "CLAIM by" in line]


class TestVentSightingSurvivesAsContent:
    def test_the_vent_body_its_room_and_its_tick_all_render(self) -> None:
        memory = _memory_at_meeting(1)
        absorb_reported_testimony(
            memory,
            statements=(_VENT_SIGHTING,),
        )

        assert _testimony_lines(
            render_for_prompt(
                memory,
            )
        ) == [
            "- [tick 15] [meeting 1] CLAIM by p-8 (unverified): "
            "saw p-4 VENT in ENGINEERING @ tick 11."
        ]

    def test_every_reported_line_names_the_meeting_it_was_spoken_at(self) -> None:
        memory = _memory_at_meeting(3)
        absorb_reported_testimony(
            memory,
            statements=(
                _VENT_SIGHTING,
                ReportedStatement(speaker="p-3", kind="accusation", subject="p-2"),
            ),
        )

        lines = _testimony_lines(
            render_for_prompt(
                memory,
            )
        )
        assert all("[meeting 3]" in line for line in lines)
        assert (
            "- [tick 15] [meeting 3] CLAIM by p-3 (unverified): accused p-2." in lines
        )

    def test_the_unverified_claim_frame_is_preserved_verbatim(self) -> None:
        # The frame is what makes a listener WEIGH the testimony instead of
        # treating a reported sighting as something it witnessed.
        memory = _memory_at_meeting(1)
        absorb_reported_testimony(
            memory,
            statements=(_VENT_SIGHTING,),
        )
        (line,) = _testimony_lines(
            render_for_prompt(
                memory,
            )
        )
        assert "CLAIM by p-8 (unverified):" in line

    def test_the_vent_statement_becomes_a_row(self) -> None:
        # The reduction is unconditional since the baseline-7 record: a spoken
        # vent sighting reaches the episodic log as CONTENT (baseline 6 dropped
        # it at ingest, so neither the rows nor the observation-id sequence they
        # shift could move).
        memory = _memory_at_meeting(1)
        absorb_reported_testimony(memory, statements=(_VENT_SIGHTING,))
        assert len(_reported_rows(memory)) == 1

    def test_the_vent_statement_changes_the_render(self) -> None:
        accusation = ReportedStatement(speaker="p-3", kind="accusation", subject="p-2")
        with_vent = _memory_at_meeting(1)
        absorb_reported_testimony(with_vent, statements=(_VENT_SIGHTING, accusation))
        without_vent = _memory_at_meeting(1)
        absorb_reported_testimony(without_vent, statements=(accusation,))

        assert render_for_prompt(with_vent) != render_for_prompt(without_vent)
        # And the frame carries the meeting index it was spoken at.
        assert _testimony_lines(render_for_prompt(with_vent)) == [
            "- [tick 15] [meeting 1] CLAIM by p-3 (unverified): accused p-2.",
            "- [tick 15] [meeting 1] CLAIM by p-8 (unverified): "
            "saw p-4 VENT in ENGINEERING @ tick 11.",
        ]

    def test_an_agent_with_no_boundary_record_gets_the_untagged_frame(self) -> None:
        # An agent that folds no meeting evidence holds no meeting-boundary
        # record, so WHICH meeting this is cannot be known. The frame states
        # nothing rather than a fabricated "[meeting 0]".
        memory = _memory_at_meeting(0)
        absorb_reported_testimony(
            memory,
            statements=(_VENT_SIGHTING,),
        )

        (line,) = _testimony_lines(
            render_for_prompt(
                memory,
            )
        )
        assert "[meeting]" in line
        assert "[meeting 0]" not in line
        # The content still survives — only the ordinal is withheld.
        assert "saw p-4 VENT in ENGINEERING @ tick 11." in line


class TestVentSightingDerivation:
    def test_a_spoken_vent_reduces_to_a_saw_vent_statement(self) -> None:
        result = MeetingResult(
            meeting_id="m-1",
            triggered_by="p-8",
            trigger_tick=11,
            outcome="SKIPPED",
            ejected_player_id=None,
            ballots=(
                VoteBallot(
                    voter="p-8",
                    target="SKIP",
                    confidence=0.5,
                    primary_reason_id=None,
                    rationale_text="r",
                ),
            ),
            transcript=MeetingTranscript(
                turns=(
                    MeetingTurn(
                        turn_id="m-1:turn-0",
                        turn_index=0,
                        speaker="p-8",
                        turn_kind="opening",
                        reply_to=None,
                        observations=(
                            SawVentObservation(
                                type="saw_vent",
                                tick=11,
                                subject="p-4",
                                room="ENGINEERING",
                            ),
                        ),
                        claims=(),
                        free_text="...",
                    ),
                )
            ),
        )

        (statement,) = derive_reported_testimony(result)
        assert statement == ReportedStatement(
            speaker="p-8",
            kind="saw_vent",
            subject="p-4",
            from_tick=11,
            to_tick=11,
            room="ENGINEERING",
        )


# --------------------------------------------------------------------------- #
# Reported-row survival under the coalesced render, recounted from the bytes.  #
# --------------------------------------------------------------------------- #

_CORPUS_9P2I: Final[Path] = (
    Path(__file__).resolve().parents[2] / "replays" / "ml_corpus" / "9p2i"
)
_CANDIDATE_BUCKETS: Final[tuple[str, ...]] = ("<=60", "61-100", "101-150", ">150")
# The rendered testimony frame. The meeting-outcome channel tags it with the
# meeting index it was spoken at ("[meeting 3] CLAIM by …"), so the stable part
# is the CLAIM half -- matching on the untagged frame counted the candidate rows
# and none of the rendered ones.
_TESTIMONY_ROW: Final[str] = "CLAIM by "
_SURVIVAL_FLOOR: Final[float] = 0.80


def _candidate_bucket(candidates: int) -> str:
    """Which candidate-count bucket a render belongs to.

    The bucket is a property of the MEMORY, not of the lever: both legs of the
    census are bucketed by the same OFF-path candidate count, so a bucket's two
    numbers are the same renders scored twice.
    """

    if candidates <= 60:
        return "<=60"
    if candidates <= 100:
        return "61-100"
    if candidates <= 150:
        return "101-150"
    return ">150"


class _SurvivalCensus(NamedTuple):
    """Reported rows offered and kept per candidate bucket."""

    offered: Mapping[str, int]
    kept: Mapping[str, int]
    renders: int


def _survival_census(sample_dir: Path) -> _SurvivalCensus:
    """Re-render every meeting's memories at ``DEFAULT_TOKEN_BUDGET``.

    The instrument's own walk, stopped at each ``MeetingOpened`` so the memory is
    the one the speaker actually held there, then rendered from the RETAINED
    composite. Each render is bucketed by how many candidate observations the
    selector saw, and the reported rows it OFFERED are scored against the
    reported rows it KEPT.

    ONE leg. The census was a two-way lever counterfactual until the raised
    reported band graduated; with the lever gone the second render was the same
    call as the first, so the differential could not detect drift and the slow
    corpus walk paid for it twice.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    roles_by_game = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    offered: Counter[str] = Counter()
    kept: Counter[str] = Counter()
    renders = 0

    for seed in seeds_on_disk(sample_dir):
        roles = roles_by_game[seed]
        memories: dict[str, MemoryStore] = {pid: MemoryStore() for pid in roles}
        composites = {pid: AgentMemory(episodic=s) for pid, s in memories.items()}
        audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-survival-")
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
        )
        try:
            for walk_event in walk_replay(
                sample_dir / f"replay-seed-{seed}.jsonl",
                seed=seed,
                num_players=num_players,
                num_impostors=num_impostors,
                tasks_per_crewmate=tasks_per_crewmate,
                game_map=game_map,
                config=_WALK_CONFIG,
            ):
                if isinstance(walk_event, TickOpened):
                    _perceive_tick(walk_event, service=service, memories=memories)
                elif isinstance(walk_event, MeetingOpened):
                    living = sorted(
                        pid
                        for pid, player in walk_event.state.players.items()
                        if player.alive
                    )
                    for pid in living:
                        composite = composites[pid]
                        own, fellows = _latest_self_guard_fields(composite.episodic)
                        candidates = _build_observations(
                            composite.episodic,
                            own_agent_id=own,
                            teammate_ids=(
                                fellows if roles.get(pid) == "IMPOSTOR" else frozenset()
                            ),
                        )
                        rows = sum(
                            1 for obs in candidates if _TESTIMONY_ROW in obs.line
                        )
                        renders += 1
                        if rows == 0:
                            continue
                        bucket = _candidate_bucket(len(candidates))
                        offered[bucket] += rows
                        rendered = render_for_prompt(
                            composite,
                            token_budget=DEFAULT_TOKEN_BUDGET,
                        )
                        kept[bucket] += sum(
                            1
                            for line in rendered.splitlines()
                            if _TESTIMONY_ROW in line
                        )
                elif isinstance(walk_event, MeetingApplied):
                    _fold_meeting_into_memories(walk_event, composites=composites)
        finally:
            service.close()
            audit_dir.cleanup()

    return _SurvivalCensus(
        offered=dict(offered),
        kept=dict(kept),
        renders=renders,
    )


@pytest.fixture(scope="module")
def survival() -> _SurvivalCensus:
    """The reported-row survival census over the committed 9p2i corpus."""

    return _survival_census(_CORPUS_9P2I)


def test_the_bucket_boundaries_partition_the_candidate_counts() -> None:
    # The gate the pins rest on, exercised directly: every boundary lands in the
    # bucket it names, so a shifted edge cannot silently move rows between pins.
    assert [_candidate_bucket(n) for n in (0, 60)] == ["<=60", "<=60"]
    assert [_candidate_bucket(n) for n in (61, 100)] == ["61-100", "61-100"]
    assert [_candidate_bucket(n) for n in (101, 150)] == ["101-150", "101-150"]
    assert [_candidate_bucket(n) for n in (151, 4000)] == [">150", ">150"]


@pytest.mark.slow
def test_reported_rows_survive_in_every_candidate_bucket(
    survival: _SurvivalCensus,
) -> None:
    # Recounted from the committed bytes of replays/ml_corpus/9p2i, the set the
    # C-73 register measured: OFF, reported rows are kept 0 of 4,150 times past 150
    # candidates and 718 of 5,886 in the 101-150 bucket
    # (audits/review-2026-08-19/B/agents-memory.md §2 F2). This recount differs from
    # those figures -- the register sampled 60 games and 1,656 renders, this walks
    # every committed game -- so the shape, not the absolute count, is what carries.
    assert set(survival.offered) == set(_CANDIDATE_BUCKETS)
    assert survival.renders == 2539  # was 2516
    # Both columns re-bucketed at the graduation sweep (Task 20.37) and NEITHER
    # moved in total. The candidate scan calls the private builder directly, and
    # until the sweep that builder's lever parameters DEFAULTED OFF -- so this
    # column counted a candidate set production never built (a ``saw_vent`` row
    # rendered nothing under the OFF default) and, because the same count keys
    # the bucket, it filed each render under an OFF-path bucket too. Deleting the
    # parameters made the scan read the path ``render_for_prompt`` always took.
    assert survival.offered == {
        "<=60": 8983,  # was 11484
        "61-100": 21947,  # was 14982
        "101-150": 16547,  # was 7316
        ">150": 7539,  # was 3341
    }
    # The raised reported band is unconditional since the baseline-7 record, so
    # there is ONE leg to count -- the differential the C-73 register measured is
    # what graduating the lever spent. Kept can exceed offered in a bucket: the
    # candidate scan counts rows the selector was HANDED, and a render can carry
    # a testimony line composed from several candidates.
    # was {"<=60": 11484, "61-100": 14965, "101-150": 7295, ">150": 3214}
    kept = {"<=60": 8983, "61-100": 21612, "101-150": 14824, ">150": 5927}
    assert survival.kept == kept
    # THE no-behaviour-moved statement, recomputed rather than asserted: the
    # sweep re-bucketed the kept rows and minted none. Every kept row comes off
    # ``render_for_prompt``, whose path the sweep did not touch, so on the
    # baseline-7 bytes the TOTAL was the number the pre-sweep buckets summed to
    # (11,707 + 13,622 + 7,074 + 3,331). The offered total legitimately GREW by
    # the saw_vent rows the OFF default used to swallow.
    assert sum(kept.values()) == 51346  # was 36958
    assert sum(survival.offered.values()) == 55016  # was 37123
    # Every bucket clears the survival floor now, including the largest render --
    # the bucket the register measured keeping NO reported row at all.
    for bucket in _CANDIDATE_BUCKETS:
        offered = survival.offered[bucket]
        assert survival.kept[bucket] / offered >= _SURVIVAL_FLOOR, (
            f"{bucket}: kept {survival.kept[bucket]} of {offered}"
        )


# --------------------------------------------------------------------------- #
# The testimony-shapes lever: what the three new kinds do on the INGEST side   #
# --------------------------------------------------------------------------- #

_SHAPES_ON: Final[Mapping[str, str]] = {"AILIBI_TESTIMONY_SHAPES": "1"}


def _shapes_meeting() -> MeetingResult:
    """One meeting whose only content is the three lever-gated shapes."""

    return MeetingResult(
        meeting_id="m-shapes",
        triggered_by="p-2",
        trigger_tick=30,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=tuple(
            VoteBallot(
                voter=voter,
                target="SKIP",
                confidence=0.0,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="skip",
            )
            for voter in ("p-1", "p-2", "p-3", "p-4")
        ),
        transcript=MeetingTranscript(
            turns=(
                MeetingTurn(
                    turn_id="m-shapes:turn-0",
                    turn_index=0,
                    speaker="p-2",
                    turn_kind="opening",
                    reply_to=None,
                    observations=(
                        WhereaboutsClaim(type="whereabouts", tick=11, room="MEDBAY"),
                        SawMoveObservation(
                            type="saw_move",
                            tick=12,
                            subject="p-4",
                            from_room="ADMIN",
                            to_room="LABS",
                        ),
                        SawKillObservation(
                            type="saw_kill", tick=13, subject="p-3", room="REACTOR"
                        ),
                    ),
                    claims=(),
                    free_text="I saw it happen.",
                ),
            )
        ),
    )


class TestTestimonyShapesIngest:
    def test_off_leaves_the_alibi_map_and_the_rows_exactly_as_head_leaves_them(
        self,
    ) -> None:
        # The perturbation the lever's OFF path is entitled to: the SAME fixture
        # meeting, derived with the lever unset, folds nothing at all -- no
        # episodic row, no belief row, no alibi.
        memory = _memory_for(agent_id="p-1", self_tick=20)
        absorb_reported_testimony(
            memory,
            statements=derive_reported_testimony(
                _shapes_meeting(), testimony_shapes=False
            ),
        )

        assert _reported_rows(memory) == ()
        assert memory.beliefs.view("p-2").alibis == ()

    def test_a_whereabouts_feeds_the_alibi_map_exactly_as_an_alibi_does(self) -> None:
        memory = _memory_for(agent_id="p-1", self_tick=20)
        absorb_reported_testimony(
            memory,
            statements=derive_reported_testimony(
                _shapes_meeting(), testimony_shapes=True
            ),
        )

        belief = memory.beliefs.view("p-2")
        assert len(belief.alibis) == 1
        alibi = belief.alibis[0]
        assert (alibi.player_id, alibi.room, alibi.tick, alibi.source) == (
            "p-2",
            "MEDBAY",
            11,
            "p-2",
        )
        # Only the self-placement reaches the map: a witnessed transition and a
        # witnessed kill are sightings of SOMEONE ELSE, not location accounts the
        # subject gave, so neither is a stated alibi.
        assert memory.beliefs.view("p-4").alibis == ()
        assert memory.beliefs.view("p-3").alibis == ()

    def test_the_three_kinds_land_as_reported_rows(self) -> None:
        memory = _memory_for(agent_id="p-1", self_tick=20)
        absorb_reported_testimony(
            memory,
            statements=derive_reported_testimony(
                _shapes_meeting(), testimony_shapes=True
            ),
        )

        rows = _reported_rows(memory)
        assert {row.payload["kind"] for row in rows} == {
            "whereabouts",
            "saw_move",
            "saw_kill",
        }
        assert {row.provenance for row in rows} == {PROVENANCE_REPORTED}
        assert {row.tick for row in rows} == {21}

    def test_the_three_kinds_render_inside_the_unverified_frame(self) -> None:
        memory = _memory_for(agent_id="p-1", self_tick=20)
        absorb_reported_testimony(
            memory,
            statements=derive_reported_testimony(
                _shapes_meeting(), testimony_shapes=True
            ),
        )

        view = render_for_prompt(memory)
        assert "p-2 placed themselves in MEDBAY @ tick 11" in view
        assert "saw p-4 arrive in LABS @ tick 12" in view
        assert "saw p-3 KILL in REACTOR @ tick 13" in view
        # The frame is load-bearing: every one of them reads as a third party's
        # unverified assertion, never as something this agent witnessed.
        for body in (
            "p-2 placed themselves in MEDBAY @ tick 11",
            "saw p-4 arrive in LABS @ tick 12",
            "saw p-3 KILL in REACTOR @ tick 13",
        ):
            line = next(line for line in view.splitlines() if body in line)
            assert "CLAIM by p-2 (unverified):" in line

    def test_the_own_statement_guard_still_drops_a_speakers_own_roll_call(
        self,
    ) -> None:
        # A whereabouts is a SELF-placement, so the own-statement guard is what
        # stops an agent's own roll-call echoing back at it as a third-party
        # claim -- and it fires before the alibi-map write, so no SELF belief row
        # materialises either.
        memory = _memory_for(agent_id="p-2", self_tick=20)
        absorb_reported_testimony(
            memory,
            statements=derive_reported_testimony(
                _shapes_meeting(), testimony_shapes=True
            ),
        )

        assert _reported_rows(memory) == ()
        assert memory.beliefs.view("p-2").alibis == ()

    def test_a_non_roster_speaker_is_still_dropped(self) -> None:
        memory = _memory_for(
            agent_id="p-1", roster_sightings=("p-3", "p-4"), self_tick=20
        )
        absorb_reported_testimony(
            memory,
            statements=derive_reported_testimony(
                _shapes_meeting(), testimony_shapes=True
            ),
        )

        # p-2 was never engine-witnessed by this agent, so neither its
        # self-placement nor its sightings materialise anything.
        assert _reported_rows(memory) == ()
        assert memory.beliefs.view("p-2").alibis == ()

    def test_a_malformed_payload_of_each_new_kind_renders_nothing(self) -> None:
        # The module's defensive ``.get`` convention: a row planted with its room
        # missing renders no line rather than a half-formed one.
        memory = _memory_for(agent_id="p-1", self_tick=20)
        for kind in ("whereabouts", "saw_move", "saw_kill"):
            memory.episodic.append(
                EpisodicEvent(
                    tick=21,
                    type=EVENT_REPORTED_TESTIMONY,
                    payload={
                        "speaker": "p-2",
                        "kind": kind,
                        "subject": "p-3",
                        "meeting_index": 1,
                        "from_tick": 13,
                        "to_tick": 13,
                        "room": None,
                        "co_present": [],
                    },
                    provenance=PROVENANCE_REPORTED,
                )
            )

        view = render_for_prompt(memory)
        assert "CLAIM by p-2" not in view
        # And the gate is not vacuous: the same rows WITH a room do render.
        memory_ok = _memory_for(agent_id="p-1", self_tick=20)
        memory_ok.episodic.append(
            EpisodicEvent(
                tick=21,
                type=EVENT_REPORTED_TESTIMONY,
                payload={
                    "speaker": "p-2",
                    "kind": "saw_kill",
                    "subject": "p-3",
                    "meeting_index": 1,
                    "from_tick": 13,
                    "to_tick": 13,
                    "room": "REACTOR",
                    "co_present": [],
                },
                provenance=PROVENANCE_REPORTED,
            )
        )
        assert "saw p-3 KILL in REACTOR @ tick 13" in render_for_prompt(memory_ok)


# --- Round 5: re-cutting a stay must be invisible to the LISTENER ------------


def _cuts_of_one_stay(stay: AlibiSegment) -> tuple[tuple[AlibiSegment, ...], ...]:
    """Every way of narrating ONE continuous stay as contiguous same-room legs.

    The same enumeration ``tests/meetings/test_contradictions.py`` runs against
    the detectors, restated here because it is what the LISTENER must also be
    blind to: a stay of ``n`` ticks has ``n - 1`` interior boundaries and each
    may be cut or not, so all ``2 ** (n - 1)`` shapes are enumerated -- the
    uncut stay at mask 0 and the all-one-tick legs the operational prompts ask
    for at the last mask.
    """

    boundaries = stay.to_tick - stay.from_tick
    shapes: list[tuple[AlibiSegment, ...]] = []
    for mask in range(1 << boundaries):
        legs: list[AlibiSegment] = []
        start = stay.from_tick
        for offset in range(boundaries):
            if mask >> offset & 1:
                legs.append(
                    AlibiSegment(
                        room=stay.room,
                        from_tick=start,
                        to_tick=stay.from_tick + offset,
                    )
                )
                start = stay.from_tick + offset + 1
        legs.append(AlibiSegment(room=stay.room, from_tick=start, to_tick=stay.to_tick))
        shapes.append(tuple(legs))
    return tuple(shapes)


def _recuts_of(route: tuple[AlibiSegment, ...]) -> tuple[tuple[AlibiSegment, ...], ...]:
    """Every re-cut of ``route``: the cross product of each stay's own cuts."""

    shapes: tuple[tuple[AlibiSegment, ...], ...] = ((),)
    for stay in route:
        shapes = tuple(
            (*prefix, *legs) for prefix in shapes for legs in _cuts_of_one_stay(stay)
        )
    return shapes


def _spellings_of(room: str) -> tuple[str, ...]:
    """Canonically-equal ways the model spells one room (round 6).

    The listener twin of ``tests/meetings/test_contradictions.py``'s helper.
    Case is free text to a model and ``_TRANSITION`` is the token it appends to
    a room it names as transit, so all three of these are ONE place -- three
    labels a speaker may hang on the legs of one continuous stay.
    """

    spellings = (room, room.lower(), f"{room}_TRANSITION")
    assert len({canonical_rooms(spelling) for spelling in spellings}) == 1, room
    return spellings


def _spelled_narrations_of(
    route: tuple[AlibiSegment, ...],
) -> dict[tuple[int, frozenset[str]], list[tuple[AlibiSegment, ...]]]:
    """Every mixed-spelling narration of ``route``, grouped by ACCOUNT.

    One stay at a time: stay ``i`` is restated as every cut of itself under
    every assignment of its canonically-equal spellings, the other stays left
    as the route states them. Narrations in ONE group are the same account said
    the same way, so the listener must hold exactly the same thing; narrations
    in different groups are different WORDINGS of it, whose quoted label
    legitimately differs.
    """

    groups: dict[tuple[int, frozenset[str]], list[tuple[AlibiSegment, ...]]] = {}
    for index, stay in enumerate(route):
        spellings = _spellings_of(stay.room)
        for cut in _cuts_of_one_stay(stay):
            for assignment in itertools.product(spellings, repeat=len(cut)):
                legs = tuple(
                    AlibiSegment(
                        room=room, from_tick=leg.from_tick, to_tick=leg.to_tick
                    )
                    for leg, room in zip(cut, assignment, strict=True)
                )
                groups.setdefault((index, frozenset(assignment)), []).append(
                    (*route[:index], *legs, *route[index + 1 :])
                )
    return groups


_LISTENER: Final[str] = "p-9"
_RECUT_VOTERS: Final[tuple[str, ...]] = ("p-1", "p-2", "p-9")

# The proxy account a rival gives about the speaker: ONE contradicting
# placement, the row a flood of the speaker's own legs used to evict.
_RIVAL_PROXY: Final[tuple[AlibiSegment, ...]] = (
    AlibiSegment(room="MEDBAY", from_tick=8, to_tick=8),
)

_ONE_STAY: Final[tuple[AlibiSegment, ...]] = (
    AlibiSegment(room="STORAGE", from_tick=2, to_tick=8),
)
_TWO_STAYS: Final[tuple[AlibiSegment, ...]] = (
    AlibiSegment(room="STORAGE", from_tick=2, to_tick=6),
    AlibiSegment(room="CAFETERIA", from_tick=7, to_tick=11),
)
# Seed 41's honest walk, the exhibit the whole card is written from: four rooms,
# four stays, and not one of them re-cuttable.
_FOUR_STAYS: Final[tuple[AlibiSegment, ...]] = (
    AlibiSegment(room="ENGINEERING", from_tick=12, to_tick=12),
    AlibiSegment(room="EAST_HALL", from_tick=13, to_tick=13),
    AlibiSegment(room="ADMIN", from_tick=14, to_tick=14),
    AlibiSegment(room="WEST_HALL", from_tick=15, to_tick=15),
)


def _alibi_turn(
    *, index: int, speaker: str, subject: str, route: tuple[AlibiSegment, ...]
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-recut:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "reply",
        reply_to=None,
        observations=(),
        claims=(AlibiClaim(type="alibi", subject=subject, route=route),),
        free_text="",
    )


def _recut_meeting(
    route: tuple[AlibiSegment, ...],
    *,
    rival: tuple[AlibiSegment, ...] = _RIVAL_PROXY,
) -> MeetingResult:
    """The rival's proxy account first, then ``p-1``'s own account of itself."""

    return MeetingResult(
        meeting_id="m-recut",
        triggered_by=_LISTENER,
        trigger_tick=20,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=tuple(
            VoteBallot(
                voter=voter,
                target="SKIP",
                confidence=0.0,
                primary_reason_id=None,
                rationale_text="skip",
            )
            for voter in _RECUT_VOTERS
        ),
        transcript=MeetingTranscript(
            turns=(
                _alibi_turn(index=0, speaker="p-2", subject="p-1", route=rival),
                _alibi_turn(index=1, speaker="p-1", subject="p-1", route=route),
            )
        ),
    )


def _listener_memory() -> AgentMemory:
    """``p-9``'s memory, perception run once over the meeting's roster."""

    return _memory_for(agent_id=_LISTENER, roster_sightings=("p-1", "p-2"), self_tick=0)


class _ListenerReading(NamedTuple):
    """Everything an alibi narration may leave in a listener, as bytes."""

    statements: tuple[ReportedStatement, ...]
    belief_alibis: tuple[tuple[object, ...], ...]
    meeting_lines: tuple[str, ...]
    rendered: str


def _listener_reading(
    route: tuple[AlibiSegment, ...],
    *,
    rival: tuple[AlibiSegment, ...] = _RIVAL_PROXY,
) -> _ListenerReading:
    """Drive the PRODUCTION path and read back what the listener holds."""

    statements = derive_reported_testimony(_recut_meeting(route, rival=rival))
    memory = _listener_memory()
    absorb_reported_testimony(memory, statements=statements)
    rendered = render_for_prompt(memory)
    return _ListenerReading(
        statements=statements,
        belief_alibis=tuple(
            (subject, alibi.room, alibi.tick, alibi.source)
            for subject in sorted(memory.beliefs.known_players())
            for alibi in memory.beliefs.view(subject).alibis
        ),
        meeting_lines=tuple(
            line for line in rendered.splitlines() if "[meeting" in line
        ),
        rendered=rendered,
    )


class TestReCuttingAStayChangesNothingTheListenerHolds:
    """The class-closing property, carried across the meeting/agent firewall.

    ``tests/meetings/test_contradictions.py`` closes the re-cut class for the
    DETECTORS. This closes it for the other consumer that decides a vote: what
    a listener absorbs. The reduction files one ``ReportedStatement`` per
    maximal STAY, so one continuous stay restated as contiguous same-room legs
    lands as ONE belief row and ONE ``[meeting]`` line however it was cut, and
    ``render_for_prompt`` is byte-identical.

    Why it has to be: leg count was a WEIGHT the accused set. The alibi cap
    meant a speaker who itemised their own stay finely enough pushed a rival's
    contradicting placement out of the belief block entirely, and the
    ``[meeting]`` lines are charged against the memory budget, so the flood
    could also shed unrelated memory. The operational prompts ASK for
    fine-grained routes, so an honest one-tick-per-leg narrator did it to their
    own listeners without meaning to.

    Exhaustive, not sampled: every one of the ``2 ** (n - 1)`` narrations of
    each stay, the uncut stay and the all-one-tick legs included.
    """

    @pytest.mark.parametrize(
        ("name", "route"),
        (
            ("one_stay", _ONE_STAY),
            ("two_stays", _TWO_STAYS),
            ("four_stays", _FOUR_STAYS),
        ),
    )
    def test_every_recut_leaves_the_listener_identical(
        self, name: str, route: tuple[AlibiSegment, ...]
    ) -> None:
        baseline = _listener_reading(route)
        recuts = _recuts_of(route)

        # The enumeration must contain the adverse shapes, or the property
        # would be passing on a family of one.
        assert len(recuts) == functools.reduce(
            lambda total, stay: total * (1 << (stay.to_tick - stay.from_tick)),
            route,
            1,
        )
        assert route in recuts
        assert (
            tuple(
                AlibiSegment(room=stay.room, from_tick=tick, to_tick=tick)
                for stay in route
                for tick in range(stay.from_tick, stay.to_tick + 1)
            )
            in recuts
        )

        for recut in recuts:
            assert _listener_reading(recut) == baseline, (
                name,
                [(leg.room, leg.from_tick, leg.to_tick) for leg in recut],
            )

    def test_the_baseline_of_every_shape_carries_the_rival_and_the_speaker(
        self,
    ) -> None:
        # A property comparing two empty renders proves nothing: each shape has
        # to put BOTH voices in the block for the invariance to be about the
        # thing the finding was about.
        for route in (_ONE_STAY, _TWO_STAYS, _FOUR_STAYS):
            reading = _listener_reading(route)
            assert "per p-1" in reading.rendered
            assert "in MEDBAY at tick 8 per p-2" in reading.rendered

    def test_a_genuine_four_room_walk_still_lands_as_four_statements(self) -> None:
        # The stay rule is not a compression of movement: four rooms are four
        # stays, and every one of them reaches the listener.
        statements = [
            statement
            for statement in _listener_reading(_FOUR_STAYS).statements
            if statement.kind == "alibi" and statement.speaker == "p-1"
        ]
        assert [(s.room, s.from_tick, s.to_tick) for s in statements] == [
            ("ENGINEERING", 12, 12),
            ("EAST_HALL", 13, 13),
            ("ADMIN", 14, 14),
            ("WEST_HALL", 15, 15),
        ]


class TestTheRoundFiveListenerExhibits:
    """The two verified round-5 listener findings, as the verifier stated them."""

    def test_a_thirteen_leg_narration_does_not_evict_the_rivals_placement(
        self,
    ) -> None:
        # The repro: p-2 places p-1 in MEDBAY at tick 8; p-1 self-alibis
        # STORAGE 2-14. Stated as the envelope the listener held both rows.
        # Stated as thirteen one-tick legs the belief block read "in STORAGE at
        # tick 12 ...; tick 13 ...; tick 14 per p-1" and the rival's row was
        # GONE from the block p-9 reasons and votes from.
        envelope = (AlibiSegment(room="STORAGE", from_tick=2, to_tick=14),)
        one_tick_legs = tuple(
            AlibiSegment(room="STORAGE", from_tick=tick, to_tick=tick)
            for tick in range(2, 15)
        )

        from_envelope = _listener_reading(envelope)
        from_legs = _listener_reading(one_tick_legs)

        assert (
            "alibi: in STORAGE at tick 2 per p-1; in MEDBAY at tick 8 per p-2"
            in from_envelope.rendered
        )
        assert from_legs.rendered == from_envelope.rendered
        # And the flood of [meeting] lines is gone with it: 2 either way, not 14.
        assert len(from_legs.meeting_lines) == len(from_envelope.meeting_lines) == 2

    def test_an_honest_four_stay_route_does_not_evict_a_rivals_row(self) -> None:
        # Stays alone do not close the cap: an HONEST four-room mover really
        # has four rows, and a per-SUBJECT cap of three would have dropped the
        # rival's single contradicting placement to make room for the fourth.
        # Per (subject, source) it cannot: each voice keeps its own most-recent
        # rows whatever anyone else says.
        rendered = _listener_reading(_FOUR_STAYS).rendered
        assert "in MEDBAY at tick 8 per p-2" in rendered
        for room, tick in (("EAST_HALL", 13), ("ADMIN", 14), ("WEST_HALL", 15)):
            assert f"in {room} at tick {tick} per p-1" in rendered
        # The cap is still a cap: the speaker's OWN oldest row is the one their
        # fourth stay displaces.
        assert "in ENGINEERING at tick 12 per p-1" not in rendered


_SUBJECT: Final[str] = "p-2"


def _rows_suffix(
    rows: tuple[tuple[str, int, str], ...], *, subject: str = _SUBJECT
) -> str:
    """``_format_alibi_suffix`` over ``(room, tick, source)`` rows about ``subject``.

    ``BeliefAlibiClaim.player_id`` IS the subject, so the two always agree:
    passing the subject separately is what tells the selection which of the
    sources is the accused speaking about itself (round 8's two pools).
    """

    return _format_alibi_suffix(
        tuple(
            BeliefAlibiClaim(player_id=subject, room=room, tick=tick, source=source)
            for room, tick, source in rows
        ),
        subject=subject,
    )


class TestTheAlibiCapIsPerSource:
    """``_format_alibi_suffix``'s cap, at the unit the round-5 review moved it to."""

    @staticmethod
    def _suffix(rows: tuple[tuple[str, int, str], ...]) -> str:
        return _rows_suffix(rows)

    def test_one_sources_volume_never_evicts_another_source(self) -> None:
        flood = tuple(("STORAGE", tick, "p-2") for tick in range(10, 20))
        suffix = self._suffix((*flood, ("MEDBAY", 8, "p-3")))
        assert "in MEDBAY at tick 8 per p-3" in suffix
        # Bounded per source all the same: three of p-2's ten rows, its newest.
        assert suffix.count("per p-2") == _MAX_RENDERED_ALIBIS
        assert "at tick 19 per p-2" in suffix
        assert "at tick 16 per p-2" not in suffix

    def test_a_single_sources_rows_read_exactly_as_they_did(self) -> None:
        # The byte-neutrality half: with ONE source the per-source cap and the
        # old per-subject cap select the same three rows in the same order, and
        # every memory state on the four committed sets is either under the cap
        # or single-source.
        rows = tuple(("STORAGE", tick, "p-3") for tick in range(10, 15))
        assert self._suffix(rows) == (
            "alibi: in STORAGE at tick 12 per p-3; "
            "in STORAGE at tick 13 per p-3; in STORAGE at tick 14 per p-3"
        )

    def test_rows_render_in_one_deterministic_order_across_sources(self) -> None:
        # Kept rows are rendered in the whole block's (tick, room, source)
        # order, not grouped by source, so the line is a chronology.
        suffix = self._suffix(
            (("MEDBAY", 8, "p-3"), ("STORAGE", 2, "p-2"), ("LABS", 5, "p-4"))
        )
        assert suffix == (
            "alibi: in STORAGE at tick 2 per p-2; in LABS at tick 5 per p-4; "
            "in MEDBAY at tick 8 per p-3"
        )


class TestMixedSpellingsOfOneStayLeaveTheListenerIdentical:
    """The round-6 half of the listener property: the cut must not pick the LABEL.

    Round 5's family enumerates every re-cut in ONE spelling, so it could not
    see what survived coalescing. ``maximal_stays`` kept the FIRST leg's room
    text and the §6.6 suffix sorted rows on that raw text, so ``CAFETERIA 2-4``
    + ``cafeteria 5-8`` and its mirror -- one account, one cut, the same two
    canonically-equal labels -- put the speaker's row on opposite sides of a
    rival's contradicting placement::

        alibi: in CAFETERIA at tick 2 per p-1; in MEDBAY at tick 2 per p-2
        alibi: in MEDBAY at tick 2 per p-2; in cafeteria at tick 2 per p-1

    The merged label is now the smallest of the labels merged (a function of
    the SET, not of the order) and the row order reads canonical rooms before
    the raw text, so both halves of that are closed.
    """

    @pytest.mark.parametrize(
        ("name", "route"),
        (("one_stay", _ONE_STAY), ("two_stays", _TWO_STAYS)),
    )
    def test_every_spelling_of_every_cut_leaves_the_listener_identical(
        self, name: str, route: tuple[AlibiSegment, ...]
    ) -> None:
        for narrations in _spelled_narrations_of(route).values():
            baseline = _listener_reading(narrations[0])
            for narration in narrations[1:]:
                assert _listener_reading(narration) == baseline, (
                    name,
                    [(leg.room, leg.from_tick, leg.to_tick) for leg in narration],
                )

    def test_the_family_carries_the_mirror_image_narrations(self) -> None:
        # The groups that matter are the ones whose label SET has more than one
        # member: those are the narrations where the cut used to choose the
        # surviving label, and each has to hold both orders of it.
        groups = _spelled_narrations_of(_ONE_STAY)
        mixed = {key: members for key, members in groups.items() if len(key[1]) > 1}
        assert mixed
        assert all(len(members) > 1 for members in mixed.values())

        stay = _ONE_STAY[0]
        first, second = _spellings_of(stay.room)[:2]
        midpoint = (stay.from_tick + stay.to_tick) // 2
        pair = groups[(0, frozenset({first, second}))]
        for left, right in ((first, second), (second, first)):
            assert (
                AlibiSegment(room=left, from_tick=stay.from_tick, to_tick=midpoint),
                AlibiSegment(room=right, from_tick=midpoint + 1, to_tick=stay.to_tick),
            ) in pair

    def test_the_baseline_of_every_group_carries_the_rival_and_the_speaker(
        self,
    ) -> None:
        # Non-vacuity: an invariance over blocks that never name both voices
        # would prove nothing.
        for narrations in _spelled_narrations_of(_ONE_STAY).values():
            rendered = _listener_reading(narrations[0]).rendered
            assert "per p-1" in rendered
            assert "in MEDBAY at tick 8 per p-2" in rendered

    # A rival placement at the account's OWN first tick, so the room text is
    # what the row order turns on rather than the tick. "CAFETERIA" sorts
    # before "MEDBAY" and "cafeteria" after it, so on raw text the same account
    # said two ways put the rival on opposite sides of the speaker.
    _TIED_RIVAL: Final[tuple[AlibiSegment, ...]] = (
        AlibiSegment(room="MEDBAY", from_tick=2, to_tick=2),
    )

    @pytest.mark.parametrize("wording", ("cafeteria", "CAFETERIA_TRANSITION"))
    def test_two_wordings_differ_only_in_the_label_they_quote(
        self, wording: str
    ) -> None:
        # Where the label SETS differ the narrations are two WORDINGS of one
        # account, exactly as "LABS 2-14" and "labs 2-14" are with one leg, so
        # the quoted label legitimately differs. Everything else must not: the
        # rows that SURVIVE, their ORDER and the sources they are attributed to
        # are identical, which is what the canonical-first sort key buys.
        named = _listener_reading(
            (AlibiSegment(room="CAFETERIA", from_tick=2, to_tick=8),),
            rival=self._TIED_RIVAL,
        )
        spelled = _listener_reading(
            (AlibiSegment(room=wording, from_tick=2, to_tick=8),),
            rival=self._TIED_RIVAL,
        )

        assert named.rendered != spelled.rendered
        assert [(row[0], row[2], row[3]) for row in named.belief_alibis] == [
            (row[0], row[2], row[3]) for row in spelled.belief_alibis
        ]
        assert [statement.speaker for statement in named.statements] == [
            statement.speaker for statement in spelled.statements
        ]
        # And the row ORDER is the thing the raw-text key used to move: the
        # speaker's own placement leads either way, so the two belief lines
        # differ in the quoted label and in nothing else.
        rows = [
            next(line for line in reading.rendered.splitlines() if "alibi:" in line)
            for reading in (named, spelled)
        ]
        for row, label in zip(rows, ("CAFETERIA", wording), strict=True):
            assert row.split("alibi: ")[1] == (
                f"in {label} at tick 2 per p-1; in MEDBAY at tick 2 per p-2"
            )
        assert rows[0].replace("CAFETERIA", wording, 1) != rows[0]


class TestTheBeliefBlockCannotOutgrowTheTokenBudget:
    """The round-6 blocking gate: the §6.6 belief block is NOT budgeted.

    ``_assemble_view`` treats the belief block as fixed and lets the
    observations take whatever is left, so a bound on the alibi rows is the
    only thing standing between a loud meeting and a render with no elastic
    memory left at all. Round 5 moved the bound from ``subjects x cap`` to
    ``subjects x sources x cap``, which on a nine-player roster is 168 rows and
    1,605 estimated tokens -- over ``DEFAULT_TOKEN_BUDGET``, with the
    observations block gone whole.

    The worst LEGAL case, built through the production path: nine players,
    every living one proxy-alibiing every other with a three-stay route (the
    per-source cap), so every subject has every other voice talking about it at
    full volume.

    Round 7 corrects what the surviving block HOLDS in that case. It is
    reported ``[meeting]`` rows, not the agent's own observations: the case
    offers reported candidates at ``_SALIENCE_REPORTED_TESTIMONY`` above the
    agent's own sightings, so first-hand retention here is zero at every value
    the roster allows and the alibi caps are not its lever. What they decide is
    how much render is left for elastic memory at all, and THAT is what the
    pins below hold.

    Round 8 widens the fixture, because the worst case moved with the rule. The
    per-subject bound is now TWO pools added -- ``_MAX_RENDERED_ALIBIS`` self
    rows plus ``_MAX_RENDERED_ALIBIS_FROM_OTHERS`` from other voices -- and the
    round-6/7 fixture carried no self-alibis at all, so it saturated only one of
    them. Every living player now proxy-alibis every other AND self-alibis, so
    both pools are full and every subject sits at 3 + 4 = 7 rows.
    """

    _ROSTER: Final[tuple[str, ...]] = tuple(f"p-{index}" for index in range(1, 10))
    _ROUTE: Final[tuple[AlibiSegment, ...]] = tuple(
        AlibiSegment(room=room, from_tick=100 + offset, to_tick=100 + offset)
        for offset, room in enumerate(("ENGINEERING", "UPPER_HALL", "ENGINEERING"))
    )

    @classmethod
    def _rendered(cls) -> str:
        turns = tuple(
            MeetingTurn(
                turn_id=f"m-budget:turn-{index}",
                turn_index=index,
                speaker=speaker,
                turn_kind="opening" if index == 0 else "reply",
                reply_to=None,
                observations=(),
                claims=(AlibiClaim(type="alibi", subject=subject, route=cls._ROUTE),),
                free_text="",
            )
            for index, (speaker, subject) in enumerate(
                (speaker, subject) for speaker in cls._ROSTER for subject in cls._ROSTER
            )
        )
        result = MeetingResult(
            meeting_id="m-budget",
            triggered_by=_LISTENER,
            trigger_tick=200,
            outcome="SKIPPED",
            ejected_player_id=None,
            ballots=tuple(
                VoteBallot(
                    voter=voter,
                    target="SKIP",
                    confidence=0.0,
                    primary_reason_id=None,
                    rationale_text="skip",
                )
                for voter in cls._ROSTER
            ),
            transcript=MeetingTranscript(turns=turns),
        )
        memory = _memory_for(
            agent_id=_LISTENER,
            roster_sightings=tuple(
                player for player in cls._ROSTER if player != _LISTENER
            ),
            self_tick=0,
        )
        absorb_reported_testimony(memory, statements=derive_reported_testimony(result))
        return render_for_prompt(memory)

    _OBSERVATIONS_HEADER: Final[str] = "## Recent observations (most salient first):"

    @classmethod
    def _observation_lines(cls, rendered: str) -> list[str]:
        """The ELASTIC block's own lines, stopping at the next top-level block.

        The beliefs block renders AFTER the observations, so splitting on the
        header alone and keeping every ``- `` line counts belief rows as
        observations -- which is how round 6 came to report reported
        ``[meeting]`` rows as first-hand observation lines (round-7 review).
        """

        if cls._OBSERVATIONS_HEADER not in rendered:
            return []
        tail = rendered.split(cls._OBSERVATIONS_HEADER, 1)[1]
        lines: list[str] = []
        for line in tail.splitlines():
            if line.startswith("## "):
                break
            if line.startswith("- "):
                lines.append(line)
        return lines

    @classmethod
    def _rendered_at(cls, from_others: int, monkeypatch: pytest.MonkeyPatch) -> str:
        monkeypatch.setattr(store, "_MAX_RENDERED_ALIBIS_FROM_OTHERS", from_others)
        return cls._rendered()

    @classmethod
    def _rendered_under_32d0cae7(cls, monkeypatch: pytest.MonkeyPatch) -> str:
        """The same memory rendered under the PRE-CARD per-subject rule, verbatim.

        Transcribed from ``git show 32d0cae7:agents/memory/store.py``: a flat
        ``_MAX_RENDERED_ALIBIS`` most-recent rows per subject, sorted on
        ``(tick, raw room, source)``, with no notion of a source at all. It is
        the honest comparator for "how much elastic section did the block leave
        before this card touched it", and it is run rather than remembered so it
        cannot go stale.
        """

        def _pre_card(alibis: tuple[Any, ...], *, subject: str) -> str:
            if not alibis:
                return ""
            ordered = sorted(alibis, key=lambda a: (a.tick, a.room, a.source))
            if len(ordered) > _MAX_RENDERED_ALIBIS:
                ordered = ordered[-_MAX_RENDERED_ALIBIS:]
            return "alibi: " + "; ".join(
                f"in {alibi.room} at tick {alibi.tick} per {alibi.source}"
                for alibi in ordered
            )

        monkeypatch.setattr(store, "_format_alibi_suffix", _pre_card)
        return cls._rendered()

    def test_the_worst_legal_nine_player_case_stays_inside_the_budget(self) -> None:
        assert _estimate_tokens(self._rendered()) <= DEFAULT_TOKEN_BUDGET

    def test_the_worst_legal_case_does_not_shed_the_observations_block(self) -> None:
        # The half that actually bites: over budget the elastic section is what
        # pays, so an unbounded belief block costs the agent the whole block.
        rendered = self._rendered()
        assert self._OBSERVATIONS_HEADER in rendered
        assert self._observation_lines(rendered)

    def test_the_shipped_pools_pin_their_measured_worst_case(self) -> None:
        # THE pin, re-measured at the round-8 head on the widened fixture. Every
        # figure is measured at the shipped pool sizes, so ANY change to EITHER
        # constant -- up OR down -- turns this red and forces the sweep to be
        # re-run and re-published. The literals ARE the pin, so they are spelled
        # out rather than derived.
        assert _MAX_RENDERED_ALIBIS == 3
        assert _MAX_RENDERED_ALIBIS_FROM_OTHERS == 4
        rendered = self._rendered()
        rows = [line for line in rendered.splitlines() if "alibi:" in line]
        assert sum(row.count(" per p-") for row in rows) == 56
        assert _estimate_tokens(rendered) == 1469
        assert DEFAULT_TOKEN_BUDGET - _estimate_tokens(rendered) == 31
        assert len(self._observation_lines(rendered)) == 36

    def test_the_elastic_section_holds_reported_rows_not_first_hand_ones(
        self,
    ) -> None:
        # The round-7 correction, pinned so it cannot be mis-stated again. In
        # THIS case the elastic section is saturated by reported ``[meeting]``
        # rows, which sit at ``_SALIENCE_REPORTED_TESTIMONY`` ABOVE the agent's
        # own sightings, so the first-hand lines are shed first and the alibi
        # caps are not what decides their fate: retention is zero at the shipped
        # pools AND across the range. The number that moves with the caps is the
        # elastic block's SIZE.
        lines = self._observation_lines(self._rendered())
        assert len(lines) == 36
        assert [line for line in lines if "[meeting]" not in line] == []

    def test_first_hand_retention_does_not_move_with_the_caps(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The measurement behind the sentence above, run rather than asserted
        # from memory: across the whole range the roster allows, the worst case
        # retains the SAME number of first-hand lines -- zero -- so no floor
        # above zero is supportable on first-hand lines in this case. Stated
        # here so a future reader does not re-derive a floor the measurement
        # does not carry.
        retained = {
            from_others: len(
                [
                    line
                    for line in self._observation_lines(
                        self._rendered_at(from_others, monkeypatch)
                    )
                    if "[meeting]" not in line
                ]
            )
            for from_others in (0, 3, 4, 5, 15)
        }
        assert retained == {0: 0, 3: 0, 4: 0, 5: 0, 15: 0}

    def test_the_elastic_block_clears_two_thirds_of_the_pre_card_comparator(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The floor the measurement DOES support, against the honest comparator
        # this test can compute: the PRE-CARD ``32d0cae7`` rule, run verbatim
        # over the same memory rather than approximated by a cap value.
        # Measured: 48 elastic lines there against 36 at the shipped pools, a
        # ratio of 0.75. Comparator measured live, so it cannot go stale; the
        # floor is two thirds.
        comparator = len(
            self._observation_lines(self._rendered_under_32d0cae7(monkeypatch))
        )
        assert comparator == 48
        monkeypatch.undo()
        shipped = len(self._observation_lines(self._rendered()))
        assert shipped == 36
        assert shipped * 3 >= comparator * 2

    def test_the_case_really_is_the_worst_the_roster_allows(self) -> None:
        # Non-vacuity: if the fixture stopped saturating the pools the budget
        # assertions above would be measuring nothing. Eight subjects reach the
        # block (the listener holds no belief row about itself); each one has
        # spoken about itself at the per-source cap AND has the seven other living
        # voices talking about it, each of those also at the per-source cap --
        # so BOTH pools bind on every subject.
        rows = [line for line in self._rendered().splitlines() if "alibi:" in line]
        assert len(rows) == len(self._ROSTER) - 1
        for row in rows:
            assert row.count(" per p-") == (
                _MAX_RENDERED_ALIBIS + _MAX_RENDERED_ALIBIS_FROM_OTHERS
            )
        # The others pool really is the binding one: the roster offers more
        # other voices than it admits, at more rows each than it admits.
        assert _MAX_RENDERED_ALIBIS_FROM_OTHERS < (
            (len(self._ROSTER) - 2) * _MAX_RENDERED_ALIBIS
        )
        assert _MAX_RENDERED_ALIBIS_FROM_OTHERS < len(self._ROSTER) - 2


class TestTheOthersPoolIsFilledRoundRobin:
    """How the OTHERS pool chooses between VOICES.

    The pool exists for the budget; the round-robin exists so that buying the
    budget back does not hand any one voice the eviction dial round 5 took off
    the accused. Every other source's newest row is taken first, then every
    other source's second-newest, and so on.

    Round 8 narrows what this class is ABOUT. The subject's own rows are no
    longer in this pool at all -- they are selected against
    ``_MAX_RENDERED_ALIBIS`` on their own, so the accused is not ranked against
    the rivals and cannot reach them. What is left here is the guarantee AMONG
    the other voices, and it is per VOICE, not per row: a voice is dropped only
    when more than ``_MAX_RENDERED_ALIBIS_FROM_OTHERS`` distinct others have
    spoken about one subject, and then the one whose newest row is stalest.
    Below that a voice with several rows CAN lose its older rows to another
    voice's newer ones, which is the round-robin working as designed.
    """

    @staticmethod
    def _suffix(rows: tuple[tuple[str, int, str], ...]) -> str:
        return _rows_suffix(rows)

    def test_no_voice_is_zeroed_while_the_pool_permits(self) -> None:
        # Other sources within the pool: every one of them keeps a row, however
        # many rows any of the others brought. Exactly the pool size, which is
        # the BOUNDARY the property has to hold at, so the count is read off the
        # constant rather than spelled -- the intent is "as many voices as the
        # pool permits", not a particular number.
        sources = tuple(
            f"p-{index}" for index in range(10, 10 + _MAX_RENDERED_ALIBIS_FROM_OTHERS)
        )
        rows = tuple(
            ("STORAGE", tick, source)
            for position, source in enumerate(sources)
            for tick in range(100 + 10 * position, 100 + 10 * position + 3)
        )
        suffix = self._suffix(rows)
        for source in sources:
            assert f"per {source}" in suffix

    def test_a_rivals_row_survives_a_flood_of_stays_and_of_proxy_speakers(
        self,
    ) -> None:
        # The round-5 finding, re-stated against the round-8 pools. The rival
        # speaks ONCE and earliest, so its row is the stalest in the block --
        # the first thing a per-subject cap by recency alone would drop. The
        # accused's thirty stays cannot touch it at all now: they are a
        # different pool.
        rival = ("MEDBAY", 8, "p-3")
        accused = tuple(("STORAGE", tick, _SUBJECT) for tick in range(10, 40))
        assert "in MEDBAY at tick 8 per p-3" in self._suffix((rival, *accused))

        proxies = tuple(
            ("STORAGE", 50 + offset, f"p-{10 + offset}")
            for offset in range(_MAX_RENDERED_ALIBIS_FROM_OTHERS - 1)
        )
        suffix = self._suffix((rival, *accused, *proxies))
        assert "in MEDBAY at tick 8 per p-3" in suffix
        assert suffix.count(" per ") == (
            _MAX_RENDERED_ALIBIS + _MAX_RENDERED_ALIBIS_FROM_OTHERS
        )

    def test_only_the_stalest_voice_goes_when_others_outnumber_the_pool(
        self,
    ) -> None:
        # Past the pool a voice HAS to go, and which one is decided by its own
        # recency -- never by how much anybody else said.
        speakers = tuple(
            ("STORAGE", 100 + offset, f"p-{10 + offset}")
            for offset in range(_MAX_RENDERED_ALIBIS_FROM_OTHERS + 1)
        )
        quiet = self._suffix(speakers)
        assert f"per {speakers[0][2]}" not in quiet
        for _, _, source in speakers[1:]:
            assert f"per {source}" in quiet

        # The same block with the newest speaker shouting: the dropped voice is
        # still the stalest one, not one the shouting chose.
        loud = self._suffix(
            (
                *speakers,
                *(("STORAGE", 200 + tick, speakers[-1][2]) for tick in range(9)),
            )
        )
        assert f"per {speakers[0][2]}" not in loud
        for _, _, source in speakers[1:]:
            assert f"per {source}" in loud

    def test_the_selection_is_deterministic_under_every_permutation(self) -> None:
        # Stored order is an accident of ingest; the render must not be. Ties on
        # (tick, canonical rooms) are broken by the raw label and then the
        # source, so both keys are total and every permutation reads the same.
        rows = (
            ("STORAGE", 8, _SUBJECT),
            ("STORAGE", 8, "p-3"),
            ("MEDBAY", 8, "p-4"),
            ("storage", 8, "p-5"),
            ("LABS", 5, _SUBJECT),
        )
        expected = self._suffix(rows)
        for permutation in itertools.permutations(rows):
            assert self._suffix(permutation) == expected

    def test_the_permutations_reach_both_pools_at_their_bounds(self) -> None:
        # The same 120 permutations where BOTH pools actually bind and every
        # row ties on (tick, canonical rooms), so the tie-breaks are what
        # decides selection rather than an accident of there being room for
        # everything. Four self rows into a pool of three, five tied other
        # voices into a pool of four.
        rows = (
            *(("STORAGE", 8, _SUBJECT) for _ in range(1)),
            ("storage", 8, _SUBJECT),
            ("STORAGE_TRANSITION", 8, _SUBJECT),
            ("STORAGE", 8, "p-3"),
            ("storage", 8, "p-4"),
        )
        expected = self._suffix(rows)
        assert expected.count(" per ") == 5
        for permutation in itertools.permutations(rows):
            assert self._suffix(permutation) == expected

        bound = (
            ("STORAGE", 8, _SUBJECT),
            ("storage", 8, _SUBJECT),
            ("STORAGE_TRANSITION", 8, _SUBJECT),
            ("STORAGE", 8, "p-3"),
            ("storage", 8, "p-4"),
            ("STORAGE_TRANSITION", 8, "p-5"),
            ("STORAGE", 8, "p-6"),
            ("storage", 8, "p-7"),
        )
        pinned = self._suffix(bound)
        assert pinned.count(" per ") == (
            _MAX_RENDERED_ALIBIS + _MAX_RENDERED_ALIBIS_FROM_OTHERS
        )
        for permutation in itertools.permutations(bound[:5]):
            assert self._suffix((*permutation, *bound[5:])) == pinned

    def test_a_lone_speakers_render_is_exactly_what_round_five_rendered(self) -> None:
        # The byte-neutrality half: with one source the per-source cap decides
        # everything and neither pool binds, so the line is unchanged -- and
        # every committed belief state on the four sets is inside both pools.
        rows = tuple(("STORAGE", tick, "p-3") for tick in range(10, 15))
        assert self._suffix(rows) == (
            "alibi: in STORAGE at tick 12 per p-3; "
            "in STORAGE at tick 13 per p-3; in STORAGE at tick 14 per p-3"
        )

    def test_the_others_pool_is_at_least_the_per_source_cap(self) -> None:
        # Otherwise a lone OTHER speaker's render would move, and with it the
        # committed prompt bytes. The SELF pool needs no such assertion: it IS
        # ``_MAX_RENDERED_ALIBIS``, so a lone self speaker is unaffected by
        # construction.
        assert _MAX_RENDERED_ALIBIS_FROM_OTHERS >= _MAX_RENDERED_ALIBIS


# --- Round 8: the two pools, made STRUCTURAL and spelling-blind -------------


def _kept_rows(suffix: str) -> tuple[tuple[str, int, str], ...]:
    """``(source, tick, raw room)`` for each row a suffix rendered, in order."""

    if not suffix:
        return ()
    rows: list[tuple[str, int, str]] = []
    for part in suffix.removeprefix("alibi: ").split("; "):
        room = part.split("in ", 1)[1].split(" at tick ", 1)[0]
        tick = int(part.split(" at tick ", 1)[1].split(" per ", 1)[0])
        rows.append((part.rsplit(" per ", 1)[1], tick, room))
    return tuple(rows)


def _canonical_rows(suffix: str) -> tuple[tuple[str, int, tuple[str, ...]], ...]:
    """The kept rows with the raw LABEL canonicalised away.

    What "selection is spelling-blind" is a property OF: two wordings of one
    account legitimately quote different labels, so the label itself may move;
    which PLACEMENT each voice got into the block may not.
    """

    return tuple(
        (source, tick, tuple(sorted(canonical_rooms(room))))
        for source, tick, room in _kept_rows(suffix)
    )


# The rival field the accused is tested against: four other voices, ticks
# chosen to TIE with the self rows the family below draws, and one voice
# carrying two rows so the per-VOICE guarantee is exercised as well.
_RIVAL_FIELD: Final[tuple[tuple[str, int, str], ...]] = (
    ("STORAGE", 10, "p-3"),
    ("LABS", 29, "p-4"),
    ("MEDBAY", 30, "p-4"),
    ("CAFETERIA", 40, "p-5"),
    ("UPPER_HALL", 41, "p-5"),
    ("ADMIN", 12, "p-6"),
)


def _self_row_families() -> tuple[tuple[tuple[str, int, str], ...], ...]:
    """Every account the ACCUSED may give of itself, as row sets.

    Zero to six rows; ticks that tie with the rival field's (29, 30, 40, 41),
    that undercut it and that outrun it; every spelling in ``_spellings_of``
    on the tied rooms, which is what round 7's finding turned on; and
    restatements, which is one speaker repeating a single placement.
    """

    families: list[tuple[tuple[str, int, str], ...]] = [()]
    for spelling in _spellings_of("MEDBAY"):
        for other in _spellings_of("UPPER_HALL"):
            families.append((("UPPER_HALL", 29, _SUBJECT), (spelling, 30, _SUBJECT)))
            families.append(((other, 41, _SUBJECT), (spelling, 30, _SUBJECT)))
            families.append(((spelling, 30, _SUBJECT),))
            families.append(
                (
                    (spelling, 30, _SUBJECT),
                    (spelling, 30, _SUBJECT),
                    (other, 41, _SUBJECT),
                )
            )
            families.append(
                tuple((spelling, tick, _SUBJECT) for tick in (2, 3, 29, 30, 41, 99))
            )
    for tick in (1, 29, 30, 41, 500):
        families.append((("CAFETERIA", tick, _SUBJECT),))
        families.append(
            tuple(("CAFETERIA", tick + step, _SUBJECT) for step in range(6))
        )
    return tuple(families)


# The verifier's four-speaker exhibit and its seven-voice variant, as the
# PROXY field each drives: (speaker, route) pairs about ``p-1``.
_FOUR_SPEAKER_FIELD: Final[tuple[tuple[str, tuple[AlibiSegment, ...]], ...]] = (
    ("p-3", (AlibiSegment(room="STORAGE", from_tick=10, to_tick=10),)),
    (
        "p-4",
        (
            AlibiSegment(room="LABS", from_tick=29, to_tick=29),
            AlibiSegment(room="MEDBAY", from_tick=30, to_tick=30),
        ),
    ),
    (
        "p-5",
        (
            AlibiSegment(room="CAFETERIA", from_tick=40, to_tick=40),
            AlibiSegment(room="UPPER_HALL", from_tick=41, to_tick=41),
        ),
    ),
)
# The same exhibit scaled until the OTHERS pool binds on VOICES: same listener,
# same subject, same accused route, six other voices. ``p-8``'s newest row TIES
# with the accused's on ``(tick, canonical rooms)`` and the two of them are the
# stalest pair, which is where round 6's single total put its boundary -- so
# there the accused's spelling decided whether ``p-8`` was in the block at all.
_SEVEN_VOICE_FIELD: Final[tuple[tuple[str, tuple[AlibiSegment, ...]], ...]] = (
    (
        "p-4",
        (
            AlibiSegment(room="LABS", from_tick=40, to_tick=40),
            AlibiSegment(room="MEDBAY", from_tick=41, to_tick=41),
        ),
    ),
    ("p-5", (AlibiSegment(room="CAFETERIA", from_tick=39, to_tick=39),)),
    ("p-6", (AlibiSegment(room="REACTOR", from_tick=38, to_tick=38),)),
    ("p-7", (AlibiSegment(room="WEST_HALL", from_tick=37, to_tick=37),)),
    ("p-3", (AlibiSegment(room="ADMIN", from_tick=36, to_tick=36),)),
    ("p-8", (AlibiSegment(room="MEDBAY", from_tick=30, to_tick=30),)),
)


def _field_belief_rows(
    *,
    field: tuple[tuple[str, tuple[AlibiSegment, ...]], ...],
    accused_route: tuple[AlibiSegment, ...],
) -> tuple[tuple[object, ...], ...]:
    """Drive the PRODUCTION path over a proxy field plus the accused's account.

    ``derive_reported_testimony`` -> ``absorb_reported_testimony`` ->
    ``render_for_prompt``, listener ``p-9``, subject ``p-1``, exactly as the
    round-7 verifier ran it. Returns the belief rows the listener ends up
    holding about ``p-1``, read back off the RENDER rather than off the store,
    so what is compared is what the agent would actually be shown.
    """

    speakers = tuple(speaker for speaker, _ in field)
    turns = tuple(
        _alibi_turn(index=index, speaker=speaker, subject="p-1", route=route)
        for index, (speaker, route) in enumerate(field)
    )
    result = MeetingResult(
        meeting_id="m-field",
        triggered_by=_LISTENER,
        trigger_tick=60,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=tuple(
            VoteBallot(
                voter=voter,
                target="SKIP",
                confidence=0.0,
                primary_reason_id=None,
                rationale_text="skip",
            )
            for voter in (*speakers, "p-1", _LISTENER)
        ),
        transcript=MeetingTranscript(
            turns=(
                *turns,
                _alibi_turn(
                    index=len(turns),
                    speaker="p-1",
                    subject="p-1",
                    route=accused_route,
                ),
            )
        ),
    )
    memory = _memory_for(
        agent_id=_LISTENER, roster_sightings=("p-1", *speakers), self_tick=0
    )
    absorb_reported_testimony(memory, statements=derive_reported_testimony(result))
    rendered = render_for_prompt(memory)
    line = next(
        line
        for line in rendered.splitlines()
        if "alibi:" in line and line.lstrip("- ").startswith("p-1:")
    )
    return _kept_rows("alibi: " + line.split("alibi: ", 1)[1].rstrip(")"))


class TestTheAccusedCannotMoveARivalsRow:
    """The round-7 blocking finding, closed STRUCTURALLY by the two pools.

    Round 6 filled ONE per-subject total round-robin across every source, the
    accused's included, and ranked those sources by the position of their
    newest row under ``_alibi_row_sort_key`` -- a key that carries the RAW
    LABEL above the source. So when the accused's newest row and a rival's
    newest row tied on ``(tick, canonical rooms)``, the accused's own SPELLING
    decided which source was fresher and which one took the last slot. Spelling
    ``MEDBAY`` as ``medbay`` cost ``p-4`` a row a listener would have held.

    With the self rows in a reserved pool the two sets are never ranked against
    each other at all, so there is nothing for a spelling, a tick, a stay count
    or a restatement to reach. The property is asserted in BOTH directions:
    what the accused says cannot move the others' rows, and what the others say
    cannot move the accused's.
    """

    def test_no_account_the_accused_gives_moves_the_others_rows(self) -> None:
        families = _self_row_families()
        assert len(families) >= 50
        baseline = [
            row for row in _kept_rows(_rows_suffix(_RIVAL_FIELD)) if row[0] != _SUBJECT
        ]
        assert baseline  # non-vacuity: the field really renders
        for self_rows in families:
            kept = _kept_rows(_rows_suffix((*_RIVAL_FIELD, *self_rows)))
            assert [row for row in kept if row[0] != _SUBJECT] == baseline

    def test_no_field_of_rivals_moves_the_accuseds_own_rows(self) -> None:
        # The mirror. The rival field is varied instead, and the accused's own
        # rendered rows must not move -- so the reservation runs both ways and a
        # crowd of proxy speakers cannot bury a subject's own account.
        self_rows = tuple(("CAFETERIA", tick, _SUBJECT) for tick in (2, 29, 30, 41, 99))
        baseline = [
            row for row in _kept_rows(_rows_suffix(self_rows)) if row[0] == _SUBJECT
        ]
        assert baseline
        fields: list[tuple[tuple[str, int, str], ...]] = [(), _RIVAL_FIELD]
        fields.append(
            tuple(("STORAGE", 100 + offset, f"p-{10 + offset}") for offset in range(12))
        )
        fields.append(tuple(("STORAGE", tick, "p-3") for tick in range(200, 230)))
        for spelling in _spellings_of("CAFETERIA"):
            fields.append(tuple((spelling, tick, "p-4") for tick in (29, 30, 41, 99)))
        for field in fields:
            kept = _kept_rows(_rows_suffix((*field, *self_rows)))
            assert [row for row in kept if row[0] == _SUBJECT] == baseline

    def test_the_round_seven_four_speaker_repro(self) -> None:
        # The verifier's exhibit, through the PRODUCTION path. Listener p-9,
        # subject p-1; p-4's tick-29 row is the one contradicting p-1. Before
        # this round, narrating the tick-30 stay as ``MEDBAY`` kept p-4's
        # LABS@29 AND MEDBAY@30, while narrating it as ``medbay`` or
        # ``MEDBAY_TRANSITION`` kept MEDBAY@30 alone.
        kept = {
            label: tuple(
                row
                for row in _field_belief_rows(
                    field=_FOUR_SPEAKER_FIELD,
                    accused_route=(
                        AlibiSegment(room="UPPER_HALL", from_tick=29, to_tick=29),
                        AlibiSegment(room=label, from_tick=30, to_tick=31),
                    ),
                )
                if row[0] != "p-1"
            )
            for label in _spellings_of("MEDBAY")
        }
        assert len(set(kept.values())) == 1
        # Non-vacuity: the others pool really is binding here, so the assertion
        # above is not just reading a block with room to spare.
        rows = next(iter(kept.values()))
        assert len(rows) == _MAX_RENDERED_ALIBIS_FROM_OTHERS
        assert len({row[0] for row in rows}) == 3

    def test_the_four_speaker_repro_is_tick_blind_too(self) -> None:
        # The other half of the round-7 finding, on the same field: round 6's
        # comment claimed "a speaker can only ever displace their OWN older
        # rows", and below the threshold that was false. Moving the accused's
        # stay from tick 30 to tick 35 made it the fresher source and took
        # p-4's LABS@29 with it; at tick 20 or 30, p-4 kept both rows.
        kept = {
            tick: tuple(
                row
                for row in _field_belief_rows(
                    field=_FOUR_SPEAKER_FIELD,
                    accused_route=(
                        AlibiSegment(
                            room="UPPER_HALL", from_tick=tick - 1, to_tick=tick - 1
                        ),
                        AlibiSegment(room="MEDBAY", from_tick=tick, to_tick=tick + 1),
                    ),
                )
                if row[0] != "p-1"
            )
            for tick in (20, 30, 35)
        }
        assert len(set(kept.values())) == 1
        assert len(next(iter(kept.values()))) == _MAX_RENDERED_ALIBIS_FROM_OTHERS

    def test_the_seven_voice_variant_of_the_four_speaker_repro(self) -> None:
        # The same exhibit with enough other voices that the OTHERS pool binds
        # on VOICES rather than on rows: seven speakers about one subject, the
        # accused among them, and p-8's newest row TIED with the accused's on
        # (tick, canonical rooms). Under round 6's single total that tie sat on
        # the boundary and the accused's spelling decided it: ``MEDBAY`` kept
        # p-8's row, ``medbay`` and ``MEDBAY_TRANSITION`` dropped it. Which of
        # the six rivals survive must be decided by their own recency and by
        # nothing the accused says.
        kept = {
            label: tuple(
                row
                for row in _field_belief_rows(
                    field=_SEVEN_VOICE_FIELD,
                    accused_route=(
                        AlibiSegment(room="UPPER_HALL", from_tick=29, to_tick=29),
                        AlibiSegment(room=label, from_tick=30, to_tick=31),
                    ),
                )
                if row[0] != "p-1"
            )
            for label in _spellings_of("MEDBAY")
        }
        assert len(set(kept.values())) == 1
        rows = next(iter(kept.values()))
        assert len(rows) == _MAX_RENDERED_ALIBIS_FROM_OTHERS
        assert len({row[0] for row in rows}) == _MAX_RENDERED_ALIBIS_FROM_OTHERS


class TestSelectionIsSpellingBlind:
    """Which rows SURVIVE must not depend on how any room was spelled.

    Round 6 made the RENDER order spelling-independent and stopped there; the
    selection kept the raw label in the source ranking, which is what round 7
    found. Both orders that decide SELECTION now keep the raw label strictly
    below a total tie-break: sources rank on ``(tick, canonical rooms,
    source)``, and within one source the row order reduces to ``(tick,
    canonical rooms, raw label)`` -- so the label only separates two rows that
    are otherwise THE SAME PLACEMENT, and the placement each voice got into the
    block is the same for every wording.
    """

    # Both pools pressed, every row at ONE tick, so nothing but a room label
    # can decide anything. The two halves press the two selection keys:
    #
    # * the SELF rows are four DIFFERENT rooms, so the per-source cut has to
    #   order rooms against each other -- canonically ``ADMIN < CAFETERIA <
    #   MEDBAY < STORAGE`` for every wording, where a raw-label cut would put
    #   ``storage`` after ``ADMIN`` and drop a different row;
    # * the OTHER voices are five spellings of ONE room, so their newest rows
    #   tie on ``(tick, canonical rooms)`` and only the SOURCE may separate
    #   them -- which is exactly the tie round 7 found the raw label deciding.
    _ROWS: Final[tuple[tuple[str, int, str], ...]] = (
        ("ADMIN", 30, _SUBJECT),
        ("CAFETERIA", 30, _SUBJECT),
        ("MEDBAY", 30, _SUBJECT),
        ("STORAGE", 30, _SUBJECT),
        ("MEDBAY", 30, "p-3"),
        ("MEDBAY", 30, "p-4"),
        ("MEDBAY", 30, "p-5"),
        ("MEDBAY", 30, "p-6"),
        ("MEDBAY", 30, "p-7"),
    )

    def test_every_assignment_of_spellings_keeps_the_same_placements(self) -> None:
        choices = tuple(_spellings_of(room) for room, _, _ in self._ROWS)
        baseline: list[tuple[str, int, tuple[str, ...]]] | None = None
        assignments = 0
        for assignment in itertools.product(*choices):
            rows = tuple(
                (label, tick, source)
                for (_, tick, source), label in zip(self._ROWS, assignment, strict=True)
            )
            kept = sorted(_canonical_rows(_rows_suffix(rows)))
            if baseline is None:
                baseline = kept
                # Non-vacuity: both pools are pressed, so the comparison is
                # about SELECTION and not about a block with room to spare.
                assert len(kept) == (
                    _MAX_RENDERED_ALIBIS + _MAX_RENDERED_ALIBIS_FROM_OTHERS
                )
            assert kept == baseline
            assignments += 1
        assert assignments == 3 ** len(self._ROWS)
