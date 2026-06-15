"""Rubric scorer (Tier 0 operationalized) — turns rubric.md R1-R7 into numbers.

Decision informed: the 10.17 smoke pre-flight (is the meeting layer becoming
load-bearing BEFORE the 5h full run?) and the phase-close audit. This scores ANY
committed sample dir's extractor facts JSON against the interestingness rubric
(experiments/lab/rubric.md). It is a design-thread analyzer, NOT a shipped eval
gate (10.16 owns the formal gate metrics); this is the "is it INTERESTING" layer.

Run on the W1 bytes to lock the baseline, then on the 10.17 smoke/full to see
whether Wave 2 moved each item the desired direction.

Each R-item prints: current value, the rubric's desired direction, and a coarse
flag (the rubric is directional, not a hard gate — flags are orientation, not
pass/fail). Items needing data the facts JSON does not yet carry (e.g. do_task
by role — added by 10.16's action ingest) print NEEDS-10.16 rather than a wrong
number.

Usage:
    uv run python experiments/lab/rubric_score.py FACTS_JSON
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _pct(n: int, d: int) -> str:
    return f"{n}/{d} ({(100 * n / d):.0f}%)" if d else f"{n}/0"


def _meetings_per_game(games: list[dict[str, Any]]) -> dict[int, int]:
    hist: dict[int, int] = {}
    for g in games:
        k = len(g["meetings"])
        hist[k] = hist.get(k, 0) + 1
    return dict(sorted(hist.items()))


def score(facts: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Return (item, value, desired) rows."""
    games = facts["games"]
    agg = facts["aggregates"]
    n = len(games)
    rows: list[tuple[str, str, str]] = []

    # ---- R1 deduction decides ----
    reasons = agg["reason_counts"]
    eject_wins = reasons.get("CREWMATE_EJECT", 0)
    task_wins = reasons.get("CREWMATE_TASKS", 0)
    zero_mtg = sum(1 for g in games if not g["meetings"])
    rows.append(
        (
            "R1 ejection-driven win share",
            _pct(eject_wins, n),
            "UP (deduction, not the clock)",
        )
    )
    rows.append(("R1 task-stopwatch win share", _pct(task_wins, n), "DOWN"))
    rows.append(("R1 zero-meeting games", _pct(zero_mtg, n), "DOWN"))

    # ---- R2 deception works sometimes ----
    # accused-impostor survival: an impostor verbally accused in a meeting who is
    # not the meeting's ejected player and is alive at game end.
    accused_imp = survived_imp = 0
    for g in games:
        roles = g["roles"]
        # An impostor "survives" deduction if, having been verbally accused, they
        # are alive at game end (not killed, not ever ejected) — the real
        # deception-effectiveness denominator, not just "not ejected this meeting".
        ejected_ever = {
            m["ejected_player_id"] for m in g["meetings"] if m.get("ejected_player_id")
        }
        gone = set(g["deaths"]) | ejected_ever
        accused_imps = {
            a["accused"]
            for m in g["meetings"]
            for a in m["accusations"]
            if roles.get(a["accused"]) == "IMPOSTOR" and a["accused"] != a["speaker"]
        }
        accused_imp += len(accused_imps)
        survived_imp += sum(1 for p in accused_imps if p not in gone)
    rows.append(
        (
            "R2 accused-impostor survival",
            _pct(survived_imp, accused_imp),
            "DOWN as deception gets catchable; effective-deflection subcount = 10.16",
        )
    )
    rows.append(
        (
            "R2 impostor do_task emissions",
            "NEEDS-10.16 (action-by-role ingest)",
            "UP from 0 (blending)",
        )
    )

    # ---- R3 suspicion arcs ----
    # zero-contradiction ejections = carry/accumulator-driven convictions (no flag
    # named the ejected this meeting) — the cross-meeting arc.
    zero_contra_eject = 0
    for g in games:
        for m in g["meetings"]:
            ej = m.get("ejected_player_id")
            if ej and ej not in (m.get("contradictions_by_subject") or {}):
                zero_contra_eject += 1
    total_eject = agg["ejection_accuracy"]["total_ejections"]
    rows.append(
        (
            "R3 carry-driven ejections (zero-contradiction)",
            _pct(zero_contra_eject, total_eject),
            "present (arcs land), reconstructed in the close audit",
        )
    )

    # ---- R4 no railroads (hard floor) ----
    inv = agg["threshold_inversions"]
    inv_count = inv.get("count", inv) if isinstance(inv, dict) else inv
    wrong = agg["ejection_accuracy"]["wrong_ejections"]
    rows.append(("R4 threshold inversions", f"{inv_count}", "0 (hard floor)"))
    rows.append(
        (
            "R4 wrong-ejection games",
            f"{len(wrong)}",
            "not RISING; all graph-consistent (close audit verifies)",
        )
    )
    rows.append(
        (
            "R4 impostor-victim (friendly) kills",
            f"{agg['impostor_victim_kills']}",
            "0 (hard floor)",
        )
    )

    # ---- R5 varied win paths ----
    eject_per_game: dict[int, int] = {}
    for g in games:
        k = sum(1 for m in g["meetings"] if m.get("ejected_player_id"))
        eject_per_game[k] = eject_per_game.get(k, 0) + 1
    rows.append(
        (
            "R5 win-reason distribution",
            json.dumps(reasons),
            ">=3 shapes each >=10% (aspirational)",
        )
    )
    rows.append(
        (
            "R5 ejections/game histogram",
            json.dumps(dict(sorted(eject_per_game.items()))),
            "spread up from 0-2",
        )
    )
    rows.append(
        (
            "R5 meetings/game histogram",
            json.dumps(_meetings_per_game(games)),
            "median up; runway for arcs",
        )
    )

    # ---- R6 agency at the margins ----
    self_acc = sum(
        1
        for g in games
        for m in g["meetings"]
        for a in m["accusations"]
        if a["speaker"] == a["accused"]
    )
    imp_reporters = sum(
        1
        for g in games
        for m in g["meetings"]
        if m.get("triggered_by_role") == "IMPOSTOR"
    )
    rows.append(
        (
            "R6 self-accusations (emergence class)",
            f"{self_acc}",
            "tracked; game-deciding per the audit",
        )
    )
    rows.append(
        (
            "R6 impostor-reporter meetings",
            f"{imp_reporters}",
            "0 today (toolkit greenfield)",
        )
    )
    rows.append(
        (
            "R6 emergency meetings",
            f"{agg.get('trigger_kind_counts', {}).get('emergency', 0)}",
            ">0 (10.8 channel live)",
        )
    )

    # ---- R7 legible stories ----
    mtgs = sum(len(g["meetings"]) for g in games)
    evid_mtgs = sum(
        1 for g in games for m in g["meetings"] if m.get("n_contradictions", 0) > 0
    )
    ft = agg["free_text_length_chars"]
    bf = agg["ballot_follows_chain"]
    rows.append(
        (
            "R7 evidence-bearing meeting share",
            _pct(evid_mtgs, mtgs),
            "UP (stories have evidence)",
        )
    )
    rows.append(
        (
            "R7 free_text medians (open/reply/optin)",
            f"{ft['opening']['median']}/{ft['reply']['median']}/{ft['opt_in']['median']} (max {ft['opening']['max']})",
            "stable ~225; no catastrophic tail",
        )
    )
    rows.append(
        (
            "R7 ballot-follows-chain",
            _pct(bf["follows_chain"], bf["non_skip_ballots"]),
            "UP (votes cite the chain)",
        )
    )

    return rows


def _win_shape(reason: str, ejected_imps: int, n_mtg: int) -> str:
    """Coarse per-game win SHAPE for R5 diversity (decouples 'interesting' from W/L)."""
    if reason == "CREWMATE_EJECT":
        return "eject-decided"
    if reason.startswith("IMPOSTOR"):
        return "impostor-win"
    if reason == "CREWMATE_TASKS":
        if n_mtg == 0:
            return "stopwatch-no-meeting"
        return "stopwatch-some-eject" if ejected_imps else "stopwatch-no-eject"
    return reason or "other"


def _game_interestingness(g: dict[str, Any]) -> dict[str, Any]:
    """Per-game interestingness from the per-game-computable rubric items (R1/R2/R3/R7).

    The score is deliberately INDEPENDENT of who won the binary game — the lab
    proved the win split is "purchasable wholesale", so 'interesting' is scored
    from whether DEDUCTION decided (R1), DECEPTION worked (R2), suspicion built
    across meetings (R3), and the story was legible (R7). R5 (win-shape diversity)
    is a set-level property, summarized in :func:`interestingness`.
    """
    roles = g["roles"]
    meetings = g["meetings"]
    n_mtg = len(meetings)
    reason = g.get("reason") or ""
    impostor_win = reason.startswith("IMPOSTOR")

    ejected_imp_mtgs = sum(1 for m in meetings if m.get("ejected_role") == "IMPOSTOR")
    ejected_ever = {
        m["ejected_player_id"] for m in meetings if m.get("ejected_player_id")
    }
    gone = set(g.get("deaths", [])) | ejected_ever
    accused_imps = {
        a["accused"]
        for m in meetings
        for a in m["accusations"]
        if roles.get(a["accused"]) == "IMPOSTOR" and a["accused"] != a["speaker"]
    }
    survived_accused = {p for p in accused_imps if p not in gone}

    # R1 decisiveness: did ejection (deduction) decide the board, not the clock?
    if reason == "CREWMATE_EJECT":
        r1 = 1.0
    elif ejected_imp_mtgs >= 1:
        r1 = 0.5  # caught some, but the task clock decided
    else:
        r1 = 0.0  # pure stopwatch / kill-gifted — deduction was inert

    # R2 deception: did the impostor deceive effectively (and was it even tested)?
    if impostor_win and accused_imps and survived_accused:
        r2 = 1.0  # won DESPITE being accused — peak deception
    elif impostor_win:
        r2 = 0.4  # won via the parity/kill race, little meeting drama
    elif accused_imps and survived_accused:
        r2 = 0.6  # survived an accusation; crew still won
    elif accused_imps:
        r2 = 0.2  # accused and caught — some drama
    else:
        r2 = 0.0  # deception never tested

    # R3 arcs: suspicion building across >=2 meetings + a carry-driven conviction
    carry_eject = any(
        m.get("ejected_player_id")
        and m["ejected_player_id"] not in (m.get("contradictions_by_subject") or {})
        for m in meetings
    )
    r3 = (0.5 + (0.5 if carry_eject else 0.0)) if n_mtg >= 2 else 0.0

    # R7 legibility: share of this game's meetings carrying structured evidence
    evid = sum(1 for m in meetings if m.get("n_contradictions", 0) > 0)
    r7 = (evid / n_mtg) if n_mtg else 0.0

    score = 100 * (0.35 * r1 + 0.25 * r2 + 0.20 * r3 + 0.20 * r7)
    return {
        "seed": g.get("seed"),
        "reason": reason,
        "n_meetings": n_mtg,
        "win_shape": _win_shape(reason, ejected_imp_mtgs, n_mtg),
        "ejected_impostors": ejected_imp_mtgs,
        "accused_impostors": len(accused_imps),
        "survived_accused": len(survived_accused),
        "r1_decisive": round(r1, 2),
        "r2_deception": round(r2, 2),
        "r3_arcs": round(r3, 2),
        "r7_legible": round(r7, 2),
        "score": round(score, 1),
    }


def interestingness(facts: dict[str, Any]) -> dict[str, Any]:
    """Per-game interestingness scores + the set-level R5 win-shape diversity."""
    games = facts["games"]
    per = sorted(
        (_game_interestingness(g) for g in games),
        key=lambda x: x["score"],
        reverse=True,
    )
    n = len(per) or 1
    shapes: dict[str, int] = {}
    for p in per:
        shapes[p["win_shape"]] = shapes.get(p["win_shape"], 0) + 1
    return {
        "mean_score": round(sum(p["score"] for p in per) / n, 1),
        "median_score": round(sorted(p["score"] for p in per)[len(per) // 2], 1)
        if per
        else 0.0,
        "n_games": len(per),
        "win_shapes": dict(sorted(shapes.items(), key=lambda kv: -kv[1])),
        "r5_shapes_over_10pct": sum(1 for c in shapes.values() if c / n >= 0.10),
        "per_game": per,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: rubric_score.py FACTS_JSON", file=sys.stderr)
        return 2
    facts = json.loads(Path(sys.argv[1]).read_text())
    label = facts.get("seedset", "?")
    head = facts.get("git_head", "?")[:12]
    print(
        f"=== Rubric R1-R7 — {label} @ {head} ({facts.get('games_analyzed')} games) ===\n"
    )
    rows = score(facts)
    width = max(len(r[0]) for r in rows)
    for item, value, desired in rows:
        print(f"{item:<{width}}  {value:<46}  desired: {desired}")

    # ---- per-game interestingness score (Phase 11 Wave 0) ----
    inter = interestingness(facts)
    print(
        f"\n=== Interestingness score (per-game; decoupled from W/L) — "
        f"mean {inter['mean_score']} / median {inter['median_score']} over "
        f"{inter['n_games']} games ==="
    )
    print(f"R5 win shapes (>=10% share count = {inter['r5_shapes_over_10pct']}): "
          f"{json.dumps(inter['win_shapes'])}")
    per = inter["per_game"]
    print("\n  rank  seed  score  shape                  mtg  R1   R2   R3   R7")
    for i, p in enumerate(per):
        if len(per) > 16 and 8 <= i < len(per) - 8:
            if i == 8:
                print("  ...")
            continue
        print(
            f"  {i + 1:>4}  {p['seed']!s:>4}  {p['score']:>5}  {p['win_shape']:<21}  "
            f"{p['n_meetings']:>3}  {p['r1_decisive']:<4} {p['r2_deception']:<4} "
            f"{p['r3_arcs']:<4} {p['r7_legible']:<4}"
        )

    out = {
        "seedset": label,
        "git_head": facts.get("git_head"),
        "rows": [{"item": i, "value": v, "desired": d} for i, v, d in rows],
        "interestingness": inter,
    }
    Path("experiments/lab/results-rubric-score.json").write_text(
        json.dumps(out, indent=2)
    )
    print("\nwrote experiments/lab/results-rubric-score.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
