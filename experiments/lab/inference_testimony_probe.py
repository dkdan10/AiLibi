"""Phase-B 13.4-CEILING probe: is there enough PUBLIC TESTIMONY to reconstruct
physically-impossible alibis (13.4's alibi_vs_physical STRONG lever)?

13.3's gate showed R7=0/50 (only 1 alibi_conflict to promote). 13.4 GENERATES STRONG
flags by reconstructing positions from STATED sightings, so its ceiling is bounded by
how much the crew actually *say*. This estimates it via the merged 13.2 helper
(reconstruct_stated_paths) over the committed transcripts:

  - richness:    stated placements per meeting (is there material at all?)
  - two-source:  subjects placed by >=2 DISTINCT other speakers (the two-source
                 conjunction 13.4 requires for a STRONG flag), role-gated
  - conflict:    a subject placed in disjoint rooms at the SAME tick by two different
                 speakers (a hard alibi_vs_physical candidate), role-gated

$0, committed replays, no engine/perception read. Roles from the re-extracted facts
(set TMPDIR to where extract_gameplay_facts.py wrote them).
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from meetings.schemas import MeetingTranscript  # noqa: E402
from meetings.transcript import reconstruct_stated_paths  # noqa: E402

SAMPLES = Path("replays/samples/9p2i")


def roles_by_seed() -> dict:
    facts_path = (
        Path(os.environ.get("TMPDIR", "/tmp")) / "ailibi-gameplay-facts-9p2i.json"
    )
    facts = json.loads(facts_path.read_text())
    return {g["seed"]: g["roles"] for g in facts["games"]}


def replay_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> int:
    print(
        "=== PHASE-B 13.4-CEILING — does public testimony support physical-alibi inference? ===\n"
    )
    roles = roles_by_seed()
    seeds = sorted(
        int(p.stem.split("-")[-1]) for p in SAMPLES.glob("replay-seed-*.jsonl")
    )
    n_mtg = tot_pl = 0
    per_mtg = []
    two_src = {"IMPOSTOR": 0, "CREWMATE": 0}
    conflict = {"IMPOSTOR": 0, "CREWMATE": 0}
    conflict_seeds: set[int] = set()
    for s in seeds:
        rl = roles.get(s, {})
        roster = frozenset(rl)
        for r in replay_rows(SAMPLES / f"replay-seed-{s}.jsonl"):
            if r.get("kind") != "meeting":
                continue
            n_mtg += 1
            tr = MeetingTranscript.model_validate(r["transcript"])
            paths = reconstruct_stated_paths(tr, roster=roster)
            tot_pl += sum(len(v) for v in paths.values())
            per_mtg.append(sum(len(v) for v in paths.values()))
            for subj, pls in paths.items():
                role = rl.get(subj)
                others = [p for p in pls if p.speaker != subj]
                if len({p.speaker for p in others}) >= 2 and role in two_src:
                    two_src[role] += 1
                by_tick: dict[int, dict[str, set]] = defaultdict(
                    lambda: defaultdict(set)
                )
                for p in others:
                    by_tick[p.tick][p.speaker] |= set(p.rooms)
                hit = False
                for spk_rooms in by_tick.values():
                    rs = list(spk_rooms.values())
                    for i in range(len(rs)):
                        for j in range(i + 1, len(rs)):
                            if rs[i] and rs[j] and not (rs[i] & rs[j]):
                                hit = True
                if hit and role in conflict:
                    conflict[role] += 1
                    conflict_seeds.add(s)

    print(
        f"meetings: {n_mtg} | total stated placements: {tot_pl}  "
        f"({tot_pl / max(n_mtg, 1):.1f}/meeting)"
    )
    print(
        f"meetings with >=1 placement: {sum(1 for x in per_mtg if x > 0)}/{n_mtg}; "
        f"with >=3: {sum(1 for x in per_mtg if x >= 3)}/{n_mtg}"
    )
    print(
        f"two-source subjects (>=2 distinct speakers place them): "
        f"IMP {two_src['IMPOSTOR']} | CREW {two_src['CREWMATE']}"
    )
    print(
        f"same-tick room CONFLICTS (alibi_vs_physical candidates): "
        f"IMP {conflict['IMPOSTOR']} | CREW {conflict['CREWMATE']} | on {len(conflict_seeds)} seeds"
    )
    print(
        "\n  Read: 13.4 needs material. Thin placements/meeting + ~0 two-source/conflict"
        "\n  => 13.4 is a no-op and B must RE-SEQUENCE (richer testimony — render/spread —"
        "\n  before the physical detector has anything to reconstruct from)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
