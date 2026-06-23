"""Conversion probe (Probe 4): with alibi_vs_sighting promoted to STRONG (all 111 flags, the real
lever = removing WEAK_REASON_SELF_STATED), how many crew flags would actually EJECT, not just flag?
The Wave-E review (audits/audit-2026-06-22-2149) flagged that the probes measured FLAG precision,
not ejection CONVERSION. This measures conversion. See report-forward-redesign-probes.md (Probe 4).

Model (deterministic-gate worst case, i.e. PRE-13.13 — the gate makes every voter vote the
argmax-suspicion subject): a promoted flag lifts its subject to ~0.5+0.3=0.80, crossing the 0.60
gate, so the eject target = the argmax flagged subject. Hence:
  - a crew flag SOLE in its meeting (no impostor flagged) -> crew is the argmax -> WRONG ejection.
  - a crew flag co-flagged with an impostor -> the impostor is the likely argmax -> crew shielded.
Caveat: 13.13 de-imperative REMOVES this gate convergence, so this is the worst-case UPPER bound; the
real 13.13+13.14 rate is measured by the held re-record smoke. Baseline = the recorded ejections by
role (the current wrong-ejection / R4 rate).

Run: uv run python experiments/lab/forward_redesign_conversion_probe.py  ($0, reads committed replays).
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))  # lab bootstrap so meetings.* imports resolve

import meetings.transcript as T  # noqa: E402
from meetings.schemas import MeetingTranscript  # noqa: E402
from meetings.transcript import detect_contradictions  # noqa: E402

SAMP = REPO / "replays" / "samples" / "9p2i"


def meetings_of(seed):
    lines = (SAMP / f"replay-seed-{seed}.jsonl").read_text().splitlines()
    return [
        r
        for r in (json.loads(s) for s in lines if s.strip())
        if r.get("kind") == "meeting"
    ]


def main():
    rep = json.loads((SAMP / "tournament-eval-report.json").read_text())
    meta = {g["seed"]: g for g in rep["report"]["games"]}

    n = rec_crew = rec_imp = rec_skip = 0
    crew_sole = crew_co = imp_total = 0
    new_wrong = []
    new_right = 0

    for seed in sorted(meta):
        roles = meta[seed]["roles"]
        roster = frozenset(roles)
        for mi, m in enumerate(meetings_of(seed)):
            n += 1
            tr = MeetingTranscript.model_validate(m["transcript"])
            T.PHYSICAL_CONTRADICTION_MIN_VOICES = 2
            flags = detect_contradictions(tr, roster=roster)
            # promote ALL alibi_vs_sighting (the real lever ignores the weak marker)
            flagged = {
                s
                for f in flags
                if f.kind == "alibi_vs_sighting"
                for s in f.subjects
                if s in roster
            }
            crew = [s for s in flagged if roles[s] == "CREWMATE"]
            imp = [s for s in flagged if roles[s] == "IMPOSTOR"]
            for _ in crew:
                if imp:
                    crew_co += 1
                else:
                    crew_sole += 1
            imp_total += len(imp)
            rec = m.get("ejected_player_id")
            if rec:
                if roles.get(rec) == "IMPOSTOR":
                    rec_imp += 1
                else:
                    rec_crew += 1
            else:
                rec_skip += 1
                if crew and not imp:
                    new_wrong.append((seed, mi, crew))
                elif imp:
                    new_right += 1

    print(f"meetings={n}")
    print("\n=== BASELINE (recorded outcomes) ===")
    print(
        f"  ejections: {rec_imp} impostor (correct) + {rec_crew} CREW (wrong / R4) | {rec_skip} SKIP"
    )
    print("\n=== WITH alibi_vs_sighting PROMOTED (deterministic-gate worst case) ===")
    print(
        f"  crew flags: {crew_sole} SOLE (would WRONG-eject) + {crew_co} co-flagged-with-impostor (shielded)"
    )
    print(f"  impostor flags: {imp_total} total")
    print("  NEW ejections the promotion CREATES from recorded SKIPs:")
    print(f"    correct (an impostor flagged): ~{new_right} meetings")
    print(f"    WRONG (sole crew flag, recorded SKIP): {len(new_wrong)} -> {new_wrong}")
    print(
        f"\n  => worst-case wrong-ejection delta vs baseline R4={rec_crew}: +{len(new_wrong)}; benefit +{new_right} correct"
    )


if __name__ == "__main__":
    main()
