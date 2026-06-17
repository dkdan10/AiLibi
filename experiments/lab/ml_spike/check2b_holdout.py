"""Check 2b — does the ES champion GENERALIZE? (closes the train/test leak).

The original Check 2 selected AND reported the champion on the same 8 seeds
(range(8)) — an in-sample maximum. Re-score the champion, random, and FSM on a
DISJOINT held-out seed band. If the champion's edge over random survives, the
learnability climb is real; if it collapses toward random, it was seed-overfit.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_spike import core  # noqa: E402

TMP = core.tmp("check2b")
TRAIN = list(range(8))
HOLD = list(range(100, 108))  # disjoint


def es(gens=10, lam=8, sigma=0.15, seed=0):
    champ = core.random_genome(seed)
    champ_fit = core.kills_over(TRAIN, TMP / "init", genome=champ)
    for gen in range(gens):
        for m in range(lam):
            cand = core.mutate(champ, seed=1000 * (gen + 1) + m, sigma=sigma)
            f = core.kills_over(TRAIN, TMP / f"g{gen}_m{m}", genome=cand)
            if f > champ_fit:
                champ, champ_fit = cand, f
    return champ, champ_fit


def main() -> int:
    champ, in_sample = es()
    rnd = core.random_genome(0)
    n = len(HOLD)
    ch_hold = core.kills_over(HOLD, TMP / "ch_hold", genome=champ)
    rn_hold = core.kills_over(HOLD, TMP / "rn_hold", genome=rnd)
    fsm_hold = core.kills_over(HOLD, TMP / "fsm_hold", genome=None)
    rn_train = core.kills_over(TRAIN, TMP / "rn_train", genome=rnd)

    print("=== Check 2b — ES generalization (train range(8) -> held-out 100-107) ===")
    print(f"IN-SAMPLE (train 8 seeds):  champion {in_sample}  | random {rn_train}")
    print(
        f"HELD-OUT ({n} seeds):       champion {ch_hold}  | random {rn_hold}  | FSM {fsm_hold}"
    )
    edge_train = in_sample - rn_train
    edge_hold = ch_hold - rn_hold
    print(f"edge over random: in-sample +{edge_train} | held-out +{edge_hold}")
    if edge_hold >= 0.5 * edge_train and edge_hold > 0:
        print("VERDICT: climb GENERALIZES (edge survives held-out) — learnability real")
    elif edge_hold > 0:
        print("VERDICT: PARTIAL — positive but shrunken edge (some seed-overfit)")
    else:
        print("VERDICT: COLLAPSE — edge was seed-overfit (learnability NOT shown)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
