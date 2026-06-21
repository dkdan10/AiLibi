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

import argparse
import json
from pathlib import Path
from typing import Any

# Filename the per-set rubric is co-located under, inside a served replay set
# dir, so ``api.replay_loader.ReplayLoader.rubric`` can serve it (Task 12.2;
# DESIGN.md §3.1, §7). Kept identical to ``api.replay_loader._RUBRIC_FILENAME``.
RUBRIC_RESULTS_FILENAME = "results-rubric-score.json"


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
    # Evidence-bearing == carries a STRONG contradiction naming a true impostor
    # (audit P0 / CAL-2), the SAME predicate the per-game R7 term scores —
    # raw n_contradictions>0 counted weak below-gate flags that eject nobody.
    evid_mtgs = sum(
        1
        for g in games
        for m in g["meetings"]
        if _meeting_has_strong_impostor_flag(g["roles"], m)
    )
    ft = agg["free_text_length_chars"]
    bf = agg["ballot_follows_chain"]
    rows.append(
        (
            "R7 strong-evidence meeting share",
            _pct(evid_mtgs, mtgs),
            "UP (a STRONG flag names a true impostor; weak alibi_vs_sighting excluded)",
        )
    )
    rows.append(
        (
            "R7 free_text medians (open/reply/optin)",
            f"{ft['opening']['median']}/{ft['reply']['median']}/{ft['opt_in']['median']} (max {ft['opening']['max']})",
            "stable ~225; no catastrophic tail",
        )
    )
    # ballot-follows-chain is a DIAGNOSTIC ONLY — dropped from any fitness
    # aggregate (audit P1 / RB-1). ~65% of non-skip ballots are null-reason BY
    # DESIGN (vote_ballot.j2 instructs null when the vote rests on own
    # observation), so it caps near 35% and measures a coherence the meeting
    # architecture deliberately suppresses — never an "UP-is-good" target.
    rows.append(
        (
            "ballot-follows-chain [DIAGNOSTIC]",
            _pct(bf["follows_chain"], bf["non_skip_ballots"]),
            "DIAGNOSTIC only — not a fitness term (null-reason is by design)",
        )
    )

    return rows


def _win_shape(reason: str, ejected_imps: int, n_mtg: int) -> str:
    """Coarse per-game win SHAPE for R5 diversity (decouples 'interesting' from W/L)."""
    if reason == "CREWMATE_EJECT":
        return "eject-decided"
    # IMPOSTOR_SABOTAGE gets its OWN shape before the startswith('IMPOSTOR')
    # catch-all (RUB-CAL-4 / P2): a sabotage-pressure win is a distinct R5 /
    # MAP-Elites axis the catch-all otherwise folds into "impostor-win", so it
    # could never register as its own diversity shape.
    if reason == "IMPOSTOR_SABOTAGE":
        return "sabotage-win"
    if reason.startswith("IMPOSTOR"):
        return "impostor-win"
    if reason == "CREWMATE_TASKS":
        if n_mtg == 0:
            return "stopwatch-no-meeting"
        return "stopwatch-some-eject" if ejected_imps else "stopwatch-no-eject"
    return reason or "other"


def _active_deflection_counts(g: dict[str, Any]) -> tuple[int, int, bool]:
    """Per-game ``(active_survivals, effective_deflections, any_accused)``.

    Reproduces ``eval.meeting_quality.compute_effective_deflection``'s
    ACTIVE-DEFLECTED split over the SAME data that function consumes — the
    per-turn :class:`~meetings.schemas.AccusationClaim`s, materialized in the
    facts JSON as each meeting's ``accusations`` rows — plus the firewalled
    role. For every (meeting, true impostor verbally accused by ANOTHER
    speaker) the impostor SURVIVES unless that meeting ejected them; a survival
    is ACTIVE iff the impostor counter-accused some player other than itself
    this meeting, and EFFECTIVE iff the strict unique eject-plurality
    (``_strict_eject_plurality``: ``None`` on a tie / all-SKIP, recovered here
    from the facts ``plurality_target`` gated on a positive ``plurality_margin``)
    landed OFF the impostor — i.e. the counter-accusation moved the table.

    This is a facts-resident derivation rather than an import of
    ``compute_effective_deflection`` itself because that function takes
    reconstructed ``GameReport`` objects, while this scorer reads only the facts
    JSON (and the committed ``regen_for_set(_facts(), tmp_path)`` contract ships
    no report on disk; ``refresh_samples.sh`` also runs this module as a script
    file with no repo root on ``sys.path``, so a module-level ``eval`` import
    would break the canonical regen). It is validated to reproduce that
    function's aggregate EXACTLY on the committed 9p2i set (active 34,
    effective 10, skip-saved 24), so the two cannot drift on what
    ACTIVE-DEFLECTED means.
    """

    roles = g["roles"]
    active = 0
    effective = 0
    any_accused = False
    for m in g["meetings"]:
        accusations = m.get("accusations", [])
        accused_impostors = {
            a["accused"]
            for a in accusations
            if roles.get(a["accused"]) == "IMPOSTOR" and a["accused"] != a["speaker"]
        }
        if not accused_impostors:
            continue
        any_accused = True
        # ``ejected_player_id`` is set IFF a player was ejected this meeting, so
        # ``ejected == impostor`` IS "caught here" without depending on a
        # separate ``outcome`` field — a meeting that carries the id but omits
        # ``outcome`` (older/minimal facts) would otherwise mis-score a caught
        # impostor as an active survival.
        ejected = m.get("ejected_player_id")
        for impostor in accused_impostors:
            if ejected == impostor:
                continue  # caught here — not a survival
            counter_targets = {
                a["accused"]
                for a in accusations
                if a["speaker"] == impostor and a["accused"] != impostor
            }
            if not counter_targets:
                continue  # passive / clock survival — no active deflection
            active += 1
            # An ACTIVE survival's EFFECTIVE-vs-skip-saved split needs the strict
            # unique eject-plurality. Require the fields rather than defaulting a
            # missing margin to 0 (which would silently MISCLASSIFY a real
            # deflection as skip-saved on a stale facts JSON that predates them).
            if "plurality_target" not in m or "plurality_margin" not in m:
                raise ValueError(
                    "meeting with an active impostor survival is missing "
                    "plurality_target / plurality_margin — re-run the "
                    "gameplay-facts extractor"
                )
            # A zero margin is a tie / all-SKIP, which the frozen §5.2 tally
            # resolves to SKIP — so it moved the plurality nowhere (mirrors
            # _strict_eject_plurality).
            plurality = m["plurality_target"] if m["plurality_margin"] > 0 else None
            if plurality is not None and plurality != impostor:
                effective += 1  # the counter-accusation MOVED the plurality off
    return active, effective, any_accused


def _meeting_has_strong_impostor_flag(
    roles: dict[str, Any], meeting: dict[str, Any]
) -> bool:
    """Whether a meeting carries a STRONG contradiction naming a true impostor.

    Reuses the extractor's ``is_weak_contradiction`` classification — each
    recorded contradiction in ``contradictions_by_subject`` already carries the
    ``strong`` bit the extractor stamped via that one-home predicate, so this
    never re-runs a parallel weak/strong check that could drift — and the
    firewalled role. Per-meeting credit is boolean (capped at 1): a meeting
    counts iff SOME subject is a true impostor with at least one STRONG
    (non-weak) flag. The all-weak ``alibi_vs_sighting`` baseline (every flag
    below the §4.6 gate, ejects nobody) scores 0.

    Missing classification FAILS LOUD rather than reading as zero strong
    evidence (AGENTS.md "no silent fallbacks"), so a stale extractor run can
    never masquerade as a valid all-weak baseline and silently zero the
    20%-weight R7 axis: an ABSENT ``contradictions_by_subject`` map on a meeting
    that nonetheless recorded ``n_contradictions > 0``, or a contradiction row
    that omits the ``strong`` bit, both raise.
    """

    by_subject = meeting.get("contradictions_by_subject")
    if by_subject is None:
        if meeting.get("n_contradictions", 0) > 0:
            raise ValueError(
                "meeting recorded n_contradictions > 0 but has no "
                "contradictions_by_subject classification map — re-run the "
                "gameplay-facts extractor"
            )
        by_subject = {}
    for subject, classifications in by_subject.items():
        if roles.get(subject) != "IMPOSTOR":
            continue
        for c in classifications:
            if "strong" not in c:
                raise ValueError(
                    "contradiction row is missing the 'strong' classification "
                    "bit (re-run the extractor's is_weak_contradiction pass); "
                    f"row keys = {sorted(c)}"
                )
            if c["strong"]:
                return True
    return False


def _strong_evidence_meeting_share(g: dict[str, Any]) -> float:
    """Share of a game's meetings that are evidence-bearing (R7)."""

    meetings = g["meetings"]
    if not meetings:
        return 0.0
    roles = g["roles"]
    evidence_bearing = sum(
        1 for m in meetings if _meeting_has_strong_impostor_flag(roles, m)
    )
    return evidence_bearing / len(meetings)


def _suspicion_rose_onto_impostor(
    g: dict[str, Any], traj_by_key: dict[tuple[Any, Any], dict[str, Any]]
) -> bool:
    """Whether the game ejected a true impostor on a RISING cross-meeting arc.

    Sources the extractor's already-computed ``accumulator_trajectories`` (the
    per-candidate across-meeting rendered-suspicion series) keyed by
    ``(seed, player)`` + the firewalled role. True iff SOME ejected player is a
    true impostor whose trajectory shows the ejection landing at a candidate
    meeting strictly LATER than its first (``>= 1`` prior meeting — a genuine
    cross-meeting arc, not a meeting-0 conviction) with rendered suspicion at
    the ejection strictly ABOVE the first meeting's. A flagless meeting-0
    conviction of an innocent (the seed-15 railroad) lands on a crewmate and so
    can never satisfy this — the railroad R4 forbids no longer scores R3.
    """

    seed = g.get("seed")
    roles = g["roles"]
    for m in g["meetings"]:
        ejected = m.get("ejected_player_id")
        if not ejected or roles.get(ejected) != "IMPOSTOR":
            continue
        record = traj_by_key.get((seed, ejected))
        if record is None:
            continue
        sequence = record.get("sequence", [])
        eject_points = [i for i, pt in enumerate(sequence) if pt.get("ejected_here")]
        if not eject_points:
            continue
        j = eject_points[0]
        if (
            j >= 1
            and sequence[j]["rendered_suspicion"] > sequence[0]["rendered_suspicion"]
        ):
            return True
    return False


def _game_interestingness(
    g: dict[str, Any], traj_by_key: dict[tuple[Any, Any], dict[str, Any]]
) -> dict[str, Any]:
    """Per-game interestingness from the per-game-computable rubric items (R1/R2/R3/R7).

    The score is deliberately INDEPENDENT of who won the binary game — the lab
    proved the win split is "purchasable wholesale", so 'interesting' is scored
    from whether DEDUCTION decided (R1), DECEPTION worked (R2), suspicion built
    across meetings (R3), and the story was legible (R7). R5 (win-shape diversity)
    is a set-level property, summarized in :func:`interestingness`. R1/R2/R3/R7
    are emitted as SEPARATE terms (not only the collapsed scalar) so Phase-C can
    read them as multi-objective fitness axes.

    The grounding audit (``experiments/lab/report-grounding-audit.md``) verified
    THREE perverse gradients in the pre-repair terms; each is closed here:

    * **R2** no longer pays for passive survival (it banked 0.6 for a
      lose-while-accused-alive game, anti-correlating R2 with the total at
      Pearson −0.281). It is now gated on an ACTIVE-DEFLECTION event
      (:func:`_active_deflection_counts`); passive / clock survival scores ≤ 0.2.
    * **R3** no longer rewards the railroad R4 forbids (it gave full credit to a
      flagless meeting-0 conviction of an innocent). It now requires a
      cross-meeting suspicion RISE that LANDS on a true impostor
      (:func:`_suspicion_rose_onto_impostor`).
    * **R7** no longer counts raw flag presence (all baseline flags are WEAK
      ``alibi_vs_sighting``, below the §4.6 gate). It now counts only meetings
      bearing a STRONG contradiction naming a true impostor
      (:func:`_strong_evidence_meeting_share`).

    R1's ``CREWMATE_EJECT`` definition is SOUND and kept byte-identical.
    """
    roles = g["roles"]
    meetings = g["meetings"]
    n_mtg = len(meetings)
    reason = g.get("reason") or ""

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
    # SOUND term (audit RB-7/G8): CREWMATE_EJECT fires iff alive_impostors == 0,
    # and crew cannot kill impostors, so it faithfully means deduction cleared
    # the board. Kept BYTE-IDENTICAL.
    if reason == "CREWMATE_EJECT":
        r1 = 1.0
    elif ejected_imp_mtgs >= 1:
        r1 = 0.5  # caught some, but the task clock decided
    else:
        r1 = 0.0  # pure stopwatch / kill-gifted — deduction was inert

    # R2 deception: credit ONLY an EFFECTIVE deflection (audit P0 / G3). The
    # codebase's own eval.meeting_quality.EffectiveDeflectionReport is explicit
    # that an active counter-accusation which survived because the table
    # SKIP-saved is "survival, not deflection" (anchor on the EFFECTIVE subcount,
    # NOT the raw active count), so skip-saved active survival stays in the
    # passive band (0.2) and is never elevated to its own tier. ``_active`` is
    # kept in the returned split for fidelity but is not itself scored.
    _active, effective_deflections, any_accused = _active_deflection_counts(g)
    if effective_deflections >= 1:
        r2 = 1.0  # a counter-accusation moved the eject-plurality off a true impostor
    elif any_accused:
        r2 = 0.2  # accused yet no EFFECTIVE deflection (passive / skip-saved / caught)
    else:
        r2 = 0.0  # deception never tested (no true impostor was accused)

    # R3 arcs: a cross-meeting suspicion RISE that LANDED on a true impostor
    # (audit P0 / G2). The old "0.5 for >=2 meetings + 0.5 for any flagless
    # carry-eject" rewarded exactly the railroad R4 forbids; this credits only a
    # genuine accumulator arc onto a real impostor.
    r3 = 1.0 if _suspicion_rose_onto_impostor(g, traj_by_key) else 0.0

    # R7 legibility: share of meetings bearing a STRONG contradiction naming a
    # true impostor (audit P0 / CAL-2). Raw n_contradictions>0 counted weak
    # below-gate flags that eject nobody; this counts only decision-grade signal.
    r7 = _strong_evidence_meeting_share(g)

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


def _accumulator_trajectory_index(
    facts: dict[str, Any],
) -> dict[tuple[Any, Any], dict[str, Any]]:
    """Index the extractor's ``accumulator_trajectories`` by ``(seed, player)``.

    The R3 arc source (audit P0). The records live under the facts JSON's
    ``aggregates.wave1_contract_inputs.accumulator_trajectories.records`` — read
    here, never re-derived — and are keyed by ``(seed, player)`` so a per-game
    score can look up an ejected subject's across-meeting suspicion series.

    A REAL extractor facts JSON always ships the aggregate; if its
    ``aggregates`` block is present but the trajectories path is missing or
    malformed (a stale / partial extractor run), this FAILS LOUD rather than
    silently zeroing the 20%-weight R3 axis on a fresh-stamped artifact
    (AGENTS.md "no silent fallbacks"). A facts dict carrying NO ``aggregates``
    block at all (the regen-plumbing fixture, which scores no real R3) yields an
    empty index — there is simply no arc source to index.
    """

    aggregates = facts.get("aggregates")
    if aggregates is None:
        return {}
    try:
        records = aggregates["wave1_contract_inputs"]["accumulator_trajectories"][
            "records"
        ]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "facts JSON carries an 'aggregates' block but is missing "
            "'aggregates.wave1_contract_inputs.accumulator_trajectories.records' "
            "(the R3 arc source) — refusing to silently score R3=0; re-run the "
            "gameplay-facts extractor"
        ) from exc
    if not isinstance(records, list):
        raise ValueError(
            "accumulator_trajectories.records must be a list, got "
            f"{type(records).__name__}"
        )
    return {(r["seed"], r["player"]): r for r in records}


def interestingness(facts: dict[str, Any]) -> dict[str, Any]:
    """Per-game interestingness scores + the set-level R5 win-shape diversity."""
    games = facts["games"]
    traj_by_key = _accumulator_trajectory_index(facts)
    per = sorted(
        (_game_interestingness(g, traj_by_key) for g in games),
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


# The ``MANIFEST.md`` git_sha column index once the leading empty cell (from the
# leading ``|``) is included — kept in lockstep with
# ``api.replay_loader._MANIFEST_GIT_SHA_COLUMN`` so the producer stamps the exact
# sha the loader's staleness guard reads back.
_MANIFEST_GIT_SHA_COLUMN = 5


def _set_manifest_sha(set_dir: Path) -> str | None:
    """The single distinct git sha across a set's ``MANIFEST.md`` data rows.

    Mirrors ``api.replay_loader._manifest_git_sha``: the rubric stamps the
    version of the replay SET it was scored from (read here, cwd-independent via
    the absolute ``set_dir``), so the loader's freshness comparison is
    "do the served replays still match what the rubric was scored against",
    NOT "what code commit happened to run the scorer". Returns ``None`` when the
    manifest is absent or carries more than one distinct sha.
    """

    try:
        text = (set_dir / "MANIFEST.md").read_text(encoding="utf-8")
    except OSError:
        return None
    shas: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) <= _MANIFEST_GIT_SHA_COLUMN:
            continue
        if not cells[1].lstrip("-").isdigit():
            continue  # header / separator row
        sha = cells[_MANIFEST_GIT_SHA_COLUMN]
        if sha:
            shas.add(sha)
    return next(iter(shas)) if len(shas) == 1 else None


def regen_for_set(
    facts: dict[str, Any], set_dir: Path, *, git_head: str | None = None
) -> Path:
    """Re-run the scorer and co-locate ``results-rubric-score.json`` into a set.

    The per-set rubric PRODUCER (Task 12.2; DESIGN.md §3.1, §7). Scores ``facts``
    (the gameplay-facts extractor's output) into the served interestingness
    surface and writes it into ``set_dir`` so ``/eval/rubric`` can serve it.

    The result is stamped with the version of the replay SET it was scored from
    — the set's ``MANIFEST.md`` git sha — NOT the scoring code commit. That makes
    the loader's staleness guard meaningful: it reads FRESH while the on-disk
    replays match what the rubric scored, and STALE only once the set is
    re-recorded (manifest sha bumped) without a re-score. (An explicit
    ``git_head`` overrides — used by tests; ``facts['git_head']`` is the last
    fallback when the set ships no manifest.) Stamping the scoring ``HEAD`` here
    instead would false-positive as stale whenever scoring ran at a later commit
    than recording, and would depend on the caller's cwd — both avoided.

    Writes the SERVED subset (``seedset`` / ``git_head`` / ``interestingness``);
    the human-readable R1–R7 ``rows`` table stays the lab-local artifact
    :func:`main` writes. Wired into the refresh / re-record path
    (``scripts/refresh_samples.sh``) so the happy path stays fresh rather than
    only banner-guarded when stale.
    """

    head = (
        git_head
        if git_head is not None
        else (_set_manifest_sha(set_dir) or facts.get("git_head"))
    )
    out = {
        "seedset": facts.get("seedset"),
        "git_head": head,
        "interestingness": interestingness(facts),
    }
    dest = Path(set_dir) / RUBRIC_RESULTS_FILENAME
    dest.write_text(json.dumps(out, indent=2))
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score rubric R1-R7 over a facts JSON."
    )
    parser.add_argument("facts_json", help="gameplay-facts extractor output")
    parser.add_argument(
        "--set-dir",
        default=None,
        help=(
            "also co-locate results-rubric-score.json into this served replay "
            "set dir, stamped with git HEAD (the per-set regen producer for "
            "/eval/rubric)"
        ),
    )
    args = parser.parse_args()
    facts = json.loads(Path(args.facts_json).read_text())
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
    print(
        f"R5 win shapes (>=10% share count = {inter['r5_shapes_over_10pct']}): "
        f"{json.dumps(inter['win_shapes'])}"
    )
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

    # Stamp the SET manifest sha (the replay version scored), NOT the scoring
    # HEAD (audit RUB-CAL-5): the pre-repair lab-local write stamped
    # ``facts['git_head']`` (a docs-descendant scoring commit), so the
    # loader's freshness guard would have read the lab artifact as scored at a
    # different version than the served copy. Resolve the set dir from
    # ``--set-dir`` or the facts JSON's own ``sample_dir`` and read the same
    # manifest sha the served copy carries, mirroring :func:`regen_for_set`.
    sample_dir = facts.get("sample_dir")
    set_dir = (
        Path(args.set_dir)
        if args.set_dir is not None
        else (Path(sample_dir) if sample_dir else None)
    )
    lab_head = (
        _set_manifest_sha(set_dir) if set_dir is not None else None
    ) or facts.get("git_head")
    out = {
        "seedset": label,
        "git_head": lab_head,
        "rows": [{"item": i, "value": v, "desired": d} for i, v, d in rows],
        "interestingness": inter,
    }
    Path("experiments/lab/results-rubric-score.json").write_text(
        json.dumps(out, indent=2)
    )
    print(f"\nwrote experiments/lab/results-rubric-score.json (set sha {lab_head})")

    if args.set_dir is not None:
        dest = regen_for_set(facts, Path(args.set_dir))
        print(f"co-located per-set rubric (git_head stamped): {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
