"""Pins + cross-pins for ``eval/deduction_metrics.py`` (Task 19.14).

audits/audit-phase-19-triage.md §7 item 15 [S-Codex / S-Claude convergent
objective; §8 rows 3, 10, 14] plus the item-24 disclosure twin Task 19.8 landed
in ``replays/ml_corpus/README.md``. The module is a pure fold over an assembled
report, so its cells are pinnable against the committed bytes — and the
committed bytes are the PRIMARY pin here: every headline assertion reads the
``deduction`` block off the four committed ``tournament-eval-report.json``
views, then a recompute proves the block is not stale.

What is pinned, and why each pin exists:

1. **The headline cross-tab under BOTH partitions, separately.** The triage's
   independent 9p recount is reproduced to the digit twice — once by MEETING
   flag (70 flagged -> 68 imp / 2 inn; 95 unflagged -> 10 / 21; unflagged
   accuracy 10/31) and once by EJECTEE-specific proof (68 proof-present of 101;
   non-direct accuracy 10/33). A dedicated test asserts the two partitions
   DISAGREE on their splits while agreeing on the ejection total — the
   define-before-counting (C5) lesson made executable, so a future refactor
   cannot quietly collapse them into one number.
2. **The corpus twins** beside them (35/89 = 39.3% non-direct).
3. **The 19.11 cross-pin.** The eval-side taxonomy is an independent
   re-implementation of ``api.schemas.classify_evidence``; here the two are run
   over the same committed flags and must agree flag-by-flag AND on the exact
   per-category counts ``tests/api/test_evidence_taxonomy.py`` pins.
4. **Verify-then-fix cells.** The triage labelled the roll-call split and the
   "13 engine-redirected under-gate ejects" source-specific and NOT
   independently re-run. Both are recomputed here and the RECOUNT is the pin,
   with the roll-call figure pinned under both estimators (pooled and
   macro-average) because the source figure and Task 19.8's recount are the same
   bytes read two ways.
5. **The witnessed-supply adoption**, against the kill-craft pins at
   ``tests/eval/test_kill_craft.py:66-135`` — asserted as literals AND once
   through a live ``compute_kill_craft_report`` walk, so the adoption path
   itself is exercised rather than assumed.
6. **The definitions** — SKIP tolerance, fail-loud classification, the
   None-not-0.0 sentinel, and the validators that forbid a cell from carrying
   counts other than its own block's.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final

import pytest
from pydantic import ValidationError

from api.schemas import classify_evidence
from engine.entities import Role
from eval.deduction_metrics import (
    MACHINERY_DECIMAL_PATTERN,
    SELF_KILL_PHRASES,
    DeductionMetricsReport,
    UnclassifiableFlagError,
    WilsonRateCell,
    _authored_target,
    _is_omniscient,
    classify_flag,
    compute_deduction_metrics,
    witnessed_supply_from_kill_craft,
)
from eval.kill_craft import compute_kill_craft_report
from eval.meeting_quality import TournamentEvalReport, compute_ballot_target_redirects
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_REASON_ID_MARKER,
    TEAMMATE_COERCED_VOTE_RATIONALE,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
)
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import is_weak_contradiction
from orchestrator.replay import LLMCallRecord

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_SAMPLES_4P1I: Final[Path] = _REPO_ROOT / "replays" / "samples" / "4p1i"
_SAMPLES_9P2I: Final[Path] = _REPO_ROOT / "replays" / "samples" / "9p2i"
_CORPUS_4P1I: Final[Path] = _REPO_ROOT / "replays" / "ml_corpus" / "4p1i"
_CORPUS_9P2I: Final[Path] = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"


def _committed(sample_dir: Path) -> TournamentEvalReport:
    return TournamentEvalReport.model_validate_json(
        (sample_dir / "tournament-eval-report.json").read_text(encoding="utf-8")
    )


# --------------------------------------------------------------------------- #
# Module-scoped fixtures — each committed report parsed ONCE.                   #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def samples_9p2i() -> TournamentEvalReport:
    return _committed(_SAMPLES_9P2I)


@pytest.fixture(scope="module")
def samples_4p1i() -> TournamentEvalReport:
    return _committed(_SAMPLES_4P1I)


@pytest.fixture(scope="module")
def corpus_9p2i() -> TournamentEvalReport:
    return _committed(_CORPUS_9P2I)


@pytest.fixture(scope="module")
def corpus_4p1i() -> TournamentEvalReport:
    return _committed(_CORPUS_4P1I)


# --------------------------------------------------------------------------- #
# 1. THE HEADLINE — the cross-tab under BOTH partitions, pinned separately.     #
# --------------------------------------------------------------------------- #


def test_samples_9p2i_meeting_flag_partition(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Partition A reproduces the triage's independent 9p recount to the digit.

    §8 row 3: "165 meetings, flagged 70 -> 68 imp/2 inn; unflagged 95 -> 10/21",
    unflagged-meeting accuracy 10/31 = 32.3%. The unit here is the MEETING.
    """

    cross_tab = samples_9p2i.deduction.meeting_flag_cross_tab
    assert cross_tab.meetings_total == 165
    assert cross_tab.flagged_meetings == 70
    assert cross_tab.unflagged_meetings == 95
    assert cross_tab.flagged_ejections_impostor == 68
    assert cross_tab.flagged_ejections_innocent == 2
    assert cross_tab.unflagged_ejections_impostor == 10
    assert cross_tab.unflagged_ejections_innocent == 21
    accuracy = cross_tab.unflagged_meeting_accuracy
    assert (accuracy.numerator, accuracy.denominator) == (10, 31)
    assert accuracy.rate == pytest.approx(0.3225806451612903)


def test_samples_9p2i_ejectee_proof_partition(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Partition B reproduces the same recount's OTHER cut, with its own numbers.

    §2 consensus #1 / §8 row 3: 101 ejections, 68 carrying an ejectee-specific
    grounded ``vent_sighting``, non-direct accuracy 10/33 = 30.3%. The unit here
    is the EJECTION — a different denominator from partition A's, deliberately.
    """

    cross_tab = samples_9p2i.deduction.ejectee_proof_cross_tab
    assert cross_tab.ejections_total == 101
    assert cross_tab.proof_present_ejections == 68
    assert cross_tab.proof_present_impostor == 68
    assert cross_tab.proof_present_innocent == 0
    assert cross_tab.non_direct_ejections == 33
    accuracy = cross_tab.non_direct_accuracy
    assert (accuracy.numerator, accuracy.denominator) == (10, 33)
    assert accuracy.rate == pytest.approx(0.30303030303030304)
    # The audits' headline share: 68 of the 78 correct ejections rode proof.
    assert cross_tab.proof_present_impostor + cross_tab.non_direct_impostor == 78


def test_the_two_partitions_are_not_interchangeable(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """The C5 lesson, executable: same bytes, same total, DIFFERENT splits.

    The fourth Codex planning round caught the two denominators being blended
    into one sentence. This test is the guard against the same blend in code:
    both partitions span every ejection, and their "evidence present" buckets
    differ (70 ejections in flagged meetings vs 68 with ejectee-specific proof),
    so any cell that divided one's numerator by the other's denominator would be
    wrong by construction.
    """

    deduction = samples_9p2i.deduction
    meeting_flag = deduction.meeting_flag_cross_tab
    ejectee_proof = deduction.ejectee_proof_cross_tab

    flagged_meeting_ejections = (
        meeting_flag.flagged_ejections_impostor
        + meeting_flag.flagged_ejections_innocent
    )
    unflagged_meeting_ejections = (
        meeting_flag.unflagged_ejections_impostor
        + meeting_flag.unflagged_ejections_innocent
    )
    assert (
        flagged_meeting_ejections + unflagged_meeting_ejections
        == ejectee_proof.ejections_total
        == deduction.ejections_total
        == 101
    )
    # The "evidence present" buckets are NOT the same set.
    assert flagged_meeting_ejections == 70
    assert ejectee_proof.proof_present_ejections == 68
    assert flagged_meeting_ejections != ejectee_proof.proof_present_ejections
    # ... and neither are the complements (31 vs 33), which is exactly why the
    # two accuracy cells carry different denominators.
    assert unflagged_meeting_ejections == 31
    assert ejectee_proof.non_direct_ejections == 33
    assert (
        meeting_flag.unflagged_meeting_accuracy.denominator
        != ejectee_proof.non_direct_accuracy.denominator
    )
    # Both partitions agree on the role totals they partition, though.
    assert (
        meeting_flag.flagged_ejections_impostor
        + meeting_flag.unflagged_ejections_impostor
        == ejectee_proof.proof_present_impostor + ejectee_proof.non_direct_impostor
    )


def test_corpus_9p2i_cross_tab_twins(corpus_9p2i: TournamentEvalReport) -> None:
    """The corpus twins of both partitions (§2 consensus #1: 213/248, 35/89)."""

    deduction = corpus_9p2i.deduction
    meeting_flag = deduction.meeting_flag_cross_tab
    ejectee_proof = deduction.ejectee_proof_cross_tab

    assert meeting_flag.meetings_total == 463
    assert meeting_flag.flagged_meetings == 219
    assert meeting_flag.unflagged_meetings == 244
    assert meeting_flag.flagged_ejections_impostor == 213
    assert meeting_flag.flagged_ejections_innocent == 3
    assert meeting_flag.unflagged_ejections_impostor == 35
    assert meeting_flag.unflagged_ejections_innocent == 51

    assert ejectee_proof.ejections_total == 302
    assert ejectee_proof.proof_present_ejections == 213
    assert ejectee_proof.proof_present_impostor == 213
    non_direct = ejectee_proof.non_direct_accuracy
    assert (non_direct.numerator, non_direct.denominator) == (35, 89)
    assert non_direct.rate == pytest.approx(0.39325842696629215)
    # 213 of the 248 correct corpus ejections rode ejectee-specific proof.
    assert (
        ejectee_proof.proof_present_impostor + ejectee_proof.non_direct_impostor == 248
    )


def test_4p_sets_cross_tab(
    samples_4p1i: TournamentEvalReport, corpus_4p1i: TournamentEvalReport
) -> None:
    """The 4p sets — the RECOUNT is the pin, correcting the triage's 4p sentence.

    §8 row 3's 4p clause reads "13 total ejections: 12 in flagged meetings and
    one in a flagless meeting; 26/27 flagless meetings skipped". The committed
    ``replays/samples/4p1i`` bytes (byte-identical to the triage's tree — no
    replay JSONL moved in Phase 19) carry **12** ejections over 39 meetings, and
    neither partition yields 13: partition A splits 10 / 2 over 10 vent-flagged
    and 29 unflagged meetings, while an ANY-flag reading gives 12 / 0 over 13
    flagged and 26 flagless. The row's 9p claims — the ones the triage DID
    independently re-run — reproduce exactly (above); this one is a source
    miscount, corrected here.
    """

    samples = samples_4p1i.deduction
    assert samples.meetings_total == 39
    assert samples.ejections_total == 12
    meeting_flag = samples.meeting_flag_cross_tab
    assert meeting_flag.flagged_meetings == 10
    assert meeting_flag.unflagged_meetings == 29
    assert meeting_flag.flagged_ejections_impostor == 9
    assert meeting_flag.flagged_ejections_innocent == 1
    assert meeting_flag.unflagged_ejections_impostor == 1
    assert meeting_flag.unflagged_ejections_innocent == 1
    # The ANY-flag reading the triage may have meant: 13 flagged meetings, all
    # 12 ejections inside them, 26 flagless meetings — still not 13 ejections.
    assert samples.evidence_taxonomy.meetings_with_any_flag == 13
    ejectee_proof = samples.ejectee_proof_cross_tab
    assert ejectee_proof.proof_present_ejections == 9
    assert ejectee_proof.non_direct_ejections == 3
    assert ejectee_proof.non_direct_accuracy.numerator == 1
    # 9 of the 10 correct ejections involved vent proof (the row's one 4p clause
    # that DOES reproduce).
    assert ejectee_proof.proof_present_impostor == 9
    assert (
        ejectee_proof.proof_present_impostor + ejectee_proof.non_direct_impostor == 10
    )

    corpus = corpus_4p1i.deduction
    assert corpus.meetings_total == 40
    assert corpus.ejections_total == 20
    assert corpus.ejectee_proof_cross_tab.proof_present_ejections == 20
    # Empty denominators are the None sentinel, never 0.0.
    assert corpus.ejectee_proof_cross_tab.non_direct_accuracy.denominator == 0
    assert corpus.ejectee_proof_cross_tab.non_direct_accuracy.rate is None
    assert corpus.meeting_flag_cross_tab.unflagged_meeting_accuracy.rate is None


# --------------------------------------------------------------------------- #
# 2. The committed block is not stale: a recompute reproduces it.               #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "sample_dir",
    [_SAMPLES_4P1I, _SAMPLES_9P2I, _CORPUS_4P1I, _CORPUS_9P2I],
    ids=["samples-4p1i", "samples-9p2i", "corpus-4p1i", "corpus-9p2i"],
)
def test_committed_block_matches_a_fresh_fold(sample_dir: Path) -> None:
    """Every committed ``deduction`` block re-derives from its own inner report.

    The one exception is ``witnessed_supply``, which is ADOPTED from the
    kill-craft engine walk rather than derived from the report — so a
    report-only recompute leaves it ``None`` by design, and the committed block
    must carry it. Both halves are asserted.
    """

    committed = _committed(sample_dir)
    recomputed = compute_deduction_metrics(committed.report)

    assert recomputed.witnessed_supply is None
    assert committed.deduction.witnessed_supply is not None
    assert (
        recomputed.model_dump()
        == committed.deduction.model_copy(
            update={"witnessed_supply": None}
        ).model_dump()
    )


def test_the_fold_is_deterministic(samples_9p2i: TournamentEvalReport) -> None:
    """Two folds over the same bytes are byte-identical (no float-order hazard)."""

    first = compute_deduction_metrics(samples_9p2i.report)
    second = compute_deduction_metrics(samples_9p2i.report)
    assert first.model_dump_json() == second.model_dump_json()


def test_accepts_a_bare_game_sequence(samples_4p1i: TournamentEvalReport) -> None:
    """The analyzer signature every sibling uses: report OR bare game sequence."""

    from_report = compute_deduction_metrics(samples_4p1i.report)
    from_games = compute_deduction_metrics(samples_4p1i.report.games)
    assert from_report.model_dump() == from_games.model_dump()


# --------------------------------------------------------------------------- #
# 3. The 19.11 cross-pin: two independent derivations, identical counts.        #
# --------------------------------------------------------------------------- #

# The exact per-category counts ``tests/api/test_evidence_taxonomy.py`` pins for
# the DTO-side derivation. Reproducing them from the eval-side twin IS the
# cross-pin the contract asks for; a diff on either side is a loud failure in
# both suites.
_EXPECTED_CATEGORY_COUNTS: Final[dict[str, tuple[int, int, int]]] = {
    # set -> (role_proof, cross_statement, weak_signal)
    "samples/9p2i": (96, 64, 26),
    "samples/4p1i": (11, 2, 3),
    "ml_corpus/9p2i": (313, 204, 90),
    "ml_corpus/4p1i": (20, 1, 0),
}


@pytest.mark.parametrize(
    ("set_name", "sample_dir"),
    [
        ("samples/4p1i", _SAMPLES_4P1I),
        ("samples/9p2i", _SAMPLES_9P2I),
        ("ml_corpus/4p1i", _CORPUS_4P1I),
        ("ml_corpus/9p2i", _CORPUS_9P2I),
    ],
)
def test_taxonomy_counts_match_the_dto_taxonomy(
    set_name: str, sample_dir: Path
) -> None:
    """The eval-side census equals Task 19.11's DTO taxonomy on the same bytes."""

    census = _committed(sample_dir).deduction.evidence_taxonomy
    role_proof, cross_statement, weak_signal = _EXPECTED_CATEGORY_COUNTS[set_name]
    assert census.role_proof_flags == role_proof
    assert census.cross_statement_flags == cross_statement
    assert census.weak_signal_flags == weak_signal
    assert census.flags_total == role_proof + cross_statement + weak_signal


def test_every_committed_flag_classifies_identically_on_both_surfaces(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """Flag-by-flag agreement, not just aggregate agreement.

    Equal totals could in principle hide two compensating disagreements, so the
    cross-pin is asserted per flag. ``api.schemas.classify_evidence`` takes
    primitives and the eval twin takes the recorded model; both are driven off
    the same ``ContradictionRef``.
    """

    checked = 0
    for report in (samples_9p2i, corpus_9p2i):
        for game in report.report.games:
            for meeting in game.meetings:
                for flag in meeting.contradictions:
                    checked += 1
                    assert classify_flag(flag) == classify_evidence(
                        kind=flag.kind,
                        event_a_id=flag.event_a_id,
                        event_b_id=flag.event_b_id,
                        weak=is_weak_contradiction(flag),
                    )
    assert checked == 186 + 607  # samples-9p2i + corpus-9p2i flag totals


def test_unclassifiable_kind_raises_rather_than_bucketing() -> None:
    """A kind with no rule is a finding to record, not a bucket to widen."""

    flag = ContradictionRef.model_construct(
        contradiction_id="c-1",
        kind="brand_new_detector_kind",
        event_a_id="a",
        event_b_id="b",
        subjects=("p-1",),
        description="",
    )
    with pytest.raises(UnclassifiableFlagError, match="unclassifiable flag"):
        classify_flag(flag)


def test_kind_check_gates_the_weak_rule() -> None:
    """An unknown kind carrying a weak stamp still raises (rule order matters)."""

    flag = ContradictionRef.model_construct(
        contradiction_id="c-2",
        kind="brand_new_detector_kind",
        event_a_id="a",
        event_b_id="b",
        subjects=("p-1",),
        description="[weak signal: narrow window] …",
    )
    assert is_weak_contradiction(flag)
    with pytest.raises(UnclassifiableFlagError):
        classify_flag(flag)


# --------------------------------------------------------------------------- #
# 4. Verify-then-fix: the two source-specific cells, recomputed.                #
# --------------------------------------------------------------------------- #


def test_roll_call_coverage_split_under_both_estimators(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """VERIFY-THEN-FIX for the §7 item-24 roll-call split (source-specific).

    The triage carried impostor coverage as ~45.5-46.5%. The recount: that
    figure is the unweighted per-meeting MACRO-AVERAGE (45.45% / 46.54%), while
    the pooled turn-level share is 49.0% / 50.0%. Both ship as separately named
    cells, matching Task 19.8's disclosure
    (``replays/ml_corpus/README.md`` item 8) byte for byte.
    """

    samples = samples_9p2i.deduction.public_response_coverage
    assert (samples.crew_turns_with_whereabouts, samples.crew_turns) == (723, 726)
    assert (samples.impostor_turns_with_whereabouts, samples.impostor_turns) == (
        120,
        245,
    )
    assert samples.crew_pooled_coverage == pytest.approx(0.9958677685950413)
    assert samples.impostor_pooled_coverage == pytest.approx(0.4897959183673469)
    # The triage's "45.5%" reproduces exactly — as the macro-average.
    assert samples.impostor_macro_average_coverage == pytest.approx(0.45454545454545453)
    assert samples.crew_macro_average_coverage == pytest.approx(0.9957575757575758)

    corpus = corpus_9p2i.deduction.public_response_coverage
    assert (corpus.crew_turns_with_whereabouts, corpus.crew_turns) == (2035, 2042)
    assert (corpus.impostor_turns_with_whereabouts, corpus.impostor_turns) == (342, 684)
    assert corpus.impostor_pooled_coverage == pytest.approx(0.5)
    # The triage's "46.5%" reproduces exactly — as the macro-average.
    assert corpus.impostor_macro_average_coverage == pytest.approx(0.4654427645788337)
    # The two estimators genuinely differ; publishing one alone is the drift.
    assert corpus.impostor_pooled_coverage != corpus.impostor_macro_average_coverage


def test_roll_call_coverage_4p_sets(
    samples_4p1i: TournamentEvalReport, corpus_4p1i: TournamentEvalReport
) -> None:
    """The 4p disclosure twins (crew 78/78 and 79/80 vs impostor 8/39 and 5/40)."""

    samples = samples_4p1i.deduction.public_response_coverage
    assert (samples.crew_turns_with_whereabouts, samples.crew_turns) == (78, 78)
    assert (samples.impostor_turns_with_whereabouts, samples.impostor_turns) == (8, 39)
    corpus = corpus_4p1i.deduction.public_response_coverage
    assert (corpus.crew_turns_with_whereabouts, corpus.crew_turns) == (79, 80)
    assert (corpus.impostor_turns_with_whereabouts, corpus.impostor_turns) == (5, 40)


def test_thirteen_engine_redirected_ejects_reproduces(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """VERIFY-THEN-FIX for §8 row 18's "13 engine-redirected under-gate ejects".

    The triage listed it UNVERIFIED-CHEAPLY. Recount over the committed bytes:
    exactly 13 redirect-marked ballots on ``replays/samples/9p2i``, all 13
    recorded as ejects, none coerced to SKIP. The source claim reproduces, and
    the recount is now the pin.
    """

    redirects = samples_9p2i.deduction.redirected_ballots
    assert redirects.redirected_ballots == 13
    assert redirects.redirected_eject_ballots == 13
    assert redirects.redirect_coerced_skip_ballots == 0
    assert redirects.ballots_total == 971
    assert redirects.redirected_ballot_share == pytest.approx(13 / 971)


@pytest.mark.parametrize(
    "sample_dir",
    [_SAMPLES_4P1I, _SAMPLES_9P2I, _CORPUS_4P1I, _CORPUS_9P2I],
    ids=["samples-4p1i", "samples-9p2i", "corpus-4p1i", "corpus-9p2i"],
)
def test_redirect_census_cross_pins_the_owning_analyzer(sample_dir: Path) -> None:
    """The redirect counts equal ``compute_ballot_target_redirects``' on the bytes.

    The deduction module matches the marker itself (it publishes a SHARE, which
    that analyzer does not carry), so the two are cross-pinned rather than one
    wrapping the other — the same discipline the 19.11 taxonomy cross-pin uses.
    """

    committed = _committed(sample_dir)
    owning = compute_ballot_target_redirects(committed.report)
    ours = committed.deduction.redirected_ballots
    assert ours.redirected_ballots == owning.redirected_ballots
    assert ours.redirected_eject_ballots == owning.redirected_eject_ballots
    assert ours.redirect_coerced_skip_ballots == owning.redirect_coerced_skip_ballots


# --------------------------------------------------------------------------- #
# 5. Weak-flag-only conviction — the injustice class, on its own denominator.   #
# --------------------------------------------------------------------------- #


def test_weak_flag_only_conviction_lands_on_the_audit_exhibit(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """§8 row 14's seed-47 exhibit is the sample set's single weak-only conviction.

    "Seed 47: innocent p-8 ejected on flags all stamped ``[weak signal…]``". The
    metric is ejectee-scoped, so it is not merely counting meetings that happen
    to be weak-flagged — and on the committed bytes EVERY weak-flag-only
    conviction, in both 9p sets, ejected an innocent. The numerator is 1 and 3,
    so the cells carry the rare-event advisory: the interval, not the rate, is
    the honest read.
    """

    samples = samples_9p2i.deduction.weak_flag_conviction
    assert samples.flag_named_ejections == 90
    assert samples.weak_flag_only_convictions == 1
    assert samples.weak_flag_only_innocent == 1
    assert samples.weak_flag_only_impostor == 0
    assert samples.weak_flag_only_rate.advisory is True

    corpus = corpus_9p2i.deduction.weak_flag_conviction
    assert corpus.flag_named_ejections == 275
    assert corpus.weak_flag_only_convictions == 3
    assert corpus.weak_flag_only_innocent == 3
    assert corpus.weak_flag_only_impostor == 0
    assert corpus.weak_flag_only_rate.advisory is True


def test_seed_47_is_the_sample_weak_only_conviction(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Name the exhibit: the one weak-only conviction is seed 47's innocent p-8."""

    hits = [
        (game.seed, meeting.meeting_id, meeting.ejected_player_id)
        for game in samples_9p2i.report.games
        for meeting in game.meetings
        if meeting.outcome == "EJECTED"
        and (
            naming := [
                flag
                for flag in meeting.contradictions
                if meeting.ejected_player_id in flag.subjects
            ]
        )
        and all(classify_flag(flag) == "weak_signal" for flag in naming)
    ]
    assert hits == [(47, "headless-seed-47:meeting-2", "p-8")]


# --------------------------------------------------------------------------- #
# 6. Turn -> ballot consistency, including the SKIP-tolerance definition.       #
# --------------------------------------------------------------------------- #


def test_turn_ballot_consistency_pins(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """The committed consistency split, buckets partitioning the denominator."""

    samples = samples_9p2i.deduction.turn_ballot_consistency
    assert samples.accusations_total == 778
    assert samples.accusing_ballots == 777
    assert samples.consistent_ballots == 347
    assert samples.inconsistent_skip_ballots == 336
    assert samples.inconsistent_other_target_ballots == 91
    assert samples.inconsistent_invalid_target_ballots == 3
    assert samples.guard_rewritten_ballots_unwound == 16
    assert samples.consistency_rate == pytest.approx(347 / 777)

    corpus = corpus_9p2i.deduction.turn_ballot_consistency
    assert corpus.accusing_ballots == 2186
    assert corpus.consistent_ballots == 1003
    assert corpus.inconsistent_skip_ballots == 829
    assert corpus.inconsistent_other_target_ballots == 354
    assert corpus.inconsistent_invalid_target_ballots == 0
    assert corpus.guard_rewritten_ballots_unwound == 46


def test_consistency_is_scored_against_the_authored_target(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """SAME-AGENT means the agent's target, not the guard's (the unwind).

    Four deterministic guards rewrite ``VoteBallot.target`` and stamp the
    ORIGINAL into ``rationale_text``. Scoring the RECORDED target would charge
    the guard's redirect to the agent and double-count it against the redirect
    census, so the fold unwinds it first. This test re-scores the same bytes
    BOTH ways and asserts the two genuinely disagree — the unwind is not a
    no-op dressed up as rigour.
    """

    committed = samples_9p2i.deduction.turn_ballot_consistency
    naive_consistent = 0
    scored = 0
    for game in samples_9p2i.report.games:
        for meeting in game.meetings:
            votable = {ballot.voter for ballot in meeting.ballots}
            accused_by: dict[str, set[str]] = {}
            for turn in meeting.transcript.turns:
                for claim in turn.claims:
                    if isinstance(claim, AccusationClaim):
                        accused_by.setdefault(turn.speaker, set()).add(claim.against)
            for ballot in meeting.ballots:
                accused = accused_by.get(ballot.voter)
                if not accused or not accused & votable:
                    continue
                scored += 1
                if ballot.target in accused:
                    naive_consistent += 1

    assert scored == committed.accusing_ballots == 777
    # The recorded-target reading is the one the metric must NOT publish.
    assert naive_consistent == 340
    assert committed.consistent_ballots == 347
    assert committed.guard_rewritten_ballots_unwound == 16


def test_authored_target_recovers_the_pre_guard_ballot() -> None:
    """The unwind reads the marker's own ``{target!r}``, on a synthetic ballot."""

    redirected = VoteBallot(
        voter="p-1",
        target="p-4",
        confidence=0.7,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=BALLOT_TARGET_REDIRECT_MARKER.format(target="p-2")
        + "they lied about Reactor.",
    )
    assert _authored_target(redirected) == ("p-2", True)

    untouched = VoteBallot(
        voter="p-1",
        target="p-2",
        confidence=0.7,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text="they lied about Reactor.",
    )
    assert _authored_target(untouched) == ("p-2", False)


@pytest.mark.parametrize(
    "sample_dir",
    [_SAMPLES_4P1I, _SAMPLES_9P2I, _CORPUS_4P1I, _CORPUS_9P2I],
    ids=["samples-4p1i", "samples-9p2i", "corpus-4p1i", "corpus-9p2i"],
)
def test_skip_tolerance_clause_is_structural_not_load_bearing(
    sample_dir: Path,
) -> None:
    """No committed accusation names a non-votable player — pinned, not assumed.

    The SKIP-tolerance clause exists because the definition demands it (a SKIP
    after accusing a DEAD player is not an inconsistency). On these bytes it
    never fires, and publishing the zeros is what keeps that checkable instead
    of folklore.
    """

    consistency = _committed(sample_dir).deduction.turn_ballot_consistency
    assert consistency.accusations_of_non_votable_targets == 0
    assert consistency.excluded_no_votable_target_ballots == 0


_EMPTY_COST: Final[GameCostSummary] = GameCostSummary(
    total_cost_usd=0.0, total_input_tokens=0, total_output_tokens=0, by_model={}
)


def _turn(index: int, speaker: PlayerId, *, accuses: PlayerId | None) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "opt_in",
        reply_to=None,
        observations=(WhereaboutsClaim(type="whereabouts", tick=1, room="CAFETERIA"),),
        claims=(
            (
                AccusationClaim(
                    type="accusation", against=accuses, confidence=0.8, reason="r"
                ),
            )
            if accuses is not None
            else ()
        ),
        free_text="",
    )


def _ballot(voter: PlayerId, target: str) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.7,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text="",
    )


def _synthetic_report(
    *,
    turns: tuple[MeetingTurn, ...],
    ballots: tuple[VoteBallot, ...],
    roles: Mapping[PlayerId, Role],
) -> TournamentReport:
    meeting = MeetingReport(
        meeting_id="m",
        tick=5,
        triggered_by="p-1",
        trigger="report",
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=MeetingTranscript(turns=turns),
        ballots=ballots,
        contradictions=(),
        llm_calls=(),
    )
    game = GameReport(
        game_id="g-0",
        seed=0,
        winner="CREWMATES",
        reason="CREWMATE_TASKS",
        final_tick=10,
        roles=roles,
        replay_ref="replay-seed-0.jsonl",
        meetings=(meeting,),
        failed_calls=(),
        prompt_versions={},
        cost=_EMPTY_COST,
    )
    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION, games=(game,), seeds_used=(0,)
    )


def _report_with(
    meeting: MeetingReport, *, roles: Mapping[PlayerId, Role]
) -> TournamentReport:
    """One synthetic game carrying ``meeting`` — for the guard-origin fixtures."""

    game = GameReport(
        game_id="g-0",
        seed=0,
        winner="CREWMATES",
        reason="CREWMATE_TASKS",
        final_tick=10,
        roles=roles,
        replay_ref="replay-seed-0.jsonl",
        meetings=(meeting,),
        failed_calls=(),
        prompt_versions={},
        cost=_EMPTY_COST,
    )
    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION, games=(game,), seeds_used=(0,)
    )


def test_skip_after_accusing_a_votable_player_is_an_inconsistency() -> None:
    """The definition's positive case: the accused could be voted for."""

    report = _synthetic_report(
        turns=(_turn(0, "p-1", accuses="p-2"),),
        ballots=(_ballot("p-1", "SKIP"), _ballot("p-2", "SKIP")),
        roles={"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
    )
    consistency = compute_deduction_metrics(report).turn_ballot_consistency
    assert consistency.accusing_ballots == 1
    assert consistency.inconsistent_skip_ballots == 1
    assert consistency.consistent_ballots == 0
    assert consistency.excluded_no_votable_target_ballots == 0


def test_skip_after_accusing_only_a_non_votable_player_is_excluded() -> None:
    """The SKIP-tolerance clause: with no votable accused, SKIP is the only ballot.

    ``p-3`` never votes, so it is not in the meeting's votable set (the living
    roster read off the record). Accusing only ``p-3`` and then SKIPping is not
    an inconsistency — the pair leaves the denominator, visibly.
    """

    report = _synthetic_report(
        turns=(_turn(0, "p-1", accuses="p-3"),),
        ballots=(_ballot("p-1", "SKIP"), _ballot("p-2", "SKIP")),
        roles={"p-1": "CREWMATE", "p-2": "CREWMATE", "p-3": "IMPOSTOR"},
    )
    consistency = compute_deduction_metrics(report).turn_ballot_consistency
    assert consistency.accusing_ballots == 0
    assert consistency.inconsistent_skip_ballots == 0
    assert consistency.excluded_no_votable_target_ballots == 1
    assert consistency.accusations_of_non_votable_targets == 1
    assert consistency.consistency_rate is None


def test_voting_the_accused_is_consistent_and_another_target_is_not() -> None:
    """The two remaining buckets, on one synthetic meeting."""

    report = _synthetic_report(
        turns=(_turn(0, "p-1", accuses="p-2"), _turn(1, "p-2", accuses="p-1")),
        ballots=(_ballot("p-1", "p-2"), _ballot("p-2", "p-3"), _ballot("p-3", "SKIP")),
        roles={"p-1": "CREWMATE", "p-2": "IMPOSTOR", "p-3": "CREWMATE"},
    )
    consistency = compute_deduction_metrics(report).turn_ballot_consistency
    assert consistency.accusing_ballots == 2
    assert consistency.consistent_ballots == 1
    assert consistency.inconsistent_other_target_ballots == 1
    assert consistency.inconsistent_skip_ballots == 0


# --------------------------------------------------------------------------- #
# 7. Scaffold leakage, split by origin.                                        #
# --------------------------------------------------------------------------- #


def test_scaffold_leakage_reproduces_the_19_8_disclosure(
    samples_9p2i: TournamentEvalReport,
    corpus_9p2i: TournamentEvalReport,
    corpus_4p1i: TournamentEvalReport,
) -> None:
    """The MODEL-originated nets match ``replays/ml_corpus/README.md`` item 7.

    29/245 and 81/684 impostor-voter ballots name a partner, with a crew
    false-positive control of 0; 8, 14 and 2 ballots state the role outright;
    player-visible ``free_text`` carries exactly one leak, in the corpus.
    """

    samples = samples_9p2i.deduction.scaffold_leakage
    assert (samples.model_partner_naming_ballots, samples.impostor_ballots) == (29, 245)
    assert samples.model_role_statement_ballots == 8
    assert samples.crew_partner_naming_ballots == 0
    assert samples.player_visible_leak_turns == 0

    corpus = corpus_9p2i.deduction.scaffold_leakage
    assert (corpus.model_partner_naming_ballots, corpus.impostor_ballots) == (81, 684)
    assert corpus.model_role_statement_ballots == 14
    assert corpus.crew_partner_naming_ballots == 0
    assert corpus.player_visible_leak_turns == 1

    assert corpus_4p1i.deduction.scaffold_leakage.model_role_statement_ballots == 2


def test_self_kill_disclosure_is_counted(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """The THIRD omniscience net: a voter narrating their own kill.

    Task 19.15's contract names "omniscient teammate/self-kill rationale text",
    so a leakage metric that saw only partner naming and role statements was
    measuring two thirds of the class. The union is below the net sum because a
    ballot can hit several nets at once, and the crew control stays clean.
    """

    samples = samples_9p2i.deduction.scaffold_leakage
    assert samples.model_self_kill_disclosure_ballots == 9
    assert samples.model_omniscient_ballots == 42
    assert samples.crew_omniscient_control_ballots == 0

    corpus = corpus_9p2i.deduction.scaffold_leakage
    assert corpus.model_self_kill_disclosure_ballots == 22
    assert corpus.model_omniscient_ballots == 110
    assert corpus.crew_omniscient_control_ballots == 0
    # The union is a union, not a sum: overlapping nets are not double-counted.
    assert corpus.model_omniscient_ballots < (
        corpus.model_partner_naming_ballots
        + corpus.model_role_statement_ballots
        + corpus.model_self_kill_disclosure_ballots
    )


def test_model_cells_read_the_pre_guard_body_not_the_recorded_one(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """Model-originated nets read what the MODEL wrote, not what the record kept.

    Task 19.15's teammate coercion REPLACES ``rationale_text`` before the ballot
    is stored, so a future teammate-aimed ballot disclosing a partner would read
    clean on the recorded surface. The nets therefore read the pre-guard body
    parsed out of the voter's own vote-call response. On the committed bytes
    every ballot pairs with exactly one parsed response — the fallback is never
    taken — which is why the source change moved no number.
    """

    for report in (samples_9p2i, corpus_9p2i):
        leakage = report.deduction.scaffold_leakage
        assert leakage.model_source_recorded_fallback_ballots == 0
        assert leakage.model_source_pre_guard_ballots == leakage.ballots_total


def test_the_pre_guard_body_is_the_parsed_field_not_the_raw_envelope(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """The machinery net reads the parsed ``rationale_text``, never the JSON blob.

    The raw vote response carries ``"confidence": 0.NN``, which the
    quoted-decimal net would read as the model reproducing its own scoring grid.
    Scanning the envelope would report 850 machinery quotations on this set
    against the 39 real ones — so the extraction is load-bearing, not cosmetic.
    """

    envelope_hits = 0
    for game in samples_9p2i.report.games:
        for meeting in game.meetings:
            for call in meeting.llm_calls:
                if '"rationale_text"' in call.response_text and (
                    MACHINERY_DECIMAL_PATTERN.search(call.response_text)
                ):
                    envelope_hits += 1

    assert envelope_hits == 850
    assert (
        samples_9p2i.deduction.scaffold_leakage.model_machinery_quotation_ballots == 39
    )


def test_guard_preserved_omniscient_rate_has_its_own_denominator(
    corpus_9p2i: TournamentEvalReport,
) -> None:
    """The guard-side RATE is over target rewrites, not over all marked ballots.

    ``guard_marked_ballot_share`` answers a different question over a different
    denominator (55/2,726 here), so it cannot stand in for the stale-rationale
    rate the contract asks for: 1/53.
    """

    leakage = corpus_9p2i.deduction.scaffold_leakage
    rate = leakage.guard_preserved_omniscient_rate
    assert (rate.numerator, rate.denominator) == (1, 53)
    assert rate.advisory is True
    assert leakage.guard_marked_ballots == 55
    assert leakage.guard_marked_ballot_share == pytest.approx(55 / 2726)
    assert rate.rate != leakage.guard_marked_ballot_share


def test_guard_preserved_leak_reads_the_recorded_rationale() -> None:
    """ "Preserved" means what SURVIVED the guard, so the cell reads the RECORD.

    Task 19.15 REPLACES the model body on a teammate-coerced ballot. Scoring the
    pre-guard body here would report the redaction as a preservation of the very
    text it removes — the metric would show the fix as ineffective precisely
    when it worked. This fixture is a redacted future ballot: the model
    disclosed a partner, the guard removed it, and the cell must read 0.
    """

    redacted = MeetingReport(
        meeting_id="m",
        tick=5,
        triggered_by="p-1",
        trigger="report",
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=MeetingTranscript(turns=()),
        ballots=(
            VoteBallot(
                voter="p-1",
                target="SKIP",
                confidence=0.5,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text=(
                    TEAMMATE_VOTE_TARGET_MARKER.format(target="p-2")
                    + TEAMMATE_COERCED_VOTE_RATIONALE
                ),
            ),
        ),
        contradictions=(),
        llm_calls=(
            LLMCallRecord(
                call_kind="meeting",
                model="fake",
                prompt="",
                response_text=json.dumps(
                    {"rationale_text": "p-2 is my partner, I cannot vote them."}
                ),
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                agent_id="p-1",
            ),
        ),
    )
    report = _report_with(redacted, roles={"p-1": "IMPOSTOR", "p-2": "IMPOSTOR"})
    leakage = compute_deduction_metrics(report).scaffold_leakage

    # The guard rewrote the target and removed the disclosure: nothing preserved.
    assert leakage.guard_target_rewrite_ballots == 1
    assert leakage.guard_preserved_omniscient_ballots == 0
    # The MODEL still authored it, and that half is counted from the pre-guard
    # body — the two origins disagree here, which is the whole point.
    assert leakage.model_partner_naming_ballots == 1
    assert leakage.model_omniscient_ballots == 1


def test_guard_census_ignores_a_marker_quoted_in_the_model_body() -> None:
    """The guard census reads the LEADING chain, not a substring of the body.

    A model rationale quoting a marker literal would otherwise inflate
    ``guard_marked_ballots``, the rewrite denominator, AND the preserved-leak
    numerator for a ballot no guard ever touched.
    """

    spoofed = MeetingReport(
        meeting_id="m",
        tick=5,
        triggered_by="p-1",
        trigger="report",
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=MeetingTranscript(turns=()),
        ballots=(
            VoteBallot(
                voter="p-1",
                target="p-2",
                confidence=0.5,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text=(
                    "The system said "
                    + BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3")
                    + "about my partner."
                ),
            ),
        ),
        contradictions=(),
        llm_calls=(),
    )
    report = _report_with(spoofed, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    deduction = compute_deduction_metrics(report)

    assert deduction.scaffold_leakage.guard_marked_ballots == 0
    assert deduction.scaffold_leakage.guard_target_rewrite_ballots == 0
    assert deduction.scaffold_leakage.guard_preserved_omniscient_ballots == 0
    assert deduction.redirected_ballots.redirected_ballots == 0
    # The model DID author partner text, and that is still counted.
    assert deduction.scaffold_leakage.model_partner_naming_ballots == 1


def test_a_voter_cannot_lawfully_target_themselves() -> None:
    """A self-accusation names nobody the voter could vote for.

    ``meetings.manager._candidate_targets(living, exclude=voter)`` removes the
    voter, so a self-accusation must not enter the denominator and a self-target
    must not score consistent.
    """

    report = _synthetic_report(
        turns=(_turn(0, "p-1", accuses="p-1"),),
        ballots=(_ballot("p-1", "SKIP"), _ballot("p-2", "SKIP")),
        roles={"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
    )
    consistency = compute_deduction_metrics(report).turn_ballot_consistency
    assert consistency.accusing_ballots == 0
    assert consistency.excluded_no_votable_target_ballots == 1
    assert consistency.accusations_of_non_votable_targets == 1

    # And a self-TARGET is unlawful, not "some other player".
    self_voted = _synthetic_report(
        turns=(_turn(0, "p-1", accuses="p-2"),),
        ballots=(_ballot("p-1", "p-1"), _ballot("p-2", "SKIP")),
        roles={"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
    )
    cells = compute_deduction_metrics(self_voted).turn_ballot_consistency
    assert cells.accusing_ballots == 1
    assert cells.inconsistent_invalid_target_ballots == 1
    assert cells.inconsistent_other_target_ballots == 0
    assert cells.consistent_ballots == 0


def test_self_kill_net_is_first_person_only() -> None:
    """A third-person accusation is not a self-disclosure.

    ``"p-3 is the one who killed p-4"`` reveals nothing private; only the
    first-person forms do. Every entry in the net is explicitly first-person, so
    the accusation shape cannot inflate the rate on a future recording.
    """

    accusation = "p-3 is the one who killed p-4, so I vote them."
    assert not any(phrase in accusation.lower() for phrase in SELF_KILL_PHRASES)
    assert not _is_omniscient(accusation)

    disclosure = "They'll realize I'm the one who killed p-8, so I skip."
    assert any(phrase in disclosure.lower() for phrase in SELF_KILL_PHRASES)
    assert _is_omniscient(disclosure)


def test_authored_target_reads_the_earliest_applied_rewrite() -> None:
    """A stacked chain resolves to the MODEL's target, not a guard intermediate.

    Guards PREPEND, so the chain reads right-to-left in application order: a
    graph redirect followed by a citation coercion records
    ``[uncited 'p-4'] [under-gate 'p-2'] body``. The model authored ``p-2``;
    reading the leftmost marker would report the guard's own ``p-4``.
    """

    stacked = VoteBallot(
        voter="p-1",
        target="SKIP",
        confidence=0.5,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=(
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-4")
            + BALLOT_TARGET_REDIRECT_MARKER.format(target="p-2")
            + "they lied about Reactor."
        ),
    )
    assert _authored_target(stacked) == ("p-2", True)

    # A non-rewriting marker in the chain is consumed, not mistaken for one.
    with_citation_null = VoteBallot(
        voter="p-1",
        target="SKIP",
        confidence=0.5,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=(
            INVALID_REASON_ID_MARKER.format(reason_id="bogus-turn")
            + BALLOT_TARGET_REDIRECT_MARKER.format(target="p-2")
            + "body"
        ),
    )
    assert _authored_target(with_citation_null) == ("p-2", True)


def test_authored_target_ignores_a_marker_quoted_inside_the_body() -> None:
    """The chain walk is ANCHORED, so marker-shaped prose cannot spoof it.

    The manager guarantees "the ballot chain must only prepend audit markers";
    this parse holds it to that instead of trusting an unanchored substring.
    """

    spoofed = VoteBallot(
        voter="p-1",
        target="p-9",
        confidence=0.5,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=(
            "I think "
            + BALLOT_TARGET_REDIRECT_MARKER.format(target="p-2")
            + "is what the system would say."
        ),
    )
    assert _authored_target(spoofed) == ("p-9", False)


def test_machinery_quotation_reproduces_the_19_8_disclosure(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """The MACHINERY half of the model-originated class (contract: role/machinery).

    ``replays/ml_corpus/README.md`` item 7: a quoted internal decimal in 39/971
    (samples 9p2i) and 94/2,726 (corpus 9p2i) ballots — the unambiguous cell —
    beside the vocabulary net, which Task 19.8 labelled an upper bound and this
    module keeps labelled rather than promoting to a leak rate.
    """

    samples = samples_9p2i.deduction.scaffold_leakage
    assert samples.model_machinery_quotation_ballots == 39
    assert samples.model_machinery_quotation_share == pytest.approx(39 / 971)
    assert samples.model_machinery_vocabulary_ballots == 116

    corpus = corpus_9p2i.deduction.scaffold_leakage
    assert corpus.model_machinery_quotation_ballots == 94
    assert corpus.model_machinery_quotation_share == pytest.approx(94 / 2726)
    assert corpus.model_machinery_vocabulary_ballots == 297
    # The vocabulary net is strictly the looser reading of the same ballots.
    assert (
        corpus.model_machinery_vocabulary_ballots
        > corpus.model_machinery_quotation_ballots
    )


@pytest.mark.parametrize(
    ("set_name", "sample_dir", "expected"),
    [
        ("samples/4p1i", _SAMPLES_4P1I, 0),
        ("samples/9p2i", _SAMPLES_9P2I, 0),
        ("ml_corpus/4p1i", _CORPUS_4P1I, 0),
        ("ml_corpus/9p2i", _CORPUS_9P2I, 1),
    ],
)
def test_guard_originated_stale_rationales_are_rare_not_absent(
    set_name: str, sample_dir: Path, expected: int
) -> None:
    """Task 19.15's class measured, not asserted — and it is NOT zero everywhere.

    19.15 redacts the omniscient rationale a target-rewriting guard used to
    preserve, and labels the path "dormant for committed bytes". Measured, that
    label is *rare*, not *absent*: ``replays/ml_corpus/9p2i`` carries exactly one
    instance. This test exists because the metric read 0 everywhere until the
    self-kill net landed — a leakage predicate that saw only partner and role
    phrasing was blind to a voter narrating their own kill, which is the third
    shape 19.15's own contract names.
    """

    leakage = _committed(sample_dir).deduction.scaffold_leakage
    assert leakage.guard_preserved_omniscient_ballots == expected
    assert leakage.guard_target_rewrite_ballots <= leakage.guard_marked_ballots


def test_the_guard_preserved_instance_is_seed_1118(
    corpus_9p2i: TournamentEvalReport,
) -> None:
    """Name the exhibit: corpus seed 1118, meeting 0, a redirected impostor ballot.

    Its preserved rationale reads "… when I know I was killing p-3 …" — the
    guard rewrote the TARGET and left the self-kill disclosure in place, which
    is exactly the text Task 19.15 redacts going forward.
    """

    hits = [
        (game.seed, meeting.meeting_id, ballot.voter)
        for game in corpus_9p2i.report.games
        for meeting in game.meetings
        for ballot in meeting.ballots
        if BALLOT_TARGET_REDIRECT_MARKER.partition("{")[0] in ballot.rationale_text
        and "i was killing" in ballot.rationale_text.lower()
    ]
    assert hits == [(1118, "headless-seed-1118:meeting-0", "p-6")]


def test_guard_marker_counts(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """The guard-originated census, pinned beside the model-originated one."""

    samples = samples_9p2i.deduction.scaffold_leakage
    assert samples.guard_marked_ballots == 18
    assert samples.guard_target_rewrite_ballots == 17
    corpus = corpus_9p2i.deduction.scaffold_leakage
    assert corpus.guard_marked_ballots == 55
    assert corpus.guard_target_rewrite_ballots == 53


# --------------------------------------------------------------------------- #
# 8. The adopted witnessed / co-present evidence supply.                        #
# --------------------------------------------------------------------------- #


def test_witnessed_supply_adopts_the_kill_craft_pins(
    samples_9p2i: TournamentEvalReport,
    samples_4p1i: TournamentEvalReport,
    corpus_9p2i: TournamentEvalReport,
) -> None:
    """The committed supply cells ARE ``tests/eval/test_kill_craft.py:66-135``.

    Corpus 505 kills / 12 crew-witnessed, samples-9p2i 177 / 6, samples-4p1i
    61 / 1, and ``co_present_histogram == {0: N}`` on every set — the
    "too-clean evidence economy" structural finding, which lands here as
    ``co_present_crew_kills == 0``.
    """

    corpus = corpus_9p2i.deduction.witnessed_supply
    assert corpus is not None
    assert (corpus.kills_total, corpus.crew_witnessed_kills) == (505, 12)
    assert corpus.co_present_crew_kills == 0

    samples9 = samples_9p2i.deduction.witnessed_supply
    assert samples9 is not None
    assert (samples9.kills_total, samples9.crew_witnessed_kills) == (177, 6)
    assert samples9.co_present_crew_kills == 0
    assert samples9.crew_witnessed_kill_rate.rate == pytest.approx(6 / 177)

    samples4 = samples_4p1i.deduction.witnessed_supply
    assert samples4 is not None
    assert (samples4.kills_total, samples4.crew_witnessed_kills) == (61, 1)
    assert samples4.co_present_crew_kills == 0


def test_adoption_path_runs_against_a_live_kill_craft_walk(
    samples_4p1i: TournamentEvalReport,
) -> None:
    """The adoption is exercised, not assumed: one live fold on the smallest set.

    ``witnessed_supply_from_kill_craft`` never recomputes a kill-craft cell — it
    reads ``kills_total`` / ``crew_witnessed_kills`` verbatim and sums the
    ``co_present_histogram`` above bucket 0 — so a live walk must reproduce the
    committed block exactly.
    """

    kill_craft = compute_kill_craft_report(_SAMPLES_4P1I)
    adopted = witnessed_supply_from_kill_craft(kill_craft)
    assert adopted.kills_total == kill_craft.kills_total
    assert adopted.crew_witnessed_kills == kill_craft.crew_witnessed_kills
    assert adopted == samples_4p1i.deduction.witnessed_supply

    threaded = compute_deduction_metrics(
        samples_4p1i.report, kill_craft=kill_craft
    ).witnessed_supply
    assert threaded == adopted


def test_supply_is_none_not_zero_when_not_supplied(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """The "not supplied" sentinel is ``None`` — never a 0 that reads as "no kills"."""

    assert compute_deduction_metrics(samples_9p2i.report).witnessed_supply is None


# --------------------------------------------------------------------------- #
# 9. The model contract: sentinels, Wilson values, and the no-mixing validators.#
# --------------------------------------------------------------------------- #


def test_empty_report_yields_none_rates_not_zeroes() -> None:
    """Every rate over an empty denominator is ``None`` (the package convention)."""

    empty = TournamentReport(
        format_version=CURRENT_FORMAT_VERSION, games=(), seeds_used=()
    )
    result = compute_deduction_metrics(empty)
    assert result.games_total == 0
    assert result.evidence_taxonomy.weak_signal_share is None
    assert result.meeting_flag_cross_tab.unflagged_meeting_accuracy.rate is None
    assert result.ejectee_proof_cross_tab.non_direct_accuracy.rate is None
    assert result.turn_ballot_consistency.consistency_rate is None
    assert result.public_response_coverage.crew_pooled_coverage is None
    assert result.public_response_coverage.crew_macro_average_coverage is None
    assert result.redirected_ballots.redirected_ballot_share is None
    assert result.scaffold_leakage.guard_marked_ballot_share is None


def test_wilson_cell_rejects_a_hand_edited_interval(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """A cell whose interval contradicts its counts fails loud on load.

    The good cell is the committed 10/31 unflagged-accuracy cell round-tripped
    through JSON — never hand-typed bounds, which is the very drift the
    validator exists to catch.
    """

    good = samples_9p2i.deduction.meeting_flag_cross_tab.unflagged_meeting_accuracy
    assert (good.numerator, good.denominator) == (10, 31)
    assert WilsonRateCell.model_validate_json(good.model_dump_json()) == good

    tampered = good.model_dump()
    tampered["rate"] = 0.9
    with pytest.raises(ValidationError, match="must equal the Wilson values"):
        WilsonRateCell.model_validate(tampered)

    widened = good.model_dump()
    widened["wilson_high"] = 1.0
    with pytest.raises(ValidationError, match="must equal the Wilson values"):
        WilsonRateCell.model_validate(widened)


def test_wilson_cell_rejects_a_wrong_advisory_flag(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """``advisory`` is derived, so a hand-set flag cannot disagree with the count."""

    rare = samples_9p2i.deduction.weak_flag_conviction.weak_flag_only_rate
    assert rare.numerator == 1 and rare.advisory is True
    flipped = rare.model_dump()
    flipped["advisory"] = False
    with pytest.raises(ValidationError, match="advisory flag must equal"):
        WilsonRateCell.model_validate(flipped)


def test_a_cross_tab_cell_cannot_carry_another_blocks_counts(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """The no-mixing validator: the 10/33 cell cannot ride partition A's block.

    This is the C5 lesson enforced by the model rather than by prose. Swapping
    the ejectee-proof accuracy cell (10/33) into the meeting-flag block, whose
    unflagged denominator is 31, must raise.
    """

    payload = samples_9p2i.deduction.model_dump()
    payload["meeting_flag_cross_tab"]["unflagged_meeting_accuracy"] = payload[
        "ejectee_proof_cross_tab"
    ]["non_direct_accuracy"]
    with pytest.raises(ValidationError, match="must carry the block's own counts"):
        DeductionMetricsReport.model_validate(payload)


def test_report_rejects_a_partition_that_misses_an_ejection(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Both partitions must span every ejection — a dropped one fails loud."""

    payload = samples_9p2i.deduction.model_dump()
    payload["ejectee_proof_cross_tab"]["non_direct_ejections"] -= 1
    payload["ejectee_proof_cross_tab"]["non_direct_innocent"] -= 1
    payload["ejectee_proof_cross_tab"]["non_direct_accuracy"]["denominator"] -= 1
    with pytest.raises(ValidationError):
        DeductionMetricsReport.model_validate(payload)


def test_block_round_trips_through_json(samples_9p2i: TournamentEvalReport) -> None:
    """The block survives the serialization the committed report rides on."""

    block = samples_9p2i.deduction
    restored = DeductionMetricsReport.model_validate_json(block.model_dump_json())
    assert restored == block
    # And it is really on disk, not only in memory.
    committed = json.loads(
        (_SAMPLES_9P2I / "tournament-eval-report.json").read_text(encoding="utf-8")
    )
    assert (
        committed["deduction"]["ejectee_proof_cross_tab"]["proof_present_ejections"]
        == 68
    )
