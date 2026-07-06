"""The HARD validity gate CLI — pass/fail over a replay-set directory (Task 15.1).

Runs the eight composed checks of :func:`eval.validity.run_validity_gate` over
ANY replay-set directory (``replays/samples/9p2i``, the 15.7 Wave-0 close set, the
15.12 corpus, a Wave-2 candidate recording — any dir of ``replay-seed-*.jsonl``
plus ``roster.json``). The gate is the HARD acceptance the Phase-14 close audit
(audits/audit-phase-14-close.md §1) grounds every number in; a failure exits
non-zero and NAMES the failing checks.

Usage::

    uv run python scripts/validity_gate.py replays/samples/9p2i
    uv run python scripts/validity_gate.py replays/samples/4p1i --json

``--json`` emits the :class:`~eval.validity.ValidityGateReport` as the
machine-readable report the 15.15 harness and the 15.7 / 15.18 audits consume
(schema documented in the ``eval.validity`` module docstring).

Exit codes: ``0`` gate PASSED, ``1`` gate FAILED (>= 1 check failed), ``2`` usage
error (directory missing or no replays). Pure + offline: no network, no
``AILIBI_*`` env.
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
    args = parser.parse_args(argv)
    replay_set_dir: Path = args.replay_set_dir
    emit_json: bool = args.json

    if not replay_set_dir.is_dir():
        print(f"Replay-set directory not found: {replay_set_dir}", file=sys.stderr)
        return 2
    try:
        report = run_validity_gate(replay_set_dir)
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
