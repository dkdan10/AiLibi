"""Decay sweep + emergence census (Tier 1).

Part 1 — DECAY SWEEP (decision: the deferred decay-rate revisit; R3 arcs).
On the W0 facts (clean 9.8 semantics — no pre-vote folds), re-fold every
(crew voter, subject) rendered-suspicion trajectory from its first observed
value under alternate decay rates d, using the §6.3 quantized model:

    r_{t+1}(d) = 0.5 + (r_t - 0.5) * (1 - d) + 0.05 * accused_t

(accused_t = subject verbally accused in meeting t, deduped per meeting — the
9.8 bump unit; corroborations are NOT modeled, so first VALIDATE at d=0.25
against observed values and report the unexplained share. Transitions failing
validation are excluded from the sweep rather than silently modeled wrong.)
Sweep d in {0.10, 0.25, 0.40}: from-below 0.60-crossings and carry survival
(>= 0.55 at the next meeting). Directional only — W0 pacing is thin (1.56
meetings/game); re-run on the fresh 10.9 bytes for the live answer.

Part 2 — EMERGENCE CENSUS (decision: R6 upside hunt; Wave-2 ambition).
Quantifies unprompted behavior classes on the Wave-1 attempt bytes:
  E1 impostor strategic skips (impostor voter SKIPs while their own rendered
     max >= 0.60 — the seed-10 class)
  E2 self-accusations (speaker accuses themself)
  E3 impostor body-reporters (impostor opens the meeting — proto self-report)
  E4 pre-emptive self-clears (opening carries the reporter's self-alibi with
     no accusation — alibi-first instinct)

Usage:
    uv run python experiments/lab/decay_emergence_lab.py W0_FACTS W1A_FACTS
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

THRESHOLD = 0.60
BUMP = 0.05
TOL = 0.011  # quantization tolerance on the rendered lattice
SWEEP = (0.10, 0.25, 0.40)


def decay_sweep(facts: dict[str, Any]) -> dict[str, Any]:
    validated = excluded = 0
    # trajectories[(seed, voter, subject)] = [(r_obs, accused_flag), ...] per meeting
    crossings = {d: 0 for d in SWEEP}
    survivals = {d: 0 for d in SWEEP}
    transitions = {d: 0 for d in SWEEP}
    for g in facts["games"]:
        meetings = g["meetings"]
        if len(meetings) < 2:
            continue
        roles = g["roles"]
        for i in range(len(meetings) - 1):
            m, nxt = meetings[i], meetings[i + 1]
            accused_now = {a["accused"] for a in m["accusations"]}
            graphs_now = m.get("suspicion_graph_by_voter") or {}
            graphs_next = nxt.get("suspicion_graph_by_voter") or {}
            for voter, graph in graphs_now.items():
                if roles.get(voter) != "CREWMATE":
                    continue
                next_graph = graphs_next.get(voter) or {}
                for subject, r_now in graph.items():
                    if subject not in next_graph:
                        continue
                    r_next = next_graph[subject]
                    bump = BUMP if subject in accused_now else 0.0
                    pred = 0.5 + (r_now - 0.5) * (1 - 0.25) + bump
                    if abs(pred - r_next) > TOL:
                        excluded += 1  # corroboration/other rule in play
                        continue
                    validated += 1
                    for d in SWEEP:
                        r_d = 0.5 + (r_now - 0.5) * (1 - d) + bump
                        transitions[d] += 1
                        if r_now < THRESHOLD <= r_d:
                            crossings[d] += 1
                        if r_d >= 0.55:
                            survivals[d] += 1
    total = validated + excluded
    return {
        "transitions_validated_at_d25": validated,
        "excluded_unexplained (corroboration etc.)": excluded,
        "unexplained_share": round(excluded / total, 3) if total else None,
        "from_below_crossings_by_decay": {str(d): crossings[d] for d in SWEEP},
        "carry_survival_ge_055_by_decay": {
            str(d): f"{survivals[d]}/{transitions[d]}" for d in SWEEP
        },
    }


def emergence_census(facts: dict[str, Any]) -> dict[str, Any]:
    e1 = []  # impostor strategic skips
    e2 = []  # self-accusations
    e3 = []  # impostor reporters
    e4 = []  # pre-emptive self-clears
    for g in facts["games"]:
        for m in g["meetings"]:
            graphs = m.get("suspicion_graph_by_voter") or {}
            for b in m["ballots"]:
                if b["target"] != "SKIP" or b["voter_role"] != "IMPOSTOR":
                    continue
                graph = graphs.get(b["voter"]) or {}
                living_max = max(
                    (v for s, v in graph.items() if s != b["voter"]), default=0.0
                )
                if living_max >= THRESHOLD:
                    e1.append(
                        {
                            "seed": g["seed"],
                            "meeting": m["meeting_index"],
                            "voter": b["voter"],
                            "rendered_max": living_max,
                        }
                    )
            for a in m["accusations"]:
                if a["speaker"] == a["accused"]:
                    e2.append(
                        {
                            "seed": g["seed"],
                            "meeting": m["meeting_index"],
                            "speaker": a["speaker"],
                            "role": a.get("speaker_role"),
                        }
                    )
            if m.get("triggered_by_role") == "IMPOSTOR":
                e3.append(
                    {
                        "seed": g["seed"],
                        "meeting": m["meeting_index"],
                        "reporter": m.get("triggered_by"),
                    }
                )
            if (
                m.get("opening_has_accusation") is False
                and m.get("trigger_kind") == "report"
            ):
                e4.append({"seed": g["seed"], "meeting": m["meeting_index"]})
    return {
        "E1_impostor_strategic_skips": {"n": len(e1), "cites": e1[:6]},
        "E2_self_accusations": {"n": len(e2), "cites": e2[:6]},
        "E3_impostor_reporters": {"n": len(e3), "cites": e3[:6]},
        "E4_openings_without_accusation": {"n": len(e4), "cites": e4[:6]},
    }


def main() -> int:
    w0 = json.loads(Path(sys.argv[1]).read_text())
    w1a = json.loads(Path(sys.argv[2]).read_text())
    out = {
        "decay_sweep_on_w0": decay_sweep(w0),
        "decay_sweep_on_w1a_directional_only": decay_sweep(w1a),
        "emergence_census_w1a": emergence_census(w1a),
        "emergence_census_w0": emergence_census(w0),
    }
    print(json.dumps(out, indent=2))
    Path("experiments/lab/results-decay-emergence.json").write_text(
        json.dumps(out, indent=2, sort_keys=True)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
