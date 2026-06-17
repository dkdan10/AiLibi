"""Check 2 — LEARNABILITY + BOOTSTRAP.

(a) ES: does an impostor-fitness (kills over K seeds) CLIMB above a random genome
    when we evolve the move-policy against the frozen FSM crew + frozen rules?
(b) Bootstrap: does imitation-init (behavior-clone the FSM's move choices, pure-
    Python SGD) reach FSM-parity, so evolution can start from competence not zero?

Pure-Python, no deps. Fitness = total impostor kills (random moves wreck the FSM
stalk, so the gap is real and the lever is the move decision).
"""

from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, "experiments/lab")
from ml_spike import core  # noqa: E402

TMP = Path(os.environ["CLAUDE_JOB_DIR"]) / "tmp" / "check2"
K = list(range(8))  # fitness seeds
ENC, HID, OUT = core.ENC_DIM, core.HID, core.OUT
O1, O2, O3 = ENC * HID, ENC * HID + HID, ENC * HID + HID + HID * OUT


# ---------- (b) behavior cloning the FSM move choices (SGD) --------------------
def harvest(seeds):
    sink: list = []
    core.run_games(seeds, TMP / "bc_harvest", record_sink=sink)
    return [(x, core._ROOM_IX[chosen]) for (x, chosen, _cur) in sink]


def _fwd_cache(g, x):
    h = [0.0] * HID
    for j in range(HID):
        s = g[O1 + j]
        base = j * ENC
        for i in range(ENC):
            s += g[base + i] * x[i]
        h[j] = math.tanh(s)
    logit = [0.0] * OUT
    for k in range(OUT):
        s = g[O3 + k]
        base = O2 + k * HID
        for j in range(HID):
            s += g[base + j] * h[j]
        logit[k] = s
    return h, logit


def _softmax(logit):
    m = max(logit)
    e = [math.exp(v - m) for v in logit]
    z = sum(e)
    return [v / z for v in e]


def bc_train(data, *, epochs=25, lr=0.2, seed=1):
    g = core.random_genome(seed, scale=0.1)
    rng = random.Random(seed)
    idx = list(range(len(data)))
    for _ in range(epochs):
        rng.shuffle(idx)
        for t in idx:
            x, tgt = data[t]
            h, logit = _fwd_cache(g, x)
            p = _softmax(logit)
            dlogit = [p[k] - (1.0 if k == tgt else 0.0) for k in range(OUT)]
            dh = [0.0] * HID
            for k in range(OUT):
                dl = dlogit[k]
                base = O2 + k * HID
                for j in range(HID):
                    dh[j] += dl * g[base + j]
                    g[base + j] -= lr * dl * h[j]
                g[O3 + k] -= lr * dl
            for j in range(HID):
                dpre = dh[j] * (1.0 - h[j] * h[j])
                base = j * ENC
                for i in range(ENC):
                    g[base + i] -= lr * dpre * x[i]
                g[O1 + j] -= lr * dpre
    return g


def bc_accuracy(g, data):
    hit = 0
    for x, tgt in data:
        _h, logit = _fwd_cache(g, x)
        if max(range(OUT), key=lambda k: (logit[k], k)) == tgt:
            hit += 1
    return hit / len(data) if data else 0.0


# ---------- (a) ES on kills ----------------------------------------------------
def fitness(genome, tag) -> int:
    return core.kills_over(K, TMP / tag, genome=genome)


def es(gens=12, lam=9, sigma=0.15, seed=0):
    champ = core.random_genome(seed)
    champ_fit = fitness(champ, "es_init")
    history = [champ_fit]
    for gen in range(gens):
        best_g, best_f = champ, champ_fit
        for m in range(lam):
            cand = core.mutate(champ, seed=1000 * (gen + 1) + m, sigma=sigma)
            f = fitness(cand, f"es_g{gen}_m{m}")
            if f > best_f:
                best_g, best_f = cand, f
        champ, champ_fit = best_g, best_f
        history.append(champ_fit)
        print(f"  gen {gen:2d}: champion kills/{len(K)}seeds = {champ_fit}")
    return champ, history


def main() -> int:
    print("=== Check 2 — learnability + bootstrap (8 fitness seeds) ===\n")
    fsm = fitness(None, "fsm")
    rnd = fitness(core.random_genome(0), "rnd")
    print(f"baselines: FSM-stalk kills = {fsm} | random-genome kills = {rnd}\n")

    print("(a) ES climbing kills from a random genome:")
    _champ, hist = es()
    print(
        f"  -> ES: {hist[0]} (gen0) -> {hist[-1]} (gen{len(hist) - 1}); FSM ceiling = {fsm}\n"
    )

    print("(b) Bootstrap — behavior-clone the FSM move policy:")
    data = harvest(list(range(12)))
    cut = int(0.8 * len(data))
    train, test = data[:cut], data[cut:]
    bc = bc_train(train)
    acc = bc_accuracy(bc, test)
    bc_kills = fitness(bc, "bc_kills")
    print(
        f"  BC dataset: {len(data)} impostor move-decisions ({len(train)} train / {len(test)} test)"
    )
    print(f"  move-prediction parity (held-out top-1): {acc:.0%}")
    print(f"  BC-genome kills = {bc_kills} vs FSM = {fsm} vs random = {rnd}")

    es_ok = hist[-1] > hist[0]
    bc_ok = bc_kills >= 0.7 * fsm
    print(f"\nVERDICT: ES-climbs={es_ok} | BC-reaches-parity={bc_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
