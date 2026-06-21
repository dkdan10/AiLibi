"""Visibility probe — does ROOM-LOCAL visibility starve the detector?

Detection counterfactual: hold each committed 9p2i game's action stream FIXED and
vary ONLY the visibility model — `same_room_and_adjacent` (today's base) vs
`same_room_only` (the proposed change) — then measure how much firsthand
KILL/BODY witnessing survives. Same kills, same movements; only "who saw what"
changes. This isolates the visibility effect the way vent_escape_lab isolated the
post-kill trail. $0, reads committed replays, NO engine edit, NO re-record.

Caveat (honest): this is a counterfactual on the DETECTOR'S INPUT on a fixed game
— agents do not re-decide under reduced sight (they would kill more / cluster
differently). It answers "does room-local starve firsthand evidence?", not the
full balance/rubric question (that needs a re-sim or re-record).
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


def load(seed: int) -> list[dict]:
    txt = (SAMPLES / f"replay-seed-{seed}.jsonl").read_text().splitlines()
    return [json.loads(ln) for ln in txt if ln.strip()]


def reconstruct(rows: list[dict]):
    """Per-tick room snapshots + kill list + impostor set (killers/venters)."""
    players: set[str] = set()
    for r in rows:
        if r.get("kind") == "tick":
            for a in r["actions"]:
                players.add(a["actor"])
    room = dict.fromkeys(players, "CAFETERIA")
    in_vent = dict.fromkeys(players, False)
    alive = set(players)
    impostors: set[str] = set()
    snaps = []  # (tick, room, in_vent, alive, kills[(killer,victim,room)])
    for r in rows:
        if r.get("kind") != "tick":
            continue
        kills = []
        for a in sorted(r["actions"], key=lambda x: x["actor"]):
            act = a["actor"]
            if act not in alive:
                continue
            ty = a["type"]
            if ty == "move":
                room[act] = a["payload"]["to_room"]
                in_vent[act] = False
            elif ty == "vent":
                impostors.add(act)
                in_vent[act] = not in_vent[act]
            elif ty == "kill":
                impostors.add(act)
                v = a["payload"]["target"]
                kills.append((act, v, room[act]))
                alive.discard(v)
        snaps.append((r["tick"], dict(room), dict(in_vent), set(alive), kills))
    return snaps, impostors


def crew_seeing(room_id, snap_room, snap_invent, snap_alive, impostors, exclude, mode):
    """Alive crew (non-impostor) who can SEE room_id under `mode`."""
    vis = {room_id} if mode == "room_only" else {room_id} | neighbors(room_id)
    out = []
    for p in snap_alive:
        if p in exclude or p in impostors or snap_invent.get(p):
            continue
        if snap_room[p] in vis:
            out.append(p)
    return out


def main() -> int:
    print("=== VISIBILITY PROBE — detection counterfactual on committed 9p2i ===")
    print("    adjacent = same_room_and_adjacent (today)  |  room_only = proposed\n")
    agg = {
        "kills": 0,
        "wit_adj": 0,
        "wit_room": 0,
        "sight_adj": 0,
        "sight_room": 0,
    }
    per_seed = []
    for s in seeds():
        snaps, imp = reconstruct(load(s))
        k = wa = wr = sa = sr = 0
        for tick, rm, iv, al, kills in snaps:
            # detector "fuel": crew->impostor tick-sightings (any crew sees any impostor)
            for ip in imp & al:
                if iv.get(ip):
                    continue
                sa += len(crew_seeing(rm[ip], rm, iv, al, imp, {ip}, "adjacent"))
                sr += len(crew_seeing(rm[ip], rm, iv, al, imp, {ip}, "room_only"))
            for killer, victim, kroom in kills:
                k += 1
                wa += (
                    1
                    if crew_seeing(kroom, rm, iv, al, imp, {killer, victim}, "adjacent")
                    else 0
                )
                wr += (
                    1
                    if crew_seeing(
                        kroom, rm, iv, al, imp, {killer, victim}, "room_only"
                    )
                    else 0
                )
        agg["kills"] += k
        agg["wit_adj"] += wa
        agg["wit_room"] += wr
        agg["sight_adj"] += sa
        agg["sight_room"] += sr
        per_seed.append((s, k, wa, wr))

    k = agg["kills"]
    print(f"KILLS total: {k}  (across {len(per_seed)} seeds)")
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
    snaps, imp = reconstruct(load(5))
    print(f"  impostors (reconstructed) = {sorted(imp)}")
    for tick, rm, iv, al, kills in snaps:
        if tick > 8:
            break
        p1 = rm.get("p-1")
        vis_adj = {p1} | neighbors(p1)
        sees_adj = [p for p in al if p != "p-1" and not iv.get(p) and rm[p] in vis_adj]
        sees_room = [p for p in al if p != "p-1" and not iv.get(p) and rm[p] == p1]
        note = ""
        for killer, victim, kroom in kills:
            note += f"  <KILL {killer}->{victim} in {kroom}>"
        flag = " p3-visible!" if "p-3" in sees_adj and "p-3" not in sees_room else ""
        print(
            f"  t{tick}: p-1 in {p1:11s} | adj-sees {sorted(sees_adj)} | "
            f"room-sees {sorted(sees_room)}{flag}{note}"
        )
    print(
        "\n  Read: where adj-sees has p-3 but room-sees does NOT, today's model lets p-1"
        "\n  witness p-3 across the room boundary; room_only would reduce it to inference."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
