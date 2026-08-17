#!/usr/bin/env python3
"""Task 18.26 per-arm scorer — the report-finalist-eval.md Part II §9.3 recipe.

Usage:
  score-arm.py <arm> --artifact <committed dir>                      # impostor arm
  score-arm.py <arm> --crew-artifact <dir> --opponent-artifact <dir> # crew arm
  score-arm.py <arm> --comparator                                    # FSM row

Reads  ~/ailibi-campaign-1826/<arm>/          (the recording set)
Writes ~/ailibi-campaign-1826/scoring/<arm>/  (all outputs; repo untouched)
Prints a compact JSON summary to stdout. Local CPU only — no network.
Run from the repo root so `uv run` resolves the project env.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path.home() / "ailibi-campaign-1826"
REPO = Path("/Users/danielkeinan/projects/AiLibi")

WITNESSED_PIN = 0.03389830508474576
FLAGS_PIN = 1.0909090909090908


def jsonable(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "_asdict"):
        return obj._asdict()
    if hasattr(obj, "__dataclass_fields__"):
        import dataclasses

        return dataclasses.asdict(obj)
    if isinstance(obj, dict):
        return {k: jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    return obj


def run_cli(args: list[str], out_path: Path) -> int:
    proc = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    out_path.write_text(proc.stdout)
    if proc.returncode not in (0, 1):
        print(f"WARN {' '.join(args[-3:])} rc={proc.returncode}: {proc.stderr[-500:]}", file=sys.stderr)
    return proc.returncode


def gauge_map(watch: Any) -> dict[str, dict[str, Any]]:
    if isinstance(watch, list):
        watch = watch[0] if watch else {}
    return {g["name"]: g for g in watch.get("supply_gauges", [])}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("arm")
    ap.add_argument("--artifact")
    ap.add_argument("--crew-artifact")
    ap.add_argument("--opponent-artifact")
    ap.add_argument("--comparator", action="store_true")
    ap.add_argument("--expect-games", type=int, default=50,
                    help="expected replay count (49 for the two stubborn-seed "
                         "fallback arms per the owner decision)")
    ap.add_argument("--diagnostic", action="store_true",
                    help="crew diagnostic: tolerate stalemate games that never "
                         "reach game_over (they carry no stamps); report them "
                         "explicitly instead of failing the stamp proof")
    a = ap.parse_args()

    rec = ROOT / a.arm
    sc = ROOT / "scoring" / a.arm
    sc.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {"arm": a.arm}

    # 1. audit sidecars out of the scorer's glob; roster check
    sidecar_dir = sc / "audit-sidecars"
    sidecar_dir.mkdir(exist_ok=True)
    moved = 0
    for f in rec.glob("*.audit.jsonl"):
        shutil.move(str(f), sidecar_dir / f.name)
        moved += 1
    summary["audit_sidecars_moved"] = moved
    expected = {"num_impostors": 2, "num_players": 9, "tasks_per_crewmate": 2}
    roster_path = rec / "roster.json"
    if not roster_path.exists():
        # operator-supplied set sidecar (the 17.14 "ensure roster.json" step)
        roster_path.write_text(json.dumps(expected, sort_keys=True) + "\n")
        summary["roster_json"] = "written"
    else:
        roster = json.loads(roster_path.read_text())
        assert all(roster.get(k) == v for k, v in expected.items()), f"roster mismatch: {roster}"
        summary["roster_json"] = "verified"

    # 2. validity + core + funnel + watchability
    validity_rc = run_cli(
        ["uv", "run", "python", "scripts/validity_gate.py", str(rec), "--json",
         "--expected-model", "Qwen/Qwen3.6-27B", "--require-zero-cost"],
        sc / "validity.json",
    )
    run_cli(["uv", "run", "python", "scripts/measure_baseline.py", str(rec), "--json"], sc / "core.json")
    run_cli(["uv", "run", "python", "scripts/measure_baseline.py", str(rec), "--funnel", "--json"], sc / "funnel.json")
    run_cli(
        ["uv", "run", "python", "scripts/measure_baseline.py", str(rec), "--watchability",
         "--baseline-id", "baseline-6", "--json"],
        sc / "watchability.json",
    )
    def load_row(p: Path) -> dict[str, Any]:
        d = json.loads(p.read_text())
        return d[0] if isinstance(d, list) else d

    validity = load_row(sc / "validity.json")
    core = load_row(sc / "core.json")
    watch = load_row(sc / "watchability.json")
    summary["validity"] = {"exit_code": validity_rc, "passed": validity.get("passed"),
                           "failed_checks": [c["name"] for c in validity.get("checks", []) if not c.get("passed")]}
    summary["core"] = {k: core.get(k) for k in
                       ("games_total", "impostor_win_rate", "crew_wins", "impostor_wins",
                        "ejection_accuracy", "meeting_rate", "genuine_class_conversion")}
    gm = gauge_map(watch)
    summary["watchability"] = {
        "referee_passed": watch.get("referee_passed"),
        "supply_floors_passed": watch.get("supply_floors_passed"),
        "integrity_ok": watch.get("integrity_ok"),
        "mean_score": watch.get("mean_score"),
        "median_score": watch.get("median_score"),
        "gauges": {n: {"measured": g["measured"], "floor": g["floor"],
                       "distance": (g["measured"] - g["floor"]) if g["measured"] is not None else None,
                       "passed": g["passed"]}
                   for n, g in gm.items()},
    }

    # 3. stamp proof, read back from the bytes
    sys.path.insert(0, str(REPO))
    from orchestrator.replay import read_policy_stamps, read_tactical_policy_stamp  # noqa: E402

    replays = sorted(rec.glob("replay-seed-*.jsonl"))
    assert len(replays) == a.expect_games, f"expected {a.expect_games} replays, found {len(replays)}"
    tacticals = [read_tactical_policy_stamp(p) for p in replays]
    crews = [read_policy_stamps(p).crew for p in replays]
    proof: dict[str, Any] = {"games": len(replays)}
    if a.comparator:
        assert all(s is None or s.weights_sha256 == "none" for s in tacticals), "learned impostor stamp in comparator!"
        assert all(c is None for c in crews), "crew stamp in comparator!"
        ids = {(s.policy_id if s else None) for s in tacticals}
        proof.update({"mode": "comparator", "opponent_absence_proven": True,
                      "tactical_ids": sorted(str(i) for i in ids), "learned_stamp_games": 0,
                      "crew_stamp_games": 0})
    elif a.crew_artifact:
        crew_sidecar = (Path(a.crew_artifact) / "weights.json.sha256").read_text().split()[0]
        opp_sidecar = (Path(a.opponent_artifact) / "weights.json.sha256").read_text().split()[0]
        stalemates = [replays[i].name for i in range(len(replays))
                      if crews[i] is None and tacticals[i] is None]
        if stalemates and not a.diagnostic:
            raise AssertionError(f"missing stamps (stalemates?): {stalemates}")
        crew_stamped = [c for c in crews if c is not None]
        tac_stamped = [s for s in tacticals if s is not None]
        assert len(crew_stamped) == len(tac_stamped) == len(replays) - len(stalemates), \
            "stamp presence mismatch beyond the stalemate set"
        assert len({c.model_dump_json() for c in crew_stamped}) == 1, "crew stamps not uniform"
        assert crew_stamped[0].weights_sha256 == crew_sidecar, "crew stamp != crew sidecar"
        assert len({s.model_dump_json() for s in tac_stamped}) == 1, "opponent stamps not uniform"
        assert tac_stamped[0].weights_sha256 == opp_sidecar, "opponent stamp != opponent sidecar"
        assert crew_stamped[0].weights_sha256 != tac_stamped[0].weights_sha256, "conflation!"
        proof.update({"mode": "crew-dual", "crew_sha": crew_sidecar, "opponent_sha": opp_sidecar,
                      "stamped_games": len(crew_stamped),
                      "stalemate_games_no_game_over": stalemates,
                      "crew_uniform_over_stamped": True, "opponent_uniform_over_stamped": True})
    else:
        sidecar = (Path(a.artifact) / "weights.json.sha256").read_text().split()[0]
        assert all(s is not None for s in tacticals), "missing stamp"
        assert len({s.model_dump_json() for s in tacticals}) == 1, "stamps not uniform"
        assert tacticals[0].weights_sha256 == sidecar, "stamp != sidecar"
        assert all(c is None for c in crews), "unexpected crew stamp"
        proof.update({"mode": "impostor", "sha": sidecar, "uniform_50": True, "no_crew_stamp": True})
    (sc / "stamp-proof.json").write_text(json.dumps(proof, indent=2))
    summary["stamp_proof"] = proof

    # 4. split-half (pre-registered cell 1: H1 even, H2 odd)
    halves = {"h1": [s for s in range(50) if s % 2 == 0], "h2": [s for s in range(50) if s % 2 == 1]}
    for name, seeds in halves.items():
        hd = sc / f"split-{name}"
        if hd.exists():
            shutil.rmtree(hd)
        hd.mkdir()
        for s in seeds:
            src = rec / f"replay-seed-{s}.jsonl"
            if src.exists():
                (hd / f"replay-seed-{s}.jsonl").symlink_to(src)
        shutil.copy(rec / "roster.json", hd / "roster.json")
        run_cli(
            ["uv", "run", "python", "scripts/measure_baseline.py", str(hd), "--watchability",
             "--baseline-id", "baseline-6", "--json"],
            sc / f"watchability-{name}.json",
        )
    h1 = gauge_map(json.loads((sc / "watchability-h1.json").read_text()))
    h2 = gauge_map(json.loads((sc / "watchability-h2.json").read_text()))
    split: dict[str, Any] = {}
    for gname in ("witnessed_event_rate", "flags_per_meeting", "testimony_backed_conversion"):
        v1, v2 = h1[gname]["measured"], h2[gname]["measured"]
        noise = abs(v1 - v2) if (v1 is not None and v2 is not None) else None
        if gname == "witnessed_event_rate":
            base = WITNESSED_PIN
        elif gname == "flags_per_meeting":
            base = FLAGS_PIN
        else:
            base = gm[gname]["floor"]  # the arm's own full-n derived floor
        ceiling = 0.25 * base
        split[gname] = {"h1": v1, "h2": v2, "noise": noise, "threshold_base": base,
                        "ceiling_25pct": ceiling,
                        "precondition": ("clears" if (noise is not None and noise <= ceiling) else "UNRESOLVABLE")}
    (sc / "split-half.json").write_text(json.dumps(split, indent=2))
    summary["split_half"] = split

    # 5. emergence instruments — byte-completeness fence FIRST
    from eval.kill_craft import compute_kill_craft_report  # noqa: E402
    from eval.deception_instruments import compute_deception_instruments  # noqa: E402
    from eval.off_menu import compute_off_menu_report  # noqa: E402
    from eval.funnel import compute_pooling_funnel  # noqa: E402

    inst_dir = rec
    inst_view: dict[str, Any] | None = None
    stale_names = set(summary.get("stamp_proof", {}).get("stalemate_games_no_game_over", []))
    if a.diagnostic and stale_names:
        # the byte-completeness fence refuses non-finalized games by design;
        # instruments run over the finalized view, exclusion recorded
        inst_dir = sc / "instruments-view"
        if inst_dir.exists():
            shutil.rmtree(inst_dir)
        inst_dir.mkdir()
        kept = 0
        for p in rec.glob("replay-seed-*.jsonl"):
            if p.name not in stale_names:
                (inst_dir / p.name).symlink_to(p)
                kept += 1
        shutil.copy(rec / "roster.json", inst_dir / "roster.json")
        inst_view = {"games": kept, "excluded_stalemates": sorted(stale_names)}

    kc = jsonable(compute_kill_craft_report(inst_dir))
    dec = jsonable(compute_deception_instruments(inst_dir))
    om = jsonable(compute_off_menu_report(inst_dir))
    fn = jsonable(compute_pooling_funnel(inst_dir))
    roll = {k: v for k, v in fn.items() if str(k).startswith("roll_call")}
    (sc / "instruments.json").write_text(json.dumps(
        {"kill_craft": kc, "deception": dec, "off_menu": om, "roll_call": roll,
         "instruments_view": inst_view}, indent=2, default=str))
    summary["instruments"] = {
        "crew_witnessed_kills": kc.get("crew_witnessed_kills"),
        "kills_total": kc.get("kills_total"),
        "off_menu_total": om.get("off_menu_total"),
        "impostor_decisions": om.get("impostor_decisions"),
        "roll_call_coverage_mean": roll.get("roll_call_coverage_mean"),
        "roll_call_coverage_crew_mean": roll.get("roll_call_coverage_crew_mean"),
    }

    # 6. duration from the leg log (rc==0 events only; retries counted)
    log = ROOT / f"leg-log-{a.arm}.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines()]
    recs = [e for e in events if e.get("event") == "seed-recorded"]
    ok = [e for e in recs if e["rc"] == 0]
    dur = {"games_ok": len(ok), "retry_events": len([e for e in recs if e["rc"] != 0]),
           "sum_wall_seconds": sum(e["wall_seconds"] for e in ok),
           "mean_min_per_game": sum(e["wall_seconds"] for e in ok) / len(ok) / 60,
           "leg_start": events[0]["at"], "leg_end": events[-1]["at"]}
    (sc / "duration.json").write_text(json.dumps(dur, indent=2))
    summary["duration"] = dur

    (sc / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
