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
loader only to compute such a boolean or an id (the kill-tick body handle in an
opening; a served own-kill ballot row), and no prompt, speech or rationale text
leaves it. :func:`fold_set` is a pure fold over that carrier, so every cell is
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
settings go to every advance through
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
predicate or deliberately not read, and a recording or carrier naming a field
outside that table raises. The predicates (:class:`SettingPredicate`) read the
carrier's plain recorded values, where a missing key means the historical
default; they never build a ``RecordedExperimentConfig``.

Each game carries an :class:`EraKey`: its settings, its temporal-observation
version, its substrate-flag stamp and its prompt stamps, the last taken only
from MANIFEST rows of games that recorded a meeting. A set whose games carry two
eras raises, and :func:`pool` raises across eras.

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
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, model_validator

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
from engine.world import Map, WorldState, load_canonical_map
from eval.balance_eval import _CURRENT_REPORT_WALK_CONFIG
from eval.process_scorecard import AGENT_CLOCK_OFFSET, COMMITTED_SETS, NINE_PLAYER_SETS
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
    MeetingTranscript,
    MeetingTurn,
    TaskActivityAccount,
)
from orchestrator.experiment_config import ConfigLayer, RecordedExperimentConfig
from orchestrator.replay import (
    GameEndReplayEntry,
    ReplayLogEntry,
    recorded_experiment_config,
    recorded_substrate_flags,
    recorded_temporal_observation_version,
)
from orchestrator.replay_integrity import resolve_ballot_tally_threshold

#: Bumped only when the published JSON changes shape in a way an older reader
#: cannot interpret. Version 1 is the first publication.
SCHEMA_VERSION: Final[int] = 1

#: A plain recorded setting value, as the recording serializes it.
SettingValue: TypeAlias = str | int | bool | None

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
#: it. A speaker without a recorded role raises.
_ROLE_WITH_ARTICLE: Final[Mapping[Role, str]] = MappingProxyType(
    {"CREWMATE": "a crewmate", "IMPOSTOR": "an impostor"}
)

#: The trigger-tick event kinds a regroup drops from the resume perception.
_REGROUP_DROPPED_KINDS: Final[tuple[str, ...]] = (
    "Moved",
    "TaskProgressed",
    "TaskCompleted",
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
    """How the census uses one recorded setting.

    ``predicates`` names the setting predicates that read the field; an empty
    tuple means the census deliberately does not read it, for ``reason``.
    """

    predicates: tuple[str, ...]
    reason: str = ""

    def __post_init__(self) -> None:
        if bool(self.predicates) == bool(self.reason):
            raise ValueError("a field is read by predicates or not read for a reason")


def _not_read(reason: str) -> FieldUse:
    return FieldUse(predicates=(), reason=reason)


#: Every recorded setting field, read by a named predicate or deliberately not
#: read. ``tests/eval/test_gameplay_census.py`` holds its names equal to
#: ``RecordedExperimentConfig.model_fields``, both ways.
FIELD_CLASSIFICATION: Final[Mapping[str, FieldUse]] = MappingProxyType(
    {
        "format_version": _not_read("a serialization version, not a game rule"),
        "redistribution_policy": _not_read(
            "decides who inherits a dead crewmate's tasks; no cell counts tasks"
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
    tick: int
    killer: PlayerId
    room: RoomId
    witnesses: frozenset[PlayerId]


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
    here and is never parsed.
    """

    body_id: str
    kill_tick: int


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

    kind: str
    from_tick: int
    to_tick: int
    subject: PlayerId | None


@dataclass(frozen=True)
class AlibiFact:
    """One alibi route: its subject and its (room, from tick, to tick) legs."""

    subject: PlayerId
    legs: tuple[tuple[RoomId, int, int], ...]


@dataclass(frozen=True)
class TurnFact:
    turn_id: str
    index: int
    speaker: PlayerId
    reply_to: str | None
    accusations: tuple[PlayerId, ...]
    observations: tuple[ObservationFact, ...]
    alibis: tuple[AlibiFact, ...]


@dataclass(frozen=True)
class BallotFact:
    """One recorded ballot.

    ``authored_target`` is what the voter wrote: the typed guard field's
    original when a rewrite reason is recorded, the recorded target otherwise,
    and ``None`` for a ballot that never parsed.
    """

    voter: PlayerId
    target: str
    authored_target: str | None
    confidence: float
    grounding_label: str | None
    cited_observation_id: str | None


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
    carrier breaking it raises.
    """

    meeting_id: str
    tick: int
    trigger_kind: str
    opener: PlayerId
    trigger_body: str | None
    bodies_at_open: tuple[tuple[str, PlayerId | None], ...]
    in_vent_at_open: frozenset[PlayerId]
    impostor_cooldowns_at_open: tuple[tuple[PlayerId, int], ...]
    living: frozenset[PlayerId]
    sabotage_active: bool
    outcome: str
    ejected: PlayerId | None
    vent_flag_subjects: tuple[frozenset[PlayerId], ...]
    turns: tuple[TurnFact, ...]
    ballots: tuple[BallotFact, ...]
    ballot_floor: float
    selector_pick: tuple[PlayerId, str] | None
    opener_prompt_has_kill_tick_handle: bool | None
    own_kill_rows: tuple[OwnKillRowFact, ...]
    trigger_tick_dropped_events: tuple[tuple[str, int], ...]
    phase_after: str
    in_vent_after: frozenset[PlayerId]
    bodies_after: frozenset[str]
    regrouped: bool

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
    winner: str | None
    terminal_tick: int


@dataclass(frozen=True)
class CensusInputs:
    """Everything the pure fold needs about one replay set.

    ``kill_cooldown_ticks`` and ``neighbours`` are read from the loaded map: the
    grace window after a regroup and the rooms an in-vent impostor infers it can
    see.
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
_CORPSES: Final[str] = "Corpses and the state play resumes in"
_REGROUP: Final[str] = "After a regroup"
_STRUCTURE: Final[str] = "Meeting structure"
_REBUTTALS: Final[str] = "Rebuttals"
_BALLOTS: Final[str] = "Ballots"
_BESIDE: Final[str] = "Reported beside the counts"

#: The published order of the headings.
HEADINGS: Final[tuple[str, ...]] = (
    _WITNESSES,
    _TRIPS,
    _PROOF,
    _CORPSES,
    _REGROUP,
    _STRUCTURE,
    _REBUTTALS,
    _BALLOTS,
    _BESIDE,
)

_KILL: Final = ("Killed",)
_VENTS: Final = ("VentEntered", "VentExited")
_MEETING_ROW: Final = ("meeting row",)

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
            "Kills made on a tick after a regroup meeting no later than the map's "
            "kill cooldown, over all kills made between a regroup and the next "
            "meeting.",
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
    return frozenset(pid for pid in players if game.roles.get(pid) == "CREWMATE")


def _is_impostor(game: GameFacts, player: PlayerId | None) -> bool:
    return player is not None and game.roles.get(player) == "IMPOSTOR"


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
    _fold_witnesses(game, acc)
    _fold_trips(game, inputs, acc)
    _fold_meetings(game, inputs, acc)
    _fold_rebuttals(game, acc)
    _fold_ballots(game, acc)
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
        crew_rooms = {
            room
            for player, room in frame.rooms.items()
            if game.roles.get(player) == "CREWMATE"
        }
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
    still in that room and out of the vent.
    """

    tick = exit_fact.tick + 1
    while tick in game.frames:
        frame = game.frames[tick]
        if frame.rooms.get(exit_fact.actor) != exit_fact.destination_room:
            return False
        if any(
            room == exit_fact.destination_room
            for player, room in frame.rooms.items()
            if game.roles.get(player) == "CREWMATE"
        ):
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
        acc.count(
            "meetings_opening_with_impostor_in_vent",
            any(_is_impostor(game, player) for player in meeting.in_vent_at_open),
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


def _vent_flag_names(meeting: MeetingFact, player: PlayerId | None) -> bool:
    return player is not None and any(
        player in subjects for subjects in meeting.vent_flag_subjects
    )


def _fold_vent_proof(game: GameFacts, meeting: MeetingFact, acc: _Accumulator) -> None:
    where = f"meeting {meeting.meeting_id}"
    seed = game.seed
    proof = any(subjects & meeting.living for subjects in meeting.vent_flag_subjects)
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
    its kill, so a row citing nothing joins no kill and is a breach too.
    """

    if row.subject in _teammates(game, row.holder):
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


def _fold_ballots(game: GameFacts, acc: _Accumulator) -> None:
    impostors = {pid for pid, role in game.roles.items() if role == "IMPOSTOR"}
    for meeting in game.meetings:
        where = f"meeting {meeting.meeting_id}"
        seed = game.seed
        for ballot in meeting.ballots:
            if ballot.voter not in impostors:
                continue
            teammates = impostors - {ballot.voter}
            voter_where = f"{where}, voter {ballot.voter}"
            eject = ballot.target != "SKIP"
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
                ballot.target in teammates,
                seed=seed,
                where=voter_where,
            )
            acc.count(
                "authored_teammate_ballot_targets",
                ballot.authored_target in teammates,
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
                bool(confident) and all(voter in impostors for voter in confident),
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


def _meeting_fact(
    opened: MeetingOpened,
    applied: MeetingApplied,
    *,
    regroup_recorded: bool,
) -> MeetingFact:
    entry = opened.entry
    state = opened.state
    if opened.trigger is None:
        raise ValueError(f"{entry.meeting_id}: a meeting tick with no trigger event")
    living = frozenset(pid for pid, player in state.players.items() if player.alive)
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
    opened: MeetingOpened | None = None
    game_end: GameEndReplayEntry | None = None
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
            entries.append(event.entry)
            frames[event.entry.tick] = _frame_of(event.state)
        elif isinstance(event, TickAdvanced):
            killed: dict[PlayerId, int] = {}
            for engine_event in event.events:
                if isinstance(engine_event, KilledEvent):
                    kills.append(
                        KillFact(
                            tick=engine_event.tick,
                            killer=engine_event.actor,
                            room=engine_event.room,
                            witnesses=frozenset(engine_event.witnesses),
                        )
                    )
                    killed[engine_event.target] = engine_event.tick
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
            opened = None
        elif isinstance(event, WalkComplete):
            game_end = event.game_end
            terminal_tick = event.terminal_tick
            if game_end is not None:
                entries.append(game_end)
    if terminal_tick is None:
        raise ValueError(f"seed {seed}: the walk never reached its terminal tick")
    stamps = prompt_stamps_from_cell(manifest_cell) if applied_meetings else None
    era = _game_era(entries, stamps)
    regroup_recorded = MEETING_REGROUP.holds(era.values)
    return GameFacts(
        seed=seed,
        roles=MappingProxyType(dict(roles)),
        era=era,
        kills=tuple(kills),
        vents=tuple(vents),
        bodies=tuple(bodies),
        frames=MappingProxyType(frames),
        meetings=tuple(
            _meeting_fact(opened_meeting, applied, regroup_recorded=regroup_recorded)
            for opened_meeting, applied in applied_meetings
        ),
        discarded=tuple(discarded),
        rows_without_dispositions=rows_without_dispositions,
        winner=game_end.winner if game_end is not None else None,
        terminal_tick=terminal_tick,
    )


def load_census_inputs(set_dir: Path) -> CensusInputs:
    """Walk one replay set on the canonical map into the census carrier.

    The one impure step. Roles come from :func:`eval.validity.roles_by_seed`,
    the seeder the sample report takes them from. No model is called and
    nothing is written.
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
    label = f"{set_dir.parent.name}/{set_dir.name}"
    return CensusInputs(
        label=label,
        source=f"replays/{label}",
        era=resolve_era(tuple(game.era for game in games)),
        kill_cooldown_ticks=resolved_map.kill_cooldown_ticks,
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
            "impostor's kill cooldown restarts at the map's value."
        ),
        "grace window": (
            "the ticks after a regroup before the impostors' restarted kill cooldown "
            "runs out: from the tick after the meeting through the map's kill "
            "cooldown."
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


class GameplayCensus(_FrozenModel):
    schema_version: int
    not_the_scorecard_note: str
    role_correctness_note: str
    count_only_note: str
    terms: dict[str, str]
    setting_meanings: dict[str, str]
    constants: dict[str, int]
    field_classification: dict[str, str]
    sets: tuple[CensusSection, ...]
    pooled_9p2i: CensusSection
    pooled: CensusSection


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
            else f"not read: {use.reason}"
        )
        for name, use in FIELD_CLASSIFICATION.items()
    }


def _constants(kill_cooldown_ticks: int) -> dict[str, int]:
    return {
        "fresh_kill_window_ticks": FRESH_KILL_WINDOW_TICKS,
        "in_vent_cap_ticks": IN_VENT_CAP_TICKS,
        "grace_window_ticks": kill_cooldown_ticks,
        "button_cooldown_ticks": BUTTON_COOLDOWN_TICKS,
        "short_window_ticks": SHORT_WINDOW_TICKS,
    }


#: The committed sets in publication order, and the nine-player pair, taken from
#: the scorecard so the two reports name one list.
CENSUS_SETS: Final[tuple[str, ...]] = COMMITTED_SETS
CENSUS_NINE_PLAYER_SETS: Final[tuple[str, ...]] = NINE_PLAYER_SETS


def census_from_inputs(inputs: Sequence[CensusInputs]) -> GameplayCensus:
    """Fold every set, pool the nine-player sets and all sets, and publish."""

    if not inputs:
        raise ValueError("no replay sets to fold")
    cooldowns = {item.kill_cooldown_ticks for item in inputs}
    if len(cooldowns) != 1:
        raise ValueError("the sets were walked on maps with different kill cooldowns")
    tallies = [fold_set(item) for item in inputs]
    nine = [
        tally
        for tally, item in zip(tallies, inputs, strict=True)
        if item.source in CENSUS_NINE_PLAYER_SETS
    ]
    return GameplayCensus(
        schema_version=SCHEMA_VERSION,
        not_the_scorecard_note=NOT_THE_SCORECARD_NOTE,
        role_correctness_note=ROLE_CORRECTNESS_NOTE,
        count_only_note=COUNT_ONLY_NOTE,
        terms=dict(TERMS),
        setting_meanings=dict(SETTING_MEANINGS),
        constants=_constants(cooldowns.pop()),
        field_classification=_field_classification_view(),
        sets=tuple(section_from_tally(tally) for tally in tallies),
        pooled_9p2i=section_from_tally(
            pool(nine, label="pooled: the two nine-player sets")
        ),
        pooled=section_from_tally(
            pool(tallies, label="pooled: all four committed sets")
        ),
    )


def compute_gameplay_census(
    root: Path, *, load: Callable[[Path], CensusInputs] = load_census_inputs
) -> GameplayCensus:
    """Walk and fold the four committed sets. Zero model calls; writes nothing.

    ``load`` walks one set; a test hands it a cached walk of the same bytes.
    """

    return census_from_inputs([load(root / name) for name in CENSUS_SETS])


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
    "BOUNDED_REBUTTAL",
    "BUTTON_COOLDOWN_TICKS",
    "CELLS",
    "CENSUS_NINE_PLAYER_SETS",
    "CENSUS_SETS",
    "CENSUS_THREADED_LAYERS",
    "CENSUS_WALK_CONFIG",
    "COUNT_ONLY_NOTE",
    "FIELD_CLASSIFICATION",
    "FRESH_KILL_WINDOW_TICKS",
    "HEADINGS",
    "IN_VENT_CAP_TICKS",
    "KILL_TICK_BODY_HANDLE_PATTERN",
    "LOOK_AND_WAIT_EXIT",
    "MEETING_REGROUP",
    "NOT_THE_SCORECARD_NOTE",
    "NO_IMPOSTOR_SELF_REPORT",
    "NO_REBUTTAL",
    "OWN_FRESH_KILL_ENTRY",
    "OWN_KILL_BALLOT_ROW",
    "OWN_KILL_ROW_TEXT",
    "PHYSICAL_VENT_WITNESS",
    "PREDICATES",
    "PUBLIC_BODY_HANDLE",
    "ROLE_CORRECTNESS_NOTE",
    "SCHEMA_VERSION",
    "SETTING_DEFAULTS",
    "SETTING_MEANINGS",
    "SHORT_WINDOW_TICKS",
    "TABLES",
    "TERMS",
    "UNSEEN_SEED_BAND",
    "AlibiFact",
    "BallotFact",
    "BodyFact",
    "CellCount",
    "CellSpec",
    "CensusCell",
    "CensusInputs",
    "CensusSection",
    "CensusTable",
    "CensusTally",
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
    "KillFact",
    "MeetingFact",
    "ObservationFact",
    "OwnKillRowFact",
    "SettingPredicate",
    "SettingValue",
    "TableSpec",
    "TurnFact",
    "VentFact",
    "canonical_settings",
    "census_from_inputs",
    "compute_gameplay_census",
    "fold_set",
    "load_census_inputs",
    "pool",
    "prompt_stamps_from_cell",
    "resolve_era",
    "section_from_tally",
    "selector_pick",
    "serialize_json",
    "served_own_kill_rows",
    "setting_value",
]
