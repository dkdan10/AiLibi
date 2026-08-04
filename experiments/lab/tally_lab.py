"""FROZEN (Phase 19 tier map, training/README.md): concluded design-thread experiment.
Bug fixes and evidence readers only; no new search.

Tally counterfactual lab (Tier 1) — the gp-8 parked owner call's data.

Replays every recorded meeting's ballots under tally VARIANTS and scores the
flips. Reads the audit extractor's facts JSON (ballots carry voter/target roles
and confidence), so the lab inherits the extractor's role ground truth and its
fail-loud provenance.

Variants (V0 is the production rule and doubles as the self-check — its
recompute must match every recorded outcome byte-for-byte):

- V0  as-is: SKIP competes for plurality; SKIP-in-leaders or any tie -> skip;
       a unique non-SKIP leader ejects only with >= 1 ballot for the leader at
       confidence >= 0.60 (DESIGN.md §5.2 + §4.6, threshold inclusive).
- V1  option-c: SKIPs ABSTAIN from the plurality race; unique non-SKIP leader
       with count >= 2 and a confident ballot ejects; non-SKIP ties skip.
- V2  nonskip-majority: unique non-SKIP leader with count > half the non-SKIP
       ballots, count >= 2, and a confident ballot ejects.
- V3  skip-halfweight: SKIP's tally weight is halved (soft bloc); unique
       non-SKIP leader must beat the halved SKIP count and every other target,
       count >= 2, confident ballot required.

Scoring per variant per set: SKIPPED->EJECTED flips split by ejected role
(impostor gained vs innocent created — the R4-cascade cost column),
EJECTED->SKIPPED losses split by role, plus per-meeting detail rows.

CAVEAT (stated per lab governance): no game-state propagation. A flipped
meeting changes everything after it in a real game; these are per-meeting
yields, never re-simulated win splits.

Usage:
    uv run python experiments/lab/tally_lab.py FACTS_JSON [FACTS_JSON ...]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# §4.6 skip-confidence threshold — frozen production constant, restated here
# because the facts JSON does not carry config. Inclusive at the cutoff.
SKIP_CONFIDENCE_THRESHOLD = 0.60
SKIP = "SKIP"


def _leader_confident(ballots: list[dict[str, Any]], leader: str) -> bool:
    return any(
        b["target"] == leader
        and b["confidence"] is not None
        and b["confidence"] >= SKIP_CONFIDENCE_THRESHOLD
        for b in ballots
    )


def tally_v0(ballots: list[dict[str, Any]]) -> str | None:
    """Production rule: SKIP competes; ties/SKIP-led -> skip; confident leader ejects."""
    if not ballots:
        return None
    counts = Counter(b["target"] for b in ballots)
    top = max(counts.values())
    leaders = sorted(t for t, c in counts.items() if c == top)
    if SKIP in leaders or len(leaders) > 1:
        return None
    return leaders[0] if _leader_confident(ballots, leaders[0]) else None


def tally_v1(ballots: list[dict[str, Any]]) -> str | None:
    """Option-c: SKIPs abstain; unique eject-plurality with floor 2 + confidence."""
    counts = Counter(b["target"] for b in ballots if b["target"] != SKIP)
    if not counts:
        return None
    top = max(counts.values())
    leaders = sorted(t for t, c in counts.items() if c == top)
    if len(leaders) > 1 or top < 2:
        return None
    return leaders[0] if _leader_confident(ballots, leaders[0]) else None


def tally_v2(ballots: list[dict[str, Any]]) -> str | None:
    """Non-SKIP majority: leader > half of non-SKIP ballots, floor 2, confidence."""
    nonskip = [b for b in ballots if b["target"] != SKIP]
    counts = Counter(b["target"] for b in nonskip)
    if not counts:
        return None
    top = max(counts.values())
    leaders = sorted(t for t, c in counts.items() if c == top)
    if len(leaders) > 1 or top < 2 or top * 2 <= len(nonskip):
        return None
    return leaders[0] if _leader_confident(ballots, leaders[0]) else None


def tally_v3(ballots: list[dict[str, Any]]) -> str | None:
    """Soft bloc: SKIP at half weight; unique leader beats halved SKIP + all targets."""
    counts = Counter(b["target"] for b in ballots if b["target"] != SKIP)
    skip_weight = sum(1 for b in ballots if b["target"] == SKIP) / 2.0
    if not counts:
        return None
    top = max(counts.values())
    leaders = sorted(t for t, c in counts.items() if c == top)
    if len(leaders) > 1 or top < 2 or top <= skip_weight:
        return None
    return leaders[0] if _leader_confident(ballots, leaders[0]) else None


VARIANTS = {
    "V0_as_is": tally_v0,
    "V1_option_c": tally_v1,
    "V2_nonskip_majority": tally_v2,
    "V3_skip_halfweight": tally_v3,
}


def run_set(facts_path: Path) -> dict[str, Any]:
    facts = json.loads(facts_path.read_text())
    label = facts.get("seedset") or facts_path.stem
    roles_by_game: dict[int, dict[str, str]] = {
        g["seed"]: g["roles"] for g in facts["games"]
    }

    rows: list[dict[str, Any]] = []
    v0_mismatches: list[dict[str, Any]] = []
    summary: dict[str, Counter[str]] = {name: Counter() for name in VARIANTS}

    for game in facts["games"]:
        seed = game["seed"]
        roles = roles_by_game[seed]
        for mi, meeting in enumerate(game["meetings"]):
            ballots = meeting["ballots"]
            recorded = meeting.get("ejected_player_id")
            results = {name: fn(ballots) for name, fn in VARIANTS.items()}

            if results["V0_as_is"] != recorded:
                v0_mismatches.append(
                    {
                        "seed": seed,
                        "meeting": mi,
                        "recorded": recorded,
                        "recomputed": results["V0_as_is"],
                    }
                )

            for name, ejected in results.items():
                if name == "V0_as_is":
                    continue
                base = results["V0_as_is"]
                if ejected == base:
                    continue
                kind = (
                    "gain"
                    if base is None and ejected is not None
                    else "loss"
                    if base is not None and ejected is None
                    else "swap"
                )
                role = (
                    roles.get(ejected, "?")
                    if ejected
                    else (roles.get(base, "?") if base else "?")
                )
                summary[name][f"{kind}:{role}"] += 1
                rows.append(
                    {
                        "set": label,
                        "variant": name,
                        "seed": seed,
                        "meeting": mi,
                        "kind": kind,
                        "v0": base,
                        "variant_ejected": ejected,
                        "ejected_role": roles.get(ejected, "?") if ejected else None,
                        "ballots": [
                            (b["voter"], b["target"], b["confidence"]) for b in ballots
                        ],
                    }
                )

    return {
        "set": label,
        "facts": str(facts_path),
        "meetings": sum(len(g["meetings"]) for g in facts["games"]),
        "v0_selfcheck_mismatches": v0_mismatches,
        "summary": {name: dict(c) for name, c in summary.items()},
        "flips": rows,
    }


def main() -> int:
    out: dict[str, Any] = {"sets": []}
    for arg in sys.argv[1:]:
        result = run_set(Path(arg))
        out["sets"].append(result)
        print(f"== {result['set']} ({result['meetings']} meetings) ==")
        n_mis = len(result["v0_selfcheck_mismatches"])
        print(
            f"V0 self-check: {'OK' if n_mis == 0 else f'{n_mis} MISMATCHES (lab invalid for this set!)'}"
        )
        if n_mis:
            for m in result["v0_selfcheck_mismatches"][:5]:
                print("  ", m)
        for name, counts in result["summary"].items():
            if name != "V0_as_is":
                print(f"{name}: {dict(sorted(counts.items())) or 'no flips'}")
    report = Path("experiments/lab/results-tally-lab.json")
    report.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\nwrote {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
