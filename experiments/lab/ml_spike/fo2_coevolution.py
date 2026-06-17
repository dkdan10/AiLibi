"""Follow-on 2 — co-evolution stability (gap 2).

The spike's clean climb was vs a FROZEN FSM crew. Phase C co-evolves BOTH sides.
Run 2-population alternating ES: evolve the impostor move-policy to MAXIMIZE kills
vs the current crew champion, then evolve the crew move-policy to MINIMIZE kills vs
the current impostor champion. The diagnostic is the ABSOLUTE benchmark each round:
impostor-champ vs the FIXED FSM crew, and FIXED FSM impostor vs crew-champ. If
those move monotonically, progress is real; if they oscillate while the co-evolved
matchup stays competitive, it's cycling / Red-Queen (motion without progress).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, "experiments/lab")
from ml_spike import core  # noqa: E402

TMP = Path(os.environ["CLAUDE_JOB_DIR"]) / "tmp" / "fo2"
K = list(range(6))


def _factory(gi, gc):
    from agents.tactical.crewmate_policy import CrewmatePolicy
    from agents.tactical.impostor_policy import ImpostorPolicy
    from orchestrator.game import TacticalAgent

    def factory(agent_id, role):
        pol = ImpostorPolicy if role == "IMPOSTOR" else CrewmatePolicy
        inner = TacticalAgent(
            agent_id=agent_id, policy=pol(agent_id=agent_id), role=role
        )
        g = gi if role == "IMPOSTOR" else gc
        return core.SpikeAgent(inner, genome=g) if g is not None else inner

    return factory


def kills2(gi, gc, tag) -> int:
    from eval.balance_eval import run_tournament_eval

    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    out = TMP / tag
    out.mkdir(parents=True, exist_ok=True)
    run_tournament_eval(
        seeds=list(K),
        output_dir=out,
        agent_factory=_factory(gi, gc),
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
        force=True,
        max_ticks=45,  # cap: random-moving crew never finishes tasks -> games run to budget
    )
    return sum(core.count_kills(out / f"replay-seed-{s}.jsonl") for s in K)


def evolve(fixed_other, *, side, champ, lam=4, gen_tag):
    """One ES generation. side='I' maximizes kills, 'C' minimizes."""
    best_g = champ
    best_f = (
        kills2(champ, fixed_other, f"{gen_tag}_base")
        if side == "I"
        else kills2(fixed_other, champ, f"{gen_tag}_base")
    )
    for m in range(lam):
        cand = core.mutate(champ, seed=hash((gen_tag, m)) % 10**6, sigma=0.15)
        f = (
            kills2(cand, fixed_other, f"{gen_tag}_m{m}")
            if side == "I"
            else kills2(fixed_other, cand, f"{gen_tag}_m{m}")
        )
        better = f > best_f if side == "I" else f < best_f
        if better:
            best_g, best_f = cand, f
    return best_g


def main() -> int:
    print("=== FO-2 — co-evolution stability (alternating 2-pop ES) ===")
    fsm_fsm = kills2(None, None, "fsm_fsm")
    print(f"reference: FSM impostor vs FSM crew = {fsm_fsm} kills/{len(K)} seeds\n")

    champ_i = core.random_genome(1)
    champ_c = core.random_genome(2)
    print("round | coevo(I vs C) | BENCH impostor vs FSM-crew | BENCH FSM-imp vs crew")
    bench_i_hist, bench_c_hist = [], []
    for r in range(5):
        champ_i = evolve(champ_c, side="I", champ=champ_i, gen_tag=f"r{r}_I")
        champ_c = evolve(champ_i, side="C", champ=champ_c, gen_tag=f"r{r}_C")
        coevo = kills2(champ_i, champ_c, f"r{r}_coevo")
        bench_i = kills2(champ_i, None, f"r{r}_bi")  # impostor-champ vs FIXED FSM crew
        bench_c = kills2(None, champ_c, f"r{r}_bc")  # FIXED FSM impostor vs crew-champ
        bench_i_hist.append(bench_i)
        bench_c_hist.append(bench_c)
        print(
            f"  {r}   |    {coevo:3d}        |        {bench_i:3d}                |     {bench_c:3d}"
        )

    def trend(h):
        return (
            "RISING"
            if h[-1] > h[0] + 2
            else "FALLING"
            if h[-1] < h[0] - 2
            else "FLAT/OSCILLATING"
        )

    print(
        f"\nimpostor absolute progress (vs FSM crew): {bench_i_hist} -> {trend(bench_i_hist)}"
    )
    print(
        f"crew absolute progress (FSM imp kills, want DOWN): {bench_c_hist} -> {trend(bench_c_hist)}"
    )
    print(
        "read: monotone benchmarks = real progress; flat/oscillating benchmarks while"
    )
    print(
        "coevo stays mid = Red-Queen cycling (the Phase-C stability risk, now observed)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
