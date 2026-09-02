"""The Phase-21 offline counterfactual: the Wave-2 slate over the re-recorded bytes.

Two modes over one machine, because the same three levers have to be read on
bytes recorded BOTH ways.

``--sets`` is the committed-record mode: the four committed replay sets, whose
bytes were recorded with every lever OFF. ``--recording <dir> --recorded-slate
on`` is the LEVER-ON mode: one directory of ``replay-seed-*.jsonl`` recorded with
the Wave-2 slate up -- 21.23's smoke and 21.24's record write exactly that, into
a scratch directory outside this repository -- and it reads the ratified
pre-registration's seven tripwire predicates off those bytes. The two modes share
the walk, the folds and the render diff; what changes is which slate the RECORD
is and therefore which direction the second render runs in.

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

Most ON cells count a prompt whose bytes MOVE. The three that name a specific
block -- ``R-13``, ``R-14`` and ``C-9`` -- count a COMPLETE gain of that block's
own lines instead, derived from the shipped template at runtime the way T5's and
T3's markers are: a whitespace-only guarded branch or an unrelated
lever-conditioned line moves bytes without putting any of the block on the page,
and a cell that credited one would report a prompt as having gained a block it
never received. The byte-diff count travels beside each of them as an
informational column; no verdict is taken from it.

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
assignment. The lever-ON mode needs a shell carrying the recording's own
``AILIBI_*`` exports -- ``api.replay_loader`` refuses a cross-substrate
reconstruction, and the manager resolves its two kwarg-toggled levers from that
same environment -- so it CHECKS the shell against the recording's stamp and
refuses a disagreement. It never writes one.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
from collections import Counter
from copy import deepcopy
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

from agents.memory.store import (  # noqa: E402
    AgentMemory,
    absorb_reported_testimony,
)
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
    TestimonySupport,
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
    MeetingReplayEntry,
    ReplayEntry,
    _TOGGLEABLE_LEVER_RESOLVERS,
    env_var_for_lever,
    read_all_entries,
    read_substrate_flags,
    retired_levers_stamped_off,
    substrate_flag_snapshot,
    substrate_slate_mismatches,
    substrate_stamp_mismatches,
)
from tests.meetings.test_prompt_byte_golden import (  # noqa: E402
    ReconstructedMeeting,
    resolve_prompt_set,
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

#: The slate a ``--recorded-slate on`` recording must stamp: the three Wave-2
#: keys ON and every other live toggle OFF. Named as the pre-registration's §9
#: slate, and the only value the lever-ON mode accepts -- a second slate is a
#: second criterion, and this instrument authors none.
RECORDED_SLATE_ON: Final[str] = "on"

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

# The four corroboration cells over the pooled four-set walk, as the
# counterfactual audit's Errata section republishes them. Task 21.19 shipped a
# walk that PRINTS them and deliberately asserts no figure; this script is where
# they first become an assertion. Three moved when the ledger's grounding
# semantics were amended before the record: a placement is now tested against
# BOTH of the speaker's own record channels, and the walkable-transit clause
# reads movement-shaped placements (#415 merge-reality, #417 amendment, then
# audits/audit-phase-21-counterfactual.md Errata E.2).
COMMITTED_CORROBORATION_CELLS: Final[Mapping[str, tuple[int, int]]] = MappingProxyType(
    {
        "accused_without_a_first_hand_source": (460, 1525),
        "ejected_without_a_first_hand_source": (10, 425),
        "ejected_on_an_answering_turn": (33, 429),
        "ejected_with_a_walkable_pair": (79, 429),
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
    """One renderer invocation, with the exact keyword inputs it was given.

    ``recorded_prompt`` is the bytes the manager produced during the walk, which
    the recorded-response stub matched against the recording's own
    ``llm_calls[].prompt``. It is the RECORD's render whichever slate the record
    was made under, so every second render below is a diff against it.
    """

    kind: str
    agent_id: PlayerId | None
    kwargs: dict[str, Any]
    recorded_prompt: str


class _CapturingRenderer:
    """Wrap a real prompt renderer, keeping every invocation's inputs.

    Returns the inner renderer's bytes unchanged, so the manager and the
    recorded-response stub see exactly the recorded prompt. The kept ``kwargs``
    are what the second render re-renders from.
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
                recorded_prompt=prompt,
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
        self._reporter_markers: dict[tuple[str, str], frozenset[str]] = {}
        self._opening_block: dict[str, frozenset[str]] = {}
        self._statement_block: dict[tuple[str, str], frozenset[str]] = {}
        self._ballot_block: dict[str, frozenset[str]] = {}

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

    def for_slate(self, set_name: str, levers: frozenset[str]) -> PromptRenderers:
        """The bundle a slate serves: only ``testimony_shapes`` re-bodies here.

        The loader reads two levers, and the Wave-2 slate holds the other one
        (``impostor_roll_call``) OFF in both modes, so the bundle is a function
        of one bit. Routing through this one accessor is what keeps the walk's
        capturing bundle and every second render on the same two objects.
        """

        return (
            self.shapes_on(set_name)
            if "testimony_shapes" in levers
            else self.off(set_name)
        )

    def reporter_markers(self, set_name: str, turn_kind: str) -> frozenset[str]:
        """The lines the REPORTER arm's own block puts on a speech prompt.

        Derived from the shipped template the way the elicitation markers are —
        one crew turn rendered with and without a ``reporter_context`` — and then
        MINUS every line a baseline BALLOT render already carries. That
        subtraction is the whole point: the Task-15.5 ballot exculpation is
        worded almost identically to this block ("Do not vote" against "Do not
        accuse"), so a marker taken from the statement render alone would report
        every body-report ballot as carrying the arm's block.

        What survives is what lets T3 be read INDEPENDENTLY of the render diff:
        the reporter arm has no ballot argument to withdraw, so a diff over the
        ballot seam is identically zero whatever the recorded bytes hold.
        """

        key = (set_name, turn_kind)
        if key not in self._reporter_markers:
            ballot_lines = frozenset(_probe_ballot(self.off(set_name)).splitlines())
            context = ReporterContext(reporter_id="p-2", tick=1)
            # BOTH reporter-owned speech surfaces. The arm renders a
            # discovery-account block on the opening and a base-rate block on
            # every other speaker's statement; either reaching the ballot is
            # the seam T3 forbids, so a marker set drawn from one surface would
            # let the other leak through reading zero.
            markers = frozenset(
                line
                for pair in (
                    (
                        _probe_crew_statement(self.off(set_name), turn_kind=turn_kind),
                        _probe_crew_statement(
                            self.off(set_name),
                            turn_kind=turn_kind,
                            reporter_context=context,
                        ),
                    ),
                    (
                        _probe_crew_opening(self.off(set_name)),
                        _probe_crew_opening(
                            self.off(set_name), reporter_context=context
                        ),
                    ),
                )
                for line in _added_lines(*pair)
                if line.strip() and line not in ballot_lines
            )
            if not markers:
                raise SystemExit(
                    f"{set_name}: every line the reporter block adds to a crew "
                    f"{turn_kind!r} turn already appears on a plain ballot, so "
                    "this reader cannot tell the arm's block apart from the "
                    "Task-15.5 exculpation the ballot renders unconditionally. "
                    "T3 would read every body-report ballot as a breach. This is "
                    "a DEFECT IN THIS SCRIPT's reader, not a finding about the "
                    "bytes"
                )
            self._reporter_markers[key] = markers
        return self._reporter_markers[key]

    def reporter_opening_markers(self, set_name: str) -> frozenset[str]:
        """R-13's block: what a crew OPENING gains from a reporter context.

        The block is ONE line whose middle clause is interpolated, so no whole
        line survives two bindings and the identification is that line's
        template-owned runs. Derived from the shipped template for the reason
        :meth:`elicitation_markers` gives — a copied sentence stops matching in
        silence and reads every opening as having lost the block.

        The line has text on BOTH sides of what it interpolates — it says who
        reported, optionally which body, and then what to do about it — and both
        sides are required. Half of it is still a sixteen-character run, so a
        reader that took any surviving run would credit an opening that names
        the report and no longer asks for the account.
        """

        if set_name not in self._opening_block:
            off = self.off(set_name)
            plain = _probe_crew_opening(off)
            first = _added_lines(
                plain, _probe_crew_opening(off, reporter_context=_REPORTER_BINDING_A)
            )
            second = _added_lines(
                plain, _probe_crew_opening(off, reporter_context=_REPORTER_BINDING_B)
            )
            held, runs = _block_markers(first, second)
            # The block is a sentence and nothing else, so its RUNS are what
            # says the sentence arrived. A wrapper it might one day grow would
            # be welcome as extra evidence and is never enough on its own.
            if not runs:
                raise SystemExit(
                    f"{set_name}: a crew OPENING gains no template-owned text "
                    "when a reporter context is supplied, so R-13 has no "
                    "discovery-account block to count. Either the block left "
                    "the template, or it now renders a different number of "
                    "lines under two bindings of its own fields — a reader that "
                    "returned 0 here would report every opening as missing the "
                    "block and STOP a correct record. This is a DEFECT IN THIS "
                    "SCRIPT's reader, not a finding about the bytes"
                )
            if not _straddles_its_interpolation(first, second):
                raise SystemExit(
                    f"{set_name}: the discovery-account block's own text now "
                    "sits on ONE side of the clause it interpolates, so half of "
                    "it has gone: the line either names the report without "
                    "asking for the account, or asks without naming it. R-13 "
                    "would credit every opening for a block that no longer asks "
                    "the reporter where they were, when they came upon the body "
                    "and what they saw on the way, and T2 would pass on it. "
                    "This is a DEFECT IN THIS SCRIPT's reader against a changed "
                    "template, not a finding about the bytes"
                )
            self._opening_block[set_name] = held | runs
        return self._opening_block[set_name]

    def reporter_statement_markers(
        self, set_name: str, turn_kind: str
    ) -> frozenset[str]:
        """R-14's block: what a non-reporter SPEECH turn gains from a context.

        A tagged frame around one interpolated sentence, and BOTH halves are
        required. The tags alone would be satisfied by a frame whose sentence
        had been deleted or guarded away — the prompt would then be credited
        with reasoning nobody was shown, and T2 would pass on it. The sentence's
        own half is the template-owned text between its two interpolations,
        which is why the probe ids agree on no character.
        """

        key = (set_name, turn_kind)
        if key not in self._statement_block:
            off = self.off(set_name)
            plain = _probe_crew_statement(off, turn_kind=turn_kind)
            held, runs = _block_markers(
                _added_lines(
                    plain,
                    _probe_crew_statement(
                        off,
                        turn_kind=turn_kind,
                        reporter_context=_STATEMENT_BINDING_A,
                    ),
                ),
                _added_lines(
                    plain,
                    _probe_crew_statement(
                        off,
                        turn_kind=turn_kind,
                        reporter_context=_STATEMENT_BINDING_B,
                    ),
                ),
            )
            if not held or not runs:
                raise SystemExit(
                    f"{set_name}: a crew {turn_kind!r} turn gains no base-rate "
                    "block this reader can identify by BOTH its frame and its "
                    "sentence, so R-14 has nothing to count. A frame with no "
                    "sentence inside it is not the block, and crediting one "
                    "would let T2 pass over prompts that carry no reasoning at "
                    "all; a reader that returned 0 instead would report every "
                    "speech turn as missing the block and STOP a correct "
                    "record. This is a DEFECT IN THIS SCRIPT's reader, not a "
                    "finding about the bytes"
                )
            self._statement_block[key] = held | runs
        return self._statement_block[key]

    def corroboration_markers(self, set_name: str) -> frozenset[str]:
        """C-9's block: what a BALLOT gains from a testimony ledger.

        Two halves, because neither reads the block on its own.

        The FRAME is what three different ledgers leave unchanged AND what still
        renders when a role-proof contradiction does. That second probe is
        load-bearing: the block's closing calibration sentence is itself guarded
        on ``not (contradiction_flags and flag_groups.proof)``, so a marker set
        that kept it would measure the proof suppression rather than the block
        and count only the ballots that carry no proof flag.

        The ROW half is the template-owned runs of the per-subject row line,
        taken across ledgers that differ in every field it interpolates. It is
        what stops an empty frame being credited: the frame renders only around
        a body, and a reader that asked for the frame alone could not say so.

        The COUNTS the block is named for cannot themselves be a marker: the
        row states them as ``N voice(s), M account(s)``, and the noun follows
        the number, so no run of template text sits on every row — requiring the
        plural form would drop every single-source row and move a published
        cell. They are checked at derivation instead, and the check is exact: a
        count is the first thing the row varies by, so two rows differing in
        THAT count alone must diverge before any text this reader identifies
        them by. Take the clause away and they first diverge at the originating
        turn instead, which puts a marker inside their shared prefix.

        Both counts are probed SEPARATELY, against partners sharing this row's
        subject and originating turn. Either clause can be deleted while the
        other still moves the divergence early, so one probe would accept a
        block that had stopped reporting half of what it promises.
        """

        if set_name not in self._ballot_block:
            off = self.off(set_name)
            plain = _probe_ballot(off)
            proofed = _probe_ballot(off, contradiction_flags=_ROLE_PROOF_FLAGS)
            one = _nonblank(
                _added_lines(
                    plain, _probe_ballot(off, testimony_ledger=_LEDGER_ONE_ACCOUNT)
                )
            )
            two = _nonblank(
                _added_lines(
                    plain, _probe_ballot(off, testimony_ledger=_LEDGER_TWO_ACCOUNTS)
                )
            )
            under_proof = _nonblank(
                _added_lines(
                    proofed,
                    _probe_ballot(
                        off,
                        testimony_ledger=_LEDGER_ONE_ACCOUNT,
                        contradiction_flags=_ROLE_PROOF_FLAGS,
                    ),
                )
            )
            none = _nonblank(
                _added_lines(
                    plain, _probe_ballot(off, testimony_ledger=_LEDGER_NO_ACCOUNT)
                )
            )
            ledger_invariant = frozenset(one) & frozenset(two)
            frame = ledger_invariant & frozenset(under_proof)
            bodies = [
                [line for line in lines if line not in ledger_invariant]
                for lines in (one, two, none)
            ]
            row_runs: frozenset[str] = frozenset()
            if all(bodies):
                row_runs = frozenset(
                    run
                    for run in _shared_runs(bodies[0][0], bodies[1][0])
                    if run in bodies[2][0]
                )
            if not frame or not row_runs:
                raise SystemExit(
                    f"{set_name}: the ballot's source-count block cannot be "
                    "identified — its unconditional frame or its row line's "
                    "template-owned text is missing, so C-9 has no block to "
                    "count. A frame-only reader would credit a block rendered "
                    "around no body, and a reader that returned 0 here would "
                    "report every ballot as missing the block and STOP a "
                    "correct record. This is a DEFECT IN THIS SCRIPT's reader, "
                    "not a finding about the bytes"
                )
            for count, partner in (
                ("first-hand accounts", _LEDGER_SAME_VOICES_TWO_ACCOUNTS),
                ("voices", _LEDGER_THREE_VOICES_ONE_ACCOUNT),
            ):
                against = _nonblank(
                    _added_lines(plain, _probe_ballot(off, testimony_ledger=partner))
                )
                rows = [line for line in against if line not in ledger_invariant]
                shared = _common_prefix(bodies[0][0], rows[0]) if rows else bodies[0][0]
                if any(run in shared for run in row_runs):
                    raise SystemExit(
                        f"{set_name}: two ledger rows differing ONLY in their "
                        f"{count} render the same text up to and past the "
                        "block's own markers, so the row no longer states how "
                        f"many {count} stand behind the name. C-9 would credit "
                        "every ballot for a source-count block that reports one "
                        "of its two counts or neither, and T6 would pass on it. "
                        "This is a DEFECT IN THIS SCRIPT's reader against a "
                        "changed template, not a finding about the bytes"
                    )
            self._ballot_block[set_name] = frame | row_runs
        return self._ballot_block[set_name]

    def block_markers(self, set_name: str, capture: _Capture) -> frozenset[str] | None:
        """The lever block this prompt class carries, or ``None`` if it has none.

        ``impostor_report`` is the ``None``: Task 21.18's overlay left that body
        untouched, so it has no reporter site, and asking this cache to derive
        one would refuse a template that is correct as shipped. The prompt stays
        in R-13's denominator and can never enter its numerator, which is how an
        impostor-filed report reads — a body-report opening that did not gain
        the block, and therefore a STOP.
        """

        if capture.kind == _KIND_CREWMATE_REPORT:
            return self.reporter_opening_markers(set_name)
        if capture.kind == _KIND_ACCUSATION_ROUND:
            return self.reporter_statement_markers(
                set_name, str(capture.kwargs.get("turn_kind"))
            )
        if capture.kind == _KIND_VOTE_BALLOT:
            return self.corroboration_markers(set_name)
        return None

    def capturing(
        self,
        sink: list[_Capture],
        *,
        levers: frozenset[str] = frozenset(),
        slate_set: str | None = None,
    ) -> dict[str, PromptRenderers]:
        """A capturing renderer bundle for every registered prompt set.

        The walk resolves each recorded meeting's set from its own stamps, so
        the mapping must cover all of them; only the set a recording actually
        used is ever invoked.

        ``slate_set`` names the ONE set whose bundle is built under ``levers`` --
        the set a lever-ON recording stamped. Every other set keeps its OFF
        bundle, because the arm's bodies exist for one set only and building the
        ON pair for a set that has none raises at construction, refusing a
        recording this walk was never asked to render. A recording that resolves
        to any other set is refused by the walk itself, so no OFF bundle here is
        ever a silent substitute for an arm's body.
        """

        bundles: dict[str, PromptRenderers] = {}
        for set_name in PROMPT_VERSION_SETS:
            inner = self.for_slate(
                set_name, levers if set_name == slate_set else frozenset()
            )
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


#: The turn kinds a speech prompt is rendered for. ``opening`` is the report
#: templates' kind and never reaches the statement renderer, so a capture
#: carrying anything else means the reader is probing a branch it has not seen.
_SPEECH_TURN_KINDS: Final[tuple[TurnKind, ...]] = ("reply", "opt_in")


def _probe_crew_opening(
    renderers: PromptRenderers, *, reporter_context: ReporterContext | None = None
) -> str:
    """One minimal CREW OPENING render, for the discovery-account block's lines.

    The reporter arm's second surface. Everything optional is left at its default
    so the render carries as little as possible beside the block being derived.
    """

    return renderers.crewmate_report(
        agent_id="p-1",
        current_tick=1,
        meeting_trigger="",
        rendered_memory="",
        public_transcript="",
        living_ids=("p-2",),
        reporter_context=reporter_context,
    )


def _probe_ballot(
    renderers: PromptRenderers,
    *,
    testimony_ledger: MeetingTestimonyLedger | None = None,
    contradiction_flags: Sequence[ContradictionRef] = (),
) -> str:
    """One minimal ballot render, WITH the unconditional reporter annotation.

    The annotation is threaded on every body-report ballot whatever the levers
    do, so a marker set that did not subtract these lines would read the Task-15.5
    exculpation as the reporter ARM's block.

    ``testimony_ledger`` and ``contradiction_flags`` are what
    :meth:`_RendererCache.corroboration_markers` varies; both default to the
    values that make this the plain ballot every other caller wants.
    """

    return renderers.vote(
        voter_id="p-1",
        rendered_memory="",
        transcript=MeetingTranscript(turns=()),
        contradiction_flags=tuple(contradiction_flags),
        suspicion_graph=(),
        candidate_targets=("p-2",),
        skip_confidence_threshold=0.5,
        reporter_id="p-2",
        testimony_ledger=testimony_ledger,
    )


def _probe_crew_statement(
    renderers: PromptRenderers,
    *,
    turn_kind: str,
    reporter_context: ReporterContext | None = None,
) -> str:
    """One minimal CREW speech render, for deriving the arm's own block.

    Everything optional is left at its default so the render carries as little
    as possible beside the block being derived, and the transcript is empty so
    no publicly spoken row can join it.
    """

    kind = next((k for k in _SPEECH_TURN_KINDS if k == turn_kind), None)
    if kind is None:
        raise SystemExit(
            f"a speech prompt was rendered for turn kind {turn_kind!r}, which "
            f"is not one of {list(_SPEECH_TURN_KINDS)}. The elicitation block is "
            "derived per turn kind, so this reader cannot probe a branch it does "
            "not know exists — falling back to another kind's block would read "
            "the wrong lines. This is a DEFECT IN THIS SCRIPT's reader"
        )
    return renderers.statement(
        agent_id="p-1",
        rendered_memory="",
        transcript=MeetingTranscript(turns=()),
        contradictions=(),
        prior_turn=None,
        turn_kind=kind,
        living_ids=("p-2",),
        reporter_context=reporter_context,
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


# --------------------------------------------------------------------------- #
# The lever blocks, identified from the shipped templates.                     #
# --------------------------------------------------------------------------- #

#: The shortest run of shared characters that can belong to a template rather
#: than to a value interpolated into it. Two player ids share ``p-``, and a
#: marker that short would match anything.
_MIN_TEMPLATE_RUN: Final[int] = 16

#: Two bindings of each reporter block's own fields, one pair per surface. A
#: marker set derived from ONE binding would carry that binding's player id and
#: stop matching the moment a different seat reported.
#:
#: The statement pair's two ids agree on no character, first or last. That is
#: what keeps a shared run from growing out of the template and into the value:
#: the block interpolates its id mid-sentence, so two ids sharing a prefix would
#: leave that prefix inside a run this reader calls template-owned. The opening
#: pair needs no such care — its two bindings diverge on whether the clause
#: renders at all, so every run there ends at the template's own punctuation.
_REPORTER_BINDING_A: Final[ReporterContext] = ReporterContext(reporter_id="p-2", tick=1)
_REPORTER_BINDING_B: Final[ReporterContext] = ReporterContext(
    reporter_id="p-7", victim_id="p-4", room="ADMIN", tick=3
)
_STATEMENT_BINDING_A: Final[ReporterContext] = ReporterContext(reporter_id="p-2")
_STATEMENT_BINDING_B: Final[ReporterContext] = ReporterContext(reporter_id="q-7")


def _support(
    *,
    subject: PlayerId,
    turn: str,
    places: tuple[tuple[PlayerId, tuple[tuple[str, str, int], ...]], ...] = (),
    silent: tuple[PlayerId, ...] = (),
    ungrounded: tuple[PlayerId, ...] = (),
    kill: tuple[PlayerId, ...] = (),
    flagged: bool = False,
    opener_charge: str | None = None,
    transits: tuple[tuple[str, str], ...] = (),
) -> TestimonySupport:
    return TestimonySupport(
        subject=subject,
        originating_turn_id=turn,
        first_hand_places=places,
        adopted_silent=silent,
        adopted_spoke_ungrounded=ungrounded,
        adopted_spoke_kill=kill,
        flagged=flagged,
        opener_charge_turn_id=opener_charge,
        walkable_transits=transits,
    )


#: Three synthetic ledgers whose ROW LINES disagree in every field the template
#: interpolates — the source counts, the originating turn, the described
#: sightings, the adoption classes and the contradiction clause. What all three
#: leave standing is the template's own text.
_LEDGER_ONE_ACCOUNT: Final[MeetingTestimonyLedger] = MeetingTestimonyLedger(
    rows=(
        _support(
            subject="p-2",
            turn="t-1",
            places=(("p-3", (("saw_move", "ADMIN", 4),)),),
            silent=("p-4",),
        ),
    ),
    opener="p-9",
)
_LEDGER_TWO_ACCOUNTS: Final[MeetingTestimonyLedger] = MeetingTestimonyLedger(
    rows=(
        _support(
            subject="p-2",
            turn="alpha:beta:9",
            places=(
                ("p-5", (("saw_vent", "CAFETERIA", 7),)),
                ("p-6", (("saw_move", "MEDBAY", 2),)),
            ),
            ungrounded=("p-8",),
            kill=("p-9",),
            flagged=True,
            opener_charge="t-3",
            transits=(("ADMIN", "MEDBAY"),),
        ),
    ),
    opener="p-2",
)
_LEDGER_NO_ACCOUNT: Final[MeetingTestimonyLedger] = MeetingTestimonyLedger(
    rows=(_support(subject="p-2", turn="zz9", silent=("p-3", "p-4"), flagged=True),),
    opener="p-9",
)

#: Two ledgers that move ONE source count each, against
#: :data:`_LEDGER_ONE_ACCOUNT`'s two voices and one account. The row states both
#: counts, and either can be deleted while the other still makes two rows
#: diverge early — so each is probed on its own, against a partner that shares
#: this row's subject and originating turn so the shared prefix really does run
#: on when the clause goes.
_LEDGER_SAME_VOICES_TWO_ACCOUNTS: Final[MeetingTestimonyLedger] = (
    MeetingTestimonyLedger(
        rows=(
            _support(
                subject="p-2",
                turn="t-1",
                places=(
                    ("p-3", (("saw_move", "ADMIN", 4),)),
                    ("p-4", (("saw_player", "MEDBAY", 6),)),
                ),
            ),
        ),
        opener="p-9",
    )
)
_LEDGER_THREE_VOICES_ONE_ACCOUNT: Final[MeetingTestimonyLedger] = (
    MeetingTestimonyLedger(
        rows=(
            _support(
                subject="p-2",
                turn="t-1",
                places=(("p-3", (("saw_move", "ADMIN", 4),)),),
                silent=("p-4", "p-5"),
            ),
        ),
        opener="p-9",
    )
)

#: One role-proof contradiction, for the probe that separates the block's
#: unconditional frame from the closing sentence the proof branch suppresses.
_ROLE_PROOF_FLAGS: Final[tuple[ContradictionRef, ...]] = (
    ContradictionRef(
        contradiction_id="c-1",
        kind="vent_sighting",
        event_a_id="o-1",
        event_b_id="o-1",
        subjects=("p-2",),
        description="a watched vent",
    ),
)

#: Which Wave-2 lever owns the block a prompt class carries. It is what decides,
#: for any leg, which of two renders is the armed one — so one reader serves a
#: lever-OFF record (the leg supplies the argument) and a lever-ON one (the leg
#: strips it).
_BLOCK_LEVER: Final[Mapping[str, str]] = MappingProxyType(
    {
        _KIND_CREWMATE_REPORT: "reporter_reasoning",
        _KIND_ACCUSATION_ROUND: "reporter_reasoning",
        _KIND_VOTE_BALLOT: "corroboration_discipline",
    }
)


def _nonblank(lines: Sequence[str]) -> list[str]:
    return [line for line in lines if line.strip()]


def _common_prefix(left: str, right: str) -> str:
    """How far two renderings of one line agree before they first differ."""

    for index, (one, other) in enumerate(zip(left, right)):
        if one != other:
            return left[:index]
    return left[: min(len(left), len(right))]


def _straddles_its_interpolation(first: Sequence[str], second: Sequence[str]) -> bool:
    """Whether a block's own text sits on BOTH sides of what it interpolates.

    Half a sentence is still a sixteen-character run, so a block that kept only
    its opening clause — or only its closing one — would still be identified by
    a non-empty marker set and credited on every prompt. The two sides are told
    apart without naming either: what two bindings share BEFORE they first
    diverge is the text ahead of the interpolation, and a run that is not part
    of that prefix is text behind it.
    """

    for one, other in zip(_nonblank(first), _nonblank(second)):
        if one == other:
            continue
        shared = _common_prefix(one, other)
        runs = _shared_runs(one, other)
        if any(run in shared for run in runs) and any(
            run not in shared for run in runs
        ):
            return True
    return False


def _shared_runs(left: str, right: str) -> tuple[str, ...]:
    """The runs two renderings of ONE line share, template-length or longer.

    The template-owned half of a line whose other half is interpolated.
    """

    matcher = difflib.SequenceMatcher(None, left, right, autojunk=False)
    return tuple(
        left[block.a : block.a + block.size]
        for block in matcher.get_matching_blocks()
        if block.size >= _MIN_TEMPLATE_RUN
    )


def _block_markers(
    first: Sequence[str], second: Sequence[str]
) -> tuple[frozenset[str], frozenset[str]]:
    """One block, split into ``(the lines that hold still, the text inside them)``.

    A line both bindings render identically is template-owned and is kept whole:
    a delimiter, or a sentence the block interpolates nothing into. A line they
    disagree on is interpolated, so what is kept is its fixed runs. The two are
    returned APART because what a block must be identified by depends on its
    shape, and no caller may settle for its wrapper alone — a frame with its
    sentence guarded away would otherwise still read as a complete gain, and the
    prompt would be credited with reasoning nobody was shown.

    Every marker must occur verbatim in the shipped template, which is what the
    reader's own test asserts: a run that straddled an interpolation boundary
    would carry a rendered value and stop matching the moment a different one
    appeared. The probe bindings are chosen so it cannot — they agree on no
    character next to an interpolation.

    BOTH halves come back empty when the block cannot be identified at all: it
    added nothing, its two bindings render different numbers of lines (this
    reader pairs them positionally, and a block it cannot pair is one it cannot
    identify), or an interpolated line holds no run long enough to be template
    text.
    """

    left, right = _nonblank(first), _nonblank(second)
    if not left or len(left) != len(right):
        return frozenset(), frozenset()
    held: set[str] = set()
    runs: set[str] = set()
    for one, other in zip(left, right):
        if one == other:
            held.add(one)
            continue
        found = _shared_runs(one, other)
        if not found:
            return frozenset(), frozenset()
        runs.update(found)
    return frozenset(held), frozenset(runs)


def _block_gain(
    *,
    capture: _Capture,
    markers: frozenset[str] | None,
    levers: frozenset[str],
    reference_levers: frozenset[str],
    rendered: str,
    reference: str,
) -> bool:
    """Whether the armed side of this pair carries the WHOLE of the block.

    A COMPLETE gain, and a gain rather than a presence: every one of the block's
    markers must occur more often in the render that carries the lever than in
    the render that does not. That is what tells the block apart from a
    whitespace-only guarded branch or an unrelated lever-conditioned line, both
    of which move bytes while putting none of the block on the page — and from a
    sentence a speaker quoted into the transcript, which stands in both renders.

    A leg and its reference on the SAME side of the block's own lever have no
    gain to read and count nothing.
    """

    if not markers:
        return False
    lever = _BLOCK_LEVER[capture.kind]
    if (lever in levers) == (lever in reference_levers):
        return False
    armed, withdrawn = (
        (rendered, reference) if lever in levers else (reference, rendered)
    )
    return all(armed.count(marker) > withdrawn.count(marker) for marker in markers)


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
    """The capture's keywords with every lever's argument set for ``levers``.

    Each of the two kwarg-toggled levers is written EXPLICITLY, ON value or OFF
    value, rather than left at whatever the capture happened to carry. That is
    what makes one function serve both directions: on a lever-OFF recording the
    OFF values are the captured ones and writing them changes no byte, while on
    a lever-ON recording they are what strips the arm back out. Every value is
    derived here from :func:`_reporter_inputs` and :func:`_ledger_for` -- this
    script's own mirror of the manager's derivation -- so a leg that carries the
    whole slate must reproduce the recorded prompt, and a disagreement is a
    mirror defect the row-level fidelity check reports rather than hides.
    """

    kwargs = dict(capture.kwargs)
    # The reporter seams are written on EVERY meeting, emergency ones included.
    # An emergency call has no reporter and arms nothing, so its ON value is the
    # same ``None`` its OFF value is -- but writing it is what makes a leak
    # visible: leaving an emergency capture's own keywords in place would render
    # a wrongly-threaded context on BOTH legs and hide it in a zero diff, and
    # "no emergency-meeting prompt gains either block" is half of T2's predicate.
    armed = "reporter_reasoning" in levers
    speaker = capture.agent_id
    context = (
        reporter.contexts.get(speaker)
        if speaker is not None and reporter.reporter_id is not None
        else None
    )
    is_reporter = reporter.reporter_id is not None and speaker == reporter.reporter_id
    if capture.kind in (_KIND_CREWMATE_REPORT, _KIND_IMPOSTOR_REPORT):
        # The opener of a body report IS its reporter, so this is the one
        # seam where the discovery account can be asked for.
        kwargs["reporter_context"] = context if armed and is_reporter else None
    elif capture.kind == _KIND_ACCUSATION_ROUND:
        kwargs["reporter_context"] = None if is_reporter or not armed else context
        kwargs["at_body"] = bool(
            armed and speaker is not None and reporter.at_body.get(speaker, False)
        )
    if capture.kind == _KIND_VOTE_BALLOT:
        kwargs["testimony_ledger"] = (
            ledger if "corroboration_discipline" in levers else None
        )
    return kwargs


# --------------------------------------------------------------------------- #
# The render diff.                                                             #
# --------------------------------------------------------------------------- #


@dataclass
class _LegTallies:
    """One slate's render census, accumulated over a whole set."""

    rendered: Counter[str] = field(default_factory=Counter)
    changed: Counter[str] = field(default_factory=Counter)
    #: The same count against the RECONSTRUCTION rather than the record, folded
    #: only when a reconstruction leg exists (the lever-ON mode). It is what
    #: gives a lever-ON row two independent readings of its own numerator: one
    #: off the recorded bytes, one off the walk's re-render of them.
    changed_vs_reconstruction: Counter[str] = field(default_factory=Counter)
    #: The same count restricted to meetings with NO reporter seat. T2's third
    #: clause is a zero over exactly this population, and the two body-report
    #: counts cannot express it: an emergency prompt is outside their
    #: denominators, so a lever that reached one would move no cell at all.
    changed_in_emergency: Counter[str] = field(default_factory=Counter)
    #: The same three counts read at BLOCK level: a prompt is counted only when
    #: the render carrying the lever carries EVERY one of the block's own marker
    #: lines and the render without it carries none of them. A byte difference is
    #: exposure; a complete block gain is the block. The two are printed side by
    #: side, and a divergence between them is a line in the output rather than a
    #: verdict.
    block_gained: Counter[str] = field(default_factory=Counter)
    block_gained_vs_reconstruction: Counter[str] = field(default_factory=Counter)
    block_gained_in_emergency: Counter[str] = field(default_factory=Counter)
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


def _on_recording_legs() -> tuple[tuple[str, frozenset[str]], ...]:
    """The slates a LEVER-ON recording renders: all three, OFF, and each dropped.

    The mirror image of :func:`_slate_legs`. The record is the all-three-ON
    render, so the second render runs BACKWARDS: the OFF leg strips the whole
    slate and each leave-one-out leg strips exactly one lever, which is how a
    row like ``R-13`` ("openings gaining the discovery-account block") is read
    off bytes that already carry the block -- the openings that LOSE it when the
    reporter argument is withdrawn are exactly the ones that gained it.

    ``all-three-ON`` is a genuine re-render here rather than the captured bytes,
    because on this side it is the FIDELITY leg: it must reproduce the recording
    prompt for prompt, and a leg that simply returned the capture could not fail.
    """

    whole = frozenset(WAVE_2_LEVERS)
    legs: list[tuple[str, frozenset[str]]] = [(_SLATE_ALL_ON, whole)]
    legs.append((_SLATE_OFF, frozenset()))
    legs.extend(
        (decomposition_label(lever), whole - {lever}) for lever in WAVE_2_LEVERS
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
            if not call.prompt.startswith(capture.recorded_prompt):
                continue
            if best is None or len(capture.recorded_prompt) > len(
                captures[best].recorded_prompt
            ):
                best = index
        if best is None:
            raise SystemExit(
                f"{meeting.set_name} {meeting.meeting_id}: a recorded LLM call "
                "matches no reconstructed render, so the render-budget fold "
                "cannot be built. This is a DEFECT IN THIS SCRIPT's attribution, "
                "not a finding about the committed bytes"
            )
        paired.append((best, call.prompt[len(captures[best].recorded_prompt) :]))
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
    recorded_label: str | None,
    recorded_levers: frozenset[str],
    elicitation_legs: tuple[str, str],
    reporter_on_ballots: list[_Capture],
) -> None:
    """Render every captured prompt once per slate and count what moved.

    ``recorded_label`` names the leg whose render IS the recorded bytes, which
    the walk already holds and never re-renders. On a lever-OFF recording that is
    the OFF leg; on a lever-ON one it is ``None``, because there the whole-slate
    leg is the fidelity check and a leg that returned the capture could not fail.

    ``recorded_levers`` is the slate the RECORD carries, which is what tells the
    block-level reader which side of each lever the recorded bytes sit on.

    ``elicitation_legs`` is the ``(without the arm, with the arm)`` pair T5's
    reader diffs — the arm is stripped on one side of the record or added on the
    other, and the block's own lines are the same either way.
    """

    living = frozenset(p.agent_id for p in meeting.participants)
    bucket = _living_bucket(len(living))
    paired = _attribute_calls(meeting, captures)
    on_prompts: dict[str, dict[int, str]] = {}
    for label, levers in legs:
        leg = tallies[label]
        rendered_for_leg: dict[int, str] = {}
        touched = False
        for index, capture in enumerate(captures):
            if label == recorded_label:
                prompt = capture.recorded_prompt
            else:
                bundle = renderers.for_slate(meeting.set_name, levers)
                prompt = _renderer_for(bundle, capture.kind)(
                    **_on_kwargs(
                        capture, levers=levers, reporter=reporter, ledger=ledger
                    )
                )
            rendered_for_leg[index] = prompt
            leg.rendered[capture.kind] += 1
            if prompt != capture.recorded_prompt:
                touched = True
                leg.changed[capture.kind] += 1
                if reporter.reporter_id is None:
                    leg.changed_in_emergency[capture.kind] += 1
                leg.added_lines[capture.kind] += prompt.count(
                    "\n"
                ) - capture.recorded_prompt.count("\n")
                # Encoded bytes, not code points: the lever blocks carry em
                # dashes and arrows, so a character count would understate what
                # the prompt actually costs.
                leg.added_bytes[capture.kind] += len(prompt.encode("utf-8")) - len(
                    capture.recorded_prompt.encode("utf-8")
                )
            if _block_gain(
                capture=capture,
                markers=renderers.block_markers(meeting.set_name, capture),
                levers=levers,
                reference_levers=recorded_levers,
                rendered=prompt,
                reference=capture.recorded_prompt,
            ):
                leg.block_gained[capture.kind] += 1
                if reporter.reporter_id is None:
                    leg.block_gained_in_emergency[capture.kind] += 1
        if touched or label == recorded_label:
            leg.meetings_touched += 1
        on_prompts[label] = rendered_for_leg
    if recorded_label is None:
        # The lever-ON side's second reading: the same counts measured against
        # the walk's own whole-slate re-render instead of the recorded bytes. A
        # row prints both, so a mirror that has drifted from the manager shows up
        # as two disagreeing columns rather than as one confident number.
        _fold_against_reconstruction(
            captures=captures,
            legs=legs,
            tallies=tallies,
            prompts=on_prompts,
            renderers=renderers,
            set_name=meeting.set_name,
        )
    first_meeting = meeting.meeting_index == 0
    for label, _levers in legs:
        leg = tallies[label]
        for index, suffix in paired:
            leg.fold_snapshot(
                on_prompts[label][index] + suffix,
                bucket=bucket,
                first_meeting=first_meeting,
            )
    reporter_markers = renderers.reporter_markers(
        meeting.set_name, str(_SPEECH_TURN_KINDS[0])
    )
    for capture in captures:
        if capture.kind != _KIND_VOTE_BALLOT:
            continue
        if _ballot_carries_a_reporter_block(
            capture,
            markers=reporter_markers,
            where=f"{meeting.set_name} {meeting.meeting_id}",
        ):
            reporter_on_ballots.append(capture)
    without, with_arm = elicitation_legs
    by_label = {
        **on_prompts,
        _RECORD_LABEL: {index: c.recorded_prompt for index, c in enumerate(captures)},
    }
    _fold_elicitation(
        meeting=meeting,
        captures=captures,
        renderers=renderers,
        off_prompts=by_label[without],
        on_prompts=by_label[with_arm],
        reconstruction_prompts=(
            on_prompts[_SLATE_ALL_ON] if recorded_label is None else None
        ),
        roles=roles,
        census=elicitation,
    )


#: The ballot template's own delimiters around the region a MODEL authors. What
#: sits between them is spoken ``free_text`` and the observations a turn carried,
#: none of it template-owned, so a marker found there says nothing about which
#: blocks the template rendered.
_BALLOT_TRANSCRIPT_OPEN: Final[str] = "<transcript>"
_BALLOT_TRANSCRIPT_CLOSE: Final[str] = "</transcript>"


def _template_owned_ballot_text(prompt: str, *, where: str) -> str:
    """One recorded ballot prompt with the model-authored transcript cut out.

    A ballot renders the meeting transcript, and a turn's ``free_text`` is
    whatever the model said. A crew agent who quoted the reporter instruction
    back at the table -- or typed the block's own opening tag -- would otherwise
    put a marker into every later ballot of that meeting without the arm reaching
    the ballot seam at all, and T3 would STOP a correct record on it. That is the
    same "a correct render read as a breach" failure §8.1 warns about for T5.

    Cut by the template's OWN delimiters rather than by counting occurrences: the
    question is which region of the page a marker sits in, and only the delimiters
    answer it exactly. A prompt missing them is refused, because a scan over a
    region this reader cannot locate is not a reading.

    The OUTER pair, because ``free_text`` is interpolated unescaped: a speaker who
    typed ``</transcript>`` would otherwise end the cut early and leave the rest
    of their own words inside the scanned text.
    """

    opened = prompt.find(_BALLOT_TRANSCRIPT_OPEN)
    closed = prompt.rfind(_BALLOT_TRANSCRIPT_CLOSE)
    if opened == -1 or closed == -1 or closed < opened:
        raise SystemExit(
            f"{where}: a recorded ballot prompt carries no "
            f"{_BALLOT_TRANSCRIPT_OPEN}/{_BALLOT_TRANSCRIPT_CLOSE} pair, so the "
            "model-authored region cannot be cut out and a reporter-block scan "
            "would read a speaker's own words as a template block. This is a "
            "DEFECT IN THIS SCRIPT's reader, not a finding about the bytes"
        )
    return prompt[:opened] + prompt[closed + len(_BALLOT_TRANSCRIPT_CLOSE) :]


def _ballot_carries_a_reporter_block(
    capture: _Capture, *, markers: frozenset[str], where: str
) -> bool:
    """Whether the BALLOT TEMPLATE put the reporter arm's block on this prompt."""

    outside = _template_owned_ballot_text(capture.recorded_prompt, where=where)
    return any(marker in outside for marker in markers)


def _fold_against_reconstruction(
    *,
    captures: Sequence[_Capture],
    legs: Sequence[tuple[str, frozenset[str]]],
    tallies: Mapping[str, _LegTallies],
    prompts: Mapping[str, Mapping[int, str]],
    renderers: _RendererCache,
    set_name: str,
) -> None:
    """Count each leg's moved prompts against the whole-slate re-render.

    Both readings, so a lever-ON row's second column is the same measurement as
    its first: the byte difference, and the complete gain of the block's own
    lines. The baseline carries the whole slate, so it is the armed side of every
    pair here.
    """

    baseline = prompts[_SLATE_ALL_ON]
    whole = frozenset(WAVE_2_LEVERS)
    for label, levers in legs:
        if label == _SLATE_ALL_ON:
            continue
        leg = tallies[label]
        for index, capture in enumerate(captures):
            if prompts[label][index] != baseline[index]:
                leg.changed_vs_reconstruction[capture.kind] += 1
            if _block_gain(
                capture=capture,
                markers=renderers.block_markers(set_name, capture),
                levers=levers,
                reference_levers=whole,
                rendered=prompts[label][index],
                reference=baseline[index],
            ):
                leg.block_gained_vs_reconstruction[capture.kind] += 1


#: The leg pair T5's reader diffs on a lever-OFF recording: the record itself
#: against the single-lever ON leg. The elicitation block is
#: ``testimony_shapes``'s alone, so that leg isolates it — and it reads the same
#: on every leg that carries the arm, because the marker is the block's own text
#: rather than a byte diff.
_ELICITATION_LEG: Final[str] = "testimony_shapes"
_ELICITATION_LEGS_OFF_RECORD: Final[tuple[str, str]] = (_SLATE_OFF, _ELICITATION_LEG)

#: The RECORD's own bytes, addressed as if they were a leg. Not a slate: the one
#: render this script never produces, only receives.
_RECORD_LABEL: Final[str] = "the recording"

#: The same pair on a lever-ON recording, where the arm is stripped rather than
#: supplied: the leave-one-out leg is the render WITHOUT the block and the
#: RECORDING itself is the render with it.
_ELICITATION_LEGS_ON_RECORD: Final[tuple[str, str]] = (
    decomposition_label("testimony_shapes"),
    _RECORD_LABEL,
)


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
    #: The same count taken against the walk's whole-slate RE-RENDER rather than
    #: against the recorded bytes. Folded only on a lever-ON recording, where the
    #: two are the row's two independent readings; empty otherwise.
    gained_from_reconstruction: Counter[str] = field(default_factory=Counter)
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
    off_prompts: Mapping[int, str],
    on_prompts: Mapping[int, str],
    reconstruction_prompts: Mapping[int, str] | None,
    roles: Mapping[PlayerId, Role],
    census: _ElicitationCensus,
) -> None:
    """Count, per speaker role, the speech prompts that gain the block.

    The pair is always ``(the render without the arm, the render with it)``, and
    which of the two the RECORDING supplied does not enter the count: the gain is
    the block's own lines appearing on one side and not the other.

    ``reconstruction_prompts`` is the second armed reading a lever-ON recording
    has and a lever-OFF one does not — the walk's own re-render of the same
    inputs, counted separately so the row can print both instead of asserting
    that they agree.
    """

    for index, capture in enumerate(captures):
        if capture.kind != _KIND_ACCUSATION_ROUND:
            continue
        role = speaker_role(
            capture, roles, where=f"{meeting.set_name} {meeting.meeting_id}"
        )
        markers = renderers.elicitation_markers(
            meeting.set_name, str(capture.kwargs.get("turn_kind"))
        )
        gained = elicitation_lines_gained(
            off_prompt=off_prompts[index],
            on_prompt=on_prompts[index],
            markers=markers,
        )
        census.rendered[role] += 1
        if gained == len(markers):
            census.gained[role] += 1
        elif gained:
            census.partial += 1
        if reconstruction_prompts is None:
            continue
        if elicitation_lines_gained(
            off_prompt=off_prompts[index],
            on_prompt=reconstruction_prompts[index],
            markers=markers,
        ) == len(markers):
            census.gained_from_reconstruction[role] += 1


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

    #: Location accounts the REAL ingest wrote into at least one listener's
    #: alibi map, per slate. Measured by running
    #: :func:`agents.memory.store.absorb_reported_testimony` over a COPY of the
    #: walk's own memories, so the own-statement, roster and tickless guards are
    #: the live ones rather than a restatement of them here.
    alibi_map_reached_off: int = 0
    alibi_map_reached_on: int = 0

    @property
    def alibi_map_off(self) -> tuple[int, int]:
        accounts = self.on_kinds["alibi"] + self.on_kinds["whereabouts"]
        return (self.alibi_map_reached_off, accounts)

    @property
    def alibi_map_on(self) -> tuple[int, int]:
        accounts = self.on_kinds["alibi"] + self.on_kinds["whereabouts"]
        return (self.alibi_map_reached_on, accounts)

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

    # BOTH sides pass an explicit env. The reduction's default is the ambient
    # process environment, and the lever-ON mode runs in a shell that exports the
    # arm on purpose -- so an unqualified call would return the ON reduction and
    # label it OFF, which is precisely the seam the committed mode's bare-shell
    # guard protects and the ON mode necessarily gives up.
    off = derive_reported_testimony(meeting.result, env={})
    on = derive_reported_testimony(meeting.result, env=_TESTIMONY_SHAPES_ENV)
    census.off_kinds.update(statement.kind for statement in off)
    census.on_kinds.update(statement.kind for statement in on)
    listeners = frozenset(ballot.voter for ballot in meeting.result.ballots)
    census.listener_slots += len(listeners)
    # The alibi-map reading uses a NARROWER set. The production fan-out runs per
    # player ALIVE AFTER the meeting (orchestrator/game.py), so the ejectee never
    # receives one, and crediting an account to a copy of their memory would
    # count a write production never performs. The published row above keeps the
    # ballot population it was measured on: this narrowing belongs to the ingest
    # cell alone.
    recipients = listeners - {meeting.result.ejected_player_id}
    census.alibi_map_reached_off += _accounts_reaching_the_map(
        meeting, statements=off, listeners=recipients
    )
    census.alibi_map_reached_on += _accounts_reaching_the_map(
        meeting, statements=on, listeners=recipients
    )
    census.off_rows += _ingest_rows(off, listeners)
    census.on_rows += _ingest_rows(on, listeners)
    spoken, fabricated, ungrounded = _vent_row_census(meeting.result, venters=venters)
    census.spoken_vent_rows += spoken
    census.fabricated_vent_rows += fabricated
    census.ungrounded_vent_rows += ungrounded


#: The statement kinds a location account can be spoken as. The widened gate the
#: ``testimony_shapes`` arm installs is ``("alibi", "whereabouts")``; with the arm
#: down the reduction emits no ``whereabouts`` at all.
_LOCATION_KINDS: Final[tuple[str, ...]] = ("alibi", "whereabouts")


def _alibi_multiset(memory: AgentMemory) -> Counter[tuple[object, ...]]:
    """Every alibi claim a belief state holds, as a MULTISET.

    A multiset and not a set: two identical accounts in one reduction, or an
    account a later meeting repeats verbatim, are separate writes. Membership
    alone would credit both when the ingest performed one.
    """

    return Counter(
        (claim.source, claim.player_id, claim.tick, claim.room)
        for player_id in memory.beliefs.known_players()
        for claim in memory.beliefs.view(player_id).alibis
    )


def _accounts_reaching_the_map(
    meeting: ReconstructedMeeting,
    *,
    statements: Sequence[ReportedStatement],
    listeners: frozenset[PlayerId],
) -> int:
    """Location accounts the REAL ingest WROTE into at least one alibi map.

    Runs :func:`agents.memory.store.absorb_reported_testimony` -- the function the
    orchestrator and the replay loader call per living agent -- over a DEEP COPY
    of each listener's own memory, and reads back what it ADDED. The copy is not
    an optimisation: these are the stores the walk's NEXT meeting renders from,
    and absorbing into them would change the bytes the reconstruction has to
    reproduce.

    Counting what the ingest WROTE rather than what the reduction OFFERED is the
    whole point. The gate's own definition says every location account reaches
    the map; the own-statement guard, the roster gate and a tickless claim can
    each stop one, and a cell derived from the offer could not see any of them.

    The reading is a BEFORE/AFTER delta, taken as a multiset and then consumed
    once per account. Reading the map's final contents instead would credit an
    account the map already held, and would credit two identical accounts to a
    single write -- either of which lets a partial ingest still read 100%.
    """

    accounts = [
        statement for statement in statements if statement.kind in _LOCATION_KINDS
    ]
    if not accounts:
        return 0
    added: Counter[tuple[object, ...]] = Counter()
    for listener in sorted(listeners):
        memory = meeting.memories.get(listener)
        if memory is None:
            continue
        probe = deepcopy(memory)
        before = _alibi_multiset(probe)
        try:
            absorb_reported_testimony(probe, statements=accounts)
        except ValueError:
            # No self_state row yet, so the ingest's own guard refuses. Nothing
            # this listener could have absorbed reached anything.
            continue
        # The per-listener delta, unioned by MAX across listeners: one account
        # written into three maps is one account that reached the map, but two
        # identical accounts must be written twice before both are credited.
        delta = _alibi_multiset(probe) - before
        for key, count in delta.items():
            added[key] = max(added[key], count)
    reached = 0
    for statement in accounts:
        key = (
            statement.speaker,
            statement.subject,
            statement.from_tick,
            statement.room if statement.room is not None else "",
        )
        if added[key] > 0:
            added[key] -= 1
            reached += 1
    return reached


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
    #: Openings a body report's own reporter spoke, through EITHER report body.
    #: T2's registered predicate is over every observed body-report opening, so
    #: this denominator is every one of them and the reader narrows it nowhere.
    #: The second count is diagnostic: ``impostor_report.j2`` carries no reporter
    #: site at all (Task 21.18's overlay left that body unchanged), so an
    #: impostor-filed report cannot gain the block and correctly takes R-13 off
    #: 100% — the count is what names WHY, instead of leaving a bare 619/620.
    #: The committed bytes hold none: the impostor policy must not file a report
    #: (agents/tactical/impostor_policy.py:53) and
    #: ``tests/eval/test_reporter_justice.py`` pins ``reporter_impostor_meetings
    #: == 0``.
    reporter_openings: int = 0
    reporter_openings_by_an_impostor: int = 0
    non_reporter_speech_turns: int = 0
    # T3, read INDEPENDENTLY of any render diff: recorded ballot prompts whose
    # bytes carry the reporter ARM's own block. The arm has no ballot argument to
    # withdraw, so a diff over that seam is identically zero and could never
    # report the breach T3 exists to catch.
    ballots_carrying_a_reporter_block: int = 0
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


def _seed_paths(sample_dir: Path) -> list[Path]:
    """The replay files of a set, in seed order.

    Built from :func:`eval.validity.seeds_on_disk` rather than from a raw glob:
    a wrapper writes a ``replay-seed-<n>.audit.jsonl`` observation sidecar beside
    each replay, and that helper is the one place that recognises the sidecar
    exactly while still refusing any other replay-shaped file. The committed sets
    carry no sidecar; a scratch recording does.
    """

    return [
        sample_dir / f"replay-seed-{seed}.jsonl" for seed in seeds_on_disk(sample_dir)
    ]


def walk_set(sample_dir: Path, *, set_name: str, withhold: str) -> _SetWalk:
    """One reconstruction pass over one committed set, every fold on the way."""

    return _walk(
        sample_dir,
        set_name=set_name,
        legs=_slate_legs(withhold),
        recorded_levers=frozenset(),
        recorded_label=_SLATE_OFF,
        elicitation_legs=_ELICITATION_LEGS_OFF_RECORD,
        slate_set=None,
    )


def walk_recording(recording_dir: Path, *, set_name: str, slate_set: str) -> _SetWalk:
    """One reconstruction pass over one LEVER-ON recording.

    The same walk, mirrored: the capturing bundle is built from the arm's own
    bodies so the manager reproduces the recorded prompts byte for byte, and
    every second render strips levers instead of supplying them.
    """

    return _walk(
        recording_dir,
        set_name=set_name,
        legs=_on_recording_legs(),
        recorded_levers=frozenset(WAVE_2_LEVERS),
        recorded_label=None,
        elicitation_legs=_ELICITATION_LEGS_ON_RECORD,
        slate_set=slate_set,
    )


def _assert_the_walk_reproduced_the_record(meeting: ReconstructedMeeting) -> None:
    """Every recorded prompt of this meeting was re-rendered byte for byte.

    The recorded-response stub keys on EXACT prompt bytes, so a render that
    misses defaults the turn and the meeting continues on invented content. On a
    lever-OFF recording the prompt-byte golden already pins this; on a lever-ON
    one nothing else does, and a bundle built for the wrong slate would miss
    every lookup and quietly produce a whole table over a defaulted transcript.

    It is also the one gate a recording whose stamps resolve to a SECOND prompt
    set trips: only the set named at capture time is given the arm's bodies, so
    a stray recording in the directory renders through bodies that carry no block
    and every one of its prompts misses here.
    """

    recorded = {call.prompt for call in meeting.entry.llm_calls}
    missed = sorted(recorded - meeting.hit_prompts)
    if missed:
        raise SystemExit(
            f"{meeting.set_name} {meeting.meeting_id}: {len(missed)} of "
            f"{len(recorded)} recorded prompts were NOT reproduced by the walk, "
            "so the recorded-response stub missed and the manager defaulted "
            f"those calls. The first one starts: {missed[0][:180]!r}. This is a "
            "DEFECT IN THIS SCRIPT's reconstruction (the wrong renderer bundle, "
            "or a shell whose levers are not the recording's), not a finding "
            "about the recorded bytes"
        )


def _walk(
    sample_dir: Path,
    *,
    set_name: str,
    legs: Sequence[tuple[str, frozenset[str]]],
    recorded_levers: frozenset[str],
    recorded_label: str | None,
    elicitation_legs: tuple[str, str],
    slate_set: str | None,
) -> _SetWalk:
    """One reconstruction pass over one replay set, every fold on the way."""

    started = time.monotonic()
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
    capturing = renderers.capturing(sink, levers=recorded_levers, slate_set=slate_set)
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
            _assert_the_walk_reproduced_the_record(meeting)
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
                walk.reporter_openings_by_an_impostor += sum(
                    1
                    for capture in captures
                    if capture.kind == _KIND_IMPOSTOR_REPORT
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
            reporter_on_ballots: list[_Capture] = []
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
                recorded_label=recorded_label,
                recorded_levers=recorded_levers,
                elicitation_legs=elicitation_legs,
                reporter_on_ballots=reporter_on_ballots,
            )
            walk.ballots_carrying_a_reporter_block += len(reporter_on_ballots)
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

    ``byte_diff`` is an INFORMATIONAL fourth column, carried only by the rows
    whose ON value is a complete BLOCK gain: the same cell counted by ANY byte
    difference, which is what those rows used to publish. It is never a verdict
    and nothing is judged against it — where the two disagree, the block-level
    count is the reading and the divergence is a line in the output.
    """

    cell_id: str
    label: str
    population: str
    note: str
    recorded_off: tuple[int, int] | None = None
    reconstructed_off: tuple[int, int] | None = None
    on: tuple[int, int] | None = None
    byte_diff: tuple[int, int] | None = None
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
            "byte_diff": list(self.byte_diff) if self.byte_diff else None,
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
            note=(
                "a RENDER cell, read as a COMPLETE gain of the block's own "
                "lines: the smoke's first ON seed can falsify it at n=1. The "
                "denominator is every observed body-report opening, an "
                "impostor-filed one included — that body carries no reporter "
                "site, so such an opening cannot gain the block and correctly "
                "takes this cell off 100%"
            ),
            reconstructed_off=_pair(0, walk.reporter_openings),
            on=_pair(
                walk.legs["reporter_reasoning"].block_gained[_KIND_CREWMATE_REPORT]
                + walk.legs["reporter_reasoning"].block_gained[_KIND_IMPOSTOR_REPORT],
                walk.reporter_openings,
            ),
            byte_diff=_pair(
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
            note=(
                "a RENDER cell, read as a COMPLETE gain of the block's own "
                "lines: per meeting and per prompt class, checkable on one seed"
            ),
            reconstructed_off=_pair(0, walk.non_reporter_speech_turns),
            on=_pair(
                walk.legs["reporter_reasoning"].block_gained[_KIND_ACCUSATION_ROUND],
                walk.non_reporter_speech_turns,
            ),
            byte_diff=_pair(
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
            note=(
                "a RENDER cell, read as a COMPLETE gain of the block's own "
                "frame and row text: falsifiable on the smoke's first ON seed"
            ),
            reconstructed_off=_pair(0, all_on.rendered[_KIND_VOTE_BALLOT]),
            on=_pair(
                walk.legs["corroboration_discipline"].block_gained[_KIND_VOTE_BALLOT],
                all_on.rendered[_KIND_VOTE_BALLOT],
            ),
            byte_diff=_pair(
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
# The same tripwires, read off a LEVER-ON recording.                           #
# --------------------------------------------------------------------------- #

#: T6's floor, quoted from the pre-registration's §8.1 predicate column. It is
#: the memo's number, not this reader's: the reader executes a ratified criterion
#: and authors none.
SOURCE_COUNT_SHARE_FLOOR: Final[float] = 0.99

_VERDICT_PASS: Final[str] = "PASS"
_VERDICT_STOP: Final[str] = "STOP"
_VERDICT_OBSERVED: Final[str] = "OBSERVED"
_VERDICT_UNREAD: Final[str] = "UNREAD (a STOP)"

#: How a row's own reading is judged against its predicate. ``zero`` and
#: ``identity`` are judgeable at any n — a one-sided count bar needs no
#: denominator, which is exactly why §8.1 says so of T1 and T5 — while ``full``
#: and ``share`` are shares and have nothing to read when their population is
#: empty.
_RULE_ZERO: Final[str] = "zero"
_RULE_FULL: Final[str] = "full"
_RULE_SHARE: Final[str] = "share"
_RULE_IDENTITY: Final[str] = "identity"
_RULE_OBSERVED: Final[str] = "observed"


@dataclass(frozen=True)
class OnRow:
    """One cell read off a LEVER-ON recording, in the mirrored three columns.

    ``recorded_on`` is the record's own bytes; ``reconstructed_on`` the walk's
    re-render of them; ``off`` the second render with the slate stripped. A row
    whose two ON readings disagree withdraws its OFF column and reads UNREAD,
    because a reconstruction that does not reproduce the record is measuring
    itself — the same rule the committed table applies to its two OFF readings.

    ``predicate`` is the pre-registration's own sample-local sentence, printed
    beside the reading so the operator reads PASS or STOP off the page rather
    than re-deriving a ratified criterion at the terminal.

    ``also_zero`` is a second, NAMED reading a compound predicate carries — T2's
    "and no emergency-meeting prompt gains either" is over a different population
    from its share, so it cannot be folded into the same fraction. It must read
    zero for the row to pass, and it is printed whether it does or not.

    ``caveat`` is what a reader must know before believing the verdict. It is set
    where the registered cell cannot fail by construction, so a PASS is not read
    as evidence the criterion was exercised.

    ``byte_diff`` is an INFORMATIONAL column, carried only by the rows whose
    reading is a complete BLOCK gain: the same cell counted by ANY byte
    difference, which is what those rows used to publish. No verdict is taken
    from it — where the two disagree, the block-level count is the reading and
    the divergence is printed as its own line.
    """

    cell_id: str
    tripwire: str
    label: str
    population: str
    predicate: str
    note: str
    rule: str = _RULE_OBSERVED
    recorded_on: tuple[int, int] | None = None
    reconstructed_on: tuple[int, int] | None = None
    off: tuple[int, int] | None = None
    byte_diff: tuple[int, int] | None = None
    also_zero: tuple[str, int] | None = None
    #: A compound predicate's ORDERING clause, as ``(name, below, above)``.
    #: Printed whether it bites or not, so the operator sees the clause was read.
    also_below: tuple[str, int, int] | None = None
    caveat: str = ""

    @property
    def agrees(self) -> bool:
        if self.recorded_on is None or self.reconstructed_on is None:
            return True
        return self.recorded_on == self.reconstructed_on

    @property
    def reading(self) -> tuple[int, int] | None:
        """The column the predicate is judged on: the record's, if it has one."""

        return (
            self.recorded_on
            if self.recorded_on is not None
            else (self.reconstructed_on)
        )

    @property
    def advisory(self) -> bool:
        return any(
            pair is not None and pair[1] <= ADVISORY_DENOMINATOR
            for pair in (self.recorded_on, self.reconstructed_on, self.off)
        )

    def verdict(self) -> str:
        """PASS, STOP, OBSERVED or UNREAD, against this row's own predicate."""

        if not self.agrees:
            return _VERDICT_UNREAD
        if self.rule == _RULE_OBSERVED:
            return _VERDICT_OBSERVED
        if self.also_zero is not None and self.also_zero[1] != 0:
            return _VERDICT_STOP
        if self.also_below is not None:
            below, above = self.also_below[1], self.also_below[2]
            # The clause reads "the OFF reconstruction is strictly below ON". An
            # OFF reading ABOVE the ON one is an inversion no slate can produce
            # and a defect in either column. An OFF reading EQUAL to it means the
            # widened gate found nothing to widen on these bytes -- a population
            # fact, and §8.1 says a population is never a trip.
            if below > above:
                return _VERDICT_STOP
        pair = self.reading
        if pair is None:
            return _VERDICT_UNREAD
        numerator, denominator = pair
        if self.rule == _RULE_ZERO:
            return _VERDICT_PASS if numerator == 0 else _VERDICT_STOP
        if self.rule == _RULE_IDENTITY:
            # An identity between the run's own two columns, so a missing OFF
            # column is not a passing one.
            if self.off is None:
                return _VERDICT_UNREAD
            return _VERDICT_PASS if pair == self.off else _VERDICT_STOP
        if denominator == 0:
            # A share over an empty population is not satisfied, it is
            # unevaluated -- and §8.1 reads a tripwire its reader cannot
            # evaluate as UNREAD, which is itself a STOP.
            return _VERDICT_UNREAD
        if self.rule == _RULE_FULL:
            return _VERDICT_PASS if numerator == denominator else _VERDICT_STOP
        if self.rule == _RULE_SHARE:
            return (
                _VERDICT_PASS
                if numerator / denominator >= SOURCE_COUNT_SHARE_FLOOR
                else _VERDICT_STOP
            )
        # A rule this method does not implement is not a rule. Falling through to
        # the nearest one would let a mistyped or newly-registered predicate exit
        # 0 under a criterion nobody wrote.
        raise SystemExit(
            f"{self.cell_id}: {self.rule!r} is not a verdict rule this reader "
            "implements, so its predicate cannot be judged at all. This is a "
            "DEFECT IN THIS SCRIPT's row table, not a finding about the bytes"
        )

    def payload(self) -> dict[str, object]:
        return {
            "cell": self.cell_id,
            "tripwire": self.tripwire,
            "label": self.label,
            "population": self.population,
            "predicate": self.predicate,
            "note": self.note,
            "advisory": self.advisory,
            "verdict": self.verdict(),
            "also_zero": list(self.also_zero) if self.also_zero is not None else None,
            "also_below": (
                list(self.also_below) if self.also_below is not None else None
            ),
            "caveat": self.caveat,
            "on_withdrawn": not self.agrees,
            "recorded_on": list(self.recorded_on) if self.recorded_on else None,
            "reconstructed_on": (
                list(self.reconstructed_on) if self.reconstructed_on else None
            ),
            "off": (list(self.off) if self.off else None) if self.agrees else None,
            "byte_diff": list(self.byte_diff) if self.byte_diff else None,
        }


def _body_report_changed(leg: _LegTallies, *kinds: str) -> int:
    """Prompts of ``kinds`` this leg moved, in a meeting that HAS a reporter.

    T2's share is over the body-report population, so an emergency prompt that
    moved is not a shortfall in it — it is the predicate's separate zero clause,
    and blending the two would let one hide the other in either direction.
    """

    return sum(leg.changed[kind] - leg.changed_in_emergency[kind] for kind in kinds)


def _body_block_gained(leg: _LegTallies, *kinds: str) -> int:
    """The same restriction over COMPLETE block gains rather than moved bytes."""

    return sum(
        leg.block_gained[kind] - leg.block_gained_in_emergency[kind] for kind in kinds
    )


def build_on_recording_rows(walk: _SetWalk) -> list[OnRow]:
    """Every §8.1 tripwire the recorded bytes can answer, plus §5's split.

    One row per registered predicate, in tripwire order, so the operator reads
    the whole ratified set off one block instead of assembling it. Nothing here
    is a bar and nothing here is new: each row is the cell the committed-record
    table already publishes, read from the other side of the slate.
    """

    census = walk.elicitation
    whole = walk.legs[_SLATE_ALL_ON]
    less_reporter = walk.legs[decomposition_label("reporter_reasoning")]
    less_corroboration = walk.legs[decomposition_label("corroboration_discipline")]
    off_leg = walk.legs[_SLATE_OFF]
    testimony = walk.testimony
    kills = walk.kill_named
    cells = walk.corroboration
    ballots = whole.rendered[_KIND_VOTE_BALLOT]
    openings = walk.reporter_openings
    speech = walk.non_reporter_speech_turns
    rows = [
        OnRow(
            cell_id="T-7",
            tripwire="T1",
            label="spoken vent accounts naming a player who never vented",
            population="statement",
            predicate="the count is 0, whatever the denominator",
            note=(
                "a NEVER-WORSE bar and a pre-record STOP. Read off the recorded "
                "transcript against the recorded action stream, so no lever "
                "enters it: an arm that mints a fabricated account shows up here "
                "as a count above zero"
            ),
            rule=_RULE_ZERO,
            reconstructed_on=_pair(
                testimony.fabricated_vent_rows, testimony.spoken_vent_rows
            ),
            off=_pair(testimony.fabricated_vent_rows, testimony.spoken_vent_rows),
        ),
        OnRow(
            cell_id="R-13",
            tripwire="T2",
            label="reporter openings gaining the discovery-account block",
            population="prompt",
            predicate=(
                "every observed body-report opening gains the block — 100% of "
                "the observed denominator"
            ),
            note=(
                "read backwards from the record: an opening GAINED the block "
                "exactly when withdrawing the reporter argument takes EVERY one "
                "of the block's own lines off the page. The denominator is "
                "every observed body-report opening, an impostor-filed one "
                "included: that body carries no reporter site, so such an "
                "opening cannot gain the block and is a STOP rather than an "
                "exclusion. The byte-diff count the cell used to publish is "
                "printed beside it, informationally"
            ),
            rule=_RULE_FULL,
            recorded_on=_pair(
                _body_block_gained(
                    less_reporter, _KIND_CREWMATE_REPORT, _KIND_IMPOSTOR_REPORT
                ),
                openings,
            ),
            reconstructed_on=_pair(
                less_reporter.block_gained_vs_reconstruction[_KIND_CREWMATE_REPORT]
                + less_reporter.block_gained_vs_reconstruction[_KIND_IMPOSTOR_REPORT]
                - less_reporter.block_gained_in_emergency[_KIND_CREWMATE_REPORT]
                - less_reporter.block_gained_in_emergency[_KIND_IMPOSTOR_REPORT],
                openings,
            ),
            off=_pair(0, openings),
            byte_diff=_pair(
                _body_report_changed(
                    less_reporter, _KIND_CREWMATE_REPORT, _KIND_IMPOSTOR_REPORT
                ),
                openings,
            ),
            also_zero=(
                "emergency openings that gained one",
                less_reporter.changed_in_emergency[_KIND_CREWMATE_REPORT]
                + less_reporter.changed_in_emergency[_KIND_IMPOSTOR_REPORT],
            ),
        ),
        OnRow(
            cell_id="R-14",
            tripwire="T2",
            label="non-reporter speech turns gaining the base-rate block",
            population="prompt",
            predicate=(
                "every observed non-reporter speech turn in a body-report "
                "meeting gains it — 100% of the observed denominator, and no "
                "emergency-meeting prompt gains either"
            ),
            note=(
                "the share's denominator is the body-report population exactly, "
                "so an emergency meeting's turns are outside it rather than "
                "counted as failures. The predicate's THIRD clause is over that "
                "excluded population and is read beside the share, because a "
                "lever that reached an emergency meeting would otherwise move no "
                "cell at all — and it stays a BYTE reading, because a zero "
                "clause about a population the lever must not touch is stricter "
                "read that way: any moved byte trips it, block or not"
            ),
            rule=_RULE_FULL,
            recorded_on=_pair(
                _body_block_gained(less_reporter, _KIND_ACCUSATION_ROUND), speech
            ),
            reconstructed_on=_pair(
                less_reporter.block_gained_vs_reconstruction[_KIND_ACCUSATION_ROUND]
                - less_reporter.block_gained_in_emergency[_KIND_ACCUSATION_ROUND],
                speech,
            ),
            off=_pair(0, speech),
            byte_diff=_pair(
                _body_report_changed(less_reporter, _KIND_ACCUSATION_ROUND), speech
            ),
            also_zero=(
                "emergency speech prompts that gained one",
                less_reporter.changed_in_emergency[_KIND_ACCUSATION_ROUND],
            ),
        ),
        OnRow(
            cell_id="R-15",
            tripwire="T3",
            label="ballots gaining a reporter block",
            population="ballot",
            predicate="the count is 0, whatever the ballot denominator",
            note=(
                "read by INDEPENDENT IDENTIFICATION, not by a render diff: the "
                "reporter arm has no ballot argument to withdraw, so a diff over "
                "that seam is identically zero whatever the ballot bytes hold. "
                "The numerator is recorded ballot prompts carrying the arm's own "
                "block, whose marker lines are derived from the shipped template "
                "and then subtracted against a plain ballot — the Task-15.5 "
                "exculpation the ballot renders unconditionally is worded almost "
                "identically and must not be read as a breach"
            ),
            rule=_RULE_ZERO,
            recorded_on=_pair(walk.ballots_carrying_a_reporter_block, ballots),
            reconstructed_on=_pair(walk.ballots_carrying_a_reporter_block, ballots),
            off=_pair(0, ballots),
        ),
        OnRow(
            cell_id="T-6",
            tripwire="T4",
            label="location accounts that reach the alibi map",
            population="statement",
            predicate=(
                "100% of observed location accounts reach the map under ON (and "
                "the OFF reconstruction of the same run is strictly below it)"
            ),
            note=(
                "an INGEST measurement, not a restatement of the offer: both "
                "columns run agents.memory.store.absorb_reported_testimony over "
                "a copy of each listener's own memory and count the accounts "
                "that landed in an alibi map, so the own-statement, roster and "
                "tickless guards are the live ones. The bolded clause is what "
                "this verdict reads; the parenthetical is printed as the OFF "
                "column beside it, because a run in which every account already "
                "reached the map under OFF had nothing for the widened gate to "
                "widen and is not a failure of it"
            ),
            rule=_RULE_FULL,
            reconstructed_on=testimony.alibi_map_on,
            off=testimony.alibi_map_off,
            also_below=(
                "the OFF ingest, which the clause requires strictly below ON",
                testimony.alibi_map_off[0],
                testimony.alibi_map_on[0],
            ),
        ),
        OnRow(
            cell_id="T-9a",
            tripwire="T5",
            label="CREW speech turns gaining the witnessed-kill elicitation block",
            population="prompt",
            predicate="every observed CREW speech turn gains the ELICITATION block",
            note=(
                "the BLOCK's own lines, derived from the shipped template — not "
                "a byte diff, which also moves for the role-blind "
                "public-transcript row a spoken kill puts in front of every "
                "later speaker"
            ),
            rule=_RULE_FULL,
            recorded_on=_pair(census.gained["CREWMATE"], census.rendered["CREWMATE"]),
            reconstructed_on=_pair(
                census.gained_from_reconstruction["CREWMATE"],
                census.rendered["CREWMATE"],
            ),
            off=_pair(0, census.rendered["CREWMATE"]),
        ),
        OnRow(
            cell_id="T-9b",
            tripwire="T5",
            label="IMPOSTOR speech turns gaining the witnessed-kill elicitation block",
            population="prompt",
            predicate=(
                "the count of IMPOSTOR speech prompts gaining an ELICITATION "
                "block is 0, whatever the denominators"
            ),
            note=(
                "a NEVER-WORSE bar and a pre-record STOP: an impostor offered "
                "the shape is a firewall question. An impostor prompt merely "
                "rendering a publicly spoken kill row is CORRECT and is excluded "
                "here by construction"
            ),
            rule=_RULE_ZERO,
            recorded_on=_pair(census.gained["IMPOSTOR"], census.rendered["IMPOSTOR"]),
            reconstructed_on=_pair(
                census.gained_from_reconstruction["IMPOSTOR"],
                census.rendered["IMPOSTOR"],
            ),
            off=_pair(0, census.rendered["IMPOSTOR"]),
        ),
        OnRow(
            cell_id="C-9",
            tripwire="T6",
            label="ballots gaining the source-count block",
            population="ballot",
            predicate=(
                f"the observed share is ≥ {SOURCE_COUNT_SHARE_FLOOR:.0%} of ballots"
            ),
            note=(
                "the residue — meetings whose ledger holds no row for any of "
                "that voter's candidate targets — is the stated explanation for "
                "the gap and is context, not a second criterion. Read as a "
                "COMPLETE gain of the block's unconditional frame AND its row "
                "text, so a ballot that renders the frame around no body is not "
                "counted; the block's closing sentence is separately guarded on "
                "the proof branch and is deliberately not a marker"
            ),
            rule=_RULE_SHARE,
            recorded_on=_pair(
                less_corroboration.block_gained[_KIND_VOTE_BALLOT], ballots
            ),
            reconstructed_on=_pair(
                less_corroboration.block_gained_vs_reconstruction[_KIND_VOTE_BALLOT],
                ballots,
            ),
            off=_pair(0, ballots),
            byte_diff=_pair(less_corroboration.changed[_KIND_VOTE_BALLOT], ballots),
        ),
        OnRow(
            cell_id="B-1m1",
            tripwire="T7",
            label="rendered memory rows per prompt snapshot, FIRST meeting only",
            population="row per snapshot",
            predicate=(
                "the meeting-1 row count is identical between the run's own OFF "
                "and ON columns"
            ),
            note=(
                "the published B-1 sums every captured meeting, where a "
                "first-meeting difference and an opposite later one cancel. "
                "RECORDED-ON is folded straight off the recorded call bytes, so "
                "the identity is read on two independent ON readings"
            ),
            rule=_RULE_IDENTITY,
            recorded_on=_pair(
                walk.recorded_first_meeting_rendered_lines,
                walk.recorded_first_meeting_snapshots,
            ),
            reconstructed_on=_pair(
                whole.first_meeting_rendered_lines, whole.first_meeting_snapshots
            ),
            off=_pair(
                off_leg.first_meeting_rendered_lines, off_leg.first_meeting_snapshots
            ),
        ),
        OnRow(
            cell_id="P-1k",
            tripwire="Q-B",
            label="non-direct convictions whose ejectee a spoken kill named",
            population="ejection",
            predicate="observed and never gated (§5)",
            note=(
                "bar 1's cell split by a spoken kill. The OFF column is BLANK by "
                "construction: whether the shape is spoken at all is a model "
                "output, so an OFF reading of it would be a prediction rather "
                "than a second render"
            ),
            reconstructed_on=_pair(kills.kill_named, kills.non_direct),
        ),
        OnRow(
            cell_id="P-1ka",
            tripwire="Q-B",
            label="of those, the ones that convicted an IMPOSTOR",
            population="ejection",
            predicate="observed and never gated (§5)",
            note=(
                "the accuracy side of the same split, so a movement in bar 1 can "
                "be attributed to the eyewitness channel rather than credited to "
                "it by assumption"
            ),
            reconstructed_on=_pair(kills.kill_named_impostor, kills.kill_named),
        ),
    ]
    rows.extend(_on_corroboration_rows(cells))
    return rows


def _on_corroboration_rows(cells: Mapping[str, int]) -> list[OnRow]:
    """The four corroboration cells, over a lever-ON run's own ledger.

    A DERIVATION over the recorded transcript rather than a render, so both
    columns read the same figure: the ledger is built the same way whatever the
    ballot then does with it. What moves between a lever-OFF record and this one
    is the transcript the ledger reads, which is a model output and is exactly
    what no offline column can predict.
    """

    shared = (
        "one of the four cells the #415/#417 records left pinned on the "
        "committed bytes; here it is re-read on the run's own"
    )
    specs = (
        (
            "C-1",
            "accused subjects with NO first-hand source",
            "accused row",
            "accused_without_a_first_hand_source",
            "rows",
        ),
        (
            "C-2",
            "ejected subjects with NO first-hand source",
            "ejection",
            "ejected_without_a_first_hand_source",
            "ejected_rows",
        ),
        (
            "C-3",
            "ejections whose charge ANSWERED the ejectee's own",
            "ejection",
            "ejected_on_an_answering_turn",
            "ejections",
        ),
        (
            "C-4",
            "ejected subjects with a map-satisfied placement pair",
            "ejection",
            "ejected_with_a_walkable_pair",
            "ejections",
        ),
    )
    return [
        OnRow(
            cell_id=cell_id,
            tripwire="§5",
            label=label,
            population=population,
            predicate="observed and never gated (§5)",
            note=shared,
            reconstructed_on=_pair(cells[numerator], cells[denominator]),
            off=_pair(cells[numerator], cells[denominator]),
        )
        for cell_id, label, population, numerator, denominator in specs
    ]


# --------------------------------------------------------------------------- #
# The guard, written before the folds.                                         #
# --------------------------------------------------------------------------- #


def _assert_live_slate(when: str, *, shell_slate: frozenset[str] = frozenset()) -> None:
    """Refuse to run once the columns this table prices cannot be produced.

    TWO environments are checked, and the second is the load-bearing one.

    The first half is the Phase-20 precedent: a lever that GRADUATED ignores the
    argument this script toggles it with, so its OFF derivation no longer exists
    in this build and the OFF column would silently be the ON column.

    The second half is the reason a passing empty-mapping check is not enough.
    Seven consumers re-derive the meeting reduction with no ``env`` argument at
    all, so a stale ``AILIBI_*`` export in the operator's shell would make every
    IMPORTED instrument's "OFF" column an ON column while the first check sailed
    through green. The refusal names the variable and says what to change.

    ``shell_slate`` is the slate the shell MUST carry, and it is the recording's
    own: a lever-OFF record demands a bare shell, and a lever-ON record demands
    exactly its stamped exports, because ``api.replay_loader`` refuses a
    cross-substrate reconstruction and the manager resolves two of the three
    levers from that same environment. Either way the rule is one rule — the
    shell equals the record — and a disagreement in EITHER direction refuses.

    That half checks EVERY live toggle, not only the priced three. The one this
    memo holds OFF is the one a stray export would damage most quietly: its arm
    swaps a template file, so it would serve a body neither priced lever's block
    reaches.
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
    wrong = [
        (key, bool(ambient.get(key, False)), key in shell_slate)
        for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
        if bool(ambient.get(key, False)) is not (key in shell_slate)
    ]
    if wrong:
        wanted = (
            "every live toggle OFF"
            if not shell_slate
            else ", ".join(sorted(shell_slate)) + " ON and every other toggle OFF"
        )
        raise SystemExit(
            f"the ambient environment is not the record's substrate {when}: the "
            f"recording needs {wanted}, but this process reads "
            + ", ".join(
                f"{key} {'ON' if live else 'OFF'} ({env_var_for_lever(key)})"
                for key, live, _ in wrong
            )
            + ". Seven consumers re-derive the meeting reduction with no env "
            "argument, so a shell that disagrees with the recording makes every "
            "imported instrument read a substrate the bytes were never made "
            "under. "
            + "; ".join(
                f"{'export' if want else 'unset'} {env_var_for_lever(key)}"
                + ("=1" if want else "")
                for key, _, want in wrong
            )
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


def read_recorded_slate(recording_dir: Path) -> dict[str, bool]:
    """The substrate a recording STAMPED, read off its own ``game_over`` rows.

    Never off the shell: the shell is what this reading is later used to judge,
    so taking the slate from it would make the check compare a value with itself.
    Every seed must stamp the same slate — a directory holding two substrates is
    two recordings, and pooling them would publish one table over bytes made
    under different rules — and an unstamped seed is refused rather than read as
    all-OFF, which is the ``read_substrate_flags`` contract.

    A stamp naming a GRADUATED lever OFF describes a substrate this build cannot
    reproduce at all, so it is refused here through the shared registry check
    rather than discovered as a wrong number downstream.
    """

    seeds = seeds_on_disk(recording_dir)
    if not seeds:
        raise SystemExit(
            f"{recording_dir}: no replay-seed-*.jsonl files found — not a "
            "recording; refusing to report a zero-game measurement"
        )
    stamps: dict[int, dict[str, bool]] = {}
    for seed in seeds:
        flags = read_substrate_flags(recording_dir / f"replay-seed-{seed}.jsonl")
        if flags is None:
            raise SystemExit(
                f"{recording_dir}: seed {seed} carries no substrate stamp, so "
                "the slate it was recorded under is UNKNOWN. An unstamped "
                "recording is not an all-OFF one, and this reader will not "
                "guess which levers its bytes were made with"
            )
        retired_off = retired_levers_stamped_off(flags)
        if retired_off:
            raise SystemExit(
                f"{recording_dir}: seed {seed} stamps the graduated lever(s) "
                + ", ".join(retired_off)
                + " OFF. Those levers have no env gate in this build, so no "
                "shell can reproduce that substrate and no column below would "
                "describe these bytes"
            )
        stamps[seed] = flags
    first = stamps[seeds[0]]
    for seed in seeds[1:]:
        if stamps[seed] != first:
            differing = sorted(
                key
                for key in set(first) | set(stamps[seed])
                if first.get(key) != stamps[seed].get(key)
            )
            raise SystemExit(
                f"{recording_dir}: seed {seeds[0]} and seed {seed} stamp "
                f"different substrates ({', '.join(differing)}). One directory "
                "is one recording; pooling two substrates would publish a table "
                "over bytes made under different rules"
            )
    return dict(first)


def _env_for_stamp(stamp: Mapping[str, bool]) -> dict[str, str]:
    """The ``AILIBI_*`` environment a recorded stamp's LIVE toggles describe.

    Feeding the stamp back through the resolvers is what lets the mandated
    comparison — :func:`orchestrator.replay.substrate_slate_mismatches`, which
    takes an environment — judge a RECORDING rather than a shell, without this
    script re-deriving the comparison itself.
    """

    return {
        env_var_for_lever(key): "1"
        for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
        if stamp.get(key, False)
    }


def assert_recording_declares(stamp: Mapping[str, bool], *, expected_on: str) -> None:
    """The recording's own stamp IS the declared slate, or refuse naming both.

    §9.2's abandon criterion, executed rather than described: the comparison is
    ``substrate_slate_mismatches`` and is never re-derived here. The only slate
    this reader accepts is the pre-registration's — the three Wave-2 keys ON with
    every other live toggle, ``impostor_roll_call`` included, OFF — because a
    second slate would be a second criterion and this instrument authors none.
    """

    if expected_on != RECORDED_SLATE_ON:
        raise SystemExit(
            f"--recorded-slate {expected_on!r} is not a slate this reader knows. "
            f"The one it reads is {RECORDED_SLATE_ON!r}: "
            + ", ".join(WAVE_2_LEVERS)
            + f" ON with {NON_WAVE_2_LEVER} OFF, which is the slate the ratified "
            "pre-registration names and 21.24 records"
        )
    problems = substrate_slate_mismatches(WAVE_2_LEVERS, env=_env_for_stamp(stamp))
    if problems:
        raise SystemExit(
            "the recording's own substrate stamp is not the declared "
            f"{RECORDED_SLATE_ON!r} slate:\n  "
            + "\n  ".join(problems)
            + "\nEvery tripwire below is registered against the Wave-2 slate, so "
            "reading these bytes as that slate would evaluate a ratified "
            "criterion over a substrate it was never written for"
        )


def assert_shell_matches_recording(stamp: Mapping[str, bool]) -> None:
    """The shell reconstructs this recording, said before the loader says it.

    ``api.replay_loader._assert_substrate_matches`` already refuses a
    cross-substrate reconstruction, and it is the mechanism that makes a
    mismatched shell a refusal rather than a wrong number. It fires deep inside a
    walk, though, and names the loader's concern; this says it first, in this
    reader's own words, before a single seed is opened. The comparison is the
    loader's own (:func:`orchestrator.replay.substrate_stamp_mismatches`) and is
    not re-derived.
    """

    mismatch = substrate_stamp_mismatches(stamp, ambient=substrate_flag_snapshot())
    if not mismatch:
        return
    lines = []
    if mismatch.differing:
        lines.append(
            "recorded the other way: "
            + ", ".join(
                f"{key} stamped {'ON' if stamp.get(key) else 'OFF'} "
                f"({env_var_for_lever(key)})"
                for key in mismatch.differing
            )
        )
    if mismatch.unknown:
        lines.append(
            "recorded by a build this one does not have: " + ", ".join(mismatch.unknown)
        )
    raise SystemExit(
        "this shell cannot reconstruct that recording — its substrate is not "
        "the recording's:\n  "
        + "\n  ".join(lines)
        + "\nRun this reader in the SAME shell the recording was made in "
        "(api/replay_loader.py refuses the reconstruction otherwise, and the "
        "manager resolves two of the three levers from that environment)"
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
            "reporter_openings": walk.reporter_openings,
            "reporter_openings_by_an_impostor": walk.reporter_openings_by_an_impostor,
            "elapsed_seconds": round(walk.elapsed, 2),
            "advisory": walk.innocent_ejections <= ADVISORY_INNOCENT_EJECTIONS,
            "rows": [row.payload() for row in rows],
            "tripwire_rows": [row.payload() for row in tripwires],
            "render_census": _render_census_payload(walk, legs=_slate_legs(withhold)),
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


def run_recording(
    recording_dirs: Sequence[Path], *, recorded_slate: str
) -> dict[str, object]:
    """Read the ratified tripwire predicates off one or more LEVER-ON recordings.

    Every refusal that can be made before a byte is walked is made first: the
    priced slate is still three keys, the build still has an OFF derivation for
    each of them, each recording's own stamp IS the declared slate, and this
    shell is the shell that recording was made in. Only then does the walk start,
    because each of those failures would otherwise surface as a wrong number
    somewhere in the middle of a table.
    """

    if not recording_dirs:
        raise SystemExit(
            "no --recording directory was given, and a verdict over zero "
            "recordings would read as a pass over nothing"
        )
    _assert_slate_is_the_three_wave_2_keys()
    stamps: dict[str, dict[str, bool]] = {}
    names: dict[str, Path] = {}
    for directory in recording_dirs:
        resolved = directory.resolve()
        name = resolved.name
        if name in names and names[name] != resolved:
            name = str(resolved)
        names[name] = resolved
        stamp = read_recorded_slate(resolved)
        assert_recording_declares(stamp, expected_on=recorded_slate)
        assert_shell_matches_recording(stamp)
        stamps[name] = stamp
    shell = frozenset(WAVE_2_LEVERS)
    _assert_live_slate("at start", shell_slate=shell)
    payload: dict[str, object] = {
        "mode": "recording",
        "levers": list(WAVE_2_LEVERS),
        "held_off": NON_WAVE_2_LEVER,
        "recorded_slate": recorded_slate,
        "slate_legs": [label for label, _ in _on_recording_legs()],
        "recordings": {name: str(path) for name, path in names.items()},
        "recorded_substrate": {name: stamp for name, stamp in stamps.items()},
    }
    per_set: dict[str, object] = {}
    pooled = _PooledOnRows()
    stopped: set[str] = set()
    for name, resolved in names.items():
        walk = walk_recording(
            resolved, set_name=name, slate_set=_arm_serving_set(resolved)
        )
        _assert_the_mirror_reproduced_the_record(walk)
        rows = build_on_recording_rows(walk)
        stopped.update(
            row.cell_id
            for row in rows
            if row.verdict() in (_VERDICT_STOP, _VERDICT_UNREAD)
        )
        per_set[name] = {
            "games": walk.games,
            "meetings": walk.meetings,
            "body_report_meetings": walk.body_report_meetings,
            "ejections": walk.ejections,
            "reporter_openings": walk.reporter_openings,
            "reporter_openings_by_an_impostor": walk.reporter_openings_by_an_impostor,
            "elapsed_seconds": round(walk.elapsed, 2),
            "rows": [row.payload() for row in rows],
            "stopped_cells": sorted(
                row.cell_id
                for row in rows
                if row.verdict() in (_VERDICT_STOP, _VERDICT_UNREAD)
            ),
            "render_census": _render_census_payload(walk, legs=_on_recording_legs()),
            "testimony_census": walk.testimony.payload(),
            "ballot_census": walk.ballots.payload(),
            "corroboration_cells": dict(sorted(walk.corroboration.items())),
        }
        for row in rows:
            pooled.add(row)
    payload["sets"] = per_set
    # The pooled block is INFORMATIONAL. Every §8.1 predicate is SAMPLE-LOCAL,
    # so a sum can pass where a member failed -- two 98/100 and 100/100 legs pool
    # to exactly T6's floor, and two opposite meeting-1 row differences cancel.
    # The verdict is therefore the union over the recordings, never the sum.
    payload["pooled"] = [row.payload() for row in pooled.rows()]
    payload["pooled_is_informational"] = True
    # The GATED predicates that did not pass, in ANY recording. An observed cell
    # can never appear here: §5's rows and the four corroboration cells are
    # reported and never judged, so listing one would invent a criterion.
    payload["stopped_cells"] = sorted(stopped)
    _assert_live_slate("at exit", shell_slate=shell)
    return payload


def _assert_the_mirror_reproduced_the_record(walk: _SetWalk) -> None:
    """This script's whole-slate re-render IS the recording, prompt for prompt.

    The walk already proves the MANAGER reproduced the recorded bytes. This is
    the other half: the script's own mirror of the manager's lever derivation
    (:func:`_reporter_inputs`, :func:`_ledger_for`, :func:`_on_kwargs`) must
    reproduce them too, because every withdrawn-lever column is a diff against
    that mirror. A row-level column comparison is not enough to catch this — a
    mirror that drifts on every reporter-affected prompt moves the two counts
    TOGETHER, so both columns agree and the row passes while the reconstruction
    reproduces nothing.
    """

    mismatches = {
        kind: count for kind, count in walk.legs[_SLATE_ALL_ON].changed.items() if count
    }
    if not mismatches:
        return
    raise SystemExit(
        f"{walk.set_name}: this script's whole-slate re-render does not "
        f"reproduce the recording — {mismatches} prompts differ by class. Every "
        "withdrawn-lever column below is a diff against that re-render, so all "
        "of them would be measuring the mirror rather than the levers. This is a "
        "DEFECT IN THIS SCRIPT's mirror of the manager's derivation, not a "
        "finding about the recorded bytes"
    )


def _arm_serving_set(recording_dir: Path) -> str:
    """The prompt set whose bodies a Wave-2 recording's stamps name.

    Recovered from the recording's own ``prompt_versions`` stamp rather than from
    the environment: the stamp is what says which bodies rendered, and the arm's
    blocks exist for one set only. Reusing the golden's reverse lookup keeps the
    walk and this pre-check on one resolution.
    """

    for seed in seeds_on_disk(recording_dir):
        for entry in read_all_entries(recording_dir / f"replay-seed-{seed}.jsonl"):
            if isinstance(entry, MeetingReplayEntry):
                return resolve_prompt_set(entry.prompt_versions)
    raise SystemExit(
        f"{recording_dir}: no recorded meeting carries a prompt_versions stamp, "
        "so which template bodies rendered these prompts is unknown. A recording "
        "with no meeting has no tripwire to read"
    )


class _PooledOnRows:
    """Lever-ON rows summed across recordings, in first-seen order.

    The recordings are disjoint games, so pooling is addition; the predicate,
    the rule and the note travel with the cell, so the pooled row is judged by
    exactly the sentence its per-recording rows were.
    """

    def __init__(self) -> None:
        self._rows: dict[str, OnRow] = {}

    def add(self, row: OnRow) -> None:
        seen = self._rows.get(row.cell_id)
        if seen is None:
            self._rows[row.cell_id] = row
            return
        self._rows[row.cell_id] = OnRow(
            cell_id=row.cell_id,
            tripwire=row.tripwire,
            label=row.label,
            population=row.population,
            predicate=row.predicate,
            note=row.note,
            rule=row.rule,
            recorded_on=_sum_pairs(seen.recorded_on, row.recorded_on),
            reconstructed_on=_sum_pairs(seen.reconstructed_on, row.reconstructed_on),
            off=_sum_pairs(seen.off, row.off),
            byte_diff=_sum_pairs(seen.byte_diff, row.byte_diff),
            # The compound clause and the caveat travel with the cell. A pooled
            # row that dropped its second zero reading would print PASS over a
            # member that STOPped on exactly that clause, and one that dropped
            # its caveat would state a construction-guaranteed value as a result.
            also_zero=_sum_also_zero(seen.also_zero, row.also_zero),
            also_below=(
                None
                if seen.also_below is None or row.also_below is None
                else (
                    row.also_below[0],
                    seen.also_below[1] + row.also_below[1],
                    seen.also_below[2] + row.also_below[2],
                )
            ),
            caveat=row.caveat or seen.caveat,
        )

    def rows(self) -> list[OnRow]:
        return list(self._rows.values())


def _sum_also_zero(
    left: tuple[str, int] | None, right: tuple[str, int] | None
) -> tuple[str, int] | None:
    """Add two named second readings, keeping ABSENT absent."""

    if left is None or right is None:
        return None
    return (right[0], left[1] + right[1])


def _sum_pairs(
    left: tuple[int, int] | None, right: tuple[int, int] | None
) -> tuple[int, int] | None:
    """Add two columns, keeping ABSENT absent rather than reading it as zero."""

    if left is None or right is None:
        return None
    return (left[0] + right[0], left[1] + right[1])


#: The columns a pooled row carries, in printing order. ``byte_diff`` is the
#: informational one and is present only on the rows that publish it.
_POOLED_COLUMNS: Final[tuple[str, ...]] = (
    "recorded_off",
    "reconstructed_off",
    "on",
    "byte_diff",
)


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
    for column in _POOLED_COLUMNS:
        if f"{key}|{column}|d" not in totals:
            columns[column] = None
            continue
        columns[column] = [totals[f"{key}|{column}|n"], totals[f"{key}|{column}|d"]]
    withheld = cell_id in withdrawn
    if withheld:
        columns["on"] = None
        columns["byte_diff"] = None
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
            ("byte_diff", row.byte_diff),
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
        pooled.alibi_map_reached_off += census.alibi_map_reached_off
        pooled.alibi_map_reached_on += census.alibi_map_reached_on
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
        byte_diff=None,
        on_slate=row.on_slate,
    )


def _class_totals(rows: Sequence[InjusticeLedgerRow]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for row in rows:
        for tag in row.tags:
            totals[tag] += 1
    totals["TOTAL"] = len(rows)
    return dict(sorted(totals.items()))


def _render_census_payload(
    walk: _SetWalk, *, legs: Sequence[tuple[str, frozenset[str]]]
) -> dict[str, object]:
    """The per-leg render census, over the legs the run actually walked.

    Keyed on the run's OWN legs rather than on the committed mode's, so a mode
    with different legs publishes all of them instead of the intersection.
    """

    labels = {label for label, _ in legs}
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
            "published them (#415 merge-reality, #417 amendment, the "
            f"counterfactual audit's Errata E.2): {disagreeing}. "
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


def _print_byte_diff(
    row: Mapping[str, object], *, reading: object, indent: str, out: TextIO
) -> None:
    """The informational byte-diff column, printed beside a block-level reading.

    Always printed where the row carries one, so the operator sees that both
    readings were taken. A DIVERGENCE is worth a line and is not a verdict:
    the block-level count is the reading, and a prompt the bytes credit without
    the block is exposure the block-level cell deliberately does not count.
    """

    byte = row.get("byte_diff")
    if byte is None:
        return
    verdict = "agrees with" if byte == reading else "DIVERGES from"
    print(
        f"{indent}byte-diff reading (informational): {_rate(byte)} — "
        f"{verdict} the block-level count above",
        file=out,
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
    _print_byte_diff(row, reading=row.get("on"), indent="       ", out=out)


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


_ON_TABLE_HEADING: Final[str] = (
    "the seven ratified tripwires (pre-registration §8.1) and §5's spoken-kill "
    "split, read off THIS recording's own bytes. No bar of the four primary "
    "bars is read here and none is declared met or missed"
)


def _print_on_row(row: Mapping[str, object], *, out: TextIO) -> None:
    mark = f" {ADVISORY_MARK}" if row.get("advisory") else ""
    print(
        f"{str(row['cell']):<6} {str(row['tripwire']):<4} "
        f"{str(row['label'])[:52]:<52} "
        f"{_rate(row.get('recorded_on')):>22} "
        f"{_rate(row.get('reconstructed_on')):>22} "
        f"{_rate(row.get('off')):>22}{mark}",
        file=out,
    )
    reading = row.get("recorded_on") or row.get("reconstructed_on")
    also = row.get("also_zero")
    beside = ""
    if isinstance(also, list):
        beside = f", {also[0]} = {also[1]}"
    ordering = row.get("also_below")
    if isinstance(ordering, list):
        beside += f", {ordering[0]} = {ordering[1]} against {ordering[2]}"
    print(
        f"       {row['tripwire']}: {row['predicate']} — READS "
        f"{_rate(reading)}{beside} → {row['verdict']}",
        file=out,
    )
    _print_byte_diff(row, reading=reading, indent="       ", out=out)
    if row.get("caveat"):
        print(f"       ⚠ {row['caveat']}", file=out)


def _print_on_table(
    payload: Mapping[str, object], *, stream: TextIO | None = None
) -> None:
    """Print the lever-ON tripwire table, verdict beside every predicate."""

    out = sys.stdout if stream is None else stream
    header = (
        f"{'cell':<6} {'trip':<4} {'label':<52} {'RECORDED-ON':>22} "
        f"{'RECONSTRUCTED-ON':>22} {'OFF':>22}"
    )
    sets = payload["sets"]
    assert isinstance(sets, dict)
    recordings = payload["recordings"]
    assert isinstance(recordings, dict)
    for name, block in sets.items():
        assert isinstance(block, dict)
        print(
            f"\n== {name} ({block['games']} games, {block['meetings']} meetings, "
            f"{block['body_report_meetings']} body reports, "
            f"{block['ejections']} ejections, {block['elapsed_seconds']}s) "
            f"— {recordings[name]}",
            file=out,
        )
        print(f"   -- {_ON_TABLE_HEADING}", file=out)
        print(header, file=out)
        for row in block["rows"]:
            _print_on_row(row, out=out)
        print(f"   testimony census: {block['testimony_census']}", file=out)
        print(f"   corroboration cells: {block['corroboration_cells']}", file=out)
        print(
            "   this recording's gated predicates that did not pass: "
            f"{block['stopped_cells'] or 'none'}",
            file=out,
        )
    print(
        "\n== POOLED — INFORMATIONAL. Every predicate is SAMPLE-LOCAL, so the "
        "verdict below is the union over the recordings and never this sum",
        file=out,
    )
    print(header, file=out)
    pooled = payload["pooled"]
    assert isinstance(pooled, list)
    for row in pooled:
        _print_on_row(row, out=out)
    stopped = payload["stopped_cells"]
    assert isinstance(stopped, list)
    print(
        "\nverdict: every GATED predicate PASSES on these bytes"
        if not stopped
        else "\nverdict: a gated predicate did NOT pass — "
        + ", ".join(str(cell) for cell in stopped)
        + " (this command exits non-zero)",
        file=out,
    )
    _print_on_reading_rules(payload, out=out)


def _print_on_reading_rules(payload: Mapping[str, object], *, out: TextIO) -> None:
    """What the operator must know before acting on the block above."""

    print("\nreading rules:", file=out)
    for line in (
        "A row marked ⚠ CANNOT FAIL on this reader: its registered cell is a "
        "derivation whose value follows from its own inputs, so its PASS is not "
        "evidence the criterion was exercised. §8.1 registers those cells and "
        "this instrument does not redefine a published one.",
        "The PREDICATE is the ratified criterion and the population is not. A "
        "denominator smaller than baseline 8's is expected at a smoke and is "
        "never a trip; stopping a correct record because its own behaviour "
        "changed a denominator is the opposite of what these tripwires are for.",
        "RECORDED-ON is the recording's own bytes and RECONSTRUCTED-ON is this "
        "walk's re-render of them. A row whose two ON readings disagree prints "
        "no OFF column and reads UNREAD — and §8.1 reads UNREAD as a STOP.",
        "OFF is a SECOND RENDER of the recorded inputs with the lever arguments "
        "withdrawn. It says what the slate put in front of a reader, never what "
        "the reader would then have done: a sentence removed from a prompt is "
        "not a vote that changes.",
        "R-13, R-14 and C-9 count a COMPLETE gain of the block's own lines, "
        "derived from the shipped template at runtime — not a byte difference, "
        "which a whitespace-only guarded branch or an unrelated "
        "lever-conditioned line also moves. The byte-diff count each cell used "
        "to publish is printed beside it and is informational: no verdict is "
        "taken from it. R-14's and R-13's emergency clause stays a BYTE "
        "reading, because a zero clause over a population the lever must not "
        "touch is stricter that way.",
        "A share predicate over an EMPTY population reads UNREAD rather than "
        "PASS. A one-sided count bar (T1, T3, T5's impostor half) needs no "
        "denominator and is judged at any n, which is why §8.1 states it as a "
        "count.",
        f"{ADVISORY_MARK} marks a row one case would dominate — any column whose "
        f"denominator is {ADVISORY_DENOMINATOR} or fewer.",
        f"The slate is the THREE Wave-2 levers with {payload['held_off']} OFF, "
        "read off the recording's own game_over stamp and compared through "
        "orchestrator.replay.substrate_slate_mismatches, never re-derived.",
        "This block writes no bar, no target and no decision rule: the "
        "pre-registration owns all four, and none of the seven tripwires is a "
        "graduating bar.",
    ):
        print(f"  {line}", file=out)


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
        "R-13, R-14 and C-9 count a COMPLETE gain of the block's own lines, "
        "derived from the shipped template at runtime — not a byte difference, "
        "which a whitespace-only guarded branch or an unrelated "
        "lever-conditioned line also moves. The byte-diff count each cell used "
        "to publish is printed beside it and is informational: no verdict is "
        "taken from it, and a divergence between the two is a line rather than "
        "a finding.",
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
        "--recording",
        type=Path,
        action="append",
        default=None,
        help=(
            "a directory of replay-seed-*.jsonl recorded with the lever slate "
            "UP, inside or outside replays/ — 21.23's smoke and 21.24's record "
            "write one. Repeat the flag to pool several legs. Requires "
            "--recorded-slate, and a shell carrying the recording's own "
            "AILIBI_* exports"
        ),
    )
    parser.add_argument(
        "--recorded-slate",
        default=None,
        choices=[RECORDED_SLATE_ON],
        help=(
            "the slate the --recording directories were recorded under, "
            "DECLARED by the operator and checked against each recording's own "
            f"game_over stamp. {RECORDED_SLATE_ON!r} is the ratified Wave-2 "
            "slate: " + ", ".join(WAVE_2_LEVERS) + f" ON with {NON_WAVE_2_LEVER} "
            "OFF"
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
    started = time.monotonic()
    if args.recording:
        if args.recorded_slate is None:
            parser.error(
                "--recording needs --recorded-slate: the slate a recording was "
                "made under is DECLARED and then checked against its own stamp, "
                "so an undeclared recording is refused rather than guessed at"
            )
        payload = run_recording(
            [Path(directory) for directory in args.recording],
            recorded_slate=str(args.recorded_slate),
        )
        printer = _print_on_table
    else:
        if args.recorded_slate is not None:
            parser.error(
                "--recorded-slate describes a --recording; the committed sets "
                "were recorded with every lever OFF and --sets reads them as such"
            )
        set_names = (
            list(CANONICAL_SETS) if args.sets == "all" else [str(args.sets).strip("/")]
        )
        payload = run(set_names, withhold=str(args.withhold))
        printer = _print_table
    elapsed = time.monotonic() - started
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        printer(payload)
        print(f"\nwall time: {elapsed:.1f}s", file=sys.stdout)
    # A tripwire that did not pass is a PRE-RECORD STOP, so the process status
    # has to say so: the smoke drives this from a shell script, and a table that
    # printed STOP while exiting 0 would let `set -e` carry straight on into a
    # 22-hour record. The committed-record mode carries no verdicts and always
    # exits 0.
    stopped = payload.get("stopped_cells")
    return 1 if isinstance(stopped, list) and stopped else 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
