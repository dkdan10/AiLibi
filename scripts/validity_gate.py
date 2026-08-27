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

from eval.validity import ValidityGateReport, run_validity_gate  # noqa: E402


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
    args = parser.parse_args(argv)
    replay_set_dir: Path = args.replay_set_dir
    emit_json: bool = args.json
    expected_model: str | None = args.expected_model
    expected_prompt_versions: dict[str, str] | None = args.expected_prompt_versions
    require_zero_cost: bool = args.require_zero_cost

    if not replay_set_dir.is_dir():
        print(f"Replay-set directory not found: {replay_set_dir}", file=sys.stderr)
        return 2
    try:
        report = run_validity_gate(
            replay_set_dir,
            expected_model=expected_model,
            expected_prompt_versions=expected_prompt_versions,
            require_zero_cost=require_zero_cost,
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
