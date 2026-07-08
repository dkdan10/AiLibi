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

from training.surrogate.dataset import build_meeting_table
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
    fold_pairs, by_game = _game_folds(table, folds=5)
    assert by_game

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


def test_committed_splits_produce_a_single_by_game_fold(tmp_path: Path) -> None:
    """A committed ``splits.json`` yields one by-game (train, test) fold."""

    splits_file = tmp_path / "splits.json"
    splits_file.write_text('{"train": [0, 1, 2, 3], "val": [4], "test": [5, 6]}')
    table = build_meeting_table(_FOUR, splits_path=splits_file)
    fold_pairs, by_game = _game_folds(table, folds=5)
    assert by_game
    assert len(fold_pairs) == 1
    train, test = fold_pairs[0]
    assert test == frozenset({5, 6})
    assert {0, 1, 2, 3, 4} <= train
    assert train.isdisjoint(test)


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
