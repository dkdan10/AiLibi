"""The V&J instruments — judgment metrics + the deterministic voice tier.

Task 16.10 (tasks/phase-16.md; audits/post-phase-14-Voice-and-Judgment-
planning.md §2; audits/audit-phase-15-close.md §11): the phase's own
before/after instrument, committed BEFORE the levers turn on, so the 16.17
close reads the same gauges on both sides of the Voice & Judgment programs.
Diagnostics ONLY — nothing here gates; the referee (``eval/watchability.py``)
alone gates. The close QUOTES these numbers.

Three groups, one report:

* **Judgment metrics.** The zero-flag conviction rate — an ``EJECTED``
  meeting whose ejected player is named by ZERO recorded
  :class:`~meetings.schemas.ContradictionRef` (the planning doc §2.1
  definition; the same flagged-subject union
  ``meetings.manager.guard_ballot_citation`` reads) — with its soft/hard
  split read off Task 16.3's TYPED :class:`~agents.memory.beliefs.
  SuspicionProvenance` decomposition at the reconstructed PRE-VOTE belief
  state, exactly where the ballot render reads it
  (``meetings.manager._suspicion_graph_with_contradictions`` over the
  meeting-open accessor snapshots — the one production fold, never a
  parallel sum). This REPLACES the planning doc's rendered-value proxy
  (max rendered suspicion ``>= 0.70`` = hard-backed); the proxy is still
  computed from the recorded vote-prompt bytes and reported beside the
  typed split as the documented cross-check. Citation compliance counts
  every ballot's two citation channels
  (:attr:`~meetings.schemas.VoteBallot.primary_reason_id` against this
  meeting's transcript turn ids;
  :attr:`~meetings.schemas.VoteBallot.primary_reason_observation_id`
  against the voter's reconstructed episodic observation-id set), valid vs
  dangling. Ballot-confidence calibration scores Brier + ECE against
  conviction correctness (``roles[target] == "IMPOSTOR"``, SKIP excluded)
  with the Task 5.3 binning (``eval.accusation_calibration``) — the 15.11
  recorded-ballot harness pattern.

* **The deterministic voice tier.** Within-meeting echo rate (share of
  ballots whose normalized rationale is a ``>= 0.5`` trigram-Jaccard
  near-duplicate of another SAME-meeting ballot), response-skeleton share
  (share of ballots in the set's top-5 exact normalized-skeleton clusters
  of size ``>= 2``), and distinct-n diversity (distinct skeletons /
  ballots, plus distinct-1/-2 token n-gram ratios). Normalization follows
  the planning doc §2.5 recipe: player ids -> ``player``, canonical room
  names -> ``room``, digit runs -> ``n``, lowercased, whitespace
  collapsed; leading bracketed audit markers (the manager's
  ``[... ] ``-prefixed coercion/normalization notes) are stripped first —
  they are system text, not model voice. Pure string folds: $0,
  deterministic, double-run identical. The LLM-judged voice tier is
  explicitly OUT (the task's $0 discipline).

* **The pooling census.** :class:`eval.funnel.PoolingFunnelReport`
  (roll-call coverage, vouch + GROUNDED-vouch rates, absence-set sizes,
  whereabouts-lie detection) is embedded as ``pooling``, computed from the
  SAME walk — so ``--vj`` is one machine-readable object per set and 16.17
  reads voice ALONGSIDE zero-flag (the phase's named NO-GO pairing).

Reconstruction + cross-checks. The walk (``eval.funnel._walk_game_vj``)
rebuilds each agent's memory by feeding it exactly what the live game fed it;
every recorded state hash is verified. Two instrument-integrity gauges ride
the report: ``provenance_sum_breaches`` counts reconstructed pre-vote rows
whose rendered scalar matches NEITHER the raw 16.3 sum
``0.5 + sum(the eight fields)`` NOR the graduated J1 clamp of that sum
(tolerance :data:`~agents.memory.beliefs.SUSPICION_PROVENANCE_ATOL`;
:func:`_row_sum_breaches`) — the J1 gate (Task 16.4) CLAMPS an entirely-soft
conviction-grade render to :data:`~agents.memory.beliefs.
HARD_EVIDENCE_GATE_RENDER_CEIL` while keeping the raw typed provenance, so a
by-design clamped row (five committed seed-12 9p2i rows; the close §2
signature) is EXEMPT by the production predicate itself, never a phantom
breach — while a scalar matching neither the raw sum nor the clamp value still
counts. ``rendered_row_mismatches`` counts per-player suspicion values in the
recorded vote prompts that the reconstruction fails to reproduce (tolerance
0.005 — the prompts render 2 decimals). Both are 0 on every committed set
(pinned in ``tests/eval/test_vj_instruments.py``). The typed-vs-proxy split
agreement is reported, not enforced: the planning doc §2.3 documents why the
value proxy misclassifies (a soft accumulation can climb into the ``>= 0.70``
band; a hard pin can mix with soft deltas) — that documented divergence is
the tolerance.

The accessors and the fold read no environment at all: every lever they once
consulted graduated, so the instrument is pure and $0 (no ``AILIBI_*`` reads)
and the reconstruction runs the baseline-7 substrate the committed sets were
recorded under, matching the recorded bytes exactly.

The walk reads the replay through :mod:`eval.replay_walk`, which calls
``read_all_entries`` directly and performs NO substrate check -- so nothing on
this path refuses a recording made under an EARLIER substrate the way the API
replay loader and the audit workflows' re-extraction spine do. Against such a
recording the reconstruction would run today's always-on rules over legacy
bytes, and the divergence would NOT be confined to the J1-clamped rendered
scalar ``rendered_row_mismatches`` counts: retired rules (the absence prior, the
evidence-quality fold) move the typed decomposition the split reads as well.
These cells are therefore stated for the committed sets only.

JSON report schema (``VJInstrumentReport.model_dump()`` / the
``scripts/measure_baseline.py --vj --json`` rows), consumed by the Task 16.17
close for the before/after finding — STABLE::

    {
      "replay_set_dir": str,
      "num_players": int, "num_impostors": int, "tasks_per_crewmate": int,
      "games_total": int, "meetings_total": int,
      # -- zero-flag conviction channel (over EJECTED meetings) --
      "convictions_total": int,
      "zero_flag_convictions": int,
      "zero_flag_conviction_rate": float | null,   # null with 0 convictions
      "zero_flag_crew_convictions": int,            # ejected was CREWMATE
      "zero_flag_impostor_convictions": int,
      # typed split of the zero-flag convictions (16.3 provenance at pre-vote)
      "zero_flag_hard_backed": int, "zero_flag_soft_only": int,
      "zero_flag_unattributed_only": int, "zero_flag_no_row": int,
      # the planning-doc rendered-value proxy, reported beside the typed split
      "zero_flag_proxy_hard_backed": int, "zero_flag_proxy_soft_only": int,
      "zero_flag_proxy_sub_gate": int, "zero_flag_proxy_no_render": int,
      "zero_flag_split_agreements": int,        # typed/proxy agree on HARD axis
      "zero_flag_split_disagreements": int,
      # -- reconstruction cross-checks (0 breaches/mismatches on committed) --
      "provenance_rows_checked": int, "provenance_sum_breaches": int,
      "rendered_rows_compared": int, "rendered_row_mismatches": int,
      # -- citation compliance (over all ballots) --
      "ballots_total": int, "skip_ballots": int, "eject_ballots": int,
      "turn_citations": int, "turn_citations_valid": int,
      "turn_citations_dangling": int,
      "observation_citations": int, "observation_citations_valid": int,
      "observation_citations_dangling": int,
      "cited_eject_ballots": int,               # non-SKIP w/ >=1 VALID citation
      "citation_compliance_rate": float | null, # cited/eject; null w/ 0 ejects
      "nulled_reason_id_markers": int,          # recorded coercion audit trail
      "nulled_observation_id_markers": int,
      "coerced_zero_flag_markers": int,
      # -- ballot-confidence calibration vs conviction correctness --
      "ballot_confidence_brier": float | null,  # null with 0 samples
      "ballot_confidence_ece": float | null,
      "ballot_calibration_total": int,
      "ballot_calibration_low_power": bool,     # < 5 populated decile bins
      # -- deterministic voice tier --
      "voice_ballots_total": int, "echo_ballots": int,
      "within_meeting_echo_rate": float | null,
      "response_skeleton_share": float | null,
      "distinct_skeletons": int, "distinct_skeleton_ratio": float | null,
      "distinct_1": float | null, "distinct_2": float | null,
      # -- the pooling census (eval.funnel.PoolingFunnelReport schema) --
      "pooling": { ... },
      "per_meeting": [ VJMeetingRow, ... ]      # judgment + voice per meeting
    }

Pure + offline: no network, no ``AILIBI_*`` env, no LLM. The public surface
(stable — downstream tasks import these): :func:`compute_vj_instruments`,
:class:`VJInstrumentReport`, :class:`VJMeetingRow`.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict

from agents.memory.beliefs import (
    SUSPICION_PROVENANCE_ATOL,
    hard_evidence_gated_suspicion,
)
from engine.entities import PlayerId
from engine.world import load_canonical_map
from eval._suspicion_parse import parse_rendered_max_suspicion
from eval.accusation_calibration import (
    DEFAULT_N_BINS,
    MIN_POPULATED_BINS_FOR_POWER,
    _bin_samples,
    _is_impostor,
)
from eval.funnel import (
    PoolingFunnelReport,
    _pooling_report_from_walks,
    _VJMeeting,
    _walk_set_vj,
)
from eval.meeting_quality import _parse_suspicion_graph
from meetings.manager import (
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    _provenance_from_entry,
    _suspicion_graph_with_contradictions,
    derive_belief_evidence,
)
from meetings.render_contract import SuspicionEntry
from meetings.transcript import MeetingTriggerKind

TypedSplit: TypeAlias = Literal[
    "hard_backed", "soft_only", "unattributed_only", "no_row"
]
"""The 16.3 typed classification of a conviction's pre-vote evidence.

Read off the ejected player's :class:`~meetings.render_contract.
SuspicionEntry` rows in the CONVICTING voters' pre-vote folded graphs:
``hard_backed`` — some convicting voter's row carries a hard component
(``|flag_lift + body_proximity + kill_or_vent_pin + carried_hard| >
SUSPICION_PROVENANCE_ATOL``); ``soft_only`` — no hard component anywhere but
some row carries positive verbal lift (``soft_total > ATOL``, the J1
predicate's sense); ``unattributed_only`` — rows exist but carry neither;
``no_row`` — the ejected player appears in NO convicting voter's graph.
"""

ProxySplit: TypeAlias = Literal["hard_backed", "soft_only", "sub_gate", "no_render"]
"""The planning-doc §2.3 rendered-value proxy buckets (the instrument this
module's typed split replaces): the MAX rendered suspicion of the ejected
player across the convicting voters' recorded vote prompts — ``>= 0.70``
hard-backed, ``0.60–0.69`` soft-only, ``< 0.60`` sub-gate, absent from every
convicting voter's rendered graph ``no_render``."""

_PROXY_HARD_BAR = 0.70
_PROXY_GATE_BAR = 0.60
# The vote prompt renders suspicion at 2 decimals; the reconstruction matches
# a parsed value when within half an ulp of that rendering.
_RENDERED_MATCH_ATOL = 0.005

# Stable grep prefixes of the manager's citation-coercion audit markers (the
# constants are ``{field!r}``-format templates; everything before the first
# placeholder is the pinned literal prefix).
_NULLED_REASON_PREFIX = INVALID_REASON_ID_MARKER.split("{", 1)[0]
_NULLED_OBSERVATION_PREFIX = INVALID_OBSERVATION_ID_MARKER.split("{", 1)[0]
_COERCED_ZERO_FLAG_PREFIX = UNCITED_ZERO_FLAG_EJECT_MARKER.split("{", 1)[0]

_PLAYER_ID_RE = re.compile(r"\bp-\d+\b", re.IGNORECASE)
_DIGIT_RUN_RE = re.compile(r"\d+")
# A leading system marker is "[...] " — strip repeatedly before voice folds.
_LEADING_MARKER_RE = re.compile(r"^\[[^\]]*\]\s*")

_ECHO_JACCARD_BAR = 0.5
_SKELETON_TOP_K = 5


# --------------------------------------------------------------------------- #
# Report types (public, stable)                                               #
# --------------------------------------------------------------------------- #


class VJMeetingRow(BaseModel):
    """Judgment + voice measurements for ONE resolved meeting (frozen).

    The judgment fields (``ejected_is_impostor`` .. ``splits_agree_on_hard``)
    are ``None`` on a ``SKIPPED`` meeting — there is no conviction to
    classify. ``echo_rate`` is ``None`` when the meeting recorded no ballots.
    Voice rides the same row as judgment so the 16.17 close reads them
    together per meeting.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    meeting_id: str
    tick: int
    trigger_kind: MeetingTriggerKind
    outcome: str
    ejected: PlayerId | None
    ejected_is_impostor: bool | None
    zero_flag_conviction: bool | None
    typed_split: TypedSplit | None
    proxy_split: ProxySplit | None
    splits_agree_on_hard: bool | None
    # citation compliance
    ballots: int
    skip_ballots: int
    turn_citations_valid: int
    turn_citations_dangling: int
    observation_citations_valid: int
    observation_citations_dangling: int
    cited_eject_ballots: int
    # deterministic voice tier
    echo_ballots: int
    echo_rate: float | None
    distinct_skeletons: int


class VJInstrumentReport(BaseModel):
    """The V&J instruments over one replay set (frozen value object).

    Aggregates the per-meeting rows into the Task 16.10 gauges (see the
    module docstring JSON schema). Every rate with an empty denominator is
    ``None`` (undefined, not ``0.0``) — the ``eval`` convention. ``pooling``
    embeds the :class:`eval.funnel.PoolingFunnelReport` computed from the
    same walk.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    meetings_total: int
    # zero-flag conviction channel
    convictions_total: int
    zero_flag_convictions: int
    zero_flag_conviction_rate: float | None
    zero_flag_crew_convictions: int
    zero_flag_impostor_convictions: int
    zero_flag_hard_backed: int
    zero_flag_soft_only: int
    zero_flag_unattributed_only: int
    zero_flag_no_row: int
    zero_flag_proxy_hard_backed: int
    zero_flag_proxy_soft_only: int
    zero_flag_proxy_sub_gate: int
    zero_flag_proxy_no_render: int
    zero_flag_split_agreements: int
    zero_flag_split_disagreements: int
    # reconstruction cross-checks
    provenance_rows_checked: int
    provenance_sum_breaches: int
    rendered_rows_compared: int
    rendered_row_mismatches: int
    # citation compliance
    ballots_total: int
    skip_ballots: int
    eject_ballots: int
    turn_citations: int
    turn_citations_valid: int
    turn_citations_dangling: int
    observation_citations: int
    observation_citations_valid: int
    observation_citations_dangling: int
    cited_eject_ballots: int
    citation_compliance_rate: float | None
    nulled_reason_id_markers: int
    nulled_observation_id_markers: int
    coerced_zero_flag_markers: int
    # ballot-confidence calibration vs conviction correctness
    ballot_confidence_brier: float | None
    ballot_confidence_ece: float | None
    ballot_calibration_total: int
    ballot_calibration_low_power: bool
    # deterministic voice tier
    voice_ballots_total: int
    echo_ballots: int
    within_meeting_echo_rate: float | None
    response_skeleton_share: float | None
    distinct_skeletons: int
    distinct_skeleton_ratio: float | None
    distinct_1: float | None
    distinct_2: float | None
    # pooling census (the eval.funnel extension region, same walk)
    pooling: PoolingFunnelReport
    per_meeting: tuple[VJMeetingRow, ...]


# --------------------------------------------------------------------------- #
# Judgment folds                                                              #
# --------------------------------------------------------------------------- #


def _pre_vote_graphs(
    meeting: _VJMeeting,
) -> Mapping[PlayerId, tuple[SuspicionEntry, ...]]:
    """Every living voter's PRE-VOTE folded suspicion graph.

    Applies the production pre-vote fold
    (``meetings.manager._suspicion_graph_with_contradictions``) to each
    voter's meeting-open snapshot with the meeting's RECORDED contradictions
    and the evidence derived exactly as the manager derives it before ballot
    collection (``derive_belief_evidence`` over the final transcript, no
    trigger kind — mirroring the production call). The fold consults no
    environment. These are the rows the ballot render reads; the rendered
    cross-check pins them against the recorded prompt bytes.
    """

    evidence = derive_belief_evidence(
        meeting.transcript,
        contradictions=meeting.contradictions,
        roster=meeting.living,
    )
    reporter = meeting.triggered_by if meeting.trigger_kind == "report" else None
    graphs: dict[PlayerId, tuple[SuspicionEntry, ...]] = {}
    for voter in sorted(meeting.living):
        graphs[voter] = _suspicion_graph_with_contradictions(
            voter_id=voter,
            suspicion_graph=meeting.suspicion_graph_by_voter[voter],
            contradictions=meeting.contradictions,
            fellow_impostor_ids=meeting.fellow_impostor_ids_by_voter[voter],
            evidence=evidence,
            transcript=meeting.transcript,
            reporter=reporter,
        )
    return graphs


def _entry_for(
    graph: Sequence[SuspicionEntry], player_id: PlayerId
) -> SuspicionEntry | None:
    for entry in graph:
        if entry.player_id == player_id:
            return entry
    return None


def _entry_hard_total(entry: SuspicionEntry) -> float:
    return (
        entry.flag_lift
        + entry.body_proximity
        + entry.kill_or_vent_pin
        + entry.carried_hard
    )


def _entry_soft_total(entry: SuspicionEntry) -> float:
    return entry.testimony_spread + entry.accusation_carry + entry.carried_soft


def _typed_split(
    ejected: PlayerId,
    convicting_voters: Sequence[PlayerId],
    graphs: Mapping[PlayerId, tuple[SuspicionEntry, ...]],
) -> TypedSplit:
    """Classify one conviction's evidence off the typed pre-vote decomposition.

    Meeting-level, mirroring the proxy's max-over-convicting-voters shape:
    hard wins over soft wins over unattributed; a conviction with no row for
    the ejected player in ANY convicting voter's graph is ``no_row`` (the
    proxy's "pure narrative" bucket, now typed).
    """

    saw_row = False
    saw_soft = False
    for voter in convicting_voters:
        entry = _entry_for(graphs[voter], ejected)
        if entry is None:
            continue
        saw_row = True
        if abs(_entry_hard_total(entry)) > SUSPICION_PROVENANCE_ATOL:
            return "hard_backed"
        if _entry_soft_total(entry) > SUSPICION_PROVENANCE_ATOL:
            saw_soft = True
    if saw_soft:
        return "soft_only"
    return "unattributed_only" if saw_row else "no_row"


def _vote_prompts(meeting: _VJMeeting) -> Mapping[PlayerId, str]:
    """Each voter's recorded vote-ballot prompt (the §4.6-verdict-bearing call).

    A meeting's ``llm_calls`` mix turn and vote prompts; the vote prompt is
    the one carrying the rendered §4.6 maximum-suspicion line
    (``eval._suspicion_parse.parse_rendered_max_suspicion``) — the
    ``eval.meeting_quality`` identification pattern. A defaulted ballot has
    no recorded vote prompt and is simply absent.
    """

    prompts: dict[PlayerId, str] = {}
    for call in meeting.llm_calls:
        if call.agent_id is None:
            continue
        if parse_rendered_max_suspicion(call.prompt) is not None:
            prompts[call.agent_id] = call.prompt
    return prompts


def _proxy_split(
    ejected: PlayerId,
    convicting_voters: Sequence[PlayerId],
    vote_prompts: Mapping[PlayerId, str],
) -> ProxySplit:
    """The planning-doc rendered-value proxy, read from the recorded prompts."""

    rendered_max: float | None = None
    for voter in convicting_voters:
        prompt = vote_prompts.get(voter)
        if prompt is None:
            continue
        value = _parse_suspicion_graph(prompt).get(ejected)
        if value is None:
            continue
        rendered_max = value if rendered_max is None else max(rendered_max, value)
    if rendered_max is None:
        return "no_render"
    if rendered_max >= _PROXY_HARD_BAR:
        return "hard_backed"
    if rendered_max >= _PROXY_GATE_BAR:
        return "soft_only"
    return "sub_gate"


def _row_expected_scalars(entry: SuspicionEntry) -> tuple[float, float]:
    """The two legitimate rendered scalars for a reconstructed row: (raw, J1-clamped).

    ``raw`` is the Task-16.3 provenance sum ``0.5 + Σ(the eight channels)``; the
    second is the graduated J1 gate applied to that sum -- the SAME production
    predicate the live runner renders through (Task 16.4,
    :func:`~agents.memory.beliefs.hard_evidence_gated_suspicion`, off the 16.3
    decomposition rebuilt by the manager's own
    :func:`~meetings.manager._provenance_from_entry`). The two coincide on every
    row except an entirely-soft conviction-grade one, where the gate clamps the
    render to :data:`~agents.memory.beliefs.HARD_EVIDENCE_GATE_RENDER_CEIL` one
    notch below the raw sum while KEEPING the raw typed provenance.
    """

    provenance = _provenance_from_entry(entry)
    raw = 0.5 + provenance.total
    return raw, hard_evidence_gated_suspicion(raw, provenance)


def _row_sum_breaches(entry: SuspicionEntry) -> bool:
    """Whether a reconstructed pre-vote row breaks the 16.3 provenance-sum
    invariant, accounting for the graduated J1 clamp.

    The raw 16.3 invariant is ``0.5 + Σ(the eight channels) == suspicion``. The
    reconstruction legitimately emits EITHER the raw scalar -- the pre-vote fold
    path (``meetings.manager._suspicion_graph_with_contradictions``) keeps
    ``0.5 + Σ == suspicion`` -- OR the J1-CLAMPED scalar, when an entirely-soft
    conviction-grade meeting-open snapshot the live runner already clamped passes
    through un-folded (the J1 render gate fired at record time, so the snapshot
    carries the clamped scalar beside its raw typed provenance). A row is SOUND
    when its rendered ``suspicion`` matches EITHER; a REAL breach matches NEITHER.
    The clamp arm is the production Task-16.4 gate verbatim
    (:func:`~agents.memory.beliefs.hard_evidence_gated_suspicion`, tolerance
    :data:`~agents.memory.beliefs.SUSPICION_PROVENANCE_ATOL`) -- never a looser
    re-derivation -- so a by-design clamped row is exempt by exactly the arithmetic
    the render applied, while a genuinely-wrong scalar on a clamped row (matching
    neither the raw sum nor the clamp value) still counts.
    """

    raw, clamped = _row_expected_scalars(entry)
    return (
        abs(raw - entry.suspicion) > SUSPICION_PROVENANCE_ATOL
        and abs(clamped - entry.suspicion) > SUSPICION_PROVENANCE_ATOL
    )


def _row_is_j1_clamp_exempt(entry: SuspicionEntry) -> bool:
    """A row the RAW 16.3 invariant would flag but the J1 clamp legitimately exempts.

    True iff the rendered ``suspicion`` breaks ``0.5 + Σ == suspicion`` yet equals
    the J1-clamped value -- the "phantom breach" class the Phase-16 close routed
    here (audits/audit-phase-16-close.md §2, §8 routed contract (a)): an
    entirely-soft conviction-grade row whose scalar the gate clamped to
    :data:`~agents.memory.beliefs.HARD_EVIDENCE_GATE_RENDER_CEIL` while keeping the
    raw typed provenance. A diagnostic predicate (not aggregated into the report);
    every such row is, by construction, NOT a breach under :func:`_row_sum_breaches`.
    The per-row pins assert it on the five committed seed-12 rows.
    """

    raw, clamped = _row_expected_scalars(entry)
    return (
        abs(raw - entry.suspicion) > SUSPICION_PROVENANCE_ATOL
        and abs(clamped - entry.suspicion) <= SUSPICION_PROVENANCE_ATOL
    )


def _cross_check_graphs(
    meeting: _VJMeeting,
    graphs: Mapping[PlayerId, tuple[SuspicionEntry, ...]],
    vote_prompts: Mapping[PlayerId, str],
) -> tuple[int, int, int, int]:
    """(rows_checked, sum_breaches, rendered_compared, rendered_mismatches).

    Two instrument-integrity gauges over EVERY living voter's pre-vote graph:
    the 16.3 provenance-sum invariant on each reconstructed row (J1-clamp-aware,
    :func:`_row_sum_breaches`), and the reconstructed scalar vs the per-player
    value the recorded vote prompt actually rendered (2-decimal tolerance). Both
    read 0 breaches/mismatches on every committed set -- the five by-design
    J1-clamped seed-12 rows are exempt (:func:`_row_is_j1_clamp_exempt`), not
    breaches.
    """

    rows_checked = 0
    sum_breaches = 0
    compared = 0
    mismatches = 0
    for voter in sorted(meeting.living):
        graph = graphs[voter]
        for entry in graph:
            rows_checked += 1
            if _row_sum_breaches(entry):
                sum_breaches += 1
        prompt = vote_prompts.get(voter)
        if prompt is None:
            continue
        reconstructed = {entry.player_id: entry.suspicion for entry in graph}
        for target, rendered in _parse_suspicion_graph(prompt).items():
            compared += 1
            value = reconstructed.get(target)
            if value is None or abs(round(value, 2) - rendered) > _RENDERED_MATCH_ATOL:
                mismatches += 1
    return rows_checked, sum_breaches, compared, mismatches


def _flagged_subjects(meeting: _VJMeeting) -> frozenset[PlayerId]:
    """The union of recorded contradiction subjects — the zero-flag predicate's
    complement (the same set ``guard_ballot_citation`` reads)."""

    return frozenset(
        subject for ref in meeting.contradictions for subject in ref.subjects
    )


def _citation_counts(
    meeting: _VJMeeting,
) -> tuple[int, int, int, int, int, int, int]:
    """Citation-compliance counts over one meeting's ballots.

    Returns ``(skip_ballots, turn_valid, turn_dangling, obs_valid,
    obs_dangling, cited_eject_ballots, eject_ballots)``. A turn citation is
    VALID iff it names one of THIS meeting's transcript turn ids; an
    observation citation is VALID iff it names an id in the voter's
    reconstructed episodic observation-id set (the same valid-id universe
    ``meetings.manager._normalize_ballot_observation_id`` validates against
    at record time). A non-SKIP ballot is CITED when it carries at least one
    valid citation of either kind.
    """

    valid_turn_ids = frozenset(turn.turn_id for turn in meeting.transcript.turns)
    skip = 0
    turn_valid = 0
    turn_dangling = 0
    obs_valid = 0
    obs_dangling = 0
    cited_ejects = 0
    ejects = 0
    for ballot in meeting.ballots:
        cited = False
        if ballot.primary_reason_id is not None:
            if ballot.primary_reason_id in valid_turn_ids:
                turn_valid += 1
                cited = True
            else:
                turn_dangling += 1
        if ballot.primary_reason_observation_id is not None:
            voter_ids = meeting.observation_ids_by_voter.get(ballot.voter, frozenset())
            if ballot.primary_reason_observation_id in voter_ids:
                obs_valid += 1
                cited = True
            else:
                obs_dangling += 1
        if ballot.target == "SKIP":
            skip += 1
        else:
            ejects += 1
            if cited:
                cited_ejects += 1
    return (
        skip,
        turn_valid,
        turn_dangling,
        obs_valid,
        obs_dangling,
        cited_ejects,
        ejects,
    )


# --------------------------------------------------------------------------- #
# The deterministic voice tier                                                #
# --------------------------------------------------------------------------- #


def _strip_leading_markers(text: str) -> str:
    """Drop leading ``[...] `` audit markers — system text, not model voice."""

    while True:
        stripped = _LEADING_MARKER_RE.sub("", text, count=1)
        if stripped == text:
            return text
        text = stripped


def _normalize_voice(text: str, room_re: re.Pattern[str]) -> str:
    """The §2.5 skeleton normalization: ids -> ``player``, rooms -> ``room``,
    digit runs -> ``n``, lowercased, whitespace collapsed."""

    text = _strip_leading_markers(text)
    text = _PLAYER_ID_RE.sub("player", text)
    text = room_re.sub("room", text)
    text = _DIGIT_RUN_RE.sub("n", text)
    return " ".join(text.lower().split())


def _room_pattern(room_ids: Sequence[str]) -> re.Pattern[str]:
    """Word-boundary alternation over the canonical room ids (longest first,
    case-insensitive — rooms render uppercase in prompts and prose)."""

    ordered = sorted(room_ids, key=lambda room: (-len(room), room))
    return re.compile(
        r"\b(?:" + "|".join(re.escape(room) for room in ordered) + r")\b",
        re.IGNORECASE,
    )


def _trigrams(tokens: Sequence[str]) -> frozenset[tuple[str, str, str]]:
    return frozenset(
        (tokens[i], tokens[i + 1], tokens[i + 2]) for i in range(len(tokens) - 2)
    )


def _is_near_dup(a: Sequence[str], b: Sequence[str]) -> bool:
    """``>= 0.5`` trigram-Jaccard near-duplicate; sub-trigram texts compare by
    exact token equality (an empty-vs-empty pair is a duplicate)."""

    ta = _trigrams(a)
    tb = _trigrams(b)
    if not ta and not tb:
        return tuple(a) == tuple(b)
    if not ta or not tb:
        return False
    return len(ta & tb) / len(ta | tb) >= _ECHO_JACCARD_BAR


def _meeting_echo(
    skeletons: Sequence[str],
) -> tuple[int, int]:
    """(echo_ballots, distinct_skeletons) for one meeting's ballot skeletons."""

    token_lists = [tuple(skeleton.split()) for skeleton in skeletons]
    echo = 0
    for i, tokens in enumerate(token_lists):
        if any(
            _is_near_dup(tokens, other) for j, other in enumerate(token_lists) if j != i
        ):
            echo += 1
    return echo, len(set(skeletons))


def _distinct_n(token_lists: Sequence[tuple[str, ...]], n: int) -> float | None:
    """distinct-n: distinct n-grams / total n-grams across all texts (Li et
    al. 1510.03055); ``None`` when no n-grams exist."""

    total = 0
    distinct: set[tuple[str, ...]] = set()
    for tokens in token_lists:
        for i in range(len(tokens) - n + 1):
            total += 1
            distinct.add(tokens[i : i + n])
    return len(distinct) / total if total else None


# --------------------------------------------------------------------------- #
# The set-level fold                                                          #
# --------------------------------------------------------------------------- #


def compute_vj_instruments(sample_dir: Path) -> VJInstrumentReport:
    """Fold a replay set's committed bytes into the V&J instrument report.

    One memory-augmented walk of the set (``eval.funnel._walk_game_vj`` —
    every recorded state hash verified, per-agent memory fed exactly as the
    live game fed it), then the judgment, voice, and pooling folds over every
    resolved meeting. Runs on any replay-set directory and both roster
    presets. Pure, offline, deterministic — two runs return identical
    reports.
    """

    walks, num_players, num_impostors, tasks_per_crewmate = _walk_set_vj(sample_dir)
    pooling = _pooling_report_from_walks(
        walks,
        sample_dir=sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    room_re = _room_pattern(sorted(load_canonical_map().rooms))

    rows: list[VJMeetingRow] = []
    calibration_samples: list[tuple[float, bool]] = []
    zero_flag_typed: Counter[str] = Counter()
    zero_flag_proxy: Counter[str] = Counter()
    convictions_total = 0
    zero_flag_convictions = 0
    zero_flag_crew = 0
    zero_flag_impostor = 0
    split_agreements = 0
    split_disagreements = 0
    provenance_rows = 0
    provenance_breaches = 0
    rendered_compared = 0
    rendered_mismatches = 0
    nulled_reason = 0
    nulled_observation = 0
    coerced_zero_flag = 0
    all_token_lists: list[tuple[str, ...]] = []
    all_skeletons: list[str] = []

    for walk in walks:
        game_id = f"headless-seed-{walk.seed}"
        for meeting in walk.meetings:
            graphs = _pre_vote_graphs(meeting)
            vote_prompts = _vote_prompts(meeting)
            checked, breaches, compared, mismatched = _cross_check_graphs(
                meeting, graphs, vote_prompts
            )
            provenance_rows += checked
            provenance_breaches += breaches
            rendered_compared += compared
            rendered_mismatches += mismatched

            ejected = meeting.ejected
            ejected_is_impostor: bool | None = None
            zero_flag: bool | None = None
            typed: TypedSplit | None = None
            proxy: ProxySplit | None = None
            agree: bool | None = None
            if meeting.outcome == "EJECTED" and ejected is not None:
                convictions_total += 1
                ejected_is_impostor = walk.roles[ejected] == "IMPOSTOR"
                zero_flag = ejected not in _flagged_subjects(meeting)
                convicting = sorted(
                    ballot.voter
                    for ballot in meeting.ballots
                    if ballot.target == ejected
                )
                typed = _typed_split(ejected, convicting, graphs)
                proxy = _proxy_split(ejected, convicting, vote_prompts)
                agree = (typed == "hard_backed") == (proxy == "hard_backed")
                if zero_flag:
                    zero_flag_convictions += 1
                    if ejected_is_impostor:
                        zero_flag_impostor += 1
                    else:
                        zero_flag_crew += 1
                    zero_flag_typed[typed] += 1
                    zero_flag_proxy[proxy] += 1
                    if agree:
                        split_agreements += 1
                    else:
                        split_disagreements += 1

            for ballot in meeting.ballots:
                if ballot.target != "SKIP":
                    calibration_samples.append(
                        (
                            ballot.confidence,
                            _is_impostor(
                                walk.roles,
                                ballot.target,
                                game_id=game_id,
                                source="vote ballot",
                            ),
                        )
                    )
                if _NULLED_REASON_PREFIX in ballot.rationale_text:
                    nulled_reason += 1
                if _NULLED_OBSERVATION_PREFIX in ballot.rationale_text:
                    nulled_observation += 1
                if _COERCED_ZERO_FLAG_PREFIX in ballot.rationale_text:
                    coerced_zero_flag += 1

            (
                skip,
                turn_valid,
                turn_dangling,
                obs_valid,
                obs_dangling,
                cited_ejects,
                ejects,
            ) = _citation_counts(meeting)

            skeletons = [
                _normalize_voice(ballot.rationale_text, room_re)
                for ballot in meeting.ballots
            ]
            echo, distinct_in_meeting = _meeting_echo(skeletons)
            all_skeletons.extend(skeletons)
            all_token_lists.extend(tuple(s.split()) for s in skeletons)

            rows.append(
                VJMeetingRow(
                    seed=meeting.seed,
                    meeting_id=meeting.meeting_id,
                    tick=meeting.tick,
                    trigger_kind=meeting.trigger_kind,
                    outcome=meeting.outcome,
                    ejected=ejected,
                    ejected_is_impostor=ejected_is_impostor,
                    zero_flag_conviction=zero_flag,
                    typed_split=typed,
                    proxy_split=proxy,
                    splits_agree_on_hard=agree,
                    ballots=len(meeting.ballots),
                    skip_ballots=skip,
                    turn_citations_valid=turn_valid,
                    turn_citations_dangling=turn_dangling,
                    observation_citations_valid=obs_valid,
                    observation_citations_dangling=obs_dangling,
                    cited_eject_ballots=cited_ejects,
                    echo_ballots=echo,
                    echo_rate=echo / len(meeting.ballots) if meeting.ballots else None,
                    distinct_skeletons=distinct_in_meeting,
                )
            )

    _bins, calibration_total, ece = _bin_samples(calibration_samples, DEFAULT_N_BINS)
    populated = sum(1 for bin_ in _bins if bin_.count)
    brier = (
        statistics.fmean(
            (confidence - (1.0 if impostor else 0.0)) ** 2
            for confidence, impostor in calibration_samples
        )
        if calibration_samples
        else None
    )

    ballots_total = sum(row.ballots for row in rows)
    skip_ballots = sum(row.skip_ballots for row in rows)
    eject_ballots = ballots_total - skip_ballots
    turn_valid_total = sum(row.turn_citations_valid for row in rows)
    turn_dangling_total = sum(row.turn_citations_dangling for row in rows)
    obs_valid_total = sum(row.observation_citations_valid for row in rows)
    obs_dangling_total = sum(row.observation_citations_dangling for row in rows)
    cited_eject_total = sum(row.cited_eject_ballots for row in rows)
    echo_total = sum(row.echo_ballots for row in rows)

    skeleton_counts = Counter(all_skeletons)
    top_cluster_ballots = sum(
        count for _, count in skeleton_counts.most_common(_SKELETON_TOP_K) if count >= 2
    )

    return VJInstrumentReport(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(walks),
        meetings_total=len(rows),
        convictions_total=convictions_total,
        zero_flag_convictions=zero_flag_convictions,
        zero_flag_conviction_rate=(
            zero_flag_convictions / convictions_total if convictions_total else None
        ),
        zero_flag_crew_convictions=zero_flag_crew,
        zero_flag_impostor_convictions=zero_flag_impostor,
        zero_flag_hard_backed=zero_flag_typed["hard_backed"],
        zero_flag_soft_only=zero_flag_typed["soft_only"],
        zero_flag_unattributed_only=zero_flag_typed["unattributed_only"],
        zero_flag_no_row=zero_flag_typed["no_row"],
        zero_flag_proxy_hard_backed=zero_flag_proxy["hard_backed"],
        zero_flag_proxy_soft_only=zero_flag_proxy["soft_only"],
        zero_flag_proxy_sub_gate=zero_flag_proxy["sub_gate"],
        zero_flag_proxy_no_render=zero_flag_proxy["no_render"],
        zero_flag_split_agreements=split_agreements,
        zero_flag_split_disagreements=split_disagreements,
        provenance_rows_checked=provenance_rows,
        provenance_sum_breaches=provenance_breaches,
        rendered_rows_compared=rendered_compared,
        rendered_row_mismatches=rendered_mismatches,
        ballots_total=ballots_total,
        skip_ballots=skip_ballots,
        eject_ballots=eject_ballots,
        turn_citations=turn_valid_total + turn_dangling_total,
        turn_citations_valid=turn_valid_total,
        turn_citations_dangling=turn_dangling_total,
        observation_citations=obs_valid_total + obs_dangling_total,
        observation_citations_valid=obs_valid_total,
        observation_citations_dangling=obs_dangling_total,
        cited_eject_ballots=cited_eject_total,
        citation_compliance_rate=(
            cited_eject_total / eject_ballots if eject_ballots else None
        ),
        nulled_reason_id_markers=nulled_reason,
        nulled_observation_id_markers=nulled_observation,
        coerced_zero_flag_markers=coerced_zero_flag,
        ballot_confidence_brier=brier,
        ballot_confidence_ece=ece,
        ballot_calibration_total=calibration_total,
        ballot_calibration_low_power=populated < MIN_POPULATED_BINS_FOR_POWER,
        voice_ballots_total=ballots_total,
        echo_ballots=echo_total,
        within_meeting_echo_rate=(
            echo_total / ballots_total if ballots_total else None
        ),
        response_skeleton_share=(
            top_cluster_ballots / ballots_total if ballots_total else None
        ),
        distinct_skeletons=len(skeleton_counts),
        distinct_skeleton_ratio=(
            len(skeleton_counts) / ballots_total if ballots_total else None
        ),
        distinct_1=_distinct_n(all_token_lists, 1),
        distinct_2=_distinct_n(all_token_lists, 2),
        pooling=pooling,
        per_meeting=tuple(rows),
    )


__all__ = [
    "ProxySplit",
    "TypedSplit",
    "VJInstrumentReport",
    "VJMeetingRow",
    "compute_vj_instruments",
]
