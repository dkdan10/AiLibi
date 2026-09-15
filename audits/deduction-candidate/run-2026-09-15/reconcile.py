"""Derive this run's usage reconciliation from the files archived beside it.

Reads only what is in this directory — the per-unit replays and the final
checkpoint — and writes aggregates: no prompt, no prefix, no transcript text and
no per-ballot text reaches the output. It exists so that
[usage-reconciliation.json](usage-reconciliation.json) is a derivation anybody
can repeat rather than a table somebody typed.

    .venv/bin/python audits/deduction-candidate/run-2026-09-15/reconcile.py \
      audits/deduction-candidate/run-2026-09-15 \
      > audits/deduction-candidate/run-2026-09-15/usage-reconciliation.json
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LEGACY_BODY_HANDLE = re.compile(r"body-p-\d+-\d+")
ANY_BODY_HANDLE = re.compile(r"body-p-\d+(?:-\d+)?")

# One accumulator per arm, heterogeneous by nature — counters, sets, floats and
# Counters in the same mapping — so the value type is deliberately open and the
# arithmetic below is checked by the output being re-derivable rather than by
# the annotation.
ArmAccumulator = dict[str, Any]


def _empty_arm() -> ArmAccumulator:
    return {
        "graded_units": 0,
        "terminal_units": 0,
        "partial_units": 0,
        "resolved_calls": 0,
        "resolved_input_tokens": 0,
        "resolved_output_tokens": 0,
        "charged_failed_attempts": 0,
        "charged_failed_input_tokens": 0,
        "charged_failed_output_tokens": 0,
        "largest_single_output": 0,
        "largest_unit_input": 0,
        "largest_unit_output": 0,
        "ejections": 0,
        "role_correct_ejections": 0,
        "wrongful_ejections": 0,
        "supported_correct_ejections": 0,
        "naming_ballots": 0,
        "off_target_citations": 0,
        "ballot_verdicts": Counter(),
        "guard_rewritten_ballots": 0,
        "defaulted_turns": 0,
        "defaulted_votes": 0,
        "defaults_by_validation": 0,
        "defaults_by_deadline": 0,
        "degraded_openings": 0,
        "units_with_defaults": 0,
        "retried_calls": 0,
        "unaccounted_attempts": 0,
        "attempts_by_trigger": Counter(),
        "units_with_retries": 0,
        "models": set(),
        "prompt_version_markers": set(),
        "temporal_observation_versions": set(),
        "experiment_configs": set(),
        "cost_usd": 0.0,
        "model_work_seconds": 0.0,
    }


def main(directory: Path) -> int:
    checkpoint = json.loads((directory / "checkpoint-final.json").read_text())
    arms: dict[str, ArmAccumulator] = defaultdict(_empty_arm)

    # 1. The graded units, from the checkpoint written at every pair boundary.
    for unit in checkpoint["units"]:
        arm = arms[unit["arm"]]
        telemetry = unit["telemetry"]
        usage = telemetry["usage"]
        arm["graded_units"] += 1
        arm["terminal_units" if unit["stop"] == "terminal" else "partial_units"] += 1
        arm["resolved_calls"] += usage["calls"]
        arm["resolved_input_tokens"] += usage["input_tokens"]
        arm["resolved_output_tokens"] += usage["output_tokens"]
        arm["cost_usd"] += usage["cost_usd"]
        arm["model_work_seconds"] += usage["model_work_seconds"]
        arm["largest_unit_input"] = max(
            arm["largest_unit_input"], usage["input_tokens"]
        )
        arm["largest_unit_output"] = max(
            arm["largest_unit_output"], usage["output_tokens"]
        )
        if unit["ejected_player_id"] is not None:
            arm["ejections"] += 1
            if unit["role_correct"]:
                arm["role_correct_ejections"] += 1
            if unit["ejected_role"] == "CREWMATE":
                arm["wrongful_ejections"] += 1
        arm["supported_correct_ejections"] += int(unit["supported_correct_ejection"])
        arm["naming_ballots"] += unit["naming_ballots"]
        arm["off_target_citations"] += unit["off_target_citations"]
        for ballot in unit["supported"]:
            arm["ballot_verdicts"][ballot["verdict"]] += 1
            if ballot["guard_rewrite_reason"] is not None:
                arm["guard_rewritten_ballots"] += 1
        for key in (
            "defaulted_turns",
            "defaulted_votes",
            "defaults_by_validation",
            "defaults_by_deadline",
            "degraded_openings",
            "retried_calls",
            "unaccounted_attempts",
        ):
            arm[key] += telemetry[key]
        arm["attempts_by_trigger"].update(telemetry["attempts_by_trigger"])
        if (
            telemetry["defaulted_turns"]
            or telemetry["defaulted_votes"]
            or telemetry["degraded_openings"]
        ):
            arm["units_with_defaults"] += 1
        if telemetry["retried_calls"] or telemetry["unaccounted_attempts"]:
            arm["units_with_retries"] += 1
        arm["models"].update(telemetry["model_ids"])
        arm["prompt_version_markers"].update(telemetry["prompt_versions"].values())

    # 2. The abandoned pair: what the stop charged outside any graded unit.
    abandoned = {
        row["arm"]: {
            "calls": row["usage"]["calls"],
            "input_tokens": row["usage"]["input_tokens"],
            "output_tokens": row["usage"]["output_tokens"],
            "model_work_seconds": row["usage"]["model_work_seconds"],
            "retried_calls": row["retried_calls"],
            "unaccounted_attempts": row["unaccounted_attempts"],
        }
        for row in checkpoint["abandoned"]["arms"]
    }

    # 3. The replays: per-call maxima, charged failed attempts, provenance, handles.
    per_unit = []
    for path in sorted(directory.glob("*.jsonl")):
        arm_name, _, seed_text = path.stem.partition("-seed-")
        arm = arms[arm_name]
        rows = [
            json.loads(line) for line in path.read_text().splitlines() if line.strip()
        ]
        meeting = next(r for r in rows if r["kind"].startswith("meeting"))
        calls = meeting["llm_calls"]
        charged_failed = [
            r
            for r in rows
            if r["kind"] == "failed_call" and (r["input_tokens"] or r["output_tokens"])
        ]
        arm["charged_failed_attempts"] += len(charged_failed)
        arm["charged_failed_input_tokens"] += sum(
            r["input_tokens"] for r in charged_failed
        )
        arm["charged_failed_output_tokens"] += sum(
            r["output_tokens"] for r in charged_failed
        )
        arm["largest_single_output"] = max(
            [arm["largest_single_output"]]
            + [c["output_tokens"] for c in calls]
            + [r["output_tokens"] for r in charged_failed]
        )
        arm["models"].update(c["model"] for c in calls)
        arm["prompt_version_markers"].update(
            meeting.get("prompt_versions", {}).values()
        )
        ticks = [r for r in rows if r["kind"] == "tick"]
        arm["temporal_observation_versions"].update(
            t["temporal_observation_version"] for t in ticks
        )
        arm["experiment_configs"].update(
            json.dumps(t["experiment_config"], sort_keys=True) for t in ticks
        )
        handles = {
            handle
            for call in calls
            for handle in ANY_BODY_HANDLE.findall(call["prompt"] or "")
        }
        per_unit.append(
            {
                "arm": arm_name,
                "seed": int(seed_text),
                "replay_kind": meeting["kind"],
                "calls": len(calls),
                "input_tokens": sum(c["input_tokens"] for c in calls),
                "output_tokens": sum(c["output_tokens"] for c in calls),
                "largest_call_output": max([0] + [c["output_tokens"] for c in calls]),
                "charged_failed_attempts": len(charged_failed),
                "deadline_default_rows": sum(
                    1
                    for r in rows
                    if r["kind"] == "failed_call"
                    and r["error_type"] == "deadline_default"
                ),
                "outcome": meeting.get("outcome"),
                "ejected_player_id": meeting.get("ejected_player_id"),
                "temporal_observation_version": (
                    ticks[0]["temporal_observation_version"] if ticks else None
                ),
                "experiment_config": ticks[0]["experiment_config"] if ticks else None,
                "legacy_body_handles_in_prompts": sorted(
                    h for h in handles if LEGACY_BODY_HANDLE.fullmatch(h)
                ),
                "body_handles_in_prompts": sorted(handles),
            }
        )

    totals = {
        "graded_calls": sum(a["resolved_calls"] for a in arms.values()),
        "graded_input_tokens": sum(a["resolved_input_tokens"] for a in arms.values()),
        "graded_output_tokens": sum(a["resolved_output_tokens"] for a in arms.values()),
        "abandoned_calls": sum(r["calls"] for r in abandoned.values()),
        "abandoned_input_tokens": sum(r["input_tokens"] for r in abandoned.values()),
        "abandoned_output_tokens": sum(r["output_tokens"] for r in abandoned.values()),
    }
    totals["charged_calls"] = totals["graded_calls"] + totals["abandoned_calls"]
    totals["charged_input_tokens"] = (
        totals["graded_input_tokens"] + totals["abandoned_input_tokens"]
    )
    totals["charged_output_tokens"] = (
        totals["graded_output_tokens"] + totals["abandoned_output_tokens"]
    )

    payload = {
        "arms": {
            name: {
                key: (
                    sorted(value)
                    if isinstance(value, set)
                    else dict(value)
                    if isinstance(value, Counter)
                    else value
                )
                for key, value in arm.items()
            }
            for name, arm in sorted(arms.items())
        },
        "abandoned": abandoned,
        "abandoned_model_work_seconds": checkpoint["abandoned"]["model_work_seconds"],
        "totals": totals,
        "limits": checkpoint["limits"],
        "sampling": checkpoint["sampling"],
        "elapsed_seconds": checkpoint["elapsed_seconds"],
        "model_work_seconds": checkpoint["model_work_seconds"],
        "completed_paired_seeds": checkpoint["completed_seeds"],
        "execution_manifest_sha256": checkpoint["manifest_sha256"],
        "held_out_manifest_sha256": checkpoint["held_out_manifest_sha256"],
        "per_unit": sorted(per_unit, key=lambda row: (row["arm"], row["seed"])),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
