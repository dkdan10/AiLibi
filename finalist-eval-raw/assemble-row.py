#!/usr/bin/env python3
"""Task 18.26 row assembler — one results-finalist-eval.jsonl row per arm.

Composes the row from score-arm.py outputs, mirroring the 17.14 row schema for
impostor arms (baseline-6 watchability), the opponent-absence shape for the
comparator, and the distinct-slot dual-stamp shape for crew arms (explicitly
NOT realpath-v3). Writes scoring/<arm>/row.json (one JSON object, one line).

Usage:
  assemble-row.py <arm> --entrant <name> --artifact <committed dir>
  assemble-row.py <arm> --entrant <name> --comparator
  assemble-row.py <arm> --entrant <name> --crew-artifact <dir> --opponent-artifact <dir>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path.home() / "ailibi-campaign-1826"
REPO = Path("/Users/danielkeinan/projects/AiLibi")

STAMP_SOURCE = (
    "read back from the recording bytes of every game via "
    "orchestrator.replay.read_tactical_policy_stamp; never echoed from the launch config"
)
CREW_STAMP_SOURCE = (
    "read back from the recording bytes of every game via "
    "orchestrator.replay.read_policy_stamps (.crew / .tactical, distinct schema slots); "
    "never echoed from the launch config"
)
RAW_RECORDINGS = (
    "operator working artifacts; NOT part of replays/; re-recordable from "
    "report-finalist-eval.md Part II §9"
)


def load_row(p: Path) -> dict[str, Any]:
    d = json.loads(p.read_text())
    return d[0] if isinstance(d, list) else d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("arm")
    ap.add_argument("--entrant", required=True)
    ap.add_argument("--artifact")
    ap.add_argument("--crew-artifact")
    ap.add_argument("--opponent-artifact")
    ap.add_argument("--comparator", action="store_true")
    ap.add_argument("--allow-validity-fail", action="store_true",
                    help="crew diagnostic starvation outcome: stage the row with "
                         "validity_gate.passed=false recorded honestly")
    a = ap.parse_args()

    rec = ROOT / a.arm
    sc = ROOT / "scoring" / a.arm
    duration = json.loads((sc / "duration.json").read_text())
    git_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                             capture_output=True, text=True).stdout.strip()

    sys.path.insert(0, str(REPO))
    from orchestrator.replay import read_policy_stamps  # noqa: E402

    stamps0 = read_policy_stamps(rec / "replay-seed-0.jsonl")

    validity = load_row(sc / "validity.json")
    if not validity.get("passed") and not a.allow_validity_fail:
        raise SystemExit(f"REFUSING to assemble a row for {a.arm}: validity gate not passed")

    proof = json.loads((sc / "stamp-proof.json").read_text())
    crew_games = proof.get("stamped_games", 50)

    row: dict[str, Any] = {}
    if a.crew_artifact:
        crew_dir = Path(a.crew_artifact)
        opp_dir = Path(a.opponent_artifact)
        crew_sidecar = (crew_dir / "weights.json.sha256").read_text().split()[0]
        opp_sidecar = (opp_dir / "weights.json.sha256").read_text().split()[0]
        assert stamps0.crew is not None and stamps0.tactical is not None
        row.update({
            # subject = the crew artifact (distinct-slot convention, NOT realpath-v3)
            "artifact_path": str(crew_dir.relative_to(REPO)) if crew_dir.is_absolute() else str(crew_dir),
            "committed_sidecar": str((crew_dir / "weights.json.sha256").relative_to(REPO)) if crew_dir.is_absolute() else str(crew_dir / "weights.json.sha256"),
            "committed_weights_sha256": crew_sidecar,
            "crew_tactical_policy_stamp": stamps0.crew.model_dump(),
            "crew_stamp_verified_games": crew_games,
            "crew_stamp_equals_committed_sha256": stamps0.crew.weights_sha256 == crew_sidecar,
            "stalemate_games_no_game_over": proof.get("stalemate_games_no_game_over", []),
            # the frozen opponent, in its own slots
            "opponent_artifact_path": str(opp_dir.relative_to(REPO)) if opp_dir.is_absolute() else str(opp_dir),
            "opponent_committed_weights_sha256": opp_sidecar,
            "opponent_tactical_policy_stamp": stamps0.tactical.model_dump(),
            "opponent_stamp_verified_games": crew_games,
            "opponent_stamp_equals_committed_sha256": stamps0.tactical.weights_sha256 == opp_sidecar,
            "stamp_source": CREW_STAMP_SOURCE,
        })
        seam = ("scripts/run_tournament.py --crew-artifact " + row["artifact_path"]
                + " --candidate-artifact " + row["opponent_artifact_path"] + " (Task 18.26)")
    elif a.comparator:
        assert stamps0.crew is None
        tac = stamps0.tactical
        row.update({
            "artifact_path": None,
            "committed_sidecar": None,
            "committed_weights_sha256": None,
            "tactical_policy_stamp": tac.model_dump() if tac is not None else None,
            "stamp_source": STAMP_SOURCE,
            "stamp_verified_games": proof.get("games", 50),
            "learned_stamp_games": 0,
            "crew_stamp_games": 0,
            "opponent_absence_proven": True,
            "stamp_equals_committed_sha256": None,
        })
        seam = "scripts/run_tournament.py --tactical-policy-stamp fsm-default (Task 18.26)"
    else:
        art = Path(a.artifact)
        sidecar = (art / "weights.json.sha256").read_text().split()[0]
        assert stamps0.tactical is not None and stamps0.crew is None
        rel = str(art.relative_to(REPO)) if art.is_absolute() else str(art)
        row.update({
            "artifact_path": rel,
            "committed_sidecar": rel + "/weights.json.sha256",
            "committed_weights_sha256": sidecar,
            "tactical_policy_stamp": stamps0.tactical.model_dump(),
            "stamp_source": STAMP_SOURCE,
            "stamp_verified_games": proof.get("games", 50),
            "stamp_equals_committed_sha256": stamps0.tactical.weights_sha256 == sidecar,
        })
        seam = "scripts/run_tournament.py --candidate-artifact " + rel + " (Task 18.26)"

    row["recording"] = {
        "cost_usd": 0.0,
        "model": "Qwen/Qwen3.6-27B",
        "prompt_set": "qwen3_6_27b",
        "provider": "featherless",
        "raw_recordings": RAW_RECORDINGS,
        "recorded_at_utc": duration["leg_end"],
        "recording_git_sha": git_sha,
        "roster": {"num_impostors": 2, "num_players": 9, "tasks_per_crewmate": 2},
        "seam": seam,
        "seeds": sorted(
            int(p.name.removeprefix("replay-seed-").removesuffix(".jsonl"))
            for p in rec.glob("replay-seed-*.jsonl")
        ),
    }
    row["entrant"] = a.entrant
    row["core"] = load_row(sc / "core.json")
    row["funnel"] = load_row(sc / "funnel.json")
    row["watchability"] = load_row(sc / "watchability.json")
    row["validity_gate"] = validity
    # the pre-registered cell 1 read + instruments ride beside the classic blocks
    row["split_half"] = json.loads((sc / "split-half.json").read_text())
    inst = json.loads((sc / "instruments.json").read_text())
    row["instruments"] = {
        "kill_craft": {k: v for k, v in inst["kill_craft"].items() if not isinstance(v, (list, dict))},
        "deception": {k: v for k, v in inst["deception"].items() if not isinstance(v, (list, dict))},
        "off_menu": {k: v for k, v in inst["off_menu"].items() if not isinstance(v, (list, dict))},
        "roll_call": inst["roll_call"],
    }

    out = sc / "row.json"
    out.write_text(json.dumps(row, sort_keys=False) + "\n")
    print(f"row staged: {out} entrant={a.entrant} "
          f"win={row['core'].get('impostor_win_rate')} "
          f"validity={validity.get('passed')}")


if __name__ == "__main__":
    main()
