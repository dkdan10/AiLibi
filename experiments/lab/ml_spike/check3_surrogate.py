"""Check 3 — SURROGATE FIDELITY.

Can the DETERMINISTIC detector (the per-meeting `contradictions` flags the engine
already computes, no LLM) predict the real-LLM meeting ejection well enough to be
the training inner-loop surrogate? Grade two surrogate variants against the actual
`ejected_player_id` on the committed 9p2i set. Report ejection-recall separately
from SKIP-agreement so a trivial always-SKIP (66% base rate) is not mistaken for
fidelity.
"""

from __future__ import annotations

import glob
import json
from collections import Counter

FILES = sorted(glob.glob("replays/samples/9p2i/replay-seed-*.jsonl"))


def _tally(contradictions, *, strong_only: bool):
    c: Counter[str] = Counter()
    for con in contradictions:
        if strong_only and "[weak signal" in (con.get("description") or ""):
            continue
        for s in con.get("subjects") or []:
            c[s] += 1
    return c


def _predict(contradictions, *, strong_only: bool):
    """Top-tallied subject, else SKIP. Lexical tie-break (deterministic)."""
    c = _tally(contradictions, strong_only=strong_only)
    if not c:
        return "SKIP"
    top = max(c.items(), key=lambda kv: (kv[1], [-ord(ch) for ch in kv[0]]))
    return top[0]


def grade(strong_only: bool) -> dict:
    eject_hit = eject_total = skip_hit = skip_total = 0
    named = named_correct = overall = total = 0
    for f in FILES:
        for line in open(f):
            r = json.loads(line)
            if r.get("kind") != "meeting":
                continue
            actual = r.get("ejected_player_id")  # None == SKIP
            pred = _predict(r.get("contradictions") or [], strong_only=strong_only)
            total += 1
            overall += (pred == "SKIP" and actual is None) or (pred == actual)
            if actual is None:
                skip_total += 1
                skip_hit += pred == "SKIP"
            else:
                eject_total += 1
                eject_hit += pred == actual
            if pred != "SKIP":
                named += 1
                named_correct += pred == actual
    return {
        "overall": (overall, total),
        "eject_recall": (eject_hit, eject_total),
        "skip_agree": (skip_hit, skip_total),
        "precision_when_named": (named_correct, named),
    }


def _pct(hit: int, tot: int) -> str:
    return f"{hit}/{tot} ({100 * hit / tot:.0f}%)" if tot else f"{hit}/0"


def main() -> int:
    print("=== Check 3 — surrogate fidelity (committed 9p2i, 50 seeds) ===")
    for label, strong in (
        ("naive (any contradiction)", False),
        ("strong-only gate", True),
    ):
        g = grade(strong)
        print(f"\n[{label}]")
        print(f"  overall agreement:        {_pct(*g['overall'])}")
        print(
            f"  EJECTION top-1 match:     {_pct(*g['eject_recall'])}   <- charter bar ~75%"
        )
        print(f"  precision when it names:  {_pct(*g['precision_when_named'])}")
        print(f"  SKIP agreement:           {_pct(*g['skip_agree'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
