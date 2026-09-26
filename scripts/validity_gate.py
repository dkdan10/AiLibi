"""The HARD validity gate CLI — pass/fail over a replay-set directory.

Runs the ten composed checks of :func:`eval.validity.run_validity_gate` over
ANY replay-set directory (``replays/samples/9p2i``, the committed ML corpus, a
candidate recording — any dir of ``replay-seed-*.jsonl`` plus ``roster.json``).
The gate is the HARD acceptance the Phase-14 close audit
(audits/audit-phase-14-close.md §1) grounds every number in; a failure exits
non-zero and NAMES the failing checks.

Usage::

    uv run python scripts/validity_gate.py replays/samples/9p2i
    uv run python scripts/validity_gate.py replays/samples/4p1i --json
    uv run python scripts/validity_gate.py replays/ml_corpus/9p2i \
        --expected-model Qwen/Qwen3.6-27B --require-zero-cost \
        --expected-prompt-versions vote_ballot=vote_ballot.qwen3_6_27b.v4,...
    uv run python scripts/validity_gate.py replays/candidates/<round>/9p2i \
        --expected-experiment-config replays/candidates/<round>/experiment-config.json \
        --expected-seeds 0-49 --require-one-recording-sha

``--expected-experiment-config`` declares the config every game must have
recorded (omitted, the historical defaults: no config), ``--expected-seeds``
the exact seed set of the replay files and the MANIFEST.md rows, and
``--require-one-recording-sha`` one recording sha across the MANIFEST.md. All
three are checked inside ``cost_and_provenance_exact``.

``--json`` emits the :class:`~eval.validity.ValidityGateReport` as the
machine-readable report the 15.15 harness and the 15.7 / 15.18 audits consume
(schema documented in the ``eval.validity`` module docstring).

Exit codes: ``0`` gate PASSED, ``1`` gate FAILED (>= 1 check failed), ``2`` usage
error (directory missing or no replays). A truncated replay — a recorded
``game_over`` row the engine reconstruction never reaches — is a FAILED gate
(exit ``1``) under ``all_games_reach_game_over``, its violations tagged
``truncated_replay``; it is not a usage error and never a PASS. Pure + offline:
no network, no ``AILIBI_*`` env.

Provenance: Task 15.1.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `uv run python scripts/validity_gate.py ...` to find top-level packages
# (mirrors scripts/_verify_samples.py + scripts/build_sample_report.py).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _declared_experiment import (  # noqa: E402
    DeclaredExperimentError,
    load_declared_config,
)
from eval.validity import ValidityGateReport, run_validity_gate  # noqa: E402
from orchestrator.experiment_config import RecordedExperimentConfig  # noqa: E402


def _parse_declared_config(raw: str) -> RecordedExperimentConfig:
    """Read ``--expected-experiment-config``; a file the config refuses is a usage error."""

    try:
        return load_declared_config(Path(raw)).config
    except DeclaredExperimentError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parse_seed_set(raw: str) -> frozenset[int]:
    """Parse ``A-B`` (inclusive) or a comma list ``A,B,C`` into a seed set.

    Every token is a non-negative integer and a range runs forwards; anything
    else raises, which argparse turns into the usage exit (``2``).
    """

    text = raw.strip()
    first, dash, last = text.partition("-")
    if dash:
        if not (first.strip().isdigit() and last.strip().isdigit()):
            raise argparse.ArgumentTypeError(
                f"expected FIRST-LAST or a comma list of seeds, got {raw!r}"
            )
        low, high = int(first), int(last)
        if low > high:
            raise argparse.ArgumentTypeError(f"the range {raw!r} runs backwards")
        return frozenset(range(low, high + 1))
    seeds: set[int] = set()
    for token in text.split(","):
        token = token.strip()
        if not token.isdigit():
            raise argparse.ArgumentTypeError(
                f"expected FIRST-LAST or a comma list of seeds, got {raw!r}"
            )
        seeds.add(int(token))
    return frozenset(seeds)


def _parse_prompt_versions(raw: str) -> dict[str, str]:
    """Parse ``KEY=VER,KEY=VER`` into the per-template version map.

    The map the gate compares against each game's recorded ``prompt_versions``.
    Every token must name a template and its full version string; a malformed
    value raises, which argparse turns into the documented usage exit (``2``)
    rather than a silently-partial pin.
    """

    versions: dict[str, str] = {}
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        key, sep, version = token.partition("=")
        key, version = key.strip(), version.strip()
        if not sep or not key or not version:
            raise argparse.ArgumentTypeError(
                f"expected KEY=VERSION pairs, got {token!r} (e.g. "
                "accusation_round=accusation_round.qwen3_6_27b.v4)"
            )
        if key in versions:
            raise argparse.ArgumentTypeError(f"template {key!r} named twice")
        versions[key] = version
    if not versions:
        raise argparse.ArgumentTypeError(f"names no template: {raw!r}")
    return versions


def _render_human(report: ValidityGateReport) -> str:
    lines: list[str] = [
        f"Validity gate over {report.replay_set_dir} ({report.games_total} games):",
    ]
    for check in report.checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(f"  [{status}] {check.name}: {check.summary}")
        for violation in check.violations:
            lines.append(f"          - {violation}")
    if report.passed:
        lines.append("Validity gate PASSED (all checks green).")
    else:
        failing = ", ".join(report.failing_checks())
        lines.append(f"Validity gate FAILED: {failing}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the HARD validity gate over a replay-set directory (Task 15.1; "
            "audits/audit-phase-14-close.md §1). Pure, offline, CPU only."
        ),
    )
    parser.add_argument(
        "replay_set_dir",
        type=Path,
        help="directory of replay-seed-*.jsonl files (e.g. replays/samples/9p2i)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable ValidityGateReport JSON instead of text",
    )
    parser.add_argument(
        "--expected-model",
        default=None,
        help=(
            "pin the provenance row to this exact model id (e.g. Qwen/Qwen3-32B); "
            "omitted, provenance is checked for coherence only (the generic default)"
        ),
    )
    parser.add_argument(
        "--expected-prompt-versions",
        type=_parse_prompt_versions,
        default=None,
        metavar="KEY=VER,KEY=VER",
        help=(
            "pin every game's prompt-version provenance to this exact "
            "per-template map, e.g. "
            "accusation_round=accusation_round.qwen3_6_27b.v4,"
            "crewmate_report=crewmate_report.qwen3_6_27b.v4 (a version string "
            "carries its own template prefix, so the pairs read doubled); "
            "omitted, the set is only checked for a COHERENT version map, which "
            "a set recorded homogeneously at the wrong version still satisfies"
        ),
    )
    parser.add_argument(
        "--require-zero-cost",
        action="store_true",
        help=(
            "require every cost row to be exactly $0 (the audit's flat-rate "
            "baselines); omitted, any finite non-negative cost is accepted"
        ),
    )
    parser.add_argument(
        "--expected-experiment-config",
        type=_parse_declared_config,
        default=None,
        metavar="FILE",
        help=(
            "require every game to have recorded exactly the experiment config "
            "this JSON file declares; a file with an unknown field or an invalid "
            "value is a usage error. Omitted, every game must have recorded "
            "none: the historical defaults"
        ),
    )
    parser.add_argument(
        "--expected-seeds",
        type=_parse_seed_set,
        default=None,
        metavar="FIRST-LAST|A,B,C",
        help=(
            "require the replay files and the MANIFEST.md rows to hold exactly "
            "these seeds; omitted, the seed set is not checked"
        ),
    )
    parser.add_argument(
        "--require-one-recording-sha",
        action="store_true",
        help=(
            "require MANIFEST.md to name one recording sha on every row; "
            "omitted, a set recorded in more than one pass is accepted"
        ),
    )
    args = parser.parse_args(argv)
    replay_set_dir: Path = args.replay_set_dir
    emit_json: bool = args.json
    expected_model: str | None = args.expected_model
    expected_prompt_versions: dict[str, str] | None = args.expected_prompt_versions
    require_zero_cost: bool = args.require_zero_cost
    expected_experiment_config: RecordedExperimentConfig | None = (
        args.expected_experiment_config
    )
    expected_seeds: frozenset[int] | None = args.expected_seeds
    require_one_recording_sha: bool = args.require_one_recording_sha

    if not replay_set_dir.is_dir():
        print(f"Replay-set directory not found: {replay_set_dir}", file=sys.stderr)
        return 2
    try:
        report = run_validity_gate(
            replay_set_dir,
            expected_model=expected_model,
            expected_prompt_versions=expected_prompt_versions,
            require_zero_cost=require_zero_cost,
            expected_experiment_config=expected_experiment_config,
            expected_seeds=expected_seeds,
            require_one_recording_sha=require_one_recording_sha,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if emit_json:
        print(report.model_dump_json(indent=2))
    else:
        print(_render_human(report))
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
