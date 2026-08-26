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
   ``tests/eval/test_kill_craft.py`` — asserted as literals AND once against a
   live kill-craft walk of the committed 4p1i bytes (the shared
   ``committed_kill_craft_4p1i`` fixture), so the adoption path itself is
   exercised rather than assumed.
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
    _scan_marker_chain,
    _split_rationale,
    _wilson_interval,
    _is_omniscient,
    classify_flag,
    compute_deduction_metrics,
    witnessed_supply_from_kill_craft,
)
from eval.kill_craft import KillCraftReport
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
    INVALID_VOTE_TARGET_MARKER,
    TEAMMATE_COERCED_VOTE_RATIONALE,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
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
    assert cross_tab.meetings_total == 152  # was 165
    assert cross_tab.flagged_meetings == 69  # was 70
    assert cross_tab.unflagged_meetings == 83  # was 95
    assert cross_tab.flagged_ejections_impostor == 69  # was 68
    assert cross_tab.flagged_ejections_innocent == 0  # was 2
    assert cross_tab.unflagged_ejections_impostor == 16  # was 10
    assert cross_tab.unflagged_ejections_innocent == 14  # was 21
    accuracy = cross_tab.unflagged_meeting_accuracy
    assert (accuracy.numerator, accuracy.denominator) == (16, 30)
    assert accuracy.rate == pytest.approx(0.5333333333333333)  # was 0.3225806451612903


def test_samples_9p2i_ejectee_proof_partition(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Partition B reproduces the same recount's OTHER cut, with its own numbers.

    §2 consensus #1 / §8 row 3: 101 ejections, 68 carrying an ejectee-specific
    grounded ``vent_sighting``, non-direct accuracy 10/33 = 30.3%. The unit here
    is the EJECTION — a different denominator from partition A's, deliberately.
    """

    cross_tab = samples_9p2i.deduction.ejectee_proof_cross_tab
    assert cross_tab.ejections_total == 99  # was 101
    assert cross_tab.proof_present_ejections == 69  # was 68
    assert cross_tab.proof_present_impostor == 69  # was 68
    assert cross_tab.proof_present_innocent == 0
    assert cross_tab.non_direct_ejections == 30  # was 33
    accuracy = cross_tab.non_direct_accuracy
    assert (accuracy.numerator, accuracy.denominator) == (16, 30)
    assert accuracy.rate == pytest.approx(0.5333333333333333)  # was 0.30303030303030304
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

    assert meeting_flag.meetings_total == 432  # was 463
    assert meeting_flag.flagged_meetings == 212  # was 219
    assert meeting_flag.unflagged_meetings == 220  # was 244
    assert meeting_flag.flagged_ejections_impostor == 212  # was 213
    assert meeting_flag.flagged_ejections_innocent == 0  # was 3
    assert meeting_flag.unflagged_ejections_impostor == 42  # was 35
    assert meeting_flag.unflagged_ejections_innocent == 26  # was 51

    assert ejectee_proof.ejections_total == 280  # was 302
    assert ejectee_proof.proof_present_ejections == 212  # was 213
    assert ejectee_proof.proof_present_impostor == 212  # was 213
    non_direct = ejectee_proof.non_direct_accuracy
    assert (non_direct.numerator, non_direct.denominator) == (42, 68)
    assert non_direct.rate == pytest.approx(
        0.6176470588235294
    )  # was 0.39325842696629215
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
    assert samples.meetings_total == 40  # was 39
    assert samples.ejections_total == 21  # was 12
    meeting_flag = samples.meeting_flag_cross_tab
    assert meeting_flag.flagged_meetings == 19  # was 10
    assert meeting_flag.unflagged_meetings == 21  # was 29
    assert meeting_flag.flagged_ejections_impostor == 19  # was 9
    assert meeting_flag.flagged_ejections_innocent == 0  # was 1
    assert meeting_flag.unflagged_ejections_impostor == 1
    assert meeting_flag.unflagged_ejections_innocent == 1
    # The ANY-flag reading the triage may have meant: 13 flagged meetings, all
    # 12 ejections inside them, 26 flagless meetings — still not 13 ejections.
    assert samples.evidence_taxonomy.meetings_with_any_flag == 19  # was 13
    ejectee_proof = samples.ejectee_proof_cross_tab
    assert ejectee_proof.proof_present_ejections == 19  # was 9
    assert ejectee_proof.non_direct_ejections == 2  # was 3
    assert ejectee_proof.non_direct_accuracy.numerator == 1
    # 9 of the 10 correct ejections involved vent proof (the row's one 4p clause
    # that DOES reproduce).
    assert ejectee_proof.proof_present_impostor == 19  # was 9
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
    assert (samples.crew_turns_with_whereabouts, samples.crew_turns) == (652, 652)
    assert (samples.impostor_turns_with_whereabouts, samples.impostor_turns) == (
        104,
        219,
    )
    assert samples.crew_pooled_coverage == pytest.approx(1.0)  # was 0.9958677685950413
    assert samples.impostor_pooled_coverage == pytest.approx(
        0.4748858447488584
    )  # was 0.4897959183673469
    # The triage's "45.5%" reproduces exactly — as the macro-average.
    assert samples.impostor_macro_average_coverage == pytest.approx(
        0.4375
    )  # was 0.45454545454545453
    assert samples.crew_macro_average_coverage == pytest.approx(
        1.0
    )  # was 0.9957575757575758

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
    assert (samples.crew_turns_with_whereabouts, samples.crew_turns) == (80, 80)
    assert (samples.impostor_turns_with_whereabouts, samples.impostor_turns) == (5, 40)
    corpus = corpus_4p1i.deduction.public_response_coverage
    assert (corpus.crew_turns_with_whereabouts, corpus.crew_turns) == (88, 88)
    assert (corpus.impostor_turns_with_whereabouts, corpus.impostor_turns) == (1, 44)


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
    assert redirects.redirected_ballots == 36  # was 13
    assert redirects.redirected_eject_ballots == 36  # was 13
    assert redirects.redirect_coerced_skip_ballots == 0
    assert redirects.ballots_total == 871  # was 971
    assert redirects.redirected_ballot_share == pytest.approx(36 / 871)  # was 13 / 971


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
    assert samples.flag_named_ejections == 72  # was 90
    assert samples.weak_flag_only_convictions == 3  # was 1
    assert samples.weak_flag_only_innocent == 3  # was 1
    assert samples.weak_flag_only_impostor == 0
    assert samples.weak_flag_only_rate.advisory is True

    corpus = corpus_9p2i.deduction.weak_flag_conviction
    assert corpus.flag_named_ejections == 214  # was 275
    assert corpus.weak_flag_only_convictions == 2  # was 3
    assert corpus.weak_flag_only_innocent == 2  # was 3
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
    assert hits == [
        (2, "headless-seed-2:meeting-0", "p-5"),
        (44, "headless-seed-44:meeting-1", "p-9"),
        (46, "headless-seed-46:meeting-3", "p-1"),
    ]


# --------------------------------------------------------------------------- #
# 6. Turn -> ballot consistency, including the SKIP-tolerance definition.       #
# --------------------------------------------------------------------------- #


def test_turn_ballot_consistency_pins(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """The committed consistency split, buckets partitioning the denominator."""

    samples = samples_9p2i.deduction.turn_ballot_consistency
    assert samples.accusations_total == 752  # was 778
    assert samples.accusing_ballots == 752  # was 777
    assert samples.consistent_ballots == 404  # was 347
    assert samples.inconsistent_skip_ballots == 276  # was 336
    assert samples.inconsistent_other_target_ballots == 69  # was 91
    assert samples.inconsistent_invalid_target_ballots == 3
    assert samples.guard_rewritten_ballots_unwound == 34  # was 16
    assert samples.consistency_rate == pytest.approx(101 / 188)  # was 347 / 777

    corpus = corpus_9p2i.deduction.turn_ballot_consistency
    assert corpus.accusing_ballots == 2113  # was 2186
    assert corpus.consistent_ballots == 1158  # was 1003
    assert corpus.inconsistent_skip_ballots == 792  # was 829
    assert corpus.inconsistent_other_target_ballots == 162  # was 354
    assert corpus.inconsistent_invalid_target_ballots == 1  # was 0
    assert corpus.guard_rewritten_ballots_unwound == 85  # was 46


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

    assert scored == committed.accusing_ballots == 752  # was 777
    # The recorded-target reading is the one the metric must NOT publish.
    assert naive_consistent == 387  # was 340
    assert committed.consistent_ballots == 404  # was 347
    assert committed.guard_rewritten_ballots_unwound == 34  # was 16


def _authored(ballot: VoteBallot, model_body: str) -> tuple[str, bool]:
    """The full authored-target path: provenance split, chain scan, then unwind.

    ``model_body`` is the voter's pre-guard text — the boundary that separates
    the machinery's marker region from the model's, so these fixtures exercise
    the same split :func:`_fold_meeting` performs rather than a shortcut.
    """

    split = _split_rationale(ballot.rationale_text, model_body)
    return _authored_target(ballot, _scan_marker_chain(split.marker_region))


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
    assert _authored(redirected, "they lied about Reactor.") == ("p-2", True)

    untouched = VoteBallot(
        voter="p-1",
        target="p-2",
        confidence=0.7,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text="they lied about Reactor.",
    )
    assert _authored(untouched, "they lied about Reactor.") == ("p-2", False)


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
    assert (samples.model_partner_naming_ballots, samples.impostor_ballots) == (27, 219)
    assert samples.model_role_statement_ballots == 7
    assert samples.crew_partner_naming_ballots == 0
    assert samples.player_visible_leak_turns == 0

    corpus = corpus_9p2i.deduction.scaffold_leakage
    assert (corpus.model_partner_naming_ballots, corpus.impostor_ballots) == (105, 625)
    assert corpus.model_role_statement_ballots == 24
    assert corpus.crew_partner_naming_ballots == 0
    assert corpus.player_visible_leak_turns == 0

    assert corpus_4p1i.deduction.scaffold_leakage.model_role_statement_ballots == 11


def test_self_kill_disclosure_is_counted(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """The THIRD omniscience net: a voter narrating their own kill.

    Task 19.15's contract names "omniscient teammate/self-kill rationale text",
    so a leakage metric that saw only partner naming and role statements was
    measuring two thirds of the class. The union is below the net sum because a
    ballot can hit several nets at once.

    The crew CONTROL is no longer zero on the baseline-7 bytes: one crew ballot
    per 9p2i set trips the text net (baseline 6 read zero on both). It is a
    false positive of the phrase matcher, not a firewall breach -- the firewall
    is enforced structurally (the import-linter contracts, tests/test_firewall.py
    and eval/leak_scan.py, all green) and a crewmate cannot receive an
    impostor-only field at all. Pinned so the control cannot drift further
    unnoticed.
    """

    samples = samples_9p2i.deduction.scaffold_leakage
    assert samples.model_self_kill_disclosure_ballots == 11  # was 9
    assert samples.model_omniscient_ballots == 41  # was 42
    assert samples.crew_omniscient_control_ballots == 1  # was 0

    corpus = corpus_9p2i.deduction.scaffold_leakage
    assert corpus.model_self_kill_disclosure_ballots == 21  # was 22
    assert corpus.model_omniscient_ballots == 139  # was 110
    assert corpus.crew_omniscient_control_ballots == 1  # was 0
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
        assert leakage.model_source_unavailable_ballots == 0
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

    assert envelope_hits == 563  # was 850
    assert (
        samples_9p2i.deduction.scaffold_leakage.model_machinery_quotation_ballots == 0
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
    assert (rate.numerator, rate.denominator) == (1, 102)
    assert rate.advisory is True
    assert leakage.guard_marked_ballots == 115
    assert leakage.guard_marked_ballot_share == pytest.approx(
        115 / 2479
    )  # was 55 / 2726
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
                    {
                        "target": "p-2",
                        "confidence": 0.5,
                        "rationale_text": "p-2 is my partner, I cannot vote them.",
                    }
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

    body = (
        "The system said "
        + BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3")
        + "about my partner."
    )
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
                rationale_text=body,
            ),
        ),
        contradictions=(),
        # The model authored the whole string, marker literal included — which
        # is exactly what makes it attributable to the model rather than a guard.
        llm_calls=(
            LLMCallRecord(
                call_kind="meeting",
                model="fake",
                prompt="",
                response_text=json.dumps(
                    {"target": "SKIP", "confidence": 0.5, "rationale_text": body}
                ),
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                agent_id="p-1",
            ),
        ),
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
    assert _authored(stacked, "they lied about Reactor.") == ("p-2", True)

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
    assert _authored(with_citation_null, "body") == ("p-2", True)


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
    assert _authored(spoofed, spoofed.rationale_text) == ("p-9", False)


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
    assert samples.model_machinery_quotation_ballots == 0  # was 39
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
    assert hits == []


def test_guard_marker_counts(
    samples_9p2i: TournamentEvalReport, corpus_9p2i: TournamentEvalReport
) -> None:
    """The guard-originated census, pinned beside the model-originated one."""

    samples = samples_9p2i.deduction.scaffold_leakage
    assert samples.guard_marked_ballots == 53  # was 18
    assert samples.guard_target_rewrite_ballots == 45  # was 17
    corpus = corpus_9p2i.deduction.scaffold_leakage
    assert corpus.guard_marked_ballots == 115  # was 55
    assert corpus.guard_target_rewrite_ballots == 102  # was 53


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
    assert (corpus.kills_total, corpus.crew_witnessed_kills) == (526, 16)
    assert corpus.co_present_crew_kills == 0

    samples9 = samples_9p2i.deduction.witnessed_supply
    assert samples9 is not None
    assert (samples9.kills_total, samples9.crew_witnessed_kills) == (177, 3)
    assert samples9.co_present_crew_kills == 0
    assert samples9.crew_witnessed_kill_rate.rate == pytest.approx(
        1 / 59
    )  # was 6 / 177

    samples4 = samples_4p1i.deduction.witnessed_supply
    assert samples4 is not None
    assert (samples4.kills_total, samples4.crew_witnessed_kills) == (61, 1)
    assert samples4.co_present_crew_kills == 0


def test_adoption_path_runs_against_a_live_kill_craft_walk(
    samples_4p1i: TournamentEvalReport,
    committed_kill_craft_4p1i: KillCraftReport,
) -> None:
    """The adoption is exercised, not assumed: one live fold on the smallest set.

    ``witnessed_supply_from_kill_craft`` never recomputes a kill-craft cell — it
    reads ``kills_total`` / ``crew_witnessed_kills`` verbatim and sums the
    ``co_present_histogram`` above bucket 0 — so a live walk must reproduce the
    committed block exactly.
    """

    kill_craft = committed_kill_craft_4p1i
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
    assert (good.numerator, good.denominator) == (16, 30)
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
        == 69
    )


# --------------------------------------------------------------------------- #
# Round 4 — provenance, not pattern; and the census bounds.                     #
# --------------------------------------------------------------------------- #


def _voter_call(agent_id: PlayerId, body: str) -> LLMCallRecord:
    """A vote call whose parsed payload carries ``body`` as the pre-guard text.

    Shaped like a real ballot response — ``target`` and ``confidence`` included
    — because that shape is the only evidence distinguishing a vote call from
    any other meeting-phase call (``call_kind`` is "meeting" for both).
    """

    return LLMCallRecord(
        call_kind="meeting",
        model="fake",
        prompt="",
        response_text=json.dumps(
            {"target": "SKIP", "confidence": 0.5, "rationale_text": body}
        ),
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
        agent_id=agent_id,
    )


def _one_ballot_meeting(
    ballot: VoteBallot, calls: tuple[LLMCallRecord, ...]
) -> MeetingReport:
    return MeetingReport(
        meeting_id="m",
        tick=5,
        triggered_by="p-1",
        trigger="report",
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=MeetingTranscript(turns=()),
        ballots=(ballot,),
        contradictions=(),
        llm_calls=calls,
    )


def test_marker_payloads_are_not_scored_as_preserved_leakage() -> None:
    """A hallucinated target is MODEL text riding inside the machinery's marker.

    ``meetings.manager._normalize_ballot_target`` interpolates ``ballot.target``
    verbatim, so a target reading "p-2 is my partner" lands inside
    ``INVALID_VOTE_TARGET_MARKER``. Scanning the whole record would bill the
    model's own words to the guard and invent guard-originated leakage.
    """

    body = "They have been quiet all round, so I am voting them."
    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="SKIP",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=(
                INVALID_VOTE_TARGET_MARKER.format(target="p-2 is my partner") + body
            ),
        ),
        (_voter_call("p-1", body),),
    )
    leakage = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    ).scaffold_leakage

    # The guard DID rewrite the target — that half is real and still counted.
    assert leakage.guard_target_rewrite_ballots == 1
    # But nothing omniscient survived into the BODY, which is what "preserved"
    # means; the phrase lives in a payload the model supplied.
    assert leakage.guard_preserved_omniscient_ballots == 0
    # And the model did not author it in its rationale either.
    assert leakage.model_partner_naming_ballots == 0


def test_a_parse_default_envelope_never_feeds_the_model_nets() -> None:
    """``_vote_parse_default`` records the raw envelope head; it is not rationale.

    The head routinely carries ``"confidence": 0.NN`` — the very false positive
    ``_model_authored_bodies`` extracts the parsed field to avoid (850 raw hits
    against 39 real ones on ``replays/samples/9p2i``). With no parsed body the
    model nets must scan NOTHING rather than fall back to the record.
    """

    raw = '{"target": "p-2", "confidence": 0.45, "rationale_tex'
    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="SKIP",
            confidence=0.0,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=VOTE_PARSE_DEFAULT_MARKER.format(head=raw),
        ),
        (),
    )
    leakage = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    ).scaffold_leakage

    assert leakage.model_machinery_quotation_ballots == 0
    assert leakage.model_machinery_vocabulary_ballots == 0
    # The absent source is published rather than silently substituted.
    assert leakage.model_source_unavailable_ballots == 1
    assert leakage.model_source_pre_guard_ballots == 0
    # A guard DID run: the marker accounts for the record in full, so its
    # provenance is established without a body boundary.
    assert leakage.guard_marked_ballots == 1
    assert leakage.guard_provenance_verified_ballots == 1


def test_a_model_body_opening_with_a_marker_is_not_machinery() -> None:
    """Anchoring is not provenance: model text starts at position 0 too.

    ``meetings.manager._preserved_ballot_markers`` makes the same argument for
    the redaction it guards — "the split is by PROVENANCE, never by pattern" —
    and resolves it with the pre-guard body as the boundary. So does this.
    """

    spoof = (
        BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3") + "and p-2 is my partner."
    )
    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="p-2",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=spoof,
        ),
        # The model authored the ENTIRE string, marker shape and all.
        (_voter_call("p-1", spoof),),
    )
    deduction = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "IMPOSTOR"})
    )
    leakage = deduction.scaffold_leakage

    assert leakage.guard_marked_ballots == 0
    assert leakage.guard_target_rewrite_ballots == 0
    assert leakage.guard_preserved_omniscient_ballots == 0
    assert deduction.redirected_ballots.redirected_ballots == 0
    # The model authored partner text, and that half is still counted.
    assert leakage.model_partner_naming_ballots == 1


def test_an_unattributable_record_trusts_no_markers_and_says_so() -> None:
    """Record and model call disagree: publish the loss, never guess the author.

    With no boundary to establish, under-counting guard cells is a visible,
    published outcome; trusting marker shape would mis-attribute silently.
    """

    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="SKIP",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=(
                BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3") + "a recorded body."
            ),
        ),
        # A body that is NOT a suffix of the record: nothing can be attributed.
        (_voter_call("p-1", "an entirely different body."),),
    )
    leakage = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    ).scaffold_leakage

    assert leakage.guard_provenance_unverifiable_ballots == 1
    assert leakage.guard_provenance_verified_ballots == 0
    assert leakage.guard_marked_ballots == 0
    # The model side still reads the pre-guard body it does have.
    assert leakage.model_source_pre_guard_ballots == 1


def test_every_committed_ballot_is_provenance_verified(
    samples_4p1i: TournamentEvalReport,
    samples_9p2i: TournamentEvalReport,
    corpus_4p1i: TournamentEvalReport,
    corpus_9p2i: TournamentEvalReport,
) -> None:
    """The boundary exists for 100% of committed bytes, so nothing was lost.

    This is what makes the round-4 provenance fixes forward-looking rather than
    a recount: every committed rationale ends with its own pre-guard body.
    """

    sets = {
        "samples/4p1i": samples_4p1i,
        "samples/9p2i": samples_9p2i,
        "ml_corpus/4p1i": corpus_4p1i,
        "ml_corpus/9p2i": corpus_9p2i,
    }
    for name, report in sets.items():
        leakage = report.deduction.scaffold_leakage
        assert leakage.guard_provenance_verified_ballots == leakage.ballots_total, name
        assert leakage.guard_provenance_unverifiable_ballots == 0, name
        assert leakage.model_source_pre_guard_ballots == leakage.ballots_total, name
        assert leakage.model_source_unavailable_ballots == 0, name


def test_census_rejects_more_flagged_meetings_than_flags(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Each counted meeting carries >= 1 flag, so the census cannot exceed them."""

    payload = samples_9p2i.deduction.model_dump()
    payload["evidence_taxonomy"]["meetings_with_any_flag"] = (
        payload["evidence_taxonomy"]["flags_total"] + 1
    )
    with pytest.raises(ValidationError, match="cannot exceed flags_total"):
        DeductionMetricsReport.model_validate(payload)


def test_census_rejects_more_flagged_meetings_than_meetings(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """The report owns the meeting denominator, so it owns that bound."""

    payload = samples_9p2i.deduction.model_dump()
    census = payload["evidence_taxonomy"]
    inflated = payload["meetings_total"] + 1
    # Keep the census internally consistent — categories partitioning the total,
    # and the total large enough to clear this block's own bound — so the only
    # rule left to catch it is the report-level meeting denominator.
    census["meetings_with_any_flag"] = inflated
    census["flags_total"] = inflated
    census["role_proof_flags"] = (
        inflated - census["cross_statement_flags"] - census["weak_signal_flags"]
    )
    census["weak_signal_share"] = census["weak_signal_flags"] / inflated
    with pytest.raises(ValidationError, match="cannot exceed the meetings folded"):
        DeductionMetricsReport.model_validate(payload)


# --------------------------------------------------------------------------- #
# Round 5 — full-record trust is parse-default only; model counts need a body.  #
# --------------------------------------------------------------------------- #


def test_a_full_record_marker_chain_is_trusted_only_for_parse_default() -> None:
    """Only ``_vote_parse_default`` writes a marker as the WHOLE rationale.

    Every other guard prepends to a body, so a bare redirect marker standing
    alone beside a *different* pre-guard body is a disagreement between the
    record and the model's own call — not evidence that a guard ran.
    """

    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="p-4",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3"),
        ),
        (_voter_call("p-1", "an entirely different body."),),
    )
    deduction = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    )

    assert deduction.scaffold_leakage.guard_provenance_unverifiable_ballots == 1
    assert deduction.scaffold_leakage.guard_marked_ballots == 0
    assert deduction.scaffold_leakage.guard_target_rewrite_ballots == 0
    assert deduction.redirected_ballots.redirected_ballots == 0


def test_an_empty_model_body_still_verifies_through_the_suffix_rule() -> None:
    """The legitimate marker-only record: the model authored an empty rationale.

    It reaches the SUFFIX rule (every string ends with ``""``), so tightening
    the full-record rule to parse-default costs nothing real.
    """

    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="p-4",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3"),
        ),
        (_voter_call("p-1", ""),),
    )
    deduction = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    )

    assert deduction.scaffold_leakage.guard_provenance_verified_ballots == 1
    assert deduction.scaffold_leakage.guard_marked_ballots == 1
    assert deduction.scaffold_leakage.guard_target_rewrite_ballots == 1
    assert deduction.redirected_ballots.redirected_ballots == 1


def test_model_counts_cannot_exceed_the_ballots_that_had_a_readable_body(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Each model net increments only while scanning a pre-guard body.

    A payload claiming no readable model ballots beside positive model leakage
    is arithmetically impossible, and the fold cannot produce it — so the model
    must not accept it either.
    """

    payload = samples_9p2i.deduction.model_dump()
    leakage = payload["scaffold_leakage"]
    # Set the readable pool to exactly what the role-disjoint pairs need, so
    # the round-6 JOINT bound is satisfied and this test isolates the per-net
    # one. The vocabulary net (116 on this set) is the cell left over-claiming.
    readable = (
        leakage["model_omniscient_ballots"] + leakage["crew_omniscient_control_ballots"]
    )
    leakage["model_source_pre_guard_ballots"] = readable
    leakage["model_source_unavailable_ballots"] = leakage["ballots_total"] - readable
    assert leakage["model_machinery_vocabulary_ballots"] > readable
    with pytest.raises(ValidationError, match="model_machinery_vocabulary_ballots"):
        DeductionMetricsReport.model_validate(payload)


def test_player_visible_leak_turns_is_not_bounded_by_ballot_provenance(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """The turn net reads ``free_text``, not a ballot body — a different source.

    Bounding it by the pre-guard BALLOT count would be a category error, so the
    guard against over-tightening is pinned alongside the bound itself.
    """

    leakage = samples_9p2i.deduction.scaffold_leakage
    # The committed set exercises the distinction only if the turn net is
    # non-trivial and its denominator is the turn total, not the ballot total.
    assert leakage.player_visible_leak_turns >= 0
    assert leakage.turns_total > 0

    payload = samples_9p2i.deduction.model_dump()
    block = payload["scaffold_leakage"]
    # Zero every model BALLOT net so the pre-guard bound is satisfiable at 0...
    for field in (
        "model_partner_naming_ballots",
        "model_role_statement_ballots",
        "model_self_kill_disclosure_ballots",
        "model_omniscient_ballots",
        "crew_partner_naming_ballots",
        "crew_omniscient_control_ballots",
        "model_machinery_quotation_ballots",
        "model_machinery_vocabulary_ballots",
    ):
        block[field] = 0
    block["model_partner_naming_rate"] = _zeroed(block["model_partner_naming_rate"])
    block["model_omniscient_rate"] = _zeroed(block["model_omniscient_rate"])
    block["model_machinery_quotation_share"] = 0.0
    block["model_source_pre_guard_ballots"] = 0
    block["model_source_unavailable_ballots"] = block["ballots_total"]
    # ...and leave the TURN net at its real, positive value. It must survive.
    block["player_visible_leak_turns"] = 1
    restored = DeductionMetricsReport.model_validate(payload)
    assert restored.scaffold_leakage.player_visible_leak_turns == 1


def _zeroed(cell: dict[str, object]) -> dict[str, object]:
    """The same Wilson cell with a zero numerator (denominator preserved)."""

    denominator = cell["denominator"]
    assert isinstance(denominator, int)
    rate, low, high = _wilson_interval(0, denominator)
    return {
        "numerator": 0,
        "denominator": denominator,
        "rate": rate,
        "wilson_low": low,
        "wilson_high": high,
        "advisory": True,
    }


# --------------------------------------------------------------------------- #
# Round 6 — the parse-default shape is exclusive; unencoded invariants closed.  #
# --------------------------------------------------------------------------- #


def test_a_marker_chain_ending_in_parse_default_is_not_machinery() -> None:
    """The writer emits the parse-default marker ALONE, never after another.

    ``_collect_vote`` returns ``_vote_parse_default`` straight out of the
    ``ValidationError`` handler, so no other guard has run or can run. A chain
    of several markers ending in a parse default is a shape the writer cannot
    produce, and must not be accepted as machinery.
    """

    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="SKIP",
            confidence=0.0,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=(
                BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3")
                + VOTE_PARSE_DEFAULT_MARKER.format(head="{")
            ),
        ),
        (),
    )
    deduction = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    )

    assert deduction.scaffold_leakage.guard_provenance_unverifiable_ballots == 1
    assert deduction.scaffold_leakage.guard_marked_ballots == 0
    assert deduction.redirected_ballots.redirected_ballots == 0


def test_a_discarded_vote_response_is_not_a_pre_guard_body() -> None:
    """A schema-invalid response is rejected WHOLESALE, rationale field included.

    The manager raises on the ballot as a unit, so a ``rationale_text`` that
    happens to parse out of the discarded payload is not this ballot's
    pre-guard body — the recorded ballot is a parse default, which by
    definition has none.
    """

    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="SKIP",
            confidence=0.0,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=VOTE_PARSE_DEFAULT_MARKER.format(head='{"target": 7'),
        ),
        # Parses as JSON and carries a rationale field — but the vote it came
        # from failed validation on another field and was thrown away.
        (_voter_call("p-1", "my suspicion is 0.45 and p-2 is my partner."),),
    )
    leakage = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    ).scaffold_leakage

    assert leakage.model_source_unavailable_ballots == 1
    assert leakage.model_source_pre_guard_ballots == 0
    assert leakage.model_machinery_quotation_ballots == 0
    assert leakage.model_partner_naming_ballots == 0


def test_an_unrecognised_leading_marker_fails_into_the_published_bucket() -> None:
    """A prefix this codebase cannot account for is not this codebase's text.

    A writer-side marker added without updating ``_BALLOT_MARKER_CHAIN`` would
    otherwise verify while contributing nothing to the census — a silent
    under-count. It lands in the published unverifiable bucket instead.
    """

    body = "they lied about Reactor."
    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="p-2",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="[future guard 'p-9' applied] " + body,
        ),
        (_voter_call("p-1", body),),
    )
    leakage = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    ).scaffold_leakage

    assert leakage.guard_provenance_unverifiable_ballots == 1
    assert leakage.guard_provenance_verified_ballots == 0
    assert leakage.guard_marked_ballots == 0
    # The model body is still readable, so the model half is unaffected.
    assert leakage.model_source_pre_guard_ballots == 1


def test_role_disjoint_nets_are_bounded_jointly_by_readable_ballots(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Impostor and crew nets draw from disjoint halves of ONE readable pool.

    Per-role minima alone let a payload claim more role-split matches than
    there were bodies — which is how a corrupt report hides a non-zero crew
    control, the cell whose entire job is to read 0.
    """

    payload = samples_9p2i.deduction.model_dump()
    block = payload["scaffold_leakage"]
    readable = block["model_source_pre_guard_ballots"]
    block["crew_omniscient_control_ballots"] = (
        readable - block["model_omniscient_ballots"] + 1
    )
    with pytest.raises(ValidationError, match="role-disjoint"):
        DeductionMetricsReport.model_validate(payload)


def test_a_meeting_cannot_carry_more_than_one_ejection(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """One ``MeetingReport``, one outcome — so ejections are bounded by meetings."""

    payload = samples_9p2i.deduction.model_dump()
    cross_tab = payload["meeting_flag_cross_tab"]
    cross_tab["flagged_ejections_impostor"] = cross_tab["flagged_meetings"] + 1
    with pytest.raises(ValidationError, match="cannot exceed flagged meetings"):
        DeductionMetricsReport.model_validate(payload)


def test_the_two_headline_views_cannot_disagree_about_role_proof(
    samples_9p2i: TournamentEvalReport,
) -> None:
    """Partition A's FLAGGED predicate and the census's ROLE-PROOF are one test.

    Read at two granularities, so a payload claiming 70 role-proof meetings and
    zero role-proof flags is the two headline views contradicting each other.
    """

    payload = samples_9p2i.deduction.model_dump()
    census = payload["evidence_taxonomy"]
    census["cross_statement_flags"] += census["role_proof_flags"]
    census["role_proof_flags"] = 0
    with pytest.raises(ValidationError, match="role-proof flag"):
        DeductionMetricsReport.model_validate(payload)


# --------------------------------------------------------------------------- #
# Round 7 — provenance beats shape; every branch is accountable.               #
# --------------------------------------------------------------------------- #


def test_a_model_quoting_the_parse_default_literal_is_not_machinery() -> None:
    """An exactly-matching recovered body is the strongest evidence there is.

    If the model's own pre-guard text IS the whole record, it authored that
    text — even when the text happens to be the parse-default audit literal.
    Shape must not overrule provenance in the one case where provenance is
    unambiguous.
    """

    quoted = VOTE_PARSE_DEFAULT_MARKER.format(head="p-2 is my partner")
    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="SKIP",
            confidence=0.4,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=quoted,
        ),
        (_voter_call("p-1", quoted),),
    )
    deduction = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    )
    leakage = deduction.scaffold_leakage

    # No guard ran: the marker region is empty, so nothing is credited to it.
    assert leakage.guard_marked_ballots == 0
    assert leakage.guard_provenance_verified_ballots == 1
    # And the model's text is read, not suppressed.
    assert leakage.model_source_pre_guard_ballots == 1
    assert leakage.model_source_unavailable_ballots == 0
    assert leakage.model_partner_naming_ballots == 1


def test_the_redaction_branch_rejects_an_unregistered_prefix() -> None:
    """The prefix-accountability rule applies to EVERY verifying branch.

    An unregistered leading marker stops the walk before the known teammate
    marker, so the ballot would contribute neither a guard rewrite nor an
    unwind while still counting as verified.
    """

    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="SKIP",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=(
                "[future guard 'p-9' applied] "
                + TEAMMATE_VOTE_TARGET_MARKER.format(target="p-2")
                + TEAMMATE_COERCED_VOTE_RATIONALE
            ),
        ),
        (_voter_call("p-1", "p-2 is my partner, I cannot vote them."),),
    )
    leakage = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "IMPOSTOR"})
    ).scaffold_leakage

    assert leakage.guard_provenance_unverifiable_ballots == 1
    assert leakage.guard_provenance_verified_ballots == 0
    assert leakage.guard_marked_ballots == 0
    assert leakage.guard_target_rewrite_ballots == 0
    # The model half is unaffected — the pre-guard body is still readable.
    assert leakage.model_partner_naming_ballots == 1


def test_a_malformed_turn_response_is_not_mistaken_for_a_vote() -> None:
    """``call_kind`` is "meeting" for turns AND votes, so shape is the evidence.

    A turn response that hallucinated a string ``rationale_text``, paired with a
    vote call that never produced a record, would otherwise supply a pre-guard
    body for a ballot whose model text is genuinely unavailable.
    """

    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="p-2",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="they lied about Reactor.",
        ),
        # A TURN payload — no target, no confidence — that happens to carry a
        # string rationale_text saying something the nets would match.
        (
            LLMCallRecord(
                call_kind="meeting",
                model="fake",
                prompt="",
                response_text=json.dumps(
                    {
                        "free_text": "I saw nothing.",
                        "rationale_text": "my suspicion is 0.45, p-2 is my partner",
                    }
                ),
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                agent_id="p-1",
            ),
        ),
    )
    leakage = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    ).scaffold_leakage

    assert leakage.model_source_unavailable_ballots == 1
    assert leakage.model_source_pre_guard_ballots == 0
    assert leakage.model_partner_naming_ballots == 0
    assert leakage.model_machinery_quotation_ballots == 0


def test_a_real_vote_payload_still_supplies_its_body() -> None:
    """The tightened discriminator must not cost a genuine vote call.

    Pinned beside the rejection above so a future narrowing cannot quietly
    start dropping real bodies — the committed sets already assert 0
    unavailable, and this states the mechanism.
    """

    meeting = _one_ballot_meeting(
        VoteBallot(
            voter="p-1",
            target="p-2",
            confidence=0.5,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="p-2 is my partner but I must vote them.",
        ),
        (
            LLMCallRecord(
                call_kind="meeting",
                model="fake",
                prompt="",
                response_text=json.dumps(
                    {
                        "target": "p-2",
                        "confidence": 0.5,
                        "primary_reason_id": None,
                        "considered_alternatives": [],
                        "rationale_text": "p-2 is my partner but I must vote them.",
                    }
                ),
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                agent_id="p-1",
            ),
        ),
    )
    leakage = compute_deduction_metrics(
        _report_with(meeting, roles={"p-1": "IMPOSTOR", "p-2": "CREWMATE"})
    ).scaffold_leakage

    assert leakage.model_source_pre_guard_ballots == 1
    assert leakage.model_source_unavailable_ballots == 0
    assert leakage.model_partner_naming_ballots == 1
