"""Deterministic Extract phase of the gameplay-data audit.

Re-derives ground-truth roles (firewalled OUT of the replays) by re-seeding the
engine, re-runs the recorded action stream through ``engine.tick.advance_tick``
(mirroring ``api.replay_loader.ReplayLoader._walk``) so the engine itself
surfaces resolved events (Killed actor/target/room, ActionRejected, Moved,
MeetingTriggered, GameOver), then emits a structured FACTS JSON plus
code-certain HARD rule-violation findings.

Because ``advance_tick`` ENFORCES every hard rule (impostor-only kill, cooldown,
same-room kill, adjacency move, alive-player gate, eligible reporter) by emitting
an ``ActionRejectedEvent`` and NOT applying the offending action, a rule-breaking
action in the recorded stream becomes a rejection — and the rejection's reason is
the code-certain classifier. We additionally re-derive each Killed event's
victim role from the re-seeded roster to catch impostor-on-impostor kills.

v2 (Phase-8 / 9p2i set): meetings are the turns-based accusation chain
(DESIGN.md §5.2; Task 8.7 ``MeetingTranscript.turns``). For every meeting this
script re-walks the recorded chain against the deterministic 3-condition
termination rule (``meetings.transcript.next_chain_step``), re-derives the
opt-in eligibility gate (``meetings.manager._opt_in_eligible_ids``), and
emits per-meeting chain facts (turn-kind counts, chain length, termination
condition, accusations with re-seeded roles, opt-in substance, ballots with
``primary_reason_id`` linkage) plus chain-protocol mechanical checks
(termination / turn-id-order / reply_to / opt-in containment / 7.12 firewall /
dangling primary_reason_id / dead speakers-voters).

v3 (Phase-10 W0+ baseline, 2026-06-11 @ 9p2i post-10.5):
* Every weak/strong + genuine-class classification is now IMPORTED from the
  one-home repaired sources (``meetings.transcript.is_weak_contradiction`` /
  ``detect_contradictions``; ``eval.vote_correctness.compute_genuine_class_
  conversion``) — never an era-frozen replica — and the re-derived genuine
  pair is CROSS-CHECKED against the shipped 10.4 metric on the same bytes
  (mismatch -> blocking finding; one classifier would be wrong).
* Point-6c Wave-1 contract-input aggregates: per-(meeting, accused-subject)
  TESTIMONY records (both roles — innocents are the cascade-risk input),
  GENUINE-CLASS records, ACCUMULATOR TRAJECTORY facts (per multi-meeting vote
  candidate's rendered-suspicion series + Rule-3/Rule-5 downward-move sanity),
  and 10.3 OPENING-RETRY telemetry (recovered single-retries from duplicate
  opening-slot llm_calls; defaults from the deadline_default rows).

v4 (Phase-10 Wave-2 CRATER baseline, 2026-06-14 @ 9p2i post-10.16): the
point-6e Wave-2 aggregates the close lenses need, plus the 10.11.1
emergency-strip telemetry on the existing emergency aggregate. Every
classification still IMPORTS its one-home source (no era-frozen replica):

* ACTIONS BY ROLE (the blending census) via the imported
  ``eval.action_ingest.tally_actions_by_role`` -> ``compute_indistinguishability``
  over the SAME shipped report games, plus a do_task INTEGRITY check folded
  from the per-tick walk: the engine ALWAYS rejects an impostor's pretend
  ``do_task`` (a non-owned map task id, Task 10.14 — ``_resolve_owned_task_
  instance`` returns None -> ActionRejectedEvent), so it never advances a real
  task instance; the trust check is that no walked ``TaskProgressedEvent`` /
  ``TaskCompletedEvent`` carries an IMPOSTOR actor (a single one is BLOCKING —
  a fake task reached the real CREWMATE_TASKS denominator).
* EFFECTIVE-DEFLECTION records via the imported
  ``eval.meeting_quality.compute_effective_deflection`` (the blend-vs-deflect
  split: ACTIVE-DEFLECTED vs PASSIVE/SKIP-saved vs CAUGHT).
* INFORM-CHANNEL conversions via the imported ``decompose_ejection_channels``
  (the 10.16 fifth channel ``CHANNEL_SINGLE_WITNESS_INFORM``) cross-checked
  against the shipped ``compute_multi_signal_conversion`` per-channel count.
* WIN-DECISION attribution (the R1 verdict input): per game eject-DECIDED
  (both impostors removed by the meeting layer -> CREWMATE_EJECT) vs STOPWATCH
  (CREWMATE_TASKS fired with an impostor still alive), with the stopwatch tick
  margin between task completion and the would-be 2nd ejection.
* 10.11.1 EMERGENCY-STRIP telemetry on the 6d emergency aggregate: the
  ``EMERGENCY_BODY_STRIP_MARKER`` on an emergency opening's free_text (the
  deterministic backstop that removed a fabricated found_body) — the residual-
  fabrication signal (how often the 9B still tried). A found_body that SURVIVED
  onto an emergency opening turn stays the blocking 10.8 leak (now read against
  the strip).

Usage:
    PYTHONPATH=<repo root> uv run python audits/workflows/extract_gameplay_facts.py
"""

from __future__ import annotations

import json
import os
import re
import statistics
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from pydantic import TypeAdapter

from engine.actions import Action
from engine.events import (
    ActionRejectedEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
)
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval._suspicion_parse import (
    SKIP_SUSPICION_THRESHOLD,
    parse_rendered_max_suspicion,
)
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    EMERGENCY_BODY_STRIP_MARKER,
    INVALID_ACCUSATION_TARGET_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
    _opt_in_eligible_ids,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    SawPlayerObservation,
    TurnKind,
)
from meetings.transcript import (
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_RETARGETED_PROXY,
    WEAK_REASON_NARROW_WINDOW,
    WEAK_REASON_SELF_STATED,
    detect_contradictions,
    independent_voices,
    is_canonically_ordered,
    is_weak_contradiction,
    next_chain_step,
)
from agents.memory.beliefs import (
    CONTRADICTION_SUSPICION_DELTA,
    TESTIMONY_INDEPENDENCE_BAR,
    WEAK_CONTRADICTION_SUSPICION_DELTA,
)
from eval.action_ingest import tally_actions_by_role
from eval.balance_eval import load_tournament_report
from eval.meeting_quality import (
    CHANNEL_SINGLE_WITNESS_INFORM,
    compute_ballot_target_redirects,
    compute_defaulted_ballots,
    compute_effective_deflection,
    compute_indistinguishability,
    compute_multi_signal_conversion,
    decompose_ejection_channels,
)
from eval.vote_correctness import (
    compute_genuine_class_conversion,
    compute_vote_correctness,
)
from experiments.lab.rubric_score import score as _rubric_score
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    FailedCallReplayEntry,
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "replays" / "samples" / "9p2i"
SEEDSET = "9p2i"

# Action adapter for deserializing recorded raw actions.
_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# v3 (conversion / 9B-artifact) constants.
#
# The rendered §4.6 vote-gate parse (the "maximum suspicion among the living
# ejection targets is **X**" regex) and the CORRECT/MISSED classification
# threshold are imported from eval._suspicion_parse — the canonical home shared
# with the shipped eval.meeting_quality conversion sentinels (Task 9.6 / gp-2),
# so this extractor and the eval report can never drift on what "the rendered
# max" or "missed" means. The SKIP partition classifies each SKIP ballot
# CORRECT (rendered max < threshold) vs MISSED (rendered max >= threshold).

# Marker *prefixes* (the literal text minus the {target!r} placeholder) the
# meeting layer writes when it DROPS a hallucinated non-living target (fb3cfa5):
# an accusation-claim target is dropped and the original recorded on the turn's
# free_text; a ballot target is normalised to SKIP and the original recorded on
# the ballot's rationale_text. Split on "{target!r}" so the prefix matches
# regardless of the (quoted) id that follows.
_INVALID_ACC_MARKER_PREFIX = INVALID_ACCUSATION_TARGET_MARKER.split("{target!r}")[0]
_INVALID_VOTE_MARKER_PREFIX = INVALID_VOTE_TARGET_MARKER.split("{target!r}")[0]

# Wave-1-CLOSE marker prefixes (point 6d), imported from meetings.manager so the
# extractor and the shipped eval.meeting_quality census (compute_defaulted_ballots
# / compute_ballot_target_redirects) can never drift on what a redirect / a
# defaulted ballot is. The 10.9.2 ballot-target graph guard prepends
# BALLOT_TARGET_REDIRECT_MARKER (preserving the original under-gate target) to a
# rewritten eject ballot's rationale_text; the 10.9.1 vote-parse fail-soft writes
# VOTE_PARSE_DEFAULT_MARKER as the WHOLE rationale_text of a twice-failed ballot
# degraded to SKIP. Split each on its placeholder so the prefix matches whatever
# (bounded) original / response-head follows. The redirect marker's preserved
# original target is recovered with the FULL regex below (the quoted value between
# the prefix and " redirected] ").
_BALLOT_REDIRECT_MARKER_PREFIX = BALLOT_TARGET_REDIRECT_MARKER.split("{target!r}")[0]
_VOTE_PARSE_DEFAULT_MARKER_PREFIX = VOTE_PARSE_DEFAULT_MARKER.split("{head!r}")[0]

# The redirect marker wraps the (bounded) original under-gate target in single
# quotes between the pinned prefix and " redirected] ", e.g.
# "[under-gate eject target 'p-1' redirected] ". Recover that original id so the
# redirect lens can resolve its role + the voter's rendered suspicion of it (the
# guard's precondition: original below the gate, redirect at/above). A player id
# is short, so _bounded_original never truncates it; the capture is non-greedy in
# case a bounded blob ever lands here.
_BALLOT_REDIRECT_ORIGINAL_RE: re.Pattern[str] = re.compile(
    re.escape(_BALLOT_REDIRECT_MARKER_PREFIX) + r"'(?P<orig>.*?)' redirected\] "
)

# A defaulted-turn failed_call carries the turn coordinates in its error_message,
# e.g. "reply turn (turn 1) defaulted (validation); p-9 submitted no turn ...".
_DEFAULTED_TURN_RE: re.Pattern[str] = re.compile(
    r"(?P<kind>opening|reply|opt_in) turn \(turn (?P<index>\d+)\) defaulted"
    r"[^;]*;\s*(?P<speaker>\S+) submitted no turn"
)
# A defaulted-VOTE row names its voter; capture it so the persisted §4.6
# verdict max (FailedCallReplayEntry.rendered_vote_max, Task 10.12 / audit
# H-H-2) joins back to the defaulted SKIP ballot. The voter is the run of
# non-"; " chars, excluding any trailing " [error: ...]" provider suffix.
_DEFAULTED_VOTE_RE: re.Pattern[str] = re.compile(
    r"vote defaulted[^;]*;\s*(?P<voter>\S+) submitted no ballot"
)

# Full invalid-accusation-target marker, including the quoted id it wraps, so the
# whole "[invalid accusation target 'imp-2' dropped] " span can be stripped out
# before measuring the model's actual prose length.
_INVALID_ACC_MARKER_FULL_RE: re.Pattern[str] = re.compile(
    re.escape(_INVALID_ACC_MARKER_PREFIX) + r".*?dropped\] "
)

# ---------------------------------------------------------------------------
# Wave-1 decomposition constants (point 6b — regression-decomposition lens).
# ---------------------------------------------------------------------------
#
# The §6.6 vote prompt renders the voter's OWN suspicion graph as a block under
# a "## Your suspicion graph" header, one row per known player:
#
#     ## Your suspicion graph
#     - `p-2`: suspicion 0.70, trust 0.50- `p-6`: suspicion 0.78, trust 0.50
#
# This is the only place a per-TARGET (not just the max) §4.6 suspicion value
# survives into the replay, so the decomposition reads the EJECTED player's
# rendered suspicion off the graphs of the OTHER voters (a voter holds no row
# about itself, so the ejected player's value never appears in their own
# prompt). Pin the header literal and the row regex; both are produced by the
# committed vote_ballot.j2 template.
_SUSPICION_GRAPH_HEADER = "## Your suspicion graph"
_SUSPICION_GRAPH_ROW_RE: re.Pattern[str] = re.compile(
    r"`(?P<pid>p-\d+)`: suspicion (?P<sus>[0-9]*\.?[0-9]+), "
    r"trust (?P<trust>[0-9]*\.?[0-9]+)"
)


# A contradiction's WEAK classification comes from the ONE-HOME predicate
# meetings.transcript.is_weak_contradiction (imported, never replicated): the
# 10.1-repaired predicate belief Rule 2 keys its graduated down-weight on, so
# this extractor and the shipped down-weight can never drift on what "weak"
# means. The individual weak REASONS (self-stated / narrow-window / endpoint-
# tick) are still read off the detector-written description marker so the
# decomposition can surface WHY a flag is weak (the endpoint-tick band is the
# genuine-class disqualifier — a non-endpoint alibi_vs_sighting naming a true
# impostor is the CANON-interior genuine class the 10.4 gate counts). A
# contradiction is_weak_contradiction()==False is STRONG (the full
# CONTRADICTION_SUSPICION_DELTA flag Rule 2 does NOT down-weight).
def _classify_contradiction(contra: Any) -> dict[str, bool]:
    """Classify a recorded ContradictionRef via the imported one-home predicate.

    ``strong`` is ``not is_weak_contradiction(flag)`` — the imported
    10.1-repaired predicate, never an inline marker check. The three weak
    reason flags are read off the description marker (the detector appends
    ``WEAK_REASON_*`` inside ``WEAK_CONTRADICTION_MARKER_PREFIX``) and are
    informational sub-classifications inside one weak marker. ``endpoint_tick``
    is the 10.1 band that disqualifies an ``alibi_vs_sighting`` from the
    genuine CANON-interior class.
    """

    desc = contra.description or ""
    weak = is_weak_contradiction(contra)
    return {
        "kind": contra.kind,
        "weak": weak,
        "weak_self_stated": weak and WEAK_REASON_SELF_STATED in desc,
        "weak_narrow": weak and WEAK_REASON_NARROW_WINDOW in desc,
        "weak_endpoint_tick": weak and WEAK_REASON_ENDPOINT_TICK in desc,
        "strong": not weak,
    }


def _testimony_vehicle(turn: Any, subject: str) -> tuple[str | None, bool]:
    """How a turn names ``subject``, and whether the mention is observation-backed.

    Wave-1 testimony lens (point 6c): for a turn that mentions ``subject``,
    classify the VEHICLE the mention rides:

    * ``"accusation"`` — an :class:`AccusationClaim` against ``subject`` (the
      chain-driving vehicle).
    * ``"sighting"`` — a :class:`SawPlayerObservation` of ``subject`` or an
      other-player :class:`AlibiClaim` placing ``subject`` somewhere (a
      location claim that feeds §5.4 detection).
    * ``"free_text_only"`` — ``subject`` appears only in the turn's free_text
      with no structured claim/observation naming them (the cascade-prone
      bare verbal mention that never enters a listener's belief store).
    * ``None`` — the turn does not name ``subject`` at all.

    ``observation_backed`` is True when the turn carries a first-hand
    :class:`SawPlayerObservation` / :class:`FoundBodyObservation` (a structured
    sighting), the signal that separates an evidence-grounded accusation from a
    bare vibe. The two returns are independent: an accusation CAN be
    observation-backed (the accuser also logged a sighting on the same turn).
    """

    has_observation = any(
        isinstance(o, (SawPlayerObservation, FoundBodyObservation))
        for o in turn.observations
    )
    accuses = any(
        isinstance(c, AccusationClaim) and c.against == subject for c in turn.claims
    )
    sights = any(
        isinstance(o, SawPlayerObservation) and o.subject == subject
        for o in turn.observations
    ) or any(isinstance(c, AlibiClaim) and c.subject == subject for c in turn.claims)
    if accuses:
        return "accusation", has_observation
    if sights:
        return "sighting", has_observation
    # free_text-only mention: the subject id appears verbatim in the prose but
    # no structured claim/observation carries it (the bare verbal-testimony
    # vehicle the Wave-1 testimony-ingestion lever targets).
    if subject in (turn.free_text or ""):
        return "free_text_only", has_observation
    return None, has_observation


def _genuine_subjects(transcript: Any, roster: frozenset[str]) -> frozenset[str]:
    """Re-derive the genuine CANON-interior subjects (one-home, Task 10.4).

    Re-runs the imported repaired detector
    (:func:`meetings.transcript.detect_contradictions`) over the recorded
    transcript under the ballot-voter roster — exactly the
    :func:`eval.vote_correctness.compute_genuine_class_conversion` definition —
    and returns every subject named by an ``alibi_vs_sighting`` flag WITHOUT the
    endpoint band (non-endpoint == interior-tick == the audit's genuinely-
    diagnostic class). Imported, never re-implemented: on post-repair
    recordings the re-run equals the recorded flags byte-for-byte (verified by
    the genuine-class cross-check invariant).
    """

    genuine: set[str] = set()
    for flag in detect_contradictions(transcript, roster=roster):
        if flag.kind != "alibi_vs_sighting":
            continue
        if WEAK_REASON_ENDPOINT_TICK in flag.description:
            continue
        # 10.6 retarget exclusion (mirrors eval.vote_correctness
        # .genuine_class_subjects): a re-targeted proxy flag names the proxy
        # SPEAKER, not a player whose own location a sighting contradicted,
        # so it never supplies the alibi-lie gate. First bites on W1 bytes
        # (seeds 16/49 impostor-named retargets — PR #147 F3).
        if WEAK_REASON_RETARGETED_PROXY in flag.description:
            continue
        genuine.update(flag.subjects)
    return frozenset(genuine)


def _parse_suspicion_graph(prompt: str) -> dict[str, float]:
    """Return {player_id: rendered_suspicion} from a vote prompt's graph block.

    Empty if the prompt carries no ``## Your suspicion graph`` section (the
    voter holds no beliefs about anyone — a 0.00 rendered max). The block ends
    at the next ``## `` header.
    """

    if _SUSPICION_GRAPH_HEADER not in prompt:
        return {}
    after = prompt.split(_SUSPICION_GRAPH_HEADER, 1)[1]
    block = after.split("## ", 1)[0]
    return {
        m.group("pid"): float(m.group("sus"))
        for m in _SUSPICION_GRAPH_ROW_RE.finditer(block)
    }


# Vote-prompt graph block header (pinned in the constants above) and the
# turn-prompt first-header literals the committed templates emit, used to
# classify each meeting llm_call by the slot it filled (Task 10.3 retry lens).
# A VOTE call is the only one that renders "## Your suspicion graph"; the three
# turn kinds are distinguished by their first markdown header (the opening's
# "## Meeting context" vs the reply / opt-in statement headers). These are the
# literals the regression-pinned vote_ballot.v5 / accusation_round.v7 /
# crewmate_report.v5 / impostor_report_v4 templates produce on this set.
_OPENING_PROMPT_FIRST_HEADER = "## Meeting context"
_REPLY_PROMPT_FIRST_HEADER = "## Your turn: a reply"
_OPTIN_PROMPT_FIRST_HEADER = "## Your turn: an opt-in info-share"
_FIRST_HEADER_RE: re.Pattern[str] = re.compile(r"^#+ .*$", re.MULTILINE)


def _classify_call_slot(prompt: str) -> str:
    """Classify a meeting llm_call by the meeting slot it filled.

    Returns one of ``vote`` / ``opening`` / ``reply`` / ``opt_in`` / ``other``.
    The §6.6 vote ballot is the only prompt carrying ``## Your suspicion
    graph``; the three turn kinds carry distinct first markdown headers (the
    opening's ``## Meeting context`` vs the reply / opt-in statement headers).
    Deterministic over the regression-pinned templates this set was recorded
    with — a divergent header lands in ``other`` rather than silently
    mis-binning, so the retry counts stay honest.
    """

    if _SUSPICION_GRAPH_HEADER in prompt:
        return "vote"
    match = _FIRST_HEADER_RE.search(prompt)
    first = match.group(0) if match else ""
    if first == _OPENING_PROMPT_FIRST_HEADER:
        return "opening"
    if first == _REPLY_PROMPT_FIRST_HEADER:
        return "reply"
    if first == _OPTIN_PROMPT_FIRST_HEADER:
        return "opt_in"
    return "other"


def _parse_redirect_original(rationale_text: str) -> str | None:
    """The original under-gate target a 10.9.2 redirect rewrote, or None.

    Reads the (bounded) preserved id out of the
    :data:`BALLOT_TARGET_REDIRECT_MARKER` span at the head of a redirected
    ballot's ``rationale_text``. None when the ballot carries no redirect
    marker (the common case). Player ids are short so the bounding never
    truncates; the value is returned verbatim for role / rendered-suspicion
    resolution by the redirect lens.
    """

    m = _BALLOT_REDIRECT_ORIGINAL_RE.search(rationale_text or "")
    return m.group("orig") if m is not None else None


def _deserialize_actions(raw_actions: list[dict[str, Any]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _length_distribution(samples: list[int]) -> dict[str, Any]:
    """median / p95 / max char-length over a turn-kind's non-defaulted turns."""

    if not samples:
        return {"n": 0, "median": None, "p95": None, "max": None}
    ordered = sorted(samples)
    # Nearest-rank p95 (deterministic, no interpolation): the smallest sample
    # at or above the 95th percentile position.
    rank = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
    return {
        "n": len(ordered),
        "median": int(statistics.median(ordered)),
        "p95": ordered[rank],
        "max": ordered[-1],
    }


def _cross_era_trajectory(
    *,
    w2_effective_deflection: Any,
    w2_multi_signal: Any,
    w2_genuine_supplied: int,
    w2_genuine_converted: int,
    w2_conversion_per_meeting: float | None,
    w2_total_meetings: int,
    w2_win_split: Mapping[str, int],
    w2_eject_decided_wins: int,
) -> dict[str, Any]:
    """W0 -> W1 -> W2 comparison rows from the committed corrected-baseline fixtures.

    Reads the committed ``tests/fixtures/phase10/corrected_w{0,1,2}_baseline.json``
    fixtures (the one-home era baselines the 10.x A/B gates were written against)
    so lenses B/E do not each re-read prior eras. The W2 row is the live
    re-derivation from THIS extraction (cross-checked against the W2 fixture's own
    numbers — a mismatch means the committed fixture and the current bytes
    diverged). Each metric is the overshoot-vs-trend signal the close-gate names:
    effective_deflection (the deception-skill subcount), genuine/multi conversion
    (the detection pipeline), conversion_per_meeting + meetings/game (pacing), and
    the impostor-win-rate / R1 eject-decided wins (the headline balance the gate
    excludes as an A/B signal but the audit still reports).
    """

    fixtures_dir = REPO_ROOT / "tests" / "fixtures" / "phase10"
    rows: dict[str, dict[str, Any]] = {}
    for era in ("w0", "w1", "w2"):
        fpath = fixtures_dir / f"corrected_{era}_baseline.json"
        if not fpath.exists():
            rows[era] = {"present": False}
            continue
        fx = json.loads(fpath.read_text(encoding="utf-8"))
        ed = fx.get("effective_deflection") or {}
        ms = fx.get("multi_signal") or fx.get("multi_signal_conversion") or {}
        gc = fx.get("genuine_class_conversion") or {}
        cpm = fx.get("conversion_per_meeting") or {}
        rows[era] = {
            "present": True,
            "effective_deflections": ed.get("effective_deflections"),
            "accused_impostor_survivals": ed.get("accused_impostor_survivals"),
            "skip_saved_active_survivals": ed.get("skip_saved_active_survivals"),
            "genuine_supplied": gc.get("supplied"),
            "genuine_converted": gc.get("converted"),
            "genuine_conversion_rate": gc.get("conversion_rate"),
            "multi_signal_conversions": ms.get("multi_signal_conversions"),
            "multi_signal_impostor_ejections": ms.get("impostor_ejections"),
            "conversions_with_single_witness_inform": ms.get(
                "conversions_with_single_witness_inform"
            ),
            "conversion_per_meeting": cpm.get("conversion_per_meeting"),
            "resolved_meetings": cpm.get("resolved_meetings"),
        }

    # The live W2 row from THIS extraction (the oracle), cross-checked against the
    # committed W2 fixture so a fixture/bytes drift is visible.
    live_w2 = {
        "effective_deflections": w2_effective_deflection.effective_deflections,
        "accused_impostor_survivals": (
            w2_effective_deflection.accused_impostor_survivals
        ),
        "skip_saved_active_survivals": (
            w2_effective_deflection.skip_saved_active_survivals
        ),
        "genuine_supplied": w2_genuine_supplied,
        "genuine_converted": w2_genuine_converted,
        "genuine_conversion_rate": (
            round(w2_genuine_converted / w2_genuine_supplied, 4)
            if w2_genuine_supplied
            else None
        ),
        "multi_signal_conversions": w2_multi_signal.multi_signal_conversions,
        "multi_signal_impostor_ejections": w2_multi_signal.impostor_ejections,
        "conversions_with_single_witness_inform": (
            w2_multi_signal.conversions_with_single_witness_inform
        ),
        "conversion_per_meeting": w2_conversion_per_meeting,
        "resolved_meetings": w2_total_meetings,
        "win_split": dict(w2_win_split),
        "impostor_win_rate": (
            round(w2_win_split.get("IMPOSTORS", 0) / sum(w2_win_split.values()), 4)
            if w2_win_split
            else None
        ),
        "r1_eject_decided_wins": w2_eject_decided_wins,
    }
    return {
        "note": (
            "W0->W1->W2 from the committed corrected-baseline fixtures "
            "(tests/fixtures/phase10) + the live W2 re-derivation. The "
            "overshoot-vs-trend signal: effective_deflections and the conversion "
            "channels across eras. live_w2 is THIS extraction; fixture_w2 is the "
            "committed baseline (a divergence is flagged by w2_matches_fixture)."
        ),
        "fixture_w0": rows.get("w0"),
        "fixture_w1": rows.get("w1"),
        "fixture_w2": rows.get("w2"),
        "live_w2": live_w2,
        "w2_effective_deflection_matches_fixture": (
            rows.get("w2", {}).get("effective_deflections")
            == live_w2["effective_deflections"]
        ),
        "w2_genuine_matches_fixture": (
            rows.get("w2", {}).get("genuine_converted") == w2_genuine_converted
            and rows.get("w2", {}).get("genuine_supplied") == w2_genuine_supplied
        ),
    }


def _git_head() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def _classify_rejection(reason: str) -> str | None:
    """Map an ActionRejected reason to a HARD-rule category, or None.

    Only reasons that correspond to a *hard rule violation in the recorded
    stream* (the producer queued an action the engine had to refuse) are
    classified. Reasons that are normal contention (e.g. a stale do_task whose
    room changed) are not hard violations and return None.
    """

    r = reason.lower()
    if "player is dead" in r or "unknown player" in r:
        return "dead_or_unknown_player_action"
    if "only impostors can kill" in r:
        return "non_impostor_kill"
    if "kill is on cooldown" in r:
        return "kill_ignored_cooldown"
    if "kill requires same room" in r:
        return "kill_cross_room"
    if "move destination must be current or adjacent" in r:
        return "move_non_adjacent"
    if "unknown destination room" in r:
        return "move_unknown_room"
    if "report requires actor and body in same room" in r:
        return "report_ineligible_room"
    if "unknown body id" in r:
        return "report_unknown_body"
    return None


def _analyze_meeting(
    *,
    seed: int,
    meeting_index: int,
    meeting_entry: MeetingReplayEntry,
    trigger_kind: str | None,
    trigger_body_id: str | None,
    roles: Mapping[str, str],
    living_ids: frozenset[str],
    findings: list[dict[str, Any]],
    invariant_failures: list[str],
    defaulted_vote_rendered_max: Mapping[str, float],
) -> dict[str, Any]:
    """Per-meeting chain facts + chain-protocol mechanical checks (v2).

    Re-walks the recorded ``transcript.turns`` against the deterministic
    DESIGN.md §5.2 PHASE-2 rule (via ``meetings.transcript.next_chain_step``)
    to re-derive the termination condition, re-derives the PHASE-3 opt-in
    eligibility gate, and emits one mechanical finding per code-certain
    protocol violation. ``living_ids`` is the alive-player set of the
    reconstructed state at the meeting tick (== the participant roster the
    manager ran with: ``orchestrator.game._build_participants`` builds one
    participant per living player).
    """

    mid = meeting_entry.meeting_id
    where = f"seed {seed} meeting {meeting_index} ({mid})"
    turns = meeting_entry.transcript.turns
    turn_id_set = {t.turn_id for t in turns}
    turn_by_id = {t.turn_id: t for t in turns}

    # ---- ADDED invariant: non-empty transcript, exactly one opening at 0 ----
    opening_positions = [i for i, t in enumerate(turns) if t.turn_kind == "opening"]
    if not turns:
        invariant_failures.append(f"{where}: transcript.turns is empty")
    elif opening_positions != [0]:
        invariant_failures.append(
            f"{where}: opening turns at positions {opening_positions}, "
            "expected exactly one opening at position 0"
        )

    # ---- TURN-ID / ORDER mechanical checks ----
    canonical = bool(is_canonically_ordered(turns))
    for i, t in enumerate(turns):
        problems: list[str] = []
        if t.turn_index != i:
            problems.append(f"turn_index {t.turn_index} at tuple position {i}")
        expected_id = f"{mid}:turn-{t.turn_index}"
        if t.turn_id != expected_id:
            problems.append(f"turn_id {t.turn_id!r} != expected {expected_id!r}")
        if i == 0 and t.turn_kind != "opening":
            problems.append(f"turn 0 has turn_kind {t.turn_kind!r}, not 'opening'")
        if i > 0 and t.turn_kind == "opening":
            problems.append(f"extra 'opening' turn at position {i}")
        if problems:
            findings.append(
                {
                    "id": f"TURNORD-{seed}-{meeting_index}-{i}",
                    "severity": "high",
                    "title": "Turn-id/order violation in meeting transcript",
                    "claim": (
                        "A recorded turn breaks the contiguous turn_index / "
                        "'{meeting_id}:turn-{index}' turn_id / opening-at-0 "
                        "contract: " + "; ".join(problems) + "."
                    ),
                    "evidence": (
                        f"{where} turn {i}: speaker {t.speaker} "
                        f"({roles.get(t.speaker, 'UNKNOWN')}); " + "; ".join(problems)
                    ),
                    "repair_hint": (
                        "meetings/manager.py assigns turn_index=len(turns) and "
                        "turn_id='{meeting_id}:turn-{N}' at the single "
                        "_collect_turn chokepoint; trace how this record "
                        "bypassed it (or how the replay row was mutated)."
                    ),
                }
            )

    # ---- REPLY_TO integrity mechanical checks ----
    for i, t in enumerate(turns):
        if t.turn_kind == "reply":
            earlier_ids = {u.turn_id for u in turns[:i]}
            if t.reply_to is None or t.reply_to not in earlier_ids:
                findings.append(
                    {
                        "id": f"REPLYTO-{seed}-{meeting_index}-{i}",
                        "severity": "high",
                        "title": "Reply turn's reply_to is not an earlier turn",
                        "claim": (
                            "A reply turn must reference an EARLIER turn_id of "
                            f"this meeting; got reply_to={t.reply_to!r}."
                        ),
                        "evidence": (
                            f"{where} turn {i}: reply by {t.speaker} "
                            f"({roles.get(t.speaker, 'UNKNOWN')}) has "
                            f"reply_to={t.reply_to!r}; earlier turn ids: "
                            f"{sorted(earlier_ids)}"
                        ),
                        "repair_hint": (
                            "The manager sets reply_to=prev.turn_id when "
                            "passing the chain; a dangling/forward reference "
                            "means the transcript was assembled out of band."
                        ),
                    }
                )
        elif t.reply_to is not None:
            findings.append(
                {
                    "id": f"REPLYTO-{seed}-{meeting_index}-{i}",
                    "severity": "high",
                    "title": f"Non-reply turn carries a reply_to ({t.turn_kind})",
                    "claim": (
                        "opening and opt_in turns must have reply_to=None "
                        f"(got {t.reply_to!r})."
                    ),
                    "evidence": (
                        f"{where} turn {i}: turn_kind={t.turn_kind!r} by "
                        f"{t.speaker} ({roles.get(t.speaker, 'UNKNOWN')}) has "
                        f"reply_to={t.reply_to!r}"
                    ),
                    "repair_hint": (
                        "meetings/manager.py passes reply_to=None for opening "
                        "and opt_in turns; check the turn-construction path."
                    ),
                }
            )

    # ---- TERMINATION re-walk (DESIGN.md §5.2 PHASE 2, deterministic) ----
    chain_len = 0
    termination: str | None = None
    walk_idx = len(turns)
    if turns:
        chain = [turns[0]]
        spoken: set[str] = {turns[0].speaker}
        prev = turns[0]
        idx = 1
        while True:
            step = next_chain_step(
                prev_turn=prev,
                spoken=frozenset(spoken),
                living_ids=living_ids,
                turns_recorded=len(chain),
            )
            if step.next_speaker is None:
                termination = step.termination
                break
            if idx >= len(turns) or turns[idx].turn_kind != "reply":
                recorded = (
                    f"turn_kind={turns[idx].turn_kind!r} by {turns[idx].speaker}"
                    if idx < len(turns)
                    else "absent (transcript ends)"
                )
                findings.append(
                    {
                        "id": f"TERM-{seed}-{meeting_index}-{idx}",
                        "severity": "high",
                        "title": (
                            "Chain stopped while no termination condition had fired"
                        ),
                        "claim": (
                            "The §5.2 three-condition rule predicts a reply by "
                            f"{step.next_speaker!r} at turn {idx}, but the "
                            "recorded chain stops there with no condition "
                            "(a)/(b)/(c) fired."
                        ),
                        "evidence": (
                            f"{where} turn {idx}: predicted next speaker "
                            f"{step.next_speaker} "
                            f"({roles.get(step.next_speaker, 'UNKNOWN')}); "
                            f"recorded turn is {recorded}"
                        ),
                        "repair_hint": (
                            "meetings/manager.py PHASE-2 loop and "
                            "meetings/transcript.py::next_chain_step must agree; "
                            "a chain that stops early without a recorded reason "
                            "means the manager broke out of the loop on a "
                            "non-rule condition (e.g. the 7.12 guarded_next "
                            "no-op firing for real)."
                        ),
                    }
                )
                break
            t = turns[idx]
            if t.speaker != step.next_speaker:
                findings.append(
                    {
                        "id": f"TERM-{seed}-{meeting_index}-{idx}-speaker",
                        "severity": "high",
                        "title": (
                            "Reply speaker diverges from the deterministic chain"
                        ),
                        "claim": (
                            "The accusation chain passes the floor to the "
                            f"accused ({step.next_speaker!r}), but the recorded "
                            f"reply is by {t.speaker!r}."
                        ),
                        "evidence": (
                            f"{where} turn {idx}: recorded speaker {t.speaker} "
                            f"({roles.get(t.speaker, 'UNKNOWN')}), predicted "
                            f"{step.next_speaker} "
                            f"({roles.get(step.next_speaker, 'UNKNOWN')})"
                        ),
                        "repair_hint": (
                            "next-speaker is a pure function of the prior "
                            "turn's first AccusationClaim; divergence means a "
                            "non-deterministic / corrupted record."
                        ),
                    }
                )
            if t.reply_to != prev.turn_id:
                findings.append(
                    {
                        "id": f"TERM-{seed}-{meeting_index}-{idx}-link",
                        "severity": "high",
                        "title": (
                            "Chain reply links to a turn other than the prior "
                            "chain turn"
                        ),
                        "claim": (
                            "Each chain reply must answer the immediately "
                            f"prior chain turn ({prev.turn_id!r}); got "
                            f"{t.reply_to!r}."
                        ),
                        "evidence": (
                            f"{where} turn {idx}: reply by {t.speaker} "
                            f"({roles.get(t.speaker, 'UNKNOWN')}) reply_to="
                            f"{t.reply_to!r}, expected {prev.turn_id!r}"
                        ),
                        "repair_hint": (
                            "meetings/transcript.py::walk_chain enforces "
                            "reply_to == prev.turn_id; check the manager's "
                            "reply_to wiring."
                        ),
                    }
                )
            chain.append(t)
            spoken.add(t.speaker)
            prev = t
            idx += 1
        chain_len = len(chain)
        walk_idx = idx

        # Turns after the walked chain: replies are violations (continued past
        # termination, or after a terminal opt_in); opt_ins must be by
        # first-time speakers.
        seen_opt_in = False
        earlier_speakers = {t.speaker for t in chain}
        for j in range(walk_idx, len(turns)):
            t = turns[j]
            if t.turn_kind == "reply":
                if seen_opt_in:
                    findings.append(
                        {
                            "id": f"OPTIN-{seed}-{meeting_index}-{j}",
                            "severity": "high",
                            "title": "Reply turn after a terminal opt_in turn",
                            "claim": (
                                "opt_in turns are terminal and cannot extend "
                                "the chain, but a reply was recorded after an "
                                "opt_in."
                            ),
                            "evidence": (
                                f"{where} turn {j}: reply by {t.speaker} "
                                f"({roles.get(t.speaker, 'UNKNOWN')}) after the "
                                "first opt_in turn"
                            ),
                            "repair_hint": (
                                "PHASE 3 opt-ins never re-enter PHASE 2; check "
                                "the manager's phase ordering."
                            ),
                        }
                    )
                elif termination is not None:
                    findings.append(
                        {
                            "id": f"TERM-{seed}-{meeting_index}-{j}-past",
                            "severity": "high",
                            "title": ("Chain continued past its termination condition"),
                            "claim": (
                                f"Termination condition {termination!r} fired "
                                f"after turn {walk_idx - 1}, but a reply was "
                                f"recorded at turn {j}."
                            ),
                            "evidence": (
                                f"{where} turn {j}: reply by {t.speaker} "
                                f"({roles.get(t.speaker, 'UNKNOWN')}) after "
                                f"termination {termination!r}"
                            ),
                            "repair_hint": (
                                "The §5.2 rule is deterministic; a reply past "
                                "the fired condition means the manager and "
                                "next_chain_step disagree."
                            ),
                        }
                    )
            elif t.turn_kind == "opt_in":
                seen_opt_in = True
                if t.speaker in earlier_speakers:
                    findings.append(
                        {
                            "id": f"OPTIN-{seed}-{meeting_index}-{j}-respoke",
                            "severity": "high",
                            "title": ("opt_in by a player who already took a turn"),
                            "claim": (
                                "Opt-in eligibility requires NOT having spoken "
                                f"this meeting, but {t.speaker!r} already took "
                                "a turn."
                            ),
                            "evidence": (
                                f"{where} turn {j}: opt_in by {t.speaker} "
                                f"({roles.get(t.speaker, 'UNKNOWN')}) who "
                                "already spoke"
                            ),
                            "repair_hint": (
                                "meetings/manager.py::_opt_in_eligible_ids "
                                "filters spoken players; check the spoken-set "
                                "bookkeeping."
                            ),
                        }
                    )
            earlier_speakers.add(t.speaker)

    # ---- Opt-in eligibility re-derivation (deterministic PHASE-3 gate) ----
    structural_chain_end = next(
        (i for i, t in enumerate(turns) if t.turn_kind == "opt_in"), len(turns)
    )
    post_chain = MeetingTranscript(turns=tuple(turns[:structural_chain_end]))
    derived_eligible = _opt_in_eligible_ids(
        transcript=post_chain,
        spoken=frozenset(t.speaker for t in turns[:structural_chain_end]),
        living_ids=living_ids,
    )
    recorded_opt_in_speakers = tuple(
        t.speaker for t in turns[structural_chain_end:] if t.turn_kind == "opt_in"
    )
    if recorded_opt_in_speakers != derived_eligible:
        findings.append(
            {
                "id": f"OPTIN-{seed}-{meeting_index}-eligibility",
                "severity": "high",
                "title": (
                    "Recorded opt_in speakers diverge from the deterministic "
                    "eligibility gate"
                ),
                "claim": (
                    "PHASE-3 eligibility is a pure function of the post-chain "
                    "transcript (co-presence with body room / accused), and "
                    "every eligible player takes exactly one terminal turn; "
                    "the recorded opt_in speakers do not match."
                ),
                "evidence": (
                    f"{where}: recorded opt_in speakers "
                    f"{list(recorded_opt_in_speakers)} vs derived eligible "
                    f"{list(derived_eligible)}"
                ),
                "repair_hint": (
                    "Re-run meetings/manager.py::_opt_in_eligible_ids on the "
                    "post-chain transcript; divergence means the recorded "
                    "transcript was not produced by the committed gate."
                ),
            }
        )

    # ---- Accusations (all turn kinds), 7.12 firewall, dead speakers ----
    # Also: per-turn invalid-accusation-target drops (fb3cfa5 marker on
    # free_text — model-hallucination signal, NOT a violation) and free_text
    # length samples per turn_kind over NON-defaulted turns (a defaulted turn
    # has an empty free_text; the burned-token verbosity lives on the
    # failed_call record instead, handled in the per-game failed-call loop).
    accusations: list[dict[str, Any]] = []
    invalid_accusation_target_drops = 0
    free_text_lengths: dict[str, list[int]] = {"opening": [], "reply": [], "opt_in": []}
    for t in turns:
        speaker_role = roles.get(t.speaker, "UNKNOWN")
        ft = t.free_text or ""
        if _INVALID_ACC_MARKER_PREFIX in ft:
            invalid_accusation_target_drops += ft.count(_INVALID_ACC_MARKER_PREFIX)
        # Strip the audit-trail marker span before measuring length so it doesn't
        # inflate the model's prose length; only measure turns the model actually
        # produced text for (a defaulted turn has empty free_text).
        measured = _INVALID_ACC_MARKER_FULL_RE.sub("", ft)
        if measured.strip():
            free_text_lengths.setdefault(t.turn_kind, []).append(len(measured))
        if t.speaker not in living_ids:
            findings.append(
                {
                    "id": f"DEADSPK-{seed}-{meeting_index}-{t.turn_index}",
                    "severity": "blocking",
                    "title": "Turn spoken by a player dead at the meeting tick",
                    "claim": (
                        "Meeting participants are the living players at the "
                        "meeting tick; a dead player took a turn."
                    ),
                    "evidence": (
                        f"{where} turn {t.turn_index}: speaker {t.speaker} "
                        f"({speaker_role}) is not alive at tick "
                        f"{meeting_entry.tick} "
                        f"(turn_kind={t.turn_kind!r})"
                    ),
                    "repair_hint": (
                        "orchestrator.game._build_participants gates on "
                        "p.alive; a dead speaker means participants were built "
                        "from a stale state."
                    ),
                }
            )
        for c in t.claims:
            if not isinstance(c, AccusationClaim):
                continue
            accused_role = roles.get(c.against, "UNKNOWN")
            accusations.append(
                {
                    "turn_index": t.turn_index,
                    "speaker": t.speaker,
                    "speaker_role": speaker_role,
                    "accused": c.against,
                    "accused_role": accused_role,
                }
            )
            if (
                speaker_role == "IMPOSTOR"
                and accused_role == "IMPOSTOR"
                and c.against != t.speaker
            ):
                findings.append(
                    {
                        "id": f"FIREWALL-{seed}-{meeting_index}-{t.turn_index}",
                        "severity": "blocking",
                        "title": (
                            "Impostor accusation names a fellow impostor "
                            "(7.12 firewall breach)"
                        ),
                        "claim": (
                            "The Task-7.12 teammate guard must drop an "
                            "impostor's accusation of a fellow impostor before "
                            "the turn is recorded; one survived."
                        ),
                        "evidence": (
                            f"{where} turn {t.turn_index} "
                            f"({t.turn_kind}): {t.speaker} (IMPOSTOR) accused "
                            f"{c.against} (IMPOSTOR)"
                        ),
                        "repair_hint": (
                            "Check agents/strategic guard "
                            "drop_teammate_statement_target wiring at the "
                            "manager's per-turn claim chokepoint."
                        ),
                    }
                )

    opt_ins = [
        {
            "turn_index": t.turn_index,
            "speaker": t.speaker,
            "speaker_role": roles.get(t.speaker, "UNKNOWN"),
            "substantive": bool(t.observations or t.claims),
        }
        for t in turns
        if t.turn_kind == "opt_in"
    ]

    # Opt-in corroborations grouped by the player they SUPPORT (Wave-1
    # decomposition: an opt_in volunteer publicly backing an accuser of a true
    # impostor is the "more corroboration would have converted" signal). Count
    # only opt_in turns (the terminal info-share); a CorroborationClaim on a
    # chain turn is a different lever.
    opt_in_corroborations_by_supported: dict[str, int] = {}
    for t in turns:
        if t.turn_kind != "opt_in":
            continue
        for c in t.claims:
            if isinstance(c, CorroborationClaim):
                opt_in_corroborations_by_supported[c.supports] = (
                    opt_in_corroborations_by_supported.get(c.supports, 0) + 1
                )

    # ---- Per-voter rendered §4.6 max suspicion (for the SKIP partition) ----
    # Match each ballot to the voter's vote-prompt llm_call (the call whose
    # prompt carries the rendered "maximum suspicion ... is **X**" line) by
    # agent_id, and regex the rendered max the voter was shown. A voter can have
    # both a turn call and a vote call; only the vote call carries the line.
    # Also parse each voter's rendered §6.6 per-target suspicion GRAPH (Wave-1
    # decomposition): the only place a per-target (not just max) suspicion value
    # survives into the replay, so the decomposition can read the suspicion
    # OTHER voters held for the ejected / accused player.
    rendered_max_by_voter: dict[str, float] = {}
    suspicion_graph_by_voter: dict[str, dict[str, float]] = {}
    for call in meeting_entry.llm_calls:
        if call.agent_id is None:
            continue
        rendered = parse_rendered_max_suspicion(call.prompt)
        if rendered is not None:
            rendered_max_by_voter[call.agent_id] = rendered
        graph = _parse_suspicion_graph(call.prompt)
        if graph:
            suspicion_graph_by_voter[call.agent_id] = graph

    # Per-TARGET rendered suspicion = the MAX value any OTHER voter rendered for
    # that player (a voter holds no row about itself). This is the deterministic
    # "the player's max rendered suspicion from the vote prompts" the lens needs.
    rendered_suspicion_by_target: dict[str, float] = {}
    for voter, graph in suspicion_graph_by_voter.items():
        for pid, sus in graph.items():
            if pid == voter:
                continue
            prior_max = rendered_suspicion_by_target.get(pid)
            if prior_max is None or sus > prior_max:
                rendered_suspicion_by_target[pid] = sus

    # ---- Ballots: roles, skip, follows-chain, dangling reason, firewall ----
    ejected_id = meeting_entry.ejected_player_id
    ejected_role = roles.get(ejected_id) if ejected_id is not None else None
    ballots_out: list[dict[str, Any]] = []
    skip_count = 0
    invalid_ballot_target_drops = 0
    skip_correct = 0
    skip_missed = 0
    skip_unclassified = 0
    threshold_inversions: list[dict[str, Any]] = []
    # Voters who cast a ballot AT the ejected player (Wave-1 decomposition: the
    # ejected player's rendered suspicion among the voters who actually ejected
    # them, read off those voters' own suspicion graphs).
    ejecting_voters: list[str] = []
    # ---- Wave-1-CLOSE per-ballot records (point 6d) ----
    # 10.9.2 REDIRECT records (the headline) and 10.9.1 DEFAULTED-ballot records,
    # both detected on the imported pinned markers so the extractor and the
    # shipped eval.meeting_quality census can never drift. A voter's own §6.6
    # graph (suspicion_graph_by_voter) carries the per-TARGET rendered values the
    # redirect lens needs to confirm the guard's precondition (original below the
    # gate, redirected-to at/above the argmax).
    redirect_records: list[dict[str, Any]] = []
    defaulted_ballot_records: list[dict[str, Any]] = []
    for b in meeting_entry.ballots:
        voter_role = roles.get(b.voter, "UNKNOWN")
        is_skip = b.target == "SKIP"
        target_role = None if is_skip else roles.get(b.target, "UNKNOWN")
        voter_graph = suspicion_graph_by_voter.get(b.voter, {})
        rationale = b.rationale_text or ""

        # ---- 10.9.1 DEFAULTED ballot (VOTE_PARSE_DEFAULT_MARKER is the WHOLE
        # rationale_text) ----
        if _VOTE_PARSE_DEFAULT_MARKER_PREFIX in rationale:
            # The defaulted ballot's own vote call failed before the recording
            # client logged its prompt, so the rendered max is absent from
            # llm_calls. Task 10.12 (audit H-H-2): fall back to the §4.6 max the
            # manager persisted onto the deadline_default failed-call row
            # (rendered_vote_max), so a defaulted ballot's true MUST-vote /
            # MUST-skip verdict is classifiable instead of always "no-render".
            v_rendered = rendered_max_by_voter.get(b.voter)
            if v_rendered is None:
                v_rendered = defaulted_vote_rendered_max.get(b.voter)
            if v_rendered is None:
                verdict = "no-render"
            elif v_rendered >= SKIP_SUSPICION_THRESHOLD:
                verdict = "MUST-vote"
            else:
                verdict = "MUST-skip"
            defaulted_ballot_records.append(
                {
                    "seed": seed,
                    "meeting_index": meeting_index,
                    "voter": b.voter,
                    "voter_role": voter_role,
                    "target": b.target,
                    "rendered_verdict": verdict,
                    "rendered_max": v_rendered,
                    # An IMPOSTOR voter's SKIP under a MUST-vote verdict is the
                    # §7.12 teammate firewall by design (the same exclusion the
                    # shipped decision census applies via
                    # missed_skip_impostor_voters), NOT a missed eject. seed-8 is
                    # this case: a defaulted impostor ballot whose verdict was
                    # MUST-vote -- firewall-correct-SKIP-under-MUST-VOTE, not the
                    # "correct-skip under MUST-skip" the briefed framing claimed.
                    # A CREWMATE MUST-vote default would be a genuine missed eject.
                    "firewall_correct": voter_role == "IMPOSTOR"
                    and verdict == "MUST-vote",
                }
            )

        # ---- 10.9.2 REDIRECT ballot (BALLOT_TARGET_REDIRECT_MARKER prefix) ----
        if _BALLOT_REDIRECT_MARKER_PREFIX in rationale:
            original_target = _parse_redirect_original(rationale)
            original_role = (
                roles.get(original_target, "UNKNOWN")
                if original_target is not None
                else None
            )
            # The voter's OWN rendered suspicion of the original (the guard's
            # precondition: below the gate) and of the recorded redirected-to
            # target (at/above, the argmax over the eligible pool). A SKIP target
            # is the teammate-only-over-gate coercion case.
            original_rendered = (
                voter_graph.get(original_target)
                if original_target is not None
                else None
            )
            redirected_rendered = None if is_skip else voter_graph.get(b.target)
            redirect_records.append(
                {
                    "seed": seed,
                    "meeting_index": meeting_index,
                    "voter": b.voter,
                    "voter_role": voter_role,
                    "original_target": original_target,
                    "original_target_role": original_role,
                    "voter_rendered_suspicion_of_original": original_rendered,
                    # The guard's precondition: the original target's rendered
                    # row is below the gate OR absent (no row == 0.0 in the
                    # verdict math, the F2 seed-12 shape -- a bare verbal
                    # accusation the voter's own graph carries no row for).
                    "original_below_gate": (
                        original_rendered is None
                        or original_rendered < SKIP_SUSPICION_THRESHOLD
                    ),
                    "original_row_absent": original_rendered is None,
                    "redirected_to_target": b.target,
                    "redirected_to_role": target_role,
                    "voter_rendered_suspicion_of_redirect": redirected_rendered,
                    "redirect_at_or_above_gate": (
                        redirected_rendered is not None
                        and redirected_rendered >= SKIP_SUSPICION_THRESHOLD
                    ),
                    "was_coerced_to_SKIP": is_skip,
                }
            )
        # Invalid ballot-target normalization (fb3cfa5): an out-of-roster target
        # is rewritten to SKIP and the original recorded on rationale_text. Count
        # it as a hallucination signal and remember it so the SKIP partition and
        # the threshold-inversion test can exclude these by-design coercions.
        is_invalid_target_skip = _INVALID_VOTE_MARKER_PREFIX in (b.rationale_text or "")
        if is_invalid_target_skip:
            invalid_ballot_target_drops += 1
        # Firewall coercion: an impostor voter whose rendered max is met but who
        # SKIPs to avoid voting a fellow impostor is a by-design protection, not
        # a genuine threshold inversion. Detect by checking whether every living
        # ejection target with suspicion >= threshold is a fellow impostor — we
        # cannot see the per-target graph here, so we approximate conservatively:
        # treat an impostor voter's met-threshold SKIP as a firewall coercion
        # (impostors are the only role the firewall protects), excluded below.
        rendered_max = rendered_max_by_voter.get(b.voter)
        if is_skip:
            skip_count += 1
            if rendered_max is None:
                skip_unclassified += 1
            elif rendered_max < SKIP_SUSPICION_THRESHOLD:
                skip_correct += 1
            else:
                skip_missed += 1
                # Genuine threshold INVERSION = rendered max >= threshold over a
                # living target yet SKIP, MINUS firewall coercions (impostor
                # voter) and invalid-target normalizations.
                if voter_role != "IMPOSTOR" and not is_invalid_target_skip:
                    threshold_inversions.append(
                        {
                            "voter": b.voter,
                            "voter_role": voter_role,
                            "rendered_max": rendered_max,
                        }
                    )
        follows_chain: bool | None = None
        if not is_skip:
            follows_chain = False
            if b.primary_reason_id is not None and b.primary_reason_id in turn_by_id:
                cited = turn_by_id[b.primary_reason_id]
                follows_chain = any(
                    isinstance(c, AccusationClaim) and c.against == b.target
                    for c in cited.claims
                )
        if b.primary_reason_id is not None and b.primary_reason_id not in turn_id_set:
            findings.append(
                {
                    "id": f"DANGLEREASON-{seed}-{meeting_index}-{b.voter}",
                    "severity": "high",
                    "title": (
                        "Ballot primary_reason_id references a turn that does not exist"
                    ),
                    "claim": (
                        "primary_reason_id must reference a MeetingTurn "
                        "turn_id from this meeting's transcript; the recorded "
                        "id is dangling."
                    ),
                    "evidence": (
                        f"{where}: ballot by {b.voter} ({voter_role}) cites "
                        f"{b.primary_reason_id!r}; transcript turn ids are "
                        f"{sorted(turn_id_set)}"
                    ),
                    "repair_hint": (
                        "The vote-ballot prompt enumerates turn ids; a "
                        "hallucinated id should be normalised or rejected at "
                        "parse time."
                    ),
                }
            )
        if b.voter not in living_ids:
            invariant_failures.append(
                f"{where}: ballot voter {b.voter} is not alive at the "
                f"meeting tick {meeting_entry.tick}"
            )
            findings.append(
                {
                    "id": f"DEADVOTE-{seed}-{meeting_index}-{b.voter}",
                    "severity": "blocking",
                    "title": "Ballot cast by a player dead at the meeting tick",
                    "claim": (
                        "Only living participants vote; a dead player's ballot "
                        "was recorded."
                    ),
                    "evidence": (
                        f"{where}: voter {b.voter} ({voter_role}) is not alive "
                        f"at tick {meeting_entry.tick}"
                    ),
                    "repair_hint": (
                        "orchestrator.game._build_participants gates on "
                        "p.alive; a dead voter means ballots were collected "
                        "from a stale roster."
                    ),
                }
            )
        if (
            voter_role == "IMPOSTOR"
            and not is_skip
            and roles.get(b.target) == "IMPOSTOR"
            and b.target != b.voter
        ):
            findings.append(
                {
                    "id": f"FIREWALL-BALLOT-{seed}-{meeting_index}-{b.voter}",
                    "severity": "blocking",
                    "title": (
                        "Impostor ballot targets a fellow impostor "
                        "(7.12 firewall breach)"
                    ),
                    "claim": (
                        "The teammate firewall must keep an impostor from "
                        "voting out a fellow impostor; one ballot breached it."
                    ),
                    "evidence": (
                        f"{where}: ballot by {b.voter} (IMPOSTOR) targets "
                        f"{b.target} (IMPOSTOR)"
                    ),
                    "repair_hint": (
                        "Check the vote-path teammate guard "
                        "(drop_teammate_ballot_target / equivalent) on the "
                        "ballot chokepoint."
                    ),
                }
            )
        if not is_skip and ejected_id is not None and b.target == ejected_id:
            ejecting_voters.append(b.voter)
        ballots_out.append(
            {
                "voter": b.voter,
                "voter_role": voter_role,
                "target": b.target,
                "target_role": target_role,
                # The §4.6 confident-ballot prong input: the recorded tally
                # ejects only if >= 1 leader ballot meets the threshold. The
                # tally-counterfactual lab (experiments/lab) replays variants
                # from these rows, so the field rides along.
                "confidence": b.confidence,
                "primary_reason_id": b.primary_reason_id,
                "follows_chain": follows_chain,
            }
        )

    # ---- Wave-1 decomposition: per-subject classified contradictions + the
    # ejected / accused players' rendered suspicion (point 6b). ----
    # Group every recorded contradiction by each of its subjects, classified
    # with the SAME weak/strong logic the 9.7 detector wrote into the marker.
    contradictions_by_subject: dict[str, list[dict[str, bool]]] = {}
    for contra in meeting_entry.contradictions:
        cls = _classify_contradiction(contra)
        for subject in contra.subjects:
            contradictions_by_subject.setdefault(subject, []).append(cls)

    # ---- Wave-1 contract-input: TESTIMONY RECORDS (point 6c) ----
    # One record per (meeting, verbally-accused LIVING subject of EITHER role).
    # The innocent rows are the cascade-risk input the testimony-ingestion lens
    # (the dominant b1 finding: spoken testimony never enters listeners'
    # beliefs) reads, so this is NOT restricted to impostors. A subject is
    # "verbally accused" iff some turn carries an AccusationClaim against it
    # (the chain-driving vehicle); for each such subject we collect EVERY turn
    # that names it (by any vehicle), the structured flags naming it (with
    # weak/strong class), each living voter's rendered suspicion OF that subject
    # (per-target, not just the max), the ballots cast for it, the plurality
    # winner + margin, and the witnesses' own ballot follow-through.
    #
    # Genuine CANON-interior subjects (Task 10.4, imported detector re-run) —
    # the per-meeting set so the genuine-class records can be assembled with
    # cross-meeting context in the per-game loop.
    ballot_voter_roster = frozenset(b.voter for b in meeting_entry.ballots)
    genuine_subjects = _genuine_subjects(meeting_entry.transcript, ballot_voter_roster)

    # Ballot tallies (non-skip) for plurality + margin, and the set of accusers
    # who followed through on their own target.
    ballot_targets = [b.target for b in meeting_entry.ballots if b.target != "SKIP"]
    target_vote_counts = Counter(ballot_targets)
    plurality_target: str | None = None
    plurality_votes = 0
    plurality_margin = 0
    if target_vote_counts:
        ordered_counts = target_vote_counts.most_common()
        plurality_target, plurality_votes = ordered_counts[0]
        runner_up = ordered_counts[1][1] if len(ordered_counts) > 1 else 0
        plurality_margin = plurality_votes - runner_up

    # Players named by at least one AccusationClaim (excluding self), restricted
    # to the living roster (a verbally-accused dead/hallucinated target is a
    # drop, counted elsewhere).
    accused_subjects = sorted(
        {
            acc["accused"]
            for acc in accusations
            if acc["accused"] != acc["speaker"] and acc["accused"] in living_ids
        }
    )
    testimony_records: list[dict[str, Any]] = []
    for subject in accused_subjects:
        subj_role = roles.get(subject, "UNKNOWN")
        testimony_turns: list[dict[str, Any]] = []
        for t in turns:
            vehicle, obs_backed = _testimony_vehicle(t, subject)
            if vehicle is None:
                continue
            testimony_turns.append(
                {
                    "turn_index": t.turn_index,
                    "speaker": t.speaker,
                    "speaker_role": roles.get(t.speaker, "UNKNOWN"),
                    "turn_kind": t.turn_kind,
                    "vehicle": vehicle,
                    "observation_backed": obs_backed,
                }
            )
        subj_flags = [
            _classify_contradiction(c)
            for c in meeting_entry.contradictions
            if subject in c.subjects
        ]
        n_strong_flags = sum(1 for f in subj_flags if f["strong"])
        # Per-voter rendered suspicion OF this subject: read each LIVING voter's
        # own §6.6 graph for the subject's row. A voter holds no row about
        # itself, so derived=False rows are real renders; if a voter rendered no
        # row for the subject (it held no belief), the value is None (not
        # derivable from the prompt alone). The max-over-others value is the
        # decisive table verdict the §4.6 gate reads.
        per_voter_susp: dict[str, dict[str, Any]] = {}
        for voter in sorted(living_ids):
            graph = suspicion_graph_by_voter.get(voter, {})
            if voter == subject:
                continue
            if subject in graph:
                per_voter_susp[voter] = {
                    "suspicion": graph[subject],
                    "derived": False,
                }
            else:
                per_voter_susp[voter] = {"suspicion": None, "derived": False}
        accusers_of_subject = {
            acc["speaker"] for acc in accusations if acc["accused"] == subject
        }
        ballots_for_subject = target_vote_counts.get(subject, 0)
        witness_follow_through = sum(
            1
            for b in meeting_entry.ballots
            if b.voter in accusers_of_subject and b.target == subject
        )
        testimony_records.append(
            {
                "subject": subject,
                "subject_role": subj_role,
                "is_genuine_class": subject in genuine_subjects,
                "testimony_turns": testimony_turns,
                "n_testimony_turns": len(testimony_turns),
                "accusers": sorted(accusers_of_subject),
                "structured_flags_naming_subject": subj_flags,
                "n_structured_flags": len(subj_flags),
                "n_strong_flags": n_strong_flags,
                "per_voter_rendered_suspicion": per_voter_susp,
                "max_rendered_suspicion": rendered_suspicion_by_target.get(subject),
                "ballots_for_subject": ballots_for_subject,
                "plurality_target": plurality_target,
                "plurality_votes": plurality_votes,
                "plurality_margin": plurality_margin,
                "is_plurality_winner": subject == plurality_target,
                "n_accusers": len(accusers_of_subject),
                "witness_ballot_follow_through": witness_follow_through,
                "ejected": subject == ejected_id,
                "outcome": meeting_entry.outcome,
            }
        )

    # The ejected player's rendered suspicion, two ways: the global max any
    # voter rendered for them, and the max among the voters who actually
    # ejected them (the decisive value).
    ejected_rendered_suspicion = (
        rendered_suspicion_by_target.get(ejected_id) if ejected_id is not None else None
    )
    ejected_rendered_suspicion_among_ejectors: float | None = None
    if ejected_id is not None:
        ej_values = [
            suspicion_graph_by_voter[v][ejected_id]
            for v in ejecting_voters
            if v in suspicion_graph_by_voter
            and ejected_id in suspicion_graph_by_voter[v]
        ]
        if ej_values:
            ejected_rendered_suspicion_among_ejectors = max(ej_values)

    # ---- Wave-1-CLOSE: PRE-VOTE FOLD events (10.7, point 6d) ----
    # Reconstruct each two-witness pre-vote fold by re-running the IMPORTED
    # meetings.transcript.independent_voices over the recorded transcript under
    # the ballot-voter roster (the same roster the live path's
    # derive_belief_evidence used) and keeping every subject whose distinct-voice
    # count meets TESTIMONY_INDEPENDENCE_BAR. The fold is LIVE at record time, so
    # the recorded vote-prompt suspicions ALREADY include the +0.05 bump — we do
    # NOT re-apply it; we only report which listeners' rendered suspicion of the
    # folded subject crossed the §4.6 gate and whether any of them ejected. Voices
    # are the imported predicate verbatim (no approximation): the function exposes
    # the speaker set per subject, so "independent voices" need not be replicated.
    voices = independent_voices(meeting_entry.transcript, roster=ballot_voter_roster)
    prevote_folds: list[dict[str, Any]] = []
    for subject in sorted(voices):
        voice_speakers = voices[subject]
        if len(voice_speakers) < TESTIMONY_INDEPENDENCE_BAR:
            continue
        subj_role = roles.get(subject, "UNKNOWN")
        # The independent voices' backing: for each voice speaker, the observation
        # claim(s) on the turn that named the subject (the fold's relevance-gated,
        # observation-backed, distinct second voice — already validated inside the
        # imported predicate; surfaced here for the lens to confirm distinctness).
        voice_backing: list[dict[str, Any]] = []
        for vsp in voice_speakers:
            vsp_obs: list[str] = []
            for t in turns:
                if t.speaker != vsp:
                    continue
                for o in t.observations:
                    if isinstance(o, SawPlayerObservation):
                        vsp_obs.append(f"saw {o.subject} in {o.room} @t{o.tick}")
                    elif isinstance(o, FoundBodyObservation):
                        vsp_obs.append(f"found_body {o.body_of} in {o.room} @t{o.tick}")
            voice_backing.append(
                {
                    "speaker": vsp,
                    "speaker_role": roles.get(vsp, "UNKNOWN"),
                    "observations": vsp_obs,
                }
            )
        # Listeners (living voters who are not the subject) whose rendered
        # suspicion of the subject is at/above the gate, and whether each ejected.
        listeners_over_gate: list[dict[str, Any]] = []
        for voter in sorted(living_ids):
            if voter == subject:
                continue
            listener_sus = suspicion_graph_by_voter.get(voter, {}).get(subject)
            if listener_sus is None or listener_sus < SKIP_SUSPICION_THRESHOLD:
                continue
            voted_eject = any(
                b.voter == voter and b.target == subject for b in meeting_entry.ballots
            )
            listeners_over_gate.append(
                {
                    "listener": voter,
                    "rendered_suspicion": listener_sus,
                    "voted_to_eject_subject": voted_eject,
                }
            )
        prevote_folds.append(
            {
                "subject": subject,
                "subject_role": subj_role,
                "n_independent_voices": len(voice_speakers),
                "independent_voices": voice_backing,
                "n_listeners_over_gate": len(listeners_over_gate),
                "listeners_over_gate": listeners_over_gate,
                "any_listener_ejected_subject": any(
                    listener["voted_to_eject_subject"]
                    for listener in listeners_over_gate
                ),
                "ballots_for_subject": target_vote_counts.get(subject, 0),
                "ejected": subject == ejected_id,
                "outcome": meeting_entry.outcome,
            }
        )

    # ---- Wave-1-CLOSE: SELF-ACCUSATIONS (point 6d) ----
    # Every accusation where speaker == accused (the lab's emergence class: the
    # game-deciding impostor self-steer the 10.9.2 guard does not cover, since it
    # only constrains the ballot TARGET, not a turn's accusation). For each, did
    # ANY OTHER voter then target the self-accuser (adoption)?
    self_accusation_records: list[dict[str, Any]] = []
    for acc in accusations:
        if acc["accused"] != acc["speaker"]:
            continue
        speaker = acc["speaker"]
        adopters = sorted(
            b.voter
            for b in meeting_entry.ballots
            if b.target == speaker and b.voter != speaker
        )
        self_accusation_records.append(
            {
                "seed": seed,
                "meeting_index": meeting_index,
                "turn_index": acc["turn_index"],
                "speaker": speaker,
                "speaker_role": acc["speaker_role"],
                "adopted_by": adopters,
                "n_adopters": len(adopters),
                "self_accuser_ejected": speaker == ejected_id,
            }
        )

    # ---- Wave-1-CLOSE: EMERGENCY meeting fact (10.8, point 6d) ----
    # A meeting is emergency iff its engine-recorded trigger is "emergency"
    # (re-derived in the per-game walk from MeetingTriggeredEvent.trigger and
    # passed in). The AUTHORITATIVE "carried a body" signal is the engine's
    # MeetingTriggeredEvent.body_id (trigger_body_id) -- an emergency button
    # reports NO corpse, so the engine attaches body_id=None; a non-None body_id
    # on an emergency trigger is the blocking 10.8 violation (the caller's loop
    # raises off `carried_body`). The opening turn's model-authored
    # FoundBodyObservation is SEPARATE: on this 9B set every emergency opening
    # fabricates a found_body in its ReportDocument (a model hallucination, not an
    # engine body), so it is recorded as a signal (`opening_found_body_subjects`)
    # but NEVER drives the blocking finding -- the engine correctly attached no
    # corpse.
    opening_found_body_subjects = (
        [
            o.body_of
            for o in turns[0].observations
            if isinstance(o, FoundBodyObservation)
        ]
        if turns
        else []
    )
    # 10.11.1 emergency-strip telemetry (point 6e, on the 6d emergency aggregate).
    # The deterministic backstop (meetings.manager) STRIPS a fabricated
    # found_body from an EMERGENCY opening and prepends EMERGENCY_BODY_STRIP_MARKER
    # to the recorded free_text (after a single re-ask for a clean opening). On
    # the FINAL recorded transcript a stripped opening therefore carries the
    # marker AND no FoundBodyObservation, so it is the residual-fabrication signal
    # (how often the 9B still tried, despite the v7 no-body prompt + the retry).
    # A found_body that SURVIVED onto an emergency opening (non-empty
    # opening_found_body_subjects on an emergency meeting) is the blocking 10.8
    # leak — the engine attached no corpse (carried_body False) yet a model body
    # leaked past both the strip and the orchestrator's fail-loud assert.
    opening_emergency_strip = bool(turns) and EMERGENCY_BODY_STRIP_MARKER in (
        turns[0].free_text or ""
    )
    is_emergency = trigger_kind == "emergency"
    caller = meeting_entry.triggered_by
    emergency_fact: dict[str, Any] | None = None
    if is_emergency:
        emergency_fact = {
            "seed": seed,
            "meeting_index": meeting_index,
            "meeting_id": mid,
            "caller": caller,
            "caller_role": roles.get(caller, "UNKNOWN"),
            "caller_rendered_max_suspicion": rendered_max_by_voter.get(caller),
            # Engine-authoritative: an emergency trigger must carry no body_id.
            "carried_body": trigger_body_id is not None,
            "trigger_body_id": trigger_body_id,
            # Model-authored opening content (hallucination signal, NOT a body).
            # On the final transcript a SURVIVING found_body on an emergency
            # opening is the blocking leak (the strip + the fail-loud assert both
            # missed it); a stripped one shows as the marker below with an empty
            # subject list.
            "opening_found_body_subjects": opening_found_body_subjects,
            "opening_found_body_survived": bool(opening_found_body_subjects),
            # 10.11.1 residual-fabrication signal: the strip fired on this
            # emergency opening (the 9B fabricated a found_body, the backstop
            # removed it).
            "opening_found_body_stripped": opening_emergency_strip,
            "outcome": meeting_entry.outcome,
            "ejected_player_id": ejected_id,
            "ejected_role": ejected_role,
        }

    kind_counts = Counter(t.turn_kind for t in turns)
    turn_kinds: tuple[TurnKind, ...] = ("opening", "reply", "opt_in")
    return {
        "meeting_id": mid,
        "meeting_index": meeting_index,
        "tick": meeting_entry.tick,
        "trigger_kind": trigger_kind,
        "triggered_by": meeting_entry.triggered_by,
        "triggered_by_role": roles.get(meeting_entry.triggered_by, "UNKNOWN"),
        "outcome": meeting_entry.outcome,
        "ejected_player_id": ejected_id,
        "ejected_role": ejected_role,
        "living_player_count": len(living_ids),
        "n_turns": len(turns),
        "turn_kind_counts": {k: kind_counts.get(k, 0) for k in turn_kinds},
        "chain_length": chain_len,
        "termination_condition": termination,
        "is_canonically_ordered": canonical,
        "opening_has_accusation": (
            any(isinstance(c, AccusationClaim) for c in turns[0].claims)
            if turns
            else False
        ),
        "accusations": accusations,
        "opt_ins": opt_ins,
        "opt_in_eligible_derived": list(derived_eligible),
        "ballots": ballots_out,
        "skip_count": skip_count,
        "skip_correct": skip_correct,
        "skip_missed": skip_missed,
        "skip_unclassified": skip_unclassified,
        "threshold_inversions": threshold_inversions,
        "invalid_accusation_target_drops": invalid_accusation_target_drops,
        "invalid_ballot_target_drops": invalid_ballot_target_drops,
        "free_text_lengths": free_text_lengths,
        "n_contradictions": len(meeting_entry.contradictions),
        # Wave-1 decomposition payloads (assembled with cross-meeting context
        # in the per-game loop).
        "contradictions_by_subject": contradictions_by_subject,
        "opt_in_corroborations_by_supported": opt_in_corroborations_by_supported,
        "rendered_suspicion_by_target": rendered_suspicion_by_target,
        "ejected_rendered_suspicion": ejected_rendered_suspicion,
        "ejected_rendered_suspicion_among_ejectors": (
            ejected_rendered_suspicion_among_ejectors
        ),
        "ejecting_voters": ejecting_voters,
        # Wave-1 contract-input payloads (point 6c).
        "testimony_records": testimony_records,
        "genuine_subjects": sorted(genuine_subjects),
        "suspicion_graph_by_voter": suspicion_graph_by_voter,
        "ballot_voter_roster": sorted(ballot_voter_roster),
        "plurality_target": plurality_target,
        "plurality_margin": plurality_margin,
        # Wave-1-CLOSE payloads (point 6d).
        "redirect_records": redirect_records,
        "defaulted_ballot_records": defaulted_ballot_records,
        "prevote_folds": prevote_folds,
        "self_accusation_records": self_accusation_records,
        "emergency_fact": emergency_fact,
        "is_emergency": is_emergency,
        "opening_fabricated_found_body": bool(opening_found_body_subjects),
    }


def main() -> int:
    game_map = load_canonical_map()
    roster = json.loads((SAMPLE_DIR / "roster.json").read_text(encoding="utf-8"))
    num_players = int(roster["num_players"])
    num_impostors = int(roster["num_impostors"])
    tasks_per_crewmate = int(roster["tasks_per_crewmate"])

    replay_paths = sorted(
        SAMPLE_DIR.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    )
    games_analyzed = len(replay_paths)

    games: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    # Self-check accumulators.
    total_meeting_records = 0
    invariant_failures: list[str] = []

    # Aggregates.
    win_split: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    total_kills = 0
    impostor_victim_kills = 0
    total_meetings = 0
    ejections_by_role: dict[str, int] = {}
    total_calls = 0
    total_failed_calls = 0
    agg_input_tokens = 0
    agg_output_tokens = 0
    agg_cost = 0.0
    no_game_over = 0
    # v2 chain/ballot aggregates.
    trigger_kind_counts: dict[str, int] = {}
    total_ballots = 0
    total_skip_ballots = 0
    chain_length_hist: dict[str, int] = {}
    termination_counts: dict[str, int] = {}
    opening_accusation_count = 0
    accusations_total = 0
    accusations_at_impostors = 0
    accusations_at_innocents = 0
    self_accusations = 0
    accusations_at_unknown = 0
    opt_in_turns_total = 0
    opt_in_substantive = 0
    opt_in_eligible_total = 0
    ballots_non_skip = 0
    ballots_follow_chain = 0
    ballots_non_skip_null_reason = 0
    total_contradictions = 0
    # v3 conversion / 9B-artifact aggregates.
    ejections_total = 0
    ejections_impostor = 0
    wrong_ejections: list[dict[str, Any]] = []
    skip_correct_total = 0
    skip_missed_total = 0
    skip_unclassified_total = 0
    threshold_inversions_all: list[dict[str, Any]] = []
    invalid_accusation_target_drops_total = 0
    invalid_ballot_target_drops_total = 0
    invalid_accusation_target_seeds: set[int] = set()
    invalid_ballot_target_seeds: set[int] = set()
    free_text_len_samples: dict[str, list[int]] = {
        "opening": [],
        "reply": [],
        "opt_in": [],
    }
    defaulted_turns: list[dict[str, Any]] = []
    defaulted_turn_unparsed = 0
    duplicate_failed_call_rows = 0
    duplicate_failed_call_input_tokens = 0
    duplicate_failed_call_output_tokens = 0
    duplicate_failed_call_seeds: set[int] = set()
    # Wave-1 decomposition record sets (point 6b — re-derived, NOT trusting
    # PR #138 numbers). Assembled per game so cross-meeting accusation history
    # is in scope (the accumulator-carry question).
    per_ejection_evidence: list[dict[str, Any]] = []
    missed_conversions: list[dict[str, Any]] = []
    zero_contradiction_ejections: list[dict[str, Any]] = []
    # Wave-1 contract-input record sets (point 6c — the headline lens depends
    # on these). Testimony rows for EVERY verbally-accused living subject of
    # either role; genuine-class rows (10.4 imported definition); accumulator
    # trajectory rows; opening-validation retry rows (10.3).
    testimony_records_all: list[dict[str, Any]] = []
    genuine_class_records: list[dict[str, Any]] = []
    accumulator_trajectories: list[dict[str, Any]] = []
    # Genuine-class cross-check accumulators (vs the shipped 10.4 metric).
    genuine_supplied_rederived = 0
    genuine_converted_rederived = 0
    # 10.3 opening-retry aggregates.
    opening_defaults = 0
    opening_retries_recovered = 0
    opening_retry_extra_calls = 0
    opening_retry_extra_input_tokens = 0
    opening_retry_extra_output_tokens = 0
    meetings_lost_opening = 0
    opening_retry_records: list[dict[str, Any]] = []
    # Wave-1-CLOSE record sets (point 6d — the close-gate lenses depend on these).
    redirect_records_all: list[dict[str, Any]] = []
    defaulted_ballot_records_all: list[dict[str, Any]] = []
    prevote_fold_records_all: list[dict[str, Any]] = []
    self_accusation_records_all: list[dict[str, Any]] = []
    emergency_meeting_records: list[dict[str, Any]] = []
    # Wave-2 CRATER record sets (point 6e — the headline lens depends on these).
    # do_task INTEGRITY: every walked TaskProgressed/TaskCompleted event by an
    # IMPOSTOR actor (the 10.14 invariant — a fake task must NEVER advance a real
    # task instance; the engine rejects the pretend id, so this list MUST be
    # empty, and a single entry is a BLOCKING finding). The per-role task-advance
    # tallies ride along for the integrity-summary.
    impostor_task_advances: list[dict[str, Any]] = []
    crew_task_progress_events = 0
    crew_task_completed_events = 0
    # Win-decision attribution (the R1 verdict input): per game, was the win
    # eject-DECIDED (both impostors removed by the meeting layer -> CREWMATE_EJECT)
    # or STOPWATCH (CREWMATE_TASKS fired with an impostor still alive)?
    win_decision_records: list[dict[str, Any]] = []
    # Inform-channel conversion records (10.16 fifth channel): impostor ejections
    # whose channel decomposition credits the single-witness inform.
    inform_channel_conversions: list[dict[str, Any]] = []

    for path in replay_paths:
        seed = int(path.stem.rsplit("-", 1)[1])
        game_id = f"headless-seed-{seed}"

        # 1) Ground-truth roles.
        init_state = seed_initial_state(
            seed=seed,
            game_map=game_map,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )
        roles = {pid: p.role for pid, p in init_state.players.items()}
        found_impostors = sum(1 for r in roles.values() if r == "IMPOSTOR")
        if found_impostors != num_impostors:
            invariant_failures.append(
                f"seed {seed}: found {found_impostors} impostors, "
                f"roster says {num_impostors}"
            )

        # 2) Reconstruct resolved events by re-running the engine.
        entries = read_all_entries(path)
        replay_entries = [e for e in entries if isinstance(e, ReplayEntry)]
        meeting_entries = [e for e in entries if isinstance(e, MeetingReplayEntry)]
        failed_call_entries = [
            e for e in entries if isinstance(e, FailedCallReplayEntry)
        ]
        game_end = next((e for e in entries if isinstance(e, GameEndReplayEntry)), None)
        meeting_by_tick = {e.tick: e for e in meeting_entries}
        total_meeting_records += len(meeting_entries)

        # Meetings whose OPENING defaulted (exhausted its single retry): the
        # recorded opening is the husk. Precomputed from the deadline_default
        # rows so the recovered-retry detector can EXCLUDE them — a defaulted
        # opening's two opening-slot llm_calls are burned attempts that ended in
        # a default, NOT a recovery (their waste is attributed to the default
        # bucket below, never double-counted as a recovery).
        opening_defaulted_meeting_ids: set[str] = set()
        # Persisted §4.6 verdict max for each DEFAULTED vote (Task 10.12, audit
        # H-H-2): {meeting_id: {voter: rendered_max}}. A defaulted ballot's vote
        # call failed before the recording client logged its prompt, so the
        # rendered max is recoverable only from the failed-call row the manager
        # stamped it onto -- absent for committed single-era replays (no field).
        defaulted_vote_rendered_max_by_meeting: dict[str, dict[str, float]] = {}
        for fc in failed_call_entries:
            if fc.error_type != "deadline_default":
                continue
            m = _DEFAULTED_TURN_RE.search(fc.error_message)
            if m is not None and m.group("kind") == "opening":
                opening_defaulted_meeting_ids.add(fc.meeting_id)
            if fc.rendered_vote_max is not None:
                vote_match = _DEFAULTED_VOTE_RE.match(fc.error_message)
                if vote_match is not None:
                    defaulted_vote_rendered_max_by_meeting.setdefault(
                        fc.meeting_id, {}
                    )[vote_match.group("voter")] = fc.rendered_vote_max

        kills: list[dict[str, Any]] = []
        deaths: set[str] = set()
        meetings_out: list[dict[str, Any]] = []
        # Win-condition-gap tracking: the first tick at which alive impostors hit 0.
        first_zero_impostor_tick: int | None = None

        state = init_state
        last_state_for_final = state
        meeting_index = 0

        for entry in replay_entries:
            actions = _deserialize_actions(list(entry.actions))
            state, events = advance_tick(state, actions, game_map=game_map)

            # State-hash self-check (replay determinism; the whole audit trusts
            # this reconstruction).
            actual = _state_hash(state)
            if actual != entry.state_hash:
                invariant_failures.append(
                    f"seed {seed} tick {entry.tick}: state-hash mismatch "
                    f"(recorded {entry.state_hash[:12]}, "
                    f"reconstructed {actual[:12]})"
                )

            for ev in events:
                if isinstance(ev, KilledEvent):
                    victim_role = roles.get(ev.target, "UNKNOWN")
                    killer_role = roles.get(ev.actor, "UNKNOWN")
                    kills.append(
                        {
                            "tick": ev.tick,
                            "killer": ev.actor,
                            "killer_role": killer_role,
                            "victim": ev.target,
                            "victim_role": victim_role,
                            "room": ev.room,
                        }
                    )
                    deaths.add(ev.target)
                    total_kills += 1
                    if victim_role == "IMPOSTOR":
                        impostor_victim_kills += 1
                        findings.append(
                            {
                                "id": f"KILL-IMP-{seed}-{ev.tick}",
                                "severity": "blocking",
                                "title": "Impostor killed a fellow impostor",
                                "claim": (
                                    "A resolved kill has victim_role==IMPOSTOR — an "
                                    "impostor was killed by another player, which "
                                    "the engine should never produce in a normal game."
                                ),
                                "evidence": (
                                    f"seed {seed} tick {ev.tick}: {ev.actor} "
                                    f"({killer_role}) killed {ev.target} (IMPOSTOR) "
                                    f"in {ev.room}"
                                ),
                                "repair_hint": (
                                    "Inspect engine.rules.resolve_kill / the agent "
                                    "target selection that produced an impostor-on-"
                                    "impostor kill; confirm role-aware target "
                                    "filtering for impostor kill intents."
                                ),
                            }
                        )
                elif isinstance(ev, ActionRejectedEvent):
                    category = _classify_rejection(ev.reason)
                    if category is not None:
                        # Severity: dead/unknown-player rejections are downstream
                        # symptoms of same-tick kill races (the actor died earlier
                        # in this tick's action ordering) — informational, not an
                        # independent hard violation. Cross-room / non-adjacent /
                        # ineligible-report are intent-generation waste -> high.
                        if category == "dead_or_unknown_player_action":
                            sev = "informational"
                        else:
                            sev = "high"
                        findings.append(
                            {
                                "id": f"REJ-{category}-{seed}-{ev.tick}",
                                "severity": sev,
                                "title": (
                                    f"Recorded action rejected by engine ({category})"
                                ),
                                "claim": (
                                    "The recorded action stream queued an action the "
                                    "engine refused: "
                                    f"{ev.reason!r}."
                                ),
                                "evidence": (
                                    f"seed {seed} tick {ev.tick}: actor {ev.actor} "
                                    f"({roles.get(ev.actor, 'UNKNOWN')}) action "
                                    f"{ev.action!r} rejected: {ev.reason!r}"
                                ),
                                "repair_hint": (
                                    "Trace the agent/orchestrator path that emitted "
                                    "this action; a producer that queues "
                                    "engine-illegal actions wastes a turn (the agent "
                                    "no-ops) and signals an intent-generation bug."
                                ),
                            }
                        )
                elif isinstance(ev, (TaskProgressedEvent, TaskCompletedEvent)):
                    # do_task INTEGRITY (Task 10.14, point 6e). A real task
                    # advance/completion by an IMPOSTOR is the crater's inviolable
                    # invariant breach: the blending lever's fake do_task uses a
                    # PRETEND map task id the impostor does not OWN, which the
                    # engine ALWAYS rejects (``_resolve_owned_task_instance``
                    # returns None -> ActionRejectedEvent "actor owns no task
                    # instance for map task"), so it can never reach the real
                    # CREWMATE_TASKS denominator. A walked TaskProgressed /
                    # TaskCompleted event whose actor re-seeds to IMPOSTOR means a
                    # fake task DID advance a real instance -> BLOCKING (a fake
                    # task that helps the crew win, the 10.14 DoD's one
                    # inviolable). A crew advance is normal play, tallied for the
                    # integrity summary.
                    actor_role = roles.get(ev.actor, "UNKNOWN")
                    if actor_role == "IMPOSTOR":
                        impostor_task_advances.append(
                            {
                                "seed": seed,
                                "tick": ev.tick,
                                "actor": ev.actor,
                                "task_id": ev.task_id,
                                "completed": isinstance(ev, TaskCompletedEvent),
                            }
                        )
                        findings.append(
                            {
                                "id": f"IMPTASK-{seed}-{ev.tick}-{ev.actor}",
                                "severity": "blocking",
                                "title": (
                                    "Impostor do_task advanced a real task instance "
                                    "(10.14 fake-task integrity breach)"
                                ),
                                "claim": (
                                    "A walked TaskProgressed/TaskCompleted event has "
                                    "an IMPOSTOR actor — the blending lever's pretend "
                                    "do_task must never advance a real task instance "
                                    "(it uses an unowned map id the engine rejects), "
                                    "so a fake task reached the real CREWMATE_TASKS "
                                    "denominator."
                                ),
                                "evidence": (
                                    f"seed {seed} tick {ev.tick}: {ev.actor} "
                                    f"(IMPOSTOR) advanced map task {ev.task_id!r} "
                                    f"(completed={isinstance(ev, TaskCompletedEvent)})"
                                ),
                                "repair_hint": (
                                    "observation/service.impostor_pretend_task_id "
                                    "must surface only UNOWNED map task ids, and the "
                                    "engine's _resolve_owned_task_instance must reject "
                                    "them; trace how an impostor came to own / advance "
                                    "a real instance."
                                ),
                            }
                        )
                    elif isinstance(ev, TaskCompletedEvent):
                        crew_task_completed_events += 1
                    else:
                        crew_task_progress_events += 1

            # Track alive impostors AFTER this tick resolved.
            alive_impostors = sum(
                1
                for pid, p in state.players.items()
                if p.alive and roles.get(pid) == "IMPOSTOR"
            )
            if alive_impostors == 0 and first_zero_impostor_tick is None:
                first_zero_impostor_tick = entry.tick

            last_state_for_final = state

            if state.phase == "GAME_OVER":
                break

            if state.phase != "MEETING":
                continue

            # Meeting resolved this tick.
            meeting_entry = meeting_by_tick.get(entry.tick)
            if meeting_entry is None:
                # Partial replay (meeting opened, never resolved). Stop the walk.
                break

            # Trigger body id (for corpse consumption) + trigger kind.
            body_id: str | None = None
            trigger_kind: str | None = None
            for ev in events:
                if isinstance(ev, MeetingTriggeredEvent):
                    body_id = ev.body_id
                    trigger_kind = ev.trigger

            # Schema-verified against meetings/schemas.py::MeetingResult
            # (Task 8.7 shape): meeting_id, triggered_by,
            # trigger_tick<-entry.tick, outcome, ejected_player_id, ballots,
            # contradictions, transcript (turns-based MeetingTranscript).
            # Mirrors api.replay_loader._meeting_result_from_entry.
            result = MeetingResult(
                meeting_id=meeting_entry.meeting_id,
                triggered_by=meeting_entry.triggered_by,
                trigger_tick=meeting_entry.tick,
                outcome=meeting_entry.outcome,
                ejected_player_id=meeting_entry.ejected_player_id,
                ballots=meeting_entry.ballots,
                contradictions=meeting_entry.contradictions,
                transcript=meeting_entry.transcript,
            )

            # Cheap cross-check: the recorded pre-meeting hash must equal this
            # tick's recorded post-tick hash (the state the meeting ran on).
            if meeting_entry.state_hash_before != entry.state_hash:
                invariant_failures.append(
                    f"seed {seed} meeting {meeting_entry.meeting_id}: "
                    "state_hash_before does not match the trigger tick's "
                    "state_hash"
                )

            # Living players at the meeting tick == the participant roster
            # (one MeetingParticipant per living player).
            living_ids = frozenset(pid for pid, p in state.players.items() if p.alive)

            m_facts = _analyze_meeting(
                seed=seed,
                meeting_index=meeting_index,
                meeting_entry=meeting_entry,
                trigger_kind=trigger_kind,
                trigger_body_id=body_id,
                roles=roles,
                living_ids=living_ids,
                findings=findings,
                invariant_failures=invariant_failures,
                defaulted_vote_rendered_max=defaulted_vote_rendered_max_by_meeting.get(
                    meeting_entry.meeting_id, {}
                ),
            )
            meetings_out.append(m_facts)
            total_meetings += 1

            # v2 aggregates from the per-meeting facts.
            if trigger_kind is not None:
                trigger_kind_counts[trigger_kind] = (
                    trigger_kind_counts.get(trigger_kind, 0) + 1
                )
            total_ballots += len(m_facts["ballots"])
            total_skip_ballots += m_facts["skip_count"]
            chain_key = str(m_facts["chain_length"])
            chain_length_hist[chain_key] = chain_length_hist.get(chain_key, 0) + 1
            term_key = m_facts["termination_condition"] or "VIOLATION_UNDETERMINED"
            termination_counts[term_key] = termination_counts.get(term_key, 0) + 1
            if m_facts["opening_has_accusation"]:
                opening_accusation_count += 1
            for acc in m_facts["accusations"]:
                accusations_total += 1
                if acc["accused"] == acc["speaker"]:
                    self_accusations += 1
                elif acc["accused_role"] == "IMPOSTOR":
                    accusations_at_impostors += 1
                elif acc["accused_role"] == "CREWMATE":
                    accusations_at_innocents += 1
                else:
                    accusations_at_unknown += 1
            opt_in_turns_total += len(m_facts["opt_ins"])
            opt_in_substantive += sum(1 for o in m_facts["opt_ins"] if o["substantive"])
            opt_in_eligible_total += len(m_facts["opt_in_eligible_derived"])
            for b in m_facts["ballots"]:
                if b["target"] == "SKIP":
                    continue
                ballots_non_skip += 1
                if b["follows_chain"] is True:
                    ballots_follow_chain += 1
                if b["primary_reason_id"] is None:
                    ballots_non_skip_null_reason += 1
            total_contradictions += m_facts["n_contradictions"]

            # v3 conversion / 9B-artifact aggregates.
            skip_correct_total += m_facts["skip_correct"]
            skip_missed_total += m_facts["skip_missed"]
            skip_unclassified_total += m_facts["skip_unclassified"]
            for inv in m_facts["threshold_inversions"]:
                threshold_inversions_all.append({"seed": seed, **inv})
            invalid_accusation_target_drops_total += m_facts[
                "invalid_accusation_target_drops"
            ]
            invalid_ballot_target_drops_total += m_facts["invalid_ballot_target_drops"]
            if m_facts["invalid_accusation_target_drops"]:
                invalid_accusation_target_seeds.add(seed)
            if m_facts["invalid_ballot_target_drops"]:
                invalid_ballot_target_seeds.add(seed)
            for kind, lengths in m_facts["free_text_lengths"].items():
                free_text_len_samples[kind].extend(lengths)

            # ---- Wave-1-CLOSE aggregation (point 6d) ----
            redirect_records_all.extend(m_facts["redirect_records"])
            defaulted_ballot_records_all.extend(m_facts["defaulted_ballot_records"])
            for fold in m_facts["prevote_folds"]:
                prevote_fold_records_all.append(
                    {"seed": seed, "meeting_index": m_facts["meeting_index"], **fold}
                )
            self_accusation_records_all.extend(m_facts["self_accusation_records"])
            if m_facts["emergency_fact"] is not None:
                emergency_meeting_records.append(m_facts["emergency_fact"])
                # 10.8 invariant: an emergency trigger must carry no engine body
                # (body_id is None) — the emergency button reports no corpse. A
                # non-None body_id on an emergency trigger is the blocking
                # violation. NOTE: a model-FABRICATED found_body in the opening's
                # ReportDocument is NOT this (the engine attached no body); it is
                # recorded as a hallucination signal, never a finding.
                if m_facts["emergency_fact"]["carried_body"]:
                    findings.append(
                        {
                            "id": f"EMERGENCY-BODY-{seed}-{m_facts['meeting_index']}",
                            "severity": "blocking",
                            "title": (
                                "Emergency meeting carried an engine-attached body"
                            ),
                            "claim": (
                                "An emergency-triggered meeting must carry no "
                                "engine body (the emergency button reports no "
                                "corpse); the MeetingTriggeredEvent carries a "
                                "non-None body_id."
                            ),
                            "evidence": (
                                f"seed {seed} meeting {m_facts['meeting_index']} "
                                f"({m_facts['emergency_fact']['meeting_id']}): "
                                "emergency trigger but body_id="
                                f"{m_facts['emergency_fact']['trigger_body_id']!r}"
                            ),
                            "repair_hint": (
                                "Trace engine.tick's meeting-trigger path; an "
                                "emergency trigger carrying a body_id means the "
                                "trigger classification or corpse attachment "
                                "mislabeled a body report as emergency."
                            ),
                        }
                    )
                # 10.11.1 EMERGENCY-BACKSTOP LEAK (point 5a / 6d): a found_body
                # that SURVIVED onto the FINAL recorded emergency opening turn is
                # the blocking leak -- the retry-then-strip backstop AND the
                # orchestrator's fail-loud assert both missed it (the engine
                # attached no corpse, carried_body False, yet a model body remains
                # on the opening). A found_body the backstop STRIPPED is gone from
                # the recorded turn, so its PRESENCE on the final transcript is the
                # leak. On this baseline 0; a single one is blocking.
                if m_facts["emergency_fact"]["opening_found_body_survived"]:
                    findings.append(
                        {
                            "id": (
                                f"EMERGENCY-BODYLEAK-{seed}-{m_facts['meeting_index']}"
                            ),
                            "severity": "blocking",
                            "title": (
                                "Fabricated found_body survived onto an emergency "
                                "opening (10.11.1 backstop leak)"
                            ),
                            "claim": (
                                "The 10.11.1 retry-then-strip backstop must remove a "
                                "fabricated found_body from an emergency opening "
                                "(the emergency button reports no corpse), and the "
                                "orchestrator fail-loud asserts none remains; a "
                                "found_body survived onto the final recorded "
                                "emergency opening turn."
                            ),
                            "evidence": (
                                f"seed {seed} meeting {m_facts['meeting_index']} "
                                f"({m_facts['emergency_fact']['meeting_id']}): "
                                "emergency opening carries found_body subjects "
                                f"{m_facts['emergency_fact']['opening_found_body_subjects']!r} "
                                "(engine body_id None)"
                            ),
                            "repair_hint": (
                                "Trace meetings/manager.py's emergency opening "
                                "retry-then-strip path and the orchestrator's "
                                "fail-loud assert; a survived found_body means the "
                                "strip did not fire or ran on stale turn content."
                            ),
                        }
                    )

            ejected_id = meeting_entry.ejected_player_id
            ejected_role = roles.get(ejected_id) if ejected_id is not None else None
            if ejected_id is not None and ejected_role is not None:
                ejections_by_role[ejected_role] = (
                    ejections_by_role.get(ejected_role, 0) + 1
                )
                ejections_total += 1
                if ejected_role == "IMPOSTOR":
                    ejections_impostor += 1
                elif ejected_role == "CREWMATE":
                    wrong_ejections.append({"seed": seed, "ejected_player": ejected_id})

            # Per-call token totals from this meeting's llm_calls.
            for call in meeting_entry.llm_calls:
                total_calls += 1
                agg_input_tokens += call.input_tokens
                agg_output_tokens += call.output_tokens
                agg_cost += call.cost_usd

            # ---- 10.3 OPENING-VALIDATION RETRY DETECTION (point 6c) ----
            # The opening is the only turn collected with retries=1: a
            # narration-only / guard-emptied / schema-invalid opening that
            # RETURNED text consumes an attempt and re-asks once. In headless
            # Ollama those returned-but-rejected attempts are LOGGED in
            # llm_calls (the recording client saw the text; the manager-side
            # validation rejected it AFTER logging, so extract_parse_failure
            # returns None and no separate failed_call row is written). So a
            # RECOVERED opening retry surfaces as >1 opening-slot llm_call for
            # the opener (the recorded opening's speaker); the extra call(s) are
            # the burned retry attempt(s). An opening that EXHAUSTED its retry
            # surfaces instead as a deadline_default failed_call row (counted in
            # the failed-call loop below, where turn_kind=="opening").
            opener = (
                meeting_entry.transcript.turns[0].speaker
                if meeting_entry.transcript.turns
                else None
            )
            opening_calls_by_agent: dict[str, list[Any]] = {}
            for call in meeting_entry.llm_calls:
                if call.agent_id is None:
                    continue
                if _classify_call_slot(call.prompt) == "opening":
                    opening_calls_by_agent.setdefault(call.agent_id, []).append(call)
            # A RECOVERED retry is an opener with >1 opening-slot call whose
            # opening did NOT ultimately default (a defaulted opening's extra
            # calls are burned-then-defaulted, attributed below). The earliest
            # opening-slot calls are the burned attempt(s); the last recorded as
            # the opening.
            opener_defaulted = meeting_entry.meeting_id in opening_defaulted_meeting_ids
            if opener is not None and not opener_defaulted:
                opener_opening_calls = opening_calls_by_agent.get(opener, [])
                extra = max(0, len(opener_opening_calls) - 1)
                if extra > 0:
                    opening_retries_recovered += 1
                    opening_retry_extra_calls += extra
                    burned = opener_opening_calls[:extra]
                    extra_in = sum(c.input_tokens for c in burned)
                    extra_out = sum(c.output_tokens for c in burned)
                    opening_retry_extra_input_tokens += extra_in
                    opening_retry_extra_output_tokens += extra_out
                    opening_retry_records.append(
                        {
                            "seed": seed,
                            "meeting_index": meeting_index,
                            "meeting_id": meeting_entry.meeting_id,
                            "opener": opener,
                            "opener_role": roles.get(opener, "UNKNOWN"),
                            "extra_opening_calls": extra,
                            "extra_input_tokens": extra_in,
                            "extra_output_tokens": extra_out,
                            "recovered_accusation": m_facts["opening_has_accusation"],
                            "outcome": "recovered",
                        }
                    )

            # ---- 10.4 GENUINE-CLASS records + cross-check (point 6b/6c) ----
            # m_facts["genuine_subjects"] is the imported-detector re-run over
            # this meeting's transcript (non-endpoint alibi_vs_sighting). Keep
            # the true-impostor subset as SUPPLIED, CONVERTED when this meeting
            # ejected that impostor — byte-equal to the shipped
            # compute_genuine_class_conversion (asserted as an invariant after
            # the walk).
            for subject in m_facts["genuine_subjects"]:
                if roles.get(subject) != "IMPOSTOR":
                    continue
                genuine_supplied_rederived += 1
                converted = (
                    meeting_entry.outcome == "EJECTED"
                    and meeting_entry.ejected_player_id == subject
                )
                if converted:
                    genuine_converted_rederived += 1
                # Find this subject's strong/weak markers + testimony summary
                # from its testimony record (if it was verbally accused).
                t_rec = next(
                    (
                        r
                        for r in m_facts["testimony_records"]
                        if r["subject"] == subject
                    ),
                    None,
                )
                genuine_class_records.append(
                    {
                        "seed": seed,
                        "meeting_index": meeting_index,
                        "subject": subject,
                        "subject_role": roles.get(subject, "UNKNOWN"),
                        "n_strong_flags": (
                            t_rec["n_strong_flags"] if t_rec is not None else None
                        ),
                        "n_structured_flags": (
                            t_rec["n_structured_flags"] if t_rec is not None else None
                        ),
                        "verbally_accused": t_rec is not None,
                        "max_rendered_suspicion": m_facts[
                            "rendered_suspicion_by_target"
                        ].get(subject),
                        "ballots_for_subject": (
                            t_rec["ballots_for_subject"] if t_rec is not None else 0
                        ),
                        "converted": bool(converted),
                        "outcome": meeting_entry.outcome,
                    }
                )

            state, post_events = apply_meeting_result(
                state,
                result,
                game_map=game_map,
                triggering_body_id=body_id,
            )
            after = _state_hash(state)
            if after != meeting_entry.state_hash_after:
                invariant_failures.append(
                    f"seed {seed} meeting {meeting_entry.meeting_id}: "
                    f"post-meeting state-hash mismatch"
                )
            meeting_index += 1

            # Re-track alive impostors after the ejection.
            alive_impostors = sum(
                1
                for pid, p in state.players.items()
                if p.alive and roles.get(pid) == "IMPOSTOR"
            )
            if alive_impostors == 0 and first_zero_impostor_tick is None:
                first_zero_impostor_tick = meeting_entry.tick

            last_state_for_final = state
            if state.phase == "GAME_OVER":
                break

        # Failed-call accounting (these carry burned tokens for the aborted run).
        # On the 9B set these are FAIL-SOFT defaulted turns (lens H): a turn whose
        # structured output truncated at the output cap so the manager defaulted
        # the turn and the meeting still resolved. The turn coordinates
        # (turn_kind / turn_index / speaker) are encoded in the error_message
        # ("reply turn (turn 1) defaulted (validation); p-9 submitted no turn ...").
        failed_calls_out: list[dict[str, Any]] = []
        seen_failed_call_keys: set[tuple[Any, ...]] = set()
        for fc in failed_call_entries:
            total_failed_calls += 1
            total_calls += 1
            agg_input_tokens += fc.input_tokens
            agg_output_tokens += fc.output_tokens
            agg_cost += fc.cost_usd
            # Detect byte-identical duplicate failed_call rows (the same
            # defaulted-turn failure recorded twice; seeds 8/36/39). The key
            # spans every distinguishing field, so two genuinely-distinct
            # failures never collide.
            fc_key = (
                fc.meeting_id,
                fc.tick,
                fc.error_message,
                fc.raw_response,
                fc.input_tokens,
                fc.output_tokens,
            )
            if fc_key in seen_failed_call_keys:
                duplicate_failed_call_rows += 1
                duplicate_failed_call_input_tokens += fc.input_tokens
                duplicate_failed_call_output_tokens += fc.output_tokens
                duplicate_failed_call_seeds.add(seed)
            seen_failed_call_keys.add(fc_key)
            parsed = _DEFAULTED_TURN_RE.search(fc.error_message)
            turn_kind = parsed.group("kind") if parsed else None
            turn_index = int(parsed.group("index")) if parsed else None
            speaker = parsed.group("speaker") if parsed else None
            if fc.error_type == "deadline_default":
                if parsed is not None:
                    fc_speaker = parsed.group("speaker")
                    defaulted_turns.append(
                        {
                            "seed": seed,
                            "meeting_id": fc.meeting_id,
                            "tick": fc.tick,
                            "turn_index": turn_index,
                            "turn_kind": turn_kind,
                            "speaker": fc_speaker,
                            "speaker_role": roles.get(fc_speaker, "UNKNOWN"),
                            "output_tokens": fc.output_tokens,
                        }
                    )
                else:
                    defaulted_turn_unparsed += 1
            failed_calls_out.append(
                {
                    "meeting_id": fc.meeting_id,
                    "tick": fc.tick,
                    "model": fc.model,
                    "error_type": fc.error_type,
                    "error_message": fc.error_message[:200],
                    "turn_kind": turn_kind,
                    "turn_index": turn_index,
                    "speaker": speaker,
                    "input_tokens": fc.input_tokens,
                    "output_tokens": fc.output_tokens,
                    "cost_usd": fc.cost_usd,
                }
            )

        # Recorded winner/reason from the game_end row (authoritative producer record).
        recorded_winner = game_end.winner if game_end is not None else None
        recorded_reason = game_end.reason if game_end is not None else None
        recorded_go_tick = game_end.tick if game_end is not None else None
        if game_end is None:
            no_game_over += 1
        else:
            win_split[recorded_winner or "NONE"] = (
                win_split.get(recorded_winner or "NONE", 0) + 1
            )
            if recorded_reason is not None:
                reason_counts[recorded_reason] = (
                    reason_counts.get(recorded_reason, 0) + 1
                )

        # --- Win-condition-gap check ---
        # If alive impostors hit 0 at tick T but the game's recorded game_over
        # tick is strictly later, the game continued past the crew-win point.
        if (
            first_zero_impostor_tick is not None
            and recorded_go_tick is not None
            and recorded_go_tick > first_zero_impostor_tick
        ):
            findings.append(
                {
                    "id": f"WINGAP-{seed}",
                    "severity": "blocking",
                    "title": "Game continued past the tick alive impostors hit 0",
                    "claim": (
                        "Alive impostors reached 0 before the recorded game_over "
                        "tick — the game ran on past the crew-win point "
                        "(win-condition gap)."
                    ),
                    "evidence": (
                        f"seed {seed}: alive impostors hit 0 at tick "
                        f"{first_zero_impostor_tick}, but game_over recorded at tick "
                        f"{recorded_go_tick} ({recorded_winner}/{recorded_reason})"
                    ),
                    "repair_hint": (
                        "engine.win_conditions now has the alive_impostors==0 crew "
                        "win; verify the replay was recorded with that build."
                    ),
                }
            )

        # --- Recorded winner vs final reconstructed state cross-check ---
        # engine/win_conditions.py orders CREWMATE_EJECT (alive impostors == 0)
        # BEFORE the task check, and state.tasks already excludes dead owners'
        # incomplete instances, so done==total remains the valid task test.
        if game_end is not None:
            alive_players = [
                p for p in last_state_for_final.players.values() if p.alive
            ]
            alive_imp = sum(1 for p in alive_players if p.role == "IMPOSTOR")
            alive_crew = sum(1 for p in alive_players if p.role == "CREWMATE")
            total_tasks = len(last_state_for_final.tasks)
            done_tasks = sum(
                1 for t in last_state_for_final.tasks.values() if t.completed
            )
            mismatch_reason: str | None = None
            if recorded_reason == "CREWMATE_TASKS":
                if not (total_tasks > 0 and done_tasks == total_tasks):
                    mismatch_reason = (
                        f"CREWMATE_TASKS but tasks {done_tasks}/{total_tasks} done"
                    )
            elif recorded_reason == "CREWMATE_EJECT":
                if alive_imp != 0:
                    mismatch_reason = (
                        f"CREWMATE_EJECT but {alive_imp} impostor(s) alive"
                    )
            elif recorded_reason == "IMPOSTOR_PARITY":
                if not (alive_imp >= alive_crew):
                    mismatch_reason = (
                        f"IMPOSTOR_PARITY but alive imp {alive_imp} < crew {alive_crew}"
                    )
            if mismatch_reason is not None:
                findings.append(
                    {
                        "id": f"WINMISMATCH-{seed}",
                        "severity": "blocking",
                        "title": "Recorded winner/reason contradicts final state",
                        "claim": (
                            "The recorded game_over winner/reason does not match the "
                            "final reconstructed alive-roles/tasks state."
                        ),
                        "evidence": (
                            f"seed {seed}: recorded {recorded_winner}/"
                            f"{recorded_reason} but {mismatch_reason}"
                        ),
                        "repair_hint": (
                            "Compare engine.win_conditions.evaluate_win_conditions "
                            "against the recorded outcome for this seed."
                        ),
                    }
                )

        # ---- WIN-DECISION ATTRIBUTION (point 6e — the R1 verdict input) ----
        # Was the win eject-DECIDED (both impostors removed by the meeting layer
        # -> CREWMATE_EJECT) or STOPWATCH (CREWMATE_TASKS fired with an impostor
        # still alive at the win tick)? CREWMATE_EJECT is engine-ordered BEFORE
        # the task check, so a CREWMATE_TASKS win is BY CONSTRUCTION one where an
        # impostor was still alive (alive_imp >= 1) — the clock, not deduction,
        # closed the game. The stopwatch tick margin is recorded_go_tick minus
        # the tick of the LAST impostor-ejecting meeting in the game (how much
        # runway the meeting layer had left before the clock pre-empted a 2nd
        # ejection; None when no impostor was ever ejected). Impostor wins
        # (IMPOSTOR_PARITY) are neither — the crew never closed it.
        if game_end is not None:
            alive_imp_final = sum(
                1
                for p in last_state_for_final.players.values()
                if p.alive and p.role == "IMPOSTOR"
            )
            game_impostor_ejections = sum(
                1 for m in meetings_out if m["ejected_role"] == "IMPOSTOR"
            )
            last_impostor_eject_tick = max(
                (m["tick"] for m in meetings_out if m["ejected_role"] == "IMPOSTOR"),
                default=None,
            )
            was_eject_decided = recorded_reason == "CREWMATE_EJECT"
            was_stopwatch = recorded_reason == "CREWMATE_TASKS" and alive_imp_final >= 1
            stopwatch_tick_margin = (
                recorded_go_tick - last_impostor_eject_tick
                if was_stopwatch
                and recorded_go_tick is not None
                and last_impostor_eject_tick is not None
                else None
            )
            win_decision_records.append(
                {
                    "seed": seed,
                    "winner": recorded_winner,
                    "reason": recorded_reason,
                    "impostors_alive_at_end": alive_imp_final,
                    "n_impostor_ejections": game_impostor_ejections,
                    "was_eject_decided": was_eject_decided,
                    "was_stopwatch": was_stopwatch,
                    "last_impostor_eject_tick": last_impostor_eject_tick,
                    "game_over_tick": recorded_go_tick,
                    "stopwatch_tick_margin": stopwatch_tick_margin,
                }
            )

        # Per-game token totals.
        game_input = sum(
            c.input_tokens for e in meeting_entries for c in e.llm_calls
        ) + sum(fc.input_tokens for fc in failed_call_entries)
        game_output = sum(
            c.output_tokens for e in meeting_entries for c in e.llm_calls
        ) + sum(fc.output_tokens for fc in failed_call_entries)
        game_cost = sum(c.cost_usd for e in meeting_entries for c in e.llm_calls) + sum(
            fc.cost_usd for fc in failed_call_entries
        )

        # Self-check: every kill-derived death has its victim in deaths.
        for k in kills:
            if k["victim"] not in deaths:
                invariant_failures.append(
                    f"seed {seed}: kill victim {k['victim']} at tick {k['tick']} "
                    f"not in deaths set"
                )

        # ---- Wave-1 decomposition assembly (point 6b) ----
        # Walk this game's meetings in order, carrying per-player accusation
        # history (who was verbally accused in EARLIER meetings + in which
        # meeting indices) so the accumulator-carry question is answerable.
        # `prior_accusations[pid]` = sorted list of earlier meeting_indexes in
        # which pid was named by an accusation claim (excluding self-accusations).
        n_game_meetings = len(meetings_out)
        prior_accusations: dict[str, list[int]] = {}
        for mi, mf in enumerate(meetings_out):
            m_idx = mf["meeting_index"]
            remaining_after = n_game_meetings - (mi + 1)
            # Players verbally accused THIS meeting (deduped, excluding self).
            accused_this_meeting = {
                acc["accused"]
                for acc in mf["accusations"]
                if acc["accused"] != acc["speaker"]
            }
            contra_by_subj = mf["contradictions_by_subject"]
            ej_id = mf["ejected_player_id"]
            ej_role = mf["ejected_role"]

            # (0) TESTIMONY RECORDS (point 6c): stamp each per-meeting testimony
            # row (one per verbally-accused living subject of EITHER role) with
            # the seed, meeting index, and the meetings-remaining count so the
            # cascade-risk + accumulator one-more-meeting questions are
            # answerable from the flat record set.
            for t_rec in mf["testimony_records"]:
                testimony_records_all.append(
                    {
                        "seed": seed,
                        "meeting_index": m_idx,
                        "meetings_remaining_after": remaining_after,
                        **t_rec,
                    }
                )

            # (i) PER-EJECTION EVIDENCE CLASS (right or wrong).
            if ej_id is not None:
                ej_contras = contra_by_subj.get(ej_id, [])
                strong_n = sum(1 for c in ej_contras if c["strong"])
                weak_n = len(ej_contras) - strong_n
                ej_max_sus = mf["ejected_rendered_suspicion"]
                # Accumulator-carry heuristic for the ejected player: their max
                # rendered suspicion exceeds what THIS meeting's own
                # contradictions naming them could reach from the 0.5 prior
                # (weak=0.08, strong=0.30 each, Rule-2 vote-time lift), AND they
                # were accused in a PRIOR meeting. Both prongs are quantized /
                # deterministic; recording the components lets the lens judge.
                this_meeting_contra_ceiling = 0.5 + (
                    strong_n * CONTRADICTION_SUSPICION_DELTA
                    + weak_n * WEAK_CONTRADICTION_SUSPICION_DELTA
                )
                priors = sorted(prior_accusations.get(ej_id, []))
                carry_unexplained_by_this_meeting = bool(
                    ej_max_sus is not None
                    and ej_max_sus > round(this_meeting_contra_ceiling, 4) + 1e-9
                )
                per_ejection_evidence.append(
                    {
                        "seed": seed,
                        "meeting_index": m_idx,
                        "ejected": ej_id,
                        "ejected_role": ej_role,
                        "correct": ej_role == "IMPOSTOR",
                        "contradictions": ej_contras,
                        "n_contradictions_naming_ejected": len(ej_contras),
                        "n_strong": strong_n,
                        "n_weak": weak_n,
                        "ejected_max_rendered_suspicion": ej_max_sus,
                        "ejected_max_rendered_suspicion_among_ejectors": mf[
                            "ejected_rendered_suspicion_among_ejectors"
                        ],
                        "this_meeting_contra_ceiling": round(
                            this_meeting_contra_ceiling, 4
                        ),
                        "prior_meeting_accusations": priors,
                        "n_prior_meeting_accusations": len(priors),
                        "carry_unexplained_by_this_meeting_contradictions": (
                            carry_unexplained_by_this_meeting
                        ),
                    }
                )

                # (iii) ZERO-CONTRADICTION EJECTIONS (accumulator-conversion
                # candidates): ejected, but NO contradiction names them.
                if not ej_contras:
                    zero_contradiction_ejections.append(
                        {
                            "seed": seed,
                            "meeting_index": m_idx,
                            "ejected": ej_id,
                            "ejected_role": ej_role,
                            "correct": ej_role == "IMPOSTOR",
                            "prior_meeting_accusations": priors,
                            "n_prior_meeting_accusations": len(priors),
                            "accused_this_meeting": ej_id in accused_this_meeting,
                            "ejected_max_rendered_suspicion": ej_max_sus,
                        }
                    )

            # (ii) MISSED-CONVERSION RECORDS: a living TRUE impostor was verbally
            # accused this meeting but NOT ejected (skipped, or someone else was).
            for impostor_id in sorted(accused_this_meeting):
                if roles.get(impostor_id) != "IMPOSTOR":
                    continue
                if impostor_id == ej_id:
                    continue  # this impostor WAS ejected — a conversion, not a miss
                imp_contras = contra_by_subj.get(impostor_id, [])
                imp_strong = sum(1 for c in imp_contras if c["strong"])
                # opt-in corroborations supporting an accuser of this impostor:
                # an opt_in turn whose CorroborationClaim.supports names a player
                # who accused this impostor this meeting.
                accusers_of_impostor = {
                    acc["speaker"]
                    for acc in mf["accusations"]
                    if acc["accused"] == impostor_id
                }
                opt_in_corr_map = mf["opt_in_corroborations_by_supported"]
                opt_in_corroborations_for_accusers = sum(
                    opt_in_corr_map.get(accuser, 0) for accuser in accusers_of_impostor
                )
                missed_conversions.append(
                    {
                        "seed": seed,
                        "meeting_index": m_idx,
                        "impostor": impostor_id,
                        "accused_by": sorted(accusers_of_impostor),
                        "n_contradictions_naming_impostor": len(imp_contras),
                        "n_strong_naming_impostor": imp_strong,
                        "n_weak_naming_impostor": len(imp_contras) - imp_strong,
                        "contradictions": imp_contras,
                        "impostor_max_rendered_suspicion": mf[
                            "rendered_suspicion_by_target"
                        ].get(impostor_id),
                        "opt_in_corroborations_supporting_an_accuser": (
                            opt_in_corroborations_for_accusers
                        ),
                        "outcome": (
                            "ejected_someone_else" if ej_id is not None else "SKIPPED"
                        ),
                        "ejected_instead": ej_id,
                        "ejected_instead_role": ej_role,
                        "meetings_remaining_after": remaining_after,
                        "n_prior_meeting_accusations": len(
                            prior_accusations.get(impostor_id, [])
                        ),
                    }
                )

            # Roll this meeting's accusations into the prior-history map AFTER
            # processing it (so "prior" is strictly earlier meetings).
            for acc_pid in accused_this_meeting:
                prior_accusations.setdefault(acc_pid, []).append(m_idx)

        # ---- ACCUMULATOR TRAJECTORY FACTS (point 6c) ----
        # For each player who is a vote CANDIDATE (appears in some other voter's
        # §6.6 suspicion graph) in 2+ meetings of THIS game, build the
        # across-meeting sequence of their rendered max suspicion plus the
        # accusations / opt-in corroborations naming them in the same meeting.
        # The lenses verify carry vs the 25% Rule-5 decay vs Rule-3 corroboration
        # drops from these. We also count DOWNWARD moves (a later meeting's
        # rendered value strictly below the earlier one) — the sanity signal
        # that 10.2's un-gated Rule-3 corroboration / Rule-5 decay is live on
        # these bytes (a pre-10.2 monotone-up store would show zero).
        candidate_meetings: dict[str, list[dict[str, Any]]] = {}
        for mf in meetings_out:
            rendered = mf["rendered_suspicion_by_target"]
            # Accusations / corroborations naming each player THIS meeting.
            acc_count: dict[str, int] = {}
            for acc in mf["accusations"]:
                if acc["accused"] != acc["speaker"]:
                    acc_count[acc["accused"]] = acc_count.get(acc["accused"], 0) + 1
            corr_count = mf["opt_in_corroborations_by_supported"]
            for pid, sus in rendered.items():
                candidate_meetings.setdefault(pid, []).append(
                    {
                        "meeting_index": mf["meeting_index"],
                        "rendered_suspicion": sus,
                        "accusations_naming": acc_count.get(pid, 0),
                        "opt_in_corroborations_naming": corr_count.get(pid, 0),
                        "ejected_here": mf["ejected_player_id"] == pid,
                    }
                )
        for pid, seq in candidate_meetings.items():
            if len(seq) < 2:
                continue
            ordered = sorted(seq, key=lambda s: s["meeting_index"])
            downward_moves = 0
            downward_with_corroboration = 0
            for prev_pt, cur in zip(ordered, ordered[1:]):
                if cur["rendered_suspicion"] < prev_pt["rendered_suspicion"] - 1e-9:
                    downward_moves += 1
                    # A downward move where the EARLIER meeting carried a
                    # corroboration of this player is the Rule-3 (corroboration
                    # −0.05) signature; decay (Rule 5) also drives down moves.
                    if prev_pt["opt_in_corroborations_naming"] > 0:
                        downward_with_corroboration += 1
            accumulator_trajectories.append(
                {
                    "seed": seed,
                    "player": pid,
                    "player_role": roles.get(pid, "UNKNOWN"),
                    "n_candidate_meetings": len(ordered),
                    "sequence": ordered,
                    "rendered_suspicion_series": [
                        s["rendered_suspicion"] for s in ordered
                    ],
                    "downward_moves": downward_moves,
                    "downward_moves_with_prior_corroboration": (
                        downward_with_corroboration
                    ),
                }
            )

        # ---- 10.3 opening-DEFAULT count (point 6c) ----
        # Openings that EXHAUSTED their single retry surface as deadline_default
        # rows with turn_kind=="opening" (collected, de-duplicated, in
        # defaulted_turns). A defaulted opening that left the recorded opening
        # with no accusation lost its chain-driving opening. Burned spend lands
        # in TWO places depending on how the attempt failed: a returned-but-
        # rejected attempt (manager-side validation) is in the meeting's
        # llm_calls (opening-slot calls for the opener); an attempt that raised
        # a ValidationError before the recording client logged it rides the
        # deadline_default row's own tokens. Both are summed here so the per-
        # opening burned cost is visible (already in the global token totals).
        this_game_opening_defaults = {
            (d["meeting_id"], d["turn_index"], d["speaker"])
            for d in defaulted_turns
            if d["seed"] == seed and d["turn_kind"] == "opening"
        }
        opening_defaults += len(this_game_opening_defaults)
        for d_mid, d_idx, d_spk in this_game_opening_defaults:
            mf_for = next((m for m in meetings_out if m["meeting_id"] == d_mid), None)
            lost = mf_for is not None and not mf_for["opening_has_accusation"]
            if lost:
                meetings_lost_opening += 1
            m_entry = next((m for m in meeting_entries if m.meeting_id == d_mid), None)
            burned_in = burned_out = 0
            if m_entry is not None:
                for call in m_entry.llm_calls:
                    if call.agent_id == d_spk and (
                        _classify_call_slot(call.prompt) == "opening"
                    ):
                        burned_in += call.input_tokens
                        burned_out += call.output_tokens
            for fc in failed_call_entries:
                if (
                    fc.meeting_id == d_mid
                    and fc.error_type == "deadline_default"
                    and (mm := _DEFAULTED_TURN_RE.search(fc.error_message)) is not None
                    and mm.group("kind") == "opening"
                    and mm.group("speaker") == d_spk
                ):
                    burned_in += fc.input_tokens
                    burned_out += fc.output_tokens
            opening_retry_records.append(
                {
                    "seed": seed,
                    "meeting_id": d_mid,
                    "opener": d_spk,
                    "opener_role": roles.get(d_spk, "UNKNOWN"),
                    "turn_index": d_idx,
                    "outcome": "defaulted",
                    "lost_chain_driving_opening": lost,
                    "burned_input_tokens": burned_in,
                    "burned_output_tokens": burned_out,
                }
            )

        games.append(
            {
                "seed": seed,
                "game_id": game_id,
                "roles": roles,
                "winner": recorded_winner,
                "reason": recorded_reason,
                "game_over_tick": recorded_go_tick,
                "kills": kills,
                "deaths": sorted(deaths),
                "meetings": meetings_out,
                "first_zero_impostor_tick": first_zero_impostor_tick,
                "tokens": {
                    "input": game_input,
                    "output": game_output,
                    "cost_usd": game_cost,
                },
                "failed_calls": failed_calls_out,
            }
        )

    # --- 10.4 genuine-class + vote-correctness CROSS-CHECK (point 6b) ---
    # Build the SHIPPED tournament report over the SAME bytes (re-seeding the
    # firewalled roles) and fold it through the owning eval helpers, then assert
    # the extractor's RE-DERIVED genuine-class supplied/converted equals the
    # shipped compute_genuine_class_conversion to the unit. A mismatch means one
    # of the two classifiers is wrong (a divergent replica would poison the
    # whole decomposition) -> BLOCKING mechanical finding. On a post-repair
    # recording (10.5+) the imported detector re-run equals the recorded flags,
    # so the two must agree exactly; the assertion is the trust anchor that they
    # do. ejection_accuracy / contradictions-flagged-but-ignored are folded for
    # the summary and a sanity cross-check against the extractor's own tallies.
    roles_by_seed = {g["seed"]: dict(g["roles"]) for g in games}
    shipped_report = load_tournament_report(
        SAMPLE_DIR,
        roles_by_seed=roles_by_seed,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    shipped_genuine = compute_genuine_class_conversion(shipped_report)
    shipped_vc = compute_vote_correctness(shipped_report)
    genuine_crosscheck_ok = (
        genuine_supplied_rederived == shipped_genuine.supplied
        and genuine_converted_rederived == shipped_genuine.converted
    )
    if not genuine_crosscheck_ok:
        findings.append(
            {
                "id": "GENUINE-CROSSCHECK",
                "severity": "blocking",
                "title": (
                    "Re-derived genuine-class diverges from the shipped 10.4 metric"
                ),
                "claim": (
                    "The extractor's imported-detector genuine-class re-run and "
                    "eval.vote_correctness.compute_genuine_class_conversion over "
                    "the same bytes must agree to the unit; they do not, so one "
                    "of the two classifiers is wrong and the whole decomposition "
                    "is poisoned."
                ),
                "evidence": (
                    f"extractor supplied={genuine_supplied_rederived} "
                    f"converted={genuine_converted_rederived}; shipped "
                    f"supplied={shipped_genuine.supplied} "
                    f"converted={shipped_genuine.converted}"
                ),
                "repair_hint": (
                    "Re-sync the extractor's _genuine_subjects to the imported "
                    "meetings.transcript.detect_contradictions + the 10.4 "
                    "non-endpoint alibi_vs_sighting definition; a drift means an "
                    "era-frozen replica crept back in."
                ),
            }
        )
    # Cross-check the extractor's own ejection tallies against the shipped
    # vote-correctness fold (both re-derive roles the same way; a mismatch is an
    # internal inconsistency -> invariant failure, not a substrate finding).
    if shipped_vc.impostor_ejections != ejections_impostor:
        invariant_failures.append(
            f"impostor-ejection count mismatch: extractor {ejections_impostor} "
            f"vs shipped vote_correctness {shipped_vc.impostor_ejections}"
        )
    if shipped_vc.crewmate_ejections != len(wrong_ejections):
        invariant_failures.append(
            f"crew-ejection count mismatch: extractor {len(wrong_ejections)} "
            f"vs shipped vote_correctness {shipped_vc.crewmate_ejections}"
        )

    # --- Wave-2 CRATER folds (point 6e) over the SAME shipped report bytes ---
    # ACTIONS BY ROLE (the blending census): the per-tick action stream is NOT in
    # the meeting-only report model, so the ingest walks the committed replay rows
    # directly (eval.action_ingest.tally_actions_by_role keyed on the report's
    # seeded roles), then the pure compute_indistinguishability fold publishes the
    # never-tasks fingerprint (impostor do_task / wait-share / top-idler).
    action_tally = tally_actions_by_role(SAMPLE_DIR, shipped_report.games)
    indistinguishability = compute_indistinguishability(action_tally)
    # EFFECTIVE DEFLECTION (the blend-vs-deflect split): the imported one-home fold
    # isolating real deception skill (the impostor's counter-accusation moved the
    # eject-plurality OFF itself) from SKIP-saved survival.
    effective_deflection = compute_effective_deflection(shipped_report)
    # INFORM-CHANNEL CONVERSIONS (the 10.16 fifth channel): decompose every
    # impostor ejection's rendered lift and keep the ones the single-witness inform
    # is credited for. Cross-checked against the shipped multi-signal census's
    # per-channel inform count (both call decompose_ejection_channels; a divergent
    # count means the extractor's loop and the shipped fold disagree -> BLOCKING).
    multi_signal = compute_multi_signal_conversion(shipped_report)
    inform_channel_conversions = []
    for game in shipped_report.games:
        roles_g = dict(game.roles)
        for mi, meeting in enumerate(game.meetings):
            channels = decompose_ejection_channels(game, mi)
            if channels is None or CHANNEL_SINGLE_WITNESS_INFORM not in channels:
                continue
            subject = meeting.ejected_player_id
            # The informing witnesses + their backing observations: the meeting's
            # turn speakers who logged a first-hand sighting / found_body of the
            # ejected subject (the single-witness inform's evidentiary base).
            informing_witnesses: list[dict[str, Any]] = []
            for turn in meeting.transcript.turns:
                obs_strs: list[str] = []
                for o in turn.observations:
                    if isinstance(o, SawPlayerObservation) and o.subject == subject:
                        obs_strs.append(f"saw {o.subject} in {o.room} @t{o.tick}")
                    elif isinstance(o, FoundBodyObservation):
                        obs_strs.append(
                            f"found_body {o.body_of} in {o.room} @t{o.tick}"
                        )
                if obs_strs:
                    informing_witnesses.append(
                        {
                            "speaker": turn.speaker,
                            "speaker_role": roles_g.get(turn.speaker, "UNKNOWN"),
                            "observations": obs_strs,
                        }
                    )
            inform_channel_conversions.append(
                {
                    "seed": game.seed,
                    "meeting_index": mi,
                    "subject": subject,
                    "subject_role": roles_g.get(subject, "UNKNOWN"),
                    "channels": sorted(channels),
                    "n_channels": len(channels),
                    "multi_signal": len(channels) >= 2,
                    "informing_witnesses": informing_witnesses,
                    # A "clean" inform conversion has an observation-backed witness
                    # of the subject (real evidence); a "marginal" one credits the
                    # inform band with no surfaced first-hand sighting in the
                    # recorded transcript (the lattice mass aligned but the
                    # evidentiary base is thinner — lens flags these).
                    "clean": bool(informing_witnesses),
                }
            )
    # Cross-check: the extractor's inform-credited ejection count must equal the
    # shipped multi-signal census's per-channel inform presence count (both fold
    # decompose_ejection_channels over the same report; a mismatch means one of
    # the two loops is wrong).
    inform_crosscheck_ok = (
        len(inform_channel_conversions)
        == multi_signal.conversions_with_single_witness_inform
    )
    if not inform_crosscheck_ok:
        findings.append(
            {
                "id": "INFORM-CHANNEL-CROSSCHECK",
                "severity": "blocking",
                "title": (
                    "Re-derived inform-channel count diverges from the shipped "
                    "10.16 multi-signal census"
                ),
                "claim": (
                    "The extractor's per-ejection decompose_ejection_channels loop "
                    "and eval.meeting_quality.compute_multi_signal_conversion over "
                    "the same bytes must agree on the single-witness-inform "
                    "presence count; they do not, so one of the two folds is wrong."
                ),
                "evidence": (
                    f"extractor inform conversions={len(inform_channel_conversions)}; "
                    "shipped conversions_with_single_witness_inform="
                    f"{multi_signal.conversions_with_single_witness_inform}"
                ),
                "repair_hint": (
                    "Both call decompose_ejection_channels; re-sync the extractor's "
                    "loop to the shipped fold's well-formed-impostor-ejection gate."
                ),
            }
        )

    # do_task INTEGRITY summary (point 6e): the engine ALWAYS rejects an impostor's
    # pretend do_task (unowned map id), so impostor_task_advances MUST be empty —
    # a single entry already emitted a BLOCKING IMPTASK finding in the walk. The
    # W2 indistinguishability fingerprint shows impostor do_task EMISSIONS > 0 (the
    # 10.14 blending lever firing), but an EMISSION is the recorded action; an
    # ADVANCE is a real task counter moving. The integrity invariant is that the
    # two never coincide for an impostor: emissions can be many, advances must be 0.
    impostor_do_task_emissions = indistinguishability.impostor_do_task
    impostor_real_task_advances = len(impostor_task_advances)

    # --- CROSS-ERA TRAJECTORY (point 6f) over the committed fixtures ---
    # The live W2 conversion_per_meeting (impostor ejections / resolved meetings)
    # and eject-decided win count, fed alongside the imported W2 folds so the
    # W0->W1->W2 row is built once (lenses B/E read it instead of re-reading the
    # prior-era fixtures).
    w2_conversion_per_meeting = (
        round(ejections_impostor / total_meetings, 4) if total_meetings else None
    )
    w2_eject_decided_wins = sum(
        1 for r in win_decision_records if r["was_eject_decided"]
    )
    cross_era_trajectory = _cross_era_trajectory(
        w2_effective_deflection=effective_deflection,
        w2_multi_signal=multi_signal,
        w2_genuine_supplied=genuine_supplied_rederived,
        w2_genuine_converted=genuine_converted_rederived,
        w2_conversion_per_meeting=w2_conversion_per_meeting,
        w2_total_meetings=total_meetings,
        w2_win_split=win_split,
        w2_eject_decided_wins=w2_eject_decided_wins,
    )

    # --- COUNTERFACTUAL ORACLE self-check (point 7) ---
    # The whole audit's counterfactual layer is built on the re-derived W2 numbers;
    # an oracle that does not reproduce the RECORDED tournament-eval-report actuals
    # is worthless (lens E depends on this). Re-derive the win split + R1 eject-
    # decided wins + effective_deflection from the walk and assert they match the
    # committed report. The recorded report's per-game winner/reason is the
    # authoritative actual; the shipped effective_deflection fold is the same
    # one-home source the gate uses, so this confirms the EXTRACTION reproduces
    # the SHIPPED metric (a divergence is a silent extraction bug -> raise).
    recorded_report_win_split: dict[str, int] = {}
    for g in shipped_report.games:
        recorded_report_win_split[g.winner or "NONE"] = (
            recorded_report_win_split.get(g.winner or "NONE", 0) + 1
        )
    oracle_win_split_ok = win_split == recorded_report_win_split
    # R1 eject-decided: a CREWMATE_EJECT win. The recorded report carries the
    # per-game reason, so re-derive the count straight off it and compare to the
    # walk-derived count (both must agree, and on this baseline both are 0).
    recorded_eject_decided = sum(
        1 for g in shipped_report.games if g.reason == "CREWMATE_EJECT"
    )
    oracle_eject_decided_ok = w2_eject_decided_wins == recorded_eject_decided
    if not oracle_win_split_ok:
        invariant_failures.append(
            "COUNTERFACTUAL ORACLE: walk-derived win split "
            f"{win_split} != recorded report win split {recorded_report_win_split}"
        )
    if not oracle_eject_decided_ok:
        invariant_failures.append(
            "COUNTERFACTUAL ORACLE: walk-derived eject-decided wins "
            f"{w2_eject_decided_wins} != recorded report CREWMATE_EJECT count "
            f"{recorded_eject_decided}"
        )

    # --- Wave-1-CLOSE census CROSS-CHECKS (point 6d) ---
    # The extractor's own marker-derived redirect / defaulted-ballot record sets
    # must equal the shipped eval.meeting_quality censuses over the same bytes
    # (both key on the identical imported pinned markers; a mismatch means one of
    # the two readers is wrong -> BLOCKING). The redirect census splits the count
    # into eject vs coerced-SKIP; the extractor's was_coerced_to_SKIP flag gives
    # the same split, so both prongs are checked.
    shipped_defaulted = compute_defaulted_ballots(shipped_report)
    shipped_redirects = compute_ballot_target_redirects(shipped_report)
    redirect_eject_rederived = sum(
        1 for r in redirect_records_all if not r["was_coerced_to_SKIP"]
    )
    redirect_skip_rederived = sum(
        1 for r in redirect_records_all if r["was_coerced_to_SKIP"]
    )
    defaulted_ballots_crosscheck_ok = (
        len(defaulted_ballot_records_all) == shipped_defaulted.defaulted_skip_ballots
    )
    redirect_crosscheck_ok = (
        len(redirect_records_all) == shipped_redirects.redirected_ballots
        and redirect_eject_rederived == shipped_redirects.redirected_eject_ballots
        and redirect_skip_rederived == shipped_redirects.redirect_coerced_skip_ballots
    )
    if not defaulted_ballots_crosscheck_ok:
        findings.append(
            {
                "id": "DEFAULTED-BALLOT-CROSSCHECK",
                "severity": "blocking",
                "title": (
                    "Re-derived defaulted-ballot count diverges from the shipped "
                    "10.9.1 census"
                ),
                "claim": (
                    "The extractor's VOTE_PARSE_DEFAULT_MARKER record set and "
                    "eval.meeting_quality.compute_defaulted_ballots over the same "
                    "bytes must agree to the unit; they do not, so one of the two "
                    "marker readers is wrong."
                ),
                "evidence": (
                    f"extractor defaulted ballots={len(defaulted_ballot_records_all)}; "
                    f"shipped defaulted_skip_ballots="
                    f"{shipped_defaulted.defaulted_skip_ballots}"
                ),
                "repair_hint": (
                    "Both read the pinned meetings.manager.VOTE_PARSE_DEFAULT_MARKER "
                    "prefix off ballot.rationale_text; re-sync the extractor's "
                    "_VOTE_PARSE_DEFAULT_MARKER_PREFIX to the imported constant."
                ),
            }
        )
    if not redirect_crosscheck_ok:
        findings.append(
            {
                "id": "REDIRECT-CROSSCHECK",
                "severity": "blocking",
                "title": (
                    "Re-derived ballot-redirect counts diverge from the shipped "
                    "10.9.2 census"
                ),
                "claim": (
                    "The extractor's BALLOT_TARGET_REDIRECT_MARKER record set and "
                    "eval.meeting_quality.compute_ballot_target_redirects over the "
                    "same bytes must agree to the unit (total + eject/coerced-SKIP "
                    "split); they do not, so one of the two marker readers is wrong."
                ),
                "evidence": (
                    f"extractor redirects total={len(redirect_records_all)} "
                    f"(eject={redirect_eject_rederived}, "
                    f"coerced_skip={redirect_skip_rederived}); shipped "
                    f"redirected_ballots={shipped_redirects.redirected_ballots} "
                    f"(eject={shipped_redirects.redirected_eject_ballots}, "
                    f"coerced_skip={shipped_redirects.redirect_coerced_skip_ballots})"
                ),
                "repair_hint": (
                    "Both read the pinned meetings.manager.BALLOT_TARGET_REDIRECT_"
                    "MARKER prefix off ballot.rationale_text; re-sync the "
                    "extractor's _BALLOT_REDIRECT_MARKER_PREFIX to the imported "
                    "constant."
                ),
            }
        )

    # --- Self-check invariants (FAIL LOUD) ---
    self_checks: list[str] = []
    ok_meetings = total_meetings == total_meeting_records
    self_checks.append(
        f"total meetings in facts ({total_meetings}) == meeting records "
        f"({total_meeting_records}): {'OK' if ok_meetings else 'FAIL'}"
    )
    if not ok_meetings:
        invariant_failures.append(
            f"meeting count mismatch: facts {total_meetings} vs records "
            f"{total_meeting_records}"
        )

    n_files = len(list(SAMPLE_DIR.glob("replay-seed-*.jsonl")))
    ok_games = games_analyzed == n_files
    self_checks.append(
        f"games_analyzed ({games_analyzed}) == replay files ({n_files}): "
        f"{'OK' if ok_games else 'FAIL'}"
    )
    if not ok_games:
        invariant_failures.append(f"games_analyzed {games_analyzed} != files {n_files}")

    impostor_check_ok = all(
        sum(1 for r in g["roles"].values() if r == "IMPOSTOR") == num_impostors
        for g in games
    )
    self_checks.append(
        f"every seed has exactly {num_impostors} impostors: "
        f"{'OK' if impostor_check_ok else 'FAIL'}"
    )

    # v2 ADDED invariants (recorded inside _analyze_meeting; summarized here).
    transcript_failures = [
        f
        for f in invariant_failures
        if "transcript.turns is empty" in f or "opening turns at positions" in f
    ]
    self_checks.append(
        "every meeting transcript is non-empty with exactly one opening at "
        f"index 0: {'OK' if not transcript_failures else 'FAIL'}"
    )
    dead_voter_failures = [f for f in invariant_failures if "ballot voter" in f]
    self_checks.append(
        "every ballot voter is alive at its meeting tick: "
        f"{'OK' if not dead_voter_failures else 'FAIL'}"
    )
    hash_before_failures = [f for f in invariant_failures if "state_hash_before" in f]
    self_checks.append(
        "every meeting state_hash_before matches its trigger tick's "
        f"state_hash: {'OK' if not hash_before_failures else 'FAIL'}"
    )
    walk_hash_failures = [
        f
        for f in invariant_failures
        if "state-hash mismatch" in f or "post-meeting state-hash" in f
    ]
    self_checks.append(
        "per-tick + post-meeting state hashes match the recorded log: "
        f"{'OK' if not walk_hash_failures else 'FAIL'}"
    )
    self_checks.append(
        "re-derived genuine-class == shipped compute_genuine_class_conversion "
        f"(supplied {genuine_supplied_rederived}/{shipped_genuine.supplied}, "
        f"converted {genuine_converted_rederived}/{shipped_genuine.converted}): "
        f"{'OK' if genuine_crosscheck_ok else 'FAIL'}"
    )
    ejection_crosscheck_ok = (
        shipped_vc.impostor_ejections == ejections_impostor
        and shipped_vc.crewmate_ejections == len(wrong_ejections)
    )
    self_checks.append(
        "extractor ejection tallies == shipped vote_correctness "
        f"(imp {ejections_impostor}/{shipped_vc.impostor_ejections}, crew "
        f"{len(wrong_ejections)}/{shipped_vc.crewmate_ejections}): "
        f"{'OK' if ejection_crosscheck_ok else 'FAIL'}"
    )
    # Wave-1-CLOSE census cross-checks (point 6d): the extractor's marker-derived
    # redirect / defaulted-ballot record sets vs the shipped eval.meeting_quality
    # censuses. A mismatch is a trust-anchor failure (one of two readers of the
    # same pinned marker is wrong) -> raise loud, like the genuine cross-check.
    self_checks.append(
        "re-derived defaulted-ballot count == shipped compute_defaulted_ballots "
        f"({len(defaulted_ballot_records_all)}/"
        f"{shipped_defaulted.defaulted_skip_ballots}): "
        f"{'OK' if defaulted_ballots_crosscheck_ok else 'FAIL'}"
    )
    self_checks.append(
        "re-derived ballot-redirect counts == shipped "
        "compute_ballot_target_redirects "
        f"(total {len(redirect_records_all)}/{shipped_redirects.redirected_ballots}, "
        f"eject {redirect_eject_rederived}/"
        f"{shipped_redirects.redirected_eject_ballots}, coerced_skip "
        f"{redirect_skip_rederived}/"
        f"{shipped_redirects.redirect_coerced_skip_ballots}): "
        f"{'OK' if redirect_crosscheck_ok else 'FAIL'}"
    )
    if not defaulted_ballots_crosscheck_ok:
        invariant_failures.append(
            "defaulted-ballot census mismatch: extractor "
            f"{len(defaulted_ballot_records_all)} vs shipped "
            f"compute_defaulted_ballots {shipped_defaulted.defaulted_skip_ballots}"
        )
    if not redirect_crosscheck_ok:
        invariant_failures.append(
            "ballot-redirect census mismatch: extractor total "
            f"{len(redirect_records_all)} (eject {redirect_eject_rederived}, "
            f"coerced_skip {redirect_skip_rederived}) vs shipped "
            f"compute_ballot_target_redirects total "
            f"{shipped_redirects.redirected_ballots} (eject "
            f"{shipped_redirects.redirected_eject_ballots}, coerced_skip "
            f"{shipped_redirects.redirect_coerced_skip_ballots})"
        )
    # Emergency meetings must carry no engine body (10.8 invariant). The blocking
    # finding is emitted per-meeting above; surface the aggregate self-check here
    # AND raise loud on any breach. The check is engine-authoritative (body_id),
    # NOT the model-fabricated opening found_body.
    emergency_with_body = [r for r in emergency_meeting_records if r["carried_body"]]
    self_checks.append(
        "every emergency meeting carries no engine body (body_id is None) "
        f"({len(emergency_meeting_records)} emergency meetings, "
        f"{len(emergency_with_body)} with a body): "
        f"{'OK' if not emergency_with_body else 'FAIL'}"
    )
    if emergency_with_body:
        for r in emergency_with_body:
            invariant_failures.append(
                f"emergency meeting carried an engine body: seed {r['seed']} "
                f"meeting {r['meeting_index']} body_id={r['trigger_body_id']!r}"
            )

    # Wave-2 do_task INTEGRITY (point 6e / Task 10.14): impostor real-task advances
    # MUST be 0 (a fake task can never move a real task counter); a single advance
    # already emitted a BLOCKING IMPTASK finding in the walk. Surface the aggregate
    # here and raise loud on any breach.
    self_checks.append(
        "no impostor do_task advanced a real task instance (10.14 integrity; "
        f"{impostor_real_task_advances} advances, "
        f"{impostor_do_task_emissions} emissions): "
        f"{'OK' if impostor_real_task_advances == 0 else 'FAIL'}"
    )
    if impostor_real_task_advances > 0:
        invariant_failures.append(
            f"do_task integrity breach: {impostor_real_task_advances} impostor "
            "real-task advance(s) (a fake task moved a real CREWMATE_TASKS counter)"
        )
    # Inform-channel cross-check (point 6e): the extractor's per-ejection
    # decompose loop vs the shipped multi-signal census inform count.
    self_checks.append(
        "re-derived inform-channel count == shipped multi-signal census "
        f"({len(inform_channel_conversions)}/"
        f"{multi_signal.conversions_with_single_witness_inform}): "
        f"{'OK' if inform_crosscheck_ok else 'FAIL'}"
    )
    if not inform_crosscheck_ok:
        invariant_failures.append(
            "inform-channel census mismatch: extractor "
            f"{len(inform_channel_conversions)} vs shipped "
            f"{multi_signal.conversions_with_single_witness_inform}"
        )
    # COUNTERFACTUAL ORACLE self-check (point 7): the re-derived W2 win split + R1
    # eject-decided wins must reproduce the recorded tournament-eval-report; an
    # oracle that does not reproduce the actuals is worthless.
    self_checks.append(
        "counterfactual oracle: walk-derived win split reproduces the recorded "
        f"report ({win_split} vs {recorded_report_win_split}): "
        f"{'OK' if oracle_win_split_ok else 'FAIL'}"
    )
    self_checks.append(
        "counterfactual oracle: walk-derived R1 eject-decided wins reproduce the "
        f"recorded report ({w2_eject_decided_wins}/{recorded_eject_decided}): "
        f"{'OK' if oracle_eject_decided_ok else 'FAIL'}"
    )
    # The effective-deflection fold IS the shipped one-home source; surface its
    # headline subcount so the oracle's deflection reproduction is visible in the
    # self-check block (cross-checked against the committed W2 fixture below).
    self_checks.append(
        "effective-deflection fold (the oracle's deflection input): "
        f"effective={effective_deflection.effective_deflections}, "
        f"skip_saved={effective_deflection.skip_saved_active_survivals}, "
        f"active={effective_deflection.active_survivals} (W2 fixture match: "
        f"{cross_era_trajectory['w2_effective_deflection_matches_fixture']})"
    )

    for line in self_checks:
        print(line, file=sys.stderr)

    if invariant_failures:
        for f in invariant_failures:
            print(f"INVARIANT FAILURE: {f}", file=sys.stderr)
        raise RuntimeError(
            f"{len(invariant_failures)} extraction invariant(s) failed; "
            "the facts file would be untrustworthy. Aborting."
        )

    aggregates = {
        "win_split": win_split,
        "reason_counts": reason_counts,
        "no_game_over_games": no_game_over,
        "total_kills": total_kills,
        "impostor_victim_kills": impostor_victim_kills,
        "total_meetings": total_meetings,
        "trigger_kind_counts": trigger_kind_counts,
        "ejections_by_role": ejections_by_role,
        "total_ballots": total_ballots,
        "skip_ballots": total_skip_ballots,
        "skip_ballot_share": (
            round(total_skip_ballots / total_ballots, 4) if total_ballots else None
        ),
        "chain_length_histogram": dict(
            sorted(chain_length_hist.items(), key=lambda kv: int(kv[0]))
        ),
        "termination_condition_counts": termination_counts,
        "opening_turns_with_accusation": opening_accusation_count,
        "accusations": {
            "total": accusations_total,
            "at_impostors": accusations_at_impostors,
            "at_innocents": accusations_at_innocents,
            "self_accusations": self_accusations,
            "at_unknown_ids": accusations_at_unknown,
        },
        "opt_ins": {
            "eligible_derived_total": opt_in_eligible_total,
            "turns_total": opt_in_turns_total,
            "substantive": opt_in_substantive,
            "empty_pass": opt_in_turns_total - opt_in_substantive,
        },
        "ballot_follows_chain": {
            "non_skip_ballots": ballots_non_skip,
            "follows_chain": ballots_follow_chain,
            "non_skip_with_null_reason": ballots_non_skip_null_reason,
        },
        "total_contradictions": total_contradictions,
        "ejection_accuracy": {
            "total_ejections": ejections_total,
            "impostor_ejections": ejections_impostor,
            "accuracy": (
                round(ejections_impostor / ejections_total, 4)
                if ejections_total
                else None
            ),
            "wrong_ejections": wrong_ejections,
        },
        "skip_partition": {
            "skip_ballots": total_skip_ballots,
            "correct": skip_correct_total,
            "missed": skip_missed_total,
            "unclassified": skip_unclassified_total,
            "note": (
                "CORRECT = rendered §4.6 max < 0.60; MISSED = rendered max >= "
                "0.60 over a living target yet voter SKIPped. unclassified = SKIP "
                "ballot with no matched vote-prompt suspicion line."
            ),
        },
        "threshold_inversions": {
            "count": len(threshold_inversions_all),
            "note": (
                "rendered max >= 0.60 over a living target yet target == SKIP, "
                "MINUS firewall coercions (impostor voter) and invalid-target "
                "normalizations; ~0 expected on a clean baseline."
            ),
            "records": threshold_inversions_all,
        },
        "wave1_decomposition": {
            "note": (
                "Re-derived regression-decomposition aggregates (point 6b; NOT "
                "PR #138's numbers). Contradiction weak/strong classes use the "
                "same marker logic the 9.7 detector wrote (self-stated / narrow "
                "window from the description; strong = no marker). Rendered "
                "suspicion is read off the §6.6 'Your suspicion graph' block in "
                "each voter's vote prompt (max over OTHER voters' rows, since a "
                "voter holds no row about itself)."
            ),
            "per_ejection_evidence": {
                "count": len(per_ejection_evidence),
                "wrong": sum(1 for r in per_ejection_evidence if not r["correct"]),
                "correct": sum(1 for r in per_ejection_evidence if r["correct"]),
                "wrong_with_only_weak_contradictions": sum(
                    1
                    for r in per_ejection_evidence
                    if not r["correct"]
                    and r["n_contradictions_naming_ejected"] > 0
                    and r["n_strong"] == 0
                ),
                "wrong_with_zero_contradictions": sum(
                    1
                    for r in per_ejection_evidence
                    if not r["correct"] and r["n_contradictions_naming_ejected"] == 0
                ),
                "correct_with_a_strong_contradiction": sum(
                    1
                    for r in per_ejection_evidence
                    if r["correct"] and r["n_strong"] > 0
                ),
                "with_accumulator_carry_signal": sum(
                    1
                    for r in per_ejection_evidence
                    if r["carry_unexplained_by_this_meeting_contradictions"]
                    and r["n_prior_meeting_accusations"] > 0
                ),
                "records": per_ejection_evidence,
            },
            "missed_conversions": {
                "count": len(missed_conversions),
                "skipped": sum(
                    1 for r in missed_conversions if r["outcome"] == "SKIPPED"
                ),
                "ejected_someone_else": sum(
                    1
                    for r in missed_conversions
                    if r["outcome"] == "ejected_someone_else"
                ),
                "with_a_strong_contradiction_naming_the_impostor": sum(
                    1 for r in missed_conversions if r["n_strong_naming_impostor"] > 0
                ),
                "with_only_weak_contradictions": sum(
                    1
                    for r in missed_conversions
                    if r["n_contradictions_naming_impostor"] > 0
                    and r["n_strong_naming_impostor"] == 0
                ),
                "with_zero_contradictions": sum(
                    1
                    for r in missed_conversions
                    if r["n_contradictions_naming_impostor"] == 0
                ),
                "with_a_later_meeting_available": sum(
                    1 for r in missed_conversions if r["meetings_remaining_after"] > 0
                ),
                "note": (
                    "One record per (meeting, living true impostor accused but "
                    "not ejected). A game with 2 impostors accused in one "
                    "skipped meeting contributes 2 records."
                ),
                "records": missed_conversions,
            },
            "zero_contradiction_ejections": {
                "count": len(zero_contradiction_ejections),
                "impostor": sum(
                    1 for r in zero_contradiction_ejections if r["correct"]
                ),
                "crew": sum(
                    1 for r in zero_contradiction_ejections if not r["correct"]
                ),
                "with_prior_meeting_accusation": sum(
                    1
                    for r in zero_contradiction_ejections
                    if r["n_prior_meeting_accusations"] > 0
                ),
                "note": (
                    "Ejections with NO contradiction naming the ejected — the "
                    "accumulator-conversion candidates (suspicion crossed the "
                    "gate via accusation bumps / decay, not a contradiction "
                    "flag)."
                ),
                "records": zero_contradiction_ejections,
            },
            "genuine_class_crosscheck": {
                "rederived_supplied": genuine_supplied_rederived,
                "rederived_converted": genuine_converted_rederived,
                "shipped_supplied": shipped_genuine.supplied,
                "shipped_converted": shipped_genuine.converted,
                "shipped_conversion_rate": shipped_genuine.conversion_rate,
                "match": genuine_crosscheck_ok,
                "shipped_ejection_accuracy": shipped_vc.ejection_accuracy,
                "shipped_contradictions_flagged_but_ignored": (
                    shipped_vc.contradictions_flagged_but_ignored
                ),
                "note": (
                    "The extractor's imported-detector genuine-class re-run vs "
                    "the shipped eval.vote_correctness.compute_genuine_class_"
                    "conversion over the same bytes. match=False is a BLOCKING "
                    "finding (one classifier is wrong)."
                ),
            },
        },
        "wave1_contract_inputs": {
            "note": (
                "Point-6c Wave-1 contract-input aggregates (the headline lens "
                "depends on these). Testimony rows cover EVERY verbally-accused "
                "living subject of either role (innocent rows = cascade-risk "
                "input). Genuine-class rows use the imported 10.4 definition. "
                "Trajectory rows track each multi-meeting vote candidate's "
                "rendered suspicion across meetings. Retry rows are the 10.3 "
                "opening-validation retries / defaults."
            ),
            "testimony": {
                "count": len(testimony_records_all),
                "subjects_impostor": sum(
                    1 for r in testimony_records_all if r["subject_role"] == "IMPOSTOR"
                ),
                "subjects_crew": sum(
                    1 for r in testimony_records_all if r["subject_role"] == "CREWMATE"
                ),
                "genuine_class_subjects": sum(
                    1 for r in testimony_records_all if r["is_genuine_class"]
                ),
                "ejected_subjects": sum(
                    1 for r in testimony_records_all if r["ejected"]
                ),
                "subjects_with_zero_structured_flags": sum(
                    1 for r in testimony_records_all if r["n_structured_flags"] == 0
                ),
                "subjects_with_a_strong_flag": sum(
                    1 for r in testimony_records_all if r["n_strong_flags"] > 0
                ),
                "accused_impostor_not_plurality": sum(
                    1
                    for r in testimony_records_all
                    if r["subject_role"] == "IMPOSTOR" and not r["is_plurality_winner"]
                ),
                "impostor_subjects_who_won_plurality": sum(
                    1
                    for r in testimony_records_all
                    if r["subject_role"] == "IMPOSTOR" and r["is_plurality_winner"]
                ),
                "witnesses_total": sum(r["n_accusers"] for r in testimony_records_all),
                "witness_follow_through_total": sum(
                    r["witness_ballot_follow_through"] for r in testimony_records_all
                ),
                "note": (
                    "One record per (meeting, verbally-accused living subject). "
                    "witness_ballot_follow_through = accusers of the subject who "
                    "also voted for it; the spoken-testimony-never-ingested lens "
                    "reads the gap between accusers and the subject's rendered "
                    "suspicion across the OTHER voters' graphs."
                ),
                "records": testimony_records_all,
            },
            "genuine_class": {
                "count": len(genuine_class_records),
                "supplied": genuine_supplied_rederived,
                "converted": genuine_converted_rederived,
                "conversion_rate": (
                    round(genuine_converted_rederived / genuine_supplied_rederived, 4)
                    if genuine_supplied_rederived
                    else None
                ),
                "verbally_accused": sum(
                    1 for r in genuine_class_records if r["verbally_accused"]
                ),
                "note": (
                    "Every (meeting, true impostor) the imported 10.4 detector "
                    "re-run flags genuine (non-endpoint alibi_vs_sighting). "
                    "converted == ejected that impostor that meeting."
                ),
                "records": genuine_class_records,
            },
            "accumulator_trajectories": {
                "count": len(accumulator_trajectories),
                "players_with_a_downward_move": sum(
                    1 for r in accumulator_trajectories if r["downward_moves"] > 0
                ),
                "total_downward_moves": sum(
                    r["downward_moves"] for r in accumulator_trajectories
                ),
                "downward_moves_with_prior_corroboration": sum(
                    r["downward_moves_with_prior_corroboration"]
                    for r in accumulator_trajectories
                ),
                "note": (
                    "Per multi-meeting vote candidate, the rendered-suspicion "
                    "series across meetings + accusations/corroborations naming "
                    "them. total_downward_moves > 0 confirms Rule-3 / Rule-5 "
                    "un-gating (10.2) is live (a monotone-up store shows zero)."
                ),
                "records": accumulator_trajectories,
            },
            "opening_retries": {
                "recovered": opening_retries_recovered,
                "defaulted": opening_defaults,
                "extra_calls_recovered": opening_retry_extra_calls,
                "extra_input_tokens_recovered": opening_retry_extra_input_tokens,
                "extra_output_tokens_recovered": opening_retry_extra_output_tokens,
                "meetings_that_lost_their_chain_driving_opening": meetings_lost_opening,
                "defaulted_burned_input_tokens": sum(
                    r.get("burned_input_tokens", 0)
                    for r in opening_retry_records
                    if r["outcome"] == "defaulted"
                ),
                "defaulted_burned_output_tokens": sum(
                    r.get("burned_output_tokens", 0)
                    for r in opening_retry_records
                    if r["outcome"] == "defaulted"
                ),
                "note": (
                    "10.3 opening single-retry telemetry. A RECOVERED retry "
                    "(failed once, succeeded second attempt) surfaces as >1 "
                    "opening-slot llm_call for the opener (the burned attempt is "
                    "logged in llm_calls because the manager rejected it AFTER "
                    "the recording client logged the returned text). A DEFAULTED "
                    "opening (exhausted its single retry) surfaces as a "
                    "deadline_default row with turn_kind=='opening'; its burned "
                    "spend lands either in the opening-slot llm_calls (returned-"
                    "but-rejected) or on the deadline_default row itself (a "
                    "pre-log ValidationError). 'lost its chain-driving opening' "
                    "= a defaulted opening whose recorded opening carries no "
                    "accusation. On THIS set every opening-validation event "
                    "ended in a default (recovered==0) and every default lost "
                    "its chain-driving opening."
                ),
                "records": opening_retry_records,
            },
        },
        "wave1_close": {
            "note": (
                "Point-6d Wave-1-CLOSE aggregates (the close-gate lenses depend "
                "on these). REDIRECT = 10.9.2 ballot-target graph guard rewrites "
                "(BALLOT_TARGET_REDIRECT_MARKER); DEFAULTED = 10.9.1 vote-parse "
                "fail-soft SKIPs (VOTE_PARSE_DEFAULT_MARKER); PRE-VOTE FOLDs = "
                "10.7 two-witness testimony folds re-run from the imported "
                "independent_voices predicate (LIVE at record time, the rendered "
                "suspicions already include the bump); EMERGENCY = 10.8 emergency "
                "meetings (must carry no found_body); SELF-ACCUSATIONS = the "
                "lab's emergence class (speaker == accused) the redirect guard "
                "does not cover. Redirect / defaulted counts are cross-checked "
                "against the shipped eval.meeting_quality censuses (a mismatch "
                "raises)."
            ),
            "redirects": {
                "count": len(redirect_records_all),
                "onto_impostor": sum(
                    1
                    for r in redirect_records_all
                    if not r["was_coerced_to_SKIP"]
                    and r["redirected_to_role"] == "IMPOSTOR"
                ),
                "onto_crew": sum(
                    1
                    for r in redirect_records_all
                    if not r["was_coerced_to_SKIP"]
                    and r["redirected_to_role"] == "CREWMATE"
                ),
                "coerced_to_skip": redirect_skip_rederived,
                "redirected_eject": redirect_eject_rederived,
                "original_target_impostor": sum(
                    1
                    for r in redirect_records_all
                    if r["original_target_role"] == "IMPOSTOR"
                ),
                "original_target_crew": sum(
                    1
                    for r in redirect_records_all
                    if r["original_target_role"] == "CREWMATE"
                ),
                "precondition_holds": sum(
                    1
                    for r in redirect_records_all
                    if r["original_below_gate"]
                    and (r["was_coerced_to_SKIP"] or r["redirect_at_or_above_gate"])
                ),
                # Wrong-ejection games whose ejected player owes its plurality to
                # a redirect (the lens-C headline input): a CREWMATE ejected this
                # meeting who was the redirected-to target of >=1 redirect ballot.
                "wrong_ejections_owing_to_a_redirect": sorted(
                    {
                        (r["seed"], r["redirected_to_target"])
                        for r in redirect_records_all
                        for w in wrong_ejections
                        if r["seed"] == w["seed"]
                        and not r["was_coerced_to_SKIP"]
                        and r["redirected_to_target"] == w["ejected_player"]
                    }
                ),
                "shipped_census": {
                    "redirected_ballots": shipped_redirects.redirected_ballots,
                    "redirected_eject_ballots": (
                        shipped_redirects.redirected_eject_ballots
                    ),
                    "redirect_coerced_skip_ballots": (
                        shipped_redirects.redirect_coerced_skip_ballots
                    ),
                },
                "crosscheck_ok": redirect_crosscheck_ok,
                "records": redirect_records_all,
            },
            "defaulted_ballots": {
                "count": len(defaulted_ballot_records_all),
                "by_rendered_verdict": dict(
                    Counter(r["rendered_verdict"] for r in defaulted_ballot_records_all)
                ),
                "seeds": sorted({r["seed"] for r in defaulted_ballot_records_all}),
                "all_games_reached_game_over": no_game_over == 0,
                "shipped_census": {
                    "defaulted_skip_ballots": (
                        shipped_defaulted.defaulted_skip_ballots
                    ),
                    "defaulted_under_must_vote": (
                        shipped_defaulted.defaulted_under_must_vote
                    ),
                    "defaulted_under_must_skip": (
                        shipped_defaulted.defaulted_under_must_skip
                    ),
                    "defaulted_without_render": (
                        shipped_defaulted.defaulted_without_render
                    ),
                },
                "crosscheck_ok": defaulted_ballots_crosscheck_ok,
                "note": (
                    "Every ballot carrying VOTE_PARSE_DEFAULT_MARKER (the whole "
                    "rationale_text). rendered_verdict is the voter's rendered "
                    "§4.6 read (MUST-vote / MUST-skip / no-render), recovered "
                    "from successful llm_calls OR -- when the vote call itself "
                    "failed before its prompt was logged -- the persisted "
                    "rendered_vote_max on the deadline_default failed-call row "
                    "(Task 10.12 / audit H-H-2). firewall_correct flags an "
                    "IMPOSTOR voter's MUST-vote SKIP (the §7.12 teammate "
                    "firewall by design, not a missed eject). On THIS committed "
                    "single-era set the field is absent, so the one defaulted "
                    "ballot (seed-8 m2, p-1 IMPOSTOR) reads no-render here; the "
                    "audit byte-verified its truncated rationale as MUST-vote "
                    "-- it is a firewall-correct-SKIP-under-MUST-VOTE, NOT the "
                    "correct-skip-under-MUST-SKIP the prior framing claimed. The "
                    "game still reaching game_over is the 10.9.1 DoD."
                ),
                "records": defaulted_ballot_records_all,
            },
            "prevote_folds": {
                "count": len(prevote_fold_records_all),
                "subjects_impostor": sum(
                    1
                    for r in prevote_fold_records_all
                    if r["subject_role"] == "IMPOSTOR"
                ),
                "subjects_crew": sum(
                    1
                    for r in prevote_fold_records_all
                    if r["subject_role"] == "CREWMATE"
                ),
                "with_a_listener_over_gate": sum(
                    1
                    for r in prevote_fold_records_all
                    if r["n_listeners_over_gate"] > 0
                ),
                "with_a_listener_ejecting": sum(
                    1
                    for r in prevote_fold_records_all
                    if r["any_listener_ejected_subject"]
                ),
                "converted": sum(1 for r in prevote_fold_records_all if r["ejected"]),
                "note": (
                    "Two-witness pre-vote folds re-run from the imported "
                    "meetings.transcript.independent_voices (>= "
                    f"{TESTIMONY_INDEPENDENCE_BAR} distinct relevance-gated, "
                    "observation-backed voices). The fold is LIVE at record time "
                    "so the listeners' rendered suspicions already carry the "
                    "+0.05 bump; listeners_over_gate are those whose rendered "
                    "suspicion of the folded subject is >= the §4.6 gate."
                ),
                "records": prevote_fold_records_all,
            },
            "emergency_meetings": {
                "count": len(emergency_meeting_records),
                "body_report_count": total_meetings - len(emergency_meeting_records),
                "with_engine_body": sum(
                    1 for r in emergency_meeting_records if r["carried_body"]
                ),
                # 10.11.1: a found_body that SURVIVED onto an emergency opening is
                # the blocking 10.8 leak (MUST be 0 — the backstop + the fail-loud
                # assert both missed it). On this baseline 0.
                "with_opening_found_body_survived": sum(
                    1
                    for r in emergency_meeting_records
                    if r["opening_found_body_survived"]
                ),
                # 10.11.1 residual-fabrication signal: emergency openings the
                # deterministic backstop STRIPPED (the 9B still fabricated a
                # found_body despite the v7 no-body prompt + the single re-ask).
                "with_opening_found_body_stripped": sum(
                    1
                    for r in emergency_meeting_records
                    if r["opening_found_body_stripped"]
                ),
                "caller_impostor": sum(
                    1
                    for r in emergency_meeting_records
                    if r["caller_role"] == "IMPOSTOR"
                ),
                "caller_crew": sum(
                    1
                    for r in emergency_meeting_records
                    if r["caller_role"] == "CREWMATE"
                ),
                "ejected_someone": sum(
                    1
                    for r in emergency_meeting_records
                    if r["ejected_player_id"] is not None
                ),
                "note": (
                    "Every meeting whose engine-recorded trigger is 'emergency'. "
                    "emergency + body_report partitions total_meetings "
                    f"({len(emergency_meeting_records)} + "
                    f"{total_meetings - len(emergency_meeting_records)} == "
                    f"{total_meetings}). with_engine_body (the authoritative "
                    "MeetingTriggeredEvent.body_id) MUST be 0 -- a non-None "
                    "body_id on an emergency trigger is a blocking finding. "
                    "10.11.1: with_opening_found_body_survived MUST be 0 -- a "
                    "found_body that survived onto the FINAL emergency opening is "
                    "the blocking leak (the strip + the fail-loud assert both "
                    "missed it). with_opening_found_body_stripped is the residual-"
                    "fabrication signal: the deterministic backstop removed a "
                    "fabricated found_body after a single re-ask (how often the 9B "
                    "still tried despite the v7 no-body prompt). On this baseline "
                    "0 survived, 10 stripped -- the backstop holds."
                ),
                "records": emergency_meeting_records,
            },
            "self_accusations": {
                "count": len(self_accusation_records_all),
                "by_speaker_role": dict(
                    Counter(r["speaker_role"] for r in self_accusation_records_all)
                ),
                "with_an_adopter": sum(
                    1 for r in self_accusation_records_all if r["n_adopters"] > 0
                ),
                "self_accuser_ejected": sum(
                    1 for r in self_accusation_records_all if r["self_accuser_ejected"]
                ),
                "seeds": sorted({r["seed"] for r in self_accusation_records_all}),
                "note": (
                    "Every accusation where speaker == accused (the impostor "
                    "self-steer the 10.9.2 ballot-target guard does not cover -- "
                    "it constrains the ballot TARGET, not a turn accusation). "
                    "adopted_by = OTHER voters who then targeted the self-accuser."
                ),
                "records": self_accusation_records_all,
            },
        },
        "wave2_crater": {
            "note": (
                "Point-6e Wave-2 CRATER aggregates (the headline lens depends on "
                "these). ACTIONS BY ROLE = the blending census + the do_task "
                "integrity invariant (impostor do_task EMISSIONS may be >0 once the "
                "10.14 lever fires, but real task ADVANCES by an impostor MUST be 0 "
                "-- the engine rejects the unowned pretend id). EFFECTIVE "
                "DEFLECTION = the imported blend-vs-deflect split (real skill vs "
                "SKIP-saved). INFORM CHANNEL = the 10.16 fifth-channel conversions. "
                "WIN DECISION = eject-DECIDED vs STOPWATCH (the R1 verdict input). "
                "All folds IMPORT their one-home source; the inform count is "
                "cross-checked against the shipped multi-signal census."
            ),
            "actions_by_role": {
                "crewmate_action_counts": dict(action_tally.crewmate_action_counts),
                "impostor_action_counts": dict(action_tally.impostor_action_counts),
                "impostor_do_task_emissions": impostor_do_task_emissions,
                "crewmate_do_task": indistinguishability.crewmate_do_task,
                "impostor_wait": indistinguishability.impostor_wait,
                "crewmate_wait": indistinguishability.crewmate_wait,
                "impostor_actions_total": indistinguishability.impostor_actions_total,
                "crewmate_actions_total": indistinguishability.crewmate_actions_total,
                "impostor_wait_share": indistinguishability.impostor_wait_share,
                "crewmate_wait_share": indistinguishability.crewmate_wait_share,
                "top_idler_wait_share": indistinguishability.top_idler_wait_share,
                "note": (
                    "Per-role action census via the imported "
                    "eval.action_ingest.tally_actions_by_role -> "
                    "compute_indistinguishability over the SAME shipped report "
                    "games. impostor_do_task_emissions is the 10.14 blending lever "
                    "firing (a recorded do_task action); see do_task_integrity for "
                    "the invariant that NO emission advanced a real task instance."
                ),
            },
            "do_task_integrity": {
                "impostor_real_task_advances": impostor_real_task_advances,
                "impostor_do_task_emissions": impostor_do_task_emissions,
                "crew_task_progress_events": crew_task_progress_events,
                "crew_task_completed_events": crew_task_completed_events,
                "records": impostor_task_advances,
                "note": (
                    "The 10.14 inviolable: a walked TaskProgressed/TaskCompleted "
                    "event with an IMPOSTOR actor (a fake task that moved a REAL "
                    "task counter). MUST be 0 -- the engine rejects the unowned "
                    "pretend id, so a fake task can never reach the CREWMATE_TASKS "
                    "denominator. impostor_real_task_advances > 0 is a BLOCKING "
                    "IMPTASK finding (emitted in the walk). Note the contrast with "
                    "impostor_do_task_emissions (the recorded action, which IS >0 "
                    "on W2): emission != advance is the whole integrity point."
                ),
            },
            "effective_deflection": {
                "accused_impostor_events": (
                    effective_deflection.accused_impostor_events
                ),
                "accused_impostor_survivals": (
                    effective_deflection.accused_impostor_survivals
                ),
                "active_survivals": effective_deflection.active_survivals,
                "effective_deflections": effective_deflection.effective_deflections,
                "named_target_deflections": (
                    effective_deflection.named_target_deflections
                ),
                "third_party_deflections": (
                    effective_deflection.third_party_deflections
                ),
                "skip_saved_active_survivals": (
                    effective_deflection.skip_saved_active_survivals
                ),
                "note": (
                    "The imported eval.meeting_quality.compute_effective_deflection "
                    "blend-vs-deflect split. effective_deflections is the real "
                    "deception-SKILL subcount (the counter-accusation MOVED the "
                    "eject-plurality off the impostor); skip_saved_active_survivals "
                    "is survival by the SKIP bloc, not skill (lens-C territory)."
                ),
            },
            "inform_channel_conversions": {
                "count": len(inform_channel_conversions),
                "multi_signal": sum(
                    1 for r in inform_channel_conversions if r["multi_signal"]
                ),
                "clean": sum(1 for r in inform_channel_conversions if r["clean"]),
                "marginal": sum(
                    1 for r in inform_channel_conversions if not r["clean"]
                ),
                "shipped_census_inform_count": (
                    multi_signal.conversions_with_single_witness_inform
                ),
                "crosscheck_ok": inform_crosscheck_ok,
                "multi_signal_census": {
                    "impostor_ejections": multi_signal.impostor_ejections,
                    "multi_signal_conversions": multi_signal.multi_signal_conversions,
                    "single_signal_conversions": (
                        multi_signal.single_signal_conversions
                    ),
                    "unattributed_conversions": (multi_signal.unattributed_conversions),
                    "conversions_with_contradiction_flag": (
                        multi_signal.conversions_with_contradiction_flag
                    ),
                    "conversions_with_body_proximity": (
                        multi_signal.conversions_with_body_proximity
                    ),
                    "conversions_with_vent_witness": (
                        multi_signal.conversions_with_vent_witness
                    ),
                    "conversions_with_prior_meeting_carry": (
                        multi_signal.conversions_with_prior_meeting_carry
                    ),
                    "conversions_with_single_witness_inform": (
                        multi_signal.conversions_with_single_witness_inform
                    ),
                    "multi_signal_rate": multi_signal.multi_signal_rate,
                },
                "note": (
                    "Every impostor ejection whose 10.16 channel decomposition "
                    "credits CHANNEL_SINGLE_WITNESS_INFORM (the crew-overshoot half "
                    "of the crater). clean = an observation-backed witness of the "
                    "subject is in the transcript; marginal = the inform band "
                    "aligned on the lattice without a surfaced first-hand sighting. "
                    "count is cross-checked == the shipped multi-signal census's "
                    "per-channel inform presence count (a mismatch raises)."
                ),
                "records": inform_channel_conversions,
            },
            "win_decision": {
                "eject_decided_wins": sum(
                    1 for r in win_decision_records if r["was_eject_decided"]
                ),
                "stopwatch_wins": sum(
                    1 for r in win_decision_records if r["was_stopwatch"]
                ),
                "impostor_wins": sum(
                    1 for r in win_decision_records if r["winner"] == "IMPOSTORS"
                ),
                "second_impostor_survival_to_stopwatch": sum(
                    1
                    for r in win_decision_records
                    if r["was_stopwatch"] and r["impostors_alive_at_end"] >= 1
                ),
                "stopwatch_tick_margins": sorted(
                    r["stopwatch_tick_margin"]
                    for r in win_decision_records
                    if r["stopwatch_tick_margin"] is not None
                ),
                "median_stopwatch_tick_margin": (
                    int(
                        statistics.median(
                            [
                                r["stopwatch_tick_margin"]
                                for r in win_decision_records
                                if r["stopwatch_tick_margin"] is not None
                            ]
                        )
                    )
                    if any(
                        r["stopwatch_tick_margin"] is not None
                        for r in win_decision_records
                    )
                    else None
                ),
                "note": (
                    "Per game eject-DECIDED (CREWMATE_EJECT, both impostors removed "
                    "by the meeting layer) vs STOPWATCH (CREWMATE_TASKS with an "
                    "impostor still alive). The R1 load-bearing number: "
                    "eject_decided_wins == 0 on this baseline means the clock, not "
                    "deduction, closes every crew win (24 impostors ejected but "
                    "never the 2nd-and-deciding one in time). stopwatch_tick_margin "
                    "= game_over_tick - last impostor-ejecting meeting tick."
                ),
                "records": win_decision_records,
            },
            "cross_era_trajectory": cross_era_trajectory,
            # rubric_scorecard is patched in AFTER the aggregates dict is built
            # (it folds the assembled facts through experiments/lab/rubric_score),
            # so lens C can name the highest-leverage R-item the retune should move.
            "rubric_scorecard": None,
        },
        "invalid_accusation_target_drops": {
            "accusation_claim_drops": invalid_accusation_target_drops_total,
            "accusation_claim_seeds": sorted(invalid_accusation_target_seeds),
            "ballot_target_drops": invalid_ballot_target_drops_total,
            "ballot_target_seeds": sorted(invalid_ballot_target_seeds),
            "total": (
                invalid_accusation_target_drops_total
                + invalid_ballot_target_drops_total
            ),
        },
        "defaulted_turns": {
            "count": len(defaulted_turns),
            "distinct": len(
                {
                    (d["seed"], d["meeting_id"], d["turn_index"], d["speaker"])
                    for d in defaulted_turns
                }
            ),
            "unparsed": defaulted_turn_unparsed,
            "by_turn_kind": dict(Counter(d["turn_kind"] for d in defaulted_turns)),
            "note": (
                "count is defaulted TURN rows (opening / reply / opt_in); "
                "distinct de-duplicates on (seed, meeting, turn_index, "
                "speaker). Defaulted VOTES are not turns and are excluded "
                "(censused under defaulted_ballots). The 9.10 writer dedup "
                "drops byte-identical duplicate failed_call rows at the write "
                "chokepoint, so on this set duplicate_failed_call_rows.count is "
                "0 -- the prior note naming seeds 8/36/39 as emitting a "
                "duplicate turn row was stale (seed-8's only failed_call is a "
                "VOTE default; seeds 36/39 have 0 failed_calls). See "
                "duplicate_failed_call_rows for the live dup census."
            ),
            "records": defaulted_turns,
        },
        "free_text_length_chars": {
            kind: _length_distribution(samples)
            for kind, samples in free_text_len_samples.items()
        },
        "duplicate_failed_call_rows": {
            "count": duplicate_failed_call_rows,
            "seeds": sorted(duplicate_failed_call_seeds),
            "double_counted_input_tokens": duplicate_failed_call_input_tokens,
            "double_counted_output_tokens": duplicate_failed_call_output_tokens,
            "note": (
                "byte-identical failed_call rows written twice for one "
                "defaulted turn; inflates failed-call token telemetry but "
                "not meeting outcomes."
            ),
        },
        "total_calls": total_calls,
        "total_failed_calls": total_failed_calls,
        "tokens": {
            "input": agg_input_tokens,
            "output": agg_output_tokens,
            "cost_usd": agg_cost,
        },
    }

    facts = {
        "git_head": _git_head(),
        "sample_dir": str(SAMPLE_DIR),
        "seedset": SEEDSET,
        "roster": roster,
        "games_analyzed": games_analyzed,
        "self_checks": self_checks,
        "aggregates": aggregates,
        "games": games,
    }

    # ---- RUBRIC SCORECARD (point 6f) ----
    # Fold the assembled facts through experiments/lab/rubric_score (the one home
    # for the R1-R7 interestingness scorecard; it reads the SAME facts JSON) so
    # lens C can name the highest-leverage R-item the retune should move, without
    # re-reading the file. Imported, never re-implemented; a divergent replica
    # would drift from the committed scorer. Patched into the already-built
    # aggregates (the scorer needs the full facts, which reference the aggregates).
    rubric_rows = _rubric_score(facts)
    wave2_crater_agg = cast("dict[str, Any]", aggregates["wave2_crater"])
    wave2_crater_agg["rubric_scorecard"] = {
        "note": (
            "experiments/lab/rubric_score R1-R7 scorecard folded over THIS facts "
            "file (the design-thread interestingness layer, NOT the shipped gate). "
            "Each row is (item, value, desired_direction); lens C names the "
            "highest-leverage R-item the Wave-2 retune should move."
        ),
        "rows": [
            {"item": item, "value": value, "desired": desired}
            for item, value, desired in rubric_rows
        ],
    }

    tmpdir = os.environ.get("TMPDIR", "/tmp")
    facts_path = Path(tmpdir) / f"ailibi-gameplay-facts-{SEEDSET}.json"
    facts_path.write_text(
        json.dumps(facts, indent=2, sort_keys=False), encoding="utf-8"
    )

    # Emit machine-readable summary for the caller on stdout.
    print(
        json.dumps(
            {
                "facts_path": str(facts_path),
                "games_analyzed": games_analyzed,
                "aggregates": aggregates,
                "n_findings": len(findings),
                "findings": findings,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
