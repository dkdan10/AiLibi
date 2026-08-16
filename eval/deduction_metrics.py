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
  than reconstructed).
* AUTHORED target: **the target the AGENT wrote, not the one the record shows.**
  Four deterministic guards rewrite ``VoteBallot.target`` and each stamps the
  ORIGINAL into ``rationale_text`` as ``{target!r}`` — the graph redirect, the
  invalid-target normalization, the teammate coercion, and the citation-gate
  coercion (``meetings/manager.py``). This metric is SAME-AGENT by name, so a
  rewritten ballot is unwound to the authored target before it is scored;
  otherwise the guard's choice would be charged to the agent, and the same
  rewrite would be counted twice — once here as "inconsistency" and once,
  correctly, in the separate redirect census (metric 7). On
  ``replays/samples/9p2i`` 16 of the 777 scored ballots change bucket under the
  unwind (46 of 2,186 on the corpus), so this is not a hypothetical.
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
* ``inconsistent_invalid_target_ballots``: the authored target names no votable
  player at all — the hallucinated-id shape the invalid-target guard normalizes
  to SKIP (2 on ``replays/samples/9p2i``, 0 elsewhere). It is its own bucket
  because the voter neither voted their accusation nor voted anyone else;
  folding it into either would misdescribe what happened.
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
Numerator: ballots whose ``rationale_text`` carries the pinned
:data:`~meetings.manager.BALLOT_TARGET_REDIRECT_MARKER` prefix. Denominator: all
recorded ballots. The count splits by the recorded target: an eject the guard
re-aimed vs a ballot coerced to SKIP. *Does NOT measure*: whether the redirect
changed the meeting's OUTCOME (that needs a counterfactual tally, which recorded
bytes cannot supply).

**8. Scaffold leakage, split by ORIGIN** (:class:`ScaffoldLeakageCells`) — the
C5 finding restated as separately-defined metrics instead of one contested
number. The contract names two leakage CLASSES on the model side — role
statements and machinery statements — and one on the guard side; all three are
counted, and the ROLE class is itself three nets because "omniscience" has three
distinguishable shapes in the committed text:

* MODEL-originated ROLE/omniscience — text the model authored.
  ``model_partner_naming_ballots`` (:data:`PARTNER_PHRASES`),
  ``model_role_statement_ballots`` (:data:`ROLE_STATEMENT_PHRASES`), and
  ``model_self_kill_disclosure_ballots`` (:data:`SELF_KILL_PHRASES` — a voter
  narrating their OWN kill: "I killed p-4", "I know I was killing p-3"). All
  three are over impostor-voter ballots; ``model_omniscient_ballots`` is their
  UNION (a ballot can hit several nets, so the union is not their sum).
  ``crew_partner_naming_ballots`` and ``crew_omniscient_control_ballots`` are
  the false-positive CONTROLS (both 0 on every committed set).
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
  just impostor ones — machinery talk is role-independent.
* GUARD-originated — text the deterministic machinery injected.
  ``guard_marked_ballots``: ballots carrying any pinned manager/voting marker.
  ``guard_target_rewrite_ballots``: the subset whose TARGET the guard rewrote.
  ``guard_preserved_omniscient_ballots``: target-rewritten ballots whose
  preserved rationale still carries ANY omniscient phrase (the union above) —
  the exact class Task 19.15 redacts going forward. It is **1** on
  ``replays/ml_corpus/9p2i`` (seed 1118, meeting 0: a redirected impostor ballot
  whose preserved rationale says "when I know I was killing p-3") and 0 on the
  other three sets. The class is therefore RARE on committed bytes, not absent —
  a distinction this module got wrong until the self-kill net existed, which is
  itself the C5 lesson landing on the metric that measures it.

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
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
)
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
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
    "one who killed",
    "i am the killer",
    "i'm the killer",
)
"""First-person KILL disclosure — a voter narrating their own kill.

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


def _marker_prefix(marker: str) -> str:
    """The literal head of a ``.format()``-interpolated marker constant.

    Mirrors ``eval/meeting_quality.py``'s prefix derivation: the constants are
    imported (never hard-coded), and the first ``{`` placeholder is where the
    fixed prefix ends, so a marker rename cannot silently break the match.
    """

    head, _, _ = marker.partition("{")
    if not head:
        raise ValueError(f"marker constant has no literal prefix: {marker!r}")
    return head


# Every pinned ballot-rationale marker the meeting layer can inject. The two
# groups are separated because only the first REWRITES the recorded target,
# which is the class Task 19.15's redaction is about.
#
# Matching is a plain unanchored substring test on the derived prefix — the same
# shape ``eval/meeting_quality.py``'s redirect / invalid-target / teammate
# censuses use. It is deliberately NOT the anchored, repr-aware regex that
# module reserves for the citation-coerced SKIP tri-split: that precision exists
# to keep a coerced ballot out of the ``threshold_inversions`` sentinel, whereas
# these cells ask only "did the machinery write into this rationale at all", for
# which the substring test is the honest (and slightly conservative-upward)
# predicate. Consequence, stated rather than hidden: a model rationale that
# quoted a marker's literal text verbatim would count as guard-originated here.
# On the committed bytes none does — Task 19.8's disclosure found zero literal
# implementation tokens in model output.
_TARGET_REWRITE_MARKER_PREFIXES: Final[tuple[str, ...]] = (
    _marker_prefix(BALLOT_TARGET_REDIRECT_MARKER),
    _marker_prefix(INVALID_VOTE_TARGET_MARKER),
    _marker_prefix(TEAMMATE_VOTE_TARGET_MARKER),
    _marker_prefix(UNCITED_ZERO_FLAG_EJECT_MARKER),
)
_OTHER_GUARD_MARKER_PREFIXES: Final[tuple[str, ...]] = (
    _marker_prefix(VOTE_PARSE_DEFAULT_MARKER),
    _marker_prefix(INVALID_REASON_ID_MARKER),
    _marker_prefix(INVALID_OBSERVATION_ID_MARKER),
)
_REDIRECT_MARKER_PREFIX: Final[str] = _marker_prefix(BALLOT_TARGET_REDIRECT_MARKER)

# The repr-aware pattern that recovers the AUTHORED target a rewriting guard
# preserved. Each of the four rewriting markers interpolates the ORIGINAL target
# as ``{target!r}`` (``meetings/manager.py``: "either way this marker preserves
# the original target"), so the agent's own ballot is recoverable from the
# record. The value alternation mirrors ``eval/meeting_quality.py``'s
# ``_MARKER_REPR_VALUE``: quote-matching consumes the whole repr first, so the
# match ends at the REAL marker boundary even when the payload contains the
# marker's tail. UNANCHORED on purpose — the citation gate is the last guard in
# the ballot chain, so a redirect marker can ride INSIDE an outer coercion
# marker; the outermost (earliest-starting) match is the one that names what the
# agent actually wrote.
_MARKER_REPR_VALUE: Final[str] = r"(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"


def _rewrite_marker_pattern(marker: str) -> re.Pattern[str]:
    head, placeholder, tail = marker.partition("{target!r}")
    if not placeholder:
        raise ValueError(f"marker constant carries no target repr: {marker!r}")
    return re.compile(
        re.escape(head) + "(" + _MARKER_REPR_VALUE + ")" + re.escape(tail)
    )


_TARGET_REWRITE_MARKER_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    _rewrite_marker_pattern(BALLOT_TARGET_REDIRECT_MARKER),
    _rewrite_marker_pattern(INVALID_VOTE_TARGET_MARKER),
    _rewrite_marker_pattern(TEAMMATE_VOTE_TARGET_MARKER),
    _rewrite_marker_pattern(UNCITED_ZERO_FLAG_EJECT_MARKER),
)


def _authored_target(ballot: VoteBallot) -> tuple[str, bool]:
    """``(the target the AGENT wrote, whether a guard rewrite was unwound)``.

    A rewriting guard replaces ``ballot.target`` and stamps the original into
    ``rationale_text``; this reverses that for the SAME-AGENT metric, leaving the
    guard's own behaviour to the redirect census. When no rewriting marker is
    present the recorded target IS the authored one.

    Fail-loud on a malformed repr (AGENTS.md "no silent fallbacks"): a marker
    that matched its own pinned pattern but whose payload will not evaluate is a
    corrupt record, not something to shrug past.
    """

    matches = [
        match
        for match in (
            pattern.search(ballot.rationale_text)
            for pattern in _TARGET_REWRITE_MARKER_PATTERNS
        )
        if match is not None
    ]
    if not matches:
        return ballot.target, False
    outermost = min(matches, key=lambda match: match.start())
    try:
        original = ast.literal_eval(outermost.group(1))
    except (ValueError, SyntaxError) as error:  # pragma: no cover - corrupt record
        raise ValueError(
            f"guard marker carries an unreadable target repr: {outermost.group(1)!r}"
        ) from error
    if not isinstance(original, str):
        raise ValueError(f"guard marker target repr is not a string: {original!r}")
    return original, True


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

    ``inconsistent_invalid_target_ballots`` is the hallucinated-id shape: the
    authored target names no votable player, so the voter neither voted their
    accusation nor voted anyone else. It is its own bucket rather than folded
    into either neighbour, because both foldings would misdescribe it (2 on
    ``replays/samples/9p2i``, 0 elsewhere).

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
      the false-positive CONTROLS over ``crew_ballots`` (both 0 on every
      committed set).
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

    GUARD-originated (the deterministic machinery injected the text):

    * ``guard_marked_ballots`` — any pinned manager/voting marker.
    * ``guard_target_rewrite_ballots`` — the subset whose TARGET the guard
      rewrote.
    * ``guard_preserved_omniscient_ballots`` — target-rewritten ballots whose
      preserved rationale still carries ANY omniscient phrase. This is exactly
      the class Task 19.15 redacts going forward. It is 1 on
      ``replays/ml_corpus/9p2i`` (seed 1118 meeting 0) and 0 on the other three
      sets: rare on committed bytes, NOT absent.

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
    guard_marked_ballots: int
    guard_target_rewrite_ballots: int
    guard_preserved_omniscient_ballots: int
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
                self.guard_marked_ballots,
                self.guard_target_rewrite_ballots,
                self.guard_preserved_omniscient_ballots,
            ),
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
        if self.impostor_ballots + self.crew_ballots != self.ballots_total:
            raise ValueError(
                "impostor + crew ballots must equal ballots_total: "
                f"{self.impostor_ballots} + {self.crew_ballots} != "
                f"{self.ballots_total}"
            )
        for label, count, limit in (
            (
                "model_partner_naming_ballots",
                self.model_partner_naming_ballots,
                self.impostor_ballots,
            ),
            (
                "model_role_statement_ballots",
                self.model_role_statement_ballots,
                self.impostor_ballots,
            ),
            (
                "model_self_kill_disclosure_ballots",
                self.model_self_kill_disclosure_ballots,
                self.impostor_ballots,
            ),
            (
                "model_omniscient_ballots",
                self.model_omniscient_ballots,
                self.impostor_ballots,
            ),
            (
                "crew_partner_naming_ballots",
                self.crew_partner_naming_ballots,
                self.crew_ballots,
            ),
            (
                "crew_omniscient_control_ballots",
                self.crew_omniscient_control_ballots,
                self.crew_ballots,
            ),
            (
                "player_visible_leak_turns",
                self.player_visible_leak_turns,
                self.turns_total,
            ),
            (
                "model_machinery_quotation_ballots",
                self.model_machinery_quotation_ballots,
                self.ballots_total,
            ),
            (
                "model_machinery_vocabulary_ballots",
                self.model_machinery_vocabulary_ballots,
                self.ballots_total,
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


def _guard_marker_classes(rationale: str) -> tuple[bool, bool]:
    """``(carries any guard marker, the guard rewrote the target)``."""

    rewrote = any(prefix in rationale for prefix in _TARGET_REWRITE_MARKER_PREFIXES)
    other = any(prefix in rationale for prefix in _OTHER_GUARD_MARKER_PREFIXES)
    return (rewrote or other), rewrote


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
        self.guard_marked = 0
        self.guard_rewrite = 0
        self.guard_omniscient = 0


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
    for turn in meeting.transcript.turns:
        for claim in turn.claims:
            if isinstance(claim, AccusationClaim):
                acc.accusations_total += 1
                if claim.against not in votable:
                    acc.accusations_non_votable += 1

    for ballot in meeting.ballots:
        acc.ballots_total += 1
        rationale = ballot.rationale_text
        if _REDIRECT_MARKER_PREFIX in rationale:
            acc.redirected += 1
            if ballot.target == SKIP_TARGET:
                acc.redirect_coerced_skip += 1
            else:
                acc.redirected_eject += 1
        marked, rewrote = _guard_marker_classes(rationale)
        omniscient = _is_omniscient(rationale)
        if marked:
            acc.guard_marked += 1
        if rewrote:
            acc.guard_rewrite += 1
            if omniscient:
                acc.guard_omniscient += 1
        if MACHINERY_DECIMAL_PATTERN.search(rationale):
            acc.machinery_quotation += 1
        if _matches(rationale, MACHINERY_VOCABULARY):
            acc.machinery_vocabulary += 1
        if roles[ballot.voter] == "IMPOSTOR":
            acc.impostor_ballots += 1
            if _matches(rationale, PARTNER_PHRASES):
                acc.model_partner += 1
            if _matches(rationale, ROLE_STATEMENT_PHRASES):
                acc.model_role += 1
            if _matches(rationale, SELF_KILL_PHRASES):
                acc.model_self_kill += 1
            if omniscient:
                acc.model_omniscient += 1
        else:
            acc.crew_ballots += 1
            if _matches(rationale, PARTNER_PHRASES):
                acc.crew_partner += 1
            if omniscient:
                acc.crew_omniscient += 1

        accused = accused_by.get(ballot.voter)
        if not accused:
            continue
        if not accused & votable:
            # SKIP-tolerance: with no votable accused, a SKIP is the only lawful
            # ballot, so the pair is excluded from the denominator, visibly.
            acc.excluded_no_votable += 1
            continue
        acc.accusing_ballots += 1
        # SAME-AGENT: score the target the AGENT wrote, unwinding a guard
        # rewrite from its own marker. The guard's behaviour is metric 7's, and
        # charging it here would both misattribute it and double-count it.
        authored, unwound = _authored_target(ballot)
        if unwound:
            acc.guard_unwound_in_denominator += 1
        if authored in accused:
            acc.consistent += 1
        elif authored == SKIP_TARGET:
            acc.inconsistent_skip += 1
        elif authored in votable:
            acc.inconsistent_other += 1
        else:
            # A hallucinated id naming no votable player: the voter neither
            # voted their accusation nor voted anyone else.
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
            guard_marked_ballots=acc.guard_marked,
            guard_target_rewrite_ballots=acc.guard_rewrite,
            guard_preserved_omniscient_ballots=acc.guard_omniscient,
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
