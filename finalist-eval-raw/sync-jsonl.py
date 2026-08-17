#!/usr/bin/env python3
"""Rebuild training/reports/results-finalist-eval.jsonl deterministically:
the two 17.14 rows (preserved verbatim from git HEAD of main) + every staged
phase-18 row present in scoring/*/row.json, in slate order. Idempotent."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path.home() / "ailibi-campaign-1826"
REPO = Path("/Users/danielkeinan/projects/AiLibi")
TARGET = REPO / "training/reports/results-finalist-eval.jsonl"

SLATE_ORDER = [
    "p18-imp-ea4bc955", "p18-imp-bfd145cb", "p18-imp-6d327dcb", "p18-imp-7f73929d",
    "p18-fsm-comparator",
    "p18-crew-c1-gen9", "p18-crew-c1-gen0", "p18-crew-c2-gen9", "p18-crew-c2-gen0",
]

# the 17.14 record, byte-preserved from the merge-base state of the file
base = subprocess.run(
    ["git", "show", "origin/main:training/reports/results-finalist-eval.jsonl"],
    cwd=REPO, capture_output=True, text=True, check=True,
).stdout
lines = [ln for ln in base.splitlines() if ln.strip()]
assert len(lines) == 2, f"expected exactly 2 preserved 17.14 rows, got {len(lines)}"
entrants = [json.loads(ln)["entrant"] for ln in lines]
assert entrants == ["utility-es", "policy-es"], entrants

out = list(lines)
staged = []
for arm in SLATE_ORDER:
    p = ROOT / "scoring" / arm / "row.json"
    if p.exists():
        out.append(p.read_text().strip())
        staged.append(arm)

TARGET.write_text("\n".join(out) + "\n")
print(f"wrote {len(out)} rows (2 preserved + {len(staged)} staged: {staged})")
