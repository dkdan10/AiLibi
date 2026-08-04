"""FROZEN (Phase 19 tier map, training/README.md): concluded design-thread experiment.
Bug fixes and evidence readers only; no new search.

Vent-escape counterfactual (offline, $0) — does hidden movement let the
impostor's alibi survive the detector?

For every recorded meeting in a committed sample set, simulate that each impostor
VENTED at its (earliest) kill: remove every SawPlayerObservation of that impostor
with tick >= its kill tick (the post-kill walk-away trail a vent hides), then
re-run the production contradiction detector on the REAL transcript. Measures how
much of the structured evidence against impostors is the post-kill sighting trail
(what vents eliminate) vs survives anyway (pre-kill sightings; self-pair alibi
drift). Upper bound: strips the whole post-kill trail, incl. non-incriminating
sightings.

Usage:
    uv run python experiments/lab/vent_escape_lab.py --sample-dir DIR --facts F.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from engine.world import load_canonical_map
from experiments.model_probe.corpus import _roles_for_seed, _roster
from meetings.schemas import ContradictionRef, MeetingTranscript, SawPlayerObservation
from meetings.transcript import WEAK_CONTRADICTION_MARKER_PREFIX, detect_contradictions
from orchestrator.replay import MeetingReplayEntry, read_all_entries


def _earliest_impostor_kills(facts_path: Path) -> dict[int, dict[str, int]]:
    facts = json.loads(facts_path.read_text())
    out: dict[int, dict[str, int]] = {}
    for g in facts["games"]:
        earliest: dict[str, int] = {}
        for k in g["kills"]:
            if k.get("killer_role") != "IMPOSTOR":
                continue
            killer, tick = k["killer"], k["tick"]
            if killer not in earliest or tick < earliest[killer]:
                earliest[killer] = tick
        out[g["seed"]] = earliest
    return out


def _strength(flag: ContradictionRef) -> str:
    return "weak" if WEAK_CONTRADICTION_MARKER_PREFIX in flag.description else "strong"


def _vent_transcript(
    transcript: MeetingTranscript, hide: dict[str, int]
) -> tuple[MeetingTranscript, int]:
    """Strip post-kill impostor sightings; return (transcript, removed_count)."""
    removed = 0
    new_turns = []
    for turn in transcript.turns:
        kept = []
        for o in turn.observations:
            if (
                isinstance(o, SawPlayerObservation)
                and o.subject in hide
                and o.tick >= hide[o.subject]
            ):
                removed += 1
                continue
            kept.append(o)
        new_turns.append(turn.model_copy(update={"observations": tuple(kept)}))
    return MeetingTranscript(turns=tuple(new_turns)), removed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-dir", type=Path, required=True)
    ap.add_argument("--facts", type=Path, required=True)
    args = ap.parse_args()

    game_map = load_canonical_map()
    roster = _roster(args.sample_dir)
    kbs = _earliest_impostor_kills(args.facts)

    base_imp: Counter[tuple[str, str]] = Counter()
    vent_imp: Counter[tuple[str, str]] = Counter()
    base_crew = vent_crew = 0
    removed_total = 0
    n_meetings = imp_meetings = base_flagged = vent_flagged = cleaned = 0

    for path in sorted(
        args.sample_dir.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    ):
        seed = int(path.stem.rsplit("-", 1)[1])
        roles = _roles_for_seed(seed, game_map, roster)
        impostors = {p for p, r in roles.items() if r == "IMPOSTOR"}
        crew = {p for p, r in roles.items() if r == "CREWMATE"}
        hide: dict[str, int] = {}
        for imp in impostors:
            kt = kbs.get(seed, {}).get(imp)
            if kt is not None:
                hide[imp] = kt

        for m in (
            e for e in read_all_entries(path) if isinstance(e, MeetingReplayEntry)
        ):
            n_meetings += 1
            rf = frozenset(b.voter for b in m.ballots)
            tv, removed = _vent_transcript(m.transcript, hide)
            removed_total += removed
            bflags = detect_contradictions(m.transcript, roster=rf)
            vflags = detect_contradictions(tv, roster=rf)

            for f in bflags:
                if any(s in impostors for s in f.subjects):
                    base_imp[(f.kind, _strength(f))] += 1
                base_crew += int(any(s in crew for s in f.subjects))
            for f in vflags:
                if any(s in impostors for s in f.subjects):
                    vent_imp[(f.kind, _strength(f))] += 1
                vent_crew += int(any(s in crew for s in f.subjects))

            for imp in impostors & rf:
                imp_meetings += 1
                b = any(imp in f.subjects for f in bflags)
                v = any(imp in f.subjects for f in vflags)
                base_flagged += int(b)
                vent_flagged += int(v)
                cleaned += int(b and not v)

    tot_b, tot_v = sum(base_imp.values()), sum(vent_imp.values())
    print(
        f"meetings: {n_meetings} | impostor-meeting instances (alive): {imp_meetings}"
    )
    print(f"post-kill impostor SawPlayer obs removed (vent-hidden): {removed_total}\n")
    pct = 100 * (tot_b - tot_v) / tot_b if tot_b else 0
    print(
        f"IMPOSTOR flags: baseline {tot_b} -> vent {tot_v} (eliminated {tot_b - tot_v}, {pct:.0f}%)"
    )
    for key in sorted(set(base_imp) | set(vent_imp)):
        print(f"    {key[0]:18} {key[1]:6}  {base_imp[key]:3} -> {vent_imp[key]:3}")
    print(f"\nCREW flags (sanity, ~unchanged): {base_crew} -> {vent_crew}\n")
    fb = 100 * base_flagged / imp_meetings if imp_meetings else 0
    fv = 100 * vent_flagged / imp_meetings if imp_meetings else 0
    cl = 100 * cleaned / base_flagged if base_flagged else 0
    print(
        f"impostor-meetings FLAGGED: baseline {base_flagged}/{imp_meetings} ({fb:.0f}%) "
        f"-> vent {vent_flagged}/{imp_meetings} ({fv:.0f}%)"
    )
    print(
        f"  ... {cleaned}/{base_flagged} baseline-flagged go FLAG-CLEAN under vent ({cl:.0f}%)"
    )


if __name__ == "__main__":
    main()
