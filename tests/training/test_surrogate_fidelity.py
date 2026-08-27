"""Tests for the surrogate fidelity harness (Task 15.11).

Pins on the committed baseline-5 bytes: by-GAME cross-validation never splits a
game's meetings across folds (the anti-leakage guarantee), the harness reports
top-1/top-2, SKIP-vs-eject accuracy, and Brier/ECE TOGETHER (never a single
headline), the honest ceiling is a measurement bounded in [0, 1], and the re-run
FO-6 logistic reproduces the audit's story — a middling ranking whose binary
decision head collapses to always-SKIP on the big set.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from agents.memory.beliefs import CONTRADICTION_RENDER_CEIL
from training.surrogate.dataset import (
    MeetingTable,
    SurrogateSplits,
    build_meeting_table,
)
from training.surrogate.fidelity import (
    FO6_DECISION_HEAD_LABEL,
    Fo6Logistic,
    MeetingPrediction,
    MeetingView,
    ThresholdScan,
    _game_folds,
    build_meeting_views,
    compute_honest_ceiling,
    fo6_rebaseline,
    run_surrogate_fidelity,
)


class _LowestTiedTauFo6(Fo6Logistic):
    """FO-6 under the PRE-21.16 scan, which broke ties toward the LOWEST tau.

    The control the tie-break tests compare against: same fit, same curve, only the
    selection from a tied plateau differs — so any channel that moves between the
    two is threshold-dependent and any channel that does not is not.
    """

    def _tune_threshold(self, meetings: Sequence[MeetingView]) -> ThresholdScan:
        scan = super()._tune_threshold(meetings)
        best_tau, best_correct = 0.5, -1
        for tau, correct in scan.curve:
            if correct > best_correct:
                best_correct, best_tau = correct, tau
        return scan.model_copy(update={"tuned_tau": best_tau})


# Task 19.27: campaign tier (training/README.md §2 FREEZE — the fidelity harnesses).
# Excluded from the default gate; runs weekly in CI's campaign-tier job and
# at phase close via `-m campaign`.
pytestmark = pytest.mark.campaign

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"
# The committed 15.12 corpus — the population the GO bar is measured on, and the
# one the FO-6 tau curve below is pinned against.
_CORPUS = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"


# --------------------------------------------------------------------------- #
# By-GAME CV — the leakage guarantee                                          #
# --------------------------------------------------------------------------- #


def test_by_game_cv_never_splits_a_games_meetings_across_folds() -> None:
    """Two meetings of one game always land in the SAME fold (§5.5 no leakage).

    Proves the harness folds by GAME, not by meeting: the per-fold TEST seed sets
    partition the games (pairwise disjoint, union = all seeds), so every meeting of
    a game shares a fold and the cross-meeting belief state never leaks between
    train and test.
    """

    table = build_meeting_table(_NINE)
    all_seeds = set(table.game_seeds())
    fold_pairs = _game_folds(table, folds=5)

    seen_test: set[int] = set()
    for train, test in fold_pairs:
        assert train.isdisjoint(test), "a game is in both train and test of a fold"
        assert seen_test.isdisjoint(test), "a game appears in two test folds"
        seen_test |= set(test)
        # Every game's meetings are wholly inside its fold — group by seed and check
        # no meeting id straddles the train/test boundary.
        test_meetings = {(r.seed, r.meeting_id) for r in table.rows if r.seed in test}
        train_meetings = {(r.seed, r.meeting_id) for r in table.rows if r.seed in train}
        assert test_meetings.isdisjoint(train_meetings)
    assert seen_test == all_seeds, "the test folds must cover every game exactly once"


def _with_splits(table: MeetingTable, **kwargs: object) -> MeetingTable:
    """Attach a :class:`SurrogateSplits` to a table without rebuilding it."""

    return table.model_copy(update={"splits": SurrogateSplits(**kwargs)})  # type: ignore[arg-type]


def test_committed_splits_produce_a_single_by_game_fold() -> None:
    """A committed ``splits.json`` (a full partition) yields one by-game fold."""

    base = build_meeting_table(_FOUR)
    seeds = list(base.game_seeds())
    test_seeds = seeds[-2:]
    train_seeds = seeds[:-3]
    val_seeds = seeds[-3:-2]
    table = _with_splits(base, train=train_seeds, val=val_seeds, test=test_seeds)
    fold_pairs = _game_folds(table, folds=5)
    assert len(fold_pairs) == 1
    train, test = fold_pairs[0]
    assert test == frozenset(test_seeds)
    assert frozenset(train_seeds) <= train
    assert train.isdisjoint(test)


def test_split_universe_is_every_recorded_game_including_no_meeting_games() -> None:
    """The fold/split universe is EVERY recorded game, not just games with rows.

    11 of the committed 4p1i games end before any meeting fires (no rows), yet a
    legitimate 15.12 ``splits.json`` must still be able to assign them to a side —
    validating against rows-bearing seeds only would falsely reject it.
    """

    table = build_meeting_table(_FOUR)
    rows_bearing = {row.seed for row in table.rows}
    assert len(table.game_seeds()) == table.games_total == 50
    assert len(rows_bearing) < table.games_total, (
        "4p1i is the fixture BECAUSE it has no-meeting games"
    )
    # A full partition that puts a no-meeting game in test validates and runs.
    no_meeting = sorted(set(table.game_seeds()) - rows_bearing)[0]
    with_meeting = next(s for s in table.game_seeds() if s in rows_bearing)
    rest = [s for s in table.game_seeds() if s not in (no_meeting, with_meeting)]
    split_table = _with_splits(
        table, train=rest, val=[], test=[no_meeting, with_meeting]
    )
    report = run_surrogate_fidelity(split_table, _OracleModel, model_name="oracle")
    assert report.folds == 1
    # The no-meeting game contributes nothing scoreable; the scored population is
    # exactly the rows-bearing test game's meetings.
    test_meetings = {
        (r.seed, r.meeting_id) for r in table.rows if r.seed == with_meeting
    }
    assert report.meetings_scored == len(test_meetings)


def test_ceiling_is_measured_over_the_scored_population() -> None:
    """``honest_ceiling`` counts EXACTLY the scored ejection meetings.

    Under K-fold every game is tested once, so ``ceiling.ejections_total ==
    ejection_meetings``; under a committed split it is the held-out games'
    ejections only — never train/val meetings — so the GO/NO-GO comparison of
    achieved top-1 vs the ceiling reads one distribution (Codex review).
    """

    table = build_meeting_table(_NINE)
    kfold = fo6_rebaseline(table)
    assert kfold.honest_ceiling.ejections_total == kfold.ejection_meetings

    seeds = list(table.game_seeds())
    test_seeds = seeds[:10]
    split = _with_splits(table, train=seeds[10:], val=[], test=test_seeds)
    report = run_surrogate_fidelity(split, _OracleModel, model_name="oracle")
    assert report.honest_ceiling.ejections_total == report.ejection_meetings
    held_out_ejections = len(
        {
            (r.seed, r.meeting_id)
            for r in table.rows
            if r.seed in set(test_seeds) and r.outcome == "EJECTED"
        }
    )
    assert report.honest_ceiling.ejections_total == held_out_ejections


def test_split_with_empty_fit_set_fails_loud() -> None:
    """``train=[] val=[] test=<all>`` raises — fit([]) must never score silently."""

    base = build_meeting_table(_FOUR)
    table = _with_splits(base, train=[], val=[], test=list(base.game_seeds()))
    with pytest.raises(ValueError, match="fit set"):
        _game_folds(table, folds=5)


def test_split_with_no_scoreable_test_meetings_fails_loud() -> None:
    """A test side made ONLY of no-meeting games raises (nothing to score).

    The split universe legitimately includes no-meeting games, so a malformed
    15.12 split could put ALL of them (and nothing else) on the test side —
    the single fold would be skipped and the harness would return
    ``meetings_scored=0`` with all-zero metrics while looking like a valid
    held-out run (Codex review).
    """

    base = build_meeting_table(_FOUR)
    no_meeting = sorted(set(base.game_seeds()) - {row.seed for row in base.rows})
    assert no_meeting, "4p1i is the fixture BECAUSE it has no-meeting games"
    rest = [s for s in base.game_seeds() if s not in set(no_meeting)]
    table = _with_splits(base, train=rest, val=[], test=no_meeting)
    with pytest.raises(ValueError, match="test set .* no scoreable meetings"):
        _game_folds(table, folds=5)


def test_split_with_no_scoreable_fit_meetings_fails_loud() -> None:
    """A fit side made ONLY of no-meeting games raises (fit([]) never scores).

    A non-empty fit seed set of no-meeting games passes the emptiness check yet
    carries zero train views, so the harness would ``fit([])`` and score an
    effectively untrained model as if it were a valid held-out run (Codex
    review); it must fail loud instead.
    """

    base = build_meeting_table(_FOUR)
    no_meeting = sorted(set(base.game_seeds()) - {row.seed for row in base.rows})
    assert no_meeting, "4p1i is the fixture BECAUSE it has no-meeting games"
    rest = [s for s in base.game_seeds() if s not in set(no_meeting)]
    table = _with_splits(base, train=no_meeting, val=[], test=rest)
    with pytest.raises(ValueError, match="fit set .* no scoreable meetings"):
        _game_folds(table, folds=5)


def test_leaky_committed_split_fails_loud() -> None:
    """A split that puts a game in both the fit and test set raises (no silent leak).

    The anti-leakage guarantee is the harness's whole point; a 15.12 corpus mistake
    that leaks the same game's meetings onto both sides of the single fold must fail
    loud rather than silently inflating the fidelity numbers.
    """

    base = build_meeting_table(_FOUR)
    seeds = list(base.game_seeds())
    # A full partition EXCEPT the last train seed is also in test (the leak).
    table = _with_splits(base, train=seeds[:-1], val=[], test=[seeds[-2], seeds[-1]])
    with pytest.raises(ValueError, match="leaks games"):
        _game_folds(table, folds=5)


def test_split_omitting_table_seed_fails_loud() -> None:
    """A split that leaves a table game out of BOTH train and test raises.

    An omitted game's meetings would be in neither fold, so the run would silently
    score a subset while reporting the full set — a corpus typo must fail loud.
    """

    base = build_meeting_table(_FOUR)
    seeds = list(base.game_seeds())
    # Covers every seed but the last — the omitted game.
    table = _with_splits(base, train=seeds[:-2], val=[], test=[seeds[-2]])
    with pytest.raises(ValueError, match="omits table games"):
        _game_folds(table, folds=5)


def test_split_referencing_unknown_seed_fails_loud() -> None:
    """A split naming a seed absent from the table raises."""

    base = build_meeting_table(_FOUR)
    seeds = list(base.game_seeds())
    table = _with_splits(base, train=seeds, val=[], test=[999999])
    with pytest.raises(ValueError, match="absent from the table"):
        _game_folds(table, folds=5)


def test_empty_test_split_fails_loud() -> None:
    """A split with an empty test set raises (nothing to score)."""

    base = build_meeting_table(_FOUR)
    seeds = list(base.game_seeds())
    table = _with_splits(base, train=seeds, val=[], test=[])
    with pytest.raises(ValueError, match="test set is empty"):
        _game_folds(table, folds=5)


def test_fo6_fit_rejects_empty_training_input() -> None:
    """``Fo6Logistic.fit([])`` raises — never a silent all-zero model."""

    with pytest.raises(ValueError, match="untrained"):
        Fo6Logistic().fit([])


def test_derived_fold_with_no_trainable_meetings_fails_loud() -> None:
    """A derived K-fold whose fit side has no meetings raises (Codex review).

    On a corpus with fewer than two meeting-bearing games, ``_game_folds`` can
    put the only scoreable game on the test side and the rest-side games carry
    no meetings; the harness must fail loud rather than fit a model on nothing
    and report valid-looking by-game-CV numbers.
    """

    base = build_meeting_table(_FOUR)
    rows_bearing = sorted({row.seed for row in base.rows})
    no_meeting = sorted(set(base.game_seeds()) - set(rows_bearing))
    assert no_meeting, "4p1i is the fixture BECAUSE it has no-meeting games"
    with_meeting = rows_bearing[0]
    tiny = base.model_copy(
        update={
            "seeds": tuple(sorted((no_meeting[0], with_meeting))),
            "rows": tuple(r for r in base.rows if r.seed == with_meeting),
            "games_total": 2,
            "splits": None,
        }
    )
    with pytest.raises(ValueError, match="no scoreable training meetings"):
        fo6_rebaseline(tiny)


def test_run_with_no_scoreable_meetings_fails_loud() -> None:
    """A derived run over ONLY no-meeting games raises, never an all-zero report.

    Every derived fold's test side is empty so every fold is skipped; without the
    guard the harness would fall through and return ``meetings_scored=0`` with
    all-zero metrics as if it were a valid fidelity run (Codex review).
    """

    base = build_meeting_table(_FOUR)
    no_meeting = sorted(set(base.game_seeds()) - {row.seed for row in base.rows})
    assert len(no_meeting) >= 2, "4p1i is the fixture BECAUSE it has no-meeting games"
    empty = base.model_copy(
        update={
            "seeds": tuple(no_meeting[:2]),
            "rows": (),
            "games_total": 2,
            "splits": None,
        }
    )
    with pytest.raises(ValueError, match="no fold scored any meeting"):
        fo6_rebaseline(empty)


def test_recon_respects_the_production_render_ceiling() -> None:
    """The recon applies the Task-14.10 certain-guilt ceiling (Codex review).

    Production caps flag-driven lift at ``max(prior, CONTRADICTION_RENDER_CEIL)``
    — a pinned-prior+flag shape renders ~0.97, never the 1.0 clamp, while a
    first-hand conclusive prior already at the clamp (a fresh witnessed-kill pin)
    holds. The prior is the strongest voter's real pre-meeting belief row
    (``public_suspicion`` — perception pins ingested at event time and Rule-5
    decayed by the real fold). The best-case recon must render the same bound or
    the ceiling counts strict argmaxes the real belief graph could not produce.
    """

    views = build_meeting_views(build_meeting_table(_NINE))
    ceiled_cases = 0
    for view in views:
        for cand in view.candidates:
            prior = view.public_suspicion[cand]
            bound = max(prior, CONTRADICTION_RENDER_CEIL)
            assert view.recon_suspicion[cand] <= bound + 1e-9
            if prior + view.features[cand]["contradiction_lift"] > bound + 1e-9:
                ceiled_cases += 1
                assert view.recon_suspicion[cand] == pytest.approx(bound)
    # The bound must actually bind somewhere on the committed bytes — the
    # pinned-prior+flag shape the 14.10 audit pinned persists on the committed
    # baseline-5 set.
    assert ceiled_cases > 0


# --------------------------------------------------------------------------- #
# The four channels reported together                                         #
# --------------------------------------------------------------------------- #


def test_report_carries_all_four_channels_together() -> None:
    """top-1/top-2 + SKIP-vs-eject + Brier/ECE are all reported (never one number)."""

    report = fo6_rebaseline(build_meeting_table(_NINE))
    assert 0.0 <= report.top1 <= report.top2 <= 1.0
    assert 0.0 <= report.skip_vs_eject_accuracy <= 1.0
    assert 0.0 <= report.brier <= 1.0
    assert 0.0 <= report.ece <= 1.0
    # The decision census reconciles with the meeting count.
    assert report.predicted_ejections + report.predicted_skips == report.meetings_scored
    assert report.ejection_meetings + report.skip_meetings == report.meetings_scored


def test_recorded_ballot_confidence_calibration_is_reported() -> None:
    """Brier/ECE on the recorded ballot confidences is a first-class channel (§5.5).

    Over the scored meetings' non-SKIP ballots, the voter's stated confidence vs
    whether its named target was ejected — reported ALONGSIDE the model's ejection
    calibration, so a badly-calibrated ballot model is judged against the real
    voters' calibration rather than only the post-tally number.
    """

    table = build_meeting_table(_NINE)
    report = fo6_rebaseline(table)
    non_skip = sum(1 for r in table.rows if r.ballot_target != "SKIP")
    assert report.ballot_rows == non_skip  # 5-fold covers every game once
    assert 0.0 <= report.ballot_brier <= 1.0
    assert 0.0 <= report.ballot_ece <= 1.0
    assert report.ballot_brier > 0.0  # real voters are imperfectly calibrated


def test_fo6_rebaseline_collapses_to_always_skip_on_the_big_set() -> None:
    """The re-run FO-6 decision head degenerates to always-SKIP on 9p2i (§5.2).

    Its binary decision head almost never predicts an ejection — on the Task-18.12
    baseline-6 re-record it skips ALL 101 true ejection meetings (a STRONGER
    degeneracy than the baseline-5 99-of-100). On the baseline-3/4 bytes that trivial
    policy was also WORSE than the always-eject constant (eject-majority meeting mix),
    which is what ``degenerates_to_skip`` encodes; the baseline-5 close record flipped
    the mix to skip-majority so always-skip briefly BEAT always-eject and the flag
    read False. The baseline-6 re-record REVERTS the mix to eject-majority (101 EJECT
    of 165 resolved — the graduated meeting layer convicts more often), so always-skip
    is once again WORSE than always-eject and the eject-era degeneracy flag reads True.

    Task-18.12 finding (the record documents it, audits/audit-phase-18-baseline-6.md
    §9): the physical rank's residual signal NO LONGER collapses to the per-candidate
    base rate. On the baseline-5 bytes top-1 fell to ~0.11 (at/below ~1/9); on the
    vent-widening re-record it RISES to 20/101 = 0.198, ABOVE the 1/9 = 0.111 base rate
    — the widened trajectories leave the six raw physical counts slightly more
    predictive of the ejected candidate. This is a rank observation only: it remains
    far under the honest reachability ceiling (0.861, guarded by
    ``test_honest_ceiling_bounds_the_fo6_top1``), and the BEHAVIORAL collapse — the
    load-bearing claim of this test — is unchanged and stronger. The surrogate stays
    prior-substrate-anchored by design (audits/audit-phase-16-close.md §8 — Phase 17
    re-grounds before any training read).
    """

    report = fo6_rebaseline(build_meeting_table(_NINE))
    assert report.model_name == "fo6-physical-logistic"
    # The physical rank's residual signal rose ABOVE the per-candidate base rate on
    # baseline 6 (the documented 18.12 flip): top-1 = 20/101, pinned exactly. It stays
    # far below the honest reachability ceiling (test_honest_ceiling_bounds_the_fo6_top1).
    assert report.top1 == pytest.approx(20 / 101)
    assert report.top1 > 1.0 / 9.0  # baseline-6 flip: now beats the base rate
    # Almost never ejects: SKIP on ALL 101 true ejection meetings.
    assert report.ejection_meetings == 101
    assert report.ejection_predicted_skips == 101
    assert 2 * report.ejection_predicted_skips > report.ejection_meetings
    # The substrate-contingent halves, re-pinned at their baseline-6 truth: the
    # meeting mix is eject-majority again, so the all-skip head scores BELOW the
    # always-eject constant and the eject-era degeneracy flag reads True.
    assert report.skip_vs_eject_accuracy < report.always_eject_baseline
    assert report.degenerates_to_skip


def test_fidelity_runs_on_the_small_preset() -> None:
    """The harness runs on the 4p1i preset (its small-set headline top-1 is high)."""

    report = fo6_rebaseline(build_meeting_table(_FOUR))
    assert report.meetings_scored > 0
    assert report.top1 > 0.0


# --------------------------------------------------------------------------- #
# FO-6's decision head is a meeting-mix tracker, published as one              #
# --------------------------------------------------------------------------- #


def test_report_publishes_both_trivial_decision_constants() -> None:
    """A tuned head is read against BOTH poles, not only the eject one.

    ``always_skip_baseline`` is the score a head that never ejects posts on the
    scored population; together with ``always_eject_baseline`` the two partition it,
    so a head that merely tracks the mix is visible instead of implied.
    """

    report = fo6_rebaseline(build_meeting_table(_NINE))
    assert report.always_skip_baseline == pytest.approx(
        report.skip_meetings / report.meetings_scored
    )
    assert report.always_eject_baseline + report.always_skip_baseline == pytest.approx(
        1.0
    )


def test_fo6_decision_head_is_published_as_a_meeting_mix_tracker() -> None:
    """The head carries its label and the full tau curve it was chosen from.

    On the committed 9p2i corpus the curve is FLAT at 120 across tau in
    [0.40, 0.95] — exactly the fit side's SKIP count (120 of 345 meetings, 225
    ejections) — and the tuned tau beats that trivial always-SKIP constant by 7
    meetings (127 of 345, 2.0%). A head whose whole margin is 7 of 345 tracks the
    meeting mix, which is why it is labelled and published rather than read as a
    physical baseline.
    """

    report = fo6_rebaseline(build_meeting_table(_CORPUS))
    head = report.decision_head
    assert head is not None
    assert head.label == FO6_DECISION_HEAD_LABEL
    # The committed corpus ships a split, so the harness fits exactly once.
    assert len(head.scans) == 1
    scan = head.scans[0]
    assert scan.fit_meetings == 345
    assert scan.fit_ejection_meetings == 225
    assert scan.fit_skip_meetings == 120

    plateau = {correct for tau, correct in scan.curve if tau >= 0.40}
    assert plateau == {scan.fit_skip_meetings}  # the always-SKIP constant, exactly
    assert scan.tuned_correct == 127
    assert scan.tuned_correct - scan.fit_skip_meetings == 7
    # ...and the curve is the whole grid, not a summary of it.
    assert [tau for tau, _ in scan.curve] == [step / 20.0 for step in range(1, 20)]


def test_tuned_threshold_breaks_ties_toward_the_higher_tau() -> None:
    """Ties go to the conservative pole, and it is a REAL tie on this corpus.

    tau 0.20 and 0.25 both score 127 on the fit side; raising tau only ever turns
    an eject into a SKIP, so the top of a tied plateau is the conservative end and
    the bottom is the all-EJECT one. The scan takes the top.
    """

    table = build_meeting_table(_CORPUS)
    report = fo6_rebaseline(table)
    assert report.decision_head is not None
    scan = report.decision_head.scans[0]
    tied = [tau for tau, correct in scan.curve if correct == scan.tuned_correct]
    assert len(tied) > 1, "no tie on this corpus — the tie-break would be untested"
    assert scan.tuned_tau == max(tied)
    assert scan.tuned_tau == 0.25  # was 0.20, the all-EJECT end of the same tie


def test_the_ranking_channel_is_untouched_by_the_tie_break() -> None:
    """Axis 2 does not move when the decision census does.

    FO-6's top-1 comes from ``ranking[0]``, a probability sort that never sees tau,
    so demoting the decision head cannot move the comparator floor the GO bar reads.
    Proven by re-scoring the SAME corpus under the OLD lowest-tied-tau rule: the
    ranking channels are identical, the decision census is not.
    """

    table = build_meeting_table(_CORPUS)
    new = fo6_rebaseline(table)
    old = run_surrogate_fidelity(
        table, _LowestTiedTauFo6, model_name="fo6-physical-logistic"
    )

    # Ranking + calibration: identical under both tie-breaks.
    assert old.top1 == new.top1
    assert old.top1_hits == new.top1_hits
    assert old.top2 == new.top2
    assert old.brier == new.brier
    assert old.ece == new.ece
    # ...and the tie-break really did select a different tau, so the control is not
    # vacuous. (The corpus TEST side happens to decide identically at 0.20 and 0.25;
    # the samples set below is where the census actually moves.)
    assert old.decision_head is None  # the plain factory publishes no head
    assert new.decision_head is not None
    assert new.decision_head.scans[0].tuned_tau == 0.25


def test_the_tie_break_moves_the_decision_census_but_not_the_ranking() -> None:
    """The asymmetry, on the set where the census actually moves.

    On ``replays/samples/9p2i`` the higher tie-break skips 3 more true ejections
    (94 -> 97) and its binary accuracy falls, while every ranking and calibration
    channel is bit-identical — the whole content of "the tuned head enters no axis
    of the bar".
    """

    table = build_meeting_table(_NINE)
    new = fo6_rebaseline(table)
    old = run_surrogate_fidelity(
        table, _LowestTiedTauFo6, model_name="fo6-physical-logistic"
    )

    assert old.top1 == new.top1
    assert old.top2 == new.top2
    assert old.brier == new.brier
    assert old.ece == new.ece

    assert old.ejection_predicted_skips == 94
    assert new.ejection_predicted_skips == 97
    assert new.skip_vs_eject_accuracy < old.skip_vs_eject_accuracy


# --------------------------------------------------------------------------- #
# The honest ceiling — a measurement                                          #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("sample_dir", [_NINE, _FOUR])
def test_honest_ceiling_is_a_bounded_measurement(sample_dir: Path) -> None:
    """The ceiling is derived from the bytes and bounded; voice = 1 - reachable."""

    views = build_meeting_views(build_meeting_table(sample_dir))
    ceiling = compute_honest_ceiling(views)
    ejections = sum(1 for v in views if v.is_ejection)

    assert ceiling.ejections_total == ejections
    assert 0 <= ceiling.reachable <= ceiling.ejections_total
    assert 0.0 <= ceiling.max_achievable_top1 <= 1.0
    assert ceiling.max_achievable_top1 == pytest.approx(
        ceiling.reachable / ejections if ejections else 0.0
    )
    assert ceiling.voice_driven_share == pytest.approx(
        1.0 - ceiling.max_achievable_top1
    )


def test_honest_ceiling_bounds_the_fo6_top1() -> None:
    """A physical+belief surrogate cannot beat its own reachability ceiling.

    FO-6 uses a strict subset of the reconstructed signal (six raw physical counts,
    no belief accumulator, no flags), so its achieved top-1 must sit at or below the
    measured ceiling — the ceiling is the maximum achievable, not a target.
    """

    report = fo6_rebaseline(build_meeting_table(_NINE))
    assert report.top1 <= report.honest_ceiling.max_achievable_top1


# --------------------------------------------------------------------------- #
# Harness mechanics — model-agnostic, verified with a synthetic oracle         #
# --------------------------------------------------------------------------- #


class _OracleModel:
    """A synthetic model that always ranks + ejects the true target (test only).

    Proves the harness's ranking / decision / calibration wiring is correct and
    model-agnostic: an oracle must score top-1 == 1.0 on ejection meetings and a
    perfect SKIP-vs-eject accuracy.
    """

    def fit(self, meetings: Sequence[MeetingView]) -> None:  # noqa: D401 - test stub
        return None

    def predict(self, meeting: MeetingView) -> MeetingPrediction:
        target = meeting.ejected
        ranking = tuple(
            sorted(
                meeting.candidates,
                key=lambda cand: (0 if cand == target else 1, cand),
            )
        )
        prob = {cand: (1.0 if cand == target else 0.0) for cand in meeting.candidates}
        return MeetingPrediction(ranking=ranking, ejected=target, ejection_prob=prob)


def test_harness_is_model_agnostic_oracle_scores_perfectly() -> None:
    """A perfect oracle model drives the harness to top-1 = 1 and acc = 1."""

    table = build_meeting_table(_FOUR)
    report = run_surrogate_fidelity(table, _OracleModel, model_name="oracle")
    assert report.top1 == pytest.approx(1.0)
    assert report.top2 == pytest.approx(1.0)
    assert report.skip_vs_eject_accuracy == pytest.approx(1.0)
    assert not report.degenerates_to_skip
    assert report.brier == pytest.approx(0.0)


class _BrokenModel:
    """A model that drops a candidate from its ranking (test only)."""

    def fit(self, meetings: Sequence[MeetingView]) -> None:  # noqa: D401 - test stub
        return None

    def predict(self, meeting: MeetingView) -> MeetingPrediction:
        # Drop the last candidate — ranking is no longer a permutation.
        truncated = meeting.candidates[:-1]
        return MeetingPrediction(
            ranking=truncated,
            ejected=None,
            ejection_prob={cand: 0.0 for cand in truncated},
        )


def test_malformed_prediction_is_rejected() -> None:
    """A model omitting a candidate fails loud rather than scoring meaningless metrics."""

    table = build_meeting_table(_FOUR)
    with pytest.raises(ValueError, match="permutation"):
        run_surrogate_fidelity(table, _BrokenModel, model_name="broken")


class _AlwaysEjectFirstModel:
    """A model that always ejects the first candidate (test only).

    Ejects on EVERY meeting (never SKIP) and names ``candidates[0]`` — so its
    SKIP-vs-eject decision is right on every ejection meeting regardless of target,
    but its top-1 is near zero. Proves the binary decision metric is decoupled from
    the exact-target top-1 channel.
    """

    def fit(self, meetings: Sequence[MeetingView]) -> None:  # noqa: D401 - test stub
        return None

    def predict(self, meeting: MeetingView) -> MeetingPrediction:
        leader = meeting.candidates[0]
        return MeetingPrediction(
            ranking=meeting.candidates,
            ejected=leader,
            ejection_prob={
                cand: (1.0 if cand == leader else 0.0) for cand in meeting.candidates
            },
        )


def test_skip_vs_eject_is_binary_not_exact_target() -> None:
    """An always-eject model scores the binary decision at the always-eject baseline.

    Ejecting the wrong player is still a correct EJECT decision (Codex review), so a
    model that ejects every meeting matches the always-eject baseline on
    ``skip_vs_eject_accuracy`` while its top-1 stays far lower — the decision channel
    is not a duplicate of top-1.
    """

    table = build_meeting_table(_NINE)
    report = run_surrogate_fidelity(
        table, _AlwaysEjectFirstModel, model_name="always-eject-first"
    )
    assert report.predicted_skips == 0
    assert report.skip_vs_eject_accuracy == pytest.approx(report.always_eject_baseline)
    assert report.top1 < report.skip_vs_eject_accuracy


def test_one_meeting_view_per_committed_meeting() -> None:
    """The meeting-level views collapse the (meeting, voter) rows one-per-meeting."""

    table = build_meeting_table(_NINE)
    views = build_meeting_views(table)
    assert len(views) == table.meetings_total
    assert len({(v.seed, v.meeting_id) for v in views}) == table.meetings_total


def test_model_factory_must_be_callable() -> None:
    """A non-callable model factory fails loud (no silent misuse)."""

    table = build_meeting_table(_FOUR)
    with pytest.raises(TypeError):
        run_surrogate_fidelity(table, object(), model_name="bad")
