"""Phase-C probe 3 — diversity vs MONOCULTURE (blindspot).

Plain ES converges to ONE policy; real Among-Us interest comes from strategy
DIVERSITY. Run N independent ES runs (different seeds, same kills objective) and
ask: do the champions converge to the SAME behavior (monoculture -> Phase-D
quality-diversity is mandatory) or naturally DIFFERENT behavior (less urgent)?
Behavior signature = each champion's chosen-move-room distribution on a fixed
held-out set; report pairwise cosine similarity + held-out kills.
"""

from __future__ import annotations

import math
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "experiments/lab")
from ml_spike import core  # noqa: E402
from observation.action_intent import MoveIntent, WaitIntent  # noqa: E402

TMP = Path(os.environ["CLAUDE_JOB_DIR"]) / "tmp" / "fo9"
K = list(range(6))
SIG = list(range(100, 106))
N = 4


class LogAgent(core.SpikeAgent):
    def __init__(self, inner, *, genome, sink):
        super().__init__(inner, genome=genome)
        self._sink = sink

    def decide(self, packet, public_map):
        action = self._inner.decide(packet, public_map)
        if self._genome is not None and isinstance(action, (MoveIntent, WaitIntent)):
            pick = core.mlp_pick_room(self._genome, packet)
            self._sink.append(pick)
            if pick == packet.self_state.room:
                return WaitIntent(actor=self._aid, type="wait")
            return MoveIntent(actor=self._aid, type="move", payload={"to_room": pick})
        return action


def signature(genome, tag):
    from agents.tactical.crewmate_policy import CrewmatePolicy
    from agents.tactical.impostor_policy import ImpostorPolicy
    from eval.balance_eval import run_tournament_eval
    from orchestrator.game import TacticalAgent

    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    sink: list[str] = []

    def factory(agent_id, role):
        inner = TacticalAgent(
            agent_id=agent_id,
            policy=(ImpostorPolicy if role == "IMPOSTOR" else CrewmatePolicy)(
                agent_id=agent_id
            ),
            role=role,
        )
        return (
            LogAgent(inner, genome=genome, sink=sink) if role == "IMPOSTOR" else inner
        )

    out = TMP / tag
    out.mkdir(parents=True, exist_ok=True)
    run_tournament_eval(
        seeds=list(SIG),
        output_dir=out,
        agent_factory=factory,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
        force=True,
    )
    c = Counter(sink)
    tot = sum(c.values()) or 1
    return [c.get(r, 0) / tot for r in core.ROOMS]


def es(seed, gens=8, lam=6):
    champ = core.random_genome(seed)
    champ_f = core.kills_over(K, TMP / f"es{seed}_init", genome=champ)
    for gen in range(gens):
        for m in range(lam):
            cand = core.mutate(champ, seed=seed * 9973 + 1000 * gen + m, sigma=0.15)
            f = core.kills_over(K, TMP / f"es{seed}_g{gen}_m{m}", genome=cand)
            if f > champ_f:
                champ, champ_f = cand, f
    return champ


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def main() -> int:
    print(f"=== FO-9 — diversity vs monoculture ({N} independent ES runs) ===")
    champs, sigs, kills = [], [], []
    for i in range(N):
        c = es(10 + i)
        champs.append(c)
        sigs.append(signature(c, f"sig{i}"))
        kills.append(core.kills_over(SIG, TMP / f"k{i}", genome=c))
        print(f"  champion {i}: held-out kills = {kills[i]}")
    sims = [cosine(sigs[i], sigs[j]) for i in range(N) for j in range(i + 1, N)]
    mean_sim = sum(sims) / len(sims)
    print(
        f"\npairwise move-distribution cosine similarity: "
        f"min {min(sims):.2f} / mean {mean_sim:.2f} / max {max(sims):.2f}"
    )
    print(f"held-out kills spread: {kills}")
    if mean_sim > 0.9:
        verdict = "MONOCULTURE — independent ES converge to the SAME behavior; Phase-D quality-diversity is MANDATORY for varied emergence"
    elif mean_sim > 0.7:
        verdict = "PARTIAL convergence — some shared structure; QD recommended"
    else:
        verdict = "NATURAL DIVERSITY — independent ES find different behaviors; QD less urgent"
    print(f"VERDICT: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
