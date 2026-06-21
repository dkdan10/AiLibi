"""Visibility RE-SIM — agents RE-DECIDE under room-local sight (fake provider, $0).

The detection counterfactual (visibility_probe.py) held games fixed. Here we
actually RE-SIMULATE under each visibility model so agents act on the reduced
sight — showing the BEHAVIORAL + balance shift (more/bolder kills? does the crew
stall harder? does the clock still decide?). Forced by monkeypatching
`engine.visibility.resolve_visibility_mode` (compute_visibility_for_player reads
it as a module global, so the patch lands).

A/B is fake-provider-vs-fake-provider: compare the two ARMS, NOT to the real
committed baseline (the fake meeting/vote stub differs from Ollama). Read the
DELTAS, not the absolute levels.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine.visibility as vis  # noqa: E402
from ml_spike import core  # noqa: E402

TMP = core.tmp("visresim")
SEEDS = list(range(50))
_ORIG = vis.resolve_visibility_mode


def run_arm(label: str, room_only: bool) -> dict:
    from eval.balance_eval import run_tournament_eval

    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    out = TMP / label
    out.mkdir(parents=True, exist_ok=True)
    if room_only:

        def _room_local(
            ws, gm
        ):  # override only the BASE; keep sabotage modes (Codex #8)
            if ws.sabotage is None or not ws.sabotage.active:
                return "same_room_only"
            return _ORIG(ws, gm)

        vis.resolve_visibility_mode = _room_local
    else:
        vis.resolve_visibility_mode = _ORIG
    try:
        run_tournament_eval(
            seeds=SEEDS,
            output_dir=out,
            num_players=9,
            num_impostors=2,
            force=True,
        )
    finally:
        vis.resolve_visibility_mode = _ORIG

    reasons: Counter[str] = Counter()
    kills = mtgs = ejects = contras = 0
    for s in SEEDS:
        path = out / f"replay-seed-{s}.jsonl"
        kills += core.count_kills(
            path
        )  # RESOLVED kills, not submitted attempts (Codex #3)
        for r in core.replay_rows(path):
            if r.get("kind") == "meeting":
                mtgs += 1
                if r.get("ejected_player_id"):
                    ejects += 1
                contras += len(r.get("contradictions", []))
            if "reason" in r:
                reasons[r["reason"]] += 1
    # the engine's impostor-kill win reason is IMPOSTOR_PARITY (there is no
    # IMPOSTOR_KILLS reason) — Codex #7
    imp = reasons.get("IMPOSTOR_PARITY", 0) + reasons.get("IMPOSTOR_SABOTAGE", 0)
    crew = reasons.get("CREWMATE_TASKS", 0) + reasons.get("CREWMATE_EJECT", 0)
    return {
        "reasons": dict(reasons),
        "kills": kills,
        "mtgs": mtgs,
        "ejects": ejects,
        "contras": contras,
        "imp_wins": imp,
        "crew_wins": crew,
        "nondecisive": len(SEEDS) - imp - crew,
    }


def main() -> int:
    print("=== VISIBILITY RE-SIM (fake provider, 50 seeds, agents re-decide) ===")
    print("    compare ARMS only; not comparable to the real committed baseline\n")
    base = run_arm("baseline", room_only=False)
    room = run_arm("room_only", room_only=True)

    def line(k, label):
        b, r = base[k], room[k]
        return f"  {label:28s} {b:>6}  ->  {r:>6}   (Δ {r - b:+d})"

    print(line("imp_wins", "impostor wins (parity+sabotage)"))
    print(line("crew_wins", "crew wins"))
    print(line("nondecisive", "non-decisive (budget/None)"))
    print(line("kills", "resolved kills"))
    print(line("mtgs", "meetings held"))
    print(line("ejects", "ejections"))
    print(line("contras", "contradictions (detector)"))
    print(f"\n  baseline win-reasons:  {base['reasons']}")
    print(f"  room_only win-reasons: {room['reasons']}")
    if base == room:
        print("\n  !! WARNING: arms identical — monkeypatch did NOT take effect")
    else:
        print("\n  (arms differ -> patch active)")
    print(
        "\n  Read: room_only should drop contradictions/ejections (detector starves) and"
        "\n  may lift kills / shift wins toward the clock or the impostor — the balance signal."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
