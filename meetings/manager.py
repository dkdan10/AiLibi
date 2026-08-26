"""Meeting state machine (DESIGN.md §5.1, §5.2).

:class:`MeetingManager` runs one meeting end-to-end as the reactive
accusation chain (DESIGN.md §5.2). It is constructed with the LLM
client, the prompt callables (Task 8.8 jinja templates wrapped as Python
callables), and a deadline configuration. :meth:`MeetingManager.run` is a
no-op until the orchestrator invokes it with a :class:`MeetingTrigger`;
from there the manager sequences a single ordered list of **turns** ->
voting -> resolution and returns a :class:`MeetingResult`.

The manager NEVER mutates engine state. It only reads agent-side inputs
(rendered memory, role, suspicion graph) supplied by the orchestrator
and emits a :class:`MeetingResult` DTO. The orchestrator applies the
outcome to engine-owned state per DESIGN.md §5.1.

Reactive accusation chain (DESIGN.md §5.2)
==========================================

A meeting is one ordered ``transcript.turns`` list followed by a vote:

1. **Opening** (turn 0) -- the body-reporter / emergency caller states
   findings and accuses one player or declares "unsure".
2. **Reactive chain** -- the accused responds; the next speaker is
   deterministically the player just accused. The chain terminates when
   the current turn names no new accusation, re-accuses someone who has
   already spoken (cycle), or the turn count reaches the living-player
   count (hard cap). The chain's next speaker and its termination are
   pure functions of the recorded turns (:mod:`meetings.transcript`), so
   a replay reconstructs the chain from ``transcript.turns`` without
   re-calling the model.
3. **Opt-in info-share** -- living non-speakers with a relevant
   observation (a deterministic co-presence gate with the body / the
   accused) each take one terminal turn; an opt-in turn may accuse but
   never extends the chain.
4. **Voting** -- contradictions (§5.4) recompute once over the full
   transcript; the PRE-VOTE half of the meeting fold (Task 10.7) is
   derived from the same final transcript (two-witness testimony bumps
   + this meeting's relevance-gated corroborations, §6.3) and applied
   to every voter's suspicion graph BEFORE the ballot prompt renders,
   so the in-prompt §4.6 verdict reads post-fold values; then every
   living agent submits a :class:`VoteBallot`.
5. **Resolution** -- plurality tally with the confidence threshold.
   The POST-VOTE half of the fold (single-voice accused-bumps + Rule-5
   decay) stays the orchestrator-owned post-meeting absorb, exactly as
   the 9.8 design wired it.

Roll-call round
===============

A roll-call round sits between the opt-in phase (PHASE 3) and voting. Every
living player who has not yet spoken takes one terminal ``opt_in``-surface turn
in ascending player-id order, executing the turn-taking routing of
``audits/audit-phase-17-absence-gate.md`` Ruling 3(a). The measured cost is
honest and large (``audits/audit-phase-18-planning.md`` §3.4): +3.13 turn
calls/meeting at today's economy (496 -> 1057 turn calls over the 179-meeting
canonical samples denominator, 2.13x), ~+36% meeting LLM calls -- the number
the 18.11 gate and the 18.13 duration plan both quote.

Single per-turn chokepoint
===========================

Every turn -- opening, reply, or opt-in -- is collected through
:meth:`MeetingManager._collect_turn`, so every turn-kind inherits the
same guards: self-alibi subject normalization, the Task 7.12 teammate
firewall (an impostor never accuses / incriminates a fellow impostor),
the strict :class:`~meetings.schemas.AlibiClaim` chronology, and the
Task 7.10 fail-soft (a malformed turn degrades to a default turn rather
than aborting the meeting). The vote inherits the third 7.12 guard,
:func:`coerce_teammate_ballot_to_skip`, and -- since Task 10.9.1 (PR
#147 F1) -- its own fail-soft: a ballot completion that still fails
schema validation after the provider-level retry degrades to the
default SKIP stamped with :data:`VOTE_PARSE_DEFAULT_MARKER` instead of
aborting the game. Caps and retry counts are frozen; the net catches,
it never re-asks. Last in the ballot chain -- after roster
normalization and the teammate coercion -- the Task 10.9.2 ballot-target
graph guard (:func:`guard_ballot_target_graph`, PR #147 F2) binds an
eject ballot under a MUST-vote verdict to a target whose rendered
suspicion meets the §4.6 threshold, redirecting an under-gate target to
the argmax-rendered eligible candidate with
:data:`BALLOT_TARGET_REDIRECT_MARKER`.

The opening additionally content-validates (Task 10.3, audit gp-9): its
recorded claims must carry an accusation OR its free_text an explicit
"unsure" declaration (DESIGN.md §5.2 PHASE 1), enforced through the same
single-retry-then-default machinery the audit-gp-2 opening retry built --
a narration-only opening consumes an attempt exactly like a
schema-validation failure.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable, Coroutine, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Any, Final, Literal, TypeVar

from pydantic import ValidationError

from agents.memory.beliefs import (
    MEETING_CONTRADICTION_LIFT_CAP,
    TESTIMONY_INDEPENDENCE_BAR,
    BeliefState,
    SuspicionProvenance,
    apply_contradiction_rule,
    apply_meeting_evidence_rules,
)
from llm.client import LLMClient, LLMResponse
from llm.provider import LLMCallFailure, extract_parse_failure
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.render_contract import (
    PromptRenderInputs,
    ReportPromptRenderer,
    StatementPromptRenderer,
    SuspicionEntry,
    VotePromptRenderer,
)
from meetings.schemas import (
    MARKER_QUOTED_ORIGINAL_MAX_CHARS,
    MARKER_TRUNCATION_SUFFIX,
    AccusationClaim,
    AlibiClaim,
    Claim,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingOutcome,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    MoveWitnessRecord,
    ObservationClaim,
    ObservationId,
    PlayerId,
    ReportedStatement,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    TurnAnnotation,
    TurnId,
    TurnKind,
    VentWitnessRecord,
    VoteBallot,
)
from meetings.transcript import (
    MeetingTriggerKind,
    absent_players,
    accusation_target,
    canonical_rooms,
    detect_contradictions,
    detect_corroborations,
    grounded_vent_subjects_from_flags,
    grounded_vouch_subjects,
    independent_voices,
    is_relevant_sighting,
    next_chain_step,
    triggering_body_rooms,
)
from meetings.voting import tally_ballots

Role = Literal["CREWMATE", "IMPOSTOR"]

# Protocol-default deadline values (DESIGN.md §5.2: T_turn = 30 s per turn,
# T2 = 30 s for the vote). The reactive chain replaces the old fixed
# ``round_count`` loop: the meeting's *total* turn cap is the living-player
# count (DESIGN.md §5.2 PHASE 2 condition (c), enforced by
# :func:`meetings.transcript.next_chain_step`), so the deterministic
# "total meeting cap" is structural -- the per-turn deadline below bounds
# each turn's wall-clock, the chain bounds their number.
DEFAULT_TURN_DEADLINE_SECONDS: Final[float] = 30.0
DEFAULT_VOTE_DEADLINE_SECONDS: Final[float] = 30.0
# The §4.6 skip-confidence gate now lives in :mod:`meetings.constants` (Task
# 15.6, its single definition home); imported above and re-exported below so
# existing ``from meetings.manager import DEFAULT_SKIP_CONFIDENCE_THRESHOLD``
# callers are unchanged.

# LLM-call settings. A :class:`MeetingTurn` (observations + claims +
# free-text prose in one object) is the most verbose meeting artifact, so
# the per-turn budget is the largest; too tight a cap truncates the model
# mid-JSON into an unterminated string that fails to parse. Vote ballots
# are smaller but get the same defense-in-depth headroom. Public defaults
# so the orchestrator can override per call without monkey-patching.
DEFAULT_TURN_MAX_TOKENS: Final[int] = 2048
DEFAULT_TURN_TEMPERATURE: Final[float] = 0.4
DEFAULT_VOTE_MAX_TOKENS: Final[int] = 1024
DEFAULT_VOTE_TEMPERATURE: Final[float] = 0.2

# Free-text recorded on a turn / ballot when a participant misses a
# deadline or emits an unparseable payload. The audit-trail requirement in
# DESIGN.md §5.2 means we always record *something*; these strings are the
# canonical audit markers downstream code (replay, eval) can match on.
DEFAULT_TURN_FREE_TEXT: Final[str] = "(missed deadline; no turn submitted)"
DEFAULT_VOTE_RATIONALE: Final[str] = "(missed deadline; default skip)"

# Audit-trail marker prefix prepended to ``rationale_text`` when the LLM
# returns a ``target`` that is neither ``"SKIP"`` nor a valid candidate.
# Such a ballot is defensively normalized to ``SKIP`` so the tally cannot
# be corrupted by a hallucinated player id; the marker preserves the
# original (invalid) target for replay analysis.
INVALID_VOTE_TARGET_MARKER: Final[str] = (
    "[invalid target {target!r} normalized to SKIP] "
)

# Audit-trail marker prepended to ``rationale_text`` when the teammate
# firewall guard (Task 7.12) coerces a ballot that targets a fellow
# impostor into ``SKIP``. A teammate is a *valid* living candidate, so the
# invalid-target normalization above never catches it; this is the
# belt-and-suspenders deterministic guard that backstops the prompt
# instruction (the 7B model may still emit a teammate target). The marker
# preserves the original (teammate) target for replay / audit analysis.
TEAMMATE_VOTE_TARGET_MARKER: Final[str] = (
    "[teammate target {target!r} coerced to SKIP] "
)

# Replacement ``rationale_text`` body recorded BEHIND
# ``TEAMMATE_VOTE_TARGET_MARKER`` when the teammate firewall guard coerces a
# ballot to SKIP (Task 19.15; audits/audit-phase-19-triage.md §7 item 16).
# The model authored that rationale to justify the betrayal target, so it can
# state the impostor's private knowledge outright ("p-3 is my partner", "I did
# the kill") -- and the coerced ballot rides ``rationale_text`` straight onto
# the spectator surface, where the marker is stripped to a chip and the
# remainder renders as the voter's stated reason. Keeping that text is
# omniscience leaking through the guard's own output, so the guard REPLACES it
# rather than preserving it. Two properties are load-bearing:
#
# * the substitution is SELF-DECLARING -- a silent swap to plausible in-world
#   prose would attribute a fabricated sentence to the model, which is the
#   laundering this task exists to avoid;
# * it names no role, no teammate, and no kill. The marker carries the
#   auditable fact that the guard rewrote the target, and gating that
#   marker's DISPLAY is a separate task (19.11, the display-side twin), so
#   the note itself says only "the vote guard", never WHICH guard.
#
# BRACKETED, not parenthesized like ``DEFAULT_VOTE_RATIONALE``: the leading
# ``[...]`` form is the repo's established "system text, not model voice"
# shape, and ``eval.vj_instruments._strip_leading_markers`` drops exactly that
# form before a ballot body enters the §2.5 echo / skeleton / distinct-n voice
# fold. A parenthesized note would survive that strip and feed the SAME
# guard-authored sentence into the model-voice diversity metrics on every
# coerced ballot -- measuring the guard's prose as the model's. The bracket is
# what keeps this synthetic body out of an instrument it was never model
# output for. It carries no ``{...!r}`` payload, so it is not a marker: the
# display-side parse (``api.replay_loader._parse_rewrite_reasons``) registers
# no chip for it and leaves it as the ballot's clean body.
#
# Forward-looking only: committed replay bytes are frozen and unaffected (no
# recorded ballot is rewritten), so this changes what a FUTURE recording
# carries and nothing that already exists on disk.
TEAMMATE_COERCED_VOTE_RATIONALE: Final[str] = (
    "[rationale redacted by the vote guard; recorded reason: "
    "no confident read this round]"
)

# Audit-trail marker prepended to ``rationale_text`` when the ballot-target
# graph guard (Task 10.9.2; PR #147 finding F2) rewrites an eject ballot
# whose target carries no over-gate rendered row. The seed-12 m0 shape:
# three voters whose rendered §4.6 verdict read MUST-vote off an over-gate
# row adopted the opening's bare verbal accusation of p-1 -- a candidate
# their own rendered graph carried NO row for -- and p-1 was ejected 3-2-2
# with zero design-channel attribution. Every other layered guard held;
# the leak was that ballot TARGET is unconstrained by the graph the
# verdict was computed from. The guard (:func:`guard_ballot_target_graph`)
# redirects such a target to the argmax-rendered eligible candidate (ties
# to the lowest player id), or coerces to SKIP when no eligible candidate
# meets the gate (an impostor voter whose only over-gate row is a
# teammate); either way this marker preserves the original target,
# bounded per the Task 10.6 rule (:func:`_bounded_original`). The guard
# NEVER fires on a SKIP ballot or under a MUST-skip verdict -- a vote
# against a MUST-skip verdict stays a recorded inversion (frozen
# measurement semantics). Downstream eval counts redirects on this
# literal beside the invalid-target and teammate-coercion counts. Pin the
# literal exactly. The owner principle this enforces is the phase's
# oldest line: innocents are ejectable, never at RANDOM.
BALLOT_TARGET_REDIRECT_MARKER: Final[str] = (
    "[under-gate eject target {target!r} redirected] "
)

# Audit-trail marker recorded AS ``rationale_text`` when a vote-ballot
# completion fails schema validation and the ballot degrades to the
# default SKIP (Task 10.9.1; PR #147 finding F1). The seed-8 abort shape:
# a rationale rambled past the frozen 1024-token vote cap, the JSON was
# left unterminated mid-string, the provider-level single retry failed the
# same way, and the propagating ``ValidationError`` killed the game
# (game_over 49/50) -- because turns have had a fail-soft since Task 7.10
# while the vote path caught only the deadline. A twice-failed ballot now
# degrades to the existing default SKIP with this marker carrying a
# BOUNDED head of the unparseable response (the Task 10.6 60-char rule,
# :func:`_bounded_original`) so the runaway stays auditable in the replay
# without splicing kilobytes into the ballot record. Unlike the sibling
# markers above this is the WHOLE ``rationale_text``, not a prefix to
# model-authored text -- nothing parsed, so there is no rationale to
# preserve. Caps and retry counts stay frozen: this is a net, never a
# retry. Downstream eval partitions the degraded SKIP on this literal
# (a DEFAULTED class beside coerced/missed -- never a threshold
# inversion, never a silent missed skip). Pin the literal exactly.
VOTE_PARSE_DEFAULT_MARKER: Final[str] = (
    "[unparseable ballot defaulted to SKIP; response head: {head!r}] "
)

# Audit-trail marker prepended to ``rationale_text`` when a ballot's
# ``primary_reason_id`` references a turn that does not exist in THIS
# meeting's transcript and cannot be recovered as a suffix form. The id is
# nulled (DESIGN.md §5.5) so the ballot-follows-chain instrument is not
# corrupted by a hallucinated id or the vote prompt's old hardcoded example
# (audit gp-3: 24/78 non-null reason ids dangled). The marker preserves the
# original (invalid) id for replay analysis and lets downstream eval count
# normalizations per game by grepping one string (mirrors the
# ``INVALID_VOTE_TARGET_MARKER`` prefix shape). Pin the literal exactly.
INVALID_REASON_ID_MARKER: Final[str] = (
    "[invalid primary_reason_id {reason_id!r} nulled] "
)

# Audit-trail marker prepended to ``rationale_text`` when a ballot's
# ``primary_reason_observation_id`` (Task 16.5, C8) cites a stable episodic
# id that is NOT in the voter's own typed valid-id set. The id is nulled
# (AGENTS.md "no silent fallbacks") so the private-hard-evidence citation
# instrument is never corrupted by a hallucinated id -- an id the voter
# never actually observed. Unlike ``INVALID_REASON_ID_MARKER`` there is no
# suffix-recovery branch: an observation id has no in-meeting ordinal table
# (the ``:turn-{k}`` echo shape is turn-id-specific), so an unknown id is
# nulled, never guessed. Preserves the original (invalid) id for replay
# analysis and lets eval count normalizations per game by grepping one
# string (mirrors the ``INVALID_REASON_ID_MARKER`` prefix shape;
# ``api.replay_loader``'s ``_marker_pattern`` relies on the ``{x!r}`` repr
# interpolation when a later task registers the chip). Pin the literal exactly.
INVALID_OBSERVATION_ID_MARKER: Final[str] = (
    "[invalid primary_reason_observation_id {observation_id!r} nulled] "
)

# Audit-trail marker prepended to ``rationale_text`` when the citation gate
# (Task 16.6, J2; audits/post-phase-14-Voice-and-Judgment-planning.md §3.4)
# coerces an EJECT ballot to ``SKIP``: the target carries NO contradiction
# flag this meeting (zero-flag) and the ballot cites NOTHING -- both
# ``primary_reason_id`` and ``primary_reason_observation_id`` are null after
# validation (a fabricated citation has already been nulled by the
# ``INVALID_REASON_ID_MARKER`` / ``INVALID_OBSERVATION_ID_MARKER`` passes
# above, so it gates exactly like a bare null). The gate -- and this marker --
# is armed on every production ballot, and it coerces, never rejects (never a crash,
# never a re-prompt), so the marker preserves the original target for replay
# / audit analysis and rides ``rationale_text`` into the recorded ballot the
# spectator surface already reads (mirrors the ``INVALID_REASON_ID_MARKER``
# prefix shape; ``api.replay_loader``'s ``_marker_pattern`` relies on the
# ``{x!r}`` repr interpolation). Both downstream consumers are WIRED: the
# spectator chip registration (``api.replay_loader._BALLOT_PREFIX_MARKERS``
# registers this literal as ``"uncited_coerced"`` -- the api-region task,
# beside 16.5's observation marker) and the eval SKIP partition
# (``eval.meeting_quality.compute_conversion_report`` learned the literal at
# Task 17.2 and diverts a citation-coerced SKIP into
# ``citation_coerced_skip_ballots`` BEFORE the tri-split, so a gated SKIP
# from a MUST-vote voter never lands in the ``threshold_inversions``
# sentinel and the §4.6 gate-obedience read cannot over-count). Eval also
# counts coercions per game by grepping this one string. Pin the literal
# exactly.
UNCITED_ZERO_FLAG_EJECT_MARKER: Final[str] = (
    "[uncited zero-flag eject target {target!r} coerced to SKIP] "
)

# The recorded-bytes shape of the ``invalid_accusation_target`` annotation:
# a marker earlier builds prepended to a turn's ``free_text`` when an
# ``AccusationClaim`` named a ``target`` (``against``) that was not a living
# meeting participant. A turn now carries the fact as a typed
# :class:`~meetings.schemas.TurnAnnotation`; the literal survives so
# ``api.replay_loader`` can project a committed transcript onto the same chips. qwen3.5:9b occasionally hallucinates an accusation
# target id (e.g. ``"imp-2"``) that names no player. The reactive chain
# already terminates on such a target (``next_chain_step`` ->
# ``TERMINATION_TARGET_NOT_LIVING``), but the claim was still recorded into
# the transcript, where the §11.3 accusation-calibration metric -- which
# resolves every accusation target's role -- failed loud on the unknown id
# (``roles[target]`` ``KeyError``). The claim is dropped before it is
# recorded, mirroring the ballot-target normalization above
# (``INVALID_VOTE_TARGET_MARKER`` -> ``SKIP``): a valid accusation target is
# a living participant, the same notion of "valid target" the vote path
# enforces via ``candidate_targets``. The marker preserves the original
# (invalid) target for replay / audit analysis and lets downstream eval count
# drops by grepping one string. Pin the literal exactly.
INVALID_ACCUSATION_TARGET_MARKER: Final[str] = (
    "[invalid accusation target {target!r} dropped] "
)

# The recorded-bytes shape of the ``invalid_alibi_subject`` /
# ``invalid_corroboration_supports`` annotations: markers earlier builds
# prepended to a turn's ``free_text`` when an
# ``AlibiClaim`` / ``CorroborationClaim`` carried a subject-bearing field
# (``subject`` / ``supports``) that was not a living meeting participant
# (Task 10.2; audit gp-6 C-C-8, H-H-6). The fb3cfa5 guard above covered
# accusation targets only, so the 9B's hallucinated structural ids -- a
# game id (``"headless-seed-9"``) as an alibi subject / corroboration
# target, a turn id or a free-text phrase (``"p-2 dead"``) in
# ``supports`` -- were still recorded: they flowed through the
# post-meeting fold into persistent belief rows and rendered as §6.6
# suspicion-graph rows inside vote prompts, and 15 corroborations
# silently no-op'd on phantom subjects (the reason belief Rule 3 never
# fired in any recorded set). The claims are dropped at the same
# per-turn chokepoint, BEFORE the turn is recorded -- a garbage subject
# never reaches contradiction detection, the belief fold, or any prompt
# surface -- with the original preserved on ``free_text``. A valid
# subject is a living meeting participant (a DEAD roster player drops
# too, the same rule as accusations). Pin the literals exactly.
INVALID_ALIBI_SUBJECT_MARKER: Final[str] = (
    "[invalid alibi subject {subject!r} dropped] "
)
INVALID_CORROBORATION_SUPPORTS_MARKER: Final[str] = (
    "[invalid corroboration supports {supports!r} dropped] "
)

# The explicit "unsure" declaration an opening turn may carry INSTEAD of an
# accusation claim (DESIGN.md §5.2 PHASE 1: the opener "EITHER accuses one
# player OR declares 'unsure'"; Task 10.3, audit gp-9 H-H-1). Matched
# case-insensitively as a substring of the model-authored ``free_text``
# (the schema is unchanged -- the marker is free_text-level, validated
# manager-side). An opening whose recorded claims carry no accusation and
# whose free_text carries no such declaration is narration-only: it kills
# the reactive chain on turn 0 (5 of 76 audited meetings), so
# :meth:`MeetingManager._collect_turn` treats it as a validation failure
# and routes it through the existing single-retry path before the standing
# fail-soft. The opening templates instruct the model to write this exact
# word; pin the literal.
OPENING_UNSURE_MARKER: Final[str] = "unsure"

# Structural bound on a bare "unsure" declaration (Task 10.12; audit
# 2026-06-13-1816 H-H-1). The 10.3 guard accepted ANY opening whose free_text
# contained the marker substring, so a reasoning-relocation husk -- the whole
# chain-of-thought dumped into free_text, incidentally containing "unsure",
# with empty claims AND empty observations -- self-certified as a deliberate
# position and skipped the retry (seed-30 m1: free_text 5266 chars, claims=[]
# observations=[], all 7 ballots SKIP). A GENUINE unsure declaration is either
# SHORT or carries observations / surviving claims; only the hollow relocation
# shape -- free_text FAR above the ~225-char free-text p95 (the audited 9p2i
# medians: opening 235 / reply 227 / opt_in 196) AND no claims AND no
# observations -- is rejected back to the retry. The bound is ~4.4x the p95 and
# ~2x the 514-char longest GENUINE opening on the audited set, so it clears
# every real opening and trips only the 5266-char husk; it is NOT the frozen
# 2048/1024 token cap (this is a free_text CHARACTER count on an already-parsed
# turn, not a generation cap -- the cap stays frozen).
OPENING_UNSURE_MAX_FREE_TEXT_CHARS: Final[int] = 1000

# Opening retry feedback (Task 10.6; audit gp-5 H-H-1/H-H-2). The single
# opening retry previously re-sent the byte-identical prompt, and at
# temp 0.4 the model returned the byte-identical failure -- 0/3 recovered
# openings for ~14.5k burned tokens on the Wave-0 set. The retry prompt
# now appends a feedback block STATING the failure: the dead-target form
# names the dropped target(s) verbatim (bounded -- see
# ``MARKER_QUOTED_ORIGINAL_MAX_CHARS``), the no-position form covers the
# narration-only shape, and both demand a LIVING target or an explicit
# "unsure". Pinned literals so tests and downstream prompt audits can
# match them exactly; appended to the rendered base prompt, never spliced
# into it (the §4.6 render itself stays frozen).
OPENING_RETRY_FEEDBACK_HEADER: Final[str] = (
    "\n\n## Retry feedback\n\nYour previous opening was INVALID: "
)
OPENING_RETRY_FEEDBACK_DEAD_TARGET: Final[str] = (
    "your accusation named {targets}, who is DEAD or not at this table. "
)
OPENING_RETRY_FEEDBACK_NO_POSITION: Final[str] = (
    'it neither accused a living player nor declared "unsure". '
)
OPENING_RETRY_FEEDBACK_DEMAND: Final[str] = (
    "You MUST either accuse exactly ONE LIVING player from the living "
    'roster above or explicitly write "unsure".'
)

# The recorded-bytes shape of the ``opening_degraded_unsure`` annotation, kept
# so ``api.replay_loader`` can project a committed transcript onto the same
# chips: a marker earlier builds prefixed to a degraded opening's ``free_text``
# (Task 10.6; audit gp-5 H-H-2). A twice-failed opening whose failures were
# CONTENT-validation failures (the turn parsed but took no position --
# e.g. its only accusation named a dead player and was guard-dropped)
# degrades to an UNSURE opening built from the model's last parsed
# attempt instead of the full placeholder default: the observations (the
# body report itself!) and surviving claims are kept, only the position
# is recorded as unsure. The full default cost the whole meeting -- a
# guard-emptied opening reduced it to a 1-turn SKIP husk with no body
# room for the opt-in gate (seed 12 m0 opened an impostor-win game that
# way). The marker contains the word "unsure", so the recorded turn
# satisfies the §5.2 PHASE 1 opening contract on its face. Pin the
# literal exactly.
OPENING_UNSURE_DEGRADE_MARKER: Final[str] = (
    "[opening degraded to unsure after failed validation] "
)

# Emergency-opening no-body backstop (Task 10.11.1; audit-2026-06-13-1816
# B-B-1). The phrase that marks an EMERGENCY meeting's ``MeetingTrigger``
# description -- the ONE home shared with
# ``orchestrator.game._build_meeting_trigger`` (the producer) and, as a
# documented JINJA-literal lockstep (a template cannot import), the
# ``crewmate_report.j2`` emergency branch. DESIGN.md keeps no structured trigger
# kind on the meeting layer -- the description IS the trigger surface -- so the
# manager detects an emergency the same way the renderer does.
EMERGENCY_TRIGGER_PHRASE: Final[str] = "called an emergency meeting"

# Retry feedback appended to an EMERGENCY opening that fabricated a found_body
# (Task 10.11.1). The crewmate_report v7 emergency branch already asks for no
# body, but the 9B can ignore it (flat seed 11 m0 re-narrated a stale corpse as
# a fresh find); the single opening retry re-asks WITH this explicit no-body
# reason before the deterministic strip fires. Appended to the rendered base
# prompt, never spliced into it (the §4.6 render stays frozen); pinned literal so
# tests and prompt audits match it exactly.
EMERGENCY_NO_BODY_RETRY_FEEDBACK: Final[str] = (
    "\n\n## Retry feedback\n\nYour previous opening was INVALID: this is an "
    "EMERGENCY meeting -- you pressed the button on SUSPICION, so there is NO "
    "body to report (DESIGN.md §5.2 PHASE 1). Do NOT include a found_body "
    "observation. State who you suspect and your first-hand reason, or write "
    '"unsure".'
)

# The recorded-bytes shape of the ``fabricated_opening`` annotation, kept so
# ``api.replay_loader`` can project a committed transcript onto the same chips:
# a marker earlier builds prefixed to an EMERGENCY opening's ``free_text`` when
# a fabricated found_body was DETERMINISTICALLY stripped (Task 10.11.1). The v7
# prompt and the single retry are best-effort; this strip is the layered-defense
# backstop that makes ``orchestrator.game._assert_no_emergency_opening_body``
# unreachable (the recorded opening never carries a body), so the fail-loud
# guard can never abort a re-record on a stubborn 9B. Body-report openings keep
# their found_body untouched -- the strip is gated on the emergency opening only.
# Pin the literal exactly.
EMERGENCY_BODY_STRIP_MARKER: Final[str] = (
    "[emergency opening: fabricated found_body stripped] "
)

# The quoted-original bound is homed in :mod:`meetings.schemas` beside
# :class:`~meetings.schemas.TurnAnnotation`, which enforces it at the record
# boundary; re-exported here for the marker call sites and their importers.

# Matches the trailing ``:turn-{k}`` ordinal of a turn id. A
# ``primary_reason_id`` whose ordinal exists in THIS meeting but whose
# meeting prefix is wrong is a recoverable suffix form (the 7B model echoes
# the bare ``m-1:turn-0`` instead of the long canonical
# ``{meeting_id}:turn-0``); :func:`_normalize_ballot_reason_id` re-anchors it
# to the canonical id. An ordinal that does not exist in the meeting is
# nulled, never guessed.
_REASON_ID_TURN_SUFFIX: Final[re.Pattern[str]] = re.compile(r":turn-(\d+)$")

_SKIP_TARGET: Final[str] = "SKIP"
_VALID_ROLES: Final[frozenset[str]] = frozenset({"CREWMATE", "IMPOSTOR"})

# Self-alibi placeholder subjects the model occasionally emits in an
# ``AlibiClaim`` instead of its own canonical player id. Each leaks a
# prompt-template / few-shot artifact into the structured ``subject``
# field; :func:`_normalize_self_alibi_subjects` rewrites them to the
# speaker's id so DESIGN.md §5.4 contradiction detection can match the
# claim across speakers (Task 3.20):
#
# * ``"self"``         -- reference token (prompt-fix covered; kept here
#                          for defense-in-depth).
# * ``"p-self"``       -- the ``p-`` sibling-example prefix concatenated
#                          with the ``self`` token.
# * ``"{{ agent_id }}"`` -- an unrendered Jinja placeholder; only
#                          reachable via a template rendering bug, but
#                          rewriting it costs nothing and fails safe.
_SELF_ALIBI_PLACEHOLDERS: Final[frozenset[str]] = frozenset(
    {
        "self",
        "p-self",
        "{{ agent_id }}",
    }
)


_T = TypeVar("_T")


class LLMProviderError(RuntimeError):
    """LLM provider / transport failure (e.g. SDK or network timeout).

    Distinct from :class:`asyncio.TimeoutError` raised by the manager's
    per-turn deadlines (:class:`MeetingDeadlines`). In Python 3.11+
    :class:`asyncio.TimeoutError` is an alias of built-in
    :class:`TimeoutError`, so without an explicit conversion the manager's
    deadline handler would silently coerce provider timeouts into default
    turns / default-skip ballots. This class is the canonical
    infrastructure-failure signal; meeting callers can catch it explicitly
    (e.g. for retry or for a kill-meeting decision in the orchestrator).
    """


async def _isolate_provider_timeout(
    coro: Coroutine[Any, Any, _T],
) -> _T:
    """Re-tag any inner :class:`TimeoutError` as :class:`LLMProviderError`.

    Used to wrap LLM client calls before they are passed to
    :func:`asyncio.wait_for`. Without this, the manager's
    ``except asyncio.TimeoutError`` handler cannot distinguish a
    deadline-driven cancellation from an infrastructure timeout surfaced
    by the provider's own transport / SDK, and would default the
    participant's response when it should fail loud (AGENTS.md "no silent
    fallbacks").
    """

    try:
        return await coro
    except TimeoutError as e:
        raise LLMProviderError("LLM provider timeout") from e


@dataclass(frozen=True)
class MeetingParticipant:
    """One living agent's contribution to the meeting (DESIGN.md §5.1).

    By default the manager treats this as a static snapshot for the
    duration of the meeting: ``rendered_memory`` is what the §6.6 renderer
    produced when the meeting opened, ``role`` selects which opening prompt
    is used, and ``suspicion_graph`` populates the vote-ballot prompt input.

    ``fellow_impostor_ids`` carries the impostor-only teammate list
    (Task 7.12) onto the meeting layer: the sorted ids of the OTHER
    impostors when ``role == "IMPOSTOR"`` and ``()`` for every crewmate
    and for a sole impostor, never the participant's own id. The
    orchestrator populates it from world-state roles; the default of
    ``()`` keeps every existing construction site valid and is the
    firewall-correct value for a crewmate.

    ``rerender_memory`` is the Task 13.5.5 unfreeze hook. The orchestrator
    attaches it unconditionally; the manager stays env-free and hook-driven, so a
    ``None`` (the structural default, e.g. a direct-construction test or
    tooling participant) keeps the frozen open-tick ``rendered_memory`` for
    the ballot too. When a hook is attached the manager
    calls it ONLY for the ballot, passing the per-voter pre-vote-folded
    suspicion (the same numbers the ballot's ``suspicion_graph`` carries) as a
    ``suspicion_override``, so the rendered belief-line suspicion and that
    graph agree by construction (the PR #198 review inconsistency). Turn
    prompts always use the frozen render: they carry no ``suspicion_graph``,
    so there is no divergence to resolve there. The hook is a pure function of
    its argument + the deterministic belief snapshot (it re-invokes the §6.6
    renderer with the additive override), so a replay rebuilds the identical
    ballot string and ``verify_samples.sh`` stays byte-identical.

    ``vent_witness_records`` (Task 15.4) is the participant's OWN typed
    witnessed-vent channel -- the grounding input behind the ``vent_sighting``
    hard flag. The orchestrator populates it from
    ``MeetingAwareAgent.vent_witness_records_for_meeting()`` (episodic
    memory, self-channel only, so it is firewall-clean); the manager threads
    the per-speaker mapping into every
    :func:`meetings.transcript.detect_contradictions` call and NOTHING else
    reads it -- in particular it never reaches a prompt surface. The default
    ``()`` keeps every existing construction site valid and means "this
    speaker grounds nothing": a spoken vent observation from such a
    participant records as ordinary testimony and raises no flag.

    ``sighting_records`` (Task 16.7) is the vent channel's polarity-inverted
    sibling: the participant's OWN typed first-hand-sighting channel. The
    orchestrator populates it from
    ``MeetingAwareAgent.sighting_records_for_meeting()`` (episodic memory,
    self-channel only, so it is firewall-clean). It has two consuming seams,
    at different stages of wiring. The manager threads the per-speaker
    mapping into every
    :func:`meetings.transcript.detect_contradictions` call, where grounded
    prosecution checks a spoken sighting against the speaker's own record
    before it can band an ``alibi_vs_sighting`` flag STRONG. The VOUCH seam -- the ``sighting_records`` parameter of
    :func:`derive_belief_evidence`, which routes the same rows through
    :func:`meetings.transcript.grounded_vouch_subjects` into the
    relevance-gated ``corroborated`` set -- stays fixture-pinned and unfed,
    because feeding it moves committed ballot-prompt bytes at rest. The
    channel never reaches a prompt surface. The default ``()`` keeps every
    existing construction site valid and means "this speaker grounds nothing":
    their spoken sightings are ordinary testimony that exculpates no one and
    convicts no one.

    ``move_witness_records`` is the vent channel's movement sibling: the
    participant's OWN typed witnessed-transition channel, the grounding input
    the movement-claim chokepoint reads. The
    orchestrator populates it from
    ``MoveWitnessAgent.move_witness_records_for_meeting()`` (episodic memory,
    self-channel only, so it is firewall-clean); the manager threads the
    per-speaker mapping into every
    :func:`meetings.transcript.detect_contradictions` call and NOTHING else
    reads it -- in particular it never reaches a prompt surface. The default
    ``()`` keeps every existing construction site valid and means "this speaker
    grounds nothing": their spoken placements are read exactly as spoken.

    ``observation_ids`` (Task 16.5, C8) is the participant's OWN stable
    episodic observation-id set -- the valid-citation universe for a ballot's
    ``primary_reason_observation_id``. The orchestrator populates it from
    ``MeetingAwareAgent.observation_ids_for_meeting()`` (episodic memory,
    self-channel only, so it is firewall-clean -- the ids name the agent's
    own memory rows and leak nothing). The manager consults it in exactly ONE
    place, :func:`_normalize_ballot_observation_id`: a cited id outside this
    set is nulled with the audit marker. It never reaches a prompt surface;
    the validated citation's one downstream consumer is the citation gate
    (:func:`guard_ballot_citation`). The default ``()`` keeps every existing construction site valid and means
    "this voter can cite nothing": any non-null citation from such a
    participant nulls.

    ``persona`` (Task 16.3) is the inert persona-text slot: the orchestrator
    populates it from the deterministic persona-assignment bank in Task 16.9,
    and Task 16.16 renders it into the report / statement / ballot prompts
    (evidence-gated, after the citation gate). The manager threads it verbatim
    into every render seam as the ``persona`` kwarg the widened renderer
    Protocols accept. The default ``""`` keeps every existing construction site
    valid and renders byte-identically until 16.16 edits the templates (the
    widen-the-contract-inert pattern).
    """

    agent_id: PlayerId
    role: Role
    rendered_memory: str
    suspicion_graph: tuple[SuspicionEntry, ...] = ()
    fellow_impostor_ids: tuple[PlayerId, ...] = ()
    rerender_memory: Callable[[Mapping[PlayerId, float]], str] | None = None
    vent_witness_records: tuple[VentWitnessRecord, ...] = ()
    sighting_records: tuple[SightingRecord, ...] = ()
    move_witness_records: tuple[MoveWitnessRecord, ...] = ()
    observation_ids: tuple[ObservationId, ...] = ()
    persona: str = ""


@dataclass(frozen=True)
class MeetingTrigger:
    """Why the meeting was opened (DESIGN.md §5.1).

    The orchestrator constructs this from the engine event that
    transitioned the world into ``MEETING`` phase. ``triggered_by`` is the
    opener (turn 0); ``description`` is a short free-text summary (e.g.
    ``"p3 reported p2's body in MedBay at tick 410"``) that the opening
    prompt surfaces to the LLM.
    """

    triggered_by: PlayerId
    trigger_tick: int
    description: str


def _trigger_is_emergency(trigger: MeetingTrigger) -> bool:
    """True iff ``trigger`` opened an EMERGENCY meeting (Task 10.11.1).

    The meeting layer carries no structured trigger kind by design -- the
    description IS the trigger surface (``orchestrator.game._build_meeting_trigger``
    builds it from :data:`EMERGENCY_TRIGGER_PHRASE`, the same substring the
    ``crewmate_report.j2`` emergency branch keys on). Detecting it here off the
    same phrase keeps the no-body strip in lockstep with the prompt the model
    actually saw.
    """

    return EMERGENCY_TRIGGER_PHRASE in trigger.description


@dataclass(frozen=True)
class MeetingDeadlines:
    """Per-turn + vote deadlines (DESIGN.md §1.4, §5.2).

    ``None`` disables the deadline for that phase (headless mode); the
    value is passed straight to :func:`asyncio.wait_for`. ``turn_seconds``
    bounds each opening / reply / opt-in turn; ``vote_seconds`` bounds each
    ballot. The meeting's *total* turn count is hard-capped at the
    living-player count by the chain protocol itself (DESIGN.md §5.2
    PHASE 2), so the deterministic total-meeting bound is structural, not a
    wall-clock budget.
    """

    turn_seconds: float | None = DEFAULT_TURN_DEADLINE_SECONDS
    vote_seconds: float | None = DEFAULT_VOTE_DEADLINE_SECONDS


@dataclass(frozen=True)
class MeetingConfig:
    """Meeting protocol configuration (DESIGN.md §5.2)."""

    deadlines: MeetingDeadlines = field(default_factory=MeetingDeadlines)
    skip_confidence_threshold: float = DEFAULT_SKIP_CONFIDENCE_THRESHOLD
    turn_max_tokens: int = DEFAULT_TURN_MAX_TOKENS
    turn_temperature: float = DEFAULT_TURN_TEMPERATURE
    vote_max_tokens: int = DEFAULT_VOTE_MAX_TOKENS
    vote_temperature: float = DEFAULT_VOTE_TEMPERATURE


# Phase the default fell back on; a turn kind (:data:`TurnKind`) or the vote.
DefaultedPhase = Literal["opening", "reply", "opt_in", "vote"]
# Why a default fired. ``deadline`` is a wall-clock miss (only reachable with a
# configured deadline -- interactive mode); ``validation`` is a payload that
# failed schema validation even after the provider's parse-tolerance (reachable
# even in deadline-free headless recording).
DefaultTrigger = Literal["deadline", "validation"]


@dataclass(frozen=True)
class DefaultedCall:
    """A meeting turn / ballot that fell back to its default (audit gp-2).

    Surfaced by :meth:`MeetingManager.run` through
    :attr:`MeetingManager.defaulted_calls` so the orchestrator can write a
    visible ``deadline_default`` record into the replay. Audit gp-2: a turn
    that defaults must never vanish from the replay -- the headless recorder
    previously lost 11 turns (9 of 91 openings) to the interactive 30 s
    deadline with no record of any kind, so the report's ``failed_calls=0`` was
    true of the records and false of the run.

    The manager carries the facts the orchestrator needs to name the default
    in its replay record (and the real spend to preserve, see
    ``parse_failures``); the orchestrator owns the
    :class:`~orchestrator.replay.FailedCallReplayEntry` write itself
    (``error_type="deadline_default"``).

    * ``phase`` -- the defaulted slot: a turn kind (``opening`` / ``reply`` /
      ``opt_in``) or ``vote``.
    * ``agent_id`` -- the participant who submitted nothing.
    * ``trigger`` -- ``deadline`` (wall-clock miss, interactive only) or
      ``validation`` (a schema-invalid payload, reachable in headless mode).
    * ``turn_index`` -- the turn ordinal for a defaulted turn; ``None`` for a
      defaulted vote.
    * ``parse_failures`` -- the per-attempt provider parse-failure metadata for
      this default, one entry per attempt whose ``complete()`` raised a
      schema :class:`~pydantic.ValidationError` (a REAL provider validates
      internally and raises *before* the recording client can log the call, so
      that spend is otherwise lost). Empty for a deadline miss (nothing
      completed) and for a manager-side validation of a returned-but-invalid
      payload (whose spend the recording client already captured in the
      meeting's ``llm_calls``) -- in both cases the orchestrator writes a
      zero-spend visibility marker instead. :func:`llm.provider.extract_parse_failure`
      is the seam that distinguishes the two, so there is no double-count.
    * ``degraded`` -- ``True`` when the recorded turn is the Task 10.6
      VALIDATION-DEGRADE (an opening rebuilt as an unsure turn from the
      model's last parsed-but-position-less attempt,
      :data:`OPENING_UNSURE_DEGRADE_MARKER`) rather than the full
      placeholder default. This is the gp-5 telemetry split: a
      cap/deadline default (``degraded=False``) lost the model's output
      entirely; a validation-degrade kept its observations and surviving
      claims and lost only the invalid position. Always ``False`` for
      replies, opt-ins, and votes (only openings degrade) -- including the
      Task 10.9.1 vote parse-default, whose recorded ballot is the full
      default SKIP (the bounded head quoted by
      :data:`VOTE_PARSE_DEFAULT_MARKER` is an audit echo of the discarded
      response, not retained content).
    """

    phase: DefaultedPhase
    agent_id: PlayerId
    trigger: DefaultTrigger
    turn_index: int | None = None
    parse_failures: tuple[LLMCallFailure, ...] = ()
    degraded: bool = False
    # The rendered §4.6 max suspicion the defaulted VOTE prompt computed over
    # this voter's living ejection candidates (Task 10.12; audit
    # 2026-06-13-1816 H-H-2). A defaulted ballot's vote call fails BEFORE the
    # recording client logs its prompt, so the offline verdict reconstruction
    # (which reads the "maximum suspicion ... is **X**" line off successful
    # ``llm_calls`` only) always read ``no-render`` and routed the ballot to
    # ``skip_unclassified`` before the verdict check --
    # ``defaulted_under_must_vote`` was 0 BY CONSTRUCTION. Persisted onto the
    # orchestrator's failed_call row so a defaulted ballot's true MUST-vote /
    # MUST-skip verdict is classifiable. ``None`` for a turn default (no §4.6
    # verdict) and for a vote default recorded before this field existed (the
    # reader tolerates its absence; the committed single-era sets carry none).
    rendered_vote_max: float | None = None


class MeetingManager:
    """State machine that runs one meeting end-to-end (DESIGN.md §5.1, §5.2).

    Construction is cheap and side-effect free: it stores references to
    the LLM client, the prompt callables, and the config. Nothing runs
    until :meth:`run` is invoked, which is the trigger lifecycle in
    DESIGN.md §5.1.

    :meth:`run` sequences the reactive accusation chain (opening ->
    reactive chain -> opt-in) then voting and resolution. The manager
    returns the result without mutating engine state; the orchestrator
    applies the outcome to engine-owned state.
    """

    def __init__(
        self,
        *,
        llm_client: LLMClient,
        crewmate_report_prompt: ReportPromptRenderer,
        impostor_report_prompt: ReportPromptRenderer,
        statement_prompt: StatementPromptRenderer,
        vote_prompt: VotePromptRenderer,
        config: MeetingConfig | None = None,
    ) -> None:
        if config is None:
            config = MeetingConfig()
        if not 0.0 <= config.skip_confidence_threshold <= 1.0:
            raise ValueError(
                "MeetingConfig.skip_confidence_threshold must be in [0, 1], "
                f"got {config.skip_confidence_threshold}"
            )
        # Reject misconfigured deadlines fail-loud. A negative or zero
        # deadline reaches ``asyncio.wait_for`` and trips ``TimeoutError``
        # before the LLM call can complete, silently routing every turn
        # into the default-turn / default-skip path. That would change
        # meeting outcomes without any explicit configuration error
        # (AGENTS.md "no silent fallbacks"). ``None`` is the explicit
        # opt-out (headless mode, §1.4).
        for name, value in (
            ("turn_seconds", config.deadlines.turn_seconds),
            ("vote_seconds", config.deadlines.vote_seconds),
        ):
            if value is None:
                continue
            if value <= 0:
                raise ValueError(
                    f"MeetingDeadlines.{name} must be None or > 0, got {value}"
                )
        self._llm_client = llm_client
        self._crewmate_report_prompt = crewmate_report_prompt
        self._impostor_report_prompt = impostor_report_prompt
        self._statement_prompt = statement_prompt
        self._vote_prompt = vote_prompt
        self._config = config
        # Per-run scratch: the defaults that fired during the most recent
        # :meth:`run`. Reset at the top of every ``run`` (the manager is reused
        # across a game's meetings) and read by the orchestrator immediately
        # after ``run`` returns (audit gp-2). Not engine state and not a DTO --
        # a turn/ballot that defaulted is recorded into the replay through the
        # existing failed-call channel, never lost silently.
        self._defaulted_calls: list[DefaultedCall] = []
        # Per-run scratch: provider parse-failures recovered on a SUCCEEDING
        # turn (an earlier retry attempt raised before the recording client
        # could log it, then a later attempt succeeded). The default path keeps
        # its failures on the ``DefaultedCall``; these are the ones a success
        # would otherwise swallow, so the orchestrator records them too -- the
        # burned spend stays visible even when the turn ultimately parses.
        self._recovered_call_failures: list[LLMCallFailure] = []

    @property
    def defaulted_calls(self) -> tuple[DefaultedCall, ...]:
        """Defaults that fired during the most recent :meth:`run` (audit gp-2).

        Reset at the start of every :meth:`run`. The orchestrator reads this
        right after ``run`` returns and writes one visible ``deadline_default``
        replay record per entry, so a turn / ballot that fell back to its
        placeholder is never lost from the replay (the headless recorder
        previously dropped 11 such turns with no record of any kind). Empty for
        a meeting in which every turn and ballot was produced normally.
        """

        return tuple(self._defaulted_calls)

    @property
    def recovered_call_failures(self) -> tuple[LLMCallFailure, ...]:
        """Provider parse-failures recovered on a succeeding turn (this run).

        A real provider validates internally and raises before the recording
        client logs the call, so a retry that fails once and then succeeds would
        otherwise lose the failed attempt's spend (it is absent from
        ``llm_calls`` and the success path carries no ``DefaultedCall``). The
        orchestrator records each as a failed-call row so call count and cost
        stay accurate. Reset at the start of every :meth:`run`.
        """

        return tuple(self._recovered_call_failures)

    async def run(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        participants: Sequence[MeetingParticipant],
        dead_ids: tuple[PlayerId, ...] = (),
        impostor_count: int | None = None,
    ) -> MeetingResult:
        """Run opening -> reactive chain -> opt-in -> voting -> resolution.

        The returned ``MeetingResult.transcript.turns`` is the single
        ordered turn list (DESIGN.md §5.2): turn 0 is the opening (the
        opener is ``trigger.triggered_by``, which MUST be a living
        participant), followed by the reactive ``reply`` chain and any
        terminal ``opt_in`` turns. Turn ids are ``"{meeting_id}:turn-{N}"``.
        The chain's next speaker and its termination are pure functions of
        the recorded turns, so a replay reconstructs the discussion from
        ``transcript.turns`` without re-calling the LLM.

        ``dead_ids`` (Task 10.3, audit gp-9) is the dead / ejected roster
        the orchestrator derived from world state. It is render-only
        context -- threaded into the turn prompts as an explicit
        do-not-accuse line under the living roster -- and never widens any
        validation: a claim naming a dead player still drops at the
        per-turn chokepoint exactly as before. ``()`` (existing call
        sites, ad-hoc runs) omits the line.

        ``impostor_count`` (Task 20.31) is how many impostors the game was
        seeded with -- the roster preset's own public setting, derived by the
        orchestrator from world state the same way ``dead_ids`` is. It is
        render-only: the templates state the count and the win condition with
        the right arithmetic, and nothing about validation or tallying reads
        it. ``None`` (existing call sites, ad-hoc runs) leaves every template
        on its singular wording.
        """

        if not meeting_id:
            raise ValueError("meeting_id must be a non-empty string")
        if not participants:
            raise ValueError(
                "MeetingManager.run requires at least one living participant"
            )
        self._validate_participants(participants, trigger=trigger)
        # A dead id that is also a living participant is contradictory
        # orchestrator wiring -- it would render the same player as both a
        # valid accusation target and a do-not-accuse line. Fail loud at
        # meeting entry (AGENTS.md "no silent fallbacks"); sort for a
        # deterministic prompt render regardless of caller ordering.
        overlap = {p.agent_id for p in participants} & set(dead_ids)
        if overlap:
            raise ValueError(
                f"dead_ids overlap living participants: {sorted(overlap)}; "
                "a meeting participant cannot also be dead"
            )
        dead_ids = tuple(sorted(dead_ids))

        # Fresh per-run ledgers (the manager is reused across a game's
        # meetings); the orchestrator reads :attr:`defaulted_calls` and
        # :attr:`recovered_call_failures` after this ``run`` returns (audit
        # gp-2).
        self._defaulted_calls = []
        self._recovered_call_failures = []
        # Render-only per-game facts, built once and threaded to every prompt
        # the way ``dead_ids`` is. The map card is not here: it is a constant of
        # the map, bound onto each renderer at construction by the loader.
        render_inputs = PromptRenderInputs(impostor_count=impostor_count)

        # Canonicalise participant order at entry. Real callers may iterate
        # over a set/dict whose order is hash-seeded and not
        # determinism-preserving; sorting by ``agent_id`` is deterministic
        # and matches the lexical ``p-N`` convention used everywhere else.
        ordered_participants = tuple(sorted(participants, key=lambda p: p.agent_id))
        by_id = {p.agent_id: p for p in ordered_participants}
        roster = frozenset(by_id)
        # Task 15.4: the per-speaker typed vent-witness channel -- the
        # grounding chokepoint's input, threaded into EVERY contradiction
        # detection below so a mid-chain turn prompt and the final recorded
        # flag set read one grounding source. A meeting-open snapshot like
        # ``rendered_memory``; participants with no records are omitted (the
        # detector treats an absent speaker as grounding nothing).
        vent_witness_records: Mapping[PlayerId, tuple[VentWitnessRecord, ...]] = {
            participant.agent_id: participant.vent_witness_records
            for participant in ordered_participants
            if participant.vent_witness_records
        }
        # The movement-claim grounding channel, threaded the same way: one
        # source for every detection below.
        move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]] = {
            participant.agent_id: participant.move_witness_records
            for participant in ordered_participants
            if participant.move_witness_records
        }
        # The grounded-prosecution channel -- the same first-hand sighting
        # rows the grounded-vouch path reads, threaded into detection so a
        # spoken sighting can be checked against the speaker's own record
        # before it convicts.
        #
        # The §4.7 TEAMMATE firewall is applied HERE, not inherited: the
        # accessor keeps an impostor's rows naming a fellow impostor because
        # its only consumer CORROBORATES, and says a prosecuting consumer must
        # re-apply the suppression. This is that consumer, so a row the §6.6
        # render hides from its own holder cannot ground a flag against the
        # teammate it names. The vouch seam is unaffected (it reads the
        # participant field, not this mapping) -- the movement channel draws
        # the same line at its accessor.
        sighting_records: dict[PlayerId, tuple[SightingRecord, ...]] = {}
        for participant in ordered_participants:
            fellows = frozenset(participant.fellow_impostor_ids)
            rows = tuple(
                record
                for record in participant.sighting_records
                if record.subject not in fellows
            )
            if rows:
                sighting_records[participant.agent_id] = rows

        # Phase 1: opening turn (turn 0, role-dispatched). The opening is a
        # single point of failure for the whole meeting -- an empty opening
        # names no accusation, so the chain is dead and every ballot votes on a
        # husk -- so it is retried once before defaulting (audit gp-2).
        opener = by_id[trigger.triggered_by]
        opening_turn = await self._collect_turn(
            meeting_id=meeting_id,
            trigger=trigger,
            participant=opener,
            living_ids=roster,
            dead_ids=dead_ids,
            render_inputs=render_inputs,
            turn_index=0,
            turn_kind="opening",
            reply_to=None,
            prior_turn=None,
            transcript_so_far=MeetingTranscript(),
            contradictions=(),
            retries=1,
        )
        turns: list[MeetingTurn] = [opening_turn]
        spoken: set[PlayerId] = {opener.agent_id}

        # Phase 2: reactive chain (next speaker = the accused; deterministic
        # 3-condition termination -- DESIGN.md §5.2 PHASE 2).
        while True:
            prev = turns[-1]
            step = next_chain_step(
                prev_turn=prev,
                spoken=frozenset(spoken),
                living_ids=roster,
                turns_recorded=len(turns),
            )
            if step.next_speaker is None:
                break
            # 7.12 defense-in-depth at the chain-passing chokepoint: never
            # pass the floor to a fellow impostor of the accuser. The per-turn
            # claim guard already strips a teammate accusation before the turn
            # is recorded, so ``accusation_target`` (and therefore
            # ``next_chain_step``) never names a teammate here -- this is a
            # provable no-op that keeps the guard on the chain path and never
            # diverges the replay-walk (which re-derives via ``next_chain_step``).
            guarded_next = drop_teammate_statement_target(
                step.next_speaker,
                fellow_impostor_ids=by_id[prev.speaker].fellow_impostor_ids,
            )
            if guarded_next is None:
                break
            transcript_so_far = MeetingTranscript(turns=tuple(turns))
            contradictions_so_far = detect_contradictions(
                transcript_so_far,
                roster=roster,
                vent_witness_records=vent_witness_records,
                move_witness_records=move_witness_records,
                sighting_records=sighting_records,
            )
            reply_turn = await self._collect_turn(
                meeting_id=meeting_id,
                trigger=trigger,
                participant=by_id[guarded_next],
                living_ids=roster,
                dead_ids=dead_ids,
                render_inputs=render_inputs,
                turn_index=len(turns),
                turn_kind="reply",
                reply_to=prev.turn_id,
                prior_turn=prev,
                transcript_so_far=transcript_so_far,
                contradictions=contradictions_so_far,
            )
            turns.append(reply_turn)
            spoken.add(guarded_next)

        # Phase 3: opt-in info-share. Eligibility is computed ONCE from the
        # post-chain transcript (a co-presence gate with the body / accused),
        # so an opt-in turn's own accusation never makes a new player eligible
        # and never extends the chain (DESIGN.md §5.2 PHASE 3).
        transcript_after_chain = MeetingTranscript(turns=tuple(turns))
        for opt_in_id in _opt_in_eligible_ids(
            transcript=transcript_after_chain,
            spoken=frozenset(spoken),
            living_ids=roster,
        ):
            transcript_so_far = MeetingTranscript(turns=tuple(turns))
            contradictions_so_far = detect_contradictions(
                transcript_so_far,
                roster=roster,
                vent_witness_records=vent_witness_records,
                move_witness_records=move_witness_records,
                sighting_records=sighting_records,
            )
            opt_in_turn = await self._collect_turn(
                meeting_id=meeting_id,
                trigger=trigger,
                participant=by_id[opt_in_id],
                living_ids=roster,
                dead_ids=dead_ids,
                render_inputs=render_inputs,
                turn_index=len(turns),
                turn_kind="opt_in",
                reply_to=None,
                prior_turn=None,
                transcript_so_far=transcript_so_far,
                contradictions=contradictions_so_far,
            )
            turns.append(opt_in_turn)
            spoken.add(opt_in_id)

        # The roll-call round. Every living player who has not yet spoken --
        # the Phase-3 co-presence gate leaves 53% of living player-meetings
        # silent (audits/audit-phase-18-planning.md §3.4) -- takes one terminal
        # ``opt_in``-surface turn in ascending player-id order, the
        # turn-allocation routing audits/audit-phase-17-absence-gate.md
        # Ruling 3(a) sends to Phase 18. Each turn reuses the existing opt-in
        # surface through the single per-turn chokepoint, so it inherits the
        # same guards and the same deadline/default fail-soft (no ``retries``
        # -- a defaulted roll-call turn is recorded exactly like a defaulted
        # opt-in). NOT co-presence-gated: every living non-speaker is asked, so
        # ``_opt_in_eligible_ids`` is deliberately not reused here.
        for roll_call_id in sorted(roster - spoken):
            transcript_so_far = MeetingTranscript(turns=tuple(turns))
            contradictions_so_far = detect_contradictions(
                transcript_so_far,
                roster=roster,
                vent_witness_records=vent_witness_records,
                move_witness_records=move_witness_records,
                sighting_records=sighting_records,
            )
            roll_call_turn = await self._collect_turn(
                meeting_id=meeting_id,
                trigger=trigger,
                participant=by_id[roll_call_id],
                living_ids=roster,
                dead_ids=dead_ids,
                render_inputs=render_inputs,
                turn_index=len(turns),
                turn_kind="opt_in",
                reply_to=None,
                prior_turn=None,
                transcript_so_far=transcript_so_far,
                contradictions=contradictions_so_far,
            )
            turns.append(roll_call_turn)
            spoken.add(roll_call_id)

        transcript = MeetingTranscript(turns=tuple(turns))

        # Phase 4: contradictions recompute ONCE over the full transcript
        # before voting (DESIGN.md §5.4), then the PRE-VOTE half of the
        # meeting fold (Task 10.7; audit gp-2): the meeting's belief
        # evidence -- including the two-witness ``pre_vote_folded``
        # subjects and the relevance-gated ``corroborated`` set -- is
        # derived once from the final transcript and threaded into every
        # ballot, so each voter's suspicion graph (and therefore the
        # in-prompt §4.6 verdict, which the frozen template computes from
        # that same graph) reads post-fold values. Both fold halves ALWAYS
        # run: this pre-vote derivation is unconditional (an evidence-free
        # meeting derives empty sets and folds nothing), and the post-vote
        # half is the orchestrator's standing post-meeting absorb.
        # Thread the trigger kind so the 13.4 physical detector's reconstruction
        # drops an EMERGENCY meeting's (possibly fabricated) opening-body
        # kill-scene exclusion (Task 10.11); ``report`` keeps the opening body.
        meeting_trigger_kind: MeetingTriggerKind = (
            "emergency" if _trigger_is_emergency(trigger) else "report"
        )
        contradictions = detect_contradictions(
            transcript,
            roster=roster,
            trigger_kind=meeting_trigger_kind,
            vent_witness_records=vent_witness_records,
            move_witness_records=move_witness_records,
            sighting_records=sighting_records,
        )
        # The VOUCH half of the sighting channel is still not threaded here.
        # Detection above receives the per-speaker mapping (grounding a spoken
        # sighting before it can convict), but passing the same mapping into
        # :func:`derive_belief_evidence` would feed the -0.05 exculpation
        # channel and move committed ballot-prompt bytes at rest -- committed
        # transcripts already carry speaker-groundable sightings (9p2i seed-0
        # meeting-0: p-5/p-6 mutual grounded vouches). Task 16.7's mechanism is
        # complete and fixture-pinned behind the parameter, unfed.
        evidence = derive_belief_evidence(
            transcript, contradictions=contradictions, roster=roster
        )
        # Task 16.8 (PR #264 review): re-derive the ABSENT set with the
        # ENGINE-derived trigger kind. The sibling folds above keep their
        # standing ``trigger_kind=None`` call shape (threading the kind into
        # them would change the recorded emergency-meeting behavior of the
        # corroboration/voices gates -- the 16.7 sighting-records precedent
        # declines exactly that), but the absent set feeds the absence prior --
        # unconditional since the Task-18.12 baseline-6 record -- and must
        # honor the Task 10.11 emergency gate: under ``None`` a
        # model-FABRICATED opening body in an emergency transcript reads as a
        # report kill scene, relevance-gates away real public sightings at
        # that room, and would now mint spurious absence on every such
        # meeting. The true-kind derivation is also what the replay path
        # already computes (:func:`extract_belief_evidence` receives the
        # trigger kind), so live and replay agree on every meeting.
        # Task 18.12: apply the 17.5 vent-placement widening here too (the
        # ``vent_sighting`` flag channel, byte-identical to the record-driven
        # widening), so the live absent set matches the replay re-derivation above.
        _vent_placed = grounded_vent_subjects_from_flags(contradictions)
        evidence = replace(
            evidence,
            absent=tuple(
                player
                for player in absent_players(
                    transcript, roster=roster, trigger_kind=meeting_trigger_kind
                )
                if player not in _vent_placed
            ),
        )
        ballots = await self._collect_ballots(
            trigger=trigger,
            participants=ordered_participants,
            transcript=transcript,
            contradictions=contradictions,
            evidence=evidence,
            render_inputs=render_inputs,
        )

        # Phase 5: resolution.
        outcome, ejected = self._tally(ballots)
        return MeetingResult(
            meeting_id=meeting_id,
            triggered_by=trigger.triggered_by,
            trigger_tick=trigger.trigger_tick,
            outcome=outcome,
            ejected_player_id=ejected,
            ballots=ballots,
            contradictions=contradictions,
            transcript=transcript,
        )

    # -- Turn collection (the single per-turn chokepoint) -----------------

    async def _collect_turn(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        participant: MeetingParticipant,
        living_ids: frozenset[PlayerId],
        turn_index: int,
        turn_kind: TurnKind,
        reply_to: str | None,
        prior_turn: MeetingTurn | None,
        transcript_so_far: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
        dead_ids: tuple[PlayerId, ...] = (),
        render_inputs: PromptRenderInputs | None = None,
        retries: int = 0,
    ) -> MeetingTurn:
        """Collect one turn through the shared guard chokepoint.

        Every turn-kind (opening / reply / opt-in) flows through here, so
        every turn inherits the same guards: self-alibi normalization, the
        Task 7.12 teammate firewall, and the Task 7.10 fail-soft. The
        manager is authoritative for the identity fields (``turn_id``,
        ``turn_index``, ``speaker``, ``turn_kind``, ``reply_to``); the LLM
        supplies only ``observations`` / ``claims`` / ``free_text``.

        ``retries`` is the number of EXTRA attempts on top of the first before
        the turn defaults (the opening passes ``retries=1`` -- audit gp-2). A
        fired default is appended to :attr:`defaulted_calls` so the orchestrator
        can record it in the replay. The BASE prompt is rendered once (its
        inputs do not change between retries); an opening retry after a
        content-validation failure re-sends it with the Task 10.6 feedback
        block appended (:data:`OPENING_RETRY_FEEDBACK_HEADER` ...), naming
        the dropped dead target(s) when the guard emptied the accusation --
        the Wave-0 retries were byte-identical re-asks at temp 0.4 and
        recovered 0/3 openings (audit gp-5 H-H-1).

        An OPENING attempt is additionally content-validated (Task 10.3,
        audit gp-9 H-H-1): a turn whose recorded claims carry no
        accusation and whose free_text carries no explicit
        :data:`OPENING_UNSURE_MARKER` declaration is narration-only -- it
        kills the reactive chain on turn 0 -- so it is treated exactly
        like a schema-validation failure and consumes an attempt through
        this same loop (one retry, then the fail-soft; no second retry
        channel). The fail-soft itself is two-tier since Task 10.6 (audit
        gp-5 H-H-2): when at least one attempt PARSED but took no
        position, the opening degrades to an UNSURE turn built from that
        attempt -- observations and surviving claims kept, position
        recorded as unsure via :data:`OPENING_UNSURE_DEGRADE_MARKER` --
        so the meeting keeps its body report and still reaches opt-ins
        and ballots; only when nothing ever parsed (deadline / schema
        failure on every attempt) does the full placeholder default fire.
        Replies / opt-ins are never content-validated: a purely defensive
        reply is a legitimate chain terminator.
        """

        base_prompt = self._render_turn_prompt(
            participant=participant,
            turn_kind=turn_kind,
            trigger=trigger,
            transcript_so_far=transcript_so_far,
            contradictions=contradictions,
            prior_turn=prior_turn,
            living_ids=living_ids,
            dead_ids=dead_ids,
            render_inputs=render_inputs,
        )
        prompt = base_prompt
        turn_id = _turn_id(meeting_id=meeting_id, turn_index=turn_index)
        # The trigger kind of the LAST failed attempt, recorded with the
        # default so the orchestrator can name it (deadline vs validation).
        trigger_kind: DefaultTrigger = "deadline"
        # Per-attempt provider parse-failure metadata (real spend the recording
        # client never logged because ``complete()`` raised before it could).
        attempt_failures: list[LLMCallFailure] = []
        # The most recent opening attempt that parsed but took no position
        # (Task 10.6 unsure-degrade source); ``None`` until one exists.
        positionless_opening: _PositionlessOpening | None = None
        for _attempt in range(retries + 1):
            try:
                response = await asyncio.wait_for(
                    _isolate_provider_timeout(
                        self._llm_client.complete(
                            prompt=prompt,
                            schema=MeetingTurn,
                            max_tokens=self._config.turn_max_tokens,
                            temperature=self._config.turn_temperature,
                            call_kind="meeting",
                            agent_id=participant.agent_id,
                        )
                    ),
                    timeout=self._config.deadlines.turn_seconds,
                )
                # The turn schema doubles as the provider's structured-output
                # contract, so ``annotations`` is askable -- but it is the
                # manager's record of its OWN guards and is never authorable.
                # Anything the model volunteered under that name is dropped
                # here, at the wire boundary, so no branch below can read a
                # model-authored row (the recording paths overwrite the field
                # too; this is the boundary layer of that defense).
                parsed = MeetingTurn.model_validate_json(response.text).model_copy(
                    update={"annotations": ()}
                )
            except (asyncio.TimeoutError, ValidationError) as exc:
                # Fail-soft on a single turn (Task 7.10): a missed deadline
                # (``TimeoutError``) and a malformed turn that still fails
                # schema validation after the provider's parse-tolerance
                # normalization (``ValidationError`` -- e.g. an ``AlibiClaim``
                # so broken the chronological-range swap cannot salvage it)
                # BOTH degrade to the same placeholder so the meeting continues
                # to its vote and the game reaches ``game_over``. A
                # provider/transport timeout is still re-tagged
                # ``LLMProviderError`` (by ``_isolate_provider_timeout``) and
                # propagates -- only the deadline + parse failures fail soft.
                # Note which fired so the surfaced ``deadline_default`` record
                # names it (audit gp-2); ``asyncio.TimeoutError`` is built-in
                # ``TimeoutError`` in 3.11+, distinct from ``ValidationError``.
                trigger_kind = (
                    "deadline"
                    if isinstance(exc, asyncio.TimeoutError)
                    else "validation"
                )
                # A REAL provider validates internally and raises *before* the
                # recording client logs the call, so its spend is lost from
                # ``llm_calls`` unless we carry it on the surfaced default. The
                # metadata rides the ``ValidationError`` (Anthropic/Ollama
                # ``_attach_parse_failure``); ``extract_parse_failure`` returns
                # ``None`` for a deadline miss and for a manager-side validation
                # of a returned-but-invalid payload (already in ``llm_calls``),
                # so collecting it here never double-counts.
                failure = extract_parse_failure(exc)
                if failure is not None:
                    attempt_failures.append(failure)
                continue
            # Defense-in-depth: rewrite self-alibi placeholder subjects (e.g.
            # "p-self") to the speaker's canonical id before the identity
            # override, so DESIGN.md §5.4 contradiction detection can match
            # this turn's self-alibi against other speakers (Task 3.20).
            normalized_claims = _normalize_self_alibi_subjects(
                parsed.claims, speaker_id=participant.agent_id
            )
            # Teammate firewall guard (Task 7.12) on EVERY turn-kind: drop any
            # accusation an impostor makes against a fellow impostor. Because
            # the chain reads its next speaker off these recorded claims,
            # guarding here is what keeps an impostor from passing the chain to
            # (or publicly incriminating) a teammate on any turn. Deterministic
            # and a no-op for a crewmate / sole impostor, so replay is
            # unaffected.
            guarded_claims = _guard_teammate_turn_claims(
                normalized_claims, fellow_impostor_ids=participant.fellow_impostor_ids
            )
            # Task 15.4: the teammate firewall's observation-side twin. A
            # structured vent observation naming a fellow impostor is
            # role-proving incrimination (grounded, it would mint a STRONG
            # ``vent_sighting`` flag against the teammate), so it drops at the
            # same per-turn chokepoint the teammate accusation does -- BEFORE
            # the turn records, so it never reaches detection, the fold, or a
            # prompt surface. Silent like the claims guard (the 7.12
            # convention); a deterministic no-op for every crewmate and a sole
            # impostor, so replay reconstruction is unaffected.
            guarded_observations = exclude_teammate_vent_observations(
                parsed.observations,
                fellow_impostor_ids=participant.fellow_impostor_ids,
            )
            if len(guarded_observations) != len(parsed.observations):
                parsed = parsed.model_copy(
                    update={"observations": guarded_observations}
                )
            # Drop claims whose subject-bearing field names no living
            # participant: accusation targets (the fb3cfa5 guard) plus
            # alibi subjects and corroboration supports (Task 10.2, audit
            # gp-6). The 9B emits structural ids ("headless-seed-9", turn
            # ids, "p-2 dead") that would otherwise record into the
            # transcript, reach §5.4 detection and the post-meeting fold,
            # and render as phantom §6.6 suspicion rows. Validation runs
            # here -- BEFORE the turn is recorded -- so a dropped subject
            # never mints a contradiction flag and never materialises a
            # belief row; each dropped claim's original value is preserved
            # on the turn as a typed annotation.
            validated_claims, drop_annotations = _drop_non_roster_claims(
                guarded_claims, living_ids=living_ids
            )
            # Emergency-opening no-body backstop (Task 10.11.1;
            # audit-2026-06-13-1816 B-B-1). An EMERGENCY meeting reports no
            # corpse (DESIGN.md §5.2 PHASE 1) -- the caller pressed the button on
            # suspicion. The v7 crewmate_report emergency branch asks for this,
            # but the 9B can ignore it (flat seed 11 m0 re-narrated a stale body
            # as a fresh find), and the orchestrator's fail-loud
            # ``_assert_no_emergency_opening_body`` then aborts the whole
            # re-record. This DETERMINISTIC strip is the layered-defense backstop
            # that makes the guard unreachable: re-ask ONCE for a clean opening
            # (the stale body can anchor the model's free_text) before stripping,
            # so a compliant retry keeps a richer opening and a stubborn one
            # still records body-free. Gated on the OPENING of an EMERGENCY
            # meeting, so every body-report opening -- and every reply / opt-in
            # turn -- stays byte-identical (the guard checks the opening only).
            if (
                turn_kind == "opening"
                and _trigger_is_emergency(trigger)
                and any(
                    isinstance(observation, FoundBodyObservation)
                    for observation in parsed.observations
                )
            ):
                if _attempt < retries:
                    trigger_kind = "validation"
                    prompt = base_prompt + EMERGENCY_NO_BODY_RETRY_FEEDBACK
                    continue
                parsed = parsed.model_copy(
                    update={
                        "observations": tuple(
                            observation
                            for observation in parsed.observations
                            if not isinstance(observation, FoundBodyObservation)
                        )
                    }
                )
                drop_annotations = (
                    TurnAnnotation(kind="fabricated_opening"),
                    *drop_annotations,
                )
            # Opening content validation (Task 10.3, audit gp-9 H-H-1): the
            # opener must accuse or explicitly declare "unsure" (DESIGN.md
            # §5.2 PHASE 1). Checked AFTER the guards, against the claims as
            # they would record -- an opening whose only accusation named a
            # dead player (the seed-13-m0 shape) or a teammate is as
            # chain-dead as pure narration -- and against the MODEL-AUTHORED
            # free_text, never the marker-prefixed text (a drop marker quotes
            # the original value, so a hallucinated target literally named
            # "unsure" must not self-certify the turn). A failure consumes
            # this attempt like any validation failure: the opening's single
            # retry (``retries=1``) re-asks once -- WITH the Task 10.6
            # feedback block naming the failure appended to the base prompt
            # -- then the fail-soft fires (the unsure-degrade, since this
            # attempt parsed).
            if turn_kind == "opening" and not _opening_takes_position(
                claims=validated_claims,
                observations=parsed.observations,
                free_text=parsed.free_text,
            ):
                trigger_kind = "validation"
                positionless_opening = _PositionlessOpening(
                    observations=parsed.observations,
                    claims=validated_claims,
                    free_text=parsed.free_text,
                    annotations=drop_annotations,
                )
                prompt = base_prompt + _opening_retry_feedback(
                    dropped_targets=tuple(
                        claim.against
                        for claim in guarded_claims
                        if isinstance(claim, AccusationClaim)
                        and claim.against not in living_ids
                    )
                )
                continue
            # What a guard changed is a typed row ON the turn; ``free_text`` is
            # exactly what the model authored.
            free_text = parsed.free_text
            recorded_annotations: tuple[TurnAnnotation, ...] = drop_annotations
            # This turn parsed, but an earlier retry attempt may have raised a
            # provider parse-failure the recording client never logged. Surface
            # that burned spend so it is recorded even though no default fired
            # (the default path instead carries its failures on the
            # ``DefaultedCall``). Empty -- the common no-retry case -- is a
            # no-op.
            self._recovered_call_failures.extend(attempt_failures)
            # Override the identity fields with the canonical values; the LLM
            # is told to emit any non-empty string and the manager is
            # authoritative for who said what and where it sits in the chain.
            return parsed.model_copy(
                update={
                    "turn_id": turn_id,
                    "turn_index": turn_index,
                    "speaker": participant.agent_id,
                    "turn_kind": turn_kind,
                    "reply_to": reply_to,
                    "claims": validated_claims,
                    "free_text": free_text,
                    # Always overridden, like the identity fields: annotations
                    # are the manager's record of its own guards, never the
                    # model's to author.
                    "annotations": recorded_annotations,
                }
            )
        # Every attempt (1 + ``retries``) failed: surface the fired default so
        # the orchestrator records it in the replay (audit gp-2 -- a defaulted
        # turn must never be invisible), carrying any provider parse-failure
        # spend so the audit trail stays accurate. Two tiers (Task 10.6, audit
        # gp-5 H-H-2): an opening with a parsed-but-position-less attempt
        # degrades to an UNSURE opening built from that attempt -- the body
        # report and surviving claims are kept, so opt-in eligibility and the
        # ballots still see them -- while a turn that never parsed returns
        # the full placeholder. ``degraded`` is the telemetry split between
        # the two (cap/deadline default vs validation-degrade).
        self._defaulted_calls.append(
            DefaultedCall(
                phase=turn_kind,
                agent_id=participant.agent_id,
                trigger=trigger_kind,
                turn_index=turn_index,
                parse_failures=tuple(attempt_failures),
                degraded=positionless_opening is not None,
            )
        )
        if positionless_opening is not None:
            degrade_annotations = (
                TurnAnnotation(kind="opening_degraded_unsure"),
                *positionless_opening.annotations,
            )
            return MeetingTurn(
                turn_id=turn_id,
                turn_index=turn_index,
                speaker=participant.agent_id,
                turn_kind=turn_kind,
                reply_to=reply_to,
                observations=positionless_opening.observations,
                claims=positionless_opening.claims,
                free_text=positionless_opening.free_text,
                annotations=degrade_annotations,
            )
        return _default_turn(
            turn_id=turn_id,
            turn_index=turn_index,
            speaker=participant.agent_id,
            turn_kind=turn_kind,
            reply_to=reply_to,
        )

    def _render_turn_prompt(
        self,
        *,
        participant: MeetingParticipant,
        turn_kind: TurnKind,
        trigger: MeetingTrigger,
        transcript_so_far: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
        prior_turn: MeetingTurn | None,
        living_ids: frozenset[PlayerId],
        dead_ids: tuple[PlayerId, ...] = (),
        render_inputs: PromptRenderInputs | None = None,
    ) -> str:
        # Living-roster accusation list (Task 9.9, audit gp-3): living
        # participants minus this turn's speaker -- an agent cannot accuse
        # itself -- via the same ``_candidate_targets`` filter the vote
        # ballot uses for its eject targets (living minus voter).
        # ``dead_ids`` (Task 10.3, audit gp-9) is the matching negative
        # list, passed verbatim to every turn renderer: the do-not-accuse
        # line names the dead for every speaker alike.
        accusation_targets = _candidate_targets(
            living_ids, exclude=participant.agent_id
        )
        # Task 13.5.5: turn prompts always read the frozen open-tick render.
        # A turn carries NO ``suspicion_graph`` kwarg (the belief-line-vs-graph
        # divergence the unfreeze hook targets exists only at the ballot), and
        # the running meeting evidence already reaches speakers via the
        # transcript -- so re-rendering here would change nothing it needs.
        if turn_kind == "opening":
            renderer = (
                self._impostor_report_prompt
                if participant.role == "IMPOSTOR"
                else self._crewmate_report_prompt
            )
            return renderer(
                agent_id=participant.agent_id,
                current_tick=trigger.trigger_tick,
                meeting_trigger=trigger.description,
                rendered_memory=participant.rendered_memory,
                public_transcript="",
                fellow_impostor_ids=participant.fellow_impostor_ids,
                living_ids=accusation_targets,
                dead_ids=dead_ids,
                # Task 16.3 inert widenings (rendered by 16.16 / 16.15). The
                # turn carries the frozen open-tick ``suspicion_graph`` as its
                # provenance input -- the same rows whose scalars the frozen
                # memory already shows -- so a later provenance surface decomposes
                # exactly that state. ``""`` / ``()`` render byte-identical today.
                persona=participant.persona,
                suspicion_provenance=participant.suspicion_graph,
                render_inputs=render_inputs,
            )
        return self._statement_prompt(
            agent_id=participant.agent_id,
            rendered_memory=participant.rendered_memory,
            transcript=transcript_so_far,
            contradictions=contradictions,
            prior_turn=prior_turn,
            turn_kind=turn_kind,
            fellow_impostor_ids=participant.fellow_impostor_ids,
            living_ids=accusation_targets,
            dead_ids=dead_ids,
            # Task 16.3 inert widenings (rendered by 16.16 / 16.15); the frozen
            # open-tick graph is the provenance input, matching the frozen memory
            # this turn renders. ``""`` / ``()`` render byte-identical today.
            persona=participant.persona,
            suspicion_provenance=participant.suspicion_graph,
            # Task 11.2 (DESIGN.md §5.2): the cover-consistency directive on
            # the reply branch fires for the impostor role. An explicit bool
            # rather than `fellow_impostor_ids` because a SOLE impostor has
            # empty fellows but must still get the directive; the template
            # scopes it to the reply branch (the opt-in turn is terminal).
            is_impostor=(participant.role == "IMPOSTOR"),
            # PR #159 review: the cover directive talks about "the body's room
            # and the tick it happened", so it must fire only on a body-report
            # meeting -- never on a body-less emergency reply, which would inject
            # contradictory "a body was found" copy. Derived from the trigger
            # via the same load-bearing substring the opening templates branch
            # on (mirrors impostor_report.j2's `body_report_opening` gate).
            is_body_report=(EMERGENCY_TRIGGER_PHRASE not in trigger.description),
            render_inputs=render_inputs,
        )

    # -- Voting -----------------------------------------------------------

    async def _collect_ballots(
        self,
        *,
        trigger: MeetingTrigger,
        participants: Sequence[MeetingParticipant],
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
        evidence: MeetingBeliefEvidence,
        render_inputs: PromptRenderInputs | None = None,
    ) -> tuple[VoteBallot, ...]:
        # Sequential collection: concurrent ballots on a single local GPU
        # inflate each call's wall-clock past vote_seconds (measured 0.71x
        # concurrency), so votes time out into default SKIP and nothing is
        # ever ejected. One-by-one keeps each call inside its deadline. Each
        # _collect_one_ballot retains its own deadline + default, and since
        # Task 10.9.1 its own parse fail-soft (a twice-failed ballot degrades
        # to a marked SKIP, PR #147 F1); only a provider/transport error
        # still propagates and fails the meeting.
        ballots: list[VoteBallot] = []
        for participant in participants:
            ballots.append(
                await self._collect_one_ballot(
                    trigger=trigger,
                    participant=participant,
                    participants=participants,
                    transcript=transcript,
                    contradictions=contradictions,
                    evidence=evidence,
                    render_inputs=render_inputs,
                )
            )
        return tuple(ballots)

    async def _collect_one_ballot(
        self,
        *,
        trigger: MeetingTrigger,
        participant: MeetingParticipant,
        participants: Sequence[MeetingParticipant],
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
        evidence: MeetingBeliefEvidence,
        render_inputs: PromptRenderInputs | None = None,
    ) -> VoteBallot:
        # Confirm the candidate set over the FINAL transcript: every living
        # participant except the voter is an eligible eject target (the same
        # ``_candidate_targets`` filter the turn prompts use for their
        # living-roster accusation list -- Task 9.9).
        candidate_targets = _candidate_targets(
            (other.agent_id for other in participants),
            exclude=participant.agent_id,
        )
        # Task 15.5 reporter exculpation -- UNCONDITIONAL since the Task-15.7
        # baseline-3 record (it was default-OFF at 15.5; graduated once
        # baseline 3 adopted it). The reporter is the body-report meeting's
        # opener (``trigger.triggered_by``, the reporter identity already at
        # meeting scope -- not re-derived from the transcript); an emergency
        # call has no body-reporter, so the exculpation never applies there.
        # The belief fold receives the reporter for a body report and caps
        # any soft lift landing on them; the render annotation is THREADED
        # for that same ballot, and whether it renders is the serving
        # template's call (only the reporter-aware ``qwen3_32b`` v6 /
        # ``qwen3_6_27b`` ballots read ``reporter_id``). An emergency call
        # (``None`` reporter) arms neither half -- no fold cap, no threaded
        # annotation. A body report arms both, though each can be inert (no
        # soft lift to cap; a reporter-unaware template).
        reporter_id = (
            trigger.triggered_by if not _trigger_is_emergency(trigger) else None
        )
        render_reporter = reporter_id
        # Belief Rule 2 (DESIGN.md §6.3): a detected contradiction lifts the
        # contradicted subject's suspicion in this voter's graph before the
        # ballot prompt renders, so the vote sees the detected lie reflected
        # in its suspicion prior -- not just in the raw flag list. The
        # pre-vote half of the meeting fold (Task 10.7) is applied to the
        # same graph in the same reconstruction, so the rendered graph AND
        # the in-template §4.6 verdict read one post-fold state source.
        # Engine state is never touched.
        suspicion_graph = _suspicion_graph_with_contradictions(
            voter_id=participant.agent_id,
            suspicion_graph=participant.suspicion_graph,
            contradictions=contradictions,
            fellow_impostor_ids=participant.fellow_impostor_ids,
            evidence=evidence,
            # The transcript carries the self-refuted-alibi signal for the
            # evidence-quality downgrade (derived inside the fold).
            transcript=transcript,
            # The body-report reporter, damped in the pre-vote fold whenever it
            # is non-None.
            reporter=reporter_id,
        )
        # Task 13.5.5: when the unfreeze hook is attached (unconditionally by
        # the orchestrator since Task 14.9), re-render
        # the ballot's memory with the pre-vote-folded ``suspicion_graph``
        # numbers substituted into the belief lines, so the belief-line
        # suspicion and the ``suspicion_graph`` kwarg below read ONE folded
        # source (the PR #198 review inconsistency, resolved by construction).
        # A hook-less participant (a direct-construction test/tooling caller)
        # keeps the frozen open-tick render.
        if participant.rerender_memory is not None:
            suspicion_override = {
                entry.player_id: entry.suspicion for entry in suspicion_graph
            }
            rendered_memory = participant.rerender_memory(suspicion_override)
        else:
            rendered_memory = participant.rendered_memory
        prompt = self._vote_prompt(
            voter_id=participant.agent_id,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradiction_flags=contradictions,
            suspicion_graph=suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=self._config.skip_confidence_threshold,
            fellow_impostor_ids=participant.fellow_impostor_ids,
            # Names the reporter + states the base rate. The kwarg is THREADED
            # for every body report (``None`` only for an emergency call, which
            # has no reporter); whether an annotation RENDERS is the serving
            # template's call -- only the reporter-aware ballots reference
            # ``reporter_id`` (``qwen3_32b`` v6, where the 15.5 bump landed,
            # and ``qwen3_6_27b``); the other sets ignore the kwarg.
            reporter_id=render_reporter,
            # Task 16.3 inert widenings (rendered by 16.16 / 16.15). ``persona``
            # is the participant's inert persona slot; ``suspicion_provenance``
            # is the SAME post-fold rows passed as ``suspicion_graph`` above (one
            # folded source by construction, the render-after-fold consistency
            # pin), so 16.15's surface decomposes exactly the scalars this ballot
            # already shows. ``""`` / ``()`` render byte-identical today.
            persona=participant.persona,
            suspicion_provenance=suspicion_graph,
            render_inputs=render_inputs,
        )
        # The in-prompt §4.6 verdict max, recomputed bit-for-bit from the SAME
        # graph + candidate set the template rendered (max suspicion over the
        # living ejection targets, default 0.0 -- the identical derivation
        # :func:`guard_ballot_target_graph` and ``vote_ballot.j2`` apply). Rides
        # the surfaced default below (Task 10.12, audit H-H-2) so a defaulted
        # ballot -- whose vote call fails before the recording client logs this
        # prompt -- carries its true verdict into the failed_call row.
        #
        # Rounded to the SAME 2-decimal precision the ``vote_ballot.j2`` §4.6
        # line renders (``"%.2f"|format``) and that
        # ``eval._suspicion_parse.parse_rendered_max_suspicion`` recovers off a
        # SUCCESSFUL call: a near-threshold raw max (e.g. 0.596 renders/parses
        # as ``**0.60**``) must classify IDENTICALLY whether recovered from the
        # persisted field or a logged prompt, or the two telemetry surfaces
        # would split a defaulted ballot's verdict at the rounding boundary
        # (0.596 -> MUST-vote off the rendered 0.60, not raw-0.596 -> MUST-skip).
        rendered_vote_max = float(
            "%.2f"
            % max(
                (
                    entry.suspicion
                    for entry in suspicion_graph
                    if entry.player_id in candidate_targets
                ),
                default=0.0,
            )
        )
        # ``response`` must survive into the ValidationError handler below:
        # when the manager-side parse of a returned payload fails, the
        # unparseable bytes are ``response.text``; when ``complete()`` itself
        # raised (a REAL provider validates internally, before the recording
        # client can log the call), it stays ``None`` and the head comes off
        # the carried ``LLMCallFailure`` instead.
        response: LLMResponse | None = None
        try:
            response = await asyncio.wait_for(
                _isolate_provider_timeout(
                    self._llm_client.complete(
                        prompt=prompt,
                        schema=VoteBallot,
                        max_tokens=self._config.vote_max_tokens,
                        temperature=self._config.vote_temperature,
                        call_kind="meeting",
                        agent_id=participant.agent_id,
                    )
                ),
                timeout=self._config.deadlines.vote_seconds,
            )
            parsed = VoteBallot.model_validate_json(response.text)
        except asyncio.TimeoutError:
            # Deadline miss: surface the fired default so the orchestrator
            # records it (audit gp-2). Deadline-free headless recording never
            # reaches here -- a vote default with this trigger is an
            # interactive-mode wall-clock miss. This branch is byte-unchanged
            # by Task 10.9.1: same ``DefaultedCall``, same default ballot.
            self._defaulted_calls.append(
                DefaultedCall(
                    phase="vote",
                    agent_id=participant.agent_id,
                    trigger="deadline",
                    rendered_vote_max=rendered_vote_max,
                )
            )
            return _default_vote(voter=participant.agent_id)
        except ValidationError as exc:
            # Vote-ballot fail-soft (Task 10.9.1; PR #147 finding F1, the
            # seed-8 vote-truncation abort). A ballot that still fails schema
            # validation after the provider-level retry -- the cap-truncation
            # runaway class, accepted at ~1/50 -- degrades to the default
            # SKIP instead of aborting the game: the same discipline the turn
            # path has had since Task 7.10, mirrored at the seam where the
            # deadline catch sits. NO new retry and no cap change -- this is
            # a net. The degrade is a pure function of the failed response
            # (:func:`_vote_parse_default`), so replaying the same bytes
            # yields the same ballot. A provider/transport timeout is still
            # re-tagged ``LLMProviderError`` by ``_isolate_provider_timeout``
            # and propagates -- only the deadline + parse failures fail soft.
            # ``extract_parse_failure`` carries a REAL provider's burned
            # spend onto the surfaced default (it raised before the recording
            # client could log the call); it is ``None`` for the manager-side
            # parse of a returned payload, whose spend ``llm_calls`` already
            # holds -- no double-count (the turn-path convention, audit gp-2).
            failure = extract_parse_failure(exc)
            self._defaulted_calls.append(
                DefaultedCall(
                    phase="vote",
                    agent_id=participant.agent_id,
                    trigger="validation",
                    parse_failures=() if failure is None else (failure,),
                    rendered_vote_max=rendered_vote_max,
                )
            )
            unparseable = (
                response.text
                if response is not None
                else ("" if failure is None else failure.raw_response)
            )
            return _vote_parse_default(
                voter=participant.agent_id, raw_response=unparseable
            )
        # Defensive normalization: if the LLM hallucinates a target id that
        # is not in ``candidate_targets`` (and not ``"SKIP"``), ``_tally``
        # would otherwise count it as a real eject and could resolve to
        # ``EJECTED`` with a non-participant id. Replace the target with
        # ``"SKIP"`` and mark the rationale so the original (bad) target is
        # preserved for audit / replay.
        normalized = _normalize_ballot_target(
            ballot=parsed, candidate_targets=candidate_targets
        )
        # primary_reason_id integrity (DESIGN.md §5.5; audit gp-3): the id is
        # the only mechanical deliberation->vote link, so a dangling id
        # silently zeroes the ballot-follows-chain instrument. Validate it
        # against THIS meeting's turn-id set -- a recoverable ``:turn-{k}``
        # suffix form normalizes to the canonical id, anything else is nulled
        # with an audit marker. The valid-id set is built once from the final
        # transcript (cheap; the chain is a handful of turns).
        valid_reason_ids = frozenset(turn.turn_id for turn in transcript.turns)
        reason_id_by_ordinal = {
            turn.turn_index: turn.turn_id for turn in transcript.turns
        }
        normalized = _normalize_ballot_reason_id(
            ballot=normalized,
            valid_reason_ids=valid_reason_ids,
            reason_id_by_ordinal=reason_id_by_ordinal,
        )
        # primary_reason_observation_id integrity (Task 16.5, C8): the private
        # citation channel names a stable episodic id from the voter's OWN
        # memory, so a hallucinated id must not corrupt the instrument.
        # Validate against the voter's typed valid-id set read DIRECTLY off
        # the participant (no per-speaker Mapping like the vent channel's --
        # the ballot validator needs only THIS voter's own set, not every
        # speaker's). Out-of-set -> nulled with an audit marker; never
        # guessed. The validated field's one consumer is the Task 16.6
        # citation gate at the END of this chain (unconditional since the
        # Task-16.17 baseline-5 record; default-OFF at 16.6): a nulled
        # fabrication gates exactly like a bare null.
        normalized = _normalize_ballot_observation_id(
            ballot=normalized,
            valid_observation_ids=frozenset(participant.observation_ids),
        )
        # Teammate firewall guard (Task 7.12): a teammate is a *valid* living
        # candidate, so the invalid-target normalization above never catches
        # it. Coerce a ballot that targets a fellow impostor to SKIP so an
        # impostor can never supply the betrayal vote that ejects a teammate.
        # Deterministic, no RNG, and a no-op for a crewmate / sole impostor.
        # ``model_rationale_text`` (Task 19.15) is the trusted provenance
        # boundary for the coercion's rationale redaction: ``parsed`` is the
        # ballot as the model returned it, so everything the chain has
        # prepended since is this codebase's own audit text and is preserved,
        # while the model's body -- which can name a teammate outright -- is
        # replaced. Splitting on marker SHAPE instead would let a rationale
        # that opens with marker-shaped prose smuggle that payload through.
        normalized = coerce_teammate_ballot_to_skip(
            ballot=normalized,
            fellow_impostor_ids=participant.fellow_impostor_ids,
            model_rationale_text=parsed.rationale_text,
        )
        # Ballot-target graph guard (Task 10.9.2; PR #147 F2): an eject
        # ballot under a MUST-vote verdict must name a target whose
        # rendered suspicion meets the threshold, or it is redirected to
        # the argmax-rendered eligible candidate (SKIP-coerced when only a
        # teammate row is over the gate). The verdict is recomputed from
        # the SAME ``suspicion_graph`` / ``candidate_targets`` /
        # ``skip_confidence_threshold`` passed to the prompt renderer
        # above, so guard and in-prompt §4.6 verdict read one source. Runs
        # LAST among the target-shaping guards -- after roster
        # normalization and the §7.12 coercion -- so it only sees valid
        # living non-teammate targets and can never create a betrayal
        # ballot for the firewall to re-coerce; only the post-redirect
        # citation gate below runs after it.
        normalized = guard_ballot_target_graph(
            ballot=normalized,
            voter_id=participant.agent_id,
            suspicion_graph=suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=self._config.skip_confidence_threshold,
            fellow_impostor_ids=participant.fellow_impostor_ids,
        )
        # Citation gate (Task 16.6, J2; planning doc §3.4): a zero-flag EJECT
        # ballot -- its target carries no contradiction flag among THIS
        # meeting's detected ``contradictions`` -- that cites neither a
        # transcript turn (``primary_reason_id``) nor a private observation
        # (``primary_reason_observation_id``, the 16.5 path) coerces to SKIP
        # with :data:`UNCITED_ZERO_FLAG_EJECT_MARKER` -- mark-and-coerce,
        # never a crash, never a re-prompt. The POST-REDIRECT slot is the
        # contract: a redirected ballot is judged on the REDIRECTED target's
        # flag status, not the original's.
        normalized = guard_ballot_citation(
            ballot=normalized,
            contradictions=contradictions,
        )
        return normalized.model_copy(update={"voter": participant.agent_id})

    # -- Resolution -------------------------------------------------------

    def _tally(
        self,
        ballots: Sequence[VoteBallot],
    ) -> tuple[MeetingOutcome, PlayerId | None]:
        """Resolve the meeting via :func:`meetings.voting.tally_ballots`.

        The ejection rule (DESIGN.md §5.2 + §4.6 + §5.5 -- ``SKIP`` as a
        first-class tally target, tie -> skip, the inclusive confidence
        cutoff) has ONE implementation as of 2026-08-16 (Task 19.26). This
        method is the call site the meeting protocol resolves through; the
        rule itself lives in :mod:`meetings.voting`, the canonical home the
        module named for it at Task 3.10. See
        :func:`meetings.voting.tally_ballots` for the full resolution rules.

        Before the consolidation the manager carried its own private copy
        (Task 3.8) and the two bodies were held equal by a paragraph in
        ``meetings/voting.py`` -- audits/audit-phase-19-triage.md §7 item 27.
        ``tests/meetings/test_vote_tally_parity.py`` ran both over every
        committed meeting's recorded ballots (707 meetings / 3,934 ballots,
        all four committed sets) plus synthetic edge fixtures and found zero
        disagreements; it now pins this delegation and the recorded outcomes.

        The threshold is :attr:`MeetingConfig.skip_confidence_threshold`,
        validated in ``[0, 1]`` by :meth:`__init__` on a frozen config.
        ``tally_ballots`` re-validates it per call -- redundant here (a
        constructed manager cannot carry an out-of-range threshold), which is
        precisely why the delegation is behaviour-preserving.
        """

        return tally_ballots(
            ballots,
            skip_confidence_threshold=self._config.skip_confidence_threshold,
        )

    @staticmethod
    def _validate_participants(
        participants: Sequence[MeetingParticipant],
        *,
        trigger: MeetingTrigger,
    ) -> None:
        seen: set[PlayerId] = set()
        for participant in participants:
            if participant.agent_id in seen:
                raise ValueError(
                    "MeetingManager.run participants must have unique agent_ids; "
                    f"duplicate: {participant.agent_id!r}"
                )
            seen.add(participant.agent_id)
            # ``MeetingParticipant`` is a runtime dataclass; the ``Role``
            # ``Literal`` is enforced by mypy --strict at the call site but
            # not at runtime. A typo like ``"impostor"`` would otherwise fall
            # through the ``role == "IMPOSTOR"`` check in
            # ``_render_turn_prompt`` and silently route the agent to the
            # crewmate prompt. Fail-loud at entry.
            if participant.role not in _VALID_ROLES:
                raise ValueError(
                    "MeetingParticipant.role must be one of "
                    f"{sorted(_VALID_ROLES)}; got {participant.role!r} "
                    f"for agent {participant.agent_id!r}"
                )
            # Task 7.12 firewall (mirrors the 7.2 crew-empty invariant):
            # ``fellow_impostor_ids`` is impostor-only self-channel data, and
            # the manager runs no leak scanner of its own before threading it
            # into the shared turn / vote prompts. A non-impostor carrying a
            # non-empty teammate list would render the teammate block into a
            # crewmate's prompt, leaking impostor identities outside the self
            # channel. Fail loud rather than leak (AGENTS.md "no silent
            # fallbacks").
            if participant.role != "IMPOSTOR" and participant.fellow_impostor_ids:
                raise ValueError(
                    "MeetingParticipant.fellow_impostor_ids must be empty for a "
                    f"non-impostor; got {participant.fellow_impostor_ids!r} for "
                    f"{participant.role!r} agent {participant.agent_id!r} "
                    "(teammate identity is impostor-only self-channel data)"
                )
        # The protocol opens with the reporter (DESIGN.md §5.2 PHASE 1). A
        # trigger whose ``triggered_by`` is not in the participant set is an
        # upstream orchestrator bug -- not something to silently demote.
        # Failing loud here surfaces the wiring error at meeting entry,
        # before any LLM traffic is spent (AGENTS.md "no silent fallbacks").
        if trigger.triggered_by not in seen:
            raise ValueError(
                f"MeetingTrigger.triggered_by={trigger.triggered_by!r} is not in "
                f"the participant set ({sorted(seen)}); the protocol requires "
                "the opener to be a living participant"
            )


def _opt_in_eligible_ids(
    *,
    transcript: MeetingTranscript,
    spoken: frozenset[PlayerId],
    living_ids: frozenset[PlayerId],
) -> tuple[PlayerId, ...]:
    """Living non-speakers with a relevant observation (DESIGN.md §5.2 PHASE 3).

    The "relevant observation" gate is a deterministic co-presence check
    against the body and the accused, computed purely from the recorded
    turns (so it is replay-stable and needs no extra LLM call): a living
    non-speaker is eligible iff the public ``saw_player`` observations
    place them co-present with the body's room or with a player who was
    accused during the meeting. Co-presence is symmetric -- "p was seen
    near the body / with the accused" means p holds a relevant
    first-hand observation -- so the transcript is a sufficient, leak-safe
    source for the gate. Returned in ascending player-id order (DESIGN.md
    §5.2 PHASE 3 "in player-id order").

    Task 15.4: a spoken ``saw_vent`` observation is a relevance source in
    exactly the co-presence gate's terms -- its room is a scene (like the
    body's room: a non-speaker placed there holds first-hand context worth
    voicing), and its subject is implicated testimony-side (like an accused:
    a sighting of them is relevant). A vent observation also places its OWN
    subject at the vent scene, so an unspoken subject becomes eligible to
    answer the incrimination, mirroring how a ``saw_player`` at the body
    room makes its subject eligible today. The VENT-scene prong compares
    CANONICAL room sets (:func:`meetings.transcript.canonical_rooms` -- the
    same normalisation the grounding chokepoint applies, so a compound
    spoken label like ``"LABS/MEDBAY"`` still places a ``MEDBAY`` sighting
    at the scene, and a non-spatial label locates nothing); the body-room
    prong keeps its standing raw comparison byte-identically.
    """

    body_rooms = {
        observation.room
        for turn in transcript.turns
        for observation in turn.observations
        if isinstance(observation, FoundBodyObservation)
    }
    vent_scene_rooms: frozenset[str] = frozenset()
    for turn in transcript.turns:
        for observation in turn.observations:
            if isinstance(observation, SawVentObservation):
                vent_scene_rooms |= canonical_rooms(observation.room)
    accused: set[PlayerId] = set()
    for turn in transcript.turns:
        target = accusation_target(turn)
        if target is not None:
            accused.add(target)

    relevant: set[PlayerId] = set()
    for turn in transcript.turns:
        for observation in turn.observations:
            if isinstance(observation, SawPlayerObservation):
                group = {observation.subject, *observation.co_present}
            elif isinstance(observation, SawVentObservation):
                group = {observation.subject}
            else:
                continue
            at_scene = observation.room in body_rooms or bool(
                canonical_rooms(observation.room) & vent_scene_rooms
            )
            if at_scene or observation.subject in accused or (group & accused):
                relevant |= group

    return tuple(
        player_id
        for player_id in sorted(living_ids)
        if player_id not in spoken and player_id in relevant
    )


def _joint_capped_suspicion(*, prior: float, lifted: float) -> float:
    """Bound a subject's combined transient meeting lift (Task 13.14).

    The vote-time graph applies TWO upward suspicion channels in sequence on
    the same reconstructed state -- belief Rule 2's contradiction lift
    (:func:`agents.memory.beliefs.apply_contradiction_rule`, capped per
    subject at
    :data:`~agents.memory.beliefs.MEETING_CONTRADICTION_LIFT_CAP`) and the
    Task 13.7 pre-vote testimony spread
    (:func:`~agents.memory.beliefs.apply_meeting_evidence_rules`, graduated
    +0.05 / +0.12 / +0.15). Those two caps are INDEPENDENT, so before this
    joint cap a subject both lone-STRONG-flagged -- Task 13.14 promotes a
    single-witness ``alibi_vs_sighting`` to the full
    :data:`~agents.memory.beliefs.CONTRADICTION_SUSPICION_DELTA` -- AND named
    by two+ accusers stacked to 0.5 + 0.3 + 0.12 = 0.92 rendered into the
    ballot, and the spread is itself a per-listener convergence mechanism
    that amplifies exactly the crew false-positive convergence the
    LONE-STRONG decision must bound (audit-2026-06-22-2149 Blocking #3).

    This caps the COMBINED upward lift per subject at one strong flag's worth
    -- the same ``MEETING_CONTRADICTION_LIFT_CAP`` bound -- above the
    subject's pre-fold prior, so a single STRONG contradiction still crosses
    the §4.6 gate (0.5 -> 0.80, the owner LONE-STRONG outcome) while the
    spread can no longer push it past the bound. Only the UPWARD direction is
    bounded: a corroboration that lowers suspicion below the prior leaves
    ``lifted`` under the cap, so the ``min`` is a no-op for it. The bound is
    relative to the prior (mirroring the Rule-2 lift cap), so an accumulated
    cross-round prior is preserved rather than flattened. Pure function of
    its two scalar arguments -- replay-stable.
    """

    return min(lifted, prior + MEETING_CONTRADICTION_LIFT_CAP)


def _provenance_from_entry(entry: SuspicionEntry) -> SuspicionProvenance:
    """Rebuild a :class:`SuspicionProvenance` from a graph row's eight fields.

    Task 16.3: the render-contract leaf mirrors
    :class:`agents.memory.beliefs.SuspicionProvenance` field-by-name (it cannot
    import ``agents.*``), so the manager reconstitutes the decomposition here to
    reseed the reconstructed :class:`BeliefState` -- the seed carries the incoming
    decomposition, and :meth:`BeliefState.seed_player` reconciles any residual
    against the scalar into ``unattributed`` so the sum invariant holds on the
    seed regardless of the caller's (scalar, decomposition) consistency. Pure.
    """

    return SuspicionProvenance(
        flag_lift=entry.flag_lift,
        body_proximity=entry.body_proximity,
        kill_or_vent_pin=entry.kill_or_vent_pin,
        testimony_spread=entry.testimony_spread,
        accusation_carry=entry.accusation_carry,
        carried_hard=entry.carried_hard,
        carried_soft=entry.carried_soft,
        unattributed=entry.unattributed,
    )


def _capped_provenance(
    *,
    seeded: SuspicionProvenance,
    updated: SuspicionProvenance,
    prior: float,
    lifted: float,
    capped: float,
) -> SuspicionProvenance:
    """Attribute the :func:`_joint_capped_suspicion` reduction to this-call lift.

    Task 16.3, the render-after-fold provenance pin. The joint cap (Task 13.14)
    bounds the COMBINED transient meeting lift a subject accrues THIS call
    (contradiction lift + testimony spread) above the seeded ``prior``; when it
    binds it lowers only the transient lift, never the carried prior. So the
    emitted decomposition scales the per-component this-call DELTA
    (``updated - seeded``) by the realized ``(capped - prior) / (lifted - prior)``
    and adds it back onto the seeded components -- the seeded carry buckets ride
    through untouched (their delta is zero: the pre-vote fold never rolls), which
    is exactly "the cap bounds the lift, not the prior".

    The scaling preserves the sum invariant on the emitted row: the seeded total
    is ``prior - 0.5`` and the scaled delta total is ``capped - prior``, so
    ``0.5 + emitted.total == capped`` (the scalar the entry carries) to within
    :data:`~agents.memory.beliefs.SUSPICION_PROVENANCE_ATOL`. When the cap does
    not bind (``capped == lifted``) or nothing moved (``lifted == prior``, where
    ``capped == lifted`` too since the cap adds a non-negative bound), the
    post-rule provenance already sums to the scalar, so it is emitted as-is. Pure.
    """

    if capped == lifted or lifted == prior:
        return updated
    factor = (capped - prior) / (lifted - prior)
    return SuspicionProvenance(
        flag_lift=seeded.flag_lift + (updated.flag_lift - seeded.flag_lift) * factor,
        body_proximity=(
            seeded.body_proximity
            + (updated.body_proximity - seeded.body_proximity) * factor
        ),
        kill_or_vent_pin=(
            seeded.kill_or_vent_pin
            + (updated.kill_or_vent_pin - seeded.kill_or_vent_pin) * factor
        ),
        testimony_spread=(
            seeded.testimony_spread
            + (updated.testimony_spread - seeded.testimony_spread) * factor
        ),
        accusation_carry=(
            seeded.accusation_carry
            + (updated.accusation_carry - seeded.accusation_carry) * factor
        ),
        carried_hard=(
            seeded.carried_hard + (updated.carried_hard - seeded.carried_hard) * factor
        ),
        carried_soft=(
            seeded.carried_soft + (updated.carried_soft - seeded.carried_soft) * factor
        ),
        unattributed=(
            seeded.unattributed + (updated.unattributed - seeded.unattributed) * factor
        ),
    )


def _suspicion_graph_with_contradictions(
    *,
    voter_id: PlayerId,
    suspicion_graph: tuple[SuspicionEntry, ...],
    contradictions: tuple[ContradictionRef, ...],
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    evidence: MeetingBeliefEvidence | None = None,
    transcript: MeetingTranscript | None = None,
    reporter: PlayerId | None = None,
) -> tuple[SuspicionEntry, ...]:
    """Apply belief Rule 2 + the pre-vote fold to a voter's graph (§6.3, §4.6).

    Reconstructs an agents-side :class:`BeliefState` from the voter's
    incoming suspicion-graph snapshot, runs
    :func:`agents.memory.beliefs.apply_contradiction_rule` over the
    detected ``contradictions``, applies the PRE-VOTE half of the
    meeting fold (Task 10.7) when ``evidence`` carries one, and projects
    the result back into a sorted :class:`SuspicionEntry` tuple for the
    vote-ballot prompt.

    A contradicted / folded / corroborated subject the voter had no
    prior row for is added (the belief store materialises a default 0.5
    prior before the delta). The voter never accrues suspicion about
    themselves.

    Pre-vote fold (Tasks 10.7, 10.15, 13.7; audit gp-2 and 2026-06-13 C-C-1).
    When ``evidence`` names ``pre_vote_folded`` (two-witness),
    ``pre_vote_informed`` (single-witness inform,
    :data:`agents.memory.beliefs.WITNESS_INFORM_REASON`), or
    ``corroborated`` subjects, the same reconstructed state takes
    :func:`agents.memory.beliefs.apply_meeting_evidence_rules` with
    ``phase="pre_vote"`` AFTER the Rule-2 lift: the testimony bumps and this
    meeting's relevance-gated -0.05 corroborations land on the graph the
    ballot prompt renders -- and because the frozen vote template computes
    the §4.6 verdict from that same rendered graph, the graph and the verdict
    read ONE post-fold state source by construction (the render-after-fold
    consistency pin; a freshly-informed MUST-vote ballot is therefore NOT
    a threshold inversion -- the gate rule is untouched, only the rendered
    prior moved). The testimony bump is GRADUATED by the
    ``pre_vote_voice_counts`` COUNT (Task 13.7): a single voice keeps the
    +0.05 inform, two corroborating voices lift +0.12 (the first §4.6
    gate-cross), three+ cap at +0.15. Crucially this graduated lift is
    TRANSIENT: the post-meeting persistent absorb
    (``orchestrator.game._absorb_meeting_beliefs``) passes NO counts, so only
    the flat +0.05/-0.05 deltas carry across the meeting boundary -- a
    gate-crossing two-voice ballot prior never railroads the next round.
    When the evidence folds nothing (no voiced subject, no relevance-gated
    corroboration), this path is byte-identical to the pre-10.7 behaviour
    -- the channel is invisible until a witness speaks.

    Team-internal firewall (Task 9.3, DESIGN.md §4.7), the deterministic
    voter-side backstop that mirrors the 7.12 ballot coercion on the input
    side: an impostor voter's graph carries NO edge against a fellow
    impostor. A teammate id in ``fellow_impostor_ids`` is dropped from the
    projected graph in BOTH paths -- so even if a teammate-incriminating
    sighting slipped through perception/render and a contradiction lifted
    the teammate, the impostor's ballot prompt still shows no team
    suspicion -- and the pre-vote fold call carries the same
    ``fellow_impostor_ids``, so its input-side guard drops a teammate
    from the testimony bump as well (the 10.7 teammate guard on the new
    channel). The list is ``()`` for every crewmate and a sole impostor,
    where this is a no-op: with no contradictions, no fold, and no
    teammates the incoming graph is returned unchanged, so the crew /
    no-flag path is byte-identical (a precondition for replay stability).

    Evidence-quality lift (Task 14.10; audit 2026-07-01 §3a). ``transcript``
    is the data channel for the fold's self-refuted-alibi downgrade:
    :func:`agents.memory.beliefs.apply_contradiction_rule` derives the
    self-refutation signal from it at fold time
    (:func:`meetings.transcript.self_refuted_alibi_claim_ids`), so a
    contradiction fold ALWAYS requires the transcript: folding
    contradictions WITHOUT one fails loud below (PR #217 review) -- the graph
    would otherwise silently skip the self-refuted-alibi downgrade and render
    values the run's stamped substrate says cannot exist (AGENTS.md "no silent
    fallbacks"). A contradiction-free fold may still pass ``None``.

    Reporter exculpation (Task 15.5) -- UNCONDITIONAL since the Task-15.7
    baseline-3 record (it was default-OFF at 15.5; graduated once baseline 3
    adopted it). ``reporter`` is the body-report meeting's own reporter
    (``None`` for an emergency call), passed straight into the pre-vote
    :func:`agents.memory.beliefs.apply_meeting_evidence_rules` fold, which caps
    the reporter's soft accusation lift so proximity-at-discovery no longer
    reads as guilt. The cap bites only when soft lift actually lands on the
    reporter this meeting (an accusation-spread or absence delta); a reporter
    taking no soft lift -- and the ``None`` reporter of an emergency call --
    leaves this path untouched.

    Absence prior. ``evidence.absent`` -- the living roster minus the players
    public testimony placed (:func:`meetings.transcript.absent_players`) -- is
    threaded into the same pre-vote fold, where each absent subject takes the
    TRANSIENT :data:`agents.memory.beliefs.ABSENCE_SUSPICION_DELTA`. The lift
    composes through the fold's existing ceilings AND this function's joint cap
    below -- absence + a strong flag caps at ``prior + 0.30`` like every other
    stack -- and it moves suspicion only (no :class:`ContradictionRef` is
    minted), so the citation gate's zero-flag boundary never sees it. An
    absence-only meeting with a non-empty absent set therefore enters the fold
    path; an EMPTY absent set stays a no-op.
    """

    # Task 14.10 fail-loud seam guard (PR #217 review; unconditional since the
    # 14.12 close): every contradiction fold must carry the transcript the
    # downgrade signal is derived from. This also hardens the production seam --
    # a refactor that drops the ``_collect_one_ballot`` threading now raises on
    # the first flagged ballot instead of silently shipping bound 2
    # half-implemented.
    if contradictions and transcript is None:
        raise ValueError(
            "a contradiction fold was requested without the meeting "
            "transcript; thread the recorded transcript (the evidence-quality "
            "self-refuted-alibi downgrade -- unconditional since the Task-14.12 "
            "close -- is derived from it at fold time)"
        )

    teammates = frozenset(fellow_impostor_ids)
    # A meeting whose ONLY pre-vote evidence is a non-empty absent set still
    # takes the fold path: the absence delta is the evidence.
    folds = evidence is not None and bool(
        evidence.pre_vote_folded
        or evidence.pre_vote_informed
        or evidence.corroborated
        or evidence.absent
    )

    if not contradictions and not folds:
        if not teammates:
            return suspicion_graph
        return tuple(
            entry for entry in suspicion_graph if entry.player_id not in teammates
        )

    beliefs = BeliefState()
    for entry in suspicion_graph:
        # Task 16.3: seed the incoming decomposition alongside the scalar so the
        # projected rows carry provenance through the pre-vote fold (the fold's
        # own writes then accumulate onto it via their source tags). Scalar
        # arithmetic is byte-identical -- the scalar assigned is the same clamp.
        beliefs.seed_player(
            entry.player_id,
            suspicion=entry.suspicion,
            trust=entry.trust,
            provenance=_provenance_from_entry(entry),
        )
    updated = apply_contradiction_rule(beliefs, contradictions, transcript=transcript)
    if folds and evidence is not None:
        updated = apply_meeting_evidence_rules(
            updated,
            own_id=voter_id,
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
            fellow_impostor_ids=fellow_impostor_ids,
            phase="pre_vote",
            pre_vote_folded=frozenset(evidence.pre_vote_folded),
            pre_vote_informed=frozenset(evidence.pre_vote_informed),
            # Task 13.7: graduate the transient pre-vote bump by the voice
            # COUNT (2 -> +0.12, 3+ -> +0.15). The counts ride the meeting
            # context only; the post-meeting persistent absorb passes none, so
            # only the flat +0.05 carries across rounds.
            pre_vote_voice_counts=dict(evidence.pre_vote_voice_counts),
            # Task 15.5: the body-report meeting's reporter (or None for an
            # emergency / non-vote-time call). The fold reads the
            # reporter_exculpation resolver -- unconditional since the
            # Task-15.7 record (default-OFF at 15.5) -- and caps any soft
            # lift landing on a passed reporter; ``None``, or a reporter
            # taking no soft lift this meeting, is inert.
            reporter=reporter,
            # The publicly-unplaced set, taking the TRANSIENT absence delta.
            # Like the voice counts, it rides the meeting context only -- the
            # persistent absorb never passes it, so only this vote-time graph
            # ever sees the lift.
            absent=frozenset(evidence.absent),
        )

    entries: list[SuspicionEntry] = []
    for player_id in sorted(updated.known_players()):
        if player_id == voter_id or player_id in teammates:
            continue
        belief = updated.view(player_id)
        # Task 13.14 joint cap: ``beliefs`` still holds the pre-rule seeded
        # prior (both rules above are pure and return new states; ``copy``
        # deep-copies), so a subject the rules materialised reads the default
        # 0.5. Bound the COMBINED contradiction-lift + testimony-spread above
        # that prior so a lone-STRONG-flagged + multi-accused subject cannot
        # stack past one strong flag's worth (0.92 -> capped at 0.80).
        prior = beliefs.view(player_id).suspicion
        capped = _joint_capped_suspicion(
            prior=prior,
            lifted=belief.suspicion,
        )
        # Task 16.3: emit the source-tagged decomposition alongside the capped
        # scalar. The cap reduction (when it binds) is attributed to THIS call's
        # transient lift -- the seeded carry prior is never re-scaled -- so
        # ``0.5 + sum(the eight fields) == capped`` holds on every emitted row.
        emitted = _capped_provenance(
            seeded=beliefs.view(player_id).provenance,
            updated=belief.provenance,
            prior=prior,
            lifted=belief.suspicion,
            capped=capped,
        )
        entries.append(
            SuspicionEntry(
                player_id=player_id,
                suspicion=capped,
                trust=belief.trust,
                flag_lift=emitted.flag_lift,
                body_proximity=emitted.body_proximity,
                kill_or_vent_pin=emitted.kill_or_vent_pin,
                testimony_spread=emitted.testimony_spread,
                accusation_carry=emitted.accusation_carry,
                carried_hard=emitted.carried_hard,
                carried_soft=emitted.carried_soft,
                unattributed=emitted.unattributed,
            )
        )
    return tuple(entries)


def _turn_id(*, meeting_id: str, turn_index: int) -> str:
    """The canonical turn id ``"{meeting_id}:turn-{turn_index}"`` (DESIGN.md §5.2).

    Keyed on the turn ordinal, not the speaker, so it is unique even when
    a player speaks twice; :attr:`VoteBallot.primary_reason_id` references
    it.
    """

    return f"{meeting_id}:turn-{turn_index}"


def _default_turn(
    *,
    turn_id: str,
    turn_index: int,
    speaker: PlayerId,
    turn_kind: TurnKind,
    reply_to: str | None,
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=turn_id,
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,
        reply_to=reply_to,
        observations=(),
        claims=(),
        free_text=DEFAULT_TURN_FREE_TEXT,
    )


def _default_vote(*, voter: PlayerId) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=_SKIP_TARGET,
        confidence=0.0,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=DEFAULT_VOTE_RATIONALE,
    )


def _vote_parse_default(*, voter: PlayerId, raw_response: str) -> VoteBallot:
    """Degraded SKIP ballot for a twice-failed ballot completion (Task 10.9.1).

    Reuses the :func:`_default_vote` shape (target ``SKIP``, confidence
    ``0.0``, no reason id -- the tally can never eject off it) and records
    :data:`VOTE_PARSE_DEFAULT_MARKER` as the whole ``rationale_text``,
    quoting a bounded head of the unparseable response per the Task 10.6
    rule (:func:`_bounded_original`) so the seed-8 runaway class stays
    auditable without splicing the full blob into the ballot. A pure
    function of ``(voter, raw_response)`` -- no clock, no RNG, no state --
    so replaying the same recorded bytes yields the same ballot.
    """

    marker = VOTE_PARSE_DEFAULT_MARKER.format(head=_bounded_original(raw_response))
    return _default_vote(voter=voter).model_copy(update={"rationale_text": marker})


def _normalize_self_alibi_subjects(
    claims: tuple[Claim, ...],
    *,
    speaker_id: PlayerId,
) -> tuple[Claim, ...]:
    """Rewrite known self-alibi placeholder subjects to ``speaker_id``.

    The model occasionally emits ``subject: "self"`` or ``"p-self"`` in an
    :class:`~meetings.schemas.AlibiClaim`, leaking a prompt-template /
    few-shot placeholder into the structured ``subject`` field (Task 3.20).
    Those claims are unambiguously the speaker's own self-alibi; this
    rewrites their ``subject`` to the speaker's canonical player id so
    DESIGN.md §5.4 contradiction detection -- which indexes alibis by
    ``(subject, tick_range, location)`` -- can match them against other
    speakers' claims. The full placeholder set is
    :data:`_SELF_ALIBI_PLACEHOLDERS`.

    A ``subject`` that is NOT in the placeholder set is passed through
    unchanged; this helper deliberately does not validate ``subject``
    against the meeting's roster (an unknown subject simply fails to match
    in contradiction detection, no worse than today). Only
    :class:`~meetings.schemas.AlibiClaim`s are inspected; accusation /
    corroboration claims are returned as-is.
    """

    normalized: list[Claim] = []
    for claim in claims:
        if isinstance(claim, AlibiClaim) and claim.subject in _SELF_ALIBI_PLACEHOLDERS:
            normalized.append(claim.model_copy(update={"subject": speaker_id}))
        else:
            normalized.append(claim)
    return tuple(normalized)


@dataclass(frozen=True)
class _PositionlessOpening:
    """An opening attempt that parsed but took no position (Task 10.6).

    The unsure-degrade source: the model's structured output survived the
    guards but its recorded claims carry no accusation and its free_text
    no "unsure" declaration -- the seed-12/seed-48 shape, where the only
    accusation named a dead player and the chokepoint dropped it. The
    fields are the post-guard artifacts exactly as the success path would
    have recorded them, so the degraded turn loses ONLY the invalid
    position, never the body report.
    """

    observations: tuple[ObservationClaim, ...]
    claims: tuple[Claim, ...]
    free_text: str
    annotations: tuple[TurnAnnotation, ...]


def _opening_retry_feedback(*, dropped_targets: tuple[PlayerId, ...]) -> str:
    """The Task 10.6 feedback block appended to an opening retry prompt.

    States the failure reason -- the dead-target form names every dropped
    accusation target (bounded, deduplicated, in claim order) and the
    no-position form covers pure narration -- then demands a LIVING
    target or an explicit "unsure" (audit gp-5 H-H-1: a byte-identical
    retry at temp 0.4 is provably a no-op against this failure shape).
    """

    if dropped_targets:
        seen: set[PlayerId] = set()
        names: list[str] = []
        for target in dropped_targets:
            if target in seen:
                continue
            seen.add(target)
            names.append(repr(_bounded_original(target)))
        reason = OPENING_RETRY_FEEDBACK_DEAD_TARGET.format(targets=", ".join(names))
    else:
        reason = OPENING_RETRY_FEEDBACK_NO_POSITION
    return OPENING_RETRY_FEEDBACK_HEADER + reason + OPENING_RETRY_FEEDBACK_DEMAND


def _bounded_original(value: str) -> str:
    """Truncate a marker's quoted-original to the audit-safe bound (Task 10.6).

    Values at or under :data:`MARKER_QUOTED_ORIGINAL_MAX_CHARS` chars pass
    through verbatim (every real player id does); a longer value -- the
    seed-35 3499-char reasoning blob hallucinated as an alibi subject --
    keeps its head plus a literal ``"..."`` so the marker cannot balloon
    the recorded turn while the original stays identifiable.
    """

    if len(value) <= MARKER_QUOTED_ORIGINAL_MAX_CHARS:
        return value
    return value[:MARKER_QUOTED_ORIGINAL_MAX_CHARS] + MARKER_TRUNCATION_SUFFIX


def _opening_takes_position(
    *,
    claims: tuple[Claim, ...],
    observations: tuple[ObservationClaim, ...],
    free_text: str,
) -> bool:
    """True iff an opening turn commits to a position (DESIGN.md §5.2 PHASE 1).

    The opening must EITHER accuse one player OR declare "unsure"; a
    narration-only opening kills the reactive chain on turn 0 (Task 10.3,
    audit gp-9 H-H-1: 5 of 76 audited meetings opened without either and
    every one collapsed to a chain-length-1 SKIP). The check is a pure
    function of the turn content the manager is about to record:

    * ``claims`` are the POST-GUARD claims (teammate-firewalled and
      roster-validated), so an accusation that was dropped -- a dead-id
      target, a teammate -- does not count: the recorded turn would carry
      no accusation and the chain would still die.
    * ``free_text`` is the MODEL-AUTHORED text (``parsed.free_text``,
      before any drop markers are prefixed); the
      :data:`OPENING_UNSURE_MARKER` substring is matched
      case-insensitively, per the opening templates' instruction to write
      the word "unsure".

    The unsure declaration is gated on free_text STRUCTURE (Task 10.12, audit
    2026-06-13-1816 H-H-1): a bare substring match accepted a 5266-char
    reasoning-relocation husk (claims=[] observations=[], incidentally
    containing "unsure") as a deliberate position, so the 10.3 retry never
    fired (seed-30 m1). A declaration in the hollow relocation SHAPE --
    free_text far above the p95 (:data:`OPENING_UNSURE_MAX_FREE_TEXT_CHARS`)
    AND no surviving claims AND no observations -- is treated as no position
    and routed back through the retry / fail-soft; a SHORT genuine "unsure",
    or one carrying observations / claims, still passes.
    """

    if any(isinstance(claim, AccusationClaim) for claim in claims):
        return True
    if OPENING_UNSURE_MARKER not in free_text.lower():
        return False
    # An "unsure" buried in a reasoning-relocation husk is not a deliberate
    # declaration: reject the hollow shape (long free_text with nothing else)
    # to the retry. Any observations or surviving claims, or a short opening,
    # keep the declaration valid.
    is_hollow_relocation = (
        len(free_text) > OPENING_UNSURE_MAX_FREE_TEXT_CHARS
        and not claims
        and not observations
    )
    return not is_hollow_relocation


def _normalize_ballot_target(
    *,
    ballot: VoteBallot,
    candidate_targets: tuple[PlayerId, ...],
) -> VoteBallot:
    """Defensively normalize an LLM-produced ballot target.

    Returns the ballot unchanged when ``target`` is ``"SKIP"`` or in
    ``candidate_targets``. When the LLM hallucinates an unknown id, the
    ballot is rewritten to ``"SKIP"`` with a marker prefix on
    ``rationale_text`` preserving the original (invalid) target. The tally
    cannot then resolve to ``EJECTED`` against a non-participant id; the
    audit trail records what the LLM actually emitted.
    """

    if ballot.target == _SKIP_TARGET or ballot.target in candidate_targets:
        return ballot
    marker = INVALID_VOTE_TARGET_MARKER.format(target=ballot.target)
    return ballot.model_copy(
        update={
            "target": _SKIP_TARGET,
            "rationale_text": marker + ballot.rationale_text,
        }
    )


def _normalize_ballot_reason_id(
    *,
    ballot: VoteBallot,
    valid_reason_ids: frozenset[TurnId],
    reason_id_by_ordinal: Mapping[int, TurnId],
) -> VoteBallot:
    """Validate / normalize a ballot's ``primary_reason_id`` (DESIGN.md §5.5).

    ``primary_reason_id`` must reference a real ``turn_id`` from THIS
    meeting's transcript -- it is the only mechanical link from the
    deliberation chain to the vote, so a dangling id silently zeroes the
    ballot-follows-chain instrument (audit gp-3). Mirrors
    :func:`_normalize_ballot_target`:

    * ``None`` or an already-canonical id passes through unchanged.
    * A recoverable suffix form -- one whose trailing ``:turn-{k}`` ordinal
      exists in this meeting but whose meeting prefix is wrong (the 7B model
      echoes the bare ``m-1:turn-0`` instead of the long canonical
      ``{meeting_id}:turn-0``) -- normalizes to the canonical ``turn_id``
      for that ordinal.
    * Anything else (a hallucinated ordinal, the prompt's old hardcoded
      example, a malformed string) is nulled, never guessed, with
      :data:`INVALID_REASON_ID_MARKER` prefixed to ``rationale_text``.
    """

    reason_id = ballot.primary_reason_id
    if reason_id is None or reason_id in valid_reason_ids:
        return ballot
    match = _REASON_ID_TURN_SUFFIX.search(reason_id)
    if match is not None:
        canonical = reason_id_by_ordinal.get(int(match.group(1)))
        if canonical is not None:
            return ballot.model_copy(update={"primary_reason_id": canonical})
    marker = INVALID_REASON_ID_MARKER.format(reason_id=reason_id)
    return ballot.model_copy(
        update={
            "primary_reason_id": None,
            "rationale_text": marker + ballot.rationale_text,
        }
    )


def _normalize_ballot_observation_id(
    *,
    ballot: VoteBallot,
    valid_observation_ids: frozenset[ObservationId],
) -> VoteBallot:
    """Validate / normalize ``primary_reason_observation_id`` (Task 16.5, C8).

    ``primary_reason_observation_id`` is the private-hard-evidence citation
    channel (DESIGN.md §5.5, §6.6): a stable ``{agent_id}:{tick}:{seq}``
    episodic id the voter cites for evidence NOBODY spoke (a witnessed
    kill/vent held first-hand). It must name a real observation from the
    VOTER'S OWN memory, so it is validated against ``valid_observation_ids``
    -- the voter's own typed id set threaded onto
    :class:`MeetingParticipant`. Mirrors :func:`_normalize_ballot_reason_id`
    and NEVER raises:

    * ``None`` or a member of the set passes through unchanged.
    * Anything else is nulled with :data:`INVALID_OBSERVATION_ID_MARKER`
      prefixed to ``rationale_text``, preserving the original (invalid) id.

    Unlike the turn-id validator there is NO suffix-recovery branch: the
    ``:turn-{k}`` ordinal recovery is turn-id-specific (the 7B echo shape),
    and an observation id has no in-meeting ordinal table to recover
    against -- an unknown id is nulled, never guessed. The validated field's
    one consumer is the citation gate
    (:func:`guard_ballot_citation`): a nulled
    fabrication gates exactly like a bare null. The tally never reads it.
    """

    observation_id = ballot.primary_reason_observation_id
    if observation_id is None or observation_id in valid_observation_ids:
        return ballot
    marker = INVALID_OBSERVATION_ID_MARKER.format(observation_id=observation_id)
    return ballot.model_copy(
        update={
            "primary_reason_observation_id": None,
            "rationale_text": marker + ballot.rationale_text,
        }
    )


# ---------------------------------------------------------------------------
# Teammate firewall guard (Task 7.12).
#
# Meeting output is LLM-driven, so the fix is two layers: a prompt layer that
# tells an impostor who its teammates are (the ``.j2`` templates) and these
# deterministic guards that hard-exclude a teammate from the produced
# accusation / ballot regardless of what the model emits. Each helper is a
# pure function of ``fellow_impostor_ids`` with no RNG and no new LLM call,
# and is an exact no-op when ``fellow_impostor_ids`` is empty (every crewmate
# and a sole impostor), so replay reconstruction of the committed sets is
# unaffected. Shared by :class:`MeetingManager` (the production meeting path)
# and the strategic reasoner. In the reactive chain the accusation lives in a
# turn's ``claims`` (there is no separate ``Statement.target`` field), so
# :func:`exclude_teammate_accusation_claims` is the operative chain-safety
# guard and :func:`drop_teammate_statement_target` backstops the derived
# next-speaker target (:func:`_guard_teammate_turn_claims`).
# ---------------------------------------------------------------------------


def exclude_teammate_accusation_claims(
    claims: tuple[Claim, ...],
    *,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> tuple[Claim, ...]:
    """Drop every :class:`AccusationClaim` aimed at a fellow impostor.

    Returns ``claims`` unchanged when ``fellow_impostor_ids`` is empty
    (crewmate / sole impostor) so the no-coordination path is
    byte-identical. Only :class:`AccusationClaim`s are filtered: an
    :class:`AlibiClaim` for a teammate or a :class:`CorroborationClaim`
    supporting a teammate *helps* the team and is retained.
    """

    if not fellow_impostor_ids:
        return claims
    teammates = frozenset(fellow_impostor_ids)
    return tuple(
        claim
        for claim in claims
        if not (isinstance(claim, AccusationClaim) and claim.against in teammates)
    )


def exclude_teammate_vent_observations(
    observations: tuple[ObservationClaim, ...],
    *,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> tuple[ObservationClaim, ...]:
    """Drop every :class:`SawVentObservation` naming a fellow impostor (Task 15.4).

    The observation-side twin of :func:`exclude_teammate_accusation_claims`,
    made necessary by the same 7.12 doctrine the moment vents became
    speakable: a structured vent observation is role-PROVING incrimination
    (and, grounded, mints a STRONG ``vent_sighting`` flag), so without this
    guard 15.4 would open the first path by which an impostor's structured
    output can hard-flag its own teammate -- the render layer does NOT
    suppress a witnessed teammate vent (``_sighting_is_suppressed`` covers
    only kill-window sightings), so the elicitation can surface one. Returns
    ``observations`` unchanged when ``fellow_impostor_ids`` is empty (every
    crewmate and a sole impostor), so the no-coordination path is
    byte-identical; only vent observations are filtered -- the three existing
    observation kinds pass through untouched, exactly as the claims guard
    retains teammate alibis and corroborations.
    """

    if not fellow_impostor_ids:
        return observations
    teammates = frozenset(fellow_impostor_ids)
    return tuple(
        observation
        for observation in observations
        if not (
            isinstance(observation, SawVentObservation)
            and observation.subject in teammates
        )
    )


def drop_teammate_statement_target(
    target: PlayerId | None,
    *,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> PlayerId | None:
    """Null an accusation target that names a fellow impostor.

    Returns ``target`` unchanged when ``fellow_impostor_ids`` is empty or
    when ``target`` is not a teammate; a teammate-naming target degrades to
    ``None``. In the reactive chain this guards the derived next-speaker
    target (the floor never passes to a fellow impostor) -- a defensive
    backstop to :func:`exclude_teammate_accusation_claims`, which has
    already stripped the teammate accusation from the recorded claims.
    """

    if not fellow_impostor_ids or target is None:
        return target
    if target in fellow_impostor_ids:
        return None
    return target


# Every ballot marker interpolates its payload with ``{x!r}`` -- a Python repr
# of a string, hence always quoted -- so a marker's untrusted part is exactly
# its quoted literal. Matching a payload as a quoted literal (rather than
# scanning for the marker's static tail) stays correct when the payload itself
# contains that tail text. Mirrors ``api.replay_loader``'s
# ``_MARKER_REPR_VALUE``; the two cannot share an implementation because
# ``api`` imports ``meetings``, never the reverse.
#
# This pattern is applied ONLY to text already established as validator-written
# by the provenance split in :func:`_preserved_ballot_markers` -- never to
# model output. That ordering is the whole safety argument: pattern-matching
# untrusted text is what let marker-shaped model prose pose as an audit marker.
_MARKER_REPR_VALUE: Final[str] = r"(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"

# What a preserved marker's payload becomes on the redaction path (Task 19.15).
# ``TurnId`` / ``ObservationId`` are bare ``str`` aliases, so a hallucinated
# ``primary_reason_id`` is arbitrary MODEL text -- it can read "p-5 is my
# partner" as easily as "m-1:turn-99". The marker around it is this codebase's,
# but the payload inside it is not, so redacting the body while preserving the
# payload verbatim would leave the same omniscience in the recorded rationale
# through a narrower channel. Only the coercion path redacts payloads; an
# uncoerced ballot keeps its markers whole, so the fabricated-id evidence stays
# fully readable everywhere the leak does not apply.
#
# Written as a ``repr`` so the marker keeps the shape every consumer parses:
# ``api.replay_loader``'s chip regex still matches a quoted literal, the
# substring / prefix greps in ``eval`` are unaffected (they key on the static
# head), and the class and count of the nulled citation survive -- only the
# untrusted value is gone. It contains no ``]``, which would otherwise stop
# ``eval.vj_instruments``'s leading-marker strip early and leak a fragment into
# the voice fold.
_REDACTED_MARKER_PAYLOAD: Final[str] = repr("(redacted)")


def _preserved_ballot_markers(
    rationale_text: str, model_rationale_text: str | None
) -> str:
    """The upstream audit markers a rationale redaction must carry across.

    The ballot chain in :meth:`MeetingManager._collect_vote` runs both
    citation-id validators BEFORE the teammate coercion, so a betrayal ballot
    that also carried a hallucinated reason / observation id reaches the guard
    with their markers already prepended. The Task 19.15 redaction removes
    only the MODEL-authored body, so those markers are carried across:
    dropping them would silently un-count nulled citations for every consumer
    that reads markers straight off the recorded string
    (``eval.vj_instruments``'s substring counts, ``api.replay_loader``'s
    chips, ``eval.meeting_quality``'s prefix greps) -- laundering one guard's
    audit trail through another's.

    The split is by PROVENANCE, never by pattern. ``model_rationale_text`` is
    the body as the model wrote it, before any validator ran; every marker in
    the chain is a *prefix*, so the recorded rationale always ends with that
    body and everything ahead of it was written by this codebase. Matching
    marker-SHAPED text instead would hand the model a bypass: a rationale that
    opens with a convincing ``[invalid primary_reason_id 'p-3 is my partner'
    nulled]`` would be preserved as an audit marker -- carrying the omniscient
    payload this redaction exists to remove, and inflating the nulled-citation
    counts with a citation that was never nulled. A null id field is not proof
    the validator wrote anything; the model may simply have cited nothing.

    The markers are preserved as a CLASS, not verbatim: each one's quoted
    payload is replaced with :data:`_REDACTED_MARKER_PAYLOAD`. The marker
    text belongs to this codebase, but the id inside it is a raw model field
    (``TurnId`` / ``ObservationId`` are bare ``str``), so a hallucinated
    ``primary_reason_id`` reading "p-5 is my partner" would otherwise carry
    the same omniscience into the record through a narrower channel than the
    body this function exists to remove. Chip, class and count all survive;
    only the untrusted value is dropped. Payload matching is safe HERE and
    only here -- the provenance split has already established that this text
    is validator-written, so there is nothing for a lookalike to spoof.

    ``model_rationale_text`` is ``None`` for a caller with no trusted
    boundary to offer (the guard is a pure function others may call
    directly). Then NOTHING is preserved and the whole rationale is replaced
    -- the safe direction, since over-redacting only loses audit detail while
    under-redacting leaks the text this guard exists to suppress.
    """

    if model_rationale_text is None:
        return ""
    if not rationale_text.endswith(model_rationale_text):
        # Structural invariant, not model input: every guard in the ballot
        # chain PREPENDS its marker, so the model's body is always the
        # suffix. A violation means the chain grew a rewrite that edits the
        # body -- fail loud rather than guess where the markers end.
        raise ValueError(
            "ballot rationale does not end with the model-authored body; "
            "the ballot chain must only prepend audit markers"
        )
    markers = rationale_text[: len(rationale_text) - len(model_rationale_text)]
    return re.sub(_MARKER_REPR_VALUE, lambda _: _REDACTED_MARKER_PAYLOAD, markers)


def coerce_teammate_ballot_to_skip(
    *,
    ballot: VoteBallot,
    fellow_impostor_ids: tuple[PlayerId, ...],
    model_rationale_text: str | None = None,
) -> VoteBallot:
    """Coerce a ballot that targets a fellow impostor to ``SKIP``.

    A teammate is a *valid* living candidate, so the hallucinated-target
    normalization (:func:`_normalize_ballot_target`) never catches it. This
    guard is what stops an impostor from supplying the betrayal vote that
    ejects a teammate. Returns ``ballot`` unchanged when
    ``fellow_impostor_ids`` is empty or the target is not a teammate;
    otherwise rewrites ``target`` to ``SKIP`` and prepends
    :data:`TEAMMATE_VOTE_TARGET_MARKER` to the rationale so the original
    (teammate) target stays auditable in the replay record.

    The coercion also nulls ``primary_reason_id`` (DESIGN.md §5.5; audit
    gp-3): once the vote collapses to SKIP the reason id is stale (it was
    chosen to justify the betrayal target), so a coerced ballot that kept
    its now-meaningless reason id would corrupt the ballot-follows-chain
    instrument exactly as a hallucinated id does.

    For the same reason the model-authored ``rationale_text`` is REPLACED
    with :data:`TEAMMATE_COERCED_VOTE_RATIONALE` rather than preserved
    (Task 19.15; audits/audit-phase-19-triage.md §7 item 16). That text was
    written to justify the betrayal target, so it can state the impostor's
    private knowledge outright ("p-3 is my partner", "I did the kill"), and
    it rides the coerced ballot onto the spectator surface, where the
    marker is stripped to a chip and the remainder renders as the voter's
    stated reason -- omniscience leaking through the guard's own output.
    EVERY audit marker survives the redaction, not just this guard's:
    auditability is never laundered. The redaction removes the model's body
    and nothing else -- markers the upstream ballot chain already prepended
    (a nulled ``primary_reason_id`` / ``primary_reason_observation_id``) are
    carried across by :func:`_preserved_ballot_markers`, so a coerced ballot
    still reports its nulled citations to every downstream marker consumer.
    That split is by PROVENANCE: pass ``model_rationale_text`` -- the body
    as the model wrote it, before any validator ran -- and everything ahead
    of it in ``ballot.rationale_text`` is by construction this codebase's
    own text. Omit it (the default) and nothing is preserved: the whole
    rationale is replaced, which loses audit detail but can never leak
    model text. Never split on marker SHAPE; a rationale that opens with
    convincing marker-shaped prose would otherwise smuggle exactly the
    payload this guard removes. The replacement body is itself a
    self-declaring substitution note, never fabricated in-world prose
    attributed to the model. This is the guard-originated TEXT class only;
    model-originated fourth-wall statements elsewhere in a transcript are a
    separate concern (measured and disclosed, not rewritten), and the
    display-side gating of the ``teammate_coerced`` chip is Task 19.11's.

    **Dormant for committed bytes.** No recorded replay is rewritten: the
    committed corpus is frozen and this guard runs only while a meeting is
    being collected, so the redaction changes what a FUTURE recording's
    coerced ballots carry and nothing that already exists on disk.
    """

    if not fellow_impostor_ids or ballot.target not in fellow_impostor_ids:
        return ballot
    marker = TEAMMATE_VOTE_TARGET_MARKER.format(target=ballot.target)
    upstream_markers = _preserved_ballot_markers(
        ballot.rationale_text, model_rationale_text
    )
    return ballot.model_copy(
        update={
            "target": _SKIP_TARGET,
            "primary_reason_id": None,
            "rationale_text": (
                marker + upstream_markers + TEAMMATE_COERCED_VOTE_RATIONALE
            ),
        }
    )


def _render_gate_value(value: float) -> float:
    """Round a suspicion float to the 2dp grid the vote prompt renders (Task 15.6).

    The frozen ``vote_ballot.j2`` §4.6 max line and every per-player
    suspicion row format with ``"%.2f"``, so the model reads a 2-decimal
    value. Any recomputation of the §4.6 verdict that must agree with what
    the model saw (:func:`guard_ballot_target_graph`) compares on THIS
    grid, so a raw value in the ``[0.595, 0.60)`` band -- which renders as
    ``0.60`` (MUST-vote) while its raw float reads MUST-skip -- cannot make
    guard and model disagree (audit post-phase-14-pause §4.1). Identical to
    the ``float("%.2f" % ...)`` rounding the persisted ``rendered_vote_max``
    already applies in :meth:`MeetingManager._collect_vote`.
    """

    return float("%.2f" % value)


def guard_ballot_target_graph(
    *,
    ballot: VoteBallot,
    voter_id: PlayerId,
    suspicion_graph: Sequence[SuspicionEntry],
    candidate_targets: tuple[PlayerId, ...],
    skip_confidence_threshold: float,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> VoteBallot:
    """Bind an eject ballot's target to the voter's rendered graph (Task 10.9.2).

    The PR #147 F2 repair, the last unguarded seam for a RANDOM ejection
    (DESIGN.md §4.6, §6.3): a voter whose rendered verdict reads MUST-vote
    may name ANY living candidate -- including one their own rendered graph
    carries no over-gate row for (seed 12 m0: the opening's bare verbal
    accusation adopted as ballot target over the graph's 0.80 argmax). The
    guard is deterministic and fires only when ALL of:

    * the ballot is an eject (``target != "SKIP"``) -- a SKIP ballot is
      byte-unchanged, always;
    * the verdict over ``candidate_targets`` reads MUST-vote: the max
      rendered suspicion among the graph rows naming a candidate is at or
      above ``skip_confidence_threshold``, the IDENTICAL derivation the
      frozen ``vote_ballot.j2`` template renders in-prompt (the same
      ``suspicion_graph`` / ``candidate_targets`` the prompt renderer
      received). The comparison runs on the 2-decimal grid the template
      renders each value at (:func:`_render_gate_value`, Task 15.6), so a
      raw suspicion in the ``[0.595, 0.60)`` band -- which the model reads
      as ``0.60`` -- cannot make guard and rendered verdict disagree. Under
      a MUST-skip verdict an eject ballot is byte-unchanged -- it stays a
      recorded inversion, frozen measurement semantics;
    * the named target's rendered row is below the threshold or absent.
      ANY over-gate target passes unredirected, even when a higher row
      exists -- the model keeps free choice among over-gate targets.

    The redirect goes to the argmax-rendered candidate in the eligible
    pool -- ``candidate_targets`` minus the voter minus
    ``fellow_impostor_ids`` -- with ties broken by the lowest player id
    (lexicographic ``min``, the module's id-ordering convention). The
    teammate exclusion composes with the §7.12 firewall by construction:
    the guard can never create the betrayal ballot the firewall exists to
    coerce. When the eligible pool's max is itself below the threshold (an
    impostor voter whose only over-gate row is a teammate), the ballot
    coerces to SKIP instead, nulling the now-stale ``primary_reason_id``
    exactly as :func:`coerce_teammate_ballot_to_skip` does. Either way
    :data:`BALLOT_TARGET_REDIRECT_MARKER` is prepended to
    ``rationale_text`` preserving the original target (bounded per the
    Task 10.6 rule). A redirected eject keeps its ``primary_reason_id``:
    the cited turn still drove the decision to EJECT -- the guard
    constrains only the target.

    Runs AFTER roster normalization (:func:`_normalize_ballot_target`) and
    the §7.12 teammate coercion, so it only ever sees a valid living
    non-teammate eject target. Pure function of its inputs -- no RNG, no
    clock -- so replaying the same graph + ballot yields the same redirect.
    """

    if ballot.target == _SKIP_TARGET:
        return ballot
    rendered = {
        entry.player_id: entry.suspicion
        for entry in suspicion_graph
        if entry.player_id in candidate_targets
    }
    # The in-prompt §4.6 verdict, recomputed bit-for-bit. The model reads
    # every suspicion at the 2-decimal grid the frozen ``vote_ballot.j2``
    # renders ("%.2f"|format on each row AND the §4.6 max line), so the
    # verdict is recomputed on that SAME rounded grid (Task 15.6, audit
    # post-phase-14-pause §4.1): a raw value in the [0.595, 0.60) band
    # renders as 0.60 (the model reads MUST-vote) while its raw float reads
    # MUST-skip. Quantize-then-compare pins guard and model to the identical
    # number by construction -- the same rounding the persisted
    # ``rendered_vote_max`` already applies. The redirect *target* still
    # selects on the raw argmax below, so the only behavior change is inside
    # the band; the frozen template reads MUST-vote at or above the threshold.
    gate = _render_gate_value(skip_confidence_threshold)
    verdict_max = max(
        (_render_gate_value(value) for value in rendered.values()), default=0.0
    )
    if verdict_max < gate:
        return ballot
    target_row = rendered.get(ballot.target)
    if target_row is not None and _render_gate_value(target_row) >= gate:
        return ballot
    marker = BALLOT_TARGET_REDIRECT_MARKER.format(
        target=_bounded_original(ballot.target)
    )
    eligible = {
        player_id: suspicion
        for player_id, suspicion in rendered.items()
        if player_id != voter_id and player_id not in fellow_impostor_ids
    }
    if (
        not eligible
        or max(_render_gate_value(value) for value in eligible.values()) < gate
    ):
        return ballot.model_copy(
            update={
                "target": _SKIP_TARGET,
                "primary_reason_id": None,
                "rationale_text": marker + ballot.rationale_text,
            }
        )
    redirect = min(eligible, key=lambda player_id: (-eligible[player_id], player_id))
    return ballot.model_copy(
        update={
            "target": redirect,
            "rationale_text": marker + ballot.rationale_text,
        }
    )


def guard_ballot_citation(
    *,
    ballot: VoteBallot,
    contradictions: tuple[ContradictionRef, ...],
) -> VoteBallot:
    """Coerce an uncited zero-flag EJECT ballot to ``SKIP`` (Task 16.6, J2).

    The enforcement tooth of the citation chain
    (audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2): a claim
    counts toward conviction only if it cites a specific in-game source. The
    guard is deterministic and fires only when ALL of:

    * the ballot is an eject (``target != "SKIP"``) -- a SKIP ballot is
      byte-unchanged, always;
    * the target is ZERO-FLAG: no :class:`ContradictionRef` detected THIS
      meeting names it in ``subjects``. A flagged target is convictable
      uncited -- the flag IS the in-game source, already on the public
      record;
    * the ballot cites NOTHING: ``primary_reason_id`` (the transcript-turn
      channel) AND ``primary_reason_observation_id`` (the 16.5 private-
      observation channel) are BOTH null. The upstream validators
      (:func:`_normalize_ballot_reason_id` /
      :func:`_normalize_ballot_observation_id`) have already nulled any
      fabricated id with its own marker, so a hallucinated citation gates
      exactly like a bare null -- nulls-then-coerces, two markers.

    A gated ballot COERCES to ``SKIP`` with
    :data:`UNCITED_ZERO_FLAG_EJECT_MARKER` prepended to ``rationale_text``
    (the mark-and-coerce pattern of :func:`coerce_teammate_ballot_to_skip`);
    the gate never rejects, never crashes, never re-prompts. Both citation
    fields are already null on every coerced ballot by the predicate above,
    so there is no stale reason id to null.

    Scope honesty (the planning doc's own analysis): the gate cannot
    distinguish an honest memory-only conviction from a bare pile-on when the
    voter cites nothing -- that is WHY 16.5's observation-citation path lands
    first (an honest witness can cite their private observation id) and why
    the gate shipped only after the served ballot prompt stopped sanctioning
    a blanket null-citation register (``vote_ballot.j2`` "use ``null`` when
    your call rests on your own memory" -- the earlier bespoke sets still
    carry that prose verbatim). The 16.15 elicitation rewrote the served
    set's "Gut-read" register to a memory-citing one (every EJECT is asked to
    source a turn or observation id; a memory-based SKIP legitimately stays
    null) and 16.17 measured the soundness counterfactual, so this guard runs
    on every production ballot.

    Runs AFTER :func:`guard_ballot_target_graph` (the post-redirect slot in
    the chain), so a redirected eject is judged on the REDIRECTED target's
    flag status, not the original's. A redirect that KEPT its citation also
    keeps its gate pass: the 10.9.2 redirect deliberately preserves
    ``primary_reason_id`` (the cited turn still drove the decision to
    EJECT; that guard constrains only the target), so a cited under-gate
    eject redirected onto a zero-flag argmax passes this gate on the kept
    citation. Deliberate, and pinned by fixture: the gate enforces citation
    VALIDITY, never relevance -- neither upstream validator links a
    citation to the ballot's target (a voter naming any target may cite any
    real turn / own observation), so the direct-vote twin passes
    identically and the redirect opens no new hole. Nulling the citation at
    the redirect instead would edit ``guard_ballot_target_graph``'s recorded
    behavior, which this gate does not own; citation QUALITY is
    16.15/16.17's measured business. The zero-flag predicate reads only this
    meeting's detected ``contradictions`` -- never suspicion values -- so
    the absence delta (which moves suspicion and mints no flag) cannot
    change the gate's decision by construction. Pure function of its inputs
    (no RNG, no clock, no env read), so replaying the same ballot + flags
    yields the same coercion.
    """

    if ballot.target == _SKIP_TARGET:
        return ballot
    if (
        ballot.primary_reason_id is not None
        or ballot.primary_reason_observation_id is not None
    ):
        return ballot
    flagged = frozenset(
        subject
        for contradiction in contradictions
        for subject in contradiction.subjects
    )
    if ballot.target in flagged:
        return ballot
    marker = UNCITED_ZERO_FLAG_EJECT_MARKER.format(target=ballot.target)
    return ballot.model_copy(
        update={
            "target": _SKIP_TARGET,
            "rationale_text": marker + ballot.rationale_text,
        }
    )


def _guard_teammate_turn_claims(
    claims: tuple[Claim, ...],
    *,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> tuple[Claim, ...]:
    """Apply the Task 7.12 claim-level teammate guards to one turn's claims.

    Runs the primary guard (:func:`exclude_teammate_accusation_claims`,
    which drops accusation claims naming a teammate) and then a
    :func:`drop_teammate_statement_target` backstop on the derived
    accusation target: the reactive chain passes the floor to the player a
    turn accuses, so the recorded claims must never leave a teammate as
    that target. The backstop is a no-op once the primary guard has run
    (the teammate accusation is already gone); it is retained so all three
    7.12 guards wrap every turn-kind. A no-op for a crewmate / sole
    impostor (empty ``fellow_impostor_ids``).
    """

    guarded = exclude_teammate_accusation_claims(
        claims, fellow_impostor_ids=fellow_impostor_ids
    )
    target = next(
        (claim.against for claim in guarded if isinstance(claim, AccusationClaim)),
        None,
    )
    if (
        target is not None
        and drop_teammate_statement_target(
            target, fellow_impostor_ids=fellow_impostor_ids
        )
        is None
    ):
        guarded = tuple(
            claim
            for claim in guarded
            if not (isinstance(claim, AccusationClaim) and claim.against == target)
        )
    return guarded


# ---------------------------------------------------------------------------
# Meeting belief evidence (Tasks 9.8, 10.7).
#
# The vote-time contradiction lift (`_suspicion_graph_with_contradictions`)
# rebuilds a throwaway BeliefState and is discarded with the meeting, so until
# Task 9.8 a verbal accusation touched nothing durable -- 25/47 impostor-accused
# meetings carried no contradiction and the §4.6 gate forced SKIP (audit gp-1
# recall). `derive_belief_evidence` is the meeting-side half of the persistent
# path: it reduces a final transcript + flags to the deduplicated public
# subject sets that `agents.memory.beliefs.apply_meeting_evidence_rules` folds
# into each living agent's STORED beliefs. Task 10.7 split the fold into two
# deterministic halves that ALWAYS run, sharing this one derivation:
#
# * PRE-VOTE half -- the manager derives the evidence from the final
#   transcript inside :meth:`MeetingManager.run` and applies the two-witness
#   testimony bumps + this meeting's relevance-gated corroborations
#   (``phase="pre_vote"``) to every voter's suspicion graph BEFORE the ballot
#   prompts render, so the §4.6 verdict reads post-fold values. The
#   ``pre_vote_folded`` subjects are marked HERE, on the meeting context --
#   the belief store never knows about phases.
# * POST-VOTE half -- the orchestrator's standing post-meeting fan-out
#   (``orchestrator.game._absorb_meeting_beliefs`` ->
#   ``agents.memory.store.absorb_meeting_evidence``) persists the whole
#   meeting's evidence into each living agent's store through the composed
#   default-phase call: single-voice accused-bumps + Rule-5 decay land there
#   exactly as before 10.7, and the pre-vote deltas persist at the same
#   boundary -- once, because the composition bumps each accused subject
#   exactly once (the double-fold guard; the per-meeting total for a folded
#   subject equals the unfolded total).
#
# Evidence is read from the recorded transcript and flags only -- ballots are
# post-hoc transparency, never visible to agents (DESIGN.md §5.5) -- so a
# replay re-derives identical evidence from the recorded meeting alone.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MeetingBeliefEvidence:
    """One meeting's public belief-relevant subjects (Tasks 9.8, 10.7).

    Each tuple is sorted and deduplicated, so a pile-on of accusers within
    one meeting is a single meeting-level "was accused" event -- the
    accusation bump is per meeting, not per accuser -- and downstream
    iteration is deterministic.

    * ``accused`` -- subjects named by at least one recorded
      :class:`~meetings.schemas.AccusationClaim` (teammate-guarded and
      living-validated by the per-turn chokepoint before recording).
    * ``corroborated`` -- subjects supported by at least one
      :class:`~meetings.schemas.CorroborationClaim` (living-validated by
      the per-turn chokepoint since Task 10.2 -- audit H-H-6's 15
      phantom-subject no-ops can no longer reach the fold), plus
      subjects of a detector-derived containment-consistent
      (alibi, sighting) pair
      (:func:`meetings.transcript.detect_corroborations`, Task 10.1) --
      a third-party sighting confirming a stated alibi is
      corroboration-class evidence (§6.3 Rule 3). The detector-derived
      half is roster-filtered to the meeting's living participants,
      matching the recording-time detection path. BOTH halves pass the
      Task 10.6 Rule-3 relevance gate
      (:func:`meetings.transcript.is_relevant_sighting`, audit C-C-3):
      the detector half inside ``detect_corroborations`` itself, the
      claim-stated half here against the claim's ``on_tick`` (a claim
      carries no room, so only the spawn-window prong can gate it --
      tick-0/1 vouches are the everyone-was-at-spawn shape). The set
      is deduplicated per meeting, so a corroborated subject receives the
      Rule-3 delta exactly once however many pairs confirm them.
    * ``contradicted`` -- subjects of the meeting's detected
      :class:`~meetings.schemas.ContradictionRef` flags; new evidence for
      the §6.3 Rule 5 decay exemption (the persistent lift itself stays
      Rule 2's transient vote-time mechanism).
    * ``pre_vote_folded`` -- the Task 10.7 two-witness subjects: accused
      subjects with at least
      :data:`agents.memory.beliefs.TESTIMONY_INDEPENDENCE_BAR` distinct
      independent voices behind the accusation
      (:func:`meetings.transcript.independent_voices` -- observation
      backing, the §6.3 relevance predicate, the opt-in
      corroboration-alignment rule, and the Task 10.15 echo-dedup are the
      guards). These subjects take the +0.05 accused-bump in the PRE-VOTE
      half; the post-vote half skips them (the phase routing in
      :func:`agents.memory.beliefs.apply_meeting_evidence_rules`), so
      the bump lands exactly once per meeting. Always a subset of
      ``accused``. The folded mark lives here, on the meeting context --
      never in the belief store.
    * ``pre_vote_informed`` -- the Task 10.15 single-witness subjects
      (:data:`agents.memory.beliefs.WITNESS_INFORM_REASON`): accused
      subjects with EXACTLY one independent voice (below the fold bar).
      They take the IDENTICAL +0.05 accused-bump in the PRE-VOTE half --
      the inform spreads one observation-backed witness's testimony to
      the listeners so near-gate priors can cross the §4.6 gate within
      the round (audit 2026-06-13 C-C-1: the 37/59 over-gate-lost-
      plurality bloc). Disjoint from ``pre_vote_folded`` (one voice vs
      two+) and likewise always a subset of ``accused``; the post-vote
      half skips it too, so the per-meeting total stays +0.05.
    * ``pre_vote_voice_counts`` -- the Task 13.7 graduated testimony
      spread input: a sorted ``(subject, voice_count)`` pair per voiced
      subject (the :func:`meetings.transcript.independent_voices` COUNT),
      covering exactly ``pre_vote_folded | pre_vote_informed``. The
      vote-time pre-vote fold reads it to GRADUATE the bump by count --
      1 voice +0.05 (byte-identical), 2 +0.12 (the first §4.6 gate-cross),
      3+ +0.15 (capped) -- so two corroborating accounts EJECT where one
      only informs. Carried on the meeting context ONLY: the persistent
      post-meeting absorb passes no counts, so only the flat +0.05
      persists (no cross-round railroad). Empty when no subject is voiced,
      which keeps a no-witness meeting byte-identical.
    * ``absent`` -- the Task 16.8 absent set: the meeting's living roster
      minus the players public testimony placed
      (:func:`meetings.transcript.absent_players` -- a sighting names you
      or your own Task 16.7 whereabouts answer places you; otherwise you
      are absent). Derived unconditionally (pure, PUBLIC-transcript-only,
      so the replay path re-derives the identical set), but CONSUMED only
      by the vote-time pre-vote fold, where each absent subject takes the TRANSIENT
      :data:`agents.memory.beliefs.ABSENCE_SUSPICION_DELTA`. Derived with
      THIS function's ``trigger_kind`` -- both live paths supply the true
      engine-derived kind (the manager's pre-vote region re-derives this
      field with it, PR #264 review; :func:`extract_belief_evidence`
      threads it), so a fabricated emergency-opening body never widens the
      kill-scene exclusion into spurious absence (the Task 10.11 gate).
      The persistent post-meeting absorb never reads it, so absence never
      accumulates across meetings (the sizing contract on the delta's
      docstring).
    """

    accused: tuple[PlayerId, ...]
    corroborated: tuple[PlayerId, ...]
    contradicted: tuple[PlayerId, ...]
    pre_vote_folded: tuple[PlayerId, ...] = ()
    pre_vote_informed: tuple[PlayerId, ...] = ()
    pre_vote_voice_counts: tuple[tuple[PlayerId, int], ...] = ()
    absent: tuple[PlayerId, ...] = ()


def derive_belief_evidence(
    transcript: MeetingTranscript,
    *,
    contradictions: Sequence[ContradictionRef],
    roster: frozenset[PlayerId],
    trigger_kind: MeetingTriggerKind | None = None,
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]] | None = None,
) -> MeetingBeliefEvidence:
    """Derive a meeting's public belief evidence (Tasks 9.8, 10.7).

    The single evidence derivation behind BOTH fold halves: the manager
    calls it pre-vote on the final transcript (Task 10.7 -- the
    invocation point moved, the logic did not), and
    :func:`extract_belief_evidence` delegates here post-meeting for the
    orchestrator's persistent absorb and for replay-side re-derivation.
    Pure function of its arguments: walks every recorded turn's claims
    (opening / reply / opt-in alike -- an opt-in accusation is as public
    as a chain one) plus the detected contradiction flags. Claims are
    read AS RECORDED, i.e. after the per-turn guards ran: a teammate
    accusation was already stripped (Task 7.12) and a claim naming a
    non-living subject -- accusation target, alibi subject, or
    corroboration supports -- already dropped
    (:func:`_drop_non_roster_claims`; fb3cfa5 + Task 10.2), so the
    evidence can only name living meeting participants the chain itself
    honoured.

    ``roster`` is the meeting's living-participant set: the live path
    passes the participant ids, the replay path the recorded ballot
    voters (identical sets -- every living participant casts exactly one
    ballot, defaults included). It scopes the detector-derived
    corroborations and the independent-voices derivation exactly as the
    recording-time ``detect_contradictions`` call was scoped; the
    claim-stated fields need no second filter (the chokepoint already
    validated them before recording).

    ``sighting_records`` (Task 16.7) is the per-speaker typed
    first-hand-sighting channel -- the GROUNDED VOUCH input. When present,
    a third producer joins the ``corroborated`` set:
    :func:`meetings.transcript.grounded_vouch_subjects`, the subjects of
    spoken sightings that match the SPEAKER'S OWN records (relevance-gated
    like both existing halves, deduplicated by the same set fold, priced
    by the same -0.05 delta -- one channel, three producers, never a
    parallel path). NO production caller passes it yet: committed
    transcripts already carry speaker-groundable sightings, so the live
    pre-vote feed would move committed ballot-prompt bytes; the task that
    adopts it passes the participant mapping from
    :meth:`MeetingManager.run`. ``None`` (every current
    caller, including every replay-side re-derivation, which has no
    private records by construction) is byte-identical to the pre-16.7
    derivation, so a recorded meeting still re-derives its persistent
    evidence from the public record alone (DESIGN.md §0 rule 1).
    """

    accused: set[PlayerId] = set()
    corroborated: set[PlayerId] = set()
    # Rule-3 relevance gate (Task 10.6; audit gp-2 C-C-3): a claim-stated
    # vouch passes the same named predicate the detector-derived pairs go
    # through inside ``detect_corroborations`` -- one gate, two producers.
    # A CorroborationClaim carries a tick but no room, so its empty room
    # set can never trip the kill-scene prong; the spawn-window prong is
    # the operative one (a tick-0/1 "I can vouch" is the
    # everyone-spawned-together shape that confirms nothing).
    body_rooms = triggering_body_rooms(transcript, trigger_kind=trigger_kind)
    for turn in transcript.turns:
        for claim in turn.claims:
            if isinstance(claim, AccusationClaim):
                accused.add(claim.against)
            elif isinstance(claim, CorroborationClaim) and is_relevant_sighting(
                tick=claim.on_tick,
                rooms=frozenset(),
                triggering_body_rooms=body_rooms,
            ):
                corroborated.add(claim.supports)
    # Detector-derived corroboration (Task 10.1, audit gp-2 C-C-1): a
    # containment-consistent (alibi, sighting) pair re-derived from the
    # transcript is Rule-3 evidence alongside the claim-stated
    # CorroborationClaims. Pure re-derivation, so a replay folds the
    # identical evidence from the recorded meeting alone; a hallucinated
    # non-player subject (audit C-8) whose alibi and sighting happen to
    # agree can never corroborate itself into a phantom belief row (an
    # explicitly-empty roster indexes nothing).
    corroborated.update(
        corroboration.subject
        for corroboration in detect_corroborations(
            transcript, roster=roster, trigger_kind=trigger_kind
        )
    )
    # Grounded vouches (Task 16.7): a spoken sighting matching the SPEAKER'S
    # OWN typed record proves the speaker honestly reported what they saw --
    # corroboration-class evidence for the subject, folded into the SAME set
    # (same relevance gate inside the chokepoint, same per-meeting dedup,
    # same -0.05) rather than a parallel path. Never a flag, never trust.
    if sighting_records:
        corroborated.update(
            grounded_vouch_subjects(
                transcript,
                sighting_records=sighting_records,
                roster=roster,
                trigger_kind=trigger_kind,
            )
        )
    contradicted = {
        subject
        for contradiction in contradictions
        for subject in contradiction.subjects
    }
    # The testimony derivation (Tasks 10.7, 10.15; audit gp-2 C-C-2 and
    # 2026-06-13 C-C-1): one independent-voices count, partitioned by the
    # fold bar. Subjects with TESTIMONY_INDEPENDENCE_BAR+ voices FOLD
    # pre-vote (10.7 two-witness); subjects with exactly one voice INFORM
    # pre-vote (10.15 single-witness belief-spread) -- the same +0.05, the
    # same pre-vote half, distinguished only so the bands stay nameable for
    # Wave-2 attribution. The two are disjoint by construction and both are
    # subsets of ``accused`` (voice subjects are accusation targets), the
    # invariants the belief-side phase routing validates.
    voices = independent_voices(transcript, roster=roster, trigger_kind=trigger_kind)
    pre_vote_folded = tuple(
        sorted(
            subject
            for subject, speakers in voices.items()
            if len(speakers) >= TESTIMONY_INDEPENDENCE_BAR
        )
    )
    pre_vote_informed = tuple(
        sorted(
            subject
            for subject, speakers in voices.items()
            if len(speakers) < TESTIMONY_INDEPENDENCE_BAR
        )
    )
    # The Task 13.7 graduated-spread input: the raw voice COUNT per voiced
    # subject (covering exactly pre_vote_folded | pre_vote_informed), which the
    # vote-time pre-vote fold maps to the graduated delta. Carried on the
    # context only; the persistent absorb passes no counts, so only +0.05
    # persists.
    pre_vote_voice_counts = tuple(
        sorted((subject, len(speakers)) for subject, speakers in voices.items())
    )
    return MeetingBeliefEvidence(
        accused=tuple(sorted(accused)),
        corroborated=tuple(sorted(corroborated)),
        contradicted=tuple(sorted(contradicted)),
        pre_vote_folded=pre_vote_folded,
        pre_vote_informed=pre_vote_informed,
        pre_vote_voice_counts=pre_vote_voice_counts,
        # Task 16.8: the absent set rides the SAME derivation (same roster,
        # same trigger_kind) as every other evidence fold here, so the replay
        # path re-derives it bit-identically from the public record alone.
        # Task 18.12: the 17.5 vent-placement WIDENING ships with the vent package
        # (18.11 ruling C) -- a GROUNDED vent sighting places its subject, so a
        # vent-flagged subject is removed from the absent set rather than
        # double-counted as absent by the graduated absence prior. Driven by the
        # ``vent_sighting`` flag channel (:func:`grounded_vent_subjects_from_flags`),
        # which is byte-identical to the record-driven widening AND identical live vs
        # replay -- ``contradictions`` is the public record here.
        absent=tuple(
            player
            for player in absent_players(
                transcript, roster=roster, trigger_kind=trigger_kind
            )
            if player not in grounded_vent_subjects_from_flags(contradictions)
        ),
    )


def extract_belief_evidence(
    result: MeetingResult,
    *,
    trigger_kind: MeetingTriggerKind | None = None,
) -> MeetingBeliefEvidence:
    """Reduce a resolved meeting to its public belief evidence (Task 9.8).

    The post-meeting / replay entry point: delegates to
    :func:`derive_belief_evidence` (one derivation, two invocation
    points -- Task 10.7) with the roster read off the recorded ballots.
    Every living participant casts exactly one ballot (defaults
    included), so the ballot voters ARE the living-participant roster
    the meeting ran with; a hand-built result with no ballots therefore
    derives no detector-sourced corroborations and no voices.

    ``trigger_kind`` (Task 10.11; audit-2026-06-13-1816 B-B-1) is the
    engine-authoritative reason the meeting opened, threaded from the
    orchestrator (:func:`orchestrator.game._absorb_meeting_beliefs`). It
    flows to the §6.3 Rule-3 relevance gate so an EMERGENCY meeting never
    trusts a fabricated opening ``found_body`` to widen its exclusion
    zone. ``None`` preserves the pre-10.11 read-the-opening behaviour for
    callers without the kind in hand.
    """

    return derive_belief_evidence(
        result.transcript,
        contradictions=result.contradictions,
        roster=frozenset(ballot.voter for ballot in result.ballots),
        trigger_kind=trigger_kind,
    )


def _reported_statement_sort_key(
    statement: ReportedStatement,
) -> tuple[PlayerId, str, PlayerId, int, int, str]:
    """Total order over reported statements for replay-deterministic output.

    Every component is concrete (``None`` ticks/room collapse to a sentinel),
    so the sort is stable and byte-identical across runs regardless of the
    transcript's turn order.
    """

    return (
        statement.speaker,
        statement.kind,
        statement.subject,
        statement.from_tick if statement.from_tick is not None else -1,
        statement.to_tick if statement.to_tick is not None else -1,
        statement.room if statement.room is not None else "",
    )


@dataclass(frozen=True)
class MeetingOutcomeSummary:
    """One resolved meeting's PUBLIC vote tally.

    The tally announced at the table, and nothing else: ``ejected_id`` is the
    player the vote removed (``None`` on a skip or a tie), ``votes_for_ejected``
    the ballots naming that player, and ``skip_votes`` the ballots naming SKIP.
    Role-BLIND by construction -- the meeting layer never sees a role, so the
    confirm-ejects announcement is the orchestrator's half to add.
    """

    ejected_id: PlayerId | None
    votes_for_ejected: int
    skip_votes: int


def derive_meeting_outcome_summary(result: MeetingResult) -> MeetingOutcomeSummary:
    """Reduce a resolved meeting to the tally the table heard announced.

    The outcome twin of :func:`derive_reported_testimony`: a pure,
    replay-deterministic function of the recorded ``MeetingResult`` that imports
    no engine, reads only ``ballots`` plus the recorded ejection, and returns the
    same summary every time.

    The ejected player's own count and the skip count are carried SEPARATELY
    rather than as a winner/runner-up pair because ``SKIP`` is a first-class
    tally target (:mod:`meetings.voting`) and a tie resolves to SKIPPED: on a
    skipped meeting there is no winner to count, only the skips.
    """

    ejected_id = result.ejected_player_id
    votes_for_ejected = (
        0
        if ejected_id is None
        else sum(1 for ballot in result.ballots if ballot.target == ejected_id)
    )
    skip_votes = sum(1 for ballot in result.ballots if ballot.target == _SKIP_TARGET)
    return MeetingOutcomeSummary(
        ejected_id=ejected_id,
        votes_for_ejected=votes_for_ejected,
        skip_votes=skip_votes,
    )


def derive_reported_testimony(result: MeetingResult) -> tuple[ReportedStatement, ...]:
    """Reduce a resolved meeting to its public reported testimony (Task 13.5.2).

    The content twin of :func:`extract_belief_evidence` -- where that reduction
    collapses a meeting to scalar suspicion subject-sets, this one preserves the
    WHAT of public speech as :class:`~meetings.schemas.ReportedStatement` rows
    (the 2026-06-25 memory diagnosis, workflow ``wg54kfoxy``: "social info is a
    scalar, not content"). A pure, replay-deterministic function of the recorded
    ``MeetingResult``: it imports no engine and no perception, reads only the
    recorded ``transcript.turns`` (NEVER ``free_text``), and returns the same
    sorted tuple every time.

    Scope: the STRUCTURED kinds only --
    :class:`~meetings.schemas.SawPlayerObservation` and
    :class:`~meetings.schemas.SawVentObservation` sightings,
    :class:`~meetings.schemas.AlibiClaim`,
    :class:`~meetings.schemas.AccusationClaim`, and
    :class:`~meetings.schemas.CorroborationClaim`. ``completed_task`` /
    ``found_body`` observations and all free-text are dropped. A vent sighting
    reduces to ``saw_vent`` so the listener keeps its room and tick as content;
    whether it RENDERS is the ingest side's call
    (:func:`agents.memory.store.absorb_reported_testimony`), and the reduction
    mints no evidence -- the STRONG ``vent_sighting`` flag is a separate,
    grounded channel.

    Speaker-gated; subject gating deferred to ingest (Codex P2, Task 13.5.2):
    ``roster`` is the meeting's living-participant set read off the recorded
    ballots (identical to :func:`extract_belief_evidence`). Only the SPEAKER is
    gated here -- only a living participant takes a turn. The SUBJECT is NOT gated
    against this living set, because a ``saw_player`` observation about a player
    DEAD before this meeting (the body victim, an earlier ejection) is real public
    testimony yet is absent from the ballots; gating it here would silently drop
    the kill-scene sightings the prompts explicitly elicit. Subject validity is
    enforced per-agent at ingest against
    :func:`agents.memory.store._known_roster_ids` (the engine-witnessed set, which
    covers dead-but-seen players via co-spawn), so a hallucinated structural id
    still never reaches an episodic row. Claims (alibi/accusation/corroboration)
    are already living-subject by the per-turn chokepoint
    (:func:`_drop_non_roster_claims`); observations are NOT chokepoint-validated,
    which is why the ingest gate is load-bearing for them.

    NOT teammate-firewalled: reported content is PUBLIC speech, so an impostor's
    derivation carries a statement that publicly incriminates its own team
    exactly as a crewmate's does. Only the SCALAR suspicion path keeps the
    teammate firewall (unchanged, :func:`extract_belief_evidence` ->
    :func:`apply_meeting_evidence_rules`).
    """

    roster = frozenset(ballot.voter for ballot in result.ballots)
    statements: list[ReportedStatement] = []
    for turn in result.transcript.turns:
        speaker = turn.speaker
        if speaker not in roster:
            continue
        for observation in turn.observations:
            if isinstance(observation, SawPlayerObservation):
                statements.append(
                    ReportedStatement(
                        speaker=speaker,
                        kind="saw_player",
                        subject=observation.subject,
                        from_tick=observation.tick,
                        to_tick=observation.tick,
                        room=observation.room,
                        co_present=observation.co_present,
                    )
                )
            elif isinstance(observation, SawVentObservation):
                statements.append(
                    ReportedStatement(
                        speaker=speaker,
                        kind="saw_vent",
                        subject=observation.subject,
                        from_tick=observation.tick,
                        to_tick=observation.tick,
                        room=observation.room,
                    )
                )
        for claim in turn.claims:
            if isinstance(claim, AlibiClaim):
                statements.append(
                    ReportedStatement(
                        speaker=speaker,
                        kind="alibi",
                        subject=claim.subject,
                        from_tick=claim.from_tick,
                        to_tick=claim.to_tick,
                        room=claim.room,
                    )
                )
            elif isinstance(claim, AccusationClaim):
                statements.append(
                    ReportedStatement(
                        speaker=speaker,
                        kind="accusation",
                        subject=claim.against,
                    )
                )
            elif isinstance(claim, CorroborationClaim):
                statements.append(
                    ReportedStatement(
                        speaker=speaker,
                        kind="corroboration",
                        subject=claim.supports,
                        from_tick=claim.on_tick,
                        to_tick=claim.on_tick,
                    )
                )
    return tuple(sorted(statements, key=_reported_statement_sort_key))


def _candidate_targets(
    player_ids: Iterable[PlayerId],
    *,
    exclude: PlayerId,
) -> tuple[PlayerId, ...]:
    """Living players minus ``exclude``, sorted (DESIGN.md §5.5).

    The single definition of "valid target" shared by the vote ballot's
    ``candidate_targets`` (living minus voter) and the turn prompts'
    living-roster accusation list (living minus speaker -- an agent cannot
    accuse itself; Task 9.9, audit gp-3). One filter, two prompt surfaces,
    so the rosters can never drift.
    """

    return tuple(sorted(pid for pid in player_ids if pid != exclude))


def _drop_non_roster_claims(
    claims: tuple[Claim, ...],
    *,
    living_ids: frozenset[PlayerId],
) -> tuple[tuple[Claim, ...], tuple[TurnAnnotation, ...]]:
    """Drop claims whose subject-bearing field names no living participant.

    The single roster-validation chokepoint for every subject-bearing
    claim field (Task 10.2; audit gp-6 C-C-8, H-H-6), extending the
    fb3cfa5 accusation-target guard:

    * ``accusation.against`` -- the fb3cfa5 case: a hallucinated target
      (e.g. ``"imp-2"``) the chain cannot pass to
      (:func:`meetings.transcript.next_chain_step` ->
      ``TERMINATION_TARGET_NOT_LIVING``) and the §11.3
      accusation-calibration metric cannot resolve to a role.
    * ``alibi.subject`` -- the 9B emitted game ids as alibi subjects
      (``"headless-seed-9"``, seed 9 m1 turns 2-3); recorded, they reach
      §5.4 contradiction detection and render as phantom players.
    * ``corroboration.supports`` -- 15 recorded corroborations carried a
      turn id or a free-text phrase (``"p-2 dead"``, seed 40 m0) and
      silently no-op'd the §9.8 fold on a phantom subject -- the reason
      belief Rule 3 never fired in any recorded set.

    A valid subject is a living meeting participant -- the same notion of
    "valid target" the vote path enforces via ``candidate_targets`` -- so
    a corroboration naming a DEAD roster player is dropped exactly like
    an accusation naming one. Runs at the per-turn chokepoint BEFORE the
    turn is recorded: a dropped claim never reaches the transcript,
    contradiction detection, the post-meeting belief fold, or any prompt
    surface.

    Returns ``(surviving_claims, annotations)``, both in claim order. Each
    drop yields one :class:`~meetings.schemas.TurnAnnotation` naming the
    field and carrying the original value, which the caller records on the
    turn (:func:`structured_turn_markers_enabled`) or renders as the
    equivalent ``free_text`` audit marker
    (:func:`_turn_annotation_marker`). Either way the original stays
    auditable and downstream eval can count drops per field. The original is
    bounded (:func:`_bounded_original`): a hallucinated mega-value -- the
    seed-35 3499-char reasoning blob emitted AS an alibi subject -- can no
    longer balloon the recorded turn; real player ids pass through verbatim.
    Deterministic and a no-op when every claim names a living participant, so
    a clean replay is byte-unaffected.
    """

    surviving: list[Claim] = []
    annotations: list[TurnAnnotation] = []
    for claim in claims:
        if isinstance(claim, AccusationClaim) and claim.against not in living_ids:
            annotations.append(
                TurnAnnotation(
                    kind="invalid_accusation_target",
                    original=_bounded_original(claim.against),
                )
            )
        elif isinstance(claim, AlibiClaim) and claim.subject not in living_ids:
            annotations.append(
                TurnAnnotation(
                    kind="invalid_alibi_subject",
                    original=_bounded_original(claim.subject),
                )
            )
        elif isinstance(claim, CorroborationClaim) and claim.supports not in living_ids:
            annotations.append(
                TurnAnnotation(
                    kind="invalid_corroboration_supports",
                    original=_bounded_original(claim.supports),
                )
            )
        else:
            surviving.append(claim)
    return tuple(surviving), tuple(annotations)


__all__ = [
    "BALLOT_TARGET_REDIRECT_MARKER",
    "DEFAULT_SKIP_CONFIDENCE_THRESHOLD",
    "DEFAULT_TURN_DEADLINE_SECONDS",
    "DEFAULT_TURN_FREE_TEXT",
    "DEFAULT_TURN_MAX_TOKENS",
    "DEFAULT_TURN_TEMPERATURE",
    "DEFAULT_VOTE_DEADLINE_SECONDS",
    "DEFAULT_VOTE_MAX_TOKENS",
    "DEFAULT_VOTE_RATIONALE",
    "DEFAULT_VOTE_TEMPERATURE",
    "EMERGENCY_BODY_STRIP_MARKER",
    "EMERGENCY_NO_BODY_RETRY_FEEDBACK",
    "EMERGENCY_TRIGGER_PHRASE",
    "INVALID_ACCUSATION_TARGET_MARKER",
    "INVALID_ALIBI_SUBJECT_MARKER",
    "INVALID_CORROBORATION_SUPPORTS_MARKER",
    "INVALID_OBSERVATION_ID_MARKER",
    "INVALID_REASON_ID_MARKER",
    "INVALID_VOTE_TARGET_MARKER",
    "MARKER_QUOTED_ORIGINAL_MAX_CHARS",
    "MARKER_TRUNCATION_SUFFIX",
    "OPENING_RETRY_FEEDBACK_DEAD_TARGET",
    "OPENING_RETRY_FEEDBACK_DEMAND",
    "OPENING_RETRY_FEEDBACK_HEADER",
    "OPENING_RETRY_FEEDBACK_NO_POSITION",
    "OPENING_UNSURE_DEGRADE_MARKER",
    "OPENING_UNSURE_MARKER",
    "OPENING_UNSURE_MAX_FREE_TEXT_CHARS",
    "TEAMMATE_COERCED_VOTE_RATIONALE",
    "TEAMMATE_VOTE_TARGET_MARKER",
    "UNCITED_ZERO_FLAG_EJECT_MARKER",
    "VOTE_PARSE_DEFAULT_MARKER",
    "DefaultTrigger",
    "DefaultedCall",
    "DefaultedPhase",
    "LLMProviderError",
    "MeetingBeliefEvidence",
    "MeetingConfig",
    "MeetingDeadlines",
    "MeetingManager",
    "MeetingOutcomeSummary",
    "MeetingParticipant",
    "MeetingTrigger",
    "PromptRenderInputs",
    "ReportPromptRenderer",
    "Role",
    "StatementPromptRenderer",
    "SuspicionEntry",
    "VotePromptRenderer",
    "coerce_teammate_ballot_to_skip",
    "derive_belief_evidence",
    "derive_meeting_outcome_summary",
    "derive_reported_testimony",
    "drop_teammate_statement_target",
    "exclude_teammate_accusation_claims",
    "exclude_teammate_vent_observations",
    "extract_belief_evidence",
    "guard_ballot_citation",
    "guard_ballot_target_graph",
]
