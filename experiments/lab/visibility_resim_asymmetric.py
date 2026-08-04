"""FROZEN (Phase 19 tier map, training/README.md): concluded design-thread experiment.
Bug fixes and evidence readers only; no new search.

Asymmetric-visibility re-sim: crew = same_room_only, impostor = same_room_and_adjacent.

Tests the proposal that keeping the IMPOSTOR's adjacent sight (while crew go room-only)
avoids the impostor-weakening the SYMMETRIC room-local flip caused (visibility_resim.py:
impostor wins 11->5, kills 165->141) — and measures how far the balance swings.

Role-parameterized visibility: at base visibility, crew are downgraded to same_room_only
while the impostor keeps the base same_room_and_adjacent; an ACTIVE sabotage degrade
(mode != base, e.g. lights) still degrades everyone. compute_visibility_for_player calls
visible_rooms_for_player as a module global, so the monkeypatch lands.

Fake-provider A/B (deduction-blind -> measures BEHAVIOR/balance, not detector quality).
Compare the three ARMS; not comparable to the real committed baseline. $0, no re-record.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine.visibility as vis  # noqa: E402
from ml_spike import core  # noqa: E402

TMP = core.tmp("visasym")
SEEDS = list(range(50))
_ORIG_MODE = vis.resolve_visibility_mode
_ORIG_ROOMS = vis.visible_rooms_for_player


def _reset() -> None:
    vis.resolve_visibility_mode = _ORIG_MODE
    vis.visible_rooms_for_player = _ORIG_ROOMS


def run_arm(label: str, arm: str) -> dict:
    from eval.balance_eval import run_tournament_eval

    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    out = TMP / label
    out.mkdir(parents=True, exist_ok=True)
    _reset()
    if arm == "room_only_sym":

        def _ro(ws, gm):  # everyone room-only at base; keep sabotage modes
            if ws.sabotage is None or not ws.sabotage.active:
                return "same_room_only"
            return _ORIG_MODE(ws, gm)

        vis.resolve_visibility_mode = _ro
    elif arm == "asymmetric":

        def _vrfp(
            *, observer, game_map, mode
        ):  # crew room-only at base; impostor keeps base
            if (
                mode == game_map.visibility_defaults.base
                and observer.role != "IMPOSTOR"
            ):
                mode = "same_room_only"
            return _ORIG_ROOMS(observer=observer, game_map=game_map, mode=mode)

        vis.visible_rooms_for_player = _vrfp
    try:
        run_tournament_eval(
            seeds=SEEDS, output_dir=out, num_players=9, num_impostors=2, force=True
        )
    finally:
        _reset()

    reasons: Counter[str] = Counter()
    kills = mtgs = 0
    for s in SEEDS:
        path = out / f"replay-seed-{s}.jsonl"
        kills += core.count_kills(path)
        for r in core.replay_rows(path):
            if r.get("kind") == "meeting":
                mtgs += 1
            if "reason" in r:
                reasons[r["reason"]] += 1
    imp = reasons.get("IMPOSTOR_PARITY", 0) + reasons.get("IMPOSTOR_SABOTAGE", 0)
    crew = reasons.get("CREWMATE_TASKS", 0) + reasons.get("CREWMATE_EJECT", 0)
    return {
        "reasons": dict(reasons),
        "kills": kills,
        "mtgs": mtgs,
        "imp": imp,
        "crew": crew,
        "nd": len(SEEDS) - imp - crew,
    }


def main() -> int:
    print("=== ASYMMETRIC visibility re-sim (fake provider, 50 seeds) ===")
    print(
        "    crew = same_room_only, impostor = same_room_and_adjacent; compare ARMS\n"
    )
    base = run_arm("baseline", "baseline")
    sym = run_arm("room_only_sym", "room_only_sym")
    asym = run_arm("asymmetric", "asymmetric")

    def row(label: str, d: dict) -> str:
        return (
            f"  {label:<18} imp_wins {d['imp']:>3} | crew {d['crew']:>3} | "
            f"nondec {d['nd']:>2} | kills {d['kills']:>4} | mtgs {d['mtgs']:>3}"
        )

    print(row("baseline (today)", base))
    print(row("room_only (sym)", sym))
    print(row("asymmetric", asym))
    print(f"\n  baseline reasons:   {base['reasons']}")
    print(f"  room_only reasons:  {sym['reasons']}")
    print(f"  asymmetric reasons: {asym['reasons']}")
    print(
        f"\n  impostor wins: baseline {base['imp']} | sym room-only {sym['imp']} (CRATERED) | "
        f"asymmetric {asym['imp']}"
    )
    print(
        f"  kills:         baseline {base['kills']} | sym room-only {sym['kills']} | "
        f"asymmetric {asym['kills']}"
    )
    print(
        "\n  Read: if asymmetric imp_wins/kills hold NEAR or ABOVE baseline (not cratered like"
        "\n  sym), the impostor is NOT re-blinded; imp_wins ABOVE baseline = the balance-swing"
        "\n  magnitude toward the impostor (watch vs the Phase-11 ~14% floor)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
