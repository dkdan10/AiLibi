"""The conviction-economy model g(pre-meeting state) → supply (Task 18.15).

:class:`ConvictionEconomyModel` is the training-signal instrument the phase was
chartered around (audits/audit-phase-18-planning.md §2.3): a deterministic numpy
fit over the fenced per-meeting features
(:data:`training.conviction.dataset.CONVICTION_FEATURE_NAMES`) predicting the
two quantities the referee economy gates —

* ``expected_flags`` — a ridge-solved standardized LINEAR head on the
  ``flags_minted`` label (closed-form ``np.linalg.solve``; no iteration, no
  RNG). Its output is a real-valued supply score judged by RANK (the GO bar's
  Spearman channel), so no clipping is applied.
* ``conversion_prob`` — a standardized LOGISTIC head on the
  ``testimony_backed_conversion`` label, fit by full-batch gradient descent
  (zeros init, fixed epochs, no RNG — the ``Fo6Logistic`` /
  ``BallotPredictor`` recipe).

Determinism carries the surrogate's documented platform caveat verbatim: no RNG
and a fixed example order make a refit byte-identical ON THE RECORDING PLATFORM,
while numpy's SIMD reduction grouping varies by CPU, so a cross-platform refit
is ULP-equivalent. The COMMITTED artifact bytes — not a refit — are the frozen
ground truth the sha256 sidecar pins.

**The artifact** mirrors ``training/surrogate/ballots.py``: float-hex JSON
weights (lossless ``float.hex()``, sorted keys, trailing newline — byte-stable
round trip), a ``<name>.json.sha256`` shasum sidecar, and a committed
``max-uses.json`` staleness cap. The cap follows the standing ~143× rule made
mechanical at Task 17.10 (:data:`CONVICTION_USES_PER_FIT_MEETING` — the
surrogate's ``STALENESS_USES_PER_FIT_MEETING`` rule, restated locally because
the two are INDEPENDENT artifacts with independent verdicts, the 18.15 designer
ruling): ``max_uses = 143 × the fit-side meeting count``, re-derived at every
re-ground and never held at a previous baseline's number by habit.
:class:`ConvictionUseCounter` meters every model evaluation against the frozen
sha — one predicted meeting is one use — so no trainer optimizes indefinitely
against a frozen instrument (the §5.6 model-exploitation doctrine); 18.16
threads ONE counter through both fitness sides and the pre-screen.

**The corpus fit entry** (:func:`fit_corpus_conviction_model`) enforces the
17.10 discipline mechanically: the walk re-validation
(:func:`training.surrogate.dataset.measure_belief_render_parity` gated by
:func:`training.conviction.dataset.require_clean_walk`) runs BEFORE any fit —
0 raw mismatches or no fit — and the measured parity travels back to the caller
so the report quotes it.

Public surface (stable — downstream tasks import these):
:class:`ConvictionEconomyModel`, :class:`ConvictionPrediction`,
:class:`ConvictionStalenessCap`, :class:`ConvictionStalenessExceededError`,
:class:`ConvictionUseCounter`, :func:`derive_conviction_max_uses`,
:func:`fit_corpus_conviction_model`, :func:`write_conviction_model_artifact`,
:func:`load_conviction_model_artifact`, :func:`load_conviction_staleness_cap`.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field

from training.conviction.dataset import (
    CONVICTION_FEATURE_NAMES,
    ConvictionMeetingRow,
    ConvictionTable,
    build_conviction_table,
    require_clean_walk,
    validate_conviction_split,
)
from training.surrogate.dataset import (
    BeliefRenderParity,
    measure_belief_render_parity,
)
from training.surrogate.runner import load_fit_corpus_record
from training.provenance import (
    EvidenceScope,
    validate_evidence_scope,
    verify_fit_identity,
)

# Fit hyperparameters — the deterministic recipe shared with Fo6Logistic /
# BallotPredictor (no RNG; zeros init; fixed epoch count; full batch).
DEFAULT_EPOCHS: Final[int] = 300
DEFAULT_LEARNING_RATE: Final[float] = 0.3

# The flags head's ridge regularizer — the same numerically-stabilizing epsilon
# the ballot predictor's confidence head solves with.
RIDGE_LAMBDA: Final[float] = 1e-8

# The committed artifact filenames under ``training/artifacts/conviction/``.
ARTIFACT_FORMAT: Final[str] = "conviction-model.v1"
WEIGHTS_FILENAME: Final[str] = "conviction-model.json"
WEIGHTS_SHA256_FILENAME: Final[str] = "conviction-model.json.sha256"
STALENESS_FILENAME: Final[str] = "max-uses.json"

# The ~143× staleness rule (the Task-17.10 designer ruling, applied to THIS
# artifact): cap = 143 × the fit corpus's fit-side MEETING count. Restated
# locally rather than imported from ``training/surrogate/ballots.py`` — the
# conviction model and the ballot surrogate are independent artifacts with
# independent verdicts (the 18.15 designer ruling), so neither's constant may
# silently retune the other's cap.
CONVICTION_USES_PER_FIT_MEETING: Final[int] = 143


def derive_conviction_max_uses(fit_side_meetings: int) -> int:
    """The ~143× staleness rule: cap = 143 × the fit-side meeting count.

    ``fit_side_meetings`` is the number of meetings in the fit corpus's
    committed fit side (``train ∪ val`` games) — the grounding data the frozen
    weights were fit on. Refuses a non-positive count (a cap derived from no
    grounding data is meaningless — AGENTS.md "no silent fallbacks").
    """

    if fit_side_meetings <= 0:
        raise ValueError(
            f"derive_conviction_max_uses needs a positive fit-side meeting "
            f"count, got {fit_side_meetings}"
        )
    return CONVICTION_USES_PER_FIT_MEETING * fit_side_meetings


class ConvictionStalenessExceededError(RuntimeError):
    """A consumer spent the committed cap of conviction-model evaluations.

    Raised by :meth:`ConvictionUseCounter.record_use` when one more predicted
    meeting would exceed the committed ``max_uses``. Deliberately NOT silently
    recoverable: a trainer at the cap must re-ground (record fresh real-LLM
    meetings, rebuild the table, re-fit, re-measure —
    ``training/reports/report-conviction-model.md`` §8).
    """


class ConvictionStalenessCap(BaseModel):
    """The committed staleness cap beside the conviction weights (frozen).

    ``max_uses`` is the maximum number of model-predicted MEETINGS (the pinned
    unit — one :meth:`ConvictionEconomyModel.predict` call metered by the
    consumer is one use) a training run may consume against the frozen artifact
    identified by ``weights_sha256``. OWNERSHIP mirrors the surrogate cap: the
    18.16 integration owns ONE :class:`ConvictionUseCounter` per run and
    threads it through both fitness sides and the pre-screen — the counter keys
    on this sha256 and is cumulative, so a fresh consumer never resets it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    weights_sha256: str = Field(min_length=64, max_length=64)
    max_uses: int = Field(gt=0)
    unit: Literal["meetings"]


class ConvictionUseCounter:
    """The cumulative use-counter for one frozen conviction artifact.

    An explicit object (never module state — AGENTS.md "no global state") the
    consumer constructs ONCE per run from the committed cap; ``record_use``
    keys every use on the weights sha256 so a counter can never be silently
    reused against different weights.
    """

    def __init__(self, cap: ConvictionStalenessCap) -> None:
        self._cap = cap
        self._uses = 0

    @property
    def cap(self) -> ConvictionStalenessCap:
        return self._cap

    @property
    def uses(self) -> int:
        """Model-predicted meetings recorded so far (the cap's unit)."""

        return self._uses

    def record_use(self, *, weights_sha256: str) -> int:
        """Record one predicted meeting; raise once the committed cap is spent."""

        if weights_sha256 != self._cap.weights_sha256:
            raise ValueError(
                "ConvictionUseCounter is keyed on weights sha256 "
                f"{self._cap.weights_sha256!r} but was asked to record a use of "
                f"{weights_sha256!r} — one counter never meters two artifacts"
            )
        if self._uses >= self._cap.max_uses:
            raise ConvictionStalenessExceededError(
                f"the frozen conviction model {weights_sha256[:12]}… has "
                f"reached its committed staleness cap of {self._cap.max_uses} "
                "predicted meetings for this run; re-ground before training "
                "further (training/reports/report-conviction-model.md §8)"
            )
        self._uses += 1
        return self._uses


@dataclass(frozen=True)
class ConvictionPrediction:
    """The model's output for one meeting (Task 18.15).

    ``expected_flags`` is the flags head's real-valued supply score — judged by
    RANK (deliberately unclipped; a negative score is a legitimate bottom
    rank). ``conversion_prob`` is the logistic head's P(testimony-backed
    conversion) in ``[0, 1]``.
    """

    expected_flags: float
    conversion_prob: float


class ConvictionEconomyModel:
    """The two-head conviction-economy fit (Task 18.15 public type).

    ``fit`` trains both heads on conviction rows; ``predict`` scores one
    meeting's feature mapping. Inference is a pure function of the fitted
    weights — the double-fit determinism test and the float-hex artifact
    round-trip pin it. See the module docstring for the heads and the platform
    caveat.
    """

    def __init__(
        self, *, epochs: int = DEFAULT_EPOCHS, lr: float = DEFAULT_LEARNING_RATE
    ) -> None:
        self._epochs = epochs
        self._lr = lr
        self._mean: NDArray[np.float64] | None = None
        self._std: NDArray[np.float64] | None = None
        self._flags_weights: NDArray[np.float64] | None = None
        self._conversion_weights: NDArray[np.float64] | None = None
        self._conversion_bias: float = 0.0

    @staticmethod
    def _vector(features: Mapping[str, float]) -> NDArray[np.float64]:
        """Canonicalize a feature mapping into the artifact's vector layout.

        The KEY SET must match :data:`CONVICTION_FEATURE_NAMES` exactly (a
        missing or unexpected key fails loud, both named); insertion order is
        deliberately NOT part of the public contract — the vector is always
        assembled by indexing the canonical name order, so a live consumer
        may build its mapping in any order (Codex review, PR #302).
        """

        keys = frozenset(features)
        expected = frozenset(CONVICTION_FEATURE_NAMES)
        if keys != expected:
            raise ValueError(
                "feature mapping does not match CONVICTION_FEATURE_NAMES: "
                f"missing {sorted(expected - keys)}, unexpected "
                f"{sorted(keys - expected)} — a drifted layout must never "
                "silently mis-multiply"
            )
        return np.asarray(
            [features[name] for name in CONVICTION_FEATURE_NAMES], dtype=np.float64
        )

    def fit(self, rows: Sequence[ConvictionMeetingRow]) -> None:
        """Fit both heads on conviction rows (deterministic; see module caveat).

        Refuses an empty row set (never install a silent untrained model —
        AGENTS.md "no silent fallbacks"). An all-negative conversion corpus
        still fits: the logistic head converges toward the base rate and the
        verdict machinery downstream fails loud where a judgment would be
        dishonest.
        """

        if not rows:
            raise ValueError(
                "ConvictionEconomyModel.fit received no rows; refusing to "
                "install an untrained model"
            )
        matrix = np.stack([self._vector(row.features) for row in rows])
        mean = matrix.mean(axis=0)
        std = matrix.std(axis=0)
        std[std == 0.0] = 1.0
        standardized = (matrix - mean) / std

        # Flags head: closed-form ridge on [standardized | 1] — no iteration.
        design = np.concatenate(
            [standardized, np.ones((matrix.shape[0], 1), dtype=np.float64)], axis=1
        )
        flag_labels = np.asarray(
            [float(row.flags_minted) for row in rows], dtype=np.float64
        )
        gram = design.T @ design + RIDGE_LAMBDA * np.eye(design.shape[1])
        flags_weights = np.asarray(
            np.linalg.solve(gram, design.T @ flag_labels), dtype=np.float64
        )

        # Conversion head: full-batch logistic, zeros init, fixed epochs.
        conversion_labels = np.asarray(
            [1.0 if row.testimony_backed_conversion else 0.0 for row in rows],
            dtype=np.float64,
        )
        weights = np.zeros(len(CONVICTION_FEATURE_NAMES), dtype=np.float64)
        bias = 0.0
        n = float(matrix.shape[0])
        for _ in range(self._epochs):
            logits = standardized @ weights + bias
            probs = 1.0 / (1.0 + np.exp(-np.clip(logits, -30.0, 30.0)))
            error = probs - conversion_labels
            weights -= self._lr * (standardized.T @ error) / n
            bias -= self._lr * float(error.mean())

        self._mean = mean
        self._std = std
        self._flags_weights = flags_weights
        self._conversion_weights = weights
        self._conversion_bias = bias

    def _require_fitted(
        self,
    ) -> tuple[
        NDArray[np.float64],
        NDArray[np.float64],
        NDArray[np.float64],
        NDArray[np.float64],
    ]:
        if (
            self._mean is None
            or self._std is None
            or self._flags_weights is None
            or self._conversion_weights is None
        ):
            raise RuntimeError(
                "ConvictionEconomyModel.predict called before fit / artifact load"
            )
        return (
            self._mean,
            self._std,
            self._flags_weights,
            self._conversion_weights,
        )

    def predict(self, features: Mapping[str, float]) -> ConvictionPrediction:
        """Score one meeting's fenced feature mapping deterministically."""

        mean, std, flags_weights, conversion_weights = self._require_fitted()
        standardized = (self._vector(features) - mean) / std
        design = np.concatenate([standardized, np.ones(1, dtype=np.float64)])
        expected_flags = float(design @ flags_weights)
        logit = float(standardized @ conversion_weights + self._conversion_bias)
        conversion_prob = 1.0 / (1.0 + float(np.exp(-max(min(logit, 30.0), -30.0))))
        return ConvictionPrediction(
            expected_flags=expected_flags, conversion_prob=conversion_prob
        )

    # -- float-hex serialization ------------------------------------------------

    def to_artifact_json(self) -> str:
        """Serialize the fitted weights as byte-stable float-hex JSON.

        Every float travels as ``float.hex()`` (lossless for float64 — the
        ``training/surrogate/ballots.py`` convention); keys are sorted and the
        payload ends in one newline, so re-serializing an identical fit is
        byte-identical and the sha256 sidecar is stable.
        """

        mean, std, flags_weights, conversion_weights = self._require_fitted()

        def hex_list(values: NDArray[np.float64]) -> list[str]:
            return [float(value).hex() for value in values.tolist()]

        payload = {
            "format": ARTIFACT_FORMAT,
            "feature_names": list(CONVICTION_FEATURE_NAMES),
            "epochs": self._epochs,
            "lr": float(self._lr).hex(),
            "mean": hex_list(mean),
            "std": hex_list(std),
            "flags_weights": hex_list(flags_weights),
            "conversion_weights": hex_list(conversion_weights),
            "conversion_bias": float(self._conversion_bias).hex(),
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    @classmethod
    def from_artifact_json(cls, data: str) -> "ConvictionEconomyModel":
        """Reload a model from :meth:`to_artifact_json` bytes (fail loud).

        Validates the format marker and the feature layout — a drifted layout
        must never silently mis-multiply against reordered features.
        """

        raw = json.loads(data)
        if not isinstance(raw, dict):
            raise ValueError("conviction-model artifact must be a JSON object")
        if raw.get("format") != ARTIFACT_FORMAT:
            raise ValueError(
                f"conviction-model artifact format {raw.get('format')!r} != "
                f"{ARTIFACT_FORMAT!r}"
            )
        if tuple(raw.get("feature_names", ())) != CONVICTION_FEATURE_NAMES:
            raise ValueError(
                f"artifact feature_names {raw.get('feature_names')!r} do not "
                f"match CONVICTION_FEATURE_NAMES {CONVICTION_FEATURE_NAMES!r}"
            )

        def hex_array(key: str, length: int) -> NDArray[np.float64]:
            values = raw.get(key)
            if not isinstance(values, list) or len(values) != length:
                raise ValueError(
                    f"artifact field {key!r} must be a list of {length} "
                    f"float-hex strings, got {values!r}"
                )
            return np.asarray(
                [float.fromhex(item) for item in values], dtype=np.float64
            )

        dims = len(CONVICTION_FEATURE_NAMES)
        model = cls(epochs=int(raw["epochs"]), lr=float.fromhex(raw["lr"]))
        model._mean = hex_array("mean", dims)
        model._std = hex_array("std", dims)
        model._flags_weights = hex_array("flags_weights", dims + 1)
        model._conversion_weights = hex_array("conversion_weights", dims)
        model._conversion_bias = float.fromhex(raw["conversion_bias"])
        return model


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def write_conviction_model_artifact(
    model: ConvictionEconomyModel,
    artifact_dir: Path,
    *,
    max_uses: int,
) -> str:
    """Commit the weights + sha256 sidecar + staleness cap under ``artifact_dir``.

    Writes :data:`WEIGHTS_FILENAME` (float-hex JSON),
    :data:`WEIGHTS_SHA256_FILENAME` (``"<hex>  <filename>\\n"``, the shasum
    format), and :data:`STALENESS_FILENAME` (the committed
    :class:`ConvictionStalenessCap`, keyed on the same sha256). Returns the
    sha256 hex digest. ``max_uses`` is REQUIRED and derived via
    :func:`derive_conviction_max_uses` (the ~143× rule) — deliberately no
    default, so a re-ground can never hold a previous baseline's cap by habit.
    """

    artifact_dir.mkdir(parents=True, exist_ok=True)
    payload = model.to_artifact_json()
    digest = _sha256_hex(payload)
    (artifact_dir / WEIGHTS_FILENAME).write_text(payload)
    (artifact_dir / WEIGHTS_SHA256_FILENAME).write_text(
        f"{digest}  {WEIGHTS_FILENAME}\n"
    )
    cap = ConvictionStalenessCap(
        weights_sha256=digest, max_uses=max_uses, unit="meetings"
    )
    (artifact_dir / STALENESS_FILENAME).write_text(
        json.dumps(cap.model_dump(), indent=2, sort_keys=True) + "\n"
    )
    return digest


def load_conviction_model_artifact(
    artifact_dir: Path,
    *,
    corpus_dir: Path | None = None,
    evidence_scope: EvidenceScope = "current",
) -> tuple[ConvictionEconomyModel, str]:
    """Read raw weights with their SHA sidecar; optionally verify a fit identity.

    Without corpus_dir this is a weights-only restoration API, not a certificate
    that the model fits current inputs. Scoring/install bundles always supply the
    corpus and scope. Current identity requires version two; explicit historical
    diagnostics reproduce version-one corpus bytes without claiming current
    roster or derivation binding.
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
    validate_evidence_scope(evidence_scope, artifact_dir)
    if corpus_dir is not None:
        _verify_conviction_fit_corpus(
            artifact_dir,
            corpus_dir=corpus_dir,
            weights_sha256=digest,
            evidence_scope=evidence_scope,
        )
    return ConvictionEconomyModel.from_artifact_json(payload), digest


def _verify_conviction_fit_corpus(
    artifact_dir: Path,
    *,
    corpus_dir: Path,
    weights_sha256: str,
    evidence_scope: EvidenceScope,
) -> None:
    """Refuse weights whose fit corpus is not the corpus about to score them."""

    try:
        record = load_fit_corpus_record(artifact_dir)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"{error}; the conviction re-grounding recipe writes it beside the "
            "weights (training/reports/report-conviction-model.md §8 step 4), so "
            "an artifact without one was not committed by that recipe"
        ) from error
    if record.weights_sha256 != weights_sha256:
        raise ValueError(
            f"fit-corpus provenance under {artifact_dir} is keyed on weights "
            f"{record.weights_sha256!r} but the committed weights hash to "
            f"{weights_sha256!r} — the fit-corpus record and the artifact "
            "drifted apart (a re-fit must re-write both together)"
        )
    verify_fit_identity(
        artifact_dir=artifact_dir,
        corpus_dir=corpus_dir,
        fingerprint_version=record.fingerprint_version,
        corpus_sha256=record.corpus_sha256,
        scope=evidence_scope,
    )


def load_conviction_staleness_cap(artifact_dir: Path) -> ConvictionStalenessCap:
    """Read the committed staleness cap beside the weights artifact (fail loud)."""

    path = artifact_dir / STALENESS_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed staleness cap at {path}; the conviction model must "
            "never run uncapped (the §5.6 doctrine under the ~143× rule)"
        )
    return ConvictionStalenessCap.model_validate_json(path.read_text())


def fit_corpus_conviction_model(
    sample_dir: Path,
    *,
    epochs: int = DEFAULT_EPOCHS,
    lr: float = DEFAULT_LEARNING_RATE,
) -> tuple[ConvictionEconomyModel, ConvictionTable, BeliefRenderParity]:
    """The corpus training entry: walk re-validation FIRST, then fit.

    Enforces the 17.10 discipline mechanically: the belief-fold parity walk
    runs and must be clean (:func:`require_clean_walk` — 0 raw mismatches)
    BEFORE any table is trusted or any fit runs. Requires a committed split
    and fits on its fit side (``train ∪ val``) only — the exact fit the
    fidelity harness's held-out evaluation judges. Returns the fitted model,
    the built table, and the measured parity (the report quotes all three).
    """

    parity = require_clean_walk(measure_belief_render_parity(sample_dir))
    table = build_conviction_table(sample_dir)
    # The committed split must partition the games (disjoint fit/test, full
    # coverage, no unknown seeds) BEFORE the fit-side rows are selected — the
    # same fail-loud gate the held-out evaluation runs.
    fit_seeds, _ = validate_conviction_split(table)
    rows = [row for row in table.rows if row.seed in fit_seeds]
    model = ConvictionEconomyModel(epochs=epochs, lr=lr)
    model.fit(rows)
    return model, table, parity


__all__ = [
    "ARTIFACT_FORMAT",
    "CONVICTION_USES_PER_FIT_MEETING",
    "DEFAULT_EPOCHS",
    "DEFAULT_LEARNING_RATE",
    "RIDGE_LAMBDA",
    "STALENESS_FILENAME",
    "WEIGHTS_FILENAME",
    "WEIGHTS_SHA256_FILENAME",
    "ConvictionEconomyModel",
    "ConvictionPrediction",
    "ConvictionStalenessCap",
    "ConvictionStalenessExceededError",
    "ConvictionUseCounter",
    "derive_conviction_max_uses",
    "fit_corpus_conviction_model",
    "load_conviction_model_artifact",
    "load_conviction_staleness_cap",
    "write_conviction_model_artifact",
]
