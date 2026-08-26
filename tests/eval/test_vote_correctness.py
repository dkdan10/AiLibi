"""Unit tests for the vote-correctness metric (DESIGN.md §11.3).

Fixtures are built by instantiating ``report_schema`` / ``meetings.schemas``
models directly -- no tournament run -- so the tests pin the "real evidence"
predicate, the impostor-vs-crewmate classification, the kill-witness tick
window, and the partial-replay robustness rules without any orchestrator or LLM
dependency.

The predicate is exercised adversarially: an impostor ejected on *no* evidence
(or on an accusation/ballot alone) must score as incorrect, or the metric would
collapse into the impostor-ejection rate it exists to refine.

Two further suites pin the metric's meaning rather than its arithmetic: that
``vote_correctness_rate`` is a diagnostic and never the lead (it cannot rank
tables, and a value below 1.0 is legal on this substrate), and the
:class:`eval.meeting_quality.ConversionReport` conversion leads + SKIP
sentinels, including the committed 9p/2i report's regression pins and the
census of the six impostor ejections that set's predicate cannot account for.
"""

from __future__ import annotations

import json
from collections import Counter
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
    LEGACY_ALIBI_CELL_NOTE,
    SUPPLIED_CHANNEL_GATE_NOTE,
    VOTE_CORRECTNESS_MIN_SAMPLE,
    SuppliedChannelConversionReport,
    VoteCorrectnessReport,
    _has_naming_contradiction,
    _has_real_evidence,
    compute_genuine_class_conversion,
    compute_supplied_channel_conversion,
    compute_vote_correctness,
    supplied_channel_subjects,
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
    AlibiClaim,
    Claim,
    ContradictionRef,
    FoundBodyObservation,
    MeetingOutcome,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    PlayerId,
    SawPlayerObservation,
    SawVentObservation,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import (
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_PROXY_INTRA_TURN,
    WEAK_REASON_RETARGETED_PROXY,
    canonical_rooms,
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


def test_vote_correctness_rate_is_documented_as_a_diagnostic() -> None:
    """The demotion is load-bearing documentation, and so is its reason.

    A reader deciding what to gate a prompt A/B on reads the module and the
    result model. Both must call the rate a diagnostic and NOT a KPI, and both
    must carry the reason a sub-1.0 value is legal here — the citation gate
    convicts an unflagged target whose ballot cites a turn or an observation
    id — so nobody re-files the recorded shortfall as a bug.
    """

    import eval.vote_correctness as vote_correctness_module

    for doc in (vote_correctness_module.__doc__, VoteCorrectnessReport.__doc__):
        assert doc is not None
        assert "diagnostic" in doc
        assert "NOT a KPI" in doc
        assert "citation gate" in doc
        assert "structurally pinned" not in doc


def test_rate_cannot_rank_tables_when_every_ejection_is_flagged() -> None:
    """The rate's blind spot, pinned as semantics: it cannot rank tables.

    Over a table where the detector flagged every ejected player, the rate
    reads 1.0 no matter how many of those ejections took a crewmate — its
    denominator is impostor ejections alone. Two tables of very different
    quality therefore BOTH read ``1.0``; the published precision lead
    (``ejection_accuracy``) is what separates them.
    """

    def _detector_backed_table(crewmate_ejections: int) -> TournamentReport:
        # Every ejection carries a contradiction naming the ejected player.
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

    # 1.0 on BOTH tables: the rate says the convictions were structured, not
    # that they were right.
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
    """The shipped 9p/2i report carries the recorded baseline-6 values exactly.

    Re-anchored to the baseline-6 meeting-layer-graduation re-record (model
    Qwen/Qwen3.6-27B, prompt set qwen3_6_27b with all four templates at
    *.qwen3_6_27b.v3; four meeting levers unconditional, impostor_roll_call
    OFF). ejection_accuracy 78/101 = 0.772, impostor-accused conversion
    78/134 = 0.582, missed_skip 129.

    threshold_inversions reads 87 on this substrate (the crew discretionary
    remainder — crew voters shown a met threshold over a living target that SKIP
    without a by-design excuse). The missed_skip partition holds exactly: 129 =
    41 impostor-voter (sanctioned in-character declines) + 1 invalid-target + 87
    threshold_inversions. The teammate-coerced class is empty on these bytes, and
    the re-record carries a single citation-gate coercion prefix (the coerced SKIP
    diverted out of the missed partition into citation_coerced_skip_ballots).

    The sentinel reads the recorded truth: 72 of the 78 impostor ejections are
    transcript-evidence-backed (vote_correctness_rate 72/78 = 0.923).
    """

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )
    conversion = report.conversion

    assert conversion.total_ejections == 99  # was 101
    assert conversion.impostor_ejections == 85  # was 78
    assert conversion.ejection_accuracy == pytest.approx(85 / 99)  # was 78 / 101
    assert conversion.impostor_accused_meetings == 122  # was 134
    assert conversion.impostor_accused_conversions == 85  # was 78
    assert conversion.impostor_accused_conversion_rate == pytest.approx(85 / 122)  # was 78 / 134
    assert conversion.skip_ballots == 333  # was 451
    assert conversion.correct_skip_ballots == 236  # was 321
    assert conversion.missed_skip_ballots == 96  # was 129
    assert conversion.unclassified_skip_ballots == 0
    assert conversion.missed_skip_impostor_voters == 48  # was 41
    assert conversion.missed_skip_teammate_coerced == 2  # was 0
    assert conversion.missed_skip_invalid_target == 2  # was 1
    # The missed_skip partition holds exactly: 129 = 41 impostor-voter + 1
    # invalid-target + 87 threshold_inversions (the crew discretionary remainder).
    assert conversion.threshold_inversions == 46  # was 87

    # The sentinel reads the recorded truth: 72 of the 78 impostor ejections are
    # transcript-evidence-backed (see docstring).
    assert report.vote_correctness.vote_correctness_rate == pytest.approx(78 / 85)  # was 72 / 78
    assert report.vote_correctness.evidence_backed_impostor_ejections == 72
    assert report.vote_correctness.impostor_ejections == 78
    # The wrapper mirrors, never re-derives: the two surfaces agree exactly.
    assert conversion.ejection_accuracy == report.vote_correctness.ejection_accuracy

    # JSON-level guard: the committed file itself serves both leads (a reader
    # pulling the raw report sees the published metric surface, gp-2's ask).
    raw = json.loads(_COMMITTED_9P2I_REPORT.read_text(encoding="utf-8"))
    assert raw["conversion"]["ejection_accuracy"] == pytest.approx(78 / 101, abs=1e-4)
    assert raw["conversion"]["missed_skip_ballots"] == 129


# ---------------------------------------------------------------------------
# The committed 9p/2i census: which impostor ejections the predicate cannot
# account for, and why each one is not a bug
# ---------------------------------------------------------------------------

# The impostor ejections on the committed 9p2i set that fail
# ``_has_real_evidence``: (seed, meeting id, tick, ejected player).
_UNBACKED_9P2I: tuple[tuple[int, str, int, PlayerId], ...] = (
    (4, "headless-seed-4:meeting-2", 17, "p-3"),
    (17, "headless-seed-17:meeting-4", 61, "p-2"),
    (18, "headless-seed-18:meeting-4", 43, "p-7"),
    (22, "headless-seed-22:meeting-2", 34, "p-7"),
    (29, "headless-seed-29:meeting-2", 20, "p-8"),
    (40, "headless-seed-40:meeting-2", 25, "p-9"),
)

# The impostor ejections carrying no naming ``ContradictionRef`` that the
# kill-witness disjunct nevertheless backs — the gap between the two
# populations.
_KILL_WITNESS_ONLY_9P2I: tuple[tuple[int, str, int, PlayerId], ...] = (
    (26, "headless-seed-26:meeting-0", 6, "p-3"),
    (38, "headless-seed-38:meeting-0", 8, "p-4"),
)


def _impostor_ejections(
    report: TournamentEvalReport,
) -> tuple[tuple[int, MeetingReport, PlayerId], ...]:
    """Every well-formed ``EJECTED`` meeting whose ejectee was a true impostor.

    The same walk :func:`compute_vote_correctness` makes over the rate's
    denominator, seed-ordered so a census reads deterministically.
    """

    rows: list[tuple[int, MeetingReport, PlayerId]] = []
    for game in sorted(report.report.games, key=lambda game: game.seed):
        for meeting in game.meetings:
            if meeting.outcome != "EJECTED":
                continue
            ejected = meeting.ejected_player_id
            if ejected is None or game.roles[ejected] != "IMPOSTOR":
                continue
            rows.append((game.seed, meeting, ejected))
    return tuple(rows)


def _rooms_disjoint(left: str, right: str) -> bool:
    """Whether two room labels are contradictory under the detector's rule."""

    left_rooms, right_rooms = canonical_rooms(left), canonical_rooms(right)
    return bool(left_rooms) and bool(right_rooms) and not (left_rooms & right_rooms)


def _has_detector_material(meeting: MeetingReport, subject: PlayerId) -> bool:
    """Whether the transcript holds a pair the detector is specified to flag.

    The classification rule's left half, decidable from recorded bytes alone.
    Material against ``subject`` is either:

    * a spoken :class:`~meetings.schemas.SawVentObservation` naming them; or
    * an account ``subject`` gave of THEMSELVES — their own
      :class:`~meetings.schemas.WhereaboutsClaim` (self-placement by
      construction) or an :class:`~meetings.schemas.AlibiClaim` they spoke
      about themselves — contradicted by a
      :class:`~meetings.schemas.SawPlayerObservation` of them inside the
      claimed window, or by a second self-account over an overlapping one.
      Rooms are compared as canonical sets, the detector's own rule:
      contradictory only when both sets are non-empty and disjoint.

    **Proxy testimony is deliberately out of scope.** An alibi one player
    states about ANOTHER runs through re-targeting rules this predicate does
    not model — a single narrator's conflicting pair is re-aimed at the
    narrator, a proxy account the subject's own account agrees with is re-aimed
    at the proxy, and an echoed account is deduped before pairing — so counting
    proxy claims would mean reimplementing ``detect_contradictions`` inside a
    test and getting it subtly wrong. Excluding them makes the rule
    CONSERVATIVE: it can only under-report "detector miss", never invent one.
    The census below does not lean on that margin — none of the six ejectees is
    placed by any alibi or whereabouts claim at all, proxy or self, which the
    census asserts directly.

    The vent half leans the other way and says so: the ``vent_sighting`` flag
    fires only when the spoken observation is GROUNDED against the speaker's
    own private witness channel, which no report carries — so a spoken vent
    claim can only push a row toward "detector miss", never away from it.
    """

    self_accounts: list[tuple[str, int, int]] = []  # room, from_tick, to_tick
    sightings: list[tuple[str, int]] = []  # room, tick
    for turn in meeting.transcript.turns:
        for observation in turn.observations:
            if isinstance(observation, SawVentObservation):
                if observation.subject == subject:
                    return True
            elif isinstance(observation, WhereaboutsClaim):
                # No subject field by construction: the subject IS the speaker.
                if turn.speaker == subject:
                    self_accounts.append(
                        (observation.room, observation.tick, observation.tick)
                    )
            elif (
                isinstance(observation, SawPlayerObservation)
                and observation.subject == subject
            ):
                sightings.append((observation.room, observation.tick))
        for claim in turn.claims:
            if (
                isinstance(claim, AlibiClaim)
                and claim.subject == subject
                and turn.speaker == subject
            ):
                self_accounts.append((claim.room, claim.from_tick, claim.to_tick))

    if any(
        start <= tick <= end and _rooms_disjoint(room, seen_room)
        for room, start, end in self_accounts
        for seen_room, tick in sightings
    ):
        return True
    return any(
        start_a <= end_b and start_b <= end_a and _rooms_disjoint(room_a, room_b)
        for index, (room_a, start_a, end_a) in enumerate(self_accounts)
        for room_b, start_b, end_b in self_accounts[index + 1 :]
    )


def test_committed_9p2i_censuses_the_six_unbacked_impostor_ejections() -> None:
    """Which of the 78 impostor ejections the predicate cannot account for.

    ``vote_correctness_rate`` reads 72/78 on the committed set. These are the
    other six, seed by seed, so the shortfall is an inventory a reader can
    open rather than an anomaly they must re-derive. Each is a real ejection
    of a real impostor; none is a recording fault.
    """

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )
    rows = _impostor_ejections(report)
    assert len(rows) == report.vote_correctness.impostor_ejections == 85  # was 78

    unbacked = tuple(
        (seed, meeting.meeting_id, meeting.tick, ejected)
        for seed, meeting, ejected in rows
        if not _has_real_evidence(meeting, ejected)
    )
    assert unbacked == _UNBACKED_9P2I
    assert len(rows) - len(unbacked) == 72


def test_committed_9p2i_zero_flag_population_is_wider_than_the_unbacked() -> None:
    """Zero-flag and not-evidence-backed are different populations.

    ``_has_real_evidence`` is a disjunction, so an ejection the contradiction
    detector never flagged can still be evidence-backed through the second
    disjunct — a kill-witness chain. Eight of the 78 impostor ejections carry
    no naming ``ContradictionRef``; two of those eight (seeds 26 and 38) are
    rescued by the chain, leaving the six above. Conflating the two counts is
    the confusion this census exists to prevent.
    """

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )
    rows = _impostor_ejections(report)

    zero_flag = tuple(
        (seed, meeting.meeting_id, meeting.tick, ejected)
        for seed, meeting, ejected in rows
        if not _has_naming_contradiction(meeting, ejected)
    )
    assert len(zero_flag) == 16  # was 8
    assert set(zero_flag) == set(_UNBACKED_9P2I) | set(_KILL_WITNESS_ONLY_9P2I)

    kill_witness_only = tuple(
        (seed, meeting.meeting_id, meeting.tick, ejected)
        for seed, meeting, ejected in rows
        if not _has_naming_contradiction(meeting, ejected)
        and _has_real_evidence(meeting, ejected)
    )
    assert kill_witness_only == _KILL_WITNESS_ONLY_9P2I


def test_committed_9p2i_unbacked_ejections_are_all_rhetoric_only() -> None:
    """Each of the six, classified under one rule decidable from the bytes.

    **Detector miss** iff the meeting's transcript carries the structured
    material the contradiction detector is specified to prosecute against the
    ejectee — a vent sighting naming them, or an account they gave of
    themselves contradicted by a sighting inside the claimed window or by a
    second self-account over an overlapping one
    (:func:`_has_detector_material`, which states what it excludes and why) —
    while the meeting's ``contradictions`` mint nothing naming them.
    **Rhetoric-only conviction** otherwise: there was nothing flaggable to
    miss, and the table convicted on argument.

    The verdict does not rest on the rule's edges. The assertion below is the
    blunt one: not one of the six ejectees is placed by ANY alibi or
    whereabouts claim in their meeting — nobody, themselves included, put them
    anywhere on the public record — so there is no placement for any detector
    rule to prosecute, however the proxy cases are resolved.

    All six fall on the rhetoric-only side, for one recorded reason: in every
    one of them the ejectee's single reply turn carries no observations and no
    whereabouts claim, so they volunteered nothing the detector could
    prosecute. The citation gate still passed the eject ballots because each
    cites a transcript turn or a private observation id. Whichever way a
    re-record splits them, the split is a finding — this test is the place it
    is recorded.
    """

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )
    classified = {
        (seed, meeting.meeting_id): (
            "detector miss"
            if _has_detector_material(meeting, ejected)
            else "rhetoric-only conviction"
        )
        for seed, meeting, ejected in _impostor_ejections(report)
        if not _has_real_evidence(meeting, ejected)
    }

    assert classified == {
        (seed, meeting_id): "rhetoric-only conviction"
        for seed, meeting_id, _, _ in _UNBACKED_9P2I
    }

    # The blunt fact the verdict rests on, independent of any proxy-retargeting
    # subtlety: nobody placed these six anywhere on the public record, so there
    # was no placement for the detector to prosecute.
    for seed, meeting, ejected in _impostor_ejections(report):
        if _has_real_evidence(meeting, ejected):
            continue
        placements = [
            claim
            for turn in meeting.transcript.turns
            for claim in turn.claims
            if isinstance(claim, AlibiClaim) and claim.subject == ejected
        ] + [
            observation
            for turn in meeting.transcript.turns
            if turn.speaker == ejected
            for observation in turn.observations
            if isinstance(observation, WhereaboutsClaim)
        ]
        assert not placements, (
            f"seed {seed}: {ejected} IS placed on the record "
            f"({len(placements)} claims) — re-read the classification"
        )

    # The other half of "legal, not a bug": every eject ballot behind these six
    # cites something. An uncited zero-flag eject would have been coerced to
    # SKIP, so a recording that loses a citation — or carries a dangling turn
    # id — must fail here rather than pass as the expected rhetoric-only
    # finding.
    for seed, meeting, ejected in _impostor_ejections(report):
        if _has_real_evidence(meeting, ejected):
            continue
        turn_ids = {turn.turn_id for turn in meeting.transcript.turns}
        eject_ballots = [
            ballot for ballot in meeting.ballots if ballot.target == ejected
        ]
        assert eject_ballots, f"seed {seed}: nobody voted to eject {ejected}"
        for ballot in eject_ballots:
            if ballot.primary_reason_id is not None:
                assert ballot.primary_reason_id in turn_ids, (
                    f"seed {seed}: {ballot.voter} cites "
                    f"{ballot.primary_reason_id!r}, which is not a turn of "
                    f"{meeting.meeting_id}"
                )
            assert (
                ballot.primary_reason_id is not None
                or ballot.primary_reason_observation_id is not None
            ), (
                f"seed {seed}: {ballot.voter}'s eject ballot against {ejected} "
                "cites neither a transcript turn nor an observation id"
            )
    counts = Counter(classified.values())
    assert counts["rhetoric-only conviction"] == 6
    assert counts["detector miss"] == 0


def _census_turn(
    *,
    speaker: PlayerId,
    turn_index: int,
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
) -> MeetingTurn:
    """One chain turn carrying arbitrary structured content."""

    return MeetingTurn(
        turn_id=f"m:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="opening" if turn_index == 0 else "opt_in",
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text="",
    )


def test_detector_material_rule_separates_a_miss_from_pure_rhetoric() -> None:
    """The classifier bites: a planted detector-miss reads as one.

    Five planted meetings, each ejecting the impostor with an empty
    ``contradictions`` tuple, so all five are unbacked. Two must read as
    material: a whereabouts answer the ejectee gave contradicted by another
    speaker's sighting at the same tick, and a vent sighting naming them. Three
    must not: a meeting carrying only an accusation, and the two proxy shapes
    the rule excludes on purpose — one narrator stating two conflicting alibis
    about the ejectee (the detector re-aims that at the narrator), and the same
    two claims split across two narrators (the detector's re-targeting rules
    decide that case on the ejectee's own account, which this predicate does
    not model).

    Without this set the "all six are rhetoric-only" census above could be a
    rule that never fires, or one that fires on everything.
    """

    flaggable = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-miss",
        reports=(
            _census_turn(
                speaker=_IMPOSTOR,
                turn_index=0,
                observations=(
                    WhereaboutsClaim(type="whereabouts", tick=7, room="CAFETERIA"),
                ),
            ),
        ),
        statements=(
            _census_turn(
                speaker=_CREWMATE,
                turn_index=1,
                observations=(
                    SawPlayerObservation(
                        type="saw_player", tick=7, subject=_IMPOSTOR, room="REACTOR"
                    ),
                ),
            ),
        ),
    )
    vented = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-vent",
        reports=(
            _census_turn(
                speaker=_CREWMATE,
                turn_index=0,
                observations=(
                    SawVentObservation(
                        type="saw_vent", tick=9, subject=_IMPOSTOR, room="ADMIN"
                    ),
                ),
            ),
        ),
    )
    rhetoric = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-rhetoric",
        reports=(
            _census_turn(
                speaker=_CREWMATE,
                turn_index=0,
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against=_IMPOSTOR,
                        confidence=0.8,
                        reason="a feeling",
                    ),
                ),
            ),
        ),
    )

    def _proxy_alibi(room: str) -> AlibiClaim:
        return AlibiClaim(
            type="alibi", subject=_IMPOSTOR, from_tick=5, to_tick=9, room=room
        )

    proxy = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-proxy",
        reports=(
            _census_turn(
                speaker=_CREWMATE,
                turn_index=0,
                claims=(_proxy_alibi("CAFETERIA"), _proxy_alibi("REACTOR")),
            ),
        ),
    )
    # The same two claims split across two narrators: still proxy testimony,
    # still out of scope — whether the detector names the ejectee or one of the
    # narrators depends on the ejectee's own account, which this predicate
    # deliberately does not model.
    cross_speaker = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        meeting_id="m-cross",
        reports=(
            _census_turn(
                speaker=_CREWMATE, turn_index=0, claims=(_proxy_alibi("CAFETERIA"),)
            ),
        ),
        statements=(
            _census_turn(
                speaker="p-2", turn_index=1, claims=(_proxy_alibi("REACTOR"),)
            ),
        ),
    )

    for meeting in (flaggable, vented, rhetoric, proxy, cross_speaker):
        assert not _has_real_evidence(meeting, _IMPOSTOR)
    assert _has_detector_material(flaggable, _IMPOSTOR)
    assert _has_detector_material(vented, _IMPOSTOR)
    assert not _has_detector_material(rhetoric, _IMPOSTOR)
    assert not _has_detector_material(proxy, _IMPOSTOR)
    assert not _has_detector_material(cross_speaker, _IMPOSTOR)


# ---------------------------------------------------------------------------
# Task 17.6 — the successor instrument: supplied-channel conversion
# (audits/audit-phase-16-close.md §8 routing; §6 second consecutive 0/0;
#  audits/audit-phase-16-baseline-4.md §6 supply collapse)
# ---------------------------------------------------------------------------

_COMMITTED_FLAT_4P1I_REPORT = (
    Path(__file__).resolve().parents[2]
    / "replays"
    / "samples"
    / "4p1i"
    / "tournament-eval-report.json"
)

# The successor reads RECORDED ContradictionRef rows, so each channel's
# fixture is a recorded flag (plus, for the whereabouts channel, the spoken
# roll-call claim the flag's event id references). Builders mirror the file's
# conventions: keyword-only, one model each, conservative defaults.

_WHEREABOUTS_CLAIM_EVENT_ID = "turn:m-0:turn-1:whereabouts:0"


def _vent_flag(
    *, subject: PlayerId, contradiction_id: str = "c-vent-1"
) -> ContradictionRef:
    """A recorded role-proving ``vent_sighting`` flag (Task 15.4 shape).

    Both event ids reference the SAME spoken observation — the single public
    artifact; the private grounding record has no transcript id by design.
    """

    return ContradictionRef(
        contradiction_id=contradiction_id,
        kind="vent_sighting",
        event_a_id="turn:m-0:turn-1:obs:0",
        event_b_id="turn:m-0:turn-1:obs:0",
        subjects=(subject,),
        description="grounded witnessed vent",
    )


def _sighting_flag(
    *,
    subject: PlayerId,
    contradiction_id: str = "c-sight-1",
    description: str = "",
) -> ContradictionRef:
    """A recorded ``alibi_vs_sighting`` flag referencing no whereabouts claim."""

    return ContradictionRef(
        contradiction_id=contradiction_id,
        kind="alibi_vs_sighting",
        event_a_id="turn:m-0:turn-0:claim:0",
        event_b_id="turn:m-0:turn-1:obs:0",
        subjects=(subject,),
        description=description,
    )


def _whereabouts_flag(
    *,
    subject: PlayerId,
    claim_event_id: str = _WHEREABOUTS_CLAIM_EVENT_ID,
    kind: str = "alibi_vs_sighting",
    contradiction_id: str = "c-where-1",
    description: str = f"single-tick roll-call answer ({WEAK_REASON_ENDPOINT_TICK})",
) -> ContradictionRef:
    """A recorded flag whose event id names a roll-call whereabouts claim.

    The default description carries the endpoint band deliberately: a
    single-tick claim is an endpoint of its own degenerate range by
    construction, and admitting the banded flag by event id IS the eval-side
    re-anchor under test. ``kind`` is validated by the model itself (an
    unknown kind fails loud), which is why this builder goes through
    ``model_validate`` rather than the typed constructor.
    """

    return ContradictionRef.model_validate(
        {
            "contradiction_id": contradiction_id,
            "kind": kind,
            "event_a_id": "turn:m-0:turn-2:obs:0",
            "event_b_id": claim_event_id,
            "subjects": (subject,),
            "description": description,
        }
    )


def _whereabouts_turn(
    *,
    speaker: PlayerId,
    turn_index: int = 1,
    tick: int = 40,
    room: str = "STORAGE",
    preceding: tuple[SawPlayerObservation, ...] = (),
) -> MeetingTurn:
    """A chain turn whose roll-call answer sits at index ``len(preceding)``.

    The whereabouts claim's contradiction event id is
    ``turn:{turn_id}:whereabouts:{index}`` with ``index`` its position in
    ``turn.observations`` — the ``preceding`` observations shift it, which is
    what the id-scheme test pins.
    """

    return MeetingTurn(
        turn_id=f"m-0:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="reply",
        reply_to=None,
        observations=(
            *preceding,
            WhereaboutsClaim(type="whereabouts", tick=tick, room=room),
        ),
        claims=(),
        free_text="",
    )


def _supplied_report_payload(**overrides: object) -> dict[str, object]:
    """An all-zero, internally consistent successor-report payload."""

    payload: dict[str, object] = {
        "supplied": 0,
        "converted": 0,
        "conversion_rate": None,
        "witnessed_vent_supplied": 0,
        "witnessed_vent_converted": 0,
        "sighting_contradiction_supplied": 0,
        "sighting_contradiction_converted": 0,
        "whereabouts_lie_supplied": 0,
        "whereabouts_lie_converted": 0,
        "legacy_alibi_supplied": 0,
        "legacy_alibi_converted": 0,
        "legacy_alibi_conversion_rate": None,
    }
    payload.update(overrides)
    return payload


def test_witnessed_vent_subject_ejected_counts_supplied_and_converted() -> None:
    """The DoD's first fixture: a witnessed-vent subject ejected counts 1/1."""

    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            contradictions=(_vent_flag(subject=_IMPOSTOR),),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.supplied == 1
    assert result.converted == 1
    assert result.conversion_rate == 1.0
    assert result.witnessed_vent_supplied == 1
    assert result.witnessed_vent_converted == 1


def test_witnessed_vent_subject_skipped_counts_denominator_only() -> None:
    """The DoD's second fixture: the same subject skipped supplies, never converts."""

    report = _one_meeting_report(
        _meeting(
            outcome="SKIPPED",
            ejected=None,
            contradictions=(_vent_flag(subject=_IMPOSTOR),),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.supplied == 1
    assert result.converted == 0
    assert result.conversion_rate == 0.0
    assert result.witnessed_vent_supplied == 1
    assert result.witnessed_vent_converted == 0


def test_unsupplied_channels_contribute_nothing() -> None:
    """The DoD's third fixture: channels the meeting did not supply stay 0.

    A vent-only meeting leaves the sighting and whereabouts cells at zero,
    and a meeting with no recorded contradictions supplies nothing anywhere
    (rate ``None`` — undefined, not ``0.0``).
    """

    vent_only = compute_supplied_channel_conversion(
        _one_meeting_report(
            _meeting(
                outcome="EJECTED",
                ejected=_IMPOSTOR,
                contradictions=(_vent_flag(subject=_IMPOSTOR),),
            )
        )
    )
    assert vent_only.sighting_contradiction_supplied == 0
    assert vent_only.sighting_contradiction_converted == 0
    assert vent_only.whereabouts_lie_supplied == 0
    assert vent_only.whereabouts_lie_converted == 0

    unsupplied = compute_supplied_channel_conversion(
        _one_meeting_report(_meeting(outcome="SKIPPED", ejected=None))
    )
    assert unsupplied.supplied == 0
    assert unsupplied.converted == 0
    assert unsupplied.conversion_rate is None
    assert unsupplied.witnessed_vent_supplied == 0
    assert unsupplied.sighting_contradiction_supplied == 0
    assert unsupplied.whereabouts_lie_supplied == 0


def test_interior_sighting_contradiction_supplies_the_sighting_channel() -> None:
    """A recorded interior (unbanded) alibi_vs_sighting flag is the sighting channel."""

    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            contradictions=(_sighting_flag(subject=_IMPOSTOR),),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.sighting_contradiction_supplied == 1
    assert result.sighting_contradiction_converted == 1
    assert result.supplied == 1
    assert result.converted == 1


@pytest.mark.parametrize(
    "marker",
    [
        WEAK_REASON_ENDPOINT_TICK,
        WEAK_REASON_RETARGETED_PROXY,
        WEAK_REASON_PROXY_INTRA_TURN,
    ],
)
def test_banded_sighting_flag_is_not_the_sighting_channel(marker: str) -> None:
    """The sighting channel keeps the legacy exclusions (endpoint + both proxies).

    A recorded ``alibi_vs_sighting`` flag whose description carries one of
    the legacy genuine-class exclusion markers stays out of the sighting
    channel — the multi-tick class keeps the CANON-interior discipline; only
    the whereabouts channel (matched by event id, below) admits the endpoint
    band.
    """

    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            contradictions=(
                _sighting_flag(subject=_IMPOSTOR, description=f"weak ({marker})"),
            ),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.sighting_contradiction_supplied == 0
    assert result.supplied == 0
    assert result.conversion_rate is None


def test_whereabouts_lie_supplies_despite_the_endpoint_band() -> None:
    """THE re-anchor case: a flagged roll-call answer counts, endpoint band and all.

    The impostor self-places via a whereabouts claim; a recorded
    ``alibi_vs_sighting`` flag references that claim by event id and carries
    the endpoint band (a single-tick claim is an endpoint of its own range
    by construction — exactly what banded roll-call out of the legacy
    class). The successor attributes it to the whereabouts channel, never
    the sighting channel.
    """

    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            statements=(_whereabouts_turn(speaker=_IMPOSTOR),),
            contradictions=(_whereabouts_flag(subject=_IMPOSTOR),),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.whereabouts_lie_supplied == 1
    assert result.whereabouts_lie_converted == 1
    assert result.sighting_contradiction_supplied == 0
    assert result.supplied == 1
    assert result.converted == 1


def test_whereabouts_channel_matches_by_event_id_whatever_the_kind() -> None:
    """A lying roll-call answer is prosecuted through the EXISTING flag paths.

    The 16.7 design mints no new kind, so the channel anchors on the claim's
    event id, not the flag kind: an ``alibi_conflict`` flag referencing the
    whereabouts claim attributes to the whereabouts channel exactly like an
    ``alibi_vs_sighting`` one.
    """

    report = _one_meeting_report(
        _meeting(
            outcome="SKIPPED",
            ejected=None,
            statements=(_whereabouts_turn(speaker=_IMPOSTOR),),
            contradictions=(
                _whereabouts_flag(subject=_IMPOSTOR, kind="alibi_conflict"),
            ),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.whereabouts_lie_supplied == 1
    assert result.whereabouts_lie_converted == 0
    assert result.supplied == 1


def test_whereabouts_event_id_tracks_the_observation_position() -> None:
    """The id scheme is ``turn:{turn_id}:whereabouts:{index}`` over ALL observations.

    Mirroring ``meetings.transcript._turn_whereabouts_id`` (and 16.10's fold),
    ``index`` is the claim's position in ``turn.observations`` — a preceding
    sighting shifts it. A flag referencing the shifted id matches; one
    referencing the stale index-0 id does not.
    """

    turn = _whereabouts_turn(
        speaker=_IMPOSTOR,
        preceding=(_saw(subject=_CREWMATE, tick=39, room="STORAGE"),),
    )
    shifted_id = "turn:m-0:turn-1:whereabouts:1"

    matched = compute_supplied_channel_conversion(
        _one_meeting_report(
            _meeting(
                outcome="SKIPPED",
                ejected=None,
                statements=(turn,),
                contradictions=(
                    _whereabouts_flag(subject=_IMPOSTOR, claim_event_id=shifted_id),
                ),
            )
        )
    )
    assert matched.whereabouts_lie_supplied == 1

    stale = compute_supplied_channel_conversion(
        _one_meeting_report(
            _meeting(
                outcome="SKIPPED",
                ejected=None,
                statements=(turn,),
                contradictions=(_whereabouts_flag(subject=_IMPOSTOR),),
            )
        )
    )
    assert stale.whereabouts_lie_supplied == 0
    # The unmatched flag falls through to the sighting channel's rules and is
    # endpoint-banded there, so it supplies nothing anywhere.
    assert stale.supplied == 0


def test_whereabouts_flag_naming_someone_else_attributes_nothing() -> None:
    """A flag referencing a claim while naming another player supplies nobody.

    The whereabouts channel prosecutes the CLAIMANT: the flagged claim's
    speaker must be among the flag's subjects, so a proxy-shaped row cannot
    smuggle a different player into the denominator.
    """

    report = _one_meeting_report(
        _meeting(
            outcome="SKIPPED",
            ejected=None,
            statements=(_whereabouts_turn(speaker=_IMPOSTOR),),
            contradictions=(_whereabouts_flag(subject=_CREWMATE),),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.whereabouts_lie_supplied == 0
    assert result.supplied == 0


def test_plain_alibi_kind_flags_are_not_a_supplied_channel() -> None:
    """alibi_conflict / alibi_vs_physical without a whereabouts claim supply nothing.

    They are the starved alibi-anchored substrate the legacy cell already
    reports (7 flags on baseline 4, every one crew-subject) — not one of the
    close §8 channels.
    """

    conflict = ContradictionRef(
        contradiction_id="c-plain-1",
        kind="alibi_conflict",
        event_a_id="turn:m-0:turn-0:claim:0",
        event_b_id="turn:m-0:turn-1:claim:0",
        subjects=(_IMPOSTOR,),
        description="",
    )
    physical = ContradictionRef(
        contradiction_id="c-plain-2",
        kind="alibi_vs_physical",
        event_a_id="turn:m-0:turn-0:claim:0",
        event_b_id="turn:m-0:turn-2:obs:0",
        subjects=(_IMPOSTOR,),
        description="",
    )
    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            contradictions=(conflict, physical),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.supplied == 0
    assert result.conversion_rate is None


def test_crew_subjects_never_enter_the_denominator() -> None:
    """The successor measures the legacy question: evidence against IMPOSTORS.

    Flags naming crewmates — the actual shape of baseline 5's whereabouts
    lies and residual sighting flags — supply nothing on any channel; the
    role-blind membership itself still reports them (the caller applies
    ground truth, mirroring ``genuine_class_subjects``).
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        statements=(_whereabouts_turn(speaker=_CREWMATE),),
        contradictions=(
            _vent_flag(subject=_CREWMATE),
            _sighting_flag(subject=_CREWMATE),
            _whereabouts_flag(subject=_CREWMATE, contradiction_id="c-where-2"),
        ),
    )

    membership = supplied_channel_subjects(meeting)
    assert membership["witnessed_vent"] == frozenset({_CREWMATE})
    assert membership["sighting_contradiction"] == frozenset({_CREWMATE})
    assert membership["whereabouts_lie"] == frozenset({_CREWMATE})

    result = compute_supplied_channel_conversion(_one_meeting_report(meeting))
    assert result.supplied == 0
    assert result.witnessed_vent_supplied == 0
    assert result.sighting_contradiction_supplied == 0
    assert result.whereabouts_lie_supplied == 0


def test_supply_dedupes_per_meeting_and_across_channels() -> None:
    """The denominator-inflation guard: one meeting, one subject, one headline pair.

    Two vent flags against the same subject supply the vent channel once
    (the gp-2 flag-fountain lesson), and a subject supplied on two channels
    counts once in the headline while each channel cell keeps its own count.
    """

    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=_IMPOSTOR,
            statements=(_whereabouts_turn(speaker=_IMPOSTOR),),
            contradictions=(
                _vent_flag(subject=_IMPOSTOR),
                _vent_flag(subject=_IMPOSTOR, contradiction_id="c-vent-2"),
                _whereabouts_flag(subject=_IMPOSTOR),
            ),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.witnessed_vent_supplied == 1
    assert result.whereabouts_lie_supplied == 1
    assert result.supplied == 1
    assert result.converted == 1
    assert result.witnessed_vent_converted == 1
    assert result.whereabouts_lie_converted == 1


def test_same_subject_in_two_meetings_supplies_twice() -> None:
    """Dedup is per meeting, never per game: a repeat offender re-supplies."""

    game = _game(
        meetings=(
            _meeting(
                meeting_id="m-0",
                outcome="SKIPPED",
                ejected=None,
                contradictions=(_vent_flag(subject=_IMPOSTOR),),
            ),
            _meeting(
                meeting_id="m-1",
                outcome="EJECTED",
                ejected=_IMPOSTOR,
                contradictions=(_vent_flag(subject=_IMPOSTOR),),
            ),
        )
    )

    result = compute_supplied_channel_conversion(_tournament(game))

    assert result.supplied == 2
    assert result.converted == 1
    assert result.conversion_rate == 0.5


def test_malformed_ejected_meeting_supplies_but_never_converts() -> None:
    """An EJECTED meeting with no ejected id can supply, never convert.

    ``MeetingReport`` does not enforce the outcome/ejection coupling, so the
    malformed shape is type-possible; the conversion join requires an exact
    ejected-subject match (partial-replay robustness, the module convention).
    """

    report = _one_meeting_report(
        _meeting(
            outcome="EJECTED",
            ejected=None,
            contradictions=(_vent_flag(subject=_IMPOSTOR),),
        )
    )

    result = compute_supplied_channel_conversion(report)

    assert result.supplied == 1
    assert result.converted == 0


def test_supplied_subject_absent_from_roles_fails_loud() -> None:
    """A flagged subject missing from the ground truth is an internal inconsistency."""

    report = _one_meeting_report(
        _meeting(
            outcome="SKIPPED",
            ejected=None,
            contradictions=(_vent_flag(subject="p-99"),),
        )
    )

    with pytest.raises(KeyError):
        compute_supplied_channel_conversion(report)


def test_legacy_cells_mirror_compute_genuine_class_conversion() -> None:
    """The legacy column is the one-home fold, mirrored — never re-implemented.

    A transcript the repaired detector flags as genuine CANON-interior (the
    impostor's self-stated alibi against a crewmate's interior-tick sighting
    in a disjoint canonical room) supplies the LEGACY cell via re-derivation
    even with NO recorded rows — while the successor's own channels, which
    read only recorded rows, stay empty. The divergence is the proof that
    the two cells are independent instruments on one report.
    """

    meeting = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        reports=(
            MeetingTurn(
                turn_id="m-0:turn-0",
                turn_index=0,
                speaker=_IMPOSTOR,
                turn_kind="opening",
                reply_to=None,
                observations=(),
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject=_IMPOSTOR,
                        from_tick=2,
                        to_tick=8,
                        room="CAFETERIA",
                    ),
                ),
                free_text="",
            ),
        ),
        statements=(
            MeetingTurn(
                turn_id="m-0:turn-1",
                turn_index=1,
                speaker=_CREWMATE,
                turn_kind="reply",
                reply_to=None,
                observations=(_saw(subject=_IMPOSTOR, tick=5, room="STORAGE"),),
                claims=(),
                free_text="",
            ),
        ),
        ballots=tuple(
            _ballot(target="SKIP", voter=voter, reason_id=None) for voter in _ROLES
        ),
    )
    report = _one_meeting_report(meeting)

    result = compute_supplied_channel_conversion(report)
    legacy = compute_genuine_class_conversion(report)

    assert legacy.supplied == 1
    assert result.legacy_alibi_supplied == legacy.supplied
    assert result.legacy_alibi_converted == legacy.converted
    assert result.legacy_alibi_conversion_rate == legacy.conversion_rate
    # The successor's own channels read recorded rows only — none here.
    assert result.supplied == 0
    assert result.conversion_rate is None


def test_successor_report_ships_both_notes_verbatim() -> None:
    """Both cells are labeled: the canary-eligible successor and the starved legacy."""

    result = compute_supplied_channel_conversion(_tournament())

    assert result.note == SUPPLIED_CHANNEL_GATE_NOTE
    assert result.legacy_note == LEGACY_ALIBI_CELL_NOTE
    assert "canary-eligible" in SUPPLIED_CHANNEL_GATE_NOTE
    assert "NEVER a canary" in LEGACY_ALIBI_CELL_NOTE
    assert "STARVED" in LEGACY_ALIBI_CELL_NOTE
    # The re-examination pointer for a future substrate that re-supplies
    # alibi lies (the DoD's docstring/provenance requirement, on the report).
    assert "re-supplies checkable alibi lies" in LEGACY_ALIBI_CELL_NOTE


def test_successor_accepts_bare_sequence_and_empty_tournament() -> None:
    """Signature parity with the module's other analyzers."""

    meeting = _meeting(
        outcome="EJECTED",
        ejected=_IMPOSTOR,
        contradictions=(_vent_flag(subject=_IMPOSTOR),),
    )
    game = _game(meetings=(meeting,))

    assert compute_supplied_channel_conversion(
        [game]
    ) == compute_supplied_channel_conversion(_tournament(game))

    empty = compute_supplied_channel_conversion(_tournament())
    assert empty.supplied == 0
    assert empty.converted == 0
    assert empty.conversion_rate is None
    assert empty.legacy_alibi_supplied == 0
    assert empty.legacy_alibi_conversion_rate is None


def test_successor_model_validators_fail_loud() -> None:
    """An inconsistent successor report can never be constructed."""

    with pytest.raises(ValidationError, match="non-negative"):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(supplied=-1)
        )
    with pytest.raises(ValidationError, match="converted cannot exceed supplied"):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(converted=1)
        )
    with pytest.raises(
        ValidationError, match="channel's converted cannot exceed its supplied"
    ):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(
                supplied=1,
                converted=1,
                conversion_rate=1.0,
                witnessed_vent_supplied=0,
                witnessed_vent_converted=1,
            )
        )
    with pytest.raises(
        ValidationError, match="channel's supplied cannot exceed the headline"
    ):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(witnessed_vent_supplied=1)
        )
    with pytest.raises(
        ValidationError, match="headline supplied cannot exceed the sum"
    ):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(supplied=1, conversion_rate=0.0)
        )
    with pytest.raises(ValidationError, match="must be None when nothing was supplied"):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(conversion_rate=0.0)
        )
    with pytest.raises(ValidationError, match="must be set when supplied > 0"):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(supplied=1, converted=0, witnessed_vent_supplied=1)
        )
    with pytest.raises(
        ValidationError, match="legacy converted cannot exceed legacy supplied"
    ):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(legacy_alibi_converted=1)
        )
    with pytest.raises(ValidationError, match="legacy_alibi_conversion_rate"):
        SuppliedChannelConversionReport.model_validate(
            _supplied_report_payload(legacy_alibi_conversion_rate=0.5)
        )

    frozen = compute_supplied_channel_conversion(_tournament())
    with pytest.raises(ValidationError):
        frozen.supplied = 1


def test_committed_9p2i_report_pins_the_successor_instrument() -> None:
    """The successor's committed-bytes cells on the baseline-6 9p2i set.

    Re-anchored to the baseline-6 meeting-layer-graduation re-record (model
    Qwen/Qwen3.6-27B, prompt set qwen3_6_27b.v3; four meeting levers
    unconditional, impostor_roll_call OFF); NOT immutable — the next re-record
    regenerates the report and updates these pins, the standard re-record
    pattern.

    The substrate supplies the successor 79 (meeting, impostor) pairs across
    three channels: 76 witnessed-vent pairs (68 converted), 2 sighting-
    contradiction pairs (both converted), and 7 whereabouts-lie pairs (5
    converted), for 70 conversions overall (rate 0.886). The legacy
    alibi-anchored cell now reads a non-zero 4/3 (rate 0.75), mirrored from the
    committed gate block.

    Task 19.5 wires this cell onto ``GateMetricsReport``, so the STORED block
    is pinned against the recompute here too.
    """

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )
    result = compute_supplied_channel_conversion(report.report)

    assert result.supplied == 76  # was 79
    assert result.converted == 69  # was 70
    assert result.conversion_rate == pytest.approx(69 / 76)  # was 70 / 79
    assert result.witnessed_vent_supplied == 74  # was 76
    assert result.witnessed_vent_converted == 69  # was 68
    assert result.sighting_contradiction_supplied == 0  # was 2
    assert result.sighting_contradiction_converted == 0  # was 2
    assert result.whereabouts_lie_supplied == 5  # was 7
    assert result.whereabouts_lie_converted == 2  # was 5

    # The legacy alibi-anchored cell: preserved, labeled, now reading a non-zero
    # 4/3 (rate 0.75), mirrored exactly from the committed gate block (one home,
    # never recomputed differently).
    assert result.legacy_alibi_supplied == 1  # was 4
    assert result.legacy_alibi_converted == 0  # was 3
    assert result.legacy_alibi_conversion_rate == pytest.approx(0.0)  # was 0.75
    committed_legacy = report.gate_metrics.genuine_class_conversion
    assert result.legacy_alibi_supplied == committed_legacy.supplied
    assert result.legacy_alibi_converted == committed_legacy.converted
    assert result.legacy_alibi_conversion_rate == committed_legacy.conversion_rate

    assert result.note == SUPPLIED_CHANNEL_GATE_NOTE
    assert result.legacy_note == LEGACY_ALIBI_CELL_NOTE

    # STORED vs RECOMPUTE (Task 19.5): the cell now ships on the committed gate
    # block, so the regenerated bytes must equal what the analyzer recomputes.
    assert report.gate_metrics.supplied_channel_conversion == result

    # Cross-surface sanity: converted pairs are impostor ejections, so the
    # successor's numerator is bounded by the recorded impostor-ejection
    # census (70 of the set's 78).
    assert result.converted <= report.vote_correctness.impostor_ejections

    # Per-seed identity: the aggregate is the sum of its per-seed parts
    # (dedup is per meeting, never cross-game — no masked cancellation).
    per_seed = [
        compute_supplied_channel_conversion((game,)) for game in report.report.games
    ]
    assert sum(row.supplied for row in per_seed) == result.supplied
    assert sum(row.converted for row in per_seed) == result.converted
    assert (
        sum(row.witnessed_vent_supplied for row in per_seed)
        == result.witnessed_vent_supplied
    )


def test_committed_flat_4p1i_report_pins_the_successor_instrument() -> None:
    """The flat 4p/1i set's successor cells, pinned at the baseline-6 re-record.

    NOT immutable — the next re-record regenerates and updates these. The
    reference set supplies 11 pairs — 10 witnessed-vent (9 converted) plus
    1 sighting-contradiction pair (converted) — and converts 10 of 11; the
    recorded whereabouts-lie flags name crew liars, so the whereabouts cell reads
    0 impostor pairs; the legacy cell reads 1/1.

    Task 19.5 wires this cell onto ``GateMetricsReport``, so the STORED block
    is pinned against the recompute here too.
    """

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_FLAT_4P1I_REPORT.read_text(encoding="utf-8")
    )
    result = compute_supplied_channel_conversion(report.report)

    assert result.supplied == 19  # was 11
    assert result.converted == 19  # was 10
    assert result.conversion_rate == pytest.approx(1 / 1)  # was 10 / 11
    assert result.witnessed_vent_supplied == 19  # was 10
    assert result.witnessed_vent_converted == 19  # was 9
    assert result.sighting_contradiction_supplied == 0  # was 1
    assert result.whereabouts_lie_supplied == 0

    assert result.legacy_alibi_supplied == 0  # was 1
    assert result.legacy_alibi_converted == 0  # was 1
    assert result.legacy_alibi_conversion_rate == pytest.approx(1.0)
    committed_legacy = report.gate_metrics.genuine_class_conversion
    assert result.legacy_alibi_supplied == committed_legacy.supplied
    assert result.legacy_alibi_converted == committed_legacy.converted

    # STORED vs RECOMPUTE (Task 19.5): the cell now ships on the committed gate
    # block, so the regenerated bytes must equal what the analyzer recomputes.
    assert report.gate_metrics.supplied_channel_conversion == result
