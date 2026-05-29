"""Unit tests for the vote-correctness metric (DESIGN.md §11.3).

Fixtures are built by instantiating ``report_schema`` / ``meetings.schemas``
models directly -- no tournament run -- so the tests pin the "real evidence"
predicate, the impostor-vs-crewmate classification, the kill-witness tick
window, and the partial-replay robustness rules without any orchestrator or LLM
dependency.

The predicate is exercised adversarially: an impostor ejected on *no* evidence
(or on an accusation/ballot alone) must score as incorrect, or the metric would
collapse into the impostor-ejection rate it exists to refine.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.report_schema import (
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from eval.vote_correctness import (
    KILL_WITNESS_TICK_WINDOW,
    VoteCorrectnessReport,
    compute_vote_correctness,
)
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    FoundBodyObservation,
    MeetingOutcome,
    MeetingTranscript,
    PlayerId,
    ReportDocument,
    SawPlayerObservation,
    Statement,
    VoteBallot,
)

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
) -> ReportDocument:
    return ReportDocument(
        agent_id=agent_id,
        tick=tick,
        observations=observations,
        claims=(),
        free_text="",
    )


def _accusation_statement(*, against: PlayerId, sid: str = "s-1") -> Statement:
    return Statement(
        statement_id=sid,
        speaker="p-0",
        tick=40,
        round_index=0,
        target=against,
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


def _ballot(*, target: PlayerId, reason_id: str | None = "s-1") -> VoteBallot:
    return VoteBallot(
        voter="p-0",
        target=target,
        confidence=0.9,
        primary_reason_id=reason_id,
        rationale_text="",
    )


def _meeting(
    *,
    outcome: MeetingOutcome,
    ejected: PlayerId | None,
    meeting_id: str = "m-0",
    tick: int = 40,
    reports: tuple[ReportDocument, ...] = (),
    statements: tuple[Statement, ...] = (),
    contradictions: tuple[ContradictionRef, ...] = (),
    ballots: tuple[VoteBallot, ...] = (),
) -> MeetingReport:
    return MeetingReport(
        meeting_id=meeting_id,
        tick=tick,
        triggered_by="p-0",
        outcome=outcome,
        ejected_player_id=ejected,
        transcript=MeetingTranscript(reports=reports, statements=statements),
        ballots=ballots,
        contradictions=contradictions,
        llm_calls=(),
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
    return TournamentReport(games=games, seeds_used=tuple(game.seed for game in games))


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
        )


def test_result_model_rejects_rate_when_no_impostor_ejections() -> None:
    with pytest.raises(ValidationError, match="must be None"):
        VoteCorrectnessReport(
            total_ejections=0,
            impostor_ejections=0,
            crewmate_ejections=0,
            evidence_backed_impostor_ejections=0,
            vote_correctness_rate=0.0,
        )


def test_result_model_rejects_backed_exceeding_impostor() -> None:
    with pytest.raises(ValidationError, match="cannot exceed impostor_ejections"):
        VoteCorrectnessReport(
            total_ejections=1,
            impostor_ejections=1,
            crewmate_ejections=0,
            evidence_backed_impostor_ejections=2,
            vote_correctness_rate=1.0,
        )
