"""The Phase-21 offline counterfactual: the Wave-2 slate over the re-recorded bytes.

One command, one shipping slate, one table. It prices the three Wave-2 levers --
``reporter_reasoning``, ``corroboration_discipline``, ``testimony_shapes`` -- over
the four committed replay sets and prints, per set and pooled with a numerator and
a denominator on every cell, what the recorded bytes can say about them offline.

Three columns, in this order, because the third is only worth reading once the
first two agree:

* **RECORDED-OFF** -- a committed instrument (``eval.reporter_justice``,
  ``eval.evidence_honesty``, ``eval.deduction_metrics`` read off each set's
  ``tournament-eval-report.json``) reading the recorded bytes. This IS the
  record's own substrate.
* **RECONSTRUCTED-OFF** -- the same cell folded from the re-derived inputs of one
  reconstruction walk with the whole slate OFF. A cell whose two OFF readings
  disagree prints no ON value: the counterfactual would be measuring the
  reconstruction, not the lever.
* **ON** -- a SECOND RENDER of the same rebuilt memory and the same recorded
  meeting inputs with the lever's argument supplied. The process environment is
  never written and no replay is read twice.

The ON column is a RENDER DIFF and is never fed back into the manager. The
reconstruction's recorded-response stub keys on EXACT prompt bytes, so a
lever-ON prompt would miss every recorded response and fail-soft the whole
meeting into a defaulted transcript, defaulted ballots and fictional memory from
meeting 1 onward. Every ON cell below therefore re-renders the OFF inputs and
counts bytes; nothing downstream of a model's reaction to those bytes is
predicted here, and the section that names what cannot be predicted is part of
the deliverable rather than a caveat.

The slate is toggled by ARGUMENT, and only one of the three arguments is an
``env`` mapping:

* ``testimony_shapes`` is env-parameterised on both its effect paths --
  :func:`meetings.manager.derive_reported_testimony` for the meeting reduction
  and :func:`agents.strategic.prompts.loader.build_prompt_renderers` for the
  three re-bodied templates;
* ``corroboration_discipline`` has no env seam on its effect path at all: its ON
  leg is obtained by CALLING
  :func:`meetings.corroboration.build_testimony_ledger` and passing the result
  as the ballot renderer's ``testimony_ledger=`` keyword;
* ``reporter_reasoning`` likewise: the manager resolves it from a
  constructor-bound boolean or the ambient environment, so its ON leg is
  obtained by constructing :class:`meetings.render_contract.ReporterContext` from
  recorded fields plus each speaker's own ``body_discovery_records`` and passing
  it as ``reporter_context=`` / ``at_body=``.

Instrument cells are imported, never re-implemented: no cell this table prints is
born here except the injustice ledger, which is a join over recorded fields plus
one declared judgment regex and lives here until a task that owns a gauge asks
for it.

Beside that table it prints a short block of TRIPWIRE READERS -- cells the
ratified pre-registration names as criteria and no published cell can evaluate:
the elicitation offer split by the speaker's role (its T5), the render budget at
the first meeting alone (its T7) and bar 1's non-direct cell split by a spoken
kill (its §5). They sit outside the published table because that table is a
census pinned row for row by the memo it appears in. None of them is a bar.

The reconstruction walk is :func:`tests.meetings.test_prompt_byte_golden.
walk_replay_meetings`. Importing it from a test module is deliberate and ruled:
it is the only committed reconstruction that drives the real ``MeetingManager``
and yields per-meeting participants carrying ``sighting_records``,
``move_witness_records`` and ``body_discovery_records`` -- all three of which the
Wave-2 ON legs need and which ``eval.replay_walk.walk_replay`` and
``api.replay_loader.ReplayLoader`` do not supply. ``.importlinter`` does not
model ``tests``; the inversion has precedent in ``eval/determinism_test.py`` and
``eval/leak_test.py``. Promoting the walk to a production home is Task 21.25's.

Purity: offline, no network, no LLM call, no replay written, no ``os.environ``
assignment.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, TextIO

# Allow `uv run python scripts/counterfactual_phase21.py ...` to find top-level
# packages (mirrors scripts/counterfactual_phase20.py).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.strategic.prompts.loader import (  # noqa: E402
    PromptRenderers,
    build_prompt_renderers,
)
from engine.entities import PlayerId, Role  # noqa: E402
from engine.world import load_canonical_map  # noqa: E402
from eval.evidence_honesty import (  # noqa: E402
    _RENDERED_ROW,
    _TESTIMONY_ROW,
    RenderBudgetCells,
    _living_bucket,
    compute_evidence_honesty,
)
from eval.deduction_metrics import ScaffoldLeakageCells, classify_flag  # noqa: E402
from eval.meeting_quality import TournamentEvalReport  # noqa: E402
from eval.reporter_justice import (  # noqa: E402
    ReporterJusticeCells,
    _meeting_trigger,
    compute_reporter_justice,
    pool_reporter_justice,
)
from eval.solvability import SolvabilityReport, compute_solvability_report  # noqa: E402
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk  # noqa: E402
from meetings.corroboration import (  # noqa: E402
    MeetingTestimonyLedger,
    build_testimony_ledger,
)
from meetings.render_contract import ReporterContext  # noqa: E402
from meetings.manager import (  # noqa: E402
    MeetingParticipant,
    _discoveries_in_window,
    _reporter_context_for,
    derive_reported_testimony,
)
from meetings.schemas import (  # noqa: E402
    AccusationClaim,
    ContradictionRef,
    MeetingResult,
    MeetingTranscript,
    ReportedStatement,
    SawKillObservation,
    SawVentObservation,
    SightingRecord,
    TurnKind,
    VoteBallot,
)
from meetings.transcript import is_weak_contradiction, turn_observation_id  # noqa: E402
from orchestrator.game import PROMPT_VERSION_SETS  # noqa: E402
from orchestrator.replay import (  # noqa: E402
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    ReplayEntry,
    _TOGGLEABLE_LEVER_RESOLVERS,
    env_var_for_lever,
    read_all_entries,
    substrate_flag_snapshot,
)
from tests.meetings.test_prompt_byte_golden import (  # noqa: E402
    ReconstructedMeeting,
    _seed_paths,
    walk_replay_meetings,
)

# --------------------------------------------------------------------------- #
# The slate.                                                                   #
# --------------------------------------------------------------------------- #

# The four committed sets, in the record audit's order.
CANONICAL_SETS: Final[tuple[str, ...]] = (
    "samples/9p2i",
    "ml_corpus/9p2i",
    "samples/4p1i",
    "ml_corpus/4p1i",
)

# The THREE Wave-2 levers this memo prices, in registration order.
WAVE_2_LEVERS: Final[tuple[str, ...]] = (
    "reporter_reasoning",
    "corroboration_discipline",
    "testimony_shapes",
)

# The live toggle the Wave-2 slate holds OFF. Its arm SWAPS ``accusation_round.j2``
# for a variant carrying neither sibling's block, so an all-four slate would drop
# the reporter and testimony-shapes effects from every statement turn while a
# composite stamp claimed them (tests/meetings/test_prompt_byte_golden.py, the
# file-swap gap). This script refuses a fourth key.
NON_WAVE_2_LEVER: Final[str] = "impostor_roll_call"

_SLATE_OFF: Final[str] = "OFF"
_SLATE_ALL_ON: Final[str] = "all-three-ON"

# The env mapping the ONE env-parameterised lever takes. The other two levers
# have no env seam on the path this script uses and are toggled by render kwarg.
_TESTIMONY_SHAPES_ENV: Final[Mapping[str, str]] = MappingProxyType(
    {env_var_for_lever("testimony_shapes"): "1"}
)

_KIND_CREWMATE_REPORT: Final[str] = "crewmate_report"
_KIND_IMPOSTOR_REPORT: Final[str] = "impostor_report"
_KIND_ACCUSATION_ROUND: Final[str] = "accusation_round"
_KIND_VOTE_BALLOT: Final[str] = "vote_ballot"
_TURN_KINDS: Final[tuple[str, ...]] = (
    _KIND_CREWMATE_REPORT,
    _KIND_IMPOSTOR_REPORT,
    _KIND_ACCUSATION_ROUND,
)

# --------------------------------------------------------------------------- #
# The committed OFF pins the table is proven against.                          #
# --------------------------------------------------------------------------- #

# audits/audit-phase-21-rerecord.md §5.1, published cell 2, plus the direct-proof
# and non-direct cells of published cell 1. Keyed by set directory under
# ``replays/``. A disagreement is a DEFECT IN THIS SCRIPT's join, not a finding
# about the bytes.
COMMITTED_INNOCENT_EJECTIONS: Final[Mapping[str, int]] = MappingProxyType(
    {
        "samples/9p2i": 13,
        "ml_corpus/9p2i": 29,
        "samples/4p1i": 4,
        "ml_corpus/4p1i": 0,
    }
)

# The four corroboration cells as the #415 merge-reality and #417 amendment
# records left them, over the pooled four-set walk. Task 21.19 shipped a walk
# that PRINTS them and deliberately asserts no figure; this script is where they
# first become an assertion.
COMMITTED_CORROBORATION_CELLS: Final[Mapping[str, tuple[int, int]]] = MappingProxyType(
    {
        "accused_without_a_first_hand_source": (475, 1525),
        "ejected_without_a_first_hand_source": (11, 425),
        "ejected_on_an_answering_turn": (33, 429),
        "ejected_with_a_walkable_pair": (48, 429),
    }
)

# --------------------------------------------------------------------------- #
# The one judgment net, committed rather than described.                       #
# --------------------------------------------------------------------------- #

IMPOSSIBLE_TRANSIT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"impossib|teleport|can'?t (?:be|walk|get|reach|make|sprint)|"
    r"cannot (?:be|walk|get|reach|traverse)|must have vent|had to vent|"
    r"you vented|they vented|not a walk|faster than|physically",
    re.I,
)
"""Ballot prose asserting a physical impossibility about the ejectee.

A JUDGMENT NET, and quoted as one wherever it appears: two independently written
classifiers agreed on the pooled total while disagreeing on two rows that
cancelled, and the net over-triggers on true statements about venting
("venting is impossible for crew"). Committed verbatim from the finding whose
verifier ruled on it (audits/review-2026-08-26/A/collated-findings.md:1298) so
the tagged rows can be re-judged rather than re-guessed. The charge it names is
"asserts a physical impossibility about a player who could not have performed
one": a crewmate's reconstructed route is map-legal by construction, so the
route test carries no information and is not run here.
"""

# --------------------------------------------------------------------------- #
# Public types.                                                                #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class LeverExposureCensus:
    """How many recorded prompts one lever's rendered surface reaches.

    ``changed`` is the number of prompts of ``prompt_class`` whose bytes MOVE
    under ``slate``; ``rendered`` is the number of prompts of that class the
    record holds. Exposure, never effect: a prompt the lever re-renders is not a
    vote that changes, and no consumer may subtract one of these counts from an
    injustice count.

    ``added_lines`` and ``added_bytes`` are the size of the change, so the render
    budget the three levers spend against is priced rather than assumed.
    """

    lever: str
    prompt_class: str
    rendered: int
    changed: int
    added_lines: int
    added_bytes: int

    @property
    def share(self) -> float:
        return self.changed / self.rendered if self.rendered else 0.0


@dataclass(frozen=True)
class InjusticeLedgerRow:
    """One innocent ejection, with the tags that classify how it happened.

    The structural tags are exact joins over recorded fields and reproduce digit
    for digit. ``impossible_transit`` is the one JUDGMENT tag: it is
    :data:`IMPOSSIBLE_TRANSIT_PATTERN` over ballot prose and is labelled a
    judgment net wherever it is quoted.
    """

    set_name: str
    seed: int
    meeting_index: int
    meeting_id: str
    victim: PlayerId
    trigger_kind: str
    tally: Mapping[str, int]
    # Structural tags, recorded fields only.
    reporter_convicted: bool
    boomerang: bool
    impostor_rides: bool
    endgame: bool
    flagged: bool
    weak_flag_only: bool
    guard_redirected: bool
    # The judgment tag.
    impossible_transit: bool

    @property
    def tags(self) -> tuple[str, ...]:
        named = (
            ("RC", self.reporter_convicted),
            ("BOOM", self.boomerang),
            ("PIT", self.impossible_transit),
            ("IMP-RIDES", self.impostor_rides),
            ("WEAKFLAG", self.weak_flag_only),
            ("REDIRECT", self.guard_redirected),
            ("ENDGAME", self.endgame),
        )
        return tuple(tag for tag, present in named if present)

    def payload(self) -> dict[str, object]:
        return {
            "set": self.set_name,
            "seed": self.seed,
            "meeting": self.meeting_index,
            "meeting_id": self.meeting_id,
            "victim": self.victim,
            "trigger_kind": self.trigger_kind,
            "tally": dict(self.tally),
            "tags": list(self.tags),
            "judgment_tag": "PIT" if self.impossible_transit else None,
        }


# --------------------------------------------------------------------------- #
# The capture seam: one walk, every render kept with its inputs.               #
# --------------------------------------------------------------------------- #


@dataclass
class _Capture:
    """One renderer invocation, with the exact keyword inputs it was given."""

    kind: str
    agent_id: PlayerId | None
    kwargs: dict[str, Any]
    off_prompt: str


class _CapturingRenderer:
    """Wrap a real prompt renderer, keeping every invocation's inputs.

    Returns the inner renderer's bytes unchanged, so the manager and the
    recorded-response stub see exactly the recorded prompt. The kept ``kwargs``
    are what the ON legs re-render from.
    """

    def __init__(self, kind: str, inner: Any, sink: list[_Capture]) -> None:
        self._kind = kind
        self._inner = inner
        self._sink = sink

    def __call__(self, **kwargs: Any) -> str:
        prompt: str = self._inner(**kwargs)
        agent_id = kwargs.get("agent_id")
        if agent_id is None:
            agent_id = kwargs.get("voter_id")
        self._sink.append(
            _Capture(
                kind=self._kind,
                agent_id=agent_id,
                kwargs=dict(kwargs),
                off_prompt=prompt,
            )
        )
        return prompt


class _RendererCache:
    """The OFF and testimony-shapes-ON renderer pairs for each prompt set.

    Both bundles are built under an EXPLICIT environment, never the ambient one:
    the loader's own lever reads (``impostor_roll_call``, ``testimony_shapes``)
    decide which template BODIES serve, so an OFF bundle that consulted the
    process environment would render an operator's stale export instead of the
    recorded substrate. The ambient guard refuses such an export outright; this
    is the belt to that brace.

    Only the set every committed recording used carries the three re-bodied
    ``testimony_shapes`` templates; the loader refuses to build the ON pair for
    any other set, and that refusal is left to fail loud rather than caught.
    """

    def __init__(self) -> None:
        self._off: dict[str, PromptRenderers] = {}
        self._on: dict[str, PromptRenderers] = {}
        self._markers: dict[tuple[str, str], frozenset[str]] = {}

    def off(self, set_name: str) -> PromptRenderers:
        if set_name not in self._off:
            self._off[set_name] = build_prompt_renderers(set_name, env={})
        return self._off[set_name]

    def shapes_on(self, set_name: str) -> PromptRenderers:
        if set_name not in self._on:
            self._on[set_name] = build_prompt_renderers(
                set_name, env=_TESTIMONY_SHAPES_ENV
            )
        return self._on[set_name]

    def elicitation_markers(self, set_name: str, turn_kind: str) -> frozenset[str]:
        """The lines a CREW speech prompt gains when the testimony arm is up.

        Derived by rendering one crew turn of this kind through both bundles,
        never written out here: the block's wording moves whenever the template
        is amended (PR #420 re-worded it), and a copied sentence would stop
        matching in silence and read every crew turn as having lost the block.

        The probe renders an EMPTY transcript, which is what keeps the marker
        set the ELICITATION block alone. A spoken ``saw_kill`` also puts a
        role-blind PUBLIC-TRANSCRIPT row in front of every later speaker,
        impostor prompts included; that row is correct, and a marker set derived
        from a render that carried one would read it as an impostor turn being
        offered the shape.
        """

        key = (set_name, turn_kind)
        if key not in self._markers:
            markers = frozenset(
                line
                for line in _added_lines(
                    _probe_crew_statement(self.off(set_name), turn_kind=turn_kind),
                    _probe_crew_statement(
                        self.shapes_on(set_name), turn_kind=turn_kind
                    ),
                )
                if line.strip()
            )
            if not markers:
                raise SystemExit(
                    f"{set_name}: a crew {turn_kind!r} turn gains NO line when "
                    "testimony_shapes is supplied, so this build offers no "
                    "elicitation block for the T5 reader to find. Either the "
                    "block left the template or its guard leaked into the OFF "
                    "body — a reader that returned 0 here would report every "
                    "crew turn as missing the block and STOP a correct record"
                )
            self._markers[key] = markers
        return self._markers[key]

    def capturing(self, sink: list[_Capture]) -> dict[str, PromptRenderers]:
        """A capturing renderer bundle for every registered prompt set.

        The walk resolves each recorded meeting's set from its own stamps, so
        the mapping must cover all of them; only the set a recording actually
        used is ever invoked.
        """

        bundles: dict[str, PromptRenderers] = {}
        for set_name in PROMPT_VERSION_SETS:
            inner = self.off(set_name)
            bundles[set_name] = PromptRenderers(
                crewmate_report=_CapturingRenderer(
                    _KIND_CREWMATE_REPORT, inner.crewmate_report, sink
                ),
                impostor_report=_CapturingRenderer(
                    _KIND_IMPOSTOR_REPORT, inner.impostor_report, sink
                ),
                statement=_CapturingRenderer(
                    _KIND_ACCUSATION_ROUND, inner.statement, sink
                ),
                vote=_CapturingRenderer(_KIND_VOTE_BALLOT, inner.vote, sink),
            )
        return bundles


def _renderer_for(renderers: PromptRenderers, kind: str) -> Any:
    if kind == _KIND_CREWMATE_REPORT:
        return renderers.crewmate_report
    if kind == _KIND_IMPOSTOR_REPORT:
        return renderers.impostor_report
    if kind == _KIND_ACCUSATION_ROUND:
        return renderers.statement
    return renderers.vote


# --------------------------------------------------------------------------- #
# The elicitation block: what the testimony arm OFFERS a crew speaker.         #
# --------------------------------------------------------------------------- #


def _probe_crew_statement(renderers: PromptRenderers, *, turn_kind: str) -> str:
    """One minimal CREW speech render, for deriving the arm's own block.

    Everything optional is left at its default so the render carries as little
    as possible beside the block being derived, and the transcript is empty so
    no publicly spoken row can join it.
    """

    kind: TurnKind = "opt_in" if turn_kind == "opt_in" else "reply"
    return renderers.statement(
        agent_id="p-1",
        rendered_memory="",
        transcript=MeetingTranscript(turns=()),
        contradictions=(),
        prior_turn=None,
        turn_kind=kind,
        living_ids=("p-2",),
    )


def _added_lines(off: str, on: str) -> tuple[str, ...]:
    """The lines ``on`` renders that ``off`` does not, as a MULTISET difference.

    Containment would call a line "added" that both renders already carried; the
    multiset difference reports exactly what the second render puts on the page.
    """

    remaining = Counter(off.splitlines())
    added: list[str] = []
    for line in on.splitlines():
        if remaining[line]:
            remaining[line] -= 1
        else:
            added.append(line)
    return tuple(added)


def elicitation_lines_gained(
    *, off_prompt: str, on_prompt: str, markers: frozenset[str]
) -> int:
    """How many of the elicitation block's own lines the ON render ADDS.

    A GAIN, never a presence. A line already in the OFF bytes was not put there
    by the arm, and a sentence some speaker quoted into the transcript sits in
    both renders — counting the difference is what lets the crew half and the
    impostor half of T5's predicate be read off the same function.
    """

    return sum(
        1 for marker in markers if on_prompt.count(marker) > off_prompt.count(marker)
    )


def spoken_kill_subjects(transcript: MeetingTranscript) -> frozenset[PlayerId]:
    """Every player a spoken ``saw_kill`` observation names as the killer."""

    return frozenset(
        observation.subject
        for turn in transcript.turns
        for observation in turn.observations
        if isinstance(observation, SawKillObservation)
    )


def is_non_direct_ejection(
    contradictions: Sequence[ContradictionRef], ejected: PlayerId
) -> bool:
    """Whether bar 1's non-direct cell holds this conviction.

    The partition is ``EjecteeProofCrossTab``'s and is imported rather than
    restated: an ejection is DIRECT exactly when a ``role_proof`` flag named the
    ejectee, so everything else is the non-direct cell. ``ROLE_PROOF_KINDS`` is
    ``{"vent_sighting"}``, which is why an eyewitness-kill conviction lands here
    as deduction and needs a split of its own.
    """

    return ejected not in frozenset(
        subject
        for flag in contradictions
        if classify_flag(flag) == "role_proof"
        for subject in flag.subjects
    )


# --------------------------------------------------------------------------- #
# Per-meeting ON inputs.                                                       #
# --------------------------------------------------------------------------- #


def _firewalled_sightings(
    participants: Sequence[MeetingParticipant],
) -> dict[PlayerId, tuple[SightingRecord, ...]]:
    """The §4.7 teammate firewall re-applied exactly as the manager applies it."""

    kept: dict[PlayerId, tuple[SightingRecord, ...]] = {}
    for participant in participants:
        fellows = frozenset(participant.fellow_impostor_ids)
        rows = tuple(
            record
            for record in participant.sighting_records
            if record.subject not in fellows
        )
        if rows:
            kept[participant.agent_id] = rows
    return kept


def _ledger_for(meeting: ReconstructedMeeting) -> MeetingTestimonyLedger:
    """The corroboration lever's ON input: the builder CALLED, nothing toggled."""

    return build_testimony_ledger(
        meeting.result.transcript,
        contradictions=meeting.result.contradictions,
        sighting_records=_firewalled_sightings(meeting.participants),
        move_witness_records={
            p.agent_id: p.move_witness_records
            for p in meeting.participants
            if p.move_witness_records
        },
        opener=meeting.result.triggered_by,
        roster=frozenset(p.agent_id for p in meeting.participants),
        trigger_kind=meeting.trigger_kind,
    )


@dataclass(frozen=True)
class _ReporterInputs:
    """The reporter lever's ON render inputs for one meeting, per speaker."""

    reporter_id: PlayerId | None
    contexts: Mapping[PlayerId, ReporterContext]
    at_body: Mapping[PlayerId, bool]


def _reporter_inputs(
    meeting: ReconstructedMeeting,
    *,
    trigger_kind: str,
    victim_id: PlayerId | None,
) -> _ReporterInputs:
    """Mirror ``MeetingManager``'s own reporter-voice derivation, lever ON.

    A body report's reporter is the trigger's opener; an emergency call has no
    reporter and arms nothing. The concrete discovery clause is the RECEIVING
    speaker's own, read off their ``body_discovery_records`` through the
    manager's window helper, so no fact reaches a reader who did not perceive it.
    """

    if trigger_kind != "body_report":
        return _ReporterInputs(reporter_id=None, contexts={}, at_body={})
    reporter_id = meeting.entry.triggered_by
    trigger_tick = meeting.entry.tick
    contexts: dict[PlayerId, ReporterContext] = {}
    at_body: dict[PlayerId, bool] = {}
    for participant in meeting.participants:
        discoveries = _discoveries_in_window(
            participant.body_discovery_records,
            trigger_tick=trigger_tick,
            victim_id=victim_id,
        )
        contexts[participant.agent_id] = _reporter_context_for(
            reporter_id=reporter_id,
            trigger_tick=trigger_tick,
            discoveries=discoveries,
        )
        at_body[participant.agent_id] = participant.agent_id != reporter_id and bool(
            discoveries
        )
    return _ReporterInputs(reporter_id=reporter_id, contexts=contexts, at_body=at_body)


def _on_kwargs(
    capture: _Capture,
    *,
    levers: frozenset[str],
    reporter: _ReporterInputs,
    ledger: MeetingTestimonyLedger,
) -> dict[str, Any]:
    """The capture's keywords with each ON lever's own argument supplied."""

    kwargs = dict(capture.kwargs)
    if "reporter_reasoning" in levers and reporter.reporter_id is not None:
        speaker = capture.agent_id
        context = reporter.contexts.get(speaker) if speaker is not None else None
        is_reporter = speaker == reporter.reporter_id
        if capture.kind in (_KIND_CREWMATE_REPORT, _KIND_IMPOSTOR_REPORT):
            # The opener of a body report IS its reporter, so this is the one
            # seam where the discovery account can be asked for.
            kwargs["reporter_context"] = context if is_reporter else None
        elif capture.kind == _KIND_ACCUSATION_ROUND:
            kwargs["reporter_context"] = None if is_reporter else context
            kwargs["at_body"] = bool(
                speaker is not None and reporter.at_body.get(speaker, False)
            )
    if "corroboration_discipline" in levers and capture.kind == _KIND_VOTE_BALLOT:
        kwargs["testimony_ledger"] = ledger
    return kwargs


# --------------------------------------------------------------------------- #
# The render diff.                                                             #
# --------------------------------------------------------------------------- #


@dataclass
class _LegTallies:
    """One slate's render census, accumulated over a whole set."""

    rendered: Counter[str] = field(default_factory=Counter)
    changed: Counter[str] = field(default_factory=Counter)
    added_lines: Counter[str] = field(default_factory=Counter)
    added_bytes: Counter[str] = field(default_factory=Counter)
    meetings_touched: int = 0
    # The render-budget fold, over the same recorded calls the instrument reads.
    snapshots: int = 0
    rendered_lines: int = 0
    testimony_rows: int = 0
    testimony_by_bucket: Counter[str] = field(default_factory=Counter)
    # The same fold restricted to the game's FIRST meeting. A whole-game total
    # can net a first-meeting difference against an opposite later one, and the
    # first meeting is the only one whose ON render is derivable from recorded
    # inputs, so the cell that answers "did prose displace memory here" has to
    # be scoped to it.
    first_meeting_snapshots: int = 0
    first_meeting_rendered_lines: int = 0

    def fold_snapshot(self, prompt: str, *, bucket: str, first_meeting: bool) -> None:
        """Count one rendered prompt's memory rows into the budget."""

        rows = len(_RENDERED_ROW.findall(prompt))
        testimony = sum(
            1 for line in prompt.splitlines() if _TESTIMONY_ROW.match(line) is not None
        )
        self.snapshots += 1
        self.rendered_lines += rows
        self.testimony_rows += testimony
        self.testimony_by_bucket[bucket] += testimony
        if first_meeting:
            self.first_meeting_snapshots += 1
            self.first_meeting_rendered_lines += rows

    def budget(self) -> RenderBudgetCells:
        return RenderBudgetCells(
            snapshots=self.snapshots,
            rendered_lines_total=self.rendered_lines,
            rendered_lines_mean=(
                self.rendered_lines / self.snapshots if self.snapshots else None
            ),
            testimony_rows_total=self.testimony_rows,
            testimony_rows_by_living_bucket=dict(
                sorted(self.testimony_by_bucket.items())
            ),
        )


def _slate_legs(withhold: str) -> tuple[tuple[str, frozenset[str]], ...]:
    """The slates the table renders: OFF, each lever alone, all three, minus one."""

    legs: list[tuple[str, frozenset[str]]] = [(_SLATE_OFF, frozenset())]
    legs.extend((lever, frozenset({lever})) for lever in WAVE_2_LEVERS)
    legs.append((_SLATE_ALL_ON, frozenset(WAVE_2_LEVERS)))
    legs.append(
        (
            decomposition_label(withhold),
            frozenset(WAVE_2_LEVERS) - {withhold},
        )
    )
    return tuple(legs)


def decomposition_label(withhold: str) -> str:
    """The label the leave-one-out leg is printed and keyed under."""

    return f"two-ON (less {withhold})"


def _attribute_calls(
    meeting: ReconstructedMeeting, captures: Sequence[_Capture]
) -> list[tuple[int, str]]:
    """Pair every recorded LLM call with the render that produced its base.

    A manager-side retry appends feedback to the base render, so a recorded
    prompt is a base render plus a (possibly empty) suffix; the longest such base
    is the producing render. Returns ``(capture index, suffix)`` pairs. Fails
    loud on a call no render explains -- the prompt-byte golden pins that this
    never happens, and a silent drop would shrink the render-budget denominator
    the instrument publishes.
    """

    paired: list[tuple[int, str]] = []
    for call in meeting.entry.llm_calls:
        best: int | None = None
        for index, capture in enumerate(captures):
            if not call.prompt.startswith(capture.off_prompt):
                continue
            if best is None or len(capture.off_prompt) > len(captures[best].off_prompt):
                best = index
        if best is None:
            raise SystemExit(
                f"{meeting.set_name} {meeting.meeting_id}: a recorded LLM call "
                "matches no reconstructed render, so the render-budget fold "
                "cannot be built. This is a DEFECT IN THIS SCRIPT's attribution, "
                "not a finding about the committed bytes"
            )
        paired.append((best, call.prompt[len(captures[best].off_prompt) :]))
    return paired


def _fold_render_diff(
    *,
    meeting: ReconstructedMeeting,
    captures: Sequence[_Capture],
    renderers: _RendererCache,
    reporter: _ReporterInputs,
    ledger: MeetingTestimonyLedger,
    legs: Sequence[tuple[str, frozenset[str]]],
    tallies: Mapping[str, _LegTallies],
    roles: Mapping[PlayerId, Role],
    elicitation: _ElicitationCensus,
) -> None:
    """Render every captured prompt once per slate and count what moved."""

    living = frozenset(p.agent_id for p in meeting.participants)
    bucket = _living_bucket(len(living))
    paired = _attribute_calls(meeting, captures)
    on_prompts: dict[str, dict[int, str]] = {}
    for label, levers in legs:
        leg = tallies[label]
        rendered_for_leg: dict[int, str] = {}
        touched = False
        for index, capture in enumerate(captures):
            if not levers:
                prompt = capture.off_prompt
            else:
                bundle = (
                    renderers.shapes_on(meeting.set_name)
                    if "testimony_shapes" in levers
                    else renderers.off(meeting.set_name)
                )
                prompt = _renderer_for(bundle, capture.kind)(
                    **_on_kwargs(
                        capture, levers=levers, reporter=reporter, ledger=ledger
                    )
                )
            rendered_for_leg[index] = prompt
            leg.rendered[capture.kind] += 1
            if prompt != capture.off_prompt:
                touched = True
                leg.changed[capture.kind] += 1
                leg.added_lines[capture.kind] += prompt.count(
                    "\n"
                ) - capture.off_prompt.count("\n")
                # Encoded bytes, not code points: the lever blocks carry em
                # dashes and arrows, so a character count would understate what
                # the prompt actually costs.
                leg.added_bytes[capture.kind] += len(prompt.encode("utf-8")) - len(
                    capture.off_prompt.encode("utf-8")
                )
        if touched or not levers:
            leg.meetings_touched += 1
        on_prompts[label] = rendered_for_leg
    first_meeting = meeting.meeting_index == 0
    for label, _levers in legs:
        leg = tallies[label]
        for index, suffix in paired:
            leg.fold_snapshot(
                on_prompts[label][index] + suffix,
                bucket=bucket,
                first_meeting=first_meeting,
            )
    _fold_elicitation(
        meeting=meeting,
        captures=captures,
        renderers=renderers,
        on_prompts=on_prompts[_ELICITATION_LEG],
        roles=roles,
        census=elicitation,
    )


#: The leg whose ON renders the T5 reader reads. The elicitation block is
#: ``testimony_shapes``'s alone, so the single-lever leg is the one that isolates
#: it — and it reads the same on every leg that carries the arm, because the
#: marker is the block's own text rather than a byte diff.
_ELICITATION_LEG: Final[str] = "testimony_shapes"


@dataclass
class _ElicitationCensus:
    """Speech prompts OFFERED the witnessed-kill shape, split by speaker role.

    The T5 predicate has two halves — every observed crew speech turn gains the
    block, and no impostor speech prompt does — and neither half can be read off
    the aggregate byte diff: two offsetting errors leave it unchanged, and a
    role split of the byte diff would count the role-blind public-transcript row
    an impostor prompt correctly carries as an offer it must never receive.
    """

    rendered: Counter[str] = field(default_factory=Counter)
    gained: Counter[str] = field(default_factory=Counter)
    #: Prompts that gained SOME but not all of the block's lines. The block is
    #: one offer rendered by guards that share a condition, so a partial gain
    #: means this reader can no longer read it as one unit.
    partial: int = 0


def speaker_role(
    capture: _Capture, roles: Mapping[PlayerId, Role], *, where: str
) -> Role:
    """The rendering speaker's role, taken from the re-seeded roster.

    The role the roster re-derives and the role the template was rendered under
    must describe the same seat. They come from different places — the re-seeded
    engine and the recorded render inputs — so a disagreement means one of them
    is reading a different player, and T5's whole split would be drawn on the
    wrong line rather than fail visibly.
    """

    speaker = capture.agent_id
    if speaker is None:
        raise SystemExit(
            f"{where}: a {capture.kind} render carries no speaker, so its "
            "prompt cannot be split by role. This is a DEFECT IN THIS SCRIPT's "
            "capture, not a finding about the committed bytes"
        )
    role = roles[speaker]
    rendered_as_impostor = capture.kwargs.get("is_impostor")
    if rendered_as_impostor is not None and bool(rendered_as_impostor) != (
        role == "IMPOSTOR"
    ):
        raise SystemExit(
            f"{where}: {speaker} renders with "
            f"is_impostor={rendered_as_impostor!r} but the re-seeded roster "
            f"calls them {role}. This is a DEFECT IN THIS SCRIPT's role join, "
            "not a finding about the committed bytes"
        )
    return role


def _fold_elicitation(
    *,
    meeting: ReconstructedMeeting,
    captures: Sequence[_Capture],
    renderers: _RendererCache,
    on_prompts: Mapping[int, str],
    roles: Mapping[PlayerId, Role],
    census: _ElicitationCensus,
) -> None:
    """Count, per speaker role, the speech prompts that gain the block."""

    for index, capture in enumerate(captures):
        if capture.kind != _KIND_ACCUSATION_ROUND:
            continue
        role = speaker_role(
            capture, roles, where=f"{meeting.set_name} {meeting.meeting_id}"
        )
        markers = renderers.elicitation_markers(
            meeting.set_name, str(capture.kwargs.get("turn_kind", "reply"))
        )
        gained = elicitation_lines_gained(
            off_prompt=capture.off_prompt,
            on_prompt=on_prompts[index],
            markers=markers,
        )
        census.rendered[role] += 1
        if gained == len(markers):
            census.gained[role] += 1
        elif gained:
            census.partial += 1


# --------------------------------------------------------------------------- #
# The ballot census the corroboration lever is scored against.                 #
# --------------------------------------------------------------------------- #

_CITATION_CLASSES: Final[tuple[str, ...]] = (
    "own_obs",
    "other_obs",
    "own_turn",
    "hearsay",
    "none",
)


def _citation_class(
    ballot: VoteBallot, *, transcript_speakers: Mapping[str, str]
) -> str:
    """Which channel a convicting ballot cited, as a five-way partition.

    ``own_obs`` is a private observation id out of the voter's OWN memory (the
    ``{agent_id}:{tick}:{seq}`` scheme the manager validates against the voter's
    typed valid-id set); ``other_obs`` is one that names another agent, which the
    manager's normalizer nulls, so it is expected empty and is reported rather
    than assumed away. ``own_turn`` and ``hearsay`` split the public turn
    citation by whether the cited turn is the voter's own. ``none`` is a ballot
    citing neither.
    """

    observation_id = ballot.primary_reason_observation_id
    if observation_id is not None:
        owner = str(observation_id).split(":", 1)[0]
        return "own_obs" if owner == ballot.voter else "other_obs"
    turn_id = ballot.primary_reason_id
    if turn_id is None:
        return "none"
    speaker = transcript_speakers.get(str(turn_id))
    return "own_turn" if speaker == ballot.voter else "hearsay"


@dataclass
class _BallotCensus:
    """The ejecting-ballot census over one set's innocent ejections."""

    ejecting_ballots: int = 0
    citations: Counter[str] = field(default_factory=Counter)
    confidence_by_flag: dict[str, list[float]] = field(
        default_factory=lambda: {"flagged": [], "unflagged": []}
    )
    driver_role: Counter[str] = field(default_factory=Counter)
    follower_counts: dict[str, Counter[int]] = field(
        default_factory=lambda: {"CREWMATE": Counter(), "IMPOSTOR": Counter()}
    )
    impostor_ballots_in_these_meetings: int = 0
    impostor_ballots_joining_the_pile: int = 0

    def payload(self) -> dict[str, object]:
        return {
            "ejecting_ballots": self.ejecting_ballots,
            "citation_mix": {
                name: self.citations.get(name, 0) for name in _CITATION_CLASSES
            },
            "mean_confidence": {
                status: (round(sum(values) / len(values), 4) if values else None)
                for status, values in self.confidence_by_flag.items()
            },
            "ejections_by_flag_status": {
                status: len(values)
                for status, values in self.confidence_by_flag.items()
            },
            "pile_driver_role": dict(sorted(self.driver_role.items())),
            "follower_counts": {
                role: dict(sorted(counts.items()))
                for role, counts in self.follower_counts.items()
            },
            "impostor_ballots_cast": self.impostor_ballots_in_these_meetings,
            "impostor_ballots_joining_the_pile": self.impostor_ballots_joining_the_pile,
        }


# --------------------------------------------------------------------------- #
# The testimony census the ingest lever is scored against.                     #
# --------------------------------------------------------------------------- #


@dataclass
class _TestimonyCensus:
    """The reduction and ingest cells, OFF and ON, over one set."""

    off_kinds: Counter[str] = field(default_factory=Counter)
    on_kinds: Counter[str] = field(default_factory=Counter)
    off_rows: int = 0
    on_rows: int = 0
    listener_slots: int = 0
    spoken_vent_rows: int = 0
    fabricated_vent_rows: int = 0
    ungrounded_vent_rows: int = 0

    @property
    def alibi_map_off(self) -> tuple[int, int]:
        accounts = self.on_kinds["alibi"] + self.on_kinds["whereabouts"]
        return (self.off_kinds["alibi"], accounts)

    @property
    def alibi_map_on(self) -> tuple[int, int]:
        accounts = self.on_kinds["alibi"] + self.on_kinds["whereabouts"]
        return (accounts, accounts)

    def payload(self) -> dict[str, object]:
        return {
            "statements_off": dict(sorted(self.off_kinds.items())),
            "statements_on": dict(sorted(self.on_kinds.items())),
            "episodic_rows_off": self.off_rows,
            "episodic_rows_on": self.on_rows,
            "listener_slots": self.listener_slots,
            "alibi_map_off": list(self.alibi_map_off),
            "alibi_map_on": list(self.alibi_map_on),
            "spoken_vent_rows": self.spoken_vent_rows,
            "fabricated_vent_rows": self.fabricated_vent_rows,
            "ungrounded_vent_rows": self.ungrounded_vent_rows,
        }


def _vent_row_census(
    result: MeetingResult, *, venters: frozenset[PlayerId]
) -> tuple[int, int, int]:
    """``(spoken, fabricated, ungrounded)`` over one meeting's vent accounts.

    Two different questions, kept apart because they answer different things.

    * FABRICATED is the subject-side join: the spoken account names a player who
      never vented in this game at all, read off the recorded action stream. This
      is the laundering class's own predicate.
    * UNGROUNDED is the speaker-side census: the detector minted no
      ``vent_sighting`` flag on this account, so the SPEAKER's own typed record
      does not bear it out. A grounded flag carries the spoken observation's id
      in both event ids, so resolving the id back to its turn is exact. This is
      what the corroboration ledger reads as a first-hand source; it is NOT a
      fabrication count and no lever is claimed to remove it.
    """

    grounded = frozenset(
        flag.event_a_id
        for flag in result.contradictions
        if flag.kind == "vent_sighting"
    )
    spoken = fabricated = ungrounded = 0
    for turn in result.transcript.turns:
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawVentObservation):
                continue
            spoken += 1
            if observation.subject not in venters:
                fabricated += 1
            if turn_observation_id(turn=turn, index=index) not in grounded:
                ungrounded += 1
    return spoken, fabricated, ungrounded


def venters_in_game(ticks: Sequence[ReplayEntry]) -> frozenset[PlayerId]:
    """Every player the recorded action stream shows actually venting.

    An APPLIED action is the only one that vented anything: a submitted-and-
    rejected vent moved nobody, and counting it would clear an account the
    engine refused. A recording whose ticks carry no dispositions predates the
    field and every action in it was applied.
    """

    venters: set[PlayerId] = set()
    for entry in ticks:
        dispositions = entry.action_dispositions
        for index, action in enumerate(entry.actions):
            if str(action.get("type")) != "vent":
                continue
            if dispositions is not None and dispositions[index] != "applied":
                continue
            actor = action.get("actor")
            if isinstance(actor, str):
                venters.add(actor)
    return frozenset(venters)


def _fold_testimony(
    meeting: ReconstructedMeeting,
    census: _TestimonyCensus,
    *,
    venters: frozenset[PlayerId],
) -> None:
    """Fold one meeting's reduction census, ONE STEP AHEAD of the record.

    Meeting 1's ON reduction is derivable from meeting 1's recorded inputs, but
    meeting 2's ON transcript is a model output that does not exist -- so every
    cell here is read at a RECORDED meeting boundary against RECORDED speech and
    compounds nowhere. The listener multiplication applies the own-statement
    guard and NOT the roster gate (which needs each listener's episodic store,
    which the reconstruction does not expose), so the row counts are an upper
    bound and are printed as one.
    """

    off = derive_reported_testimony(meeting.result)
    on = derive_reported_testimony(meeting.result, env=_TESTIMONY_SHAPES_ENV)
    census.off_kinds.update(statement.kind for statement in off)
    census.on_kinds.update(statement.kind for statement in on)
    listeners = frozenset(ballot.voter for ballot in meeting.result.ballots)
    census.listener_slots += len(listeners)
    census.off_rows += _ingest_rows(off, listeners)
    census.on_rows += _ingest_rows(on, listeners)
    spoken, fabricated, ungrounded = _vent_row_census(meeting.result, venters=venters)
    census.spoken_vent_rows += spoken
    census.fabricated_vent_rows += fabricated
    census.ungrounded_vent_rows += ungrounded


def _ingest_rows(
    statements: Sequence[ReportedStatement], listeners: frozenset[PlayerId]
) -> int:
    return sum(
        1
        for statement in statements
        for listener in listeners
        if statement.speaker != listener
    )


# --------------------------------------------------------------------------- #
# The walk.                                                                    #
# --------------------------------------------------------------------------- #


@dataclass
class _KillNamedConvictions:
    """Bar 1's non-direct cell, split by whether a spoken kill named the ejectee.

    ``ROLE_PROOF_KINDS`` is ``{"vent_sighting"}``, so under ``testimony_shapes``
    an eyewitness-kill conviction enters the non-direct cell as deduction and is
    not separable there. This is the split that lets bar 1's movement be
    decomposed at the record; it is observed and gates nothing.
    """

    non_direct: int = 0
    kill_named: int = 0
    kill_named_impostor: int = 0


def _fold_kill_named_conviction(
    *,
    result: MeetingResult,
    roles: Mapping[PlayerId, Role],
    census: _KillNamedConvictions,
) -> None:
    """Join this meeting's conviction (if any) onto the spoken-kill split."""

    ejected = result.ejected_player_id
    if ejected is None:
        return
    if not is_non_direct_ejection(result.contradictions, ejected):
        return
    census.non_direct += 1
    if ejected not in spoken_kill_subjects(result.transcript):
        return
    census.kill_named += 1
    if roles[ejected] == "IMPOSTOR":
        census.kill_named_impostor += 1


@dataclass
class _SetWalk:
    """Everything one reconstruction pass over one committed set produced."""

    set_name: str
    games: int = 0
    meetings: int = 0
    body_report_meetings: int = 0
    ejections: int = 0
    innocent_ejections: int = 0
    legs: dict[str, _LegTallies] = field(default_factory=dict)
    ledger_rows: list[InjusticeLedgerRow] = field(default_factory=list)
    ballots: _BallotCensus = field(default_factory=_BallotCensus)
    testimony: _TestimonyCensus = field(default_factory=_TestimonyCensus)
    corroboration: Counter[str] = field(default_factory=Counter)
    reporter_openings: int = 0
    non_reporter_speech_turns: int = 0
    elicitation: _ElicitationCensus = field(default_factory=_ElicitationCensus)
    kill_named: _KillNamedConvictions = field(default_factory=_KillNamedConvictions)
    # The render budget at the FIRST meeting, folded straight off the recorded
    # call bytes rather than through the reconstruction, so the meeting-1 cell
    # carries the same two independent OFF readings the whole-run one does.
    recorded_first_meeting_snapshots: int = 0
    recorded_first_meeting_rendered_lines: int = 0
    elapsed: float = 0.0


def _weak_only(
    flags: Sequence[ContradictionRef], victim: PlayerId
) -> tuple[bool, bool]:
    """``(named, weak_only)`` for the contradictions naming one player.

    ``weak_only`` uses the detector's OWN weak-signal predicate, the same one the
    committed weak-flag conviction cell keys on, so the tag and that cell cannot
    disagree about what "weak" means.
    """

    naming = [flag for flag in flags if victim in flag.subjects]
    if not naming:
        return False, False
    return True, all(is_weak_contradiction(flag) for flag in naming)


def _fold_ledger(
    *,
    meeting: ReconstructedMeeting,
    roles: Mapping[PlayerId, Role],
    trigger_kind: str,
    walk: _SetWalk,
) -> None:
    """Join one meeting's innocent ejection (if any) onto its structural tags."""

    result = meeting.result
    ejected = result.ejected_player_id
    if ejected is None:
        return
    walk.ejections += 1
    convicting = [ballot for ballot in result.ballots if ballot.target == ejected]
    if roles[ejected] == "IMPOSTOR":
        return
    walk.innocent_ejections += 1
    turns = result.transcript.turns
    turn_zero = turns[0].speaker if turns else None
    boomerang = bool(
        turn_zero is not None
        and ejected == turn_zero
        and len(turns) > 1
        and any(
            isinstance(claim, AccusationClaim) and claim.against == turn_zero
            for claim in turns[1].claims
        )
    )
    named, weak_only = _weak_only(result.contradictions, ejected)
    living_impostors = {
        participant.agent_id
        for participant in meeting.participants
        if roles[participant.agent_id] == "IMPOSTOR"
    }
    walk.ledger_rows.append(
        InjusticeLedgerRow(
            set_name=walk.set_name,
            seed=meeting.seed,
            meeting_index=meeting.meeting_index,
            meeting_id=meeting.meeting_id,
            victim=ejected,
            trigger_kind=trigger_kind,
            tally=dict(Counter(str(ballot.target) for ballot in result.ballots)),
            reporter_convicted=(
                trigger_kind == "body_report" and ejected == result.triggered_by
            ),
            boomerang=boomerang,
            impostor_rides=any(
                ballot.voter in living_impostors for ballot in convicting
            ),
            endgame=len(result.ballots) <= 3,
            flagged=named,
            weak_flag_only=weak_only,
            guard_redirected=any(
                ballot.guard_rewrite_reason is not None for ballot in convicting
            ),
            impossible_transit=any(
                IMPOSSIBLE_TRANSIT_PATTERN.search(ballot.rationale_text or "")
                for ballot in convicting
            ),
        )
    )
    _fold_ballot_census(
        meeting=meeting,
        roles=roles,
        ejected=ejected,
        convicting=convicting,
        flagged=named,
        census=walk.ballots,
    )


def _fold_ballot_census(
    *,
    meeting: ReconstructedMeeting,
    roles: Mapping[PlayerId, Role],
    ejected: PlayerId,
    convicting: Sequence[VoteBallot],
    flagged: bool,
    census: _BallotCensus,
) -> None:
    """The citation, confidence and sole-source cells over the ejecting ballots."""

    speakers = {
        str(turn.turn_id): turn.speaker for turn in meeting.result.transcript.turns
    }
    census.ejecting_ballots += len(convicting)
    for ballot in convicting:
        census.citations[_citation_class(ballot, transcript_speakers=speakers)] += 1
    if convicting:
        mean = sum(ballot.confidence for ballot in convicting) / len(convicting)
        census.confidence_by_flag["flagged" if flagged else "unflagged"].append(mean)
    cited_other = Counter(
        str(ballot.primary_reason_id)
        for ballot in convicting
        if ballot.primary_reason_id is not None
        and speakers.get(str(ballot.primary_reason_id)) not in (None, ballot.voter)
    )
    if not cited_other:
        census.driver_role["NONE"] += 1
    else:
        turn_id, followers = cited_other.most_common(1)[0]
        driver = speakers[turn_id]
        role = roles[driver]
        census.driver_role[role] += 1
        census.follower_counts[role][followers] += 1
    for ballot in meeting.result.ballots:
        if roles[ballot.voter] != "IMPOSTOR":
            continue
        census.impostor_ballots_in_these_meetings += 1
        if ballot.target == ejected:
            census.impostor_ballots_joining_the_pile += 1


def _fold_corroboration(
    meeting: ReconstructedMeeting,
    ledger: MeetingTestimonyLedger,
    cells: Counter[str],
) -> None:
    """The four cells the corroboration block would state, over the same walk."""

    for row in ledger.rows:
        cells["rows"] += 1
        if not row.first_hand:
            cells["accused_without_a_first_hand_source"] += 1
    ejected = meeting.result.ejected_player_id
    if ejected is None:
        return
    cells["ejections"] += 1
    match = [row for row in ledger.rows if row.subject == ejected]
    if not match:
        return
    cells["ejected_rows"] += 1
    row = match[0]
    if not row.first_hand:
        cells["ejected_without_a_first_hand_source"] += 1
    if row.opener_charge_turn_id is not None:
        cells["ejected_on_an_answering_turn"] += 1
    if row.walkable_transits:
        cells["ejected_with_a_walkable_pair"] += 1


def walk_set(sample_dir: Path, *, set_name: str, withhold: str) -> _SetWalk:
    """One reconstruction pass over one committed set, every fold on the way."""

    started = time.monotonic()
    legs = _slate_legs(withhold)
    walk = _SetWalk(set_name=set_name, legs={label: _LegTallies() for label, _ in legs})
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    if not seeds_on_disk(sample_dir):
        raise SystemExit(
            f"{sample_dir}: no replay-seed-*.jsonl files found — not a replay "
            "set; refusing to report a zero-game measurement"
        )
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    game_map = load_canonical_map()
    renderers = _RendererCache()
    sink: list[_Capture] = []
    capturing = renderers.capturing(sink)
    for seed_path in _seed_paths(sample_dir):
        walk.games += 1
        seed = int(seed_path.stem.rsplit("-", 1)[-1])
        roles = per_seed_roles[seed]
        ticks = [
            entry
            for entry in read_all_entries(seed_path)
            if isinstance(entry, ReplayEntry)
        ]
        venters = venters_in_game(ticks)
        sink.clear()
        for meeting in walk_replay_meetings(
            seed_path, game_map=game_map, renderers_for_set=capturing
        ):
            captures = list(sink)
            sink.clear()
            walk.meetings += 1
            trigger_kind, victim_id = _meeting_trigger(
                ticks, entry=meeting.entry, roster=roles
            )
            # Two independent derivations of the same fact -- the recorded
            # action stream and the engine event the reconstruction replayed.
            # A disagreement means one of them is reading the wrong meeting.
            rebuilt = "body_report" if meeting.trigger_kind == "report" else "emergency"
            if rebuilt != trigger_kind:
                raise SystemExit(
                    f"{set_name} {meeting.meeting_id}: the recorded action "
                    f"stream says {trigger_kind!r} and the reconstruction says "
                    f"{rebuilt!r}. This is a DEFECT IN THIS SCRIPT's join, not a "
                    "finding about the committed bytes"
                )
            if trigger_kind == "body_report":
                walk.body_report_meetings += 1
            reporter = _reporter_inputs(
                meeting, trigger_kind=trigger_kind, victim_id=victim_id
            )
            if reporter.reporter_id is not None:
                walk.reporter_openings += sum(
                    1
                    for capture in captures
                    if capture.kind in (_KIND_CREWMATE_REPORT, _KIND_IMPOSTOR_REPORT)
                    and capture.agent_id == reporter.reporter_id
                )
                walk.non_reporter_speech_turns += sum(
                    1
                    for capture in captures
                    if capture.kind == _KIND_ACCUSATION_ROUND
                    and capture.agent_id != reporter.reporter_id
                )
            if meeting.meeting_index == 0:
                for call in meeting.entry.llm_calls:
                    walk.recorded_first_meeting_snapshots += 1
                    walk.recorded_first_meeting_rendered_lines += len(
                        _RENDERED_ROW.findall(call.prompt)
                    )
            ledger = _ledger_for(meeting)
            _fold_render_diff(
                meeting=meeting,
                captures=captures,
                renderers=renderers,
                reporter=reporter,
                ledger=ledger,
                legs=legs,
                tallies=walk.legs,
                roles=roles,
                elicitation=walk.elicitation,
            )
            _fold_kill_named_conviction(
                result=meeting.result, roles=roles, census=walk.kill_named
            )
            _fold_corroboration(meeting, ledger, walk.corroboration)
            _fold_testimony(meeting, walk.testimony, venters=venters)
            _fold_ledger(
                meeting=meeting, roles=roles, trigger_kind=trigger_kind, walk=walk
            )
    if walk.elicitation.partial:
        raise SystemExit(
            f"{set_name}: {walk.elicitation.partial} speech prompts gained SOME "
            "but not all of the elicitation block's lines. The block is one "
            "offer whose lines share a guard, so this reader counts it as one "
            "unit; a partial gain means the template now renders it in pieces "
            "and T5's two halves would be read against different things. This "
            "is a DEFECT IN THIS SCRIPT's reader, not a finding about the bytes"
        )
    walk.elapsed = time.monotonic() - started
    return walk


# --------------------------------------------------------------------------- #
# The table.                                                                   #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Row:
    """One published cell, in the three-column discipline.

    ``recorded_off`` is a committed instrument's reading; ``reconstructed_off``
    the same cell folded from the reconstruction with the slate OFF; ``on`` the
    render diff. A row whose two OFF readings disagree prints no ON value.
    """

    cell_id: str
    label: str
    population: str
    note: str
    recorded_off: tuple[int, int] | None = None
    reconstructed_off: tuple[int, int] | None = None
    on: tuple[int, int] | None = None
    on_slate: str = _SLATE_ALL_ON

    @property
    def agrees(self) -> bool:
        if self.recorded_off is None or self.reconstructed_off is None:
            return True
        return self.recorded_off == self.reconstructed_off

    @property
    def advisory(self) -> bool:
        """Whether one case moves this ROW by more than a reading can bear.

        Keyed on the row's OWN denominator rather than on any set-level count: a
        cell measured over three turns is fragile in a set of 439 meetings, and
        labelling it by the set would hide exactly that.
        """

        return any(
            pair is not None and pair[1] <= ADVISORY_DENOMINATOR
            for pair in (self.recorded_off, self.reconstructed_off, self.on)
        )

    def payload(self) -> dict[str, object]:
        return {
            "cell": self.cell_id,
            "label": self.label,
            "population": self.population,
            "note": self.note,
            "on_slate": self.on_slate,
            "advisory": self.advisory,
            "recorded_off": list(self.recorded_off) if self.recorded_off else None,
            "reconstructed_off": (
                list(self.reconstructed_off) if self.reconstructed_off else None
            ),
            "on": list(self.on) if self.on else None,
        }


#: A published cell whose denominator is this small moves by more than five
#: points when one case changes, so it carries an advisory label wherever it is
#: printed and takes no part in a directional statement.
ADVISORY_DENOMINATOR: Final[int] = 20


def _pair(numerator: int, denominator: int) -> tuple[int, int]:
    return (numerator, denominator)


def build_rows(
    *,
    walk: _SetWalk,
    reporter: ReporterJusticeCells,
    evidence_budget: RenderBudgetCells,
    solvability: SolvabilityReport,
    committed: TournamentEvalReport,
    withhold: str,
) -> list[Row]:
    """Every cell the instruments and the recorded bytes can supply offline."""

    rows: list[Row] = []
    cross_tab = committed.deduction.ejectee_proof_cross_tab
    leakage = committed.deduction.scaffold_leakage
    all_on = walk.legs[_SLATE_ALL_ON]

    # -- The record's own cells, the ledger's denominators. ------------------ #
    rows.append(
        Row(
            cell_id="P-1",
            label="non-direct conviction accuracy (impostor / non-direct ejections)",
            population="ejection",
            note=(
                "the record audit's published cell 1; NOT predictable offline — a "
                "sentence added to a prompt is not a vote that changes"
            ),
            recorded_off=_pair(
                cross_tab.non_direct_accuracy.numerator,
                cross_tab.non_direct_accuracy.denominator,
            ),
        )
    )
    rows.append(
        Row(
            cell_id="P-2",
            label="innocent ejections (of every ejection)",
            population="ejection",
            note=(
                "the record audit's published cell 2, and this memo's shared "
                "population; NOT predictable offline"
            ),
            recorded_off=_pair(
                cross_tab.non_direct_innocent + cross_tab.proof_present_innocent,
                cross_tab.ejections_total,
            ),
            reconstructed_off=_pair(walk.innocent_ejections, walk.ejections),
        )
    )
    rows.append(
        Row(
            cell_id="P-3",
            label="direct-proof ejections that convicted an impostor",
            population="ejection",
            note="the proof-present cell; innocent-free on these bytes",
            recorded_off=_pair(
                cross_tab.proof_present_impostor, cross_tab.proof_present_ejections
            ),
        )
    )
    rows.append(
        Row(
            cell_id="P-4",
            label="body-meeting ejections landing on an already-cleared player",
            population="ejection",
            note=(
                "the solvability gap the ledger sits inside: the crew's own "
                "pooled perception had ruled this player out; NOT predictable "
                "offline"
            ),
            recorded_off=_pair(
                solvability.cleared_player_ejections.numerator,
                solvability.cleared_player_ejections.denominator,
            ),
        )
    )

    # -- The reporter lever. ------------------------------------------------- #
    rows.extend(_reporter_rows(walk=walk, reporter=reporter, all_on=all_on))
    # -- The corroboration lever. -------------------------------------------- #
    rows.extend(_corroboration_rows(walk=walk, all_on=all_on))
    # -- The testimony lever. ------------------------------------------------ #
    rows.extend(_testimony_rows(walk=walk, all_on=all_on, leakage=leakage))
    # -- The render budget, priced for the whole slate. ---------------------- #
    rows.extend(
        _budget_rows(walk=walk, evidence_budget=evidence_budget, withhold=withhold)
    )
    return rows


def _reporter_rows(
    *, walk: _SetWalk, reporter: ReporterJusticeCells, all_on: _LegTallies
) -> list[Row]:
    """The reporter lever's OFF instrument column and its render census."""

    rows = [
        Row(
            cell_id="R-1",
            label="body-report meetings (of every meeting)",
            population="meeting",
            note="the only meetings that have a reporter seat at all",
            recorded_off=_pair(reporter.body_report_meetings, reporter.meetings),
            reconstructed_off=_pair(walk.body_report_meetings, walk.meetings),
        ),
        Row(
            cell_id="R-2",
            label="reporter is a CREWMATE (of body-report meetings)",
            population="meeting",
            note="the premise check: an impostor reporter would make the block a laundering channel",
            recorded_off=_pair(
                reporter.reporter_crewmate_meetings, reporter.body_report_meetings
            ),
        ),
        Row(
            cell_id="R-3",
            label="innocent ejections that ejected the meeting's own reporter",
            population="ejection",
            note="the class the lever aims at; exposure, not a predicted flip",
            recorded_off=_pair(
                reporter.reporter_innocent_ejections, reporter.innocent_ejections
            ),
        ),
        Row(
            cell_id="R-4",
            label="reporter ejected (per reporter slot)",
            population="slot",
            note="against R-5, the same rate for an innocent non-reporter seat",
            recorded_off=_pair(reporter.reporter_ejections, reporter.reporter_slots),
        ),
        Row(
            cell_id="R-5",
            label="innocent non-reporter ejected (per slot)",
            population="slot",
            note="R-4's baseline; the relative risk is R-4 over this",
            recorded_off=_pair(
                reporter.innocent_non_reporter_ejections,
                reporter.innocent_non_reporter_slots,
            ),
        ),
        Row(
            cell_id="R-6",
            label="crew SPEECH accusations aimed at the reporter",
            population="accusation",
            note="the channel the lever re-renders; the ballot half is R-8",
            recorded_off=_pair(
                reporter.crew_accusations_at_reporter, reporter.crew_accusations
            ),
        ),
        Row(
            cell_id="R-7",
            label="impostor SPEECH accusations aimed at the reporter",
            population="accusation",
            note="the impostor's standing aim at the reporter seat",
            recorded_off=_pair(
                reporter.impostor_accusations_at_reporter, reporter.impostor_accusations
            ),
        ),
        Row(
            cell_id="R-8",
            label="crew BALLOTS aimed at the reporter",
            population="ballot",
            note="the half that convicts; NOT predictable offline",
            recorded_off=_pair(
                reporter.crew_ballots_at_reporter, reporter.crew_ballots
            ),
        ),
        Row(
            cell_id="R-9",
            label="impostor BALLOTS aimed at the reporter",
            population="ballot",
            note="the impostor half of R-8; NOT predictable offline",
            recorded_off=_pair(
                reporter.impostor_ballots_at_reporter, reporter.impostor_ballots
            ),
        ),
        Row(
            cell_id="R-10",
            label="ballot rationales carrying an exculpatory hinge (upper bound)",
            population="ballot",
            note=(
                "the exculpation ARGUED rather than merely rendered; an upper "
                "bound by the instrument's own stated hinge list"
            ),
            recorded_off=_pair(
                reporter.ballot_rationales_with_hinge, reporter.ballot_rationales
            ),
        ),
        Row(
            cell_id="R-11",
            label="body-report meetings carrying a non-reporter co-discoverer",
            population="meeting",
            note="the population A-38's widening was rejected over",
            recorded_off=_pair(
                reporter.meetings_with_co_discoverer, reporter.body_report_meetings
            ),
        ),
        Row(
            cell_id="R-12",
            label="co-discoverer slots held by an IMPOSTOR",
            population="slot",
            note=(
                "the OVER-DAMPING exposure: extending exculpatory framing beyond "
                "the report action hands it to an impostor this often"
            ),
            recorded_off=_pair(
                reporter.co_discoverer_slots_impostor, reporter.co_discoverer_slots
            ),
        ),
        Row(
            cell_id="R-13",
            label="reporter openings gaining the discovery-account block",
            population="prompt",
            note="a RENDER cell: the smoke's first ON seed can falsify it at n=1",
            reconstructed_off=_pair(0, walk.reporter_openings),
            on=_pair(
                walk.legs["reporter_reasoning"].changed[_KIND_CREWMATE_REPORT]
                + walk.legs["reporter_reasoning"].changed[_KIND_IMPOSTOR_REPORT],
                walk.reporter_openings,
            ),
            on_slate="reporter_reasoning",
        ),
        Row(
            cell_id="R-14",
            label="non-reporter speech turns gaining the base-rate block",
            population="prompt",
            note="a RENDER cell: per meeting and per prompt class, checkable on one seed",
            reconstructed_off=_pair(0, walk.non_reporter_speech_turns),
            on=_pair(
                walk.legs["reporter_reasoning"].changed[_KIND_ACCUSATION_ROUND],
                walk.non_reporter_speech_turns,
            ),
            on_slate="reporter_reasoning",
        ),
        Row(
            cell_id="R-15",
            label="ballots gaining a reporter block",
            population="ballot",
            note=(
                "exactly zero by construction: the 15.5 exculpation already "
                "renders on every body-report ballot, unconditionally"
            ),
            reconstructed_off=_pair(0, all_on.rendered[_KIND_VOTE_BALLOT]),
            on=_pair(
                walk.legs["reporter_reasoning"].changed[_KIND_VOTE_BALLOT],
                all_on.rendered[_KIND_VOTE_BALLOT],
            ),
            on_slate="reporter_reasoning",
        ),
    ]
    return rows


def _corroboration_rows(*, walk: _SetWalk, all_on: _LegTallies) -> list[Row]:
    """The four ledger cells, the ballot census and the block's render census."""

    cells = walk.corroboration
    return [
        Row(
            cell_id="C-1",
            label="accused subjects with NO first-hand source",
            population="accused row",
            note=(
                "the block's headline row; first pinned here, sourced to the "
                "#415/#417 records"
            ),
            reconstructed_off=_pair(
                cells["accused_without_a_first_hand_source"], cells["rows"]
            ),
            on=_pair(cells["accused_without_a_first_hand_source"], cells["rows"]),
            on_slate="corroboration_discipline",
        ),
        Row(
            cell_id="C-2",
            label="ejected subjects with NO first-hand source",
            population="ejection",
            note="over the ejections that carry a row at all",
            reconstructed_off=_pair(
                cells["ejected_without_a_first_hand_source"], cells["ejected_rows"]
            ),
            on=_pair(
                cells["ejected_without_a_first_hand_source"], cells["ejected_rows"]
            ),
            on_slate="corroboration_discipline",
        ),
        Row(
            cell_id="C-3",
            label="ejections whose charge ANSWERED the ejectee's own",
            population="ejection",
            note="an answer to a charge is not a second witness",
            reconstructed_off=_pair(
                cells["ejected_on_an_answering_turn"], cells["ejections"]
            ),
            on=_pair(cells["ejected_on_an_answering_turn"], cells["ejections"]),
            on_slate="corroboration_discipline",
        ),
        Row(
            cell_id="C-4",
            label="ejected subjects with a map-satisfied placement pair",
            population="ejection",
            note="the pair one tick of walking reconciles, capped at two per subject",
            reconstructed_off=_pair(
                cells["ejected_with_a_walkable_pair"], cells["ejections"]
            ),
            on=_pair(cells["ejected_with_a_walkable_pair"], cells["ejections"]),
            on_slate="corroboration_discipline",
        ),
        Row(
            cell_id="C-5",
            label="ejecting ballots citing HEARSAY (another speaker's turn)",
            population="ballot",
            note="over the ballots that ejected an innocent; the pile's own channel",
            reconstructed_off=_pair(
                walk.ballots.citations.get("hearsay", 0), walk.ballots.ejecting_ballots
            ),
        ),
        Row(
            cell_id="C-6",
            label="ejecting ballots citing the voter's OWN observation",
            population="ballot",
            note="C-5's grounded counterpart, same denominator",
            reconstructed_off=_pair(
                walk.ballots.citations.get("own_obs", 0), walk.ballots.ejecting_ballots
            ),
        ),
        Row(
            cell_id="C-7",
            label="ejecting ballots citing NOTHING",
            population="ballot",
            note="expected zero: the citation gate coerces an uncited eject to SKIP",
            reconstructed_off=_pair(
                walk.ballots.citations.get("none", 0), walk.ballots.ejecting_ballots
            ),
        ),
        Row(
            cell_id="C-8",
            label="innocent ejections carrying an impossible-transit charge",
            population="ejection",
            note=(
                "A JUDGMENT NET, quoted as one: a regex over ballot prose that "
                "over-triggers on true statements about venting"
            ),
            reconstructed_off=_pair(
                sum(1 for row in walk.ledger_rows if row.impossible_transit),
                len(walk.ledger_rows),
            ),
        ),
        Row(
            cell_id="C-9",
            label="ballots gaining the source-count block",
            population="ballot",
            note="a RENDER cell: falsifiable on the smoke's first ON seed",
            reconstructed_off=_pair(0, all_on.rendered[_KIND_VOTE_BALLOT]),
            on=_pair(
                walk.legs["corroboration_discipline"].changed[_KIND_VOTE_BALLOT],
                all_on.rendered[_KIND_VOTE_BALLOT],
            ),
            on_slate="corroboration_discipline",
        ),
    ]


def _testimony_rows(
    *, walk: _SetWalk, all_on: _LegTallies, leakage: ScaffoldLeakageCells
) -> list[Row]:
    """The reduction, ingest, laundering and confession cells."""

    census = walk.testimony
    off_total = sum(census.off_kinds.values())
    on_total = sum(census.on_kinds.values())
    rows = [
        Row(
            cell_id="T-1",
            label="spoken statements surviving the reduction",
            population="statement",
            note=(
                "ONE STEP AHEAD at each recorded boundary: meeting 2's ON "
                "transcript is a model output that does not exist"
            ),
            reconstructed_off=_pair(off_total, on_total),
            on=_pair(on_total, on_total),
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-2",
            label="whereabouts self-placements dropped whole",
            population="statement",
            note="the largest single shape the reduction discards; ONE STEP AHEAD",
            reconstructed_off=_pair(0, census.on_kinds["whereabouts"]),
            on=_pair(census.on_kinds["whereabouts"], census.on_kinds["whereabouts"]),
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-3",
            label="saw_move transitions dropped whole",
            population="statement",
            note="the movement channel the reduction discards; ONE STEP AHEAD",
            reconstructed_off=_pair(0, census.on_kinds["saw_move"]),
            on=_pair(census.on_kinds["saw_move"], census.on_kinds["saw_move"]),
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-4",
            label="saw_kill accounts carried as content",
            population="statement",
            note=(
                "the strongest testimony has NO structured form on the committed "
                "bytes: the shape did not exist before the lever"
            ),
            reconstructed_off=_pair(0, census.on_kinds["saw_kill"]),
            on=_pair(census.on_kinds["saw_kill"], census.on_kinds["saw_kill"]),
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-5",
            label="episodic rows the ingest writes at recorded boundaries",
            population="row",
            note=(
                "an UPPER BOUND (the own-statement guard applied, the per-listener "
                "roster gate not); ONE STEP AHEAD, never compounded"
            ),
            reconstructed_off=_pair(census.off_rows, census.on_rows),
            on=_pair(census.on_rows, census.on_rows),
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-6",
            label="location accounts that reach the alibi map",
            population="statement",
            note=(
                "the widened ('alibi','whereabouts') gate takes this to the full "
                "population — a natural full-population tripwire"
            ),
            reconstructed_off=census.alibi_map_off,
            on=census.alibi_map_on,
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-7",
            label="spoken vent accounts naming a player who never vented",
            population="statement",
            note=(
                "an exact-ZERO OFF reading, offered as a ZERO TRIPWIRE: ON must "
                "not raise it. No lever removes anything here"
            ),
            reconstructed_off=_pair(
                census.fabricated_vent_rows, census.spoken_vent_rows
            ),
            on=_pair(census.fabricated_vent_rows, census.spoken_vent_rows),
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-7b",
            label="spoken vent accounts the SPEAKER's own record does not bear out",
            population="statement",
            note=(
                "the speaker-side grounding census the corroboration ledger "
                "reads, printed beside T-7 so the two are not blended: an "
                "account can name a real venter and still be a source this "
                "speaker cannot supply. NOT a fabrication count, and no lever is "
                "claimed to remove it"
            ),
            reconstructed_off=_pair(
                census.ungrounded_vent_rows, census.spoken_vent_rows
            ),
            on=_pair(census.ungrounded_vent_rows, census.spoken_vent_rows),
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-8",
            label="player-visible self-disclosure turns by an IMPOSTOR speaker",
            population="turn",
            note=(
                "read straight off the shipped disambiguation pair; never "
                "re-conditioned here"
            ),
            recorded_off=_pair(
                leakage.model_self_disclosure_visible_turns,
                leakage.model_self_disclosure_visible_turns
                + leakage.crew_self_disclosure_control_turns,
            ),
        ),
        Row(
            cell_id="T-9",
            label="speech turns gaining a testimony-shape block",
            population="prompt",
            note="a RENDER cell: crew-only elicitation, checkable on one seed",
            reconstructed_off=_pair(0, all_on.rendered[_KIND_ACCUSATION_ROUND]),
            on=_pair(
                walk.legs["testimony_shapes"].changed[_KIND_ACCUSATION_ROUND],
                all_on.rendered[_KIND_ACCUSATION_ROUND],
            ),
            on_slate="testimony_shapes",
        ),
        Row(
            cell_id="T-10",
            label="opening prompts gaining a testimony-shape block",
            population="prompt",
            note="a RENDER cell on the crewmate-report body, every meeting",
            reconstructed_off=_pair(0, all_on.rendered[_KIND_CREWMATE_REPORT]),
            on=_pair(
                walk.legs["testimony_shapes"].changed[_KIND_CREWMATE_REPORT],
                all_on.rendered[_KIND_CREWMATE_REPORT],
            ),
            on_slate="testimony_shapes",
        ),
    ]
    return rows


def _budget_rows(
    *, walk: _SetWalk, evidence_budget: RenderBudgetCells, withhold: str
) -> list[Row]:
    """The render budget the three levers spend against, priced first-class."""

    off_leg = walk.legs[_SLATE_OFF]
    all_on = walk.legs[_SLATE_ALL_ON]
    less = walk.legs[decomposition_label(withhold)]
    return [
        Row(
            cell_id="B-1",
            label="rendered memory rows per prompt snapshot",
            population="row per snapshot",
            note=(
                "the budget the levers spend against. LEVER-INVARIANT at the "
                "recorded boundary by construction: the memory snapshot is "
                "composed before a template renders, so added prose displaces no "
                "row. The slate can only move this cell through the widened "
                "INGEST, and that is the compounding effect no offline "
                "instrument can reach"
            ),
            recorded_off=_pair(
                evidence_budget.rendered_lines_total, evidence_budget.snapshots
            ),
            reconstructed_off=_pair(off_leg.rendered_lines, off_leg.snapshots),
            on=_pair(all_on.rendered_lines, all_on.snapshots),
        ),
        Row(
            cell_id="B-2",
            label="reported-testimony rows retained (of rendered rows)",
            population="row",
            note=(
                "the retention the widened ingest competes for; the bucketed "
                "split is in the per-set render census"
            ),
            recorded_off=_pair(
                evidence_budget.testimony_rows_total,
                evidence_budget.rendered_lines_total,
            ),
            reconstructed_off=_pair(off_leg.testimony_rows, off_leg.rendered_lines),
            on=_pair(all_on.testimony_rows, all_on.rendered_lines),
        ),
        Row(
            cell_id="B-3",
            label="prose lines the slate ADDS, per rendered prompt",
            population="line per prompt",
            note=(
                "what three levers writing into the same prompt actually cost, "
                "which is the interaction that can make an ON arm strictly worse"
            ),
            reconstructed_off=_pair(0, _rendered_prompts(off_leg)),
            on=_pair(sum(all_on.added_lines.values()), _rendered_prompts(all_on)),
        ),
        Row(
            cell_id="B-4",
            label="prose lines added, leave-one-out",
            population="line per prompt",
            note=f"B-3 with {withhold} withheld — the attribution leg",
            reconstructed_off=_pair(0, _rendered_prompts(off_leg)),
            on=_pair(sum(less.added_lines.values()), _rendered_prompts(less)),
            on_slate=decomposition_label(withhold),
        ),
    ]


def _rendered_prompts(leg: _LegTallies) -> int:
    return sum(leg.rendered.values())


# --------------------------------------------------------------------------- #
# The tripwire readers the pre-registration ratified but had no cell for.      #
# --------------------------------------------------------------------------- #


def build_tripwire_rows(
    *, walk: _SetWalk, committed: TournamentEvalReport
) -> list[Row]:
    """The three cells the ratified pre-registration named and could not read.

    Published BESIDE the counterfactual's own table rather than inside it: that
    table is a published census, pinned row for row by the memo it appears in,
    and these cells are readers for criteria ratified after it. Each answers one
    predicate of ``audits/audit-phase-21-preregistration.md`` — T5's role split
    (§8.1), T7's first-meeting identity (§8.1) and bar 1's spoken-kill split
    (§5) — and none of them is a bar.
    """

    census = walk.elicitation
    off_leg = walk.legs[_SLATE_OFF]
    all_on = walk.legs[_SLATE_ALL_ON]
    cross_tab = committed.deduction.ejectee_proof_cross_tab
    kills = walk.kill_named
    return [
        Row(
            cell_id="T-9a",
            label="CREW speech turns gaining the witnessed-kill elicitation block",
            population="prompt",
            note=(
                "T5's first half. Presence of the BLOCK's own lines, derived "
                "from the shipped template by rendering one crew turn both "
                "ways — not a byte diff, which also moves for the role-blind "
                "public-transcript row"
            ),
            reconstructed_off=_pair(0, census.rendered["CREWMATE"]),
            on=_pair(census.gained["CREWMATE"], census.rendered["CREWMATE"]),
            on_slate=_ELICITATION_LEG,
        ),
        Row(
            cell_id="T-9b",
            label="IMPOSTOR speech turns gaining the witnessed-kill elicitation block",
            population="prompt",
            note=(
                "T5's second half, a NEVER-WORSE bar's count: an impostor "
                "offered the shape is a firewall question. An impostor prompt "
                "merely rendering a publicly spoken kill row is CORRECT and is "
                "excluded here by construction"
            ),
            reconstructed_off=_pair(0, census.rendered["IMPOSTOR"]),
            on=_pair(census.gained["IMPOSTOR"], census.rendered["IMPOSTOR"]),
            on_slate=_ELICITATION_LEG,
        ),
        Row(
            cell_id="B-1m1",
            label="rendered memory rows per prompt snapshot, FIRST meeting only",
            population="row per snapshot",
            note=(
                "T7's predicate, which is a first-meeting identity: the "
                "published B-1 sums every captured meeting, where a "
                "first-meeting difference and an opposite later one cancel. "
                "RECORDED-OFF is folded from the recorded call bytes, "
                "RECONSTRUCTED-OFF from the re-render that reproduces them"
            ),
            recorded_off=_pair(
                walk.recorded_first_meeting_rendered_lines,
                walk.recorded_first_meeting_snapshots,
            ),
            reconstructed_off=_pair(
                off_leg.first_meeting_rendered_lines, off_leg.first_meeting_snapshots
            ),
            on=_pair(
                all_on.first_meeting_rendered_lines, all_on.first_meeting_snapshots
            ),
        ),
        Row(
            cell_id="P-1k",
            label="non-direct convictions whose ejectee a spoken kill named",
            population="ejection",
            note=(
                "bar 1's cell split by a spoken kill, observed and never "
                "gated. The denominator is bar 1's own, from the committed "
                "cross-tab; NOT predictable offline, because whether anyone "
                "speaks the shape is a model output"
            ),
            recorded_off=_pair(kills.kill_named, cross_tab.non_direct_ejections),
            reconstructed_off=_pair(kills.kill_named, kills.non_direct),
        ),
        Row(
            cell_id="P-1ka",
            label="of those, the ones that convicted an IMPOSTOR",
            population="ejection",
            note=(
                "the accuracy side of the same split, so a movement in bar 1 "
                "can be attributed to the eyewitness channel rather than "
                "credited to it by assumption"
            ),
            recorded_off=_pair(kills.kill_named_impostor, kills.kill_named),
            reconstructed_off=_pair(kills.kill_named_impostor, kills.kill_named),
        ),
    ]


# --------------------------------------------------------------------------- #
# The guard, written before the folds.                                         #
# --------------------------------------------------------------------------- #


def _assert_live_slate(when: str) -> None:
    """Refuse to run once the OFF column this table prices cannot be produced.

    TWO environments are checked, and the second is the load-bearing one.

    The first half is the Phase-20 precedent: a lever that GRADUATED ignores the
    argument this script toggles it with, so its OFF derivation no longer exists
    in this build and the OFF column would silently be the ON column.

    The second half is the reason a passing empty-mapping check is not enough.
    Seven consumers re-derive the meeting reduction with no ``env`` argument at
    all, so a stale ``AILIBI_*`` export in the operator's shell would make every
    IMPORTED instrument's "OFF" column an ON column while the first check sailed
    through green. The refusal names the variable and says to unset it.

    That half checks EVERY live toggle, not only the priced three. The recorded
    substrate stamps all of them OFF, and the one this memo holds OFF is the one
    an export would damage most quietly: its arm swaps a template file, so a
    stale export would serve a body neither priced lever's block reaches.
    """

    registered = {key for key, _ in _TOGGLEABLE_LEVER_RESOLVERS}
    missing = sorted(key for key in WAVE_2_LEVERS if key not in registered)
    if missing:
        raise SystemExit(
            f"the OFF column cannot be produced {when}: "
            + ", ".join(f"{key} ({env_var_for_lever(key)})" for key in missing)
            + " is no longer a live toggle in "
            "orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS, so this build has "
            "no OFF derivation to compare against. A lever graduates at the "
            "record that adopts it; the memo's table is FROZEN as the pre-record "
            "prediction it was: audits/audit-phase-21-counterfactual.md"
        )
    empty = substrate_flag_snapshot({})
    graduated = sorted(key for key in WAVE_2_LEVERS if empty.get(key, False))
    if graduated:
        raise SystemExit(
            f"the OFF column cannot be produced {when}: "
            + ", ".join(f"{key} ({env_var_for_lever(key)})" for key in graduated)
            + " reads ON under an EMPTY environment, so it graduated to "
            "unconditionally ON at the record that adopted it and this build has "
            "no OFF derivation to compare against. The memo's table is FROZEN as "
            "the pre-record prediction it was: "
            "audits/audit-phase-21-counterfactual.md"
        )
    ambient = substrate_flag_snapshot()
    exported = sorted(
        key for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS if ambient.get(key, False)
    )
    if exported:
        raise SystemExit(
            f"the ambient environment is not the record's substrate {when}: "
            + ", ".join(f"{key} ({env_var_for_lever(key)})" for key in exported)
            + " is exported ON in this process, and the committed recordings "
            "stamp every live toggle OFF. Seven consumers re-derive the meeting "
            "reduction with no env argument, so every imported instrument's OFF "
            "column would silently be an ON column. Unset "
            + ", ".join(env_var_for_lever(key) for key in exported)
            + " and run again"
        )


def _assert_slate_is_the_three_wave_2_keys() -> None:
    """The slate is three keys, and a fourth is refused."""

    if len(WAVE_2_LEVERS) != 3 or NON_WAVE_2_LEVER in WAVE_2_LEVERS:
        raise SystemExit(
            "the priced slate must be exactly the three Wave-2 keys with "
            f"{NON_WAVE_2_LEVER} OFF: that arm SWAPS accusation_round.j2 for a "
            "variant carrying neither sibling's block, so a four-key slate would "
            "drop the reporter and testimony-shapes effects from every statement "
            "turn while a composite stamp claimed them"
        )


# --------------------------------------------------------------------------- #
# The run.                                                                     #
# --------------------------------------------------------------------------- #

#: A per-set cell this small moves by more than the difference the memo is
#: discussing when one case changes, so it takes no part in a directional
#: statement and is printed with an advisory label instead.
ADVISORY_INNOCENT_EJECTIONS: Final[int] = 5


def run(
    set_names: Sequence[str], *, withhold: str = "testimony_shapes"
) -> dict[str, object]:
    """Compute the whole table for the named sets, plus the pooled column."""

    _assert_slate_is_the_three_wave_2_keys()
    _assert_live_slate("at start")
    if withhold not in WAVE_2_LEVERS:
        raise SystemExit(
            f"--withhold {withhold!r} is not a Wave-2 lever; the leave-one-out "
            f"leg drops one of {list(WAVE_2_LEVERS)}"
        )
    payload: dict[str, object] = {
        "levers": list(WAVE_2_LEVERS),
        "held_off": NON_WAVE_2_LEVER,
        "decomposition_withholds": withhold,
        "slate_legs": [label for label, _ in _slate_legs(withhold)],
        "sets": {},
    }
    per_set: dict[str, object] = {}
    pooled_walks: list[_SetWalk] = []
    pooled_reporter: list[ReporterJusticeCells] = []
    pooled = _PooledRows()
    pooled_tripwires = _PooledRows()
    ledger_rows: list[InjusticeLedgerRow] = []
    # Cells whose two OFF readings disagreed on ANY set. The pooled ON column is
    # withdrawn for every one of them: summing the sets that DID reproduce would
    # publish a pooled row over a silently reduced denominator, which is the
    # opposite of what the fidelity refusal exists to do.
    withdrawn: set[str] = set()
    for set_name in set_names:
        sample_dir = _REPO_ROOT / "replays" / set_name
        walk = walk_set(sample_dir, set_name=set_name, withhold=withhold)
        expected = COMMITTED_INNOCENT_EJECTIONS.get(set_name)
        if expected is not None and walk.innocent_ejections != expected:
            raise SystemExit(
                f"{set_name}: the innocent-ejection enumeration reproduced "
                f"{walk.innocent_ejections}, not the committed record cell "
                f"{expected} (audits/audit-phase-21-rerecord.md §5.1, published "
                "cell 2) — this is a DEFECT IN THIS SCRIPT's join, not a finding "
                "about the committed bytes; fix the enumeration before reading "
                "any ON number"
            )
        reporter = compute_reporter_justice(sample_dir)
        evidence = compute_evidence_honesty(sample_dir)
        solvability = compute_solvability_report(sample_dir)
        committed = TournamentEvalReport.model_validate_json(
            (sample_dir / "tournament-eval-report.json").read_text(encoding="utf-8")
        )
        _assert_ledger_matches_the_instruments(
            walk=walk, reporter=reporter, committed=committed
        )
        rows = build_rows(
            walk=walk,
            reporter=reporter,
            evidence_budget=evidence.render_budget,
            solvability=solvability,
            committed=committed,
            withhold=withhold,
        )
        tripwires = build_tripwire_rows(walk=walk, committed=committed)
        disagreeing = [row for row in (*rows, *tripwires) if not row.agrees]
        withdrawn.update(row.cell_id for row in disagreeing)
        rows = [row if row.agrees else _withdraw_on_column(row) for row in rows]
        tripwires = [
            row if row.agrees else _withdraw_on_column(row) for row in tripwires
        ]
        per_set[set_name] = {
            "games": walk.games,
            "meetings": walk.meetings,
            "body_report_meetings": walk.body_report_meetings,
            "ejections": walk.ejections,
            "innocent_ejections": walk.innocent_ejections,
            "elapsed_seconds": round(walk.elapsed, 2),
            "advisory": walk.innocent_ejections <= ADVISORY_INNOCENT_EJECTIONS,
            "rows": [row.payload() for row in rows],
            "tripwire_rows": [row.payload() for row in tripwires],
            "render_census": _render_census_payload(walk, withhold=withhold),
            "ballot_census": walk.ballots.payload(),
            "testimony_census": walk.testimony.payload(),
            "injustice_ledger": [row.payload() for row in walk.ledger_rows],
            "ledger_class_totals": _class_totals(walk.ledger_rows),
            "disagreeing_cells": [row.cell_id for row in disagreeing],
        }
        ledger_rows.extend(walk.ledger_rows)
        pooled_walks.append(walk)
        pooled_reporter.append(reporter)
        for row in rows:
            pooled.add(row)
        for row in tripwires:
            pooled_tripwires.add(row)
    payload["sets"] = per_set
    payload["pooled"] = pooled.payload(withdrawn=withdrawn)
    payload["pooled_tripwire_rows"] = pooled_tripwires.payload(withdrawn=withdrawn)
    payload["withdrawn_on_cells"] = sorted(withdrawn)
    payload["pooled_ledger_class_totals"] = _class_totals(ledger_rows)
    payload["pooled_injustice_ledger"] = [row.payload() for row in ledger_rows]
    payload["pooled_reporter_justice"] = _reporter_payload(
        pool_reporter_justice(pooled_reporter)
    )
    payload["pooled_ballot_census"] = _pool_ballot_census(pooled_walks)
    payload["pooled_testimony_census"] = _pool_testimony_census(pooled_walks)
    payload["pooled_render_census"] = _pool_render_census(
        pooled_walks, withhold=withhold
    )
    payload["corroboration_pins"] = _corroboration_pin_check(pooled_walks)
    _assert_live_slate("at exit")
    return payload


def _pooled_row(
    *,
    key: str,
    cell_id: str,
    label: str,
    population: str,
    note: str,
    on_slate: str,
    totals: Mapping[str, int],
    withdrawn: set[str],
) -> dict[str, object]:
    """One pooled row, with the ON column withdrawn if any set disagreed."""

    columns: dict[str, list[int] | None] = {}
    for column in ("recorded_off", "reconstructed_off", "on"):
        if f"{key}|{column}|d" not in totals:
            columns[column] = None
            continue
        columns[column] = [totals[f"{key}|{column}|n"], totals[f"{key}|{column}|d"]]
    withheld = cell_id in withdrawn
    if withheld:
        columns["on"] = None
        note = (
            f"{note} — the pooled ON column is WITHDRAWN: at least one set's two "
            "OFF readings disagreed, and pooling the sets that did reproduce "
            "would publish a row over a silently reduced denominator"
        )
    denominators = [pair[1] for pair in columns.values() if pair is not None]
    return {
        "cell": cell_id,
        "label": label,
        "population": population,
        "note": note,
        "on_slate": on_slate,
        "advisory": any(value <= ADVISORY_DENOMINATOR for value in denominators),
        "on_withdrawn": withheld,
        **columns,
    }


class _PooledRows:
    """One table's rows summed across sets, published in first-seen order.

    The sets are disjoint games, so pooling is addition. A cell is keyed by its
    id AND its label, so a row whose meaning changed between sets cannot be
    summed onto the old one.
    """

    def __init__(self) -> None:
        self._totals: Counter[str] = Counter()
        self._labels: dict[str, tuple[str, str, str, str, str]] = {}

    def add(self, row: Row) -> None:
        key = f"{row.cell_id}|{row.label}"
        self._labels[key] = (
            row.cell_id,
            row.label,
            row.population,
            row.note,
            row.on_slate,
        )
        for column, pair in (
            ("recorded_off", row.recorded_off),
            ("reconstructed_off", row.reconstructed_off),
            ("on", row.on),
        ):
            if pair is None:
                continue
            self._totals[f"{key}|{column}|n"] += pair[0]
            self._totals[f"{key}|{column}|d"] += pair[1]

    def payload(self, *, withdrawn: set[str]) -> list[dict[str, object]]:
        return [
            _pooled_row(
                key=key,
                cell_id=cell_id,
                label=label,
                population=population,
                note=note,
                on_slate=on_slate,
                totals=self._totals,
                withdrawn=withdrawn,
            )
            for key, (
                cell_id,
                label,
                population,
                note,
                on_slate,
            ) in self._labels.items()
        ]


def _pool_ballot_census(walks: Sequence[_SetWalk]) -> dict[str, object]:
    """The ejecting-ballot census summed over every walked set.

    Counts over disjoint games, so pooling is addition; the confidence means are
    re-derived from the pooled numerator and denominator rather than averaged,
    which is what stops a four-ejection set dragging a rate.
    """

    citations: Counter[str] = Counter()
    driver: Counter[str] = Counter()
    followers = {"CREWMATE": Counter[int](), "IMPOSTOR": Counter[int]()}
    confidence: dict[str, list[float]] = {"flagged": [], "unflagged": []}
    ejecting = cast = joined = 0
    for walk in walks:
        census = walk.ballots
        ejecting += census.ejecting_ballots
        citations.update(census.citations)
        driver.update(census.driver_role)
        for role, counts in census.follower_counts.items():
            followers[role].update(counts)
        for status, values in census.confidence_by_flag.items():
            confidence[status].extend(values)
        cast += census.impostor_ballots_in_these_meetings
        joined += census.impostor_ballots_joining_the_pile
    return {
        "ejecting_ballots": ejecting,
        "citation_mix": {name: citations.get(name, 0) for name in _CITATION_CLASSES},
        "mean_confidence": {
            status: (round(sum(values) / len(values), 4) if values else None)
            for status, values in confidence.items()
        },
        "ejections_by_flag_status": {
            status: len(values) for status, values in confidence.items()
        },
        "pile_driver_role": dict(sorted(driver.items())),
        "follower_counts": {
            role: dict(sorted(counts.items())) for role, counts in followers.items()
        },
        "impostor_ballots_cast": cast,
        "impostor_ballots_joining_the_pile": joined,
    }


def _pool_testimony_census(walks: Sequence[_SetWalk]) -> dict[str, object]:
    """The reduction and ingest census summed over every walked set."""

    pooled = _TestimonyCensus()
    for walk in walks:
        census = walk.testimony
        pooled.off_kinds.update(census.off_kinds)
        pooled.on_kinds.update(census.on_kinds)
        pooled.off_rows += census.off_rows
        pooled.on_rows += census.on_rows
        pooled.listener_slots += census.listener_slots
        pooled.spoken_vent_rows += census.spoken_vent_rows
        pooled.fabricated_vent_rows += census.fabricated_vent_rows
        pooled.ungrounded_vent_rows += census.ungrounded_vent_rows
    return pooled.payload()


def _pool_render_census(
    walks: Sequence[_SetWalk], *, withhold: str
) -> dict[str, object]:
    """The per-lever render census summed over every walked set."""

    labels = [label for label, _ in _slate_legs(withhold)]
    pooled: dict[str, object] = {}
    for label in labels:
        totals = _LegTallies()
        touched = 0
        for walk in walks:
            leg = walk.legs[label]
            touched += leg.meetings_touched
            totals.snapshots += leg.snapshots
            totals.rendered_lines += leg.rendered_lines
            totals.testimony_rows += leg.testimony_rows
            totals.testimony_by_bucket.update(leg.testimony_by_bucket)
            totals.rendered.update(leg.rendered)
            totals.changed.update(leg.changed)
            totals.added_lines.update(leg.added_lines)
            totals.added_bytes.update(leg.added_bytes)
        pooled[label] = {
            "meetings_touched": touched,
            "by_prompt_class": _census_by_class(label, totals),
            "render_budget": totals.budget().model_dump(),
        }
    return pooled


def _census_by_class(label: str, leg: _LegTallies) -> dict[str, dict[str, object]]:
    """One :class:`LeverExposureCensus` per prompt class the leg rendered."""

    return {
        kind: vars(
            LeverExposureCensus(
                lever=label,
                prompt_class=kind,
                rendered=leg.rendered[kind],
                changed=leg.changed[kind],
                added_lines=leg.added_lines[kind],
                added_bytes=leg.added_bytes[kind],
            )
        )
        for kind in (*_TURN_KINDS, _KIND_VOTE_BALLOT)
        if leg.rendered[kind]
    }


def _assert_ledger_matches_the_instruments(
    *,
    walk: _SetWalk,
    reporter: ReporterJusticeCells,
    committed: TournamentEvalReport,
) -> None:
    """Two structural ledger tags cross-checked against committed instruments.

    RC is the reporter class and must equal ``eval.reporter_justice``'s own
    ``reporter_innocent_ejections``; WEAKFLAG must equal the committed
    weak-flag conviction cell's innocent count. Both are joins over the same
    recorded fields by two independently written folds, so a disagreement is a
    DEFECT IN THIS SCRIPT's tagging, not a finding about the bytes.

    The spoken-kill split's own denominator is checked the same way: it is bar
    1's non-direct cell, so this walk's partition must land on the committed
    cross-tab's count or the split is decomposing a different population.
    """

    totals = _class_totals(walk.ledger_rows)
    checks = (
        (
            "RC",
            totals.get("RC", 0),
            reporter.reporter_innocent_ejections,
            "eval.reporter_justice.compute_reporter_justice",
        ),
        (
            "WEAKFLAG",
            totals.get("WEAKFLAG", 0),
            committed.deduction.weak_flag_conviction.weak_flag_only_innocent,
            "the committed weak-flag conviction cell",
        ),
        (
            "non-direct",
            walk.kill_named.non_direct,
            committed.deduction.ejectee_proof_cross_tab.non_direct_ejections,
            "the committed EjecteeProofCrossTab",
        ),
    )
    for tag, measured, expected, source in checks:
        if measured != expected:
            raise SystemExit(
                f"{walk.set_name}: this walk's {tag} class counted "
                f"{measured} against {expected} from {source} — this is a DEFECT "
                "IN THIS SCRIPT's join, not a finding about the committed "
                "bytes; fix the join before reading any ON number"
            )


def _withdraw_on_column(row: Row) -> Row:
    """Keep the RECORDED value and drop the ON one, naming both readings."""

    return Row(
        cell_id=row.cell_id,
        label=row.label,
        population=row.population,
        note=(
            f"{row.note} — RECORDED-OFF and RECONSTRUCTED-OFF DISAGREE "
            f"({row.recorded_off} vs {row.reconstructed_off}); no ON value is "
            "printed for a cell whose baseline does not reproduce, and the "
            "disagreement is a DEFECT IN THIS SCRIPT"
        ),
        recorded_off=row.recorded_off,
        reconstructed_off=row.reconstructed_off,
        on=None,
        on_slate=row.on_slate,
    )


def _class_totals(rows: Sequence[InjusticeLedgerRow]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for row in rows:
        for tag in row.tags:
            totals[tag] += 1
    totals["TOTAL"] = len(rows)
    return dict(sorted(totals.items()))


def _render_census_payload(walk: _SetWalk, *, withhold: str) -> dict[str, object]:
    labels = {label for label, _ in _slate_legs(withhold)}
    return {
        label: {
            "meetings_touched": leg.meetings_touched,
            "by_prompt_class": _census_by_class(label, leg),
            "render_budget": leg.budget().model_dump(),
        }
        for label, leg in walk.legs.items()
        if label in labels
    }


def _reporter_payload(cells: ReporterJusticeCells) -> dict[str, object]:
    return {
        name: getattr(cells, name)
        for name in type(cells).__dataclass_fields__
        if name != "set_name"
    }


def _corroboration_pin_check(walks: Sequence[_SetWalk]) -> dict[str, object]:
    """The four corroboration cells against the records that published them.

    Task 21.19 shipped a walk that PRINTS these and deliberately asserts no
    figure, so this is where they first become an assertion. Only a full
    four-set run can be compared: a subset has a different population by
    construction and is reported unchecked rather than failed.
    """

    totals: Counter[str] = Counter()
    for walk in walks:
        totals.update(walk.corroboration)
    denominators = {
        "accused_without_a_first_hand_source": "rows",
        "ejected_without_a_first_hand_source": "ejected_rows",
        "ejected_on_an_answering_turn": "ejections",
        "ejected_with_a_walkable_pair": "ejections",
    }
    measured = {
        cell: [totals[cell], totals[denominator]]
        for cell, denominator in denominators.items()
    }
    if len(walks) != len(CANONICAL_SETS):
        return {"checked": False, "measured": measured}
    disagreeing = {
        cell: {"measured": measured[cell], "committed": list(expected)}
        for cell, expected in COMMITTED_CORROBORATION_CELLS.items()
        if tuple(measured[cell]) != expected
    }
    if disagreeing:
        raise SystemExit(
            "the corroboration ledger cells disagree with the records that "
            f"published them (#415 merge-reality, #417 amendment): {disagreeing}. "
            "This is a DEFECT IN THIS SCRIPT's walk, not a finding about the "
            "committed bytes; this script is where those four cells FIRST become "
            "a pin, so fix the walk before reading any ON number"
        )
    return {"checked": True, "measured": measured}


# --------------------------------------------------------------------------- #
# Printing.                                                                    #
# --------------------------------------------------------------------------- #


def _rate(pair: object) -> str:
    if pair is None:
        return "—"
    assert isinstance(pair, (list, tuple))
    numerator, denominator = int(pair[0]), int(pair[1])
    if denominator == 0:
        return f"{numerator}/0"
    return f"{numerator}/{denominator} = {numerator / denominator:.4f}"


ADVISORY_MARK: Final[str] = "[ADV]"
"""Printed beside any cell whose own denominator one case would dominate."""

_TRIPWIRE_HEADING: Final[str] = (
    "tripwire readers (pre-registration §8.1 T5 / T7 and §5's spoken-kill "
    "split); not part of this memo's published table, and no bar"
)


def _print_row(row: Mapping[str, object], *, out: TextIO) -> None:
    mark = f" {ADVISORY_MARK}" if row.get("advisory") else ""
    print(
        f"{str(row['cell']):<6} {str(row['label'])[:52]:<52} "
        f"{_rate(row.get('recorded_off')):>24} "
        f"{_rate(row.get('reconstructed_off')):>24} "
        f"{_rate(row.get('on')):>24}{mark}",
        file=out,
    )


def _print_table(
    payload: Mapping[str, object], *, stream: TextIO | None = None
) -> None:
    """Print the OFF/ON table the memo reproduces row for row."""

    out = sys.stdout if stream is None else stream
    header = (
        f"{'cell':<6} {'label':<52} {'RECORDED-OFF':>24} "
        f"{'RECONSTRUCTED-OFF':>24} {'ON':>24}"
    )
    sets = payload["sets"]
    assert isinstance(sets, dict)
    for set_name, block in sets.items():
        assert isinstance(block, dict)
        advisory = (
            " [ADVISORY — one case moves this set's cells]" if block["advisory"] else ""
        )
        print(
            f"\n== {set_name} ({block['games']} games, {block['meetings']} meetings, "
            f"{block['body_report_meetings']} body reports, "
            f"{block['innocent_ejections']} innocent ejections, "
            f"{block['elapsed_seconds']}s){advisory}",
            file=out,
        )
        print(header, file=out)
        for row in block["rows"]:
            _print_row(row, out=out)
        print(f"   -- {_TRIPWIRE_HEADING}", file=out)
        for row in block["tripwire_rows"]:
            _print_row(row, out=out)
        print(f"   injustice-ledger classes: {block['ledger_class_totals']}", file=out)
        for row in block["injustice_ledger"]:
            tags = "+".join(row["tags"]) or "(no tag)"
            print(
                f"     {row['set']} {row['seed']}:m{row['meeting']} "
                f"{row['victim']:<5} {tags:<48} {row['tally']}",
                file=out,
            )
        print(f"   ballot census: {block['ballot_census']}", file=out)
        print(f"   testimony census: {block['testimony_census']}", file=out)
        for label, census in block["render_census"].items():
            print(f"   render census [{label}]: {census['by_prompt_class']}", file=out)
    print("\n== POOLED", file=out)
    print(header, file=out)
    pooled = payload["pooled"]
    assert isinstance(pooled, list)
    for row in pooled:
        _print_row(row, out=out)
    print(f"-- {_TRIPWIRE_HEADING}", file=out)
    pooled_tripwires = payload["pooled_tripwire_rows"]
    assert isinstance(pooled_tripwires, list)
    for row in pooled_tripwires:
        _print_row(row, out=out)
    print(
        f"\npooled injustice-ledger classes: {payload['pooled_ledger_class_totals']}",
        file=out,
    )
    print(f"pooled ballot census: {payload['pooled_ballot_census']}", file=out)
    print(f"pooled testimony census: {payload['pooled_testimony_census']}", file=out)
    pooled_render = payload["pooled_render_census"]
    assert isinstance(pooled_render, dict)
    for label, census in pooled_render.items():
        print(
            f"pooled render census [{label}]: {census['by_prompt_class']} "
            f"budget={census['render_budget']}",
            file=out,
        )
    withdrawn = payload["withdrawn_on_cells"]
    assert isinstance(withdrawn, list)
    if withdrawn:
        print(
            "pooled ON column WITHDRAWN for: " + ", ".join(str(c) for c in withdrawn),
            file=out,
        )
    print(f"corroboration pins: {payload['corroboration_pins']}", file=out)
    _print_reading_rules(payload, out=out)


def _print_reading_rules(payload: Mapping[str, object], *, out: TextIO) -> None:
    """The footnotes a reader needs before comparing two columns."""

    print("\nreading rules:", file=out)
    for line in (
        "A sentence added to a prompt is not a vote that changes. Every ON cell "
        "here is a RENDER DIFF over the recorded inputs: it says what the lever "
        "puts in front of a reader, never what the reader then does.",
        "Exposure is an UPPER BOUND. A case a lever touches is not a case the "
        "lever fixes, and no row above subtracts an exposure count from an "
        "injustice count.",
        "C-8 (impossible transit) is a JUDGMENT NET in both readings and is "
        "quoted as one; its tagged rows are listed per set above so a reader can "
        "re-judge them.",
        "Every testimony-shapes ingest and render cell (T-1..T-7b, T-9, T-10) is "
        "a ONE-STEP-AHEAD reading at each recorded meeting boundary: meeting 1's "
        "ON render is derivable from meeting 1's recorded inputs, but meeting 2's "
        "ON transcript is a model output that does not exist.",
        "T-7 is an exact-zero OFF cell offered as a ZERO TRIPWIRE, never as an "
        "injustice a lever removes. T-7b is the speaker-side grounding census "
        "beside it and is a different question, not a fabrication count.",
        f"{ADVISORY_MARK} marks a row one case would dominate — any column whose "
        f"denominator is {ADVISORY_DENOMINATOR} or fewer. Such a row takes no "
        "part in a directional statement, whatever the size of the set it sits "
        "in.",
        "P-1, P-2, R-8, R-9, the stated-confidence response to any anchoring "
        "rule, whether crew stop laundering witnessed kills into vent rows, and "
        "the win split carry NO ON column at all.",
        "The tripwire rows (T-9a, T-9b, B-1m1, P-1k, P-1ka) read predicates "
        "the pre-registration ratified and no cell of the table above can "
        "evaluate. T-9a/T-9b test for the ELICITATION BLOCK's own lines, not "
        "for a byte difference: a spoken kill renders a role-blind "
        "public-transcript row into every later prompt, and an impostor "
        "carrying that row is correct.",
        f"The slate is the THREE Wave-2 levers with {payload['held_off']} OFF; "
        f"the leave-one-out leg withholds {payload['decomposition_withholds']}.",
        "This table writes no bar, no target and no decision rule.",
    ):
        print(f"  {line}", file=out)


# --------------------------------------------------------------------------- #
# The CLI.                                                                     #
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "The Phase-21 offline counterfactual: every Wave-2 cell the "
            "committed bytes can supply, OFF slate and ON slate, $0 and offline."
        )
    )
    parser.add_argument(
        "--sets",
        default="all",
        help=(
            "'all' for the four committed sets in the record audit's order, or "
            "one set name under replays/ (e.g. samples/4p1i) for iteration"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the same table machine-readably for the pre-registration",
    )
    parser.add_argument(
        "--withhold",
        default="testimony_shapes",
        choices=list(WAVE_2_LEVERS),
        help=(
            "the lever the render census's leave-one-out leg drops (default: "
            "testimony_shapes, the leg the memo publishes beside the headline). "
            "The headline ON column is always the full three"
        ),
    )
    args = parser.parse_args(argv)
    set_names = (
        list(CANONICAL_SETS) if args.sets == "all" else [str(args.sets).strip("/")]
    )
    started = time.monotonic()
    payload = run(set_names, withhold=str(args.withhold))
    elapsed = time.monotonic() - started
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_table(payload)
        print(f"\nwall time: {elapsed:.1f}s", file=sys.stdout)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
