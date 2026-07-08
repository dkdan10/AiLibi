"""Tests for the surrogate fidelity harness (Task 15.11).

Pins on the committed baseline-3 bytes: by-GAME cross-validation never splits a
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

from training.surrogate.dataset import (
    MeetingTable,
    SurrogateSplits,
    build_meeting_table,
)
from training.surrogate.fidelity import (
    MeetingPrediction,
    MeetingView,
    _game_folds,
    build_meeting_views,
    compute_honest_ceiling,
    fo6_rebaseline,
    run_surrogate_fidelity,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


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

    Its top-1 clears the ~1/9 base rate (the physical rank has SOME signal) but its
    binary decision head is worse than the trivial always-eject constant and skips
    the majority of true ejection meetings — the collapse the single top-1 number
    hid.
    """

    report = fo6_rebaseline(build_meeting_table(_NINE))
    assert report.model_name == "fo6-physical-logistic"
    assert report.top1 > 1.0 / 9.0  # beats the per-candidate base rate
    assert report.degenerates_to_skip
    assert report.skip_vs_eject_accuracy < report.always_eject_baseline
    assert 2 * report.ejection_predicted_skips > report.ejection_meetings


def test_fidelity_runs_on_the_small_preset() -> None:
    """The harness runs on the 4p1i preset (its small-set headline top-1 is high)."""

    report = fo6_rebaseline(build_meeting_table(_FOUR))
    assert report.meetings_scored > 0
    assert report.top1 > 0.0


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
