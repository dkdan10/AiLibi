"""FROZEN (Phase 19 tier map, training/README.md): concluded design-thread experiment.
Bug fixes and evidence readers only; no new search.

Stopwatch sensitivity lab (Tier 1) — how close is the task-clock race, really?

Decision informed: Wave-2 balance knobs + the 10.13 gate (any clock-slow or
kill-cadence change must be modeled before it is tuned); R1 (deduction decides)
and R5 (varied win paths) sizing.

Method: for every CREWMATE_TASKS win, extrapolate the impostors' time-to-parity
at the game's OBSERVED kill cadence (per-game mean kill interval; set-wide mean
when a game has <2 kills) from the game-over tick, and compute
``flip_margin = extrapolated_parity_tick - game_over_tick`` — how many more
ticks the crew clock could have run before parity plausibly arrived. Sweep a
task-clock slowdown Δ and count plausible flips (flip_margin <= Δ).

CAVEATS (per lab governance): pure extrapolation — assumes constant kill
cadence, no meetings, no ejections in the extension window. Wave 1's whole
point is that more runway ALSO means more ejection chances, so these numbers
are an upper bound on flip risk, not a prediction. No game-state propagation.

Usage: uv run python experiments/lab/stopwatch_lab.py FACTS_JSON [...]
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

DELTAS = (2, 4, 6, 8, 12, 16, 24)


def run_set(facts_path: Path) -> dict[str, Any]:
    facts = json.loads(facts_path.read_text())
    games = facts["games"]
    all_intervals: list[int] = []
    for g in games:
        ticks = sorted(k["tick"] for k in g["kills"])
        all_intervals.extend(b - a for a, b in zip(ticks, ticks[1:]))
    set_mean_interval = statistics.mean(all_intervals) if all_intervals else 6.0

    rows: list[dict[str, Any]] = []
    for g in games:
        if g["reason"] != "CREWMATE_TASKS":
            continue
        roles = g["roles"]
        dead = set(g["deaths"])
        ejected = {
            m["ejected_player_id"] for m in g["meetings"] if m.get("ejected_player_id")
        }
        gone = dead | ejected
        living_imp = [p for p, r in roles.items() if r == "IMPOSTOR" and p not in gone]
        living_crew = [p for p, r in roles.items() if r == "CREWMATE" and p not in gone]
        if not living_imp:
            continue  # impostors eliminated — not a stopwatch win
        kills_needed = max(0, len(living_crew) - len(living_imp))
        ticks = sorted(k["tick"] for k in g["kills"])
        intervals = [b - a for a, b in zip(ticks, ticks[1:])]
        cadence = statistics.mean(intervals) if intervals else set_mean_interval
        flip_margin = kills_needed * cadence
        rows.append(
            {
                "seed": g["seed"],
                "game_over_tick": g["game_over_tick"],
                "living_crew": len(living_crew),
                "living_imp": len(living_imp),
                "kills_needed_for_parity": kills_needed,
                "observed_cadence": round(cadence, 2),
                "flip_margin_ticks": round(flip_margin, 1),
            }
        )

    margins = sorted(r["flip_margin_ticks"] for r in rows)
    sweep = {str(d): sum(1 for m in margins if m <= d) for d in DELTAS}
    return {
        "set": facts.get("seedset") or facts_path.stem,
        "task_wins_analyzed": len(rows),
        "set_mean_kill_interval": round(set_mean_interval, 2),
        "flip_margin_quartiles": (
            [
                margins[0],
                margins[len(margins) // 4],
                margins[len(margins) // 2],
                margins[(3 * len(margins)) // 4],
                margins[-1],
            ]
            if margins
            else []
        ),
        "plausible_flips_at_clock_slow_delta": sweep,
        "rows": rows,
    }


def main() -> int:
    out = {"sets": [run_set(Path(a)) for a in sys.argv[1:]]}
    for s in out["sets"]:
        print(
            f"== {s['set']} — {s['task_wins_analyzed']} stopwatch wins, "
            f"set kill-interval {s['set_mean_kill_interval']} =="
        )
        print("flip-margin quartiles (ticks):", s["flip_margin_quartiles"])
        print(
            "plausible flips if task clock slowed by Δ:",
            s["plausible_flips_at_clock_slow_delta"],
        )
    Path("experiments/lab/results-stopwatch-lab.json").write_text(
        json.dumps(out, indent=2, sort_keys=True)
    )
    print("\nwrote experiments/lab/results-stopwatch-lab.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
