"""FROZEN (Phase 19 tier map, training/README.md): evidence reader; instrument frozen.
Bug fixes and evidence readers only; no new search.

The conviction-model fidelity harness + the pre-stated GO bar (Task 18.15).

Judges a :class:`~training.conviction.model.ConvictionEconomyModel` on the
committed corpus split's HELD-OUT side against the bar the task contract
pre-states (audits/audit-phase-18-planning.md §2.3; committed here BEFORE the
first evaluation ran):

1. **Flag channel** — held-out per-meeting flag-count RANK correlation:
   Spearman(predicted ``expected_flags``, actual ``flags_minted``) over every
   test meeting, with average ranks on ties (flag counts are small integers).
   Bar: :data:`CONVICTION_SPEARMAN_BAR` (≥ 0.5).
2. **Conversion channel** — conversion-prediction fidelity ≥
   :data:`CONVICTION_CONVERSION_CEILING_RATIO` × (1 − ``voice_driven_share``),
   BOTH measured on the same held-out population. Fidelity is the held-out
   RECALL on the actual testimony-backed-conversion meetings (the model calls
   conversion at P ≥ :data:`CONVICTION_CONVERSION_DECISION_THRESHOLD`): the
   ceiling's structure is a recall bound — a conversion that formed from the
   current meeting's spoken narrative carries no pre-meeting physical signal,
   so a fenced model structurally cannot flag it, exactly as the honest
   ceiling bounds the surrogate's top-1 (``training/surrogate/fidelity.py``).
   Precision and accuracy are reported beside it, never substituted for it.
3. **Trivial-constant channel** — held-out ``conversion_accuracy`` strictly above
   the population's own best constant answer
   (:func:`conversion_trivial_baseline`). Recall alone cannot see a degenerate
   head: an always-convert model has no false negatives, so its recall is 1.0 on
   any corpus and axis 2 waves it through. The surrogate bar has carried exactly
   this comparator (``always_eject_baseline``) since it was written; this is its
   conviction-side twin, a strict inequality against a MEASURED constant, so it
   adds no tunable threshold.

``voice_driven_share`` is the honest ceiling's complement measured on the
held-out rows via the table's per-row ``ceiling_reachable`` bit
(1 − reachable/ejections) — the structural denominator the verdict quotes, a
MEASUREMENT, never a target.

The population-relative doctrine travels: every number in the verdict is
measured on the SAME held-out population by this harness; nothing is compared
against a previous baseline's absolute figure.

**The verdict is machine-readable for 18.16** (:class:`ConvictionGoVerdict`):
GO ⇔ every axis holds, and the consequence mapping is pre-committed in the same
breath — GO ⇒ the fitness term SHIPS on both sides and the referee pre-screen
GATES real-path spend; NO-GO ⇒ the term is structurally ABSENT (not
zero-weighted) and the pre-screen is ADVISORY only, the model surviving as a
diagnostic. The committed ``verdict.json`` beside the weights artifact carries
exactly this object, sha-keyed to the weights it judged, so 18.16 consumes the
verdict's fields — never a prose reading of the report.

Public surface (stable — downstream tasks import these):
:class:`ConvictionFidelityReport`, :class:`ConvictionGoVerdict`,
:func:`run_conviction_fidelity`, :func:`decide_conviction_go`,
:func:`spearman_rank_correlation`, :func:`conversion_trivial_baseline`,
:func:`write_conviction_verdict_artifact`, :func:`load_conviction_verdict`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final, Literal

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field

from training.conviction.dataset import ConvictionTable, validate_conviction_split
from training.conviction.model import (
    DEFAULT_EPOCHS,
    DEFAULT_LEARNING_RATE,
    ConvictionEconomyModel,
)

# The pre-stated GO bar's two constants (task contract, committed before the
# first held-out evaluation): the Spearman floor is absolute BY DESIGN (a rank
# correlation is already population-relative — it carries no unit the
# population could move); the conversion bar is population-relative through the
# measured voice-driven share, per the ratified anti-absolute-number doctrine.
CONVICTION_SPEARMAN_BAR: Final[float] = 0.5
CONVICTION_CONVERSION_CEILING_RATIO: Final[float] = 0.75

# The conversion head's decision threshold: the standard probability argmax
# (P ≥ 0.5 calls conversion). Fixed BEFORE the first held-out evaluation and
# never tuned against it — tuning the threshold on the verdict population
# would be exactly the peeking the FIRST-evaluation discipline forbids.
CONVICTION_CONVERSION_DECISION_THRESHOLD: Final[float] = 0.5

# The committed verdict filename beside the weights artifact.
VERDICT_FILENAME: Final[str] = "verdict.json"


def conversion_trivial_baseline(*, conversions: int, meetings: int) -> float:
    """The accuracy a constant conversion head reaches on this population.

    ``max(base_rate, 1 - base_rate)`` over ``conversions / meetings`` — whichever
    constant answer, "always convert" or "never convert", the population itself
    rewards more. A measured constant, so the axis it feeds introduces no tunable
    threshold; the surrogate bar has compared against its own such constant
    (``always_eject_baseline``) since the bar was written, and axis 3 below is
    the conviction side of the same comparator.
    """

    if meetings <= 0:
        raise ValueError(
            "the trivial conversion baseline is undefined on an empty held-out "
            "population"
        )
    base_rate = conversions / meetings
    return max(base_rate, 1.0 - base_rate)


def _average_ranks(values: NDArray[np.float64]) -> NDArray[np.float64]:
    """1-based average ranks (ties share the mean rank) — deterministic."""

    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=np.float64)
    sorted_values = values[order]
    index = 0
    n = len(values)
    while index < n:
        end = index
        while end + 1 < n and sorted_values[end + 1] == sorted_values[index]:
            end += 1
        average = (index + end) / 2.0 + 1.0
        for position in range(index, end + 1):
            ranks[order[position]] = average
        index = end + 1
    return ranks


def spearman_rank_correlation(
    predicted: NDArray[np.float64], actual: NDArray[np.float64]
) -> float:
    """Spearman rank correlation with average ranks on ties (deterministic).

    Pearson correlation over the two rank vectors — the standard tie-aware
    form (flag counts are small integers, so ties are the norm, not the edge
    case). Fails loud on degenerate input: fewer than two observations or a
    side with zero rank variance has no defined rank correlation, and a
    silent 0.0 would read as an honest miss (AGENTS.md "no silent fallbacks").
    """

    if len(predicted) != len(actual):
        raise ValueError(
            f"spearman needs paired samples, got {len(predicted)} predictions "
            f"vs {len(actual)} labels"
        )
    if len(predicted) < 2:
        raise ValueError(f"spearman is undefined over {len(predicted)} observation(s)")
    predicted_ranks = _average_ranks(predicted)
    actual_ranks = _average_ranks(actual)
    predicted_std = float(predicted_ranks.std())
    actual_std = float(actual_ranks.std())
    if predicted_std == 0.0 or actual_std == 0.0:
        raise ValueError(
            "spearman is undefined on a constant side (zero rank variance) — "
            "refusing to report a fabricated correlation"
        )
    centered_predicted = predicted_ranks - predicted_ranks.mean()
    centered_actual = actual_ranks - actual_ranks.mean()
    return float(
        (centered_predicted @ centered_actual)
        / (len(predicted) * predicted_std * actual_std)
    )


class ConvictionFidelityReport(BaseModel):
    """The conviction model's held-out fidelity, all channels together (frozen).

    Measured on the committed split's TEST games only — the fit side
    (``train ∪ val``) never contributes a scored meeting. The conversion
    confusion census (``true_positives`` …) makes the recall concrete;
    ``voice_driven_share`` is the held-out ceiling complement the conversion
    bar divides through. Fit-side label censuses are context, never verdict
    inputs.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    games_total: int
    fit_games: int
    test_games: int
    fit_meetings: int
    test_meetings: int
    # Flag channel (every test meeting).
    flag_spearman: float
    flag_mae: float
    test_flags_total: int
    fit_flags_total: int
    # Conversion channel (test meetings; threshold-called at the pinned 0.5).
    conversions_fit: int
    conversions_test: int
    conversion_attempts_test: int
    predicted_conversions: int
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    conversion_recall: float
    conversion_precision: float | None
    conversion_accuracy: float
    # The honest ceiling on the SAME held-out population (a measurement).
    test_ejections: int
    test_reachable: int
    voice_driven_share: float


def run_conviction_fidelity(
    table: ConvictionTable,
    *,
    model: ConvictionEconomyModel | None = None,
    epochs: int = DEFAULT_EPOCHS,
    lr: float = DEFAULT_LEARNING_RATE,
) -> tuple[ConvictionFidelityReport, ConvictionEconomyModel]:
    """Evaluate on the committed split's held-out side (fit side never scored).

    Requires a committed ``splits.json`` — the verdict's held-out discipline
    has no meaning under derived folds (a K-fold union scores every game, so
    nothing stays held out for a single pre-registered evaluation). ``model``
    ``None`` fits a fresh model on the fit side (the canonical corpus path —
    the exact fit :func:`~training.conviction.model.fit_corpus_conviction_model`
    commits); passing a fitted (typically artifact-loaded) model evaluates the
    FROZEN weights without a refit, the byte-exact reload path. Degenerate
    held-out populations fail loud: zero test ejections or zero test
    conversions leave an axis undefined, and no verdict over them can be
    honest.
    """

    # The committed split must PARTITION the table's games (disjoint, full
    # coverage, no unknown seeds) before any row selection — a leaked seed
    # would fit on a test game and silently bias the verdict.
    fit_seeds, test_seeds = validate_conviction_split(table)
    fit_rows = [row for row in table.rows if row.seed in fit_seeds]
    test_rows = [row for row in table.rows if row.seed in test_seeds]
    if not fit_rows:
        raise ValueError(
            f"{table.replay_set_dir}: the committed fit side carries no "
            "meetings — nothing to fit on"
        )
    if not test_rows:
        raise ValueError(
            f"{table.replay_set_dir}: the committed test side carries no "
            "meetings — nothing to judge"
        )

    if model is None:
        model = ConvictionEconomyModel(epochs=epochs, lr=lr)
        model.fit(fit_rows)

    predictions = [model.predict(row.features) for row in test_rows]
    predicted_flags = np.asarray(
        [prediction.expected_flags for prediction in predictions], dtype=np.float64
    )
    actual_flags = np.asarray(
        [float(row.flags_minted) for row in test_rows], dtype=np.float64
    )
    flag_spearman = spearman_rank_correlation(predicted_flags, actual_flags)
    flag_mae = float(np.mean(np.abs(predicted_flags - actual_flags)))

    true_positives = false_positives = false_negatives = true_negatives = 0
    for row, prediction in zip(test_rows, predictions, strict=True):
        called = prediction.conversion_prob >= CONVICTION_CONVERSION_DECISION_THRESHOLD
        if row.testimony_backed_conversion:
            if called:
                true_positives += 1
            else:
                false_negatives += 1
        elif called:
            false_positives += 1
        else:
            true_negatives += 1
    conversions_test = true_positives + false_negatives
    if conversions_test == 0:
        raise ValueError(
            f"{table.replay_set_dir}: the held-out population carries no "
            "testimony-backed conversions — the conversion axis is undefined, "
            "so no verdict can be honest"
        )
    test_ejections = sum(1 for row in test_rows if row.is_ejection)
    if test_ejections == 0:
        raise ValueError(
            f"{table.replay_set_dir}: the held-out population carries no "
            "ejections — the voice-driven share is undefined, so no verdict "
            "can be honest"
        )
    test_reachable = sum(1 for row in test_rows if row.ceiling_reachable)
    predicted_conversions = true_positives + false_positives

    return (
        ConvictionFidelityReport(
            replay_set_dir=table.replay_set_dir,
            games_total=table.games_total,
            fit_games=len(fit_seeds),
            test_games=len(test_seeds),
            fit_meetings=len(fit_rows),
            test_meetings=len(test_rows),
            flag_spearman=flag_spearman,
            flag_mae=flag_mae,
            test_flags_total=sum(row.flags_minted for row in test_rows),
            fit_flags_total=sum(row.flags_minted for row in fit_rows),
            conversions_fit=sum(
                1 for row in fit_rows if row.testimony_backed_conversion
            ),
            conversions_test=conversions_test,
            conversion_attempts_test=sum(row.conversion_attempted for row in test_rows),
            predicted_conversions=predicted_conversions,
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            true_negatives=true_negatives,
            conversion_recall=true_positives / conversions_test,
            conversion_precision=(
                true_positives / predicted_conversions
                if predicted_conversions
                else None
            ),
            conversion_accuracy=(true_positives + true_negatives) / len(test_rows),
            test_ejections=test_ejections,
            test_reachable=test_reachable,
            voice_driven_share=1.0 - test_reachable / test_ejections,
        ),
        model,
    )


class ConvictionGoVerdict(BaseModel):
    """The pre-stated GO/NO-GO verdict for the conviction model (frozen).

    GO ⇔ ALL THREE axes hold on the held-out population, judged by this harness:

    1. ``flag_spearman >= CONVICTION_SPEARMAN_BAR`` (0.5);
    2. ``conversion_recall >= CONVICTION_CONVERSION_CEILING_RATIO ×
       (1 − voice_driven_share)`` — the voice-driven share measured on the
       SAME population, never a previous baseline's figure;
    3. ``conversion_accuracy > conversion_trivial_baseline`` — the population's
       own best constant answer (:func:`conversion_trivial_baseline`). A head
       that always calls conversion has recall 1.0 and clears axis 2 on any
       corpus; axis 3 is what a degenerate head cannot pass.

    Pre-committed in the same breath (the task contract): NO-GO ⇒ the model is
    DIAGNOSTIC-ONLY — the fitness term does not ship (structurally absent from
    both sides, not zero-weighted) and 18.16 integrates the pre-screen only as
    advisory. ``fitness_term`` / ``prescreen_role`` / ``model_role`` encode
    exactly that mapping so 18.16 consumes the verdict, not a prose reading of
    it. ``weights_sha256`` keys the verdict to the exact frozen artifact it
    judged. The staleness cap ships regardless of the verdict.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    weights_sha256: str = Field(min_length=64, max_length=64)
    # The shared held-out population every number below was measured on.
    test_meetings: int
    test_ejections: int
    conversions_test: int
    # Axis 1 — held-out per-meeting flag-count rank correlation.
    flag_spearman: float
    spearman_bar: float
    meets_spearman_bar: bool
    # Axis 2 — conversion recall against the honest-ceiling-relative bar.
    conversion_recall: float
    voice_driven_share: float
    conversion_ceiling: float
    conversion_ceiling_ratio: float
    conversion_bar: float
    meets_conversion_bar: bool
    # Axis 3 — held-out conversion accuracy against the population's own trivial
    # constant. ``None`` means exactly one thing: this verdict predates axis 3.
    # :func:`decide_conviction_go` always populates all three (a test pins that),
    # so the only artifact that can read ``None`` is one committed before the
    # axis existed, which still loads rather than taking the composed runner's
    # GO gate down with it.
    conversion_accuracy: float | None = None
    conversion_trivial_baseline: float | None = None
    beats_trivial_conversion: bool | None = None
    verdict: Literal["GO", "NO-GO"]
    # The machine-readable consequence mapping for 18.16.
    fitness_term: Literal["ships", "absent"]
    prescreen_role: Literal["gating", "advisory"]
    model_role: Literal["training-signal", "diagnostic-only"]


def decide_conviction_go(
    report: ConvictionFidelityReport, *, weights_sha256: str
) -> ConvictionGoVerdict:
    """Apply the pre-stated bar to a held-out fidelity report.

    ``weights_sha256`` names the frozen artifact the report's numbers were
    produced by, keying the committed verdict to it. The verdict is taken on
    the FIRST held-out evaluation — the report's numbers are never iterated
    against the bar (a process discipline this function cannot enforce but the
    committed report records).
    """

    meets_spearman = report.flag_spearman >= CONVICTION_SPEARMAN_BAR
    conversion_ceiling = 1.0 - report.voice_driven_share
    conversion_bar = CONVICTION_CONVERSION_CEILING_RATIO * conversion_ceiling
    meets_conversion = report.conversion_recall >= conversion_bar
    trivial_baseline = conversion_trivial_baseline(
        conversions=report.conversions_test, meetings=report.test_meetings
    )
    beats_trivial = report.conversion_accuracy > trivial_baseline
    is_go = meets_spearman and meets_conversion and beats_trivial
    return ConvictionGoVerdict(
        replay_set_dir=report.replay_set_dir,
        weights_sha256=weights_sha256,
        test_meetings=report.test_meetings,
        test_ejections=report.test_ejections,
        conversions_test=report.conversions_test,
        flag_spearman=report.flag_spearman,
        spearman_bar=CONVICTION_SPEARMAN_BAR,
        meets_spearman_bar=meets_spearman,
        conversion_recall=report.conversion_recall,
        voice_driven_share=report.voice_driven_share,
        conversion_ceiling=conversion_ceiling,
        conversion_ceiling_ratio=CONVICTION_CONVERSION_CEILING_RATIO,
        conversion_bar=conversion_bar,
        meets_conversion_bar=meets_conversion,
        conversion_accuracy=report.conversion_accuracy,
        conversion_trivial_baseline=trivial_baseline,
        beats_trivial_conversion=beats_trivial,
        verdict="GO" if is_go else "NO-GO",
        # The pre-committed consequence mapping: a NO-GO model is a diagnostic
        # — the fitness term is structurally absent and the pre-screen only
        # ever advises; 18.16 branches on these fields.
        fitness_term="ships" if is_go else "absent",
        prescreen_role="gating" if is_go else "advisory",
        model_role="training-signal" if is_go else "diagnostic-only",
    )


def write_conviction_verdict_artifact(
    verdict: ConvictionGoVerdict, artifact_dir: Path
) -> None:
    """Commit the machine-readable verdict beside the weights artifact.

    Sorted keys + one trailing newline (byte-stable re-serialization). 18.16
    loads this file — never re-derives the verdict at integration time and
    never reads it out of the report's prose.
    """

    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / VERDICT_FILENAME).write_text(
        json.dumps(verdict.model_dump(), indent=2, sort_keys=True) + "\n"
    )


def load_conviction_verdict(artifact_dir: Path) -> ConvictionGoVerdict:
    """Read the committed verdict beside the weights artifact (fail loud)."""

    path = artifact_dir / VERDICT_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed conviction verdict at {path}; 18.16 consumes the "
            "machine-readable verdict, never a prose reading of the report"
        )
    return ConvictionGoVerdict.model_validate_json(path.read_text())


__all__ = [
    "CONVICTION_CONVERSION_CEILING_RATIO",
    "CONVICTION_CONVERSION_DECISION_THRESHOLD",
    "CONVICTION_SPEARMAN_BAR",
    "VERDICT_FILENAME",
    "ConvictionFidelityReport",
    "ConvictionGoVerdict",
    "conversion_trivial_baseline",
    "decide_conviction_go",
    "load_conviction_verdict",
    "run_conviction_fidelity",
    "spearman_rank_correlation",
    "write_conviction_verdict_artifact",
]
