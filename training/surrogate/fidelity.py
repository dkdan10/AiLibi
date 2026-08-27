"""FROZEN (Phase 19 tier map, training/README.md): evidence reader; instrument frozen.
Bug fixes and evidence readers only; no new search.

The surrogate fidelity harness — by-GAME CV + the honest ceiling (Task 15.11).

The instrument the phase judges ALL meeting models with
(audits/post-phase-14-ML-training-signal.md §5.5): never a single headline number,
always the four channels together —

* **top-1 / top-2 ejected-target ranking** — the continuous suspicion-rank signal
  (does the model rank the actually-ejected player first / in its top two).
* **SKIP-vs-eject decision accuracy** — the decision FO-6 failed at (its binary head
  degenerates to always-SKIP, §5.2).
* **Brier / ECE calibration** — on two channels, both reported: the model's
  per-candidate ejection confidence against the binary ejected outcome, AND the
  recorded **ballot confidences** (each non-SKIP voter's stated confidence vs
  whether its named target was ejected — the WOLF vote-prediction channel, Brier
  ~0.26-0.29, arXiv:2512.09187). Brier is numeric-probability fidelity, the ranking
  is ordering — arXiv:2504.18278 says report both.

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
from typing import Final, Literal, Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict

from agents.memory.beliefs import CONTRADICTION_RENDER_CEIL
from engine.entities import PlayerId
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
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
    rows once; ``public_suspicion`` is the strongest NON-self voter's full pre-meeting
    belief row toward each candidate (the real evidence fold plus event-time
    perception pins, Rule-5 decayed — the max over voters, since the sharpest-informed
    voter's ballot is what a surrogate could ride). ``ejected`` is ``None`` on a SKIP
    meeting.
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

    ``plurality_confidence`` is the quantity the REAL tally gates an ejection on
    (``meetings.voting.tally_ballots`` rule 4): the MAX confidence among the
    predicted ballots naming the single non-SKIP plurality target, or ``0.0`` when
    the predicted tally reaches no such target (SKIP leads, or the top is tied — the
    confidence gate is then never consulted). It is deliberately NOT
    ``ejection_prob``, which is a mean of per-voter target-probability mass. A
    ballot-free model leaves it ``None``: the cell is unmeasured there, not zero.
    """

    ranking: tuple[PlayerId, ...]
    ejected: PlayerId | None
    ejection_prob: dict[PlayerId, float]
    plurality_confidence: float | None = None


def _validate_prediction(
    prediction: MeetingPrediction, meeting: MeetingView, *, model_name: str
) -> None:
    """Reject a malformed model prediction before it is scored (Codex review).

    The harness must fail loud, not silently produce meaningless top-k / Brier / ECE
    numbers, when a model (e.g. the 15.13 surrogate) emits a broken prediction
    (AGENTS.md "no silent fallbacks"). Enforces that ``ranking`` is a PERMUTATION of
    the meeting's living candidates, ``ejected`` is a living candidate or ``None``
    (SKIP), and ``ejection_prob`` covers exactly those candidates with values in
    ``[0, 1]``.
    """

    candidates = frozenset(meeting.candidates)
    where = f"model {model_name!r} meeting {meeting.seed}:{meeting.meeting_id}"
    if len(prediction.ranking) != len(meeting.candidates) or (
        frozenset(prediction.ranking) != candidates
    ):
        raise ValueError(
            f"{where}: ranking {prediction.ranking} is not a permutation of the "
            f"living candidates {tuple(meeting.candidates)}"
        )
    if prediction.ejected is not None and prediction.ejected not in candidates:
        raise ValueError(
            f"{where}: ejected {prediction.ejected!r} is not a living candidate or None"
        )
    if frozenset(prediction.ejection_prob) != candidates:
        raise ValueError(
            f"{where}: ejection_prob keys {sorted(prediction.ejection_prob)} != "
            f"living candidates {sorted(candidates)}"
        )
    for cand, prob in prediction.ejection_prob.items():
        if not 0.0 <= prob <= 1.0:
            raise ValueError(
                f"{where}: ejection_prob[{cand!r}] = {prob} is outside [0, 1]"
            )
    confidence = prediction.plurality_confidence
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise ValueError(
            f"{where}: plurality_confidence = {confidence} is outside [0, 1]"
        )


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
        # The perception pins (``witnessed_kill`` / ``witnessed_vent`` /
        # ``body_proximity``) are VOTER-LOCAL (only the perceiving voter's row
        # carries them, Codex review), so a meeting-level signal is the OR across
        # voters — "at least one voter holds this evidence", which is what a
        # ballot-predicting surrogate could ride (that voter's ballot names the
        # target). Every other physical column is voter-independent and read off
        # any row.
        witnessed_kill_any = {
            c.candidate for row in rows for c in row.candidates if c.witnessed_kill
        }
        witnessed_vent_any = {
            c.candidate for row in rows for c in row.candidates if c.witnessed_vent
        }
        body_proximity_any = {
            c.candidate for row in rows for c in row.candidates if c.body_proximity
        }
        features: dict[PlayerId, dict[str, float]] = {}
        flag_legible: set[PlayerId] = set()
        proximity_legible: set[PlayerId] = set()
        for feat in sample.candidates:
            cid = feat.candidate
            features[cid] = {
                "witnessed": float(feat.witnessed),
                "isolation": float(feat.isolation),
                "seen_at_kill": float(feat.seen_at_kill),
                "witnessed_kill": float(cid in witnessed_kill_any),
                "witnessed_vent": float(cid in witnessed_vent_any),
                "is_reporter": float(feat.is_reporter),
                "meeting_index": float(sample.meeting_index),
                "alive_count": alive_count,
                "strong_flags": float(feat.strong_flags),
                "weak_flags": float(feat.weak_flags),
                "vent_flags": float(feat.vent_flags),
                "contradiction_lift": float(feat.contradiction_lift),
                "body_proximity": float(cid in body_proximity_any),
                "task_submissions": float(feat.task_submissions),
                "move_count": float(feat.move_count),
            }
            if feat.strong_flags + feat.weak_flags + feat.vent_flags > 0:
                flag_legible.add(cid)
            if (
                feat.seen_at_kill
                or cid in body_proximity_any
                or cid in witnessed_kill_any
                or cid in witnessed_vent_any
            ):
                proximity_legible.add(cid)
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
        # Best-case reconstructed pre-meeting suspicion per candidate: the PRIOR
        # is the strongest voter's real pre-meeting belief row (``public`` — the
        # table's ``belief_suspicion`` already carries the perception pins
        # ingested at event time AND their Rule-5 decay through the real fold, so
        # a stale pin is never re-applied at full strength; Codex review). The
        # vote-time transient is the table's ``contradiction_lift`` column —
        # RENDERED by the real ``apply_contradiction_rule`` (one delta per
        # (subject, claim) lift group, capped at one strong flag's worth) —
        # applied under the Task-14.10 certain-guilt render ceiling exactly as
        # production renders it: the flag-driven delta is capped at
        # ``max(prior, CONTRADICTION_RENDER_CEIL) - prior``, so a body+flag shape
        # renders ~0.97, never the 1.0 clamp, while a first-hand conclusive prior
        # already at the clamp (a fresh witnessed-kill pin) holds — the ceiling
        # bounds the lift, never the prior. This is the sharpest ranking a
        # physical+belief surrogate could form; the honest ceiling reads its
        # strict argmax (:func:`compute_honest_ceiling`).
        recon: dict[PlayerId, float] = {}
        for cand in candidates:
            prior = public[cand]
            lift = min(
                features[cand]["contradiction_lift"],
                max(prior, CONTRADICTION_RENDER_CEIL) - prior,
            )
            recon[cand] = min(1.0, prior + lift)
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


class ThresholdScan(BaseModel):
    """One FO-6 fit's tuned SKIP threshold and the whole curve it was chosen from.

    Published so a reader can see the margin the tuned tau actually won by.
    ``curve`` is every ``(tau, exact-target-correct)`` pair the scan visited over the
    fit-side meetings; ``fit_skip_meetings`` is the score a trivial always-SKIP head
    would post on the same population, so a tuned head that merely tracks the
    meeting mix is visible as a curve that plateaus at that count.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    fit_meetings: int
    fit_ejection_meetings: int
    fit_skip_meetings: int
    tuned_tau: float
    tuned_correct: int
    curve: tuple[tuple[float, int], ...]


class DecisionHeadReport(BaseModel):
    """What produced a model's SKIP-vs-eject decisions, and how it was tuned.

    ``label`` names the decision channel in the report itself so a published census
    cannot be read as more than it is. ``scans`` carries one
    :class:`ThresholdScan` per fold fit, in fold order.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str
    scans: tuple[ThresholdScan, ...]


# What FO-6's tuned binary head is, stated where its census is published: a tracker
# of the fit-side meeting mix, not a physical baseline. Its tau scan maximises
# exact-target accuracy over ALL meetings including SKIPs, so the trivial always-SKIP
# constant is its floor and it has flipped SKIP -> all-EJECT -> SKIP across three
# records (audits/audit-phase-20-baseline-7.md §10.2). FO-6's RANKING is unaffected
# and remains the bar's valid comparator floor.
FO6_DECISION_HEAD_LABEL: Final[str] = "meeting-mix tracker (not a physical baseline)"


class Fo6Logistic:
    """The re-run FO-6 physical vote-surrogate (Task 15.11; the failed prior).

    A deterministic standardized logistic regression on the six LLM-free physical
    features (:data:`FO6_FEATURE_NAMES`) per candidate, label ``1`` iff the candidate
    is the ejected one — the exact structure of
    ``experiments/lab/ml_spike/fo6_learned_vote_surrogate.py`` Part B, re-run here
    (never imported: the spike is mypy-excluded). Full-batch gradient descent (no
    RNG — the spike's SGD shuffle is replaced by a deterministic full pass so the
    re-baseline is replay-stable).

    The SKIP threshold is tuned on the training meetings exactly as FO-6 tuned it,
    and :attr:`threshold_scan` publishes the whole curve — the tuned head is a
    :data:`FO6_DECISION_HEAD_LABEL`, not a physical prior. The RANKING is
    threshold-independent (:meth:`predict` sorts by probability; tau touches only
    ``ejected``), which is why the bar's comparator floor reads the ranking alone.
    """

    def __init__(self, *, epochs: int = 300, lr: float = 0.3) -> None:
        self._epochs = epochs
        self._lr = lr
        self._mean: NDArray[np.float64] | None = None
        self._std: NDArray[np.float64] | None = None
        self._weights: NDArray[np.float64] | None = None
        self._bias: float = 0.0
        self._tau: float = 0.5
        self._scan: ThresholdScan | None = None

    @property
    def threshold_scan(self) -> ThresholdScan:
        """The tuned tau and its full curve; raises before :meth:`fit`."""

        if self._scan is None:
            raise RuntimeError("Fo6Logistic.threshold_scan read before fit")
        return self._scan

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
            # Never install a silent untrained model (Codex review; AGENTS.md
            # "no silent fallbacks") — an all-zero logistic would still emit
            # valid-looking fidelity numbers.
            raise ValueError(
                "Fo6Logistic.fit received no meetings; refusing to install an "
                "untrained (all-zero) model"
            )
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
        self._scan = self._tune_threshold(meetings)
        self._tau = self._scan.tuned_tau

    def _prob(self, meeting: MeetingView) -> dict[PlayerId, float]:
        if self._weights is None or self._mean is None or self._std is None:
            raise RuntimeError("Fo6Logistic.predict called before fit")
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

    def _tune_threshold(self, meetings: Sequence[MeetingView]) -> ThresholdScan:
        """Scan tau for maximum exact-target accuracy and publish the whole curve.

        Ties break toward the HIGHER tau: raising tau only ever converts an eject
        into a SKIP, so the top of a tied plateau is the conservative pole and the
        bottom is the all-EJECT one. The ascending scan therefore keeps replacing
        the incumbent on an equal score.
        """

        best_tau, best_correct = 0.5, -1
        curve: list[tuple[float, int]] = []
        for step in range(1, 20):
            tau = step / 20.0
            correct = 0
            for meeting in meetings:
                probs = self._prob(meeting)
                decision = self._decide(meeting, probs, tau)
                if decision == meeting.ejected:
                    correct += 1
            curve.append((tau, correct))
            if correct >= best_correct:
                best_correct, best_tau = correct, tau
        ejections = sum(1 for meeting in meetings if meeting.is_ejection)
        return ThresholdScan(
            fit_meetings=len(meetings),
            fit_ejection_meetings=ejections,
            fit_skip_meetings=len(meetings) - ejections,
            tuned_tau=best_tau,
            tuned_correct=best_correct,
            curve=tuple(curve),
        )

    @staticmethod
    def _decide(
        meeting: MeetingView, probs: dict[PlayerId, float], tau: float
    ) -> PlayerId | None:
        if not probs:
            return None
        # Smallest-id tie-break — the SAME leader ranking[0] carries (predict sorts
        # by (-prob, cand)) and the spike's own first-strict-max scan picked, so the
        # decision head and the ranking never disagree on an exact-probability tie.
        leader = min(meeting.candidates, key=lambda cand: (-probs[cand], cand))
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
    # SKIP-vs-eject BINARY decision accuracy (over ALL scored meetings): right when
    # the model's eject/skip choice matches the outcome, regardless of which player
    # it named (exact-target accuracy is the separate top-1 channel).
    skip_vs_eject_accuracy: float
    # The scored population's TWO trivial decision constants, published together so
    # a tuned head is read against both poles rather than only the eject one.
    always_eject_baseline: float
    always_skip_baseline: float
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
    # Calibration of the model's per-candidate ejection confidence (§5.5).
    brier: float
    ece: float
    # Calibration of the RECORDED ballot confidences (§5.5 "Brier/ECE on the ballot
    # confidences"; the WOLF vote-prediction channel, arXiv:2512.09187): over the
    # scored meetings' non-SKIP ballots, the voter's stated confidence vs whether
    # that ballot's named target was ejected. Model-independent (a property of the
    # committed ballots), so a badly-calibrated ballot surrogate is judged against
    # the real voters' calibration rather than only the post-tally ejection number.
    ballot_brier: float
    ballot_ece: float
    ballot_rows: int
    # Whether the tally's own eject gate is REACHABLE at all under this model:
    # ``decision_reachable_meetings`` counts the scored meetings whose predicted
    # plurality-target confidence clears
    # ``meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD``, and
    # ``plurality_confidence_meetings`` how many predictions carried that cell at all
    # — 0 for a ballot-free model, so an unmeasured channel never reads as a
    # measured zero.
    #
    # For a model that decides through the real tally this necessarily EQUALS
    # ``predicted_ejections`` — the tally ejects exactly when this gate clears — and
    # that is the point: it names WHICH gate holds the decision channel shut, on the
    # verdict, where someone decides whether axis 3 is worth a fit at all.
    decision_reachable_meetings: int
    decision_reachability: float
    plurality_confidence_meetings: int
    # What produced the decisions above (``None`` when the model publishes no
    # tuned head — the ballot surrogate decides through the real tally).
    decision_head: DecisionHeadReport | None = None
    # The honest ceiling (a measurement, not a target).
    honest_ceiling: HonestCeiling


def _game_folds(
    table: MeetingTable, *, folds: int
) -> list[tuple[frozenset[int], frozenset[int]]]:
    """Deterministic by-GAME (train, test) fold pairs; honour ``splits.json``.

    Every returned pair assigns whole GAMES to one side, so no meeting of a game
    is ever split across folds (the anti-leakage guarantee; asserted by the
    leakage test). The fold universe is ``table.seeds`` — EVERY recorded game,
    including no-meeting games (they contribute no scoreable views but must
    still be assignable, or a legitimate 15.12 split naming them would be
    falsely rejected).

    When the table carries a committed split, returns the single (train ∪ val,
    test) pair it names — VALIDATED first (Codex review): the fit set
    ``(train ∪ val)`` and the test set must be DISJOINT, together they must
    PARTITION every recorded game, and BOTH sides must carry at least one
    scoreable meeting (an empty — or all-no-meeting — test side scores
    nothing; an empty or all-no-meeting fit side would silently evaluate an
    untrained model). A 15.12 corpus mistake that put a seed on both sides
    would leak the same game's meetings into fitting and scoring — exactly the
    cross-meeting belief leak this by-game harness exists to prevent — so every
    violation fails loud rather than silently biasing the fidelity numbers.
    Otherwise partitions the sorted game seeds into ``folds`` strided test
    blocks (train = the rest).
    """

    seeds = list(table.game_seeds())
    if table.splits is not None:
        table_seeds = frozenset(seeds)
        test = frozenset(table.splits.test)
        train = frozenset(table.splits.train) | frozenset(table.splits.val)
        unknown = (train | test) - table_seeds
        if unknown:
            raise ValueError(
                f"splits.json references seeds absent from the table: {sorted(unknown)}"
            )
        omitted = table_seeds - (train | test)
        if omitted:
            raise ValueError(
                f"splits.json omits table games {sorted(omitted)}: they would be in "
                "neither train nor test, so the run would silently score a subset "
                "while reporting the full set — the split must partition every game"
            )
        overlap = train & test
        if overlap:
            raise ValueError(
                "splits.json leaks games across the fit/test boundary: seeds "
                f"{sorted(overlap)} are in both (train ∪ val) and test — the same "
                "game's meetings would be used for fitting and scoring"
            )
        if not test:
            raise ValueError("splits.json test set is empty; nothing to score")
        if not train:
            raise ValueError(
                "splits.json fit set (train ∪ val) is empty; the run would fit on "
                "nothing and score an untrained model as if it were by-game CV"
            )
        # Seed-set membership is necessary but not sufficient (Codex review): the
        # universe legitimately includes no-meeting games, so a side made ONLY of
        # them is non-empty yet carries zero scoreable meetings — the run would
        # return an all-zero report (test side) or fit([]) and score an untrained
        # model (fit side) while looking like a valid held-out fidelity run.
        scoreable = frozenset(row.seed for row in table.rows)
        if not (test & scoreable):
            raise ValueError(
                f"splits.json test set {sorted(test)} has no scoreable meetings: "
                "every test game ends before any meeting fires, so the run would "
                "score nothing while reporting a valid-looking held-out run"
            )
        if not (train & scoreable):
            raise ValueError(
                f"splits.json fit set (train ∪ val) {sorted(train)} has no "
                "scoreable meetings: every fit game ends before any meeting "
                "fires, so the run would fit on no rows and score an untrained "
                "model"
            )
        return [(train, test)]
    k = max(1, min(folds, len(seeds)))
    blocks: list[tuple[frozenset[int], frozenset[int]]] = []
    for fold in range(k):
        test = frozenset(seeds[fold::k])
        train = frozenset(seeds) - test
        blocks.append((train, test))
    return blocks


def run_surrogate_fidelity(
    table: MeetingTable,
    model_factory: object,
    *,
    model_name: str,
    folds: int = DEFAULT_CV_FOLDS,
) -> SurrogateFidelityReport:
    """Judge a meeting model over ``table`` under by-GAME CV + the honest ceiling.

    ``model_factory`` is a zero-arg callable returning a fresh :class:`MeetingModel`
    and EVERY fold RE-FITS: this function calls ``model.fit(train_views)`` on the
    model the factory produced, once per fold, so the reported numbers are never
    "frozen weights" — a factory that pre-installs an artifact-loaded predictor
    scores identically to one that does not, because
    :meth:`training.surrogate.ballots.BallotSurrogateModel.fit` REPLACES the
    installed predictor rather than refining it. Pools the
    per-fold TEST predictions into the four fidelity channels and the decision
    census, and attaches the honest ceiling measured over the SAME scored
    (test-side) meetings every other channel reports on — under K-fold CV that is
    every meeting (each game is tested exactly once); under a committed split it
    is the held-out test games only, so the ceiling bounds the score it is
    compared against rather than a different distribution (Codex review).
    Deterministic: the folds, the fit, and every metric are pure functions of the
    committed table.
    """

    if not callable(model_factory):
        raise TypeError("model_factory must be a zero-arg callable returning a model")
    views = build_meeting_views(table)
    views_by_seed: dict[int, list[MeetingView]] = defaultdict(list)
    for view in views:
        views_by_seed[view.seed].append(view)

    fold_pairs = _game_folds(table, folds=folds)
    # The scored population: the union of the test folds (every game exactly once
    # under K-fold; the committed test set under a split). The ballot calibration
    # AND the honest ceiling are measured over exactly this population, so every
    # channel in the report describes one distribution.
    scored_seeds: set[int] = set()
    for _, test_seeds in fold_pairs:
        scored_seeds |= set(test_seeds)
    scored_views = [view for view in views if view.seed in scored_seeds]

    top1_hits = 0
    top2_hits = 0
    ejection_meetings = 0
    predicted_ejections = 0
    predicted_skips = 0
    correct_skip = 0
    correct_eject = 0
    meetings_scored = 0
    ejection_pred_skips = 0
    decision_reachable = 0
    plurality_confidence_meetings = 0
    brier_terms: list[float] = []
    calib: list[tuple[float, int]] = []

    for fold_index, (train_seeds, test_seeds) in enumerate(fold_pairs):
        train_views = [v for s in sorted(train_seeds) for v in views_by_seed[s]]
        test_views = [v for s in sorted(test_seeds) for v in views_by_seed[s]]
        if not test_views:
            # A derived fold whose test block holds only no-meeting games scores
            # nothing; the union of the other test folds still covers every
            # rows-bearing game exactly once. (A committed split cannot reach
            # here — _game_folds already rejects a no-scoreable-meeting side.)
            continue
        if not train_views:
            # Model-agnostic twin of the Fo6Logistic.fit guard (Codex review): a
            # derived fold on a tiny/no-meeting corpus must not silently score
            # an untrained model as if it were by-game CV.
            raise ValueError(
                f"fold {fold_index} has no scoreable training meetings: every "
                "fit-side game ends before any meeting fires, so the model "
                "would fit on nothing — use a larger corpus or a committed split"
            )
        model = model_factory()
        if not isinstance(model, MeetingModel):
            raise TypeError(
                f"model_factory produced {type(model)!r}, which is not a MeetingModel"
            )
        model.fit(train_views)
        for view in test_views:
            meetings_scored += 1
            prediction = model.predict(view)
            _validate_prediction(prediction, view, model_name=model_name)
            true_eject = view.ejected
            predicted = prediction.ejected
            if predicted is None:
                predicted_skips += 1
            else:
                predicted_ejections += 1
            # Accumulated in the SAME walk that scores every other channel: a
            # second pass would re-run the model and drift from this one the
            # moment the folds change.
            confidence = prediction.plurality_confidence
            if confidence is not None:
                plurality_confidence_meetings += 1
                if confidence >= DEFAULT_SKIP_CONFIDENCE_THRESHOLD:
                    decision_reachable += 1
            # SKIP-vs-eject is a BINARY decision (Codex review): correct iff the
            # model's eject/skip CHOICE matches the outcome's, regardless of WHICH
            # player it named (that exactness is the separate top-1 channel, and the
            # always-eject baseline is binary too). Compare None-ness, not identity.
            if (predicted is None) == (true_eject is None):
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

    # Recorded ballot-confidence calibration over the SCORED meetings' non-SKIP
    # ballots (§5.5). Model-independent — read straight off the table's recorded
    # ballots for the scored population.
    ballot_calib: list[tuple[float, int]] = []
    for row in table.rows:
        if row.seed not in scored_seeds or row.ballot_target == "SKIP":
            continue
        label = 1 if row.ballot_target == row.ejected_player_id else 0
        ballot_calib.append((row.ballot_confidence, label))
    ballot_brier = (
        float(np.mean([(c - y) ** 2 for c, y in ballot_calib])) if ballot_calib else 0.0
    )
    ballot_ece = _expected_calibration_error(ballot_calib)

    if meetings_scored == 0:
        # Every derived fold was skipped (a corpus of only no-meeting games) —
        # a committed split cannot reach here (_game_folds rejects a
        # no-scoreable-meeting side). Fail loud rather than return a
        # valid-looking all-zero report (Codex review; AGENTS.md "no silent
        # fallbacks").
        raise ValueError(
            f"{table.replay_set_dir}: no fold scored any meeting — every recorded "
            "game ends before a meeting fires, so there is nothing to judge; "
            "refusing to emit an all-zero fidelity report"
        )

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
        # By-game by construction: _game_folds only ever assigns whole games to a
        # side (K-fold strides seeds; a committed split is validated to partition
        # them), so this is a documented guarantee, not a runtime branch.
        by_game_cv=True,
        meetings_scored=meetings_scored,
        ejection_meetings=ejection_meetings,
        skip_meetings=skip_meetings,
        top1=(top1_hits / ejection_meetings) if ejection_meetings else 0.0,
        top2=(top2_hits / ejection_meetings) if ejection_meetings else 0.0,
        top1_hits=top1_hits,
        top2_hits=top2_hits,
        skip_vs_eject_accuracy=decision_accuracy,
        always_eject_baseline=always_eject_baseline,
        always_skip_baseline=(
            skip_meetings / meetings_scored if meetings_scored else 0.0
        ),
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
        ballot_brier=ballot_brier,
        ballot_ece=ballot_ece,
        ballot_rows=len(ballot_calib),
        decision_reachable_meetings=decision_reachable,
        decision_reachability=(
            decision_reachable / meetings_scored if meetings_scored else 0.0
        ),
        plurality_confidence_meetings=plurality_confidence_meetings,
        # Measured over the SCORED (test-side) views only, the same population as
        # top1/ejection_meetings — under a committed split the ceiling bounds the
        # held-out score, never a train/val distribution (Codex review).
        honest_ceiling=compute_honest_ceiling(scored_views),
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

    Pins the true prior baseline the GO bar's comparator axis reads: FO-6's RANKING,
    which is threshold-independent. Runs the same six-feature logistic
    (re-implemented, :class:`Fo6Logistic` — the spike is mypy-excluded and never
    imported) under by-GAME CV, surfacing the ranking, the decision census and the
    calibration TOGETHER.

    Its DECISION head is published as what it is — a
    :data:`FO6_DECISION_HEAD_LABEL` — beside the population's two trivial constants
    (``always_eject_baseline`` / ``always_skip_baseline``) and its full tau curve,
    so the margin the tuned threshold won by is visible rather than implied. The
    15.13 ballot surrogate instead decides through the real tally at
    ``meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD`` and publishes no tuned
    head at all.
    """

    fits: list[Fo6Logistic] = []

    def factory() -> Fo6Logistic:
        model = Fo6Logistic()
        fits.append(model)
        return model

    report = run_surrogate_fidelity(
        table,
        factory,
        model_name="fo6-physical-logistic",
        folds=folds,
    )
    return report.model_copy(
        update={
            "decision_head": DecisionHeadReport(
                label=FO6_DECISION_HEAD_LABEL,
                scans=tuple(model.threshold_scan for model in fits),
            )
        }
    )


# ---------------------------------------------------------------------------
# GO/NO-GO wiring (Task 15.13's region — 15.11 owns everything above).
# ---------------------------------------------------------------------------

# The GO bar's single relative multiplier, OWNER-RATIFIED (2026-07-09, mid-wave
# review Q1) and committed BEFORE the surrogate was trained. Every axis of the
# bar is population-relative — measured by THIS harness on the SAME scored
# population as the surrogate's own numbers — because every absolute number in
# this project's history moved when the population changed (FO-6 64% -> 26%;
# ceiling 65.1 -> 70.6): the samples-set 70.6% ceiling, 78.4% always-eject and
# 25.7% FO-6 figures do NOT transfer to the corpus test split and are never
# compared against.
GO_TOP1_CEILING_RATIO: Final[float] = 0.75

# The identity of the bar a verdict was decided under, stamped on every verdict so
# a published GO/NO-GO can never be re-read against a differently-shaped successor.
# ``split-ranking-decision.v1`` reports the ranking and decision claims separately
# and composes them; the axes, their constants and their strictness are the same
# three the ratified bar committed.
GO_BAR_ID: Final[str] = "split-ranking-decision.v1"


class GoNoGoVerdict(BaseModel):
    """The pre-stated GO/NO-GO verdict for the ballot surrogate (Task 15.13).

    GO ⇔ ALL THREE population-relative axes hold on the held-out scored
    population, judged by this harness:

    1. ``surrogate_top1 >= GO_TOP1_CEILING_RATIO * ceiling_top1`` — the honest
       ceiling measured on the SAME scored population (never the samples-set
       70.6% figure);
    2. ``surrogate_top1 > baseline_top1`` — the corpus-re-baselined FO-6
       logistic (never the spike's 64% or the samples-set 25.7%);
    3. ``surrogate skip-vs-eject accuracy > always_eject_baseline`` — the
       scored population's OWN trivial constant (never the samples-set 78.4%).

    The verdict also REPORTS the two claims separately, because they are two
    different claims about two different instruments: ``ranking_verdict`` is axes
    1 ∧ 2 — the suspicion-ranking claim the surrogate actually supports — and
    ``decision_verdict`` is axis 3, the decision channel. Reporting is ALL the
    split does: ``verdict`` remains their conjunction, so no input that was NO-GO
    under the unsplit bar can become GO under this one, and the consequence
    mapping below is untouched.

    Pre-committed in the same breath: NO-GO ⇒ fallback (a) — the fake-provider
    MeetingManager stays the bake-off's training-time runner and the surrogate
    ships as a DIAGNOSTIC only (its fidelity report still lands; nothing trains
    against it). ``training_time_runner`` / ``surrogate_role`` encode exactly
    that mapping so the bake-off consumes the verdict, not a prose reading of
    it. The staleness cap ships regardless of the verdict.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    bar_id: str
    replay_set_dir: str
    surrogate_model_name: str
    baseline_model_name: str
    # The shared scored population both reports were measured on.
    meetings_scored: int
    ejection_meetings: int
    # Axis 1 — held-out top-1 against the same-population honest ceiling.
    surrogate_top1: float
    ceiling_top1: float
    top1_bar: float
    meets_ceiling_bar: bool
    # How much ranking headroom is left: ``ceiling_top1 − surrogate_top1``. At 0.0
    # the surrogate is AT the measured ceiling — it is not "above a floor with room
    # to grow", it has taken every reachable ejection the physical+belief channels
    # expose.
    top1_ceiling_gap: float
    # WHY the ceiling sits where it does — the ceiling's own overlapping channel
    # counts, carried so a reader need not re-open the fidelity report.
    ceiling_flag_present: int
    ceiling_proximity_present: int
    ceiling_belief_lead: int
    ceiling_reachable: int
    ceiling_voice_driven_share: float
    # Axis 2 — held-out top-1 against the corpus-re-baselined FO-6 prior.
    baseline_top1: float
    beats_prior_baseline: bool
    # Axis 3 — SKIP-vs-eject accuracy against the population's own constant.
    surrogate_skip_vs_eject_accuracy: float
    always_eject_baseline: float
    beats_always_eject: bool
    # Whether axis 3 is REACHABLE before anyone spends a fit on it: the scored
    # meetings whose predicted plurality-target confidence clears the tally's own
    # eject gate (``meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD``).
    decision_reachable_meetings: int
    decision_reachability: float
    # The two claims, reported apart...
    ranking_verdict: Literal["GO", "NO-GO"]
    decision_verdict: Literal["GO", "NO-GO"]
    # ...and the composed verdict that drives the consequence mapping.
    verdict: Literal["GO", "NO-GO"]
    training_time_runner: Literal["surrogate", "fake-provider-meeting-manager"]
    surrogate_role: Literal["training-time-runner", "diagnostic-only"]


def decide_go_no_go(
    surrogate: SurrogateFidelityReport,
    prior_baseline: SurrogateFidelityReport,
) -> GoNoGoVerdict:
    """Apply the pre-stated bar to two same-population fidelity reports.

    ``surrogate`` is the 15.13 ballot surrogate's report; ``prior_baseline`` is
    the FO-6 re-baseline (:func:`fo6_rebaseline`) run over the SAME table with
    the SAME folds. Both must describe one scored population — a bar compared
    across populations is exactly the absolute-number mistake the ratified
    wording forbids, so any population mismatch fails loud instead of producing
    a verdict.
    """

    mismatches = [
        name
        for name, ours, theirs in (
            ("replay_set_dir", surrogate.replay_set_dir, prior_baseline.replay_set_dir),
            ("folds", surrogate.folds, prior_baseline.folds),
            (
                "meetings_scored",
                surrogate.meetings_scored,
                prior_baseline.meetings_scored,
            ),
            (
                "ejection_meetings",
                surrogate.ejection_meetings,
                prior_baseline.ejection_meetings,
            ),
            ("honest_ceiling", surrogate.honest_ceiling, prior_baseline.honest_ceiling),
            (
                "always_eject_baseline",
                surrogate.always_eject_baseline,
                prior_baseline.always_eject_baseline,
            ),
        )
        if ours != theirs
    ]
    if mismatches:
        raise ValueError(
            "GO/NO-GO requires both reports to describe the SAME scored "
            f"population; fields {mismatches} differ between "
            f"{surrogate.model_name!r} and {prior_baseline.model_name!r}"
        )
    if surrogate.ejection_meetings == 0:
        raise ValueError(
            f"{surrogate.replay_set_dir}: the scored population has no ejection "
            "meetings — top-1 is undefined, so no verdict can be honest"
        )
    ceiling_top1 = surrogate.honest_ceiling.max_achievable_top1
    top1_bar = GO_TOP1_CEILING_RATIO * ceiling_top1
    meets_ceiling_bar = surrogate.top1 >= top1_bar
    beats_prior_baseline = surrogate.top1 > prior_baseline.top1
    beats_always_eject = (
        surrogate.skip_vs_eject_accuracy > surrogate.always_eject_baseline
    )
    # The split is a REPORTING split: the ranking claim and the decision claim are
    # stated apart, and the composed verdict is still every axis conjoined, so
    # nothing that failed before can pass now.
    ranking_go = meets_ceiling_bar and beats_prior_baseline
    decision_go = beats_always_eject
    is_go = ranking_go and decision_go
    ceiling = surrogate.honest_ceiling
    return GoNoGoVerdict(
        bar_id=GO_BAR_ID,
        replay_set_dir=surrogate.replay_set_dir,
        surrogate_model_name=surrogate.model_name,
        baseline_model_name=prior_baseline.model_name,
        meetings_scored=surrogate.meetings_scored,
        ejection_meetings=surrogate.ejection_meetings,
        surrogate_top1=surrogate.top1,
        ceiling_top1=ceiling_top1,
        top1_bar=top1_bar,
        meets_ceiling_bar=meets_ceiling_bar,
        top1_ceiling_gap=ceiling_top1 - surrogate.top1,
        ceiling_flag_present=ceiling.flag_present,
        ceiling_proximity_present=ceiling.proximity_present,
        ceiling_belief_lead=ceiling.belief_lead,
        ceiling_reachable=ceiling.reachable,
        ceiling_voice_driven_share=ceiling.voice_driven_share,
        baseline_top1=prior_baseline.top1,
        beats_prior_baseline=beats_prior_baseline,
        surrogate_skip_vs_eject_accuracy=surrogate.skip_vs_eject_accuracy,
        always_eject_baseline=surrogate.always_eject_baseline,
        beats_always_eject=beats_always_eject,
        decision_reachable_meetings=surrogate.decision_reachable_meetings,
        decision_reachability=surrogate.decision_reachability,
        ranking_verdict="GO" if ranking_go else "NO-GO",
        decision_verdict="GO" if decision_go else "NO-GO",
        verdict="GO" if is_go else "NO-GO",
        # The pre-committed fallback mapping: a NO-GO surrogate is a diagnostic,
        # never a training-time runner — fallback (a) keeps the bake-off unblocked.
        training_time_runner=(
            "surrogate" if is_go else "fake-provider-meeting-manager"
        ),
        surrogate_role=("training-time-runner" if is_go else "diagnostic-only"),
    )


__all__ = [
    "DEFAULT_CV_FOLDS",
    "FO6_DECISION_HEAD_LABEL",
    "FO6_FEATURE_NAMES",
    "GO_BAR_ID",
    "GO_TOP1_CEILING_RATIO",
    "DecisionHeadReport",
    "Fo6Logistic",
    "GoNoGoVerdict",
    "HonestCeiling",
    "MeetingModel",
    "MeetingPrediction",
    "MeetingView",
    "SurrogateFidelityReport",
    "ThresholdScan",
    "build_meeting_views",
    "compute_honest_ceiling",
    "decide_go_no_go",
    "fo6_rebaseline",
    "run_surrogate_fidelity",
]
