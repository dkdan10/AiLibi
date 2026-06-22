"""Two $0-offline probes that de-risk the forward-redesign minimal fix on the committed
9p2i set (50 games / 114 meetings), before any code lands. See
audits/audit-2026-06-22-1558-forward-redesign.md (steps 0 + 2) and the write-up in
experiments/lab/report-forward-redesign-probes.md.

PROBE 1 (A-1 desk test) — does the §4.6 prompt imperative change OUTCOMES, given the
deterministic tally floor is kept? Recompute tally(recorded ballots) [correctness check],
then two counterfactuals: BELIEF (each voter votes their OWN spoken accusation, else SKIP)
and LOOSE (votes for never-spoken-accused targets drop to SKIP). Count outcome flips. Few
flips => A-1 is a rationale-text fix; many => the imperative is a real outcome lever.

PROBE 2 (detector signal) — does an inferential cross-speaker alibi-conflict detector light
R7 off 0/114? Firewall-clean: an alibi (S in room R over ticks [f,t]) contradicted by ANOTHER
speaker's saw_player(subject=S, room R2 != R, tick in [f,t]). Plus a ground-truth ceiling
(alibi vs the actual reconstructed position) = the maximum catchable lying in the substrate.

Run: uv run python experiments/lab/forward_redesign_probes.py
Reads only committed replays + roles; emits no files; $0.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SAMP = REPO / "replays" / "samples" / "9p2i"
THR = 0.6  # skip_confidence_threshold (DESIGN.md §4.6 default)
SPAWN = "CAFETERIA"  # engine/maps/canonical_1.yaml spawn.room == meeting.room


def rows_for(seed):
    path = SAMP / f"replay-seed-{seed}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def tally(ballots):
    """ballots: list of (target, confidence). Replicates meetings.voting.tally_ballots:
    plurality, SKIP a first-class target, tie->SKIP, leader confidence floor."""
    counts = Counter(t for t, _ in ballots)
    if not counts:
        return ("SKIPPED", None)
    mx = max(counts.values())
    leaders = sorted(t for t, c in counts.items() if c == mx)
    if "SKIP" in leaders:
        return ("SKIPPED", None)
    if len(leaders) > 1:
        return ("SKIPPED", None)
    leader = leaders[0]
    leader_max_conf = max(c for t, c in ballots if t == leader)
    if leader_max_conf < THR:
        return ("SKIPPED", None)
    return ("EJECTED", leader)


def parse_meeting(m):
    """-> (accusations_by_speaker, accused_targets, alibis, sightings, ballots)."""
    turns = (m.get("transcript") or {}).get("turns") or []
    accus_by_speaker = defaultdict(list)
    accused_targets = set()
    alibis, sightings = [], []
    for tn in turns:
        spk = tn.get("speaker")
        for c in tn.get("claims") or []:
            ct = c.get("type")
            if ct == "accusation" and c.get("against"):
                accus_by_speaker[spk].append(
                    (c["against"], float(c.get("confidence") or 0.0))
                )
                accused_targets.add(c["against"])
            elif ct == "alibi":
                alibis.append(
                    (
                        c.get("subject") or spk,
                        c.get("room"),
                        c.get("from_tick"),
                        c.get("to_tick"),
                    )
                )
        for o in tn.get("observations") or []:
            if o.get("type") == "saw_player":
                sightings.append((spk, o.get("subject"), o.get("room"), o.get("tick")))
    ballots = [
        (b.get("voter"), b.get("target"), float(b.get("confidence") or 0.0))
        for b in m.get("ballots") or []
    ]
    return accus_by_speaker, accused_targets, alibis, sightings, ballots


def positions_by_tick(rows):
    """Reconstruct each player's room per tick from move actions (spawn=CAFETERIA,
    reset to CAFETERIA after each meeting). -> {tick: {player: room}}."""
    pos, snap = {}, {}
    for r in rows:
        if r.get("kind") == "tick":
            for a in r.get("actions") or []:
                if a.get("type") == "move":
                    room = (a.get("payload") or {}).get("to_room")
                    if a.get("actor") and room:
                        pos[a["actor"]] = room
            snap[r.get("tick")] = dict(pos)
        elif r.get("kind") == "meeting":
            for p in list(pos):
                pos[p] = SPAWN
    return snap


def main():
    rep = json.loads((SAMP / "tournament-eval-report.json").read_text())
    meta = {g["seed"]: g for g in rep["report"]["games"]}
    seeds = sorted(meta)

    p1 = {
        "meetings": 0,
        "rec_eject": 0,
        "rec_skip": 0,
        "tally_mismatch": 0,
        "imperative_only_eject": 0,
        "belief_flip": Counter(),
        "loose_flip": Counter(),
    }
    p2 = {
        "meetings": 0,
        "mtg_with_alibi": 0,
        "n_alibi": 0,
        "n_sighting": 0,
        "mtg_strong": set(),
        "tp_subjects": 0,
        "fp_subjects": 0,
        "ceiling_false_imp_alibi": 0,
        "ceiling_false_crew_alibi": 0,
        "seeds_with_strong": set(),
        "examples": [],
    }

    for seed in seeds:
        rows = rows_for(seed)
        rl = meta[seed]["roles"]
        mtgs = [r for r in rows if r.get("kind") == "meeting"]
        snap = positions_by_tick(rows)
        for mi, m in enumerate(mtgs):
            accus, accused, alibis, sightings, ballots = parse_meeting(m)

            # ---- PROBE 1 ----
            p1["meetings"] += 1
            rec = tally([(t, c) for (_, t, c) in ballots])
            recorded = (
                ("EJECTED", m.get("ejected_player_id"))
                if m.get("ejected_player_id")
                else ("SKIPPED", None)
            )
            if rec != recorded:
                p1["tally_mismatch"] += 1
            if rec[0] == "EJECTED":
                p1["rec_eject"] += 1
                if rec[1] not in accused:
                    p1["imperative_only_eject"] += 1
            else:
                p1["rec_skip"] += 1
            belief_bal = []
            for v, _t, c in ballots:
                al = accus.get(v, [])
                belief_bal.append(max(al, key=lambda x: x[1]) if al else ("SKIP", c))
            loose_bal = [
                (t if (t == "SKIP" or t in accused) else "SKIP", c)
                for (_, t, c) in ballots
            ]
            for label, alt in (
                ("belief", tally(belief_bal)),
                ("loose", tally(loose_bal)),
            ):
                if rec[0] == "EJECTED" and alt[0] == "EJECTED" and rec[1] != alt[1]:
                    key = "EJECT->EJECT(redirect)"
                else:
                    key = (
                        ("EJECT" if rec[0] == "EJECTED" else "SKIP")
                        + "->"
                        + ("EJECT" if alt[0] == "EJECTED" else "SKIP")
                    )
                p1[label + "_flip"][key] += 1

            # ---- PROBE 2 ----
            p2["meetings"] += 1
            p2["n_alibi"] += len(alibis)
            p2["n_sighting"] += len(sightings)
            if alibis:
                p2["mtg_with_alibi"] += 1
            flagged = set()
            for sub, room, f, t in alibis:
                if not room:
                    continue
                for obs, seen, room2, tk in sightings:
                    if seen == sub and obs != sub and room2 and room2 != room:
                        in_window = not (
                            f is not None and t is not None and tk is not None
                        ) or (f <= tk <= t)
                        if in_window:
                            flagged.add(sub)
            if flagged:
                p2["mtg_strong"].add((seed, mi))
                p2["seeds_with_strong"].add(seed)
                for sub in flagged:
                    if rl.get(sub) == "IMPOSTOR":
                        p2["tp_subjects"] += 1
                    else:
                        p2["fp_subjects"] += 1
                if len(p2["examples"]) < 8:
                    p2["examples"].append(
                        (seed, mi, sorted((s, rl.get(s)) for s in flagged))
                    )
            for sub, room, f, t in alibis:
                if not room or f is None or t is None:
                    continue
                actual = {snap.get(tk, {}).get(sub) for tk in range(f, t + 1)}
                actual.discard(None)
                if actual and room not in actual:
                    key = (
                        "ceiling_false_imp_alibi"
                        if rl.get(sub) == "IMPOSTOR"
                        else "ceiling_false_crew_alibi"
                    )
                    p2[key] += 1

    print("=" * 72)
    print("PROBE 1 - A-1 desk test (does the §4.6 imperative change OUTCOMES?)")
    print("=" * 72)
    print(
        f"  meetings={p1['meetings']}  recorded EJECT={p1['rec_eject']}  SKIP={p1['rec_skip']}"
    )
    print(f"  tally replication mismatches (should be ~0): {p1['tally_mismatch']}")
    print(
        f"  recorded ejections where the ejectee was accused by NOBODY (imperative-only): "
        f"{p1['imperative_only_eject']}/{p1['rec_eject']}"
    )
    print("  BELIEF cf (voters vote their own spoken accusation, else SKIP):")
    for k, v in sorted(p1["belief_flip"].items()):
        print(f"      {k:24} {v}")
    print("  LOOSE cf (drop votes for never-spoken-accused targets):")
    for k, v in sorted(p1["loose_flip"].items()):
        print(f"      {k:24} {v}")

    print("\n" + "=" * 72)
    print(
        "PROBE 2 - inferential cross-speaker alibi-conflict detector (does R7 leave 0?)"
    )
    print("=" * 72)
    print(
        f"  meetings={p2['meetings']}  with >=1 alibi={p2['mtg_with_alibi']}  "
        f"total alibis={p2['n_alibi']}  total sightings={p2['n_sighting']}"
    )
    print(
        f"  meetings with >=1 cross-speaker alibi_conflict (firewall-clean STRONG proxy): "
        f"{len(p2['mtg_strong'])}/{p2['meetings']}  on {len(p2['seeds_with_strong'])} seeds"
    )
    print(
        f"  flagged subjects: {p2['tp_subjects']} true-impostor (TP) | {p2['fp_subjects']} crewmate (FP)"
    )
    print(
        f"  ground-truth ceiling (alibi vs reconstructed position): "
        f"false impostor-alibis={p2['ceiling_false_imp_alibi']}  false crew-alibis={p2['ceiling_false_crew_alibi']}"
    )
    print("  examples (seed, meeting#, [flagged (player, role)]):")
    for ex in p2["examples"]:
        print(f"      seed {ex[0]} m{ex[1]}: {ex[2]}")


if __name__ == "__main__":
    main()
