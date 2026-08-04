"""FROZEN (Phase 19 tier map, training/README.md): the throwaway feasibility spike.
Bug fixes and evidence readers only; no new search.

Follow-on 6 — the LINCHPIN: a LEARNED vote-surrogate (gap 5, decisive).

FO-5 showed the rule-based deterministic gate can't predict LLM ejections. The
pressure-test said: a LEARNED model on the detector signal might. But a deeper
finding first: ALL 112 committed contradictions are alibi-based (alibi_vs_sighting/
alibi_conflict) — they need the LLM's spoken alibi, so at TRAINING time (no LLM)
there are ZERO flags. So this tests two surrogates by supervised learning on the
committed real-LLM ejections, by-GAME train/test split:

  Part A (flag features)     — OPTIMISTIC upper bound: needs the LLM to exist, but
                               answers "does learning beat the 56% hand-tally?"
  Part B (physical features) — the HONEST LLM-free surrogate: reconstruct positions
                               from the action stream -> sightings, proximity-to-kill,
                               reporter. The only signal available at training time.

If Part B can't predict ejections, no cheap surrogate exists -> Phase C must use a
real-LLM selection gate or a tactically-reachable interestingness proxy.
"""

from __future__ import annotations

import glob
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)  # experiments/lab (Comment 4)
from ml_spike import core  # noqa: E402

FILES = sorted(glob.glob("replays/samples/9p2i/replay-seed-*.jsonl"))


def parse_game(path: Path):
    """Snapshot per-meeting candidate features (flag + physical) + the ejected label,
    using `core.reconstruct` for engine-faithful positions/sightings — it resolves
    kills in engine order (excludes rejected same-tick kills, round-2 Comment 1/3) and
    hides vented players from sightings (round-2 Comment 7)."""
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    witnessed: dict[str, int] = defaultdict(int)
    isolation: dict[str, int] = defaultdict(int)
    seen_at_kill: dict[str, int] = defaultdict(int)
    carry: dict[str, float] = defaultdict(float)
    pending_kills: list[tuple[int, str]] = []  # (tick, body_room) -- resolved only
    meetings = []
    midx = 0

    for st in core.reconstruct(rows):
        if "tick" in st:
            tick = st["tick"]
            for players in st["visible"].values():  # vent-excluded, co-location groups
                if len(players) >= 2:
                    for p in players:
                        witnessed[p] += 1
                else:
                    isolation[players[0]] += 1
            for _killer, _victim, broom in st["kills"]:  # resolved kills only
                pending_kills.append((tick, broom))
            for ktick, broom in pending_kills:
                if 0 <= tick - ktick <= 2:
                    here = st["visible"].get(broom, [])
                    if len(here) >= 2:
                        for p in here:
                            seen_at_kill[p] = 1
        else:  # meeting
            row, ejected, alive = st["meeting"], st["ejected"], st["alive"]
            weak: dict[str, int] = defaultdict(int)
            strong: dict[str, int] = defaultdict(int)
            for c in row.get("contradictions") or []:
                is_weak = "[weak signal" in (c.get("description") or "")
                for s in c.get("subjects") or []:
                    (weak if is_weak else strong)[s] += 1
                    carry[s] += 0.08 if is_weak else 0.30
            reporter = row.get("triggered_by")
            cands = []
            for p in sorted(alive):
                flag_feat = [
                    weak[p],
                    strong[p],
                    carry[p],
                    float(p == reporter),
                    float(midx),
                    float(len(alive)),
                ]
                phys_feat = [
                    witnessed[p],
                    isolation[p],
                    float(seen_at_kill[p]),
                    float(p == reporter),
                    float(midx),
                    float(len(alive)),
                ]
                cands.append((p, flag_feat, phys_feat, 1 if p == ejected else 0))
            meetings.append({"cands": cands, "ejected": ejected})
            witnessed = defaultdict(int)
            isolation = defaultdict(int)
            seen_at_kill = defaultdict(int)
            pending_kills = []
            midx += 1
    return meetings


# ---- pure-Python standardized logistic regression -----------------------------
def _standardize(rows):
    n = len(rows[0])
    mean = [sum(r[i] for r in rows) / len(rows) for i in range(n)]
    var = [sum((r[i] - mean[i]) ** 2 for r in rows) / len(rows) for i in range(n)]
    std = [math.sqrt(v) or 1.0 for v in var]
    return mean, std


def _z(x, mean, std):
    return [(x[i] - mean[i]) / std[i] for i in range(len(x))]


def train_logit(X, y, *, epochs=120, lr=0.1, seed=0):
    mean, std = _standardize(X)
    Xz = [_z(x, mean, std) for x in X]
    n = len(Xz[0])
    w = [0.0] * n
    b = 0.0
    rng = random.Random(seed)
    idx = list(range(len(Xz)))
    for _ in range(epochs):
        rng.shuffle(idx)
        for t in idx:
            z = b + sum(w[i] * Xz[t][i] for i in range(n))
            p = 1.0 / (1.0 + math.exp(-max(min(z, 30), -30)))
            g = p - y[t]
            for i in range(n):
                w[i] -= lr * g * Xz[t][i]
            b -= lr * g
    return (w, b, mean, std)


def _score(model, x):
    w, b, mean, std = model
    xz = _z(x, mean, std)
    z = b + sum(w[i] * xz[i] for i in range(len(w)))
    return 1.0 / (1.0 + math.exp(-max(min(z, 30), -30)))


def evaluate(meetings_train, meetings_test, feat_ix):
    X = [c[feat_ix] for m in meetings_train for c in m["cands"]]
    y = [c[3] for m in meetings_train for c in m["cands"]]
    model = train_logit(X, y)
    # tune SKIP threshold on train
    best_tau, best_acc = 0.5, -1.0
    for tau in [i / 20 for i in range(1, 20)]:
        acc = sum(_meeting_correct(m, model, feat_ix, tau) for m in meetings_train)
        if acc > best_acc:
            best_acc, best_tau = acc, tau
    # test
    ej_hit = ej_tot = sk_hit = sk_tot = rank_hit = top2_hit = 0
    for m in meetings_test:
        pred = _predict(m, model, feat_ix, best_tau)
        if m["ejected"] is None:
            sk_tot += 1
            sk_hit += pred == "SKIP"
        else:
            ej_tot += 1
            ej_hit += pred == m["ejected"]
            # rank recall (argmax, ignore SKIP) + top-2 (matters for a CONTINUOUS
            # suspicion-rank fitness, which is the real training use)
            ranked = sorted(m["cands"], key=lambda c: -_score(model, c[feat_ix]))
            rank_hit += ranked[0][0] == m["ejected"]
            top2_hit += (
                m["ejected"] in {ranked[0][0], ranked[1][0]} if len(ranked) > 1 else 0
            )
    return ej_hit, ej_tot, sk_hit, sk_tot, best_tau, rank_hit, top2_hit


def _predict(m, model, feat_ix, tau):
    best_p, best_c = -1.0, "SKIP"
    for c in m["cands"]:
        p = _score(model, c[feat_ix])
        if p > best_p:
            best_p, best_c = p, c[0]
    return best_c if best_p >= tau else "SKIP"


def _meeting_correct(m, model, feat_ix, tau):
    pred = _predict(m, model, feat_ix, tau)
    return (pred == "SKIP" and m["ejected"] is None) or (pred == m["ejected"])


def main() -> int:
    games = [parse_game(Path(f)) for f in FILES]
    train = [m for g in games[:35] for m in g]
    test = [m for g in games[35:] for m in g]
    n_ej = sum(1 for m in test if m["ejected"])
    print("=== FO-6 — learned vote-surrogate (by-game split: 35 train / 15 test) ===")
    print(
        "reframe: ALL 112 contradictions are alibi-based -> a TRUE no-LLM surrogate "
        "has ZERO flags; Part A is an optimistic upper bound."
    )
    print(f"test set: {len(test)} meetings, {n_ej} ejections\n")
    print(
        f"{'surrogate':30} | RANK top-1 (vs naive 56%) | RANK top-2 | with-SKIP | SKIP agree"
    )
    for label, ix in (
        ("A: flag features (LLM-dep)", 1),
        ("B: physical features (LLM-FREE)", 2),
    ):
        eh, et, sh, st, tau, rh, t2 = evaluate(train, test, ix)
        print(
            f"{label:30} |     {rh}/{et} ({100 * rh / et:.0f}%)        |  {t2}/{et} ({100 * t2 / et:.0f}%)  |"
            f"  {eh}/{et} ({100 * eh / et:.0f}%)  |  {sh}/{st} ({100 * sh / st:.0f}%)"
        )
    print(
        "\nRANK recall = argmax candidate==ejected ignoring SKIP (apples-to-apples vs the"
    )
    print("naive top-subject tally's 56%). baselines: naive 56% / faithful-gate 5%.")
    print("read: if Part B (LLM-free physical) clears ~the naive bar, a cheap learned")
    print("surrogate is viable; if it stays near base-rate, no cheap surrogate exists")
    print("-> Phase C needs a real-LLM selection gate or a tactically-reachable proxy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
