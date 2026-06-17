"""Phase-C probe 2 — does a non-degenerate crew BUDDY SYSTEM emerge? (blindspot).

FO-2's co-evolution collapsed because the crew move-override had NO task pressure
(clumping trivially denies kills). Here the crew keeps task pressure: a learned gate
decides each tick between BUDDY (move toward the room with the most visible
crewmates) and TASK (pass through the FSM's task routing). Fitness = crew WINS
(CREWMATE_TASKS) vs a fixed FSM impostor — which requires BOTH surviving (buddy) AND
completing tasks (don't buddy forever). If ES beats the FSM crew by learning to buddy
selectively, the buddy system emerges non-degenerately; always-buddy should LOSE
(never finishes tasks -> tick budget), proving the task pressure bites.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_spike import core  # noqa: E402
from observation.action_intent import MoveIntent, WaitIntent  # noqa: E402

TMP = core.tmp("fo8")
K = list(range(12))
GLEN = core.ENC_DIM + 1


def gate_genome(seed, scale=0.5):
    import random

    rng = random.Random(seed)
    return [rng.gauss(0.0, scale) for _ in range(GLEN)]


def _buddy(genome, packet) -> bool:
    x = core.encode(packet)
    return genome[-1] + sum(genome[i] * x[i] for i in range(core.ENC_DIM)) > 0.0


class BuddyAgent(core.SpikeAgent):
    def __init__(self, inner, *, gate, mode="learned"):
        super().__init__(inner, genome=None)
        self._gate = gate
        self._mode = mode

    def decide(self, packet, public_map):
        action = self._inner.decide(packet, public_map)
        do_buddy = self._mode == "always" or (
            self._mode == "learned" and _buddy(self._gate, packet)
        )
        # only override the task-vs-buddy ROUTING choice; never suppress a report/
        # repair/emergency interrupt the FSM chose (round-2 Comment 5)
        if do_buddy and isinstance(action, (MoveIntent, WaitIntent)):
            cur = packet.self_state.room
            # move toward the legal room holding the most visible OTHER players
            counts: dict[str, int] = {}
            for p in packet.visible_players:
                counts[p.room] = counts.get(p.room, 0) + 1
            legal = core._legal_rooms(cur)
            best = max(sorted(legal), key=lambda rm: counts.get(rm, 0))
            if counts.get(best, 0) > counts.get(cur, 0) and best != cur:
                return MoveIntent(
                    actor=self._aid, type="move", payload={"to_room": best}
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
        if role == "CREWMATE" and mode != "fsm":
            return BuddyAgent(inner, gate=gate, mode=mode)
        return inner

    return factory


def crew_wins(gate, mode, tag):
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
        max_ticks=80,
    )
    reasons: Counter[str] = Counter()
    for s in K:
        for r in core.replay_rows(out / f"replay-seed-{s}.jsonl"):
            if "reason" in r:
                reasons[r["reason"]] += 1
    return reasons.get("CREWMATE_TASKS", 0), dict(reasons)


def main() -> int:
    print("=== FO-8 — crew buddy-system under task pressure ===")
    fsm = crew_wins(None, "fsm", "fsm")
    always = crew_wins(gate_genome(0), "always", "always")
    print(f"FSM crew:       crew-wins {fsm[0]}/{len(K)} | {fsm[1]}")
    print(
        f"always-buddy:   crew-wins {always[0]}/{len(K)} | {always[1]}  (expect LOW: never finishes tasks)"
    )

    champ = gate_genome(3)
    champ_f = crew_wins(champ, "learned", "init")[0]
    print("\n(1+6)-ES on the buddy/task gate (fitness = crew wins):")
    for gen in range(10):
        best_g, best_f = champ, champ_f
        for m in range(6):
            cand = [
                w + g
                for w, g in zip(
                    champ, core.random_genome(700 * (gen + 1) + m, 0.2)[:GLEN]
                )
            ]
            f = crew_wins(cand, "learned", f"g{gen}_m{m}")[0]
            if f > best_f:
                best_g, best_f = cand, f
        champ, champ_f = best_g, best_f
        print(f"  gen {gen:2d}: champion crew-wins = {champ_f}/{len(K)}")

    lw, lr = crew_wins(champ, "learned", "final")
    print(f"\nLEARNED gate: crew-wins {lw}/{len(K)} | {lr}")
    verdict = (
        "EMERGES (beats FSM, beats always-buddy)"
        if lw > fsm[0] and lw > always[0]
        else "no gain over FSM"
        if lw <= fsm[0]
        else "matches FSM"
    )
    print(f"VERDICT: non-degenerate buddy system -> {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
