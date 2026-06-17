"""Follow-on 1 — sparse-lever learnability (gap 1).

The spike learned a DENSE decision (move every tick). The Phase-11 levers
(kill/vent/sabotage) are SPARSE — they fire a handful of times per game. Does ES
still climb when the decision is sparse? Test the same MOVE machinery but gate it
to fire ONLY in the post-kill window (the COVER moment the vent lever lives in);
the FSM drives every other tick. Fitness = post-kill EXPOSURE (co-located alive
players in the K ticks after the impostor's kill) — lower = stealthier escape, the
exact thing the validated vent lever optimizes. If ES drives exposure below the
random gate using only a few decisions/game, sparse-lever learnability holds.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_spike import core  # noqa: E402
from observation.action_intent import MoveIntent, WaitIntent  # noqa: E402

TMP = core.tmp("fo1")
KWIN = 6
K = list(range(8))
HOLD = list(range(100, 108))


class CoverAgent(core.SpikeAgent):
    def __init__(self, inner, *, genome, acc):
        super().__init__(inner, genome=genome)
        self._acc = acc  # {'exp': float, 'dec': int} shared across games
        self._last_kill = -999
        self._tick = 0

    def decide(self, packet, public_map):
        self._tick += 1
        action = self._inner.decide(packet, public_map)
        if getattr(action, "type", None) == "kill":
            self._last_kill = self._tick
        post_kill = (self._tick - self._last_kill) < KWIN
        if post_kill:
            room = packet.self_state.room
            self._acc["exp"] += sum(1 for p in packet.visible_players if p.room == room)
            if self._genome is not None and isinstance(
                action, (MoveIntent, WaitIntent)
            ):
                self._acc["dec"] += 1
                pick = core.mlp_pick_room(self._genome, packet)
                if pick == room:
                    return WaitIntent(actor=self._aid, type="wait")
                return MoveIntent(
                    actor=self._aid, type="move", payload={"to_room": pick}
                )
        return action


def _factory(genome, acc):
    from agents.tactical.crewmate_policy import CrewmatePolicy
    from agents.tactical.impostor_policy import ImpostorPolicy
    from orchestrator.game import TacticalAgent

    def factory(agent_id, role):
        if role == "IMPOSTOR":
            inner = TacticalAgent(
                agent_id=agent_id, policy=ImpostorPolicy(agent_id=agent_id), role=role
            )
            return CoverAgent(inner, genome=genome, acc=acc)
        return TacticalAgent(
            agent_id=agent_id, policy=CrewmatePolicy(agent_id=agent_id), role=role
        )

    return factory


def exposure(seeds, tag, genome):
    from eval.balance_eval import run_tournament_eval

    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    acc = {"exp": 0.0, "dec": 0}
    out = TMP / tag
    out.mkdir(parents=True, exist_ok=True)
    run_tournament_eval(
        seeds=list(seeds),
        output_dir=out,
        agent_factory=_factory(genome, acc),
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
        force=True,
    )
    return acc["exp"], acc["dec"]


def main() -> int:
    print("=== FO-1 — sparse-lever learnability (post-kill move gate) ===")
    fsm_exp, _ = exposure(K, "fsm", None)
    rnd_exp, rnd_dec = exposure(K, "rnd", core.random_genome(0))
    print(
        f"baselines (lower=stealthier): FSM exposure {fsm_exp:.0f} | random-gate {rnd_exp:.0f}"
    )
    print(
        f"  sparseness: ~{rnd_dec / len(K):.1f} gated decisions/game (vs ~30+ ticks/game)"
    )

    champ = core.random_genome(0)
    champ_f, _ = exposure(K, "init", champ)
    print("\n(1+8)-ES minimizing post-kill exposure, 10 gens:")
    for gen in range(10):
        best_g, best_f = champ, champ_f
        for m in range(8):
            cand = core.mutate(champ, seed=1000 * (gen + 1) + m, sigma=0.15)
            f, _ = exposure(K, f"g{gen}_m{m}", cand)
            if f < best_f:
                best_g, best_f = cand, f
        champ, champ_f = best_g, best_f
        print(f"  gen {gen:2d}: champion exposure = {champ_f:.0f}")

    ch_hold, _ = exposure(HOLD, "ch_hold", champ)
    rn_hold, _ = exposure(HOLD, "rn_hold", core.random_genome(0))
    print(
        f"\nIN-SAMPLE: champ {champ_f:.0f} vs random {rnd_exp:.0f} vs FSM {fsm_exp:.0f}"
    )
    print(f"HELD-OUT:  champ {ch_hold:.0f} vs random {rn_hold:.0f}")
    drop_in = (rnd_exp - champ_f) / rnd_exp if rnd_exp else 0
    drop_hold = (rn_hold - ch_hold) / rn_hold if rn_hold else 0
    print(
        f"exposure reduction vs random: in-sample {drop_in:.0%} | held-out {drop_hold:.0%}"
    )
    print(
        f"VERDICT: sparse-lever ES {'CLIMBS' if drop_hold > 0.05 else 'does NOT climb'} held-out"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
