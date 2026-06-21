"""Phase-B FEASIBILITY probe: does ROOM-LOCAL + DEPARTURE-BREADCRUMB restore the
detector signal that pure room-only loses?

For each resolved kill (killer K in room R), build the "who could have done it"
suspect set the crew could COLLECTIVELY form under three info models, and measure
RECALL (does the set contain the real killer) and DISCRIMINATION (how many innocent
crew are swept in):

  adjacency   = today: a crew member in R or any room ADJACENT to R sees into R.
  room_only   = a crew member must be IN R (kills are usually private -> dark).
  room+bc     = room_only PLUS the departure breadcrumb: a player X is a suspect if
                X is in R now AND a crew member was co-located in X's PREVIOUS room
                when X took its last hop into R ("I saw X head to Storage").

If room+bc recovers most of adjacency's recall that room_only loses, while keeping
the suspect set small, the breadcrumb is a viable substrate for B's inferential
detector. Engine-faithful reconstruction (resolved kills, vent-hidden); roles from
the committed eval report. $0, committed replays, NO engine edit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_spike import core  # noqa: E402

MAP = core._MAP
SAMPLES = Path("replays/samples/9p2i")


def neighbors(room: str) -> set[str]:
    return set(MAP.room_neighbors(room)) if room in core._ROOM_IX else set()


def seeds() -> list[int]:
    return sorted(
        int(p.stem.split("-")[-1]) for p in SAMPLES.glob("replay-seed-*.jsonl")
    )


def impostors_by_seed() -> dict:
    rep = json.loads((SAMPLES / "tournament-eval-report.json").read_text())
    return {
        g["seed"]: {p for p, role in g["roles"].items() if role == "IMPOSTOR"}
        for g in rep["report"]["games"]
    }


def reconstruct(rows: list[dict]):
    """Per-tick room snapshots (None = vented/dead) + resolved kills, engine order."""
    players: set[str] = set()
    for r in rows:
        if r.get("kind") == "tick":
            for a in r["actions"]:
                players.add(a["actor"])
    room = dict.fromkeys(players, "CAFETERIA")
    in_vent = dict.fromkeys(players, False)
    alive = set(players)
    hist = []  # (tick, {p: room|None}, alive set, kills[(K,Vic,R)])
    for r in rows:
        if r.get("kind") == "tick":
            kills = []
            for a in sorted(r["actions"], key=lambda x: x["actor"]):
                w, ty = a["actor"], a["type"]
                if w not in alive:
                    continue
                if ty == "move":
                    room[w], in_vent[w] = a["payload"]["to_room"], False
                elif ty == "vent":
                    room[w] = core.VENT_ROOM.get(a["payload"]["vent_id"], room[w])
                    in_vent[w] = not in_vent[w]
                elif ty == "kill":
                    tgt = a["payload"]["target"]
                    if (
                        tgt in alive
                        and not in_vent[w]
                        and not in_vent.get(tgt, False)
                        and room.get(tgt) == room[w]
                    ):
                        alive.discard(tgt)
                        kills.append((w, tgt, room[w]))
            snap = {
                p: (None if in_vent[p] or p not in alive else room[p]) for p in players
            }
            hist.append((r["tick"], snap, set(alive), kills))
        elif r.get("kind") == "meeting":
            ej = r.get("ejected_player_id")
            alive.discard(ej)
            for p in alive:
                room[p], in_vent[p] = "CAFETERIA", False
    return hist


def suspect_sets(hist, i, R, victim, crew_alive):
    """adjacency / room_only / room+breadcrumb suspect sets for a kill in R at hist[i]."""
    snap = hist[i][1]
    in_R = {p for p, rm in snap.items() if rm == R and p != victim}
    adj = (
        in_R if any(snap.get(c) in ({R} | neighbors(R)) for c in crew_alive) else set()
    )
    room_only = in_R if any(snap.get(c) == R for c in crew_alive) else set()
    bc = set()
    for x in in_R:
        j = i  # walk back to the start of x's current continuous stay in R
        while j > 0 and hist[j - 1][1].get(x) == R:
            j -= 1
        frm = hist[j - 1][1].get(x) if j > 0 else None  # room x hopped in FROM
        if frm is not None and any(
            hist[j - 1][1].get(c) == frm for c in crew_alive if c != x
        ):
            bc.add(x)  # a crew member saw x depart frm -> R
    return adj, room_only, bc


def main() -> int:
    print("=== PHASE-B FEASIBILITY — does room+breadcrumb restore detector signal? ===")
    print("    suspect set = 'who could have done it'; RECALL = contains the killer\n")
    imp_by = impostors_by_seed()
    agg = {a: {"recall": 0, "size": 0, "innoc": 0} for a in ("adj", "room", "bc")}
    nkills = 0
    s5 = []
    for s in seeds():
        rows = [
            json.loads(line)
            for line in (SAMPLES / f"replay-seed-{s}.jsonl").read_text().splitlines()
            if line.strip()
        ]
        hist = reconstruct(rows)
        imp = imp_by.get(s, set())
        for i, (_tick, _snap, alive, kills) in enumerate(hist):
            crew_alive = [p for p in alive if p not in imp]
            for K, Vic, R in kills:
                nkills += 1
                sets = dict(
                    zip(
                        ("adj", "room", "bc"), suspect_sets(hist, i, R, Vic, crew_alive)
                    )
                )
                for a, st in sets.items():
                    agg[a]["recall"] += 1 if K in st else 0
                    agg[a]["size"] += len(st)
                    agg[a]["innoc"] += len(st & set(crew_alive))
                if s == 5:
                    s5.append(
                        (
                            K,
                            Vic,
                            R,
                            {a: (K in st, sorted(st)) for a, st in sets.items()},
                        )
                    )

    print(f"resolved kills: {nkills}\n")
    print(
        f"  {'arm':<10}{'recall (has killer)':<24}{'mean set size':<16}{'mean innocent-in-set'}"
    )
    for a, lbl in (
        ("adj", "adjacency (today)"),
        ("room", "room_only"),
        ("bc", "room+breadcrumb"),
    ):
        r = agg[a]
        print(
            f"  {lbl:<22}{r['recall']}/{nkills} ({r['recall'] / nkills:.0%})"
            f"        {r['size'] / nkills:>5.2f}           {r['innoc'] / nkills:>5.2f}"
        )
    rec = lambda a: agg[a]["recall"] / nkills  # noqa: E731
    if rec("adj"):
        print(
            f"\n  breadcrumb recovers {rec('bc') / rec('adj'):.0%} of adjacency recall; "
            f"room_only alone recovers {rec('room') / rec('adj'):.0%}"
        )
    print("\n=== SEED-5 kills: can the crew finger the killer under each arm? ===")
    for K, Vic, R, res in s5:
        print(f"  {K} killed {Vic} in {R}:")
        for a in ("adj", "room", "bc"):
            has, st = res[a]
            print(
                f"     {a:<5} {'HAS killer' if has else 'misses   '} | suspect set {st}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
