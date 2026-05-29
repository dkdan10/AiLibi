"""Unit tests for the accusation-calibration metric (DESIGN.md §11.3).

Fixtures are built by instantiating the schema models directly (this task does
not touch the tournament runner; that is Task 5.6). They pin: the binning and
boundary convention (``confidence`` exactly ``0.0`` and ``1.0``); the
well-calibrated vs mis-calibrated readings; the two confidence sources reported
separately; ``"SKIP"`` ballot exclusion before the role lookup; partial-replay
robustness (no accusations / no meetings / all-``SKIP``); and the fail-loud
behaviour when an accusation target is absent from the role ground truth.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.accusation_calibration import (
    DEFAULT_N_BINS,
    AccusationCalibrationReport,
    CalibrationBin,
    compute_accusation_calibration,
)
from eval.report_schema import (
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    CorroborationClaim,
    MeetingTranscript,
    PlayerId,
    ReportDocument,
    Statement,
    VoteBallot,
)

# A 4-player roster with p-3 the impostor; the default where the specific
# assignment does not matter.
_ROLES: Mapping[PlayerId, Role] = {
    "p-0": "CREWMATE",
    "p-1": "CREWMATE",
    "p-2": "CREWMATE",
    "p-3": "IMPOSTOR",
}


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _acc(against: str, confidence: float) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=against, confidence=confidence, reason="r"
    )


def _ballot(target: str, confidence: float, *, voter: str = "p-0") -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=None,
        rationale_text="",
    )


def _meeting(
    *,
    report_claims: tuple[Claim, ...] = (),
    statement_claims: tuple[Claim, ...] = (),
    ballots: tuple[VoteBallot, ...] = (),
    meeting_id: str = "m-0",
) -> MeetingReport:
    """A meeting carrying one report + one statement (claims may be empty)."""

    transcript = MeetingTranscript(
        reports=(
            ReportDocument(agent_id="p-0", tick=10, claims=report_claims, free_text=""),
        ),
        statements=(
            Statement(
                statement_id="s-0",
                speaker="p-0",
                tick=10,
                round_index=0,
                target=None,
                claims=statement_claims,
                free_text="",
            ),
        ),
    )
    return MeetingReport(
        meeting_id=meeting_id,
        tick=10,
        triggered_by="p-0",
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=transcript,
        ballots=ballots,
        contradictions=(),
        llm_calls=(),
    )


def _game(
    *,
    game_id: str,
    roles: Mapping[PlayerId, Role],
    meetings: tuple[MeetingReport, ...],
    seed: int = 1,
) -> GameReport:
    return GameReport(
        game_id=game_id,
        seed=seed,
        winner=None,
        reason="test",
        final_tick=None,
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
    return TournamentReport(games=games, seeds_used=tuple(g.seed for g in games))


# ---------------------------------------------------------------------------
# Well-calibrated vs mis-calibrated
# ---------------------------------------------------------------------------


def test_high_confidence_against_impostor_is_well_calibrated() -> None:
    meeting = _meeting(statement_claims=(_acc("p-3", 0.95), _acc("p-3", 0.95)))
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report)

    assert result.accusation_claim_total == 2
    top = result.accusation_claim_bins[-1]
    assert top.bin_index == DEFAULT_N_BINS - 1
    assert top.count == 2
    assert top.impostor_hits == 2
    assert top.actual_impostor_rate == 1.0
    assert top.mean_confidence == pytest.approx(0.95)
    # Confident accusations that are right -> small calibration error.
    assert result.accusation_claim_ece == pytest.approx(0.05)


def test_high_confidence_against_crewmate_is_miscalibrated() -> None:
    meeting = _meeting(statement_claims=(_acc("p-1", 0.95), _acc("p-2", 0.95)))
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report)

    top = result.accusation_claim_bins[-1]
    assert top.count == 2
    assert top.impostor_hits == 0
    # A genuine 0.0 rate (populated bin, all misses) -- distinct from a None
    # empty bin.
    assert top.actual_impostor_rate == 0.0
    assert top.mean_confidence == pytest.approx(0.95)
    # Confident accusations that are wrong -> large calibration error.
    assert result.accusation_claim_ece == pytest.approx(0.95)


# ---------------------------------------------------------------------------
# Binning + boundary convention
# ---------------------------------------------------------------------------


def test_spread_pins_boundary_convention() -> None:
    # 0.0 (against a crewmate) -> bin 0; 0.5 (against the impostor) -> bin 5;
    # 1.0 (against the impostor) -> the closed top bin, never an index-10 bin.
    meeting = _meeting(
        statement_claims=(_acc("p-0", 0.0), _acc("p-3", 0.5), _acc("p-3", 1.0))
    )
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report, n_bins=10)
    bins = result.accusation_claim_bins

    assert result.accusation_claim_total == 3
    assert len(bins) == 10

    assert bins[0].lo == 0.0
    assert bins[0].count == 1
    assert bins[0].impostor_hits == 0
    assert bins[0].actual_impostor_rate == 0.0
    # A populated bin whose only accusation has confidence 0.0 reports a real
    # 0.0 mean -- not the None of an empty bin.
    assert bins[0].mean_confidence == 0.0

    assert bins[5].count == 1
    assert bins[5].impostor_hits == 1
    assert bins[5].actual_impostor_rate == 1.0

    # confidence == 1.0 lands in the closed final bin [0.9, 1.0].
    assert bins[-1].bin_index == 9
    assert bins[-1].hi == 1.0
    assert bins[-1].count == 1
    assert bins[-1].impostor_hits == 1
    assert bins[-1].actual_impostor_rate == 1.0
    assert bins[-1].mean_confidence == 1.0

    # Every other bin is empty: count 0 with None (not 0.0, not NaN) rate.
    populated = {0, 5, 9}
    for index, current_bin in enumerate(bins):
        if index not in populated:
            assert current_bin.count == 0
            assert current_bin.impostor_hits == 0
            assert current_bin.actual_impostor_rate is None
            assert current_bin.mean_confidence is None


def test_n_bins_parameter_controls_bin_count() -> None:
    meeting = _meeting(statement_claims=(_acc("p-3", 0.95),))
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report, n_bins=4)

    assert result.n_bins == 4
    assert len(result.accusation_claim_bins) == 4
    assert len(result.vote_ballot_bins) == 4
    # int(0.95 * 4) == 3 -> the top quartile bin [0.75, 1.0].
    top = result.accusation_claim_bins[-1]
    assert top.bin_index == 3
    assert top.lo == 0.75
    assert top.hi == 1.0
    assert top.midpoint == 0.875
    assert top.count == 1


def test_n_bins_below_one_raises() -> None:
    report = TournamentReport(games=(), seeds_used=())
    with pytest.raises(ValueError, match="n_bins"):
        compute_accusation_calibration(report, n_bins=0)


# ---------------------------------------------------------------------------
# Two confidence sources, reported separately
# ---------------------------------------------------------------------------


def test_vote_ballots_tracked_separately_and_skip_excluded() -> None:
    meeting = _meeting(
        ballots=(
            _ballot("p-3", 0.85, voter="p-0"),  # impostor -> bin 8, hit
            _ballot("SKIP", 0.2, voter="p-1"),  # excluded BEFORE any lookup
            _ballot("p-1", 0.85, voter="p-2"),  # crewmate -> bin 8, miss
        ),
    )
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report)

    # No accusation claims -> that curve is entirely empty.
    assert result.accusation_claim_total == 0
    assert all(b.count == 0 for b in result.accusation_claim_bins)
    assert result.accusation_claim_ece is None

    # SKIP excluded: 3 ballots in, 2 scored.
    assert result.vote_ballot_total == 2
    ballot_bin = result.vote_ballot_bins[8]
    assert ballot_bin.count == 2
    assert ballot_bin.impostor_hits == 1
    assert ballot_bin.actual_impostor_rate == 0.5
    assert ballot_bin.mean_confidence == pytest.approx(0.85)


def test_accusation_claims_counted_from_reports_and_statements() -> None:
    meeting = _meeting(
        report_claims=(_acc("p-3", 0.95),),
        statement_claims=(_acc("p-3", 0.95),),
    )
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report)

    assert result.accusation_claim_total == 2
    assert result.accusation_claim_bins[-1].count == 2


def test_non_accusation_claims_are_ignored() -> None:
    alibi: Claim = AlibiClaim(
        type="alibi", subject="p-0", from_tick=1, to_tick=5, room="MEDBAY"
    )
    corroboration: Claim = CorroborationClaim(
        type="corroboration", supports="p-1", on_tick=3, reason="r"
    )
    meeting = _meeting(
        report_claims=(alibi,),
        statement_claims=(corroboration, _acc("p-3", 0.95)),
    )
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report)

    assert result.accusation_claim_total == 1


# ---------------------------------------------------------------------------
# Aggregation + ECE
# ---------------------------------------------------------------------------


def test_correctness_uses_each_games_own_roles() -> None:
    roles_a: Mapping[PlayerId, Role] = {
        "p-0": "CREWMATE",
        "p-1": "CREWMATE",
        "p-2": "CREWMATE",
        "p-3": "IMPOSTOR",
    }
    # Impostor swapped: p-2 is the impostor here, p-3 a crewmate.
    roles_b: Mapping[PlayerId, Role] = {
        "p-0": "CREWMATE",
        "p-1": "CREWMATE",
        "p-2": "IMPOSTOR",
        "p-3": "CREWMATE",
    }
    game_a = _game(
        game_id="a",
        roles=roles_a,
        seed=1,
        meetings=(_meeting(statement_claims=(_acc("p-3", 0.95),)),),
    )
    game_b = _game(
        game_id="b",
        roles=roles_b,
        seed=2,
        meetings=(_meeting(statement_claims=(_acc("p-2", 0.95),)),),
    )
    report = _tournament(game_a, game_b)

    result = compute_accusation_calibration(report)

    top = result.accusation_claim_bins[-1]
    assert top.count == 2
    # Both hits only if each accusation is scored against its own game's roles.
    assert top.impostor_hits == 2
    assert top.actual_impostor_rate == 1.0


def test_expected_calibration_error_is_population_weighted() -> None:
    # n_bins=2: bin 0 = [0, 0.5), bin 1 = [0.5, 1.0].
    #   bin 0: two accusations at 0.25, one hits -> rate 0.5, mean 0.25.
    #   bin 1: two accusations at 0.75, both hit -> rate 1.0, mean 0.75.
    #   ECE = (2/4)|0.5-0.25| + (2/4)|1.0-0.75| = 0.125 + 0.125 = 0.25.
    meeting = _meeting(
        statement_claims=(
            _acc("p-3", 0.25),  # hit  -> bin 0
            _acc("p-1", 0.25),  # miss -> bin 0
            _acc("p-3", 0.75),  # hit  -> bin 1
            _acc("p-3", 0.75),  # hit  -> bin 1
        )
    )
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report, n_bins=2)

    assert result.n_bins == 2
    bin0, bin1 = result.accusation_claim_bins
    assert bin0.count == 2
    assert bin0.impostor_hits == 1
    assert bin0.actual_impostor_rate == 0.5
    assert bin0.mean_confidence == pytest.approx(0.25)
    assert bin1.count == 2
    assert bin1.impostor_hits == 2
    assert bin1.actual_impostor_rate == 1.0
    assert bin1.mean_confidence == pytest.approx(0.75)
    assert result.accusation_claim_ece == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# Partial-replay robustness (absence of accusations never raises)
# ---------------------------------------------------------------------------


def test_absent_accusations_yield_empty_bins_without_raising() -> None:
    no_meeting_game = _game(game_id="g0", roles=_ROLES, meetings=(), seed=1)
    all_skip_meeting = _meeting(
        ballots=(
            _ballot("SKIP", 0.5, voter="p-0"),
            _ballot("SKIP", 0.9, voter="p-1"),
        ),
    )
    empty_meeting_game = _game(
        game_id="g1", roles=_ROLES, meetings=(all_skip_meeting,), seed=2
    )
    report = _tournament(no_meeting_game, empty_meeting_game)

    result = compute_accusation_calibration(report)

    assert result.n_bins == DEFAULT_N_BINS
    assert result.accusation_claim_total == 0
    assert result.vote_ballot_total == 0
    assert result.accusation_claim_ece is None
    assert result.vote_ballot_ece is None
    assert len(result.accusation_claim_bins) == DEFAULT_N_BINS
    assert len(result.vote_ballot_bins) == DEFAULT_N_BINS
    for current_bin in (*result.accusation_claim_bins, *result.vote_ballot_bins):
        assert current_bin.count == 0
        assert current_bin.impostor_hits == 0
        assert current_bin.actual_impostor_rate is None
        assert current_bin.mean_confidence is None


def test_empty_tournament_is_empty_without_raising() -> None:
    report = TournamentReport(games=(), seeds_used=())

    result = compute_accusation_calibration(report)

    assert result.accusation_claim_total == 0
    assert result.vote_ballot_total == 0
    assert result.accusation_claim_ece is None
    assert result.vote_ballot_ece is None
    assert all(b.count == 0 for b in result.accusation_claim_bins)
    assert all(b.count == 0 for b in result.vote_ballot_bins)


# ---------------------------------------------------------------------------
# Fail-loud on an unresolvable target
# ---------------------------------------------------------------------------


def test_accusation_claim_target_absent_from_roles_raises() -> None:
    meeting = _meeting(statement_claims=(_acc("p-99", 0.9),))
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    with pytest.raises(ValueError, match="p-99"):
        compute_accusation_calibration(report)


def test_vote_ballot_target_absent_from_roles_raises() -> None:
    meeting = _meeting(ballots=(_ballot("p-99", 0.9),))
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    with pytest.raises(ValueError, match="p-99"):
        compute_accusation_calibration(report)


# ---------------------------------------------------------------------------
# Result-model invariants
# ---------------------------------------------------------------------------


def test_result_model_is_frozen() -> None:
    meeting = _meeting(statement_claims=(_acc("p-3", 0.95),))
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))
    result = compute_accusation_calibration(report)

    with pytest.raises(ValidationError):
        result.accusation_claim_total = 99
    with pytest.raises(ValidationError):
        result.accusation_claim_bins[0].count = 99


def test_result_model_round_trips_through_json() -> None:
    meeting = _meeting(
        statement_claims=(_acc("p-0", 0.0), _acc("p-3", 1.0)),
        ballots=(_ballot("p-3", 0.85), _ballot("SKIP", 0.1)),
    )
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))
    result = compute_accusation_calibration(report)

    restored = AccusationCalibrationReport.model_validate_json(result.model_dump_json())

    assert restored == result


def test_report_validates_bin_count_matches_n_bins() -> None:
    one_bin = (
        CalibrationBin(
            bin_index=0,
            lo=0.0,
            hi=1.0,
            midpoint=0.5,
            count=0,
            impostor_hits=0,
            actual_impostor_rate=None,
            mean_confidence=None,
        ),
    )
    with pytest.raises(ValidationError, match="n_bins"):
        AccusationCalibrationReport(
            n_bins=10,
            accusation_claim_bins=one_bin,
            accusation_claim_total=0,
            accusation_claim_ece=None,
            vote_ballot_bins=one_bin,
            vote_ballot_total=0,
            vote_ballot_ece=None,
        )
