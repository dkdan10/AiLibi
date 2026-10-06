"""The gameplay census: a count of what happens in the games themselves.

A second committed report beside the nine-row process scorecard
(:mod:`eval.process_scorecard`), and deliberately separate from it. The
scorecard asks whether each decision rested on data the agent held; this census
counts what the game put in front of the agents: who saw a kill or a vent, what
lay on the floor when a meeting opened, the state play resumed in, the order in
which the meeting spoke, and how the impostors voted. No cell here joins the
scorecard, and nothing here gates anything. Role-correctness is reported beside
the counts and feeds nothing back to any agent.

Count-only, with zero model calls
---------------------------------
:func:`load_census_inputs` walks one replay set through the engine and keeps
ids, rooms, ticks, kinds, labels, recorded dispositions, plain recorded setting
values and booleans it computes itself. A recorded prompt is read inside the
loader only to compute such a boolean, an id or a place name (the kill-tick body
handle in an opening; a served own-kill ballot row; whether a prompt after a
regroup carries every earlier regroup's notice; the places a holds-nothing
SKIP's own ballot prompt names a living candidate), and no prompt, speech or
rationale text leaves it. :func:`fold_set` is a pure fold over that carrier, so every cell is
plantable from a hand-built :class:`CensusInputs` with no replay on disk, and
:func:`pool` adds counts and recomputes each rate from the pooled numerator and
denominator.

The walk profile
----------------
``gameplay-census`` is the current-report profile with three more checks:
a MEETING tick with no meeting row is a violation rather than a truncation, a
doubled meeting row is refused, and a walk that never reaches its terminal tick
is refused. It therefore verifies tick hashes, action dispositions, meeting
post-hashes and chronology, and accepts recordings that carry experiment
settings or temporal delivery. The profile's row belongs to the drift table in
:mod:`eval.replay_walk`, which this module does not edit; it is documented here.

Recorded settings reach the walk by the arm spine's contract. Engine-layer
settings go to the seeding, every advance and every applied meeting through
:func:`orchestrator.experiment_config.engine_arguments`, which refuses, before
the first advance, one it does not thread. The profile declares its own
``threaded_layers`` rather than inheriting the current-report profile's:
:data:`CENSUS_THREADED_LAYERS` is orchestrator, tactical and meeting, every
layer a profile can declare, because the census classifies every field in them.
A profile without one of them refuses that layer's Stage-B settings before its
first advance, and a setting the census has not classified raises
:class:`GameplayCensusFieldError`.

Settings, eras and the cells a setting forces to zero
-----------------------------------------------------
Every field of :class:`orchestrator.experiment_config.RecordedExperimentConfig`
is classified in :data:`FIELD_CLASSIFICATION` as read by a named setting
predicate, read as a value, or deliberately not read, and a recording or carrier
naming a field outside that table raises. The one field read as a value is the
recorded kill cooldown: it sets the grace window's length and the value the
kill cooldown cell checks every engine write of a cooldown against. The predicates (:class:`SettingPredicate`) read the
carrier's plain recorded values, where a missing key means the historical
default; they never build a ``RecordedExperimentConfig``.

Each game carries an :class:`EraKey`: its settings, its temporal-observation
version, its substrate-flag stamp and its prompt stamps, the last taken only
from MANIFEST rows of games that recorded a meeting. A set whose games carry two
eras raises, and :func:`pool` raises across eras. The committed sets are grouped
by the era registry (:mod:`eval.eras`); each era is published with its own named
windows, a pool exists only inside one era, and :func:`verify_era_registry`
holds the registry to the keys the recordings fold to.

A cell that a recorded setting makes zero by construction carries that
setting's predicate. While the predicate holds, the fold raises
:class:`GameplayCensusConformanceError` naming the set, seed and meeting (or
tick) of the first breach, and the page renders the zero as "0 by construction"
naming the setting, never as a measured improvement. An empty denominator is
``n/a``, never 0.

Some cells count what a setting's own mechanism did among things every era has:
the vent trips a regroup ended, the vent exits the in-vent cap forced. Some
tables have rows only that mechanism makes: the events a regroup drops, who
received a rebuttal. Each such cell or table carries the setting's predicate as
its scope (:attr:`CellSpec.scope`, :attr:`TableSpec.scope`). It is counted only
in games whose recorded settings satisfy the scope; in every other era it counts
nothing and reads ``n/a``, never a measured 0. A cell whose denominator is itself
made only by a setting's mechanism (regroup meetings, rebuttal turns) has no
scope. On a walked recording that denominator is empty in every other era: the
loader marks a meeting regrouped only under the recorded regroup reset, and at
the historical rebuttal setting the fold raises on any rebuttal.

What a ballot held, and the shape of a game
-------------------------------------------
Two checks read a ballot against data, never against a role. The holds-nothing
check reads a SKIP labelled ``none_held`` against its voter's own recorded
ballot prompt: whether an observation row, an open contradiction, an evidence
row or a typed or spoken turn line names a living candidate, by whole token.
The blocks and memory sections it reads and skips are classified tables pinned
to the templates and the memory renderer, and an unclassified one raises. The
cited-line check reads every placement of a supported EJECT's target in its
cited turn against the honesty instrument's route, each kind at that
instrument's own clock (:data:`PLACEMENT_WINDOWS`), through its own comparison,
and an edge row shows the placements a clock one tick earlier would turn true.
The game-shape tables describe each game's ending, kill cadence, closeness at
game over, sabotages, body finders and pairs of players, all role-blind. None of
these is a gate, and none feeds back to an agent: a line held is not a reason to
vote, and a true cited line is not a correct vote.

The recorded tally
------------------
Every meeting's recorded ballots are re-tallied by the game's own function,
:func:`meetings.voting.tally_ballots`, at the meeting's recorded confidence
floor. The tally of the ballots as recorded must reproduce the recorded outcome;
a meeting where it does not raises :class:`GameplayCensusConformanceError`
naming the set, seed and meeting. Two re-tallies then read every impostor
ballot as SKIP, or remove it, holding every other ballot fixed; they count which
recorded ejections would not stand. Real voters would have heard different
speech, so a re-tally describes the ballots, never what the table would have
done. The re-tallies read the voter's role only to pick the ballots they change.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal, TypeAlias, get_args

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from agents.tactical.crewmate_policy import EMERGENCY_COOLDOWN_TICKS
from engine.entities import PlayerId, Role, RoomId
from engine.events import (
    KilledEvent,
    MovedEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.win_conditions import WinResultType
from engine.world import Map, WorldState, load_canonical_map, resolve_kill_cooldown
from eval.balance_eval import _CURRENT_REPORT_WALK_CONFIG
from eval.eras import COMMITTED_SETS as REGISTERED_SETS
from eval.eras import CommittedSet, era_groups
from eval.evidence_honesty import _contradicts
from eval.process_scorecard import AGENT_CLOCK_OFFSET
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    ReplayWalkConfig,
    TickAdvanced,
    TickOpened,
    WalkComplete,
    walk_replay,
)
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from meetings.rebuttal import select_bounded_rebuttal
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    BallotGroundingLabel,
    MeetingOutcome,
    MeetingTranscript,
    MeetingTurn,
    SawMoveObservation,
    SawPlayerObservation,
    TaskActivityAccount,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import canonical_rooms
from meetings.voting import SKIP_TARGET, tally_ballots
from orchestrator.experiment_config import ConfigLayer, RecordedExperimentConfig
from orchestrator.replay import (
    GameEndReplayEntry,
    GameStopReason,
    LLMCallRecord,
    MeetingReplayEntry,
    ReplayLogEntry,
    WinnerSide,
    read_all_entries,
    recorded_experiment_config,
    recorded_substrate_flags,
    recorded_temporal_observation_version,
)
from orchestrator.replay_integrity import resolve_ballot_tally_threshold

#: Bumped only when the published JSON changes shape in a way an older reader
#: cannot interpret. Version 1 is the first publication; version 2 groups the
#: sets by recorded era (the promotion of candidate round 2, 2026-10-02).
SCHEMA_VERSION: Final[int] = 2

#: A plain recorded setting value, as the recording serializes it.
SettingValue: TypeAlias = str | int | bool | None

#: What opened a meeting, as the engine's trigger event names it.
TriggerKind: TypeAlias = Literal["report", "emergency"]

#: The phase a meeting's result leaves the game in, as the engine's state names it.
Phase: TypeAlias = Literal["PLAY", "MEETING", "GAME_OVER"]

#: The engine step that set an impostor's kill cooldown: the seeding at round
#: start, a kill (the killer's own cooldown), or the regroup at a meeting's close.
CooldownWriter: TypeAlias = Literal["round_start", "after_kill", "regroup"]

#: The ``type`` of every observation shape the meeting schema accepts.
ObservationKind: TypeAlias = Literal[
    "completed_task",
    "found_body",
    "saw_kill",
    "saw_move",
    "saw_player",
    "saw_vent",
    "task_activity",
    "whereabouts",
]

#: The frozen meaning of ``vent_entry_policy = "own_fresh_kill"``: an entry is
#: conforming only when the impostor's own victim lies in that room, killed at
#: most this many ticks before the entry, with no meeting between. Once a round
#: records this value its meaning never changes; a revision adds a new value.
FRESH_KILL_WINDOW_TICKS: Final[int] = 3

#: The frozen meaning of ``vent_exit_policy = "look_and_wait"``: the most play
#: ticks an impostor stays inside a vent, the count restarting at a meeting
#: boundary. At this count it must surface; before it, it surfaces only when no
#: non-teammate stands in a room it infers it can see.
IN_VENT_CAP_TICKS: Final[int] = 4

#: The window of the reported "post-meeting kills" and "kills soon after a
#: surfacing" cells. Reported only; no setting reads it.
SHORT_WINDOW_TICKS: Final[int] = 2

#: The emergency-button cooldown the crew policy observes after a meeting, read
#: from the policy itself so the regroup button cell cannot drift from it.
BUTTON_COOLDOWN_TICKS: Final[int] = EMERGENCY_COOLDOWN_TICKS

#: The exact description of the served own-kill ballot row. The ballot card pins
#: its row text to this constant; a served row in any other wording is not found,
#: so a wording mismatch reads ``n/a`` on the row cells, never 0.
OWN_KILL_ROW_TEXT: Final[str] = "you watched them KILL in {room} at tick {tick}"

#: The kill-tick body handle, ``body-p-<victim>-<death tick>``. The same pattern
#: as ``experiments.held_out_prefixes.LEGACY_BODY_HANDLE_PATTERN``; this module
#: does not import the held-out generator, and a test pins the two equal.
KILL_TICK_BODY_HANDLE_PATTERN: Final[re.Pattern[str]] = re.compile(r"body-p-\d+-\d+")

#: A seed band no census walk may read. The loader refuses such a seed before it
#: opens the file.
UNSEEN_SEED_BAND: Final[range] = range(2100, 3000)

#: One served evidence row, as the ballot template renders it: a bullet naming
#: the subject, the row's description, then a parenthetical that ends with the
#: citation or with the note that nothing is citable.
_OWN_KILL_ROW_RE: Final[re.Pattern[str]] = re.compile(
    r"^- `(?P<subject>p-\d+)` \S+ "
    + re.escape(OWN_KILL_ROW_TEXT)
    .replace(r"\{room\}", r"(?P<room>[A-Z][A-Z0-9_]*)")
    .replace(r"\{tick\}", r"(?P<tick>\d+)")
    + r" \((?:[^`\n]*?cite `(?P<citation>[^`\n]+)`)?[^\n]*\)$",
    re.MULTILINE,
)

#: An episodic observation id, ``{agent}:{tick}:{seq}`` in the agent's frame.
_OBSERVATION_ID_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<agent>p-\d+):(?P<tick>\d+):(?P<seq>\d+)$"
)

#: The observation kinds that name a player seen: the meeting schema's
#: observation shapes that carry a ``subject``, whoever it names.
_SIGHTING_KINDS: Final[frozenset[str]] = frozenset(
    {"saw_player", "saw_vent", "saw_kill", "saw_move"}
)

#: The role of an answered turn's speaker, as a rebuttal-beneficiaries row names
#: it. A speaker without a recorded role, or with a role this table lacks, raises.
_ROLE_WITH_ARTICLE: Final[Mapping[Role, str]] = MappingProxyType(
    {"CREWMATE": "a crewmate", "IMPOSTOR": "an impostor"}
)

#: The trigger-tick event kinds a regroup drops from the resume perception.
_REGROUP_DROPPED_KINDS: Final[tuple[str, ...]] = (
    "Moved",
    "TaskProgressed",
    "TaskCompleted",
)

#: The public regroup's notice, in the wording the memory's meetings block
#: renders from the regroup's tick and room. A test pins it equal to the
#: renderer's own wording; the loader looks for it in this wording only.
REGROUP_NOTICE_TEXT: Final[str] = (
    "Public regroup at the start of tick {tick}: living players were placed in "
    "{room}; this was not a walking journey."
)

#: The grounding label of a ballot whose voter said outright that it held
#: nothing that resolves the vote. The type checker holds it to the meeting
#: layer's label vocabulary.
HOLDS_NOTHING_LABEL: Final[BallotGroundingLabel] = "none_held"

#: The row of a ballot recorded before the meeting layer labelled ballots.
UNLABELLED: Final[str] = "unlabelled"

#: Where a holds-nothing SKIP's own ballot prompt can name a living candidate:
#: the places the holds-nothing check reads, each a row of its table.
HeldSource: TypeAlias = Literal[
    "an observation row",
    "an observation row perceived since the previous meeting",
    "an evidence row",
    "a flag",
    "a typed turn line",
    "a spoken turn line",
]

#: The ballot prompt's top-level blocks the holds-nothing check reads.
#: ``tests/eval/test_gameplay_census.py`` pins these and
#: :data:`UNREAD_BALLOT_BLOCKS` to every top-level tag the ``vote_ballot*.j2``
#: templates render, and the loader raises on a recorded prompt carrying a tag
#: in neither.
READ_BALLOT_BLOCKS: Final[frozenset[str]] = frozenset(
    {"memory", "transcript", "contradictions", "evidence"}
)

#: The ballot prompt's top-level blocks the check never reads: they name the
#: voter, list every candidate, or state who backed whom.
UNREAD_BALLOT_BLOCKS: Final[frozenset[str]] = frozenset(
    {"persona", "voice", "testimony_sources", "map", "output_format"}
)

#: The rendered memory's sections, by the text before a heading's first colon,
#: with the place each one is read as, or ``None`` for a section the check
#: never reads (the beliefs section names every living player). A test pins the
#: keys to every heading :mod:`agents.memory.store` can render, and the loader
#: raises on a heading in no row.
MEMORY_SECTIONS: Final[Mapping[str, HeldSource | None]] = MappingProxyType(
    {
        "## Your role": None,
        "## Tasks completed (global)": None,
        "## Meetings so far": None,
        "## Where you were": None,
        "## Recent observations (most salient first)": "an observation row",
        "## Your current beliefs": None,
        "## Open contradictions": "a flag",
    }
)

#: A top-level block's opening or closing tag, alone on its line.
_BLOCK_TAG_RE: Final[re.Pattern[str]] = re.compile(r"^<(/?)([a-z_]+)>$")

#: A transcript turn's header line: its id, index, kind and speaker.
_TURN_HEADER_RE: Final[re.Pattern[str]] = re.compile(r"^- \[[^\]\n]+\] turn \d+ \(")

#: A player id standing as a whole token: never inside a longer id
#: (``p-1`` in ``p-10``) or a body handle (``body-p-5-12``).
_PLAYER_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"(?<![\w-])p-\d+(?!\w)")

#: An observation row's id tag, ``[obs {agent}:{tick}:{seq}]``.
_OBSERVATION_TAG_RE: Final[re.Pattern[str]] = re.compile(
    r"\[obs p-\d+:(?P<tick>\d+):\d+\]"
)

#: The spoken placements whose truth the cited-line check reads.
CheckedPlacementKind: TypeAlias = Literal[
    "saw_player", "company", "saw_move", "whereabouts"
]

#: Which engine frame a clock reads: ``settled`` is the state after a tick's
#: actions, a meeting's tick read from its applied state; ``resolved`` is the
#: state after the tick's actions before any meeting applied.
RouteFrame: TypeAlias = Literal["settled", "resolved"]

#: Each placement kind's clock: the frames, and how many ticks before the
#: spoken tick, its truth is read at. These are the honesty instrument's two
#: clocks (:mod:`eval.evidence_honesty`): a whereabouts claim for tick N at N and
#: N-1, I-2's window; a sighting stamped at agent tick T at T-1, settled for a
#: state-read sighting or resolved for an action-stamped one, and at T-2 for an
#: action-stamped one, the window its clock alignment holds every recorded
#: sighting to. A spoken sighting does not say which of the two it was.
PLACEMENT_WINDOWS: Final[
    Mapping[CheckedPlacementKind, tuple[tuple[RouteFrame, int], ...]]
] = MappingProxyType(
    {
        "whereabouts": (("settled", 0), ("settled", 1)),
        "saw_player": (("settled", 1), ("resolved", 1), ("settled", 2)),
        "company": (("settled", 1), ("resolved", 1), ("settled", 2)),
        "saw_move": (("settled", 1), ("resolved", 1), ("settled", 2)),
    }
)

#: What the route makes of one cited placement.
PlacementVerdict: TypeAlias = Literal["true", "false", "unverifiable"]

#: The edge row of the cited placements table: false in its kind's window and
#: true on the settled frame one tick before the window's earliest tick.
EDGE_VERDICT: Final[str] = "false, but true one tick before its window"

#: Why a supported EJECT's cited line could not be checked, each a row.
NOT_CHECKABLE_REASONS: Final[tuple[str, str, str]] = (
    "it cites no turn, only the voter's own observation",
    "the cited turn places the target nowhere checkable",
    "every cited placement is unverifiable",
)

#: The ending a task win records; the type checker holds it to the engine's
#: vocabulary.
TASK_WIN: Final[WinResultType] = "CREWMATE_TASKS"

#: Tick-gap buckets: each label with the most ticks it holds, in order; a gap
#: past the last lands in :data:`LONG_GAP`.
TICK_GAP_BUCKETS: Final[tuple[tuple[str, int], ...]] = (
    ("the same tick", 0),
    ("1 to 2 ticks", 2),
    ("3 to 5 ticks", 5),
    ("6 to 10 ticks", 10),
    ("11 to 20 ticks", 20),
)
LONG_GAP: Final[str] = "more than 20 ticks"

#: The kill-to-report row of a kill whose body no meeting reported.
NEVER_REPORTED: Final[str] = "its body never reported"

#: Share buckets: each label with the largest share it holds, as a numerator
#: over :data:`SHARE_QUARTERS`, in order.
SHARE_QUARTERS: Final[int] = 4
SHARE_BUCKETS: Final[tuple[tuple[str, int], ...]] = (
    ("none", 0),
    ("up to a quarter", 1),
    ("up to a half", 2),
    ("up to three quarters", 3),
    ("more than three quarters", 4),
)

#: Who opened a report meeting: a witness of some kill since the previous
#: meeting (or the game's start), or any other player.
_OPENER_WITNESS: Final[str] = "opened by a witness of a kill since the last meeting"
_OPENER_OTHER: Final[str] = "opened by another player"

#: How many living crew witnesses a held kill had at the next meeting.
_WITNESS_BANDS: Final[tuple[str, str]] = (
    "one living crew witness",
    "two or more living crew witnesses",
)

#: What the meeting after a held kill did, from the killer's side first.
_NEXT_MEETING_OUTCOMES: Final[tuple[str, str, str, str]] = (
    "the killer ejected",
    "a witness ejected",
    "another player ejected",
    "no one ejected",
)

#: Every row of the held-kill outcome table: a witness band crossed with the
#: next meeting's outcome. Each held crew-witnessed kill lands in exactly one.
WITNESS_OUTCOME_ROWS: Final[tuple[str, ...]] = tuple(
    f"{band}: {outcome}"
    for band in _WITNESS_BANDS
    for outcome in _NEXT_MEETING_OUTCOMES
)

#: The tally of the ballots as recorded, which must reproduce the outcome.
AS_RECORDED: Final[str] = "as recorded"

#: The two re-tallies, each named by what it does to an impostor's ballot;
#: every other ballot is held fixed.
IMPOSTOR_BALLOTS_AS_SKIP: Final[str] = "impostor ballots as SKIP"
IMPOSTOR_BALLOTS_REMOVED: Final[str] = "impostor ballots removed"
RETALLY_VARIANTS: Final[tuple[str, str]] = (
    IMPOSTOR_BALLOTS_AS_SKIP,
    IMPOSTOR_BALLOTS_REMOVED,
)

#: The cell each re-tally's undone ejections are counted in.
_UNDONE_CELLS: Final[Mapping[str, str]] = MappingProxyType(
    {
        IMPOSTOR_BALLOTS_AS_SKIP: "ejections_undone_with_impostor_ballots_as_skip",
        IMPOSTOR_BALLOTS_REMOVED: "ejections_undone_with_impostor_ballots_removed",
    }
)

#: The seat classes at a report meeting, reporter first whatever its role, and
#: the cells each reads: in total, without vent proof, and with it.
_REPORTER_SEAT: Final[str] = "reporter"
_OTHER_CREWMATE_SEAT: Final[str] = "other crewmate"
_IMPOSTOR_SEAT: Final[str] = "impostor"
_SEAT_CELLS: Final[Mapping[str, tuple[str, str, str]]] = MappingProxyType(
    {
        _REPORTER_SEAT: (
            "reporter_seats_ejected",
            "reporter_seats_ejected_without_vent_proof",
            "reporter_seats_ejected_with_vent_proof",
        ),
        _OTHER_CREWMATE_SEAT: (
            "other_crewmate_seats_ejected",
            "other_crewmate_seats_ejected_without_vent_proof",
            "other_crewmate_seats_ejected_with_vent_proof",
        ),
        _IMPOSTOR_SEAT: (
            "impostor_seats_ejected",
            "impostor_seats_ejected_without_vent_proof",
            "impostor_seats_ejected_with_vent_proof",
        ),
    }
)


class GameplayCensusConformanceError(RuntimeError):
    """A count a recorded setting forces to zero was not zero.

    The message names the set, seed and meeting (or tick) of the first breach.
    It is a code defect in whatever recorded the game, never a result.
    """


class GameplayCensusEraError(ValueError):
    """Two games or groups with different recorded eras were to be combined."""


class GameplayCensusFieldError(ValueError):
    """A recorded setting the census has not classified."""


# ---------------------------------------------------------------------------
# Recorded settings: the classification and the predicates that read them
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SettingPredicate:
    """A conjunction of recorded setting values, or the always-true guard.

    ``conditions`` pairs a field with the value that switches the guard on. A
    field missing from the carrier's recorded values reads its historical
    default (:data:`SETTING_DEFAULTS`).
    """

    key: str
    conditions: tuple[tuple[str, SettingValue], ...]
    always: bool = False

    def __post_init__(self) -> None:
        if self.always == bool(self.conditions):
            raise ValueError(
                f"predicate {self.key!r}: exactly one of always or conditions"
            )

    def holds(self, values: Mapping[str, SettingValue]) -> bool:
        if self.always:
            return True
        return all(
            setting_value(values, name) == value for name, value in self.conditions
        )

    def describe(self) -> str:
        if self.always:
            return "always"
        return " and ".join(
            f"{name} = {_render_value(value)}" for name, value in self.conditions
        )


def _render_value(value: SettingValue) -> str:
    if value is None:
        return "unset"
    if isinstance(value, bool):
        return "on" if value else "off"
    return str(value)


PHYSICAL_VENT_WITNESS: Final = SettingPredicate(
    key="physical_vent_witness", conditions=(("vent_witness_rule", "physical"),)
)
OWN_FRESH_KILL_ENTRY: Final = SettingPredicate(
    key="own_fresh_kill_entry",
    conditions=(("vent_entry_policy", "own_fresh_kill"),),
)
LOOK_AND_WAIT_EXIT: Final = SettingPredicate(
    key="look_and_wait_exit", conditions=(("vent_exit_policy", "look_and_wait"),)
)
MEETING_REGROUP: Final = SettingPredicate(
    key="meeting_regroup", conditions=(("meeting_reset", "hub_with_grace"),)
)
PUBLIC_BODY_HANDLE: Final = SettingPredicate(
    key="public_body_handle", conditions=(("report_body_handle_version", 1),)
)
BOUNDED_REBUTTAL: Final = SettingPredicate(
    key="bounded_rebuttal", conditions=(("bounded_rebuttal_version", 1),)
)
NO_REBUTTAL: Final = SettingPredicate(
    key="no_rebuttal", conditions=(("bounded_rebuttal_version", None),)
)
NO_IMPOSTOR_SELF_REPORT: Final = SettingPredicate(
    key="no_impostor_self_report",
    conditions=(("self_report", False), ("contextual_self_report_version", None)),
)
OWN_KILL_BALLOT_ROW: Final = SettingPredicate(
    key="own_kill_ballot_row", conditions=(("ballot_kill_row_version", 1),)
)
ALWAYS: Final = SettingPredicate(key="always", conditions=(), always=True)

#: Every predicate a cell may carry, by key.
PREDICATES: Final[Mapping[str, SettingPredicate]] = MappingProxyType(
    {
        predicate.key: predicate
        for predicate in (
            PHYSICAL_VENT_WITNESS,
            OWN_FRESH_KILL_ENTRY,
            LOOK_AND_WAIT_EXIT,
            MEETING_REGROUP,
            PUBLIC_BODY_HANDLE,
            BOUNDED_REBUTTAL,
            NO_REBUTTAL,
            NO_IMPOSTOR_SELF_REPORT,
            OWN_KILL_BALLOT_ROW,
            ALWAYS,
        )
    }
)


@dataclass(frozen=True)
class FieldUse:
    """How the census uses one recorded setting: exactly one of three kinds.

    ``predicates`` names the setting predicates that read the field.
    ``value_read_by`` names what reads the field's recorded value itself, for a
    field no predicate tests against one value. ``reason`` says why the census
    deliberately does not read the field.
    """

    predicates: tuple[str, ...] = ()
    value_read_by: str = ""
    reason: str = ""

    def __post_init__(self) -> None:
        kinds = (bool(self.predicates), bool(self.value_read_by), bool(self.reason))
        if sum(kinds) != 1:
            raise ValueError(
                "a field is read by predicates, read as a value, or not read for a "
                "reason: exactly one"
            )


def _not_read(reason: str) -> FieldUse:
    return FieldUse(reason=reason)


#: Every recorded setting field, read by a named predicate, read as a value or
#: deliberately not read. ``tests/eval/test_gameplay_census.py`` holds its names
#: equal to ``RecordedExperimentConfig.model_fields``, both ways.
FIELD_CLASSIFICATION: Final[Mapping[str, FieldUse]] = MappingProxyType(
    {
        "format_version": _not_read("a serialization version, not a game rule"),
        "redistribution_policy": _not_read(
            "decides who inherits a dead crewmate's tasks; no cell is forced by it"
        ),
        "meeting_reset": FieldUse(predicates=("meeting_regroup",)),
        "crew_idle_policy": _not_read("moves idle crewmates; no cell is forced by it"),
        "vent_exit_policy": FieldUse(predicates=("look_and_wait_exit",)),
        "post_meeting_retarget": _not_read(
            "retargets impostors after a meeting; no cell is forced by it"
        ),
        "self_report": FieldUse(predicates=("no_impostor_self_report",)),
        "sabotage_threshold": _not_read("a sabotage win rule; no cell is forced by it"),
        "evidence_reasoning_version": _not_read(
            "changes what a meeting renders; no cell is forced by it"
        ),
        "bounded_rebuttal_version": FieldUse(
            predicates=("bounded_rebuttal", "no_rebuttal")
        ),
        "public_account_version": _not_read(
            "changes what a meeting renders; no cell is forced by it"
        ),
        "attributed_testimony_version": _not_read(
            "changes what a meeting renders; no cell is forced by it"
        ),
        "investigation_version": _not_read(
            "moves idle crewmates; no cell is forced by it"
        ),
        "contextual_self_report_version": FieldUse(
            predicates=("no_impostor_self_report",)
        ),
        "vent_witness_rule": FieldUse(predicates=("physical_vent_witness",)),
        "vent_entry_policy": FieldUse(predicates=("own_fresh_kill_entry",)),
        "report_body_handle_version": FieldUse(predicates=("public_body_handle",)),
        "ballot_kill_row_version": FieldUse(predicates=("own_kill_ballot_row",)),
        "impostor_ballot_version": _not_read(
            "an instructed ballot framing; the tally does not enforce it, so no "
            "cell is forced by it"
        ),
        "kill_cooldown_ticks": FieldUse(
            value_read_by=(
                "the length of the grace window, and the value the kill cooldown "
                "cell checks every cooldown write against"
            )
        ),
    }
)


def _field_default(name: str) -> SettingValue:
    """``name``'s historical default, read from the config model's declaration.

    History: census-local defaults stood in for five fields until the arm spine
    declared them (merged at 8df69e15).
    """

    if name not in FIELD_CLASSIFICATION:
        raise GameplayCensusFieldError(f"recorded setting {name!r} is not classified")
    declared = RecordedExperimentConfig.model_fields.get(name)
    if declared is None:
        raise GameplayCensusFieldError(
            f"classified setting {name!r} is not declared on the recorded config"
        )
    default: SettingValue = declared.default
    return default


#: The historical default of every classified field: the value a missing key reads.
SETTING_DEFAULTS: Final[Mapping[str, SettingValue]] = MappingProxyType(
    {name: _field_default(name) for name in FIELD_CLASSIFICATION}
)


def setting_value(values: Mapping[str, SettingValue], name: str) -> SettingValue:
    """``name``'s recorded value, or its historical default when not recorded."""

    if name not in FIELD_CLASSIFICATION:
        raise GameplayCensusFieldError(f"recorded setting {name!r} is not classified")
    return values[name] if name in values else SETTING_DEFAULTS[name]


def canonical_settings(
    values: Mapping[str, SettingValue],
) -> tuple[tuple[str, SettingValue], ...]:
    """The recorded settings minus every value equal to its historical default.

    Raises on a field the census has not classified, so a recording carrying a
    setting no predicate was reviewed against cannot be folded.
    """

    unknown = sorted(set(values) - set(FIELD_CLASSIFICATION))
    if unknown:
        raise GameplayCensusFieldError(
            f"recorded settings {unknown} are not classified by the gameplay census"
        )
    return tuple(
        sorted(
            (name, value)
            for name, value in values.items()
            if value != SETTING_DEFAULTS[name]
        )
    )


# ---------------------------------------------------------------------------
# Eras
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EraKey:
    """The recorded settings one game or group of games shares.

    ``settings`` is canonical (:func:`canonical_settings`): only non-default
    values, sorted. ``prompt_stamps`` is ``None`` for a game that recorded no
    meeting, whose MANIFEST row therefore names no prompt stamp.
    """

    settings: tuple[tuple[str, SettingValue], ...]
    temporal_observation_version: int | None
    substrate_flags: tuple[tuple[str, bool], ...] | None
    prompt_stamps: tuple[str, ...] | None

    def __post_init__(self) -> None:
        if canonical_settings(dict(self.settings)) != self.settings:
            raise GameplayCensusFieldError(
                "an era's settings must be canonical: sorted, non-default values only"
            )

    @property
    def values(self) -> Mapping[str, SettingValue]:
        return MappingProxyType(dict(self.settings))


def resolve_era(keys: Sequence[EraKey]) -> EraKey:
    """The one era a collection of games or groups shares, or a refusal.

    Settings, temporal version and substrate stamp must be identical. Prompt
    stamps must agree among the keys that carry one; a key without one (a game
    that recorded no meeting) is compatible with any.
    """

    if not keys:
        raise GameplayCensusEraError("no games to take an era from")
    first = keys[0]
    for key in keys[1:]:
        for component in (
            "settings",
            "temporal_observation_version",
            "substrate_flags",
        ):
            if getattr(key, component) != getattr(first, component):
                raise GameplayCensusEraError(
                    f"two eras differ in {component}; the census never pools across eras"
                )
    stamps = {key.prompt_stamps for key in keys if key.prompt_stamps is not None}
    if len(stamps) > 1:
        raise GameplayCensusEraError(
            "two eras differ in prompt stamps; the census never pools across eras"
        )
    return replace(first, prompt_stamps=next(iter(stamps), None))


# ---------------------------------------------------------------------------
# The carrier: ids, rooms, ticks, kinds, labels and computed booleans only
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KillFact:
    """One kill. ``victim`` is the ``KilledEvent``'s target; the loader always
    fills it, and a hand-built kill without one joins no body."""

    tick: int
    killer: PlayerId
    room: RoomId
    witnesses: frozenset[PlayerId]
    victim: PlayerId | None = None


@dataclass(frozen=True)
class VentFact:
    """One vent entry or exit, with the engine's recorded witness lists."""

    tick: int
    actor: PlayerId
    kind: Literal["entry", "exit"]
    source_room: RoomId
    destination_room: RoomId
    source_witnesses: frozenset[PlayerId]
    destination_witnesses: frozenset[PlayerId]


@dataclass(frozen=True)
class BodyFact:
    """A corpse, joined to its victim's kill on the tick the corpse first appeared.

    ``kill_tick`` comes from that ``KilledEvent``; the body id is an opaque key
    here and is never parsed. ``victim`` is the body's own player id, so a body
    joins its kill by victim even when two kills share a tick; the loader always
    fills it.
    """

    body_id: str
    kill_tick: int
    victim: PlayerId | None = None


@dataclass(frozen=True)
class Frame:
    """The state before one play tick's actions resolve.

    ``rooms`` holds every living player not inside a vent.
    """

    rooms: Mapping[PlayerId, RoomId]
    sabotage_active: bool


@dataclass(frozen=True)
class ObservationFact:
    """One structured observation a speaker gave: kind, ticks, subject if any."""

    kind: ObservationKind
    from_tick: int
    to_tick: int
    subject: PlayerId | None


@dataclass(frozen=True)
class AlibiFact:
    """One alibi route: its subject and its (room, from tick, to tick) legs."""

    subject: PlayerId
    legs: tuple[tuple[RoomId, int, int], ...]


@dataclass(frozen=True)
class PlacementFact:
    """One spoken placement of ``player`` in a turn: when, where, and its kind.

    A sighting places its subject, and its company each by a placement of their
    own; a movement sighting places its subject at the room it arrived in; a
    whereabouts claim places its speaker. ``rooms`` is the label's canonical
    room set, and a label with no canonical room places nobody.
    """

    player: PlayerId
    tick: int
    rooms: frozenset[RoomId]
    kind: CheckedPlacementKind


@dataclass(frozen=True)
class TurnFact:
    """One recorded turn. ``placements`` are its spoken placements of the
    checked kinds; the loader fills them, and a hand-built turn holds none."""

    turn_id: str
    index: int
    speaker: PlayerId
    reply_to: str | None
    accusations: tuple[PlayerId, ...]
    observations: tuple[ObservationFact, ...]
    alibis: tuple[AlibiFact, ...]
    placements: tuple[PlacementFact, ...] = ()


@dataclass(frozen=True)
class BallotFact:
    """One recorded ballot.

    ``authored_target`` is what the voter wrote: the typed guard field's
    original when a rewrite reason is recorded, the recorded target otherwise,
    and ``None`` for a ballot that never parsed. ``primary_reason_id`` is the
    turn the ballot cites and ``counter_reason_id`` its counter slot, each a
    recorded id or ``None``; a hand-built ballot without them cites nothing.
    ``held_sources`` is set by the loader on every SKIP labelled as holding
    nothing: the places in the voter's own recorded ballot prompt that name a
    living candidate, empty when none does. It is ``None`` on every other ballot
    and on a hand-built ballot that does not set it.
    """

    voter: PlayerId
    target: str
    authored_target: str | None
    confidence: float
    grounding_label: BallotGroundingLabel | None
    cited_observation_id: str | None
    primary_reason_id: str | None = None
    counter_reason_id: str | None = None
    held_sources: frozenset[HeldSource] | None = None


@dataclass(frozen=True)
class OwnKillRowFact:
    """A served own-kill ballot row found in its holder's recorded prompt."""

    holder: PlayerId
    subject: PlayerId
    room: RoomId
    tick: int
    citation_id: str | None


@dataclass(frozen=True)
class MeetingFact:
    """One meeting, from its trigger tick through the state play resumed in.

    ``selector_pick`` is the (speaker, answered turn) the bounded-rebuttal
    selector chooses on the turns before the first repeat-speaker turn, computed
    by the loader; ``None`` when there is no repeat-speaker turn or the selector
    chooses nothing. ``opener_prompt_has_kill_tick_handle`` is ``None`` when the
    opener's first prompt was not recorded. ``regrouped`` says the recorded
    reset gathered the survivors when play resumed. ``ejected`` is set exactly
    when ``outcome`` is ``EJECTED``, the invariant a meeting result carries; a
    carrier breaking it raises. ``regroup_notices_held`` holds one boolean per
    recorded call with an agent id at a meeting after a regroup: whether its
    prompt carries the notice of every earlier regroup of the game. It is empty
    at a game's first meeting, without a regroup, and on a hand-built carrier
    that does not set it.
    """

    meeting_id: str
    tick: int
    trigger_kind: TriggerKind
    opener: PlayerId
    trigger_body: str | None
    bodies_at_open: tuple[tuple[str, PlayerId | None], ...]
    in_vent_at_open: frozenset[PlayerId]
    impostor_cooldowns_at_open: tuple[tuple[PlayerId, int], ...]
    living: frozenset[PlayerId]
    sabotage_active: bool
    outcome: MeetingOutcome
    ejected: PlayerId | None
    vent_flag_subjects: tuple[frozenset[PlayerId], ...]
    turns: tuple[TurnFact, ...]
    ballots: tuple[BallotFact, ...]
    ballot_floor: float
    selector_pick: tuple[PlayerId, str] | None
    opener_prompt_has_kill_tick_handle: bool | None
    own_kill_rows: tuple[OwnKillRowFact, ...]
    trigger_tick_dropped_events: tuple[tuple[str, int], ...]
    phase_after: Phase
    in_vent_after: frozenset[PlayerId]
    bodies_after: frozenset[str]
    regrouped: bool
    regroup_notices_held: tuple[bool, ...] = ()

    def __post_init__(self) -> None:
        if (self.outcome == "EJECTED") != (self.ejected is not None):
            raise ValueError(
                f"{self.meeting_id}: an ejected player is recorded exactly when "
                "the outcome is EJECTED"
            )


@dataclass(frozen=True)
class DiscardedAction:
    tick: int
    action_type: str


@dataclass(frozen=True)
class CooldownWrite:
    """One impostor's kill cooldown on the state an engine write left.

    ``tick`` is the tick the write belongs to: 0 at round start, the kill's tick,
    or the regroup meeting's tick. ``ticks`` is ``None`` when that state holds no
    cooldown for the impostor, which the cooldown cell counts as a difference.
    """

    writer: CooldownWriter
    tick: int
    player: PlayerId
    ticks: int | None


@dataclass(frozen=True)
class GameFacts:
    seed: int
    roles: Mapping[PlayerId, Role]
    era: EraKey
    kills: tuple[KillFact, ...]
    vents: tuple[VentFact, ...]
    bodies: tuple[BodyFact, ...]
    frames: Mapping[int, Frame]
    meetings: tuple[MeetingFact, ...]
    discarded: tuple[DiscardedAction, ...]
    rows_without_dispositions: int
    winner: WinnerSide | None
    terminal_tick: int
    #: Every impostor's kill cooldown after each engine write of it. The loader
    #: fills it; a hand-built carrier without writes checks none.
    cooldown_writes: tuple[CooldownWrite, ...] = ()
    #: The recorded reason the game ended, ``None`` without a recorded ending.
    end_reason: str | None = None
    #: The completed and the total task instances on the final state, each
    #: ``None`` on a hand-built carrier that does not set it.
    final_tasks_completed: int | None = None
    final_tasks_total: int | None = None
    #: The honesty instrument's route: every player's room on the settled frame
    #: after each tick (a meeting's tick read from its applied state), and on
    #: the frame its actions resolved in. The loader fills both; a hand-built
    #: carrier without them verifies no placement.
    settled_rooms: Mapping[int, Mapping[PlayerId, RoomId]] = field(
        default_factory=lambda: MappingProxyType({})
    )
    resolved_rooms: Mapping[int, Mapping[PlayerId, RoomId]] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True)
class CensusInputs:
    """Everything the pure fold needs about one replay set.

    ``label`` names the set on the page and ``source`` is the path of the
    directory walked. ``kill_cooldown_ticks`` is the recorded kill cooldown,
    else the map's (:func:`recorded_kill_cooldown`): the grace window after a
    regroup, and the value every cooldown write must hold. ``neighbours`` is read
    from the loaded map: the rooms an in-vent impostor infers it can see.
    """

    label: str
    source: str
    era: EraKey
    kill_cooldown_ticks: int
    neighbours: Mapping[RoomId, tuple[RoomId, ...]]
    games: tuple[GameFacts, ...]


# ---------------------------------------------------------------------------
# Cell and table definitions, published inside the artifact
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CellSpec:
    """One cell's published definition.

    ``guard`` is the setting predicate that forces the count to zero while it
    holds. ``scope`` is the setting predicate the counted thing exists under: a
    cell with a scope is counted only in games whose recorded settings satisfy
    it, and reads ``n/a`` in every other era instead of a measured zero.
    """

    title: str
    heading: str
    definition: str
    reads: tuple[str, ...]
    guard: SettingPredicate | None = None
    scope: SettingPredicate | None = None


@dataclass(frozen=True)
class TableSpec:
    """One table's published definition; ``scope`` as on :class:`CellSpec`."""

    title: str
    heading: str
    definition: str
    reads: tuple[str, ...]
    scope: SettingPredicate | None = None


def _in_scope(
    scope: SettingPredicate | None, values: Mapping[str, SettingValue]
) -> bool:
    """Whether a cell or table with ``scope`` is counted under ``values``."""

    return scope is None or scope.holds(values)


_WITNESSES: Final[str] = "Witnesses"
_TRIPS: Final[str] = "Vent trips and surfacings"
_PROOF: Final[str] = "Vent proof at meetings"
_SEATS: Final[str] = "Ejections at report meetings, by seat"
_CORPSES: Final[str] = "Corpses and the state play resumes in"
_REGROUP: Final[str] = "After a regroup"
_COOLDOWN: Final[str] = "The kill cooldown"
_STRUCTURE: Final[str] = "Meeting structure"
_REBUTTALS: Final[str] = "Rebuttals"
_BALLOTS: Final[str] = "Ballots"
_HELD: Final[str] = "What a ballot held"
_SHAPE: Final[str] = "The shape of a game"
_BESIDE: Final[str] = "Reported beside the counts"

#: The published order of the headings.
HEADINGS: Final[tuple[str, ...]] = (
    _WITNESSES,
    _TRIPS,
    _PROOF,
    _SEATS,
    _CORPSES,
    _REGROUP,
    _COOLDOWN,
    _STRUCTURE,
    _REBUTTALS,
    _BALLOTS,
    _HELD,
    _SHAPE,
    _BESIDE,
)

_KILL: Final = ("Killed",)
_HELD_PROMPT_READS: Final = (
    "meeting row ballots",
    "recorded ballot prompt",
    "state at the meeting",
)
_CITED_LINE_READS: Final = (
    "meeting row ballots",
    "meeting row turns",
    "state after the tick",
    "state after the meeting",
)
_VENTS: Final = ("VentEntered", "VentExited")
_MEETING_ROW: Final = ("meeting row",)
_SEAT_READS: Final = (
    "MeetingTriggered",
    "state at the meeting",
    "meeting row",
    "meeting row flags",
)

CELLS: Final[Mapping[str, CellSpec]] = MappingProxyType(
    {
        "kills_seen_by_crew": CellSpec(
            "Kills a crewmate saw",
            _WITNESSES,
            "Kills with at least one crewmate among the engine's recorded witnesses, "
            "over all kills.",
            _KILL,
        ),
        "vent_entries_seen_by_crew": CellSpec(
            "Vent entries a crewmate saw",
            _WITNESSES,
            "Vent entries with a crewmate among either recorded witness list, over "
            "all vent entries.",
            ("VentEntered",),
        ),
        "vent_exits_seen_by_crew": CellSpec(
            "Vent exits a crewmate saw",
            _WITNESSES,
            "Vent exits with a crewmate among either recorded witness list, over all "
            "vent exits.",
            ("VentExited",),
        ),
        "vent_exits_seen_from_exit_room": CellSpec(
            "Vent exits seen from the room surfaced into",
            _WITNESSES,
            "Vent exits with a crewmate among the witnesses in the room the impostor "
            "surfaced into, over all vent exits.",
            ("VentExited",),
        ),
        "vent_exits_seen_only_from_room_left": CellSpec(
            "Vent exits seen only from the room left",
            _WITNESSES,
            "Vent exits with a crewmate among the witnesses in the room the impostor "
            "left and none in the room it surfaced into, over all vent exits.",
            ("VentExited",),
            PHYSICAL_VENT_WITNESS,
        ),
        "impostors_seen_venting_ejected": CellSpec(
            "Impostors seen venting, then ejected",
            _WITNESSES,
            "Impostors ejected at some meeting, over impostors with at least one "
            "vent entry or exit a crewmate saw.",
            (*_VENTS, "meeting row"),
        ),
        "impostors_vented_unseen_ejected": CellSpec(
            "Impostors who vented unseen, then ejected",
            _WITNESSES,
            "Impostors ejected at some meeting, over impostors who vented but whom "
            "no crewmate ever saw venting.",
            (*_VENTS, "meeting row"),
        ),
        "impostors_never_vented_ejected": CellSpec(
            "Impostors who never vented, then ejected",
            _WITNESSES,
            "Impostors ejected at some meeting, over impostors who never vented.",
            (*_VENTS, "meeting row"),
        ),
        "vent_entries_not_after_own_fresh_kill": CellSpec(
            "Vent entries not after the impostor's own fresh kill",
            _TRIPS,
            "Vent entries where no victim of the entering impostor lies in that room, "
            f"killed at most {FRESH_KILL_WINDOW_TICKS} ticks before the entry with no "
            "meeting in between, over all vent entries.",
            ("VentEntered", "Killed", "meeting row"),
            OWN_FRESH_KILL_ENTRY,
        ),
        "surfacings_before_cap_in_view": CellSpec(
            "Surfacings before the cap with someone in view",
            _TRIPS,
            "Vent exits made before the in-vent cap while a living non-teammate stood, "
            "just before the exit tick, in a room the impostor infers it can see "
            "from inside the vent, over all vent exits.",
            ("VentEntered", "VentExited", "state before the tick"),
            LOOK_AND_WAIT_EXIT,
        ),
        "trips_longer_than_cap": CellSpec(
            "Vent trips longer than the cap",
            _TRIPS,
            "Vent trips whose ticks inside exceed the in-vent cap, over vent trips "
            "that stayed inside for more than one tick.",
            (*_VENTS, "meeting row"),
            LOOK_AND_WAIT_EXIT,
        ),
        "forced_surfacings": CellSpec(
            "Surfacings at the cap",
            _TRIPS,
            "Vent exits made exactly at the in-vent cap, over all vent exits.",
            (*_VENTS, "meeting row"),
            scope=LOOK_AND_WAIT_EXIT,
        ),
        "vent_exits_into_occupied_room": CellSpec(
            "Vent exits into a room a crewmate stood in",
            _TRIPS,
            "Vent exits whose destination room held a living crewmate just before "
            "the exit tick, over all vent exits.",
            ("VentExited", "state before the tick"),
        ),
        "vent_exits_into_visibly_occupied_room": CellSpec(
            "Vent exits into a room the impostor could see a crewmate in",
            _TRIPS,
            "Vent exits whose destination room was among the impostor's inferred-"
            "visible rooms and held a living crewmate just before the exit tick, over "
            "all vent exits.",
            ("VentExited", "state before the tick"),
        ),
        "vent_exits_while_room_left_occupied": CellSpec(
            "Vent exits while a crewmate stood in the room left",
            _TRIPS,
            "Vent exits whose source room held a living crewmate just before the "
            "exit tick, over all vent exits.",
            ("VentExited", "state before the tick"),
        ),
        "in_place_surfacings_near_crew": CellSpec(
            "Surfacings in place with a crewmate arriving before the walk-out",
            _TRIPS,
            "Vent exits back into the room the impostor entered from, where a living "
            "crewmate stands in that room on some tick after the surfacing and "
            "before the impostor leaves it, over all such in-place exits.",
            ("VentExited", "state before the tick"),
        ),
        "kills_soon_after_surfacing": CellSpec(
            "Kills soon after the killer surfaced",
            _TRIPS,
            f"Kills made at most {SHORT_WINDOW_TICKS} ticks after the killer's own "
            "vent exit, over all kills.",
            ("Killed", "VentExited"),
        ),
        "meetings_with_vent_proof": CellSpec(
            "Meetings with vent proof",
            _PROOF,
            "Meetings with a vent-sighting flag naming a player alive when the "
            "meeting opened, over all meetings.",
            ("meeting row flags",),
        ),
        "vent_band_impostor_ejections": CellSpec(
            "Impostor ejections in the vent band",
            _PROOF,
            "Impostor ejections whose ejected player a vent-sighting flag names, over "
            "all impostor ejections.",
            ("meeting row flags",),
        ),
        "vent_band_crew_ejections": CellSpec(
            "Crewmate ejections in the vent band",
            _PROOF,
            "Crewmate ejections whose ejected player a vent-sighting flag names, over "
            "all crewmate ejections.",
            ("meeting row flags",),
        ),
        "impostor_ejections_without_vent_proof": CellSpec(
            "Impostor ejections without vent proof",
            _PROOF,
            "Impostor ejections at meetings without vent proof, over all impostor "
            "ejections.",
            ("meeting row flags",),
        ),
        "vent_band_resting_only_on_room_left": CellSpec(
            "Vent-band ejections resting only on the room left",
            _PROOF,
            "Vent-band impostor ejections where every crewmate who saw the ejected "
            "impostor vent before the meeting, and was alive at it, saw only an exit "
            "from the room left, over all vent-band impostor ejections.",
            (*_VENTS, "meeting row flags"),
            PHYSICAL_VENT_WITNESS,
        ),
        "meetings_without_vent_proof_ejecting": CellSpec(
            "Meetings without vent proof that ejected",
            _PROOF,
            "Meetings without vent proof that ejected someone, over all meetings "
            "without vent proof.",
            ("meeting row flags",),
        ),
        "ejections_without_vent_proof_of_impostors": CellSpec(
            "Ejections without vent proof that removed an impostor",
            _PROOF,
            "Impostor ejections, over all ejections at meetings without vent proof.",
            ("meeting row flags",),
        ),
        "button_meetings_with_vent_proof": CellSpec(
            "Button meetings with vent proof",
            _PROOF,
            "Button meetings with vent proof, over all button meetings.",
            ("MeetingTriggered", "meeting row flags"),
        ),
        "reporter_seats_ejected": CellSpec(
            "Reporter seats ejected",
            _SEATS,
            "Report meetings that ejected their reporter, over the reporter's "
            "seats: one per report meeting, whatever the reporter's role.",
            _SEAT_READS,
        ),
        "reporter_seats_ejected_without_vent_proof": CellSpec(
            "Reporter seats ejected, without vent proof",
            _SEATS,
            "Report meetings without vent proof that ejected their reporter, over "
            "the reporter's seats at report meetings without vent proof.",
            _SEAT_READS,
        ),
        "reporter_seats_ejected_with_vent_proof": CellSpec(
            "Reporter seats ejected, with vent proof",
            _SEATS,
            "Report meetings with vent proof that ejected their reporter, over the "
            "reporter's seats at report meetings with vent proof.",
            _SEAT_READS,
        ),
        "other_crewmate_seats_ejected": CellSpec(
            "Other crewmate seats ejected",
            _SEATS,
            "Seats of living crewmates other than the reporter that a report "
            "meeting ejected, over those seats at every report meeting.",
            _SEAT_READS,
        ),
        "other_crewmate_seats_ejected_without_vent_proof": CellSpec(
            "Other crewmate seats ejected, without vent proof",
            _SEATS,
            "Seats of living crewmates other than the reporter that a report "
            "meeting without vent proof ejected, over those seats at report "
            "meetings without vent proof.",
            _SEAT_READS,
        ),
        "other_crewmate_seats_ejected_with_vent_proof": CellSpec(
            "Other crewmate seats ejected, with vent proof",
            _SEATS,
            "Seats of living crewmates other than the reporter that a report "
            "meeting with vent proof ejected, over those seats at report meetings "
            "with vent proof.",
            _SEAT_READS,
        ),
        "impostor_seats_ejected": CellSpec(
            "Impostor seats ejected",
            _SEATS,
            "Seats of living impostors other than the reporter that a report "
            "meeting ejected, over those seats at every report meeting.",
            _SEAT_READS,
        ),
        "impostor_seats_ejected_without_vent_proof": CellSpec(
            "Impostor seats ejected, without vent proof",
            _SEATS,
            "Seats of living impostors other than the reporter that a report "
            "meeting without vent proof ejected, over those seats at report "
            "meetings without vent proof.",
            _SEAT_READS,
        ),
        "impostor_seats_ejected_with_vent_proof": CellSpec(
            "Impostor seats ejected, with vent proof",
            _SEATS,
            "Seats of living impostors other than the reporter that a report "
            "meeting with vent proof ejected, over those seats at report meetings "
            "with vent proof.",
            _SEAT_READS,
        ),
        "reporters_among_ejected_crewmates": CellSpec(
            "Reporters among the crewmates ejected",
            _SEATS,
            "Crewmates a report meeting ejected who were its reporter, over all "
            "crewmates report meetings ejected.",
            _SEAT_READS,
        ),
        "reporters_among_crewmate_seats": CellSpec(
            "Reporters among the crewmate seats",
            _SEATS,
            "Crewmate seats at report meetings that were the reporter's, over all "
            "crewmate seats at report meetings.",
            _SEAT_READS,
        ),
        "stale_report_meetings": CellSpec(
            "Stale report meetings",
            _CORPSES,
            "Report meetings whose reported corpse already lay on the floor when the "
            "previous meeting opened, over all report meetings.",
            ("MeetingTriggered", "state at the meeting"),
            MEETING_REGROUP,
        ),
        "meetings_opening_with_another_unreported_corpse": CellSpec(
            "Meetings opening with another unreported corpse",
            _CORPSES,
            "Meetings that opened with a corpse other than the reported one that no "
            "one had discovered, over all meetings.",
            ("state at the meeting",),
        ),
        "play_resumes_with_impostor_in_vent": CellSpec(
            "Play resumes with an impostor in a vent",
            _CORPSES,
            "Meetings after which play resumed with an impostor inside a vent, over "
            "meetings after which play resumed.",
            ("state after the meeting",),
            MEETING_REGROUP,
        ),
        "play_resumes_with_corpse": CellSpec(
            "Play resumes with a corpse on the floor",
            _CORPSES,
            "Meetings after which play resumed with a corpse on the floor, over "
            "meetings after which play resumed.",
            ("state after the meeting",),
            MEETING_REGROUP,
        ),
        "post_meeting_kills_soon_after": CellSpec(
            "Kills soon after a meeting",
            _CORPSES,
            f"Kills made at most {SHORT_WINDOW_TICKS} ticks after the previous "
            "meeting's tick, over all kills made after some meeting.",
            ("Killed", "meeting row"),
        ),
        "meetings_opening_with_impostor_in_vent": CellSpec(
            "Meetings opening with an impostor in a vent",
            _CORPSES,
            "Meetings that opened with an impostor inside a vent, over all meetings.",
            ("state at the meeting",),
        ),
        "impostor_cooldown_zero_at_open": CellSpec(
            "Impostors able to kill when a meeting opened",
            _CORPSES,
            "Living impostors whose kill cooldown was zero when a meeting opened, "
            "over living impostors at every meeting.",
            ("state at the meeting",),
        ),
        "kills_in_grace_window_after_regroup": CellSpec(
            "Kills in the grace window after a regroup",
            _REGROUP,
            "Kills made on a tick after a regroup meeting no later than the "
            "recorded kill cooldown, else the map's, over all kills made between a "
            "regroup and the next meeting.",
            ("Killed", "meeting row"),
            MEETING_REGROUP,
        ),
        "report_corpses_older_than_last_close": CellSpec(
            "Reported corpses older than the last regroup",
            _REGROUP,
            "Report meetings whose reported victim was killed on or before the "
            "previous meeting's tick, over report meetings whose previous meeting "
            "regrouped.",
            ("Killed", "MeetingTriggered", "meeting row"),
            MEETING_REGROUP,
        ),
        "trips_closed_by_regroup": CellSpec(
            "Vent trips ended by a regroup",
            _REGROUP,
            "Vent trips that ended because a regroup cleared the vent, with no exit, "
            "over all vent trips that ended.",
            (*_VENTS, "meeting row"),
            scope=MEETING_REGROUP,
        ),
        "kill_witness_button_calls_soon_after_regroup": CellSpec(
            "Kill witnesses pressing the button soon after a regroup",
            _REGROUP,
            f"Button meetings called at most {BUTTON_COOLDOWN_TICKS} ticks after a "
            "regroup by a player who witnessed a kill since it, over button meetings "
            "whose previous meeting regrouped.",
            ("Killed", "MeetingTriggered", "meeting row"),
        ),
        "sabotage_active_at_regroup": CellSpec(
            "Sabotage active at a regroup",
            _REGROUP,
            "Regroup meetings that opened with a sabotage active, over all regroup "
            "meetings.",
            ("state at the meeting",),
        ),
        "prompts_missing_a_regroup_notice": CellSpec(
            "Prompts after a regroup missing an earlier regroup's notice",
            _REGROUP,
            "Recorded meeting prompts of a player at a meeting after a regroup that "
            "lack the notice of some earlier regroup of the same game, in the "
            "wording the memory renders from that regroup's tick and room, over "
            "all such prompts.",
            ("recorded meeting prompts", "meeting row"),
            MEETING_REGROUP,
        ),
        "kill_cooldowns_differing_from_recorded": CellSpec(
            "Kill cooldowns that differ from the recorded value",
            _COOLDOWN,
            "Impostor kill cooldowns that differ from the recorded kill cooldown, "
            "else the map's, read on the state each engine write leaves: every "
            "impostor at round start, the killer after each of its kills and every "
            "living impostor after each regroup; over all such writes.",
            ("state at round start", "Killed", "state after the meeting"),
            ALWAYS,
        ),
        "first_reply_accuses_opener": CellSpec(
            "The first reply accuses the opener",
            _STRUCTURE,
            "Meetings whose second turn carries a structured accusation of the "
            "opener, over all meetings.",
            ("meeting row turns",),
        ),
        "opener_accused_after_opening": CellSpec(
            "Someone accuses the opener",
            _STRUCTURE,
            "Meetings where a speaker other than the opener accused the opener, over "
            "all meetings.",
            ("meeting row turns",),
        ),
        "opener_speaks_again": CellSpec(
            "The opener speaks a second time",
            _STRUCTURE,
            "Meetings where the opener took more than one turn, over all meetings.",
            ("meeting row turns",),
        ),
        "accused_opener_answers": CellSpec(
            "An accused opener answers",
            _STRUCTURE,
            "Meetings where the opener spoke again after another speaker accused "
            "them, over meetings where another speaker accused the opener.",
            ("meeting row turns",),
            NO_REBUTTAL,
        ),
        "meetings_with_repeat_speaker": CellSpec(
            "Meetings where someone spoke twice",
            _STRUCTURE,
            "Meetings with at least one turn by a player who had already spoken, "
            "over all meetings.",
            ("meeting row turns",),
            NO_REBUTTAL,
        ),
        "meetings_with_second_repeat_speaker": CellSpec(
            "Meetings with two repeat-speaker turns",
            _STRUCTURE,
            "Meetings with two or more turns by players who had already spoken, over "
            "all meetings.",
            ("meeting row turns",),
            ALWAYS,
        ),
        "impostor_openers": CellSpec(
            "Meetings opened by an impostor",
            _STRUCTURE,
            "Meetings whose opener is an impostor, over all meetings.",
            ("MeetingTriggered",),
            NO_IMPOSTOR_SELF_REPORT,
        ),
        "report_openings_with_kill_tick_handle": CellSpec(
            "Report openings that name the kill tick in the body handle",
            _STRUCTURE,
            "Report meetings whose opener's first recorded prompt carries a body "
            "handle embedding the death tick, over report meetings with a recorded "
            "opener prompt.",
            ("MeetingTriggered", "recorded opener prompt"),
            PUBLIC_BODY_HANDLE,
        ),
        "openers_among_innocent_ejections": CellSpec(
            "Openers among ejected crewmates",
            _STRUCTURE,
            "Crewmate ejections that removed the meeting's opener, over all crewmate "
            "ejections.",
            ("MeetingTriggered", "meeting row"),
        ),
        "skipped_report_meetings": CellSpec(
            "Report meetings that skipped",
            _STRUCTURE,
            "Report meetings that ejected no one, over all report meetings.",
            ("MeetingTriggered", "meeting row"),
        ),
        "rebuttals_differing_from_selector": CellSpec(
            "Rebuttals the selector would not have chosen",
            _REBUTTALS,
            "Meetings whose first repeat-speaker turn has a speaker or answered turn "
            "different from the bounded-rebuttal selector's pick on the turns before "
            "it, over meetings with a repeat-speaker turn.",
            ("meeting row turns",),
            BOUNDED_REBUTTAL,
        ),
        "rebuttals_with_alibi": CellSpec(
            "Rebuttals carrying an alibi",
            _REBUTTALS,
            "Repeat-speaker turns carrying an alibi about the speaker, over all "
            "repeat-speaker turns.",
            ("meeting row turns",),
        ),
        "rebuttals_with_whereabouts": CellSpec(
            "Rebuttals carrying a whereabouts claim",
            _REBUTTALS,
            "Repeat-speaker turns carrying a whereabouts observation, over all "
            "repeat-speaker turns.",
            ("meeting row turns",),
        ),
        "rebuttals_with_sighting": CellSpec(
            "Rebuttals carrying a sighting",
            _REBUTTALS,
            "Repeat-speaker turns carrying a sighting (an observation naming a "
            "player seen in a room, venting, killing or moving, the speaker "
            "included), over all repeat-speaker turns.",
            ("meeting row turns",),
        ),
        "rebuttals_redirect_only": CellSpec(
            "Rebuttals that only redirect",
            _REBUTTALS,
            "Repeat-speaker turns carrying an accusation and no alibi, whereabouts or "
            "sighting, over all repeat-speaker turns.",
            ("meeting row turns",),
        ),
        "rebuttal_accusations_against_earlier_speakers": CellSpec(
            "Rebuttal accusations against players who already spoke",
            _REBUTTALS,
            "Accusations in repeat-speaker turns naming a player who spoke earlier in "
            "the meeting, over all accusations in repeat-speaker turns.",
            ("meeting row turns",),
        ),
        "opener_rebuttals_answering_charged_tick": CellSpec(
            "Opener rebuttals answering the charged tick",
            _REBUTTALS,
            "Repeat-speaker turns by the opener carrying an alibi leg, a whereabouts "
            "claim or a sighting at a tick the answered turn observed the opener, "
            "over such turns whose answered turn observed the opener at some tick; "
            "the rest are not evaluable.",
            ("meeting row turns",),
        ),
        "ballots_citing_a_rebuttal": CellSpec(
            "Ballots whose cited turn is a rebuttal",
            _REBUTTALS,
            "Ballots whose cited turn is a repeat-speaker turn of the same meeting, "
            "over all ballots at meetings with a repeat-speaker turn.",
            ("meeting row turns", "meeting row ballots"),
            scope=BOUNDED_REBUTTAL,
        ),
        "ballots_countering_with_a_rebuttal": CellSpec(
            "Ballots whose counter slot names a rebuttal",
            _REBUTTALS,
            "Ballots whose counter slot, the strongest thing the voter held "
            "pointing away from its choice, names a repeat-speaker turn of the "
            "same meeting, over all ballots at meetings with a repeat-speaker turn.",
            ("meeting row turns", "meeting row ballots"),
            scope=BOUNDED_REBUTTAL,
        ),
        "impostor_skip_ballots": CellSpec(
            "Impostor ballots that skip",
            _BALLOTS,
            "Impostor ballots whose recorded target is SKIP, over all impostor "
            "ballots.",
            ("meeting row ballots",),
        ),
        "impostor_eject_ballots": CellSpec(
            "Impostor ballots that name a player",
            _BALLOTS,
            "Impostor ballots whose recorded target is a player, over all impostor "
            "ballots.",
            ("meeting row ballots",),
        ),
        "impostor_ejects_labelled_supported": CellSpec(
            "Impostor ballots naming a player with a supported label",
            _BALLOTS,
            "Impostor ballots naming a player whose meeting-layer grounding label is "
            "supported, over impostor ballots naming a player.",
            ("meeting row ballots",),
        ),
        "recorded_teammate_ballot_targets": CellSpec(
            "Impostor ballots recorded against a teammate",
            _BALLOTS,
            "Impostor ballots whose recorded target is a fellow impostor, over all "
            "impostor ballots.",
            ("meeting row ballots",),
            ALWAYS,
        ),
        "authored_teammate_ballot_targets": CellSpec(
            "Impostor ballots written against a teammate",
            _BALLOTS,
            "Impostor ballots whose authored target, read from the typed guard "
            "fields, is a fellow impostor, over all impostor ballots.",
            ("meeting row ballots",),
        ),
        "ejections_carried_only_by_impostor_ballots": CellSpec(
            "Ejections whose confidence floor only impostors met",
            _BALLOTS,
            "Ejections where every ballot for the ejected player at or above the "
            "tally's recorded confidence floor was cast by an impostor, over all "
            "ejections.",
            ("meeting row ballots",),
        ),
        "ejections_undone_with_impostor_ballots_as_skip": CellSpec(
            "Ejections that would not stand with impostor ballots read as SKIP",
            _BALLOTS,
            "Ejections whose re-tally, with every impostor ballot read as SKIP and "
            "every other ballot held fixed, ejects no one or a different player, "
            "over all ejections.",
            ("meeting row ballots",),
        ),
        "ejections_undone_with_impostor_ballots_removed": CellSpec(
            "Ejections that would not stand with impostor ballots removed",
            _BALLOTS,
            "Ejections whose re-tally, with every impostor ballot removed and every "
            "other ballot held fixed, ejects no one or a different player, over all "
            "ejections.",
            ("meeting row ballots",),
        ),
        "own_kill_rows_breaching": CellSpec(
            "Own-kill ballot rows naming a teammate or held by a non-witness",
            _BALLOTS,
            "Served own-kill rows that name the holder's fellow impostor as the "
            "killer, whatever they cite, or that do not cite, by the holder's own "
            "observation id, a kill the named player made with the holder among its "
            "witnesses, over all served own-kill rows. A row citing nothing counts "
            "here, because the row is specified to cite its kill.",
            ("recorded ballot prompt", "Killed"),
            OWN_KILL_BALLOT_ROW,
        ),
        "own_kill_rows_cited_by_holder": CellSpec(
            "Own-kill ballot rows their holder cited",
            _BALLOTS,
            "Served own-kill rows whose holder's ballot cites the row's observation, "
            "over all served own-kill rows.",
            ("recorded ballot prompt", "meeting row ballots"),
        ),
        "crew_witnessed_kills_held_at_next_meeting": CellSpec(
            "Kills a crewmate saw, held by a living witness at the next meeting",
            _BALLOTS,
            "Crew-witnessed kills with a crewmate witness alive at the next meeting, "
            "over crew-witnessed kills a meeting followed; the rest are not "
            "evaluable.",
            ("Killed", "meeting row"),
        ),
        "held_kill_witnesses_voting_killer": CellSpec(
            "Held kills whose witness voted the killer",
            _BALLOTS,
            "Held crew-witnessed kills where a living witness's ballot names the "
            "killer, over held crew-witnessed kills.",
            ("Killed", "meeting row ballots"),
        ),
        "held_kill_killers_ejected": CellSpec(
            "Held kills whose killer was ejected",
            _BALLOTS,
            "Held crew-witnessed kills whose killer the next meeting ejected, over "
            "held crew-witnessed kills.",
            ("Killed", "meeting row"),
        ),
        "held_kill_killers_ejected_at_any_later_meeting": CellSpec(
            "Held kills whose killer some later meeting ejected",
            _BALLOTS,
            "Held crew-witnessed kills whose killer the next meeting, or any "
            "meeting after it, ejected, over held crew-witnessed kills.",
            ("Killed", "meeting row"),
        ),
        "held_kill_witnesses_ejected": CellSpec(
            "Held kills whose living witness was ejected",
            _BALLOTS,
            "Held crew-witnessed kills where the next meeting ejected one of the "
            "kill's living crew witnesses, over held crew-witnessed kills.",
            ("Killed", "meeting row"),
        ),
        "skips_holding_nothing": CellSpec(
            "SKIP ballots labelled as holding nothing",
            _BALLOTS,
            "SKIP ballots, whatever the voter's role, whose recorded grounding label "
            "says the voter stated outright that it held nothing that resolves the "
            "vote, over all SKIP ballots. The label restates the voter's own "
            "statement, and the holds-nothing check reads it against the lines "
            "the voter's own ballot prompt held.",
            ("meeting row ballots",),
        ),
        "holds_nothing_skips_naming_no_candidate": CellSpec(
            "Holds-nothing SKIPs whose prompt names no living candidate",
            _HELD,
            "SKIP ballots labelled as holding nothing, whatever the voter's role, "
            "whose voter's own recorded ballot prompt names no living candidate in "
            "an observation row, an evidence row, a flag or a typed or spoken turn "
            "line, over all SKIP ballots labelled as holding nothing. The label "
            "reads as nothing that resolves the vote, not as nothing held, and a "
            "line held is not a reason to vote.",
            _HELD_PROMPT_READS,
        ),
        "holds_nothing_skips_naming_a_candidate": CellSpec(
            "Holds-nothing SKIPs whose prompt names a living candidate",
            _HELD,
            "SKIP ballots labelled as holding nothing, whatever the voter's role, "
            "whose voter's own recorded ballot prompt names a living candidate in "
            "at least one of those places, over all SKIP ballots labelled as "
            "holding nothing: the complement of the cell above. A line held is not "
            "a reason to vote.",
            _HELD_PROMPT_READS,
        ),
        "cited_lines_true_to_the_route": CellSpec(
            "Supported EJECTs whose cited line the route makes true",
            _HELD,
            "EJECT ballots labelled supported, whatever the voter's role, whose "
            "every checkable placement of the target in the cited turn the engine "
            "route makes true, over supported EJECTs whose cited turn places the "
            "target checkably. A true cited line is not a correct vote.",
            _CITED_LINE_READS,
        ),
        "cited_lines_false_to_the_route": CellSpec(
            "Supported EJECTs whose cited line the route makes false",
            _HELD,
            "EJECT ballots labelled supported, whatever the voter's role, with at "
            "least one placement of the target in the cited turn the engine route "
            "makes false, over supported EJECTs whose cited turn places the target "
            "checkably. A voter who believed a false line still held it.",
            _CITED_LINE_READS,
        ),
        "task_wins_with_sabotage_in_play": CellSpec(
            "Task wins in games with a sabotage in play",
            _SHAPE,
            "Games the crew won on tasks in which a sabotage was active before at "
            "least one play tick, over games the crew won on tasks. This counts "
            "co-occurrence and measures no delay.",
            ("game over row", "state before the tick"),
        ),
        "impostor_wins": CellSpec(
            "Games the impostors won",
            _BESIDE,
            "Games whose recorded winner is the impostors, over games with a recorded "
            "winner.",
            ("game over row",),
        ),
        "role_correct_ejections": CellSpec(
            "Ejections that removed an impostor",
            _BESIDE,
            "Impostor ejections, over all ejections. Reported, never a gate.",
            ("meeting row",),
        ),
    }
)

TABLES: Final[Mapping[str, TableSpec]] = MappingProxyType(
    {
        "ticks_inside_per_trip": TableSpec(
            "Ticks inside per surfaced vent trip",
            _TRIPS,
            "Vent exits by the number of play ticks the impostor spent inside, the "
            "count restarting at a meeting boundary.",
            (*_VENTS, "meeting row"),
        ),
        "vent_band_by_moment": TableSpec(
            "Which vent moment the vent band rests on",
            _PROOF,
            "Vent-band impostor ejections by whether a crewmate saw the ejected "
            "impostor's exit only, entry only, both, or neither before the meeting.",
            (*_VENTS, "meeting row flags"),
        ),
        "corpse_age_at_report": TableSpec(
            "Corpse age at report",
            _CORPSES,
            "Report meetings by the ticks between the reported victim's kill and the "
            "meeting.",
            ("Killed", "MeetingTriggered"),
        ),
        "trigger_tick_events_dropped_by_regroup": TableSpec(
            "Trigger-tick movement and task events a regroup drops",
            _REGROUP,
            "Movement and task events on the trigger tick of every regroup meeting, "
            "by kind.",
            _REGROUP_DROPPED_KINDS,
            scope=MEETING_REGROUP,
        ),
        "kill_cooldown_writes_by_writer": TableSpec(
            "Kill cooldown writes by writer",
            _COOLDOWN,
            "The writes the kill cooldown cell checks, by the engine step that made "
            "them: round_start (the seeding), after_kill (the killer's own "
            "cooldown) and regroup (every living impostor at a regroup).",
            ("state at round start", "Killed", "state after the meeting"),
        ),
        "meetings_by_trigger": TableSpec(
            "Meetings by trigger",
            _STRUCTURE,
            "Meetings by what opened them: a reported corpse or a button press.",
            ("MeetingTriggered",),
        ),
        "innocent_opener_ejections_by_trigger": TableSpec(
            "Ejected crewmate openers by trigger",
            _STRUCTURE,
            "Crewmate ejections that removed the opener, by what opened the meeting.",
            ("MeetingTriggered", "meeting row"),
        ),
        "actions_thrown_away_on_trigger_ticks": TableSpec(
            "Actions thrown away on trigger ticks",
            _STRUCTURE,
            "Submitted actions the engine never ran because an earlier action on the "
            "same tick opened a meeting, by action type, read from the recorded "
            "dispositions; tick rows recorded without dispositions are not "
            "evaluable.",
            ("recorded action dispositions",),
        ),
        "rebuttal_beneficiaries": TableSpec(
            "Who received the rebuttal, and who had accused them",
            _REBUTTALS,
            "Repeat-speaker turns by the speaker's seat (the opener, or another "
            "crewmate or impostor) and the role of the speaker of the turn answered.",
            ("meeting row turns",),
            scope=BOUNDED_REBUTTAL,
        ),
        "retally_outcome_changes": TableSpec(
            "Outcomes a re-tally changes",
            _BALLOTS,
            "Meetings whose re-tally differs from the recorded outcome, by re-tally, "
            "by the recorded outcome (the reporter, another crewmate, an impostor or "
            "no one ejected) and by what the re-tally gives instead. Every other "
            "ballot is held fixed; real voters would have heard different speech.",
            ("MeetingTriggered", "meeting row ballots"),
        ),
        "held_kill_next_meeting_outcomes": TableSpec(
            "What the next meeting did after a held kill",
            _BALLOTS,
            "Held crew-witnessed kills by how many of the kill's crew witnesses were "
            "alive at the next meeting, one or two or more, and by what that "
            "meeting did: ejected the killer, ejected one of those witnesses, "
            "ejected another player, or ejected no one. Every row is listed.",
            ("Killed", "meeting row"),
        ),
        "skips_by_grounding_label": TableSpec(
            "SKIP ballots by grounding label",
            _BALLOTS,
            "Every SKIP ballot by its recorded grounding label. Every label the "
            "meeting layer can write is listed, and unlabelled counts a ballot "
            "recorded before ballots were labelled.",
            ("meeting row ballots",),
        ),
        "holds_nothing_skips_by_source": TableSpec(
            "Where a holds-nothing SKIP's prompt names a living candidate",
            _HELD,
            "SKIP ballots labelled as holding nothing, by each place in the voter's "
            "own recorded ballot prompt that names a living candidate: an "
            "observation row; an observation row whose id was perceived after the "
            "previous meeting (after the game began, at its first meeting); an "
            "evidence row; a flag; a typed turn line; a spoken turn line. One SKIP "
            "can name a candidate in several places, so the rows overlap and do not "
            "add up to the cell. Every place is listed.",
            _HELD_PROMPT_READS,
        ),
        "cited_placements_by_kind_and_verdict": TableSpec(
            "Cited placements of the target, by kind and by what the route makes "
            "of them",
            _HELD,
            "Every placement of the target in the cited turn of a supported EJECT, "
            "by its kind and by whether the engine route makes it true or false at "
            "its kind's own clock, or cannot verify it. A whereabouts claim for a "
            "tick is read at that tick and the one before it; a sighting at the two "
            "ticks before the tick it names. The edge row counts a false placement "
            "the route makes true one tick before its window, so a clock off by "
            "one shows there rather than widening either window. Every row is "
            "listed.",
            _CITED_LINE_READS,
        ),
        "supported_ejects_not_checkable_by_reason": TableSpec(
            "Supported EJECTs whose cited line cannot be checked, by reason",
            _HELD,
            "EJECT ballots labelled supported that neither cell above counts: the "
            "ballot cites no turn, only the voter's own observation; the cited "
            "turn, if it is one of this meeting's, places the target nowhere "
            "checkable; or the route cannot verify any cited placement. Every row "
            "is listed.",
            _CITED_LINE_READS,
        ),
        "games_by_ending": TableSpec(
            "Games by ending",
            _SHAPE,
            "Games by the recorded reason they ended. Every ending the engine or "
            "the runner can record is listed; a game with no recorded ending is "
            "not evaluable.",
            ("game over row",),
        ),
        "kills_per_game": TableSpec(
            "Kills per game",
            _SHAPE,
            "Games by how many kills they held.",
            _KILL,
        ),
        "ticks_between_kills": TableSpec(
            "Ticks between consecutive kills",
            _SHAPE,
            "Each kill after a game's first, by the ticks since the kill before it "
            "in the same game.",
            _KILL,
        ),
        "ticks_from_kill_to_report": TableSpec(
            "Ticks from a kill to the meeting that reported its body",
            _SHAPE,
            "Every kill by the ticks from it to the report meeting whose reported "
            "body is its victim's, a meeting on the kill's own tick included, or "
            "by its body never being reported. A body joins its kill by victim, so "
            "two kills on one tick each keep their own row.",
            ("Killed", "MeetingTriggered"),
        ),
        "living_players_at_game_over_by_ending": TableSpec(
            "Living players at game over, by ending",
            _SHAPE,
            "Games by their recorded ending and the players still alive when it "
            "ended: every player less those killed and those ejected.",
            ("game over row", "Killed", "meeting row"),
        ),
        "tasks_left_at_game_over_by_ending": TableSpec(
            "Tasks left at game over, by ending",
            _SHAPE,
            "Games by their recorded ending and the share of all task instances "
            "still unfinished on the final state.",
            ("game over row", "final state"),
        ),
        "sabotages_started_per_game": TableSpec(
            "Sabotages started per game",
            _SHAPE,
            "Games by how many times a sabotage went from inactive to active "
            "between one play tick and the next. A sabotage that stays active "
            "across a meeting is one start.",
            ("state before the tick",),
        ),
        "report_openers_by_witness": TableSpec(
            "Who found the body",
            _SHAPE,
            "Report meetings by whether their opener was among the recorded "
            "witnesses of some kill since the previous meeting (since the game "
            "began, at its first meeting), and by the ticks from the reported "
            "body's kill to the report. Every row is listed.",
            ("Killed", "MeetingTriggered"),
        ),
        "copresence_share_per_game": TableSpec(
            "How often a player stood with exactly one other",
            _SHAPE,
            "Games by the share of their player-ticks, each a living player standing "
            "in a room before a play tick, on which exactly one other living player "
            "stood in the same room. A player inside a vent stands in no room.",
            ("state before the tick",),
        ),
    }
)


# ---------------------------------------------------------------------------
# The fold
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CellCount:
    numerator: int = 0
    denominator: int = 0
    not_evaluable: int = 0

    def __add__(self, other: CellCount) -> CellCount:
        return CellCount(
            self.numerator + other.numerator,
            self.denominator + other.denominator,
            self.not_evaluable + other.not_evaluable,
        )


@dataclass(frozen=True)
class CensusTally:
    """Every count one group contributes; groups pool by addition."""

    label: str
    sources: tuple[str, ...]
    era: EraKey
    games: int
    meetings: int
    cells: Mapping[str, CellCount]
    tables: Mapping[str, Mapping[str, int]]
    table_not_evaluable: Mapping[str, int]


@dataclass
class _Accumulator:
    """The fold's working counts. Local to one :func:`fold_set` call."""

    label: str
    values: Mapping[str, SettingValue]
    cells: dict[str, list[int]] = field(
        default_factory=lambda: {key: [0, 0, 0] for key in CELLS}
    )
    tables: dict[str, Counter[str]] = field(
        default_factory=lambda: {key: Counter() for key in TABLES}
    )
    table_not_evaluable: dict[str, int] = field(
        default_factory=lambda: {key: 0 for key in TABLES}
    )

    def count(self, key: str, hit: bool, *, seed: int, where: str) -> None:
        """Add one denominator entry to ``key``; a hit adds to the numerator.

        A hit on a cell whose setting predicate holds is a breach and raises. A
        cell whose scope does not hold for this group counts nothing.
        """

        if not _in_scope(CELLS[key].scope, self.values):
            return
        cell = self.cells[key]
        cell[1] += 1
        if not hit:
            return
        guard = CELLS[key].guard
        if guard is not None and guard.holds(self.values):
            raise GameplayCensusConformanceError(
                f"{CELLS[key].title} must be 0 by construction while "
                f"{guard.describe()}, but set {self.label}, seed {seed}, {where} "
                "breaches it"
            )
        cell[0] += 1

    def not_evaluable(self, key: str) -> None:
        self.cells[key][2] += 1

    def tally(self, name: str, row: str, amount: int = 1) -> None:
        """Add ``amount`` to one row; a table out of scope counts nothing."""

        if not _in_scope(TABLES[name].scope, self.values):
            return
        self.tables[name][row] += amount


def fold_set(inputs: CensusInputs) -> CensusTally:
    """Fold one set's carrier into counts. Pure: reads nothing but ``inputs``."""

    era = resolve_era(tuple(game.era for game in inputs.games))
    if era != inputs.era:
        raise GameplayCensusEraError(
            f"set {inputs.label}: its games' era disagrees with the set's recorded era"
        )
    acc = _Accumulator(label=inputs.label, values=era.values)
    meetings = 0
    for game in inputs.games:
        meetings += len(game.meetings)
        _fold_game(game, inputs, acc)
    return CensusTally(
        label=inputs.label,
        sources=(inputs.source,),
        era=era,
        games=len(inputs.games),
        meetings=meetings,
        cells=MappingProxyType(
            {key: CellCount(*counts) for key, counts in acc.cells.items()}
        ),
        tables=MappingProxyType(
            {key: MappingProxyType(dict(rows)) for key, rows in acc.tables.items()}
        ),
        table_not_evaluable=MappingProxyType(dict(acc.table_not_evaluable)),
    )


def pool(tallies: Sequence[CensusTally], *, label: str) -> CensusTally:
    """Pool disjoint groups by ADDING counts; refuse groups of different eras."""

    era = resolve_era(tuple(tally.era for tally in tallies))
    cells: dict[str, CellCount] = {key: CellCount() for key in CELLS}
    tables: dict[str, Counter[str]] = {key: Counter() for key in TABLES}
    not_evaluable: dict[str, int] = {key: 0 for key in TABLES}
    for tally in tallies:
        for key, count in tally.cells.items():
            cells[key] = cells[key] + count
        for key, rows in tally.tables.items():
            tables[key].update(rows)
        for key, value in tally.table_not_evaluable.items():
            not_evaluable[key] += value
    return CensusTally(
        label=label,
        sources=tuple(source for tally in tallies for source in tally.sources),
        era=era,
        games=sum(tally.games for tally in tallies),
        meetings=sum(tally.meetings for tally in tallies),
        cells=MappingProxyType(cells),
        tables=MappingProxyType(
            {key: MappingProxyType(dict(rows)) for key, rows in tables.items()}
        ),
        table_not_evaluable=MappingProxyType(not_evaluable),
    )


def _crew(game: GameFacts, players: Iterable[PlayerId]) -> frozenset[PlayerId]:
    """The crewmates among ``players``. A player with no recorded role raises."""

    return frozenset(pid for pid in players if game.roles[pid] == "CREWMATE")


def _is_impostor(game: GameFacts, player: PlayerId) -> bool:
    """Whether ``player`` is an impostor. A player with no recorded role raises."""

    return game.roles[player] == "IMPOSTOR"


def _teammates(game: GameFacts, player: PlayerId) -> frozenset[PlayerId]:
    if not _is_impostor(game, player):
        return frozenset()
    return frozenset(
        pid for pid, role in game.roles.items() if role == "IMPOSTOR" and pid != player
    )


@dataclass(frozen=True)
class _Trip:
    close_tick: int
    close: Literal["exit", "regroup", "ejected", "game_end"]
    ticks_inside: int
    exit: VentFact | None


def _trips(game: GameFacts) -> tuple[_Trip, ...]:
    """Every vent trip: entry to exit, or to the regroup, ejection or game end.

    Ticks inside count play ticks since the entry, restarting at a meeting
    boundary: a trip open across a meeting at tick ``m`` counts from ``m``.
    """

    meeting_ticks = tuple(meeting.tick for meeting in game.meetings)
    closers: dict[int, MeetingFact] = {
        meeting.tick: meeting for meeting in game.meetings
    }
    trips: list[_Trip] = []
    open_entry: dict[PlayerId, int] = {}

    def inside(entry_tick: int, close_tick: int) -> int:
        anchor = max([entry_tick, *(t for t in meeting_ticks if t < close_tick)])
        return close_tick - anchor

    events: list[tuple[int, int, VentFact | MeetingFact]] = [
        (vent.tick, 0, vent) for vent in game.vents
    ]
    events.extend((meeting.tick, 1, meeting) for meeting in game.meetings)
    for tick, _order, item in sorted(events, key=lambda row: (row[0], row[1])):
        if isinstance(item, VentFact):
            if item.kind == "entry":
                if item.actor in open_entry:
                    raise ValueError(
                        f"seed {game.seed}: {item.actor} entered a vent twice at {tick}"
                    )
                open_entry[item.actor] = tick
                continue
            entry_tick = open_entry.pop(item.actor, None)
            if entry_tick is None:
                raise ValueError(
                    f"seed {game.seed}: {item.actor} left a vent never entered at {tick}"
                )
            trips.append(_Trip(tick, "exit", inside(entry_tick, tick), item))
            continue
        meeting = closers[tick]
        for actor in sorted(open_entry):
            reason: Literal["regroup", "ejected"] | None = None
            if meeting.ejected == actor:
                reason = "ejected"
            elif meeting.regrouped:
                reason = "regroup"
            if reason is None:
                continue
            entry_tick = open_entry.pop(actor)
            trips.append(_Trip(tick, reason, inside(entry_tick, tick), None))
    end = game.terminal_tick
    for entry_tick in open_entry.values():
        trips.append(_Trip(end, "game_end", inside(entry_tick, end), None))
    return tuple(trips)


def _frame(game: GameFacts, tick: int) -> Frame:
    frame = game.frames.get(tick)
    if frame is None:
        raise ValueError(f"seed {game.seed}: no recorded state before tick {tick}")
    return frame


def _inferred_visible(
    room: RoomId, frame: Frame, neighbours: Mapping[RoomId, tuple[RoomId, ...]]
) -> frozenset[RoomId]:
    """What an impostor inside the vent in ``room`` infers it can see.

    Its own room plus the map's neighbours, or its own room alone while any
    sabotage is active. This is the policy's own inference, never the engine's
    visibility set.
    """

    if frame.sabotage_active:
        return frozenset({room})
    return frozenset({room, *neighbours[room]})


def _fold_game(game: GameFacts, inputs: CensusInputs, acc: _Accumulator) -> None:
    _fold_cooldown_writes(game, inputs, acc)
    _fold_witnesses(game, acc)
    _fold_trips(game, inputs, acc)
    _fold_meetings(game, inputs, acc)
    _fold_rebuttals(game, acc)
    _fold_ballots(game, acc)
    _fold_held_data(game, acc)
    _fold_game_shape(game, acc)
    for discarded in game.discarded:
        acc.tally("actions_thrown_away_on_trigger_ticks", discarded.action_type)
    acc.table_not_evaluable["actions_thrown_away_on_trigger_ticks"] += (
        game.rows_without_dispositions
    )
    if game.winner is None:
        acc.not_evaluable("impostor_wins")
    else:
        acc.count(
            "impostor_wins",
            game.winner == "IMPOSTORS",
            seed=game.seed,
            where="the game over row",
        )


def _fold_cooldown_writes(
    game: GameFacts, inputs: CensusInputs, acc: _Accumulator
) -> None:
    """Check every cooldown write against the set's recorded kill cooldown."""

    for write in game.cooldown_writes:
        acc.tally("kill_cooldown_writes_by_writer", write.writer)
        acc.count(
            "kill_cooldowns_differing_from_recorded",
            write.ticks != inputs.kill_cooldown_ticks,
            seed=game.seed,
            where=(
                f"the {write.writer} write of {write.player}'s cooldown at tick "
                f"{write.tick} ({write.ticks} against {inputs.kill_cooldown_ticks})"
            ),
        )


def _fold_witnesses(game: GameFacts, acc: _Accumulator) -> None:
    for kill in game.kills:
        acc.count(
            "kills_seen_by_crew",
            bool(_crew(game, kill.witnesses)),
            seed=game.seed,
            where=f"tick {kill.tick}",
        )
    for vent in game.vents:
        seen_from_source = bool(_crew(game, vent.source_witnesses))
        seen_from_destination = bool(_crew(game, vent.destination_witnesses))
        where = f"tick {vent.tick}"
        if vent.kind == "entry":
            acc.count(
                "vent_entries_seen_by_crew",
                seen_from_source or seen_from_destination,
                seed=game.seed,
                where=where,
            )
            continue
        acc.count(
            "vent_exits_seen_by_crew",
            seen_from_source or seen_from_destination,
            seed=game.seed,
            where=where,
        )
        acc.count(
            "vent_exits_seen_from_exit_room",
            seen_from_destination,
            seed=game.seed,
            where=where,
        )
        acc.count(
            "vent_exits_seen_only_from_room_left",
            seen_from_source and not seen_from_destination,
            seed=game.seed,
            where=where,
        )
    ejected = {meeting.ejected for meeting in game.meetings if meeting.ejected}
    for player, role in sorted(game.roles.items()):
        if role != "IMPOSTOR":
            continue
        acts = [vent for vent in game.vents if vent.actor == player]
        if not acts:
            key = "impostors_never_vented_ejected"
        elif any(
            _crew(game, vent.source_witnesses | vent.destination_witnesses)
            for vent in acts
        ):
            key = "impostors_seen_venting_ejected"
        else:
            key = "impostors_vented_unseen_ejected"
        acc.count(key, player in ejected, seed=game.seed, where=f"player {player}")


def _own_fresh_kill_before(game: GameFacts, entry: VentFact) -> bool:
    meeting_ticks = [meeting.tick for meeting in game.meetings]
    return any(
        kill.killer == entry.actor
        and kill.room == entry.source_room
        and entry.tick - FRESH_KILL_WINDOW_TICKS <= kill.tick < entry.tick
        and not any(kill.tick <= tick < entry.tick for tick in meeting_ticks)
        for kill in game.kills
    )


def _fold_trips(game: GameFacts, inputs: CensusInputs, acc: _Accumulator) -> None:
    for vent in game.vents:
        if vent.kind != "entry":
            continue
        acc.count(
            "vent_entries_not_after_own_fresh_kill",
            not _own_fresh_kill_before(game, vent),
            seed=game.seed,
            where=f"tick {vent.tick}",
        )
    trips = _trips(game)
    for trip in trips:
        acc.count(
            "trips_closed_by_regroup",
            trip.close == "regroup",
            seed=game.seed,
            where=f"tick {trip.close_tick}",
        )
        if trip.ticks_inside > 1:
            acc.count(
                "trips_longer_than_cap",
                trip.ticks_inside > IN_VENT_CAP_TICKS,
                seed=game.seed,
                where=f"tick {trip.close_tick}",
            )
        exit_fact = trip.exit
        if exit_fact is None:
            continue
        where = f"tick {exit_fact.tick}"
        acc.tally("ticks_inside_per_trip", str(trip.ticks_inside))
        acc.count(
            "forced_surfacings",
            trip.ticks_inside == IN_VENT_CAP_TICKS,
            seed=game.seed,
            where=where,
        )
        frame = _frame(game, exit_fact.tick)
        # Every player in the state is looked up before any count, so a player
        # without a recorded role raises before the exit policy's guard is read.
        crew_rooms = {
            room
            for player, room in frame.rooms.items()
            if game.roles[player] == "CREWMATE"
        }
        teammates = _teammates(game, exit_fact.actor)
        visible = _inferred_visible(exit_fact.source_room, frame, inputs.neighbours)
        in_view = any(
            room in visible
            for player, room in frame.rooms.items()
            if player != exit_fact.actor and player not in teammates
        )
        acc.count(
            "surfacings_before_cap_in_view",
            trip.ticks_inside < IN_VENT_CAP_TICKS and in_view,
            seed=game.seed,
            where=where,
        )
        acc.count(
            "vent_exits_into_occupied_room",
            exit_fact.destination_room in crew_rooms,
            seed=game.seed,
            where=where,
        )
        acc.count(
            "vent_exits_into_visibly_occupied_room",
            exit_fact.destination_room in crew_rooms
            and exit_fact.destination_room in visible,
            seed=game.seed,
            where=where,
        )
        acc.count(
            "vent_exits_while_room_left_occupied",
            exit_fact.source_room in crew_rooms,
            seed=game.seed,
            where=where,
        )
        if exit_fact.source_room == exit_fact.destination_room:
            acc.count(
                "in_place_surfacings_near_crew",
                _crew_arrives_before_walk_out(game, exit_fact),
                seed=game.seed,
                where=where,
            )
    exits = [vent for vent in game.vents if vent.kind == "exit"]
    for kill in game.kills:
        acc.count(
            "kills_soon_after_surfacing",
            any(
                vent.actor == kill.killer
                and 0 < kill.tick - vent.tick <= SHORT_WINDOW_TICKS
                for vent in exits
            ),
            seed=game.seed,
            where=f"tick {kill.tick}",
        )


def _crew_arrives_before_walk_out(game: GameFacts, exit_fact: VentFact) -> bool:
    """Whether a crewmate stands in the room before the surfaced impostor leaves.

    Reads the states after the surfacing tick, in order, while the impostor is
    still in that room and out of the vent, looking up the role of every player
    in each state it reads.
    """

    tick = exit_fact.tick + 1
    while tick in game.frames:
        frame = game.frames[tick]
        if frame.rooms.get(exit_fact.actor) != exit_fact.destination_room:
            return False
        crew_rooms = {
            room
            for player, room in frame.rooms.items()
            if game.roles[player] == "CREWMATE"
        }
        if exit_fact.destination_room in crew_rooms:
            return True
        tick += 1
    return False


def _fold_meetings(game: GameFacts, inputs: CensusInputs, acc: _Accumulator) -> None:
    bodies = {body.body_id: body for body in game.bodies}
    previous: MeetingFact | None = None
    for index, meeting in enumerate(game.meetings):
        where = f"meeting {meeting.meeting_id}"
        seed = game.seed
        acc.tally("meetings_by_trigger", meeting.trigger_kind)
        is_report = meeting.trigger_kind == "report"
        if is_report:
            if meeting.trigger_body is None or meeting.trigger_body not in bodies:
                raise ValueError(
                    f"seed {seed}, {where}: the reported corpse joins to no kill"
                )
            body = bodies[meeting.trigger_body]
            acc.tally("corpse_age_at_report", str(meeting.tick - body.kill_tick))
            floor_before = (
                {body_id for body_id, _ in previous.bodies_at_open}
                if previous is not None
                else set()
            )
            acc.count(
                "stale_report_meetings",
                meeting.trigger_body in floor_before,
                seed=seed,
                where=where,
            )
            acc.count(
                "skipped_report_meetings",
                meeting.outcome != "EJECTED",
                seed=seed,
                where=where,
            )
            if previous is not None and previous.regrouped:
                acc.count(
                    "report_corpses_older_than_last_close",
                    body.kill_tick <= previous.tick,
                    seed=seed,
                    where=where,
                )
        acc.count(
            "meetings_opening_with_another_unreported_corpse",
            any(
                body_id != meeting.trigger_body and discovered_by is None
                for body_id, discovered_by in meeting.bodies_at_open
            ),
            seed=seed,
            where=where,
        )
        impostors_inside = {
            player for player in meeting.in_vent_at_open if _is_impostor(game, player)
        }
        acc.count(
            "meetings_opening_with_impostor_in_vent",
            bool(impostors_inside),
            seed=seed,
            where=where,
        )
        for player, cooldown in meeting.impostor_cooldowns_at_open:
            acc.count(
                "impostor_cooldown_zero_at_open",
                cooldown == 0,
                seed=seed,
                where=f"{where}, player {player}",
            )
        if meeting.phase_after == "PLAY":
            acc.count(
                "play_resumes_with_impostor_in_vent",
                bool(meeting.in_vent_after),
                seed=seed,
                where=where,
            )
            acc.count(
                "play_resumes_with_corpse",
                bool(meeting.bodies_after),
                seed=seed,
                where=where,
            )
        _fold_vent_proof(game, meeting, acc)
        if is_report:
            _fold_report_seats(game, meeting, acc)
        for held in meeting.regroup_notices_held:
            acc.count(
                "prompts_missing_a_regroup_notice", not held, seed=seed, where=where
            )
        _fold_structure(game, meeting, acc)
        next_tick = (
            game.meetings[index + 1].tick if index + 1 < len(game.meetings) else None
        )
        after = [
            kill
            for kill in game.kills
            if meeting.tick < kill.tick
            and (next_tick is None or kill.tick <= next_tick)
        ]
        for kill in after:
            acc.count(
                "post_meeting_kills_soon_after",
                kill.tick - meeting.tick <= SHORT_WINDOW_TICKS,
                seed=seed,
                where=f"tick {kill.tick}",
            )
        if meeting.regrouped:
            _fold_regroup(game, meeting, after, next_tick, inputs, acc)
        previous = meeting


def _fold_regroup(
    game: GameFacts,
    meeting: MeetingFact,
    after: Sequence[KillFact],
    next_tick: int | None,
    inputs: CensusInputs,
    acc: _Accumulator,
) -> None:
    where = f"meeting {meeting.meeting_id}"
    acc.count(
        "sabotage_active_at_regroup",
        meeting.sabotage_active,
        seed=game.seed,
        where=where,
    )
    for kind, count in meeting.trigger_tick_dropped_events:
        acc.tally("trigger_tick_events_dropped_by_regroup", kind, count)
    for kill in after:
        acc.count(
            "kills_in_grace_window_after_regroup",
            kill.tick - meeting.tick <= inputs.kill_cooldown_ticks,
            seed=game.seed,
            where=f"tick {kill.tick} after {where}",
        )
    following = next(
        (other for other in game.meetings if other.tick == next_tick), None
    )
    if following is None or following.trigger_kind != "emergency":
        return
    witnessed = any(following.opener in kill.witnesses for kill in after)
    acc.count(
        "kill_witness_button_calls_soon_after_regroup",
        witnessed and following.tick - meeting.tick <= BUTTON_COOLDOWN_TICKS,
        seed=game.seed,
        where=f"meeting {following.meeting_id}",
    )


def _vent_flag_names(meeting: MeetingFact, player: PlayerId) -> bool:
    return any(player in subjects for subjects in meeting.vent_flag_subjects)


def _has_vent_proof(meeting: MeetingFact) -> bool:
    """Whether a vent-sighting flag names a player alive when the meeting opened."""

    return any(subjects & meeting.living for subjects in meeting.vent_flag_subjects)


def seat_class(game: GameFacts, meeting: MeetingFact, player: PlayerId) -> str:
    """``player``'s seat class at a report meeting: the reporter first.

    The reporter's seat is the reporter's whatever its role, so the three
    classes partition the living seats even when an impostor reports. Any other
    seat is classed by its recorded role; a player without one raises.
    """

    if player == meeting.opener:
        return _REPORTER_SEAT
    return _IMPOSTOR_SEAT if _is_impostor(game, player) else _OTHER_CREWMATE_SEAT


def _fold_report_seats(
    game: GameFacts, meeting: MeetingFact, acc: _Accumulator
) -> None:
    """Every living seat at one report meeting, and whether it was ejected."""

    proof = _has_vent_proof(meeting)
    for player in sorted(meeting.living):
        where = f"meeting {meeting.meeting_id}, seat {player}"
        ejected = meeting.ejected == player
        total, without_proof, with_proof = _SEAT_CELLS[
            seat_class(game, meeting, player)
        ]
        acc.count(total, ejected, seed=game.seed, where=where)
        acc.count(
            with_proof if proof else without_proof,
            ejected,
            seed=game.seed,
            where=where,
        )
        if _is_impostor(game, player):
            continue
        is_reporter = player == meeting.opener
        acc.count(
            "reporters_among_crewmate_seats", is_reporter, seed=game.seed, where=where
        )
        if ejected:
            acc.count(
                "reporters_among_ejected_crewmates",
                is_reporter,
                seed=game.seed,
                where=where,
            )


def _fold_vent_proof(game: GameFacts, meeting: MeetingFact, acc: _Accumulator) -> None:
    where = f"meeting {meeting.meeting_id}"
    seed = game.seed
    proof = _has_vent_proof(meeting)
    acc.count("meetings_with_vent_proof", proof, seed=seed, where=where)
    if meeting.trigger_kind == "emergency":
        acc.count("button_meetings_with_vent_proof", proof, seed=seed, where=where)
    ejected = meeting.ejected
    if not proof:
        acc.count(
            "meetings_without_vent_proof_ejecting",
            ejected is not None,
            seed=seed,
            where=where,
        )
        if ejected is not None:
            acc.count(
                "ejections_without_vent_proof_of_impostors",
                _is_impostor(game, ejected),
                seed=seed,
                where=where,
            )
    if ejected is None:
        return
    in_band = _vent_flag_names(meeting, ejected)
    impostor = _is_impostor(game, ejected)
    acc.count("role_correct_ejections", impostor, seed=seed, where=where)
    if not impostor:
        acc.count("vent_band_crew_ejections", in_band, seed=seed, where=where)
        return
    acc.count("vent_band_impostor_ejections", in_band, seed=seed, where=where)
    acc.count(
        "impostor_ejections_without_vent_proof", not proof, seed=seed, where=where
    )
    if not in_band:
        return
    prior = [
        vent
        for vent in game.vents
        if vent.actor == ejected and vent.tick <= meeting.tick
    ]
    seen_exit = any(
        vent.kind == "exit"
        and _crew(game, vent.source_witnesses | vent.destination_witnesses)
        for vent in prior
    )
    seen_entry = any(
        vent.kind == "entry"
        and _crew(game, vent.source_witnesses | vent.destination_witnesses)
        for vent in prior
    )
    moment = (
        "both"
        if seen_exit and seen_entry
        else "exit only"
        if seen_exit
        else "entry only"
        if seen_entry
        else "neither"
    )
    acc.tally("vent_band_by_moment", moment)
    sightings: set[str] = set()
    for vent in prior:
        if _crew(game, vent.source_witnesses) & meeting.living:
            sightings.add(f"{vent.kind} from the room left")
        if _crew(game, vent.destination_witnesses) & meeting.living:
            sightings.add(f"{vent.kind} from the room entered")
    acc.count(
        "vent_band_resting_only_on_room_left",
        bool(sightings) and sightings <= {"exit from the room left"},
        seed=seed,
        where=where,
    )


def _repeat_turns(meeting: MeetingFact) -> tuple[TurnFact, ...]:
    spoken: set[PlayerId] = set()
    repeats: list[TurnFact] = []
    for turn in sorted(meeting.turns, key=lambda item: item.index):
        if turn.speaker in spoken:
            repeats.append(turn)
        spoken.add(turn.speaker)
    return tuple(repeats)


def _fold_structure(game: GameFacts, meeting: MeetingFact, acc: _Accumulator) -> None:
    where = f"meeting {meeting.meeting_id}"
    seed = game.seed
    opener = meeting.opener
    turns = sorted(meeting.turns, key=lambda item: item.index)
    acc.count(
        "first_reply_accuses_opener",
        len(turns) > 1 and opener in turns[1].accusations,
        seed=seed,
        where=where,
    )
    first_charge = next(
        (
            position
            for position, turn in enumerate(turns)
            if turn.speaker != opener and opener in turn.accusations
        ),
        None,
    )
    acc.count(
        "opener_accused_after_opening",
        first_charge is not None,
        seed=seed,
        where=where,
    )
    acc.count(
        "opener_speaks_again",
        sum(1 for turn in turns if turn.speaker == opener) > 1,
        seed=seed,
        where=where,
    )
    if first_charge is not None:
        acc.count(
            "accused_opener_answers",
            any(turn.speaker == opener for turn in turns[first_charge + 1 :]),
            seed=seed,
            where=where,
        )
    repeats = _repeat_turns(meeting)
    acc.count("meetings_with_repeat_speaker", bool(repeats), seed=seed, where=where)
    acc.count(
        "meetings_with_second_repeat_speaker",
        len(repeats) > 1,
        seed=seed,
        where=where,
    )
    acc.count("impostor_openers", _is_impostor(game, opener), seed=seed, where=where)
    if meeting.trigger_kind == "report":
        if meeting.opener_prompt_has_kill_tick_handle is None:
            acc.not_evaluable("report_openings_with_kill_tick_handle")
        else:
            acc.count(
                "report_openings_with_kill_tick_handle",
                meeting.opener_prompt_has_kill_tick_handle,
                seed=seed,
                where=where,
            )
    ejected = meeting.ejected
    if ejected is not None and not _is_impostor(game, ejected):
        acc.count(
            "openers_among_innocent_ejections",
            ejected == opener,
            seed=seed,
            where=where,
        )
        if ejected == opener:
            acc.tally("innocent_opener_ejections_by_trigger", meeting.trigger_kind)


def _fold_rebuttals(game: GameFacts, acc: _Accumulator) -> None:
    for meeting in game.meetings:
        where = f"meeting {meeting.meeting_id}"
        seed = game.seed
        by_id = {turn.turn_id: turn for turn in meeting.turns}
        repeats = _repeat_turns(meeting)
        if repeats:
            first = repeats[0]
            acc.count(
                "rebuttals_differing_from_selector",
                meeting.selector_pick != (first.speaker, first.reply_to),
                seed=seed,
                where=where,
            )
            rebuttal_ids = frozenset(turn.turn_id for turn in repeats)
            for ballot in meeting.ballots:
                voter_where = f"{where}, voter {ballot.voter}"
                acc.count(
                    "ballots_citing_a_rebuttal",
                    ballot.primary_reason_id in rebuttal_ids,
                    seed=seed,
                    where=voter_where,
                )
                acc.count(
                    "ballots_countering_with_a_rebuttal",
                    ballot.counter_reason_id in rebuttal_ids,
                    seed=seed,
                    where=voter_where,
                )
        for turn in repeats:
            earlier = {
                other.speaker for other in meeting.turns if other.index < turn.index
            }
            has_alibi = any(alibi.subject == turn.speaker for alibi in turn.alibis)
            has_whereabouts = any(
                observation.kind == "whereabouts" for observation in turn.observations
            )
            has_sighting = any(
                observation.kind in _SIGHTING_KINDS for observation in turn.observations
            )
            acc.count("rebuttals_with_alibi", has_alibi, seed=seed, where=where)
            acc.count(
                "rebuttals_with_whereabouts", has_whereabouts, seed=seed, where=where
            )
            acc.count("rebuttals_with_sighting", has_sighting, seed=seed, where=where)
            acc.count(
                "rebuttals_redirect_only",
                bool(turn.accusations)
                and not (has_alibi or has_whereabouts or has_sighting),
                seed=seed,
                where=where,
            )
            for target in turn.accusations:
                acc.count(
                    "rebuttal_accusations_against_earlier_speakers",
                    target in earlier,
                    seed=seed,
                    where=where,
                )
            answered = by_id.get(turn.reply_to) if turn.reply_to is not None else None
            accuser = (
                "no recorded turn"
                if answered is None
                else _ROLE_WITH_ARTICLE[game.roles[answered.speaker]]
            )
            seat = (
                "the opener"
                if turn.speaker == meeting.opener
                else "another impostor"
                if _is_impostor(game, turn.speaker)
                else "another crewmate"
            )
            acc.tally("rebuttal_beneficiaries", f"{seat}, answering {accuser}")
            if turn.speaker != meeting.opener:
                continue
            charged = {
                tick
                for observation in (answered.observations if answered else ())
                if observation.subject == meeting.opener
                for tick in range(observation.from_tick, observation.to_tick + 1)
            }
            if not charged:
                acc.not_evaluable("opener_rebuttals_answering_charged_tick")
                continue
            answers = any(
                leg_from <= tick <= leg_to
                for alibi in turn.alibis
                if alibi.subject == turn.speaker
                for _room, leg_from, leg_to in alibi.legs
                for tick in charged
            ) or any(
                (
                    observation.kind == "whereabouts"
                    or observation.kind in _SIGHTING_KINDS
                )
                and observation.from_tick in charged
                for observation in turn.observations
            )
            acc.count(
                "opener_rebuttals_answering_charged_tick",
                answers,
                seed=seed,
                where=where,
            )


def _own_kill_row_breaches(game: GameFacts, row: OwnKillRowFact) -> bool:
    """Whether one served own-kill row breaches the own-kill row setting.

    The row names its killer, so a row naming the holder's fellow impostor is a
    breach whatever it cites. Any other row must cite, by the holder's own
    observation id, a kill the named player made on that tick with the holder
    among its witnesses. The ballot card specifies that every own-kill row cites
    its kill, so a row citing nothing joins no kill and is a breach too. The
    holder's and the subject's roles are both looked up, so a row naming a
    player without a recorded role raises.
    """

    holder_is_impostor = _is_impostor(game, row.holder)
    subject_is_impostor = _is_impostor(game, row.subject)
    if holder_is_impostor and subject_is_impostor and row.subject != row.holder:
        return True
    if row.citation_id is None:
        return True
    match = _OBSERVATION_ID_RE.match(row.citation_id)
    if match is None or match["agent"] != row.holder:
        return True
    engine_tick = int(match["tick"]) - AGENT_CLOCK_OFFSET
    return not any(
        kill.tick == engine_tick
        and kill.killer == row.subject
        and row.holder in kill.witnesses
        for kill in game.kills
    )


def grounding_labels() -> tuple[str, ...]:
    """Every grounding label the meeting layer writes, read from its type.

    Read at call time from :data:`meetings.schemas.BallotGroundingLabel`, so the
    label table's rows and the vocabulary check follow the type, never a copy.
    """

    return tuple(get_args(BallotGroundingLabel))


def _tally_ballots(
    game: GameFacts, meeting: MeetingFact, tally: str
) -> tuple[BallotFact, ...]:
    """The meeting's ballots under one tally: as recorded, or one re-tally.

    A re-tally changes impostor ballots only, reading each as SKIP or removing
    it; every other ballot is held fixed. An unknown tally raises.
    """

    if tally == AS_RECORDED:
        return meeting.ballots
    if tally == IMPOSTOR_BALLOTS_AS_SKIP:
        return tuple(
            replace(ballot, target=SKIP_TARGET)
            if _is_impostor(game, ballot.voter)
            else ballot
            for ballot in meeting.ballots
        )
    if tally == IMPOSTOR_BALLOTS_REMOVED:
        return tuple(
            ballot for ballot in meeting.ballots if not _is_impostor(game, ballot.voter)
        )
    raise ValueError(f"no tally is named {tally!r}")


def tally_outcome(
    ballots: Sequence[BallotFact], floor: float
) -> tuple[MeetingOutcome, PlayerId | None]:
    """``ballots`` tallied by the game's own function at the confidence ``floor``."""

    return tally_ballots(
        tuple(
            VoteBallot(
                voter=ballot.voter,
                target=ballot.target,
                confidence=ballot.confidence,
                primary_reason_id=None,
                rationale_text="",
            )
            for ballot in ballots
        ),
        skip_confidence_threshold=floor,
    )


def retally(
    game: GameFacts, meeting: MeetingFact
) -> Mapping[str, tuple[MeetingOutcome, PlayerId | None]]:
    """The meeting's outcome under the recorded tally and each re-tally.

    Every tally runs at the meeting's recorded confidence floor.
    """

    return MappingProxyType(
        {
            tally: tally_outcome(
                _tally_ballots(game, meeting, tally), meeting.ballot_floor
            )
            for tally in (AS_RECORDED, *RETALLY_VARIANTS)
        }
    )


def _recorded_outcome_class(game: GameFacts, meeting: MeetingFact) -> str:
    """Who the meeting ejected, by seat: the reporter first, whatever its role."""

    ejected = meeting.ejected
    if ejected is None:
        return "no one ejected"
    if meeting.trigger_kind == "report" and ejected == meeting.opener:
        return "the reporter ejected"
    return (
        "an impostor ejected"
        if _is_impostor(game, ejected)
        else "another crewmate ejected"
    )


def _retally_result_class(recorded: PlayerId | None, result: PlayerId | None) -> str:
    """What a re-tally that changed the outcome gives instead."""

    if result is None:
        return "no one ejected"
    return "someone ejected" if recorded is None else "a different player ejected"


def _fold_retally(game: GameFacts, meeting: MeetingFact, acc: _Accumulator) -> None:
    """Hold the recorded tally to the outcome, then count what each re-tally undoes."""

    where = f"meeting {meeting.meeting_id}"
    outcomes = retally(game, meeting)
    recorded = (meeting.outcome, meeting.ejected)
    if outcomes[AS_RECORDED] != recorded:
        tallied_outcome, tallied_ejected = outcomes[AS_RECORDED]
        raise GameplayCensusConformanceError(
            "The recorded ballots, tallied by the game's own function at the "
            "recorded confidence floor, must give the recorded outcome, but set "
            f"{acc.label}, seed {game.seed}, {where} breaches it: the tally gives "
            f"{tallied_outcome} {tallied_ejected} against the recorded "
            f"{meeting.outcome} {meeting.ejected}"
        )
    recorded_class = _recorded_outcome_class(game, meeting)
    for variant in RETALLY_VARIANTS:
        _, result = outcomes[variant]
        if meeting.ejected is not None:
            acc.count(
                _UNDONE_CELLS[variant],
                result != meeting.ejected,
                seed=game.seed,
                where=where,
            )
        if result != meeting.ejected:
            acc.tally(
                "retally_outcome_changes",
                f"{variant}: {recorded_class} -> "
                f"{_retally_result_class(meeting.ejected, result)}",
            )


def _witness_outcome_row(
    kill: KillFact, alive: frozenset[PlayerId], following: MeetingFact
) -> str:
    """One held kill's row: its living crew witnesses and the next meeting's act."""

    band = _WITNESS_BANDS[0] if len(alive) == 1 else _WITNESS_BANDS[1]
    ejected = following.ejected
    if ejected == kill.killer:
        outcome = _NEXT_MEETING_OUTCOMES[0]
    elif ejected in alive:
        outcome = _NEXT_MEETING_OUTCOMES[1]
    elif ejected is not None:
        outcome = _NEXT_MEETING_OUTCOMES[2]
    else:
        outcome = _NEXT_MEETING_OUTCOMES[3]
    return f"{band}: {outcome}"


def _fold_ballots(game: GameFacts, acc: _Accumulator) -> None:
    labels = grounding_labels()
    # Every label row and every witness row is listed, at zero when nothing
    # lands in it, so each table always shows its whole shape.
    for listed_label in (*labels, UNLABELLED):
        acc.tally("skips_by_grounding_label", listed_label, 0)
    for outcome_row in WITNESS_OUTCOME_ROWS:
        acc.tally("held_kill_next_meeting_outcomes", outcome_row, 0)
    for meeting in game.meetings:
        where = f"meeting {meeting.meeting_id}"
        seed = game.seed
        for ballot in meeting.ballots:
            # Every voter, and every recorded target but SKIP, is looked up, so
            # a player without a recorded role raises. The authored target is
            # only tested for membership: a rewritten one may name no player.
            eject = ballot.target != "SKIP"
            voter_is_impostor = _is_impostor(game, ballot.voter)
            target_is_impostor = eject and _is_impostor(game, ballot.target)
            voter_where = f"{where}, voter {ballot.voter}"
            label = ballot.grounding_label
            if label is not None and label not in labels:
                raise ValueError(
                    f"set {acc.label}, seed {seed}, {voter_where}: the grounding "
                    f"label {label!r} is not one the meeting layer writes"
                )
            if not eject:
                acc.count(
                    "skips_holding_nothing",
                    label == HOLDS_NOTHING_LABEL,
                    seed=seed,
                    where=voter_where,
                )
                acc.tally(
                    "skips_by_grounding_label", UNLABELLED if label is None else label
                )
            if not voter_is_impostor:
                continue
            acc.count("impostor_skip_ballots", not eject, seed=seed, where=voter_where)
            acc.count("impostor_eject_ballots", eject, seed=seed, where=voter_where)
            if eject:
                acc.count(
                    "impostor_ejects_labelled_supported",
                    ballot.grounding_label == "supported",
                    seed=seed,
                    where=voter_where,
                )
            acc.count(
                "recorded_teammate_ballot_targets",
                target_is_impostor and ballot.target != ballot.voter,
                seed=seed,
                where=voter_where,
            )
            acc.count(
                "authored_teammate_ballot_targets",
                ballot.authored_target in _teammates(game, ballot.voter),
                seed=seed,
                where=voter_where,
            )
        if meeting.ejected is not None:
            confident = [
                ballot.voter
                for ballot in meeting.ballots
                if ballot.target == meeting.ejected
                and ballot.confidence >= meeting.ballot_floor
            ]
            acc.count(
                "ejections_carried_only_by_impostor_ballots",
                bool(confident)
                and all(_is_impostor(game, voter) for voter in confident),
                seed=seed,
                where=where,
            )
        ballots_by_voter = {ballot.voter: ballot for ballot in meeting.ballots}
        for row in meeting.own_kill_rows:
            row_where = f"{where}, holder {row.holder}"
            acc.count(
                "own_kill_rows_breaching",
                _own_kill_row_breaches(game, row),
                seed=seed,
                where=row_where,
            )
            held = ballots_by_voter.get(row.holder)
            acc.count(
                "own_kill_rows_cited_by_holder",
                held is not None
                and row.citation_id is not None
                and held.cited_observation_id == row.citation_id,
                seed=seed,
                where=row_where,
            )
        _fold_retally(game, meeting, acc)
    for kill in game.kills:
        witnesses = _crew(game, kill.witnesses)
        if not witnesses:
            continue
        following = next(
            (meeting for meeting in game.meetings if meeting.tick >= kill.tick), None
        )
        if following is None:
            acc.not_evaluable("crew_witnessed_kills_held_at_next_meeting")
            continue
        alive = witnesses & following.living
        where = f"meeting {following.meeting_id}"
        acc.count(
            "crew_witnessed_kills_held_at_next_meeting",
            bool(alive),
            seed=game.seed,
            where=where,
        )
        if not alive:
            continue
        acc.count(
            "held_kill_witnesses_voting_killer",
            any(
                ballot.voter in alive and ballot.target == kill.killer
                for ballot in following.ballots
            ),
            seed=game.seed,
            where=where,
        )
        acc.count(
            "held_kill_killers_ejected",
            following.ejected == kill.killer,
            seed=game.seed,
            where=where,
        )
        acc.count(
            "held_kill_killers_ejected_at_any_later_meeting",
            any(
                later.ejected == kill.killer
                for later in game.meetings
                if later.tick >= kill.tick
            ),
            seed=game.seed,
            where=where,
        )
        acc.count(
            "held_kill_witnesses_ejected",
            following.ejected in alive,
            seed=game.seed,
            where=where,
        )
        acc.tally(
            "held_kill_next_meeting_outcomes",
            _witness_outcome_row(kill, alive, following),
        )


# ---------------------------------------------------------------------------
# What a ballot held: the holds-nothing check and the truth of the cited line
# ---------------------------------------------------------------------------


def held_source_rows() -> tuple[HeldSource, ...]:
    """Every place the holds-nothing check reads, read from its type."""

    rows: tuple[HeldSource, ...] = get_args(HeldSource)
    return rows


def placement_verdicts() -> tuple[PlacementVerdict, ...]:
    """Every verdict the route gives one cited placement, read from its type."""

    verdicts: tuple[PlacementVerdict, ...] = get_args(PlacementVerdict)
    return verdicts


def checked_placement_kinds() -> tuple[CheckedPlacementKind, ...]:
    """Every placement kind the cited-line check reads, read from its type."""

    kinds: tuple[CheckedPlacementKind, ...] = get_args(CheckedPlacementKind)
    return kinds


def route_rooms(
    game: GameFacts,
    player: PlayerId,
    tick: int,
    window: Sequence[tuple[RouteFrame, int]],
) -> tuple[RoomId, ...]:
    """``player``'s rooms on the route at each frame and offset of ``window``.

    A frame tick the route does not hold, or a player it does not hold there,
    contributes nothing, as in the honesty instrument.
    """

    frames: Mapping[RouteFrame, Mapping[int, Mapping[PlayerId, RoomId]]] = {
        "settled": game.settled_rooms,
        "resolved": game.resolved_rooms,
    }
    rooms: list[RoomId] = []
    for frame, offset in window:
        room = frames[frame].get(tick - offset, {}).get(player)
        if room is not None:
            rooms.append(room)
    return tuple(rooms)


def edge_window(kind: CheckedPlacementKind) -> tuple[tuple[RouteFrame, int], ...]:
    """The settled frame one tick before ``kind``'s window opens."""

    return (("settled", max(offset for _, offset in PLACEMENT_WINDOWS[kind]) + 1),)


def placement_verdict(game: GameFacts, placement: PlacementFact) -> PlacementVerdict:
    """What the route makes of one placement, at its kind's own clock.

    False only when the placement's canonical rooms intersect none of the
    player's rooms in the window, by the honesty instrument's own comparison;
    a placement with no canonical room, or with no route room in the window, is
    unverifiable, never false.
    """

    rooms = route_rooms(
        game, placement.player, placement.tick, PLACEMENT_WINDOWS[placement.kind]
    )
    if not placement.rooms or not rooms:
        return "unverifiable"
    return "false" if _contradicts(placement.rooms, rooms) else "true"


def true_at_the_edge(game: GameFacts, placement: PlacementFact) -> bool:
    """Whether the route makes ``placement`` true one tick before its window."""

    rooms = route_rooms(
        game, placement.player, placement.tick, edge_window(placement.kind)
    )
    return bool(placement.rooms and rooms) and not _contradicts(placement.rooms, rooms)


def _fold_held_data(game: GameFacts, acc: _Accumulator) -> None:
    """Fold the holds-nothing check and the truth of every cited line."""

    # Every row is listed, at zero when nothing lands in it.
    for source in held_source_rows():
        acc.tally("holds_nothing_skips_by_source", source, 0)
    for kind in checked_placement_kinds():
        for verdict in (*placement_verdicts(), EDGE_VERDICT):
            acc.tally("cited_placements_by_kind_and_verdict", f"{kind}: {verdict}", 0)
    for reason in NOT_CHECKABLE_REASONS:
        acc.tally("supported_ejects_not_checkable_by_reason", reason, 0)
    for meeting in game.meetings:
        for ballot in meeting.ballots:
            where = f"meeting {meeting.meeting_id}, voter {ballot.voter}"
            if ballot.target == SKIP_TARGET:
                _fold_holds_nothing(ballot, acc, seed=game.seed, where=where)
            elif ballot.held_sources is not None:
                raise ValueError(
                    f"set {acc.label}, seed {game.seed}, {where}: an EJECT carries "
                    "the holds-nothing check"
                )
            elif ballot.grounding_label == "supported":
                _fold_cited_line(game, meeting, ballot, acc, where=where)


def _fold_holds_nothing(
    ballot: BallotFact, acc: _Accumulator, *, seed: int, where: str
) -> None:
    """Count one SKIP's holds-nothing check, when it is labelled as holding nothing."""

    sources = ballot.held_sources
    if ballot.grounding_label != HOLDS_NOTHING_LABEL:
        if sources is not None:
            raise ValueError(
                f"set {acc.label}, seed {seed}, {where}: a SKIP not labelled as "
                "holding nothing carries the holds-nothing check"
            )
        return
    if sources is None:
        acc.not_evaluable("holds_nothing_skips_naming_no_candidate")
        acc.not_evaluable("holds_nothing_skips_naming_a_candidate")
        return
    unknown = sorted(set(sources) - set(held_source_rows()))
    if unknown:
        raise ValueError(
            f"set {acc.label}, seed {seed}, {where}: {unknown} are not places the "
            "holds-nothing check reads"
        )
    acc.count(
        "holds_nothing_skips_naming_no_candidate",
        not sources,
        seed=seed,
        where=where,
    )
    acc.count(
        "holds_nothing_skips_naming_a_candidate",
        bool(sources),
        seed=seed,
        where=where,
    )
    for source in sources:
        acc.tally("holds_nothing_skips_by_source", source)


def _fold_cited_line(
    game: GameFacts,
    meeting: MeetingFact,
    ballot: BallotFact,
    acc: _Accumulator,
    *,
    where: str,
) -> None:
    """Read one supported EJECT's cited turn against the route."""

    reasons = "supported_ejects_not_checkable_by_reason"
    if ballot.primary_reason_id is None:
        acc.tally(reasons, NOT_CHECKABLE_REASONS[0])
        return
    cited = next(
        (turn for turn in meeting.turns if turn.turn_id == ballot.primary_reason_id),
        None,
    )
    placements = (
        ()
        if cited is None
        else tuple(spot for spot in cited.placements if spot.player == ballot.target)
    )
    if not placements:
        acc.tally(reasons, NOT_CHECKABLE_REASONS[1])
        return
    verdicts: list[PlacementVerdict] = []
    for placement in placements:
        verdict = placement_verdict(game, placement)
        verdicts.append(verdict)
        acc.tally(
            "cited_placements_by_kind_and_verdict", f"{placement.kind}: {verdict}"
        )
        if verdict == "false" and true_at_the_edge(game, placement):
            acc.tally(
                "cited_placements_by_kind_and_verdict",
                f"{placement.kind}: {EDGE_VERDICT}",
            )
    checkable = [verdict for verdict in verdicts if verdict != "unverifiable"]
    if not checkable:
        acc.tally(reasons, NOT_CHECKABLE_REASONS[2])
        return
    false = "false" in checkable
    acc.count("cited_lines_true_to_the_route", not false, seed=game.seed, where=where)
    acc.count("cited_lines_false_to_the_route", false, seed=game.seed, where=where)


# ---------------------------------------------------------------------------
# The shape of a game: role-blind and descriptive
# ---------------------------------------------------------------------------


def game_endings() -> tuple[str, ...]:
    """Every ending the engine or the runner records, read from their types."""

    return (*get_args(WinResultType), *get_args(GameStopReason))


def tick_gap_rows() -> tuple[str, ...]:
    """Every tick-gap bucket, in order."""

    return (*(label for label, _ in TICK_GAP_BUCKETS), LONG_GAP)


def tick_gap_bucket(gap: int) -> str:
    """The bucket of a gap of ``gap`` ticks; a negative gap raises."""

    if gap < 0:
        raise ValueError(f"a gap of {gap} ticks runs backwards")
    for label, most in TICK_GAP_BUCKETS:
        if gap <= most:
            return label
    return LONG_GAP


def share_bucket(part: int, whole: int) -> str:
    """The bucket of the share ``part`` of ``whole``; outside [0, whole] raises."""

    if whole <= 0 or not 0 <= part <= whole:
        raise ValueError(f"{part} of {whole} is not a share")
    for label, quarters in SHARE_BUCKETS:
        if part * SHARE_QUARTERS <= whole * quarters:
            return label
    raise ValueError(f"{part} of {whole} lands in no share bucket")


def _fold_game_shape(game: GameFacts, acc: _Accumulator) -> None:
    """Fold the ending, the kill cadence, the closeness at game over, the
    sabotages, who found each body, and how often players stood in pairs."""

    endings = game_endings()
    for ending in endings:
        acc.tally("games_by_ending", ending, 0)
    reason = game.end_reason
    if reason is not None and reason not in endings:
        raise ValueError(
            f"set {acc.label}, seed {game.seed}: the recorded ending {reason!r} is "
            "not one the engine or the runner records"
        )
    if reason is None:
        acc.table_not_evaluable["games_by_ending"] += 1
    else:
        acc.tally("games_by_ending", reason)
    _fold_kill_cadence(game, acc)
    _fold_closeness(game, acc)
    _fold_sabotage(game, acc)
    _fold_body_finders(game, acc)
    _fold_copresence(game, acc)


def _fold_kill_cadence(game: GameFacts, acc: _Accumulator) -> None:
    """Kills per game, the gaps between them, and each kill to its report."""

    for row in tick_gap_rows():
        acc.tally("ticks_between_kills", row, 0)
        acc.tally("ticks_from_kill_to_report", row, 0)
    acc.tally("ticks_from_kill_to_report", NEVER_REPORTED, 0)
    acc.tally("kills_per_game", str(len(game.kills)))
    ticks = sorted(kill.tick for kill in game.kills)
    for earlier, later in zip(ticks, ticks[1:], strict=False):
        acc.tally("ticks_between_kills", tick_gap_bucket(later - earlier))
    bodies = {body.body_id: body for body in game.bodies}
    reports: dict[PlayerId, MeetingFact] = {}
    joinable = True
    for meeting in game.meetings:
        if meeting.trigger_kind != "report":
            continue
        # The meeting fold has already refused a corpse that joins no kill.
        reported = bodies[meeting.trigger_body or ""]
        if reported.victim is None:
            joinable = False
            continue
        reports.setdefault(reported.victim, meeting)
    for kill in game.kills:
        if kill.victim is None or not joinable:
            acc.table_not_evaluable["ticks_from_kill_to_report"] += 1
            continue
        report = reports.get(kill.victim)
        acc.tally(
            "ticks_from_kill_to_report",
            NEVER_REPORTED
            if report is None
            else tick_gap_bucket(report.tick - kill.tick),
        )


def _fold_closeness(game: GameFacts, acc: _Accumulator) -> None:
    """The living players and the tasks left when the game ended, by ending."""

    reason = game.end_reason
    living_table = "living_players_at_game_over_by_ending"
    tasks_table = "tasks_left_at_game_over_by_ending"
    if reason is None or any(kill.victim is None for kill in game.kills):
        acc.table_not_evaluable[living_table] += 1
    else:
        removed = {kill.victim for kill in game.kills} | {
            meeting.ejected for meeting in game.meetings if meeting.ejected is not None
        }
        living = len(set(game.roles) - removed)
        acc.tally(living_table, f"{reason}: {living} living")
    completed, total = game.final_tasks_completed, game.final_tasks_total
    if reason is None or completed is None or total is None or total == 0:
        acc.table_not_evaluable[tasks_table] += 1
        return
    acc.tally(tasks_table, f"{reason}: {share_bucket(total - completed, total)}")


def _fold_sabotage(game: GameFacts, acc: _Accumulator) -> None:
    """Sabotage starts, and task wins in games where a sabotage was in play."""

    starts = 0
    previous = False
    for tick in sorted(game.frames):
        active = game.frames[tick].sabotage_active
        if active and not previous:
            starts += 1
        previous = active
    acc.tally("sabotages_started_per_game", str(starts))
    if game.end_reason == TASK_WIN:
        acc.count(
            "task_wins_with_sabotage_in_play",
            starts > 0,
            seed=game.seed,
            where="the game over row",
        )


def _fold_body_finders(game: GameFacts, acc: _Accumulator) -> None:
    """Each report meeting by whether a kill witness opened it, and the gap."""

    table_key = "report_openers_by_witness"
    for opener in (_OPENER_WITNESS, _OPENER_OTHER):
        for row in tick_gap_rows():
            acc.tally(table_key, f"{opener}, {row}", 0)
    bodies = {body.body_id: body for body in game.bodies}
    previous_tick = -1
    for meeting in game.meetings:
        if meeting.trigger_kind == "report":
            # The meeting fold has already refused a corpse that joins no kill.
            reported = bodies[meeting.trigger_body or ""]
            witnessed = any(
                meeting.opener in kill.witnesses
                for kill in game.kills
                if previous_tick < kill.tick <= meeting.tick
            )
            opener = _OPENER_WITNESS if witnessed else _OPENER_OTHER
            gap = tick_gap_bucket(meeting.tick - reported.kill_tick)
            acc.tally(table_key, f"{opener}, {gap}")
        previous_tick = meeting.tick


def _fold_copresence(game: GameFacts, acc: _Accumulator) -> None:
    """The game's share of player-ticks spent with exactly one other player."""

    paired = 0
    player_ticks = 0
    for frame in game.frames.values():
        occupancy = Counter(frame.rooms.values())
        for room in frame.rooms.values():
            player_ticks += 1
            if occupancy[room] == 2:
                paired += 1
    if player_ticks == 0:
        acc.table_not_evaluable["copresence_share_per_game"] += 1
        return
    acc.tally("copresence_share_per_game", share_bucket(paired, player_ticks))


# ---------------------------------------------------------------------------
# The loader: the one impure step
# ---------------------------------------------------------------------------


#: The layers besides the engine whose later settings the census reads. Every
#: field in them is classified in :data:`FIELD_CLASSIFICATION`, and the fold
#: reads each as a recorded value. Where such a setting changes the walk itself,
#: the walk reads it from the recorded config: the meeting reset when it applies
#: a meeting's result, and the tactical options when it re-decides a format-3
#: recording's actions. The walk replays every recorded meeting and re-decides
#: none.
CENSUS_THREADED_LAYERS: Final[frozenset[ConfigLayer]] = frozenset(
    {"orchestrator", "tactical", "meeting"}
)

#: The census walk profile (module docstring, "The walk profile"): the
#: current-report profile plus three refusals, declaring its own layers rather
#: than inheriting the current-report profile's.
CENSUS_WALK_CONFIG: Final[ReplayWalkConfig] = replace(
    _CURRENT_REPORT_WALK_CONFIG,
    profile="gameplay-census",
    missing_meeting_row="violation",
    reject_duplicate_meeting_rows=True,
    require_terminal_tick=True,
    threaded_layers=CENSUS_THREADED_LAYERS,
)


def served_own_kill_rows(
    prompt: str, *, holder: PlayerId
) -> tuple[OwnKillRowFact, ...]:
    """The own-kill rows served to ``holder`` in one recorded prompt.

    Only rows in the exact wording of :data:`OWN_KILL_ROW_TEXT` are found. The
    prompt text never leaves this function: it returns ids, rooms and ticks.
    """

    if "KILL in" not in prompt:
        return ()
    return tuple(
        OwnKillRowFact(
            holder=holder,
            subject=match["subject"],
            room=match["room"],
            tick=int(match["tick"]),
            citation_id=match["citation"],
        )
        for match in _OWN_KILL_ROW_RE.finditer(prompt)
    )


def _manifest_prompt_cells(set_dir: Path) -> Mapping[int, str]:
    """``seed -> prompt_versions`` cell of the set's MANIFEST table.

    The prompt-versions column is the third cell in every table width the
    manifest writer has produced (seed, model, prompt versions, ...).
    """

    manifest = set_dir / "MANIFEST.md"
    if not manifest.is_file():
        raise FileNotFoundError(f"{set_dir}: no MANIFEST.md to read prompt stamps from")
    cells: dict[int, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        parts = [part.strip() for part in stripped.strip("|").split("|")]
        if len(parts) < 3 or not parts[0].isdigit():
            continue
        cells[int(parts[0])] = parts[2]
    return MappingProxyType(cells)


def prompt_stamps_from_cell(cell: str) -> tuple[str, ...]:
    """The stamps of a MANIFEST row whose game recorded a meeting.

    A cell that is not a comma-separated list of stamps (the writer's note for a
    game without meetings, for instance) raises: a game that recorded a meeting
    must name the prompts it was served.
    """

    stamps = tuple(stamp.strip() for stamp in cell.split(","))
    if any(not stamp or " " in stamp for stamp in stamps):
        raise ValueError("a MANIFEST row of a game with meetings names no prompt stamp")
    return tuple(sorted(stamps))


def _game_era(
    entries: Sequence[ReplayLogEntry], prompt_stamps: tuple[str, ...] | None
) -> EraKey:
    config = recorded_experiment_config(entries)
    values: dict[str, SettingValue] = (
        dict(config.model_dump(mode="json")) if config is not None else {}
    )
    flags = recorded_substrate_flags(entries)
    return EraKey(
        settings=canonical_settings(values),
        temporal_observation_version=recorded_temporal_observation_version(entries),
        substrate_flags=tuple(sorted(flags.items())) if flags is not None else None,
        prompt_stamps=prompt_stamps,
    )


def _frame_of(state: WorldState) -> Frame:
    return Frame(
        rooms=MappingProxyType(
            {
                pid: player.room
                for pid, player in state.players.items()
                if player.alive and not player.in_vent
            }
        ),
        sabotage_active=state.sabotage is not None and state.sabotage.active,
    )


def _turn_fact(turn: MeetingTurn) -> TurnFact:
    observations = tuple(
        ObservationFact(
            kind=observation.type,
            from_tick=(
                observation.from_tick
                if isinstance(observation, TaskActivityAccount)
                else observation.tick
            ),
            to_tick=(
                observation.to_tick
                if isinstance(observation, TaskActivityAccount)
                else observation.tick
            ),
            subject=getattr(observation, "subject", None),
        )
        for observation in turn.observations
    )
    return TurnFact(
        turn_id=turn.turn_id,
        index=turn.turn_index,
        speaker=turn.speaker,
        reply_to=turn.reply_to,
        accusations=tuple(
            claim.against for claim in turn.claims if isinstance(claim, AccusationClaim)
        ),
        observations=observations,
        alibis=tuple(
            AlibiFact(
                subject=claim.subject,
                legs=tuple(
                    (leg.room, leg.from_tick, leg.to_tick) for leg in claim.route
                ),
            )
            for claim in turn.claims
            if isinstance(claim, AlibiClaim)
        ),
        placements=turn_placements(turn),
    )


def turn_placements(turn: MeetingTurn) -> tuple[PlacementFact, ...]:
    """The turn's spoken placements of the kinds the cited-line check reads.

    A sighting places its subject in its room and each companion it lists there
    (once each, never the subject again); a movement sighting places its
    subject in the room it arrived in; a whereabouts claim places the speaker.
    A label with no canonical room places nobody. These are the placements the
    route-check replay's placement reader gives these four kinds, which a test
    holds equal on every committed meeting.
    """

    found: list[PlacementFact] = []
    for observation in turn.observations:
        # One dispatch over the kinds, the movement sighting among them.
        match observation:
            case SawPlayerObservation():
                rooms = canonical_rooms(observation.room)
                if not rooms:
                    continue
                found.append(
                    PlacementFact(
                        observation.subject, observation.tick, rooms, "saw_player"
                    )
                )
                companions = dict.fromkeys(
                    companion
                    for companion in observation.co_present
                    if companion != observation.subject
                )
                found.extend(
                    PlacementFact(companion, observation.tick, rooms, "company")
                    for companion in companions
                )
            case SawMoveObservation():
                rooms = canonical_rooms(observation.to_room)
                if rooms:
                    found.append(
                        PlacementFact(
                            observation.subject, observation.tick, rooms, "saw_move"
                        )
                    )
            case WhereaboutsClaim():
                rooms = canonical_rooms(observation.room)
                if rooms:
                    found.append(
                        PlacementFact(
                            turn.speaker, observation.tick, rooms, "whereabouts"
                        )
                    )
    return tuple(found)


def ballot_call(entry: MeetingReplayEntry, voter: PlayerId) -> LLMCallRecord | None:
    """The voter's last recorded call whose response validates as a ballot."""

    found: LLMCallRecord | None = None
    for call in entry.llm_calls:
        if call.agent_id != voter:
            continue
        try:
            VoteBallot.model_validate_json(call.response_text)
        except ValidationError:
            continue
        found = call
    return found


def ballot_prompt_blocks(prompt: str) -> Mapping[str, tuple[str, ...]]:
    """A recorded ballot prompt's top-level blocks: each tag's lines.

    A block opens on a line holding only its tag and closes on the line holding
    only its closing tag; inside it every other line is its content. A tag the
    census has not classified, a block opened twice or never closed, a closing
    tag outside a block, and a prompt without its memory or transcript block
    each raise. The prompt text never leaves the census loader.
    """

    known = READ_BALLOT_BLOCKS | UNREAD_BALLOT_BLOCKS
    blocks: dict[str, list[str]] = {}
    open_tag: str | None = None
    for line in prompt.splitlines():
        match = _BLOCK_TAG_RE.match(line)
        if open_tag is not None:
            if match is not None and match[1] == "/" and match[2] == open_tag:
                open_tag = None
            else:
                blocks[open_tag].append(line)
            continue
        if match is None:
            continue
        closing, tag = match[1], match[2]
        if closing:
            raise ValueError(f"the closing tag </{tag}> stands outside any block")
        if tag not in known:
            raise ValueError(f"the block <{tag}> is not one the census classifies")
        if tag in blocks:
            raise ValueError(f"the block <{tag}> opens twice")
        blocks[tag] = []
        open_tag = tag
    if open_tag is not None:
        raise ValueError(f"the block <{open_tag}> never closes")
    for required in ("memory", "transcript"):
        if required not in blocks:
            raise ValueError(f"the prompt holds no <{required}> block")
    return MappingProxyType({tag: tuple(lines) for tag, lines in blocks.items()})


def _memory_lines(
    lines: Sequence[str], *, since_tick: int
) -> Iterator[tuple[HeldSource, str]]:
    """Each line of the memory sections the check reads, with its place.

    An observation row whose id was perceived after ``since_tick`` is also an
    observation row perceived since the previous meeting. A heading in no row
    of :data:`MEMORY_SECTIONS`, or a line before the first heading, raises.
    """

    started = False
    section: HeldSource | None = None
    for line in lines:
        if line.startswith("## "):
            heading = line.split(":", 1)[0]
            if heading not in MEMORY_SECTIONS:
                raise ValueError(
                    f"the memory section {heading!r} is not one the census classifies"
                )
            started = True
            section = MEMORY_SECTIONS[heading]
            continue
        if not started:
            raise ValueError("a memory line stands before any section heading")
        if section is None:
            continue
        yield section, line
        if section == "an observation row":
            tag = _OBSERVATION_TAG_RE.search(line)
            if tag is not None and int(tag["tick"]) > since_tick:
                yield "an observation row perceived since the previous meeting", line


def _transcript_lines(lines: Sequence[str]) -> Iterator[tuple[HeldSource, str]]:
    """Each transcript line but the turn headers, as a typed or a spoken line.

    A line under a turn that opens no typed or spoken line continues the line
    before it. A line before any turn other than the empty transcript's note
    raises.
    """

    current: HeldSource | None = None
    for line in lines:
        if _TURN_HEADER_RE.match(line):
            current = None
            continue
        if line.startswith("  said: "):
            current = "a spoken turn line"
        elif line.startswith("  - ") or line in ("  saw:", "  claims:"):
            current = "a typed turn line"
        elif current is None:
            if line == "(no turns recorded)":
                continue
            raise ValueError("a transcript line stands outside any turn")
        yield current, line


def held_sources(
    prompt: str,
    *,
    voter: PlayerId,
    living: frozenset[PlayerId],
    since_tick: int,
) -> frozenset[HeldSource]:
    """The places in one recorded ballot prompt that name a living candidate.

    A living candidate is a player living at the meeting's open other than the
    voter, named as a whole token. Read: the memory's observation rows and open
    contradictions, the contradictions and evidence blocks, and every transcript
    line but the turn headers. Never read: every other memory section (the
    beliefs name every living player), every other block, and the page outside
    the blocks (the suspicion graph and the candidate list). Only place names
    leave this function.
    """

    candidates = living - {voter}
    blocks = ballot_prompt_blocks(prompt)
    lines: list[tuple[HeldSource, str]] = [
        *_memory_lines(blocks["memory"], since_tick=since_tick),
        *_transcript_lines(blocks["transcript"]),
        *(("a flag", line) for line in blocks.get("contradictions", ())),
        *(("an evidence row", line) for line in blocks.get("evidence", ())),
    ]
    return frozenset(
        source
        for source, line in lines
        if any(token in candidates for token in _PLAYER_TOKEN_RE.findall(line))
    )


def selector_pick(
    turns: Sequence[MeetingTurn], living: frozenset[PlayerId]
) -> tuple[PlayerId, str] | None:
    """The bounded-rebuttal selector's pick on the turns before the first repeat.

    ``None`` when no player speaks twice, or when the selector would choose no
    one on the turns before the first repeat-speaker turn.
    """

    spoken: set[PlayerId] = set()
    ordered = sorted(turns, key=lambda turn: turn.turn_index)
    for position, turn in enumerate(ordered):
        if turn.speaker in spoken:
            pick = select_bounded_rebuttal(
                MeetingTranscript(turns=tuple(ordered[:position])), living_ids=living
            )
            return None if pick is None else (pick.speaker, pick.reply_to)
        spoken.add(turn.speaker)
    return None


def regroup_notices_held(
    entry: MeetingReplayEntry, notices: Sequence[str]
) -> tuple[bool, ...]:
    """Per recorded call with an agent id: does its prompt carry every notice?

    ``notices`` are the earlier regroups' notices in the renderer's wording.
    Empty when no earlier regroup was announced, so a game's first meeting adds
    nothing to the count. The prompt text never leaves this function.
    """

    if not notices:
        return ()
    return tuple(
        all(notice in call.prompt for notice in notices)
        for call in entry.llm_calls
        if call.agent_id is not None
    )


def holds_nothing_check(
    entry: MeetingReplayEntry,
    ballot: VoteBallot,
    *,
    living: frozenset[PlayerId],
    since_tick: int,
    where: str,
) -> frozenset[HeldSource] | None:
    """One recorded ballot's holds-nothing check, or ``None`` when it has none.

    Only a SKIP labelled as holding nothing is checked, against the prompt of
    its voter's last recorded call whose response validates as a ballot. Such a
    SKIP without one, or with a prompt the check cannot read, raises naming
    ``where`` and the voter.
    """

    if ballot.target != SKIP_TARGET or ballot.grounding_label != HOLDS_NOTHING_LABEL:
        return None
    named = f"{where}, voter {ballot.voter}"
    call = ballot_call(entry, ballot.voter)
    if call is None:
        raise ValueError(
            f"{named}: a SKIP labelled as holding nothing has no recorded ballot call"
        )
    try:
        return held_sources(
            call.prompt, voter=ballot.voter, living=living, since_tick=since_tick
        )
    except ValueError as error:
        raise ValueError(f"{named}: {error}") from error


def _meeting_fact(
    opened: MeetingOpened,
    applied: MeetingApplied,
    *,
    regroup_recorded: bool,
    earlier_notices: Sequence[str] = (),
    previous_tick: int = 0,
    where: str = "",
) -> MeetingFact:
    entry = opened.entry
    state = opened.state
    if opened.trigger is None:
        raise ValueError(f"{entry.meeting_id}: a meeting tick with no trigger event")
    living = frozenset(pid for pid, player in state.players.items() if player.alive)
    meeting_where = f"{where}meeting {entry.meeting_id}"
    opener_calls = [
        call for call in entry.llm_calls if call.agent_id == entry.triggered_by
    ]
    rows: list[OwnKillRowFact] = []
    for call in entry.llm_calls:
        if call.agent_id is not None:
            rows.extend(served_own_kill_rows(call.prompt, holder=call.agent_id))
    dropped: Counter[str] = Counter(
        event.type
        for event in opened.events
        if isinstance(event, (MovedEvent, TaskProgressedEvent, TaskCompletedEvent))
    )
    after = applied.state
    return MeetingFact(
        meeting_id=entry.meeting_id,
        tick=entry.tick,
        trigger_kind=opened.trigger.trigger,
        opener=entry.triggered_by,
        trigger_body=opened.body_id,
        bodies_at_open=tuple(
            sorted(
                (body_id, body.discovered_by) for body_id, body in state.bodies.items()
            )
        ),
        in_vent_at_open=frozenset(
            pid
            for pid, player in state.players.items()
            if player.alive and player.in_vent
        ),
        impostor_cooldowns_at_open=tuple(
            sorted(
                (pid, value)
                for pid, value in state.cooldowns.items()
                if pid in living and state.players[pid].role == "IMPOSTOR"
            )
        ),
        living=living,
        sabotage_active=state.sabotage is not None and state.sabotage.active,
        outcome=entry.outcome,
        ejected=entry.ejected_player_id,
        vent_flag_subjects=tuple(
            frozenset(flag.subjects)
            for flag in entry.contradictions
            if flag.kind == "vent_sighting"
        ),
        turns=tuple(_turn_fact(turn) for turn in entry.transcript.turns),
        ballots=tuple(
            BallotFact(
                voter=ballot.voter,
                target=ballot.target,
                authored_target=(
                    ballot.guard_redirected_from
                    if ballot.guard_rewrite_reason is not None
                    else ballot.target
                ),
                confidence=ballot.confidence,
                grounding_label=ballot.grounding_label,
                cited_observation_id=ballot.primary_reason_observation_id,
                primary_reason_id=ballot.primary_reason_id,
                counter_reason_id=ballot.counter_reason_id,
                held_sources=holds_nothing_check(
                    entry,
                    ballot,
                    living=living,
                    since_tick=previous_tick,
                    where=meeting_where,
                ),
            )
            for ballot in entry.ballots
        ),
        ballot_floor=resolve_ballot_tally_threshold(entry),
        selector_pick=selector_pick(entry.transcript.turns, living),
        opener_prompt_has_kill_tick_handle=(
            KILL_TICK_BODY_HANDLE_PATTERN.search(opener_calls[0].prompt) is not None
            if opener_calls
            else None
        ),
        own_kill_rows=tuple(rows),
        trigger_tick_dropped_events=tuple(
            (kind, dropped[kind]) for kind in _REGROUP_DROPPED_KINDS if dropped[kind]
        ),
        phase_after=after.phase,
        in_vent_after=frozenset(
            pid
            for pid, player in after.players.items()
            if player.alive and player.in_vent
        ),
        bodies_after=frozenset(after.bodies),
        regrouped=regroup_recorded and after.phase == "PLAY",
        regroup_notices_held=regroup_notices_held(entry, earlier_notices),
    )


def _load_game(
    path: Path,
    *,
    seed: int,
    roles: Mapping[PlayerId, Role],
    manifest_cell: str,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    game_map: Map,
) -> GameFacts:
    entries: list[ReplayLogEntry] = []
    frames: dict[int, Frame] = {}
    kills: list[KillFact] = []
    vents: list[VentFact] = []
    bodies: list[BodyFact] = []
    discarded: list[DiscardedAction] = []
    rows_without_dispositions = 0
    applied_meetings: list[tuple[MeetingOpened, MeetingApplied]] = []
    cooldown_writes: list[CooldownWrite] = []
    settled_rooms: dict[int, Mapping[PlayerId, RoomId]] = {}
    resolved_rooms: dict[int, Mapping[PlayerId, RoomId]] = {}
    opened: MeetingOpened | None = None
    game_end: GameEndReplayEntry | None = None
    final_state: WorldState | None = None
    terminal_tick: int | None = None
    for event in walk_replay(
        path,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
        config=CENSUS_WALK_CONFIG,
    ):
        if isinstance(event, TickOpened):
            if not entries:
                cooldown_writes.extend(
                    _impostor_cooldowns(event.state, "round_start", event.state.tick)
                )
            entries.append(event.entry)
            frames[event.entry.tick] = _frame_of(event.state)
        elif isinstance(event, TickAdvanced):
            resolved_rooms[event.entry.tick] = settled_rooms[event.entry.tick] = (
                _rooms_of(event.state)
            )
            killed: dict[PlayerId, int] = {}
            for engine_event in event.events:
                if isinstance(engine_event, KilledEvent):
                    kills.append(
                        KillFact(
                            tick=engine_event.tick,
                            killer=engine_event.actor,
                            room=engine_event.room,
                            witnesses=frozenset(engine_event.witnesses),
                            victim=engine_event.target,
                        )
                    )
                    killed[engine_event.target] = engine_event.tick
                    cooldown_writes.append(
                        CooldownWrite(
                            writer="after_kill",
                            tick=engine_event.tick,
                            player=engine_event.actor,
                            ticks=event.state.cooldowns.get(engine_event.actor),
                        )
                    )
                elif isinstance(engine_event, (VentEnteredEvent, VentExitedEvent)):
                    vents.append(
                        VentFact(
                            tick=engine_event.tick,
                            actor=engine_event.actor,
                            kind=(
                                "entry"
                                if isinstance(engine_event, VentEnteredEvent)
                                else "exit"
                            ),
                            source_room=engine_event.source_room,
                            destination_room=engine_event.destination_room,
                            source_witnesses=frozenset(engine_event.source_witnesses),
                            destination_witnesses=frozenset(
                                engine_event.destination_witnesses
                            ),
                        )
                    )
            for body_id, body in event.state.bodies.items():
                if body_id in event.pre_state.bodies:
                    continue
                if body.player_id not in killed:
                    raise ValueError(
                        f"seed {seed}: a corpse appeared at tick {event.entry.tick} "
                        "with no kill of its victim on that tick"
                    )
                bodies.append(
                    BodyFact(
                        body_id=body_id,
                        kill_tick=killed[body.player_id],
                        victim=body.player_id,
                    )
                )
            dispositions = event.entry.action_dispositions
            if dispositions is None:
                rows_without_dispositions += 1
            else:
                discarded.extend(
                    DiscardedAction(tick=event.entry.tick, action_type=action.type)
                    for action, disposition in zip(
                        event.actions, dispositions, strict=True
                    )
                    if disposition == "discarded_by_meeting"
                )
        elif isinstance(event, MeetingOpened):
            opened = event
        elif isinstance(event, MeetingApplied):
            if opened is None or opened.entry.meeting_id != event.entry.meeting_id:
                raise ValueError(f"seed {seed}: a meeting applied without opening")
            applied_meetings.append((opened, event))
            # A meeting's tick is read from its applied state, as agents read it.
            settled_rooms[event.entry.tick] = _rooms_of(event.state)
            opened = None
        elif isinstance(event, WalkComplete):
            game_end = event.game_end
            final_state = event.state
            terminal_tick = event.terminal_tick
            if game_end is not None:
                entries.append(game_end)
    if terminal_tick is None or final_state is None:
        raise ValueError(f"seed {seed}: the walk never reached its terminal tick")
    stamps = prompt_stamps_from_cell(manifest_cell) if applied_meetings else None
    era = _game_era(entries, stamps)
    regroup_recorded = MEETING_REGROUP.holds(era.values)
    if regroup_recorded:
        for opened_meeting, applied in applied_meetings:
            if applied.state.phase == "PLAY":
                cooldown_writes.extend(
                    _impostor_cooldowns(
                        applied.state, "regroup", opened_meeting.entry.tick
                    )
                )
    # Each meeting reads the notices of the regroups before it in this game; a
    # regroup's notice is formed only when a later meeting reads it.
    meetings = tuple(
        _meeting_fact(
            opened_meeting,
            applied,
            regroup_recorded=regroup_recorded,
            earlier_notices=tuple(
                _regroup_notice(prior)
                for _, prior in applied_meetings[:index]
                if regroup_recorded and prior.state.phase == "PLAY"
            ),
            previous_tick=(applied_meetings[index - 1][1].entry.tick if index else 0),
            where=f"set {path.parent}, seed {seed}, ",
        )
        for index, (opened_meeting, applied) in enumerate(applied_meetings)
    )
    return GameFacts(
        seed=seed,
        roles=MappingProxyType(dict(roles)),
        era=era,
        kills=tuple(kills),
        vents=tuple(vents),
        bodies=tuple(bodies),
        frames=MappingProxyType(frames),
        meetings=meetings,
        discarded=tuple(discarded),
        rows_without_dispositions=rows_without_dispositions,
        winner=game_end.winner if game_end is not None else None,
        terminal_tick=terminal_tick,
        cooldown_writes=tuple(cooldown_writes),
        end_reason=game_end.reason if game_end is not None else None,
        final_tasks_completed=sum(
            1 for task in final_state.tasks.values() if task.completed
        ),
        final_tasks_total=len(final_state.tasks),
        settled_rooms=MappingProxyType(settled_rooms),
        resolved_rooms=MappingProxyType(resolved_rooms),
    )


def _rooms_of(state: WorldState) -> Mapping[PlayerId, RoomId]:
    """Every player's room on ``state``, the honesty instrument's route frame."""

    return MappingProxyType({pid: player.room for pid, player in state.players.items()})


def _regroup_notice(applied: MeetingApplied) -> str:
    """The notice the memory renders for the regroup ``applied``'s close made.

    The regroup's tick is the resumed state's, the tick the announced row
    records; its room is the one the walk regrouped the survivors into. A
    regroup the walk names no room for raises.
    """

    if applied.regroup_room is None:
        raise ValueError(
            f"{applied.entry.meeting_id}: the recorded reset regrouped the "
            "survivors, but the walk names no room they were placed in"
        )
    return REGROUP_NOTICE_TEXT.format(
        tick=applied.state.tick, room=applied.regroup_room
    )


def _impostor_cooldowns(
    state: WorldState, writer: CooldownWriter, tick: int
) -> tuple[CooldownWrite, ...]:
    """Every living impostor's kill cooldown on ``state``, as ``writer``'s writes."""

    return tuple(
        CooldownWrite(
            writer=writer, tick=tick, player=pid, ticks=state.cooldowns.get(pid)
        )
        for pid, player in sorted(state.players.items())
        if player.alive and player.role == "IMPOSTOR"
    )


def recorded_kill_cooldown(era: EraKey, game_map: Map) -> int:
    """The kill cooldown an era's games ran at: the recorded value, else the map's.

    Read through :func:`engine.world.resolve_kill_cooldown`, the engine's own
    rule, so the grace window and the cooldown cell follow the recording.
    """

    value = setting_value(era.values, "kill_cooldown_ticks")
    if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
        raise GameplayCensusFieldError(
            f"the recorded kill_cooldown_ticks={value!r} is not a tick count"
        )
    return resolve_kill_cooldown(game_map, value)


#: The checkout this module lies in. A walked directory inside it is named
#: relative to it, so a committed set reads ``replays/<set>`` on every machine.
_CHECKOUT_ROOT: Final[Path] = Path(__file__).resolve().parents[1]


def _walked_source(walked: Path) -> str:
    """The resolved directory a walk read, as the published section names it.

    Relative to the checkout when it lies inside it (a candidate at
    ``replays/candidates/<run>/9p2i`` reads that path), else absolute (a scratch
    copy outside the checkout).
    """

    if walked.is_relative_to(_CHECKOUT_ROOT):
        return walked.relative_to(_CHECKOUT_ROOT).as_posix()
    return walked.as_posix()


def load_census_inputs(set_dir: Path) -> CensusInputs:
    """Walk one replay set on the canonical map into the census carrier.

    The one impure step. Roles come from :func:`eval.validity.roles_by_seed`,
    the seeder the sample report takes them from. No model is called and
    nothing is written. The label and the source both name the directory
    actually walked, resolved: the label its two innermost names, the source its
    path (:func:`_walked_source`).
    """

    resolved_map = load_canonical_map()
    seeds = seeds_on_disk(set_dir)
    unseen = [seed for seed in seeds if seed in UNSEEN_SEED_BAND]
    if unseen:
        raise ValueError(
            f"{set_dir}: {len(unseen)} seed(s) in a band no census walk may read"
        )
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(set_dir)
    roles = roles_by_seed(
        set_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=resolved_map,
    )
    cells = _manifest_prompt_cells(set_dir)
    missing = [seed for seed in seeds if seed not in cells]
    if missing:
        raise ValueError(f"{set_dir}: {len(missing)} seed(s) have no MANIFEST row")
    games = tuple(
        _load_game(
            set_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            roles=roles[seed],
            manifest_cell=cells[seed],
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=resolved_map,
        )
        for seed in seeds
    )
    walked = set_dir.resolve()
    era = resolve_era(tuple(game.era for game in games))
    return CensusInputs(
        label=f"{walked.parent.name}/{walked.name}",
        source=_walked_source(walked),
        era=era,
        kill_cooldown_ticks=recorded_kill_cooldown(era, resolved_map),
        neighbours=MappingProxyType(
            {
                room: resolved_map.room_neighbors(room)
                for room in sorted(resolved_map.rooms)
            }
        ),
        games=games,
    )


# ---------------------------------------------------------------------------
# The published artifact
# ---------------------------------------------------------------------------

#: What the page says about itself before any number.
NOT_THE_SCORECARD_NOTE: Final[str] = (
    "This is not the process scorecard. The scorecard asks whether each decision "
    "rested on data the agent held; this census counts what happened in the games "
    "themselves. No cell here joins the scorecard, and nothing here is a gate."
)

#: The role-correctness demotion, stated wherever the census is read.
ROLE_CORRECTNESS_NOTE: Final[str] = (
    "Role-correctness is reported and gates nothing. Where a cell reads a role it "
    "is to describe the game, never to judge a decision, and nothing here feeds "
    "back to any agent or pushes one toward the correct answer."
)

#: How the counts were made.
COUNT_ONLY_NOTE: Final[str] = (
    "Every cell is a count over recordings already in the tree, made with zero "
    "model calls. The walk re-runs each game through the engine and verifies every "
    "recorded state hash; no prompt, speech or rationale text is copied into this "
    "report."
)

#: The terms the page uses, defined where it uses them.
TERMS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "opener": (
            "the player whose body report or button press opened a meeting; the "
            "opener speaks first."
        ),
        "trigger tick": (
            "the play tick on which a meeting opened. Actions submitted for that "
            "tick after the one that opened the meeting are thrown away unexecuted."
        ),
        "vent proof": (
            "a meeting's contradiction flag of the vent-sighting kind naming a "
            "player who was alive when the meeting opened."
        ),
        "vent band": (
            "the ejections whose ejected player such a vent-sighting flag names."
        ),
        "regroup": (
            "the optional meeting reset: when play resumes every survivor stands in "
            "the meeting room, corpses are cleared, no one is inside a vent and each "
            "impostor's kill cooldown restarts at the recorded kill cooldown, else the "
            "map's value."
        ),
        "grace window": (
            "the ticks after a regroup before the impostors' restarted kill cooldown "
            "runs out: from the tick after the meeting through the recorded kill "
            "cooldown, else the map's."
        ),
        "vent trip": (
            "an impostor's stay inside the vents, from its entry to its exit, or to "
            "the meeting or game end that closed it."
        ),
        "ticks inside": (
            "the play ticks a vent trip lasted, counting again from zero at a "
            "meeting the trip spanned."
        ),
        "in-vent cap": (
            f"{IN_VENT_CAP_TICKS} ticks inside: under the look-and-wait exit an "
            "impostor must surface at this count."
        ),
        "fresh kill": (
            f"the impostor's own victim, killed at most {FRESH_KILL_WINDOW_TICKS} "
            "ticks earlier in the same room, with no meeting in between."
        ),
        "inferred-visible rooms": (
            "the rooms an impostor inside a vent can infer it sees: the vent's own "
            "room and its map neighbours, or the own room alone while any sabotage "
            "is active. Never the engine's own visibility."
        ),
        "rebuttal": (
            "a turn by a player who already spoke in the same meeting; the only such "
            "turn the meeting layer can produce is the bounded rebuttal."
        ),
        "seat": (
            "one living player at one report meeting. The reporter's seat is the "
            "reporter's whatever its role; every other seat belongs to a crewmate "
            "or an impostor. A player dead before the meeting has no seat."
        ),
        "living witnesses": (
            "the crewmates the engine recorded as seeing a kill who are still alive "
            "at the next meeting, counted as one, or as two or more. A fellow "
            "impostor who saw the kill is never one of them."
        ),
        "held kill": (
            "a kill a crewmate saw whose crew witness is still alive when the next "
            "meeting opens, a meeting on the kill's own tick included."
        ),
        "re-tally": (
            "the meeting's recorded ballots counted again by the game's own vote "
            "count at the meeting's recorded confidence floor, with each impostor "
            "ballot read as a SKIP or removed. Every other ballot is held fixed, "
            "so a re-tally describes the ballots, not what the table would have "
            "done: real voters would have heard different speech."
        ),
        "holds-nothing label": (
            "the grounding label a SKIP ballot carries when its voter stated "
            "outright that it held nothing that resolves the vote. The label "
            "restates the voter's own statement; the holds-nothing check reads it "
            "against the lines the voter's own ballot prompt held."
        ),
        "living candidate": (
            "a player alive when the meeting opened, other than the voter: someone "
            "the voter's ballot could name."
        ),
        "holds-nothing check": (
            "whether a SKIP labelled as holding nothing was shown, in its own "
            "ballot prompt, a line naming a living candidate: an observation row "
            "of its memory, an open contradiction, an evidence row, or a typed or "
            "spoken turn line, never a turn's header naming its speaker, the "
            "beliefs section or the list of candidates, which name every living "
            "player. Such a line is held data, true or false. The label reads as "
            "nothing that resolves the vote, not as nothing held, and a line held "
            "is not a reason to vote."
        ),
        "cited line": (
            "the turn an EJECT ballot cites as its reason, read for its spoken "
            "placements of the ballot's target: a sighting of the target, the "
            "target seen as company in another's sighting, the target seen "
            "arriving in a room, or the target's own whereabouts claim."
        ),
        "checkable": (
            "a cited placement the engine route can verify: its room is a room of "
            "the map and the route holds the target at the ticks its kind is read "
            "at. A checkable placement is true when the route puts the target "
            "there at one of those ticks and false otherwise; a true cited line is "
            "not a correct vote, and a false one may still have been believed."
        ),
        "rebuttal citation": (
            "a ballot whose cited turn, or whose counter slot (the strongest thing "
            "the voter held pointing away from its choice), names a rebuttal of "
            "the same meeting."
        ),
        "era": (
            "the recorded settings a group of games shares: its experiment settings, "
            "its observation delivery version, its substrate-flag stamp and its "
            "prompt versions. Games of different eras are never pooled."
        ),
        "by construction": (
            "a count a recorded setting forces to zero. While the setting is on the "
            "census checks the count is zero and stops with an error naming the "
            "game and the meeting or tick if it is not, and the page says 0 by "
            "construction instead of presenting a measured improvement."
        ),
        "n/a": (
            "nothing to count, so no rate exists: either nothing of that kind "
            "happened, or the cell or table counts only games recorded with a "
            "setting these games were not recorded with."
        ),
    }
)

#: What each recorded setting a guard names does, in plain words.
SETTING_MEANINGS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "vent_witness_rule": (
            "who sees a vent exit: under physical, only the room surfaced into."
        ),
        "vent_entry_policy": (
            "when an impostor enters a vent: under own_fresh_kill, only at its own "
            "fresh kill."
        ),
        "vent_exit_policy": (
            "when an impostor surfaces: under look_and_wait, only when no "
            "non-teammate stands in its inferred-visible rooms, or at the in-vent cap."
        ),
        "meeting_reset": "what a meeting leaves behind: under hub_with_grace, a regroup.",
        "report_body_handle_version": (
            "how a report names the corpse: version 1 uses a handle without the "
            "death tick."
        ),
        "bounded_rebuttal_version": (
            "whether one extra turn goes to a player charged after speaking: "
            "version 1 grants it; unset grants none."
        ),
        "self_report": "whether an impostor may report a corpse: off means never.",
        "contextual_self_report_version": (
            "a situational impostor self-report: unset means never."
        ),
        "ballot_kill_row_version": (
            "whether a kill witness's ballot gets its own first-hand kill row: "
            "version 1 serves it."
        ),
    }
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CensusCell(_FrozenModel):
    """One published cell: its counts, its definition, its guard and its scope.

    ``rate`` is ``None`` iff the denominator is 0. ``by_construction`` names the
    setting predicate that forces the cell to zero for this group, when it holds;
    a published cell carrying it must count zero. ``scope`` names the setting
    predicate the cell is counted under, and ``in_scope`` says whether this
    group's era satisfies it; a cell out of its scope counts nothing, so it reads
    ``n/a``.
    """

    title: str
    heading: str
    definition: str
    reads: tuple[str, ...]
    numerator: int
    denominator: int
    not_evaluable: int
    rate: float | None
    guard: str | None
    by_construction: str | None
    scope: str | None
    in_scope: bool

    @model_validator(mode="after")
    def _counts_are_coherent(self) -> CensusCell:
        if min(self.numerator, self.denominator, self.not_evaluable) < 0:
            raise ValueError("census counts must be non-negative")
        if self.numerator > self.denominator:
            raise ValueError("numerator exceeds denominator")
        expected = (
            round(self.numerator / self.denominator, 6) if self.denominator else None
        )
        if self.rate != expected:
            raise ValueError(
                "rate must be its own counts' quotient, or None when empty"
            )
        if self.by_construction is not None and self.numerator:
            raise ValueError("a cell forced to zero by construction must count zero")
        if self.scope is None and not self.in_scope:
            raise ValueError("a cell without a scope is counted in every era")
        if not self.in_scope and (self.denominator or self.not_evaluable):
            raise ValueError("a cell out of its scope must count nothing")
        return self


class CensusTable(_FrozenModel):
    """One published table; ``scope`` and ``in_scope`` as on :class:`CensusCell`."""

    title: str
    heading: str
    definition: str
    reads: tuple[str, ...]
    counts: dict[str, int]
    not_evaluable: int
    scope: str | None
    in_scope: bool

    @model_validator(mode="after")
    def _scope_is_coherent(self) -> CensusTable:
        if self.scope is None and not self.in_scope:
            raise ValueError("a table without a scope is counted in every era")
        if not self.in_scope and (self.counts or self.not_evaluable):
            raise ValueError("a table out of its scope must count nothing")
        return self


class EraView(_FrozenModel):
    settings: dict[str, str | int | bool | None]
    temporal_observation_version: int | None
    substrate_flags: dict[str, bool] | None
    prompt_stamps: tuple[str, ...] | None


class CensusSection(_FrozenModel):
    label: str
    sources: tuple[str, ...]
    games: int
    meetings: int
    era: EraView
    cells: dict[str, CensusCell]
    tables: dict[str, CensusTable]


class CensusEra(_FrozenModel):
    """One recorded era of the committed sets, as the era registry names it.

    ``constants`` are the era's named windows (the grace window is its recorded
    kill cooldown, else the map's). ``pooled`` adds the counts of the era's sets
    when it holds more than one and is ``None`` for a one-set era, whose own
    section is its only reading; no pool crosses two eras.
    """

    era_id: str
    record: str
    recorded_on: str
    declared_config: str | None
    constants: dict[str, int]
    sets: tuple[str, ...]
    pooled: CensusSection | None


class GameplayCensus(_FrozenModel):
    schema_version: int
    not_the_scorecard_note: str
    role_correctness_note: str
    count_only_note: str
    terms: dict[str, str]
    setting_meanings: dict[str, str]
    field_classification: dict[str, str]
    eras: tuple[CensusEra, ...]
    sets: tuple[CensusSection, ...]


def _era_view(era: EraKey) -> EraView:
    return EraView(
        settings=dict(era.settings),
        temporal_observation_version=era.temporal_observation_version,
        substrate_flags=(
            dict(era.substrate_flags) if era.substrate_flags is not None else None
        ),
        prompt_stamps=era.prompt_stamps,
    )


def section_from_tally(tally: CensusTally) -> CensusSection:
    """One group's published section, in the registry's order."""

    values = tally.era.values
    cells: dict[str, CensusCell] = {}
    for key, spec in CELLS.items():
        count = tally.cells[key]
        holds = spec.guard is not None and spec.guard.holds(values)
        cells[key] = CensusCell(
            title=spec.title,
            heading=spec.heading,
            definition=spec.definition,
            reads=spec.reads,
            numerator=count.numerator,
            denominator=count.denominator,
            not_evaluable=count.not_evaluable,
            rate=(
                round(count.numerator / count.denominator, 6)
                if count.denominator
                else None
            ),
            guard=spec.guard.describe() if spec.guard is not None else None,
            by_construction=(
                spec.guard.describe() if spec.guard is not None and holds else None
            ),
            scope=spec.scope.describe() if spec.scope is not None else None,
            in_scope=_in_scope(spec.scope, values),
        )
    tables = {
        key: CensusTable(
            title=spec.title,
            heading=spec.heading,
            definition=spec.definition,
            reads=spec.reads,
            counts=dict(sorted(tally.tables[key].items(), key=_row_order)),
            not_evaluable=tally.table_not_evaluable[key],
            scope=spec.scope.describe() if spec.scope is not None else None,
            in_scope=_in_scope(spec.scope, values),
        )
        for key, spec in TABLES.items()
    }
    return CensusSection(
        label=tally.label,
        sources=tally.sources,
        games=tally.games,
        meetings=tally.meetings,
        era=_era_view(tally.era),
        cells=cells,
        tables=tables,
    )


def _row_order(item: tuple[str, int]) -> tuple[int, int, str]:
    """Numeric rows in numeric order, then the rest alphabetically."""

    key = item[0]
    return (0, int(key), "") if key.isdigit() else (1, 0, key)


def _field_classification_view() -> dict[str, str]:
    return {
        name: (
            "read by: " + ", ".join(use.predicates)
            if use.predicates
            else f"read as a value by: {use.value_read_by}"
            if use.value_read_by
            else f"not read: {use.reason}"
        )
        for name, use in FIELD_CLASSIFICATION.items()
    }


def _constants(kill_cooldown_ticks: int) -> dict[str, int]:
    """The named windows; the grace window is the recorded kill cooldown, else the map's."""

    return {
        "fresh_kill_window_ticks": FRESH_KILL_WINDOW_TICKS,
        "in_vent_cap_ticks": IN_VENT_CAP_TICKS,
        "grace_window_ticks": kill_cooldown_ticks,
        "button_cooldown_ticks": BUTTON_COOLDOWN_TICKS,
        "short_window_ticks": SHORT_WINDOW_TICKS,
    }


#: The committed sets in publication order, from the era registry.
CENSUS_SETS: Final[tuple[str, ...]] = tuple(entry.path for entry in REGISTERED_SETS)


def census_from_inputs(
    inputs: Sequence[CensusInputs],
    *,
    registry: Sequence[CommittedSet] = REGISTERED_SETS,
) -> GameplayCensus:
    """Fold every set, pool each era's sets inside that era, and publish.

    Each input's ``source`` must be a committed set ``registry`` names, and the
    registry decides its era. Pooling an era's sets raises
    :class:`GameplayCensusEraError` when their recorded keys differ, which is
    what a set filed under the wrong era does; no pool crosses two eras.
    """

    if not inputs:
        raise ValueError("no replay sets to fold")
    tallies = [fold_set(item) for item in inputs]
    by_source = {
        item.source: (item, tally) for item, tally in zip(inputs, tallies, strict=True)
    }
    if len(by_source) != len(inputs):
        raise ValueError("one set was given twice")
    eras: list[CensusEra] = []
    for era, members in era_groups([item.source for item in inputs], registry=registry):
        group = [by_source[source] for source in members]
        pooled = (
            pool([tally for _, tally in group], label=f"pooled: the {era.id} sets")
            if len(group) > 1
            else None
        )
        cooldowns = {item.kill_cooldown_ticks for item, _ in group}
        if len(cooldowns) != 1:
            raise GameplayCensusEraError(
                f"the {era.id} sets ran at different kill cooldowns (recorded, "
                "else the map's); the census never pools across eras"
            )
        eras.append(
            CensusEra(
                era_id=era.id,
                record=era.record,
                recorded_on=era.recorded_on,
                declared_config=era.declared_config,
                constants=_constants(cooldowns.pop()),
                sets=tuple(tally.label for _, tally in group),
                pooled=section_from_tally(pooled) if pooled is not None else None,
            )
        )
    return GameplayCensus(
        schema_version=SCHEMA_VERSION,
        not_the_scorecard_note=NOT_THE_SCORECARD_NOTE,
        role_correctness_note=ROLE_CORRECTNESS_NOTE,
        count_only_note=COUNT_ONLY_NOTE,
        terms=dict(TERMS),
        setting_meanings=dict(SETTING_MEANINGS),
        field_classification=_field_classification_view(),
        eras=tuple(eras),
        sets=tuple(section_from_tally(tally) for tally in tallies),
    )


def compute_gameplay_census(
    root: Path, *, load: Callable[[Path], CensusInputs] = load_census_inputs
) -> GameplayCensus:
    """Walk and fold the four committed sets. Zero model calls; writes nothing.

    ``load`` walks one set; a test hands it a cached walk of the same bytes.
    """

    return census_from_inputs([load(root / name) for name in CENSUS_SETS])


def recorded_game_eras(set_dir: Path) -> Mapping[int, EraKey]:
    """Every game's :class:`EraKey` in ``set_dir``, read without an engine walk.

    The key :func:`load_census_inputs` gives the same game: its recorded
    settings, temporal version and substrate stamp, plus the MANIFEST row's
    prompt stamps when the recording holds a meeting row. The rows alone are
    enough, because the key states what was recorded rather than what was played.
    """

    cells = _manifest_prompt_cells(set_dir)
    keys: dict[int, EraKey] = {}
    for seed in seeds_on_disk(set_dir):
        if seed in UNSEEN_SEED_BAND:
            raise ValueError(f"{set_dir}: a seed in a band no census read may touch")
        entries = read_all_entries(set_dir / f"replay-seed-{seed}.jsonl")
        held_meeting = any(isinstance(entry, MeetingReplayEntry) for entry in entries)
        if held_meeting and seed not in cells:
            raise ValueError(f"{set_dir}: seed {seed} has no MANIFEST row")
        stamps = prompt_stamps_from_cell(cells[seed]) if held_meeting else None
        keys[seed] = _game_era(entries, stamps)
    if not keys:
        raise ValueError(f"{set_dir}: no replay to read an era from")
    return MappingProxyType(keys)


def verify_era_registry(
    root: Path, *, registry: Sequence[CommittedSet] = REGISTERED_SETS
) -> Mapping[str, EraKey]:
    """Hold the era registry to the recordings: each set's key, or a refusal.

    Every set's games must fold to one key; the sets of one era id must share
    it and sets of different ids must not; every game of an era with a declared
    config must have recorded exactly that config, and every game of an era with
    none must have recorded no setting off its default. Raises
    :class:`GameplayCensusEraError` naming the set, and the seed for a config
    breach.
    """

    keys: dict[str, EraKey] = {}
    by_era: dict[str, EraKey] = {}
    for entry in registry:
        games = recorded_game_eras(root / entry.path)
        try:
            key = resolve_era(tuple(games.values()))
        except GameplayCensusEraError as error:
            raise GameplayCensusEraError(f"{entry.path}: {error}") from error
        declared = entry.era.declared_config
        expected = (
            canonical_settings(
                RecordedExperimentConfig.model_validate_json(
                    (root / declared).read_bytes()
                ).model_dump(mode="json")
            )
            if declared is not None
            else ()
        )
        for seed, game in games.items():
            if game.settings != expected:
                raise GameplayCensusEraError(
                    f"{entry.path}: seed {seed} recorded settings that differ from "
                    f"the {entry.era.id} era's declared config"
                )
        if by_era.setdefault(entry.era.id, key) != key:
            raise GameplayCensusEraError(
                f"{entry.path}: its recordings fold to a different era from the "
                f"other {entry.era.id} sets"
            )
        keys[entry.path] = key
    ids_by_key: dict[EraKey, str] = {}
    for era_id, key in by_era.items():
        other = ids_by_key.setdefault(key, era_id)
        if other != era_id:
            raise GameplayCensusEraError(
                f"the {other} and {era_id} eras fold to one recorded key; one "
                "recorded era carries one id"
            )
    return MappingProxyType(keys)


def serialize_json(model: BaseModel) -> str:
    """Deterministic JSON: sorted keys, two-space indent, one trailing newline."""

    return (
        json.dumps(
            model.model_dump(mode="json"), indent=2, sort_keys=True, ensure_ascii=False
        )
        + "\n"
    )


__all__ = [
    "ALWAYS",
    "AS_RECORDED",
    "BOUNDED_REBUTTAL",
    "BUTTON_COOLDOWN_TICKS",
    "CELLS",
    "CENSUS_SETS",
    "CENSUS_THREADED_LAYERS",
    "CENSUS_WALK_CONFIG",
    "COUNT_ONLY_NOTE",
    "EDGE_VERDICT",
    "FIELD_CLASSIFICATION",
    "FRESH_KILL_WINDOW_TICKS",
    "HEADINGS",
    "HOLDS_NOTHING_LABEL",
    "IMPOSTOR_BALLOTS_AS_SKIP",
    "IMPOSTOR_BALLOTS_REMOVED",
    "IN_VENT_CAP_TICKS",
    "KILL_TICK_BODY_HANDLE_PATTERN",
    "LONG_GAP",
    "LOOK_AND_WAIT_EXIT",
    "MEETING_REGROUP",
    "MEMORY_SECTIONS",
    "NEVER_REPORTED",
    "NOT_CHECKABLE_REASONS",
    "NOT_THE_SCORECARD_NOTE",
    "NO_IMPOSTOR_SELF_REPORT",
    "NO_REBUTTAL",
    "OWN_FRESH_KILL_ENTRY",
    "OWN_KILL_BALLOT_ROW",
    "OWN_KILL_ROW_TEXT",
    "PHYSICAL_VENT_WITNESS",
    "PLACEMENT_WINDOWS",
    "PREDICATES",
    "PUBLIC_BODY_HANDLE",
    "READ_BALLOT_BLOCKS",
    "REGROUP_NOTICE_TEXT",
    "RETALLY_VARIANTS",
    "ROLE_CORRECTNESS_NOTE",
    "SCHEMA_VERSION",
    "SETTING_DEFAULTS",
    "SETTING_MEANINGS",
    "SHARE_BUCKETS",
    "SHARE_QUARTERS",
    "SHORT_WINDOW_TICKS",
    "TABLES",
    "TASK_WIN",
    "TERMS",
    "TICK_GAP_BUCKETS",
    "UNLABELLED",
    "UNREAD_BALLOT_BLOCKS",
    "UNSEEN_SEED_BAND",
    "WITNESS_OUTCOME_ROWS",
    "AlibiFact",
    "BallotFact",
    "BodyFact",
    "CellCount",
    "CellSpec",
    "CensusCell",
    "CensusEra",
    "CensusInputs",
    "CensusSection",
    "CensusTable",
    "CensusTally",
    "CheckedPlacementKind",
    "CooldownWrite",
    "CooldownWriter",
    "DiscardedAction",
    "EraKey",
    "EraView",
    "FieldUse",
    "Frame",
    "GameFacts",
    "GameplayCensus",
    "GameplayCensusConformanceError",
    "GameplayCensusEraError",
    "GameplayCensusFieldError",
    "HeldSource",
    "KillFact",
    "MeetingFact",
    "ObservationFact",
    "ObservationKind",
    "OwnKillRowFact",
    "Phase",
    "PlacementFact",
    "PlacementVerdict",
    "RouteFrame",
    "SettingPredicate",
    "SettingValue",
    "TableSpec",
    "TriggerKind",
    "TurnFact",
    "VentFact",
    "ballot_call",
    "ballot_prompt_blocks",
    "canonical_settings",
    "census_from_inputs",
    "checked_placement_kinds",
    "compute_gameplay_census",
    "edge_window",
    "fold_set",
    "game_endings",
    "grounding_labels",
    "held_source_rows",
    "held_sources",
    "holds_nothing_check",
    "load_census_inputs",
    "placement_verdict",
    "placement_verdicts",
    "pool",
    "prompt_stamps_from_cell",
    "recorded_game_eras",
    "recorded_kill_cooldown",
    "regroup_notices_held",
    "resolve_era",
    "retally",
    "route_rooms",
    "seat_class",
    "section_from_tally",
    "selector_pick",
    "serialize_json",
    "served_own_kill_rows",
    "setting_value",
    "share_bucket",
    "tally_outcome",
    "tick_gap_bucket",
    "tick_gap_rows",
    "true_at_the_edge",
    "turn_placements",
    "verify_era_registry",
]
