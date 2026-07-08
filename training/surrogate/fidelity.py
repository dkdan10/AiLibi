"""The surrogate fidelity harness — by-GAME CV + the honest ceiling (Task 15.11).

The instrument the phase judges ALL meeting models with
(audits/post-phase-14-ML-training-signal.md §5.5): never a single headline number,
always the four channels together —

* **top-1 / top-2 ejected-target ranking** — the continuous suspicion-rank signal
  (does the model rank the actually-ejected player first / in its top two).
* **SKIP-vs-eject decision accuracy** — the decision FO-6 failed at (its binary head
  degenerates to always-SKIP, §5.2).
* **Brier / ECE calibration** — of the model's per-candidate ejection confidence
  against the binary ejected outcome (Brier is numeric-probability fidelity, the
  ranking is ordering — arXiv:2504.18278 says report both; WOLF reports Brier
  ~0.26-0.29 for werewolf vote prediction, arXiv:2512.09187).

All under **by-GAME cross-validation** — a game's meetings never split across folds
(by-meeting CV would leak a game's cross-meeting belief state between train and
test, §5.5). When the set ships a committed ``splits.json`` the harness honours it;
otherwise it derives K deterministic by-game folds.

Plus the **HONEST CEILING** (§2.2): the measured voice-driven share of ejections a
physical+belief surrogate structurally cannot see. The crew's entire deduction
signal under same-room-only vision is physical (sightings, kill-proximity) plus the
cross-meeting belief accumulator; a conviction that formed from THIS meeting's spoken
narrative — no flag, no proximity, no pre-meeting suspicion lead — is invisible to a
training-time surrogate (no LLM → no current transcript). The ceiling is a
MEASUREMENT from the committed bytes, stated as the surrogate's maximum achievable
top-1, NOT a target to chase.

This module also RE-RUNS the FO-6 logistic (the failed prior,
``experiments/lab/ml_spike/fo6_learned_vote_surrogate.py`` — re-run here, never
imported: the spike is mypy-excluded) under this harness to pin the true prior
baseline and make its always-SKIP collapse explicit
(:func:`fo6_rebaseline`).

The GO/NO-GO wiring on top of this report is Task 15.13's region — this module ships
only the measurement.

Public surface (stable — downstream tasks import these):
:class:`SurrogateFidelityReport`, :class:`HonestCeiling`,
:func:`run_surrogate_fidelity`, :func:`fo6_rebaseline`.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict

from agents.memory.beliefs import (
    BODY_PROXIMITY_SUSPICION_DELTA,
    CONTRADICTION_SUSPICION_DELTA,
    WEAK_CONTRADICTION_SUSPICION_DELTA,
)
from engine.entities import PlayerId
from training.surrogate.dataset import MeetingTable, MeetingTableRow

# The by-game CV fold count when the set ships no committed ``splits.json``. Five is
# the §5.5 default (WOLF-scale corpora); the leakage guarantee holds for any K.
DEFAULT_CV_FOLDS: int = 5

# The ECE reliability-bin count (10 equal-width bins on [0, 1], the standard).
ECE_BINS: int = 10

# The FO-6 physical feature order (``experiments/lab/ml_spike/
# fo6_learned_vote_surrogate.py`` Part B — the honest LLM-free set): witnessed,
# isolation, seen-at-kill, reporter, meeting-index, alive-count. Re-run, not imported.
FO6_FEATURE_NAMES: tuple[str, ...] = (
    "witnessed",
    "isolation",
    "seen_at_kill",
    "is_reporter",
    "meeting_index",
    "alive_count",
)


@dataclass(frozen=True)
class MeetingView:
    """One meeting reduced to the harness's ranking/decision inputs (Task 15.11).

    Built from the table's (meeting, voter) rows: the candidate physical features are
    voter-independent (identical across a meeting's voters), so they are read off the
    rows once; ``public_suspicion`` is the cross-meeting belief accumulator toward
    each candidate from a NON-self perspective (crew voters share the public
    evidence). ``ejected`` is ``None`` on a SKIP meeting.
    """

    seed: int
    meeting_id: str
    meeting_index: int
    candidates: tuple[PlayerId, ...]
    ejected: PlayerId | None
    features: dict[PlayerId, dict[str, float]]
    public_suspicion: dict[PlayerId, float]
    recon_suspicion: dict[PlayerId, float]
    flag_legible: frozenset[PlayerId]
    proximity_legible: frozenset[PlayerId]

    @property
    def is_ejection(self) -> bool:
        return self.ejected is not None


@dataclass(frozen=True)
class MeetingPrediction:
    """A model's output for one meeting (Task 15.11).

    ``ranking`` orders every living candidate by descending suspicion (top-1 is the
    model's most-suspected). ``ejected`` is the model's SKIP-vs-eject decision
    (``None`` == SKIP). ``ejection_prob`` is the per-candidate P(this candidate is
    ejected) the calibration channel scores against the binary outcome.
    """

    ranking: tuple[PlayerId, ...]
    ejected: PlayerId | None
    ejection_prob: dict[PlayerId, float]


@runtime_checkable
class MeetingModel(Protocol):
    """The interface every meeting model the harness judges implements.

    :func:`fit` trains on the fold's TRAIN meetings; :func:`predict` scores one test
    meeting into a :class:`MeetingPrediction`. FO-6 (:class:`Fo6Logistic`) is the
    committed implementation; the 15.13 ballot surrogate implements the same two
    methods (its per-candidate ejection prob derives from predicted ballots fed to
    the real tally).
    """

    def fit(self, meetings: Sequence[MeetingView]) -> None: ...

    def predict(self, meeting: MeetingView) -> MeetingPrediction: ...


def build_meeting_views(table: MeetingTable) -> list[MeetingView]:
    """Reduce the (meeting, voter) table to per-meeting ranking/decision views.

    Groups rows by ``(seed, meeting_id)`` in table order (already sorted), reads the
    voter-independent physical candidate features off the group, and derives the
    public belief suspicion per candidate as the max over the OTHER voters' rows (a
    candidate never holds a belief row about itself, so its own-row 0.5 is excluded).
    """

    by_meeting: dict[tuple[int, str], list[MeetingTableRow]] = defaultdict(list)
    for row in table.rows:
        by_meeting[(row.seed, row.meeting_id)].append(row)

    views: list[MeetingView] = []
    for (seed, meeting_id), rows in by_meeting.items():
        sample = rows[0]
        candidates = tuple(c.candidate for c in sample.candidates)
        alive_count = float(len(candidates))
        features: dict[PlayerId, dict[str, float]] = {}
        flag_legible: set[PlayerId] = set()
        proximity_legible: set[PlayerId] = set()
        for feat in sample.candidates:
            features[feat.candidate] = {
                "witnessed": float(feat.witnessed),
                "isolation": float(feat.isolation),
                "seen_at_kill": float(feat.seen_at_kill),
                "is_reporter": float(feat.is_reporter),
                "meeting_index": float(sample.meeting_index),
                "alive_count": alive_count,
                "strong_flags": float(feat.strong_flags),
                "weak_flags": float(feat.weak_flags),
                "vent_flags": float(feat.vent_flags),
                "body_proximity": float(feat.body_proximity),
                "task_submissions": float(feat.task_submissions),
                "move_count": float(feat.move_count),
            }
            if feat.strong_flags + feat.weak_flags + feat.vent_flags > 0:
                flag_legible.add(feat.candidate)
            if feat.seen_at_kill or feat.body_proximity:
                proximity_legible.add(feat.candidate)
        # Public belief suspicion toward each candidate: the max over voters who are
        # NOT that candidate (a candidate's own row carries the neutral 0.5 self
        # prior). Crew voters share the public evidence, so the max is the public
        # accumulator; excluding self avoids reading the neutral self-row.
        public: dict[PlayerId, float] = {cand: 0.0 for cand in candidates}
        seen: dict[PlayerId, bool] = {cand: False for cand in candidates}
        for row in rows:
            for feat in row.candidates:
                cid = feat.candidate
                if cid == row.voter:
                    continue
                if not seen[cid] or feat.belief_suspicion > public[cid]:
                    public[cid] = feat.belief_suspicion
                    seen[cid] = True
        for cand in candidates:
            if not seen[cand]:
                public[cand] = 0.5
        # Best-case reconstructed pre-meeting suspicion per candidate: the public
        # belief accumulator PLUS the flag / proximity channels weighted by the
        # REAL belief-fold deltas (agents/memory/beliefs.py) — vent_sighting is a
        # strong flag (Task 15.4). This is the sharpest ranking a physical+belief
        # surrogate could form from the pre-meeting bytes; the honest ceiling reads
        # its strict argmax (:func:`compute_honest_ceiling`).
        recon: dict[PlayerId, float] = {}
        for cand in candidates:
            feats = features[cand]
            recon[cand] = (
                public[cand]
                + CONTRADICTION_SUSPICION_DELTA * feats["strong_flags"]
                + CONTRADICTION_SUSPICION_DELTA * feats["vent_flags"]
                + WEAK_CONTRADICTION_SUSPICION_DELTA * feats["weak_flags"]
                + BODY_PROXIMITY_SUSPICION_DELTA * feats["body_proximity"]
                + BODY_PROXIMITY_SUSPICION_DELTA * feats["seen_at_kill"]
            )
        views.append(
            MeetingView(
                seed=seed,
                meeting_id=meeting_id,
                meeting_index=sample.meeting_index,
                candidates=candidates,
                ejected=sample.ejected_player_id,
                features=features,
                public_suspicion=public,
                recon_suspicion=recon,
                flag_legible=frozenset(flag_legible),
                proximity_legible=frozenset(proximity_legible),
            )
        )
    return views


class Fo6Logistic:
    """The re-run FO-6 physical vote-surrogate (Task 15.11; the failed prior).

    A deterministic standardized logistic regression on the six LLM-free physical
    features (:data:`FO6_FEATURE_NAMES`) per candidate, label ``1`` iff the candidate
    is the ejected one — the exact structure of
    ``experiments/lab/ml_spike/fo6_learned_vote_surrogate.py`` Part B, re-run here
    (never imported: the spike is mypy-excluded). Full-batch gradient descent (no
    RNG — the spike's SGD shuffle is replaced by a deterministic full pass so the
    re-baseline is replay-stable). The SKIP threshold is tuned on the training
    meetings exactly as FO-6 tuned it; the harness then surfaces that the tuned
    decision head degenerates to always-SKIP.
    """

    def __init__(self, *, epochs: int = 300, lr: float = 0.3) -> None:
        self._epochs = epochs
        self._lr = lr
        self._mean: NDArray[np.float64] | None = None
        self._std: NDArray[np.float64] | None = None
        self._weights: NDArray[np.float64] | None = None
        self._bias: float = 0.0
        self._tau: float = 0.5

    def _matrix(self, meetings: Sequence[MeetingView]) -> NDArray[np.float64]:
        rows = [
            [meeting.features[cand][name] for name in FO6_FEATURE_NAMES]
            for meeting in meetings
            for cand in meeting.candidates
        ]
        if not rows:
            return np.zeros((0, len(FO6_FEATURE_NAMES)), dtype=np.float64)
        return np.asarray(rows, dtype=np.float64)

    def _labels(self, meetings: Sequence[MeetingView]) -> NDArray[np.float64]:
        labels = [
            1.0 if cand == meeting.ejected else 0.0
            for meeting in meetings
            for cand in meeting.candidates
        ]
        return np.asarray(labels, dtype=np.float64)

    def fit(self, meetings: Sequence[MeetingView]) -> None:
        matrix = self._matrix(meetings)
        labels = self._labels(meetings)
        if matrix.shape[0] == 0:
            self._weights = np.zeros(len(FO6_FEATURE_NAMES), dtype=np.float64)
            return
        mean = matrix.mean(axis=0)
        std = matrix.std(axis=0)
        std[std == 0.0] = 1.0
        standardized = (matrix - mean) / std
        weights = np.zeros(matrix.shape[1], dtype=np.float64)
        bias = 0.0
        n = float(matrix.shape[0])
        for _ in range(self._epochs):
            logits = standardized @ weights + bias
            probs = 1.0 / (1.0 + np.exp(-np.clip(logits, -30.0, 30.0)))
            error = probs - labels
            weights -= self._lr * (standardized.T @ error) / n
            bias -= self._lr * float(error.mean())
        self._mean = mean
        self._std = std
        self._weights = weights
        self._bias = bias
        self._tau = self._tune_threshold(meetings)

    def _prob(self, meeting: MeetingView) -> dict[PlayerId, float]:
        if self._weights is None or self._mean is None or self._std is None:
            return {cand: 0.0 for cand in meeting.candidates}
        out: dict[PlayerId, float] = {}
        for cand in meeting.candidates:
            vector = np.asarray(
                [meeting.features[cand][name] for name in FO6_FEATURE_NAMES],
                dtype=np.float64,
            )
            standardized = (vector - self._mean) / self._std
            logit = float(standardized @ self._weights + self._bias)
            out[cand] = 1.0 / (1.0 + float(np.exp(-max(min(logit, 30.0), -30.0))))
        return out

    def _tune_threshold(self, meetings: Sequence[MeetingView]) -> float:
        best_tau, best_acc = 0.5, -1.0
        for step in range(1, 20):
            tau = step / 20.0
            correct = 0
            for meeting in meetings:
                probs = self._prob(meeting)
                decision = self._decide(meeting, probs, tau)
                if decision == meeting.ejected:
                    correct += 1
            if correct > best_acc:
                best_acc, best_tau = float(correct), tau
        return best_tau

    @staticmethod
    def _decide(
        meeting: MeetingView, probs: dict[PlayerId, float], tau: float
    ) -> PlayerId | None:
        if not probs:
            return None
        leader = max(meeting.candidates, key=lambda cand: (probs[cand], cand))
        return leader if probs[leader] >= tau else None

    def predict(self, meeting: MeetingView) -> MeetingPrediction:
        probs = self._prob(meeting)
        ranking = tuple(
            sorted(meeting.candidates, key=lambda cand: (-probs[cand], cand))
        )
        ejected = self._decide(meeting, probs, self._tau)
        return MeetingPrediction(ranking=ranking, ejected=ejected, ejection_prob=probs)


class HonestCeiling(BaseModel):
    """The measured voice-driven ceiling on any physical+belief surrogate (frozen).

    Computed from the committed bytes (§2.2): over the set's EJECTION meetings, the
    fraction whose ejected target carries SOME pre-meeting-reconstructable
    discriminating signal — a contradiction flag (``flag_legible``), a physical
    placement (``proximity_legible``: seen-at-kill / body-proximity), or a strict
    pre-meeting belief-suspicion lead among living candidates (``belief_lead``).
    ``max_achievable_top1`` is the union share; ``voice_driven_share`` its complement
    — the ejections that formed from the current meeting's spoken narrative, which a
    training-time surrogate (no LLM, no current transcript) structurally cannot see.
    A MEASUREMENT, not a target.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ejections_total: int
    # Decomposition — the share of ejections whose target carries EACH pre-meeting
    # channel (informative; overlapping, so they do not sum to the headline).
    flag_present: int
    proximity_present: int
    belief_lead: int
    # The headline: ejections where the ejected target is the STRICT argmax of the
    # best-case reconstructed physical+belief suspicion (a physical+belief ranker
    # could top-1 it). Its complement is the voice-driven share.
    reachable: int
    max_achievable_top1: float
    voice_driven_share: float


def compute_honest_ceiling(views: Sequence[MeetingView]) -> HonestCeiling:
    """Measure the honest ceiling over a set's ejection meetings (§2.2).

    The headline ``max_achievable_top1`` is the share of ejections whose ejected
    target is the STRICT (unique) argmax of the best-case reconstructed physical +
    belief suspicion (:attr:`MeetingView.recon_suspicion`): the maximum top-1 any
    physical+belief surrogate could reach, since a flat tie (an early meeting with no
    prior evidence and no flag) is NOT uniquely rankable and correctly counts as
    unreachable. ``voice_driven_share`` is its complement — the ejections that formed
    from the current meeting's spoken narrative, invisible to a training-time
    surrogate (§2.2). The ``*_present`` / ``belief_lead`` counts decompose WHICH
    channel carried each ejected target (overlapping).
    """

    ejections = [view for view in views if view.is_ejection]
    total = len(ejections)
    flag = 0
    proximity = 0
    belief = 0
    reachable = 0
    for view in ejections:
        target = view.ejected
        assert target is not None  # is_ejection guards this
        flag += int(target in view.flag_legible)
        proximity += int(target in view.proximity_legible)
        belief += int(_is_strict_leader(view, view.public_suspicion, target))
        reachable += int(_is_strict_leader(view, view.recon_suspicion, target))
    return HonestCeiling(
        ejections_total=total,
        flag_present=flag,
        proximity_present=proximity,
        belief_lead=belief,
        reachable=reachable,
        max_achievable_top1=(reachable / total) if total else 0.0,
        voice_driven_share=(1.0 - reachable / total) if total else 0.0,
    )


def _is_strict_leader(
    view: MeetingView, scores: dict[PlayerId, float], target: PlayerId
) -> bool:
    """Whether ``target`` is the STRICT (unique) argmax of ``scores`` among candidates.

    A flat tie (every candidate at the neutral prior — the first meeting, no prior
    evidence, no flag) is NOT a strict lead, so an early voice-driven ejection
    correctly counts as unreachable by that channel.
    """

    target_score = scores[target]
    return all(
        scores[cand] < target_score for cand in view.candidates if cand != target
    )


class SurrogateFidelityReport(BaseModel):
    """A meeting model's by-GAME CV fidelity + the honest ceiling (Task 15.11 type).

    Reports the four channels TOGETHER (never a single headline): ``top1`` / ``top2``
    ejected-target ranking, ``skip_vs_eject_accuracy``, and ``brier`` / ``ece``
    calibration. ``degenerates_to_skip`` trips when the tuned decision head predicts
    SKIP on EVERY ejection meeting (the FO-6 always-SKIP collapse, §5.2); the
    predicted-decision census (``predicted_ejections`` / ``predicted_skips``) makes
    it concrete. ``honest_ceiling`` is the set's measured maximum achievable top-1.
    Signature stable per the task contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_name: str
    replay_set_dir: str
    games_total: int
    folds: int
    by_game_cv: bool
    meetings_scored: int
    ejection_meetings: int
    skip_meetings: int
    # Ranking (over ejection meetings — a SKIP meeting has no target to rank).
    top1: float
    top2: float
    top1_hits: int
    top2_hits: int
    # SKIP-vs-eject decision (over ALL scored meetings).
    skip_vs_eject_accuracy: float
    always_eject_baseline: float
    predicted_ejections: int
    predicted_skips: int
    correct_skip_decisions: int
    correct_eject_decisions: int
    # Of the TRUE ejection meetings, how many the decision head wrongly called SKIP.
    ejection_predicted_skips: int
    # The FO-6 always-SKIP collapse (§5.2): the tuned head calls SKIP on a MAJORITY
    # of true-ejection meetings AND does no better than the trivial always-eject
    # constant — the physical features cannot learn the SKIP/eject decision.
    degenerates_to_skip: bool
    # Calibration of the per-candidate ejection confidence (both, §5.5).
    brier: float
    ece: float
    # The honest ceiling (a measurement, not a target).
    honest_ceiling: HonestCeiling


def _game_folds(
    table: MeetingTable, *, folds: int
) -> tuple[list[tuple[frozenset[int], frozenset[int]]], bool]:
    """Deterministic by-GAME (train, test) fold pairs; honour ``splits.json``.

    When the table carries a committed split, returns the single (train ∪ val, test)
    pair it names — a by-game split by construction. Otherwise partitions the sorted
    game seeds into ``folds`` contiguous test blocks (train = the rest). Either way a
    game's seed lands wholly inside one test fold, so no meeting of a game is ever
    split across folds (the anti-leakage guarantee; asserted by the leakage test).
    """

    seeds = list(table.game_seeds())
    if table.splits is not None:
        test = frozenset(table.splits.test)
        train = frozenset(table.splits.train) | frozenset(table.splits.val)
        return [(train, test)], True
    k = max(1, min(folds, len(seeds)))
    blocks: list[tuple[frozenset[int], frozenset[int]]] = []
    for fold in range(k):
        test = frozenset(seeds[fold::k])
        train = frozenset(seeds) - test
        blocks.append((train, test))
    return blocks, True


def run_surrogate_fidelity(
    table: MeetingTable,
    model_factory: object,
    *,
    model_name: str,
    folds: int = DEFAULT_CV_FOLDS,
) -> SurrogateFidelityReport:
    """Judge a meeting model over ``table`` under by-GAME CV + the honest ceiling.

    ``model_factory`` is a zero-arg callable returning a fresh :class:`MeetingModel`
    (a new model is fit per fold on that fold's TRAIN games only). Pools the
    per-fold TEST predictions into the four fidelity channels and the decision
    census, and attaches the set's measured honest ceiling. Deterministic: the folds,
    the fit, and every metric are pure functions of the committed table.
    """

    if not callable(model_factory):
        raise TypeError("model_factory must be a zero-arg callable returning a model")
    views = build_meeting_views(table)
    views_by_seed: dict[int, list[MeetingView]] = defaultdict(list)
    for view in views:
        views_by_seed[view.seed].append(view)

    fold_pairs, by_game = _game_folds(table, folds=folds)

    top1_hits = 0
    top2_hits = 0
    ejection_meetings = 0
    predicted_ejections = 0
    predicted_skips = 0
    correct_skip = 0
    correct_eject = 0
    meetings_scored = 0
    ejection_pred_skips = 0
    brier_terms: list[float] = []
    calib: list[tuple[float, int]] = []

    for train_seeds, test_seeds in fold_pairs:
        train_views = [v for s in sorted(train_seeds) for v in views_by_seed[s]]
        test_views = [v for s in sorted(test_seeds) for v in views_by_seed[s]]
        if not test_views:
            continue
        model = model_factory()
        if not isinstance(model, MeetingModel):
            raise TypeError(
                f"model_factory produced {type(model)!r}, which is not a MeetingModel"
            )
        model.fit(train_views)
        for view in test_views:
            meetings_scored += 1
            prediction = model.predict(view)
            true_eject = view.ejected
            predicted = prediction.ejected
            if predicted is None:
                predicted_skips += 1
            else:
                predicted_ejections += 1
            if predicted == true_eject or (predicted is None and true_eject is None):
                if true_eject is None:
                    correct_skip += 1
                else:
                    correct_eject += 1
            if view.is_ejection:
                ejection_meetings += 1
                if prediction.ranking and prediction.ranking[0] == true_eject:
                    top1_hits += 1
                if true_eject in prediction.ranking[:2]:
                    top2_hits += 1
                if predicted is None:
                    ejection_pred_skips += 1
            for cand in view.candidates:
                prob = prediction.ejection_prob.get(cand, 0.0)
                label = 1 if cand == true_eject else 0
                brier_terms.append((prob - label) ** 2)
                calib.append((prob, label))

    skip_meetings = meetings_scored - ejection_meetings
    brier = float(np.mean(brier_terms)) if brier_terms else 0.0
    ece = _expected_calibration_error(calib)
    decision_accuracy = (
        (correct_skip + correct_eject) / meetings_scored if meetings_scored else 0.0
    )
    always_eject_baseline = (
        ejection_meetings / meetings_scored if meetings_scored else 0.0
    )
    return SurrogateFidelityReport(
        model_name=model_name,
        replay_set_dir=table.replay_set_dir,
        games_total=table.games_total,
        folds=len(fold_pairs),
        by_game_cv=by_game,
        meetings_scored=meetings_scored,
        ejection_meetings=ejection_meetings,
        skip_meetings=skip_meetings,
        top1=(top1_hits / ejection_meetings) if ejection_meetings else 0.0,
        top2=(top2_hits / ejection_meetings) if ejection_meetings else 0.0,
        top1_hits=top1_hits,
        top2_hits=top2_hits,
        skip_vs_eject_accuracy=decision_accuracy,
        always_eject_baseline=always_eject_baseline,
        predicted_ejections=predicted_ejections,
        predicted_skips=predicted_skips,
        correct_skip_decisions=correct_skip,
        correct_eject_decisions=correct_eject,
        ejection_predicted_skips=ejection_pred_skips,
        # Always-SKIP collapse: the decision head skips the MAJORITY of true
        # ejection meetings AND is no better than the trivial always-eject constant.
        degenerates_to_skip=ejection_meetings > 0
        and 2 * ejection_pred_skips > ejection_meetings
        and decision_accuracy <= always_eject_baseline,
        brier=brier,
        ece=ece,
        honest_ceiling=compute_honest_ceiling(views),
    )


def _expected_calibration_error(calib: Sequence[tuple[float, int]]) -> float:
    """Expected calibration error over 10 equal-width probability bins."""

    if not calib:
        return 0.0
    total = len(calib)
    error = 0.0
    for b in range(ECE_BINS):
        low = b / ECE_BINS
        high = (b + 1) / ECE_BINS
        if b == ECE_BINS - 1:
            members = [(p, y) for p, y in calib if low <= p <= high]
        else:
            members = [(p, y) for p, y in calib if low <= p < high]
        if not members:
            continue
        avg_conf = sum(p for p, _ in members) / len(members)
        avg_acc = sum(y for _, y in members) / len(members)
        error += (len(members) / total) * abs(avg_conf - avg_acc)
    return error


def fo6_rebaseline(
    table: MeetingTable, *, folds: int = DEFAULT_CV_FOLDS
) -> SurrogateFidelityReport:
    """Re-run the FO-6 physical logistic under this harness (§2.1, §5.2).

    Pins the true prior baseline: FO-6's headline top-1 64% collapsed to 26%/43% on
    baseline 2, and its binary head degenerates to always-SKIP. This runs the same
    six-feature logistic (re-implemented, :class:`Fo6Logistic` — the spike is
    mypy-excluded and never imported) under by-GAME CV, surfacing the ranking, the
    always-SKIP collapse, and the calibration TOGETHER. FO-6 predicts ejections, not
    ballots, so — unlike the 15.13 ballot surrogate, whose decision comes from the
    real tally at ``meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD`` (0.60) —
    its decision head is its own tuned threshold, which is exactly what collapses.
    """

    return run_surrogate_fidelity(
        table,
        Fo6Logistic,
        model_name="fo6-physical-logistic",
        folds=folds,
    )


__all__ = [
    "DEFAULT_CV_FOLDS",
    "FO6_FEATURE_NAMES",
    "Fo6Logistic",
    "HonestCeiling",
    "MeetingModel",
    "MeetingPrediction",
    "MeetingView",
    "SurrogateFidelityReport",
    "build_meeting_views",
    "compute_honest_ceiling",
    "fo6_rebaseline",
    "run_surrogate_fidelity",
]
