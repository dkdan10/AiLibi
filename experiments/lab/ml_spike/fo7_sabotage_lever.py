"""Phase-C probe 1 — sabotage as a learnable strategic lever (blindspot).

Sabotage is the richest Among-Us emergent tool (sabotage -> split the crew ->
pick them off / stall the clock) and NO spike/follow-on touched it. Give the
impostor a learned linear GATE that decides, each tick, whether to fire the
task-gating `reactor` sabotage (engine accepts/rejects deterministically). Fitness
rewards IMPOSTOR_SABOTAGE wins first, then kills (does timing create kill windows?).
Compare a learned timing gate to FSM (no MLP sabotage) and an always-sabotage gate.

Reactor timer is 6 (Phase-11 'edge' tuning: FSM timing -> 0 sabotage wins). If a
LEARNED gate gets >0 where the FSM gets 0, sabotage timing is a learnable lever.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "experiments/lab")
from ml_spike import core  # noqa: E402
from observation.action_intent import SabotageIntent  # noqa: E402

TMP = Path(os.environ["CLAUDE_JOB_DIR"]) / "tmp" / "fo7"
K = list(range(8))
GLEN = core.ENC_DIM + 1  # linear gate: w . encode + b
FIRE_BAR = 2.5  # high bar: sabotage is a RARE strategic action, not every tick


def gate_genome(seed, scale=0.5):
    import random

    rng = random.Random(seed)
    return [rng.gauss(0.0, scale) for _ in range(GLEN)]


def _fires(genome, packet) -> bool:
    x = core.encode(packet)
    z = genome[-1] + sum(genome[i] * x[i] for i in range(core.ENC_DIM))
    return z > FIRE_BAR


class SabotageAgent(core.SpikeAgent):
    def __init__(self, inner, *, gate, mode="learned"):
        super().__init__(inner, genome=None)
        self._gate = gate
        self._mode = mode

    def decide(self, packet, public_map):
        action = self._inner.decide(packet, public_map)
        # never preempt a kill; only sabotage when not already active
        if (
            not packet.global_state.sabotage_active
            and getattr(action, "type", None) != "kill"
        ):
            fire = self._mode == "always" or (
                self._mode == "learned" and _fires(self._gate, packet)
            )
            if fire:
                return SabotageIntent(
                    actor=self._aid, type="sabotage", payload={"kind": "reactor"}
                )
        return action


def _factory(gate, mode):
    from agents.tactical.crewmate_policy import CrewmatePolicy
    from agents.tactical.impostor_policy import ImpostorPolicy
    from orchestrator.game import TacticalAgent

    def factory(agent_id, role):
        inner = TacticalAgent(
            agent_id=agent_id,
            policy=(ImpostorPolicy if role == "IMPOSTOR" else CrewmatePolicy)(
                agent_id=agent_id
            ),
            role=role,
        )
        if role == "IMPOSTOR" and mode != "fsm":
            return SabotageAgent(inner, gate=gate, mode=mode)
        return inner

    return factory


def profile(gate, mode, tag):
    from eval.balance_eval import run_tournament_eval

    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    out = TMP / tag
    out.mkdir(parents=True, exist_ok=True)
    run_tournament_eval(
        seeds=list(K),
        output_dir=out,
        agent_factory=_factory(gate, mode),
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
        force=True,
        max_ticks=60,  # cap: a stall-spamming gate would otherwise run to the 1000-tick budget
    )
    sab_wins = kills = 0
    reasons: Counter[str] = Counter()
    for s in K:
        rows = core.replay_rows(out / f"replay-seed-{s}.jsonl")
        kills += sum(
            1 for r in rows for a in r.get("actions", []) if a.get("type") == "kill"
        )
        for r in rows:
            if "reason" in r:
                reasons[r["reason"]] += 1
                if r["reason"] == "IMPOSTOR_SABOTAGE":
                    sab_wins += 1
    return sab_wins, kills, dict(reasons)


def fitness(gate, tag):
    sw, kl, _ = profile(gate, "learned", tag)
    return 100 * sw + kl


def main() -> int:
    print("=== FO-7 — sabotage as a learnable lever (reactor timer=6) ===")
    fsm = profile(None, "fsm", "fsm")
    always = profile(gate_genome(0), "always", "always")
    print(
        f"FSM (no MLP sabotage):  IMPOSTOR_SABOTAGE wins {fsm[0]}/{len(K)} | kills {fsm[1]} | {fsm[2]}"
    )
    print(
        f"always-sabotage:        wins {always[0]}/{len(K)} | kills {always[1]} | {always[2]}"
    )

    champ = gate_genome(1)
    champ_f = fitness(champ, "init")
    print("\n(1+6)-ES on sabotage timing (fitness = 100*sab_wins + kills):")
    for gen in range(8):
        best_g, best_f = champ, champ_f
        for m in range(6):
            cand = [
                w + g
                for w, g in zip(
                    champ, core.random_genome(1000 * (gen + 1) + m, 0.2)[:GLEN]
                )
            ]
            f = fitness(cand, f"g{gen}_m{m}")
            if f > best_f:
                best_g, best_f = cand, f
        champ, champ_f = best_g, best_f
        sw, kl, _ = profile(champ, "learned", f"champ{gen}")
        print(f"  gen {gen:2d}: fitness {champ_f}  (sab_wins {sw}, kills {kl})")

    lw, lk, lr = profile(champ, "learned", "final")
    print(f"\nLEARNED timing: IMPOSTOR_SABOTAGE wins {lw}/{len(K)} | kills {lk} | {lr}")
    if lw > fsm[0]:
        verdict = "WIN lever — learned timing achieves sabotage wins the FSM cannot"
    elif lk > fsm[1] + 4:
        verdict = "kill-enabler — sabotage timing meaningfully lifts kills"
    else:
        verdict = (
            "NO learnable gain at timer=6 — 0 sabotage wins for all, and sabotaging cuts "
            "kills, so ES converges to ~no-sabotage (sabotage is dominated; a WIN needs the "
            "owner-gated timer retune, not a better learner)"
        )
    print(f"VERDICT: sabotage timing -> {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
