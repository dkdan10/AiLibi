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

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.accusation_calibration import (
    DEFAULT_N_BINS,
    MIN_POPULATED_BINS_FOR_POWER,
    AccusationCalibrationReport,
    CalibrationBin,
    CalibrationCurve,
    compute_accusation_calibration,
)
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
)
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
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
    MeetingTurn,
    PlayerId,
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
    """A meeting whose chain has an opening turn + a reply turn (§5.2).

    ``report_claims`` ride the opening turn and ``statement_claims`` the reply
    turn; either may be empty. The calibration metric walks every turn's claims,
    so the two are summed exactly as the old (reports, statements) pair was.
    """

    transcript = MeetingTranscript(
        turns=(
            MeetingTurn(
                turn_id=f"{meeting_id}:turn-0",
                turn_index=0,
                speaker="p-0",
                turn_kind="opening",
                reply_to=None,
                observations=(),
                claims=report_claims,
                free_text="",
            ),
            MeetingTurn(
                turn_id=f"{meeting_id}:turn-1",
                turn_index=1,
                speaker="p-0",
                turn_kind="reply",
                reply_to=None,
                observations=(),
                claims=statement_claims,
                free_text="",
            ),
        ),
    )
    return MeetingReport(
        meeting_id=meeting_id,
        tick=10,
        triggered_by="p-0",
        trigger="report",
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
    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=games,
        seeds_used=tuple(g.seed for g in games),
    )


_EMPTY_BINS: tuple[CalibrationBin, ...] = tuple(
    CalibrationBin(
        bin_index=i,
        lo=i / DEFAULT_N_BINS,
        hi=(i + 1) / DEFAULT_N_BINS,
        midpoint=(i + 0.5) / DEFAULT_N_BINS,
        count=0,
        impostor_hits=0,
        actual_impostor_rate=None,
        mean_confidence=None,
    )
    for i in range(DEFAULT_N_BINS)
)


def _empty_curve(bins: tuple[CalibrationBin, ...]) -> CalibrationCurve:
    """A zero-sample curve over ``bins`` — the filler for validator fixtures."""

    return _curve_with_total(bins, 0)


def _curve_with_total(bins: tuple[CalibrationBin, ...], total: int) -> CalibrationCurve:
    """A curve declaring ``total`` samples over ``bins``, populated bins derived."""

    populated = sum(1 for b in bins if b.count > 0)
    return CalibrationCurve(
        bins=bins,
        total=total,
        ece=None,
        populated_bins=populated,
        low_power=populated < MIN_POPULATED_BINS_FOR_POWER,
    )


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
    report = TournamentReport(
        format_version=CURRENT_FORMAT_VERSION, games=(), seeds_used=()
    )
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
    report = TournamentReport(
        format_version=CURRENT_FORMAT_VERSION, games=(), seeds_used=()
    )

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
            accusation_claim_populated_bins=0,
            accusation_claim_low_power=True,
            accusation_claim_crew_accuser=_empty_curve(one_bin),
            accusation_claim_impostor_accuser=_empty_curve(one_bin),
            vote_ballot_bins=one_bin,
            vote_ballot_total=0,
            vote_ballot_ece=None,
            vote_ballot_populated_bins=0,
            vote_ballot_low_power=True,
            vote_ballot_guard_authored_excluded=0,
        )


# ---------------------------------------------------------------------------
# Task 7.11 per-bin power flag (audit F-F-3 / gp-7)
# ---------------------------------------------------------------------------


def test_clustered_confidences_flag_low_power() -> None:
    """Confidences clustered into a couple of bins -> low_power (the qwen2.5 case).

    Accusation claims all at 0.55 / 0.85 (two bins) and ballots all at 0.85 (one
    bin) populate far fewer than MIN_POPULATED_BINS_FOR_POWER bins, so both
    curves are flagged low-power even though their ECE is a valid number.
    """

    meeting = _meeting(
        statement_claims=(_acc("p-3", 0.55), _acc("p-1", 0.85), _acc("p-3", 0.85)),
        ballots=(_ballot("p-3", 0.85), _ballot("p-1", 0.85)),
    )
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report)

    assert result.accusation_claim_populated_bins == 2  # 0.55 bin + 0.85 bin
    assert result.accusation_claim_populated_bins < MIN_POPULATED_BINS_FOR_POWER
    assert result.accusation_claim_low_power is True
    assert result.vote_ballot_populated_bins == 1  # all at 0.85
    assert result.vote_ballot_low_power is True
    # The flag is advisory: the ECE is still computed, not nulled.
    assert result.accusation_claim_ece is not None


def test_well_spread_confidences_are_not_low_power() -> None:
    """Accusations spread across >= MIN_POPULATED_BINS_FOR_POWER bins: not flagged."""

    # One accusation in each of MIN_POPULATED_BINS_FOR_POWER distinct deciles.
    claims = tuple(
        _acc("p-3", (bin_index + 0.5) / DEFAULT_N_BINS)
        for bin_index in range(MIN_POPULATED_BINS_FOR_POWER)
    )
    meeting = _meeting(statement_claims=claims)
    report = _tournament(_game(game_id="g", roles=_ROLES, meetings=(meeting,)))

    result = compute_accusation_calibration(report)

    assert result.accusation_claim_populated_bins == MIN_POPULATED_BINS_FOR_POWER
    assert result.accusation_claim_low_power is False


def test_empty_curve_is_low_power_with_zero_populated_bins() -> None:
    """A curve that binned nothing has zero populated bins and is low-power."""

    result = compute_accusation_calibration(_tournament())
    assert result.accusation_claim_total == 0
    assert result.accusation_claim_populated_bins == 0
    assert result.accusation_claim_low_power is True
    assert result.accusation_claim_ece is None


def test_report_rejects_mismatched_populated_bin_count() -> None:
    """The validator fails loud if declared populated_bins != actual non-empty bins."""

    bins = tuple(
        CalibrationBin(
            bin_index=i,
            lo=i / DEFAULT_N_BINS,
            hi=(i + 1) / DEFAULT_N_BINS,
            midpoint=(i + 0.5) / DEFAULT_N_BINS,
            count=(1 if i == 0 else 0),
            impostor_hits=0,
            actual_impostor_rate=(0.0 if i == 0 else None),
            mean_confidence=(0.05 if i == 0 else None),
        )
        for i in range(DEFAULT_N_BINS)
    )
    with pytest.raises(ValidationError, match="populated-bin count must equal"):
        AccusationCalibrationReport(
            n_bins=DEFAULT_N_BINS,
            accusation_claim_bins=bins,
            accusation_claim_total=1,
            accusation_claim_ece=0.05,
            accusation_claim_populated_bins=5,  # actual is 1
            accusation_claim_low_power=True,
            accusation_claim_crew_accuser=_curve_with_total(bins, 1),
            accusation_claim_impostor_accuser=_empty_curve(_EMPTY_BINS),
            vote_ballot_bins=bins,
            vote_ballot_total=1,
            vote_ballot_ece=0.05,
            vote_ballot_populated_bins=1,
            vote_ballot_low_power=True,
            vote_ballot_guard_authored_excluded=0,
        )


# ---------------------------------------------------------------------------
# Task 21.9 — the accuser-role split and the guard-authored exclusion (A-8/A-3)
# ---------------------------------------------------------------------------

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

# Each committed set's re-derived claim curves: pooled, crew-accuser and
# impostor-accuser, as (ece, total). Re-derived from the committed reports; a
# re-record regenerates them.
_COMMITTED_SPLIT: Final[
    Mapping[str, tuple[tuple[float, int], tuple[float, int], tuple[float, int]]]
] = {
    "replays/samples/9p2i": (
        (0.2977642276422763, 738),  # was (0.30033244680851046, 752)
        (0.17509090909090924, 550),  # was (0.18190730837789656, 561)
        (0.6757978723404261, 188),  # was (0.6769633507853406, 191)
    ),
    "replays/ml_corpus/9p2i": (
        (0.27847654435671193, 2153),  # was (0.28170283018867964, 2120)
        (0.163608374384236, 1624),  # was (0.17446038677479642, 1603)
        (0.6791304347826082, 529),  # was (0.671856866537717, 517)
    ),
    "replays/samples/4p1i": (
        (0.2946601941747573, 103),  # was (0.24866071428571437, 112)
        (0.12307692307692301, 65),  # was (0.06506849315068489, 73)
        (0.6407894736842105, 38),  # was (0.6282051282051283, 39)
    ),
    "replays/ml_corpus/4p1i": (
        (0.28750000000000003, 120),  # was (0.26585365853658544, 123)
        (0.10064935064935064, 77),  # was (0.09493670886075953, 79)
        (0.6453488372093021, 43),  # was (0.6409090909090909, 44)
    ),
}


def _committed_calibration(sample_dir: str) -> AccusationCalibrationReport:
    raw = (_REPO_ROOT / sample_dir / "tournament-eval-report.json").read_text(
        encoding="utf-8"
    )
    return AccusationCalibrationReport.model_validate(
        json.loads(raw)["accusation_calibration"]
    )


@pytest.mark.parametrize("sample_dir", sorted(_COMMITTED_SPLIT))
def test_committed_sets_pin_the_accuser_role_split(sample_dir: str) -> None:
    """The role-conditioned curves on the committed bytes, and what they mean.

    The pooled curve is UNMOVED by the split — same ece, same total — and the
    two conditioned curves partition it. The impostor curve hits ZERO on every
    set, and the reading is two-part: on 9p2i the teammate firewall deletes the
    accusation of the one other scoring-correct target, and on 4p1i there is no
    teammate at all, which is STRUCTURAL; the remaining scoring-correct target
    on both shapes is a SELF-accusation, which is recordable and would score, so
    its absence here is a fact about this corpus (see
    ``test_a_self_accusation_by_an_impostor_does_score_as_a_hit``). So the
    impostor curve's ece is essentially its mean stated confidence, and reading
    the pooled number as agent overconfidence prices that narrowing as a
    behaviour.
    """

    result = _committed_calibration(sample_dir)
    (pooled_ece, pooled_total), crew_pin, impostor_pin = _COMMITTED_SPLIT[sample_dir]
    assert result.accusation_claim_ece == pooled_ece
    assert result.accusation_claim_total == pooled_total

    crew = result.accusation_claim_crew_accuser
    impostor = result.accusation_claim_impostor_accuser
    assert (crew.ece, crew.total) == crew_pin
    assert (impostor.ece, impostor.total) == impostor_pin
    # A partition, asserted on both sides of the identity.
    assert crew.total + impostor.total == result.accusation_claim_total
    # The ceiling itself: not one impostor accusation on the record scores.
    assert sum(b.impostor_hits for b in impostor.bins) == 0
    assert all(b.actual_impostor_rate == 0.0 for b in impostor.bins if b.count > 0)


def _populated_bins(index: int, count: int, hits: int) -> tuple[CalibrationBin, ...]:
    """``n_bins`` bins with ``count``/``hits`` at ``index`` and nothing elsewhere."""

    return tuple(
        CalibrationBin(
            bin_index=i,
            lo=i / DEFAULT_N_BINS,
            hi=(i + 1) / DEFAULT_N_BINS,
            midpoint=(i + 0.5) / DEFAULT_N_BINS,
            count=(count if i == index else 0),
            impostor_hits=(hits if i == index else 0),
            actual_impostor_rate=(hits / count if i == index and count else None),
            mean_confidence=(
                (i + 0.5) / DEFAULT_N_BINS if i == index and count else None
            ),
        )
        for i in range(DEFAULT_N_BINS)
    )


def _report(
    *,
    pooled: tuple[CalibrationBin, ...],
    pooled_total: int,
    crew: CalibrationCurve,
    impostor: CalibrationCurve,
) -> AccusationCalibrationReport:
    """A report over ``pooled`` with the given role curves (validators run)."""

    return AccusationCalibrationReport(
        n_bins=DEFAULT_N_BINS,
        accusation_claim_bins=pooled,
        accusation_claim_total=pooled_total,
        accusation_claim_ece=None,
        accusation_claim_populated_bins=sum(1 for b in pooled if b.count > 0),
        accusation_claim_low_power=True,
        accusation_claim_crew_accuser=crew,
        accusation_claim_impostor_accuser=impostor,
        vote_ballot_bins=_EMPTY_BINS,
        vote_ballot_total=0,
        vote_ballot_ece=None,
        vote_ballot_populated_bins=0,
        vote_ballot_low_power=True,
        vote_ballot_guard_authored_excluded=0,
    )


def test_a_curve_total_that_no_bin_supports_is_rejected() -> None:
    """PLANTED: a scalar total must be the sum of the distribution beside it.

    Aggregate totals that merely add up are not enough — a report whose bins are
    all empty while the totals claim a sample is impossible, and used to pass.
    """

    with pytest.raises(ValidationError, match="counts must sum to the curve's total"):
        _report(
            pooled=_EMPTY_BINS,
            pooled_total=1,
            crew=_curve_with_total(_EMPTY_BINS, 1),
            impostor=_empty_curve(_EMPTY_BINS),
        )


def test_a_split_that_sums_in_aggregate_but_not_per_bin_is_rejected() -> None:
    """PLANTED: the partition is asserted BIN BY BIN, not just on the totals.

    A crew curve holding its one accusation in a different bin from the pooled
    curve adds up correctly in aggregate and is still not a partition.
    """

    pooled = _populated_bins(9, 1, 1)
    misplaced = _populated_bins(2, 1, 1)
    with pytest.raises(ValidationError, match="bin by bin"):
        _report(
            pooled=pooled,
            pooled_total=1,
            crew=_curve_with_total(misplaced, 1),
            impostor=_empty_curve(_EMPTY_BINS),
        )

    # ...and the HITS half of the same rule: right bin, wrong hit count.
    with pytest.raises(ValidationError, match="bin by bin"):
        _report(
            pooled=pooled,
            pooled_total=1,
            crew=_curve_with_total(_populated_bins(9, 1, 0), 1),
            impostor=_empty_curve(_EMPTY_BINS),
        )

    # The well-formed version of the same report is accepted, so the rule is
    # rejecting the defect rather than the shape.
    accepted = _report(
        pooled=pooled,
        pooled_total=1,
        crew=_curve_with_total(pooled, 1),
        impostor=_empty_curve(_EMPTY_BINS),
    )
    assert accepted.accusation_claim_total == 1


def test_a_self_accusation_by_an_impostor_does_score_as_a_hit() -> None:
    """PLANTED: the impostor curve's zero is not an arithmetic impossibility.

    A hit is ``roles[against] == "IMPOSTOR"``, and the teammate firewall drops
    only OTHER impostors, so an impostor accusing THEMSELVES is both recordable
    and scoring — a prior baseline's prompts produced a few
    (``tests/eval/test_validity.py::
    test_betrayal_ignores_impostor_self_accusation_and_self_vote``). This pins
    that the committed 0-hit reading is a fact about the corpus on that channel
    rather than a property of the instrument, so the docstrings may not call the
    whole ceiling structural.

    Self-accusations stay IN both conditioned curves: filtering them would break
    the partition and move the pooled cells.
    """

    roles: Mapping[PlayerId, Role] = {"p-0": "CREWMATE", "p-3": "IMPOSTOR"}
    transcript = MeetingTranscript(
        turns=(
            MeetingTurn(
                turn_id="m-0:turn-0",
                turn_index=0,
                speaker="p-3",
                turn_kind="opening",
                reply_to=None,
                observations=(),
                claims=(_acc("p-3", 0.95),),
                free_text="",
            ),
        ),
    )
    meeting = MeetingReport(
        meeting_id="m-0",
        tick=10,
        triggered_by="p-0",
        trigger="report",
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=transcript,
        ballots=(),
        contradictions=(),
        llm_calls=(),
    )
    result = compute_accusation_calibration(
        _tournament(_game(game_id="g", roles=roles, meetings=(meeting,)))
    )

    impostor = result.accusation_claim_impostor_accuser
    assert impostor.total == 1
    assert result.accusation_claim_crew_accuser.total == 0
    # The hit the committed corpus never produced.
    assert sum(b.impostor_hits for b in impostor.bins) == 1
    assert impostor.bins[9].impostor_hits == 1
    # ...and the partition still holds with it in.
    assert (
        result.accusation_claim_crew_accuser.total + impostor.total
        == result.accusation_claim_total
        == 1
    )


def test_the_4p1i_impostor_curves_are_honestly_low_power() -> None:
    """Four populated bins under the five-bin power bar is signal, not a bug.

    A single-impostor roster gives the impostor accuser few lawful confidences
    to spread, so the conditioned curve legitimately flags. The 9p2i curves,
    with two impostors accusing, do not.
    """

    for sample_dir in ("replays/samples/4p1i", "replays/ml_corpus/4p1i"):
        curve = _committed_calibration(sample_dir).accusation_claim_impostor_accuser
        assert curve.populated_bins == 4
        assert curve.populated_bins < MIN_POPULATED_BINS_FOR_POWER
        assert curve.low_power is True
    for sample_dir in ("replays/samples/9p2i", "replays/ml_corpus/9p2i"):
        curve = _committed_calibration(sample_dir).accusation_claim_impostor_accuser
        assert curve.low_power is False


def test_the_split_is_a_partition_on_constructed_data() -> None:
    """SYNTHETIC: moving one accusation between speakers moves exactly one curve.

    Pinned on hand-built data as well as the corpus, so the conditioning is a
    property of the code rather than of the committed bytes.
    """

    roles: Mapping[PlayerId, Role] = {
        "p-0": "CREWMATE",
        "p-1": "CREWMATE",
        "p-2": "IMPOSTOR",
        "p-3": "IMPOSTOR",
    }

    def report(second_speaker: str) -> TournamentReport:
        transcript = MeetingTranscript(
            turns=(
                MeetingTurn(
                    turn_id="m-0:turn-0",
                    turn_index=0,
                    speaker="p-0",
                    turn_kind="opening",
                    reply_to=None,
                    observations=(),
                    claims=(_acc("p-2", 0.85),),
                    free_text="",
                ),
                MeetingTurn(
                    turn_id="m-0:turn-1",
                    turn_index=1,
                    speaker=second_speaker,
                    turn_kind="reply",
                    reply_to=None,
                    observations=(),
                    claims=(_acc("p-1", 0.45),),
                    free_text="",
                ),
            ),
        )
        meeting = MeetingReport(
            meeting_id="m-0",
            tick=10,
            triggered_by="p-0",
            trigger="report",
            outcome="SKIPPED",
            ejected_player_id=None,
            transcript=transcript,
            ballots=(),
            contradictions=(),
            llm_calls=(),
        )
        return _tournament(_game(game_id="g", roles=roles, meetings=(meeting,)))

    crew_authored = compute_accusation_calibration(report("p-0"))
    impostor_authored = compute_accusation_calibration(report("p-3"))

    for result in (crew_authored, impostor_authored):
        assert result.accusation_claim_total == 2
        assert (
            result.accusation_claim_crew_accuser.total
            + result.accusation_claim_impostor_accuser.total
            == result.accusation_claim_total
        )

    # The pooled curve cannot tell the two apart; the split does, and exactly
    # one sample crosses.
    assert crew_authored.accusation_claim_ece == impostor_authored.accusation_claim_ece
    assert crew_authored.accusation_claim_crew_accuser.total == 2
    assert crew_authored.accusation_claim_impostor_accuser.total == 0
    assert impostor_authored.accusation_claim_crew_accuser.total == 1
    assert impostor_authored.accusation_claim_impostor_accuser.total == 1
    # The 0.85 accusation stayed with the crew speaker; only the 0.45 one moved.
    assert impostor_authored.accusation_claim_crew_accuser.bins[8].count == 1
    assert impostor_authored.accusation_claim_impostor_accuser.bins[4].count == 1


def test_a_guard_redirected_ballot_is_excluded_from_the_vote_curve() -> None:
    """PLANTED: a guard-authored ballot leaves the curve and is counted.

    The redirect rewrites the TARGET while preserving the voter's confidence in
    the target they authored, so the recorded pair is not one agent's act. The
    exclusion is by predicate over the marker constant, so the marker's wording
    can change without the predicate going quietly blind.
    """

    marker = BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3")
    authored = _ballot("p-3", 0.9, voter="p-0")
    redirected = authored.model_copy(
        update={
            "target": "p-1",
            "rationale_text": marker + "p-3 vented. Vote p-3.",
        }
    )

    clean = _tournament(
        _game(game_id="g", roles=_ROLES, meetings=(_meeting(ballots=(authored,)),))
    )
    planted = _tournament(
        _game(game_id="g", roles=_ROLES, meetings=(_meeting(ballots=(redirected,)),))
    )

    clean_result = compute_accusation_calibration(clean)
    planted_result = compute_accusation_calibration(planted)

    assert clean_result.vote_ballot_total == 1
    assert clean_result.vote_ballot_guard_authored_excluded == 0
    # The redirected ballot is dropped, not binned as a 0.9-confidence miss.
    assert planted_result.vote_ballot_total == 0
    assert planted_result.vote_ballot_guard_authored_excluded == 1
    assert planted_result.vote_ballot_ece is None


def test_a_marked_skip_ballot_is_not_counted_as_a_guard_drop() -> None:
    """PLANTED: the published count is the DROP, not the marker census.

    A marked ballot whose recorded target is already ``"SKIP"`` was never
    binnable, so counting it would publish a number that cannot be reconciled
    against ``vote_ballot_total`` — the exact defect this pins shut.
    """

    marked_skip = _ballot("SKIP", 0.4, voter="p-0").model_copy(
        update={
            "rationale_text": (
                TEAMMATE_VOTE_TARGET_MARKER.format(target="p-3") + "no confident read"
            )
        }
    )
    marked_eject = _ballot("p-3", 0.9, voter="p-1").model_copy(
        update={
            "target": "p-1",
            "rationale_text": (
                BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3") + "p-3 vented."
            ),
        }
    )
    clean = _ballot("p-3", 0.8, voter="p-2")

    result = compute_accusation_calibration(
        _tournament(
            _game(
                game_id="g",
                roles=_ROLES,
                meetings=(_meeting(ballots=(marked_skip, marked_eject, clean)),),
            )
        )
    )

    # Three ballots carry a marker or a SKIP; only ONE was dropped BY the guard
    # rule, because the marked SKIP was never binnable in the first place.
    assert result.vote_ballot_guard_authored_excluded == 1
    assert result.vote_ballot_total == 1


def test_the_committed_guard_drop_reconciles_against_the_vote_curve() -> None:
    """The published drop equals the curve's own shortfall, per set.

    Recomputes both sides from the committed bytes: the binnable population
    ignoring the guard rule, minus the curve's total, must equal the published
    count. A census that over-counted marked SKIPs would fail here.
    """

    for sample_dir in sorted(_COMMITTED_SPLIT):
        served = _committed_calibration(sample_dir)
        raw = json.loads(
            (_REPO_ROOT / sample_dir / "tournament-eval-report.json").read_text(
                encoding="utf-8"
            )
        )
        non_skip = sum(
            1
            for game in raw["report"]["games"]
            for meeting in game["meetings"]
            for ballot in meeting["ballots"]
            if ballot["target"] != "SKIP"
        )
        assert (
            non_skip - served.vote_ballot_total
            == served.vote_ballot_guard_authored_excluded
        ), sample_dir
        assert served.vote_ballot_guard_authored_excluded > 0, sample_dir


def test_marker_shaped_prose_the_model_wrote_is_not_treated_as_a_guard_marker() -> None:
    """The predicate is anchored and repr-aware, so a quoted marker mid-body misses.

    Without the anchor a voter who quotes the marker in their own rationale would
    be silently dropped from the curve — the mirror-image failure of missing a
    real one.
    """

    quoting = _ballot("p-3", 0.9, voter="p-0").model_copy(
        update={
            "rationale_text": (
                "I saw the log say "
                + BALLOT_TARGET_REDIRECT_MARKER.format(target="p-1")
                + "so I distrust the tally."
            )
        }
    )
    result = compute_accusation_calibration(
        _tournament(
            _game(game_id="g", roles=_ROLES, meetings=(_meeting(ballots=(quoting,)),))
        )
    )
    assert result.vote_ballot_total == 1
    assert result.vote_ballot_guard_authored_excluded == 0
