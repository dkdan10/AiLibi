"""Stopwatch / task-clock retune sweep ($0, fake provider) — what breaks the stopwatch?

The fake provider runs the full physical FSM (movement, tasks, kills, body-reports -> meetings)
deterministically; only the meeting RESOLUTION is dead (no deduction -> ~no ejections). So this
measures PACING + the no-deduction balance floor under different task configs. Goal: find configs
that LENGTHEN games + raise meetings/game (deduction room) + break CREWMATE_TASKS stopwatch
dominance, WITHOUT the impostor trivially stomping. The REAL balance (with the crew's ~0.88
deduction) must be confirmed on a real-Ollama run; this narrows the levers first.

Levers (per arm): tasks_per_crewmate (run_tournament_eval param), per-task duration scale (custom
map via model_copy), and the dead-crewmate task RULE (monkeypatch ``engine.tick._apply_kill``):
  - ``drop``         engine default: a kill DELETES the victim's incomplete instances (burden shrinks).
  - ``keep``         the victim's incomplete instances stay (uncompletable) -> no task-win after a
                     death; in fake the crew idle and games stall to the tick budget.
  - ``redistribute`` the victim's incomplete instances RE-KEY to a living crewmate (carry progress);
                     the burden does not shrink AND the crew stay active -> no stall.

Findings (50 seeds/arm, fake): more tasks/player is the WRONG lever (heads-down -> fewer kills ->
fewer meetings -> more stopwatch); per-task DURATION is a clean monotonic lever; REDISTRIBUTE is the
strongest -- it removes the stopwatch (CREW_TASKS 39->3) and DOUBLES meetings (2.3->3.7) while
terminating. See report-stopwatch-sweep.md. $0, no LLM, no engine edit committed (sim-only patch).

Run: ``SWEEP_N=50 PYTHONPATH=. uv run python experiments/lab/stopwatch_sweep.py``
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from dataclasses import replace as dc_replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
TMP = Path(
    os.environ.get("SWEEP_OUT")
    or (Path(os.environ.get("TMPDIR") or "/tmp") / "stopwatch_sweep")
)
SEEDS = list(range(int(os.environ.get("SWEEP_N", "50"))))

import engine.tick as tick_mod  # noqa: E402
from engine.world import load_canonical_map  # noqa: E402

_ORIG_APPLY_KILL = tick_mod._apply_kill
BASE_MAP = load_canonical_map()


def _keep_apply_kill(state, game_map, action):
    """Don't-drop variant: re-add the victim's incomplete instances the engine dropped (uncompletable)."""
    new_state, event = _ORIG_APPLY_KILL(state, game_map, action)
    victim = action.payload.target
    restored = dict(new_state.tasks)
    for tid, t in state.tasks.items():
        if t.owner == victim and not t.completed:
            restored[tid] = t
    return dc_replace(new_state, tasks=restored), event


def _redistribute_apply_kill(state, game_map, action):
    """Redistribute variant: re-key the victim's incomplete instances to LIVING crewmates (carry
    progress) so the burden does not shrink yet the crew stay active. Deterministic by sorted id.
    Reads roles in the engine (the engine already knows them) -- a real impl must keep that
    firewall-clean and deterministic."""
    new_state, event = _ORIG_APPLY_KILL(state, game_map, action)
    victim = action.payload.target
    living_crew = sorted(
        pid for pid, p in new_state.players.items() if p.alive and p.role == "CREWMATE"
    )
    if not living_crew:
        return new_state, event
    tasks = dict(new_state.tasks)
    for t in state.tasks.values():
        if t.owner == victim and not t.completed:
            recipient = next(
                (c for c in living_crew if f"{c}:{t.map_task_id}" not in tasks), None
            )
            if recipient is None:
                continue  # every living crewmate already owns this map task; drop it
            new_id = f"{recipient}:{t.map_task_id}"
            tasks[new_id] = dc_replace(t, id=new_id, owner=recipient)
    return dc_replace(new_state, tasks=tasks), event


def scaled_map(scale: float):
    if scale == 1.0:
        return BASE_MAP
    new_tasks = {
        tid: td.model_copy(
            update={"duration_ticks": max(1, round(td.duration_ticks * scale))}
        )
        for tid, td in BASE_MAP.tasks.items()
    }
    return BASE_MAP.model_copy(update={"tasks": new_tasks})


def run_arm(name: str, tpc: int, scale: float, mode: str) -> dict:
    from eval.balance_eval import run_tournament_eval

    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    out = TMP / name
    out.mkdir(parents=True, exist_ok=True)
    tick_mod._apply_kill = {
        "keep": _keep_apply_kill,
        "redistribute": _redistribute_apply_kill,
    }.get(mode, _ORIG_APPLY_KILL)
    try:
        run_tournament_eval(
            seeds=SEEDS,
            output_dir=out,
            num_players=9,
            num_impostors=2,
            tasks_per_crewmate=tpc,
            game_map=scaled_map(scale),
            force=True,
        )
    finally:
        tick_mod._apply_kill = _ORIG_APPLY_KILL

    reasons: Counter = Counter()
    lens = []
    mtgs = []
    kills = []
    for s in SEEDS:
        p = out / f"replay-seed-{s}.jsonl"
        if not p.exists():
            continue
        rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
        mtgs.append(sum(1 for r in rows if r.get("kind") == "meeting"))
        go = [r for r in rows if r.get("kind") == "game_over"]
        if go:
            reasons[go[0].get("reason")] += 1
            t = go[0].get("tick")
            lens.append(t if t is not None else 0)
        else:
            reasons["TIMEOUT"] += 1
            tk = [r["tick"] for r in rows if r.get("kind") == "tick"]
            lens.append(max(tk) if tk else 0)
        kills.append(
            sum(
                1
                for r in rows
                if r.get("kind") == "tick"
                for a in (r.get("actions") or [])
                if a.get("type") == "kill"
            )
        )
    return {
        "name": name,
        "tpc": tpc,
        "scale": scale,
        "mode": mode,
        "len": sum(lens) / max(len(lens), 1),
        "mtg": sum(mtgs) / max(len(mtgs), 1),
        "kill": sum(kills) / max(len(kills), 1),
        "reasons": dict(reasons),
        "ct": reasons.get("CREWMATE_TASKS", 0),
        "ip": reasons.get("IMPOSTOR_PARITY", 0),
        "ce": reasons.get("CREWMATE_EJECT", 0),
        "to": reasons.get("TIMEOUT", 0),
    }


ARMS = [
    ("baseline", 2, 1.0, "drop"),
    ("tpc3", 3, 1.0, "drop"),
    ("tpc4", 4, 1.0, "drop"),
    ("dur1.2", 2, 1.2, "drop"),
    ("dur1.5", 2, 1.5, "drop"),
    ("dur2.0", 2, 2.0, "drop"),
    ("keep_no_drop", 2, 1.0, "keep"),
    ("redistribute", 2, 1.0, "redistribute"),
    ("redist_dur1.5", 2, 1.5, "redistribute"),
]


def main() -> int:
    print(f"=== STOPWATCH SWEEP ({len(SEEDS)} fake seeds/arm, 9p2i) ===", flush=True)
    rows = []
    for name, tpc, scale, mode in ARMS:
        r = run_arm(name, tpc, scale, mode)
        rows.append(r)
        print(
            f"  {name:14} len {r['len']:6.1f} | mtg/game {r['mtg']:4.1f} | kills {r['kill']:4.1f} | "
            f"CT {r['ct']:2} IP {r['ip']:2} CE {r['ce']:2} TO {r['to']:2}",
            flush=True,
        )
    out = []
    out.append(
        "\n=== TABLE (want mtg/game UP + CREW_TASKS down + terminates, no IMP_PARITY runaway) ==="
    )
    out.append(
        f"  {'arm':14}{'tpc':>4}{'dur':>5}{'mode':>14}{'len':>8}{'mtg/g':>7}{'kills':>7}{'CRW_TASK':>10}{'IMP_PAR':>9}{'TIMEOUT':>9}"
    )
    for r in rows:
        out.append(
            f"  {r['name']:14}{r['tpc']:>4}{r['scale']:>5}{r['mode']:>14}"
            f"{r['len']:>8.1f}{r['mtg']:>7.1f}{r['kill']:>7.1f}{r['ct']:>10}{r['ip']:>9}{r['to']:>9}"
        )
    out.append(
        "\nfake = no deduction -> CREW_TASKS=out-task, IMP_PARITY=impostor kills; real crew deduce ~0.88."
    )
    txt = "\n".join(out)
    print(txt, flush=True)
    (TMP / "sweep-result.txt").write_text(txt)
    (TMP / "sweep-result.json").write_text(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
