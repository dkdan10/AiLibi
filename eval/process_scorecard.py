"""The nine-row process scorecard — was a decision grounded in what the agent held?

The one home of the nine measures
[the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md)
§8 names, computed with **zero model calls** over bytes already in the tree. The
owner accepted D1 that day: the process suite is the headline, role-correctness
is a REPORTED cell and the preregistered ``supported_correct_ejection`` stops
being the project's gate. That demotion is written into every artifact this
module produces (:data:`ROLE_CORRECTNESS_NOTE`), and nothing here ever reads a
role to decide whether a decision was grounded.

Two rows carry the weight D1 rests on. Without **argmax-independence** (row 2)
the headline certifies an arithmetic aggregator as a reasoner: 93.6% of crew
EJECT ballots on the shipped corpus simply name the voter's own rendered
suspicion argmax, and every one of the departing 6.4% carries a valid citation,
so "cited and on-target" scores an 8.6%-accurate ballot exactly like a
96.1%-accurate one. Without the **manufactured-contradiction rate** (row 3) it
certifies seed 41: the alibi schema compresses a truthfully-moving player into a
single-room envelope, the detectors flag the envelope, and a right-looking
process convicts an innocent on evidence the schema invented. 103 of the 104
false self-alibis in the shipped 9p2i corpora are that artifact; exactly 2 of
955 are flat lies.

Definitions before counting
---------------------------
The house rule of :mod:`eval.deduction_metrics` and :mod:`eval.evidence_honesty`
holds here: every row states its numerator, denominator, non-coverage and clock
convention BEFORE it is counted, and the sentence it states lives in
:data:`ROW_DEFINITIONS` and is published inside the artifact itself, so a reader
of the scorecard alone can tell what each cell counted.
``tests/eval/test_process_scorecard.py`` pins every definition with a planted
case that turns the row the other way.

What this module never does
---------------------------
No model is called, on any path: the suite is a fold over committed bytes, which
is the property D3 ("ship on today's bytes") rests on. No held-out band is
generated, drawn or rendered, and no prefix, prompt or transcript TEXT reaches an
output — only counts. Nothing is written inside a recording directory; the
writer that publishes this fold
(``scripts/publish_process_scorecard.py``) protects every ``replays/**`` path and
the fifth run's archive before it opens its destination. ``citation_relevance_version``
stays ``None``: relevance is computed offline here and the production lever never
goes on.

Reuse, not re-implementation
----------------------------
Every analyzer this suite needs already exists and is read by name rather than
copied: :func:`meetings.citation_relevance.citations_bear_on` is the ONE
aboutness rule (the guard and the instrument ask it of the same ballot, so a
third phrasing here would let them disagree);
:func:`eval.meeting_quality._rendered_suspicion_by_target_per_voter` and its
valid-target twin :func:`eval.meeting_quality.rendered_valid_targets_by_voter`
read the recorded prompts; :func:`eval.meeting_quality.recorded_contradiction_flags`
is the evidence-supply census;
:func:`eval.meeting_quality.compute_ballot_target_redirects` is the redirect
census; :func:`eval.deduction_metrics._authored_target` unwinds a guard rewrite
for recordings older than the typed provenance fields, exactly as
``meetings/schemas.py`` prescribes; :func:`eval.alibi_fabrication.compute_alibi_fabrication_rate`
and :func:`eval.reporter_justice.compute_reporter_justice` supply the context
cells; and ground truth is the engine itself —
:func:`eval.replay_walk.walk_replay` under a state-hash-verifying profile, with
roles from :func:`eval.validity.roles_by_seed`, the seeder that
``scripts/build_sample_report.py`` takes them from.

The clock, stated
-----------------
:data:`AGENT_CLOCK_OFFSET` is 1, the same convention
:mod:`eval.evidence_honesty` names and asserts: an agent-frame tick ``T``
describes the engine's post-advance state at tick ``T - 1``, and agent tick 0
describes the seeded pre-advance state of engine tick 0. A recorded
:class:`~meetings.schemas.AlibiClaim` is spoken in the agent frame, so its span
is resolved against ``route[T - 1]``. The census the module reproduces
(955 / 104 / 103 / 2) holds under that convention and under no other, which is
what pins it.

Eras are labelled, never averaged
---------------------------------
Stated rather than discovered: once the grounded-SKIP card and the weighing
channel land and the re-record runs, the SKIP rows move off zero and rows 2 and 9
stop being comparable across that boundary. The published artifact carries the
provenance of the recordings it read for exactly that reason. Row 2 keeps reading
the OLD bytes correctly after the weighing card drops the rendered trust column,
because that card widens :data:`eval.meeting_quality._SUSPICION_GRAPH_ROW_RE`
rather than re-scoring history.
"""

from __future__ import annotations

import dataclasses
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Final, NoReturn

from pydantic import BaseModel, ConfigDict, model_validator

from engine.entities import Role
from engine.world import Map, load_canonical_map
from eval.alibi_fabrication import compute_alibi_fabrication_rate
from eval.balance_eval import load_tournament_report
from eval.deduction_metrics import _authored_target, _scan_marker_chain
from eval.meeting_quality import (
    compute_ballot_target_redirects,
    recorded_contradiction_flags,
    rendered_valid_targets_by_voter,
    _rendered_suspicion_by_target_per_voter,
)
from eval.replay_walk import (
    ReplayWalkConfig,
    TickAdvanced,
    TickOpened,
    WalkViolation,
    walk_replay,
)
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameReport,
    MeetingReport,
)
from eval.reporter_justice import ReporterJusticeCells, compute_reporter_justice
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from meetings.citation_relevance import (
    carries_citation,
    citations_bear_on,
    every_string_in,
    names_player,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    ContradictionRef,
    MeetingTurn,
    PlayerId,
    RoomId,
    VoteBallot,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries

#: Bumped only when the published JSON changes shape in a way an older reader
#: cannot interpret. Version 1 is the first publication (2026-09-19).
SCHEMA_VERSION: Final[int] = 1

#: The date D1 was accepted, stamped into every artifact so the demotion is
#: dated wherever the scorecard is read.
DECISION_DATE: Final[str] = "2026-09-19"

#: The D1 demotion, verbatim in the markdown header and as typed keys in the
#: JSON. Role-correctness is the LAST row of the suite and gates nothing.
ROLE_CORRECTNESS_NOTE: Final[str] = (
    "Role-correctness is REPORTED and is NOT a gate. The owner accepted decision "
    "D1 of tasks/direction-2026-09-19-process-over-outcome.md section 10 on "
    "2026-09-19: the process suite is the headline, role-correctness is a "
    "reported cell beside it, and the preregistered supported_correct_ejection "
    "outcome stops being the project's gate. Nothing in this scorecard, and "
    "nothing any card derived from it gates on, pushes an agent toward the "
    "correct answer: a wrong decision on believable data is the game working, "
    "and it is counted in row 8, never penalised."
)

#: Stated in the JSON so a reader does not mistake the artifact for a live feed.
NO_CONSUMER_NOTE: Final[str] = (
    "No component reads this file yet. It is published beside the markdown so a "
    "spectator surface can load it later; today its only consumer is "
    "scripts/publish_process_scorecard.py --check, which recomputes both files "
    "from the committed recordings and fails on drift."
)

#: The agent frame runs exactly +1 against the engine frame: a claim spoken at
#: agent tick ``T`` describes the engine's post-advance state at ``T - 1``, and
#: agent tick 0 describes the seeded state before engine tick 0 resolved. The
#: same constant and the same sentence live in :mod:`eval.evidence_honesty`;
#: this module resolves alibi spans under it and publishes the census that only
#: holds there.
AGENT_CLOCK_OFFSET: Final[int] = 1

#: The contradiction kinds whose basis is a spoken alibi. Read from the owning
#: census in :mod:`eval.alibi_fabrication` rather than re-listed, so a new alibi
#: kind cannot start being scored by one module and not the other.
ALIBI_FLAG_KINDS: Final[frozenset[str]] = frozenset(
    {"alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical"}
)

#: A whole-token player id in free prose, the boundary rule
#: :data:`meetings.citation_relevance.PLAYER_TOKEN` states: ``p-1`` must not
#: match inside ``p-10``.
_PLAYER_TOKEN_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<![0-9A-Za-z_-])(p-\d+)(?![0-9A-Za-z_-])"
)

#: A tick reference in free prose. Row 6 tests the NUMBER against the surfaces
#: the voter actually held, never the proposition wrapped around it.
_TICK_REFERENCE_RE: Final[re.Pattern[str]] = re.compile(
    r"\btick\s+(\d+)", re.IGNORECASE
)

#: The nine sentences, published inside every artifact. Each states numerator,
#: denominator and non-coverage; ``tests/eval/test_process_scorecard.py`` asserts
#: the keys match the rows the fold emits, so a row cannot ship undefined.
ROW_DEFINITIONS: Final[Mapping[str, str]] = {
    "grounded_decision_rate": (
        "Numerator: ballots whose citation RESOLVES in the voter's own inputs "
        "(primary_reason_id in this meeting's turns, or "
        "primary_reason_observation_id carried whole-token on a line of that "
        "voter's own recorded prompts) AND bears on the decision's subject by "
        "meetings.citation_relevance.citations_bear_on - the subject being the "
        "recorded target for an EJECT and any member of considered_alternatives "
        "for a SKIP. Denominator: all ballots of that decision kind. "
        "Not-evaluable: ballots whose voter has no recorded prompt in the "
        "meeting. An UNCITED ballot is not grounded: citations_bear_on is "
        "vacuously true with nothing cited, so presence and resolution are "
        "required before aboutness is asked. It does NOT measure whether the "
        "cited line was factually true."
    ),
    "argmax_independence": (
        "Over CREW EJECT ballots, comparing the RECORDED target with the argmax "
        "of that voter's own rendered suspicion rows INTERSECTED with that "
        "voter's rendered valid-ejection-target list. Numerator: the DEVIATING "
        "ballots, whose recorded target is not that argmax. Denominator: the "
        "unambiguous ballots. Ties are excluded and counted; a ballot whose "
        "voter's prompts carry no row inside the valid list is not-evaluable "
        "and counted. Roles come from the seeder, are used only to report the "
        "role-correctness of followers and deviators BESIDE the split, and gate "
        "nothing. Chance is the mean, over the SAME unambiguous ballots that "
        "form the denominator - never over the excluded ties or the "
        "not-evaluable ballots - of the living-impostor share of each voter's "
        "own rendered valid-target list. It does NOT "
        "measure whether the voter read the graph, only whether the recorded "
        "call equals the arithmetic the engine handed it."
    ),
    "manufactured_contradiction_rate": (
        "Numerator: recorded contradiction flags whose kind is an alibi class "
        "(alibi_conflict, alibi_vs_sighting, alibi_vs_physical) and whose "
        "subjects name the speaker of a SELF-alibi claim in that meeting that is "
        "TRUE at at least one tick of its own span against that speaker's "
        "engine route from a state-hash-verified walk_replay. Denominator: all "
        "alibi-class flags. Not-evaluable: an alibi-class flag naming no "
        "self-alibi speaker in its meeting, or one whose claim covers a tick the "
        "walk does not reach. Ticks are agent-frame and resolve against engine "
        "tick T - 1. It does NOT measure intent, and it does NOT clear a flag "
        "whose subject lied at every tick - that flag is evidence, not an "
        "artifact."
    ),
    "unexplained_decision_rate": (
        "Numerator: an EJECT whose citations do not resolve in the voter's own "
        "inputs, or a SKIP that names no player at all - empty "
        "considered_alternatives AND a MODEL-AUTHORED rationale carrying no "
        "whole-token player id. Model-authored means the remainder once the "
        "meeting layer's own audit markers are cut off by provenance, the same "
        "anchored chain eval.deduction_metrics._scan_marker_chain walks and "
        "api.replay_loader cuts for rationale_text_clean: a guard marker "
        "preserves the coerced target's id and the teammate firewall then "
        "redacts the body, so reading the raw text would let the machinery's "
        "prose answer for a voter who named nothing. Denominator: all ballots. "
        "Not-evaluable: ballots whose voter has no recorded prompt. The two "
        "halves are reported separately because they are different defects: an "
        "EJECT with no basis, and an abstention that names nothing it weighed."
    ),
    "evidence_quality_mix": (
        "A mix, not a rate: one numerator per band, summing to the denominator. "
        "One row per EJECTION (a meeting whose outcome is EJECTED), classified "
        "ROLE-BLIND into the highest band the ejected player carried: vent_flag "
        "(a recorded vent_sighting flag names them), contradiction_flag (a "
        "recorded non-vent flag names them), first_hand (no flag, but an EJECT "
        "ballot against them cites a resolving observation of the voter's own "
        "memory, or a transcript turn carrying a structured observation that "
        "NAMES them - whole-token, by meetings.citation_relevance.names_player "
        "over the observation's dumped structure, so a turn whose only "
        "observation places somebody else, and a turn merely SPOKEN by the "
        "ejected player, are not first-hand accounts of them), "
        "hearsay (no flag, and the cited turn carries only an accusation), "
        "unevidenced (no flag and no resolving, on-target citation). "
        "Denominator: all ejections. Role-correctness is reported beside each "
        "band and gates nothing. eval.meeting_quality.decompose_ejection_channels "
        "is NOT used here: it returns None unless the ejected player is a true "
        "impostor, which would make the mix role-conditioned."
    ),
    "rationale_faithfulness": (
        "Numerator: ballots every extracted TOKEN of whose rationale_text is "
        "present in what the voter held - whole-token player ids (matched by "
        "meetings.citation_relevance.names_player), canonical room ids (matched "
        "case-insensitively, underscore or space), and tick references - checked "
        "against this meeting's transcript and that voter's own recorded "
        "prompts. Denominator: ballots carrying at least one such token. "
        "Not-evaluable: ballots with no extractable token, and ballots whose "
        "voter has no recorded prompt. It reads rationale_text WHOLE, guard "
        "audit markers included, and deliberately differs from row 4 there: "
        "this row asks whether every token in the RECORDED text is one the "
        "voter held, and a marker's preserved id always is, while row 4 asks "
        "the authorship question and must cut the machinery's prose off first. "
        "LIMITS, stated: this tests TOKENS, not "
        "propositions - an assertion and its negation score alike, and a true "
        "sentence assembled from present tokens scores the same as a false one. "
        "The direction memo's section 3 result on invented facts is two-method "
        "agreement between two graders, NOT this measurement."
    ),
    "agent_authored_share": (
        "Numerator: ballots the meeting layer did not re-aim - neither a typed "
        "guard_rewrite_reason (any BallotTargetRewriteReason member) nor a "
        "target-rewriting marker unwound by eval.deduction_metrics._authored_"
        "target, the fallback meetings/schemas.py prescribes for recordings made "
        "before the typed fields. Denominator: all ballots. Citation-only "
        "rewrites are NOT counted against the share and are reported separately "
        "as 'citation nulled, target intact'; a ballot carrying both is counted "
        "among the rewrites, because the target moved. The marker-only redirect "
        "census rides beside as a sub-count: it keys on the graph-redirect "
        "marker alone and is therefore smaller than the typed layer."
    ),
    "wrong_but_believable_rate": (
        "Numerator: EJECT ballots that are role-INCORRECT (the recorded target "
        "is a crewmate) AND grounded by row 1 AND not resting on a "
        "manufactured contradiction by row 3 (no manufactured flag in that "
        "meeting names the ballot's target). Denominator: all EJECT ballots. "
        "REPORTED, NEVER PENALISED: this is the owner's preferred case - a wrong "
        "decision on believable data - and the direction of this row is "
        "deliberately unstated."
    ),
    "role_correct_ejection_rate": (
        "Numerator: ejections whose ejected player was an IMPOSTOR. "
        "Denominator: all ejections. REPORTED BESIDE the suite, NEVER A GATE "
        "(decision D1, 2026-09-19). It is published last on purpose."
    ),
}


#: Row 6's limits, published inside the row so a reader of the cell alone has them.
FAITHFULNESS_LIMITS: Final[str] = (
    "This row tests TOKENS, not propositions. An assertion and its negation "
    "score alike, and a false sentence assembled entirely from tokens the voter "
    "held scores as faithful. It cannot see an invented RELATION between present "
    "tokens. The direction memo's section 3 finding that rationales invent "
    "almost no facts is TWO-METHOD AGREEMENT between two independent graders of "
    "the fifth run's rationales; it is not this measurement, and this row neither "
    "confirms nor replaces it."
)


class ProcessScorecardReconstructionError(RuntimeError):
    """A committed recording did not reconstruct under the walk's profile.

    Fail-loud rather than a partial fold: row 3 compares a spoken alibi against
    the ENGINE'S route, so a recording whose state hashes do not verify would
    yield a route the engine never produced and a census nobody could trust.
    """


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base — the ``eval/`` report convention."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class RateCell(_FrozenModel):
    """One rate beside the three counts that produce it.

    ``rate`` is ``None`` iff ``denominator`` is 0 — the package's
    None-iff-undefined convention, never ``0.0``. ``not_evaluable`` is published
    separately rather than folded into either side, so a reader can tell a cell
    that measured nothing from one that measured a zero.
    """

    numerator: int
    denominator: int
    not_evaluable: int
    rate: float | None

    @model_validator(mode="after")
    def _counts_are_coherent(self) -> RateCell:
        if self.numerator < 0 or self.denominator < 0 or self.not_evaluable < 0:
            raise ValueError("process-scorecard counts must be non-negative")
        if self.numerator > self.denominator:
            raise ValueError(
                f"numerator exceeds denominator: {self.numerator} > {self.denominator}"
            )
        if self.denominator == 0:
            if self.rate is not None:
                raise ValueError("rate must be None when the denominator is 0")
        elif self.rate is None:
            raise ValueError("rate must be set when the denominator is > 0")
        return self


class ArgmaxIndependenceRow(_FrozenModel):
    """Row 2: how often a crew EJECT is the voter's own arithmetic argmax."""

    definition: str
    unambiguous_ballots: int
    followers: int
    deviators: int
    follower_role_correct: int
    deviator_role_correct: int
    ties_excluded: int
    no_rendered_row: int
    follower_share: float | None
    deviator_share: float | None
    follower_role_correct_share: float | None
    deviator_role_correct_share: float | None
    chance_baseline: float | None
    zero_flag_followers: int
    zero_flag_deviators: int
    zero_flag_follower_role_correct: int
    zero_flag_deviator_role_correct: int


class ManufacturedContradictionRow(_FrozenModel):
    """Row 3: alibi flags the claim schema invented, plus the claim census."""

    definition: str
    flags: RateCell
    # A manufactured flag splits two ways, and the split is published because
    # the pooled rate alone would read as one failure when it is two: a flag
    # against a claim the route makes true at EVERY tick contradicts a wholly
    # honest account, while one against a claim true only at SOME tick is the
    # envelope artifact proper — the moving player compressed into one room.
    manufactured_on_a_wholly_true_claim: int
    self_alibi_claims: int
    self_alibi_claims_multi_tick: int
    self_alibi_claims_envelope_false: int
    self_alibi_claims_envelope_false_multi_tick: int
    self_alibi_claims_strict_false: int
    self_alibi_claims_unresolvable: int
    other_subject_alibi_claims: int


class UnexplainedDecisionRow(_FrozenModel):
    """Row 4: decisions carrying no machine-checkable basis at all."""

    definition: str
    decisions: RateCell
    uncited_ejects: int
    skips_naming_no_player: int
    skips_with_considered_alternatives: int
    skips_naming_a_player_in_prose: int


class EvidenceQualityMixRow(_FrozenModel):
    """Row 5: what each ejection rested on, role-blind, with roles reported beside."""

    definition: str
    ejections: int
    band_counts: Mapping[str, int]
    band_role_correct: Mapping[str, int]


class RationaleFaithfulnessRow(_FrozenModel):
    """Row 6: whether a rationale's tokens are present in what the voter held."""

    definition: str
    ballots: RateCell
    tokens_checked: int
    tokens_absent: int
    limits: str


class AgentAuthoredRow(_FrozenModel):
    """Row 7: the share of ballots the meeting layer did not re-aim."""

    definition: str
    ballots: RateCell
    rewrite_reasons: Mapping[str, int]
    marker_unwound_without_typed_reason: int
    citation_nulled_target_intact: int
    redirect_marker_ballots: int
    redirect_marker_eject_ballots: int
    redirect_marker_coerced_skip_ballots: int


class ContextCells(_FrozenModel):
    """Context from the two analyzers the card names, adopted and never recomputed."""

    impostor_alibis: int
    impostor_alibis_survived: int
    impostor_alibi_survival_rate: float | None
    reporter_slots: int
    reporter_ejections: int
    innocent_non_reporter_slots: int
    innocent_non_reporter_ejections: int


class SetScorecard(_FrozenModel):
    """The nine rows over one labelled group of recordings."""

    label: str
    sources: tuple[str, ...]
    games: int
    meetings: int
    ballots: int
    eject_ballots: int
    skip_ballots: int
    grounded_eject: RateCell
    grounded_skip: RateCell
    grounded_all: RateCell
    grounded_definition: str
    argmax_independence: ArgmaxIndependenceRow
    manufactured_contradiction: ManufacturedContradictionRow
    unexplained_decision: UnexplainedDecisionRow
    evidence_quality_mix: EvidenceQualityMixRow
    rationale_faithfulness: RationaleFaithfulnessRow
    agent_authored_share: AgentAuthoredRow
    wrong_but_believable: RateCell
    wrong_but_believable_definition: str
    wrong_but_believable_label: str
    role_correct_ejection: RateCell
    role_correct_ejection_definition: str
    role_correct_ejection_label: str
    context: ContextCells


class FifthRunArm(_FrozenModel):
    """One arm of the fifth run's archive, counts only."""

    arm: str
    recordings: int
    meetings: int
    eject_ballots: int
    eject_ballots_cited: int
    skip_ballots: int
    skip_ballots_cited: int


class FifthRunAppendix(_FrozenModel):
    """The closing appendix — labelled OUT of the headline, read and never written."""

    label: str
    archive: str
    note: str
    arms: tuple[FifthRunArm, ...]
    ballots_per_meeting: Mapping[str, int]


class ProcessScorecard(_FrozenModel):
    """The published fold: per-set rows, two pooled groups and the appendix."""

    schema_version: int
    decision_date: str
    role_correctness_is_a_gate: bool
    role_correctness_reported: bool
    role_correctness_note: str
    no_consumer_note: str
    row_definitions: Mapping[str, str]
    report_format_version: int
    recording_provenance: tuple[str, ...]
    sets: tuple[SetScorecard, ...]
    pooled: SetScorecard
    pooled_9p2i: SetScorecard
    appendix: FifthRunAppendix

    @model_validator(mode="after")
    def _role_correctness_stays_demoted(self) -> ProcessScorecard:
        """The D1 demotion is a typed invariant, not a sentence in a header."""

        if self.role_correctness_is_a_gate or not self.role_correctness_reported:
            raise ValueError(
                "role-correctness is reported and is not a gate (decision D1, "
                f"{DECISION_DATE}); a scorecard claiming otherwise is not one"
            )
        if set(self.row_definitions) != set(ROW_DEFINITIONS):
            raise ValueError(
                "every published row carries its own definition: "
                f"{sorted(set(ROW_DEFINITIONS) ^ set(self.row_definitions))}"
            )
        return self


# ---------------------------------------------------------------------------
# Tallies — integers only, so pooling is addition and nothing is averaged twice
# ---------------------------------------------------------------------------


@dataclass
class ProcessTally:
    """Every count one group contributes, summed field-wise when groups pool.

    Counts only, with two exceptions that are still exact: ``chance_share_sum``
    is a :class:`~fractions.Fraction` (a mean of per-ballot shares with
    different denominators cannot be recovered from two integers, and a float
    accumulator would make pooling order-sensitive), and the two ``Mapping``
    fields are count tables keyed by a class name.
    """

    games: int = 0
    meetings: int = 0
    ballots: int = 0
    eject_ballots: int = 0
    skip_ballots: int = 0
    no_prompt_ballots: int = 0

    grounded_eject: int = 0
    grounded_skip: int = 0

    followers: int = 0
    deviators: int = 0
    follower_role_correct: int = 0
    deviator_role_correct: int = 0
    argmax_ties: int = 0
    argmax_no_row: int = 0
    zero_flag_followers: int = 0
    zero_flag_deviators: int = 0
    zero_flag_follower_role_correct: int = 0
    zero_flag_deviator_role_correct: int = 0
    chance_share_sum: Fraction = Fraction(0)
    chance_ballots: int = 0

    alibi_flags: int = 0
    alibi_flags_manufactured: int = 0
    alibi_flags_manufactured_wholly_true: int = 0
    alibi_flags_not_evaluable: int = 0
    self_alibi_claims: int = 0
    self_alibi_multi_tick: int = 0
    self_alibi_envelope_false: int = 0
    self_alibi_envelope_false_multi_tick: int = 0
    self_alibi_strict_false: int = 0
    self_alibi_unresolvable: int = 0
    other_subject_alibi_claims: int = 0

    unexplained: int = 0
    uncited_ejects: int = 0
    skips_naming_no_player: int = 0
    skips_with_alternatives: int = 0
    skips_naming_a_player_in_prose: int = 0

    ejections: int = 0
    ejections_role_correct: int = 0
    band_counts: dict[str, int] = field(default_factory=dict)
    band_role_correct: dict[str, int] = field(default_factory=dict)

    faithful_ballots: int = 0
    faithfulness_checked: int = 0
    faithfulness_no_token: int = 0
    tokens_checked: int = 0
    tokens_absent: int = 0

    authored_ballots: int = 0
    rewrite_reasons: dict[str, int] = field(default_factory=dict)
    marker_unwound_without_typed_reason: int = 0
    citation_nulled_target_intact: int = 0
    redirect_marker_ballots: int = 0
    redirect_marker_eject_ballots: int = 0
    redirect_marker_coerced_skip_ballots: int = 0

    wrong_but_believable: int = 0

    impostor_alibis: int = 0
    impostor_alibis_survived: int = 0
    reporter_slots: int = 0
    reporter_ejections: int = 0
    innocent_non_reporter_slots: int = 0
    innocent_non_reporter_ejections: int = 0


def _add(left: ProcessTally, right: ProcessTally) -> ProcessTally:
    """Field-wise sum of two tallies — every field is a count or a count table."""

    merged = ProcessTally()
    for entry in dataclasses.fields(ProcessTally):
        a = getattr(left, entry.name)
        b = getattr(right, entry.name)
        if isinstance(a, dict):
            table = dict(a)
            for key, value in b.items():
                table[key] = table.get(key, 0) + value
            setattr(merged, entry.name, table)
        else:
            setattr(merged, entry.name, a + b)
    return merged


def _cell(numerator: int, denominator: int, not_evaluable: int = 0) -> RateCell:
    """A rate cell whose rate is ``None`` iff its denominator is 0."""

    return RateCell(
        numerator=numerator,
        denominator=denominator,
        not_evaluable=not_evaluable,
        rate=round(numerator / denominator, 6) if denominator else None,
    )


def _share(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


# ---------------------------------------------------------------------------
# Inputs — what one group of recordings supplies to the pure fold
# ---------------------------------------------------------------------------

#: ``seed -> engine tick -> player -> room``. Engine ticks, not agent ticks.
Routes = Mapping[int, Mapping[int, Mapping[PlayerId, RoomId]]]


@dataclass(frozen=True)
class SetInputs:
    """Everything the pure fold needs about one committed replay set.

    Separating this from :func:`load_set_inputs` is what makes every row
    plantable: a test builds a two-meeting :class:`~eval.report_schema.GameReport`
    and a three-tick route by hand and folds it, with no replay on disk and no
    walk to run.
    """

    label: str
    source: str
    games: tuple[GameReport, ...]
    routes: Routes
    rooms: tuple[RoomId, ...]
    context: ContextCells


def _raise_walk_violation(violation: WalkViolation) -> NoReturn:
    """Turn a profile violation into this module's fail-loud error."""

    raise ProcessScorecardReconstructionError(
        f"process scorecard: replay walk violation {violation.kind} in "
        f"{violation.game_id} — the engine route is the ground truth row 3 "
        "rests on, so a recording that does not reconstruct is refused rather "
        "than folded"
    )


def _walk_config() -> ReplayWalkConfig:
    """A state-hash-verifying profile: the route is ground truth or it is nothing.

    A violated hash raises rather than yielding a route the engine never
    produced — an instrument must never silently under-measure (AGENTS.md "no
    silent fallbacks"), and row 3's whole claim is that the route is the
    engine's own.
    """

    return ReplayWalkConfig(
        profile="process-scorecard",
        on_violation=_raise_walk_violation,
        verify_tick_hashes=True,
        supports_temporal_observations=True,
        supports_experiments=True,
    )


def walk_routes(
    sample_dir: Path,
    *,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    game_map: Map,
) -> Routes:
    """Every game's per-tick room table, from a state-hash-verified engine walk.

    ``route[seed][t][player]`` is the room ``player`` occupied in the engine's
    POST-advance state of tick ``t`` — the frame the row's ``state_hash``
    covers. Tick ``-1`` is the seeded PRE-advance state of tick 0, which is what
    an agent-frame tick 0 describes; without it a claim covering the game's
    first tick would read as unresolvable and, counted as false, would inflate
    the envelope census by 11 claims on the shipped 9p2i corpora.
    """

    config = _walk_config()
    routes: dict[int, dict[int, Mapping[PlayerId, RoomId]]] = {}
    for seed in seeds_on_disk(sample_dir):
        per_tick: dict[int, Mapping[PlayerId, RoomId]] = {}
        for event in walk_replay(
            sample_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
            config=config,
        ):
            if isinstance(event, TickOpened):
                per_tick.setdefault(
                    event.entry.tick - 1,
                    {pid: player.room for pid, player in event.state.players.items()},
                )
            elif isinstance(event, TickAdvanced):
                per_tick[event.entry.tick] = {
                    pid: player.room for pid, player in event.state.players.items()
                }
        routes[seed] = per_tick
    return routes


def load_set_inputs(sample_dir: Path, *, game_map: Map | None = None) -> SetInputs:
    """Load one committed replay set: the eval report, the routes, the context.

    Impure by design — everything downstream of it is a pure fold. Roles come
    from :func:`eval.validity.roles_by_seed`, the seeder
    ``scripts/build_sample_report.py`` takes them from, and are read for rows 2,
    5, 8 and 9 only. No model is called.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    report = load_tournament_report(
        sample_dir,
        roles_by_seed=per_seed_roles,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    routes = walk_routes(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=resolved_map,
    )
    alibi = compute_alibi_fabrication_rate(report)
    reporter = compute_reporter_justice(sample_dir)
    label = f"{sample_dir.parent.name}/{sample_dir.name}"
    return SetInputs(
        label=label,
        source=f"replays/{label}",
        games=report.games,
        routes=routes,
        rooms=tuple(sorted(resolved_map.rooms)),
        context=_context_cells(alibi.total_impostor_alibis, alibi.survived, reporter),
    )


def _context_cells(
    impostor_alibis: int, survived: int, reporter: ReporterJusticeCells
) -> ContextCells:
    return ContextCells(
        impostor_alibis=impostor_alibis,
        impostor_alibis_survived=survived,
        impostor_alibi_survival_rate=_share(survived, impostor_alibis),
        reporter_slots=reporter.reporter_slots,
        reporter_ejections=reporter.reporter_ejections,
        innocent_non_reporter_slots=reporter.innocent_non_reporter_slots,
        innocent_non_reporter_ejections=reporter.innocent_non_reporter_ejections,
    )


# ---------------------------------------------------------------------------
# The fold
# ---------------------------------------------------------------------------


def _prompt_lines_by_voter(meeting: MeetingReport) -> dict[PlayerId, list[str]]:
    """Every line of every prompt each agent received in this meeting.

    The grader's surface, as :mod:`meetings.citation_relevance` describes it:
    the recording-time guard holds one rendered ballot prompt, an offline reader
    holds every prompt that voter received during the unit. Taking the union is
    what makes "resolves in the voter's OWN inputs" answerable offline without
    faking the guard's surface.
    """

    lines: dict[PlayerId, list[str]] = {}
    for call in meeting.llm_calls:
        if call.agent_id is None:
            continue
        lines.setdefault(call.agent_id, []).extend(call.prompt.splitlines())
    return lines


def _citation_resolves(
    ballot: VoteBallot,
    *,
    turn_ids: frozenset[str],
    lines: Sequence[str],
) -> bool:
    """Whether either citation channel resolves in the voter's own inputs."""

    if ballot.primary_reason_id is not None and ballot.primary_reason_id in turn_ids:
        return True
    observation = ballot.primary_reason_observation_id
    return observation is not None and any(
        carries_citation(line, observation) for line in lines
    )


def _bears_on_any(
    ballot: VoteBallot,
    subjects: Iterable[PlayerId],
    *,
    turns_by_id: Mapping[str, MeetingTurn],
    lines: Sequence[str],
) -> bool:
    """Whether the ballot's citations bear on any of ``subjects``."""

    return any(
        citations_bear_on(
            cited_turn_id=ballot.primary_reason_id,
            cited_observation_id=ballot.primary_reason_observation_id,
            subject=subject,
            turns_by_id=turns_by_id,
            lines=lines,
        )
        for subject in subjects
    )


def _is_grounded(
    ballot: VoteBallot,
    *,
    turns_by_id: Mapping[str, MeetingTurn],
    turn_ids: frozenset[str],
    lines: Sequence[str],
) -> bool:
    """Row 1 for one ballot: a citation that resolves AND bears on the subject."""

    if not _citation_resolves(ballot, turn_ids=turn_ids, lines=lines):
        return False
    subjects: tuple[PlayerId, ...] = (
        tuple(ballot.considered_alternatives)
        if ballot.target == "SKIP"
        else (ballot.target,)
    )
    return bool(subjects) and _bears_on_any(
        ballot, subjects, turns_by_id=turns_by_id, lines=lines
    )


def _claim_truth(
    claim: AlibiClaim,
    speaker: PlayerId,
    route: Mapping[int, Mapping[PlayerId, RoomId]],
) -> tuple[bool, bool] | None:
    """``(true at every tick, true at some tick)`` for one self-alibi claim.

    ``None`` when the claim's span reaches a tick the walk does not hold — the
    not-evaluable branch, published rather than counted as a lie.
    """

    every = True
    some = False
    for spoken_tick in range(claim.from_tick, claim.to_tick + 1):
        rooms = route.get(spoken_tick - AGENT_CLOCK_OFFSET)
        if rooms is None:
            return None
        if rooms.get(speaker) == claim.room:
            some = True
        else:
            every = False
    return every, some


def _self_alibi_truths(
    meeting: MeetingReport, route: Mapping[int, Mapping[PlayerId, RoomId]]
) -> dict[PlayerId, list[tuple[bool, bool] | None]]:
    """Each speaker's own alibi claims in this meeting, resolved against the route."""

    truths: dict[PlayerId, list[tuple[bool, bool] | None]] = {}
    for turn in meeting.transcript.turns:
        for claim in turn.claims:
            if isinstance(claim, AlibiClaim) and claim.subject == turn.speaker:
                truths.setdefault(turn.speaker, []).append(
                    _claim_truth(claim, turn.speaker, route)
                )
    return truths


def _flag_is_manufactured(
    flag: ContradictionRef,
    truths: Mapping[PlayerId, Sequence[tuple[bool, bool] | None]],
) -> tuple[bool, bool] | None:
    """``(manufactured, rests on a wholly true claim)``; ``None`` when unanswerable.

    ``None`` on two shapes, both published as not-evaluable rather than scored:
    a flag naming no speaker who filed a self-alibi in this meeting (there is no
    claim to test), and one whose claim reaches a tick the walk does not hold.
    Otherwise the flag is MANUFACTURED iff some named speaker's own alibi was
    true at some tick of its span — a claim false at every tick is a lie the
    detector caught, not an artifact the schema minted. The second element says
    whether some named speaker's claim was true at EVERY tick, which separates a
    flag against a wholly honest account from the span-envelope artifact.
    """

    resolved = [truth for subject in flag.subjects for truth in truths.get(subject, ())]
    if not resolved or any(truth is None for truth in resolved):
        return None
    return any(truth[1] for truth in resolved if truth is not None), any(
        truth[0] for truth in resolved if truth is not None
    )


def _room_spellings(
    rooms: Sequence[RoomId],
) -> tuple[tuple[RoomId, tuple[str, ...]], ...]:
    """Each canonical room id beside the spellings prose may use for it.

    ``EAST_HALL`` is written ``EAST_HALL`` in a rendered memory line and ``East
    Hall`` at the table, so both spellings resolve to the one id on the
    extraction side AND on the check side — a room the voter held must not read
    as absent merely because the rationale wrote it the human way.
    """

    return tuple(
        (room, (room.lower(), room.replace("_", " ").lower())) for room in rooms
    )


def _ejection_band(
    meeting: MeetingReport,
    ejected: PlayerId,
    *,
    turns_by_id: Mapping[str, MeetingTurn],
    turn_ids: frozenset[str],
    lines_by_voter: Mapping[PlayerId, Sequence[str]],
) -> str:
    """Row 5's band for one ejection, decided role-blind and highest band first."""

    if any(
        flag.kind == "vent_sighting" and ejected in flag.subjects
        for flag in meeting.contradictions
    ):
        return "vent_flag"
    if any(ejected in flag.subjects for flag in recorded_contradiction_flags(meeting)):
        return "contradiction_flag"
    hearsay = False
    for ballot in meeting.ballots:
        if ballot.target != ejected:
            continue
        lines = lines_by_voter.get(ballot.voter, ())
        if not _citation_resolves(ballot, turn_ids=turn_ids, lines=lines):
            continue
        if not _bears_on_any(ballot, (ejected,), turns_by_id=turns_by_id, lines=lines):
            continue
        if ballot.primary_reason_observation_id is not None:
            return "first_hand"
        turn = turns_by_id.get(ballot.primary_reason_id or "")
        if turn is None:
            continue
        if _observes_player(turn, ejected):
            return "first_hand"
        if any(isinstance(claim, AccusationClaim) for claim in turn.claims):
            hearsay = True
    return "hearsay" if hearsay else "unevidenced"


def _observes_player(turn: MeetingTurn, player: PlayerId) -> bool:
    """Whether a turn carries a structured observation NAMING ``player``.

    Row 5's ``first_hand`` band asks for an observation ABOUT the ejected
    player, so a non-empty ``observations`` tuple is not enough: a turn whose
    only observation places somebody else, or whose speaker happens to be the
    ejected player, carries no first-hand account of THEM and falls through to
    the hearsay / unevidenced test the way the published definition says it
    should.

    The observation is walked as the DUMPED STRUCTURE
    (:func:`meetings.citation_relevance.every_string_in`) for the reason
    :func:`meetings.citation_relevance.turn_bears_on` gives: the eight
    observation shapes name players under ``subject``, ``co_present`` and
    ``body_of``, and a rule enumerating those keys would silently stop covering
    the ones a later schema adds. The name half is the
    whole-token :func:`~meetings.citation_relevance.names_player` boundary, so
    ``p-1`` never answers for ``p-10``. Deliberately NOT ``turn_bears_on``
    itself, which is true for the speaker's own turn and for a name appearing
    anywhere in a CLAIM or in free text - that is the aboutness rule row 1
    asks, not the evidence-shape rule this band asks.
    """

    return any(
        names_player(text, player)
        for observation in turn.observations
        for text in every_string_in(observation.model_dump(mode="json"))
    )


def _rationale_tokens(
    rationale: str, spellings: Sequence[tuple[RoomId, tuple[str, ...]]]
) -> list[tuple[str, str]]:
    """``(kind, token)`` for every player id, room id and tick a rationale names."""

    tokens: list[tuple[str, str]] = [
        ("player", pid) for pid in sorted(set(_PLAYER_TOKEN_RE.findall(rationale)))
    ]
    lowered = rationale.lower()
    tokens.extend(
        ("room", room)
        for room, written in spellings
        if any(_whole_token(spelling, lowered) for spelling in written)
    )
    tokens.extend(
        ("tick", tick) for tick in sorted(set(_TICK_REFERENCE_RE.findall(rationale)))
    )
    return tokens


def _whole_token(spelling: str, lowered_text: str) -> bool:
    """Whether ``spelling`` appears in already-lowercased text as a whole token."""

    return (
        re.search(rf"(?<![0-9a-z_]){re.escape(spelling)}(?![0-9a-z_])", lowered_text)
        is not None
    )


def _token_is_held(
    kind: str,
    token: str,
    *,
    haystack: str,
    lowered_haystack: str,
    spellings: Mapping[RoomId, tuple[str, ...]],
) -> bool:
    """Whether one extracted token appears in what the voter actually held."""

    if kind == "player":
        return names_player(haystack, token)
    if kind == "room":
        return any(
            _whole_token(spelling, lowered_haystack)
            for spelling in spellings.get(token, (token.lower(),))
        )
    return (
        re.search(rf"\btick\s+{re.escape(token)}\b", haystack, re.IGNORECASE)
        is not None
    )


def _authored_by_the_agent(ballot: VoteBallot) -> tuple[bool, bool]:
    """``(the agent authored the recorded target, a marker unwound one)``.

    Both channels, because they do not agree by construction: the typed
    ``guard_rewrite_reason`` covers every
    :data:`~meetings.schemas.BallotTargetRewriteReason` member while the marker
    chain only carries the ones that prepend a target repr, and a recording made
    before the typed fields existed carries only the marker — which is the
    fallback ``meetings/schemas.py`` prescribes and
    :func:`eval.deduction_metrics._authored_target` implements.
    """

    chain = _scan_marker_chain(ballot.rationale_text)
    _target, unwound = _authored_target(ballot, chain)
    typed = ballot.guard_rewrite_reason is not None
    return (not typed and not unwound), (unwound and not typed)


def _model_authored_rationale(rationale: str) -> str:
    """What is left of a rationale once the GUARD's own audit prose is gone.

    The meeting layer prepends audit markers to ``rationale_text`` and those
    markers preserve ids: the teammate firewall writes
    ``[teammate target 'p-3' coerced to SKIP]`` and then REDACTS the model's
    body (:data:`~meetings.manager.TEAMMATE_COERCED_VOTE_RATIONALE`), so a
    coerced SKIP can carry a player id no agent put there. Row 4 asks whether
    the AGENT named anything it weighed, so it must read the model-authored
    remainder; asking the raw text lets the machinery answer for the voter and
    silently rescues a ballot with no basis at all.

    The cut is by PROVENANCE, not by pattern: it is the same anchored,
    repr-aware chain :func:`eval.deduction_metrics._scan_marker_chain` walks for
    every other guard-origin cell in this package, and ``consumed`` is how far
    that chain reached. ``api.replay_loader._parse_rewrite_reasons`` makes the
    identical cut for the spectator surface's ``rationale_text_clean``. A
    rationale that is ENTIRELY markers - the vote-parse default, whose bounded
    response head is machinery-written even though the head's bytes came from an
    unparseable completion - leaves the empty string, which is the honest
    reading: nothing parsed, so the agent named nothing.
    """

    return rationale[_scan_marker_chain(rationale).consumed :]


def fold_set(inputs: SetInputs) -> ProcessTally:
    """Fold one group of recordings into its counts. Pure: no I/O, no model call."""

    spellings = _room_spellings(inputs.rooms)
    tally = ProcessTally()
    tally.games = len(inputs.games)
    tally.impostor_alibis = inputs.context.impostor_alibis
    tally.impostor_alibis_survived = inputs.context.impostor_alibis_survived
    tally.reporter_slots = inputs.context.reporter_slots
    tally.reporter_ejections = inputs.context.reporter_ejections
    tally.innocent_non_reporter_slots = inputs.context.innocent_non_reporter_slots
    tally.innocent_non_reporter_ejections = (
        inputs.context.innocent_non_reporter_ejections
    )
    redirects = compute_ballot_target_redirects(inputs.games)
    tally.redirect_marker_ballots = redirects.redirected_ballots
    tally.redirect_marker_eject_ballots = redirects.redirected_eject_ballots
    tally.redirect_marker_coerced_skip_ballots = redirects.redirect_coerced_skip_ballots

    for game in inputs.games:
        route = inputs.routes.get(game.seed, {})
        for meeting in game.meetings:
            _fold_meeting(
                meeting, game=game, route=route, spellings=spellings, tally=tally
            )
    return tally


def _fold_meeting(
    meeting: MeetingReport,
    *,
    game: GameReport,
    route: Mapping[int, Mapping[PlayerId, RoomId]],
    spellings: Sequence[tuple[RoomId, tuple[str, ...]]],
    tally: ProcessTally,
) -> None:
    """Every row's contribution from one meeting, over one pass of its ballots."""

    roles = game.roles
    tally.meetings += 1
    turns_by_id: dict[str, MeetingTurn] = {
        turn.turn_id: turn for turn in meeting.transcript.turns
    }
    turn_ids = frozenset(turns_by_id)
    lines_by_voter = _prompt_lines_by_voter(meeting)
    transcript_text = json.dumps(
        meeting.transcript.model_dump(mode="json"), sort_keys=True
    )
    rendered = _rendered_suspicion_by_target_per_voter(meeting)
    valid_targets = rendered_valid_targets_by_voter(meeting)
    no_flag_meeting = not meeting.contradictions

    truths = _self_alibi_truths(meeting, route)
    _fold_alibi_census(meeting, route=route, tally=tally)
    manufactured_subjects: set[PlayerId] = set()
    for flag in meeting.contradictions:
        if flag.kind not in ALIBI_FLAG_KINDS:
            continue
        tally.alibi_flags += 1
        verdict = _flag_is_manufactured(flag, truths)
        if verdict is None:
            tally.alibi_flags_not_evaluable += 1
            continue
        manufactured, wholly_true = verdict
        if manufactured:
            tally.alibi_flags_manufactured += 1
            manufactured_subjects.update(flag.subjects)
            if wholly_true:
                tally.alibi_flags_manufactured_wholly_true += 1

    for ballot in meeting.ballots:
        tally.ballots += 1
        is_skip = ballot.target == "SKIP"
        if is_skip:
            tally.skip_ballots += 1
        else:
            tally.eject_ballots += 1

        authored, unwound_only = _authored_by_the_agent(ballot)
        if authored:
            tally.authored_ballots += 1
        if unwound_only:
            tally.marker_unwound_without_typed_reason += 1
        reason = ballot.guard_rewrite_reason
        if reason is not None:
            tally.rewrite_reasons[reason] = tally.rewrite_reasons.get(reason, 0) + 1
        else:
            chain = _scan_marker_chain(ballot.rationale_text)
            if (
                chain.any_marker
                and not chain.rewrote_target
                and not chain.parse_default
            ):
                tally.citation_nulled_target_intact += 1

        lines = lines_by_voter.get(ballot.voter)
        if lines is None:
            tally.no_prompt_ballots += 1
            continue

        resolves = _citation_resolves(ballot, turn_ids=turn_ids, lines=lines)
        grounded = _is_grounded(
            ballot, turns_by_id=turns_by_id, turn_ids=turn_ids, lines=lines
        )
        names_a_player = bool(
            _PLAYER_TOKEN_RE.search(_model_authored_rationale(ballot.rationale_text))
        )
        if is_skip:
            if grounded:
                tally.grounded_skip += 1
            if ballot.considered_alternatives:
                tally.skips_with_alternatives += 1
            if names_a_player:
                tally.skips_naming_a_player_in_prose += 1
            if not ballot.considered_alternatives and not names_a_player:
                tally.skips_naming_no_player += 1
                tally.unexplained += 1
        else:
            if grounded:
                tally.grounded_eject += 1
            if not resolves:
                tally.uncited_ejects += 1
                tally.unexplained += 1
            if (
                roles[ballot.target] != "IMPOSTOR"
                and grounded
                and ballot.target not in manufactured_subjects
            ):
                tally.wrong_but_believable += 1
            if roles[ballot.voter] == "CREWMATE":
                _fold_argmax(
                    ballot,
                    roles=roles,
                    rendered=rendered.get(ballot.voter, {}),
                    allowed=valid_targets.get(ballot.voter, frozenset()),
                    no_flag_meeting=no_flag_meeting,
                    tally=tally,
                )

        _fold_faithfulness(
            ballot,
            haystack=transcript_text + "\n" + "\n".join(lines),
            spellings=spellings,
            tally=tally,
        )

    if meeting.outcome == "EJECTED" and meeting.ejected_player_id is not None:
        ejected = meeting.ejected_player_id
        tally.ejections += 1
        correct = roles[ejected] == "IMPOSTOR"
        if correct:
            tally.ejections_role_correct += 1
        band = _ejection_band(
            meeting,
            ejected,
            turns_by_id=turns_by_id,
            turn_ids=turn_ids,
            lines_by_voter=lines_by_voter,
        )
        tally.band_counts[band] = tally.band_counts.get(band, 0) + 1
        tally.band_role_correct.setdefault(band, 0)
        if correct:
            tally.band_role_correct[band] += 1


def _fold_alibi_census(
    meeting: MeetingReport,
    *,
    route: Mapping[int, Mapping[PlayerId, RoomId]],
    tally: ProcessTally,
) -> None:
    """The claim census that rides beside row 3, over one meeting's transcript."""

    for turn in meeting.transcript.turns:
        for claim in turn.claims:
            if not isinstance(claim, AlibiClaim):
                continue
            if claim.subject != turn.speaker:
                tally.other_subject_alibi_claims += 1
                continue
            tally.self_alibi_claims += 1
            multi_tick = claim.to_tick > claim.from_tick
            if multi_tick:
                tally.self_alibi_multi_tick += 1
            truth = _claim_truth(claim, turn.speaker, route)
            if truth is None:
                tally.self_alibi_unresolvable += 1
                continue
            every, some = truth
            if not every:
                tally.self_alibi_envelope_false += 1
                if multi_tick:
                    tally.self_alibi_envelope_false_multi_tick += 1
            if not some:
                tally.self_alibi_strict_false += 1


def _fold_argmax(
    ballot: VoteBallot,
    *,
    roles: Mapping[PlayerId, Role],
    rendered: Mapping[PlayerId, float],
    allowed: frozenset[PlayerId],
    no_flag_meeting: bool,
    tally: ProcessTally,
) -> None:
    """Row 2's contribution from one crew EJECT ballot.

    The chance baseline accumulates AFTER the two non-coverage returns, so its
    population is the row's own denominator - the unambiguous ballots - exactly
    as the published definition says ("the mean, over the SAME unambiguous
    ballots that form the denominator"). A ballot that lands in
    ``argmax_no_row`` or ``argmax_ties`` is excluded from the split and is
    excluded from chance with it; folding it into chance alone would publish a
    baseline no denominator on the row accounts for, which
    :func:`scorecard_from_tally` now refuses outright.
    """

    rows = {target: value for target, value in rendered.items() if target in allowed}
    if not rows:
        tally.argmax_no_row += 1
        return
    best = max(rows.values())
    winners = [target for target, value in rows.items() if value == best]
    if len(winners) != 1:
        tally.argmax_ties += 1
        return
    # Past both returns ``allowed`` is non-empty by construction: every key of
    # ``rows`` is one of its members.
    impostors = sum(1 for target in allowed if roles[target] == "IMPOSTOR")
    tally.chance_share_sum += Fraction(impostors, len(allowed))
    tally.chance_ballots += 1
    correct = roles[ballot.target] == "IMPOSTOR"
    if winners[0] == ballot.target:
        tally.followers += 1
        tally.follower_role_correct += int(correct)
        if no_flag_meeting:
            tally.zero_flag_followers += 1
            tally.zero_flag_follower_role_correct += int(correct)
    else:
        tally.deviators += 1
        tally.deviator_role_correct += int(correct)
        if no_flag_meeting:
            tally.zero_flag_deviators += 1
            tally.zero_flag_deviator_role_correct += int(correct)


def _fold_faithfulness(
    ballot: VoteBallot,
    *,
    haystack: str,
    spellings: Sequence[tuple[RoomId, tuple[str, ...]]],
    tally: ProcessTally,
) -> None:
    """Row 6's contribution from one ballot's rationale."""

    tokens = _rationale_tokens(ballot.rationale_text, spellings)
    if not tokens:
        tally.faithfulness_no_token += 1
        return
    tally.faithfulness_checked += 1
    lowered = haystack.lower()
    written = dict(spellings)
    absent = sum(
        1
        for kind, token in tokens
        if not _token_is_held(
            kind,
            token,
            haystack=haystack,
            lowered_haystack=lowered,
            spellings=written,
        )
    )
    tally.tokens_checked += len(tokens)
    tally.tokens_absent += absent
    if absent == 0:
        tally.faithful_ballots += 1


def scorecard_from_tally(
    tally: ProcessTally, *, label: str, sources: Sequence[str]
) -> SetScorecard:
    """Build the published rows from a tally, deriving every rate exactly once."""

    chance = (
        round(float(tally.chance_share_sum / tally.chance_ballots), 6)
        if tally.chance_ballots
        else None
    )
    unambiguous = tally.followers + tally.deviators
    # The published definition says chance is the mean over the SAME ballots the
    # denominator counts, so the two populations are one population. They were
    # not once (chance accumulated before the tie and no-row returns), and a
    # baseline over a population no cell on the row accounts for is exactly the
    # kind of silent divergence AGENTS.md rule 5 says to raise on rather than
    # publish.
    if tally.chance_ballots != unambiguous:
        raise ValueError(
            "the chance baseline's population must be the row's denominator: "
            f"{tally.chance_ballots} chance ballots against {unambiguous} "
            "unambiguous ones"
        )
    return SetScorecard(
        label=label,
        sources=tuple(sources),
        games=tally.games,
        meetings=tally.meetings,
        ballots=tally.ballots,
        eject_ballots=tally.eject_ballots,
        skip_ballots=tally.skip_ballots,
        grounded_definition=ROW_DEFINITIONS["grounded_decision_rate"],
        grounded_eject=_cell(
            tally.grounded_eject, tally.eject_ballots, tally.no_prompt_ballots
        ),
        grounded_skip=_cell(
            tally.grounded_skip, tally.skip_ballots, tally.no_prompt_ballots
        ),
        grounded_all=_cell(
            tally.grounded_eject + tally.grounded_skip,
            tally.ballots,
            tally.no_prompt_ballots,
        ),
        argmax_independence=ArgmaxIndependenceRow(
            definition=ROW_DEFINITIONS["argmax_independence"],
            unambiguous_ballots=unambiguous,
            followers=tally.followers,
            deviators=tally.deviators,
            follower_role_correct=tally.follower_role_correct,
            deviator_role_correct=tally.deviator_role_correct,
            ties_excluded=tally.argmax_ties,
            no_rendered_row=tally.argmax_no_row,
            follower_share=_share(tally.followers, unambiguous),
            deviator_share=_share(tally.deviators, unambiguous),
            follower_role_correct_share=_share(
                tally.follower_role_correct, tally.followers
            ),
            deviator_role_correct_share=_share(
                tally.deviator_role_correct, tally.deviators
            ),
            chance_baseline=chance,
            zero_flag_followers=tally.zero_flag_followers,
            zero_flag_deviators=tally.zero_flag_deviators,
            zero_flag_follower_role_correct=tally.zero_flag_follower_role_correct,
            zero_flag_deviator_role_correct=tally.zero_flag_deviator_role_correct,
        ),
        manufactured_contradiction=ManufacturedContradictionRow(
            definition=ROW_DEFINITIONS["manufactured_contradiction_rate"],
            flags=_cell(
                tally.alibi_flags_manufactured,
                tally.alibi_flags,
                tally.alibi_flags_not_evaluable,
            ),
            manufactured_on_a_wholly_true_claim=(
                tally.alibi_flags_manufactured_wholly_true
            ),
            self_alibi_claims=tally.self_alibi_claims,
            self_alibi_claims_multi_tick=tally.self_alibi_multi_tick,
            self_alibi_claims_envelope_false=tally.self_alibi_envelope_false,
            self_alibi_claims_envelope_false_multi_tick=(
                tally.self_alibi_envelope_false_multi_tick
            ),
            self_alibi_claims_strict_false=tally.self_alibi_strict_false,
            self_alibi_claims_unresolvable=tally.self_alibi_unresolvable,
            other_subject_alibi_claims=tally.other_subject_alibi_claims,
        ),
        unexplained_decision=UnexplainedDecisionRow(
            definition=ROW_DEFINITIONS["unexplained_decision_rate"],
            decisions=_cell(tally.unexplained, tally.ballots, tally.no_prompt_ballots),
            uncited_ejects=tally.uncited_ejects,
            skips_naming_no_player=tally.skips_naming_no_player,
            skips_with_considered_alternatives=tally.skips_with_alternatives,
            skips_naming_a_player_in_prose=tally.skips_naming_a_player_in_prose,
        ),
        evidence_quality_mix=EvidenceQualityMixRow(
            definition=ROW_DEFINITIONS["evidence_quality_mix"],
            ejections=tally.ejections,
            band_counts=dict(sorted(tally.band_counts.items())),
            band_role_correct=dict(sorted(tally.band_role_correct.items())),
        ),
        rationale_faithfulness=RationaleFaithfulnessRow(
            definition=ROW_DEFINITIONS["rationale_faithfulness"],
            ballots=_cell(
                tally.faithful_ballots,
                tally.faithfulness_checked,
                tally.faithfulness_no_token + tally.no_prompt_ballots,
            ),
            tokens_checked=tally.tokens_checked,
            tokens_absent=tally.tokens_absent,
            limits=FAITHFULNESS_LIMITS,
        ),
        agent_authored_share=AgentAuthoredRow(
            definition=ROW_DEFINITIONS["agent_authored_share"],
            ballots=_cell(tally.authored_ballots, tally.ballots),
            rewrite_reasons=dict(sorted(tally.rewrite_reasons.items())),
            marker_unwound_without_typed_reason=(
                tally.marker_unwound_without_typed_reason
            ),
            citation_nulled_target_intact=tally.citation_nulled_target_intact,
            redirect_marker_ballots=tally.redirect_marker_ballots,
            redirect_marker_eject_ballots=tally.redirect_marker_eject_ballots,
            redirect_marker_coerced_skip_ballots=(
                tally.redirect_marker_coerced_skip_ballots
            ),
        ),
        wrong_but_believable=_cell(
            tally.wrong_but_believable, tally.eject_ballots, tally.no_prompt_ballots
        ),
        wrong_but_believable_definition=ROW_DEFINITIONS["wrong_but_believable_rate"],
        wrong_but_believable_label="reported, never penalised",
        role_correct_ejection=_cell(tally.ejections_role_correct, tally.ejections),
        role_correct_ejection_definition=ROW_DEFINITIONS["role_correct_ejection_rate"],
        role_correct_ejection_label="reported beside, never a gate",
        context=ContextCells(
            impostor_alibis=tally.impostor_alibis,
            impostor_alibis_survived=tally.impostor_alibis_survived,
            impostor_alibi_survival_rate=_share(
                tally.impostor_alibis_survived, tally.impostor_alibis
            ),
            reporter_slots=tally.reporter_slots,
            reporter_ejections=tally.reporter_ejections,
            innocent_non_reporter_slots=tally.innocent_non_reporter_slots,
            innocent_non_reporter_ejections=tally.innocent_non_reporter_ejections,
        ),
    )


def pool(
    tallies: Sequence[ProcessTally], *, label: str, sources: Sequence[str]
) -> SetScorecard:
    """Pool disjoint groups by ADDING their counts, never by averaging rates.

    Every field is a count over disjoint recordings, so pooling is addition and
    each rate recomputes from the pooled numerator and denominator — a small set
    cannot drag a rate the way a mean of rates would. The chance baseline pools
    the same way because it is carried as an exact sum of per-ballot shares plus
    the ballot count, not as a float mean.
    """

    merged = ProcessTally()
    for tally in tallies:
        merged = _add(merged, tally)
    return scorecard_from_tally(merged, label=label, sources=sources)


# ---------------------------------------------------------------------------
# The fifth run's archive — a closing appendix, read and never written
# ---------------------------------------------------------------------------

#: What the appendix says about itself wherever it is published.
APPENDIX_NOTE: Final[str] = (
    "OUT OF THE HEADLINE. The fifth run is a 3-ballot arena on a proof-free "
    "held-out band whose generator filters out the one evidence channel that "
    "reliably works, so neither arm is adoptable and neither arm's cells pool "
    "with the committed sets. It is reported because the two arms differ on the "
    "process measures the frozen outcome scored 0 and 2. Counts only: no prefix, "
    "prompt or transcript text is read into this artifact, and nothing under the "
    "archive is written."
)


def fold_fifth_run(archive: Path) -> FifthRunAppendix:
    """Fold the fifth run's per-arm recordings into counts. Read-only."""

    arms: dict[str, dict[str, int]] = {}
    per_meeting: dict[int, int] = {}
    for path in sorted(archive.glob("*-seed-*.jsonl")):
        arm = path.name.split("-seed-", 1)[0]
        cells = arms.setdefault(
            arm,
            {
                "recordings": 0,
                "meetings": 0,
                "eject": 0,
                "eject_cited": 0,
                "skip": 0,
                "skip_cited": 0,
            },
        )
        cells["recordings"] += 1
        for entry in read_all_entries(path):
            if not isinstance(entry, MeetingReplayEntry):
                continue
            cells["meetings"] += 1
            per_meeting[len(entry.ballots)] = per_meeting.get(len(entry.ballots), 0) + 1
            for ballot in entry.ballots:
                key = "skip" if ballot.target == "SKIP" else "eject"
                cells[key] += 1
                if (
                    ballot.primary_reason_id is not None
                    or ballot.primary_reason_observation_id is not None
                ):
                    cells[f"{key}_cited"] += 1
    if not arms:
        raise ValueError(
            f"{archive}: no arm recordings found — refusing to publish an empty "
            "appendix as a measurement"
        )
    return FifthRunAppendix(
        label="Appendix: the fifth run (2026-09-16), out of the headline",
        archive=_relative_to_repo(archive),
        note=APPENDIX_NOTE,
        arms=tuple(
            FifthRunArm(
                arm=arm,
                recordings=cells["recordings"],
                meetings=cells["meetings"],
                eject_ballots=cells["eject"],
                eject_ballots_cited=cells["eject_cited"],
                skip_ballots=cells["skip"],
                skip_ballots_cited=cells["skip_cited"],
            )
            for arm, cells in sorted(arms.items())
        ),
        ballots_per_meeting={
            str(size): count for size, count in sorted(per_meeting.items())
        },
    )


def _relative_to_repo(path: Path) -> str:
    """A repo-relative posix path, so the artifact names no machine's layout."""

    root = Path(__file__).resolve().parents[1]
    return path.resolve().relative_to(root).as_posix()


# ---------------------------------------------------------------------------
# The published fold
# ---------------------------------------------------------------------------

#: The four committed sets, in publication order, and the two that carry the
#: 9p2i pins the direction memo's sections 4 and 5 state.
COMMITTED_SETS: Final[tuple[str, ...]] = (
    "replays/ml_corpus/9p2i",
    "replays/samples/9p2i",
    "replays/ml_corpus/4p1i",
    "replays/samples/4p1i",
)
NINE_PLAYER_SETS: Final[tuple[str, ...]] = (
    "replays/ml_corpus/9p2i",
    "replays/samples/9p2i",
)

#: The fifth run's archive, bound by the card: read, never written, never moved.
FIFTH_RUN_ARCHIVE: Final[str] = "audits/deduction-candidate/run-2026-09-16"


def scorecard_source_paths(root: Path) -> tuple[Path, ...]:
    """Every committed input this fold reads, for the writer's destination guard."""

    paths = [
        path
        for name in (*COMMITTED_SETS, FIFTH_RUN_ARCHIVE)
        for path in (root / name).rglob("*")
        if path.is_file()
    ]
    return tuple(sorted(paths))


def compute_process_scorecard(root: Path) -> ProcessScorecard:
    """Fold the four committed sets plus the fifth run's archive into the suite.

    Zero model calls, on every path. The engine walk is state-hash-verified, the
    roles come from the seeder, and nothing is written anywhere.
    """

    game_map = load_canonical_map()
    inputs = [
        load_set_inputs(root / name, game_map=game_map) for name in COMMITTED_SETS
    ]
    tallies = {item.label: fold_set(item) for item in inputs}
    sets = tuple(
        scorecard_from_tally(
            tallies[item.label], label=item.label, sources=(item.source,)
        )
        for item in inputs
    )
    nine_player = [
        item for item in inputs if f"replays/{item.label}" in NINE_PLAYER_SETS
    ]
    return ProcessScorecard(
        schema_version=SCHEMA_VERSION,
        decision_date=DECISION_DATE,
        role_correctness_is_a_gate=False,
        role_correctness_reported=True,
        role_correctness_note=ROLE_CORRECTNESS_NOTE,
        no_consumer_note=NO_CONSUMER_NOTE,
        row_definitions=dict(ROW_DEFINITIONS),
        report_format_version=CURRENT_FORMAT_VERSION,
        recording_provenance=tuple(item.source for item in inputs),
        sets=sets,
        pooled=pool(
            [tallies[item.label] for item in inputs],
            label="pooled: all four committed sets",
            sources=tuple(item.source for item in inputs),
        ),
        pooled_9p2i=pool(
            [tallies[item.label] for item in nine_player],
            label="pooled: the two 9p2i sets",
            sources=tuple(item.source for item in nine_player),
        ),
        appendix=fold_fifth_run(root / FIFTH_RUN_ARCHIVE),
    )


def serialize_scorecard(scorecard: ProcessScorecard) -> str:
    """Deterministic JSON: sorted keys, two-space indent, one trailing newline."""

    return (
        json.dumps(
            scorecard.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )


__all__ = [
    "AGENT_CLOCK_OFFSET",
    "ALIBI_FLAG_KINDS",
    "APPENDIX_NOTE",
    "COMMITTED_SETS",
    "DECISION_DATE",
    "FAITHFULNESS_LIMITS",
    "FIFTH_RUN_ARCHIVE",
    "NINE_PLAYER_SETS",
    "NO_CONSUMER_NOTE",
    "ROLE_CORRECTNESS_NOTE",
    "ROW_DEFINITIONS",
    "SCHEMA_VERSION",
    "AgentAuthoredRow",
    "ArgmaxIndependenceRow",
    "ContextCells",
    "EvidenceQualityMixRow",
    "FifthRunAppendix",
    "FifthRunArm",
    "ManufacturedContradictionRow",
    "ProcessScorecard",
    "ProcessScorecardReconstructionError",
    "ProcessTally",
    "RateCell",
    "RationaleFaithfulnessRow",
    "SetInputs",
    "SetScorecard",
    "UnexplainedDecisionRow",
    "compute_process_scorecard",
    "fold_fifth_run",
    "fold_set",
    "load_set_inputs",
    "pool",
    "scorecard_from_tally",
    "scorecard_source_paths",
    "serialize_scorecard",
    "walk_routes",
]
