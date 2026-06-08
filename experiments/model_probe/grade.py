"""Deterministic grader + report over a probe run.

Reads a ``probe-*.jsonl`` matrix run and aggregates per cell
(model x think x num_ctx x variant):

- **F1 (decision):** conversion rate — how often the model voted an *available*
  true impostor (one the prompt showed at suspicion >= threshold) — plus skip
  rate and parse-success. The corpus is pre-filtered to crew votes where a
  conversion was available, so a low conversion rate is the F1 failure.
- **F2 (config):** rationale length (the think=false reason-in-output
  pollution), thinking length, output tokens, latency, and parse-success (the
  truncation / empty-response symptoms) by think-mode and num_ctx.

With >1 variant present it also does **attribution**: per corpus item, across
variants on the same model+config, classify the recorded skip as
prompt-fixable (some variant converts it), config-fixable (a config flips it),
or model-bound (nothing converts it on any cell).

Usage::

    python -m experiments.model_probe.grade --in p1-5seed --out p1-5seed
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"


@dataclass
class Cell:
    model: str
    think: bool
    num_ctx: int
    variant: str
    records: list[dict[str, object]] = field(default_factory=list)

    @property
    def key(self) -> tuple[str, bool, int, str]:
        return (self.model, self.think, self.num_ctx, self.variant)

    def _f(self, name: str) -> list[float]:
        out: list[float] = []
        for record in self.records:
            value = record.get(name)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                out.append(float(value))
        return out

    def summary(self) -> dict[str, object]:
        n = len(self.records)
        parsed = [r for r in self.records if r.get("parsed_ok")]
        converted = [r for r in parsed if r.get("voted_available_impostor")]
        skips = [r for r in parsed if r.get("target") == "SKIP"]

        # Bucket A: an impostor was available (>= threshold) -> conversion metric.
        # Bucket B: none available -> any non-SKIP vote is a false ejection.
        bucket_a = [r for r in parsed if r.get("available_impostor_ids")]
        bucket_b = [r for r in parsed if not r.get("available_impostor_ids")]
        conv_a = [r for r in bucket_a if r.get("voted_available_impostor")]
        false_eject_b = [r for r in bucket_b if r.get("target") not in (None, "SKIP")]

        def _mean(vals: list[float]) -> float:
            return round(statistics.fmean(vals), 1) if vals else 0.0

        return {
            "model": self.model,
            "think": self.think,
            "num_ctx": self.num_ctx,
            "variant": self.variant,
            "calls": n,
            "parse_ok": len(parsed),
            "parse_ok_rate": round(len(parsed) / n, 3) if n else 0.0,
            # conversion among ALL calls (parse-fail = no vote = no conversion,
            # the production-realistic denominator) and among parsed only.
            "conversion_of_all": round(len(converted) / n, 3) if n else 0.0,
            "conversion_of_parsed": (
                round(len(converted) / len(parsed), 3) if parsed else 0.0
            ),
            # Bucket-split (the load-bearing pair): conversion where an impostor
            # was available, false-ejection where none was.
            "n_avail": len(bucket_a),
            "conversion_avail": (
                round(len(conv_a) / len(bucket_a), 3) if bucket_a else None
            ),
            "n_noavail": len(bucket_b),
            "false_eject_noavail": (
                round(len(false_eject_b) / len(bucket_b), 3) if bucket_b else None
            ),
            "skip_rate_of_parsed": (
                round(len(skips) / len(parsed), 3) if parsed else 0.0
            ),
            "mean_latency_s": _mean(self._f("latency_s")),
            "mean_out_tokens": _mean(self._f("out_tokens")),
            "mean_rationale_chars": _mean(self._f("rationale_chars")),
            "max_rationale_chars": (
                int(max(self._f("rationale_chars")))
                if self._f("rationale_chars")
                else 0
            ),
            "mean_thinking_chars": _mean(self._f("thinking_chars")),
        }


def load_cells(path: Path) -> dict[tuple[str, bool, int, str], Cell]:
    cells: dict[tuple[str, bool, int, str], Cell] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = (rec["model"], bool(rec["think"]), int(rec["num_ctx"]), rec["variant"])
        cells.setdefault(
            key,
            Cell(model=key[0], think=key[1], num_ctx=key[2], variant=key[3]),
        ).records.append(rec)
    return cells


def attribution(cells: dict[tuple[str, bool, int, str], Cell]) -> dict[str, object]:
    """Classify each recorded-skip item as prompt- / config- / model-fixable.

    Only meaningful with >1 variant. An item is prompt-fixable if a non-baseline
    variant converts it on the SAME (model, config) where baseline did not;
    config-fixable if a config change converts it on the baseline prompt;
    model-bound if nothing converts it anywhere.
    """

    variants = {key[3] for key in cells}
    if variants == {"baseline"}:
        return {"note": "single variant (baseline) — run >1 variant for attribution"}

    # item_id -> set of (model,think,ctx,variant) that converted it
    converters: dict[str, set[tuple[str, bool, int, str]]] = defaultdict(set)
    baseline_converters: dict[str, set[tuple[str, bool, int]]] = defaultdict(set)
    inversion_items: set[str] = set()
    for cell in cells.values():
        for rec in cell.records:
            item = str(rec["item_id"])
            if rec.get("is_inversion"):
                inversion_items.add(item)
            if rec.get("parsed_ok") and rec.get("voted_available_impostor"):
                converters[item].add(cell.key)
                if cell.variant == "baseline":
                    baseline_converters[item].add(
                        (cell.model, cell.think, cell.num_ctx)
                    )

    prompt_fixable: list[str] = []
    config_fixable: list[str] = []
    model_bound: list[str] = []
    for item in sorted(inversion_items):
        cell_keys = converters.get(item, set())
        if any(k[3] != "baseline" for k in cell_keys):
            prompt_fixable.append(item)
        elif baseline_converters.get(item):
            config_fixable.append(item)
        else:
            model_bound.append(item)
    return {
        "inversion_items": len(inversion_items),
        "prompt_fixable": prompt_fixable,
        "config_fixable": config_fixable,
        "model_bound": model_bound,
    }


def _table(rows: list[dict[str, object]]) -> str:
    cols = [
        "model",
        "think",
        "num_ctx",
        "variant",
        "calls",
        "parse_ok_rate",
        "n_avail",
        "conversion_avail",
        "n_noavail",
        "false_eject_noavail",
        "skip_rate_of_parsed",
        "mean_rationale_chars",
        "mean_latency_s",
    ]
    head = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    lines = [head, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="infile", type=str, required=True)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    in_path = RESULTS_DIR / f"probe-{args.infile}.jsonl"
    cells = load_cells(in_path)
    rows = sorted(
        (c.summary() for c in cells.values()),
        key=lambda r: (r["model"], r["think"], r["num_ctx"], r["variant"]),
    )

    table = _table(rows)
    attr = attribution(cells)
    print(table)
    print("\nattribution:", json.dumps(attr, indent=2))

    if args.out:
        md = [
            f"# Model-probe findings — {args.infile}",
            "",
            "## Per-cell metrics (model × think × num_ctx × variant)",
            "",
            table,
            "",
            "## Attribution (recorded skips: prompt- vs config- vs model-fixable)",
            "",
            "```json",
            json.dumps(attr, indent=2),
            "```",
        ]
        out_path = RESULTS_DIR / f"findings-{args.out}.md"
        out_path.write_text("\n".join(md), encoding="utf-8")
        print(f"\nfindings -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
