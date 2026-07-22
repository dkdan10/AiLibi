"""The conviction-economy proxy — evidence supply → conviction (Task 18.15).

The training-signal instrument Phase 18 was chartered around
(audits/audit-phase-18-planning.md §2.3, owner-ratified locked decision 1): a
deterministic model ``g(pre-meeting typed state) → (expected contradiction
flags minted, expected testimony-backed conversion)`` fit on the committed
corpus's recorded triples, over ONLY channels a training-time runner honestly
reconstructs at ``run_meeting`` time — never a transcript-derived feature.
INDEPENDENT of the ballot surrogate (``training/surrogate/`` — untouched, its
own fence, its own verdict; the 18.15 designer ruling) and AST-firewalled from
``eval/watchability.py`` (the labels are mirrored from recorded bytes, never
imported — the Goodhart-adjacent seam's structural guard).

Three committed folds:

* :mod:`training.conviction.dataset` — the per-meeting table: fenced
  evidence-supply features (belief-scalar aggregates, vent-witness pins,
  kill/body-proximity pins, roster scalars) joined to the mirrored referee
  labels (flags minted, testimony-backed conversion) and the per-row honest-
  ceiling reachability bit.
* :mod:`training.conviction.model` — the two-head deterministic numpy fit,
  the float-hex + sha256 artifact, and the sha-keyed staleness machinery under
  the ~143× rule.
* :mod:`training.conviction.fidelity` — the single pre-registered held-out
  evaluation, the pre-stated GO bar (Spearman ≥ 0.5 AND conversion recall ≥
  0.75 × (1 − voice_driven_share), same-population), and the machine-readable
  GO/NO-GO consequence 18.16 consumes.

Public surface (stable signatures — downstream tasks import these):

* :class:`training.conviction.model.ConvictionEconomyModel`
* :func:`training.conviction.dataset.build_conviction_table`
* :func:`training.conviction.fidelity.decide_conviction_go`
"""

from __future__ import annotations

from training.conviction.dataset import (
    CONVICTION_FEATURE_NAMES,
    CONVICTION_FEATURE_PROVENANCE,
    ConvictionMeetingRow,
    ConvictionTable,
    build_conviction_table,
    require_clean_walk,
    validate_conviction_split,
)
from training.conviction.fidelity import (
    ConvictionFidelityReport,
    ConvictionGoVerdict,
    decide_conviction_go,
    load_conviction_verdict,
    run_conviction_fidelity,
)
from training.conviction.model import (
    ConvictionEconomyModel,
    ConvictionPrediction,
    ConvictionStalenessCap,
    ConvictionUseCounter,
    derive_conviction_max_uses,
    fit_corpus_conviction_model,
    load_conviction_model_artifact,
)

__all__ = [
    "CONVICTION_FEATURE_NAMES",
    "CONVICTION_FEATURE_PROVENANCE",
    "ConvictionEconomyModel",
    "ConvictionFidelityReport",
    "ConvictionGoVerdict",
    "ConvictionMeetingRow",
    "ConvictionPrediction",
    "ConvictionStalenessCap",
    "ConvictionTable",
    "ConvictionUseCounter",
    "build_conviction_table",
    "decide_conviction_go",
    "derive_conviction_max_uses",
    "fit_corpus_conviction_model",
    "load_conviction_model_artifact",
    "load_conviction_verdict",
    "require_clean_walk",
    "run_conviction_fidelity",
    "validate_conviction_split",
]
