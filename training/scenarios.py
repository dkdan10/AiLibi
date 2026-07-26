"""Scenario staging: the skill-scenario library + per-scenario dense fitness (18.23).

The training-grounds instrument (audits/audit-phase-18-planning.md §4 #12):
constructed MID-GAME skill situations injected into the headless game through the
``HeadlessGame(initial_state=...)`` seam and run on the no-replay live-assembly
path (:meth:`training.env.TacticalRolloutEnv.rollout_injected`), so per-skill
pressure exists without full games. Four load-bearing disciplines:

* **Determinism is inherited, never re-invented.** Every staged state stamps
  ``rng_state`` with the canonical ``EngineRng.from_seed(seed).snapshot()`` and
  ``seed`` with the same seed, so ``advance_tick`` purity makes an injected
  episode a pure function of ``(scenario, seed, policies)`` — the same
  scenario + seed produces an identical state-hash chain twice.
* **Dense fitness from tactical facts only.** Scenario episodes are truncated by
  construction (a staged tick plus a short horizon), so they score through the
  dense channel — the typed event log, per-step frame scalars, meeting records,
  and :func:`training.rewards.side_specific_terms` (consumed as-is) — NEVER
  ``compute_shaped_reward``'s terminal gate, and never the ``winner`` literal:
  an episode that happens to reach ``GAME_OVER`` inside its horizon scores
  through the identical dense definition. Watchability quantities never appear
  in scenario fitness, and the standing gates/referee never move.
* **Every fitness names what it deliberately does NOT reward.** The
  Goodhart-adjacent part (the FO-2 lesson — the ml-spike co-evolution probe
  collapsed into meeting-starvation equilibria): each
  :class:`ScenarioSpec` carries ``rewards`` AND ``does_not_reward``, and the
  non-reward clause is part of the definition, not commentary — e.g.
  body-discovery-latency scores 0.0 (its floor) when no crew-routed report
  meeting ever happens, so suppressing meetings can never pay.
* **The provider owns its own game budget and states it.** Scenario episodes
  sit OUTSIDE the driver's ``projected_game_bound`` ceiling guard;
  :meth:`ScenarioProvider.games_per_evaluation` is the stated per-ES-evaluation
  episode cost.

The scenario roster ids follow the ``orchestrator.seeder`` role-neutral ``p-N``
convention, but the CAST IS FIXED per scenario (no seed-shuffled roles): a
scenario is a staged situation, and the seed varies only the rng snapshot the
determinism story rides. The library is written against the canonical map's
rooms/tasks/vents; a foreign map fails loud in the builders.

The campaign consumes scenarios ONLY through 18.21's additive scenario-provider
seam: :class:`ScenarioProvider` conforms to
:data:`training.coevo.driver.CoevoScenarioProvider` (called once per swap with
``(swap_index, moving_side)``) and returns one named
:class:`~training.coevo.driver.CoevoScenarioTerm` per scenario of the moving
side — each term's fitness a pure deterministic function of the flat genome
(the ES purity contract; the provider closes over the side's selector builder
and runs its own episodes).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final, TypeAlias, get_args

from engine.entities import (
    BodyState,
    PlayerId,
    PlayerState,
    Role,
    TaskInstanceId,
    TaskState,
)
from engine.events import (
    KilledEvent,
    MeetingTriggeredEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.rng import EngineRng, RngStateHashPolicy
from engine.world import Map, WorldState, load_canonical_map
from orchestrator.game import MeetingRunner
from training.coevo.driver import CoevoScenarioTerm
from training.coevo.hall_of_fame import Side
from training.env import IntentSelector, TacticalRolloutEnv
from training.rewards import side_specific_terms
from training.rollout import EpisodeRollout

#: A per-scenario dense fitness over one injected episode: tactical facts only
#: (events, frame scalars, meeting records, roles) — never the terminal gate.
ScenarioFitness: TypeAlias = Callable[[EpisodeRollout], float]

#: A raw staged-state constructor ``(game_map, seed) -> WorldState``; the
#: validated public entry is :func:`build_scenario_state`.
ScenarioStateBuilder: TypeAlias = Callable[[Map, int], WorldState]

#: Turns one flat genome into the side-scoped :data:`IntentSelector` that
#: drives its scenario episodes (the provider closes over this — the selector
#: itself is responsible for delegating the other side's decisions to the FSM).
SelectorBuilder: TypeAlias = Callable[[tuple[float, ...]], IntentSelector]

# The runtime-valid side set, derived from the ``Side`` Literal so it never
# drifts (the ``training.rewards._validate_side`` precedent): a side arriving
# as a plain string from config/CLI must fail loud at spec construction, never
# silently make the scenario unservable by every provider lookup.
_VALID_SIDES: Final[frozenset[str]] = frozenset(get_args(Side))


@dataclass(frozen=True)
class ScenarioSpec:
    """One staged mid-game skill situation + its dense fitness (18.23 public type).

    ``name`` is the scenario's stable identity — it rides campaign rows as the
    :class:`~training.coevo.driver.CoevoScenarioTerm` label. ``side`` names the
    campaign side the drill pressures (the provider serves a scenario only when
    that side is moving). ``staged_tick`` is the mid-game tick the state is
    staged at; ``horizon_ticks`` is the tick budget past it (truncation by
    construction: an episode runs at most ``staged_tick + horizon_ticks``).
    ``build_state`` is the raw constructor — use :func:`build_scenario_state`,
    which validates engine-acceptance, hash-coherence, and the canonical
    rng-snapshot discipline. ``rewards`` documents the fitness definition from
    tactical facts; ``does_not_reward`` names what the definition deliberately
    withholds credit for (the FO-2 Goodhart guard) — both are part of the
    scenario's contract. Signature is stable per the task contract.
    """

    name: str
    side: Side
    staged_tick: int
    horizon_ticks: int
    build_state: ScenarioStateBuilder
    fitness: ScenarioFitness
    rewards: str
    does_not_reward: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("ScenarioSpec.name must be non-empty")
        if self.side not in _VALID_SIDES:
            raise ValueError(
                f"unknown scenario side {self.side!r}; expected one of "
                f"{sorted(_VALID_SIDES)}"
            )
        if self.staged_tick < 0:
            raise ValueError(f"staged_tick must be >= 0, got {self.staged_tick}")
        if self.horizon_ticks < 1:
            raise ValueError(f"horizon_ticks must be >= 1, got {self.horizon_ticks}")

    @property
    def max_ticks(self) -> int:
        """The absolute tick budget of one episode (``staged_tick + horizon``)."""

        return self.staged_tick + self.horizon_ticks


# --------------------------------------------------------------------------- #
# Staged-state construction helpers.                                           #
# --------------------------------------------------------------------------- #


def _player(
    index: int,
    player_id: PlayerId,
    role: Role,
    room: str,
    *,
    alive: bool = True,
) -> PlayerState:
    """One staged player, positioned by roster index like the seeder's spawn."""

    return PlayerState(
        id=player_id,
        role=role,
        alive=alive,
        room=room,
        position=(float(index), 0.0),
        last_action=None,
        in_vent=False,
    )


def _task_instance(
    game_map: Map,
    owner: PlayerId,
    map_task_id: str,
    *,
    progress: int = 0,
    completed: bool = False,
) -> tuple[TaskInstanceId, TaskState]:
    """One per-player task instance keyed/id'd ``"{owner}:{map_task_id}"``.

    ``room`` / ``required_ticks`` are read off the map definition so the
    instance can never drift from the map contract; a completed instance pins
    ``progress == required_ticks`` (the engine's own completion semantics).
    """

    definition = game_map.tasks[map_task_id]
    if completed:
        progress = definition.duration_ticks
    instance_id: TaskInstanceId = f"{owner}:{map_task_id}"
    return instance_id, TaskState(
        id=instance_id,
        owner=owner,
        map_task_id=map_task_id,
        room=definition.room,
        progress=progress,
        required_ticks=definition.duration_ticks,
        completed=completed,
    )


def _staged_state(
    *,
    game_map: Map,
    seed: int,
    tick: int,
    players: Mapping[PlayerId, PlayerState],
    tasks: Mapping[TaskInstanceId, TaskState],
    bodies: Mapping[str, BodyState] | None = None,
    cooldowns: Mapping[PlayerId, int] | None = None,
) -> WorldState:
    """Assemble a staged PLAY-phase state with the canonical rng discipline.

    ``rng_state`` is ALWAYS the canonical ``EngineRng.from_seed(seed)``
    snapshot and ``seed`` the same seed — the one rule every scenario shares,
    centralized so no builder can drift from it (``advance_tick`` is then a
    pure function and the determinism story is inherited, not re-invented).
    """

    return WorldState(
        tick=tick,
        phase="PLAY",
        map=game_map.id,
        players=players,
        bodies=bodies if bodies is not None else {},
        tasks=tasks,
        sabotage=None,
        cooldowns=cooldowns if cooldowns is not None else {},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


# --------------------------------------------------------------------------- #
# The four scenarios.                                                          #
# --------------------------------------------------------------------------- #

_KILL_WITNESS_TICK: Final[int] = 40
_KILL_WITNESS_HORIZON: Final[int] = 20

_VENT_PATROL_TICK: Final[int] = 30
_VENT_PATROL_HORIZON: Final[int] = 12

_FORCE_PARITY_TICK: Final[int] = 80
_FORCE_PARITY_HORIZON: Final[int] = 24

_BODY_DISCOVERY_TICK: Final[int] = 50
_BODY_DISCOVERY_HORIZON: Final[int] = 20
# The staged corpse: killed four ticks before the staged tick, id per the
# engine's ``body-{victim}-{tick}`` minting convention (engine/rules.py).
_BODY_DISCOVERY_BODY_ID: Final[str] = f"body-p-6-{_BODY_DISCOVERY_TICK - 4}"


def _build_kill_with_witness_state(game_map: Map, seed: int) -> WorldState:
    """The staged kill window: victim co-located, a witness one room over.

    The impostor (p-4) stands in LABS with the victim (p-5), kill off cooldown
    — the window is open NOW. The nearby witness (p-3) works MEDBAY, LABS's one
    doorway neighbor: under the base ``same_room_and_adjacent`` visibility the
    witness sees the scene, but kill witnesses are same-room only, so the kill
    itself mints no crew testimony — what follows (the body find, the sighting
    records, the meeting) is exactly the scrutiny the drill is about surviving.
    The rest of the crew is spread mid-map, each with a live local task.
    """

    players = {
        "p-1": _player(0, "p-1", "CREWMATE", "CAFETERIA"),
        "p-2": _player(1, "p-2", "CREWMATE", "ADMIN"),
        "p-3": _player(2, "p-3", "CREWMATE", "MEDBAY"),
        "p-4": _player(3, "p-4", "IMPOSTOR", "LABS"),
        "p-5": _player(4, "p-5", "CREWMATE", "LABS"),
        "p-6": _player(5, "p-6", "CREWMATE", "ENGINEERING"),
    }
    tasks = dict(
        (
            _task_instance(game_map, "p-1", "empty_trash"),
            _task_instance(game_map, "p-2", "swipe_card"),
            _task_instance(game_map, "p-3", "submit_scan"),
            _task_instance(game_map, "p-5", "analyze_specimen"),
            _task_instance(game_map, "p-6", "calibrate_distributor"),
        )
    )
    return _staged_state(
        game_map=game_map,
        seed=seed,
        tick=_KILL_WITNESS_TICK,
        players=players,
        tasks=tasks,
        cooldowns={"p-4": 0},
    )


def _kill_with_witness_fitness(rollout: EpisodeRollout) -> float:
    """kill landed (capped at one) + survived the CREW's POST-KILL meeting.

    ``kills`` comes from the standing impostor dense terms
    (:func:`training.rewards.side_specific_terms`, consumed as-is); the
    survival clause reads the meeting records: at least one meeting ROUTED BY
    A CREWMATE, triggered on a STRICTLY LATER tick than the first kill,
    concluded, and no concluded meeting ejected an impostor. Both qualifiers
    are load-bearing: the scrutiny must be the crew's doing, so an impostor
    cannot farm the credit by self-reporting its own kill (the default fake
    meeting layer can never eject, which would otherwise make "survived"
    collapse into "any meeting concluded"), and it must FOLLOW the kill — a
    meeting triggered before OR ON the kill's tick was decided from packets
    built before the kill resolved (intents are collected pre-tick), so it
    cannot be scrutiny of it; the strict inequality closes both the pre-kill
    button press and the same-action-batch variant. No qualifying case is
    lost: a same-tick crew report of the fresh corpse is unreachable anyway
    (the body is absent from the pre-kill observation packets the batch's
    intents were chosen from). The survival credit is also gated on the kill —
    the drill is "kill, then survive the scrutiny", not "hide through a
    meeting". Under an ejection-capable meeting layer
    (:class:`ScenarioProvider`'s ``meeting_runner_factory``) the no-ejection
    clause becomes fully live.
    """

    terms = side_specific_terms(rollout, "IMPOSTOR")
    kill_landed = 1.0 if terms["kills"] >= 1.0 else 0.0
    kill_ticks = [
        event.tick for event in rollout.events if isinstance(event, KilledEvent)
    ]
    first_kill_tick = min(kill_ticks) if kill_ticks else None
    concluded = [m for m in rollout.meetings if m.outcome is not None]
    crew_scrutiny_after_kill = first_kill_tick is not None and any(
        meeting.tick > first_kill_tick
        and rollout.roles.get(meeting.triggered_by) == "CREWMATE"
        for meeting in concluded
    )
    no_impostor_ejected = all(
        meeting.ejected_player_id is None
        or rollout.roles.get(meeting.ejected_player_id) != "IMPOSTOR"
        for meeting in concluded
    )
    survived = (
        1.0 if kill_landed and crew_scrutiny_after_kill and no_impostor_ejected else 0.0
    )
    return kill_landed + survived


KILL_WITH_WITNESS_NEARBY: Final[ScenarioSpec] = ScenarioSpec(
    name="kill-with-witness-nearby-then-survive-the-meeting",
    side="impostor",
    staged_tick=_KILL_WITNESS_TICK,
    horizon_ticks=_KILL_WITNESS_HORIZON,
    build_state=_build_kill_with_witness_state,
    fitness=_kill_with_witness_fitness,
    rewards=(
        "1.0 for landing at least one kill (the staged window: victim "
        "co-located, cooldown 0, a witness one room over) plus 1.0 for then "
        "having at least one CREW-routed meeting, triggered strictly after "
        "the first kill's tick, conclude with no impostor ejected in any "
        "concluded meeting."
    ),
    does_not_reward=(
        "un-witnessed-ness (the drill IS acting under nearby observation — "
        "contrast the standing unwitnessed_kills term); second kills (the kill "
        "credit caps at one, so silencing the witness earns nothing); meeting "
        "suppression (the survival credit REQUIRES a crew-routed concluded "
        "meeting, so preventing one forfeits it); self-report spam (an "
        "impostor-routed meeting never carries the survival credit); "
        "pre-kill or same-tick meetings (a meeting triggered before or in the "
        "kill's own action batch was decided from pre-kill observations and "
        "is not scrutiny of it); surviving a meeting without the kill."
    ),
)


def _build_vent_patrol_state(game_map: Map, seed: int) -> WorldState:
    """The staged vent choice: one watched exit, one watched door, one way out.

    The impostor (p-4) sits in REACTOR — a vented dead end. Its vent connects
    to STORAGE (empty) and ADMIN (watched by p-3); the only doorway leads to
    ENGINEERING (patrolled by p-2, who also covers ENGINEERING_VENT). The kill
    is staged OFF the table (full cooldown): the drill is moving through the
    vent network without a crew witness, not clearing the patrol.
    """

    players = {
        "p-1": _player(0, "p-1", "CREWMATE", "CAFETERIA"),
        "p-2": _player(1, "p-2", "CREWMATE", "ENGINEERING"),
        "p-3": _player(2, "p-3", "CREWMATE", "ADMIN"),
        "p-4": _player(3, "p-4", "IMPOSTOR", "REACTOR"),
        "p-5": _player(4, "p-5", "CREWMATE", "WEST_HALL"),
        "p-6": _player(5, "p-6", "CREWMATE", "MEDBAY"),
    }
    tasks = dict(
        (
            _task_instance(game_map, "p-1", "fix_wiring_cafeteria"),
            _task_instance(game_map, "p-2", "align_engine_output"),
            _task_instance(game_map, "p-3", "upload_logs"),
            _task_instance(game_map, "p-5", "inspect_samples"),
            _task_instance(game_map, "p-6", "submit_scan"),
        )
    )
    return _staged_state(
        game_map=game_map,
        seed=seed,
        tick=_VENT_PATROL_TICK,
        players=players,
        tasks=tasks,
        cooldowns={"p-4": game_map.kill_cooldown_ticks},
    )


def _vent_patrol_fitness(rollout: EpisodeRollout) -> float:
    """a vent-NETWORK transit + no crew witness on any vent event.

    A transit is a ``VentExited`` whose source and destination VENTS DIFFER —
    the actor actually moved through the network. The engine also accepts
    exiting at the current vent, so an in-place enter/exit bob in the staged
    empty room would otherwise satisfy an any-enter+any-exit reading and
    collect the unseen credit for free; the source!=destination requirement
    closes that hole. ``witnesses`` on the events is the engine's union of
    source- and destination-room witnesses, filtered here to crew (a fellow
    impostor is no witness risk); the unseen credit covers EVERY impostor
    vent event and is conditional on the transit, so holding still — in a
    room or inside a vent — is worth exactly zero.
    """

    vent_events = [
        event
        for event in rollout.events
        if isinstance(event, (VentEnteredEvent, VentExitedEvent))
        and rollout.roles.get(event.actor) == "IMPOSTOR"
    ]
    transited = any(
        isinstance(event, VentExitedEvent)
        and event.source_vent_id != event.destination_vent_id
        for event in vent_events
    )
    if not transited:
        return 0.0
    crew_saw = any(
        rollout.roles.get(witness) == "CREWMATE"
        for event in vent_events
        for witness in event.witnesses
    )
    return 1.0 + (0.0 if crew_saw else 1.0)


VENT_UNSEEN_UNDER_PATROL: Final[ScenarioSpec] = ScenarioSpec(
    name="vent-unseen-under-patrol",
    side="impostor",
    staged_tick=_VENT_PATROL_TICK,
    horizon_ticks=_VENT_PATROL_HORIZON,
    build_state=_build_vent_patrol_state,
    fitness=_vent_patrol_fitness,
    rewards=(
        "1.0 for a completed vent-network transit (a VentExited whose source "
        "and destination vents differ) plus 1.0 when no crew witness appears "
        "on any impostor vent event (source or destination room)."
    ),
    does_not_reward=(
        "kills (the cooldown is staged full — clearing the patrol by killing "
        "it earns nothing); hiding in place (the unseen credit requires a "
        "real transit, so never venting scores zero); in-place vent bobs "
        "(entering and exiting the SAME vent is not a transit and scores "
        "zero); witness-free play that never touches the vent network."
    ),
)


def _build_force_parity_state(game_map: Map, seed: int) -> WorldState:
    """The staged endgame: one impostor, two crew, one kill from parity.

    Mid-game attrition already happened — two crew are dead (ejected across
    earlier meetings, so no bodies remain) and each holds only completed work,
    keeping the crew task race honestly alive on the two survivors' instances.
    The impostor (p-2) starts on full cooldown one doorway from the STORAGE
    crew: the drill is converting a won position within the horizon.
    """

    players = {
        "p-1": _player(0, "p-1", "CREWMATE", "MEDBAY"),
        "p-2": _player(1, "p-2", "IMPOSTOR", "ENGINEERING"),
        "p-3": _player(2, "p-3", "CREWMATE", "CAFETERIA", alive=False),
        "p-4": _player(3, "p-4", "CREWMATE", "ADMIN", alive=False),
        "p-5": _player(4, "p-5", "CREWMATE", "STORAGE"),
    }
    tasks = dict(
        (
            _task_instance(game_map, "p-1", "submit_scan", progress=4),
            _task_instance(game_map, "p-3", "swipe_card", completed=True),
            _task_instance(game_map, "p-4", "log_findings", completed=True),
            _task_instance(game_map, "p-5", "fuel_reserves", progress=2),
        )
    )
    return _staged_state(
        game_map=game_map,
        seed=seed,
        tick=_FORCE_PARITY_TICK,
        players=players,
        tasks=tasks,
        cooldowns={"p-2": game_map.kill_cooldown_ticks},
    )


def _force_parity_fitness(rollout: EpisodeRollout) -> float:
    """kill progress toward parity + parity actually reached, from frame facts.

    ``needed`` is the staged kill deficit (crew minus impostors on the opening
    frame — build validation guarantees it is positive; the ``max`` is pure
    divide-safety for foreign rollouts). Parity is read off the FINAL frame's
    alive counts — engine facts — never the ``winner`` literal, so a game that
    ends inside the horizon scores through the same definition.
    """

    first = rollout.frames[0]
    last = rollout.frames[-1]
    needed = max(1, first.alive_crew - first.alive_impostors)
    kills = sum(1 for event in rollout.events if isinstance(event, KilledEvent))
    progress = min(float(kills), float(needed)) / float(needed)
    parity = 1.0 if last.alive_impostors >= last.alive_crew else 0.0
    return progress + parity


FORCE_PARITY_ENDGAME: Final[ScenarioSpec] = ScenarioSpec(
    name="force-parity-endgame",
    side="impostor",
    staged_tick=_FORCE_PARITY_TICK,
    horizon_ticks=_FORCE_PARITY_HORIZON,
    build_state=_build_force_parity_state,
    fitness=_force_parity_fitness,
    rewards=(
        "kill progress toward the staged parity deficit (kills / needed, "
        "capped at 1.0) plus 1.0 when the final frame's alive impostors >= "
        "alive crew — the forced-parity roster, read from frame scalars."
    ),
    does_not_reward=(
        "the terminal winner literal (parity is read from alive counts, never "
        "the outcome — the terminal gate stays closed); sabotage-clock wins "
        "(an IMPOSTOR_SABOTAGE timeout ends the game without moving the "
        "roster and earns nothing); stealth (witnesses are irrelevant to the "
        "tempo drill)."
    ),
)


def _build_body_discovery_state(game_map: Map, seed: int) -> WorldState:
    """The staged discovery problem: a fresh body in the far dead-end room.

    p-6 was killed in STORAGE four ticks ago (the body id carries the engine's
    ``body-{victim}-{tick}`` minting convention) and the killer (p-3) has
    walked back to ADMIN, kill ready again. The crew is spread mid-map; p-2
    owns a live STORAGE task, so the patrol routes past the scene — the drill
    is how fast the crew turns the body into a routed report meeting, under
    the live threat of a second kill.
    """

    victim = _player(5, "p-6", "CREWMATE", "STORAGE", alive=False)
    body = BodyState(
        id=_BODY_DISCOVERY_BODY_ID,
        player_id="p-6",
        room="STORAGE",
        position=victim.position,
        killed_by="p-3",
        discovered_by=None,
    )
    players = {
        "p-1": _player(0, "p-1", "CREWMATE", "CAFETERIA"),
        "p-2": _player(1, "p-2", "CREWMATE", "ENGINEERING"),
        "p-3": _player(2, "p-3", "IMPOSTOR", "ADMIN"),
        "p-4": _player(3, "p-4", "CREWMATE", "MEDBAY"),
        "p-5": _player(4, "p-5", "CREWMATE", "EAST_HALL"),
        "p-6": victim,
    }
    tasks = dict(
        (
            _task_instance(game_map, "p-1", "empty_trash"),
            _task_instance(game_map, "p-2", "fuel_reserves"),
            _task_instance(game_map, "p-4", "inspect_samples"),
            _task_instance(game_map, "p-5", "upload_logs"),
        )
    )
    return _staged_state(
        game_map=game_map,
        seed=seed,
        tick=_BODY_DISCOVERY_TICK,
        players=players,
        tasks=tasks,
        bodies={body.id: body},
        cooldowns={"p-3": 0},
    )


def _body_discovery_fitness(rollout: EpisodeRollout) -> float:
    """1 - latency/horizon for the crew's report of THE STAGED BODY; else 0.

    Latency is the first ``MeetingTriggeredEvent`` with ``trigger == "report"``
    whose ``body_id`` IS the staged body's, routed by a crewmate, in ticks past
    the staged tick, normalized by the horizon. The body-id filter is
    load-bearing: a fresh in-episode kill mints a new body whose report is not
    the staged discovery problem — without the filter, an easier-to-find fresh
    corpse would substitute for the drill. No qualifying report scores 0.0 —
    the definition's floor — so a crew that suppresses or simply never
    produces the meeting can never outscore one that does (the FO-2 lesson,
    encoded rather than hoped for).
    """

    first_tick = rollout.frames[0].tick
    report = next(
        (
            event
            for event in rollout.events
            if isinstance(event, MeetingTriggeredEvent)
            and event.trigger == "report"
            and event.body_id == _BODY_DISCOVERY_BODY_ID
            and rollout.roles.get(event.actor) == "CREWMATE"
        ),
        None,
    )
    if report is None:
        return 0.0
    latency = report.tick - first_tick
    return max(0.0, 1.0 - latency / _BODY_DISCOVERY_HORIZON)


BODY_DISCOVERY_LATENCY: Final[ScenarioSpec] = ScenarioSpec(
    name="body-discovery-latency",
    side="crew",
    staged_tick=_BODY_DISCOVERY_TICK,
    horizon_ticks=_BODY_DISCOVERY_HORIZON,
    build_state=_build_body_discovery_state,
    fitness=_body_discovery_fitness,
    rewards=(
        "max(0, 1 - latency/horizon) where latency is the tick delay from the "
        "staged state to the first report-triggered meeting of the STAGED "
        "body, routed by a crewmate — faster discovery scores higher."
    ),
    does_not_reward=(
        "meeting suppression (no crew-routed report of the staged body scores "
        "0.0, the floor — fewer meetings can never outscore discovery; the "
        "FO-2 lesson); emergency-button meetings (button spam is not "
        "discovery); impostor-routed reports (a self-report gains the crew "
        "nothing); reports of OTHER bodies (a fresh in-episode kill's corpse "
        "is not the staged discovery problem)."
    ),
)


#: The standing skill-scenario library (the first four, per the task contract).
SCENARIO_LIBRARY: Final[tuple[ScenarioSpec, ...]] = (
    KILL_WITH_WITNESS_NEARBY,
    VENT_UNSEEN_UNDER_PATROL,
    FORCE_PARITY_ENDGAME,
    BODY_DISCOVERY_LATENCY,
)


def scenario_by_name(name: str) -> ScenarioSpec:
    """Look up a library scenario by its stable name (fail loud on unknown)."""

    for spec in SCENARIO_LIBRARY:
        if spec.name == name:
            return spec
    known = ", ".join(spec.name for spec in SCENARIO_LIBRARY)
    raise ValueError(f"unknown scenario {name!r}; known scenarios: {known}")


# --------------------------------------------------------------------------- #
# Validated staged-state construction (the 18.23 public entry).                #
# --------------------------------------------------------------------------- #


def build_scenario_state(
    spec: ScenarioSpec,
    *,
    seed: int,
    game_map: Map | None = None,
) -> WorldState:
    """Build ``spec``'s staged state for ``seed``, validated (18.23 public entry).

    Constructs the state through ``spec.build_state`` and then fails loud
    (AGENTS.md "no silent fallbacks") on anything the engine would accept
    silently but no real game could produce — the validation is what makes
    "engine-accepted, hash-coherent" a checked property rather than a hope:
    the canonical rng-snapshot discipline, the PLAY phase, roster viability
    (an immediate parity/eject/task win is a construction bug), task-instance
    key coherence, dead players owning no incomplete work, bodies referencing
    dead players, and vent/cooldown/room sanity. Signature is stable per the
    task contract.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    state = spec.build_state(resolved_map, seed)
    _validate_scenario_state(spec, state, game_map=resolved_map, seed=seed)
    return state


def _validate_scenario_state(
    spec: ScenarioSpec, state: WorldState, *, game_map: Map, seed: int
) -> None:
    def _fail(message: str) -> None:
        raise ValueError(f"scenario {spec.name!r}: {message}")

    if state.phase != "PLAY":
        _fail(f"staged state must be PLAY-phase, got {state.phase!r}")
    if state.map != game_map.id:
        _fail(f"staged state is for map {state.map!r}, expected {game_map.id!r}")
    if state.tick != spec.staged_tick:
        _fail(f"staged tick {state.tick} != spec.staged_tick {spec.staged_tick}")
    if state.seed != seed:
        _fail(f"staged seed {state.seed} != requested seed {seed}")
    # The rng-snapshot discipline: canonical from_seed snapshot, byte-exact.
    if state.rng_state != EngineRng.from_seed(seed).snapshot():
        _fail(
            "rng_state is not the canonical EngineRng.from_seed(seed) snapshot "
            "(the determinism discipline every scenario state must carry)"
        )

    alive_impostors = sum(
        1 for p in state.players.values() if p.alive and p.role == "IMPOSTOR"
    )
    alive_crew = sum(
        1 for p in state.players.values() if p.alive and p.role == "CREWMATE"
    )
    if alive_impostors < 1:
        _fail("staged state has no living impostor (instant CREWMATE_EJECT)")
    if alive_crew <= alive_impostors:
        _fail(
            f"staged state has {alive_crew} living crew vs {alive_impostors} "
            "living impostors — parity uses >=, so this is an instant "
            "IMPOSTOR_PARITY game-over"
        )

    for player_id, player in state.players.items():
        if player.id != player_id:
            _fail(f"players key {player_id!r} != PlayerState.id {player.id!r}")
        if player.room not in game_map.rooms:
            _fail(f"player {player_id!r} stands in unknown room {player.room!r}")
        if player.in_vent:
            if not player.alive:
                _fail(f"dead player {player_id!r} cannot be in a vent")
            if game_map.vent_for_room(player.room) is None:
                _fail(
                    f"player {player_id!r} is in_vent in ventless room "
                    f"{player.room!r} (advance_tick would crash on its next "
                    "vent action)"
                )

    incomplete = 0
    for instance_id, task in state.tasks.items():
        if task.id != instance_id:
            _fail(f"tasks key {instance_id!r} != TaskState.id {task.id!r}")
        if task.id != f"{task.owner}:{task.map_task_id}":
            _fail(
                f"task instance id {task.id!r} must be the composite "
                f"'{task.owner}:{task.map_task_id}'"
            )
        owner = state.players.get(task.owner)
        if owner is None:
            _fail(f"task {task.id!r} owned by unknown player {task.owner!r}")
        elif owner.role != "CREWMATE":
            _fail(
                f"task {task.id!r} owned by impostor {task.owner!r}: no game "
                "path mints impostor-owned instances (the seeder deals to "
                "crew only; impostors get pretend task ids), and an "
                "impostor-owned incomplete instance would permanently block "
                "CREWMATE_TASKS"
            )
        definition = game_map.tasks.get(task.map_task_id)
        if definition is None:
            _fail(f"task {task.id!r} references unknown map task")
        else:
            if task.room != definition.room:
                _fail(
                    f"task {task.id!r} room {task.room!r} != map room "
                    f"{definition.room!r}"
                )
            if task.required_ticks != definition.duration_ticks:
                _fail(
                    f"task {task.id!r} required_ticks {task.required_ticks} != "
                    f"map duration {definition.duration_ticks}"
                )
        if task.completed:
            if task.progress != task.required_ticks:
                _fail(f"completed task {task.id!r} must have full progress")
        else:
            incomplete += 1
            if not (0 <= task.progress < task.required_ticks):
                _fail(f"incomplete task {task.id!r} has out-of-range progress")
            if owner is not None and not owner.alive:
                _fail(
                    f"dead player {task.owner!r} owns incomplete task "
                    f"{task.id!r} (violates the engine's dead-task invariant "
                    "and permanently blocks CREWMATE_TASKS)"
                )
    if state.tasks and incomplete == 0:
        _fail("all task instances completed (instant CREWMATE_TASKS game-over)")

    for body_id, body in state.bodies.items():
        if body.id != body_id:
            _fail(f"bodies key {body_id!r} != BodyState.id {body.id!r}")
        victim = state.players.get(body.player_id)
        if victim is None or victim.alive:
            _fail(f"body {body.id!r} must reference a dead roster player")
        if body.room not in game_map.rooms:
            _fail(f"body {body.id!r} lies in unknown room {body.room!r}")

    for player_id, cooldown in state.cooldowns.items():
        cooldown_owner = state.players.get(player_id)
        if cooldown_owner is None or cooldown_owner.role != "IMPOSTOR":
            _fail(
                f"cooldown key {player_id!r} is not a roster impostor (the "
                "seeder discipline: only impostors carry kill cooldowns)"
            )
        if not 0 <= cooldown <= game_map.kill_cooldown_ticks:
            _fail(
                f"cooldown {cooldown} for {player_id!r} is outside "
                f"[0, {game_map.kill_cooldown_ticks}]: the engine only ever "
                "sets a cooldown to the map maximum and decrements it, so a "
                "larger staged value is a state no game can produce (and can "
                "silently bench the impostor for a short drill's whole "
                "horizon)"
            )

    if state.sabotage is not None and state.sabotage.active:
        if state.sabotage.kind not in game_map.sabotages:
            _fail(f"active sabotage kind {state.sabotage.kind!r} unknown to map")
        if state.sabotage.remaining_ticks <= 0:
            _fail("active sabotage at 0 remaining ticks (instant IMPOSTOR_SABOTAGE)")


# --------------------------------------------------------------------------- #
# The scenario provider (the 18.21 seam conformer).                            #
# --------------------------------------------------------------------------- #


class ScenarioProvider:
    """A :data:`~training.coevo.driver.CoevoScenarioProvider` conformer (18.23).

    Called by the driver ONCE per swap with ``(swap_index, moving_side)``; it
    returns one :class:`~training.coevo.driver.CoevoScenarioTerm` per scenario
    configured for the moving side (the term label is the scenario name — it
    rides campaign rows as ``scenario_labels``). Sides without a selector
    builder or without scenarios yield ``()``, which the driver treats as
    inert.

    **Purity (the ES contract).** Each term's fitness is a pure deterministic
    function of the flat genome: it builds the side's selector from the
    genome, replays the scenario's episodes fresh over the fixed
    ``fitness_seeds`` (every staged state carries the canonical
    ``EngineRng.from_seed`` snapshot; the default meeting layer is the env's
    forced fake provider), and averages the per-episode dense fitness. No
    state crosses calls, so the same genome always returns the same value —
    the only way a provider could break the driver's pinned double-run digest
    is ruled out by construction. An injected ``meeting_runner_factory``
    inherits that obligation: the runner it builds must itself be
    deterministic (e.g. the surrogate / gated composed runner), never a live
    LLM.

    **Budget (stated, per the task contract).** Scenario episodes sit OUTSIDE
    the driver's ``projected_game_bound`` ceiling guard, so this provider owns
    and states its own budget: one ``term.fitness(genome)`` call runs
    ``len(fitness_seeds)`` episodes, so one driver ES evaluation costs
    :meth:`games_per_evaluation` episodes for the moving side (the driver
    evaluates ``1 + population`` genomes per generation). Episodes are
    horizon-capped by construction (``spec.staged_tick + spec.horizon_ticks``),
    far below a full game.

    ``selector_builders`` maps each side to a genome→selector factory; the
    built selector drives EVERY agent in the episode, so it is responsible for
    delegating decisions it does not own (typically the other side's, via
    ``MaskedDecision.fsm_intent``). ``meeting_runner_factory`` installs an
    ejection-capable meeting layer in the scenario episodes (the env's default
    forced-fake layer resolves every meeting SKIPPED, so ejection-conditioned
    fitness clauses only become fully live through this seam).
    ``rng_hash_policy`` forwards the standard training fast-path opt-in
    (trajectories — and therefore fitness — are identical under either
    policy).
    """

    def __init__(
        self,
        *,
        selector_builders: Mapping[Side, SelectorBuilder],
        fitness_seeds: Sequence[int],
        scenarios: Mapping[Side, Sequence[ScenarioSpec]] | None = None,
        game_map: Map | None = None,
        meeting_runner_factory: Callable[[], MeetingRunner] | None = None,
        rng_hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL,
    ) -> None:
        seeds = tuple(fitness_seeds)
        if not seeds:
            raise ValueError("ScenarioProvider requires at least one fitness seed")
        if len(set(seeds)) != len(seeds):
            raise ValueError(
                f"fitness_seeds must be unique, got {seeds!r}: a duplicate seed "
                "silently double-weights that seed's episode in the scenario mean"
            )
        resolved: dict[Side, tuple[ScenarioSpec, ...]]
        if scenarios is None:
            sides: tuple[Side, ...] = ("impostor", "crew")
            resolved = {
                side: tuple(spec for spec in SCENARIO_LIBRARY if spec.side == side)
                for side in sides
            }
        else:
            resolved = {side: tuple(specs) for side, specs in scenarios.items()}
        for side, specs in resolved.items():
            for spec in specs:
                if spec.side != side:
                    raise ValueError(
                        f"scenario {spec.name!r} is a {spec.side!r}-side drill "
                        f"but was configured under side {side!r}"
                    )
            names = [spec.name for spec in specs]
            if len(set(names)) != len(names):
                raise ValueError(
                    f"duplicate scenario names for side {side!r}: {names!r} — a "
                    "repeated scenario silently double-weights its term in the "
                    "swap's ES fitness (labels ride campaign rows as provenance)"
                )
        self._selector_builders = dict(selector_builders)
        self._fitness_seeds = seeds
        self._scenarios = resolved
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._meeting_runner_factory = meeting_runner_factory
        self._rng_hash_policy = rng_hash_policy

    @property
    def fitness_seeds(self) -> tuple[int, ...]:
        return self._fitness_seeds

    def games_per_evaluation(self, side: Side) -> int:
        """Scenario episodes one ES evaluation of ``side`` costs (the budget).

        ``len(scenarios[side]) * len(fitness_seeds)`` — every term runs each
        fitness seed once per genome; 0 when the side has no selector builder
        or no scenarios (the provider is inert for it).
        """

        if side not in self._selector_builders:
            return 0
        return len(self._scenarios.get(side, ())) * len(self._fitness_seeds)

    def __call__(self, swap_index: int, side: Side) -> tuple[CoevoScenarioTerm, ...]:
        # Scenario pressure is swap-independent (the seam passes swap_index for
        # providers that stage curricula; this library serves a constant set).
        del swap_index
        builder = self._selector_builders.get(side)
        specs = self._scenarios.get(side, ())
        if builder is None or not specs:
            return ()
        return tuple(
            CoevoScenarioTerm(
                label=spec.name,
                fitness=self._build_term_fitness(spec, builder),
            )
            for spec in specs
        )

    def _build_term_fitness(
        self, spec: ScenarioSpec, builder: SelectorBuilder
    ) -> Callable[[tuple[float, ...]], float]:
        def fitness(genome: tuple[float, ...]) -> float:
            selector = builder(genome)
            total = math.fsum(
                spec.fitness(self._run_episode(spec, selector, seed))
                for seed in self._fitness_seeds
            )
            return total / len(self._fitness_seeds)

        return fitness

    def _run_episode(
        self, spec: ScenarioSpec, selector: IntentSelector, seed: int
    ) -> EpisodeRollout:
        state = build_scenario_state(spec, seed=seed, game_map=self._game_map)
        env = TacticalRolloutEnv(
            game_map=self._game_map,
            intent_selector=selector,
            meeting_runner_factory=self._meeting_runner_factory,
            max_ticks=spec.max_ticks,
            no_replay=True,
            rng_hash_policy=self._rng_hash_policy,
        )
        return env.rollout_injected(state)


__all__ = [
    "BODY_DISCOVERY_LATENCY",
    "FORCE_PARITY_ENDGAME",
    "KILL_WITH_WITNESS_NEARBY",
    "SCENARIO_LIBRARY",
    "VENT_UNSEEN_UNDER_PATROL",
    "ScenarioFitness",
    "ScenarioProvider",
    "ScenarioSpec",
    "ScenarioStateBuilder",
    "SelectorBuilder",
    "build_scenario_state",
    "scenario_by_name",
]
