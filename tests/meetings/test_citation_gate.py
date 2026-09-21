"""The citation gate: uncited zero-flag EJECTs coerce to SKIP (Task 16.6, J2).

Pins the enforcement tooth of the citation chain
(audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2) end to end,
unconditional since the Task-16.17 baseline-5 record:

* the pure guard (:func:`meetings.manager.guard_ballot_citation`): a zero-flag
  EJECT ballot (its target carries NO contradiction flag this meeting) whose
  ``primary_reason_id`` AND ``primary_reason_observation_id`` are both null is
  coerced to SKIP with :data:`meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER`
  -- mark-and-coerce, never a crash, never a re-prompt -- and the five
  contract fixtures: zero-flag+no-citation coerced; flagged-target unaffected;
  turn citation satisfies; observation citation satisfies; fabricated citation
  nulls (16.5's validators) then coerces;
* the guard ORDERING pin: the citation gate runs AFTER
  :func:`meetings.manager.guard_ballot_target_graph`, so a redirected eject is
  judged on the REDIRECTED target's flag status, never the original's;
* scope: an uncited zero-flag eject is always coerced -- the guard renders
  nothing (the byte-identity instruments ``scripts/verify_samples.sh`` + the
  16.3 prompt-byte golden stay blind to it); only the gated case is ever
  changed;
* the Task 16.8 non-interaction pin: the gate's zero-flag predicate reads
  ONLY this meeting's detected ``contradictions`` -- suspicion never reaches
  it, so an absence-prior suspicion delta (which mints no flag) cannot move
  the gate's decision.

The manager harness mirrors ``tests.meetings.test_manager`` (the shared
scripted-client helpers) and ``tests.meetings.test_ballot_observation_citation``
(the 16.5 observation-citation responder this gate's satisfied-citation path
consumes).
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    OFF_TARGET_CITATION_EJECT_MARKER,
    SuspicionEntry,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    guard_ballot_citation,
    guard_ballot_target_graph,
)
from meetings.schemas import (
    AlibiClaim,
    AlibiSegment,
    Claim,
    ContradictionRef,
    MeetingTurn,
    ObservationId,
    VoteBallot,
)
from tests.meetings._manager_helpers import (
    _make_responder,
    _obs_vote_responder,
    _participant,
    _participants,
    _run_meeting,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _ballot(
    *,
    voter: str = "p-1",
    target: str = "p-2",
    confidence: float = 0.8,
    primary_reason_id: str | None = None,
    primary_reason_observation_id: str | None = None,
    rationale_text: str = "a bare gut read.",
) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=primary_reason_id,
        primary_reason_observation_id=primary_reason_observation_id,
        considered_alternatives=(),
        rationale_text=rationale_text,
    )


def _flag(*subjects: str, kind: str = "alibi_conflict") -> ContradictionRef:
    return ContradictionRef(
        contradiction_id="c-1",
        kind=kind,  # type: ignore[arg-type]
        event_a_id="e-a",
        event_b_id="e-b",
        subjects=subjects,
        description="test flag",
    )


def _conflict_claims() -> dict[str, tuple[Claim, ...]]:
    """Two conflicting alibis for p-2 -> exactly one ``alibi_conflict`` flag.

    The ``TestContradictionsWiring`` recipe from ``tests.meetings.test_manager``:
    the recorded contradiction carries ``subjects == ("p-2",)``, which is the
    flag the gate's zero-flag predicate reads.
    """

    return {
        "p-1": (
            AlibiClaim(
                type="alibi",
                subject="p-2",
                route=(AlibiSegment(room="STORAGE", from_tick=100, to_tick=200),),
            ),
        ),
        "p-3": (
            AlibiClaim(
                type="alibi",
                subject="p-2",
                route=(AlibiSegment(room="CAFETERIA", from_tick=150, to_tick=180),),
            ),
        ),
    }


class TestCitationGateMarker:
    """The audit marker the J2 citation guard writes onto a coerced ballot."""

    def test_marker_literal_pinned_exactly(self) -> None:
        # Downstream eval greps this literal and the spectator marker parser
        # relies on the {x!r} repr interpolation -- pin it byte-for-byte.
        assert (
            UNCITED_ZERO_FLAG_EJECT_MARKER
            == "[uncited zero-flag eject target {target!r} coerced to SKIP] "
        )


class TestGuardBallotCitationUnit:
    """The pure guard, called directly (no manager, no env)."""

    def test_zero_flag_uncited_eject_coerces_with_marker(self) -> None:
        ballot = _ballot(target="p-2", rationale_text="no one vouched for them.")
        coerced = guard_ballot_citation(ballot=ballot, contradictions=())

        assert coerced.target == "SKIP"
        assert coerced.rationale_text == (
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-2")
            + "no one vouched for them."
        )
        # Mark-and-coerce only: everything else rides through untouched.
        assert coerced.voter == ballot.voter
        assert coerced.confidence == ballot.confidence
        assert coerced.primary_reason_id is None
        assert coerced.primary_reason_observation_id is None

    def test_skip_ballot_is_byte_unchanged(self) -> None:
        ballot = _ballot(target="SKIP")
        assert guard_ballot_citation(ballot=ballot, contradictions=()) is ballot

    def test_flagged_target_is_unaffected(self) -> None:
        ballot = _ballot(target="p-2")
        result = guard_ballot_citation(ballot=ballot, contradictions=(_flag("p-2"),))
        assert result is ballot

    def test_flag_on_another_subject_does_not_shield(self) -> None:
        # The predicate is keyed by TARGET: a flag naming someone else leaves
        # this ballot exactly as uncited-zero-flag as no flag at all.
        ballot = _ballot(target="p-2")
        coerced = guard_ballot_citation(ballot=ballot, contradictions=(_flag("p-3"),))
        assert coerced.target == "SKIP"
        assert coerced.rationale_text.startswith(
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-2")
        )

    def test_turn_citation_satisfies(self) -> None:
        ballot = _ballot(target="p-2", primary_reason_id="m-1:turn-0")
        assert guard_ballot_citation(ballot=ballot, contradictions=()) is ballot

    def test_observation_citation_satisfies(self) -> None:
        ballot = _ballot(target="p-2", primary_reason_observation_id="p-1:410:0")
        assert guard_ballot_citation(ballot=ballot, contradictions=()) is ballot

    def test_vent_sighting_flag_shields_like_any_flag(self) -> None:
        # The 15.4 role-proving kind is a ContradictionRef like the others;
        # the gate never branches on kind, only on subjects.
        ballot = _ballot(target="p-2")
        result = guard_ballot_citation(
            ballot=ballot,
            contradictions=(_flag("p-2", kind="vent_sighting"),),
        )
        assert result is ballot

    def test_multi_subject_flag_shields_every_named_subject(self) -> None:
        # A ContradictionRef may name several subjects (the alibi-conflict
        # kinds flag both sides); the gate's shield set flattens EVERY
        # subject, so an uncited eject of EITHER named player is flag-backed
        # while a third party stays gated.
        flag = _flag("p-2", "p-3")
        for shielded in ("p-2", "p-3"):
            ballot = _ballot(target=shielded)
            assert (
                guard_ballot_citation(ballot=ballot, contradictions=(flag,)) is ballot
            )
        outsider = _ballot(target="p-4")
        assert (
            guard_ballot_citation(ballot=outsider, contradictions=(flag,)).target
            == "SKIP"
        )


class TestCitationGuardRunsAfterRedirect:
    """The ordering pin: flag status is judged on the REDIRECTED target.

    Composes the two guards exactly as ``_collect_one_ballot`` chains them
    (target-graph redirect first, citation gate second).
    """

    _CANDIDATES = ("p-2", "p-3")

    def _chain(
        self,
        *,
        ballot: VoteBallot,
        suspicion_graph: tuple[SuspicionEntry, ...],
        contradictions: tuple[ContradictionRef, ...],
    ) -> VoteBallot:
        redirected = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=suspicion_graph,
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
        )
        return guard_ballot_citation(ballot=redirected, contradictions=contradictions)

    def test_redirect_onto_zero_flag_target_coerces(self) -> None:
        # Original target p-2 is FLAGGED but under-gate; the redirect lands on
        # the zero-flag argmax p-3. The gate must judge p-3 (coerce), not be
        # bought off by the original target's flag.
        graph = (
            SuspicionEntry(player_id="p-2", suspicion=0.40, trust=0.5),
            SuspicionEntry(player_id="p-3", suspicion=0.80, trust=0.5),
        )
        result = self._chain(
            ballot=_ballot(target="p-2"),
            suspicion_graph=graph,
            contradictions=(_flag("p-2"),),
        )
        assert result.target == "SKIP"
        assert UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3") in (
            result.rationale_text
        )

    def test_redirect_onto_flagged_target_passes(self) -> None:
        # The inverse: original target p-2 is zero-flag and under-gate; the
        # redirect lands on the FLAGGED argmax p-3, whose flag satisfies the
        # gate -- the eject stands on the redirected target.
        graph = (
            SuspicionEntry(player_id="p-2", suspicion=0.40, trust=0.5),
            SuspicionEntry(player_id="p-3", suspicion=0.80, trust=0.5),
        )
        result = self._chain(
            ballot=_ballot(target="p-2"),
            suspicion_graph=graph,
            contradictions=(_flag("p-3"),),
        )
        assert result.target == "p-3"
        assert UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3") not in (
            result.rationale_text
        )

    def test_redirect_keeps_citation_and_passes_the_gate(self) -> None:
        # The kept-citation redirect (PR #262 review): the 10.9.2 redirect
        # deliberately preserves primary_reason_id, so a CITED under-gate
        # eject redirected onto a zero-flag argmax passes the gate on the
        # kept citation. Deliberate, not a hole: with the relevance lever OFF
        # the gate enforces citation VALIDITY and never relevance -- no
        # validator links a citation to the ballot's target, so the direct-vote
        # twin (voting p-3 outright while citing the same p-2-era turn) passes
        # identically. Pinned so the interaction is explicit for the 16.15
        # elicitation / 16.17 graduation review, which measure citation
        # quality. This is the ballot the lever flips: the ON twin of this
        # fixture is
        # `TestCitationRelevanceLever.test_the_redirect_that_kept_an_off_target_citation_coerces_on`.
        graph = (
            SuspicionEntry(player_id="p-2", suspicion=0.40, trust=0.5),
            SuspicionEntry(player_id="p-3", suspicion=0.80, trust=0.5),
        )
        result = self._chain(
            ballot=_ballot(target="p-2", primary_reason_id="m-1:turn-0"),
            suspicion_graph=graph,
            contradictions=(),
        )
        assert result.target == "p-3"
        assert result.primary_reason_id == "m-1:turn-0"
        assert UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3") not in (
            result.rationale_text
        )
        # The direct-vote twin: the same citation on an outright p-3 eject
        # passes the gate the same way -- the redirect adds nothing.
        direct = guard_ballot_citation(
            ballot=_ballot(target="p-3", primary_reason_id="m-1:turn-0"),
            contradictions=(),
        )
        assert direct.target == "p-3"

    def test_production_chain_redirects_then_gates_the_redirected_target(
        self,
    ) -> None:
        # The same ordering proven through the REAL _collect_one_ballot chain
        # (not a hand-composed pair): p-1's rendered graph reads MUST-vote off
        # p-3's 0.80 row while the named target p-2 renders 0.40 (under-gate),
        # so guard_ballot_target_graph redirects the eject to p-3 FIRST; the
        # citation gate (unconditional since 16.17) then judges the REDIRECTED
        # zero-flag target and coerces. The recorded marker stack pins the
        # production order: the gate's prefix names p-3 (never p-2) and sits
        # OUTSIDE the redirect marker.
        participants = (
            _participant(
                "p-1",
                suspicion_graph=(
                    SuspicionEntry(player_id="p-2", suspicion=0.4, trust=0.5),
                    SuspicionEntry(player_id="p-3", suspicion=0.8, trust=0.5),
                ),
            ),
            _participant("p-2"),
            _participant("p-3"),
            _participant("p-4"),
        )
        result, _ = _run_meeting(
            _make_responder(vote_targets={"p-1": "p-2"}),
            participants=participants,
        )

        ballot = next(b for b in result.ballots if b.voter == "p-1")
        assert ballot.target == "SKIP"
        assert ballot.rationale_text.startswith(
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3")
            + BALLOT_TARGET_REDIRECT_MARKER.format(target="p-2")
        )


class TestCitationGateOnProductionPath:
    """End-to-end through ``MeetingManager.run`` with the scripted client."""

    _EJECT_VOTES = {"p-1": "p-3", "p-2": "p-3", "p-4": "p-3"}

    def test_uncited_zero_flag_ejects_coerce_and_flip_to_skip(self) -> None:
        # DEFAULT (the gate is unconditional since 16.17): today's sanctioned
        # null-citation ballots (vote_ballot.j2: "use null when your call rests on
        # your own memory") are coerced to SKIP -- a zero-flag eject with no
        # citation never stands.
        result, _ = _run_meeting(_make_responder(vote_targets=self._EJECT_VOTES))

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None
        for voter in self._EJECT_VOTES:
            ballot = next(b for b in result.ballots if b.voter == voter)
            assert ballot.target == "SKIP"
            assert ballot.rationale_text.startswith(
                UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3")
            )

    def test_flagged_target_ejects_uncited(self) -> None:
        # The conflicting-alibi recipe mints exactly one alibi_conflict flag
        # with subjects == ("p-2",): an uncited EJECT of p-2 is flag-backed
        # and must ride through the gate untouched.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-3", "p-3": None},
                claims_by=_conflict_claims(),
                vote_targets={"p-1": "p-2", "p-3": "p-2", "p-4": "p-2"},
            )
        )

        assert result.contradictions
        assert all("p-2" in ref.subjects for ref in result.contradictions)
        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-2"
        assert not any(
            "coerced to SKIP" in ballot.rationale_text for ballot in result.ballots
        )

    def test_turn_citation_satisfies(self) -> None:
        # "m-1:turn-0" is the canonical id of this meeting's opening turn
        # (turn ids are "{meeting_id}:turn-{N}" and _run_meeting pins
        # meeting_id="m-1"), so the citation validates and the eject stands.
        result, _ = _run_meeting(
            _make_responder(
                vote_targets=self._EJECT_VOTES,
                vote_reason_ids={voter: "m-1:turn-0" for voter in self._EJECT_VOTES},
            )
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"
        for voter in self._EJECT_VOTES:
            ballot = next(b for b in result.ballots if b.voter == voter)
            assert ballot.target == "p-3"
            assert ballot.primary_reason_id == "m-1:turn-0"

    def test_observation_citation_satisfies(self) -> None:
        # The 16.5 private-citation path: each voter cites an id from their
        # OWN threaded valid-id set, so the citation validates and the
        # zero-flag eject stands -- the honest-witness path the gate must
        # never silence (the C3 catch).
        cited = {"p-1": "p-1:410:0", "p-2": "p-2:410:0", "p-4": "p-4:410:0"}
        by_voter: dict[str, ObservationId | None] = dict(cited)
        result, _ = _run_meeting(
            _obs_vote_responder(
                observation_ids_by_voter=by_voter,
                targets=self._EJECT_VOTES,
            ),
            participants=_participants(
                {voter: (obs_id,) for voter, obs_id in cited.items()}
            ),
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"
        for voter, obs_id in cited.items():
            ballot = next(b for b in result.ballots if b.voter == voter)
            assert ballot.target == "p-3"
            assert ballot.primary_reason_observation_id == obs_id

    def test_fabricated_observation_citation_nulls_then_coerces(self) -> None:
        # The nulls-then-coerces composition: 16.5's validator nulls the
        # fabricated id with its own marker FIRST (the voter's valid set is
        # p-2:410:0, the citation is not), then the gate sees a bare null on
        # a zero-flag eject and coerces -- two markers, stacked in chain
        # order (the gate's prefix outermost).
        result, _ = _run_meeting(
            _obs_vote_responder(
                observation_ids_by_voter={"p-2": "p-2:999:9"},
                targets={"p-2": "p-3"},
            ),
            participants=_participants({"p-2": ("p-2:410:0",)}),
        )

        ballot = next(b for b in result.ballots if b.voter == "p-2")
        assert ballot.target == "SKIP"
        assert ballot.primary_reason_observation_id is None
        assert ballot.rationale_text.startswith(
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3")
            + INVALID_OBSERVATION_ID_MARKER.format(observation_id="p-2:999:9")
        )
        assert result.outcome == "SKIPPED"

    def test_fabricated_turn_citation_nulls_then_coerces(self) -> None:
        # Same composition through the turn-id channel: a dangling reason id
        # with an unrecoverable ordinal nulls (INVALID_REASON_ID_MARKER),
        # then the gate coerces the now-uncited zero-flag eject.
        result, _ = _run_meeting(
            _make_responder(
                vote_targets={"p-2": "p-3"},
                vote_reason_ids={"p-2": "m-3:turn-14"},
            )
        )

        ballot = next(b for b in result.ballots if b.voter == "p-2")
        assert ballot.target == "SKIP"
        assert ballot.primary_reason_id is None
        assert ballot.rationale_text.startswith(
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3")
            + INVALID_REASON_ID_MARKER.format(reason_id="m-3:turn-14")
        )


class TestAbsenceDeltaNonInteraction:
    """Task 16.8's absence prior cannot reach the gate except via flags.

    The absence delta moves SUSPICION and mints no ContradictionRef, so by
    construction it cannot change the gate's zero-flag boundary. Pinned two
    ways: structurally (the guard consumes no suspicion input at all) and
    behaviorally (an arbitrarily large suspicion lift on a zero-flag target
    leaves the coercion exactly in place; only a flag lifts it).
    """

    def test_guard_signature_admits_no_suspicion_input(self) -> None:
        # The pin is the EXACT parameter set, so a widening is a deliberate
        # edit here rather than a silent one. It widened once, for the
        # relevance lever: the three names below are a version switch and the
        # two surfaces aboutness is read off, and not one of them is a
        # suspicion value -- which is the claim this case makes and the reason
        # it is an equality rather than a membership test.
        assert set(inspect.signature(guard_ballot_citation).parameters) == {
            "ballot",
            "contradictions",
            "citation_relevance_version",
            "turns",
            "prompt_lines",
        }

    def test_suspicion_lift_never_moves_the_gate_only_flags_do(self) -> None:
        ballot = _ballot(target="p-2")
        graph_high = (SuspicionEntry(player_id="p-2", suspicion=0.99, trust=0.5),)
        # An absence-shaped lift keeps the target over the §4.6 gate, so the
        # redirect guard passes the eject through untouched -- and the
        # citation gate still coerces: suspicion is not evidence.
        redirected = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=graph_high,
            candidate_targets=("p-2",),
            skip_confidence_threshold=0.6,
        )
        assert redirected is ballot
        assert (
            guard_ballot_citation(ballot=redirected, contradictions=()).target == "SKIP"
        )
        # The ONLY escape channel is a flag -- which absence never mints.
        assert (
            guard_ballot_citation(ballot=redirected, contradictions=(_flag("p-2"),))
            is ballot
        )


def _turn(
    *,
    turn_id: str = "m-1:turn-0",
    turn_index: int = 0,
    speaker: str = "p-3",
    free_text: str = "I was in STORAGE the whole round.",
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=turn_id,
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="opening",
        reply_to=None,
        free_text=free_text,
    )


@dataclass(frozen=True)
class _CommittedMeeting:
    """One committed replay's meeting, as the three surfaces the guard reads."""

    ballots: tuple[VoteBallot, ...]
    contradictions: tuple[ContradictionRef, ...]
    turns: tuple[MeetingTurn, ...]
    prompts_by_agent: Mapping[str, tuple[str, ...]]

    def lines_for(self, voter: str) -> tuple[str, ...]:
        return tuple(
            line
            for prompt in self.prompts_by_agent.get(voter, ())
            for line in prompt.splitlines()
        )


def _committed_meetings() -> list[_CommittedMeeting]:
    """Every meeting of the two committed `replays/samples/` sets.

    Recorded bytes rather than a hand-built fixture: the byte-identity claim is
    about what the guard does to ballots that EXIST, and 986 of them do.
    """

    meetings: list[_CommittedMeeting] = []
    for path in sorted((_REPO_ROOT / "replays" / "samples").glob("*/*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("kind") != "meeting":
                continue
            prompts: dict[str, list[str]] = {}
            for call in row.get("llm_calls", ()):
                agent = call.get("agent_id")
                if isinstance(agent, str) and call.get("prompt"):
                    prompts.setdefault(agent, []).append(call["prompt"])
            meetings.append(
                _CommittedMeeting(
                    ballots=tuple(
                        VoteBallot.model_validate(ballot) for ballot in row["ballots"]
                    ),
                    contradictions=tuple(
                        ContradictionRef.model_validate(flag)
                        for flag in row["contradictions"]
                    ),
                    turns=tuple(
                        MeetingTurn.model_validate(turn)
                        for turn in row["transcript"]["turns"]
                    ),
                    prompts_by_agent={
                        agent: tuple(texts) for agent, texts in prompts.items()
                    },
                )
            )
    return meetings


class TestCitationRelevanceLever:
    """The relevance half of the gate, behind ``citation_relevance_version``.

    ON, a citation must also BEAR ON the ballot's own target: a resolved turn
    id about somebody else, or a private observation id whose rendered line
    names somebody else, takes the disposition an uncited EJECT takes -- exempt
    when the target is contradiction-flagged, coerced to SKIP otherwise -- under
    its own marker and its own ``off_target_coerced`` rewrite reason.

    Every case below is a pair: the same ballot OFF and ON. OFF is the
    pre-lever guard byte for byte, which is what makes the lever a lever.
    """

    def test_marker_literal_pinned_exactly(self) -> None:
        # Same discipline as the uncited marker: the display layer parses it
        # by the ``{x!r}`` repr interpolation, so it is pinned byte for byte.
        assert (
            OFF_TARGET_CITATION_EJECT_MARKER
            == "[off-target citation for eject target {target!r} coerced to SKIP] "
        )

    def test_an_on_target_turn_citation_passes_on_and_off(self) -> None:
        ballot = _ballot(target="p-3", primary_reason_id="m-1:turn-0")
        turns = (_turn(speaker="p-3"),)
        assert guard_ballot_citation(ballot=ballot, contradictions=()) is ballot
        assert (
            guard_ballot_citation(
                ballot=ballot,
                contradictions=(),
                citation_relevance_version=1,
                turns=turns,
            )
            is ballot
        )

    def test_an_off_target_turn_citation_passes_off_and_coerces_on(self) -> None:
        # PLANTED against the pre-lever gate: p-1 ejects p-2 while citing a
        # turn p-3 spoke about p-4. Today's gate passes it -- the id resolves.
        ballot = _ballot(
            target="p-2",
            primary_reason_id="m-1:turn-0",
            rationale_text="they have been quiet.",
        )
        turns = (_turn(speaker="p-3", free_text="I was in STORAGE with p-4."),)
        assert guard_ballot_citation(ballot=ballot, contradictions=()) is ballot

        coerced = guard_ballot_citation(
            ballot=ballot,
            contradictions=(),
            citation_relevance_version=1,
            turns=turns,
        )
        assert coerced.target == "SKIP"
        assert coerced.guard_rewrite_reason == "off_target_coerced"
        assert coerced.guard_redirected_from == "p-2"
        assert coerced.rationale_text == (
            OFF_TARGET_CITATION_EJECT_MARKER.format(target="p-2")
            + "they have been quiet."
        )
        # The citation is REAL and is kept: it is the evidence the coercion
        # rests on, unlike the uncited class where both fields are already null.
        assert coerced.primary_reason_id == "m-1:turn-0"

    def test_a_turn_naming_the_target_bears_on_it_however_it_names_them(
        self,
    ) -> None:
        # The aboutness rule reads the whole dumped turn, not the speaker
        # alone: a turn about p-2 spoken by p-3 is about p-2.
        ballot = _ballot(target="p-2", primary_reason_id="m-1:turn-0")
        turns = (_turn(speaker="p-3", free_text="p-2 never said where they were."),)
        assert (
            guard_ballot_citation(
                ballot=ballot,
                contradictions=(),
                citation_relevance_version=1,
                turns=turns,
            )
            is ballot
        )

    def test_a_flagged_target_still_ejects_on_an_off_target_citation(self) -> None:
        # ONE exemption, shared by both classes: the flag IS the in-game
        # source, so a flagged target is convictable however the ballot cites.
        ballot = _ballot(target="p-2", primary_reason_id="m-1:turn-0")
        turns = (_turn(speaker="p-3", free_text="I was in STORAGE with p-4."),)
        assert (
            guard_ballot_citation(
                ballot=ballot,
                contradictions=(_flag("p-2"),),
                citation_relevance_version=1,
                turns=turns,
            )
            is ballot
        )

    def test_an_off_target_observation_citation_coerces_on(self) -> None:
        ballot = _ballot(target="p-2", primary_reason_observation_id="p-1:4:0")
        lines = [
            "[obs p-1:4:0] tick 4: p-3 left ELECTRICAL.",
            "[obs p-1:5:0] tick 5: p-2 in MEDBAY.",
        ]
        assert guard_ballot_citation(ballot=ballot, contradictions=()) is ballot
        coerced = guard_ballot_citation(
            ballot=ballot,
            contradictions=(),
            citation_relevance_version=1,
            prompt_lines=lines,
        )
        assert coerced.target == "SKIP"
        assert coerced.guard_rewrite_reason == "off_target_coerced"
        # The LINE is the unit: the id and the name are both in this prompt,
        # and a prompt-wide search would have called this relevant.
        on_target = _ballot(target="p-2", primary_reason_observation_id="p-1:5:0")
        assert (
            guard_ballot_citation(
                ballot=on_target,
                contradictions=(),
                citation_relevance_version=1,
                prompt_lines=lines,
            )
            is on_target
        )

    def test_a_cited_id_is_not_satisfied_by_a_longer_ids_line(self) -> None:
        # PLANTED against the substring rule the shared module shipped with:
        # `p-1:4:1` is a string prefix of `p-1:4:10`, so the voter's TENTH
        # observation of tick 4 -- the only line naming p-2 -- answered for its
        # FIRST, and this EJECT passed the gate ON. Ids are
        # `{agent}:{tick}:{seq}`, so every voter reaching a tenth observation in
        # a tick renders the collision.
        ballot = _ballot(target="p-2", primary_reason_observation_id="p-1:4:1")
        lines = [
            "[obs p-1:4:1] tick 4: p-3 left ELECTRICAL.",
            "[obs p-1:4:10] tick 4: p-2 vented in MEDBAY.",
        ]
        coerced = guard_ballot_citation(
            ballot=ballot,
            contradictions=(),
            citation_relevance_version=1,
            prompt_lines=lines,
        )
        assert coerced.target == "SKIP"
        assert coerced.guard_rewrite_reason == "off_target_coerced"
        # The ballot that cites the vent line itself still ejects.
        on_target = _ballot(target="p-2", primary_reason_observation_id="p-1:4:10")
        assert (
            guard_ballot_citation(
                ballot=on_target,
                contradictions=(),
                citation_relevance_version=1,
                prompt_lines=lines,
            )
            is on_target
        )

    def test_an_uncited_eject_keeps_its_own_reason_under_the_lever(self) -> None:
        # The lever adds a class; it does not relabel the one that was there.
        ballot = _ballot(target="p-2")
        coerced = guard_ballot_citation(
            ballot=ballot, contradictions=(), citation_relevance_version=1
        )
        assert coerced.guard_rewrite_reason == "uncited_coerced"
        assert coerced.rationale_text.startswith(
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-2")
        )

    def test_the_redirect_that_kept_an_off_target_citation_coerces_on(self) -> None:
        # The fifth run's seed 8006, as a fixture: an under-gate eject of p-2
        # is redirected onto the zero-flag argmax p-3 and KEEPS a citation
        # about p-2. OFF it passes on the kept citation (the deliberate scope
        # choice `test_redirect_keeps_citation_and_passes_the_gate` pins); ON
        # it coerces, because the gate reads the RECORDED target.
        graph = (
            SuspicionEntry(player_id="p-2", suspicion=0.40, trust=0.5),
            SuspicionEntry(player_id="p-3", suspicion=0.80, trust=0.5),
        )
        turns = (_turn(speaker="p-4", free_text="p-2 was nowhere near ADMIN."),)
        redirected = guard_ballot_target_graph(
            ballot=_ballot(target="p-2", primary_reason_id="m-1:turn-0"),
            voter_id="p-1",
            suspicion_graph=graph,
            candidate_targets=("p-2", "p-3"),
            skip_confidence_threshold=0.6,
        )
        assert redirected.target == "p-3"
        assert redirected.guard_rewrite_reason == "under_gate_redirect"
        assert guard_ballot_citation(ballot=redirected, contradictions=()) is redirected

        coerced = guard_ballot_citation(
            ballot=redirected,
            contradictions=(),
            citation_relevance_version=1,
            turns=turns,
        )
        assert coerced.target == "SKIP"
        # The KNOWN TRAP: `ballot_target_rewrite_provenance` records the FIRST
        # rewrite only, so the typed field still reads `under_gate_redirect`
        # while BOTH markers stack on the rationale. A count of this class
        # reads the marker stack, never the single field.
        assert coerced.guard_rewrite_reason == "under_gate_redirect"
        assert coerced.rationale_text.startswith(
            OFF_TARGET_CITATION_EJECT_MARKER.format(target="p-3")
            + BALLOT_TARGET_REDIRECT_MARKER.format(target="p-2")
        )

    def test_the_lever_off_leaves_every_committed_ballot_untouched(self) -> None:
        """Byte-identity, ballot by ballot, over the committed replay sets.

        Both `replays/samples/` sets are replayed through the guard twice: once
        with no lever argument at all (today's call) and once with the lever at
        ``None`` and BOTH surfaces supplied. Every ballot must come back
        identical -- which is the claim `scripts/verify_samples.sh` and the four
        `--check` report runs make about the committed bytes, made here about
        the guard itself, ballot by ballot rather than file by file.
        """

        seen = 0
        moved_when_on = 0
        for meeting in _committed_meetings():
            for ballot in meeting.ballots:
                seen += 1
                today = guard_ballot_citation(
                    ballot=ballot, contradictions=meeting.contradictions
                )
                lever_off = guard_ballot_citation(
                    ballot=ballot,
                    contradictions=meeting.contradictions,
                    citation_relevance_version=None,
                    turns=meeting.turns,
                    prompt_lines=meeting.lines_for(ballot.voter),
                )
                assert lever_off == today
                lever_on = guard_ballot_citation(
                    ballot=ballot,
                    contradictions=meeting.contradictions,
                    citation_relevance_version=1,
                    turns=meeting.turns,
                    prompt_lines=meeting.lines_for(ballot.voter),
                )
                if lever_on != today:
                    moved_when_on += 1
                    assert lever_on.target == "SKIP"
        assert seen == 986, seen
        # The OFF assertion above is only worth making because ON moves
        # something on this very set: a fixture the lever cannot reach would
        # prove byte-identity vacuously.
        assert moved_when_on > 0, moved_when_on
