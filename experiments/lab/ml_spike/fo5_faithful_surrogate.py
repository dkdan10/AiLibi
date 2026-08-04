"""FROZEN (Phase 19 tier map, training/README.md): the throwaway feasibility spike.
Bug fixes and evidence readers only; no new search.

Follow-on 5 — grade the FAITHFUL deterministic surrogate (gap 5).

The pressure-test flagged check3's naive top-1 tally as a strawman: the real
pipeline weights flags (weak 0.08 / strong 0.30) against a 0.60 gate and
accumulates across meetings. Grade that gate against the committed real-LLM
ejections, single-meeting AND cross-meeting-accumulated, to see whether a
faithful RULE-BASED surrogate can carry the inner loop or whether the ejection
cases genuinely need a learned/real-LLM gate.

Caveat: no decay (the real accumulator decays when a subject is cleared); the
accumulated variant is therefore an UPPER bound on what the gate would fire.
"""

from __future__ import annotations

import glob
import json
from collections import defaultdict

FILES = sorted(glob.glob("replays/samples/9p2i/replay-seed-*.jsonl"))
# weak/strong are suspicion DELTAS from the 0.5 prior (agents/memory/beliefs.py:33,54);
# the §4.6 gate is an ABSOLUTE suspicion of 0.60, so eject iff 0.5 + Σdelta >= 0.60
# (round-2 Comment 6: comparing Σdelta >= 0.60 wrongly forced one-strong / two-weak to SKIP).
PRIOR, WEAK, STRONG, GATE = 0.5, 0.08, 0.30, 0.60


def _weights(contradictions):
    w: dict[str, float] = defaultdict(float)
    for con in contradictions:
        delta = WEAK if "[weak signal" in (con.get("description") or "") else STRONG
        for s in con.get("subjects") or []:
            w[s] += delta
    return w


def _gate_pred(weights):
    top = max(weights.items(), key=lambda kv: (kv[1], kv[0]), default=None)
    # suspicion = prior + accumulated delta, clamped to 1.0; eject the top subject if
    # it clears the absolute 0.60 gate (round-2 Comment 6)
    if top and min(1.0, PRIOR + top[1]) >= GATE:
        return top[0]
    return "SKIP"


def grade():
    res = {
        k: dict(
            eject_hit=0, eject_total=0, skip_hit=0, skip_total=0, named=0, named_ok=0
        )
        for k in ("single", "accumulated")
    }
    for f in FILES:
        carry: dict[str, float] = defaultdict(float)
        for line in open(f):
            r = json.loads(line)
            if r.get("kind") != "meeting":
                continue
            actual = r.get("ejected_player_id")
            w = _weights(r.get("contradictions") or [])
            for s, d in w.items():
                carry[s] += d
            preds = {"single": _gate_pred(w), "accumulated": _gate_pred(dict(carry))}
            for k, pred in preds.items():
                b = res[k]
                if actual is None:
                    b["skip_total"] += 1
                    b["skip_hit"] += pred == "SKIP"
                else:
                    b["eject_total"] += 1
                    b["eject_hit"] += pred == actual
                if pred != "SKIP":
                    b["named"] += 1
                    b["named_ok"] += pred == actual
    return res


def _p(h, t):
    return f"{h}/{t} ({100 * h / t:.0f}%)" if t else f"{h}/0"


def main() -> int:
    print("=== FO-5 — faithful surrogate (weak .08 / strong .30, gate .60) ===")
    res = grade()
    for k in ("single", "accumulated"):
        b = res[k]
        print(f"\n[{k} meeting]")
        print(f"  EJECTION top-1 recall: {_p(b['eject_hit'], b['eject_total'])}")
        print(f"  precision when named:  {_p(b['named_ok'], b['named'])}")
        print(f"  SKIP agreement:        {_p(b['skip_hit'], b['skip_total'])}")
    print("\nread: a faithful gate is high-SKIP-precision but low-ejection-recall —")
    print("the committed flags are too weak to reach .60, so the LLM's ejections are")
    print("driven by signals the deterministic layer lacks (testimony/plurality).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
