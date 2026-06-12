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
from typing import Any

from pydantic import TypeAdapter

from engine.actions import Action
from engine.events import (
    ActionRejectedEvent,
    KilledEvent,
    MeetingTriggeredEvent,
)
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval._suspicion_parse import (
    SKIP_SUSPICION_THRESHOLD,
    parse_rendered_max_suspicion,
)
from meetings.manager import (
    INVALID_ACCUSATION_TARGET_MARKER,
    INVALID_VOTE_TARGET_MARKER,
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
    WEAK_REASON_NARROW_WINDOW,
    WEAK_REASON_SELF_STATED,
    detect_contradictions,
    is_canonically_ordered,
    is_weak_contradiction,
    next_chain_step,
)
from agents.memory.beliefs import (
    CONTRADICTION_SUSPICION_DELTA,
    WEAK_CONTRADICTION_SUSPICION_DELTA,
)
from eval.balance_eval import load_tournament_report
from eval.vote_correctness import (
    compute_genuine_class_conversion,
    compute_vote_correctness,
)
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

# A defaulted-turn failed_call carries the turn coordinates in its error_message,
# e.g. "reply turn (turn 1) defaulted (validation); p-9 submitted no turn ...".
_DEFAULTED_TURN_RE: re.Pattern[str] = re.compile(
    r"(?P<kind>opening|reply|opt_in) turn \(turn (?P<index>\d+)\) defaulted"
    r"[^;]*;\s*(?P<speaker>\S+) submitted no turn"
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
    roles: Mapping[str, str],
    living_ids: frozenset[str],
    findings: list[dict[str, Any]],
    invariant_failures: list[str],
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
    for b in meeting_entry.ballots:
        voter_role = roles.get(b.voter, "UNKNOWN")
        is_skip = b.target == "SKIP"
        target_role = None if is_skip else roles.get(b.target, "UNKNOWN")
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
        for fc in failed_call_entries:
            if fc.error_type != "deadline_default":
                continue
            m = _DEFAULTED_TURN_RE.search(fc.error_message)
            if m is not None and m.group("kind") == "opening":
                opening_defaulted_meeting_ids.add(fc.meeting_id)

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
                roles=roles,
                living_ids=living_ids,
                findings=findings,
                invariant_failures=invariant_failures,
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
                "count includes byte-identical duplicate failed_call rows "
                "(seeds 8/36/39 emit the same defaulted-turn row twice); "
                "distinct is the de-duplicated turn count."
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
