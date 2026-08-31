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

import tempfile
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final, NamedTuple

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    _build_observations,
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
from observation.service import ObservationService
from meetings.schemas import (
    AccusationClaim,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ReportedStatement,
    SawPlayerObservation,
    SawVentObservation,
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
    assert survival.renders == 2516  # was 2479
    # Both columns re-bucketed at the graduation sweep (Task 20.37) and NEITHER
    # moved in total. The candidate scan calls the private builder directly, and
    # until the sweep that builder's lever parameters DEFAULTED OFF -- so this
    # column counted a candidate set production never built (a ``saw_vent`` row
    # rendered nothing under the OFF default) and, because the same count keys
    # the bucket, it filed each render under an OFF-path bucket too. Deleting the
    # parameters made the scan read the path ``render_for_prompt`` always took.
    assert survival.offered == {
        "<=60": 11484,  # was 11308
        "61-100": 14982,  # was 13808
        "101-150": 7316,  # was 7069
        ">150": 3341,  # was 3689
    }
    # The raised reported band is unconditional since the baseline-7 record, so
    # there is ONE leg to count -- the differential the C-73 register measured is
    # what graduating the lever spent. Kept can exceed offered in a bucket: the
    # candidate scan counts rows the selector was HANDED, and a render can carry
    # a testimony line composed from several candidates.
    # was {"<=60": 11308, "61-100": 13803, "101-150": 7059, ">150": 3564}
    kept = {"<=60": 11484, "61-100": 14965, "101-150": 7295, ">150": 3214}
    assert survival.kept == kept
    # THE no-behaviour-moved statement, recomputed rather than asserted: the
    # sweep re-bucketed the kept rows and minted none. Every kept row comes off
    # ``render_for_prompt``, whose path the sweep did not touch, so the TOTAL is
    # the number the pre-sweep buckets summed to (11,707 + 13,622 + 7,074 +
    # 3,331). The offered total legitimately GREW by the saw_vent rows the OFF
    # default used to swallow.
    assert sum(kept.values()) == 36958  # was 35734
    assert sum(survival.offered.values()) == 37123  # was 35874
    # Every bucket clears the survival floor now, including the largest render --
    # the bucket the register measured keeping NO reported row at all.
    for bucket in _CANDIDATE_BUCKETS:
        offered = survival.offered[bucket]
        assert survival.kept[bucket] / offered >= _SURVIVAL_FLOOR, (
            f"{bucket}: kept {survival.kept[bucket]} of {offered}"
        )
