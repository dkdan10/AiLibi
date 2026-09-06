"""Publish the bounded, offline reasoning-evidence mechanics scorecard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.reasoning_evidence import run_scorecard, scorecard_source_paths
from _report_output import atomic_write_report, preflight_report_output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    protected = [
        *root.glob("replays/**/*.jsonl"),
        *root.glob("replays/**/roster.json"),
        *scorecard_source_paths(root),
    ]
    preflight_report_output(args.output, protected)
    result = run_scorecard(root)
    atomic_write_report(
        args.output, json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    print(
        f"Offline mechanics: {result['passed']}/{result['eligible']} cases passed; "
        f"model decision quality was not measured. Report: {args.output}"
    )
    return 0 if result["passed"] == result["eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
