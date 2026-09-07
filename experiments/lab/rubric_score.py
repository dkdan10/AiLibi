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
import hashlib
import json
import math
import statistics
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from orchestrator.recording_fingerprint import recording_fingerprint  # noqa: E402

# Filename the per-set rubric is co-located under, inside a served replay set
# dir, so ``api.replay_loader.ReplayLoader.rubric`` can serve it (Task 12.2;
# DESIGN.md §3.1, §7). Kept identical to ``api.replay_loader._RUBRIC_FILENAME``.
RUBRIC_RESULTS_FILENAME = "results-rubric-score.json"

# Filename for the geomean interestingness validation artifact (Task 13.15) — the
# held-out referee's D1-D4 breakdown + the report-rubric-design.md §6 validation,
# mirroring ``results-rubric-score.json``. It is a LAB-LOCAL record, NOT served by
# the DTO: it carries the D1-D4 detail the ``extra="forbid"`` ``RubricGameView``
# (``api/schemas.py``) would reject, so it lives outside the served per_game rows.
GEOMEAN_RESULTS_FILENAME = "results-rubric-geomean.json"

# --- Geomean interestingness composition (Task 13.15; report-rubric-design.md §3) ---
# The per-game score is the epsilon-floored, weighted GEOMETRIC mean of the four
# contest dimensions D1-D4 (replacing the old additive R1-R7 sum): one dead
# dimension SINKS the score, so a live term can no longer mask a dead one (the
# additive sum let a live R2 mask a dead R1 — it ranked the seed-0/16 stopwatch
# wins ABOVE every eject-decided game). D1-D4 route AROUND the dead R7 (it is NOT a
# geomean input), so the score lands independently of R7 and does NOT collapse to 0
# on the committed R7=0 set. The weights / epsilon / scale are implementer
# DECISIONS (the design is a narrative, not a numeric spec); see the rationale +
# the achieved ranking in report-rubric-design.md "## Decisions".
_GEOMEAN_WEIGHTS = {"d1": 0.40, "d2": 0.25, "d3": 0.15, "d4": 0.20}
_GEOMEAN_EPSILON = 1e-3
# The §4.6 vote gate (DESIGN.md §4.6): a CREWMATE ejected with rendered suspicion
# below it (the gate bypassed) is a RAILROAD floor; ejected above it is an honest
# (mistaken) deduction, not a railroad.
_SKIP_SUSPICION_THRESHOLD = 0.60
# Suspicion-separation [0,1] normalizer: a per-meeting mean-impostor-minus-mean-crew
# rendered suspicion of >= this maps to 1.0 (committed max ~0.42; a clean +0.30
# separation is a decisively truth-tracking table).
_D2_SEPARATION_SCALE = 0.30


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


def _geomean_weighted(dims: dict[str, float]) -> float:
    """Epsilon-floored weighted geometric mean of the contest dimensions D1-D4.

    ``exp(sum(w_n * ln(max(d_n, eps))))`` with ``sum(w_n) == 1`` (a true weighted
    geomean in ``[eps, 1]``). The epsilon (``_GEOMEAN_EPSILON``) floors each term
    so a single ZERO dimension SINKS the score (the multiplicative "requires
    contest" property; report-rubric-design.md §3 Composition) WITHOUT driving
    ``ln(0)`` to ``-inf`` / NaN. Unlike the additive R1-R7 sum, a live dimension
    cannot mask a dead one.
    """
    total = math.fsum(
        weight * math.log(max(dims[key], _GEOMEAN_EPSILON))
        for key, weight in _GEOMEAN_WEIGHTS.items()
    )
    return math.exp(total)


def _d1_resolution(g: dict[str, Any]) -> float:
    """D1 — did PLAY decide the board, not the clock? (report-rubric-design.md §3 D1)

    Scores the RESOLUTION mechanism, decoupled from who won: a crew DEDUCTION win
    (``CREWMATE_EJECT`` — both impostors ejected via meetings) is the canonical
    "play decided" (1.0); a CONTESTED impostor win (``IMPOSTOR_PARITY`` /
    ``IMPOSTOR_SABOTAGE`` with >= 1 meeting — the crew tried and failed to deduce)
    also scores (0.6); a game where some impostor was ejected but the task clock
    decided scores partial (0.3); a pure stopwatch or a pre-meeting stomp scores 0.
    Anti-perverse: passivity and the clock score 0, and BOTH sides can score on
    play (it does not reward winning — see the §6 Pearson check).
    """
    reason = g.get("reason") or ""
    n_mtg = len(g["meetings"])
    ejected_imp_mtgs = sum(
        1 for m in g["meetings"] if m.get("ejected_role") == "IMPOSTOR"
    )
    if reason == "CREWMATE_EJECT":
        return 1.0
    if reason in ("IMPOSTOR_PARITY", "IMPOSTOR_SABOTAGE") and n_mtg >= 1:
        return 0.6
    if ejected_imp_mtgs >= 1:
        return 0.3
    return 0.0


def _meeting_suspicion_separation(
    meeting: dict[str, Any], roles: dict[str, Any]
) -> float | None:
    """Mean rendered-suspicion(true impostors) − mean(crew) for ONE meeting.

    Reads the meeting's ``suspicion_graph_by_voter`` (each living voter's §6.6
    rendered suspicion of every other player) + the firewalled roles, partitions
    every ``voter -> target`` row by the TARGET's true role (excluding self rows),
    and returns impostor-mean minus crew-mean. ``None`` when either side has no
    rows (no separation is computable). This is the D2 truth-tracking primitive:
    a positive value means the table suspects impostors MORE than crew. The raw
    suspicion graph exists in the extractor facts (Task 13.15 specifies this
    formula; it does not re-extract).
    """
    imp: list[float] = []
    crew: list[float] = []
    for voter, graph in (meeting.get("suspicion_graph_by_voter") or {}).items():
        for target, susp in graph.items():
            if target == voter:
                continue
            role = roles.get(target)
            if role == "IMPOSTOR":
                imp.append(susp)
            elif role == "CREWMATE":
                crew.append(susp)
    if not imp or not crew:
        return None
    return (math.fsum(imp) / len(imp)) - (math.fsum(crew) / len(crew))


def _subject_has_observation_backed_accusation(rec: dict[str, Any] | None) -> bool:
    """A testimony record carries an OBSERVATION-BACKED ACCUSATION of its subject.

    The shared "observation-backed accusation" predicate (report-rubric-design.md
    §3 D2 + the railroad floor): an ``accusation`` turn naming the subject whose
    accuser ALSO logged a first-hand sighting (``observation_backed``). A
    sighting-only turn (``vehicle == "sighting"``) or a bare free-text mention does
    NOT count — only a *backed accusation* does, so an enriched meeting's mere
    sightings cannot masquerade as evidence-backed convictions.
    """
    return rec is not None and any(
        turn.get("observation_backed") and turn.get("vehicle") == "accusation"
        for turn in rec.get("testimony_turns", [])
    )


def _observation_backed_impostors(meeting: dict[str, Any]) -> set[str]:
    """True impostors named by an OBSERVATION-BACKED ACCUSATION this meeting.

    The D2 conversion DENOMINATOR: a true impostor against whom some turn carried
    an observation-backed *accusation* (:func:`_subject_has_observation_backed_accusation`),
    never a sighting-only mention or a flagless vibe.
    """
    return {
        rec["subject"]
        for rec in meeting.get("testimony_records", [])
        if rec.get("subject_role") == "IMPOSTOR"
        and _subject_has_observation_backed_accusation(rec)
    }


def _d2_crew_deduction(g: dict[str, Any]) -> tuple[float, float, float]:
    """D2 — does collective suspicion track truth AND convert? (§3 D2)

    Returns ``(d2, separation_norm, conversion)``. Blends two REACHABLE signals
    (the suspicion graph is ALWAYS populated — unlike R7's dead strong-flag
    requirement, which is why D2 routes around R7):

    * **separation** — the game-mean of :func:`_meeting_suspicion_separation`,
      normalized to [0,1] by ``_D2_SEPARATION_SCALE`` and clamped at 0: a NEGATIVE
      separation (a railroad raising suspicion on an INNOCENT lowers
      impostor-over-crew separation) is penalized, never rewarded.
    * **conversion** — of every ``(meeting, observation-backed-accused true
      impostor)`` pair, the fraction the meeting actually EJECTED. Correct
      conviction counts only when observation-backed, never flagless.

    ``d2 = 0.5 * separation_norm + 0.5 * conversion``.
    """
    roles = g["roles"]
    separations = [
        sep
        for m in g["meetings"]
        if (sep := _meeting_suspicion_separation(m, roles)) is not None
    ]
    separation_norm = (
        max(
            0.0,
            min(
                1.0, (math.fsum(separations) / len(separations)) / _D2_SEPARATION_SCALE
            ),
        )
        if separations
        else 0.0
    )
    converted = attempted = 0
    for m in g["meetings"]:
        ejected = m.get("ejected_player_id")
        for subject in _observation_backed_impostors(m):
            attempted += 1
            if ejected == subject:
                converted += 1
    conversion = (converted / attempted) if attempted else 0.0
    return 0.5 * separation_norm + 0.5 * conversion, separation_norm, conversion


def _d3_impostor_craft(g: dict[str, Any]) -> float:
    """D3 — is deception + agency load-bearing? (§3 D3)

    Anchored on the repaired-R2 EFFECTIVE-deflection subcount
    (:func:`_active_deflection_counts`): 1.0 when a counter-accusation MOVED the
    eject-plurality off a true impostor; 0.2 when a true impostor was accused but
    not effectively deflected (passive / skip-saved / caught); 0.0 when no true
    impostor was ever accused. Anti-perverse (the R2 trap): survival counts ONLY
    when accused — a passive impostor that is simply never accused scores 0. This
    is the SAME value the per-game ``r2_deception`` term reports (one source, no
    drift). Evasion / tool-use / steering (also §3 D3) fold in at the held
    re-record's richer data; the committed-set anchor is effective deflection.
    """
    _active, effective_deflections, any_accused = _active_deflection_counts(g)
    if effective_deflections >= 1:
        return 1.0
    if any_accused:
        return 0.2
    return 0.0


def _game_has_swing(
    g: dict[str, Any], traj_by_key: dict[tuple[Any, Any], dict[str, Any]]
) -> bool:
    """The D4 SWING term: a knife-edge eject + REAL cross-meeting suspicion movement.

    Task 13.15: ``plurality_margin == 1`` (the table swung on a single ballot) AND
    cross-meeting suspicion movement. Movement is read from the ejected subject's
    accumulator trajectory (the same source as the arc), NOT a bare ``n_meetings >
    1`` count (which the separate ``contest`` term already rewards): the eject must
    land at a trajectory point ``j >= 1`` (the subject was a candidate in >= 1
    PRIOR meeting) whose rendered suspicion DIFFERS from its first appearance — a
    genuine cross-meeting build, not a one-shot first-appearance knife-edge eject
    or a flat sustained-high eject.
    """
    seed = g.get("seed")
    for m in g["meetings"]:
        if not (m.get("ejected_player_id") and m.get("plurality_margin") == 1):
            continue
        record = traj_by_key.get((seed, m["ejected_player_id"]))
        if record is None:
            continue
        sequence = record.get("sequence", [])
        eject_points = [i for i, pt in enumerate(sequence) if pt.get("ejected_here")]
        if not eject_points:
            continue
        j = eject_points[0]
        if (
            j >= 1
            and abs(
                sequence[j]["rendered_suspicion"] - sequence[0]["rendered_suspicion"]
            )
            > 1e-9
        ):
            return True
    return False


def _d4_arc(
    g: dict[str, Any], traj_by_key: dict[tuple[Any, Any], dict[str, Any]]
) -> tuple[float, float, float, float]:
    """D4 — a CONTESTED build, not a one-shot. (§3 D4)

    Returns ``(d4, arc, swing, contest)``. Rewards suspicion MOVEMENT and a
    contested chain, not raw length:

    * **arc** — a cross-meeting suspicion RISE that landed on a true impostor
      (:func:`_suspicion_rose_onto_impostor`; the same signal as ``r3_arcs``).
    * **swing** — the Task-13.15 knife-edge term (:func:`_game_has_swing`).
    * **contest** — a multi-meeting build, ``min(1, (n_meetings - 1) / 2)`` (0 for
      one meeting, 0.5 for two, 1.0 for three+) — graded and CAPPED, so raw
      stalling is not rewarded.

    ``d4 = 0.45 * arc + 0.35 * swing + 0.20 * contest``.
    """
    n_mtg = len(g["meetings"])
    arc = 1.0 if _suspicion_rose_onto_impostor(g, traj_by_key) else 0.0
    swing = 1.0 if _game_has_swing(g, traj_by_key) else 0.0
    contest = min(1.0, max(0, n_mtg - 1) / 2.0)
    return 0.45 * arc + 0.35 * swing + 0.20 * contest, arc, swing, contest


def _facts_integrity_ok(facts: dict[str, Any]) -> bool:
    """Whether the extractor's self-checks all passed (no determinism/leak breach).

    The firewall/determinism FLOOR input (report-rubric-design.md §3). Reads the
    extractor's ``self_checks`` list (each entry ends ': OK' or ': FAIL'); any
    'FAIL' is a breach -> every game is floored to 0. A real (aggregates-bearing)
    facts JSON that OMITS ``self_checks`` (a stale / partial extractor run) FAILS
    LOUD rather than certifying integrity by default — the floor depends on these
    checks to detect a state-hash / leak breach, so a missing surface is not
    "clean" (AGENTS.md "no silent fallbacks"; mirrors
    :func:`_accumulator_trajectory_index`). Only the regen-plumbing fixture (NO
    aggregates block, i.e. no real games to score) reads OK on absence. A
    present-but-malformed value also FAILS LOUD.
    """
    checks = facts.get("self_checks")
    if checks is None:
        if facts.get("aggregates") is not None:
            raise ValueError(
                "aggregates-bearing facts JSON is missing 'self_checks' (the "
                "firewall/determinism floor input) — refusing to certify "
                "integrity by default; re-run the gameplay-facts extractor"
            )
        return True
    if not isinstance(checks, list):
        raise ValueError("facts 'self_checks' must be a list of check strings")
    if not all(isinstance(c, str) for c in checks):
        raise ValueError(
            "facts 'self_checks' contains a non-string entry (malformed) — "
            "refusing to certify integrity; re-run the gameplay-facts extractor"
        )
    return not any("FAIL" in c for c in checks)


def _floor_multiplier(g: dict[str, Any], *, integrity_ok: bool) -> float:
    """The hard integrity floors (report-rubric-design.md §3 "Hard floors").

    Returns 0.0 (sinks the WHOLE game) on ANY integrity breach, else 1.0. These
    are punish-only gates, never tradeable dimensions:

    * **friendly-fire** — an impostor killed a fellow impostor (engine-forbidden;
      the floor guards a regression).
    * **railroad ejection** — a CREWMATE ejected as a railroad
      (:func:`_is_railroad_ejection`).
    * **firewall / determinism breach** — ``integrity_ok`` is False (a failing
      extractor self-check: a state-hash mismatch or a leak).
    """
    if not integrity_ok:
        return 0.0
    if any(k.get("victim_role") == "IMPOSTOR" for k in g.get("kills", [])):
        return 0.0
    for m in g["meetings"]:
        if (
            m.get("ejected_player_id")
            and m.get("ejected_role") == "CREWMATE"
            and _is_railroad_ejection(m)
        ):
            return 0.0
    return 1.0


def _is_railroad_ejection(meeting: dict[str, Any]) -> bool:
    """Whether a CREWMATE ejection is a railroad (report-rubric-design.md §3 floor).

    'An innocent ejected with no observation-backed suspicion' has two structural
    forms, EITHER of which floors the game:

    * **gate-bypass** — the ejected crewmate's rendered suspicion among the
      ejectors is below the §4.6 gate (``_SKIP_SUSPICION_THRESHOLD``) or absent
      (the deterministic anti-railroad tally was structurally bypassed).
    * **evidence-free conviction** — NO observation-backed accusation names the
      ejected (:func:`_subject_has_observation_backed_accusation`) AND no
      contradiction flag names them: the eject rests on NO legible meeting evidence
      at all (an unarticulated conviction on private vibes).

    A crewmate ejected ABOVE the gate WITH an observation-backed accusation or a
    contradiction flag is an honest (mistaken) deduction, NOT a railroad — it is
    scored low by D2 (it lowers separation / conversion), never floored.
    """
    among = meeting.get("ejected_rendered_suspicion_among_ejectors")
    if among is None or among < _SKIP_SUSPICION_THRESHOLD:
        return True
    ejected = meeting["ejected_player_id"]
    rec = next(
        (r for r in meeting.get("testimony_records", []) if r["subject"] == ejected),
        None,
    )
    has_flag = ejected in (meeting.get("contradictions_by_subject") or {})
    return not _subject_has_observation_backed_accusation(rec) and not has_flag


def _contest_dimensions(
    g: dict[str, Any],
    traj_by_key: dict[tuple[Any, Any], dict[str, Any]],
    *,
    integrity_ok: bool,
) -> dict[str, Any]:
    """The four [0,1] contest dimensions D1-D4 + the floor + the composed score.

    The SINGLE source for the geomean composition (report-rubric-design.md §3):
    ``score = 100 * floor_multiplier * geomean_weighted(D1, D2, D3, D4)``. Both
    the served per_game ``score`` and the lab geomean artifact route through here,
    so they can never drift.
    """
    d1 = _d1_resolution(g)
    d2, d2_sep, d2_conv = _d2_crew_deduction(g)
    d3 = _d3_impostor_craft(g)
    d4, d4_arc, d4_swing, d4_contest = _d4_arc(g, traj_by_key)
    floor = _floor_multiplier(g, integrity_ok=integrity_ok)
    geomean = _geomean_weighted({"d1": d1, "d2": d2, "d3": d3, "d4": d4})
    return {
        "d1_resolution": d1,
        "d2_deduction": d2,
        "d3_craft": d3,
        "d4_arc": d4,
        "d2_separation_norm": d2_sep,
        "d2_conversion": d2_conv,
        "d4_arc_term": d4_arc,
        "d4_swing_term": d4_swing,
        "d4_contest_term": d4_contest,
        "floor_multiplier": floor,
        "geomean": geomean,
        "score": 100.0 * floor * geomean,
    }


def _game_interestingness(
    g: dict[str, Any],
    traj_by_key: dict[tuple[Any, Any], dict[str, Any]],
    *,
    integrity_ok: bool,
) -> dict[str, Any]:
    """Per-game interestingness — the geomean of D1-D4, with the r1-r7 axes kept.

    The ``score`` is the epsilon-floored, weighted GEOMETRIC mean of the four
    contest dimensions (``floor_multiplier * geomean_weighted(D1, D2, D3, D4)``,
    Task 13.15; report-rubric-design.md §3), replacing the old additive R1-R7 sum:
    one dead dimension SINKS the score, so a live term can no longer mask a dead
    one. D1-D4 route AROUND the dead R7 (it is NOT a geomean input), so the score
    lands independently of R7 and does not collapse to 0 on the committed R7=0 set.

    per_game KEEPS its ``r1``-``r7`` keys (the geomean replaces ONLY the ``score``
    value, so the ``extra="forbid"`` ``RubricGameView`` does not break); the D1-D4
    breakdown is emitted in :func:`geomean_validation` /
    ``results-rubric-geomean.json``, never in this DTO-served row. The score is
    deliberately INDEPENDENT of who won the binary game — the lab proved the win
    split is "purchasable wholesale" — and the §6 Pearson check confirms it does
    not reward winning. R5 (win-shape diversity) is a set-level property,
    summarized in :func:`interestingness`. R1/R2/R3/R7 stay emitted as SEPARATE
    terms so Phase-C can read them as multi-objective fitness axes.

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

    # R2 deception == D3 impostor craft: credit ONLY an EFFECTIVE deflection
    # (audit P0 / G3). Computed via :func:`_d3_impostor_craft` (the EFFECTIVE
    # subcount — a skip-saved active survival stays in the passive 0.2 band, never
    # its own tier), so the per-game ``r2_deception`` term and the geomean's D3
    # input are ONE value and can never drift.
    r2 = _d3_impostor_craft(g)

    # R3 arcs: a cross-meeting suspicion RISE that LANDED on a true impostor
    # (audit P0 / G2). The old "0.5 for >=2 meetings + 0.5 for any flagless
    # carry-eject" rewarded exactly the railroad R4 forbids; this credits only a
    # genuine accumulator arc onto a real impostor.
    r3 = 1.0 if _suspicion_rose_onto_impostor(g, traj_by_key) else 0.0

    # R7 legibility: share of meetings bearing a STRONG contradiction naming a
    # true impostor (audit P0 / CAL-2). Raw n_contradictions>0 counted weak
    # below-gate flags that eject nobody; this counts only decision-grade signal.
    r7 = _strong_evidence_meeting_share(g)

    # GEOMEAN composition (Task 13.15): score = 100 * floor * geomean(D1-D4),
    # replacing the additive 0.35·R1 + 0.25·R2 + 0.20·R3 + 0.20·R7 sum. The
    # additive sum let a live R2 mask a dead R1 (it ranked the seed-0/16 stopwatch
    # wins above every eject-decided game); the geomean SINKS the score on any one
    # dead dimension. D1-D4 route AROUND the dead R7 (it is NOT an input), so the
    # score lands independently of R7 and does not collapse to 0 on the R7=0 set.
    # r1-r7 above stay emitted as per_game keys (the geomean replaces ONLY this
    # score value); the D1-D4 breakdown lives in results-rubric-geomean.json.
    score = _contest_dimensions(g, traj_by_key, integrity_ok=integrity_ok)["score"]
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


def _require_meeting_inputs(facts: dict[str, Any]) -> None:
    """Fail loud when a real facts JSON is missing the meeting inputs the scorer needs.

    When ``aggregates`` is present (a real extractor run), every meeting must carry
    the inputs the geomean dimensions read; a stale / partial / renamed-field /
    null run raises rather than silently zeroing or undercounting a dimension
    (mirrors :func:`_accumulator_trajectory_index`). Validated per meeting:

    * ``suspicion_graph_by_voter`` — a dict (the D2 separation input). A missing /
      null / non-dict value raises — it would silently zero the 25%-weight D2. May
      be EMPTY, mirroring ``testimony_records`` below: a no-accusation SKIP meeting
      (nobody voiced a suspicion → an empty graph) legitimately scores D2=0, so an
      empty dict is a real game state, not the data error the tripwire guards.
    * ``testimony_records`` — a list (the D2 conversion + railroad input). May be
      EMPTY: a meeting with no accused subjects is legitimate.
    * ``plurality_margin`` — present on every EJECTION meeting (the D4 swing
      input). Absent on an ejection meeting raises — it would silently undercount
      the swing.

    A facts dict with NO ``aggregates`` block (the regen-plumbing fixture, no real
    meeting to score) is skipped.
    """
    if facts.get("aggregates") is None:
        return
    for g in facts["games"]:
        for m in g["meetings"]:
            mid = m.get("meeting_id")
            graph = m.get("suspicion_graph_by_voter")
            # An EMPTY dict is legitimate (a no-accusation SKIP meeting voices no
            # suspicion → an empty graph → a correct D2=0), mirroring the empty
            # testimony_records case below; only a missing / null / non-dict value
            # is the data error this tripwire guards against.
            if not isinstance(graph, dict):
                raise ValueError(
                    f"meeting {mid!r} has a missing / null / non-dict "
                    "'suspicion_graph_by_voter' (the D2 separation input) on an "
                    "aggregates-bearing facts JSON — refusing to silently score "
                    "D2=0; re-run the gameplay-facts extractor"
                )
            if not isinstance(m.get("testimony_records"), list):
                raise ValueError(
                    f"meeting {mid!r} is missing the list 'testimony_records' (the "
                    "D2 conversion input) on an aggregates-bearing facts JSON — "
                    "re-run the gameplay-facts extractor"
                )
            if m.get("ejected_player_id") and "plurality_margin" not in m:
                raise ValueError(
                    f"ejection meeting {mid!r} is missing 'plurality_margin' (the "
                    "D4 swing input) on an aggregates-bearing facts JSON — refusing "
                    "to silently undercount the swing; re-run the extractor"
                )


def interestingness(facts: dict[str, Any]) -> dict[str, Any]:
    """Per-game interestingness scores + the set-level R5 win-shape diversity."""
    games = facts["games"]
    _require_meeting_inputs(facts)
    traj_by_key = _accumulator_trajectory_index(facts)
    integrity_ok = _facts_integrity_ok(facts)
    per = sorted(
        (
            _game_interestingness(g, traj_by_key, integrity_ok=integrity_ok)
            for g in games
        ),
        key=lambda x: x["score"],
        reverse=True,
    )
    n = len(per) or 1
    shapes: dict[str, int] = {}
    for p in per:
        shapes[p["win_shape"]] = shapes.get(p["win_shape"], 0) + 1
    return {
        "mean_score": round(sum(p["score"] for p in per) / n, 1),
        # statistics.median averages the two middle values on an even-sized set
        # (not the upper-middle), so a 50-game set reports the true median.
        "median_score": round(statistics.median(p["score"] for p in per), 1)
        if per
        else 0.0,
        "n_games": len(per),
        "win_shapes": dict(sorted(shapes.items(), key=lambda kv: -kv[1])),
        "r5_shapes_over_10pct": sum(1 for c in shapes.values() if c / n >= 0.10),
        "per_game": per,
    }


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    """Pearson correlation, or ``None`` when undefined (n < 2 or a flat series)."""
    n = len(xs)
    if n < 2:
        return None
    mx = math.fsum(xs) / n
    my = math.fsum(ys) / n
    sxy = math.fsum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = math.fsum((x - mx) ** 2 for x in xs)
    syy = math.fsum((y - my) ** 2 for y in ys)
    if sxx == 0.0 or syy == 0.0:
        return None
    return sxy / math.sqrt(sxx * syy)


def _geomean_breakdown(
    g: dict[str, Any],
    traj_by_key: dict[tuple[Any, Any], dict[str, Any]],
    *,
    integrity_ok: bool,
) -> dict[str, Any]:
    """A per-game D1-D4 record for the geomean validation artifact (NOT DTO-served).

    Merges the DTO per_game row (r1-r7 + the geomean ``score``) with the full
    D1-D4 breakdown the ``extra="forbid"`` :class:`RubricGameView` would reject, so
    ``results-rubric-geomean.json`` can carry the contest dimensions + their
    sub-terms for the §6 validation while the served ``results-rubric-score.json``
    keeps its exact key set.
    """
    base = _game_interestingness(g, traj_by_key, integrity_ok=integrity_ok)
    dims = _contest_dimensions(g, traj_by_key, integrity_ok=integrity_ok)
    return {
        "seed": base["seed"],
        "reason": base["reason"],
        "win_shape": base["win_shape"],
        "n_meetings": base["n_meetings"],
        "score": base["score"],
        "floor_multiplier": dims["floor_multiplier"],
        "d1_resolution": round(dims["d1_resolution"], 3),
        "d2_deduction": round(dims["d2_deduction"], 3),
        "d3_craft": round(dims["d3_craft"], 3),
        "d4_arc": round(dims["d4_arc"], 3),
        "d2_separation_norm": round(dims["d2_separation_norm"], 3),
        "d2_conversion": round(dims["d2_conversion"], 3),
        "d4_arc_term": round(dims["d4_arc_term"], 3),
        "d4_swing_term": round(dims["d4_swing_term"], 3),
        "d4_contest_term": round(dims["d4_contest_term"], 3),
        "r1_decisive": base["r1_decisive"],
        "r2_deception": base["r2_deception"],
        "r3_arcs": base["r3_arcs"],
        "r7_legible": base["r7_legible"],
    }


def geomean_validation(facts: dict[str, Any]) -> dict[str, Any]:
    """The §6 validation of the geomean rubric over committed replays ($0).

    Mirrors report-rubric-design.md §6: (1) does the geomean rank
    contested/eject-decided games ABOVE the stopwatch; (2) NO perverse gradient —
    no dimension rewards losing / railroading / passivity (per-reason dimension
    means + ``Pearson(dim, crew_win)``, which must stay weak); (3) reachability —
    every dimension is non-zero somewhere on the committed data (unlike R7, 0/50);
    (4) a watch-the-games top/bottom slice for the human eyeball check. Emitted as
    ``results-rubric-geomean.json`` — the held-out referee's record. $0; reads the
    committed facts only.
    """
    games = facts["games"]
    _require_meeting_inputs(facts)
    traj = _accumulator_trajectory_index(facts)
    integrity_ok = _facts_integrity_ok(facts)
    per = sorted(
        (_geomean_breakdown(g, traj, integrity_ok=integrity_ok) for g in games),
        key=lambda r: r["score"],
        reverse=True,
    )

    by_reason: dict[str, list[dict[str, Any]]] = {}
    for r in per:
        by_reason.setdefault(r["reason"], []).append(r)

    # (1) ranking — eject-decided (CREWMATE_EJECT) above the stopwatch (CREWMATE_TASKS)
    eject = [r for r in per if r["reason"] == "CREWMATE_EJECT"]
    tasks = [r for r in per if r["reason"] == "CREWMATE_TASKS"]
    worst_eject = min((r["score"] for r in eject), default=None)
    best_tasks = max((r["score"] for r in tasks), default=None)
    ranking = {
        "n_eject_decided": len(eject),
        "n_stopwatch": len(tasks),
        "eject_decided_score_range": [
            worst_eject,
            max((r["score"] for r in eject), default=None),
        ],
        "stopwatch_score_range": [
            min((r["score"] for r in tasks), default=None),
            best_tasks,
        ],
        "all_eject_decided_above_all_stopwatch": (
            worst_eject is not None
            and best_tasks is not None
            and worst_eject > best_tasks
        ),
        "n_stopwatch_at_or_above_worst_eject": sum(
            1 for r in tasks if worst_eject is not None and r["score"] >= worst_eject
        ),
    }

    # (2) no perverse gradient — per-reason dimension means + Pearson(dim, crew_win)
    dim_keys = ("d1_resolution", "d2_deduction", "d3_craft", "d4_arc", "score")
    crew_win = [1.0 if r["reason"].startswith("CREWMATE") else 0.0 for r in per]
    gradient = {
        "mean_dim_by_reason": {
            reason: {
                k: round(math.fsum(r[k] for r in rows) / len(rows), 3) for k in dim_keys
            }
            for reason, rows in sorted(by_reason.items())
        },
        "pearson_dim_vs_crew_win": {
            k: (
                round(p, 3)
                if (p := _pearson([r[k] for r in per], crew_win)) is not None
                else None
            )
            for k in dim_keys
        },
        "floored_games": [r["seed"] for r in per if r["floor_multiplier"] == 0.0],
    }

    # (3) reachability — every dimension non-zero somewhere
    reachability = {
        k: {
            "max": round(max(r[k] for r in per), 3),
            "n_nonzero": sum(1 for r in per if r[k] > 0.0),
        }
        for k in ("d1_resolution", "d2_deduction", "d3_craft", "d4_arc")
    }

    # (4) watch-the-games — top/bottom slice for the human eyeball check
    slice_keys = (
        "seed",
        "reason",
        "score",
        "d1_resolution",
        "d2_deduction",
        "d3_craft",
        "d4_arc",
    )
    watch = {
        "top": [{k: r[k] for k in slice_keys} for r in per[:5]],
        "bottom": [{k: r[k] for k in slice_keys} for r in per[-5:]],
    }

    return {
        "weights": _GEOMEAN_WEIGHTS,
        "epsilon": _GEOMEAN_EPSILON,
        "separation_scale": _D2_SEPARATION_SCALE,
        "railroad_gate": _SKIP_SUSPICION_THRESHOLD,
        "n_games": len(per),
        "mean_score": round(math.fsum(r["score"] for r in per) / len(per), 2)
        if per
        else 0.0,
        # true even-size median (averages the two middle values), not upper-middle.
        "median_score": round(statistics.median(r["score"] for r in per), 2)
        if per
        else 0.0,
        "validation": {
            "ranking_contested_above_stopwatch": ranking,
            "no_perverse_gradient": gradient,
            "reachability": reachability,
            "watch_the_games": watch,
        },
        "per_game": per,
    }


# ``git_sha`` is the 4th ``|``-split cell from the END of a ``MANIFEST.md`` data
# row — robust to the optional Task-14.7 ``flags`` column (inserted after
# ``prompt_versions``, so it shifts every HEAD-index but not the tail). A fixed
# head-index would slide onto ``refreshed_at`` for 8-col rows and stamp a DATE as
# the "scored-against" sha. Kept in lockstep with
# ``api.replay_loader._MANIFEST_GIT_SHA_FROM_END`` so the producer stamps the exact
# sha the loader's staleness guard reads back.
_MANIFEST_GIT_SHA_FROM_END = -4
_MANIFEST_MIN_ROW_CELLS = 9

# The mixed-provenance SET FINGERPRINT (Task 19.9). Kept in lockstep with
# ``api.replay_loader._SET_FINGERPRINT_PREFIX`` / ``_SET_FINGERPRINT_DIGEST_LEN``:
# the loader VALIDATES this exact shape (``multi:<12 hex>``) before treating a
# stamp as a fingerprint at all, and compares it by exact equality — so the
# producer must never emit a shortened or differently-cased key.
_SET_FINGERPRINT_PREFIX = "multi:"
_SET_FINGERPRINT_DIGEST_LEN = 12


def _manifest_seed_shas(set_dir: Path) -> list[tuple[str, str]]:
    """The ``(seed, git_sha)`` pairs of a set's ``MANIFEST.md`` data rows.

    Mirrors ``api.replay_loader._manifest_seed_shas`` so producer and loader
    derive the SAME provenance key from the same bytes.
    """

    try:
        text = (set_dir / "MANIFEST.md").read_text(encoding="utf-8")
    except OSError:
        return []
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) < _MANIFEST_MIN_ROW_CELLS:
            continue
        if not cells[1].lstrip("-").isdigit():
            continue  # header / separator row
        sha = cells[_MANIFEST_GIT_SHA_FROM_END]
        if sha:
            rows.append((cells[1], sha))
    return rows


def _set_fingerprint(rows: Iterable[tuple[str, str]]) -> str:
    """A stable digest of a set's sorted per-seed recording shas.

    Byte-identical to ``api.replay_loader._set_fingerprint`` — the loader
    recomputes this exact string from the manifest and compares it to the stamp
    written here, so the two sides can never disagree on a mixed-provenance set.
    """

    payload = "\n".join(f"{seed}:{sha}" for seed, sha in sorted(set(rows)))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"{_SET_FINGERPRINT_PREFIX}{digest[:_SET_FINGERPRINT_DIGEST_LEN]}"


def _set_manifest_sha(set_dir: Path) -> str | None:
    """A set's PROVENANCE KEY: its single recording sha, or a set fingerprint.

    Mirrors ``api.replay_loader._manifest_git_sha``: the rubric stamps the
    version of the replay SET it was scored from (read here, cwd-independent via
    the absolute ``set_dir``), so the loader's freshness comparison is
    "do the served replays still match what the rubric was scored against",
    NOT "what code commit happened to run the scorer".

    A uniformly-recorded set stamps its one distinct short sha. A PIECEMEAL-
    refreshed set — the committed 9p2i carries three distinct recording shas —
    stamps the ``multi:<digest>`` fingerprint over its sorted ``(seed, sha)``
    rows instead (Task 19.9). Both sides returned ``None`` there before, and a
    missing key reads stale unconditionally, so no re-score could clear the
    banner. This commit-label key is retained for display; the separate source
    fingerprint verifies the actual recording inputs. ``None`` only when the manifest is absent or ships no
    data rows.
    """

    rows = _manifest_seed_shas(set_dir)
    if not rows:
        return None
    shas = {sha for _, sha in rows}
    if len(shas) == 1:
        return next(iter(shas))
    return _set_fingerprint(rows)


def regen_for_set(
    facts: dict[str, Any], set_dir: Path, *, git_head: str | None = None
) -> Path:
    """Re-run the scorer and co-locate ``results-rubric-score.json`` into a set.

    The per-set rubric PRODUCER (Task 12.2; DESIGN.md §3.1, §7). Scores ``facts``
    (the gameplay-facts extractor's output) into the served interestingness
    surface and writes it into ``set_dir`` so ``/eval/rubric`` can serve it.

    ``facts.source_fingerprint`` must match the current replay, roster, and
    manifest bytes. Facts extracted before a source change cannot be relabelled
    current merely by copying the new manifest's commit identifier. Missing
    fingerprints require re-extraction. The manifest provenance key remains in
    ``git_head`` for compatible display, alongside the new raw source stamp.

    Writes the served score rows and their source/provenance stamps;
    the human-readable R1–R7 ``rows`` table stays the lab-local artifact
    :func:`main` writes. Wired into the refresh / re-record path
    (``scripts/refresh_samples.sh``) so the happy path stays fresh rather than
    only banner-guarded when stale.
    """

    source_fingerprint = facts.get("source_fingerprint")
    if source_fingerprint != recording_fingerprint(set_dir):
        raise ValueError(
            "facts do not identify the current recording bytes; re-extract them "
            "before publishing highlight scores"
        )
    head = (
        git_head
        if git_head is not None
        else (_set_manifest_sha(set_dir) or facts.get("git_head"))
    )
    out = {
        "seedset": facts.get("seedset"),
        "git_head": head,
        "source_fingerprint": source_fingerprint,
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

    # Stamp the SET manifest's provenance key (the replay version scored), NOT the
    # scoring HEAD (audit RUB-CAL-5): the pre-repair lab-local write stamped
    # ``facts['git_head']`` (a docs-descendant scoring commit), so the
    # loader's freshness guard would have read the lab artifact as scored at a
    # different version than the served copy. Resolve the set dir from
    # ``--set-dir`` or the facts JSON's own ``sample_dir`` and read the same
    # key the served copy carries, mirroring :func:`regen_for_set`.
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
    print(
        f"\nwrote experiments/lab/results-rubric-score.json "
        f"(set provenance key {lab_head})"
    )

    # ---- Geomean interestingness referee (Task 13.15) ----
    # The held-out referee's D1-D4 score + the report-rubric-design.md §6
    # validation, written as a SEPARATE lab artifact (the served per_game keeps its
    # r1-r7 DTO shape; D1-D4 cannot ride in it). $0; committed.
    geo = geomean_validation(facts)
    geo_out = {"seedset": label, "git_head": lab_head, **geo}
    Path(f"experiments/lab/{GEOMEAN_RESULTS_FILENAME}").write_text(
        json.dumps(geo_out, indent=2)
    )
    rank = geo["validation"]["ranking_contested_above_stopwatch"]
    print(
        f"wrote experiments/lab/{GEOMEAN_RESULTS_FILENAME} "
        f"(geomean mean {geo['mean_score']} / median {geo['median_score']}; "
        f"all eject-decided above all stopwatch: "
        f"{rank['all_eject_decided_above_all_stopwatch']})"
    )

    if args.set_dir is not None:
        dest = regen_for_set(facts, Path(args.set_dir))
        print(f"co-located per-set rubric (git_head stamped): {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
