"""The ballot-predictor surrogate — predict BALLOTS, feed the REAL tally (Task 15.13).

The $0 inner-loop meeting model rebuilt on the structural fix
(audits/post-phase-14-ML-training-signal.md §5.3): predict each living voter's
BALLOT ``(target, confidence)`` from the 15.11 features and let the real
deterministic :func:`meetings.voting.tally_ballots` produce the outcome, at the
explicit constants-home gate
:data:`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD`. SKIP-vs-eject
therefore emerges from plurality + the confidence gate — never from a
mis-calibrated binary head (FO-6's always-SKIP collapse, §5.2) — and one ballot
per living voter is exactly the roster the cross-meeting belief fold reads
(``meetings/manager.py::extract_belief_evidence``, roster off ``result.ballots``).

**The live-parity feature set.** :data:`BALLOT_FEATURE_NAMES` is deliberately the
subset of the 15.11 table columns that a :class:`~training.surrogate.runner.
SurrogateMeetingRunner` can derive IDENTICALLY at ``run_meeting`` time from the
trigger-time inputs the :class:`~orchestrator.game.MeetingRunner` protocol hands it
(``trigger``, ``state``, ``agents``):

* ``belief_suspicion`` / ``belief_trust`` — the voter's full pre-meeting belief row
  toward the candidate. Offline: the table's reconstructed production fold (prior
  meetings' evidence + perception pins, Rule-5 decayed). Live: the SAME stored
  :class:`~agents.memory.beliefs.BeliefState` via
  ``MeetingAwareAgent.suspicion_graph_for_meeting()``. This is the §5.4 headline
  feature — it already integrates the accumulators the LLM votes on.
* ``is_reporter`` — candidate == ``trigger.triggered_by``.
* ``witnessed_vent`` — the voter-local role-proving pin. Offline: the table's
  event-derived witness set. Live: the voter's OWN typed
  ``vent_witness_records_for_meeting()`` channel naming the candidate.
* ``meeting_index`` / ``alive_count`` — game-phase scalars.

Columns a live runner CANNOT reconstruct are excluded BY DESIGN, not oversight:
the contradiction-flag structure and ``contradiction_lift`` need THIS meeting's
transcript (a training-time surrogate has no LLM, hence no transcript — the same
structural blindness the honest ceiling measures), and the physical window stats
(``witnessed`` / ``isolation`` / ``seen_at_kill`` / ``body_proximity`` /
``task_submissions`` / ``move_count``) need the inter-meeting event history the
runner never sees. Training on features that would be identically zero (or
unobtainable) live would inflate the offline fidelity number the GO/NO-GO verdict
reads while the deployed runner behaves worse — exactly the "weaken a mitigation to
make the verdict look better" failure the task contract forbids.

**Fit/predict leakage fence.** :class:`BallotSurrogateModel` is the
:class:`~training.surrogate.fidelity.MeetingModel` adapter: the fidelity harness
hands it meeting-collapsed :class:`~training.surrogate.fidelity.MeetingView`\\ s, and
its side-channel back into the 15.11 table's per-voter rows is fenced —
:func:`ballot_features_from_row` reads FEATURE columns only (never
``ballot_target`` / ``ballot_confidence`` / ``ejected_player_id`` / ``outcome`` /
``is_ejected`` / ``is_impostor``), label columns are read ONLY by
:func:`ballot_example_from_row` on the fit side, and ``fit`` refuses a view from
outside the declared fit-side seed set. The committed leakage test poisons the
labels of every non-fit row and proves both directions byte-identical.

**Coerced-SKIP fit exclusion (Task 17.10 designer ruling).** A J2 citation-gate
coerced ballot records ``target="SKIP"`` but was a FORCED eject, not a chosen
skip — poison for the decision channel the GO/NO-GO verdict hinges on. Both fit
paths (:meth:`BallotSurrogateModel.fit` and
:func:`fit_corpus_ballot_predictor`) DROP rows whose
``MeetingTableRow.ballot_coerced_skip`` flag is set (the 15.11 table detects
the production coercion marker at reconstruction); the dropped count is
reported in ``training/reports/report-ballot-surrogate.md``. Fit-side only:
the fidelity replay scores the recorded bytes unfiltered.

The predictor itself is a standardized CONDITIONAL LOGIT (the determinism-safe
default the task hint names): one shared weight vector over the per-candidate
features plus a learned SKIP alternative over per-voter aggregates, fit by
full-batch gradient descent (no RNG, zeros init — replay-stable like
:class:`~training.surrogate.fidelity.Fo6Logistic`); the ballot confidence is a
ridge-solved linear head on the chosen target's standardized features. Weights
serialize losslessly as float-hex JSON (the
``agents/tactical/features.py::weights_to_hex_json`` convention) with a sha256
sidecar — the exact artifact the bake-off reloads and the 15.9
:class:`~orchestrator.replay.TacticalPolicyStamp` ``weights_sha256`` field can
reference — plus the committed staleness cap
(:class:`SurrogateStalenessCap`, consumed by
:mod:`training.surrogate.runner`) so no trainer optimizes indefinitely against a
frozen surrogate (§5.6, MBPO/Dreamer model-exploitation).

Public surface (stable — downstream tasks import these):
:class:`BallotPredictor`, :class:`BallotSurrogateModel`,
:func:`fit_corpus_ballot_predictor`, :func:`write_ballot_predictor_artifact`,
:func:`load_ballot_predictor_artifact`, :func:`load_staleness_cap`,
:func:`derive_max_uses`.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field

from engine.entities import PlayerId
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.schemas import VoteBallot
from meetings.voting import SKIP_TARGET, tally_ballots
from training.surrogate.dataset import MeetingTable, MeetingTableRow
from training.surrogate.fidelity import (
    MeetingPrediction,
    MeetingView,
    _expected_calibration_error,
)

# The live-parity per-candidate feature order (see the module docstring for why
# exactly these six). Serialized into the weights artifact and validated on load,
# so a drifted feature layout fails loud instead of silently mis-multiplying.
BALLOT_FEATURE_NAMES: Final[tuple[str, ...]] = (
    "belief_suspicion",
    "belief_trust",
    "is_reporter",
    "witnessed_vent",
    "meeting_index",
    "alive_count",
)

# The per-voter SKIP-alternative feature order. ``max_belief_suspicion`` is the
# §4.6 gate signal itself (the production heuristic skips when the max rendered
# suspicion sits below the 0.60 gate), so the learned SKIP utility can express
# exactly the decision surface the real voters used.
SKIP_FEATURE_NAMES: Final[tuple[str, ...]] = (
    "max_belief_suspicion",
    "meeting_index",
    "alive_count",
)

# Fit hyperparameters — full-batch gradient descent, mirroring Fo6Logistic's
# deterministic recipe (no RNG; zeros init; fixed epoch count).
DEFAULT_EPOCHS: Final[int] = 300
DEFAULT_LEARNING_RATE: Final[float] = 0.3

# The committed artifact filenames under ``training/artifacts/surrogate/``.
ARTIFACT_FORMAT: Final[str] = "ballot-predictor.v1"
WEIGHTS_FILENAME: Final[str] = "ballot-predictor.json"
WEIGHTS_SHA256_FILENAME: Final[str] = "ballot-predictor.json.sha256"
STALENESS_FILENAME: Final[str] = "max-uses.json"

# The staleness-cap rule (§5.6, made mechanical by the Task-17.10 designer
# ruling): the committed cap is ~143× the fit corpus's FIT-SIDE MEETING COUNT,
# re-derived at every re-ground — never held at a previous baseline's number by
# habit. The baseline-3 cap (50 000 ≈ 143 × 349 fit meetings) is the rule's
# origin; :func:`derive_max_uses` applies it to the current corpus. The
# rationale for the magnitude lives in
# ``training/reports/report-ballot-surrogate.md`` §7.
STALENESS_USES_PER_FIT_MEETING: Final[int] = 143


def derive_max_uses(fit_side_meetings: int) -> int:
    """The ~143× staleness rule: cap = 143 × the fit-side meeting count.

    ``fit_side_meetings`` is the number of distinct meetings in the fit corpus's
    committed fit side (``train ∪ val`` games) — the grounding data the frozen
    weights were fit on. Refuses a non-positive count (a cap derived from no
    grounding data is meaningless — AGENTS.md "no silent fallbacks").
    """

    if fit_side_meetings <= 0:
        raise ValueError(
            f"derive_max_uses needs a positive fit-side meeting count, got "
            f"{fit_side_meetings}"
        )
    return STALENESS_USES_PER_FIT_MEETING * fit_side_meetings


_SURROGATE_RATIONALE: Final[str] = (
    "surrogate-predicted ballot (no transcript; Task 15.13 ballot predictor)"
)


@dataclass(frozen=True)
class VoterBallotView:
    """One voter's live-parity prediction input (Task 15.13).

    ``candidates`` is the voter's ballot choice set — the living roster MINUS the
    voter itself, sorted (the meeting manager excludes self-votes from
    ``candidate_targets``; :func:`meetings.voting.normalize_ballot_target` treats
    them as invalid). ``features`` maps each candidate to exactly the
    :data:`BALLOT_FEATURE_NAMES` columns. Constructible from a table row
    (:func:`ballot_features_from_row`) or live from the runner's trigger-time
    inputs — the two paths produce the same shape by design.
    """

    voter: PlayerId
    candidates: tuple[PlayerId, ...]
    features: Mapping[PlayerId, Mapping[str, float]]


@dataclass(frozen=True)
class BallotExample:
    """One supervised fit example: a voter view + the RECORDED ballot labels.

    The ONLY type through which the predictor sees label columns
    (``ballot_target`` / ``ballot_confidence``); built exclusively by
    :func:`ballot_example_from_row` on the fit side of the leakage fence.
    """

    view: VoterBallotView
    target: PlayerId | str
    confidence: float


@dataclass(frozen=True)
class PredictedBallot:
    """The predictor's output for one voter.

    ``target`` is a candidate id or :data:`~meetings.voting.SKIP_TARGET`;
    ``confidence`` is the ballot confidence the real tally gates on.
    ``target_probs`` (per-candidate softmax mass) and ``skip_prob`` are surfaced
    for the ranking / calibration channels.
    """

    target: PlayerId | str
    confidence: float
    target_probs: Mapping[PlayerId, float]
    skip_prob: float


class PredictedBallotCalibration(BaseModel):
    """Calibration of the surrogate's PREDICTED ballots (Task 15.13; frozen).

    Brier / ECE of the predicted non-SKIP ballot confidences against whether the
    predicted target was actually ejected — the surrogate's OWN calibration
    channel. Distinct by construction from the harness's committed
    ``ballot_brier`` / ``ballot_ece``, which score the RECORDED voters' stated
    confidences (model-independent) and are never presented as surrogate
    calibration.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    brier: float
    ece: float
    predicted_ballots: int
    predicted_skips: int


class SurrogateStalenessCap(BaseModel):
    """The committed staleness cap beside the weights artifact (frozen).

    The §5.6 doctrine made mechanical: ``max_uses`` is the maximum number of
    surrogate-simulated MEETINGS (the pinned unit — one
    ``SurrogateMeetingRunner.run_meeting`` call is one use) a bake-off run may
    consume against the frozen weights artifact identified by
    ``weights_sha256`` before :class:`training.surrogate.runner.
    SurrogateUseCounter` raises. OWNERSHIP: the bake-off owns the ONE counter
    for its whole run and threads it through every runner factory — the counter
    keys on this sha256 and is cumulative across runner constructions, so a
    fresh runner instance never resets it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    weights_sha256: str = Field(min_length=64, max_length=64)
    max_uses: int = Field(gt=0)
    unit: Literal["meetings"]


def ballot_features_from_row(row: MeetingTableRow) -> VoterBallotView:
    """Reduce a table row to the live-parity FEATURE view (never a label).

    The predict-side half of the leakage fence: reads only feature columns —
    ``belief_suspicion`` / ``belief_trust`` / ``is_reporter`` /
    ``witnessed_vent`` off each non-self candidate, plus ``meeting_index`` and
    the living-roster size. It NEVER touches ``ballot_target`` /
    ``ballot_confidence`` / ``ejected_player_id`` / ``outcome`` /
    ``is_ejected`` / ``is_impostor`` (the committed poison test proves it).
    """

    alive_count = float(len(row.candidates))
    candidates: list[PlayerId] = []
    features: dict[PlayerId, dict[str, float]] = {}
    for feat in row.candidates:
        if feat.is_self:
            continue
        candidates.append(feat.candidate)
        features[feat.candidate] = {
            "belief_suspicion": float(feat.belief_suspicion),
            "belief_trust": float(feat.belief_trust),
            "is_reporter": float(feat.is_reporter),
            "witnessed_vent": float(feat.witnessed_vent),
            "meeting_index": float(row.meeting_index),
            "alive_count": alive_count,
        }
    return VoterBallotView(
        voter=row.voter, candidates=tuple(candidates), features=features
    )


def ballot_example_from_row(row: MeetingTableRow) -> BallotExample:
    """Join a row's feature view to its RECORDED ballot labels (fit side ONLY).

    The single label-column read in this module: ``ballot_target`` and
    ``ballot_confidence``. Callers must hold the row inside the fit-side seed
    set — :meth:`BallotSurrogateModel.fit` enforces exactly that.
    """

    return BallotExample(
        view=ballot_features_from_row(row),
        target=row.ballot_target,
        confidence=float(row.ballot_confidence),
    )


def _skip_features(view: VoterBallotView) -> dict[str, float]:
    """The per-voter SKIP-alternative features (:data:`SKIP_FEATURE_NAMES`)."""

    if view.candidates:
        max_susp = max(
            view.features[cand]["belief_suspicion"] for cand in view.candidates
        )
        sample = view.features[view.candidates[0]]
        meeting_index = sample["meeting_index"]
        alive_count = sample["alive_count"]
    else:
        max_susp = 0.5
        meeting_index = 0.0
        alive_count = 1.0
    return {
        "max_belief_suspicion": max_susp,
        "meeting_index": meeting_index,
        "alive_count": alive_count,
    }


class BallotPredictor:
    """Standardized conditional-logit ballot predictor (Task 15.13 public type).

    Per voter, scores every non-self living candidate with one shared weight
    vector over :data:`BALLOT_FEATURE_NAMES` and a learned SKIP alternative over
    :data:`SKIP_FEATURE_NAMES`; the softmax over ``candidates + [SKIP]`` is fit
    by full-batch gradient descent on the recorded ballots (deterministic: zeros
    init, fixed epochs, no RNG — the Fo6Logistic recipe). The ballot confidence
    is a ridge-solved linear head on the chosen target's standardized features,
    clipped to ``[0, 1]``; SKIP ballots carry the fitted mean recorded SKIP
    confidence (a SKIP ballot's confidence never gates the tally).

    Inference is a pure function of the fitted weights: the double-run hash test
    and the float-hex artifact round-trip pin it.
    """

    def __init__(
        self, *, epochs: int = DEFAULT_EPOCHS, lr: float = DEFAULT_LEARNING_RATE
    ) -> None:
        self._epochs = epochs
        self._lr = lr
        self._mean: NDArray[np.float64] | None = None
        self._std: NDArray[np.float64] | None = None
        self._weights: NDArray[np.float64] | None = None
        self._skip_mean: NDArray[np.float64] | None = None
        self._skip_std: NDArray[np.float64] | None = None
        self._skip_weights: NDArray[np.float64] | None = None
        self._skip_bias: float = 0.0
        self._confidence_weights: NDArray[np.float64] | None = None
        self._skip_confidence: float = 0.5

    # -- fitting ---------------------------------------------------------------

    def fit(self, examples: Sequence[BallotExample]) -> None:
        """Fit the choice model + confidence head on recorded ballots.

        Refuses an empty example set (never install a silent untrained model —
        AGENTS.md "no silent fallbacks"). Deterministic FOR A GIVEN EXAMPLE
        ORDER ON A GIVEN PLATFORM: no RNG, zeros init, fixed epochs — but
        floating-point summation is order-sensitive at the ULP level, both in
        the example sequence (every committed fit path iterates the table's
        sorted ``(seed, meeting_index, voter)`` row order) and inside numpy's
        SIMD reductions, whose grouping varies by CPU. A refit is therefore
        byte-identical on the recording platform and ULP-equivalent elsewhere
        (CI runs on a different CPU); the COMMITTED artifact bytes — not a
        refit — are the frozen ground truth the sha256 sidecar pins, and the
        round-trip test asserts refit parameter-equivalence plus frozen-weights
        reproduction of the reported numbers.
        """

        usable = [example for example in examples if example.view.candidates]
        if not usable:
            raise ValueError(
                "BallotPredictor.fit received no examples with a non-empty "
                "candidate set; refusing to install an untrained model"
            )

        candidate_rows = [
            [example.view.features[cand][name] for name in BALLOT_FEATURE_NAMES]
            for example in usable
            for cand in example.view.candidates
        ]
        matrix = np.asarray(candidate_rows, dtype=np.float64)
        mean = matrix.mean(axis=0)
        std = matrix.std(axis=0)
        std[std == 0.0] = 1.0

        skip_rows = [
            [_skip_features(example.view)[name] for name in SKIP_FEATURE_NAMES]
            for example in usable
        ]
        skip_matrix = np.asarray(skip_rows, dtype=np.float64)
        skip_mean = skip_matrix.mean(axis=0)
        skip_std = skip_matrix.std(axis=0)
        skip_std[skip_std == 0.0] = 1.0

        # Group examples by candidate count so each epoch is a handful of dense
        # batched numpy passes rather than a Python loop per example. The
        # gradient is a SUM over examples, so grouping cannot change the fit.
        groups: dict[int, list[int]] = defaultdict(list)
        for index, example in enumerate(usable):
            groups[len(example.view.candidates)].append(index)

        skip_standardized = (skip_matrix - skip_mean) / skip_std
        batches: list[
            tuple[
                NDArray[np.float64],
                NDArray[np.float64],
                NDArray[np.int64],
            ]
        ] = []
        for count in sorted(groups):
            indices = groups[count]
            stacked = np.zeros((len(indices), count, len(BALLOT_FEATURE_NAMES)))
            labels = np.zeros(len(indices), dtype=np.int64)
            for slot, example_index in enumerate(indices):
                example = usable[example_index]
                for cand_slot, cand in enumerate(example.view.candidates):
                    stacked[slot, cand_slot] = [
                        example.view.features[cand][name]
                        for name in BALLOT_FEATURE_NAMES
                    ]
                if example.target == SKIP_TARGET:
                    labels[slot] = count
                else:
                    try:
                        labels[slot] = example.view.candidates.index(
                            str(example.target)
                        )
                    except ValueError as exc:
                        raise ValueError(
                            f"recorded ballot target {example.target!r} is not in "
                            f"voter {example.view.voter!r}'s candidate set "
                            f"{example.view.candidates} — the table's rows always "
                            "carry normalised ballots, so this is corrupt input"
                        ) from exc
            standardized = (stacked - mean) / std
            batches.append(
                (
                    standardized,
                    skip_standardized[np.asarray(indices, dtype=np.int64)],
                    labels,
                )
            )

        weights = np.zeros(len(BALLOT_FEATURE_NAMES), dtype=np.float64)
        skip_weights = np.zeros(len(SKIP_FEATURE_NAMES), dtype=np.float64)
        skip_bias = 0.0
        total = float(len(usable))
        for _ in range(self._epochs):
            grad_w = np.zeros_like(weights)
            grad_v = np.zeros_like(skip_weights)
            grad_b = 0.0
            for batch_features, batch_skip, batch_labels in batches:
                utilities = batch_features @ weights
                skip_utility = batch_skip @ skip_weights + skip_bias
                logits = np.concatenate([utilities, skip_utility[:, None]], axis=1)
                logits -= logits.max(axis=1, keepdims=True)
                exp = np.exp(np.clip(logits, -30.0, 30.0))
                probs = exp / exp.sum(axis=1, keepdims=True)
                error = probs.copy()
                error[np.arange(len(batch_labels)), batch_labels] -= 1.0
                grad_w += np.einsum("mn,mnd->d", error[:, :-1], batch_features)
                grad_v += error[:, -1] @ batch_skip
                grad_b += float(error[:, -1].sum())
            weights -= self._lr * grad_w / total
            skip_weights -= self._lr * grad_v / total
            skip_bias -= self._lr * grad_b / total

        self._mean = mean
        self._std = std
        self._weights = weights
        self._skip_mean = skip_mean
        self._skip_std = skip_std
        self._skip_weights = skip_weights
        self._skip_bias = skip_bias
        self._fit_confidence_head(usable, mean=mean, std=std)

    def _fit_confidence_head(
        self,
        examples: Sequence[BallotExample],
        *,
        mean: NDArray[np.float64],
        std: NDArray[np.float64],
    ) -> None:
        """Ridge-solve the confidence head on the recorded non-SKIP ballots."""

        rows: list[list[float]] = []
        confidences: list[float] = []
        skip_confidences: list[float] = []
        for example in examples:
            if example.target == SKIP_TARGET:
                skip_confidences.append(example.confidence)
                continue
            target = str(example.target)
            vector = np.asarray(
                [example.view.features[target][name] for name in BALLOT_FEATURE_NAMES],
                dtype=np.float64,
            )
            standardized = (vector - mean) / std
            rows.append([*standardized.tolist(), 1.0])
            confidences.append(example.confidence)
        if rows:
            design = np.asarray(rows, dtype=np.float64)
            targets = np.asarray(confidences, dtype=np.float64)
            gram = design.T @ design + 1e-8 * np.eye(design.shape[1])
            self._confidence_weights = np.asarray(
                np.linalg.solve(gram, design.T @ targets), dtype=np.float64
            )
        else:
            # A corpus with only SKIP ballots cannot ground a confidence head;
            # fall back to a constant at the neutral prior — still deterministic
            # and still gated by the real tally (an all-SKIP fit predicts SKIP).
            self._confidence_weights = np.zeros(
                len(BALLOT_FEATURE_NAMES) + 1, dtype=np.float64
            )
            self._confidence_weights[-1] = 0.5
        self._skip_confidence = (
            float(np.mean(np.asarray(skip_confidences, dtype=np.float64)))
            if skip_confidences
            else 0.5
        )

    # -- inference ---------------------------------------------------------------

    def _require_fitted(
        self,
    ) -> tuple[
        NDArray[np.float64],
        NDArray[np.float64],
        NDArray[np.float64],
        NDArray[np.float64],
        NDArray[np.float64],
        NDArray[np.float64],
        NDArray[np.float64],
    ]:
        if (
            self._mean is None
            or self._std is None
            or self._weights is None
            or self._skip_mean is None
            or self._skip_std is None
            or self._skip_weights is None
            or self._confidence_weights is None
        ):
            raise RuntimeError(
                "BallotPredictor.predict_ballot called before fit / artifact load"
            )
        return (
            self._mean,
            self._std,
            self._weights,
            self._skip_mean,
            self._skip_std,
            self._skip_weights,
            self._confidence_weights,
        )

    def predict_ballot(self, view: VoterBallotView) -> PredictedBallot:
        """Predict one voter's ballot ``(target, confidence)`` deterministically.

        The choice is the softmax argmax over ``candidates + [SKIP]``; an exact
        probability tie between candidates breaks to the smallest id, and a
        candidate-vs-SKIP tie breaks to the candidate (both deterministic). The
        confidence for a non-SKIP target is the linear head's clipped output;
        for SKIP it is the fitted mean recorded SKIP confidence.
        """

        (
            mean,
            std,
            weights,
            skip_mean,
            skip_std,
            skip_weights,
            confidence_weights,
        ) = self._require_fitted()
        skip_vector = np.asarray(
            [_skip_features(view)[name] for name in SKIP_FEATURE_NAMES],
            dtype=np.float64,
        )
        skip_utility = float(
            ((skip_vector - skip_mean) / skip_std) @ skip_weights + self._skip_bias
        )
        if not view.candidates:
            # A voter with an empty choice set (no other living player) can only
            # skip; the fitted SKIP confidence keeps the ballot schema-valid.
            return PredictedBallot(
                target=SKIP_TARGET,
                confidence=self._skip_confidence,
                target_probs={},
                skip_prob=1.0,
            )
        standardized_by_candidate: dict[PlayerId, NDArray[np.float64]] = {}
        utilities: list[float] = []
        for cand in view.candidates:
            vector = np.asarray(
                [view.features[cand][name] for name in BALLOT_FEATURE_NAMES],
                dtype=np.float64,
            )
            standardized = (vector - mean) / std
            standardized_by_candidate[cand] = standardized
            utilities.append(float(standardized @ weights))
        logits = np.asarray([*utilities, skip_utility], dtype=np.float64)
        logits -= logits.max()
        exp = np.exp(np.clip(logits, -30.0, 30.0))
        probs = exp / exp.sum()
        target_probs = {
            cand: float(probs[index]) for index, cand in enumerate(view.candidates)
        }
        skip_prob = float(probs[-1])
        leader = min(view.candidates, key=lambda cand: (-target_probs[cand], cand))
        if skip_prob > target_probs[leader]:
            return PredictedBallot(
                target=SKIP_TARGET,
                confidence=self._skip_confidence,
                target_probs=target_probs,
                skip_prob=skip_prob,
            )
        design = np.asarray(
            [*standardized_by_candidate[leader].tolist(), 1.0], dtype=np.float64
        )
        confidence = float(np.clip(design @ confidence_weights, 0.0, 1.0))
        return PredictedBallot(
            target=leader,
            confidence=confidence,
            target_probs=target_probs,
            skip_prob=skip_prob,
        )

    # -- float-hex serialization ---------------------------------------------------

    def to_artifact_json(self) -> str:
        """Serialize the fitted weights as byte-stable float-hex JSON.

        Every float travels as ``float.hex()`` (lossless for float64 — the
        ``agents/tactical/features.py`` convention); keys are sorted and the
        payload ends in one newline, so re-serializing an identical fit is
        byte-identical and the sha256 sidecar is stable.
        """

        (
            mean,
            std,
            weights,
            skip_mean,
            skip_std,
            skip_weights,
            confidence_weights,
        ) = self._require_fitted()

        def hex_list(values: NDArray[np.float64]) -> list[str]:
            return [float(value).hex() for value in values.tolist()]

        payload = {
            "format": ARTIFACT_FORMAT,
            "feature_names": list(BALLOT_FEATURE_NAMES),
            "skip_feature_names": list(SKIP_FEATURE_NAMES),
            "epochs": self._epochs,
            "lr": float(self._lr).hex(),
            "mean": hex_list(mean),
            "std": hex_list(std),
            "weights": hex_list(weights),
            "skip_mean": hex_list(skip_mean),
            "skip_std": hex_list(skip_std),
            "skip_weights": hex_list(skip_weights),
            "skip_bias": float(self._skip_bias).hex(),
            "confidence_weights": hex_list(confidence_weights),
            "skip_confidence": float(self._skip_confidence).hex(),
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    @classmethod
    def from_artifact_json(cls, data: str) -> BallotPredictor:
        """Reload a predictor from :meth:`to_artifact_json` bytes (fail loud).

        Validates the format marker and that the artifact's feature layouts
        match this module's constants — a drifted layout must never silently
        mis-multiply against reordered features.
        """

        raw = json.loads(data)
        if not isinstance(raw, dict):
            raise ValueError("ballot-predictor artifact must be a JSON object")
        if raw.get("format") != ARTIFACT_FORMAT:
            raise ValueError(
                f"ballot-predictor artifact format {raw.get('format')!r} != "
                f"{ARTIFACT_FORMAT!r}"
            )
        if tuple(raw.get("feature_names", ())) != BALLOT_FEATURE_NAMES:
            raise ValueError(
                f"artifact feature_names {raw.get('feature_names')!r} do not match "
                f"BALLOT_FEATURE_NAMES {BALLOT_FEATURE_NAMES!r}"
            )
        if tuple(raw.get("skip_feature_names", ())) != SKIP_FEATURE_NAMES:
            raise ValueError(
                f"artifact skip_feature_names {raw.get('skip_feature_names')!r} do "
                f"not match SKIP_FEATURE_NAMES {SKIP_FEATURE_NAMES!r}"
            )

        def hex_array(key: str, length: int) -> NDArray[np.float64]:
            values = raw.get(key)
            if not isinstance(values, list) or len(values) != length:
                raise ValueError(
                    f"artifact field {key!r} must be a list of {length} float-hex "
                    f"strings, got {values!r}"
                )
            return np.asarray(
                [float.fromhex(item) for item in values], dtype=np.float64
            )

        d = len(BALLOT_FEATURE_NAMES)
        d_skip = len(SKIP_FEATURE_NAMES)
        predictor = cls(epochs=int(raw["epochs"]), lr=float.fromhex(raw["lr"]))
        predictor._mean = hex_array("mean", d)
        predictor._std = hex_array("std", d)
        predictor._weights = hex_array("weights", d)
        predictor._skip_mean = hex_array("skip_mean", d_skip)
        predictor._skip_std = hex_array("skip_std", d_skip)
        predictor._skip_weights = hex_array("skip_weights", d_skip)
        predictor._skip_bias = float.fromhex(raw["skip_bias"])
        predictor._confidence_weights = hex_array("confidence_weights", d + 1)
        predictor._skip_confidence = float.fromhex(raw["skip_confidence"])
        return predictor


class BallotSurrogateModel:
    """The :class:`~training.surrogate.fidelity.MeetingModel` adapter (Task 15.13).

    Bridges the harness's meeting-collapsed views back to the table's per-voter
    rows through the leakage fence (module docstring), predicts every voter's
    ballot, and lets the REAL :func:`meetings.voting.tally_ballots` — at the
    explicit :data:`~meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD` —
    produce the SKIP-vs-eject decision. The ranking / calibration channels read
    the expected vote share (mean predicted vote probability over the
    candidate's eligible voters), which is a probability in ``[0, 1]`` per
    candidate; the DECISION channel is only ever the tally's output.

    ``fit_seeds`` defaults to the table's committed split fit side
    (``train ∪ val``) when a split is present; under derived K-fold CV it is
    ``None`` and the harness's by-game folds carry the anti-leakage guarantee
    (fit still reads only the rows of the views it was handed).

    ``predictor`` pre-installs an already-fitted (typically artifact-loaded)
    :class:`BallotPredictor`, so the adapter can evaluate FROZEN committed
    weights without a refit — the bake-off's reload path and the round-trip
    test use it (a cross-platform refit reproduces the weights only to float
    ULP, so frozen-artifact evaluation is the byte-exact path). A subsequent
    ``fit`` replaces it (the fidelity harness always fits per fold).
    """

    def __init__(
        self,
        table: MeetingTable,
        *,
        fit_seeds: frozenset[int] | None = None,
        epochs: int = DEFAULT_EPOCHS,
        lr: float = DEFAULT_LEARNING_RATE,
        predictor: BallotPredictor | None = None,
    ) -> None:
        self._rows_by_meeting: dict[tuple[int, str], list[MeetingTableRow]] = (
            defaultdict(list)
        )
        for row in table.rows:
            self._rows_by_meeting[(row.seed, row.meeting_id)].append(row)
        if fit_seeds is None and table.splits is not None:
            fit_seeds = frozenset(table.splits.train) | frozenset(table.splits.val)
        self._fit_seeds = fit_seeds
        self._epochs = epochs
        self._lr = lr
        self._predictor: BallotPredictor | None = predictor

    @property
    def predictor(self) -> BallotPredictor:
        if self._predictor is None:
            raise RuntimeError("BallotSurrogateModel used before fit")
        return self._predictor

    def _rows(self, meeting: MeetingView) -> list[MeetingTableRow]:
        rows = self._rows_by_meeting.get((meeting.seed, meeting.meeting_id))
        if not rows:
            raise ValueError(
                f"meeting {meeting.seed}:{meeting.meeting_id} has no rows in the "
                "table this model was built over — view/table mismatch"
            )
        return rows

    def fit(self, meetings: Sequence[MeetingView]) -> None:
        """Fit on exactly the given meetings' rows (labels read here ONLY).

        The fit half of the leakage fence: when a fit-side seed set is declared
        (a committed split), a view from outside it is refused — the fidelity
        run must never fold a held-out game's labels into the fit.
        """

        if not meetings:
            raise ValueError(
                "BallotSurrogateModel.fit received no meetings; refusing to "
                "install an untrained model"
            )
        seeds = {meeting.seed for meeting in meetings}
        if self._fit_seeds is not None and not seeds <= self._fit_seeds:
            leaked = sorted(seeds - self._fit_seeds)
            raise ValueError(
                f"fit received meetings from seeds {leaked} outside the declared "
                f"fit-side seed set — refusing to read held-out labels"
            )
        # J2-coerced SKIP rows are EXCLUDED from every fit (Task 17.10 designer
        # ruling): a coerced ballot records ``target="SKIP"`` but was a forced
        # eject, not a chosen skip — a poisoned label for the decision channel.
        # Fit-side only: predict/fidelity still score the recorded bytes
        # unfiltered (a coerced meeting is still scored exactly as recorded).
        examples = [
            ballot_example_from_row(row)
            for meeting in meetings
            for row in self._rows(meeting)
            if not row.ballot_coerced_skip
        ]
        predictor = BallotPredictor(epochs=self._epochs, lr=self._lr)
        predictor.fit(examples)
        self._predictor = predictor

    def _predict_ballots(
        self, meeting: MeetingView
    ) -> tuple[list[VoteBallot], dict[PlayerId, PredictedBallot]]:
        """Predict every voter's ballot from FEATURE columns only."""

        predictor = self.predictor
        ballots: list[VoteBallot] = []
        by_voter: dict[PlayerId, PredictedBallot] = {}
        for row in self._rows(meeting):
            predicted = predictor.predict_ballot(ballot_features_from_row(row))
            by_voter[row.voter] = predicted
            ballots.append(
                VoteBallot(
                    voter=row.voter,
                    target=predicted.target,
                    confidence=predicted.confidence,
                    primary_reason_id=None,
                    considered_alternatives=(),
                    rationale_text=_SURROGATE_RATIONALE,
                )
            )
        return ballots, by_voter

    def predict(self, meeting: MeetingView) -> MeetingPrediction:
        ballots, by_voter = self._predict_ballots(meeting)
        # The DECISION is the real tally on the predicted ballots — the point of
        # the rebuild. Never re-implemented, never a tuned threshold.
        _, ejected = tally_ballots(
            ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
        )
        shares: dict[PlayerId, float] = {}
        for cand in meeting.candidates:
            masses = [
                predicted.target_probs.get(cand, 0.0)
                for voter, predicted in sorted(by_voter.items())
                if voter != cand
            ]
            shares[cand] = float(np.mean(masses)) if masses else 0.0
        ranking = tuple(
            sorted(meeting.candidates, key=lambda cand: (-shares[cand], cand))
        )
        return MeetingPrediction(ranking=ranking, ejected=ejected, ejection_prob=shares)

    def predicted_ballot_calibration(
        self, meetings: Sequence[MeetingView]
    ) -> PredictedBallotCalibration:
        """Brier/ECE of the PREDICTED ballot confidences over ``meetings``.

        For every predicted non-SKIP ballot: the predicted confidence against
        whether its named target was actually ejected. The surrogate's own
        calibration channel — reported beside, never instead of, the harness's
        recorded-ballot ``ballot_brier`` / ``ballot_ece``.
        """

        calibration: list[tuple[float, int]] = []
        predicted_skips = 0
        for meeting in meetings:
            _, by_voter = self._predict_ballots(meeting)
            for _, predicted in sorted(by_voter.items()):
                if predicted.target == SKIP_TARGET:
                    predicted_skips += 1
                    continue
                label = 1 if predicted.target == meeting.ejected else 0
                calibration.append((predicted.confidence, label))
        brier = (
            float(np.mean([(conf - label) ** 2 for conf, label in calibration]))
            if calibration
            else 0.0
        )
        return PredictedBallotCalibration(
            brier=brier,
            ece=_expected_calibration_error(calibration),
            predicted_ballots=len(calibration),
            predicted_skips=predicted_skips,
        )


def fit_corpus_ballot_predictor(
    table: MeetingTable,
    *,
    epochs: int = DEFAULT_EPOCHS,
    lr: float = DEFAULT_LEARNING_RATE,
) -> BallotPredictor:
    """The training entry: fit on the committed corpus split's fit side.

    Requires a committed split (the 15.12 corpus ships one) — the artifact-fit
    is the same fit the fidelity harness performs for its single
    ``(train ∪ val, test)`` fold (same examples, same order), so the committed
    weights ARE the weights the reported held-out numbers were produced by —
    asserted by the round-trip test via ULP-level parameter equivalence (a
    cross-platform refit differs in the last float bits, see :meth:`
    BallotPredictor.fit`) and by frozen-weights reproduction of the reported
    numbers. Raises on a split-less table rather than inventing a fit side.
    """

    if table.splits is None:
        raise ValueError(
            f"{table.replay_set_dir} ships no committed splits.json; the corpus "
            "training entry fits on the committed fit side (train ∪ val) only — "
            "use the 15.12 corpus, not a baseline sample set"
        )
    fit_seeds = frozenset(table.splits.train) | frozenset(table.splits.val)
    # Coerced-SKIP rows are dropped from the fit (Task 17.10 designer ruling —
    # see :meth:`BallotSurrogateModel.fit`); the dropped count is reported in
    # ``training/reports/report-ballot-surrogate.md`` (0 on the committed
    # baseline-5 corpus), never silently absorbed.
    examples = [
        ballot_example_from_row(row)
        for row in table.rows
        if row.seed in fit_seeds and not row.ballot_coerced_skip
    ]
    predictor = BallotPredictor(epochs=epochs, lr=lr)
    predictor.fit(examples)
    return predictor


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def write_ballot_predictor_artifact(
    predictor: BallotPredictor,
    artifact_dir: Path,
    *,
    max_uses: int,
) -> str:
    """Commit the weights + sha256 sidecar + staleness cap under ``artifact_dir``.

    Writes :data:`WEIGHTS_FILENAME` (float-hex JSON),
    :data:`WEIGHTS_SHA256_FILENAME` (``"<hex>  <filename>\\n"``, the shasum
    format — the value the 15.9 ``TacticalPolicyStamp.weights_sha256`` field
    references), and :data:`STALENESS_FILENAME` (the committed
    :class:`SurrogateStalenessCap`, keyed on the same sha256). Returns the
    sha256 hex digest.

    ``max_uses`` is REQUIRED and derived from the fit corpus via
    :func:`derive_max_uses` (the ~143× rule) — deliberately no default, so a
    re-ground can never hold a previous baseline's cap by habit (the Task-17.10
    designer ruling that retired the old 50 000 constant).
    """

    artifact_dir.mkdir(parents=True, exist_ok=True)
    payload = predictor.to_artifact_json()
    digest = _sha256_hex(payload)
    (artifact_dir / WEIGHTS_FILENAME).write_text(payload)
    (artifact_dir / WEIGHTS_SHA256_FILENAME).write_text(
        f"{digest}  {WEIGHTS_FILENAME}\n"
    )
    cap = SurrogateStalenessCap(
        weights_sha256=digest, max_uses=max_uses, unit="meetings"
    )
    (artifact_dir / STALENESS_FILENAME).write_text(
        json.dumps(cap.model_dump(), indent=2, sort_keys=True) + "\n"
    )
    return digest


def load_ballot_predictor_artifact(
    artifact_dir: Path,
) -> tuple[BallotPredictor, str]:
    """Reload the committed weights, verifying the sha256 sidecar (fail loud).

    Returns ``(predictor, sha256)``. A missing file, a sidecar naming a
    different file, or a digest mismatch all raise — the bake-off must reload
    EXACTLY the committed artifact, never a silently drifted one.
    """

    weights_path = artifact_dir / WEIGHTS_FILENAME
    sidecar_path = artifact_dir / WEIGHTS_SHA256_FILENAME
    if not weights_path.is_file():
        raise FileNotFoundError(f"no committed weights artifact at {weights_path}")
    if not sidecar_path.is_file():
        raise FileNotFoundError(f"no sha256 sidecar at {sidecar_path}")
    payload = weights_path.read_text()
    digest = _sha256_hex(payload)
    sidecar = sidecar_path.read_text().strip()
    expected = f"{digest}  {WEIGHTS_FILENAME}"
    if sidecar != expected:
        raise ValueError(
            f"sha256 sidecar mismatch for {weights_path}: sidecar says "
            f"{sidecar!r}, recomputed {expected!r} — the artifact drifted from "
            "its committed hash"
        )
    return BallotPredictor.from_artifact_json(payload), digest


def load_staleness_cap(artifact_dir: Path) -> SurrogateStalenessCap:
    """Read the committed staleness cap beside the weights artifact (fail loud)."""

    path = artifact_dir / STALENESS_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed staleness cap at {path}; the surrogate must never run "
            "uncapped (audits/post-phase-14-ML-training-signal.md §5.6)"
        )
    return SurrogateStalenessCap.model_validate_json(path.read_text())


__all__ = [
    "ARTIFACT_FORMAT",
    "BALLOT_FEATURE_NAMES",
    "DEFAULT_EPOCHS",
    "DEFAULT_LEARNING_RATE",
    "SKIP_FEATURE_NAMES",
    "STALENESS_FILENAME",
    "STALENESS_USES_PER_FIT_MEETING",
    "WEIGHTS_FILENAME",
    "WEIGHTS_SHA256_FILENAME",
    "BallotExample",
    "BallotPredictor",
    "BallotSurrogateModel",
    "PredictedBallot",
    "PredictedBallotCalibration",
    "SurrogateStalenessCap",
    "VoterBallotView",
    "ballot_example_from_row",
    "ballot_features_from_row",
    "derive_max_uses",
    "fit_corpus_ballot_predictor",
    "load_ballot_predictor_artifact",
    "load_staleness_cap",
    "write_ballot_predictor_artifact",
]
