"""Offline replay of the route checks on the committed recordings.

The decision this informs is the owner's: whether a round 3 is worth recording
with one meeting-layer route check, and which one. It replays the committed bytes
of three 9-player columns, each read alone and never pooled, and counts what each
candidate route check would have shown each voter at every recorded meeting:

* **(a)** the walkable-pair clause of the corroboration ledger, built exactly as
  the meeting manager builds it (:func:`meetings.corroboration.build_testimony_ledger`
  with the firewalled sighting records, the movement records, the opener, the
  living roster, the trigger kind and the public regroup ticks), shown to every
  voter whose candidate list holds the subject;
* **(b)** the travel-check lines the recorded field ``evidence_reasoning_version =
  2`` renders into each voter's memory
  (:func:`agents.memory.evidence_context.v2_evidence_context_rows`), read on a
  version-2 view of the memory the voter held at the meeting's open, and again
  with each plain recorded sighting labelled a start-of-tick snapshot
  (**b-snapshot**, an approximation of the temporal delivery that field requires);
* **(c)** a reference reading of a narrow field, computed here from existing
  functions: stated placements at the table, several hops over the whole map, and
  a crossing of the public regroup named. It is no mechanism and no arm.

Its reading is a process count, never role-correctness: charges resting on a
stated pair the map or the public regroup reconciles, ejections carried by such
a charge, and which check would have reached them. Roles are read only to set
the counts out by ejection class, as description.

Every column is pinned to a full commit sha resolved when the run starts and
materialized with ``git archive``; ``--check`` re-materializes the recorded shas,
refuses a column whose recorded tree id differs from the tree of ``SHA:PATH``,
and recomputes the JSON and the report byte for byte.

Purity: offline, no provider client (the walk's recorded-response stub answers
every call from the recording's bytes), no environment write, no recorded byte
edited. The outputs carry ids, ticks, room ids, kinds, booleans and counts only;
before it writes, the run scans both outputs for every turn text, ballot
rationale and travel line it read and refuses to write one that holds any.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import time
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal, Protocol, TypeAlias, cast, get_args

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR: Final[Path] = _REPO_ROOT / "scripts"
# The judgment net and the firewall helper live in a script module; the scripts
# directory is a mypy path, so it is imported the way the suite imports it.
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import meetings.corroboration as corroboration  # noqa: E402
from agents.memory.episodic import EpisodicEvent, MemoryStore  # noqa: E402
from agents.memory.evidence_context import v2_evidence_context_rows  # noqa: E402
from agents.memory.store import (  # noqa: E402
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    _latest_self_guard_fields,
    render_for_prompt,
)
from agents.strategic.prompts.loader import PromptRenderers  # noqa: E402
from counterfactual_phase21 import (  # noqa: E402
    IMPOSSIBLE_TRANSIT_PATTERN,
    _firewalled_sightings,
)
from engine.entities import Role  # noqa: E402
from engine.world import load_canonical_map  # noqa: E402
from eval.eras import STAGE_B_R2  # noqa: E402
from eval.gameplay_census import (  # noqa: E402
    CensusInputs,
    GameFacts,
    KillFact,
    MeetingFact,
    canonical_settings,
    load_census_inputs,
    recorded_game_eras,
)
from eval.validity import seeds_on_disk  # noqa: E402
from meetings.corroboration import (  # noqa: E402
    MeetingTestimonyLedger,
    _walkable_transits,
    build_testimony_ledger,
)
from meetings.manager import _candidate_targets  # noqa: E402
from meetings.schemas import (  # noqa: E402
    AlibiClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    MoveWitnessRecord,
    PlayerId,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import (  # noqa: E402
    CANONICAL_ROOMS,
    MeetingTriggerKind,
    StatedPlacement,
    _turn_claim_id,
    _turn_whereabouts_id,
    canonical_rooms,
    is_relevant_sighting,
    maximal_stays,
    reconstruct_stated_paths,
    room_hops,
    triggering_body_rooms,
    turn_observation_id,
)
from orchestrator.experiment_config import RecordedExperimentConfig  # noqa: E402
from orchestrator.replay import (  # noqa: E402
    MeetingReplayEntry,
    derive_regroup_ticks,
    read_all_entries,
    recorded_experiment_config,
)
from tests.meetings.test_prompt_byte_golden import (  # noqa: E402
    _KIND_VOTE_BALLOT,
    ReconstructedMeeting,
    _canonical_renderers,
    walk_replay_meetings,
)

SCHEMA_VERSION: Final[int] = 1

DEFAULT_JSON: Final[Path] = Path("experiments/lab/results-route-check-replay.json")
DEFAULT_REPORT: Final[Path] = Path("experiments/lab/report-route-check-replay.md")

PlacementKind: TypeAlias = Literal[
    "saw_player", "company", "saw_move", "whereabouts", "alibi_stay", "saw_vent"
]
MeetingKind: TypeAlias = Literal["report_vent_proof", "report_no_vent_proof", "button"]
ALeg: TypeAlias = Literal["a", "a_transcript_only", "a_no_movement", "a_no_regroup"]
DisputeLeg: TypeAlias = Literal[
    "a", "a_transcript_only", "a_no_movement", "a_no_regroup", "a_with_movement_origins"
]
Check: TypeAlias = Literal["a", "a_transcript_only", "b", "b_snapshot", "c"]
TravelVerdict: TypeAlias = Literal[
    "fits", "cannot_reconcile", "insufficient_timing", "crosses_regroup", "unverifiable"
]
Reason: TypeAlias = Literal[
    "kind",
    "relevance_gate",
    "hop_bound",
    "tick_bound",
    "cap",
    "claim_not_held",
    "phase_rule",
    "residual",
]
EjectionClass: TypeAlias = Literal["innocent", "impostor", "ejected_witness"]

MEETING_KINDS: Final[tuple[MeetingKind, ...]] = get_args(MeetingKind)
A_LEGS: Final[tuple[ALeg, ...]] = get_args(ALeg)
#: The (a) legs read for the dispute: the four ledger calls, and one informational
#: reading that also places each spoken movement sighting's origin.
DISPUTE_LEGS: Final[tuple[DisputeLeg, ...]] = get_args(DisputeLeg)
CHECKS: Final[tuple[Check, ...]] = get_args(Check)
TRAVEL_VERDICTS: Final[tuple[TravelVerdict, ...]] = get_args(TravelVerdict)
#: The fixed order an unreached case's reason is chosen in.
REASONS: Final[tuple[Reason, ...]] = get_args(Reason)
EJECTION_CLASSES: Final[tuple[EjectionClass, ...]] = get_args(EjectionClass)

#: Which inputs each leg of (a) drops: (movement records, regroup ticks).
A_LEG_DROPS: Final[Mapping[ALeg, tuple[bool, bool]]] = MappingProxyType(
    {
        "a": (False, False),
        "a_transcript_only": (True, True),
        "a_no_movement": (True, False),
        "a_no_regroup": (False, True),
    }
)

#: The spoken placement kinds each check takes in. (a) reads the stated paths
#: (sightings, their company, grounded movement, whereabouts); (c) adds the stays
#: of alibi routes; (b) can hold a spoken placement later only as an absorbed
#: claim of the three kinds its evidence context reads. Every walked meeting
#: re-derives the (a) and (c) sets from the live functions and raises on a
#: placement of another kind (:func:`_require_input_kinds`).
A_INPUT_KINDS: Final[frozenset[PlacementKind]] = frozenset(
    {"saw_player", "company", "saw_move", "whereabouts"}
)
C_INPUT_KINDS: Final[frozenset[PlacementKind]] = A_INPUT_KINDS | {"alibi_stay"}
B_CLAIM_KINDS: Final[frozenset[PlacementKind]] = frozenset(
    {"saw_player", "whereabouts", "alibi_stay"}
)

#: s9's ejections with a walkable pair under (a) as built, (numerator,
#: denominator): the round-2 record's two committed cells (69 of 411 over the
#: four baseline-9 sets, 56 of 321 over three) differ by exactly s9's games.
S9_WALKABLE_PAIR_EJECTIONS: Final[tuple[int, int]] = (13, 90)

#: Shortest recorded string the output scan looks for; shorter ones are ids and
#: room names the outputs legitimately carry.
_SCAN_MIN_LENGTH: Final[int] = 16

#: The three travel-check verdict sentences of the version-2 evidence context,
#: read here to classify each rendered row. A row ending any other way raises.
_WALK_VERDICTS: Final[Mapping[str, TravelVerdict]] = MappingProxyType(
    {
        "a walk fits the public map; this contests an impossible-travel "
        "allegation and does not establish innocence.": "fits",
        "walking cannot reconcile these placements. Check their sources; this "
        "alone does not prove a role.": "cannot_reconcile",
        "the available timing or placements are insufficient for a walking "
        "verdict.": "insufficient_timing",
    }
)
_WALK_LINE: Final[re.Pattern[str]] = re.compile(
    r"^Travel check for (?P<subject>\S+): (?P<room_a>.+?) at tick (?P<tick_a>\d+) "
    r"\((?:start|during|unspecified phase); [^)]*\) to (?P<room_b>.+?) at tick "
    r"(?P<tick_b>\d+) \((?:start|during|unspecified phase); [^)]*\)\. "
    r"(?:Assuming the claimed placement is accurate, )?(?P<verdict>.+)$"
)
_REGROUP_LINE: Final[re.Pattern[str]] = re.compile(
    r"^Travel check for (?P<subject>\S+): the interval from tick (?P<tick_a>\d+) "
    r"to tick (?P<tick_b>\d+) crosses the public regroup at tick \d+ in .+\. "
    r"A walking-only check cannot decide this interval\.$"
)
_UNVERIFIABLE_LINE: Final[re.Pattern[str]] = re.compile(
    r"^Travel check for (?P<subject>\S+): insufficient observed placements to "
    r"check the .+ at tick \d+\.$"
)
_TRAVEL_ROW_KINDS: Final[frozenset[str]] = frozenset({"travel", "travel_contradicted"})
#: The ballot template's delimiters around the rendered memory.
_MEMORY_OPEN: Final[str] = "<memory>\n"
_MEMORY_CLOSE: Final[str] = "\n</memory>"


class RouteCheckReplayError(RuntimeError):
    """The instrument refused an input or found the walk unfaithful."""


# ---------------------------------------------------------------------------
# Columns: exact provenance
# ---------------------------------------------------------------------------


#: The three columns, in the order the report sets them out: s9 is baseline 9,
#: the 9-player set shown before the promotion; r1 is candidate round 1, the
#: eight Stage-B rules; r2 is candidate round 2, the same rules with a six-tick
#: kill cooldown.
COLUMN_LABELS: Final[tuple[str, ...]] = ("s9", "r1", "r2")

#: The config file candidate round 1 recorded under.
R1_CONFIG_PATH: Final[str] = "replays/candidates/stage-b-r1/experiment-config.json"


def declared_config_path(label: str) -> str | None:
    """The experiment config a column's rows must have recorded, or ``None``.

    r2 declares its era's config, read from the era registry when asked; r1
    declares the round's own file; s9 was recorded with every experimental
    switch off. The path is read at the column's own commit.
    """

    if label == "r2":
        return STAGE_B_R2.declared_config
    if label == "r1":
        return R1_CONFIG_PATH
    if label == "s9":
        return None
    raise RouteCheckReplayError(f"column label {label!r} is not one of {COLUMN_LABELS}")


@dataclass(frozen=True)
class ColumnRequest:
    """One ``--set LABEL=COMMIT:PATH`` as given."""

    label: str
    commit: str
    path: str


@dataclass(frozen=True)
class ColumnSource:
    """One column resolved to exact bytes: its full sha, path and tree id."""

    label: str
    commit: str
    sha: str
    path: str
    tree: str


def parse_column_request(text: str) -> ColumnRequest:
    """Parse ``LABEL=COMMIT:PATH``; a malformed request raises."""

    label, equals, rest = text.partition("=")
    commit, colon, path = rest.partition(":")
    if not equals or not colon or not label or not commit or not path:
        raise RouteCheckReplayError(f"--set {text!r}: expected LABEL=COMMIT:PATH")
    return ColumnRequest(label=label, commit=commit, path=path.rstrip("/"))


def _git(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, check=False
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise RouteCheckReplayError(f"git {' '.join(args)}: {detail}")
    return completed.stdout


def resolve_commit(repo: Path, commit: str) -> str:
    """The full sha ``commit`` names; a name that resolves to no commit raises."""

    try:
        return (
            _git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
        )
    except RouteCheckReplayError as error:
        raise RouteCheckReplayError(
            f"commit {commit!r} does not resolve to a commit: {error}"
        ) from error


def tree_at(repo: Path, sha: str, path: str) -> str:
    """The tree id of ``SHA:PATH``; a path that is no directory there raises."""

    try:
        tree = _git(repo, "rev-parse", "--verify", f"{sha}:{path}").decode().strip()
        kind = _git(repo, "cat-file", "-t", tree).decode().strip()
    except RouteCheckReplayError as error:
        raise RouteCheckReplayError(
            f"path {path!r} does not resolve at {sha}: {error}"
        ) from error
    if kind != "tree":
        raise RouteCheckReplayError(
            f"path {path!r} at {sha} is a {kind}, not a directory"
        )
    return tree


def resolve_column(repo: Path, request: ColumnRequest) -> ColumnSource:
    """Pin one requested column to its full sha and tree id."""

    if request.label not in COLUMN_LABELS:
        raise RouteCheckReplayError(
            f"column label {request.label!r} is not one of {COLUMN_LABELS}"
        )
    sha = resolve_commit(repo, request.commit)
    return ColumnSource(
        label=request.label,
        commit=request.commit,
        sha=sha,
        path=request.path,
        tree=tree_at(repo, sha, request.path),
    )


def materialize(repo: Path, source: ColumnSource, destination: Path) -> Path:
    """Write ``SHA:PATH`` into ``destination`` with ``git archive``; return the set dir."""

    archive = _git(repo, "archive", "--format=tar", source.sha, "--", source.path)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        bundle.extractall(destination, filter="data")
    return destination / source.path


def declared_config(repo: Path, source: ColumnSource) -> dict[str, object] | None:
    """The config file the column's label declares, read at the column's sha."""

    path = declared_config_path(source.label)
    if path is None:
        return None
    raw = _git(repo, "show", f"{source.sha}:{path}")
    try:
        RecordedExperimentConfig.model_validate_json(raw)
    except ValueError as error:
        raise RouteCheckReplayError(
            f"column {source.label}: {path} at {source.sha} is no experiment config"
        ) from error
    return cast(dict[str, object], json.loads(raw))


def require_declared_settings(
    set_dir: Path, *, label: str, config: Mapping[str, object] | None
) -> None:
    """Refuse a column whose games recorded settings other than its label's config.

    The comparison is the era registry's (:func:`eval.gameplay_census.
    verify_era_registry`): each game's canonical recorded settings against the
    canonical settings of the declared file, or none.
    """

    expected = (
        canonical_settings(
            RecordedExperimentConfig.model_validate(config).model_dump(mode="json")
        )
        if config is not None
        else ()
    )
    for seed, era in recorded_game_eras(set_dir).items():
        if era.settings != expected:
            declared = declared_config_path(label) or "no experiment config"
            raise RouteCheckReplayError(
                f"column {label}: seed {seed} recorded settings that differ from "
                f"the config its label declares ({declared})"
            )


# ---------------------------------------------------------------------------
# The universe of spoken placements
# ---------------------------------------------------------------------------


class _Spot(Protocol):
    @property
    def tick(self) -> int: ...

    @property
    def rooms(self) -> frozenset[str]: ...


@dataclass(frozen=True)
class Placement:
    """One typed placement of ``player`` spoken at the meeting, ungated."""

    player: PlayerId
    tick: int
    rooms: frozenset[str]
    kind: PlacementKind
    event_id: str
    turn_id: str


def _placement_key(spot: Placement) -> tuple[int, tuple[str, ...], str, str]:
    return (spot.tick, tuple(sorted(spot.rooms)), spot.event_id, spot.kind)


def _alibi_stay_placements(turn: MeetingTurn) -> Iterator[Placement]:
    """Each maximal stay of each alibi route, at its first and last tick."""

    for index, claim in enumerate(turn.claims):
        if not isinstance(claim, AlibiClaim):
            continue
        event_id = _turn_claim_id(turn=turn, index=index)
        for stay in maximal_stays(claim.route):
            rooms = canonical_rooms(stay.room)
            if not rooms:
                continue
            for tick in sorted({stay.from_tick, stay.to_tick}):
                yield Placement(
                    claim.subject, tick, rooms, "alibi_stay", event_id, turn.turn_id
                )


def spoken_placements(transcript: MeetingTranscript) -> tuple[Placement, ...]:
    """Every typed placement spoken at the meeting, for every player it places.

    Sightings place their subject and their company, a movement sighting its
    destination, a whereabouts its speaker, an alibi route its subject (one
    placement at each end of each stay), a vent sighting its subject. Nothing is
    gated; a label with no canonical room places nobody.
    """

    found: set[Placement] = set()
    for turn in transcript.turns:
        for index, observation in enumerate(turn.observations):
            event_id = turn_observation_id(turn=turn, index=index)
            if isinstance(observation, SawPlayerObservation):
                rooms = canonical_rooms(observation.room)
                if not rooms:
                    continue
                found.add(
                    Placement(
                        observation.subject,
                        observation.tick,
                        rooms,
                        "saw_player",
                        event_id,
                        turn.turn_id,
                    )
                )
                for companion in observation.co_present:
                    if companion != observation.subject:
                        found.add(
                            Placement(
                                companion,
                                observation.tick,
                                rooms,
                                "company",
                                event_id,
                                turn.turn_id,
                            )
                        )
            elif isinstance(observation, SawMoveObservation):
                rooms = canonical_rooms(observation.to_room)
                if rooms:
                    found.add(
                        Placement(
                            observation.subject,
                            observation.tick,
                            rooms,
                            "saw_move",
                            event_id,
                            turn.turn_id,
                        )
                    )
            elif isinstance(observation, WhereaboutsClaim):
                rooms = canonical_rooms(observation.room)
                if rooms:
                    found.add(
                        Placement(
                            turn.speaker,
                            observation.tick,
                            rooms,
                            "whereabouts",
                            _turn_whereabouts_id(turn=turn, index=index),
                            turn.turn_id,
                        )
                    )
            elif isinstance(observation, SawVentObservation):
                rooms = canonical_rooms(observation.room)
                if rooms:
                    found.add(
                        Placement(
                            observation.subject,
                            observation.tick,
                            rooms,
                            "saw_vent",
                            event_id,
                            turn.turn_id,
                        )
                    )
        found.update(_alibi_stay_placements(turn))
    return tuple(sorted(found, key=_placement_key))


def placements_of(
    placements: Iterable[Placement], player: PlayerId
) -> tuple[Placement, ...]:
    return tuple(spot for spot in placements if spot.player == player)


def reconcilable(
    earlier: _Spot, later: _Spot, *, regroup_ticks: frozenset[int]
) -> Literal["walk", "regroup"] | None:
    """How a pair in two different rooms is reconciled, or ``None``.

    ``earlier`` must not be later than ``later``. The rooms must be disjoint
    canonical sets. A walk reconciles when ``1 <= hops <= elapsed`` over the
    whole canonical map (the hop search bounded by the room count); otherwise the
    public regroup reconciles a pair whose interval holds one of its ticks.
    """

    if earlier.tick > later.tick:
        raise ValueError("a pair is ordered by tick")
    hops = room_hops(earlier.rooms, later.rooms, max_hops=len(CANONICAL_ROOMS))
    if hops is None or hops == 0:
        return None
    if hops <= later.tick - earlier.tick:
        return "walk"
    if any(earlier.tick < tick <= later.tick for tick in regroup_ticks):
        return "regroup"
    return None


def ordered_pairs(spots: Sequence[Placement]) -> Iterator[tuple[Placement, Placement]]:
    ordered = sorted(spots, key=_placement_key)
    for index, earlier in enumerate(ordered):
        for later in ordered[index + 1 :]:
            yield earlier, later


@dataclass(frozen=True)
class Charge:
    """An EJECT ballot or a flag resting on typed placements of its target."""

    source: Literal["ballot", "flag"]
    placements: frozenset[Placement]


def charges_against(
    target: PlayerId,
    *,
    ballots: Sequence[VoteBallot],
    contradictions: Sequence[ContradictionRef],
    universe: Sequence[Placement],
) -> tuple[Charge, ...]:
    """The charges against ``target`` at one meeting.

    A charge is an EJECT ballot for ``target`` whose primary reason cites a turn
    carrying a typed placement of ``target``, or a contradiction flag naming
    ``target`` whose every event is such a placement.
    """

    own = placements_of(universe, target)
    found: list[Charge] = []
    for ballot in ballots:
        if ballot.target != target or ballot.primary_reason_id is None:
            continue
        cited = frozenset(
            spot for spot in own if spot.turn_id == ballot.primary_reason_id
        )
        if cited:
            found.append(Charge("ballot", cited))
    for flag in contradictions:
        if target not in flag.subjects:
            continue
        events = (flag.event_a_id, flag.event_b_id)
        resolved = [
            frozenset(spot for spot in own if spot.event_id == event)
            for event in events
        ]
        if all(resolved):
            found.append(Charge("flag", frozenset().union(*resolved)))
    return tuple(found)


def misjudging_pairs(
    universe_of_target: Sequence[Placement],
    charged: frozenset[Placement],
    *,
    regroup_ticks: frozenset[int],
) -> tuple[tuple[Placement, Placement], ...]:
    """The reconcilable pairs of which a charged placement is one end."""

    return tuple(
        (earlier, later)
        for earlier, later in ordered_pairs(universe_of_target)
        if (earlier in charged or later in charged)
        and reconcilable(earlier, later, regroup_ticks=regroup_ticks) is not None
    )


# ---------------------------------------------------------------------------
# One meeting's inputs, read off the walk
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MeetingInputs:
    """What one meeting's reading needs, every field the manager's own value.

    ``memories`` are the LIVE stores the walk renders the next meeting from: the
    reading copies before it renders. ``ballot_overrides`` is each voter's
    pre-vote suspicion, read off the ballot render the walk captured, and
    ``ballot_prompts`` those renders' prompts, for the re-render integrity check.
    """

    transcript: MeetingTranscript
    contradictions: tuple[ContradictionRef, ...]
    ballots: tuple[VoteBallot, ...]
    ejected: PlayerId | None
    opener: PlayerId
    trigger_kind: MeetingTriggerKind
    roster: frozenset[PlayerId]
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]]
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]]
    regroup_ticks: frozenset[int]
    first_meeting: bool
    memories: Mapping[PlayerId, AgentMemory]
    ballot_overrides: Mapping[PlayerId, Mapping[PlayerId, float]]
    ballot_prompts: Mapping[PlayerId, tuple[str, ...]]


def meeting_inputs(
    meeting: ReconstructedMeeting, *, regroup_ticks: frozenset[int]
) -> MeetingInputs:
    """Read one reconstructed meeting into the reading's inputs."""

    if meeting.trigger_kind is None:
        raise RouteCheckReplayError(
            f"{meeting.meeting_id}: the walk threaded no trigger"
        )
    participants = meeting.participants
    overrides: dict[PlayerId, Mapping[PlayerId, float]] = {}
    prompts: dict[PlayerId, tuple[str, ...]] = {}
    for participant in participants:
        renders = [
            render
            for render in meeting.renders
            if render.kind == _KIND_VOTE_BALLOT
            and render.agent_id == participant.agent_id
        ]
        if not renders:
            raise RouteCheckReplayError(
                f"{meeting.meeting_id}: no ballot render for {participant.agent_id}"
            )
        overrides[participant.agent_id] = MappingProxyType(
            {
                entry.player_id: entry.suspicion
                for entry in renders[0].suspicion_provenance
            }
        )
        prompts[participant.agent_id] = tuple(render.prompt for render in renders)
    return MeetingInputs(
        transcript=meeting.result.transcript,
        contradictions=tuple(meeting.result.contradictions),
        ballots=tuple(meeting.result.ballots),
        ejected=meeting.result.ejected_player_id,
        opener=meeting.result.triggered_by,
        trigger_kind=meeting.trigger_kind,
        roster=frozenset(p.agent_id for p in participants),
        sighting_records=MappingProxyType(_firewalled_sightings(participants)),
        move_witness_records=MappingProxyType(
            {
                p.agent_id: p.move_witness_records
                for p in participants
                if p.move_witness_records
            }
        ),
        regroup_ticks=regroup_ticks,
        first_meeting=meeting.meeting_index == 0,
        memories=MappingProxyType(dict(meeting.memories)),
        ballot_overrides=MappingProxyType(overrides),
        ballot_prompts=MappingProxyType(prompts),
    )


# ---------------------------------------------------------------------------
# (a) the walkable-pair clause, as the manager builds it
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LedgerCall:
    """The arguments of one :func:`build_testimony_ledger` call."""

    transcript: MeetingTranscript
    contradictions: tuple[ContradictionRef, ...]
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]]
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]]
    opener: PlayerId
    roster: frozenset[PlayerId]
    trigger_kind: MeetingTriggerKind
    regroup_ticks: frozenset[int]

    def build(self) -> MeetingTestimonyLedger:
        return build_testimony_ledger(
            self.transcript,
            contradictions=self.contradictions,
            sighting_records=self.sighting_records,
            move_witness_records=self.move_witness_records,
            opener=self.opener,
            roster=self.roster,
            trigger_kind=self.trigger_kind,
            regroup_ticks=self.regroup_ticks,
        )

    def stated_paths(self) -> Mapping[PlayerId, tuple[StatedPlacement, ...]]:
        """The placements the ledger's walkable clause reads, on the same inputs."""

        return reconstruct_stated_paths(
            self.transcript,
            roster=self.roster,
            trigger_kind=self.trigger_kind,
            movement_witness_records=self.move_witness_records,
            regroup_ticks=self.regroup_ticks,
        )


def ledger_call(inputs: MeetingInputs, *, leg: ALeg = "a") -> LedgerCall:
    """The ledger call of one leg: (a) as built, or with inputs dropped."""

    drop_movement, drop_regroup = A_LEG_DROPS[leg]
    return LedgerCall(
        transcript=inputs.transcript,
        contradictions=inputs.contradictions,
        sighting_records=inputs.sighting_records,
        move_witness_records=MappingProxyType({})
        if drop_movement
        else inputs.move_witness_records,
        opener=inputs.opener,
        roster=inputs.roster,
        trigger_kind=inputs.trigger_kind,
        regroup_ticks=frozenset() if drop_regroup else inputs.regroup_ticks,
    )


@dataclass(frozen=True)
class AReading:
    """One subject's row under (a): the pairs shown and the placements under them."""

    subject: PlayerId
    shown: tuple[tuple[str, str], ...]
    shown_pairs: tuple[tuple[StatedPlacement, StatedPlacement], ...]
    qualifying_pairs: tuple[tuple[StatedPlacement, StatedPlacement], ...]
    path: tuple[StatedPlacement, ...]


def a_readings(call: LedgerCall) -> Mapping[PlayerId, AReading]:
    """Every ledger row of one call, with the placement pairs its lines rest on.

    The live rule (:func:`meetings.corroboration._walkable_transits`) is asked
    about each pair of the subject's stated path on its own; the row's shown
    labels must be among the labels it qualifies, or the reading raises.
    """

    ledger = call.build()
    paths = call.stated_paths()
    readings: dict[PlayerId, AReading] = {}
    for row in ledger.rows:
        path = paths.get(row.subject, ())
        qualifying: list[tuple[StatedPlacement, StatedPlacement, tuple[str, str]]] = []
        for index, earlier in enumerate(path):
            for later in path[index + 1 :]:
                labels = _walkable_transits((earlier, later))
                if labels:
                    qualifying.append((earlier, later, labels[0]))
        known = {label for _, _, label in qualifying}
        if not set(row.walkable_transits) <= known:
            raise RouteCheckReplayError(
                f"subject {row.subject}: a shown walkable pair rests on no pair of "
                "the stated path the ledger read"
            )
        readings[row.subject] = AReading(
            subject=row.subject,
            shown=row.walkable_transits,
            shown_pairs=tuple(
                (earlier, later)
                for earlier, later, label in qualifying
                if label in row.walkable_transits
            ),
            qualifying_pairs=tuple(
                (earlier, later) for earlier, later, _ in qualifying
            ),
            path=path,
        )
    return MappingProxyType(readings)


def walkable_with_movement_origins(inputs: MeetingInputs, subject: PlayerId) -> bool:
    """Whether (a)'s live rule finds a pair once movement origins are placed too.

    Informational, for the dispute only. The live clause places a spoken movement
    sighting at its destination alone (:class:`meetings.schemas.SawMoveObservation`
    says why the origin is not placed one tick earlier); this reading adds that
    origin, through the same relevance gate, to (a) as built's stated path and asks
    :func:`meetings.corroboration._walkable_transits` again.
    """

    path = list(ledger_call(inputs).stated_paths().get(subject, ()))
    body = triggering_body_rooms(inputs.transcript, trigger_kind=inputs.trigger_kind)
    for turn in inputs.transcript.turns:
        if turn.speaker not in inputs.roster:
            continue
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawMoveObservation):
                continue
            rooms = canonical_rooms(observation.from_room)
            tick = observation.tick - 1
            if (
                observation.subject != subject
                or not rooms
                or not is_relevant_sighting(
                    tick=tick,
                    rooms=rooms,
                    triggering_body_rooms=body,
                    regroup_ticks=inputs.regroup_ticks,
                )
            ):
                continue
            path.append(
                StatedPlacement(
                    tick=tick,
                    rooms=rooms,
                    speaker=turn.speaker,
                    event_id=f"{turn_observation_id(turn=turn, index=index)}:origin",
                )
            )
    path.sort(key=lambda spot: (spot.tick, tuple(sorted(spot.rooms)), spot.event_id))
    return bool(_walkable_transits(tuple(path)))


def _shown_voter_lines(
    roster: frozenset[PlayerId], lines_by_subject: Mapping[PlayerId, int]
) -> int:
    """Lines shown summed over voters, each seeing the subjects it may vote for."""

    return sum(
        lines_by_subject.get(subject, 0)
        for voter in sorted(roster)
        for subject in _candidate_targets(roster, exclude=voter)
    )


# ---------------------------------------------------------------------------
# (c) the reference reading
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CSpot:
    """One placement (c) reads: a stated path placement or an alibi stay end."""

    tick: int
    rooms: frozenset[str]
    event_id: str


def c_spots(inputs: MeetingInputs) -> Mapping[PlayerId, tuple[CSpot, ...]]:
    """Each living candidate's placements under (c), tick-ordered."""

    paths = reconstruct_stated_paths(
        inputs.transcript,
        roster=inputs.roster,
        trigger_kind=inputs.trigger_kind,
        include_kill_scene=True,
        movement_witness_records=inputs.move_witness_records,
        regroup_ticks=inputs.regroup_ticks,
    )
    stays = [
        spot
        for turn in inputs.transcript.turns
        for spot in _alibi_stay_placements(turn)
        if spot.player in inputs.roster
    ]
    spots: dict[PlayerId, tuple[CSpot, ...]] = {}
    for candidate in sorted(inputs.roster):
        found = {
            CSpot(placement.tick, placement.rooms, placement.event_id)
            for placement in paths.get(candidate, ())
        } | {
            CSpot(stay.tick, stay.rooms, stay.event_id)
            for stay in stays
            if stay.player == candidate
        }
        spots[candidate] = tuple(
            sorted(found, key=lambda s: (s.tick, tuple(sorted(s.rooms)), s.event_id))
        )
    return MappingProxyType(spots)


def c_pairs(
    spots: Sequence[CSpot], *, regroup_ticks: frozenset[int]
) -> tuple[tuple[CSpot, CSpot, Literal["walk", "regroup"]], ...]:
    """The pairs (c) reconciles, by the map or by the regroup."""

    found: list[tuple[CSpot, CSpot, Literal["walk", "regroup"]]] = []
    for index, earlier in enumerate(spots):
        for later in spots[index + 1 :]:
            how = reconcilable(earlier, later, regroup_ticks=regroup_ticks)
            if how is not None:
                found.append((earlier, later, how))
    return tuple(found)


# ---------------------------------------------------------------------------
# (b) the version-2 travel-check lines
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TravelEnd:
    """One end of a travel line: its tick and the canonical rooms it stands for."""

    tick: int
    rooms: frozenset[str]


@dataclass(frozen=True)
class TravelLine:
    """One travel-check row, classified; ``line`` stays in memory only."""

    subject: PlayerId
    verdict: TravelVerdict
    ends: tuple[TravelEnd, TravelEnd] | None
    kept: bool
    line: str

    @property
    def two_rooms(self) -> bool:
        """Whether some room of one end differs from some room of the other."""

        if self.ends is None:
            return False
        first, second = self.ends
        return any(a != b for a in first.rooms for b in second.rooms)


def relabel_plain_sightings(store: MemoryStore) -> MemoryStore:
    """A copy of ``store`` with each plain recorded sighting labelled a snapshot.

    A plain sighting is a first-hand ``saw_player`` row built from the pre-action
    state: no action in its payload and no delivery phase. Movement rows and
    action-sourced rows keep their unknown phase.
    """

    relabelled = MemoryStore()
    for event in store.recent(since_tick=0):
        plain = (
            event.type == "saw_player"
            and event.provenance == "observed"
            and event.payload.get("action") is None
            and "observation_phase" not in event.payload
        )
        relabelled.append(
            EpisodicEvent(
                tick=event.tick,
                type=event.type,
                payload={**event.payload, "observation_phase": "snapshot"}
                if plain
                else event.payload,
                provenance=event.provenance,
                observation_id=event.observation_id,
            )
        )
    return relabelled


def version_2_view(memory: AgentMemory, *, snapshot: bool) -> AgentMemory:
    """A deep copy of ``memory`` read as version 2, optionally relabelled."""

    view = deepcopy(memory)
    view.evidence_reasoning_version = 2
    if snapshot:
        view.episodic = relabel_plain_sightings(view.episodic)
    return view


def held_rooms(memory: AgentMemory, subject: PlayerId) -> Mapping[int, frozenset[str]]:
    """The raw room labels the version-2 context can place ``subject`` in, by tick.

    The same four sources the context reads: the voter's sightings (a movement
    row by its destination), each public regroup the subject was moved by, and
    reported claims of the three kinds it reads. A walking line's rooms must be
    among these (:func:`classify_travel_row` checks it), which is what lets a
    regroup line, whose text names no rooms, take its ends' rooms from here.
    """

    rooms: dict[int, set[str]] = {}
    for row in memory.episodic.recent(since_tick=0):
        if row.type == "public_regroup" and row.provenance == "public":
            if subject in {str(pid) for pid in row.payload["player_ids"]}:
                rooms.setdefault(row.tick, set()).add(str(row.payload["room"]))
        elif row.type == "reported_testimony" and row.provenance == "reported":
            room, tick = row.payload.get("room"), row.payload.get("from_tick")
            if (
                row.payload.get("kind") in ("whereabouts", "alibi", "saw_player")
                and row.payload.get("subject") == subject
                and isinstance(room, str)
                and isinstance(tick, int)
            ):
                rooms.setdefault(tick, set()).add(room)
        elif row.provenance == "observed" and row.type in (
            "saw_player",
            "saw_player_move",
        ):
            room = (
                row.payload.get("to_room")
                if row.type == "saw_player_move"
                else row.payload.get("room")
            )
            if row.payload.get("player_id") == subject and isinstance(room, str):
                rooms.setdefault(row.tick, set()).add(room)
    return MappingProxyType({tick: frozenset(labels) for tick, labels in rooms.items()})


def _canonical_union(labels: Iterable[str]) -> frozenset[str]:
    return frozenset().union(*(canonical_rooms(label) for label in labels))


def classify_travel_row(line: str, *, memory: AgentMemory, kept: bool) -> TravelLine:
    """Classify one rendered travel row; a row of no known shape raises."""

    walk = _WALK_LINE.match(line)
    if walk is not None:
        verdict = _WALK_VERDICTS.get(walk["verdict"])
        if verdict is None:
            raise RouteCheckReplayError(
                "a travel row ends with no known walking verdict"
            )
        subject = walk["subject"]
        held = held_rooms(memory, subject)
        ends = []
        for room_key, tick_key in (("room_a", "tick_a"), ("room_b", "tick_b")):
            tick = int(walk[tick_key])
            if walk[room_key] not in held.get(tick, frozenset()):
                raise RouteCheckReplayError(
                    "a travel row names a placement the memory does not hold"
                )
            ends.append(TravelEnd(tick, canonical_rooms(walk[room_key])))
        return TravelLine(subject, verdict, (ends[0], ends[1]), kept, line)
    regroup = _REGROUP_LINE.match(line)
    if regroup is not None:
        subject = regroup["subject"]
        held = held_rooms(memory, subject)
        first, second = int(regroup["tick_a"]), int(regroup["tick_b"])
        return TravelLine(
            subject,
            "crosses_regroup",
            (
                TravelEnd(first, _canonical_union(held.get(first, ()))),
                TravelEnd(second, _canonical_union(held.get(second, ()))),
            ),
            kept,
            line,
        )
    unverifiable = _UNVERIFIABLE_LINE.match(line)
    if unverifiable is not None:
        return TravelLine(unverifiable["subject"], "unverifiable", None, kept, line)
    raise RouteCheckReplayError("a travel row matches no known travel-check shape")


@dataclass(frozen=True)
class BVoterReading:
    """One voter's travel rows under (b) or (b-snapshot), and the view they came from."""

    voter: PlayerId
    lines: tuple[TravelLine, ...]
    view: AgentMemory


def b_voter_reading(
    memory: AgentMemory,
    *,
    voter: PlayerId,
    snapshot: bool,
    suspicion_override: Mapping[PlayerId, float] | None,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
) -> BVoterReading:
    """The travel rows a version-2 render of one voter's memory offers and keeps.

    The voter's own id and teammates are derived as the store derives them. The
    rows are classified; a row is kept when a version-2 render of a deep copy at
    the ballot re-render's budget carries it.
    """

    view = version_2_view(memory, snapshot=snapshot)
    own, teammates = _latest_self_guard_fields(view.episodic)
    rows = v2_evidence_context_rows(view, own_agent_id=own, teammate_ids=teammates)
    rendered = render_for_prompt(
        deepcopy(view), token_budget=token_budget, suspicion_override=suspicion_override
    )
    lines = tuple(
        classify_travel_row(row.line, memory=view, kept=row.line in rendered)
        for row in rows
        if row.kind in _TRAVEL_ROW_KINDS
    )
    return BVoterReading(voter=voter, lines=lines, view=view)


def require_no_claim_at_first_meeting(inputs: MeetingInputs) -> None:
    """Raise when a first meeting's voter already holds a reported claim."""

    if not inputs.first_meeting:
        return
    for voter in sorted(inputs.roster):
        if any(
            row.provenance == "reported"
            for row in inputs.memories[voter].episodic.recent(since_tick=0)
        ):
            raise RouteCheckReplayError(
                f"voter {voter} holds a reported claim at a first meeting"
            )


def require_faithful_rerender(inputs: MeetingInputs) -> None:
    """Each voter's memory, re-rendered as recorded, is the ballot's memory block.

    The recorded runner re-renders the ballot's memory at the default budget
    with the pre-vote suspicion; this repeats that render on a deep copy and
    requires it, whole, as the ``<memory>`` block of the voter's captured ballot
    prompt, so the budget the (b) render uses is the recording's. The block's
    delimiters are the ballot template's, so a render the budget cut short is no
    match.
    """

    for voter in sorted(inputs.roster):
        rendered = render_for_prompt(
            deepcopy(inputs.memories[voter]),
            token_budget=DEFAULT_TOKEN_BUDGET,
            suspicion_override=inputs.ballot_overrides[voter],
        )
        block = f"{_MEMORY_OPEN}{rendered}{_MEMORY_CLOSE}"
        if not any(block in prompt for prompt in inputs.ballot_prompts[voter]):
            raise RouteCheckReplayError(
                f"voter {voter}: the memory re-render is not the ballot's memory block"
            )


# ---------------------------------------------------------------------------
# One meeting's record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CheckCase:
    """What one check did for one ejection."""

    reaches: bool
    reaches_charge: bool
    insufficient_lines: int
    reason: Reason | None
    pair_reasons: tuple[tuple[Reason, int], ...]


@dataclass(frozen=True)
class CaseRecord:
    """One ejection, read role-blind."""

    ejected: PlayerId
    eject_voters: int
    reporter: bool
    placements: int
    reconcilable_pairs: int
    charges: int
    ballot_charges: int
    flag_charges: int
    charges_on_reconcilable_pair: int
    misjudged: bool
    misjudging_pairs: int
    walkable_pair: tuple[tuple[DisputeLeg, bool], ...]
    checks: tuple[tuple[Check, CheckCase], ...]
    pit_net: bool

    def check(self, name: Check) -> CheckCase:
        return dict(self.checks)[name]

    def leg(self, name: DisputeLeg) -> bool:
        return dict(self.walkable_pair)[name]


@dataclass(frozen=True)
class MeetingRecord:
    """One meeting's counts, keyed by (seed, meeting), with no role read."""

    seed: int
    meeting: int
    tick: int
    kind: MeetingKind
    witness_meeting: bool
    opener: PlayerId
    voters: int
    charges: int
    charges_on_reconcilable_pair: int
    lines: tuple[tuple[Check, int], ...]
    b_offered: tuple[tuple[TravelVerdict, int], ...]
    b_kept: tuple[tuple[TravelVerdict, int], ...]
    b_snapshot_offered: tuple[tuple[TravelVerdict, int], ...]
    b_snapshot_kept: tuple[tuple[TravelVerdict, int], ...]
    case: CaseRecord | None


def _verdict_counts(
    lines: Iterable[TravelLine],
) -> tuple[tuple[TravelVerdict, int], ...]:
    counts = Counter(line.verdict for line in lines)
    return tuple((verdict, counts[verdict]) for verdict in TRAVEL_VERDICTS)


def _ledger_bound(name: str) -> int:
    """One of the walkable clause's bounds, read where the live rule reads it."""

    value = vars(corroboration)[name]
    if not isinstance(value, int):
        raise RouteCheckReplayError(f"the ledger's {name} is not an integer")
    return value


def _a_pair_reason(
    pair: tuple[Placement, Placement], reading: AReading | None
) -> Reason:
    """Why (a) shows no line over one misjudging pair: the first reason that applies."""

    if any(end.kind not in A_INPUT_KINDS for end in pair):
        return "kind"
    if reading is None:
        return "residual"
    by_event = {spot.event_id: spot for spot in reading.path}
    stated = [by_event.get(end.event_id) for end in pair]
    if stated[0] is None or stated[1] is None:
        return "relevance_gate"
    earlier, later = sorted((stated[0], stated[1]), key=lambda spot: spot.tick)
    if (
        room_hops(
            earlier.rooms,
            later.rooms,
            max_hops=_ledger_bound("MAP_ARBITRATION_MAX_HOPS"),
        )
        is None
    ):
        return "hop_bound"
    if later.tick - earlier.tick > _ledger_bound("MAP_ARBITRATION_MAX_TICK_GAP"):
        return "tick_bound"
    if (earlier, later) in reading.qualifying_pairs and (
        earlier,
        later,
    ) not in reading.shown_pairs:
        return "cap"
    return "residual"


def _c_pair_reason(pair: tuple[Placement, Placement], spots: Sequence[CSpot]) -> Reason:
    if any(end.kind not in C_INPUT_KINDS for end in pair):
        return "kind"
    events = {spot.event_id for spot in spots}
    if any(end.event_id not in events for end in pair):
        return "relevance_gate"
    return "residual"


def _end_held(end: Placement, held: Mapping[int, frozenset[str]]) -> bool:
    return bool(end.rooms & _canonical_union(held.get(end.tick, ())))


def _line_over(line: TravelLine, pair: tuple[Placement, Placement]) -> bool:
    if line.ends is None:
        return False
    first, second = line.ends
    return all(
        travel_end.tick == end.tick and bool(travel_end.rooms & end.rooms)
        for travel_end, end in zip((first, second), pair, strict=True)
    )


def _b_pair_reason(
    pair: tuple[Placement, Placement],
    readings: Sequence[BVoterReading],
    *,
    subject: PlayerId,
) -> Reason:
    """Why no EJECT voter's (b) render shows a reaching line over one pair."""

    holders = [
        reading
        for reading in readings
        if all(_end_held(end, held_rooms(reading.view, subject)) for end in pair)
    ]
    if not holders:
        if any(
            end.kind not in B_CLAIM_KINDS
            and not any(
                _end_held(end, held_rooms(reading.view, subject))
                for reading in readings
            )
            for end in pair
        ):
            return "kind"
        return "claim_not_held"
    over = [
        line
        for reading in holders
        for line in reading.lines
        if line.subject == subject and _line_over(line, pair)
    ]
    if any(not line.kept for line in over):
        return "cap"
    if any(line.verdict == "insufficient_timing" for line in over):
        return "phase_rule"
    return "residual"


def _reaching(line: TravelLine) -> bool:
    return line.kept and line.two_rooms and line.verdict in ("fits", "crosses_regroup")


def _holds_charge_b(line: TravelLine, charged: frozenset[Placement]) -> bool:
    if line.ends is None:
        return False
    return any(
        end.tick == spot.tick and bool(end.rooms & spot.rooms)
        for end in line.ends
        for spot in charged
    )


def _case_reason(pair_reasons: Sequence[Reason]) -> Reason | None:
    """The first reason, in the fixed order, among the pairs' reasons."""

    for reason in REASONS:
        if reason in pair_reasons:
            return reason
    return None


def _check_case(
    *,
    reaches: bool,
    reaches_charge: bool,
    insufficient_lines: int,
    misjudged: bool,
    pair_reasons: Sequence[Reason],
) -> CheckCase:
    counted = Counter(pair_reasons) if misjudged and not reaches else Counter[Reason]()
    return CheckCase(
        reaches=reaches,
        reaches_charge=reaches_charge,
        insufficient_lines=insufficient_lines,
        reason=_case_reason(pair_reasons) if misjudged and not reaches else None,
        pair_reasons=tuple(
            (reason, counted[reason]) for reason in REASONS if counted[reason]
        ),
    )


def _require_input_kinds(
    universe: Sequence[Placement],
    spots_by_subject: Mapping[PlayerId, Iterable[str]],
    kinds: frozenset[PlacementKind],
    *,
    check: str,
) -> None:
    """Every event a check placed a subject by is a spoken placement of its kinds."""

    for subject, events in spots_by_subject.items():
        allowed = {
            spot.event_id
            for spot in universe
            if spot.player == subject and spot.kind in kinds
        }
        if not set(events) <= allowed:
            raise RouteCheckReplayError(
                f"{check} placed {subject} by an event of a kind it is not read to take"
            )


def read_meeting(
    inputs: MeetingInputs,
    *,
    seed: int,
    index: int,
    tick: int,
    kind: MeetingKind,
    witness_meeting: bool,
) -> tuple[MeetingRecord, frozenset[str]]:
    """Count one meeting under every check. Reads no role.

    Returns the record and every travel row read, which the output scan holds
    the outputs against.
    """

    require_no_claim_at_first_meeting(inputs)
    require_faithful_rerender(inputs)
    universe = spoken_placements(inputs.transcript)
    regroup = inputs.regroup_ticks

    # The process count over every charged target at the table.
    targets = {
        ballot.target for ballot in inputs.ballots if ballot.target in inputs.roster
    } | {
        subject
        for flag in inputs.contradictions
        for subject in flag.subjects
        if subject in inputs.roster
    }
    charges_total = 0
    charges_resting = 0
    for target in sorted(targets):
        own = placements_of(universe, target)
        for charge in charges_against(
            target,
            ballots=inputs.ballots,
            contradictions=inputs.contradictions,
            universe=universe,
        ):
            charges_total += 1
            if misjudging_pairs(own, charge.placements, regroup_ticks=regroup):
                charges_resting += 1

    a_by_leg = {leg: a_readings(ledger_call(inputs, leg=leg)) for leg in A_LEGS}
    _require_input_kinds(
        universe,
        {s: [p.event_id for p in r.path] for s, r in a_by_leg["a"].items()},
        A_INPUT_KINDS,
        check="(a)",
    )
    spots = c_spots(inputs)
    _require_input_kinds(
        universe,
        {s: [p.event_id for p in found] for s, found in spots.items()},
        C_INPUT_KINDS,
        check="(c)",
    )
    c_lines = {
        subject: c_pairs(found, regroup_ticks=regroup)
        for subject, found in spots.items()
    }
    b_readings = {
        snapshot: {
            voter: b_voter_reading(
                inputs.memories[voter],
                voter=voter,
                snapshot=snapshot,
                suspicion_override=inputs.ballot_overrides[voter],
            )
            for voter in sorted(inputs.roster)
        }
        for snapshot in (False, True)
    }
    lines: list[tuple[Check, int]] = []
    for leg in ("a", "a_transcript_only"):
        lines.append(
            (
                leg,
                _shown_voter_lines(
                    inputs.roster,
                    {s: len(r.shown) for s, r in a_by_leg[leg].items()},
                ),
            )
        )
    for name, snapshot in (("b", False), ("b_snapshot", True)):
        lines.append(
            (
                cast(Check, name),
                sum(
                    1
                    for reading in b_readings[snapshot].values()
                    for line in reading.lines
                    if line.kept
                ),
            )
        )
    lines.append(
        (
            "c",
            _shown_voter_lines(
                inputs.roster, {s: 1 if p else 0 for s, p in c_lines.items()}
            ),
        )
    )

    case = None
    if inputs.ejected is not None:
        case = _read_case(
            inputs,
            universe=universe,
            a_by_leg=a_by_leg,
            spots=spots,
            c_lines=c_lines,
            b_readings=b_readings,
        )
    texts = frozenset(
        line.line
        for readings in b_readings.values()
        for reading in readings.values()
        for line in reading.lines
    )
    record = MeetingRecord(
        seed=seed,
        meeting=index,
        tick=tick,
        kind=kind,
        witness_meeting=witness_meeting,
        opener=inputs.opener,
        voters=len(inputs.roster),
        charges=charges_total,
        charges_on_reconcilable_pair=charges_resting,
        lines=tuple(lines),
        b_offered=_verdict_counts(
            line for r in b_readings[False].values() for line in r.lines
        ),
        b_kept=_verdict_counts(
            line for r in b_readings[False].values() for line in r.lines if line.kept
        ),
        b_snapshot_offered=_verdict_counts(
            line for r in b_readings[True].values() for line in r.lines
        ),
        b_snapshot_kept=_verdict_counts(
            line for r in b_readings[True].values() for line in r.lines if line.kept
        ),
        case=case,
    )
    return record, texts


def _read_case(
    inputs: MeetingInputs,
    *,
    universe: Sequence[Placement],
    a_by_leg: Mapping[ALeg, Mapping[PlayerId, AReading]],
    spots: Mapping[PlayerId, tuple[CSpot, ...]],
    c_lines: Mapping[
        PlayerId, Sequence[tuple[CSpot, CSpot, Literal["walk", "regroup"]]]
    ],
    b_readings: Mapping[bool, Mapping[PlayerId, BVoterReading]],
) -> CaseRecord:
    ejected = inputs.ejected
    if ejected is None:
        raise ValueError("a case is an ejection")
    regroup = inputs.regroup_ticks
    own = placements_of(universe, ejected)
    charges = charges_against(
        ejected,
        ballots=inputs.ballots,
        contradictions=inputs.contradictions,
        universe=universe,
    )
    charged = frozenset().union(*(charge.placements for charge in charges))
    pairs = misjudging_pairs(own, charged, regroup_ticks=regroup)
    misjudged = bool(pairs)
    eject_voters = sorted(
        {ballot.voter for ballot in inputs.ballots if ballot.target == ejected}
    )
    charged_events = {spot.event_id for spot in charged}

    checks: list[tuple[Check, CheckCase]] = []
    for leg in ("a", "a_transcript_only"):
        reading = a_by_leg[leg].get(ejected)
        reaches = reading is not None and bool(reading.shown) and bool(eject_voters)
        reaches_charge = (
            reaches
            and reading is not None
            and any(
                earlier.event_id in charged_events or later.event_id in charged_events
                for earlier, later in reading.shown_pairs
            )
        )
        checks.append(
            (
                leg,
                _check_case(
                    reaches=reaches,
                    reaches_charge=reaches_charge,
                    insufficient_lines=0,
                    misjudged=misjudged,
                    pair_reasons=[_a_pair_reason(pair, reading) for pair in pairs],
                ),
            )
        )
    for name, snapshot in (("b", False), ("b_snapshot", True)):
        voters = [b_readings[snapshot][voter] for voter in eject_voters]
        about = [
            line
            for reading in voters
            for line in reading.lines
            if line.subject == ejected
        ]
        reaching = [line for line in about if _reaching(line)]
        checks.append(
            (
                cast(Check, name),
                _check_case(
                    reaches=bool(reaching),
                    reaches_charge=any(
                        _holds_charge_b(line, charged) for line in reaching
                    ),
                    insufficient_lines=sum(
                        1
                        for line in about
                        if line.kept
                        and line.two_rooms
                        and line.verdict == "insufficient_timing"
                    ),
                    misjudged=misjudged,
                    pair_reasons=[
                        _b_pair_reason(pair, voters, subject=ejected) for pair in pairs
                    ],
                ),
            )
        )
    shown_c = c_lines.get(ejected, ())
    reaches_c = bool(shown_c) and bool(eject_voters)
    checks.append(
        (
            "c",
            _check_case(
                reaches=reaches_c,
                reaches_charge=reaches_c
                and any(
                    earlier.event_id in charged_events
                    or later.event_id in charged_events
                    for earlier, later, _ in shown_c
                ),
                insufficient_lines=0,
                misjudged=misjudged,
                pair_reasons=[
                    _c_pair_reason(pair, spots.get(ejected, ())) for pair in pairs
                ],
            ),
        )
    )
    return CaseRecord(
        ejected=ejected,
        eject_voters=len(eject_voters),
        reporter=inputs.trigger_kind == "report" and ejected == inputs.opener,
        placements=len(own),
        reconcilable_pairs=sum(
            1
            for earlier, later in ordered_pairs(own)
            if reconcilable(earlier, later, regroup_ticks=regroup) is not None
        ),
        charges=len(charges),
        ballot_charges=sum(1 for charge in charges if charge.source == "ballot"),
        flag_charges=sum(1 for charge in charges if charge.source == "flag"),
        charges_on_reconcilable_pair=sum(
            1
            for charge in charges
            if misjudging_pairs(own, charge.placements, regroup_ticks=regroup)
        ),
        misjudged=misjudged,
        misjudging_pairs=len(pairs),
        walkable_pair=(
            *(
                (
                    leg,
                    bool((row := a_by_leg[leg].get(ejected)) is not None and row.shown),
                )
                for leg in A_LEGS
            ),
            (
                "a_with_movement_origins",
                walkable_with_movement_origins(inputs, ejected),
            ),
        ),
        checks=tuple(checks),
        pit_net=any(
            ballot.target == ejected
            and IMPOSSIBLE_TRANSIT_PATTERN.search(ballot.rationale_text) is not None
            for ballot in inputs.ballots
        ),
    )


# ---------------------------------------------------------------------------
# The walk, with its integrity checks
# ---------------------------------------------------------------------------


def meeting_kind(fact: MeetingFact) -> MeetingKind:
    """Button, or a report with or without vent proof (the census's predicate)."""

    if fact.trigger_kind == "emergency":
        return "button"
    proof = any(subjects & fact.living for subjects in fact.vent_flag_subjects)
    return "report_vent_proof" if proof else "report_no_vent_proof"


def is_witness_meeting(
    fact: MeetingFact, *, kills: Sequence[KillFact], previous_tick: int | None
) -> bool:
    """A report whose reporter the kill facts record witnessing a kill since the last meeting."""

    if fact.trigger_kind != "report":
        return False
    floor = -1 if previous_tick is None else previous_tick
    return any(
        fact.opener in kill.witnesses and floor < kill.tick <= fact.tick
        for kill in kills
    )


def walk_game(
    path: Path,
    *,
    label: str,
    seed: int,
    renderers: Mapping[str, PromptRenderers],
) -> Iterator[ReconstructedMeeting]:
    """The recording's meetings through the faithful walk, or a raise naming one.

    A state hash the walk cannot reproduce and a recorded prompt it did not
    re-render both raise, naming (column, seed, meeting).
    """

    walker = walk_replay_meetings(
        path, game_map=load_canonical_map(), renderers_for_set=renderers
    )
    index = 0
    while True:
        try:
            meeting = next(walker)
        except StopIteration:
            return
        except AssertionError as error:
            raise RouteCheckReplayError(
                f"{label} seed {seed} meeting {index}: the walk did not reproduce "
                f"the recording ({error})"
            ) from error
        missed = {call.prompt for call in meeting.entry.llm_calls} - meeting.hit_prompts
        if missed:
            raise RouteCheckReplayError(
                f"{label} seed {seed} meeting {index}: {len(missed)} recorded "
                "prompt(s) were not re-rendered by the walk"
            )
        yield meeting
        index += 1


def read_game(
    path: Path,
    *,
    label: str,
    game: GameFacts,
    renderers: Mapping[str, PromptRenderers],
) -> tuple[tuple[MeetingRecord, ...], frozenset[str]]:
    """Every meeting of one game, each counted before the walk resumes."""

    seed = game.seed
    recorded = recorded_experiment_config(read_all_entries(path))
    earlier: list[int] = []
    records: list[MeetingRecord] = []
    texts: set[str] = set()
    for index, meeting in enumerate(
        walk_game(path, label=label, seed=seed, renderers=renderers)
    ):
        if index >= len(game.meetings):
            raise RouteCheckReplayError(
                f"{label} seed {seed} meeting {index}: the census holds no such meeting"
            )
        fact = game.meetings[index]
        if (
            fact.meeting_id != meeting.meeting_id
            or fact.opener != meeting.result.triggered_by
            or fact.ejected != meeting.result.ejected_player_id
            or fact.trigger_kind != meeting.trigger_kind
        ):
            raise RouteCheckReplayError(
                f"{label} seed {seed} meeting {index}: the census and the walk "
                "read different meetings"
            )
        inputs = meeting_inputs(
            meeting, regroup_ticks=derive_regroup_ticks(recorded, earlier)
        )
        record, read = read_meeting(
            inputs,
            seed=seed,
            index=index,
            tick=fact.tick,
            kind=meeting_kind(fact),
            witness_meeting=is_witness_meeting(
                fact,
                kills=game.kills,
                previous_tick=game.meetings[index - 1].tick if index else None,
            ),
        )
        records.append(record)
        texts.update(read)
        earlier.append(meeting.entry.tick)
    if len(records) != len(game.meetings):
        raise RouteCheckReplayError(
            f"{label} seed {seed} meeting {len(records)}: the census holds "
            f"{len(game.meetings)} meetings and the walk read {len(records)}"
        )
    return tuple(records), frozenset(texts)


def read_set(
    set_dir: Path, *, label: str, census: CensusInputs
) -> tuple[tuple[MeetingRecord, ...], frozenset[str]]:
    """Every meeting of one column's set, against that set's census."""

    games = {game.seed: game for game in census.games}
    seeds = seeds_on_disk(set_dir)
    if sorted(games) != seeds:
        raise RouteCheckReplayError(
            f"{label}: the census and the set hold different seeds"
        )
    renderers = _canonical_renderers()
    records: list[MeetingRecord] = []
    texts: set[str] = set()
    for seed in seeds:
        found, read = read_game(
            set_dir / f"replay-seed-{seed}.jsonl",
            label=label,
            game=games[seed],
            renderers=renderers,
        )
        records.extend(found)
        texts.update(read)
    return tuple(records), frozenset(texts)


def forbidden_strings(set_dir: Path) -> frozenset[str]:
    """Recorded turn texts and ballot rationales the outputs must never carry."""

    found: set[str] = set()
    for seed in seeds_on_disk(set_dir):
        for entry in read_all_entries(set_dir / f"replay-seed-{seed}.jsonl"):
            if isinstance(entry, MeetingReplayEntry):
                found.update(turn.free_text for turn in entry.transcript.turns)
                found.update(ballot.rationale_text for ballot in entry.ballots)
    return frozenset(text for text in found if len(text) >= _SCAN_MIN_LENGTH)


def scan_outputs(texts: Sequence[str], forbidden: Iterable[str]) -> None:
    """Raise when an output carries any recorded text it read."""

    for text in forbidden:
        if len(text) < _SCAN_MIN_LENGTH:
            continue
        if any(text in output for output in texts):
            raise RouteCheckReplayError(
                "an output carries recorded text; nothing written"
            )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _half(reached: int, total: int) -> bool:
    return 2 * reached >= total


def _group_counts(records: Sequence[MeetingRecord]) -> dict[str, object]:
    """Every count over one group of meetings, cases counted where they fall."""

    cases = [(record, record.case) for record in records if record.case is not None]
    misjudged = [(record, case) for record, case in cases if case.misjudged]
    counts: dict[str, object] = {
        "meetings": len(records),
        "witness_meetings": sum(1 for record in records if record.witness_meeting),
        "charges": sum(record.charges for record in records),
        "charges_on_reconcilable_pair": sum(
            record.charges_on_reconcilable_pair for record in records
        ),
        "lines": {
            check: sum(dict(record.lines)[check] for record in records)
            for check in CHECKS
        },
        "b_offered": {
            v: sum(dict(record.b_offered)[v] for record in records)
            for v in TRAVEL_VERDICTS
        },
        "b_kept": {
            v: sum(dict(record.b_kept)[v] for record in records)
            for v in TRAVEL_VERDICTS
        },
        "b_snapshot_offered": {
            v: sum(dict(record.b_snapshot_offered)[v] for record in records)
            for v in TRAVEL_VERDICTS
        },
        "b_snapshot_kept": {
            v: sum(dict(record.b_snapshot_kept)[v] for record in records)
            for v in TRAVEL_VERDICTS
        },
    }
    counts.update(_case_counts(cases))
    counts["misjudged_at_witness_meetings"] = sum(
        1 for record, _ in misjudged if record.witness_meeting
    )
    return counts


def _case_counts(
    cases: Sequence[tuple[MeetingRecord, CaseRecord]],
) -> dict[str, object]:
    misjudged = [(record, case) for record, case in cases if case.misjudged]
    at_witness = [
        (record, case) for record, case in misjudged if record.witness_meeting
    ]
    return {
        "ejections": len(cases),
        "reporter_ejections": sum(1 for _, case in cases if case.reporter),
        "ejected_witnesses": sum(
            1 for record, case in cases if case.reporter and record.witness_meeting
        ),
        "ejections_with_reconcilable_pair": sum(
            1 for _, case in cases if case.reconcilable_pairs
        ),
        "ejections_with_a_charge": sum(1 for _, case in cases if case.charges),
        "misjudged": len(misjudged),
        "walkable_pair": {
            leg: sum(1 for _, case in cases if case.leg(leg)) for leg in DISPUTE_LEGS
        },
        "pit_net": sum(1 for _, case in cases if case.pit_net),
        "pit_net_misjudged": sum(1 for _, case in misjudged if case.pit_net),
        "reaches": {
            check: sum(1 for _, case in cases if case.check(check).reaches)
            for check in CHECKS
        },
        "reaches_misjudged": {
            check: sum(1 for _, case in misjudged if case.check(check).reaches)
            for check in CHECKS
        },
        "reaches_charge_misjudged": {
            check: sum(1 for _, case in misjudged if case.check(check).reaches_charge)
            for check in CHECKS
        },
        "reaches_misjudged_at_witness": {
            check: sum(1 for _, case in at_witness if case.check(check).reaches)
            for check in CHECKS
        },
        "insufficient_lines_misjudged": {
            check: sum(case.check(check).insufficient_lines for _, case in misjudged)
            for check in CHECKS
        },
        "unreached_reasons": {
            check: {
                reason: sum(
                    1 for _, case in misjudged if case.check(check).reason == reason
                )
                for reason in REASONS
            }
            for check in CHECKS
        },
        "unreached_pair_reasons": {
            check: {
                reason: sum(
                    dict(case.check(check).pair_reasons).get(reason, 0)
                    for _, case in misjudged
                )
                for reason in REASONS
            }
            for check in CHECKS
        },
    }


def ejection_class(
    record: MeetingRecord, case: CaseRecord, roles: Mapping[PlayerId, Role]
) -> tuple[EjectionClass, ...]:
    """The classes one ejection is described under; an ejected witness is innocent too."""

    found: list[EjectionClass] = [
        "impostor" if roles[case.ejected] == "IMPOSTOR" else "innocent"
    ]
    if case.reporter and record.witness_meeting:
        found.append("ejected_witness")
    return tuple(found)


def _record_payload(record: MeetingRecord) -> dict[str, object]:
    payload: dict[str, object] = {
        "seed": record.seed,
        "meeting": record.meeting,
        "tick": record.tick,
        "kind": record.kind,
        "witness_meeting": record.witness_meeting,
        "opener": record.opener,
        "voters": record.voters,
        "charges": record.charges,
        "charges_on_reconcilable_pair": record.charges_on_reconcilable_pair,
        "lines": dict(record.lines),
        "b_kept": dict(record.b_kept),
        "b_snapshot_kept": dict(record.b_snapshot_kept),
    }
    case = record.case
    if case is not None:
        payload["case"] = {
            "ejected": case.ejected,
            "eject_voters": case.eject_voters,
            "reporter": case.reporter,
            "placements": case.placements,
            "reconcilable_pairs": case.reconcilable_pairs,
            "charges": case.charges,
            "ballot_charges": case.ballot_charges,
            "flag_charges": case.flag_charges,
            "charges_on_reconcilable_pair": case.charges_on_reconcilable_pair,
            "misjudged": case.misjudged,
            "misjudging_pairs": case.misjudging_pairs,
            "walkable_pair": dict(case.walkable_pair),
            "pit_net": case.pit_net,
            "checks": {
                name: {
                    "reaches": check.reaches,
                    "reaches_charge": check.reaches_charge,
                    "insufficient_lines": check.insufficient_lines,
                    "reason": check.reason,
                    "pair_reasons": dict(check.pair_reasons),
                }
                for name, check in case.checks
            },
        }
    return payload


def _moved_by(case: CaseRecord) -> str | None:
    """Which dropped input moves the case between (a) as built and the probe."""

    if case.leg("a") == case.leg("a_transcript_only"):
        return None
    movement = case.leg("a_no_movement") != case.leg("a")
    regroup = case.leg("a_no_regroup") != case.leg("a")
    if movement and regroup:
        return "either input alone"
    if movement:
        return "movement records"
    if regroup:
        return "regroup ticks"
    return "both inputs together"


def class_payload(
    records: Sequence[MeetingRecord], roles: Mapping[int, Mapping[PlayerId, Role]]
) -> dict[str, object]:
    """The role-read half of a column: counts and case lists by ejection class."""

    grouped: dict[EjectionClass, list[tuple[MeetingRecord, CaseRecord]]] = {
        name: [] for name in EJECTION_CLASSES
    }
    for record in records:
        if record.case is None:
            continue
        for name in ejection_class(record, record.case, roles[record.seed]):
            grouped[name].append((record, record.case))
    counts: dict[str, object] = {}
    for name in EJECTION_CLASSES:
        members = grouped[name]
        section = _case_counts(members)
        section["misjudged_at_witness_meetings"] = sum(
            1 for record, case in members if case.misjudged and record.witness_meeting
        )
        counts[name] = section
    cases = [
        {
            "seed": record.seed,
            "meeting": record.meeting,
            "classes": list(ejection_class(record, case, roles[record.seed])),
            "misjudged": case.misjudged,
            "walkable_pair": dict(case.walkable_pair),
            "moved_by": _moved_by(case),
        }
        for record in records
        if (case := record.case) is not None
        and (
            "impostor" not in ejection_class(record, case, roles[record.seed])
            or len({value for _, value in case.walkable_pair}) > 1
        )
    ]
    return {"counts": counts, "cases": cases}


def rule_inputs(counts: Mapping[str, object]) -> dict[str, object]:
    """M, W and R(X) for the reading rule, from one column's whole-set counts."""

    reaches = cast(Mapping[str, int], counts["reaches_misjudged"])
    at_witness = cast(Mapping[str, int], counts["reaches_misjudged_at_witness"])
    return {
        "M": counts["misjudged"],
        "W": counts["misjudged_at_witness_meetings"],
        "R": dict(reaches),
        "R_W": dict(at_witness),
    }


def reading_branch(inputs: Mapping[str, object]) -> int:
    """The branch of the card's rule that ``inputs`` takes (1 to 4)."""

    total = cast(int, inputs["M"])
    witnessed = cast(int, inputs["W"])
    reaches = cast(Mapping[str, int], inputs["R"])
    at_witness = cast(Mapping[str, int], inputs["R_W"])
    if total == 0:
        return 1
    for branch, check in ((2, "b_snapshot"), (3, "c")):
        if _half(reaches[check], total) and (
            witnessed == 0 or _half(at_witness[check], witnessed)
        ):
            return branch
    return 4


def s9_agreement(counts: Mapping[str, object]) -> dict[str, object]:
    """s9's walkable-pair ejections under (a) as built, held to the committed cells.

    A different figure raises: it stops the card and goes to the orchestrator,
    and is never adjusted to fit.
    """

    legs = cast(Mapping[str, int], counts["walkable_pair"])
    ejections = cast(int, counts["ejections"])
    found = (legs["a"], ejections)
    if found != S9_WALKABLE_PAIR_EJECTIONS:
        raise RouteCheckReplayError(
            f"s9: (a) as built reads {found[0]} of {found[1]} ejections with a walkable "
            f"pair; the committed cells say {S9_WALKABLE_PAIR_EJECTIONS[0]} of "
            f"{S9_WALKABLE_PAIR_EJECTIONS[1]}"
        )
    return {
        "expected": list(S9_WALKABLE_PAIR_EJECTIONS),
        "a": [legs["a"], ejections],
        "a_transcript_only": [legs["a_transcript_only"], ejections],
        "a_transcript_only_agrees": (legs["a_transcript_only"], ejections)
        == S9_WALKABLE_PAIR_EJECTIONS,
    }


def column_payload(
    source: ColumnSource,
    *,
    config: Mapping[str, object] | None,
    records: Sequence[MeetingRecord],
    roles: Mapping[int, Mapping[PlayerId, Role]],
) -> dict[str, object]:
    """One column's JSON: provenance, counts by meeting kind, classes, meetings."""

    whole = _group_counts(records)
    payload: dict[str, object] = {
        "label": source.label,
        "commit": source.commit,
        "sha": source.sha,
        "path": source.path,
        "tree": source.tree,
        "declared_config": declared_config_path(source.label),
        "recorded_experiment_config": dict(config) if config is not None else None,
        "games": len({record.seed for record in records}),
        "all": whole,
        "by_kind": {
            kind: _group_counts([record for record in records if record.kind == kind])
            for kind in MEETING_KINDS
        },
        "rule_inputs": rule_inputs(whole),
        "classes": class_payload(records, roles),
        "meetings": [_record_payload(record) for record in records],
    }
    if source.label == "s9":
        payload["s9_agreement"] = s9_agreement(whole)
    return payload


def build_payload(columns: Sequence[dict[str, object]]) -> dict[str, object]:
    labels = [cast(str, column["label"]) for column in columns]
    reading: dict[str, object] = {
        cast(str, column["label"]): {
            "branch": reading_branch(cast(Mapping[str, object], column["rule_inputs"])),
        }
        for column in columns
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "instrument": "experiments/lab/route_check_replay.py",
        "columns": columns,
        "reading": {
            "rule_applies_to": "r2" if "r2" in labels else None,
            "branches": reading,
        },
    }


def serialize(payload: Mapping[str, object]) -> str:
    """The JSON text: indented, keys sorted, one line per meeting record."""

    columns = cast(Sequence[Mapping[str, object]], payload["columns"])
    compact: dict[str, str] = {}
    shells: list[dict[str, object]] = []
    for position, column in enumerate(columns):
        meetings = cast(Sequence[Mapping[str, object]], column["meetings"])
        markers = []
        for index, record in enumerate(meetings):
            marker = f"@meeting:{position}:{index}@"
            compact[json.dumps(marker)] = json.dumps(
                record, sort_keys=True, separators=(",", ":")
            )
            markers.append(marker)
        shells.append({**column, "meetings": markers})
    text = json.dumps({**payload, "columns": shells}, indent=1, sort_keys=True)
    for marker, record_text in compact.items():
        text = text.replace(marker, record_text, 1)
    return text + "\n"


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

_LEG_NAMES: Final[Mapping[DisputeLeg, str]] = MappingProxyType(
    {
        "a": "as built",
        "a_transcript_only": "transcript only",
        "a_no_movement": "no movement records",
        "a_no_regroup": "no regroup ticks",
        "a_with_movement_origins": "with movement origins",
    }
)

_CHECK_NAMES: Final[Mapping[Check, str]] = MappingProxyType(
    {
        "a": "(a) as built",
        "a_transcript_only": "(a) transcript only",
        "b": "(b) as recorded",
        "b_snapshot": "(b-snapshot), approximation",
        "c": "(c) reference",
    }
)

_REASON_NAMES: Final[Mapping[Reason, str]] = MappingProxyType(
    {
        "kind": "placement kind outside the check's inputs",
        "relevance_gate": "dropped by the relevance gate",
        "hop_bound": "beyond the hop bound",
        "tick_bound": "beyond the tick bound",
        "cap": "cut by the cap or the memory budget",
        "claim_not_held": "claim not yet held at ballot time",
        "phase_rule": "the unknown-phase rule",
        "residual": "none of the listed reasons",
    }
)

_BRANCH_TEXT: Final[Mapping[int, str]] = MappingProxyType(
    {
        1: "no misjudged case: name no route arm",
        2: "name evidence_reasoning_version = 2, conditional on the owner lifting the "
        "temporal-observations exclusion it requires",
        3: "name the narrow new field, shaped by the reference reading's unreached reasons",
        4: "name no route arm, and state what the unreached cases share",
    }
)


def _table(header: Sequence[str], rows: Sequence[Sequence[object]]) -> list[str]:
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return lines


def render_report(payload: Mapping[str, object]) -> str:
    """The lab report, a pure function of the JSON payload."""

    columns = cast(Sequence[Mapping[str, object]], payload["columns"])
    out: list[str] = [
        "# Route-check replay",
        "",
        "Written by `experiments/lab/route_check_replay.py` from "
        "`experiments/lab/results-route-check-replay.json`; `--check` recomputes "
        "both from the commits recorded below.",
        "",
        "## Decision informed",
        "",
        "Whether a round 3 with one meeting-layer route check is worth the owner's "
        "spend, and which check. This report decides nothing and authorizes no "
        "recording.",
        "",
        "## Hypothesis",
        "",
        "Some ejections in the recorded games rest on a charge whose stated pair of "
        "places the map or the public regroup in fact allows, and at least one "
        "candidate check would have put a line about that pair in front of a voter "
        "who voted to eject.",
        "",
        "## Method",
        "",
        "Each column is one recording of seeds 0-49 at 9 players and 2 impostors, "
        "read alone and never pooled, from the exact commit below. Every meeting is "
        "re-run through the committed reconstruction walk with the recording's own "
        "settings: every state hash and every recorded prompt is reproduced or the "
        "run stops, and the meetings agree one for one with the gameplay census.",
        "",
    ]
    out.extend(
        _table(
            ("column", "commit", "path", "tree", "declared config", "games"),
            [
                (
                    column["label"],
                    f"`{column['sha']}`",
                    f"`{column['path']}`",
                    f"`{column['tree']}`",
                    f"`{column['declared_config']}`"
                    if column["declared_config"]
                    else "none",
                    column["games"],
                )
                for column in columns
            ],
        )
    )
    out.extend(
        [
            "",
            "Terms, as counted here:",
            "",
            "- A **placement** is a player put in a room at a tick by something said at "
            "the meeting: a sighting (its subject and the company it names), a movement "
            "sighting (its destination), a whereabouts (its speaker), an alibi route "
            "(each end of each stay) or a vent sighting. Nothing is filtered out.",
            "- A pair of placements of one player is **reconcilable** when the rooms "
            "differ and the doorway hops between them are at least one and at most the "
            "ticks elapsed, or when a public regroup falls inside the interval.",
            "- A **charge** is an eject ballot whose cited turn places the target, or a "
            "contradiction flag naming the target whose two events both place the target.",
            "- A **misjudged case** is an ejection with a charge whose placement is one end "
            "of a reconcilable pair. This is a count of process, not of who was guilty.",
            "- A **witness meeting** is a report whose reporter the engine recorded "
            "watching a kill since the previous meeting; an **ejected witness** is that "
            "reporter voted out.",
            "- A check **reaches** a case when it shows a line about the ejected player over "
            "two different rooms that reconciles, fits or crosses the regroup, to at least "
            "one voter who voted to eject; it **reaches the charge** when that line's pair "
            "holds a charged placement. Lines saying the timing is insufficient are counted "
            "apart and never reach.",
            "- **(a) as built** is the corroboration ledger's walkable-pair clause with the "
            "movement records and regroup ticks the meeting manager passes: one door "
            "apart, one tick apart, at most two pairs per player. **(a) transcript only** "
            "drops those two inputs, as the earlier transcript-only probe did; the legs "
            "**no movement records** and **no regroup ticks** drop one each. **With "
            "movement origins** is informational and no check: (a) as built with each "
            "spoken movement sighting also placing its subject in the room it left, one "
            "tick earlier, a placement the live clause deliberately does not make.",
            "- **(b) as recorded** is the travel-check block of the evidence-reasoning "
            "version 2 memory, rendered from the memory each voter held when the meeting "
            "opened and kept only if the ballot's memory budget keeps it. **(b-snapshot)** "
            "relabels each plain recorded sighting a start-of-tick snapshot; it is an "
            "approximation of the observation delivery that version requires, which would "
            "also add event rows these recordings do not hold.",
            "- **(c) reference** pairs every stated placement of a living candidate, "
            "including alibi stays, over the whole map, and names a crossing of the "
            "regroup. It is a reading computed here, not a mechanism.",
            "- **Lines shown to voters** sums, over the voters of every meeting, the lines "
            "each one would read: one per walkable pair under (a), one per kept "
            "travel-check row under (b), one per candidate with a reconciled pair under "
            "(c). A voter reads (a) and (c) lines about every candidate but themself.",
            "- The **judgment net** is the committed pattern for ballot prose asserting "
            "a physical impossibility (`scripts/counterfactual_phase21.py`); it is an "
            "informational column, never the reading.",
            "- An unreached misjudged case is given the first reason, in this order, that "
            "applies to any of its reconcilable charged pairs: "
            + "; ".join(_REASON_NAMES[reason] for reason in REASONS)
            + ".",
            "",
            "Replayed meetings do not carry their consequences forward: a different "
            "ejection would have changed every later meeting, so these counts are per "
            "meeting and never a re-simulated outcome.",
            "",
            "## Result",
            "",
        ]
    )
    for column in columns:
        out.extend(_column_section(column))
    out.extend(_reading_section(payload, columns))
    return "\n".join(out) + "\n"


def _column_section(column: Mapping[str, object]) -> list[str]:
    whole = cast(Mapping[str, object], column["all"])
    by_kind = cast(Mapping[str, Mapping[str, object]], column["by_kind"])
    classes = cast(Mapping[str, object], column["classes"])
    class_counts = cast(Mapping[str, Mapping[str, object]], classes["counts"])
    groups: list[tuple[str, Mapping[str, object]]] = [("all meetings", whole)]
    groups.extend((kind.replace("_", " "), by_kind[kind]) for kind in MEETING_KINDS)
    out = [f"### Column {column['label']}", ""]
    out.extend(
        _table(
            (
                "meetings",
                "count",
                "witness meetings",
                "ejections",
                "charges at the table",
                "resting on a reconcilable pair",
                "misjudged",
            ),
            [
                (
                    name,
                    group["meetings"],
                    group["witness_meetings"],
                    group["ejections"],
                    group["charges"],
                    group["charges_on_reconcilable_pair"],
                    group["misjudged"],
                )
                for name, group in groups
            ],
        )
    )
    out.append("")
    out.extend(
        _table(
            (
                "check",
                "lines shown to voters",
                "reaches misjudged",
                "reaches the charge",
            ),
            [
                (
                    _CHECK_NAMES[check],
                    cast(Mapping[str, int], whole["lines"])[check],
                    f"{cast(Mapping[str, int], whole['reaches_misjudged'])[check]} of "
                    f"{whole['misjudged']}",
                    cast(Mapping[str, int], whole["reaches_charge_misjudged"])[check],
                )
                for check in CHECKS
            ],
        )
    )
    out.append("")
    out.append(
        "By ejection class, as description only (an ejected witness is innocent too). "
        "Each check column counts the class's misjudged cases that check reaches; the "
        "judgment-net column counts the class's ejections with an eject ballot the "
        "net tags:"
    )
    out.append("")
    out.extend(
        _table(
            (
                "class",
                "ejections",
                "misjudged",
                *(_CHECK_NAMES[check] for check in CHECKS),
                "judgment net",
            ),
            [
                (
                    name.replace("_", " "),
                    counts["ejections"],
                    counts["misjudged"],
                    *(
                        cast(Mapping[str, int], counts["reaches_misjudged"])[check]
                        for check in CHECKS
                    ),
                    counts["pit_net"],
                )
                for name, counts in ((n, class_counts[n]) for n in EJECTION_CLASSES)
            ],
        )
    )
    out.append("")
    out.append(
        "Ejections with a walkable pair under each leg of (a) (any pair, charged or not):"
    )
    out.append("")
    out.extend(
        _table(
            ("class", "ejections", *(_LEG_NAMES[leg] for leg in DISPUTE_LEGS)),
            [
                (
                    name.replace("_", " "),
                    counts["ejections"],
                    *(
                        cast(Mapping[str, int], counts["walkable_pair"])[leg]
                        for leg in DISPUTE_LEGS
                    ),
                )
                for name, counts in ((n, class_counts[n]) for n in EJECTION_CLASSES)
            ],
        )
    )
    moved = [
        case
        for case in cast(Sequence[Mapping[str, object]], classes["cases"])
        if len(set(cast(Mapping[str, bool], case["walkable_pair"]).values())) > 1
    ]
    if moved:
        out.append("")
        out.append(
            "Ejections on which the legs of (a) disagree, and the input that moves "
            "each between (a) as built and the transcript-only leg:"
        )
        out.append("")
        out.extend(
            _table(
                (
                    "seed",
                    "meeting",
                    "classes",
                    *(_LEG_NAMES[leg] for leg in DISPUTE_LEGS),
                    "moved by",
                ),
                [
                    (
                        case["seed"],
                        case["meeting"],
                        ", ".join(
                            name.replace("_", " ")
                            for name in cast(Sequence[str], case["classes"])
                        ),
                        *(
                            cast(Mapping[str, bool], case["walkable_pair"])[leg]
                            for leg in DISPUTE_LEGS
                        ),
                        case["moved_by"] or "not moved",
                    )
                    for case in moved
                ],
            )
        )
    out.append("")
    out.append("Unreached misjudged cases by reason:")
    out.append("")
    reasons = cast(Mapping[str, Mapping[str, int]], whole["unreached_reasons"])
    out.extend(
        _table(
            ("reason", *(_CHECK_NAMES[check] for check in CHECKS)),
            [
                (_REASON_NAMES[reason], *(reasons[check][reason] for check in CHECKS))
                for reason in REASONS
            ],
        )
    )
    out.append("")
    out.append(
        "The same cases' reconcilable charged pairs, each given its own first reason:"
    )
    out.append("")
    pair_reasons = cast(
        Mapping[str, Mapping[str, int]], whole["unreached_pair_reasons"]
    )
    out.extend(
        _table(
            ("reason", *(_CHECK_NAMES[check] for check in CHECKS)),
            [
                (
                    _REASON_NAMES[reason],
                    *(pair_reasons[check][reason] for check in CHECKS),
                )
                for reason in REASONS
            ],
        )
    )
    out.append("")
    insufficient = cast(Mapping[str, int], whole["insufficient_lines_misjudged"])
    out.append(
        "Lines saying the timing is insufficient, about a misjudged ejected player over "
        f"two rooms, shown to a voter who voted to eject: (b) {insufficient['b']}, "
        f"(b-snapshot) {insufficient['b_snapshot']}."
    )
    if "s9_agreement" in column:
        agreement = cast(Mapping[str, object], column["s9_agreement"])
        found = cast(Sequence[int], agreement["a"])
        probe = cast(Sequence[int], agreement["a_transcript_only"])
        out.append("")
        out.append(
            f"s9 agreement: (a) as built reads {found[0]} of {found[1]} ejections with a "
            "walkable pair, the figure the round-2 record's committed cells imply; the "
            f"transcript-only leg reads {probe[0]} of {probe[1]}"
            + (
                " and would pass."
                if agreement["a_transcript_only_agrees"]
                else " and would not."
            )
        )
    out.append("")
    return out


def _reading_section(
    payload: Mapping[str, object], columns: Sequence[Mapping[str, object]]
) -> list[str]:
    reading = cast(Mapping[str, object], payload["reading"])
    branches = cast(Mapping[str, Mapping[str, int]], reading["branches"])
    out = [
        "## Decision input",
        "",
        "The card's rule, applied to r2 and set beside s9 and r1: with M the misjudged "
        "cases, W those at witness meetings and R(X) the cases check X reaches, branch 1 "
        "when M is empty; branch 2 when (b-snapshot) reaches at least half of M, and of W "
        "when W is not empty; branch 3 when (c) does; branch 4 otherwise.",
        "",
    ]
    rows = []
    for column in columns:
        inputs = cast(Mapping[str, object], column["rule_inputs"])
        reaches = cast(Mapping[str, int], inputs["R"])
        at_witness = cast(Mapping[str, int], inputs["R_W"])
        branch = branches[cast(str, column["label"])]["branch"]
        rows.append(
            (
                column["label"],
                inputs["M"],
                inputs["W"],
                f"{reaches['b']} / {at_witness['b']}",
                f"{reaches['b_snapshot']} / {at_witness['b_snapshot']}",
                f"{reaches['c']} / {at_witness['c']}",
                f"{branch}: {_BRANCH_TEXT[branch]}",
            )
        )
    out.extend(
        _table(
            (
                "column",
                "M",
                "W",
                "R(b) / of W",
                "R(b-snapshot) / of W",
                "R(c) / of W",
                "branch",
            ),
            rows,
        )
    )
    out.extend(
        [
            "",
            "The branch is advisory and gates nothing. Branch 2 would need the owner to lift "
            "the exclusion of temporal observations, which changes every prompt and fails "
            "the validity gate's provenance check, and that field also carries death-evidence "
            "and account-uncertainty lines; its one live reading cast 14 eject and 136 skip "
            "ballots. A round 3 is the owner's spend decision.",
            "",
        ]
    )
    return out


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------


def run_columns(
    repo: Path, sources: Sequence[ColumnSource]
) -> tuple[dict[str, object], frozenset[str]]:
    """Read every column from its exact bytes; return the payload and the scan set."""

    labels = [source.label for source in sources]
    if len(set(labels)) != len(labels):
        raise RouteCheckReplayError(
            "a label was given twice: columns are read alone and never pooled"
        )
    order = list(COLUMN_LABELS)
    columns: list[dict[str, object]] = []
    forbidden: set[str] = set()
    for source in sorted(sources, key=lambda s: order.index(s.label)):
        config = declared_config(repo, source)
        with tempfile.TemporaryDirectory(prefix="route-check-replay-") as scratch:
            set_dir = materialize(repo, source, Path(scratch))
            require_declared_settings(set_dir, label=source.label, config=config)
            census = load_census_inputs(set_dir)
            records, travel_rows = read_set(set_dir, label=source.label, census=census)
            forbidden.update(forbidden_strings(set_dir))
            forbidden.update(travel_rows)
            roles = {game.seed: game.roles for game in census.games}
            columns.append(
                column_payload(source, config=config, records=records, roles=roles)
            )
    return build_payload(columns), frozenset(forbidden)


def outputs_for(repo: Path, sources: Sequence[ColumnSource]) -> tuple[str, str]:
    """The JSON and the report for ``sources``, scanned before anyone writes them."""

    payload, forbidden = run_columns(repo, sources)
    json_text = serialize(payload)
    report = render_report(payload)
    scan_outputs((json_text, report), forbidden)
    return json_text, report


def recorded_sources(payload: Mapping[str, object], repo: Path) -> list[ColumnSource]:
    """The columns a JSON records, each tree id checked against its sha's tree."""

    sources: list[ColumnSource] = []
    for column in cast(Sequence[Mapping[str, str]], payload["columns"]):
        source = ColumnSource(
            label=column["label"],
            commit=column["commit"],
            sha=column["sha"],
            path=column["path"],
            tree=column["tree"],
        )
        if source.label not in COLUMN_LABELS:
            raise RouteCheckReplayError(
                f"column {source.label!r} is not a known column"
            )
        actual = tree_at(repo, source.sha, source.path)
        if actual != source.tree:
            raise RouteCheckReplayError(
                f"column {source.label}: the recorded tree id {source.tree} is not the "
                f"tree of {source.sha}:{source.path} ({actual})"
            )
        sources.append(source)
    return sources


def check(repo: Path, json_path: Path, report_path: Path) -> list[str]:
    """Recompute both outputs from the recorded shas; return what differs."""

    committed_json = json_path.read_text(encoding="utf-8")
    sources = recorded_sources(json.loads(committed_json), repo)
    json_text, report = outputs_for(repo, sources)
    problems = []
    if json_text != committed_json:
        problems.append(f"{json_path}: the recomputed JSON differs")
    if report != report_path.read_text(encoding="utf-8"):
        problems.append(f"{report_path}: the recomputed report differs")
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="LABEL=COMMIT:PATH",
        help="one column: s9, r1 or r2, a commit, and a set path (repeatable)",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    parser.add_argument(
        "--check",
        action="store_true",
        help="recompute the JSON and report from the commits the JSON records",
    )
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--repo", type=Path, default=_REPO_ROOT)
    args = parser.parse_args(argv)
    started = time.monotonic()
    try:
        if args.check:
            if args.set:
                raise RouteCheckReplayError(
                    "--check takes its columns from the JSON, never from --set"
                )
            problems = check(args.repo, args.json, args.report)
            for problem in problems:
                print(problem, file=sys.stderr)
            if problems:
                return 1
            print(
                f"route-check replay: reproduced ({time.monotonic() - started:.1f} s)"
            )
            return 0
        if not args.set or args.out_json is None or args.out_report is None:
            raise RouteCheckReplayError(
                "a run needs at least one --set, --out-json and --out-report"
            )
        requests = [parse_column_request(text) for text in args.set]
        sources = [resolve_column(args.repo, request) for request in requests]
        json_text, report = outputs_for(args.repo, sources)
    except RouteCheckReplayError as error:
        print(f"route-check replay: {error}", file=sys.stderr)
        return 1
    args.out_json.write_text(json_text, encoding="utf-8")
    args.out_report.write_text(report, encoding="utf-8")
    print(
        f"route-check replay: wrote {args.out_json} and {args.out_report} "
        f"({time.monotonic() - started:.1f} s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
