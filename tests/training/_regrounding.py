"""The interim seam while the ML re-ground is outstanding.

The baseline-7 record re-recorded ``replays/ml_corpus`` without re-fitting the
committed ML artifacts. Re-grounding them is a NAMED follow-up
(``audits/audit-phase-20-baseline-7.md`` §10.2), deliberately out of the
record's scope: a re-fit re-states the ML program's own findings, and doing that
inside a recording task would fold two decisions into one commit.

Until it lands, the committed surrogate is a baseline-6 fit sitting on a
baseline-7 corpus, and ``load_surrogate_runner_factory`` refuses to score across
that gap -- correctly, loudly, and by design (Task 18.14's fit-corpus fence).
That refusal is PINNED, not worked around:
``tests/training/test_surrogate_runner.py::test_the_committed_surrogate_is_a_baseline6_fit_on_a_baseline7_corpus``
holds the mismatch, and the fence test holds the refusal.

What this module supplies is different, and narrower: a LOCAL copy of the
committed artifact whose fit-corpus record names the corpus it is actually
handed. The weights are untouched -- this is not a shortcut around the re-ground
and produces no evidence about model quality. Its only job is to keep the
end-to-end bake-off paths (which load a surrogate before they can run at all)
under test while the fit is stale, so a regression in the HARNESS is not hidden
behind a refusal about the MODEL.

When the re-ground lands, the tripwire tests fail, this module has no reason to
exist, and every caller can point back at the committed artifact directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from training.surrogate.runner import (
    fit_corpus_fingerprint,
    load_fit_corpus_record,
)

_ARTIFACT_FILES: Final[tuple[str, ...]] = (
    "ballot-predictor.json",
    "ballot-predictor.json.sha256",
    "max-uses.json",
)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
COMMITTED_ARTIFACT_DIR: Final[Path] = (
    _REPO_ROOT / "training" / "artifacts" / "surrogate"
)
LIVE_CORPUS_DIR: Final[Path] = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"


def artifact_copy_fingerprinted_to_the_live_corpus(destination: Path) -> Path:
    """Copy the committed surrogate into ``destination``, re-fingerprinted.

    Weights, sha256 sidecar and staleness cap are copied verbatim; only the
    fit-corpus record's ``corpus_sha256`` is re-pointed at the live corpus, which
    is the one field standing between the harness and a run. Returns
    ``destination`` so a caller can pass it straight to
    ``surrogate_artifact_dir=``.
    """

    destination.mkdir(parents=True, exist_ok=True)
    for name in _ARTIFACT_FILES:
        (destination / name).write_text(
            (COMMITTED_ARTIFACT_DIR / name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    record = load_fit_corpus_record(COMMITTED_ARTIFACT_DIR).model_copy(
        update={"corpus_sha256": fit_corpus_fingerprint(LIVE_CORPUS_DIR)}
    )
    (destination / "fit-corpus.json").write_text(
        record.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    return destination
