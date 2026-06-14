"""Unit tests for the vote-correctness metric (DESIGN.md §11.3).

Fixtures are built by instantiating ``report_schema`` / ``meetings.schemas``
models directly -- no tournament run -- so the tests pin the "real evidence"
predicate, the impostor-vs-crewmate classification, the kill-witness tick
window, and the partial-replay robustness rules without any orchestrator or LLM
dependency.

The predicate is exercised adversarially: an impostor ejected on *no* evidence
(or on an accusation/ballot alone) must score as incorrect, or the metric would
collapse into the impostor-ejection rate it exists to refine.

Task 9.6 (metric hygiene; DESIGN.md §11.3, §5.5; audit gp-2) adds two suites
here per the task contract: the ``vote_correctness_rate`` bug-sentinel
semantics (the rate is structurally pinned to 1.0 on production-shaped data
and must never be read as the lead), and the
:class:`eval.meeting_quality.ConversionReport` conversion leads + SKIP
sentinels, including the committed 9p/2i report's audited regression pins.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.meeting_quality import (
    BallotTargetRedirectReport,
    ConversionReport,
    DefaultedBallotReport,
    TournamentEvalReport,
    compute_ballot_target_redirects,
    compute_conversion_report,
    compute_defaulted_ballots,
)
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from eval.vote_correctness import (
    KILL_WITNESS_TICK_WINDOW,
    VOTE_CORRECTNESS_MIN_SAMPLE,
    VoteCorrectnessReport,
    compute_vote_correctness,
)
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    DEFAULT_VOTE_RATIONALE,
    INVALID_VOTE_TARGET_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
)
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    FoundBodyObservation,
    MeetingOutcome,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
    VoteBallot,
)
from orchestrator.replay import FailedCallReplayEntry, LLMCallRecord

# Default roster: p-3 is the impostor, the rest crewmates.
_ROLES: Mapping[PlayerId, Role] = {
    "p-0": "CREWMATE",
    "p-1": "CREWMATE",
    "p-2": "CREWMATE",
    "p-3": "IMPOSTOR",
}
_IMPOSTOR: PlayerId = "p-3"
_CREWMATE: PlayerId = "p-1"


# ---------------------------------------------------------------------------
# Fixture builders -- minimal, focused on what the metric actually reads
# ---------------------------------------------------------------------------


def _contradiction(
    *, subjects: tuple[PlayerId, ...], contradiction_id: str = "c-1"
) -> ContradictionRef:
    return ContradictionRef(
        contradiction_id=contradiction_id,
        kind="alibi_vs_sighting",
        event_a_id="alibi:x",
        event_b_id="saw:x",
        subjects=subjects,
        description="",
    )


def _found_body(
    *, tick: int, room: str, body_of: PlayerId = "p-9"
) -> FoundBodyObservation:
    return FoundBodyObservation(
        type="found_body", tick=tick, body_of=body_of, room=room
    )


def _saw(*, subject: PlayerId, tick: int, room: str) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", subject=subject, tick=tick, room=room
    )


def _report(
    *,
    agent_id: PlayerId = "p-0",
    tick: int = 40,
    observations: tuple[FoundBodyObservation | SawPlayerObservation, ...] = (),
) -> MeetingTurn:
    """An ``opening`` chain turn carrying the reporter's observations (§5.2)."""

    return MeetingTurn(
        turn_id=f"{agent_id}:turn-{tick}",
        turn_index=0,
        speaker=agent_id,
        turn_kind="opening",
        reply_to=None,
        observations=observations,
        claims=(),
        free_text="",
    )


def _accusation_statement(
    *, against: PlayerId, sid: str = "s-1", speaker: PlayerId = "p-0"
) -> MeetingTurn:
    """A ``reply`` chain turn carrying one accusation claim (§5.2)."""

    return MeetingTurn(
        turn_id=sid,
        turn_index=1,
        speaker=speaker,
        turn_kind="reply",
        reply_to=None,
        observations=(),
        claims=(
            AccusationClaim(
                type="accusation",
                against=against,
                confidence=0.9,
                reason="looked guilty",
            ),
        ),
        free_text="",
    )


def _ballot(
    *,
    target: PlayerId,
    reason_id: str | None = "s-1",
    voter: PlayerId = "p-0",
    rationale_text: str = "",
) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.9,
        primary_reason_id=reason_id,
        rationale_text=rationale_text,
    )


def _vote_call(*, agent_id: PlayerId, rendered_max: float) -> LLMCallRecord:
    """A vote-prompt LLM call carrying the rendered §4.6 gate line.

    The prompt body mirrors the v5 ``vote_ballot.j2`` render (including the
    line wrap between "is" and the bolded value) so the test exercises the
    same parse the committed replays do.
    """

    return LLMCallRecord(
        call_kind="meeting",
        model="fixture-model",
        prompt=(
            "## Decision rules\n\n"
            "1. **Gate verdict — already computed for you (DESIGN.md §4.6).**\n"
            "   Your maximum suspicion among the living ejection targets is\n"
            f"   **{rendered_max:.2f}**; the skip threshold is **0.60**.\n"
        ),
        response_text="{}",
        input_tokens=10,
        output_tokens=5,
        cost_usd=0.0,
        agent_id=agent_id,
    )


def _meeting(
    *,
    outcome: MeetingOutcome,
    ejected: PlayerId | None,
    meeting_id: str = "m-0",
    tick: int = 40,
    reports: tuple[MeetingTurn, ...] = (),
    statements: tuple[MeetingTurn, ...] = (),
    contradictions: tuple[ContradictionRef, ...] = (),
    ballots: tuple[VoteBallot, ...] = (),
    llm_calls: tuple[LLMCallRecord, ...] = (),
) -> MeetingReport:
    # The chain is one ordered ``turns`` list (DESIGN.md §5.2): the opening
    # ``reports`` turn(s) followed by any ``statements`` (reply / opt-in) turns.
    return MeetingReport(
        meeting_id=meeting_id,
        tick=tick,
        triggered_by="p-0",
        trigger="report",
        outcome=outcome,
        ejected_player_id=ejected,
        transcript=MeetingTranscript(turns=tuple(reports) + tuple(statements)),
        ballots=ballots,
        contradictions=contradictions,
        llm_calls=llm_calls,
    )


def _game(
    *,
    meetings: tuple[MeetingReport, ...],
    roles: Mapping[PlayerId, Role] = _ROLES,
    game_id: str = "g-0",
    seed: int = 1,
) -> GameReport:
    return GameReport(
        game_id=game_id,
        seed=seed,
        winner=None,
        reason="fixture",
        final_tick=100,
        roles=roles,
        replay_ref=f"replay-seed-{seed}.jsonl",
        meetings=meetings,
        failed_calls=(),
        prompt_versions={},
        cost=GameCostSummary(
            total_cost_usd=0.0,
            total_input_tokens=0,
            total_output_tokens=0,
            by_model={},
        ),
    )


def _tournament(*games: GameReport) -> TournamentReport:
    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=games,
        seeds_used=tuple(game.seed for game in games),
    )


def _one_meeting_report(meeting: MeetingReport) -> TournamentReport:
    return _tournament(_game(meetings=(meeting,)))


# ---------------------------------------------------------------------------
# Correct ejections: impostor backed by structured evidence
# ---------------------------------------------------------------------------


def test_impostor_ejected_with_naming_contradiction_is_correct() -> None:
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
        )
    )

    result = compute_vote_correctness(report)

    assert result.total_ejections == 1
    assert result.impostor_ejections == 1
    assert result.crewmate_ejections == 0
    assert result.evidence_backed_impostor_ejections == 1
    assert result.vote_correctness_rate == 1.0


def test_impostor_ejected_with_kill_witness_chain_is_correct() -> None:
    # One agent finds the body in ELECTRICAL@50; another places p-3 there @52.
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            reports=(
                _report(
                    agent_id="p-0",
                    observations=(_found_body(tick=50, room="ELECTRICAL"),),
                ),
                _report(
                    agent_id="p-2",
                    observations=(_saw(subject=_IMPOSTOR, tick=52, room="ELECTRICAL"),),
                ),
            ),
        )
    )

    result = compute_vote_correctness(report)

    assert result.impostor_ejections == 1
    assert result.evidence_backed_impostor_ejections == 1
    assert result.vote_correctness_rate == 1.0


def test_kill_witness_chain_within_single_report_is_correct() -> None:
    # Both observations on the same agent's report still form a valid chain.
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            reports=(
                _report(
                    agent_id="p-0",
                    observations=(
                        _found_body(tick=50, room="STORAGE"),
                        _saw(subject=_IMPOSTOR, tick=50, room="STORAGE"),
                    ),
                ),
            ),
        )
    )

    assert compute_vote_correctness(report).evidence_backed_impostor_ejections == 1


def test_kill_witness_chain_at_window_boundary_is_evidence() -> None:
    # |sighting - found| == K exactly is inside the inclusive window.
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            reports=(
                _report(observations=(_found_body(tick=50, room="ELECTRICAL"),)),
                _report(
                    observations=(
                        _saw(
                            subject=_IMPOSTOR,
                            tick=50 + KILL_WITNESS_TICK_WINDOW,
                            room="ELECTRICAL",
                        ),
                    )
                ),
            ),
        )
    )

    assert compute_vote_correctness(report).evidence_backed_impostor_ejections == 1


# ---------------------------------------------------------------------------
# Incorrect ejections: impostor ejected without structured evidence
# ---------------------------------------------------------------------------


def test_impostor_ejected_with_no_evidence_is_incorrect() -> None:
    report = _one_meeting_report(_meeting(outcome="EJECTED", ejected=_IMPOSTOR))

    result = compute_vote_correctness(report)

    assert result.impostor_ejections == 1
    assert result.evidence_backed_impostor_ejections == 0
    assert result.vote_correctness_rate == 0.0


def test_impostor_ejected_on_accusation_and_ballot_alone_is_incorrect() -> None:
    # An accusation naming p-3 plus a ballot citing it -- but no contradiction
    # and no kill-witness chain. The metric must NOT count the accusation/ballot
    # flow (that is the circular signal it exists to avoid), so this is incorrect.
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            statements=(_accusation_statement(against=_IMPOSTOR, sid="s-1"),),
            ballots=(_ballot(target=_IMPOSTOR, reason_id="s-1"),),
        )
    )

    result = compute_vote_correctness(report)

    assert result.impostor_ejections == 1
    assert result.evidence_backed_impostor_ejections == 0
    assert result.vote_correctness_rate == 0.0


def test_contradiction_naming_other_player_does_not_back_ejection() -> None:
    # A real contradiction exists, but it names a different player than the one
    # ejected -- it is not evidence against the ejected impostor.
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            contradictions=(_contradiction(subjects=("p-1", "p-2")),),
        )
    )

    assert compute_vote_correctness(report).evidence_backed_impostor_ejections == 0


def test_kill_witness_chain_outside_window_is_not_evidence() -> None:
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            reports=(
                _report(observations=(_found_body(tick=50, room="ELECTRICAL"),)),
                _report(
                    observations=(
                        _saw(
                            subject=_IMPOSTOR,
                            tick=50 + KILL_WITNESS_TICK_WINDOW + 1,
                            room="ELECTRICAL",
                        ),
                    )
                ),
            ),
        )
    )

    assert compute_vote_correctness(report).evidence_backed_impostor_ejections == 0


def test_kill_witness_chain_in_wrong_room_is_not_evidence() -> None:
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            reports=(
                _report(observations=(_found_body(tick=50, room="ELECTRICAL"),)),
                _report(
                    observations=(_saw(subject=_IMPOSTOR, tick=51, room="MEDBAY"),)
                ),
            ),
        )
    )

    assert compute_vote_correctness(report).evidence_backed_impostor_ejections == 0


def test_kill_witness_chain_for_other_player_does_not_back_ejection() -> None:
    # The body is co-located with a sighting of p-1, not the ejected p-3.
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            reports=(
                _report(observations=(_found_body(tick=50, room="ELECTRICAL"),)),
                _report(
                    observations=(_saw(subject="p-1", tick=51, room="ELECTRICAL"),)
                ),
            ),
        )
    )

    assert compute_vote_correctness(report).evidence_backed_impostor_ejections == 0


# ---------------------------------------------------------------------------
# Crewmate ejections, skips, empty games -- contribute zero to impostor buckets
# ---------------------------------------------------------------------------


def test_ejected_crewmate_counts_toward_total_not_impostor() -> None:
    # Even with a contradiction naming the crewmate, a crewmate ejection never
    # touches the impostor buckets; with no impostor ejections the rate is None.
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_CREWMATE,
            contradictions=(_contradiction(subjects=(_CREWMATE,)),),
        )
    )

    result = compute_vote_correctness(report)

    assert result.total_ejections == 1
    assert result.impostor_ejections == 0
    assert result.crewmate_ejections == 1
    assert result.evidence_backed_impostor_ejections == 0
    assert result.vote_correctness_rate is None


def test_skipped_meeting_contributes_nothing() -> None:
    report = _one_meeting_report(_meeting(outcome="SKIPPED", ejected=None))

    result = compute_vote_correctness(report)

    assert result.total_ejections == 0
    assert result.impostor_ejections == 0
    assert result.crewmate_ejections == 0
    assert result.vote_correctness_rate is None


def test_game_with_zero_meetings_contributes_nothing() -> None:
    report = _tournament(_game(meetings=()))

    result = compute_vote_correctness(report)

    assert result.total_ejections == 0
    assert result.vote_correctness_rate is None


def test_malformed_ejected_meeting_with_none_id_is_skipped() -> None:
    # EJECTED but ejected_player_id is None -- type-possible on MeetingReport
    # (no coupling validator). Treated as malformed partial-replay data: skipped.
    report = _one_meeting_report(_meeting(outcome="EJECTED", ejected=None))

    result = compute_vote_correctness(report)

    assert result.total_ejections == 0
    assert result.impostor_ejections == 0
    assert result.vote_correctness_rate is None


def test_empty_transcript_and_no_contradictions_never_raises() -> None:
    # Partial-replay robustness: an impostor ejection with nothing attached is
    # simply unbacked, not an error.
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            reports=(),
            contradictions=(),
        )
    )

    result = compute_vote_correctness(report)

    assert result.impostor_ejections == 1
    assert result.evidence_backed_impostor_ejections == 0


# ---------------------------------------------------------------------------
# Fail-loud: a real ejected player missing from the role ground truth
# ---------------------------------------------------------------------------


def test_ejected_player_absent_from_roles_fails_loud() -> None:
    report = _one_meeting_report(_meeting(outcome="EJECTED", ejected="p-99"))

    with pytest.raises(KeyError):
        compute_vote_correctness(report)


# ---------------------------------------------------------------------------
# Aggregation across games / meetings + alternative input shapes
# ---------------------------------------------------------------------------


def test_aggregates_across_games_and_meetings() -> None:
    backed_impostor = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-a",
        contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
    )
    unbacked_impostor = _meeting(outcome="EJECTED", ejected=_IMPOSTOR, meeting_id="m-b")
    crewmate_eject = _meeting(outcome="EJECTED", ejected=_CREWMATE, meeting_id="m-c")
    skipped = _meeting(outcome="SKIPPED", ejected=None, meeting_id="m-d")

    report = _tournament(
        _game(meetings=(backed_impostor, skipped), game_id="g-a", seed=1),
        _game(meetings=(unbacked_impostor, crewmate_eject), game_id="g-b", seed=2),
        _game(meetings=(), game_id="g-c", seed=3),
    )

    result = compute_vote_correctness(report)

    assert result.total_ejections == 3
    assert result.impostor_ejections == 2
    assert result.crewmate_ejections == 1
    assert result.evidence_backed_impostor_ejections == 1
    assert result.vote_correctness_rate == 0.5


def test_accepts_bare_sequence_of_game_reports() -> None:
    games = [
        _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
                ),
            ),
            seed=7,
        )
    ]

    # A bare sequence and the same games wrapped in a TournamentReport agree.
    from_sequence = compute_vote_correctness(games)
    from_report = compute_vote_correctness(_tournament(*games))

    assert from_sequence == from_report
    assert from_sequence.vote_correctness_rate == 1.0


def test_empty_tournament_yields_zero_with_none_rate() -> None:
    result = compute_vote_correctness(_tournament())

    assert result.total_ejections == 0
    assert result.impostor_ejections == 0
    assert result.vote_correctness_rate is None


# ---------------------------------------------------------------------------
# Task 7.11 derived honesty fields (audit C-C-4, F-F-2, gp-7)
# ---------------------------------------------------------------------------


def test_ejection_accuracy_uses_full_denominator_while_rate_excludes_crewmates() -> (
    None
):
    """The audit headline: rate 1.0 but ejection_accuracy 0.5 (gp-7 / C-C-4).

    Three evidence-backed impostor ejections and three crewmate ejections:
    vote_correctness_rate is 1.0 (3/3 backed impostor ejections), but
    ejection_accuracy is 0.5 (3 impostor / 6 total) -- the wrong crewmate
    ejections the rate silently drops.
    """

    impostor_ejections = tuple(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            meeting_id=f"m-i{i}",
            contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
        )
        for i in range(3)
    )
    crewmate_ejections = tuple(
        _meeting(outcome="EJECTED", ejected=_CREWMATE, meeting_id=f"m-c{i}")
        for i in range(3)
    )
    report = _tournament(
        _game(meetings=impostor_ejections + crewmate_ejections),
    )

    result = compute_vote_correctness(report)

    assert result.total_ejections == 6
    assert result.impostor_ejections == 3
    assert result.crewmate_ejections == 3
    assert result.vote_correctness_rate == 1.0  # reads "perfect" in isolation
    assert result.ejection_accuracy == 0.5  # the honest accuracy


def test_ejection_accuracy_none_when_no_ejections() -> None:
    result = compute_vote_correctness(
        _one_meeting_report(_meeting(outcome="SKIPPED", ejected=None))
    )
    assert result.total_ejections == 0
    assert result.ejection_accuracy is None


def test_small_n_flag_tracks_impostor_ejection_count() -> None:
    """vote_correctness_small_n is True below VOTE_CORRECTNESS_MIN_SAMPLE."""

    # One impostor ejection: well under the threshold -> flagged.
    few = compute_vote_correctness(
        _one_meeting_report(
            _meeting(
                outcome="EJECTED",
                ejected=_IMPOSTOR,
                contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
            )
        )
    )
    assert few.impostor_ejections < VOTE_CORRECTNESS_MIN_SAMPLE
    assert few.vote_correctness_small_n is True

    # Exactly VOTE_CORRECTNESS_MIN_SAMPLE impostor ejections: not flagged.
    many_meetings = tuple(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            meeting_id=f"m-{i}",
            contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
        )
        for i in range(VOTE_CORRECTNESS_MIN_SAMPLE)
    )
    many = compute_vote_correctness(_tournament(_game(meetings=many_meetings)))
    assert many.impostor_ejections == VOTE_CORRECTNESS_MIN_SAMPLE
    assert many.vote_correctness_small_n is False


def test_contradictions_flagged_but_ignored_counts_skipped_with_contradiction() -> None:
    """SKIPPED meetings carrying a contradiction feed the secondary signal (F-F-2)."""

    skipped_with_contra = _meeting(
        outcome="SKIPPED",
        ejected=None,
        meeting_id="m-skip-contra",
        contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
    )
    skipped_no_contra = _meeting(
        outcome="SKIPPED", ejected=None, meeting_id="m-skip-clean"
    )
    # An EJECTED meeting with a contradiction does NOT count (it acted on it).
    ejected_with_contra = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-eject",
        contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
    )
    report = _tournament(
        _game(
            meetings=(skipped_with_contra, skipped_no_contra, ejected_with_contra),
        )
    )

    result = compute_vote_correctness(report)

    assert result.contradictions_flagged_but_ignored == 1


# ---------------------------------------------------------------------------
# Result model contract
# ---------------------------------------------------------------------------


def test_result_model_is_frozen() -> None:
    result = compute_vote_correctness(_tournament())
    with pytest.raises(ValidationError):
        result.total_ejections = 5


def test_result_model_rejects_inconsistent_buckets() -> None:
    with pytest.raises(ValidationError, match="must equal total_ejections"):
        VoteCorrectnessReport(
            total_ejections=1,
            impostor_ejections=1,
            crewmate_ejections=1,
            evidence_backed_impostor_ejections=0,
            vote_correctness_rate=0.0,
            ejection_accuracy=1.0,
            vote_correctness_small_n=True,
            contradictions_flagged_but_ignored=0,
        )


def test_result_model_rejects_rate_when_no_impostor_ejections() -> None:
    with pytest.raises(ValidationError, match="must be None"):
        VoteCorrectnessReport(
            total_ejections=0,
            impostor_ejections=0,
            crewmate_ejections=0,
            evidence_backed_impostor_ejections=0,
            vote_correctness_rate=0.0,
            ejection_accuracy=None,
            vote_correctness_small_n=True,
            contradictions_flagged_but_ignored=0,
        )


def test_result_model_rejects_backed_exceeding_impostor() -> None:
    with pytest.raises(ValidationError, match="cannot exceed impostor_ejections"):
        VoteCorrectnessReport(
            total_ejections=1,
            impostor_ejections=1,
            crewmate_ejections=0,
            evidence_backed_impostor_ejections=2,
            vote_correctness_rate=1.0,
            ejection_accuracy=1.0,
            vote_correctness_small_n=True,
            contradictions_flagged_but_ignored=0,
        )


def test_result_model_rejects_ejection_accuracy_set_with_zero_ejections() -> None:
    with pytest.raises(ValidationError, match="ejection_accuracy must be None"):
        VoteCorrectnessReport(
            total_ejections=0,
            impostor_ejections=0,
            crewmate_ejections=0,
            evidence_backed_impostor_ejections=0,
            vote_correctness_rate=None,
            ejection_accuracy=0.0,  # must be None when there are no ejections
            vote_correctness_small_n=True,
            contradictions_flagged_but_ignored=0,
        )


def test_result_model_rejects_none_ejection_accuracy_with_ejections() -> None:
    with pytest.raises(ValidationError, match="ejection_accuracy must be set"):
        VoteCorrectnessReport(
            total_ejections=1,
            impostor_ejections=0,
            crewmate_ejections=1,
            evidence_backed_impostor_ejections=0,
            vote_correctness_rate=None,
            ejection_accuracy=None,  # must be set when total_ejections > 0
            vote_correctness_small_n=True,
            contradictions_flagged_but_ignored=0,
        )


def test_result_model_rejects_negative_contradictions_ignored() -> None:
    with pytest.raises(ValidationError, match="must be non-negative"):
        VoteCorrectnessReport(
            total_ejections=0,
            impostor_ejections=0,
            crewmate_ejections=0,
            evidence_backed_impostor_ejections=0,
            vote_correctness_rate=None,
            ejection_accuracy=None,
            vote_correctness_small_n=True,
            contradictions_flagged_but_ignored=-1,
        )


# ---------------------------------------------------------------------------
# Task 9.6 — vote_correctness_rate is a bug-sentinel, NOT a KPI (audit gp-2)
# ---------------------------------------------------------------------------


def test_vote_correctness_rate_is_documented_as_a_bug_sentinel() -> None:
    """The sentinel demotion is load-bearing documentation (Task 9.6 / F-F-1).

    A future reader deciding what to gate a Wave-1 A/B on reads the module and
    the result model. Both must label ``vote_correctness_rate`` a bug-sentinel
    that is structurally pinned to 1.0 — never the lead/KPI — so this asserts
    the labels outlive any docstring rewrite.
    """

    import eval.vote_correctness as vote_correctness_module

    for doc in (vote_correctness_module.__doc__, VoteCorrectnessReport.__doc__):
        assert doc is not None
        assert "bug-sentinel" in doc
        assert "NOT a KPI" in doc
        assert "structurally pinned" in doc


def test_rate_is_pinned_to_one_on_production_shaped_data() -> None:
    """The F-F-1 tautology, pinned as semantics: the rate cannot rank tables.

    In the live pipeline an ejection only happens when the detector flagged
    the ejected player, so every impostor ejection arrives WITH the naming
    contradiction that satisfies ``_has_real_evidence``. Two tables of very
    different quality — one all-impostor ejections, one mostly-wrong
    ejections — therefore BOTH read ``vote_correctness_rate == 1.0``; the
    published precision lead (``ejection_accuracy``) is what separates them.
    """

    def _detector_backed_table(crewmate_ejections: int) -> TournamentReport:
        # Every ejection carries a contradiction naming the ejected player —
        # the production §4.6 trigger shape, for impostor and crewmate alike.
        impostor = _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            meeting_id="m-imp",
            contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
        )
        wrong = tuple(
            _meeting(
                outcome="EJECTED",
                ejected=_CREWMATE,
                meeting_id=f"m-wrong-{i}",
                contradictions=(_contradiction(subjects=(_CREWMATE,)),),
            )
            for i in range(crewmate_ejections)
        )
        return _tournament(_game(meetings=(impostor, *wrong)))

    clean_table = compute_vote_correctness(_detector_backed_table(0))
    railroaded_table = compute_vote_correctness(_detector_backed_table(3))

    # The sentinel reads 1.0 on BOTH tables: it measures the engine's own
    # trigger, not voting quality. A drop below 1.0 would mean an ejection
    # without its own triggering evidence — a bug, not a metric move.
    assert clean_table.vote_correctness_rate == 1.0
    assert railroaded_table.vote_correctness_rate == 1.0
    # The published lead is what actually separates the tables.
    assert clean_table.ejection_accuracy == 1.0
    assert railroaded_table.ejection_accuracy == 0.25


# ---------------------------------------------------------------------------
# Task 9.6 — ConversionReport: the two published leads (DESIGN.md §11.3, §5.5)
# ---------------------------------------------------------------------------


def test_conversion_mirrors_precision_lead_from_vote_correctness() -> None:
    """The precision-lead fields are the owning analyzer's numbers, mirrored."""

    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    meeting_id="m-a",
                    contradictions=(_contradiction(subjects=(_IMPOSTOR,)),),
                ),
                _meeting(outcome="EJECTED", ejected=_CREWMATE, meeting_id="m-b"),
            )
        )
    )

    vote_correctness = compute_vote_correctness(report)
    threaded = compute_conversion_report(report, vote_correctness=vote_correctness)
    recomputed = compute_conversion_report(report)

    # Threading the precomputed result and letting the analyzer call the
    # owning module itself agree exactly (one fold, two call shapes).
    assert threaded == recomputed
    assert threaded.total_ejections == vote_correctness.total_ejections == 2
    assert threaded.impostor_ejections == vote_correctness.impostor_ejections == 1
    assert threaded.ejection_accuracy == vote_correctness.ejection_accuracy == 0.5


def test_recall_lead_counts_accused_meetings_and_conversions() -> None:
    """impostor_accused -> impostor-ejected over meetings naming a true impostor."""

    converted = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-converted",
        statements=(_accusation_statement(against=_IMPOSTOR, sid="s-1"),),
    )
    accused_but_skipped = _meeting(
        outcome="SKIPPED",
        ejected=None,
        meeting_id="m-skipped",
        statements=(_accusation_statement(against=_IMPOSTOR, sid="s-2"),),
    )
    accused_but_wrong_ejection = _meeting(
        outcome="EJECTED",
        ejected=_CREWMATE,
        meeting_id="m-wrong",
        statements=(_accusation_statement(against=_IMPOSTOR, sid="s-3"),),
    )
    # Accuses only a crewmate: not in the denominator even though an impostor
    # was ejected (the conversion is accusation -> ejection, not ejection alone).
    crew_accused_impostor_ejected = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-crew-accused",
        statements=(_accusation_statement(against=_CREWMATE, sid="s-4"),),
    )
    no_accusation = _meeting(outcome="SKIPPED", ejected=None, meeting_id="m-quiet")

    result = compute_conversion_report(
        _tournament(
            _game(
                meetings=(
                    converted,
                    accused_but_skipped,
                    accused_but_wrong_ejection,
                    crew_accused_impostor_ejected,
                    no_accusation,
                )
            )
        )
    )

    assert result.impostor_accused_meetings == 3
    assert result.impostor_accused_conversions == 1
    assert result.impostor_accused_conversion_rate == pytest.approx(1 / 3)


def test_recall_lead_counts_impostor_self_accusation() -> None:
    """A self-accusation by an impostor still puts a true impostor on the table."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        statements=(
            _accusation_statement(against=_IMPOSTOR, sid="s-1", speaker=_IMPOSTOR),
        ),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.impostor_accused_meetings == 1
    assert result.impostor_accused_conversions == 0


def test_recall_lead_malformed_ejected_meeting_cannot_convert() -> None:
    """EJECTED with a None ejected_player_id counts as accused, not converted."""

    malformed = _meeting(
        outcome="EJECTED",
        ejected=None,
        statements=(_accusation_statement(against=_IMPOSTOR, sid="s-1"),),
    )

    result = compute_conversion_report(_one_meeting_report(malformed))

    assert result.impostor_accused_meetings == 1
    assert result.impostor_accused_conversions == 0


def test_recall_lead_rate_is_none_when_no_meeting_accused_an_impostor() -> None:
    result = compute_conversion_report(
        _one_meeting_report(_meeting(outcome="SKIPPED", ejected=None))
    )

    assert result.impostor_accused_meetings == 0
    assert result.impostor_accused_conversion_rate is None


# ---------------------------------------------------------------------------
# Task 9.6 — ConversionReport: SKIP sentinels over the rendered §4.6 verdict
# ---------------------------------------------------------------------------


def test_skip_ballots_classified_against_rendered_max() -> None:
    """CORRECT below the threshold, MISSED at/above it, inclusive boundary."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(target="SKIP", voter="p-0", reason_id=None),  # 0.55 correct
            _ballot(target="SKIP", voter="p-1", reason_id=None),  # 0.60 missed
            _ballot(target="SKIP", voter="p-2", reason_id=None),  # 0.80 missed
        ),
        llm_calls=(
            _vote_call(agent_id="p-0", rendered_max=0.55),
            _vote_call(agent_id="p-1", rendered_max=0.60),
            _vote_call(agent_id="p-2", rendered_max=0.80),
        ),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.skip_ballots == 3
    assert result.correct_skip_ballots == 1
    assert result.missed_skip_ballots == 2
    assert result.unclassified_skip_ballots == 0
    # Both missed voters are crew with valid targets: genuine inversions.
    assert result.missed_skip_impostor_voters == 0
    assert result.missed_skip_invalid_target == 0
    assert result.threshold_inversions == 2


def test_missed_skips_partition_impostor_then_invalid_then_genuine() -> None:
    """The MISSED partition: impostor voter > invalid-target marker > genuine.

    The audited shape (gp-2): most MISSED skips are impostor voters — by
    design (in-character self-preservation or teammate protection), NOT an
    error — so the count is a sentinel whose partition must be read, never a
    down-is-good metric. Within the impostor bucket the §7.12-coerced ballots
    (stamped with TEAMMATE_VOTE_TARGET_MARKER) are counted separately from
    voluntary declines, so the two by-design causes can never be confused.
    """

    invalid_marker = INVALID_VOTE_TARGET_MARKER.format(target="p-99")
    teammate_marker = TEAMMATE_VOTE_TARGET_MARKER.format(target="p-9")
    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            # Impostor voter over a met threshold, no marker: a VOLUNTARY
            # in-character decline (the only impostor shape on the audited
            # baseline, where the coercion guard never fired).
            _ballot(target="SKIP", voter=_IMPOSTOR, reason_id=None),
            # Crew voter whose hallucinated target was normalized to SKIP.
            _ballot(
                target="SKIP",
                voter="p-1",
                reason_id=None,
                rationale_text=invalid_marker + "I vote p-99.",
            ),
            # Crew voter, valid ballot, met threshold: genuine inversion.
            _ballot(target="SKIP", voter="p-2", reason_id=None),
        ),
        llm_calls=(
            _vote_call(agent_id=_IMPOSTOR, rendered_max=0.80),
            _vote_call(agent_id="p-1", rendered_max=0.75),
            _vote_call(agent_id="p-2", rendered_max=0.70),
        ),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.missed_skip_ballots == 3
    assert result.missed_skip_impostor_voters == 1
    assert result.missed_skip_teammate_coerced == 0  # voluntary, not coerced
    assert result.missed_skip_invalid_target == 1
    assert result.threshold_inversions == 1

    # The same impostor ballot actually rewritten by the §7.12 guard (the
    # recorded TEAMMATE marker) still lands in the impostor bucket AND is
    # counted as a real coercion.
    coerced = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_IMPOSTOR,
                reason_id=None,
                rationale_text=teammate_marker + "I vote p-9.",
            ),
        ),
        llm_calls=(_vote_call(agent_id=_IMPOSTOR, rendered_max=0.80),),
    )

    coerced_result = compute_conversion_report(_one_meeting_report(coerced))

    assert coerced_result.missed_skip_ballots == 1
    assert coerced_result.missed_skip_impostor_voters == 1
    assert coerced_result.missed_skip_teammate_coerced == 1
    assert coerced_result.threshold_inversions == 0


def test_skip_ballot_without_vote_prompt_is_unclassified() -> None:
    """No rendered gate line for the voter -> unclassified, never assumed."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(_ballot(target="SKIP", voter="p-0", reason_id=None),),
        llm_calls=(),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.skip_ballots == 1
    assert result.unclassified_skip_ballots == 1
    assert result.correct_skip_ballots == 0
    assert result.missed_skip_ballots == 0


def test_non_skip_ballots_do_not_enter_the_skip_partition() -> None:
    meeting = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        ballots=(
            _ballot(target=_IMPOSTOR, voter="p-0", reason_id=None),
            _ballot(target="SKIP", voter="p-1", reason_id=None),
        ),
        llm_calls=(
            _vote_call(agent_id="p-0", rendered_max=0.80),
            _vote_call(agent_id="p-1", rendered_max=0.10),
        ),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.skip_ballots == 1
    assert result.correct_skip_ballots == 1


# ---------------------------------------------------------------------------
# Task 10.9.1 — the DEFAULTED class of the SKIP partition (PR #147 F1)
# ---------------------------------------------------------------------------

# What the manager's vote fail-soft records as the WHOLE rationale_text of a
# ballot degraded after its completion failed schema validation: the pinned
# marker quoting a bounded head of the unparseable response (the seed-8
# cap-truncation shape).
_DEFAULTED_RATIONALE = VOTE_PARSE_DEFAULT_MARKER.format(
    head='{"voter": "p-0", "target": "p-3", "confidence": 0.72, "rationa...'
)


def test_defaulted_skip_under_must_vote_lands_in_defaulted_class() -> None:
    """The DoD partition pin: a degraded SKIP under a MUST-vote render.

    The integration risk this guards (the contract's tripwire): a degraded
    SKIP miscounted as a genuine inversion would poison the §4.6
    0-inversion HARD line on the very re-record the fail-soft exists to
    unblock. The decision census must read byte-identically with and
    without the defaulted ballot — threshold_inversions does not move,
    missed_skip does not move — while the DEFAULTED census reads 1.
    """

    # Control: a genuine inversion (crew voter, met threshold, no marker)
    # so the pin proves non-contamination, not just zeros.
    control_ballots = (_ballot(target="SKIP", voter="p-2", reason_id=None),)
    control_calls = (_vote_call(agent_id="p-2", rendered_max=0.80),)
    without_defaulted = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=control_ballots,
        llm_calls=control_calls,
    )
    with_defaulted = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=control_ballots
        + (
            _ballot(
                target="SKIP",
                voter="p-0",
                reason_id=None,
                rationale_text=_DEFAULTED_RATIONALE,
            ),
        ),
        llm_calls=control_calls + (_vote_call(agent_id="p-0", rendered_max=0.80),),
    )

    baseline = compute_conversion_report(_one_meeting_report(without_defaulted))
    result = compute_conversion_report(_one_meeting_report(with_defaulted))

    # The decision census is untouched by the defaulted ballot.
    assert result == baseline
    assert result.threshold_inversions == 1  # the control only
    assert result.missed_skip_ballots == 1
    assert result.skip_ballots == 1

    defaulted = compute_defaulted_ballots(_one_meeting_report(with_defaulted))
    assert defaulted.defaulted_skip_ballots == 1
    assert defaulted.defaulted_under_must_vote == 1
    assert defaulted.defaulted_under_must_skip == 0
    assert defaulted.defaulted_without_render == 0


def test_defaulted_skip_under_must_skip_is_correct_skip_with_telemetry() -> None:
    """A marker-bearing SKIP under a MUST-skip render is simply correct-skip.

    The degrade coincides with the decision the verdict demanded, so it
    stays in the decision census as a correct skip; the DEFAULTED census
    still sees it (the telemetry overlap is deliberate).
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter="p-0",
                reason_id=None,
                rationale_text=_DEFAULTED_RATIONALE,
            ),
        ),
        llm_calls=(_vote_call(agent_id="p-0", rendered_max=0.55),),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.skip_ballots == 1
    assert result.correct_skip_ballots == 1
    assert result.missed_skip_ballots == 0
    assert result.threshold_inversions == 0

    defaulted = compute_defaulted_ballots(_one_meeting_report(meeting))
    assert defaulted.defaulted_skip_ballots == 1
    assert defaulted.defaulted_under_must_skip == 1
    assert defaulted.defaulted_under_must_vote == 0


def test_defaulted_skip_without_render_is_censused_not_unclassified() -> None:
    """No rendered verdict (the REAL-provider shape) — the marker still keys it.

    A real provider's failed vote call raises before the recording client
    logs its prompt, so no gate line is recoverable; the marker is the only
    witness, and the ballot must land in the DEFAULTED census rather than
    drowning in ``unclassified_skip_ballots``.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter="p-0",
                reason_id=None,
                rationale_text=_DEFAULTED_RATIONALE,
            ),
        ),
        llm_calls=(),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.skip_ballots == 0
    assert result.unclassified_skip_ballots == 0
    assert result.missed_skip_ballots == 0
    assert result.threshold_inversions == 0

    defaulted = compute_defaulted_ballots(_one_meeting_report(meeting))
    assert defaulted.defaulted_skip_ballots == 1
    assert defaulted.defaulted_without_render == 1


def _defaulted_vote_failed_call(
    *,
    voter: PlayerId,
    rendered_vote_max: float | None,
    meeting_id: str = "m-0",
    trigger: str = "validation",
) -> FailedCallReplayEntry:
    """A ``deadline_default`` vote failed-call row carrying the §4.6 verdict.

    Mirrors what ``orchestrator.game._record_deadline_defaults`` writes for a
    defaulted ballot (Task 10.12): the voter is named in ``error_message`` and
    the rendered max rides ``rendered_vote_max``.
    """

    return FailedCallReplayEntry(
        game_id="g-0",
        meeting_id=meeting_id,
        tick=40,
        model="(deadline_default)",
        prompt_length=0,
        raw_response="",
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
        error_type="deadline_default",
        error_message=f"vote defaulted ({trigger}); {voter} submitted no ballot",
        rendered_vote_max=rendered_vote_max,
    )


def _report_with_failed_calls(
    meeting: MeetingReport,
    failed_calls: tuple[FailedCallReplayEntry, ...],
) -> TournamentReport:
    return _tournament(
        GameReport(
            game_id="g-0",
            seed=1,
            winner=None,
            reason="fixture",
            final_tick=100,
            roles=_ROLES,
            replay_ref="replay-seed-1.jsonl",
            meetings=(meeting,),
            failed_calls=failed_calls,
            prompt_versions={},
            cost=GameCostSummary(
                total_cost_usd=0.0,
                total_input_tokens=0,
                total_output_tokens=0,
                by_model={},
            ),
        )
    )


def test_defaulted_under_must_vote_recovered_from_persisted_failed_call() -> None:
    """The H-H-2 fix: a defaulted ballot's MUST-vote verdict is no longer hidden.

    The defaulted ballot's own vote call failed before its prompt was logged,
    so the rendered max is absent from ``llm_calls`` — pre-10.12 this forced
    ``defaulted_without_render`` and made ``defaulted_under_must_vote`` 0 BY
    CONSTRUCTION. With the rendered §4.6 max persisted onto the
    ``deadline_default`` failed-call row, the same ballot is classified
    MUST-vote — the missed-eject blind spot is now visible.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter="p-0",
                reason_id=None,
                rationale_text=_DEFAULTED_RATIONALE,
            ),
        ),
        llm_calls=(),  # the vote call failed: no logged prompt
    )
    report = _report_with_failed_calls(
        meeting,
        (_defaulted_vote_failed_call(voter="p-0", rendered_vote_max=0.65),),
    )

    defaulted = compute_defaulted_ballots(report)

    assert defaulted.defaulted_skip_ballots == 1
    assert defaulted.defaulted_under_must_vote == 1
    assert defaulted.defaulted_under_must_skip == 0
    assert defaulted.defaulted_without_render == 0


def test_defaulted_persisted_must_skip_classifies_under_must_skip() -> None:
    """A persisted sub-threshold max routes the defaulted ballot to MUST-skip."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter="p-0",
                reason_id=None,
                rationale_text=_DEFAULTED_RATIONALE,
            ),
        ),
        llm_calls=(),
    )
    report = _report_with_failed_calls(
        meeting,
        (_defaulted_vote_failed_call(voter="p-0", rendered_vote_max=0.55),),
    )

    defaulted = compute_defaulted_ballots(report)

    assert defaulted.defaulted_under_must_skip == 1
    assert defaulted.defaulted_under_must_vote == 0
    assert defaulted.defaulted_without_render == 0


def test_defaulted_without_persisted_field_stays_without_render() -> None:
    """A committed single-era replay carries no field — the ballot stays unrendered.

    Backward-compat pin: a ``deadline_default`` row whose ``rendered_vote_max``
    is ``None`` (every pre-10.12 committed replay) must not invent a verdict;
    the ballot still lands in ``defaulted_without_render``.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter="p-0",
                reason_id=None,
                rationale_text=_DEFAULTED_RATIONALE,
            ),
        ),
        llm_calls=(),
    )
    report = _report_with_failed_calls(
        meeting,
        (_defaulted_vote_failed_call(voter="p-0", rendered_vote_max=None),),
    )

    defaulted = compute_defaulted_ballots(report)

    assert defaulted.defaulted_without_render == 1
    assert defaulted.defaulted_under_must_vote == 0


def test_persisted_must_skip_counts_correct_skip_in_decision_census() -> None:
    """The two surfaces agree: a persisted MUST-skip default is a correct skip.

    ``DefaultedBallotReport.defaulted_under_must_skip`` is documented to ALSO
    stay a ``correct_skip_ballots`` entry in the decision census (the one
    deliberate overlap). Pre-fix, the decision census only read ``llm_calls``,
    so a defaulted ballot whose prompt never logged was diverted instead of
    counted — the two surfaces disagreed. The persisted failed-call fallback
    restores the overlap for the failed-call path.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter="p-0",
                reason_id=None,
                rationale_text=_DEFAULTED_RATIONALE,
            ),
        ),
        llm_calls=(),
    )
    report = _report_with_failed_calls(
        meeting,
        (_defaulted_vote_failed_call(voter="p-0", rendered_vote_max=0.55),),
    )

    result = compute_conversion_report(report)

    assert result.skip_ballots == 1
    assert result.correct_skip_ballots == 1
    assert result.missed_skip_ballots == 0
    assert result.threshold_inversions == 0
    # The telemetry census agrees on the verdict (no surface disagreement).
    assert compute_defaulted_ballots(report).defaulted_under_must_skip == 1


def test_persisted_must_vote_default_stays_diverted_from_decision_census() -> None:
    """A persisted MUST-vote default is still diverted — never a missed/inversion.

    The §4.6 0-inversion HARD line must hold: a degraded SKIP under a MUST-vote
    verdict is the fail-soft net, not the voter's decision, so the decision
    census diverts it (the divert condition now fires off the recovered max)
    and only the telemetry census records it.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter="p-0",
                reason_id=None,
                rationale_text=_DEFAULTED_RATIONALE,
            ),
        ),
        llm_calls=(),
    )
    report = _report_with_failed_calls(
        meeting,
        (_defaulted_vote_failed_call(voter="p-0", rendered_vote_max=0.65),),
    )

    result = compute_conversion_report(report)

    assert result.skip_ballots == 0
    assert result.missed_skip_ballots == 0
    assert result.threshold_inversions == 0
    assert result.unclassified_skip_ballots == 0
    assert compute_defaulted_ballots(report).defaulted_under_must_vote == 1


def test_unmarked_deadline_default_skip_is_not_poisoned_by_persisted_max() -> None:
    """An UNMARKED deadline default must never become a false threshold inversion.

    An interactive ``vote_seconds`` miss records a ``phase="vote"`` default
    carrying ``rendered_vote_max`` but returns the plain (UNMARKED)
    ``DEFAULT_VOTE_RATIONALE`` ballot, not the parse-default marker. The
    persisted fallback is marker-gated, so this unmarked SKIP keeps
    ``rendered_max is None`` and stays ``unclassified`` — it must NOT borrow the
    persisted ≥0.60 max and get scored as a missed skip / threshold inversion
    (which the marker-gated divert could not catch).
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter="p-0",  # CREWMATE: would be a threshold inversion if scored
                reason_id=None,
                rationale_text=DEFAULT_VOTE_RATIONALE,
            ),
        ),
        llm_calls=(),
    )
    report = _report_with_failed_calls(
        meeting,
        (
            _defaulted_vote_failed_call(
                voter="p-0", rendered_vote_max=0.80, trigger="deadline"
            ),
        ),
    )

    result = compute_conversion_report(report)

    assert result.threshold_inversions == 0
    assert result.missed_skip_ballots == 0
    assert result.unclassified_skip_ballots == 1
    # And it is NOT in the marker-keyed defaulted census either.
    assert compute_defaulted_ballots(report).defaulted_skip_ballots == 0


def test_defaulted_census_ignores_non_skip_and_unmarked_ballots() -> None:
    """Only marker-bearing SKIPs are DEFAULTED; everything else is invisible."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(target=_IMPOSTOR, voter="p-0", reason_id=None),
            _ballot(target="SKIP", voter="p-1", reason_id=None),
        ),
        llm_calls=(_vote_call(agent_id="p-1", rendered_max=0.10),),
    )

    defaulted = compute_defaulted_ballots(_one_meeting_report(meeting))

    assert defaulted == DefaultedBallotReport(
        defaulted_skip_ballots=0,
        defaulted_under_must_vote=0,
        defaulted_under_must_skip=0,
        defaulted_without_render=0,
    )


def test_defaulted_model_rejects_bad_partition() -> None:
    with pytest.raises(ValidationError, match="must equal\\s+defaulted_skip_ballots"):
        DefaultedBallotReport(
            defaulted_skip_ballots=2,
            defaulted_under_must_vote=1,
            defaulted_under_must_skip=0,
            defaulted_without_render=0,
        )


# ---------------------------------------------------------------------------
# Task 10.9.2 — the ballot-target redirect census (PR #147 F2)
# ---------------------------------------------------------------------------

# What the manager's ballot-target graph guard prepends to the rationale of
# a ballot whose eject target carried no over-gate rendered row under a
# MUST-vote verdict: the pinned marker preserving the original target. The
# recorded target is already the REDIRECT (or the coerced SKIP).
_REDIRECTED_RATIONALE = BALLOT_TARGET_REDIRECT_MARKER.format(target="p-1") + "stub"


def test_redirected_eject_ballot_is_censused_and_decision_census_frozen() -> None:
    """The redirect census reads the marker; the SKIP partition never moves.

    A redirected ballot still EJECTS (at the guard's over-gate target), so
    it can never enter the SKIP partition: threshold_inversions and
    missed_skip move by exactly 0 when the redirected ballot is added —
    the frozen-semantics regression pin on the eval side.
    """

    # Control: a genuine inversion (crew voter, met threshold, no marker)
    # so the pin proves non-contamination, not just zeros.
    control_ballots = (_ballot(target="SKIP", voter="p-2", reason_id=None),)
    control_calls = (_vote_call(agent_id="p-2", rendered_max=0.80),)
    without_redirect = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        ballots=control_ballots,
        llm_calls=control_calls,
    )
    with_redirect = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        ballots=control_ballots
        + (
            _ballot(
                target=_IMPOSTOR,
                voter="p-0",
                reason_id=None,
                rationale_text=_REDIRECTED_RATIONALE,
            ),
        ),
        llm_calls=control_calls + (_vote_call(agent_id="p-0", rendered_max=0.80),),
    )

    baseline = compute_conversion_report(_one_meeting_report(without_redirect))
    result = compute_conversion_report(_one_meeting_report(with_redirect))

    # The decision census is untouched by the redirected eject ballot.
    assert result == baseline
    assert result.threshold_inversions == 1  # the control only
    assert result.missed_skip_ballots == 1
    assert result.skip_ballots == 1

    redirects = compute_ballot_target_redirects(_one_meeting_report(with_redirect))
    assert redirects.redirected_ballots == 1
    assert redirects.redirected_eject_ballots == 1
    assert redirects.redirect_coerced_skip_ballots == 0


def test_redirect_coerced_skip_is_impostor_missed_skip_never_inversion() -> None:
    """The teammate-only-over-gate coercion: by-design play, not an inversion.

    The SKIP-coerce branch fires only for an impostor voter (the verdict
    can only exceed the eligible pool through a teammate row), so in the
    decision census the coerced SKIP lands in the impostor bucket exactly
    like a §7.12 teammate coercion — threshold_inversions stays 0 and
    betrayal stays 0 by construction.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_IMPOSTOR,
                reason_id=None,
                rationale_text=_REDIRECTED_RATIONALE,
            ),
        ),
        llm_calls=(_vote_call(agent_id=_IMPOSTOR, rendered_max=0.80),),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.skip_ballots == 1
    assert result.missed_skip_ballots == 1
    assert result.missed_skip_impostor_voters == 1
    assert result.threshold_inversions == 0

    redirects = compute_ballot_target_redirects(_one_meeting_report(meeting))
    assert redirects.redirected_ballots == 1
    assert redirects.redirect_coerced_skip_ballots == 1
    assert redirects.redirected_eject_ballots == 0


def test_redirect_census_ignores_unmarked_ballots() -> None:
    """Eject ballots and clean SKIPs without the marker are invisible."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(target=_IMPOSTOR, voter="p-0", reason_id=None),
            _ballot(target="SKIP", voter="p-1", reason_id=None),
            _ballot(
                target="SKIP",
                voter="p-2",
                reason_id=None,
                rationale_text=VOTE_PARSE_DEFAULT_MARKER.format(head="{}"),
            ),
        ),
        llm_calls=(),
    )

    redirects = compute_ballot_target_redirects(_one_meeting_report(meeting))

    assert redirects == BallotTargetRedirectReport(
        redirected_ballots=0,
        redirected_eject_ballots=0,
        redirect_coerced_skip_ballots=0,
    )


def test_redirect_model_rejects_bad_partition() -> None:
    with pytest.raises(ValidationError, match="must equal redirected_ballots"):
        BallotTargetRedirectReport(
            redirected_ballots=2,
            redirected_eject_ballots=1,
            redirect_coerced_skip_ballots=0,
        )


# ---------------------------------------------------------------------------
# Task 9.6 — ConversionReport model contract
# ---------------------------------------------------------------------------


def test_conversion_model_rejects_bad_skip_partition() -> None:
    with pytest.raises(ValidationError, match="must equal\\s+skip_ballots"):
        ConversionReport(
            total_ejections=0,
            impostor_ejections=0,
            ejection_accuracy=None,
            impostor_accused_meetings=0,
            impostor_accused_conversions=0,
            impostor_accused_conversion_rate=None,
            skip_ballots=2,
            correct_skip_ballots=1,
            missed_skip_ballots=0,
            unclassified_skip_ballots=0,
            missed_skip_impostor_voters=0,
            missed_skip_teammate_coerced=0,
            missed_skip_invalid_target=0,
            threshold_inversions=0,
        )


def test_conversion_model_rejects_bad_missed_partition() -> None:
    with pytest.raises(ValidationError, match="must equal\\s+missed_skip_ballots"):
        ConversionReport(
            total_ejections=0,
            impostor_ejections=0,
            ejection_accuracy=None,
            impostor_accused_meetings=0,
            impostor_accused_conversions=0,
            impostor_accused_conversion_rate=None,
            skip_ballots=1,
            correct_skip_ballots=0,
            missed_skip_ballots=1,
            unclassified_skip_ballots=0,
            missed_skip_impostor_voters=1,
            missed_skip_teammate_coerced=0,
            missed_skip_invalid_target=1,
            threshold_inversions=0,
        )


def test_conversion_model_rejects_coerced_exceeding_impostor_bucket() -> None:
    """The coerced count is a subset annotation of the impostor bucket."""

    with pytest.raises(
        ValidationError, match="cannot exceed\\s+missed_skip_impostor_voters"
    ):
        ConversionReport(
            total_ejections=0,
            impostor_ejections=0,
            ejection_accuracy=None,
            impostor_accused_meetings=0,
            impostor_accused_conversions=0,
            impostor_accused_conversion_rate=None,
            skip_ballots=1,
            correct_skip_ballots=0,
            missed_skip_ballots=1,
            unclassified_skip_ballots=0,
            missed_skip_impostor_voters=1,
            missed_skip_teammate_coerced=2,
            missed_skip_invalid_target=0,
            threshold_inversions=0,
        )


def test_conversion_model_rejects_rate_set_with_zero_denominator() -> None:
    with pytest.raises(ValidationError, match="must be None"):
        ConversionReport(
            total_ejections=0,
            impostor_ejections=0,
            ejection_accuracy=None,
            impostor_accused_meetings=0,
            impostor_accused_conversions=0,
            impostor_accused_conversion_rate=0.0,
            skip_ballots=0,
            correct_skip_ballots=0,
            missed_skip_ballots=0,
            unclassified_skip_ballots=0,
            missed_skip_impostor_voters=0,
            missed_skip_teammate_coerced=0,
            missed_skip_invalid_target=0,
            threshold_inversions=0,
        )


def test_conversion_model_rejects_conversions_exceeding_accused() -> None:
    with pytest.raises(
        ValidationError, match="cannot exceed\\s+impostor_accused_meetings"
    ):
        ConversionReport(
            total_ejections=0,
            impostor_ejections=0,
            ejection_accuracy=None,
            impostor_accused_meetings=1,
            impostor_accused_conversions=2,
            impostor_accused_conversion_rate=1.0,
            skip_ballots=0,
            correct_skip_ballots=0,
            missed_skip_ballots=0,
            unclassified_skip_ballots=0,
            missed_skip_impostor_voters=0,
            missed_skip_teammate_coerced=0,
            missed_skip_invalid_target=0,
            threshold_inversions=0,
        )


# ---------------------------------------------------------------------------
# Task 9.6 — committed 9p/2i report regression pins (the Wave-1 9.11 baseline)
# ---------------------------------------------------------------------------

_COMMITTED_9P2I_REPORT = (
    Path(__file__).resolve().parents[2]
    / "replays"
    / "samples"
    / "9p2i"
    / "tournament-eval-report.json"
)


def test_committed_9p2i_report_pins_the_audited_conversion_values() -> None:
    """The shipped 9p/2i report carries the recorded gp-2 values exactly.

    These pin the Task 10.17 Wave-2 combined re-record and are NOT immutable —
    the next re-record regenerates them, the standard re-record pattern.
    ejection_accuracy 24/27 = 0.8889, impostor-accused conversion 24/78 =
    0.3077, missed_skip 25 = 19 impostor-voter (in-character declines) + 6
    invalid-target + 1 teammate-coerced + 0 genuine. Raw comparisons to the
    0.629 (artifact-era) and 0.476 (mixed-era) accuracy numbers are
    provenance-noted history, not gates: those eras' conversions rode the
    repaired artifact classes (the audit's railroads), so the gate frame is
    genuine_class_conversion (tests/eval/test_gate_metrics.py pins).

    The sentinel reads the recorded truth: 20 of the 24 impostor ejections are
    transcript-evidence-backed (vote_correctness_rate 20/24 = 0.833); the four
    unbacked ejections converted on accumulated/carried suspicion that
    ``_has_real_evidence`` deliberately does not consult.
    """

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )
    conversion = report.conversion

    assert conversion.total_ejections == 27
    assert conversion.impostor_ejections == 24
    assert conversion.ejection_accuracy == pytest.approx(24 / 27)
    assert conversion.impostor_accused_meetings == 78
    assert conversion.impostor_accused_conversions == 24
    assert conversion.impostor_accused_conversion_rate == pytest.approx(24 / 78)
    assert conversion.skip_ballots == 394
    assert conversion.correct_skip_ballots == 369
    assert conversion.missed_skip_ballots == 25
    assert conversion.unclassified_skip_ballots == 0
    assert conversion.missed_skip_impostor_voters == 19
    assert conversion.missed_skip_teammate_coerced == 1
    assert conversion.missed_skip_invalid_target == 6
    assert conversion.threshold_inversions == 0

    # The sentinel reads the recorded truth: 20 of the 24 impostor ejections are
    # transcript-evidence-backed (see docstring).
    assert report.vote_correctness.vote_correctness_rate == pytest.approx(20 / 24)
    assert report.vote_correctness.evidence_backed_impostor_ejections == 20
    assert report.vote_correctness.impostor_ejections == 24
    # The wrapper mirrors, never re-derives: the two surfaces agree exactly.
    assert conversion.ejection_accuracy == report.vote_correctness.ejection_accuracy

    # JSON-level guard: the committed file itself serves both leads (a reader
    # pulling the raw report sees the published metric surface, gp-2's ask).
    raw = json.loads(_COMMITTED_9P2I_REPORT.read_text(encoding="utf-8"))
    assert raw["conversion"]["ejection_accuracy"] == pytest.approx(0.8889, abs=1e-4)
    assert raw["conversion"]["missed_skip_ballots"] == 25
