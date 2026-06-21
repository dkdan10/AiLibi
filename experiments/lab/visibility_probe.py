"""Visibility probe — does ROOM-LOCAL visibility starve the detector?

Detection counterfactual: hold each committed 9p2i game's action stream FIXED and
vary ONLY the visibility model — `same_room_and_adjacent` (today's base) vs
`same_room_only` (the proposed change) — then measure how much firsthand kill
witnessing survives. Same kills, same movements; only "who saw what" changes. This
isolates the visibility effect the way vent_escape_lab isolated the post-kill trail.
$0, reads committed replays, NO engine edit, NO re-record.

State is reconstructed ENGINE-FAITHFULLY via `core.reconstruct` (Codex #1/#2/#4/#6):
kills are resolved in engine actor-id order (submitted-but-rejected kills dropped),
vented players are moved to the vent room and HIDDEN from sightings, and meeting
ejections are applied so ejected players leave the alive set. Impostor roles come from
the committed `tournament-eval-report.json` (Codex #5), not inferred from actions.

Caveat: a counterfactual on a FIXED game (agents don't re-decide under reduced sight).
Witnesses are evaluated on `core.reconstruct`'s end-of-tick `visible` map — the same
basis the FO-6 surrogate uses — so within-tick kill-moment ordering is not separately
modeled.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_spike import core  # noqa: E402  (lab path bootstrap)

MAP = core._MAP
SAMPLES = Path("replays/samples/9p2i")


def neighbors(room: str) -> set[str]:
    return set(MAP.room_neighbors(room)) if room in core._ROOM_IX else set()


def seeds() -> list[int]:
    return sorted(
        int(p.stem.split("-")[-1]) for p in SAMPLES.glob("replay-seed-*.jsonl")
    )


def impostors_by_seed() -> dict:
    """Role ground truth from the committed eval report (not action-inferred)."""
    rep = json.loads((SAMPLES / "tournament-eval-report.json").read_text())
    return {
        g["seed"]: {p for p, role in g["roles"].items() if role == "IMPOSTOR"}
        for g in rep["report"]["games"]
    }


def crew_seeing(room_id, visible, impostors, exclude, mode):
    """Alive crew (from core's vent-hidden `visible`) who can SEE room_id under mode."""
    rooms = {room_id} if mode == "room_only" else {room_id} | neighbors(room_id)
    out = []
    for rm in rooms:
        for p in visible.get(rm, ()):
            if p in exclude or p in impostors:
                continue
            out.append(p)
    return out


def main() -> int:
    print("=== VISIBILITY PROBE — detection counterfactual on committed 9p2i ===")
    print("    adjacent = same_room_and_adjacent (today)  |  room_only = proposed")
    print("    engine-faithful state via core.reconstruct; roles from eval report\n")
    imp_by = impostors_by_seed()
    agg = {"kills": 0, "wit_adj": 0, "wit_room": 0, "sight_adj": 0, "sight_room": 0}
    per_seed = []
    for s in seeds():
        states = core.reconstruct(core.replay_rows(SAMPLES / f"replay-seed-{s}.jsonl"))
        imp = imp_by.get(s, set())
        k = wa = wr = sa = sr = 0
        for st in states:
            if "kills" not in st:  # meeting state
                continue
            visible, alive = st["visible"], st["alive"]
            # detector "fuel": crew->impostor tick-sightings (vent-hidden via `visible`)
            for ip in imp & alive:
                iproom = next((rm for rm, ps in visible.items() if ip in ps), None)
                if iproom is None:  # vented -> hidden
                    continue
                sa += len(crew_seeing(iproom, visible, imp, {ip}, "adjacent"))
                sr += len(crew_seeing(iproom, visible, imp, {ip}, "room_only"))
            for killer, victim, kroom in st["kills"]:
                k += 1
                wa += (
                    1
                    if crew_seeing(kroom, visible, imp, {killer, victim}, "adjacent")
                    else 0
                )
                wr += (
                    1
                    if crew_seeing(kroom, visible, imp, {killer, victim}, "room_only")
                    else 0
                )
        agg["kills"] += k
        agg["wit_adj"] += wa
        agg["wit_room"] += wr
        agg["sight_adj"] += sa
        agg["sight_room"] += sr
        per_seed.append((s, k, wa, wr))

    k = agg["kills"]
    print(f"RESOLVED KILLS total: {k}  (across {len(per_seed)} seeds)")
    print(
        f"  kills WITNESSED (>=1 crew sees killer at kill tick):"
        f"  adjacent {agg['wit_adj']}/{k} ({agg['wit_adj'] / k:.0%})"
        f"  ->  room_only {agg['wit_room']}/{k} ({agg['wit_room'] / k:.0%})"
    )
    drop = (agg["wit_adj"] - agg["wit_room"]) / agg["wit_adj"] if agg["wit_adj"] else 0
    print(f"  => room_only removes {drop:.0%} of in-the-act kill witnessing")
    print(
        f"  crew->impostor tick-sightings (detector fuel):"
        f"  adjacent {agg['sight_adj']}  ->  room_only {agg['sight_room']}"
        f"  ({1 - agg['sight_room'] / agg['sight_adj']:.0%} less)"
    )
    print("\n  per-seed kills witnessed (adj -> room):")
    for s, kk, wa, wr in per_seed:
        print(f"    seed {s:2d}: {kk} kills | {wa} -> {wr} witnessed")

    # --- seed-5 trace: p-1's sight of the p-3 -> p-7 kill (storage) ---
    print("\n=== SEED-5 TRACE: what p-1 sees of p-3's kill of p-7 ===")
    states = core.reconstruct(core.replay_rows(SAMPLES / "replay-seed-5.jsonl"))
    print(f"  impostors (eval report) = {sorted(imp_by.get(5, set()))}")
    for st in states:
        if "kills" not in st or st["tick"] > 8:
            if "kills" not in st:
                continue
            break
        visible = st["visible"]
        p1room = next((rm for rm, ps in visible.items() if "p-1" in ps), None)
        if p1room is None:
            continue
        vis_adj = {p1room} | neighbors(p1room)
        sees_adj = sorted(
            p for rm in vis_adj for p in visible.get(rm, ()) if p != "p-1"
        )
        sees_room = sorted(p for p in visible.get(p1room, ()) if p != "p-1")
        note = "".join(f"  <KILL {a}->{b} in {c}>" for a, b, c in st["kills"])
        flag = " p3-visible!" if "p-3" in sees_adj and "p-3" not in sees_room else ""
        print(
            f"  t{st['tick']}: p-1 in {p1room:11s} | adj-sees {sees_adj} | "
            f"room-sees {sees_room}{flag}{note}"
        )
    print(
        "\n  Read: where adj-sees has p-3 but room-sees does NOT, today's model lets p-1"
        "\n  witness p-3 across the room boundary; room_only would reduce it to inference."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
