"""Follow-on 3 — rubric fitness vs the tactical layer (gap 3).

The spike optimized KILLS (dense, tactical). The real objective is the rubric, which
is ~80% meeting-driven (R1 ejection-decided, R2 deception, R3 arcs, R7 evidence). Does
the tactical layer even MOVE the rubric? Compare two impostor policies whose KILLS
differ ~2x (random vs FSM) and read their rubric-relevant outcomes off the generated
games. If kills swing 2x while the rubric components stay pinned near zero, kills and
the rubric are DECOUPLED and the tactical layer cannot climb the rubric in the fake-
meeting harness — i.e. rubric-as-fitness REQUIRES a working (real/surrogate) meeting
layer in the loop (which FO-5 showed is the hard part). That is the fitness-mismatch
made concrete, and it ties gap 3 to gap 5.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "experiments/lab")
from ml_spike import core  # noqa: E402

TMP = Path(os.environ["CLAUDE_JOB_DIR"]) / "tmp" / "fo3"
SEEDS = list(range(12))


def profile(genome, tag):
    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    core.run_games(SEEDS, TMP / tag, genome=genome)
    kills = reasons = mtgs = evid_mtgs = ejections = 0
    reasons = Counter()
    for s in SEEDS:
        for row in core.replay_rows(TMP / tag / f"replay-seed-{s}.jsonl"):
            if row.get("kind") == "meeting":
                mtgs += 1
                if row.get("contradictions"):
                    evid_mtgs += 1
                if row.get("ejected_player_id"):
                    ejections += 1
            for a in row.get("actions", []):
                if a.get("type") == "kill":
                    kills += 1
            if "reason" in row:
                reasons[row["reason"]] += 1
    return dict(
        kills=kills, mtgs=mtgs, evid=evid_mtgs, eject=ejections, reasons=dict(reasons)
    )


def main() -> int:
    print(
        "=== FO-3 — does the tactical layer move the RUBRIC? (fake-meeting harness) ===\n"
    )
    rnd = profile(core.random_genome(0), "rnd")
    fsm = profile(None, "fsm")
    print(
        f"{'policy':10} | kills | meetings | evidence-mtgs (R7) | ejections (R1) | win-reasons"
    )
    for name, p in (("random", rnd), ("FSM", fsm)):
        print(
            f"{name:10} |  {p['kills']:3d}  |   {p['mtgs']:3d}    |        {p['evid']:2d}          |"
            f"      {p['eject']:2d}        | {p['reasons']}"
        )
    print()
    print(
        f"kills swing: random {rnd['kills']} -> FSM {fsm['kills']} "
        f"({fsm['kills'] / max(rnd['kills'], 1):.1f}x)"
    )
    print(
        f"rubric R1 (ejections): {rnd['eject']} vs {fsm['eject']}  |  "
        f"R7 (evidence meetings): {rnd['evid']} vs {fsm['evid']}"
    )
    flat = rnd["eject"] == fsm["eject"] and rnd["evid"] == fsm["evid"]
    print(
        f"\nVERDICT: rubric components {'FLAT across a 2x kill swing' if flat else 'moved'} -> "
        f"tactical play {'cannot' if flat else 'can'} climb the rubric in the fake harness."
    )
    print(
        "=> rubric-as-fitness needs a real/surrogate MEETING layer in the loop (gap 5);"
    )
    print(
        "   training the tactical layer on the rubric without it would optimize noise."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
