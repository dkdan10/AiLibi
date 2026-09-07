"""Held-out proof-free physical prefixes: generated from a preregistered seed band.

The fresh-model deduction evaluation needs meeting-open inputs nobody has read.
`audits/deduction-candidate/preregistration.md` (section "Use the known seven
cases only for development/operational checks") requires a separate reviewer to
prepare and freeze those inputs, and treats an inspected schedule as development
data. This module is that preparation: a deterministic generator plus a
proof-free filter, whose output is committed as HASHES ONLY
(:data:`MANIFEST_PATH`). No prefix bytes are committed anywhere; the runner
regenerates the set from this module and the band and refuses to proceed if a
hash differs.

Three properties make the set reviewable without opening it:

* determinism -- every choice is drawn from a :class:`random.Random` seeded from
  the prefix seed alone, so the same seed yields the same prefix on the same
  source;
* legality -- each prefix is replayed through :class:`~orchestrator.game.HeadlessGame`
  with NO meeting runner, so the engine itself accepts (or rejects) every step
  and the run halts at ``MEETING_PHASE_REACHED`` without a single model call;
* proof-freedom -- a prefix is kept only when no LIVING CREWMATE's episodic
  memory holds an observed ``saw_player`` row carrying a ``kill`` or ``vent``
  action at meeting open. The killer's own record is deliberately NOT counted;
  the follow-up review's NG2-6 records that
  ``experiments/deduction_evaluation.validate_channels`` already excludes it, so
  the manifest states the exclusion rather than leaving it implied.

Unlike :class:`experiments.deduction_scenarios.ScenarioDefinition`, which pins
seed 1 and the 4p1i roster as ``Literal`` fields because it describes seven
hand-authored cases, :class:`HeldOutPrefix` carries seed and roster as plain
values: the whole point is that the set spans a band of seeds.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal, Self

from pydantic import BaseModel, ConfigDict, TypeAdapter, model_validator

from agents.base import AgentInterface
from agents.memory.beliefs import OBSERVED_KILL_ACTION, OBSERVED_VENT_ACTION
from agents.memory.store import AgentMemory
from agents.perception import (
    EVENT_OWN_KILL,
    EVENT_SAW_PLAYER,
    PROVENANCE_OBSERVED,
    ingest_packet,
)
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.events import (
    ActionRejectedEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    MovedEvent,
    SabotageRepairedEvent,
    SabotageRepairProgressedEvent,
    SabotageStartedEvent,
    VentEnteredEvent,
    VentExitedEvent,
    WaitedEvent,
)
from engine.world import Map, RoomId, WorldState, load_canonical_map
from experiments.deduction_scenarios import ScenarioCase, scenario_definition
from observation.action_intent import ActionIntent, WaitIntent
from observation.body_ids import public_body_id
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView

# ``_build_meeting_trigger`` is the ONE renderer of the meeting-trigger line the
# model reads (``orchestrator/game.py``); the body-handle assertion below has to
# run over that renderer's real output rather than a copy of its format string,
# or it would assert about this module instead of about the run. The prompt
# byte-golden walk imports it on the same grounds
# (``tests/meetings/test_prompt_byte_golden.py``).
from orchestrator.game import (  # noqa: PLC2701 -- renderer of record, see above
    HeadlessGame,
    TacticalAgent,
    UnrecordedGameResult,
    _build_meeting_trigger,
)
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.replay import substrate_flag_snapshot
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

_INTENT_ADAPTER: Final[TypeAdapter[ActionIntent]] = TypeAdapter(ActionIntent)

#: The temporal observation version the prefixes are generated and filtered
#: under. The authorization card binds both evaluation arms to temporal 2, so a
#: prefix screened under any other clock would not be the input the run uses.
TEMPORAL_OBSERVATION_VERSION: Final[Literal[2]] = 2

#: The provider the filter states rather than inherits. The replay halts at
#: ``MEETING_PHASE_REACHED`` and constructs no provider at all, so this is the
#: flag the manifest records, not a runtime dependency.
_FILTER_PROVIDER: Final[Literal["fake"]] = "fake"


def filter_environment() -> Mapping[str, str]:
    """The filter's environment, stated rather than inherited and built per use.

    A developer's shell must not be able to move which prefixes pass, so the two
    flags the filter screens under are written here instead of read from
    ``os.environ``. They are BUILT on each call from this module's pinned
    constants rather than stored in a module-level mapping: a stored mapping is
    state a same-process caller can reach, and prefix selection must not depend
    on any state a caller can reach. The returned mapping is a
    :class:`~types.MappingProxyType`, so a caller holding one cannot mutate it
    either -- and because the next call builds a fresh one, mutating a copy could
    not have moved the next replay's flags in any case.

    What this does NOT claim: a caller that rebinds a module attribute is
    rewriting this module, and no in-module mechanism prevents that. The freeze's
    guard against a rewritten module is the manifest, which records both this
    environment (``filter_environment``) and the module's own bytes
    (``source_sha256``); ``test_the_committed_manifest_regenerates_from_its_own_band``
    compares both against the committed record.
    """

    return MappingProxyType(
        {
            "AILIBI_LLM_PROVIDER": _FILTER_PROVIDER,
            "AILIBI_TEMPORAL_OBSERVATIONS": str(TEMPORAL_OBSERVATION_VERSION),
        }
    )


#: Every tick budget in the set. Wide enough for the longest schedule this
#: generator can draw (kill at tick 5, a six-hop walk to the body, report at
#: tick 12) and identical to the seven development cases' budget.
MAX_TICKS: Final[int] = 14

#: The frozen manifest, relative to the repository root.
MANIFEST_PATH: Final[str] = "audits/deduction-candidate/held-out/manifest.json"

#: The legacy body handle: ``body-p-<victim>-<death tick>``. Temporal v2 renders
#: ``observation.body_ids.public_body_id`` instead, which carries no death tick.
LEGACY_BODY_HANDLE_PATTERN: Final[re.Pattern[str]] = re.compile(r"body-p-\d+-\d+")

#: The source files whose bytes decide which prefixes this generator produces
#: and which the filter keeps. Recorded in the manifest so a source edit after
#: the freeze is visible rather than silent.
GENERATOR_SOURCES: Final[tuple[str, ...]] = (
    "agents/memory/beliefs.py",
    "agents/memory/store.py",
    "agents/perception.py",
    "agents/tactical/crewmate_policy.py",
    "agents/tactical/impostor_policy.py",
    "engine/actions.py",
    "engine/entities.py",
    "engine/maps/canonical_1.yaml",
    "engine/rules.py",
    "engine/tick.py",
    "engine/visibility.py",
    "engine/world.py",
    "experiments/held_out_prefixes.py",
    "observation/action_intent.py",
    "observation/body_ids.py",
    "observation/service.py",
    "observation/temporal.py",
    "orchestrator/action_ordering.py",
    "orchestrator/boundary.py",
    "orchestrator/game.py",
    "orchestrator/observation_delivery.py",
    "orchestrator/seeder.py",
)

#: The rooms a scripted kill may happen in: the six non-hallway rooms other than
#: the spawn/meeting room, which every player starts in and which no isolated
#: kill can be staged in on tick 4.
_KILL_ROOMS: Final[tuple[RoomId, ...]] = (
    "ADMIN",
    "ENGINEERING",
    "LABS",
    "MEDBAY",
    "REACTOR",
    "STORAGE",
)

#: Kill ticks the map's four-tick round-start cooldown allows (the earliest legal
#: kill is tick 4) and that still leave room for the longest walk to the body
#: within :data:`MAX_TICKS`.
_KILL_TICKS: Final[tuple[int, ...]] = (4, 5)

#: The last tick a report may open the meeting on, so every schedule fits
#: :data:`MAX_TICKS` with a tick to spare.
_LATEST_REPORT_TICK: Final[int] = 12

#: The generator's RNG domain. The seeder already consumes ``random.Random(seed)``
#: for role assignment and task dealing; drawing this module's choices from a
#: domain-separated stream keeps the schedule from correlating with which player
#: the seeder made the impostor, while staying a pure function of the seed.
_RNG_DOMAIN: Final[str] = "ailibi/held-out-prefix/v1"

RejectionReason = Literal[
    "engine_rejected_action",
    "meeting_did_not_open",
    "schedule_exceeds_tick_budget",
    "wrong_living_count",
    "unexpected_kill_shape",
    "witnessed_kill",
    "witnessed_vent",
    "legacy_body_handle",
]


class HeldOutPrefixError(RuntimeError):
    """Raised when the preregistered band cannot produce the requested set."""


class ScheduleTickBudgetError(HeldOutPrefixError):
    """Raised when one seed's drawn schedule does not fit its tick budget.

    A distinct class because the disposition differs: this is a property of the
    seed's own draw, so :func:`generate` and :func:`tally_reasons` record it as a
    ``schedule_exceeds_tick_budget`` skip and walk on. Every other
    :class:`HeldOutPrefixError` out of :func:`build_prefix` -- an unauthorized
    roster, a map with no route at all -- is invalid input to the generator
    rather than a seed the band may drop, and keeps raising.
    """


class SeedBand(BaseModel):
    """A preregistered, half-open seed range drawn in ascending order."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    first_seed: int
    last_seed: int
    size: int

    def seeds(self) -> tuple[int, ...]:
        if self.last_seed < self.first_seed:
            raise ValueError("a seed band must not run backwards")
        if self.size < 1:
            raise ValueError("a seed band must request at least one prefix")
        return tuple(range(self.first_seed, self.last_seed + 1))


class PrefixRoster(BaseModel):
    """The roster a prefix is built for; plain values, never ``Literal`` pins."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


class PrefixStep(BaseModel):
    """One scripted action. Every action NOT listed here is an explicit wait."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tick: int
    action: ActionIntent


class HeldOutPrefix(BaseModel):
    """A scripted physical prefix up to and including the report that opens the meeting.

    ``steps`` stops at the report: nothing past the meeting boundary belongs to a
    prefix, because everything past it is what the evaluation measures.

    :func:`canonical_prefix_json` and :func:`prefix_sha256` bind EVERY step, so a
    digest is only honest if the replay executes every step it binds. Two of the
    three ways a schedule can bind an action the replay would never run are
    refused here, before a prefix object exists:

    * a second step for a ``(tick, actor)`` pair already used -- a player submits
      exactly one action per tick, and :class:`_PrefixAgent` keys its script by
      tick, so a duplicate would be silently overwritten at replay;
    * a step outside the replayed window -- the loop halts at
      ``MEETING_PHASE_REACHED`` on ``report_tick`` and the scheduler stops at
      ``max_ticks``, so a step past either is hashed and never asked for.

    Every other way -- a step for a player the roster never seats, for one the
    replay stops asking because it is dead, or for the report tick, whose meeting
    interrupts the tick before the actions ordered after the reporter's are
    reached -- cannot be judged from the schedule alone, so :func:`_replay_prefix`
    closes them by requiring the ENGINE to have resolved an action for every
    hashed ``(tick, actor)`` pair.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: int = 1
    seed: int
    roster: PrefixRoster
    max_ticks: int
    steps: tuple[PrefixStep, ...]
    report_tick: int
    kill_tick: int

    @model_validator(mode="after")
    def _one_action_per_actor_and_tick(self) -> Self:
        seen: set[tuple[int, PlayerId]] = set()
        for step in self.steps:
            key = (step.tick, step.action.actor)
            if key in seen:
                raise ValueError(
                    "a prefix carries at most one action per actor per tick; "
                    f"duplicate step for {key[1]} at tick {key[0]}"
                )
            seen.add(key)
        return self

    @model_validator(mode="after")
    def _every_step_falls_inside_the_replayed_window(self) -> Self:
        if not 0 <= self.report_tick < self.max_ticks:
            raise ValueError(
                "a prefix's report tick must fall inside its tick budget; "
                f"report_tick {self.report_tick} against max_ticks {self.max_ticks}"
            )
        for step in self.steps:
            if not 0 <= step.tick <= self.report_tick:
                raise ValueError(
                    "a prefix step must fall inside the replayed window "
                    f"0-{self.report_tick}; step at tick {step.tick}"
                )
        return self


#: The band preregistered by ``tasks/work/held-out-prefix-freeze.md``. Seeds 3000
#: to 3999 drawn ascending; the first fifty that pass the filter are the set. The
#: preparer may not widen it: a band that cannot fill fifty is a stop, not a
#: bigger band.
PREREGISTERED_BAND: Final[SeedBand] = SeedBand(first_seed=3000, last_seed=3999, size=50)

#: The roster the authorization card binds: 4p1i with three living voters at
#: meeting open, one task per crewmate (the flat determinism reference).
AUTHORIZED_ROSTER: Final[PrefixRoster] = PrefixRoster(
    num_players=4, num_impostors=1, tasks_per_crewmate=1
)


@dataclass(frozen=True)
class SkippedSeed:
    """A band seed the filter refused, with the reason code it refused it for."""

    seed: int
    reason: RejectionReason


@dataclass(frozen=True)
class PrefixEvaluation:
    """One prefix's filter outcome. ``reason`` is ``None`` when it passed.

    The two counters make the filter's asymmetry inspectable without opening the
    prefix: ``living_crew_proof_rows`` is what disqualifies a prefix, and
    ``killer_own_kill_records`` is the record that deliberately does not. Both
    read zero when the run failed before the memories were scanned.
    """

    seed: int
    reason: RejectionReason | None
    trigger_line: str | None
    living_crew_proof_rows: int = 0
    killer_own_kill_records: int = 0


@dataclass(frozen=True)
class GeneratedSet:
    """The accepted prefixes in band order, their digests, and the skips."""

    band: SeedBand
    roster: PrefixRoster
    prefixes: tuple[HeldOutPrefix, ...]
    digests: tuple[str, ...]
    skipped: tuple[SkippedSeed, ...]


def canonical_prefix_json(prefix: HeldOutPrefix) -> str:
    """The one serialisation a prefix is hashed from."""

    return json.dumps(
        prefix.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )


def prefix_sha256(prefix: HeldOutPrefix) -> str:
    """The sha256 of :func:`canonical_prefix_json`, which the manifest records."""

    return hashlib.sha256(canonical_prefix_json(prefix).encode("utf-8")).hexdigest()


def legacy_body_handles(texts: Iterable[str]) -> tuple[str, ...]:
    """Every ``body-p-<victim>-<tick>`` handle in ``texts``, in encounter order."""

    return tuple(
        match.group(0)
        for text in texts
        for match in LEGACY_BODY_HANDLE_PATTERN.finditer(text)
    )


def assert_no_legacy_body_handles(texts: Iterable[str]) -> None:
    """Fail loud on a death-tick body handle reaching a listener-visible surface."""

    found = legacy_body_handles(texts)
    if found:
        raise HeldOutPrefixError(
            "temporal version 2 must render no death-tick body handle; found "
            + ", ".join(sorted(set(found)))
        )


def prefix_surface_texts(
    prefix: HeldOutPrefix, *, trigger_line: str | None
) -> tuple[str, ...]:
    """The texts the body-handle assertion runs over: the steps and the trigger."""

    texts = [canonical_prefix_json(prefix)]
    if trigger_line is not None:
        texts.append(trigger_line)
    return tuple(texts)


def source_digests(
    repo_root: Path, sources: Sequence[str] = GENERATOR_SOURCES
) -> dict[str, str]:
    """sha256 of each source file the generated set depends on."""

    digests: dict[str, str] = {}
    for name in sources:
        path = repo_root / name
        if not path.is_file():
            raise HeldOutPrefixError(f"generator source is missing: {name}")
        digests[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def development_definition_digests() -> dict[str, str]:
    """sha256 of each of the seven committed development definitions.

    Recorded so the manifest can assert them absent from the held-out digests:
    the development cases are seed 1 by construction and must never re-enter the
    set that confirms a candidate.
    """

    cases: tuple[ScenarioCase, ...] = (
        "honest",
        "impossible_account",
        "insufficient_evidence",
        "already_known_dead",
        "witnessed_kill",
        "witnessed_vent",
        "late_accusation",
    )
    return {
        case: hashlib.sha256(
            json.dumps(
                scenario_definition(case).model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        for case in cases
    }


# ---------------------------------------------------------------------------
# Map routing helpers
# ---------------------------------------------------------------------------


def _shortest_routes(
    game_map: Map, *, start: RoomId, goal: RoomId
) -> tuple[tuple[RoomId, ...], ...]:
    """Every shortest ``start -> goal`` route, in sorted order, excluding ``start``.

    Sorted so a caller that wants a stable route without spending an RNG draw can
    take the first, and a caller that wants variety can index into it.
    """

    if start == goal:
        return ((),)
    routes: list[tuple[RoomId, ...]] = []
    frontier: list[tuple[RoomId, ...]] = [(start,)]
    seen_depth: dict[RoomId, int] = {start: 0}
    while frontier and not routes:
        next_frontier: list[tuple[RoomId, ...]] = []
        for path in frontier:
            for neighbor in game_map.room_neighbors(path[-1]):
                if neighbor in path:
                    continue
                depth = len(path)
                if seen_depth.get(neighbor, depth) < depth:
                    continue
                seen_depth[neighbor] = depth
                extended = (*path, neighbor)
                if neighbor == goal:
                    routes.append(extended[1:])
                else:
                    next_frontier.append(extended)
        frontier = next_frontier
    return tuple(sorted(routes))


def _move(actor: PlayerId, room: RoomId) -> ActionIntent:
    return _INTENT_ADAPTER.validate_python(
        {"actor": actor, "type": "move", "payload": {"to_room": room}}
    )


# ---------------------------------------------------------------------------
# Schedule construction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Walk:
    """One player's tick-indexed rooms plus the moves that produced them."""

    rooms: tuple[RoomId, ...]
    steps: tuple[tuple[int, RoomId], ...]


def _routed_walk(
    *,
    rng: random.Random,
    game_map: Map,
    start: RoomId,
    goal: RoomId,
    first_tick: int,
    latest_arrival: int,
) -> tuple[tuple[int, RoomId], ...]:
    """Move ``start -> goal`` along a randomly chosen shortest route, after a delay."""

    routes = _shortest_routes(game_map, start=start, goal=goal)
    if not routes:
        raise HeldOutPrefixError(f"no legal route from {start} to {goal}")
    route = routes[rng.randrange(len(routes))]
    slack = latest_arrival - (first_tick + len(route) - 1)
    if slack < 0:
        raise ScheduleTickBudgetError(
            f"route {start}->{goal} does not fit the tick budget"
        )
    delay = rng.randint(0, slack)
    return tuple(
        (first_tick + delay + offset, room) for offset, room in enumerate(route)
    )


def _random_walk(
    *,
    rng: random.Random,
    game_map: Map,
    start: RoomId,
    first_tick: int,
    last_tick: int,
) -> _Walk:
    """A legal per-tick wander: each tick the player stays put or takes one door."""

    room = start
    rooms: list[RoomId] = []
    steps: list[tuple[int, RoomId]] = []
    for tick in range(first_tick, last_tick + 1):
        choices: tuple[RoomId | None, ...] = (None, *game_map.room_neighbors(room))
        choice = choices[rng.randrange(len(choices))]
        if choice is not None:
            steps.append((tick, choice))
            room = choice
        rooms.append(room)
    return _Walk(rooms=tuple(rooms), steps=tuple(steps))


def build_prefix(
    *, seed: int, roster: PrefixRoster, game_map: Map, max_ticks: int = MAX_TICKS
) -> HeldOutPrefix:
    """Build one seed's legal kill-then-report schedule. Deterministic in ``seed``.

    The shape is fixed -- one kill before the meeting, a crewmate body report as
    the trigger -- while the roles, the kill room, the kill tick, the routes and
    the two uninvolved crewmates' wandering are all drawn from the seed. The
    wandering is what makes the proof-free filter load-bearing rather than
    decorative: a bystander is free to walk into the kill room on the kill tick,
    and the filter is what removes that seed from the set.
    """

    if roster.num_players < 4 or roster.num_impostors != 1:
        raise HeldOutPrefixError(
            "the authorized held-out roster is one impostor among at least four players"
        )
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=roster.num_players,
        num_impostors=roster.num_impostors,
        tasks_per_crewmate=roster.tasks_per_crewmate,
    )
    impostor = next(
        pid for pid in sorted(state.players) if state.players[pid].role == "IMPOSTOR"
    )
    crewmates = [pid for pid in sorted(state.players) if pid != impostor]
    spawn = game_map.spawn.room

    rng = random.Random(f"{_RNG_DOMAIN}/{seed}")
    victim = crewmates[rng.randrange(len(crewmates))]
    remaining = [pid for pid in crewmates if pid != victim]
    reporter = remaining[rng.randrange(len(remaining))]
    bystanders = [pid for pid in remaining if pid != reporter]
    kill_room = _KILL_ROOMS[rng.randrange(len(_KILL_ROOMS))]
    kill_tick = _KILL_TICKS[rng.randrange(len(_KILL_TICKS))]

    steps: list[tuple[int, ActionIntent]] = []

    # The impostor and the victim settle in the kill room a tick BEFORE the kill,
    # so no same-tick arrival can reorder into or out of the witness set.
    for actor in (impostor, victim):
        for tick, room in _routed_walk(
            rng=rng,
            game_map=game_map,
            start=spawn,
            goal=kill_room,
            first_tick=0,
            latest_arrival=kill_tick - 1,
        ):
            steps.append((tick, _move(actor, room)))
    steps.append(
        (
            kill_tick,
            _INTENT_ADAPTER.validate_python(
                {"actor": impostor, "type": "kill", "payload": {"target": victim}}
            ),
        )
    )

    # The reporter wanders until the kill tick, then walks to the body and calls
    # it in. Its wandering may leave it standing in the kill room when the kill
    # lands, which the filter rejects.
    reporter_walk = _random_walk(
        rng=rng, game_map=game_map, start=spawn, first_tick=0, last_tick=kill_tick
    )
    staged_room = reporter_walk.rooms[-1]
    approach = _shortest_routes(game_map, start=staged_room, goal=kill_room)[0]
    report_tick = kill_tick + len(approach) + 1
    if report_tick > _LATEST_REPORT_TICK or report_tick >= max_ticks:
        raise ScheduleTickBudgetError(
            f"seed {seed} staged the reporter beyond the tick budget"
        )
    for tick, room in reporter_walk.steps:
        steps.append((tick, _move(reporter, room)))
    for offset, room in enumerate(approach):
        steps.append((kill_tick + 1 + offset, _move(reporter, room)))
    steps.append(
        (
            report_tick,
            _INTENT_ADAPTER.validate_python(
                {
                    "actor": reporter,
                    "type": "report",
                    "payload": {"body_id": public_body_id(victim)},
                }
            ),
        )
    )

    # The killer leaves the scene on the tick after the kill, then wanders.
    departures = game_map.room_neighbors(kill_room)
    first_departure = departures[rng.randrange(len(departures))]
    steps.append((kill_tick + 1, _move(impostor, first_departure)))
    for tick, room in _random_walk(
        rng=rng,
        game_map=game_map,
        start=first_departure,
        first_tick=kill_tick + 2,
        last_tick=report_tick,
    ).steps:
        steps.append((tick, _move(impostor, room)))

    # The uninvolved crewmates wander for the whole prefix, unconstrained.
    for bystander in bystanders:
        for tick, room in _random_walk(
            rng=rng,
            game_map=game_map,
            start=spawn,
            first_tick=0,
            last_tick=report_tick,
        ).steps:
            steps.append((tick, _move(bystander, room)))

    # Nobody but the reporter acts on the report tick. The meeting interrupts
    # that tick: ``advance_tick`` returns the instant the report puts the world
    # in ``MEETING``, so every action ordered after the reporter's is discarded
    # without even a rejection, and a move drawn for that tick would be hashed
    # into a digest the engine never executed. The walks above are drawn exactly
    # as before -- the draws are untouched and only the drawn step is discarded --
    # so a seed's world up to the report is the same world it always was.
    ordered = tuple(
        PrefixStep(tick=tick, action=action)
        for tick, action in sorted(steps, key=lambda row: (row[0], row[1].actor))
        if tick != report_tick or action.actor == reporter
    )
    return HeldOutPrefix(
        seed=seed,
        roster=roster,
        max_ticks=max_ticks,
        steps=ordered,
        report_tick=report_tick,
        kill_tick=kill_tick,
    )


# ---------------------------------------------------------------------------
# The proof-free filter
# ---------------------------------------------------------------------------


class _PrefixAgent(TacticalAgent):
    """A scripted agent: the prefix's action for this tick, else an explicit wait."""

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        role: Role,
        prefix: HeldOutPrefix,
        memory: AgentMemory,
    ) -> None:
        policy = (
            ImpostorPolicy(agent_id=agent_id)
            if role == "IMPOSTOR"
            else CrewmatePolicy(agent_id=agent_id)
        )
        super().__init__(agent_id=agent_id, policy=policy, role=role, memory=memory)
        # Keying by tick alone loses nothing: ``HeldOutPrefix`` rejects a second
        # step for the same ``(tick, actor)``, so no hashed action is overwritten
        # here. That is all the model can guarantee. Whether the loop ever ASKS
        # for a scripted tick depends on the run, and whether the ENGINE resolves
        # what this agent hands back depends on the tick, so neither is counted
        # here: ``_replay_prefix`` reads that off the engine's own events.
        self._scripted: dict[int, ActionIntent] = {
            step.tick: step.action
            for step in prefix.steps
            if step.action.actor == agent_id
        }

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        # Keep the real typed perception seam without letting a tactical decision
        # mutate policy state ahead of the predetermined legal action.
        del public_map
        ingest_packet(
            packet=packet, memory=self.memory.episodic, beliefs=self.memory.beliefs
        )
        scripted = self._scripted.get(packet.tick)
        if scripted is None:
            return WaitIntent(type="wait", actor=self.agent_id)
        return scripted


@dataclass(frozen=True)
class _ProofScan:
    """What the living crew can prove outright, and what the killer privately knows."""

    reason: RejectionReason | None
    living_crew_proof_rows: int
    killer_own_kill_records: int


def _scan_for_proof(
    *, agents: Mapping[PlayerId, _PrefixAgent], state: WorldState
) -> _ProofScan:
    """Reject a prefix any LIVING CREWMATE could win the meeting with outright.

    The killer's own kill record is not counted: it is the impostor's private
    knowledge of its own act, never crew evidence, and
    ``experiments.deduction_evaluation.validate_channels`` already excludes it
    (follow-up review NG2-6). Only the living crew's observed ``saw_player``
    rows carrying a ``kill`` or ``vent`` action can disqualify a prefix; the
    killer's rows are counted separately so the exclusion is visible rather than
    inferred from an absence.
    """

    reason: RejectionReason | None = None
    crew_rows = 0
    own_kills = 0
    for player_id in sorted(agents):
        player = state.players[player_id]
        if not player.alive:
            continue
        for event in agents[player_id].memory.episodic.recent(since_tick=0):
            if player.role != "CREWMATE":
                if event.type == EVENT_OWN_KILL:
                    own_kills += 1
                continue
            if event.provenance != PROVENANCE_OBSERVED:
                continue
            if event.type != EVENT_SAW_PLAYER:
                continue
            action = event.payload.get("action")
            if action in (OBSERVED_KILL_ACTION, OBSERVED_VENT_ACTION):
                crew_rows += 1
                if reason is None:
                    reason = (
                        "witnessed_kill"
                        if action == OBSERVED_KILL_ACTION
                        else "witnessed_vent"
                    )
    return _ProofScan(
        reason=reason,
        living_crew_proof_rows=crew_rows,
        killer_own_kill_records=own_kills,
    )


@dataclass(frozen=True)
class _Replay:
    """One prefix replayed to meeting open, with the agents whose memories it filled."""

    result: UnrecordedGameResult
    agents: Mapping[PlayerId, _PrefixAgent]


def _resolved_action_pairs(
    result: UnrecordedGameResult,
) -> set[tuple[int, PlayerId]]:
    """Every ``(tick, actor)`` the ENGINE resolved an action for during the run.

    One event per resolved action is the tick function's own contract
    (``engine/tick.py``, step 1): ``_apply_action`` returns the event for an
    action it executes and the loop appends an ``ActionRejected`` for one it
    refuses, so the union of those events is the record of what the engine
    answered for. ``TaskProgressed`` and ``TaskCompleted`` are deliberately
    absent: ``advance_tick`` also emits them from its PASSIVE task step, for
    actors that submitted nothing, so their presence would not prove an action
    was resolved. A schedule that ever scripts a task action must therefore bring
    its own proof rather than borrow theirs -- it would be refused here, which is
    the safe direction.
    """

    pairs: set[tuple[int, PlayerId]] = set()
    for step in result.tick_steps:
        for event in step.events:
            if isinstance(
                event,
                (
                    ActionRejectedEvent,
                    KilledEvent,
                    MeetingTriggeredEvent,
                    MovedEvent,
                    SabotageRepairedEvent,
                    SabotageRepairProgressedEvent,
                    SabotageStartedEvent,
                    VentEnteredEvent,
                    VentExitedEvent,
                    WaitedEvent,
                ),
            ):
                pairs.add((event.tick, event.actor))
    return pairs


def _replay_prefix(
    prefix: HeldOutPrefix,
    *,
    game_map: Map | None = None,
    public_map: PublicMapView | None = None,
) -> _Replay:
    """Drive ``prefix`` through the engine with no meeting runner and no recording.

    ``meeting_runner=None`` halts the loop at ``MEETING_PHASE_REACHED`` -- the
    agents have already received the meeting tick's event observations by then --
    and ``replay_path=None`` routes the observation audit to the null device, so
    the whole filter writes nothing to disk and makes no provider call of any
    kind, live or fake.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    resolved_public_map = (
        public_map
        if public_map is not None
        else public_map_from_engine_map(resolved_map)
    )
    agents: dict[PlayerId, _PrefixAgent] = {}

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        agent = _PrefixAgent(
            agent_id=agent_id,
            role=role,
            prefix=prefix,
            memory=AgentMemory(public_map=resolved_public_map),
        )
        agents[agent_id] = agent
        return agent

    result = HeadlessGame(
        seed=prefix.seed,
        num_players=prefix.roster.num_players,
        num_impostors=prefix.roster.num_impostors,
        tasks_per_crewmate=prefix.roster.tasks_per_crewmate,
        game_map=resolved_map,
        agent_factory=factory,
        replay_path=None,
        scheduler=TickScheduler(max_ticks=prefix.max_ticks),
        meeting_runner=None,
        substrate_flags=substrate_flag_snapshot(filter_environment()),
        temporal_observation_version=TEMPORAL_OBSERVATION_VERSION,
    ).run_unrecorded()
    # The certifying seam. ``prefix_sha256`` binds every step, so a digest may
    # only be computed for a schedule the ENGINE resolved step for step. What the
    # agent HANDED the loop is not that measure: ``decide`` returning an action
    # says only that the agent was asked, and the loop can still drop what it
    # gets back -- ``advance_tick`` returns the instant a report puts the world in
    # ``MEETING``, so every action ordered after the reporter's on the report tick
    # is discarded without even a rejection. So the comparison runs against the
    # engine's own events instead. The model already refuses a duplicate
    # ``(tick, actor)`` and a step outside ``0..report_tick``; what it cannot see
    # from the schedule alone is a step addressed to a player this roster never
    # seats -- no agent exists for that id, so the step reaches nothing -- one
    # addressed to a player the loop stopped asking because it was dead, and one
    # the meeting tick discarded. None of the three leaves an event behind, and
    # all three are invalid input rather than a rejection reason: a
    # ``PrefixEvaluation`` for a schedule the run only partly executed would be a
    # verdict about a run that never happened. Counts only, never steps: this
    # message is allowed to name how many pairs went unresolved, never which.
    resolved = _resolved_action_pairs(result)
    unresolved = sum(
        1 for step in prefix.steps if (step.tick, step.action.actor) not in resolved
    )
    if unresolved:
        raise HeldOutPrefixError(
            f"the engine resolved no action for {unresolved} of the prefix's "
            f"{len(prefix.steps)} hashed steps; a digest may only certify a "
            "schedule the engine executed step for step"
        )
    return _Replay(result=result, agents=agents)


def evaluate_prefix(
    prefix: HeldOutPrefix,
    *,
    game_map: Map | None = None,
    public_map: PublicMapView | None = None,
) -> PrefixEvaluation:
    """Replay ``prefix`` and decide whether the held-out set may keep it."""

    replay = _replay_prefix(prefix, game_map=game_map, public_map=public_map)
    result, agents = replay.result, replay.agents

    events = [event for step in result.tick_steps for event in step.events]
    kills = [event for event in events if isinstance(event, KilledEvent)]
    # A player killed part-way through a tick still submitted an action for that
    # tick -- the loop demands one from every player alive when the tick opened --
    # and the engine rejects it as "player is dead" whenever the killer's id
    # sorts ahead of the victim's in the tick's action order. That is the engine
    # resolving a death, not a defect in the schedule, so the victim's own action
    # on its own death tick is the one rejection this filter does not count.
    death_actions = {(event.tick, event.target) for event in kills}
    if any(
        isinstance(event, ActionRejectedEvent)
        and (event.tick, event.actor) not in death_actions
        for event in events
    ):
        return PrefixEvaluation(
            seed=prefix.seed, reason="engine_rejected_action", trigger_line=None
        )
    triggers = [event for event in events if isinstance(event, MeetingTriggeredEvent)]
    if (
        result.outcome != "MEETING_PHASE_REACHED"
        or result.final_state.phase != "MEETING"
        or len(triggers) != 1
        or triggers[0].trigger != "report"
        or triggers[0].tick != prefix.report_tick
    ):
        return PrefixEvaluation(
            seed=prefix.seed, reason="meeting_did_not_open", trigger_line=None
        )
    living = [pid for pid, player in result.final_state.players.items() if player.alive]
    if len(living) != prefix.roster.num_players - 1:
        return PrefixEvaluation(
            seed=prefix.seed, reason="wrong_living_count", trigger_line=None
        )
    if (
        len(kills) != 1
        or kills[0].tick != prefix.kill_tick
        or result.final_state.players[kills[0].actor].role != "IMPOSTOR"
        or triggers[0].actor == kills[0].actor
    ):
        return PrefixEvaluation(
            seed=prefix.seed, reason="unexpected_kill_shape", trigger_line=None
        )

    scan = _scan_for_proof(agents=agents, state=result.final_state)
    if scan.reason is not None:
        return PrefixEvaluation(
            seed=prefix.seed,
            reason=scan.reason,
            trigger_line=None,
            living_crew_proof_rows=scan.living_crew_proof_rows,
            killer_own_kill_records=scan.killer_own_kill_records,
        )

    trigger, _, _ = _build_meeting_trigger(
        state=result.final_state,
        events=result.tick_steps[-1].events,
        temporal_observations=True,
    )
    reason: RejectionReason | None = (
        "legacy_body_handle"
        if legacy_body_handles(
            prefix_surface_texts(prefix, trigger_line=trigger.description)
        )
        else None
    )
    return PrefixEvaluation(
        seed=prefix.seed,
        reason=reason,
        trigger_line=trigger.description,
        living_crew_proof_rows=scan.living_crew_proof_rows,
        killer_own_kill_records=scan.killer_own_kill_records,
    )


def generate(
    band: SeedBand = PREREGISTERED_BAND, roster: PrefixRoster = AUTHORIZED_ROSTER
) -> GeneratedSet:
    """Draw ``band`` ascending and keep the first ``band.size`` prefixes that pass.

    Stops -- it does not widen the band -- when the band runs out before the set
    is full. Every skipped seed is recorded with its reason code, including the
    seed whose own draw does not fit the tick budget: a schedule that cannot be
    built is a seed the band drops, exactly like one the filter refuses, and
    aborting the whole draw on it would make one unlucky seed a stop.
    """

    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    prefixes: list[HeldOutPrefix] = []
    digests: list[str] = []
    skipped: list[SkippedSeed] = []
    for seed in band.seeds():
        if len(prefixes) == band.size:
            break
        try:
            prefix = build_prefix(seed=seed, roster=roster, game_map=game_map)
        except ScheduleTickBudgetError:
            skipped.append(
                SkippedSeed(seed=seed, reason="schedule_exceeds_tick_budget")
            )
            continue
        evaluation = evaluate_prefix(prefix, game_map=game_map, public_map=public_map)
        if evaluation.reason is not None:
            skipped.append(SkippedSeed(seed=seed, reason=evaluation.reason))
            continue
        prefixes.append(prefix)
        digests.append(prefix_sha256(prefix))
    if len(prefixes) != band.size:
        raise HeldOutPrefixError(
            f"the preregistered band {band.first_seed}-{band.last_seed} yielded "
            f"{len(prefixes)} prefixes, not {band.size}; this is a stop, not a "
            "reason to widen the band"
        )
    return GeneratedSet(
        band=band,
        roster=roster,
        prefixes=tuple(prefixes),
        digests=tuple(digests),
        skipped=tuple(skipped),
    )


@dataclass(frozen=True)
class ReasonTally:
    """How :func:`tally_reasons` dispositioned a seed range. Aggregates only.

    The totals are FIELDS, not entries beside the histogram. A single flat dict
    would let a future reason code named ``seeds`` or ``accepted`` overwrite a
    total silently and make the tally under-report itself; the reason codes live
    in ``reasons`` where no name of theirs can collide with a total.
    """

    seeds: int
    accepted: int
    reasons: Mapping[RejectionReason, int]


def tally_reasons(
    first_seed: int,
    last_seed: int,
    roster: PrefixRoster = AUTHORIZED_ROSTER,
) -> ReasonTally:
    """Count how the filter dispositions an OUT-OF-BAND seed range. Aggregates only.

    This is the reproducing command behind the card's out-of-band rejection rate:
    it evaluates every seed in ``[first_seed, last_seed]`` exactly as
    :func:`generate` would and returns the number of seeds walked, the number
    accepted, and the histogram of rejection reason codes. It never returns,
    prints or otherwise exposes a prefix, a step, a room, a route or a digest.

    It REFUSES any range that touches :data:`PREREGISTERED_BAND`. A count is
    aggregate, but a per-range count over band seeds is still a probe of the
    held-out set -- narrow the range and it becomes a per-seed read -- so the
    band is out of reach of this function rather than merely discouraged.

    A seed whose own draw does not fit the tick budget is counted as a
    ``schedule_exceeds_tick_budget`` skip, exactly as :func:`generate` records
    it, so the tally stays a count of what the generator would do rather than a
    different disposition of the same seed. Every other build failure still
    raises: an unauthorized roster is invalid input to both, not a seed either
    of them drops.
    """

    if last_seed < first_seed:
        raise HeldOutPrefixError("a tally range must not run backwards")
    if (
        first_seed <= PREREGISTERED_BAND.last_seed
        and PREREGISTERED_BAND.first_seed <= last_seed
    ):
        raise HeldOutPrefixError(
            f"seeds {first_seed}-{last_seed} intersect the preregistered band "
            f"{PREREGISTERED_BAND.first_seed}-{PREREGISTERED_BAND.last_seed}; "
            "the held-out set is not tallied, only regenerated and hashed"
        )
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    reasons: Counter[RejectionReason] = Counter()
    accepted = 0
    for seed in range(first_seed, last_seed + 1):
        try:
            prefix = build_prefix(seed=seed, roster=roster, game_map=game_map)
        except ScheduleTickBudgetError:
            reasons["schedule_exceeds_tick_budget"] += 1
            continue
        evaluation = evaluate_prefix(prefix, game_map=game_map, public_map=public_map)
        if evaluation.reason is None:
            accepted += 1
        else:
            reasons[evaluation.reason] += 1
    return ReasonTally(
        seeds=last_seed - first_seed + 1,
        accepted=accepted,
        reasons={reason: reasons[reason] for reason in sorted(reasons)},
    )


# ---------------------------------------------------------------------------
# The freeze manifest
# ---------------------------------------------------------------------------

_STATUS_NOTE: Final[str] = (
    "held_out until a held-out result informs a fix. That flip is recorded HERE, "
    'by setting status to "development" and stating the record that converted '
    "the set -- never by deleting this file. Confirming a generalization claim "
    "after such a flip needs a new band frozen under a new card."
)

_FILTER_NOTE: Final[str] = (
    "A prefix is kept only when no LIVING CREWMATE's episodic memory holds an "
    "observed saw_player row carrying a kill or vent action at meeting open. The "
    "impostor's own kill record is NOT counted: it is the killer's private "
    "knowledge, never crew evidence, and experiments/deduction_evaluation.py's "
    "validate_channels already excludes it (follow-up review NG2-6). The filter "
    "replays each prefix through HeadlessGame with no meeting runner, so it halts "
    "at MEETING_PHASE_REACHED and makes no provider call."
)

_PREFIX_BYTES_NOTE: Final[str] = (
    "No prefix bytes are committed. The runner regenerates the set from "
    "experiments/held_out_prefixes.py and the band below and refuses to proceed "
    "if any digest differs from accepted[].sha256."
)


def build_manifest(
    generated: GeneratedSet, *, repo_root: Path, card: str
) -> dict[str, object]:
    """Assemble the freeze record: band, roster, hashes and skips -- never prefixes."""

    development = development_definition_digests()
    collisions = sorted(set(development.values()) & set(generated.digests))
    if collisions:
        raise HeldOutPrefixError(
            "a development definition digest appears in the held-out set: "
            + ", ".join(collisions)
        )
    reasons = Counter(skip.reason for skip in generated.skipped)
    return {
        "version": 1,
        "status": "held_out",
        "status_note": _STATUS_NOTE,
        "card": card,
        "prefix_bytes": _PREFIX_BYTES_NOTE,
        "band": {
            "first_seed": generated.band.first_seed,
            "last_seed": generated.band.last_seed,
            "size": generated.band.size,
            "draw_order": "ascending",
        },
        "roster": generated.roster.model_dump(mode="json"),
        "max_ticks": MAX_TICKS,
        "temporal_observation_version": TEMPORAL_OBSERVATION_VERSION,
        "filter": _FILTER_NOTE,
        "filter_environment": dict(filter_environment()),
        "canonical_json": (
            "json.dumps(prefix.model_dump(mode='json'), sort_keys=True, "
            "separators=(',', ':')) encoded as UTF-8, hashed with sha256"
        ),
        "source_sha256": source_digests(repo_root),
        "accepted": [
            {"seed": prefix.seed, "sha256": digest}
            for prefix, digest in zip(generated.prefixes, generated.digests)
        ],
        "last_accepted_seed": generated.prefixes[-1].seed,
        "skipped": [
            {"seed": skip.seed, "reason": skip.reason} for skip in generated.skipped
        ],
        "skipped_reason_counts": {
            reason: reasons[reason] for reason in sorted(reasons)
        },
        "development_definitions": {
            "sha256": development,
            "absent_from_accepted": True,
            "note": (
                "The seven hand-authored development cases in "
                "experiments/deduction_scenarios.py are seed 1 by construction, "
                "so the band excludes them; their digests are recorded here and "
                "asserted absent from accepted[].sha256."
            ),
        },
        "body_handle_assertion": {
            "pattern": LEGACY_BODY_HANDLE_PATTERN.pattern,
            "note": (
                "Under temporal version 2 neither the rendered meeting trigger "
                "line nor any prefix step text matches this pattern; the death "
                "tick stays out of the listener-visible handle."
            ),
        },
    }


def write_manifest(repo_root: Path, *, card: str) -> Path:
    """Regenerate the set and rewrite :data:`MANIFEST_PATH`. Used by ``__main__``."""

    manifest = build_manifest(generate(), repo_root=repo_root, card=card)
    path = repo_root / MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", "utf-8")
    return path


__all__ = [
    "AUTHORIZED_ROSTER",
    "GENERATOR_SOURCES",
    "GeneratedSet",
    "HeldOutPrefix",
    "HeldOutPrefixError",
    "LEGACY_BODY_HANDLE_PATTERN",
    "MANIFEST_PATH",
    "MAX_TICKS",
    "PREREGISTERED_BAND",
    "PrefixEvaluation",
    "PrefixRoster",
    "PrefixStep",
    "ReasonTally",
    "RejectionReason",
    "ScheduleTickBudgetError",
    "SeedBand",
    "SkippedSeed",
    "TEMPORAL_OBSERVATION_VERSION",
    "assert_no_legacy_body_handles",
    "build_manifest",
    "build_prefix",
    "canonical_prefix_json",
    "development_definition_digests",
    "evaluate_prefix",
    "filter_environment",
    "generate",
    "legacy_body_handles",
    "prefix_sha256",
    "prefix_surface_texts",
    "source_digests",
    "tally_reasons",
    "write_manifest",
]


_USAGE: Final[str] = (
    "usage: python -m experiments.held_out_prefixes [--tally FIRST LAST]"
)


if __name__ == "__main__":  # pragma: no cover - the freeze and tally commands
    _argv = sys.argv[1:]
    if not _argv:
        written = write_manifest(
            Path(__file__).resolve().parents[1],
            card="tasks/work/held-out-prefix-freeze.md",
        )
        print(f"wrote {written}")
    elif _argv[0] == "--tally" and len(_argv) == 3:
        _tally = tally_reasons(int(_argv[1]), int(_argv[2]))
        print(f"seeds {_tally.seeds}")
        print(f"accepted {_tally.accepted}")
        for _reason, _count in _tally.reasons.items():
            print(f"{_reason} {_count}")
    else:
        raise SystemExit(_USAGE)
