"""What "deduction" MEANS, instrumented (Task 19.14).

Anchored to ``audits/audit-phase-19-triage.md`` §7 item 15 [S-Codex / S-Claude
convergent objective; §8 rows 3, 10, 14] plus the item-24 disclosure twin that
Task 19.8 landed in ``replays/ml_corpus/README.md``. Locked decision 6 makes this
module the PRECONDITION for any later gameplay phase: the evidence-honesty
substrate fixes are decided AFTER the metrics, from these cells, and Task 19.28
puts them in front of the owner. Nothing here touches gameplay — ``meetings/``
and ``agents/`` are untouched by construction; this is measurement only.

The headline finding both external audits reached independently is that the
project's "ejection accuracy" number is dominated by engine-donated vent proof.
Restating it needs TWO different partitions of the same bytes, and the fourth
Codex planning round caught them being mixed inside one sentence. So the C5
lesson (the audits' fourth-wall counts differed ONLY by definition) is applied
literally here: **every metric is defined below — numerator, denominator, and
what it does NOT measure — before it is counted**, each partition owns its own
frozen model, and no cell ever divides one partition's numerator by the other's
denominator.

Purity + provenance
-------------------
:func:`compute_deduction_metrics` is a pure function of an assembled
:class:`~eval.report_schema.TournamentReport` (plus one OPTIONAL adopted input,
below). It does no I/O, no engine re-run, and no LLM call, so it composes into
:func:`eval.meeting_quality.build_tournament_eval_report` and rides on every
committed ``tournament-eval-report.json``. Roles come from the report's post-game
ground truth (``GameReport.roles``), never from the replay.

Why the kill-craft cells arrive as a PARAMETER
----------------------------------------------
The witnessed / co-present evidence supply is ADOPTED from
:func:`eval.kill_craft.compute_kill_craft_report`, never re-derived: those cells
need a state-hash-verified engine walk over a replay-set DIRECTORY, which the
report does not carry. Importing :mod:`eval.kill_craft` here would also close an
import cycle (``eval.kill_craft`` -> ``eval.validity`` -> ``api.replay_loader``
-> ``eval.meeting_quality`` -> this module), so the adoption is expressed
structurally instead: :class:`KillCraftSupplyCells` is a Protocol over the three
cells this module reads, and the CALLER (``scripts/build_sample_report.py``)
passes the real report. When no kill-craft report is supplied,
``witnessed_supply`` is ``None`` — the explicit "not supplied" sentinel, never a
zero that would read as "no kills".

------------------------------------------------------------------------------
THE DEFINITIONS (written before the counting; each states what it does NOT
measure)
------------------------------------------------------------------------------

**1. The evidence taxonomy census** (:class:`EvidenceTaxonomyCensus`) — the
eval-side twin of Task 19.11's DTO taxonomy (``api.schemas.classify_evidence``).
Deliberately a RE-IMPLEMENTATION of the same rule table rather than an import:
the api-side docstring names this module as the twin and the two are cross-pinned
on the same committed bytes in ``tests/eval/test_deduction_metrics.py``, which is
only evidence if the two derivations are independent. The table, in order:

===========================================  ==================
condition                                    category
===========================================  ==================
``kind`` is not a KNOWN kind                 *raise*
``kind`` in :data:`ROLE_PROOF_KINDS`         ``role_proof``
``event_a_id == event_b_id`` (self-linked)   ``role_proof``
detector weak stamp                          ``weak_signal``
otherwise                                    ``cross_statement``
===========================================  ==================

Numerator: each recorded :class:`~meetings.schemas.ContradictionRef` in the
report. Denominator: all of them (``flags_total``). Weakness comes from
:func:`meetings.transcript.is_weak_contradiction` — imported, never
re-implemented, so the marker predicate stays single-sourced beside the marker
writer. ``meetings_with_any_flag`` counts meetings carrying >= 1 flag of ANY
category — deliberately a different name from partition A's ``flagged_meetings``
(role proof only), because on ``replays/samples/9p2i`` the two differ (100 vs
70) and one name for two predicates is how a cross-tab gets mis-cited.
*Does NOT measure*: whether anybody READ a flag, whether a flag was true, or
whether the two sides of a cross-statement conflict are equally credible.

**2. The MEETING-flag cross-tab** (:class:`MeetingFlagCrossTab`) — partition A.
The unit is the MEETING. A meeting is FLAGGED iff it carries at least one
``role_proof`` flag (a grounded ``vent_sighting``), *regardless of whom that
flag names* — NOT "carries any flag", which is the taxonomy census's
``meetings_with_any_flag``. Every ejection is then bucketed by its own meeting's
flag status and by the ejected player's role.

* ``flagged_meetings`` + ``unflagged_meetings`` == ``meetings_total``.
* ``unflagged_meeting_accuracy`` = ``unflagged_ejections_impostor`` /
  (``unflagged_ejections_impostor`` + ``unflagged_ejections_innocent``) — the
  triage's 10/31 = 32.3% on ``replays/samples/9p2i``.

*Does NOT measure*: whether the proof named the player who was ejected (that is
partition B, and the two denominators are NOT interchangeable); nor whether the
voters cited the flag.

**3. The EJECTEE-specific-proof cross-tab** (:class:`EjecteeProofCrossTab`) —
partition B. The unit is the EJECTION. An ejection is PROOF-PRESENT iff the
ejected player is a subject of at least one ``role_proof`` flag *in the meeting
that ejected them*.

* ``proof_present_ejections`` + ``non_direct_ejections`` == ``ejections_total``.
* ``non_direct_accuracy`` = ``non_direct_impostor`` / ``non_direct_ejections`` —
  the triage's 10/33 = 30.3% on ``replays/samples/9p2i``, 35/89 = 39.3% on the
  corpus twin.

*Does NOT measure*: how many meetings had proof available (partition A);
*Does NOT claim*: that a proof-present ejection was CAUSED by the proof — the
cell is co-occurrence at meeting granularity, which is precisely why it is
labelled "proof-present", not "proof-driven".

The two partitions share only ``ejections_total``. Their splits differ by
construction: on ``replays/samples/9p2i`` partition A puts 70 ejections in
flagged meetings and 31 in unflagged ones, while partition B puts 68 on
ejectee-specific proof and 33 without it. Both are correct; a sentence that
divides one's numerator by the other's denominator is not.

**4. Weak-flag-only conviction** (:class:`WeakFlagConvictionCells`) — the
injustice class the audits traced (consensus #9; §8 row 14's seed-47 exhibit).
Numerator: ejections where the ejected player is named by at least one flag AND
*every* flag naming them classifies ``weak_signal``. Denominator:
``flag_named_ejections`` — ejections where the ejectee is named by at least one
flag of any category. The innocent share of the numerator is published beside it
because that is the harm. *Does NOT measure*: whether a voter actually cited the
weak flag (ballots carry a citation, but the belief-side weight is not
recoverable from the recorded bytes); *does NOT* claim a weak flag caused the
ejection.

**5. Same-agent turn -> ballot consistency**
(:class:`TurnBallotConsistencyCells`) — did the speaker vote the way they spoke?
The definition is written first *because* two things need a rule: SKIP (the
implementation hint) and the vote guard.

* VOTABLE set of a meeting = the players who cast a ballot in it (every living
  participant votes, so this is the living roster read off the record rather
  than reconstructed). Each voter's LEGAL target set is that minus THEMSELVES,
  mirroring ``meetings.manager._candidate_targets(living, exclude=voter)``: a
  player cannot vote for themselves, so a self-accusation names nobody they
  could lawfully eject. It therefore cannot put a ballot into the denominator,
  and a self-target can never score consistent.
* AUTHORED target: **the target the AGENT wrote, not the one the record shows.**
  Four deterministic guards rewrite ``VoteBallot.target`` and each stamps the
  ORIGINAL into ``rationale_text`` as ``{target!r}`` — the graph redirect, the
  invalid-target normalization, the teammate coercion, and the citation-gate
  coercion (``meetings/manager.py``). This metric is SAME-AGENT by name, so a
  rewritten ballot is unwound to the authored target before it is scored;
  otherwise the guard's choice would be charged to the agent, and the same
  rewrite would be counted twice — once here as "inconsistency" and once,
  correctly, in the separate redirect census (metric 7). On
  ``replays/samples/9p2i`` 16 of the 777 scored ballots are unwound and all 16
  change bucket; on the corpus 46 of 2,186 are unwound and 44 change bucket
  (twice the authored AND rewritten targets were both legal players outside
  the voter's accused set, so "inconsistent-other" held). Not a hypothetical
  either way.
  ``guard_rewritten_ballots_unwound`` publishes how many were unwound.
* Denominator ``accusing_ballots``: (meeting, voter) pairs where the voter cast
  a ballot, spoke at least one turn carrying an
  :class:`~meetings.schemas.AccusationClaim`, and accused at least one VOTABLE
  player.
* ``consistent_ballots``: the authored target is one of that voter's accused
  players.
* ``inconsistent_skip_ballots``: the authored target is SKIP (the accused was
  votable, so the SKIP-tolerance clause does not excuse it).
* ``inconsistent_other_target_ballots``: the authored target is a VOTABLE player
  the voter never accused.
* ``inconsistent_invalid_target_ballots``: the authored target is not in the
  voter's LEGAL set — a hallucinated id, or the voter themselves (3 on
  ``replays/samples/9p2i``, 0 elsewhere). It is its own bucket because the voter
  neither voted their accusation nor voted anyone else; folding it into either
  neighbour would misdescribe what happened.
* ``excluded_no_votable_target_ballots``: accusing ballots where NO accused
  player was votable — excluded from the denominator, published so the exclusion
  is visible rather than silent. ``accusations_of_non_votable_targets`` counts
  the accusation claims naming a non-votable player at all.

*Does NOT measure*: whether the accusation or the vote was CORRECT; whether the
guard's rewrite was right (metric 7 owns the guard); and it deliberately scores
an honest mid-meeting revision as an inconsistency — it measures follow-through,
not virtue.

**6. Public response coverage split by role**
(:class:`PublicResponseCoverageCells`) — the triage's item-24 disclosure twin.
Numerator: transcript turns carrying a structured
:class:`~meetings.schemas.WhereaboutsClaim` (the roll-call answer). Denominator:
that role's transcript turns. TWO estimators are published side by side under
distinct names, because the triage's source-specific figure and Task 19.8's
recount are the SAME bytes under different estimators (verify-then-fix — see the
provenance note below):

* ``*_pooled_coverage`` — pooled over turns (the headline; 120/245 = 49.0%
  impostor on ``replays/samples/9p2i``).
* ``*_macro_average_coverage`` — the unweighted per-meeting macro-average
  (45.45% impostor on the same bytes: the triage's "45.5%").

*Does NOT measure*: whether the answer was TRUE (Task 19.8 measured that
separately), and it is NOT an observation-firewall leak — it is a behavioural
tell produced by the templates' role-differentiated output contract.

**7. Engine-redirected ballot share** (:class:`RedirectedBallotCells`) — how much
of the ballot record is the deterministic vote guard rather than the model.
Numerator: ballots whose LEADING MARKER CHAIN carries the pinned
:data:`~meetings.manager.BALLOT_TARGET_REDIRECT_MARKER`. Denominator: all
recorded ballots. The count splits by the recorded target: an eject the guard
re-aimed vs a ballot coerced to SKIP. *Does NOT measure*: whether the redirect
changed the meeting's OUTCOME (that needs a counterfactual tally, which recorded
bytes cannot supply).

Every guard-origin question in this module — this share, the leakage census's
marker cells, and the authored-target unwind — reads the same ANCHORED chain
(:func:`_scan_marker_chain`), never a substring search of the whole rationale.
The manager guarantees "the ballot chain must only prepend audit markers", so a
marker literal appearing anywhere else is by construction the MODEL quoting it;
an unanchored test would count that ballot as guard-touched and inflate the
census, the rewrite denominator, and the preserved-leak numerator at once.

**8. Scaffold leakage, split by ORIGIN** (:class:`ScaffoldLeakageCells`) — the
C5 finding restated as separately-defined metrics instead of one contested
number. The contract names two leakage CLASSES on the model side — role
statements and machinery statements — and one on the guard side; all three are
counted, and the ROLE class is itself three nets because "omniscience" has three
distinguishable shapes in the committed text.

The two origins read DIFFERENT sources, by construction, and the boundary
between those sources is established by PROVENANCE rather than by pattern
(:class:`_RationaleSplit`). A recorded ``rationale_text`` is a machinery-written
marker region followed by a body; the model's own pre-guard text is the
boundary that separates them, exactly as
:func:`meetings.manager._preserved_ballot_markers` separates them for the
redaction it guards. Three cells, three regions:

* GUARD cells scan the MARKER REGION for markers. Not the whole record —
  anchoring alone would let a model body that OPENS with marker-shaped prose
  pass as machinery. Not the payloads either: those carry model-supplied targets
  (``_normalize_ballot_target`` interpolates a hallucinated target verbatim) and
  raw response heads.
* ``guard_preserved_omniscient_ballots`` scans the recorded BODY — what survived
  the guard, which is what "preserved" means.
* MODEL cells scan the PRE-GUARD body and nothing else, because Task 19.15's
  teammate coercion REPLACES the recorded rationale before the ballot is stored:
  a future teammate-aimed ballot disclosing a partner would read clean on the
  recorded surface, and this metric would under-count precisely the class that
  redaction exists to remove. A ballot with no pre-guard body scans NOTHING
  rather than falling back to the record, which for a parse-default ballot is a
  bounded head of the raw JSON envelope — ``"confidence": 0.NN`` included.

``model_source_pre_guard_ballots`` / ``model_source_unavailable_ballots`` and
``guard_provenance_verified_ballots`` /
``guard_provenance_unverifiable_ballots`` each partition every ballot, so both
boundaries are counted rather than assumed. On all four committed sets every
ballot is suffix-verified (unavailable 0, unverifiable 0) and every cell is
identical to the whole-record reading — the fixes are forward-looking, and the
pins say so.

* MODEL-originated ROLE/omniscience — text the model authored.
  ``model_partner_naming_ballots`` (:data:`PARTNER_PHRASES`),
  ``model_role_statement_ballots`` (:data:`ROLE_STATEMENT_PHRASES`), and
  ``model_self_kill_disclosure_ballots`` (:data:`SELF_KILL_PHRASES` — a voter
  narrating their OWN kill: "I killed p-4", "I know I was killing p-3"). All
  three are over impostor-voter ballots; ``model_omniscient_ballots`` is their
  UNION (a ballot can hit several nets, so the union is not their sum).
  ``crew_partner_naming_ballots`` and ``crew_omniscient_control_ballots`` are
  the false-positive CONTROLS. Re-derived over the committed reports the partner
  control is 0 on all four sets and the omniscient control is **1** on each of
  the two 9p2i sets and 0 on the two 4p1i ones — a small, non-zero base rate a
  reader of the leak cells must know about.
  ``player_visible_leak_turns`` is the partner net over player-visible
  ``free_text``.

  First-person VENT mentions are deliberately EXCLUDED from the self-kill net.
  On the committed bytes they are dominated by denials and quotations of an
  accusation — "You claim I vented", "They scream I vented" — which a substring
  net cannot separate from an admission, and counting a denial as a leak would
  invert the metric. A genuine vent admission that also states the role
  ("I am the killer. I vented.") is already caught by the role net.
* MODEL-originated MACHINERY — the model reproducing its own scoring scaffold.
  Two cells, because the two registers do not deserve the same confidence
  (Task 19.8's finding, carried rather than flattened):
  ``model_machinery_quotation_ballots`` counts a QUOTED internal decimal
  (:data:`MACHINERY_DECIMAL_PATTERN`, ``0.NN``) — unambiguous, since the
  two-decimal grid is exactly what ``vote_ballot.j2`` renders; while
  ``model_machinery_vocabulary_ballots`` counts :data:`MACHINERY_VOCABULARY`
  ("threshold" / "suspicion") and is an explicit UPPER BOUND, because a
  deduction game says those words naturally. Both are over ALL ballots, not
  just impostor ones — machinery talk is role-independent. Beside them, the
  ORACLE-REGISTER cells (:data:`MACHINERY_ORACLE_PATTERNS`) count a player
  crediting the engine with a verdict — "the engine flagged it" — across all
  three spoken surfaces: ``model_oracle_register_ballots`` over the pre-guard
  ballot body, ``oracle_register_turns`` over ``free_text``, and
  ``oracle_register_claim_reasons`` over accusation/corroboration ``reason``
  against ``claim_reasons_total``. That register has no innocent in-world
  reading, so these are leak counts rather than an upper bound.
* GUARD-originated — text the deterministic machinery injected.
  ``guard_marked_ballots``: ballots whose LEADING CHAIN carries any pinned
  manager/voting marker.
  ``guard_target_rewrite_ballots``: the subset whose TARGET the guard rewrote.
  ``guard_preserved_omniscient_ballots`` and its own rate
  ``guard_preserved_omniscient_rate``: target-rewritten ballots whose preserved
  rationale still carries ANY omniscient phrase (the union above), over the
  ``guard_target_rewrite_ballots`` denominator — the exact class Task 19.15
  redacts going forward, and the guard-side RATE the contract asks for.
  ``guard_marked_ballot_share`` is NOT a substitute: it answers a different
  question over a different denominator (55/2,726 vs 1/53 on the corpus). The
  cell is **1/53** on ``replays/ml_corpus/9p2i`` (seed 1118, meeting 0: a
  redirected impostor ballot whose preserved rationale says "when I know I was
  killing p-3") and 0 on the other three sets. The class is therefore RARE on
  committed bytes, not absent — a distinction this module got wrong until the
  self-kill net existed, which is itself the C5 lesson landing on the metric
  that measures it.

Every net is a substring or regex match over recorded text and is therefore an
UPPER bound on intent and a LOWER bound on leakage: a phrase list cannot see a
leak it does not list. *Does NOT measure*: paraphrase, and *does NOT* claim the
nets are exhaustive. The partner, role, decimal and vocabulary nets are Task
19.8's, carried verbatim so the two surfaces cannot drift; the self-kill net is
new here and is stated as new.

**9. Witnessed / co-present evidence supply**
(:class:`WitnessedSupplyCells`) — ADOPTED wholesale from
:func:`eval.kill_craft.compute_kill_craft_report` (Task 18.2), never
recomputed. ``crew_witnessed_kills`` / ``kills_total`` is the share of kills any
crewmate witnessed; ``co_present_crew_kills`` is the number of kills with at
least one non-victim living crewmate co-present in the kill room at the
pre-advance decision frame (0 on every committed set — the structural
"too-clean evidence economy" finding). This is the SUPPLY side of deduction:
how much direct kill testimony the corpus offers at all. *Does NOT measure*:
whether the testimony was used.

------------------------------------------------------------------------------
Verify-then-fix provenance (the triage's evidence labels are binding)
------------------------------------------------------------------------------
Two inputs to this module were labelled source-specific and NOT independently
re-run by the triage (§8 rows 18, 24). Both were recomputed from the committed
bytes here, and the RECOUNT is the pin:

* **The roll-call coverage split.** The triage carried impostor coverage as
  45.5-46.5%. Recount: that figure reproduces exactly as the unweighted
  per-meeting MACRO-AVERAGE (45.45% samples-9p2i / 46.54% ml_corpus-9p2i); the
  pooled turn-level share is 49.0% / 50.0%. Both estimators ship as separately
  named cells rather than one contested number, matching Task 19.8's disclosure
  byte for byte.
* **The "13 engine-redirected under-gate ejects".** Recount: exactly 13
  redirect-marked ballots on ``replays/samples/9p2i``, all 13 recorded as ejects
  and none coerced to SKIP. The source claim reproduces.

One source cell did NOT reproduce and is corrected here rather than carried:
§8 row 3's 4p sentence ("13 total ejections: 12 in flagged meetings and one in a
flagless meeting; 26/27 flagless meetings skipped"). ``replays/samples/4p1i``
carries **12** ejections over 39 meetings; the flagged/flagless split depends on
which partition is meant, and neither reading yields 13 (partition A: 10 in
vent-flagged meetings, 2 in unflagged; ANY-flag: 12 and 0, over 13 flagged and
26 flagless meetings). The replay bytes are byte-identical to the triage's tree,
so this is a source miscount, not corpus drift. The row's 9p claims — which the
triage DID independently re-run — reproduce to the digit under both partitions.

Rare-event advisory + Wilson
----------------------------
:class:`WilsonRateCell` pairs a rate with its Wilson 95% score interval (stdlib
``math`` only), following the Task 18.1 precedent in
``eval/deception_instruments.py``. That module's cell is not imported: it is
FROZEN under the Phase-19 tier map and its import chain
(``eval.funnel`` -> ``eval.validity`` -> ``api.replay_loader``) would close the
same cycle described above.

Leak-safety
-----------
Every model here carries only ints, floats, ``float | None`` rates, and bools —
no roles, transcripts, player ids, or engine-owned types cross a model boundary.
"""

from __future__ import annotations

import ast
import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import Final, Literal, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, model_validator

from engine.entities import Role
from eval.report_schema import GameReport, MeetingReport, TournamentReport
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    TEAMMATE_COERCED_VOTE_RATIONALE,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
)
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    CorroborationClaim,
    PlayerId,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import is_weak_contradiction

# 95% two-sided Wilson score constant (the 18.1 value).
_WILSON_Z: Final[float] = 1.96
# Rare-event advisory bar, adopted verbatim from the Task 18.1 rule
# (``eval/deception_instruments.py``): at or below this numerator the point rate
# is statistically fragile and the interval should be read instead.
_RARE_EVENT_ADVISORY_MAX_NUMERATOR: Final[int] = 7

SKIP_TARGET: Final[str] = "SKIP"

# The keys that identify a parsed payload as a VOTE BALLOT rather than any other
# meeting-phase response. ``LLMCallRecord.call_kind`` is only "meeting"/"trigger"
# — turn calls and vote calls share it, and share ``agent_id`` — so the record
# carries no phase discriminator and the payload SHAPE is the only evidence
# available. ``rationale_text`` alone is not enough: a malformed TURN response
# that hallucinated that field would be picked up as a ballot's pre-guard body
# whenever the real vote call is missing. These three are the ballot schema's
# required, turn-absent fields (``meetings.schemas.VoteBallot``).
_VOTE_PAYLOAD_KEYS: Final[frozenset[str]] = frozenset(
    {"target", "confidence", "rationale_text"}
)


# ---------------------------------------------------------------------------
# The evidence taxonomy (the eval-side twin of Task 19.11's DTO rule table)
# ---------------------------------------------------------------------------

EvidenceCategory: TypeAlias = Literal["role_proof", "cross_statement", "weak_signal"]
"""What KIND of evidence a recorded flag is (the twin of ``api.schemas``').

Deliberately re-declared rather than imported: the cross-pin in
``tests/eval/test_deduction_metrics.py`` is evidence only if the two
derivations are independent (``api.schemas.classify_evidence``'s own docstring
names this module as that twin).
"""

ROLE_PROOF_KINDS: Final[frozenset[str]] = frozenset({"vent_sighting"})
"""Kinds that are role PROOF whatever their event ids look like (Task 15.4)."""

CROSS_STATEMENT_KINDS: Final[frozenset[str]] = frozenset(
    {"alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical"}
)
"""Kinds asserting two DIFFERENT public statements cannot both be true."""


class UnclassifiableFlagError(ValueError):
    """A recorded flag matches no :data:`EvidenceCategory` rule.

    Raised, never defaulted: the taxonomy must be TOTAL over every committed
    byte, so a new ``ContradictionRef.kind`` added in ``meetings/`` without a
    rule here is a finding to record rather than a bucket to widen (AGENTS.md
    "no silent fallbacks").
    """


def classify_flag(flag: ContradictionRef) -> EvidenceCategory:
    """Classify one recorded flag into its :data:`EvidenceCategory`.

    The rule table in the module docstring, in order. The kind check comes
    FIRST and gates everything, so an unrecognised kind that happened to carry a
    weak stamp raises instead of quietly bucketing as ``weak_signal``.
    Self-linkage (``event_a_id == event_b_id``) is a rule of its own: a flag
    whose two ids reference the SAME artifact is not a conflict between two
    statements, whatever it is called.

    :raises UnclassifiableFlagError: on any kind the table does not cover.
    """

    kind = flag.kind
    if kind not in ROLE_PROOF_KINDS and kind not in CROSS_STATEMENT_KINDS:
        raise UnclassifiableFlagError(
            f"unclassifiable flag: kind={kind!r} "
            f"(contradiction_id={flag.contradiction_id!r}); the deduction-metric "
            "taxonomy has no rule for it — record it as a finding rather than "
            "widening a bucket"
        )
    if kind in ROLE_PROOF_KINDS or flag.event_a_id == flag.event_b_id:
        return "role_proof"
    if is_weak_contradiction(flag):
        return "weak_signal"
    return "cross_statement"


# ---------------------------------------------------------------------------
# Scaffold-leakage phrase nets (carried verbatim from the Task 19.8 disclosure)
# ---------------------------------------------------------------------------

PARTNER_PHRASES: Final[tuple[str, ...]] = (
    "my partner",
    "my teammate",
    "my fellow impostor",
)
"""The STRICT partner-naming net (``replays/ml_corpus/README.md`` item 7).

Matched case-insensitively as substrings. Task 19.8 counted 29/245 (samples
9p2i) and 81/684 (corpus 9p2i) impostor-voter ballots with this net, and 0/2,926
crew ballots — the false-positive control this module republishes.
"""

ROLE_STATEMENT_PHRASES: Final[tuple[str, ...]] = (
    "i am the impostor",
    "i am an impostor",
    "i'm the impostor",
    "i'm an impostor",
)
"""The STRICT outright-role-statement net (Task 19.8's 8/245 S9, 14/684 C9)."""

SELF_KILL_PHRASES: Final[tuple[str, ...]] = (
    "i killed",
    "i kill ",
    "i was killing",
    "i had killed",
    "i was the one who killed",
    "i am the one who killed",
    "i'm the one who killed",
    "i am the killer",
    "i'm the killer",
)
"""First-person KILL disclosure — a voter narrating their own kill.

EVERY entry is explicitly first-person. The bare fragment ``"one who killed"``
was tried and rejected: it also matches an ordinary third-person accusation
("p-3 is the one who killed p-4"), which discloses nothing private and would
inflate the rate on future records. Replacing it with the three first-person
forms leaves every committed count unchanged (the committed matches were all
"I'm the one who killed"), so the tightening costs no recall on these bytes and
removes a false-positive class from the next ones.

The third omniscience shape, and the one Task 19.15's contract names beside
"teammate" ("omniscient teammate/self-kill rationale text"). It is NEW here
rather than carried from Task 19.8, which counted only partner naming and
outright role statements; the committed bytes carry 9/245 (samples 9p2i) and
22/684 (corpus 9p2i) impostor-voter ballots under it, including the one
guard-preserved instance the module docstring names.

First-person VENT mentions are deliberately absent. On the committed bytes they
are dominated by denials and quotations of an accusation ("You claim I vented",
"They scream I vented"), which a substring net cannot separate from an
admission; counting a denial as a leak would invert the metric. A genuine vent
admission that also states the role is caught by
:data:`ROLE_STATEMENT_PHRASES`. Crew false-positive control: 0 across all four
committed sets.
"""

MACHINERY_DECIMAL_PATTERN: Final[re.Pattern[str]] = re.compile(r"0\.\d\d")
"""The UNAMBIGUOUS machinery-quotation net: a quoted internal decimal.

Two decimals is exactly the grid ``vote_ballot.j2`` renders suspicion and the
§4.6 max on (``"%.2f"|format``), so a rationale reproducing one is quoting the
scoring scaffold rather than talking like a player. Task 19.8: 39/971 (samples
9p2i) and 94/2,726 (corpus 9p2i) ballots.
"""

MACHINERY_VOCABULARY: Final[tuple[str, ...]] = ("threshold", "suspicion")
"""The machinery-vocabulary net — an explicit UPPER BOUND, not a leak count.

A deduction game says "suspicion" and "threshold" naturally, so this net cannot
distinguish quotation from ordinary play; Task 19.8 labelled it an upper bound
and this module keeps that label rather than promoting it to a leak rate. It
ships beside :data:`MACHINERY_DECIMAL_PATTERN`, never instead of it.
"""


# The in-world nouns a bare ``engine`` match would otherwise swallow: the ship's
# engine room and the ``align_engine_output`` task (engine/maps/canonical_1.yaml)
# are correct player speech, and a net that scores them is measuring the fiction
# rather than the leak. "the engine maintenance report" is the same class — an
# engine-qualified ship-maintenance noun phrase, not the apparatus speaking.
_ORACLE_IN_FICTION: Final[str] = (
    r"room|rooms|output|outputs|bay|bays|core|cores|maintenance|repair|repairs"
    r"|diagnostics|coolant|manifold|reactor"
)
# A machinery ACTOR: the game's own scoring apparatus named as an agent. The
# ``\b`` after ``engine`` is load-bearing — it keeps "Engineering" (the ship's
# wing) and "the engines" (its machinery) out, which is most of the excess a
# substring net returns. The exclusion spans an optional possessive, so "the
# engine's output" is refused exactly like "the engine output"; leaving the
# possessive to a later group would let it walk past the lookahead.
_ORACLE_ACTOR: Final[str] = (
    rf"the\s+(?:engine\b(?!(?:'s|’s)?\s+(?:{_ORACLE_IN_FICTION})\b)"
    r"|system\b|detector\b)"
)
# One word that may sit between the actor and its verdict verb. An in-fiction
# noun may NOT: "the engine maintenance report says …" is the ship's paperwork
# talking, and letting a descriptor slip through here would re-open the hole the
# actor's own lookahead closes for the adjacent case.
_ORACLE_GAP_WORD: Final[str] = rf"\s+(?!(?:{_ORACLE_IN_FICTION})\b)[\w'’-]+"
# A VERDICT act: the apparatus deciding, certifying or announcing a fact.
_ORACLE_VERDICT: Final[str] = (
    r"(?:flag|certif|confirm|verif|prove|proven|proof|declar|rul|seal|say|says"
    r"|said|state|report|clear|log|settl|find|found)"
)
# The evidence nouns a possessive apparatus produces ("the engine's cold truth").
_ORACLE_EVIDENCE_NOUN: Final[str] = (
    r"(?:truth|verdict|certification|proof|flags?|ruling|judg\w*|word|call|readout)"
)

MACHINERY_ORACLE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        rf"\b{_ORACLE_ACTOR}(?:'s|’s)?(?:{_ORACLE_GAP_WORD}){{0,3}}\s+"
        rf"{_ORACLE_VERDICT}",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b{_ORACLE_VERDICT}\w*\s+(?:by|with|per)\s+{_ORACLE_ACTOR}",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b(?:engine|system|detector)\b[-\s]{_ORACLE_VERDICT}",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b{_ORACLE_ACTOR}(?:'s|’s)(?:{_ORACLE_GAP_WORD}){{0,2}}\s+"
        rf"{_ORACLE_EVIDENCE_NOUN}\b",
        re.IGNORECASE,
    ),
)
"""The ORACLE-REGISTER net — a player crediting the game engine with a verdict.

"the engine flagged it", "certified by the system flags", "the engine's cold
truth": the apparatus named as an authority that has already decided. Unlike
:data:`MACHINERY_VOCABULARY` this register has no innocent in-world reading, so
its counts are leak counts rather than an upper bound, and it ships as its own
cells beside the vocabulary net rather than folded into it.

Precision is the whole design. A match needs a machinery ACTOR next to a VERDICT
act (or a machinery-qualified evidence noun), the ``engine`` alternative carries
a word boundary so the ship's Engineering wing never matches, and the ship's
engine room and ``align_engine_output`` task are excluded outright.
"""


# The repr-aware ANCHORED marker chain that recovers the AUTHORED target a
# rewriting guard preserved. Each rewriting marker interpolates the target as it
# stood BEFORE that guard ran (``meetings/manager.py``: "either way this marker
# preserves the original target"), so the agent's own ballot is recoverable —
# but only if the chain is read in the right direction.
#
# Every guard PREPENDS (``marker + ballot.rationale_text``, manager.py x5), so
# the chain reads RIGHT-TO-LEFT in application order: the LEFTMOST marker is the
# guard that ran LAST and its payload is an intermediate target some earlier
# guard already produced, while the RIGHTMOST rewriting marker is the guard that
# ran FIRST and its payload is what the MODEL wrote. Concretely, a graph
# redirect followed by a citation coercion records
# ``[uncited … 'p-4' …] [under-gate … 'p-2' …] body`` — the model authored p-2,
# and reading leftmost would report the guard's own p-4.
#
# The walk is ANCHORED and consumes the whole prefix chain (including the
# non-rewriting markers, which carry no target), so a marker's literal text
# appearing inside the model's BODY can never be mistaken for a real marker —
# the manager guarantees "the ballot chain must only prepend audit markers", and
# this parse holds it to that rather than trusting a substring.
_MARKER_REPR_VALUE: Final[str] = r"(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"


def _marker_pattern(marker: str) -> re.Pattern[str]:
    """An anchored, repr-aware pattern for one ``.format()``-interpolated marker.

    Generalizes over the placeholder name (``{target!r}`` / ``{reason_id!r}`` /
    ``{observation_id!r}`` / ``{head!r}``) so every pinned marker compiles from
    its imported constant and a rename cannot silently break the parse.
    """

    head, _, rest = marker.partition("{")
    _, _, tail = rest.partition("}")
    if not head or not rest:
        raise ValueError(f"marker constant carries no repr placeholder: {marker!r}")
    return re.compile(
        re.escape(head) + "(" + _MARKER_REPR_VALUE + ")" + re.escape(tail)
    )


# ``(pattern, rewrites_the_target, is_the_graph_redirect, is_the_parse_default)``
# for every marker the ballot chain prepends. ONE table drives every guard-origin
# question — the census, the redirect share, the authored-target unwind, and the
# provenance split — so no consumer can disagree with another about what "the
# machinery wrote here" means. The parse-default column is flagged because it is
# the only marker the writer ever emits as a WHOLE rationale rather than a prefix.
_BALLOT_MARKER_CHAIN: Final[tuple[tuple[re.Pattern[str], bool, bool, bool], ...]] = (
    (_marker_pattern(BALLOT_TARGET_REDIRECT_MARKER), True, True, False),
    (_marker_pattern(INVALID_VOTE_TARGET_MARKER), True, False, False),
    (_marker_pattern(TEAMMATE_VOTE_TARGET_MARKER), True, False, False),
    (_marker_pattern(UNCITED_ZERO_FLAG_EJECT_MARKER), True, False, False),
    (_marker_pattern(INVALID_REASON_ID_MARKER), False, False, False),
    (_marker_pattern(INVALID_OBSERVATION_ID_MARKER), False, False, False),
    (_marker_pattern(VOTE_PARSE_DEFAULT_MARKER), False, False, True),
)


class _MarkerChain(BaseModel):
    """What the ANCHORED leading marker chain of one rationale says.

    Every guard-origin cell reads this, and reads it over the PROVENANCE-
    established marker region only (:func:`_split_rationale`), never over the
    whole rationale. Anchoring alone is not enough: a model body that OPENS
    with marker-shaped prose sits at position 0 too, so shape cannot separate
    the machinery's text from the model's. ``meetings.manager``'s own redaction
    guard makes the same argument and resolves it the same way — "the split is
    by PROVENANCE, never by pattern" (:func:`~meetings.manager.
    _preserved_ballot_markers`) — using the pre-guard body as the boundary.

    ``authored_target`` is the LAST rewriting marker's payload — the first guard
    to have run, whose target is the model's own — or ``None`` when no guard
    rewrote the target. ``consumed`` is how far into the scanned text the chain
    reached, which is what lets a record made ENTIRELY of markers be recognized
    as such.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    any_marker: bool
    rewrote_target: bool
    redirected: bool
    parse_default: bool
    marker_count: int
    authored_target: str | None
    consumed: int


def _scan_marker_chain(rationale: str) -> _MarkerChain:
    """Walk the anchored prefix chain once and report everything it carries.

    Fail-loud on a malformed repr (AGENTS.md "no silent fallbacks"): a marker
    that matched its own pinned pattern but whose payload will not evaluate is a
    corrupt record, not something to shrug past.
    """

    position = 0
    marker_count = 0
    any_marker = rewrote = redirected = parse_default = False
    authored: str | None = None
    while True:
        for (
            pattern,
            rewrites_target,
            is_redirect,
            is_parse_default,
        ) in _BALLOT_MARKER_CHAIN:
            match = pattern.match(rationale, position)
            if match is None:
                continue
            any_marker = True
            marker_count += 1
            redirected = redirected or is_redirect
            parse_default = parse_default or is_parse_default
            if rewrites_target:
                rewrote = True
                try:
                    original = ast.literal_eval(match.group(1))
                except (ValueError, SyntaxError) as error:  # pragma: no cover
                    raise ValueError(
                        "guard marker carries an unreadable target repr: "
                        f"{match.group(1)!r}"
                    ) from error
                if not isinstance(original, str):
                    raise ValueError(
                        f"guard marker target repr is not a string: {original!r}"
                    )
                # Later iterations reach EARLIER-applied guards, so the last
                # assignment is the model-authored target.
                authored = original
            position = match.end()
            break
        else:
            break
    return _MarkerChain(
        any_marker=any_marker,
        rewrote_target=rewrote,
        redirected=redirected,
        parse_default=parse_default,
        marker_count=marker_count,
        authored_target=authored,
        consumed=position,
    )


class _RationaleSplit(BaseModel):
    """One recorded rationale cut along its PROVENANCE boundary.

    A recorded ``rationale_text`` is two texts with two different authors, and
    every cell in metric 8 depends on which one it is reading:

    * ``marker_region`` — written by this codebase. Guard-origin cells scan it.
      Its marker PAYLOADS are model-supplied (``_normalize_ballot_target``
      interpolates the hallucinated target verbatim, ``_vote_parse_default`` a
      bounded head of the unparseable response), so it is scanned for MARKERS
      and never for leakage phrases.
    * ``body_region`` — the body that SURVIVED into the record. The
      guard-preserved cell scans this, because "preserved" means what survived.
    * ``model_body`` — what the model wrote before any guard ran, or ``None``
      when the vote response yielded no rationale field at all. Model-origin
      cells scan this and NOTHING else: falling back to the recorded string
      would feed a parse-default ballot's raw JSON envelope — ``"confidence":
      0.NN`` and all — straight into the machinery-quotation net.

    ``verified`` says whether the boundary was ESTABLISHED rather than assumed.
    Three ways it can be, in the order they are tried:

    1. the record ends with the model's own pre-guard body, so everything ahead
       of that body is by construction this codebase's (the boundary
       ``meetings.manager._preserved_ballot_markers`` uses);
    2. the record ends with Task 19.15's fixed replacement note, i.e. the guard
       replaced the body — checked AFTER (1) so a model body that merely quotes
       the note cannot claim the machinery's side of the line;
    3. the record is ENTIRELY the one marker the writer emits as a whole
       rationale — ``VOTE_PARSE_DEFAULT_MARKER`` — and no model body exists to
       contradict it. Every other guard PREPENDS to a body, so a full-record
       chain of any other marker is not evidence of machinery: a bare redirect
       marker sitting beside a different pre-guard body is a disagreement to
       publish, not a record to trust. (A model that authored an empty body is
       already covered by (1), which matches the empty suffix.)

    Failing all three, the record and the model's own call disagree in a way
    this module cannot attribute, so nothing is trusted as machinery: the
    marker region is empty and the ballot is counted in
    ``guard_provenance_unverifiable_ballots``. That direction is deliberate —
    under-counting guard cells is a visible, published loss, whereas trusting
    shape mis-attributes model text as machinery silently.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    marker_region: str
    body_region: str
    model_body: str | None
    verified: bool


# Every redaction body the teammate firewall has written, newest first. A
# recorded rationale is guard-authored when it ends with ANY of them, because
# this module reads FROZEN bytes: recognising only the live value would read a
# past recording through today's vocabulary and file its well-understood
# redactions as unverifiable — the silent under-count the accountability rule
# below exists to prevent. An unrecognised body still falls through to
# unverifiable, so a genuinely new writer-side body surfaces rather than
# passing.
#
# Entries retire when no committed recording carries them. The pre-reword body
# retired at the baseline-8 record: it appeared 36 times across 18 replays of the
# previous recording and appears ZERO times in these bytes, while the live
# constant went 0 -> 14. One entry is the whole history the committed sets need.
_TEAMMATE_COERCED_BODIES: Final[tuple[str, ...]] = (TEAMMATE_COERCED_VOTE_RATIONALE,)


def _split_rationale(rationale: str, model_body: str | None) -> _RationaleSplit:
    """Cut a recorded rationale along its provenance boundary (see the class)."""

    # FIRST, because it settles the model body too. ``_vote_parse_default`` runs
    # in the ``ValidationError`` handler and RETURNS immediately, so the record
    # is that marker ALONE — no other guard ran, and none can have. A chain of
    # several markers ending in a parse default is a shape the writer cannot
    # emit, so it is unverifiable rather than machinery.
    chain = _scan_marker_chain(rationale)
    if (
        chain.parse_default
        and chain.marker_count == 1
        and chain.consumed == len(rationale)
        # ...unless the model's OWN recovered body is the whole record. Then the
        # strongest evidence available says the model authored that text — it
        # quoted the audit literal — and shape must not overrule provenance. The
        # suffix rule below takes it with an empty marker region, so no guard is
        # credited and the model-side nets still read it.
        and model_body != rationale
    ):
        # ``model_body`` is dropped, not passed through. The manager rejected
        # the whole response, so a ``rationale_text`` that happened to parse out
        # of it was DISCARDED — it is not this ballot's pre-guard body, and
        # counting it would let a response the writer threw away re-enter the
        # model-origin metrics through the one ballot that provably has none.
        return _RationaleSplit(
            marker_region=rationale,
            body_region="",
            model_body=None,
            verified=True,
        )
    if model_body is not None and rationale.endswith(model_body):
        cut = len(rationale) - len(model_body)
        prefix = rationale[:cut]
        # The prefix is only THIS codebase's if this codebase can account for
        # all of it. An unrecognised leading marker — a writer-side marker added
        # without updating the table — would otherwise verify while contributing
        # nothing to the census, silently under-counting the guard side. Failing
        # into the published unverifiable bucket surfaces it instead.
        if _scan_marker_chain(prefix).consumed != len(prefix):
            return _RationaleSplit(
                marker_region="",
                body_region=rationale,
                model_body=model_body,
                verified=False,
            )
        return _RationaleSplit(
            marker_region=prefix,
            body_region=model_body,
            model_body=model_body,
            verified=True,
        )
    coerced_body = next(
        (body for body in _TEAMMATE_COERCED_BODIES if rationale.endswith(body)), None
    )
    if coerced_body is not None:
        cut = len(rationale) - len(coerced_body)
        prefix = rationale[:cut]
        # Same accountability rule as the suffix branch above, for the same
        # reason: an unregistered leading marker stops the walk early, so the
        # KNOWN teammate marker behind it would go uncounted while the ballot
        # still read as verified — a silent under-count of exactly the guard
        # whose redaction this branch exists to recognise.
        if _scan_marker_chain(prefix).consumed != len(prefix):
            return _RationaleSplit(
                marker_region="",
                body_region=rationale,
                model_body=model_body,
                verified=False,
            )
        return _RationaleSplit(
            marker_region=prefix,
            body_region=coerced_body,
            model_body=model_body,
            verified=True,
        )
    return _RationaleSplit(
        marker_region="",
        body_region=rationale,
        model_body=model_body,
        verified=False,
    )


def _authored_target(ballot: VoteBallot, chain: _MarkerChain) -> tuple[str, bool]:
    """``(the target the AGENT wrote, whether a guard rewrite was unwound)``.

    ``chain`` is the scan of the ballot's PROVENANCE-established marker region,
    so an unverifiable record contributes no rewrite and the recorded target
    stands. When no rewriting marker is present the recorded target IS the
    authored one.
    """

    if chain.authored_target is None:
        return ballot.target, False
    return chain.authored_target, True


# ---------------------------------------------------------------------------
# Model primitives
# ---------------------------------------------------------------------------


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base (the ``eval/`` report convention)."""

    model_config = ConfigDict(frozen=True, extra="forbid")


def _wilson_interval(
    numerator: int, denominator: int
) -> tuple[float | None, float | None, float | None]:
    """Point rate and Wilson 95% score interval for ``numerator`` of ``denominator``.

    Returns ``(rate, low, high)``; all three are ``None`` when ``denominator``
    is 0 (the None-not-0.0 sentinel this package uses for an undefined rate).
    Pure stdlib ``math`` — no numpy (``numpy`` is confined to ``training/``).
    """

    if denominator == 0:
        return None, None, None
    z = _WILSON_Z
    n = denominator
    p_hat = numerator / n
    denom = 1.0 + z * z / n
    center = (p_hat + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n))
    return p_hat, max(0.0, center - half), min(1.0, center + half)


class WilsonRateCell(_FrozenModel):
    """A rate beside its Wilson 95% score interval (the 18.1 shape).

    ``rate`` / ``wilson_low`` / ``wilson_high`` are ``None`` iff
    ``denominator == 0``. ``advisory`` fires when ``numerator`` is at most
    :data:`_RARE_EVENT_ADVISORY_MAX_NUMERATOR`, flagging that the point rate is
    statistically fragile and the interval should be read instead — the whole
    point on cells like weak-flag-only conviction, whose numerator is 1 on
    ``replays/samples/9p2i``.

    **Leak-safety.** Two ints, three ``float | None`` fields, one bool.
    """

    numerator: int
    denominator: int
    rate: float | None
    wilson_low: float | None
    wilson_high: float | None
    advisory: bool

    @model_validator(mode="after")
    def _validate(self) -> WilsonRateCell:
        if self.numerator < 0 or self.denominator < 0:
            raise ValueError("WilsonRateCell counts must be non-negative")
        if self.numerator > self.denominator:
            raise ValueError(
                "WilsonRateCell numerator cannot exceed denominator: "
                f"{self.numerator} > {self.denominator}"
            )
        expected_rate, expected_low, expected_high = _wilson_interval(
            self.numerator, self.denominator
        )
        # Fail-loud value check (AGENTS.md "no silent fallbacks"): a cell loaded
        # from stale or hand-built JSON must not carry a rate or interval that
        # contradicts its own counts. Exact equality is correct — construction
        # and the JSON round-trip both preserve the identical doubles.
        if (
            self.rate != expected_rate
            or self.wilson_low != expected_low
            or self.wilson_high != expected_high
        ):
            raise ValueError(
                "WilsonRateCell rate/interval must equal the Wilson values "
                f"recomputed from {self.numerator}/{self.denominator}: got "
                f"({self.rate}, {self.wilson_low}, {self.wilson_high}), expected "
                f"({expected_rate}, {expected_low}, {expected_high})"
            )
        if self.advisory != (self.numerator <= _RARE_EVENT_ADVISORY_MAX_NUMERATOR):
            raise ValueError(
                "WilsonRateCell advisory flag must equal numerator <= "
                f"{_RARE_EVENT_ADVISORY_MAX_NUMERATOR}"
            )
        return self


def _cell(numerator: int, denominator: int) -> WilsonRateCell:
    """Build a :class:`WilsonRateCell` with its interval and advisory flag."""

    rate, low, high = _wilson_interval(numerator, denominator)
    return WilsonRateCell(
        numerator=numerator,
        denominator=denominator,
        rate=rate,
        wilson_low=low,
        wilson_high=high,
        advisory=numerator <= _RARE_EVENT_ADVISORY_MAX_NUMERATOR,
    )


def _rate_or_none(numerator: int, denominator: int) -> float | None:
    """``numerator/denominator``, or ``None`` when the denominator is 0."""

    return numerator / denominator if denominator else None


def _require_non_negative(label: str, counts: Sequence[int]) -> None:
    if any(count < 0 for count in counts):
        raise ValueError(f"{label} counts must be non-negative")


# ---------------------------------------------------------------------------
# 1. Evidence taxonomy census
# ---------------------------------------------------------------------------


class EvidenceTaxonomyCensus(_FrozenModel):
    """Every recorded flag, partitioned by :data:`EvidenceCategory` (metric 1).

    Numerator/denominator: each category's count over ``flags_total``, which is
    every :class:`~meetings.schemas.ContradictionRef` in the report. The three
    categories partition the total exactly (enforced below). Cross-pinned
    against ``api.schemas.classify_evidence`` on the same bytes.

    ``meetings_with_any_flag`` is deliberately NOT named ``flagged_meetings``:
    :class:`MeetingFlagCrossTab` owns that name for a DIFFERENT predicate
    (a meeting carrying >= 1 ``role_proof`` flag), and on
    ``replays/samples/9p2i`` the two differ — 100 meetings carry some flag, 70
    carry role proof. One name, two predicates, is how a cross-tab gets
    mis-cited; the rename removes the collision at the source.

    *Does NOT measure* whether a flag was read, was true, or moved a vote.
    """

    flags_total: int
    role_proof_flags: int
    cross_statement_flags: int
    weak_signal_flags: int
    meetings_with_any_flag: int
    weak_signal_share: float | None

    @model_validator(mode="after")
    def _validate(self) -> EvidenceTaxonomyCensus:
        _require_non_negative(
            "evidence-taxonomy",
            (
                self.flags_total,
                self.role_proof_flags,
                self.cross_statement_flags,
                self.weak_signal_flags,
                self.meetings_with_any_flag,
            ),
        )
        parts = (
            self.role_proof_flags + self.cross_statement_flags + self.weak_signal_flags
        )
        if parts != self.flags_total:
            raise ValueError(
                "the three evidence categories must partition flags_total: "
                f"{self.role_proof_flags} + {self.cross_statement_flags} + "
                f"{self.weak_signal_flags} != {self.flags_total}"
            )
        # Every counted meeting contributes >= 1 flag by definition, so a
        # payload claiming more flagged meetings than flags is arithmetically
        # impossible. Without this a hand-edited or stale report validates and
        # is served as evidence.
        if self.meetings_with_any_flag > self.flags_total:
            raise ValueError(
                "meetings_with_any_flag cannot exceed flags_total (each counted "
                f"meeting carries >= 1 flag): {self.meetings_with_any_flag} > "
                f"{self.flags_total}"
            )
        _validate_rate(
            "weak_signal_share",
            self.weak_signal_share,
            self.weak_signal_flags,
            self.flags_total,
        )
        return self


# ---------------------------------------------------------------------------
# 2. Partition A — the MEETING-flag cross-tab
# ---------------------------------------------------------------------------


class MeetingFlagCrossTab(_FrozenModel):
    """Partition A of the headline cross-tab: the unit is the MEETING (metric 2).

    A meeting is FLAGGED iff it carries >= 1 ``role_proof`` flag, whoever that
    flag names. Its ejections are bucketed by that meeting-level status and by
    the ejected player's role.

    Named cells, with their own denominators and nobody else's:

    * ``flagged_meetings`` / ``unflagged_meetings`` partition
      ``meetings_total``.
    * ``flagged_meeting_accuracy`` = ``flagged_ejections_impostor`` over the
      flagged-meeting ejections.
    * ``unflagged_meeting_accuracy`` = ``unflagged_ejections_impostor`` over the
      unflagged-meeting ejections (the triage's 10/31 on samples-9p2i).

    *Does NOT measure* whether the proof named the EJECTED player — that is
    :class:`EjecteeProofCrossTab`, whose denominators are different and must
    never be mixed with these.
    """

    meetings_total: int
    flagged_meetings: int
    unflagged_meetings: int
    flagged_ejections_impostor: int
    flagged_ejections_innocent: int
    unflagged_ejections_impostor: int
    unflagged_ejections_innocent: int
    flagged_meeting_accuracy: WilsonRateCell
    unflagged_meeting_accuracy: WilsonRateCell

    @model_validator(mode="after")
    def _validate(self) -> MeetingFlagCrossTab:
        _require_non_negative(
            "meeting-flag cross-tab",
            (
                self.meetings_total,
                self.flagged_meetings,
                self.unflagged_meetings,
                self.flagged_ejections_impostor,
                self.flagged_ejections_innocent,
                self.unflagged_ejections_impostor,
                self.unflagged_ejections_innocent,
            ),
        )
        if self.flagged_meetings + self.unflagged_meetings != self.meetings_total:
            raise ValueError(
                "flagged + unflagged meetings must equal meetings_total: "
                f"{self.flagged_meetings} + {self.unflagged_meetings} != "
                f"{self.meetings_total}"
            )
        # A ``MeetingReport`` carries exactly one outcome, so a meeting
        # contributes at most one ejection. Each side's ejections are therefore
        # bounded by its own meeting count — the bound that stops "1 flagged
        # meeting, 100 flagged ejections" from being served as a cross-tab.
        for side, ejections, meetings in (
            (
                "flagged",
                self.flagged_ejections_impostor + self.flagged_ejections_innocent,
                self.flagged_meetings,
            ),
            (
                "unflagged",
                self.unflagged_ejections_impostor + self.unflagged_ejections_innocent,
                self.unflagged_meetings,
            ),
        ):
            if ejections > meetings:
                raise ValueError(
                    f"{side} ejections cannot exceed {side} meetings (one outcome "
                    f"per meeting): {ejections} > {meetings}"
                )
        _validate_cell_against(
            "flagged_meeting_accuracy",
            self.flagged_meeting_accuracy,
            self.flagged_ejections_impostor,
            self.flagged_ejections_impostor + self.flagged_ejections_innocent,
        )
        _validate_cell_against(
            "unflagged_meeting_accuracy",
            self.unflagged_meeting_accuracy,
            self.unflagged_ejections_impostor,
            self.unflagged_ejections_impostor + self.unflagged_ejections_innocent,
        )
        return self


# ---------------------------------------------------------------------------
# 3. Partition B — the EJECTEE-specific-proof cross-tab
# ---------------------------------------------------------------------------


class EjecteeProofCrossTab(_FrozenModel):
    """Partition B of the headline cross-tab: the unit is the EJECTION (metric 3).

    An ejection is PROOF-PRESENT iff the ejected player is a subject of >= 1
    ``role_proof`` flag in the meeting that ejected them.

    * ``proof_present_ejections`` + ``non_direct_ejections`` ==
      ``ejections_total``.
    * ``direct_proof_accuracy`` = ``proof_present_impostor`` over
      ``proof_present_ejections``.
    * ``non_direct_accuracy`` = ``non_direct_impostor`` over
      ``non_direct_ejections`` (the triage's 10/33 = 30.3% on samples-9p2i,
      35/89 = 39.3% on the corpus twin).

    *Does NOT measure* meeting-level proof availability (that is
    :class:`MeetingFlagCrossTab`), and does NOT claim the proof CAUSED the
    ejection — the cell is co-occurrence inside one meeting, which is why it is
    named "proof-present" and not "proof-driven".
    """

    ejections_total: int
    proof_present_ejections: int
    proof_present_impostor: int
    proof_present_innocent: int
    non_direct_ejections: int
    non_direct_impostor: int
    non_direct_innocent: int
    direct_proof_accuracy: WilsonRateCell
    non_direct_accuracy: WilsonRateCell

    @model_validator(mode="after")
    def _validate(self) -> EjecteeProofCrossTab:
        _require_non_negative(
            "ejectee-proof cross-tab",
            (
                self.ejections_total,
                self.proof_present_ejections,
                self.proof_present_impostor,
                self.proof_present_innocent,
                self.non_direct_ejections,
                self.non_direct_impostor,
                self.non_direct_innocent,
            ),
        )
        if (
            self.proof_present_ejections + self.non_direct_ejections
            != self.ejections_total
        ):
            raise ValueError(
                "proof-present + non-direct must equal ejections_total: "
                f"{self.proof_present_ejections} + {self.non_direct_ejections} != "
                f"{self.ejections_total}"
            )
        if (
            self.proof_present_impostor + self.proof_present_innocent
            != self.proof_present_ejections
        ):
            raise ValueError(
                "the proof-present role split must sum to proof_present_ejections: "
                f"{self.proof_present_impostor} + {self.proof_present_innocent} != "
                f"{self.proof_present_ejections}"
            )
        if (
            self.non_direct_impostor + self.non_direct_innocent
            != self.non_direct_ejections
        ):
            raise ValueError(
                "the non-direct role split must sum to non_direct_ejections: "
                f"{self.non_direct_impostor} + {self.non_direct_innocent} != "
                f"{self.non_direct_ejections}"
            )
        _validate_cell_against(
            "direct_proof_accuracy",
            self.direct_proof_accuracy,
            self.proof_present_impostor,
            self.proof_present_ejections,
        )
        _validate_cell_against(
            "non_direct_accuracy",
            self.non_direct_accuracy,
            self.non_direct_impostor,
            self.non_direct_ejections,
        )
        return self


# ---------------------------------------------------------------------------
# 4. Weak-flag-only conviction
# ---------------------------------------------------------------------------


class WeakFlagConvictionCells(_FrozenModel):
    """Convictions resting on nothing but detector-stamped weak signals (metric 4).

    Numerator ``weak_flag_only_convictions``: ejections whose ejectee is named
    by >= 1 flag and where EVERY flag naming them classifies ``weak_signal``.
    Denominator ``flag_named_ejections``: ejections whose ejectee is named by
    >= 1 flag of any category. The innocent share of the numerator rides beside
    it because that is the harm the audits traced.

    *Does NOT measure* whether a voter cited the weak flag, and does NOT claim
    causation — only that no stronger evidence NAMED the person who was ejected.
    """

    flag_named_ejections: int
    weak_flag_only_convictions: int
    weak_flag_only_impostor: int
    weak_flag_only_innocent: int
    weak_flag_only_rate: WilsonRateCell
    weak_flag_only_innocent_share: WilsonRateCell

    @model_validator(mode="after")
    def _validate(self) -> WeakFlagConvictionCells:
        _require_non_negative(
            "weak-flag conviction",
            (
                self.flag_named_ejections,
                self.weak_flag_only_convictions,
                self.weak_flag_only_impostor,
                self.weak_flag_only_innocent,
            ),
        )
        if (
            self.weak_flag_only_impostor + self.weak_flag_only_innocent
            != self.weak_flag_only_convictions
        ):
            raise ValueError(
                "the weak-flag-only role split must sum to the conviction count: "
                f"{self.weak_flag_only_impostor} + {self.weak_flag_only_innocent} "
                f"!= {self.weak_flag_only_convictions}"
            )
        _validate_cell_against(
            "weak_flag_only_rate",
            self.weak_flag_only_rate,
            self.weak_flag_only_convictions,
            self.flag_named_ejections,
        )
        _validate_cell_against(
            "weak_flag_only_innocent_share",
            self.weak_flag_only_innocent_share,
            self.weak_flag_only_innocent,
            self.weak_flag_only_convictions,
        )
        return self


# ---------------------------------------------------------------------------
# 5. Turn -> ballot consistency
# ---------------------------------------------------------------------------


class TurnBallotConsistencyCells(_FrozenModel):
    """Did the speaker vote the way they spoke? (metric 5).

    Scored against the AUTHORED target — the one the agent wrote, recovered
    from the guard marker whenever a deterministic guard rewrote
    ``VoteBallot.target``. The metric is same-AGENT by name, so charging the
    guard's redirect to the agent would both misattribute it and double-count
    it against the redirect census (:class:`RedirectedBallotCells`).
    ``guard_rewritten_ballots_unwound`` publishes how many scored ballots that
    unwind touched (16 of 777 on ``replays/samples/9p2i``).

    Denominator ``accusing_ballots``: (meeting, voter) pairs where the voter
    cast a ballot, spoke >= 1 accusing turn, and accused >= 1 VOTABLE player
    (votable = cast a ballot in that meeting). The four outcome buckets
    partition it exactly.

    Scored against each voter's LEGAL target set — the living roster minus
    THEMSELVES, mirroring ``meetings.manager._candidate_targets``. A player
    cannot vote for themselves, so a self-accusation names nobody they could
    lawfully eject: it cannot put a ballot in the denominator, and a self-target
    can never score consistent.

    ``inconsistent_invalid_target_ballots`` is the unlawful-target shape: the
    authored target is not in the voter's legal set — a hallucinated id, or the
    voter themselves — so they neither voted their accusation nor voted anyone
    else. It is its own bucket rather than folded into either neighbour, because
    both foldings would misdescribe it (3 on ``replays/samples/9p2i``, 0
    elsewhere).

    ``excluded_no_votable_target_ballots`` is the SKIP-tolerance clause made
    visible: accusing ballots whose every accused player was non-votable are
    dropped from the denominator rather than scored, because a SKIP is then the
    only lawful ballot. ``accusations_of_non_votable_targets`` counts the
    accusation claims that name a non-votable player at all. Both are 0 on every
    committed set — the clause is structural, not empirically load-bearing on
    these bytes, and publishing the zeros is how that stays checkable.

    *Does NOT measure* correctness of either the accusation or the vote, nor
    whether the guard's rewrite was right, and deliberately scores an honest
    mid-meeting revision as an inconsistency: it measures follow-through, not
    virtue.
    """

    accusations_total: int
    accusations_of_non_votable_targets: int
    accusing_ballots: int
    consistent_ballots: int
    inconsistent_skip_ballots: int
    inconsistent_other_target_ballots: int
    inconsistent_invalid_target_ballots: int
    excluded_no_votable_target_ballots: int
    guard_rewritten_ballots_unwound: int
    consistency_rate: float | None

    @model_validator(mode="after")
    def _validate(self) -> TurnBallotConsistencyCells:
        _require_non_negative(
            "turn->ballot consistency",
            (
                self.accusations_total,
                self.accusations_of_non_votable_targets,
                self.accusing_ballots,
                self.consistent_ballots,
                self.inconsistent_skip_ballots,
                self.inconsistent_other_target_ballots,
                self.inconsistent_invalid_target_ballots,
                self.excluded_no_votable_target_ballots,
                self.guard_rewritten_ballots_unwound,
            ),
        )
        parts = (
            self.consistent_ballots
            + self.inconsistent_skip_ballots
            + self.inconsistent_other_target_ballots
            + self.inconsistent_invalid_target_ballots
        )
        if parts != self.accusing_ballots:
            raise ValueError(
                "the consistency buckets must partition accusing_ballots: "
                f"{self.consistent_ballots} + {self.inconsistent_skip_ballots} + "
                f"{self.inconsistent_other_target_ballots} + "
                f"{self.inconsistent_invalid_target_ballots} != "
                f"{self.accusing_ballots}"
            )
        if self.guard_rewritten_ballots_unwound > self.accusing_ballots:
            raise ValueError(
                "unwound ballots cannot exceed the scored denominator: "
                f"{self.guard_rewritten_ballots_unwound} > {self.accusing_ballots}"
            )
        if self.accusations_of_non_votable_targets > self.accusations_total:
            raise ValueError(
                "non-votable accusation targets cannot exceed accusations_total: "
                f"{self.accusations_of_non_votable_targets} > {self.accusations_total}"
            )
        _validate_rate(
            "consistency_rate",
            self.consistency_rate,
            self.consistent_ballots,
            self.accusing_ballots,
        )
        return self


# ---------------------------------------------------------------------------
# 6. Public response coverage split by role
# ---------------------------------------------------------------------------


class PublicResponseCoverageCells(_FrozenModel):
    """Roll-call answer coverage, split by role, under TWO estimators (metric 6).

    Numerator: transcript turns carrying a structured
    :class:`~meetings.schemas.WhereaboutsClaim`. Denominator: that role's
    transcript turns. Both estimators ship under distinct names because the
    triage's source figure and Task 19.8's recount are the same bytes read two
    ways (verify-then-fix):

    * pooled — over turns (49.0% impostor on samples-9p2i);
    * macro-average — unweighted mean of the per-meeting shares over meetings
      where the role spoke at all (45.45% impostor on the same bytes, which is
      the triage's "45.5%").

    *Does NOT measure* whether the answer was TRUE, and is NOT a firewall leak:
    it is a behavioural tell produced by the templates' role-differentiated
    output contract.
    """

    crew_turns: int
    crew_turns_with_whereabouts: int
    crew_pooled_coverage: float | None
    crew_macro_average_coverage: float | None
    crew_macro_meetings: int
    impostor_turns: int
    impostor_turns_with_whereabouts: int
    impostor_pooled_coverage: float | None
    impostor_macro_average_coverage: float | None
    impostor_macro_meetings: int

    @model_validator(mode="after")
    def _validate(self) -> PublicResponseCoverageCells:
        _require_non_negative(
            "public-response coverage",
            (
                self.crew_turns,
                self.crew_turns_with_whereabouts,
                self.crew_macro_meetings,
                self.impostor_turns,
                self.impostor_turns_with_whereabouts,
                self.impostor_macro_meetings,
            ),
        )
        if self.crew_turns_with_whereabouts > self.crew_turns:
            raise ValueError(
                "crew whereabouts turns cannot exceed crew turns: "
                f"{self.crew_turns_with_whereabouts} > {self.crew_turns}"
            )
        if self.impostor_turns_with_whereabouts > self.impostor_turns:
            raise ValueError(
                "impostor whereabouts turns cannot exceed impostor turns: "
                f"{self.impostor_turns_with_whereabouts} > {self.impostor_turns}"
            )
        _validate_rate(
            "crew_pooled_coverage",
            self.crew_pooled_coverage,
            self.crew_turns_with_whereabouts,
            self.crew_turns,
        )
        _validate_rate(
            "impostor_pooled_coverage",
            self.impostor_pooled_coverage,
            self.impostor_turns_with_whereabouts,
            self.impostor_turns,
        )
        for name, macro, meetings in (
            (
                "crew_macro_average_coverage",
                self.crew_macro_average_coverage,
                self.crew_macro_meetings,
            ),
            (
                "impostor_macro_average_coverage",
                self.impostor_macro_average_coverage,
                self.impostor_macro_meetings,
            ),
        ):
            if meetings == 0 and macro is not None:
                raise ValueError(f"{name} must be None when its meeting count is 0")
            if meetings > 0 and macro is None:
                raise ValueError(f"{name} must be defined when meetings were counted")
        return self


# ---------------------------------------------------------------------------
# 7. Engine-redirected ballot share
# ---------------------------------------------------------------------------


class RedirectedBallotCells(_FrozenModel):
    """How much of the ballot record the deterministic vote guard re-aimed (metric 7).

    Numerator ``redirected_ballots``: ballots whose ``rationale_text`` carries
    the pinned :data:`~meetings.manager.BALLOT_TARGET_REDIRECT_MARKER` prefix.
    Denominator ``ballots_total``: every recorded ballot. The count splits by the
    RECORDED target — an eject the guard re-aimed vs a ballot coerced to SKIP —
    and the two sum to the total.

    *Does NOT measure* whether a redirect changed the meeting's OUTCOME: that
    needs a counterfactual tally the recorded bytes cannot supply.
    """

    ballots_total: int
    redirected_ballots: int
    redirected_eject_ballots: int
    redirect_coerced_skip_ballots: int
    redirected_ballot_share: float | None

    @model_validator(mode="after")
    def _validate(self) -> RedirectedBallotCells:
        _require_non_negative(
            "redirected-ballot",
            (
                self.ballots_total,
                self.redirected_ballots,
                self.redirected_eject_ballots,
                self.redirect_coerced_skip_ballots,
            ),
        )
        parts = self.redirected_eject_ballots + self.redirect_coerced_skip_ballots
        if parts != self.redirected_ballots:
            raise ValueError(
                "eject + coerced-skip must equal redirected_ballots: "
                f"{self.redirected_eject_ballots} + "
                f"{self.redirect_coerced_skip_ballots} != {self.redirected_ballots}"
            )
        if self.redirected_ballots > self.ballots_total:
            raise ValueError(
                "redirected_ballots cannot exceed ballots_total: "
                f"{self.redirected_ballots} > {self.ballots_total}"
            )
        _validate_rate(
            "redirected_ballot_share",
            self.redirected_ballot_share,
            self.redirected_ballots,
            self.ballots_total,
        )
        return self


# ---------------------------------------------------------------------------
# 8. Scaffold leakage, split by origin
# ---------------------------------------------------------------------------


class ScaffoldLeakageCells(_FrozenModel):
    """Fourth-wall leakage, split by ORIGIN rather than pooled (metric 8).

    **Source, by origin — and the boundary is provenance, not pattern.** Each
    recorded rationale is cut by :func:`_split_rationale` into the machinery's
    marker region and the body, using the model's own pre-guard text as the
    boundary. GUARD-originated cells scan the MARKER REGION for markers (never
    its payloads, which carry model-supplied targets and raw response heads);
    ``guard_preserved_omniscient_ballots`` scans the recorded BODY;
    MODEL-originated cells scan the PRE-GUARD body parsed out of the voter's own
    vote-call response (:func:`_model_authored_bodies`) and nothing else,
    because Task 19.15's teammate coercion REPLACES the recorded rationale
    before the ballot is stored: a future teammate-aimed ballot disclosing a
    partner would read clean on the recorded surface and the metric would
    under-count exactly the class the redaction removes.

    A ballot with no pre-guard body scans NOTHING model-side rather than falling
    back to the record — a parse-default ballot's record is a bounded head of
    the unparseable JSON envelope, whose ``"confidence": 0.NN`` the machinery
    net would read as the model quoting its own scoring grid.
    ``model_source_pre_guard_ballots`` / ``model_source_unavailable_ballots``
    and ``guard_provenance_verified_ballots`` /
    ``guard_provenance_unverifiable_ballots`` each partition ``ballots_total``,
    so both boundaries are counted, never silent (0 unavailable and 0
    unverifiable on all four committed sets, where every cell equals its
    whole-record reading).

    MODEL-originated ROLE/omniscience (the model authored the text); all three
    nets are over ``impostor_ballots``:

    * ``model_partner_naming_ballots`` — matches :data:`PARTNER_PHRASES`.
    * ``model_role_statement_ballots`` — matches :data:`ROLE_STATEMENT_PHRASES`.
    * ``model_self_kill_disclosure_ballots`` — matches
      :data:`SELF_KILL_PHRASES` (a voter narrating their OWN kill).
    * ``model_omniscient_ballots`` — the UNION of the three. A ballot can hit
      several nets, so this is deliberately not their sum; it is the count the
      guard-side cell below is scoped against.
    * ``crew_partner_naming_ballots`` / ``crew_omniscient_control_ballots`` —
      the false-positive CONTROLS over ``crew_ballots``. Re-derived over the
      committed reports: partner 0 on all four sets, omniscient 1 on each 9p2i
      set and 0 on each 4p1i set.
    * ``player_visible_leak_turns`` — the partner net over player-visible
      ``free_text``; denominator ``turns_total``.

    MODEL-originated MACHINERY (over ALL ballots — machinery talk is
    role-independent):

    * ``model_machinery_quotation_ballots`` — a quoted internal decimal
      (:data:`MACHINERY_DECIMAL_PATTERN`). Unambiguous: two decimals is the grid
      the frozen vote template renders.
    * ``model_machinery_vocabulary_ballots`` — :data:`MACHINERY_VOCABULARY`, an
      explicit UPPER BOUND rather than a leak count, kept labelled instead of
      being promoted or dropped.
    * ``model_oracle_register_ballots`` / ``oracle_register_turns`` /
      ``oracle_register_claim_reasons`` — :data:`MACHINERY_ORACLE_PATTERNS` over
      the three surfaces a player speaks on: the pre-guard ballot body, turn
      ``free_text``, and the ``reason`` of an accusation or corroboration claim.
      Denominators ``ballots_total``, ``turns_total`` and
      ``claim_reasons_total``. Unlike the vocabulary net this register has no
      innocent in-world reading, so these are leak counts. ``AlibiClaim`` is not
      scanned: it carries ``evidence``, not ``reason``, and the register is
      absent from every committed ``evidence`` string.

    GUARD-originated (the deterministic machinery injected the text):

    * ``guard_marked_ballots`` — any pinned manager/voting marker in the
      provenance-established marker region (never a substring of the model's
      body, and never marker-shaped prose the model opened with).
    * ``guard_target_rewrite_ballots`` — the subset whose TARGET the guard
      rewrote.
    * ``guard_preserved_omniscient_ballots`` / ``guard_preserved_omniscient_rate``
      — target-rewritten ballots whose recorded BODY still carries ANY
      omniscient phrase, over the ``guard_target_rewrite_ballots`` denominator.
      The recorded body, never the pre-guard one: "preserved" means what
      SURVIVED into the record, so scoring the model's original here would
      report Task 19.15's redaction as a preservation of the very text it
      removes. The body, never the whole record: a marker payload holds the
      model's own words (a hallucinated target reading "p-2 is my partner" is
      interpolated verbatim), and billing those to the machinery would invent
      guard-originated leakage out of model-originated text.
      This is exactly the class Task 19.15 redacts going forward. It is 1/53 on
      ``replays/ml_corpus/9p2i`` (seed 1118 meeting 0) and 0 on the other three
      sets: rare on committed bytes, NOT absent. The rate ships as its own cell
      because ``guard_marked_ballot_share`` answers a different question over a
      different denominator (55/2,726 on the same set) and cannot stand in for
      it.

    *Does NOT measure* paraphrase, and does NOT claim the nets are exhaustive: a
    substring/regex net is an upper bound on intent and a lower bound on
    leakage. The partner, role, decimal and vocabulary nets are Task 19.8's,
    carried verbatim so the two surfaces cannot drift; the self-kill net is new
    here.
    """

    ballots_total: int
    impostor_ballots: int
    crew_ballots: int
    turns_total: int
    model_partner_naming_ballots: int
    model_role_statement_ballots: int
    model_self_kill_disclosure_ballots: int
    model_omniscient_ballots: int
    crew_partner_naming_ballots: int
    crew_omniscient_control_ballots: int
    player_visible_leak_turns: int
    model_partner_naming_rate: WilsonRateCell
    model_omniscient_rate: WilsonRateCell
    model_machinery_quotation_ballots: int
    model_machinery_vocabulary_ballots: int
    model_machinery_quotation_share: float | None
    claim_reasons_total: int
    model_oracle_register_ballots: int
    oracle_register_turns: int
    oracle_register_claim_reasons: int
    model_source_pre_guard_ballots: int
    model_source_unavailable_ballots: int
    guard_provenance_verified_ballots: int
    guard_provenance_unverifiable_ballots: int
    guard_marked_ballots: int
    guard_target_rewrite_ballots: int
    guard_preserved_omniscient_ballots: int
    guard_preserved_omniscient_rate: WilsonRateCell
    guard_marked_ballot_share: float | None

    @model_validator(mode="after")
    def _validate(self) -> ScaffoldLeakageCells:
        _require_non_negative(
            "scaffold-leakage",
            (
                self.ballots_total,
                self.impostor_ballots,
                self.crew_ballots,
                self.turns_total,
                self.model_partner_naming_ballots,
                self.model_role_statement_ballots,
                self.model_self_kill_disclosure_ballots,
                self.model_omniscient_ballots,
                self.crew_partner_naming_ballots,
                self.crew_omniscient_control_ballots,
                self.player_visible_leak_turns,
                self.model_machinery_quotation_ballots,
                self.model_machinery_vocabulary_ballots,
                self.claim_reasons_total,
                self.model_oracle_register_ballots,
                self.oracle_register_turns,
                self.oracle_register_claim_reasons,
                self.model_source_pre_guard_ballots,
                self.model_source_unavailable_ballots,
                self.guard_provenance_verified_ballots,
                self.guard_provenance_unverifiable_ballots,
                self.guard_marked_ballots,
                self.guard_target_rewrite_ballots,
                self.guard_preserved_omniscient_ballots,
            ),
        )
        if (
            self.model_source_pre_guard_ballots + self.model_source_unavailable_ballots
            != self.ballots_total
        ):
            raise ValueError(
                "the model-source provenance split must span every ballot: "
                f"{self.model_source_pre_guard_ballots} + "
                f"{self.model_source_unavailable_ballots} != "
                f"{self.ballots_total}"
            )
        if (
            self.guard_provenance_verified_ballots
            + self.guard_provenance_unverifiable_ballots
            != self.ballots_total
        ):
            raise ValueError(
                "the guard-provenance split must span every ballot: "
                f"{self.guard_provenance_verified_ballots} + "
                f"{self.guard_provenance_unverifiable_ballots} != "
                f"{self.ballots_total}"
            )
        if self.guard_marked_ballots > self.guard_provenance_verified_ballots:
            raise ValueError(
                "a guard marker can only be counted where its provenance was "
                f"established: {self.guard_marked_ballots} marked > "
                f"{self.guard_provenance_verified_ballots} verified"
            )
        # The union is bounded below by each net and above by their sum: a
        # ballot may hit several, so equality with the sum is NOT required, but
        # a union smaller than its largest member (or larger than the total)
        # would be arithmetically impossible.
        widest_net = max(
            self.model_partner_naming_ballots,
            self.model_role_statement_ballots,
            self.model_self_kill_disclosure_ballots,
        )
        net_sum = (
            self.model_partner_naming_ballots
            + self.model_role_statement_ballots
            + self.model_self_kill_disclosure_ballots
        )
        if not widest_net <= self.model_omniscient_ballots <= net_sum:
            raise ValueError(
                "model_omniscient_ballots must lie between its widest net and "
                f"the net sum: {widest_net} <= {self.model_omniscient_ballots} "
                f"<= {net_sum} is false"
            )
        if self.crew_partner_naming_ballots > self.crew_omniscient_control_ballots:
            raise ValueError(
                "the crew partner control is a subset of the crew omniscient "
                f"control: {self.crew_partner_naming_ballots} > "
                f"{self.crew_omniscient_control_ballots}"
            )
        # The impostor and crew nets draw from DISJOINT halves of one readable
        # pool, so their per-role minima do not constrain them jointly: a block
        # could otherwise claim more role-split matches than there were bodies
        # to match against, which is exactly how a corrupt payload hides a
        # non-zero crew control (the cell whose whole job is to read 0).
        for label, impostor_side, crew_side in (
            (
                "omniscient",
                self.model_omniscient_ballots,
                self.crew_omniscient_control_ballots,
            ),
            (
                "partner-naming",
                self.model_partner_naming_ballots,
                self.crew_partner_naming_ballots,
            ),
        ):
            if impostor_side + crew_side > self.model_source_pre_guard_ballots:
                raise ValueError(
                    f"the {label} nets are role-disjoint, so they cannot jointly "
                    "exceed the ballots with a readable body: "
                    f"{impostor_side} + {crew_side} > "
                    f"{self.model_source_pre_guard_ballots}"
                )
        if self.impostor_ballots + self.crew_ballots != self.ballots_total:
            raise ValueError(
                "impostor + crew ballots must equal ballots_total: "
                f"{self.impostor_ballots} + {self.crew_ballots} != "
                f"{self.ballots_total}"
            )
        # Every model-originated BALLOT net increments only while scanning a
        # pre-guard body, so no such count can exceed the ballots that had one.
        # Without this the report could serve "0 readable model ballots" beside
        # positive model leakage — an impossible pair the fold cannot produce.
        # ``player_visible_leak_turns`` is deliberately NOT bounded this way: it
        # is the partner net over turn ``free_text``, not over a ballot body.
        readable = self.model_source_pre_guard_ballots
        for label, count, limit in (
            (
                "model_partner_naming_ballots",
                self.model_partner_naming_ballots,
                min(self.impostor_ballots, readable),
            ),
            (
                "model_role_statement_ballots",
                self.model_role_statement_ballots,
                min(self.impostor_ballots, readable),
            ),
            (
                "model_self_kill_disclosure_ballots",
                self.model_self_kill_disclosure_ballots,
                min(self.impostor_ballots, readable),
            ),
            (
                "model_omniscient_ballots",
                self.model_omniscient_ballots,
                min(self.impostor_ballots, readable),
            ),
            (
                "crew_partner_naming_ballots",
                self.crew_partner_naming_ballots,
                min(self.crew_ballots, readable),
            ),
            (
                "crew_omniscient_control_ballots",
                self.crew_omniscient_control_ballots,
                min(self.crew_ballots, readable),
            ),
            (
                "player_visible_leak_turns",
                self.player_visible_leak_turns,
                self.turns_total,
            ),
            (
                "model_machinery_quotation_ballots",
                self.model_machinery_quotation_ballots,
                readable,
            ),
            (
                "model_machinery_vocabulary_ballots",
                self.model_machinery_vocabulary_ballots,
                readable,
            ),
            (
                "model_oracle_register_ballots",
                self.model_oracle_register_ballots,
                readable,
            ),
            ("oracle_register_turns", self.oracle_register_turns, self.turns_total),
            (
                "oracle_register_claim_reasons",
                self.oracle_register_claim_reasons,
                self.claim_reasons_total,
            ),
            ("guard_marked_ballots", self.guard_marked_ballots, self.ballots_total),
            (
                "guard_target_rewrite_ballots",
                self.guard_target_rewrite_ballots,
                self.guard_marked_ballots,
            ),
            (
                "guard_preserved_omniscient_ballots",
                self.guard_preserved_omniscient_ballots,
                self.guard_target_rewrite_ballots,
            ),
        ):
            if count > limit:
                raise ValueError(
                    f"{label} cannot exceed its denominator: {count} > {limit}"
                )
        _validate_cell_against(
            "model_partner_naming_rate",
            self.model_partner_naming_rate,
            self.model_partner_naming_ballots,
            self.impostor_ballots,
        )
        _validate_cell_against(
            "model_omniscient_rate",
            self.model_omniscient_rate,
            self.model_omniscient_ballots,
            self.impostor_ballots,
        )
        _validate_rate(
            "model_machinery_quotation_share",
            self.model_machinery_quotation_share,
            self.model_machinery_quotation_ballots,
            self.ballots_total,
        )
        _validate_cell_against(
            "guard_preserved_omniscient_rate",
            self.guard_preserved_omniscient_rate,
            self.guard_preserved_omniscient_ballots,
            self.guard_target_rewrite_ballots,
        )
        _validate_rate(
            "guard_marked_ballot_share",
            self.guard_marked_ballot_share,
            self.guard_marked_ballots,
            self.ballots_total,
        )
        return self


# ---------------------------------------------------------------------------
# 9. Witnessed / co-present evidence supply (ADOPTED)
# ---------------------------------------------------------------------------


class KillCraftSupplyCells(Protocol):
    """The three cells this module ADOPTS from ``eval.kill_craft.KillCraftReport``.

    A Protocol, not an import: :mod:`eval.kill_craft` reaches
    :mod:`api.replay_loader` transitively, which imports
    :mod:`eval.meeting_quality`, which imports this module — so importing the
    concrete report here would close a cycle. Structural typing keeps the
    adoption checked by mypy without the edge.
    """

    @property
    def kills_total(self) -> int: ...

    @property
    def crew_witnessed_kills(self) -> int: ...

    @property
    def co_present_histogram(self) -> Mapping[int, int]: ...


class WitnessedSupplyCells(_FrozenModel):
    """The kill-scene evidence SUPPLY, adopted from the kill-craft fold (metric 9).

    Every count comes from :func:`eval.kill_craft.compute_kill_craft_report`
    (Task 18.2) and is never recomputed here: ``kills_total`` and
    ``crew_witnessed_kills`` verbatim, ``co_present_crew_kills`` as the sum of
    the fold's ``co_present_histogram`` above bucket 0 (kills with >= 1
    non-victim living crewmate co-present at the pre-advance decision frame).

    This is the supply side of deduction — how much direct kill testimony the
    corpus offers at all. On every committed set ``co_present_crew_kills`` is 0:
    the scripted impostor only kills isolated targets, so convictions ride the
    post-kill vent tell instead.

    *Does NOT measure* whether that testimony was used, spoken, or believed.
    """

    kills_total: int
    crew_witnessed_kills: int
    co_present_crew_kills: int
    crew_witnessed_kill_rate: WilsonRateCell
    co_present_crew_kill_rate: WilsonRateCell

    @model_validator(mode="after")
    def _validate(self) -> WitnessedSupplyCells:
        _require_non_negative(
            "witnessed-supply",
            (self.kills_total, self.crew_witnessed_kills, self.co_present_crew_kills),
        )
        _validate_cell_against(
            "crew_witnessed_kill_rate",
            self.crew_witnessed_kill_rate,
            self.crew_witnessed_kills,
            self.kills_total,
        )
        _validate_cell_against(
            "co_present_crew_kill_rate",
            self.co_present_crew_kill_rate,
            self.co_present_crew_kills,
            self.kills_total,
        )
        return self


def witnessed_supply_from_kill_craft(
    kill_craft: KillCraftSupplyCells,
) -> WitnessedSupplyCells:
    """Adopt a kill-craft report's supply cells (no metric is recomputed)."""

    co_present = sum(
        count for bucket, count in kill_craft.co_present_histogram.items() if bucket > 0
    )
    kills = kill_craft.kills_total
    return WitnessedSupplyCells(
        kills_total=kills,
        crew_witnessed_kills=kill_craft.crew_witnessed_kills,
        co_present_crew_kills=co_present,
        crew_witnessed_kill_rate=_cell(kill_craft.crew_witnessed_kills, kills),
        co_present_crew_kill_rate=_cell(co_present, kills),
    )


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------


class DeductionMetricsReport(_FrozenModel):
    """What "deduction" means on one replay set, instrumented (Task 19.14).

    A pure fold of an assembled :class:`~eval.report_schema.TournamentReport`
    into the nine metric families defined in the module docstring, each with its
    own denominators. ``witnessed_supply`` is ``None`` when no kill-craft report
    was supplied to :func:`compute_deduction_metrics` — the explicit
    "not supplied" sentinel, never a zero that would read as "no kills".

    **Leak-safety.** Ints, ``float | None`` rates, bools, and nested frozen
    count-only cells — no roles, transcripts, player ids, or engine-owned types.
    """

    games_total: int
    meetings_total: int
    ejections_total: int
    ballots_total: int
    turns_total: int
    evidence_taxonomy: EvidenceTaxonomyCensus
    meeting_flag_cross_tab: MeetingFlagCrossTab
    ejectee_proof_cross_tab: EjecteeProofCrossTab
    weak_flag_conviction: WeakFlagConvictionCells
    turn_ballot_consistency: TurnBallotConsistencyCells
    public_response_coverage: PublicResponseCoverageCells
    redirected_ballots: RedirectedBallotCells
    scaffold_leakage: ScaffoldLeakageCells
    witnessed_supply: WitnessedSupplyCells | None = None

    @model_validator(mode="after")
    def _validate(self) -> DeductionMetricsReport:
        _require_non_negative(
            "deduction-metric",
            (
                self.games_total,
                self.meetings_total,
                self.ejections_total,
                self.ballots_total,
                self.turns_total,
            ),
        )
        # The ONE thing the two partitions share is the ejection total. Their
        # SPLITS are different by construction and are never reconciled — that
        # is the C5 define-before-counting rule made mechanical.
        if self.meeting_flag_cross_tab.meetings_total != self.meetings_total:
            raise ValueError(
                "the meeting-flag partition must span every meeting: "
                f"{self.meeting_flag_cross_tab.meetings_total} != {self.meetings_total}"
            )
        # The census counts a SUBSET of the same meetings, so it cannot exceed
        # them. Its own validator bounds it against flags_total; the report is
        # the only place that knows the meeting denominator.
        if self.evidence_taxonomy.meetings_with_any_flag > self.meetings_total:
            raise ValueError(
                "meetings_with_any_flag cannot exceed the meetings folded: "
                f"{self.evidence_taxonomy.meetings_with_any_flag} > "
                f"{self.meetings_total}"
            )
        # Partition A's FLAGGED predicate and the census's ROLE-PROOF category
        # are the same ``classify_flag(...) == "role_proof"`` test read at two
        # granularities, and each flagged meeting contributes >= 1 such flag. So
        # the two headline views cannot contradict each other about whether role
        # proof exists — without this, the committed 9p2i payload still
        # validates with role_proof_flags zeroed and flagged_meetings left at 70.
        flagged = self.meeting_flag_cross_tab.flagged_meetings
        if flagged > self.evidence_taxonomy.role_proof_flags:
            raise ValueError(
                "a flagged meeting carries >= 1 role-proof flag, so flagged "
                f"meetings cannot exceed them: {flagged} > "
                f"{self.evidence_taxonomy.role_proof_flags}"
            )
        if flagged > self.evidence_taxonomy.meetings_with_any_flag:
            raise ValueError(
                "role-proof-flagged meetings are a subset of the meetings "
                f"carrying any flag: {flagged} > "
                f"{self.evidence_taxonomy.meetings_with_any_flag}"
            )
        flagged_ejections = (
            self.meeting_flag_cross_tab.flagged_ejections_impostor
            + self.meeting_flag_cross_tab.flagged_ejections_innocent
            + self.meeting_flag_cross_tab.unflagged_ejections_impostor
            + self.meeting_flag_cross_tab.unflagged_ejections_innocent
        )
        if flagged_ejections != self.ejections_total:
            raise ValueError(
                "the meeting-flag partition must span every ejection: "
                f"{flagged_ejections} != {self.ejections_total}"
            )
        if self.ejectee_proof_cross_tab.ejections_total != self.ejections_total:
            raise ValueError(
                "the ejectee-proof partition must span every ejection: "
                f"{self.ejectee_proof_cross_tab.ejections_total} != "
                f"{self.ejections_total}"
            )
        if self.weak_flag_conviction.flag_named_ejections > self.ejections_total:
            raise ValueError(
                "flag-named ejections cannot exceed ejections_total: "
                f"{self.weak_flag_conviction.flag_named_ejections} > "
                f"{self.ejections_total}"
            )
        if self.redirected_ballots.ballots_total != self.ballots_total:
            raise ValueError(
                "the redirect census must span every ballot: "
                f"{self.redirected_ballots.ballots_total} != {self.ballots_total}"
            )
        if self.scaffold_leakage.ballots_total != self.ballots_total:
            raise ValueError(
                "the leakage census must span every ballot: "
                f"{self.scaffold_leakage.ballots_total} != {self.ballots_total}"
            )
        if self.scaffold_leakage.turns_total != self.turns_total:
            raise ValueError(
                "the leakage census must span every turn: "
                f"{self.scaffold_leakage.turns_total} != {self.turns_total}"
            )
        coverage = self.public_response_coverage
        if coverage.crew_turns + coverage.impostor_turns != self.turns_total:
            raise ValueError(
                "the coverage split must span every turn: "
                f"{coverage.crew_turns} + {coverage.impostor_turns} != "
                f"{self.turns_total}"
            )
        return self


def _validate_rate(
    name: str, rate: float | None, numerator: int, denominator: int
) -> None:
    """Enforce the None-iff-zero-denominator sentinel and the ratio value."""

    if denominator == 0:
        if rate is not None:
            raise ValueError(f"{name} must be None when its denominator is 0")
        return
    if rate is None:
        raise ValueError(f"{name} must be defined when its denominator is positive")
    if abs(rate - numerator / denominator) > 1e-12:
        raise ValueError(
            f"{name} must equal numerator/denominator: "
            f"{rate} != {numerator}/{denominator}"
        )


def _validate_cell_against(
    name: str, cell: WilsonRateCell, numerator: int, denominator: int
) -> None:
    """Pin a nested cell's counts to the block's own counts (no free-floating cells)."""

    if cell.numerator != numerator or cell.denominator != denominator:
        raise ValueError(
            f"{name} must carry the block's own counts: got "
            f"{cell.numerator}/{cell.denominator}, expected "
            f"{numerator}/{denominator}"
        )


# ---------------------------------------------------------------------------
# The fold
# ---------------------------------------------------------------------------


def _role_proof_subjects(meeting: MeetingReport) -> frozenset[PlayerId]:
    """Every player named by a ``role_proof`` flag in this meeting."""

    return frozenset(
        subject
        for flag in meeting.contradictions
        if classify_flag(flag) == "role_proof"
        for subject in flag.subjects
    )


def _has_role_proof(meeting: MeetingReport) -> bool:
    """Whether the meeting carries >= 1 ``role_proof`` flag (partition A's test)."""

    return any(classify_flag(flag) == "role_proof" for flag in meeting.contradictions)


def _accused_by_speaker(meeting: MeetingReport) -> dict[PlayerId, set[PlayerId]]:
    """Map each speaker to every player they accused in this meeting."""

    accused: dict[PlayerId, set[PlayerId]] = {}
    for turn in meeting.transcript.turns:
        for claim in turn.claims:
            if isinstance(claim, AccusationClaim):
                accused.setdefault(turn.speaker, set()).add(claim.against)
    return accused


def _matches(text: str, phrases: Sequence[str]) -> bool:
    """Case-insensitive substring match of ``text`` against a phrase net."""

    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def _is_oracle_register(text: str) -> bool:
    """Whether one utterance credits the game engine with a verdict.

    Any of :data:`MACHINERY_ORACLE_PATTERNS` matching is a hit; the patterns are
    alternative shapes of the same register, not independent nets.
    """

    return any(pattern.search(text) for pattern in MACHINERY_ORACLE_PATTERNS)


def _is_omniscient(rationale: str) -> bool:
    """Whether a rationale carries ANY of the three omniscience nets.

    The union behind ``model_omniscient_ballots`` and the predicate the
    guard-preserved cell is scoped against — partner naming, an outright role
    statement, or a first-person kill disclosure.
    """

    return (
        _matches(rationale, PARTNER_PHRASES)
        or _matches(rationale, ROLE_STATEMENT_PHRASES)
        or _matches(rationale, SELF_KILL_PHRASES)
    )


def _model_authored_bodies(meeting: MeetingReport) -> dict[PlayerId, str]:
    """Each voter's PRE-GUARD rationale body, parsed from its own vote call.

    The model-originated leakage nets must read what the MODEL wrote, not what
    the record kept: Task 19.15's teammate coercion REPLACES ``rationale_text``
    with a fixed redaction before the ballot is recorded
    (``meetings.manager.TEAMMATE_COERCED_VOTE_RATIONALE``), so a future
    teammate-aimed ballot carrying a partner or self-kill disclosure would read
    clean on the recorded surface — the metric would silently under-count
    exactly the class the redaction exists to remove.

    :class:`~orchestrator.replay.LLMCallRecord` keeps the original structured
    response, so the pre-guard body is recoverable. A vote call is identified by
    its parsed payload carrying a string ``rationale_text`` (the ballot schema's
    distinctive field) and is attributed by ``agent_id``. The field is EXTRACTED
    from the parsed JSON rather than scanned raw, because the raw envelope
    carries ``"confidence": 0.NN`` — which the machinery-quotation net would
    otherwise read as the model quoting its own scoring grid (850 false
    positives against 39 real ones on ``replays/samples/9p2i``).

    A response that does not parse, or carries no such field, is simply absent
    here; the caller falls back to the recorded rationale and COUNTS the
    fallback, so the substitution is never silent. On all four committed sets
    every ballot pairs with exactly one parsed vote response, and every net
    reproduces its recorded-surface count exactly.
    """

    bodies: dict[PlayerId, str] = {}
    for call in meeting.llm_calls:
        if call.agent_id is None:
            continue
        try:
            payload = json.loads(call.response_text)
        except (ValueError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue
        body = payload.get("rationale_text")
        if isinstance(body, str) and _VOTE_PAYLOAD_KEYS <= payload.keys():
            bodies[call.agent_id] = body
    return bodies


class _Accumulator:
    """Mutable per-set tallies for one fold pass (never module-level state)."""

    def __init__(self) -> None:
        self.meetings_total = 0
        self.turns_total = 0
        self.ballots_total = 0
        self.ejections_total = 0
        # taxonomy
        self.flags_total = 0
        self.role_proof_flags = 0
        self.cross_statement_flags = 0
        self.weak_signal_flags = 0
        self.meetings_with_any_flag = 0
        # partition A
        self.flagged_meetings = 0
        self.flagged_ej_impostor = 0
        self.flagged_ej_innocent = 0
        self.unflagged_ej_impostor = 0
        self.unflagged_ej_innocent = 0
        # partition B
        self.proof_present = 0
        self.proof_present_impostor = 0
        self.proof_present_innocent = 0
        self.non_direct = 0
        self.non_direct_impostor = 0
        self.non_direct_innocent = 0
        # weak-flag conviction
        self.flag_named_ejections = 0
        self.weak_only = 0
        self.weak_only_impostor = 0
        self.weak_only_innocent = 0
        # consistency
        self.accusations_total = 0
        self.accusations_non_votable = 0
        self.accusing_ballots = 0
        self.consistent = 0
        self.inconsistent_skip = 0
        self.inconsistent_other = 0
        self.inconsistent_invalid = 0
        self.excluded_no_votable = 0
        self.guard_unwound_in_denominator = 0
        # coverage
        self.crew_turns = 0
        self.crew_whereabouts = 0
        self.impostor_turns = 0
        self.impostor_whereabouts = 0
        self.crew_macro_sum = 0.0
        self.crew_macro_meetings = 0
        self.impostor_macro_sum = 0.0
        self.impostor_macro_meetings = 0
        # redirects
        self.redirected = 0
        self.redirected_eject = 0
        self.redirect_coerced_skip = 0
        # leakage
        self.impostor_ballots = 0
        self.crew_ballots = 0
        self.model_partner = 0
        self.model_role = 0
        self.model_self_kill = 0
        self.model_omniscient = 0
        self.crew_partner = 0
        self.crew_omniscient = 0
        self.player_visible_leak = 0
        self.machinery_quotation = 0
        self.machinery_vocabulary = 0
        self.claim_reasons_total = 0
        self.oracle_ballots = 0
        self.oracle_turns = 0
        self.oracle_claim_reasons = 0
        self.guard_marked = 0
        self.guard_rewrite = 0
        self.guard_omniscient = 0
        self.model_source_pre_guard = 0
        self.model_source_unavailable = 0
        self.guard_provenance_verified = 0
        self.guard_provenance_unverifiable = 0


def _fold_meeting(
    acc: _Accumulator, meeting: MeetingReport, roles: Mapping[PlayerId, Role]
) -> None:
    """Fold one meeting into ``acc`` (every metric family, one pass)."""

    acc.meetings_total += 1

    for flag in meeting.contradictions:
        acc.flags_total += 1
        category = classify_flag(flag)
        if category == "role_proof":
            acc.role_proof_flags += 1
        elif category == "cross_statement":
            acc.cross_statement_flags += 1
        else:
            acc.weak_signal_flags += 1
    if meeting.contradictions:
        acc.meetings_with_any_flag += 1

    has_proof = _has_role_proof(meeting)
    if has_proof:
        acc.flagged_meetings += 1

    if meeting.outcome == "EJECTED":
        ejected = meeting.ejected_player_id
        # MeetingResult's coupled invariant: EJECTED implies a non-None id.
        assert ejected is not None
        acc.ejections_total += 1
        is_impostor = roles[ejected] == "IMPOSTOR"
        # Partition A — bucket by the MEETING's flag status.
        if has_proof:
            if is_impostor:
                acc.flagged_ej_impostor += 1
            else:
                acc.flagged_ej_innocent += 1
        elif is_impostor:
            acc.unflagged_ej_impostor += 1
        else:
            acc.unflagged_ej_innocent += 1
        # Partition B — bucket by whether the proof named the EJECTEE.
        if ejected in _role_proof_subjects(meeting):
            acc.proof_present += 1
            if is_impostor:
                acc.proof_present_impostor += 1
            else:
                acc.proof_present_innocent += 1
        else:
            acc.non_direct += 1
            if is_impostor:
                acc.non_direct_impostor += 1
            else:
                acc.non_direct_innocent += 1
        # Weak-flag-only conviction — ejectee-scoped, never meeting-scoped.
        naming = [flag for flag in meeting.contradictions if ejected in flag.subjects]
        if naming:
            acc.flag_named_ejections += 1
            if all(classify_flag(flag) == "weak_signal" for flag in naming):
                acc.weak_only += 1
                if is_impostor:
                    acc.weak_only_impostor += 1
                else:
                    acc.weak_only_innocent += 1

    # Public response coverage — pooled + the per-meeting macro terms.
    per_meeting = {"CREWMATE": [0, 0], "IMPOSTOR": [0, 0]}
    for turn in meeting.transcript.turns:
        acc.turns_total += 1
        role = roles[turn.speaker]
        answered = any(
            isinstance(observation, WhereaboutsClaim)
            for observation in turn.observations
        )
        per_meeting[role][1] += 1
        if answered:
            per_meeting[role][0] += 1
        if role == "IMPOSTOR":
            acc.impostor_turns += 1
            if answered:
                acc.impostor_whereabouts += 1
        else:
            acc.crew_turns += 1
            if answered:
                acc.crew_whereabouts += 1
        if _matches(turn.free_text, PARTNER_PHRASES):
            acc.player_visible_leak += 1
        if _is_oracle_register(turn.free_text):
            acc.oracle_turns += 1
        # The claim REASON is spoken text like any other. ``AlibiClaim`` carries
        # ``evidence``, not ``reason``, and is not scanned — a ruling backed by a
        # census: the register is absent from every committed evidence string.
        for claim in turn.claims:
            if not isinstance(claim, (AccusationClaim, CorroborationClaim)):
                continue
            acc.claim_reasons_total += 1
            if _is_oracle_register(claim.reason):
                acc.oracle_claim_reasons += 1
    crew_answered, crew_spoke = per_meeting["CREWMATE"]
    if crew_spoke:
        acc.crew_macro_sum += crew_answered / crew_spoke
        acc.crew_macro_meetings += 1
    impostor_answered, impostor_spoke = per_meeting["IMPOSTOR"]
    if impostor_spoke:
        acc.impostor_macro_sum += impostor_answered / impostor_spoke
        acc.impostor_macro_meetings += 1

    # Ballot-side metrics: redirects, leakage, and turn -> ballot consistency.
    votable = {ballot.voter for ballot in meeting.ballots}
    accused_by = _accused_by_speaker(meeting)
    model_bodies = _model_authored_bodies(meeting)
    for turn in meeting.transcript.turns:
        for claim in turn.claims:
            if isinstance(claim, AccusationClaim):
                acc.accusations_total += 1
                # Non-votable FOR THIS SPEAKER: dead, or the speaker themselves
                # (``_candidate_targets`` excludes the voter, so a
                # self-accusation names someone they could never vote for).
                if claim.against not in votable - {turn.speaker}:
                    acc.accusations_non_votable += 1

    for ballot in meeting.ballots:
        acc.ballots_total += 1
        # Cut the record along its provenance boundary FIRST: which text each
        # cell may read is decided by who wrote it, never by what it looks like.
        split = _split_rationale(ballot.rationale_text, model_bodies.get(ballot.voter))
        chain = _scan_marker_chain(split.marker_region)
        if split.verified:
            acc.guard_provenance_verified += 1
        else:
            acc.guard_provenance_unverifiable += 1
        if chain.redirected:
            acc.redirected += 1
            if ballot.target == SKIP_TARGET:
                acc.redirect_coerced_skip += 1
            else:
                acc.redirected_eject += 1
        # MODEL-originated cells read the PRE-GUARD body and nothing else, so
        # Task 19.15's redaction cannot hide a disclosure from the metric that
        # exists to count it. A ballot with no such body scans NOTHING: the old
        # fallback to the recorded string fed a parse-default ballot's raw JSON
        # envelope to the machinery net, the exact false positive
        # ``_model_authored_bodies`` extracts the parsed field to avoid.
        if split.model_body is None:
            acc.model_source_unavailable += 1
        else:
            acc.model_source_pre_guard += 1
        model_body = split.model_body or ""

        if chain.any_marker:
            acc.guard_marked += 1
        if chain.rewrote_target:
            acc.guard_rewrite += 1
            # The recorded BODY — not the whole record, and never the marker
            # payloads, which carry model-supplied targets and response heads
            # verbatim. "Preserved" means the stale body SURVIVED the guard, so
            # scoring the model's pre-guard text would report Task 19.15's
            # redaction as a preservation of the very text it removes, and
            # scoring the payloads would bill the model's own words to the
            # machinery.
            if _is_omniscient(split.body_region):
                acc.guard_omniscient += 1
        if MACHINERY_DECIMAL_PATTERN.search(model_body):
            acc.machinery_quotation += 1
        if _matches(model_body, MACHINERY_VOCABULARY):
            acc.machinery_vocabulary += 1
        if _is_oracle_register(model_body):
            acc.oracle_ballots += 1
        if roles[ballot.voter] == "IMPOSTOR":
            acc.impostor_ballots += 1
            if _matches(model_body, PARTNER_PHRASES):
                acc.model_partner += 1
            if _matches(model_body, ROLE_STATEMENT_PHRASES):
                acc.model_role += 1
            if _matches(model_body, SELF_KILL_PHRASES):
                acc.model_self_kill += 1
            if _is_omniscient(model_body):
                acc.model_omniscient += 1
        else:
            acc.crew_ballots += 1
            if _matches(model_body, PARTNER_PHRASES):
                acc.crew_partner += 1
            if _is_omniscient(model_body):
                acc.crew_omniscient += 1

        accused = accused_by.get(ballot.voter)
        if not accused:
            continue
        # The voter's own LEGAL target set: the living roster minus themselves,
        # mirroring ``meetings.manager._candidate_targets(living, exclude=voter)``.
        # A self-accusation names someone the voter cannot lawfully vote for, so
        # it must not enter the denominator, and a self-target must not score
        # consistent.
        legal_targets = votable - {ballot.voter}
        if not accused & legal_targets:
            # SKIP-tolerance: with no lawfully votable accused, a SKIP is the
            # only lawful ballot, so the pair leaves the denominator, visibly.
            acc.excluded_no_votable += 1
            continue
        acc.accusing_ballots += 1
        # SAME-AGENT: score the target the AGENT wrote, unwinding a guard
        # rewrite from its own marker. The guard's behaviour is metric 7's, and
        # charging it here would both misattribute it and double-count it.
        authored, unwound = _authored_target(ballot, chain)
        if unwound:
            acc.guard_unwound_in_denominator += 1
        if authored in accused and authored in legal_targets:
            acc.consistent += 1
        elif authored == SKIP_TARGET:
            acc.inconsistent_skip += 1
        elif authored in legal_targets:
            acc.inconsistent_other += 1
        else:
            # A target the voter could not lawfully cast: a hallucinated id, or
            # the voter themselves. Either way they neither voted their
            # accusation nor voted anyone else.
            acc.inconsistent_invalid += 1


def compute_deduction_metrics(
    report: TournamentReport | Sequence[GameReport],
    *,
    kill_craft: KillCraftSupplyCells | None = None,
) -> DeductionMetricsReport:
    """Fold a tournament report into the deduction metrics (Task 19.14).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (the signature every
    other analyzer in this package uses). Pure: no I/O, no engine re-run, no
    LLM call. Roles come from each game's post-game ground truth.

    ``kill_craft`` is the OPTIONAL adopted input for the witnessed / co-present
    evidence supply — pass the result of
    :func:`eval.kill_craft.compute_kill_craft_report` for the same replay set.
    Omitted, ``witnessed_supply`` is ``None`` (not supplied), never zero.

    :raises UnclassifiableFlagError: if a recorded flag matches no taxonomy rule.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)
    acc = _Accumulator()
    for game in games:
        for meeting in game.meetings:
            _fold_meeting(acc, meeting, game.roles)

    return DeductionMetricsReport(
        games_total=len(games),
        meetings_total=acc.meetings_total,
        ejections_total=acc.ejections_total,
        ballots_total=acc.ballots_total,
        turns_total=acc.turns_total,
        evidence_taxonomy=EvidenceTaxonomyCensus(
            flags_total=acc.flags_total,
            role_proof_flags=acc.role_proof_flags,
            cross_statement_flags=acc.cross_statement_flags,
            weak_signal_flags=acc.weak_signal_flags,
            meetings_with_any_flag=acc.meetings_with_any_flag,
            weak_signal_share=_rate_or_none(acc.weak_signal_flags, acc.flags_total),
        ),
        meeting_flag_cross_tab=MeetingFlagCrossTab(
            meetings_total=acc.meetings_total,
            flagged_meetings=acc.flagged_meetings,
            unflagged_meetings=acc.meetings_total - acc.flagged_meetings,
            flagged_ejections_impostor=acc.flagged_ej_impostor,
            flagged_ejections_innocent=acc.flagged_ej_innocent,
            unflagged_ejections_impostor=acc.unflagged_ej_impostor,
            unflagged_ejections_innocent=acc.unflagged_ej_innocent,
            flagged_meeting_accuracy=_cell(
                acc.flagged_ej_impostor,
                acc.flagged_ej_impostor + acc.flagged_ej_innocent,
            ),
            unflagged_meeting_accuracy=_cell(
                acc.unflagged_ej_impostor,
                acc.unflagged_ej_impostor + acc.unflagged_ej_innocent,
            ),
        ),
        ejectee_proof_cross_tab=EjecteeProofCrossTab(
            ejections_total=acc.ejections_total,
            proof_present_ejections=acc.proof_present,
            proof_present_impostor=acc.proof_present_impostor,
            proof_present_innocent=acc.proof_present_innocent,
            non_direct_ejections=acc.non_direct,
            non_direct_impostor=acc.non_direct_impostor,
            non_direct_innocent=acc.non_direct_innocent,
            direct_proof_accuracy=_cell(acc.proof_present_impostor, acc.proof_present),
            non_direct_accuracy=_cell(acc.non_direct_impostor, acc.non_direct),
        ),
        weak_flag_conviction=WeakFlagConvictionCells(
            flag_named_ejections=acc.flag_named_ejections,
            weak_flag_only_convictions=acc.weak_only,
            weak_flag_only_impostor=acc.weak_only_impostor,
            weak_flag_only_innocent=acc.weak_only_innocent,
            weak_flag_only_rate=_cell(acc.weak_only, acc.flag_named_ejections),
            weak_flag_only_innocent_share=_cell(acc.weak_only_innocent, acc.weak_only),
        ),
        turn_ballot_consistency=TurnBallotConsistencyCells(
            accusations_total=acc.accusations_total,
            accusations_of_non_votable_targets=acc.accusations_non_votable,
            accusing_ballots=acc.accusing_ballots,
            consistent_ballots=acc.consistent,
            inconsistent_skip_ballots=acc.inconsistent_skip,
            inconsistent_other_target_ballots=acc.inconsistent_other,
            inconsistent_invalid_target_ballots=acc.inconsistent_invalid,
            excluded_no_votable_target_ballots=acc.excluded_no_votable,
            guard_rewritten_ballots_unwound=acc.guard_unwound_in_denominator,
            consistency_rate=_rate_or_none(acc.consistent, acc.accusing_ballots),
        ),
        public_response_coverage=PublicResponseCoverageCells(
            crew_turns=acc.crew_turns,
            crew_turns_with_whereabouts=acc.crew_whereabouts,
            crew_pooled_coverage=_rate_or_none(acc.crew_whereabouts, acc.crew_turns),
            crew_macro_average_coverage=(
                acc.crew_macro_sum / acc.crew_macro_meetings
                if acc.crew_macro_meetings
                else None
            ),
            crew_macro_meetings=acc.crew_macro_meetings,
            impostor_turns=acc.impostor_turns,
            impostor_turns_with_whereabouts=acc.impostor_whereabouts,
            impostor_pooled_coverage=_rate_or_none(
                acc.impostor_whereabouts, acc.impostor_turns
            ),
            impostor_macro_average_coverage=(
                acc.impostor_macro_sum / acc.impostor_macro_meetings
                if acc.impostor_macro_meetings
                else None
            ),
            impostor_macro_meetings=acc.impostor_macro_meetings,
        ),
        redirected_ballots=RedirectedBallotCells(
            ballots_total=acc.ballots_total,
            redirected_ballots=acc.redirected,
            redirected_eject_ballots=acc.redirected_eject,
            redirect_coerced_skip_ballots=acc.redirect_coerced_skip,
            redirected_ballot_share=_rate_or_none(acc.redirected, acc.ballots_total),
        ),
        scaffold_leakage=ScaffoldLeakageCells(
            ballots_total=acc.ballots_total,
            impostor_ballots=acc.impostor_ballots,
            crew_ballots=acc.crew_ballots,
            turns_total=acc.turns_total,
            model_partner_naming_ballots=acc.model_partner,
            model_role_statement_ballots=acc.model_role,
            model_self_kill_disclosure_ballots=acc.model_self_kill,
            model_omniscient_ballots=acc.model_omniscient,
            crew_partner_naming_ballots=acc.crew_partner,
            crew_omniscient_control_ballots=acc.crew_omniscient,
            player_visible_leak_turns=acc.player_visible_leak,
            model_partner_naming_rate=_cell(acc.model_partner, acc.impostor_ballots),
            model_omniscient_rate=_cell(acc.model_omniscient, acc.impostor_ballots),
            model_machinery_quotation_ballots=acc.machinery_quotation,
            model_machinery_vocabulary_ballots=acc.machinery_vocabulary,
            model_machinery_quotation_share=_rate_or_none(
                acc.machinery_quotation, acc.ballots_total
            ),
            claim_reasons_total=acc.claim_reasons_total,
            model_oracle_register_ballots=acc.oracle_ballots,
            oracle_register_turns=acc.oracle_turns,
            oracle_register_claim_reasons=acc.oracle_claim_reasons,
            model_source_pre_guard_ballots=acc.model_source_pre_guard,
            model_source_unavailable_ballots=acc.model_source_unavailable,
            guard_provenance_verified_ballots=acc.guard_provenance_verified,
            guard_provenance_unverifiable_ballots=acc.guard_provenance_unverifiable,
            guard_marked_ballots=acc.guard_marked,
            guard_target_rewrite_ballots=acc.guard_rewrite,
            guard_preserved_omniscient_ballots=acc.guard_omniscient,
            guard_preserved_omniscient_rate=_cell(
                acc.guard_omniscient, acc.guard_rewrite
            ),
            guard_marked_ballot_share=_rate_or_none(
                acc.guard_marked, acc.ballots_total
            ),
        ),
        witnessed_supply=(
            witnessed_supply_from_kill_craft(kill_craft)
            if kill_craft is not None
            else None
        ),
    )


__all__ = [
    "CROSS_STATEMENT_KINDS",
    "MACHINERY_DECIMAL_PATTERN",
    "MACHINERY_ORACLE_PATTERNS",
    "MACHINERY_VOCABULARY",
    "PARTNER_PHRASES",
    "ROLE_PROOF_KINDS",
    "ROLE_STATEMENT_PHRASES",
    "SELF_KILL_PHRASES",
    "DeductionMetricsReport",
    "EjecteeProofCrossTab",
    "EvidenceCategory",
    "EvidenceTaxonomyCensus",
    "KillCraftSupplyCells",
    "MeetingFlagCrossTab",
    "PublicResponseCoverageCells",
    "RedirectedBallotCells",
    "ScaffoldLeakageCells",
    "TurnBallotConsistencyCells",
    "UnclassifiableFlagError",
    "WeakFlagConvictionCells",
    "WilsonRateCell",
    "WitnessedSupplyCells",
    "classify_flag",
    "compute_deduction_metrics",
    "witnessed_supply_from_kill_craft",
]
