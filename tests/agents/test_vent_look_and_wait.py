"""B1 on hand-built memories: impostors look before leaving a vent and vent only
after their own fresh kill.

Every memory below is built on the canonical public map, in the order perception
appends rows, except where a case says it builds its own map or runs the engine.
Each case also states what ``target_distance`` or ``any_body`` does with the same
memory, so it shows the behaviour it contrasts with. On the tree before this card
building the policy with either value raised the spine's refusal, so every case
that builds one was red there.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import agents.tactical.experimental as experimental
import eval.gameplay_census as census
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import _EVENT_MEETING_BOUNDARY
from agents.perception import ingest_event_observations, ingest_packet
from agents.tactical.experimental import (
    FRESH_KILL_WINDOW_TICKS,
    IN_VENT_CAP_TICKS,
    ExperimentalImpostorPolicy,
    TacticalExperimentOptions,
    inferred_visible_rooms,
)
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.actions import Action, KillAction, WaitAction
from engine.entities import Role, SabotageState
from engine.tick import advance_tick
from engine.visibility import compute_visibility_for_player
from engine.world import WorldState, load_canonical_map
from eval.gameplay_census import (
    CensusInputs,
    EraKey,
    Frame,
    GameFacts,
    GameplayCensusConformanceError,
    VentFact,
    canonical_settings,
    fold_set,
    resolve_era,
)
from observation.action_intent import ActionIntent
from observation.packet import EventObservationBatch, OwnKillView
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.seeder import seed_initial_state

ENGINE_MAP = load_canonical_map()
MAP = public_map_from_engine_map(ENGINE_MAP)
ME = "p-1"
TEAMMATE = "p-2"
CREW = "p-5"
OTHER_CREW = "p-6"
VICTIM = "p-7"

Sabotage = Literal["reactor", "lights"] | None
ExitPolicy = Literal["target_distance", "observed_risk", "look_and_wait"]
EntryPolicy = Literal["any_body", "own_fresh_kill"]


# --------------------------------------------------------------------------- #
# Builders                                                                     #
# --------------------------------------------------------------------------- #


def _policy(
    exit_policy: ExitPolicy = "look_and_wait", entry_policy: EntryPolicy = "any_body"
) -> ExperimentalImpostorPolicy:
    return ExperimentalImpostorPolicy(
        agent_id=ME,
        options=TacticalExperimentOptions(
            vent_exit_policy=exit_policy, vent_entry_policy=entry_policy
        ),
    )


def _row(
    memory: MemoryStore,
    tick: int,
    kind: str,
    *,
    provenance: str = "observed",
    **payload: Any,
) -> None:
    memory.append(
        EpisodicEvent(tick=tick, type=kind, provenance=provenance, payload=payload)
    )


def _tick(
    memory: MemoryStore,
    *,
    tick: int,
    room: str,
    in_vent: bool,
    cooldown: int = 3,
    teammates: tuple[str, ...] = (TEAMMATE,),
    seen: Iterable[tuple[str, str]] = (),
    bodies: Iterable[tuple[str, str]] = (),
    own_kill: tuple[str, str] | None = None,
    sabotage: Sabotage = None,
) -> None:
    """One observation tick, in perception's append order."""

    _row(
        memory,
        tick,
        "self_state",
        agent_id=ME,
        room=room,
        role="IMPOSTOR",
        pending_task_id=None,
        owned_task_ids=(),
        fellow_impostor_ids=teammates,
        in_vent=in_vent,
    )
    if own_kill is not None:
        _row(memory, tick, "own_kill", victim_id=own_kill[0], room=own_kill[1])
    _row(memory, tick, "cooldown_status", cooldown=cooldown)
    for player, where in seen:
        _row(memory, tick, "saw_player", player_id=player, room=where, action=None)
    for victim, where in bodies:
        _row(
            memory,
            tick,
            "saw_body",
            body_id=f"body-{victim}",
            room=where,
            victim_id=victim,
        )
    _row(
        memory,
        tick,
        "global_status",
        provenance="inferred",
        tasks_completed=0,
        tasks_total=14,
        task_completion_percent=0.0,
        sabotage_active=sabotage is not None,
        sabotage_kind=sabotage,
        sabotage_repair_rooms=(),
        sabotage_is_gating=sabotage == "reactor",
    )


def _boundary(memory: MemoryStore, tick: int) -> None:
    _row(memory, tick, _EVENT_MEETING_BOUNDARY, provenance="inferred")


def _inside(
    room: str,
    *,
    inside: int = 1,
    first_tick: int = 20,
    seen: Iterable[tuple[str, str]] = (),
    bodies: Iterable[tuple[str, str]] = (),
    sabotage: Sabotage = None,
    cooldown: int = 3,
    earlier_sightings: Iterable[tuple[int, str, str]] = (),
    boundary_after: int | None = None,
) -> MemoryStore:
    """An impostor that entered the vent in ``room`` and has ``inside`` rows in it.

    The last tick carries ``seen``, ``bodies`` and ``sabotage``; earlier ticks
    inside see nobody. ``earlier_sightings`` are (tick, player, room) rows placed
    before the entry. ``boundary_after`` puts a meeting boundary before that many
    trailing in-vent rows, as the post-meeting fold does at the resume tick.
    """

    memory = MemoryStore()
    for tick, player, where in earlier_sightings:
        _tick(memory, tick=tick, room=room, in_vent=False, seen=((player, where),))
    entry = first_tick
    _tick(memory, tick=entry, room=room, in_vent=False, cooldown=cooldown + 1)
    last = entry + inside
    for tick in range(entry + 1, last + 1):
        if boundary_after is not None and tick == last - boundary_after + 1:
            _boundary(memory, tick)
        is_last = tick == last
        _tick(
            memory,
            tick=tick,
            room=room,
            in_vent=True,
            cooldown=cooldown,
            seen=seen if is_last else (),
            bodies=bodies,
            sabotage=sabotage if is_last else None,
        )
    return memory


def _vent(intent: ActionIntent) -> str:
    assert intent.type == "vent", intent
    return intent.payload.vent_id


# --------------------------------------------------------------------------- #
# The exit                                                                     #
# --------------------------------------------------------------------------- #


def test_a_watched_exit_makes_it_wait_then_it_surfaces_clear() -> None:
    body = ((VICTIM, "STORAGE"),)
    watched = _inside("STORAGE", seen=((CREW, "ENGINEERING"),), bodies=body)
    # target_distance steers to the room of the crewmate it just saw.
    assert _vent(_policy("target_distance").decide(watched, MAP)) == "ENGINEERING_VENT"
    assert _policy().decide(watched, MAP).type == "wait"
    # Next tick ENGINEERING is clear: it surfaces there, a room with no body
    # that is not the room it fled.
    _tick(
        watched,
        tick=22,
        room="STORAGE",
        in_vent=True,
        seen=((CREW, "EAST_HALL"),),
        bodies=body,
    )
    assert _vent(_policy().decide(watched, MAP)) == "ENGINEERING_VENT"


def test_the_blind_exit_contrast() -> None:
    # REACTOR sees ENGINEERING; neither connected vent's room is visible.
    watched = _inside("REACTOR", seen=((CREW, "ENGINEERING"),))
    anchor = _vent(_policy("target_distance").decide(watched, MAP))
    assert anchor in ("STORAGE_VENT", "ADMIN_VENT")
    assert _policy().decide(watched, MAP).type == "wait"
    # Every visible room clear: in place, never at a room it cannot see, even
    # with its own victim underfoot and the blind rooms showing no body.
    clear = _inside("REACTOR", bodies=((VICTIM, "REACTOR"),))
    assert _vent(_policy().decide(clear, MAP)) == "REACTOR_VENT"
    assert _vent(_policy("target_distance").decide(clear, MAP)) != "REACTOR_VENT"


def test_a_non_teammate_in_its_own_room_forces_a_wait() -> None:
    # Under the physical rule this crewmate would not witness an exit into
    # ENGINEERING; the look waits for it anyway.
    memory = _inside("STORAGE", seen=((CREW, "STORAGE"),))
    assert _policy().decide(memory, MAP).type == "wait"
    assert _policy("target_distance").decide(memory, MAP).type == "vent"


@pytest.mark.parametrize("where", ["ADMIN", "UPPER_HALL", "EAST_HALL", "WEST_HALL"])
def test_a_teammate_is_never_a_watcher(where: str) -> None:
    memory = _inside("ADMIN", seen=((TEAMMATE, where),))
    assert _vent(_policy().decide(memory, MAP)) == "ADMIN_VENT"
    # target_distance surfaces at a connected vent.
    assert _vent(_policy("target_distance").decide(memory, MAP)) == "MEDBAY_VENT"


def test_the_teammate_list_comes_from_self_state() -> None:
    # The same sighting with no fellow ids recorded is a watcher.
    memory = MemoryStore()
    _tick(memory, tick=20, room="ADMIN", in_vent=False, teammates=())
    _tick(
        memory,
        tick=21,
        room="ADMIN",
        in_vent=True,
        teammates=(),
        seen=((TEAMMATE, "ADMIN"),),
    )
    assert _policy().decide(memory, MAP).type == "wait"


@pytest.mark.parametrize("provenance", ["reported", "inferred"])
def test_a_sighting_that_is_not_first_hand_never_counts(provenance: str) -> None:
    memory = _inside("ADMIN")
    _row(memory, 21, "saw_player", provenance=provenance, player_id=CREW, room="ADMIN")
    assert _vent(_policy().decide(memory, MAP)) == "ADMIN_VENT"
    observed = _inside("ADMIN", seen=((CREW, "ADMIN"),))
    assert _policy().decide(observed, MAP).type == "wait"


def test_a_sighting_of_itself_is_not_a_watcher() -> None:
    memory = _inside("ADMIN", seen=((ME, "ADMIN"),))
    assert _vent(_policy().decide(memory, MAP)) == "ADMIN_VENT"


def test_a_sighting_outside_its_inferred_sight_is_not_read() -> None:
    # CAFETERIA is not a neighbour of ADMIN; a row placing someone there is
    # outside what the impostor infers it sees.
    memory = _inside("ADMIN", seen=((CREW, "CAFETERIA"),))
    assert _vent(_policy().decide(memory, MAP)) == "ADMIN_VENT"


def test_a_clear_room_with_a_body_loses_to_one_without() -> None:
    # In place has no body, the visible connected room has one: in place.
    memory = _inside("STORAGE", bodies=((VICTIM, "ENGINEERING"),))
    assert _vent(_policy().decide(memory, MAP)) == "STORAGE_VENT"


def test_a_clear_connected_room_beats_the_room_it_fled() -> None:
    # Neither room holds a body; the vent ids alone would keep it in place.
    memory = _inside("ENGINEERING")
    assert _vent(_policy().decide(memory, MAP)) == "STORAGE_VENT"


# --------------------------------------------------------------------------- #
# The cap                                                                      #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("inside", [1, 2, 3])
def test_it_waits_before_the_cap_with_a_watcher_in_view(inside: int) -> None:
    memory = _inside("STORAGE", inside=inside, seen=((CREW, "ENGINEERING"),))
    assert _policy().decide(memory, MAP).type == "wait"


def test_at_the_cap_it_surfaces_by_the_ruled_key() -> None:
    # STORAGE clear, ENGINEERING watched, REACTOR unseen: clear before unseen
    # before watched puts it in place. The literal fewest-visible key (an unseen
    # room counts 0 and a connected vent beats in place) takes REACTOR, and
    # target_distance takes the watched room.
    memory = _inside(
        "STORAGE",
        inside=IN_VENT_CAP_TICKS,
        seen=((CREW, "ENGINEERING"),),
        bodies=((VICTIM, "STORAGE"),),
    )
    assert _vent(_policy().decide(memory, MAP)) == "STORAGE_VENT"
    assert _vent(_policy("target_distance").decide(memory, MAP)) == "ENGINEERING_VENT"
    literal = min(
        ("STORAGE_VENT", "REACTOR_VENT", "ENGINEERING_VENT"),
        key=lambda vent: (
            1 if vent == "ENGINEERING_VENT" else 0,
            vent == "STORAGE_VENT",
            vent,
        ),
    )
    assert literal == "REACTOR_VENT"


def test_at_the_cap_an_unseen_room_beats_a_watched_one() -> None:
    memory = _inside(
        "STORAGE",
        inside=IN_VENT_CAP_TICKS,
        seen=((CREW, "ENGINEERING"), (OTHER_CREW, "STORAGE")),
    )
    assert _vent(_policy().decide(memory, MAP)) == "REACTOR_VENT"


def test_at_the_cap_a_clear_room_without_a_body_beats_one_with() -> None:
    # Both STORAGE and ENGINEERING are clear; only ENGINEERING holds a body.
    memory = _inside(
        "STORAGE",
        inside=IN_VENT_CAP_TICKS,
        seen=((CREW, "EAST_HALL"),),
        bodies=((VICTIM, "ENGINEERING"),),
    )
    assert _vent(_policy().decide(memory, MAP)) == "STORAGE_VENT"


def test_at_the_cap_two_unseen_rooms_fall_to_the_vent_id() -> None:
    memory = _inside("REACTOR", inside=IN_VENT_CAP_TICKS, seen=((CREW, "REACTOR"),))
    assert _vent(_policy().decide(memory, MAP)) == "ADMIN_VENT"


def _two_link_map() -> PublicMapView:
    """A map where the vent in H links to two visible rooms and a second vent in H."""

    return PublicMapView(
        map_id="two_links",
        room_ids=("H", "A", "B", "C"),
        room_neighbors={
            "H": ("A", "B"),
            "A": ("H", "C"),
            "B": ("H", "C"),
            "C": ("A", "B"),
        },
        vent_rooms={"VH": "H", "VH2": "H", "VA": "A", "VB": "B", "VC": "C"},
        vent_graph={
            "VH": ("VA", "VB", "VC", "VH2"),
            "VH2": ("VH",),
            "VA": ("VH",),
            "VB": ("VH",),
            "VC": ("VH",),
        },
        task_locations={},
        spawn_room="H",
        meeting_room="H",
        emergency_button_room="H",
    )


def _custom_inside(
    *,
    inside: int,
    seen: Iterable[tuple[str, str]],
    bodies: Iterable[tuple[str, str]] = (),
) -> MemoryStore:
    memory = MemoryStore()
    _tick(memory, tick=10, room="H", in_vent=False)
    for tick in range(11, 11 + inside):
        last = tick == 10 + inside
        _tick(
            memory,
            tick=tick,
            room="H",
            in_vent=True,
            seen=seen if last else (),
            bodies=bodies if last else (),
        )
    return memory


def test_at_the_cap_fewer_watchers_win_within_the_watched_class() -> None:
    # H, A and B are all watched. With the unseen C linked, C wins on class;
    # with it unlinked the fewest watchers decide, where the later terms (the
    # fled room, in place, then the vent id) would take VA.
    watched = _custom_inside(
        inside=IN_VENT_CAP_TICKS,
        seen=(("p-5", "H"), ("p-6", "H"), ("p-7", "A"), ("p-8", "A"), ("p-9", "B")),
    )
    assert _vent(_policy().decide(watched, _two_link_map())) == "VC"
    no_unseen = _two_link_map().model_copy(
        update={
            "vent_graph": {
                **_two_link_map().vent_graph,
                "VH": ("VA", "VB", "VH2"),
                "VC": (),
            }
        }
    )
    assert _vent(_policy().decide(watched, no_unseen)) == "VB"


def test_at_the_cap_a_connected_vent_in_the_same_room_beats_in_place() -> None:
    # VH2 sits in the fled room too: only "a connected vent before in place"
    # separates it from VH, and the vent id alone would keep VH.
    two_in_h = _two_link_map().model_copy(
        update={"vent_graph": {**_two_link_map().vent_graph, "VH": ("VH2",)}}
    )
    memory = _custom_inside(inside=IN_VENT_CAP_TICKS, seen=())
    assert _vent(_policy().decide(memory, two_in_h)) == "VH2"


def test_at_the_cap_a_room_other_than_the_one_fled_wins() -> None:
    # VH2 (in the fled room H) and VZ (in A) are both connected, clear and
    # bodiless; only the fled-room term separates them, and the vent id alone
    # would take VH2.
    fled = PublicMapView.model_validate(
        {
            **_two_link_map().model_dump(),
            "vent_rooms": {"VH": "H", "VH2": "H", "VZ": "A", "VB": "B", "VC": "C"},
            "vent_graph": {
                "VH": ("VH2", "VZ"),
                "VH2": ("VH",),
                "VZ": ("VH",),
                "VB": (),
                "VC": (),
            },
        }
    )
    memory = _custom_inside(inside=IN_VENT_CAP_TICKS, seen=())
    assert _vent(_policy().decide(memory, fled)) == "VZ"


@pytest.mark.parametrize("restart_at", [1, 2, 3])
def test_a_meeting_boundary_inside_the_streak_restarts_the_count(
    restart_at: int,
) -> None:
    # Six rows inside, a boundary before the last ``restart_at`` of them: the
    # count reads ``restart_at``, below the cap, so it still waits.
    memory = _inside(
        "STORAGE",
        inside=6,
        seen=((CREW, "ENGINEERING"),),
        boundary_after=restart_at,
    )
    assert ExperimentalImpostorPolicy._ticks_inside(memory.recent(since_tick=0)) == (
        restart_at
    )
    assert _policy().decide(memory, MAP).type == "wait"


def test_counting_from_the_entry_alone_fails_the_restart_case(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Perturbed: a count that ignores the boundary surfaces at the restart case."""

    def from_entry(events: tuple[EpisodicEvent, ...]) -> int:
        inside = 0
        for event in reversed(events):
            if event.type != "self_state":
                continue
            if not event.payload["in_vent"]:
                break
            inside += 1
        return inside

    memory = _inside(
        "STORAGE", inside=6, seen=((CREW, "ENGINEERING"),), boundary_after=2
    )
    monkeypatch.setattr(
        ExperimentalImpostorPolicy, "_ticks_inside", staticmethod(from_entry)
    )
    assert _policy().decide(memory, MAP).type == "vent"


def test_an_earlier_trip_does_not_add_to_the_count() -> None:
    # Two rows inside an earlier trip, out for three ticks, then two rows inside
    # this one: the count is 2, below the cap, so a watcher still means a wait.
    memory = MemoryStore()
    _tick(memory, tick=10, room="STORAGE", in_vent=False)
    for tick in (11, 12):
        _tick(memory, tick=tick, room="STORAGE", in_vent=True)
    for tick in (13, 14, 15):
        _tick(memory, tick=tick, room="STORAGE", in_vent=False)
    _tick(memory, tick=16, room="STORAGE", in_vent=True)
    _tick(
        memory,
        tick=17,
        room="STORAGE",
        in_vent=True,
        seen=((CREW, "ENGINEERING"),),
    )
    assert ExperimentalImpostorPolicy._ticks_inside(memory.recent(since_tick=0)) == 2
    assert _policy().decide(memory, MAP).type == "wait"


def test_the_count_comes_from_memory_never_from_instance_state() -> None:
    policy = _policy()
    for inside in (1, 2, 3, IN_VENT_CAP_TICKS, 2):
        memory = _inside("STORAGE", inside=inside, seen=((CREW, "ENGINEERING"),))
        fresh = _policy().decide(memory, MAP)
        assert policy.decide(memory, MAP) == fresh
        assert fresh.type == ("vent" if inside >= IN_VENT_CAP_TICKS else "wait")


# --------------------------------------------------------------------------- #
# No steering inside                                                           #
# --------------------------------------------------------------------------- #


def test_stale_target_sightings_do_not_steer_the_exit() -> None:
    near = _inside(
        "STORAGE", cooldown=0, earlier_sightings=((8, CREW, "REACTOR"),), first_tick=20
    )
    far = _inside(
        "STORAGE", cooldown=0, earlier_sightings=((8, CREW, "LABS"),), first_tick=20
    )
    assert _policy().decide(near, MAP) == _policy().decide(far, MAP)
    assert _vent(_policy().decide(near, MAP)) == "ENGINEERING_VENT"
    anchors = {
        _vent(_policy("target_distance").decide(memory, MAP)) for memory in (near, far)
    }
    assert anchors == {"REACTOR_VENT", "ENGINEERING_VENT"}


def test_the_in_vent_branch_never_reads_the_kill_ranking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def refuse(*args: object, **kwargs: object) -> object:
        raise AssertionError("the kill ranking was read")

    memory = _inside("STORAGE", seen=((CREW, "ENGINEERING"),))
    monkeypatch.setattr(ImpostorPolicy, "_scored_targets", staticmethod(refuse))
    monkeypatch.setattr(ImpostorPolicy, "_decision_targets", staticmethod(refuse))
    assert _policy().decide(memory, MAP).type == "wait"
    with pytest.raises(AssertionError, match="kill ranking"):
        _policy("target_distance").decide(memory, MAP)


# --------------------------------------------------------------------------- #
# Sabotage and the census predicate                                            #
# --------------------------------------------------------------------------- #


def _census_surfacing(crew_room: str, *, sabotage: bool) -> CensusInputs:
    """One look-and-wait trip: entry, then an exit in place one tick later."""

    roles: dict[str, Role] = {ME: "IMPOSTOR", TEAMMATE: "IMPOSTOR", CREW: "CREWMATE"}
    era = EraKey(
        settings=canonical_settings({"vent_exit_policy": "look_and_wait"}),
        temporal_observation_version=None,
        substrate_flags=None,
        prompt_stamps=None,
    )
    game = GameFacts(
        seed=0,
        roles=MappingProxyType(roles),
        era=era,
        kills=(),
        vents=(
            VentFact(20, ME, "entry", "STORAGE", "STORAGE", frozenset(), frozenset()),
            VentFact(21, ME, "exit", "STORAGE", "STORAGE", frozenset(), frozenset()),
        ),
        bodies=(),
        frames=MappingProxyType(
            {
                21: Frame(
                    rooms=MappingProxyType({CREW: crew_room, TEAMMATE: "CAFETERIA"}),
                    sabotage_active=sabotage,
                )
            }
        ),
        meetings=(),
        discarded=(),
        rows_without_dispositions=0,
        winner=None,
        terminal_tick=40,
    )
    return CensusInputs(
        label="planted/b1",
        source="planted/b1",
        era=resolve_era((era,)),
        kill_cooldown_ticks=ENGINE_MAP.kill_cooldown_ticks,
        neighbours=MappingProxyType(
            {room: ENGINE_MAP.room_neighbors(room) for room in sorted(ENGINE_MAP.rooms)}
        ),
        games=(game,),
    )


@pytest.mark.parametrize("sabotage", ["reactor", "lights"])
def test_under_a_sabotage_a_neighbour_counts_as_unseen(sabotage: Sabotage) -> None:
    # The crewmate stands in ENGINEERING, which the engine still shows under a
    # reactor sabotage; the impostor treats it as unseen and surfaces in place.
    memory = _inside("STORAGE", seen=((CREW, "ENGINEERING"),), sabotage=sabotage)
    assert _vent(_policy().decide(memory, MAP)) == "STORAGE_VENT"
    base = _inside("STORAGE", seen=((CREW, "ENGINEERING"),))
    assert _policy().decide(base, MAP).type == "wait"
    # The census predicate reads the same inputs: no breach for this surfacing,
    # one breach with the crewmate in the impostor's own room instead.
    folded = fold_set(_census_surfacing("ENGINEERING", sabotage=True))
    assert folded.cells["surfacings_before_cap_in_view"].numerator == 0
    assert folded.cells["surfacings_before_cap_in_view"].denominator == 1
    with pytest.raises(GameplayCensusConformanceError, match="in view"):
        fold_set(_census_surfacing("STORAGE", sabotage=True))


def test_under_a_sabotage_a_body_in_a_neighbour_is_not_read_at_the_cap() -> None:
    # Reactor: STORAGE watched, ENGINEERING and REACTOR both unseen. A body the
    # engine still shows in ENGINEERING is not read, so the vent id decides.
    memory = _inside(
        "STORAGE",
        inside=IN_VENT_CAP_TICKS,
        seen=((CREW, "STORAGE"),),
        bodies=((VICTIM, "ENGINEERING"),),
        sabotage="reactor",
    )
    assert _vent(_policy().decide(memory, MAP)) == "ENGINEERING_VENT"


# --------------------------------------------------------------------------- #
# The sight model, pinned to the engine                                        #
# --------------------------------------------------------------------------- #


def _impostor_in(room: str, *, sabotage: str | None) -> WorldState:
    state = seed_initial_state(seed=0, game_map=ENGINE_MAP, num_players=4)
    players = {
        pid: replace(
            player,
            role="IMPOSTOR" if pid == ME else "CREWMATE",
            room=room if pid == ME else player.room,
            in_vent=pid == ME,
        )
        for pid, player in state.players.items()
    }
    sabotage_state = (
        None
        if sabotage is None
        else SabotageState(
            kind=sabotage, remaining_ticks=10, affected_rooms=(), active=True
        )
    )
    return replace(state, players=players, sabotage=sabotage_state)


def _sight_mismatches(public_map: PublicMapView) -> list[str]:
    """Rooms where the inferred sight differs from the engine's for an impostor."""

    mismatches: list[str] = []
    for room in sorted(ENGINE_MAP.rooms):
        for sabotage in (None, "lights"):
            engine = compute_visibility_for_player(
                observer_id=ME,
                world_state=_impostor_in(room, sabotage=sabotage),
                game_map=ENGINE_MAP,
            ).visible_rooms
            inferred = inferred_visible_rooms(
                public_map, room, sabotage_active=sabotage is not None
            )
            if frozenset(engine) != inferred:
                mismatches.append(f"{room}/{sabotage}")
    return mismatches


def test_the_inferred_sight_equals_the_engines_at_base_and_under_lights() -> None:
    assert _sight_mismatches(MAP) == []
    # Under a reactor sabotage the engine still shows the neighbours: the
    # inference is narrower, never wider.
    for room in sorted(ENGINE_MAP.rooms):
        engine = compute_visibility_for_player(
            observer_id=ME,
            world_state=_impostor_in(room, sabotage="reactor"),
            game_map=ENGINE_MAP,
        ).visible_rooms
        assert inferred_visible_rooms(MAP, room, sabotage_active=True) < frozenset(
            engine
        )


def test_an_adjacency_with_one_extra_neighbour_fails_the_pin() -> None:
    """Perturbed: one invented neighbour of STORAGE."""

    extra = MAP.model_copy(
        update={
            "room_neighbors": {
                **MAP.room_neighbors,
                "STORAGE": (*MAP.room_neighbors["STORAGE"], "CAFETERIA"),
            }
        }
    )
    assert _sight_mismatches(extra) == ["STORAGE/None"]


def test_an_unknown_room_has_no_inferred_sight() -> None:
    with pytest.raises(ValueError, match="no neighbours for room 'NOWHERE'"):
        inferred_visible_rooms(MAP, "NOWHERE", sabotage_active=False)


# --------------------------------------------------------------------------- #
# The entry gate                                                               #
# --------------------------------------------------------------------------- #


def _entry_memory(
    *,
    own_kill: tuple[str, str] | None,
    kill_row_tick: int = 11,
    decide_tick: int = 11,
    body: tuple[str, str] = (VICTIM, "STORAGE"),
    seen: Iterable[tuple[str, str]] = (),
    boundary: int | None = None,
    boundary_first: bool = False,
) -> MemoryStore:
    memory = MemoryStore()
    _tick(memory, tick=10, room="STORAGE", in_vent=False, cooldown=0)
    for tick in range(kill_row_tick, decide_tick + 1):
        if boundary is not None and tick == boundary and boundary_first:
            _boundary(memory, tick)
        _tick(
            memory,
            tick=tick,
            room="STORAGE",
            in_vent=False,
            cooldown=4,
            own_kill=own_kill if tick == kill_row_tick else None,
            bodies=(body,),
            seen=seen if tick == decide_tick else (),
        )
        if boundary is not None and tick == boundary and not boundary_first:
            _boundary(memory, tick + 1)
    return memory


def _entry(memory: MemoryStore, entry_policy: EntryPolicy) -> ActionIntent:
    return _policy("target_distance", entry_policy).decide(memory, MAP)


def test_a_teammates_victim_makes_it_walk_away() -> None:
    memory = _entry_memory(own_kill=None)
    assert _vent(_entry(memory, "any_body")) == "STORAGE_VENT"
    walked = _entry(memory, "own_fresh_kill")
    assert walked.type == "move" and walked.payload.to_room == "ENGINEERING"
    assert walked == ImpostorPolicy(agent_id=ME)._cover(
        public_map=MAP, own_room="STORAGE"
    )


def test_a_fresh_own_kill_vents_exactly_as_any_body_does() -> None:
    memory = _entry_memory(own_kill=(VICTIM, "STORAGE"))
    assert _entry(memory, "own_fresh_kill") == _entry(memory, "any_body")
    assert _vent(_entry(memory, "own_fresh_kill")) == "STORAGE_VENT"


def test_an_own_victim_across_a_meeting_makes_it_walk_away() -> None:
    # The kill row at 11, a meeting boundary at 12, the decision at 13.
    memory = _entry_memory(own_kill=(VICTIM, "STORAGE"), decide_tick=13, boundary=11)
    assert _vent(_entry(memory, "any_body")) == "STORAGE_VENT"
    assert _entry(memory, "own_fresh_kill").type == "move"


def test_a_kill_on_a_meeting_trigger_tick_is_across_that_meeting() -> None:
    # A kill on the trigger tick is perceived on the resume tick, after the
    # boundary the post-meeting fold appended at that same tick.
    memory = _entry_memory(
        own_kill=(VICTIM, "STORAGE"), boundary=11, boundary_first=True
    )
    rows = memory.recent(since_tick=11)
    assert [row.type for row in rows[:2]] == [_EVENT_MEETING_BOUNDARY, "self_state"]
    assert _vent(_entry(memory, "any_body")) == "STORAGE_VENT"
    assert _entry(memory, "own_fresh_kill").type == "move"


@pytest.mark.parametrize("own_kill", [(VICTIM, "STORAGE"), None])
def test_a_non_teammate_in_the_room_keeps_the_walk_away_under_both(
    own_kill: tuple[str, str] | None,
) -> None:
    memory = _entry_memory(own_kill=own_kill, seen=((CREW, "STORAGE"),))
    assert _entry(memory, "any_body").type == "move"
    assert _entry(memory, "own_fresh_kill") == _entry(memory, "any_body")


def test_an_own_kill_row_in_another_room_is_not_this_body() -> None:
    memory = _entry_memory(own_kill=(VICTIM, "ENGINEERING"))
    assert _entry(memory, "own_fresh_kill").type == "move"


def test_an_own_victim_sighted_in_a_neighbour_is_not_this_body() -> None:
    # The own victim's body is sighted next door; the body here is another's.
    memory = _entry_memory(own_kill=(VICTIM, "STORAGE"), body=(OTHER_CREW, "STORAGE"))
    _row(
        memory,
        11,
        "saw_body",
        body_id=f"body-{VICTIM}",
        room="ENGINEERING",
        victim_id=VICTIM,
    )
    assert _vent(_entry(memory, "any_body")) == "STORAGE_VENT"
    assert _entry(memory, "own_fresh_kill").type == "move"


def test_an_own_victim_whose_body_is_not_here_is_not_this_body() -> None:
    memory = _entry_memory(own_kill=(VICTIM, "STORAGE"), body=(OTHER_CREW, "STORAGE"))
    assert _vent(_entry(memory, "any_body")) == "STORAGE_VENT"
    assert _entry(memory, "own_fresh_kill").type == "move"


@pytest.mark.parametrize(
    "payload",
    [{"room": "STORAGE"}, {"victim_id": VICTIM}, {"victim_id": 7, "room": "STORAGE"}],
)
def test_a_malformed_own_kill_row_raises(payload: dict[str, Any]) -> None:
    memory = _entry_memory(own_kill=None)
    _row(memory, 11, "own_kill", **payload)
    with pytest.raises(ValueError, match="own_kill event missing") as raised:
        _entry(memory, "own_fresh_kill")
    assert repr(payload)[1:-1] in str(raised.value)


def test_an_event_time_own_kill_row_is_refused() -> None:
    # The temporal path dates the row at the kill's own tick; the gate reads
    # snapshot rows only and refuses rather than misdate the kill.
    memory = MemoryStore()
    _tick(memory, tick=10, room="STORAGE", in_vent=False, cooldown=0)
    ingest_event_observations(
        batch=EventObservationBatch(
            tick=10,
            agent_id=ME,
            own_kill=OwnKillView(victim_id=VICTIM, room="STORAGE"),
        ),
        memory=memory,
    )
    _tick(
        memory,
        tick=11,
        room="STORAGE",
        in_vent=False,
        cooldown=4,
        bodies=((VICTIM, "STORAGE"),),
    )
    assert _vent(_entry(memory, "any_body")) == "STORAGE_VENT"
    with pytest.raises(ValueError, match="event-time row"):
        _entry(memory, "own_fresh_kill")


@dataclass(frozen=True)
class _EngineKill:
    """A kill run through the engine, the observation service and perception."""

    kill_tick: int
    memories: Mapping[int, MemoryStore]
    impostor: str


def _engine_kill(tmp_path: Path, *, ticks_after: int) -> _EngineKill:
    """The impostor kills alone in STORAGE, then everyone waits.

    Returns the impostor's memory as it stands at each observation tick after the
    kill, built by the real observation service and perception from engine
    states, never from hand-typed row ticks.
    """

    state = seed_initial_state(
        seed=3, game_map=ENGINE_MAP, num_players=5, num_impostors=1
    )
    impostor = next(pid for pid, p in state.players.items() if p.role == "IMPOSTOR")
    victim = next(pid for pid in sorted(state.players) if pid != impostor)
    players = {
        pid: replace(
            player,
            room="STORAGE" if pid in (impostor, victim) else "CAFETERIA",
        )
        for pid, player in state.players.items()
    }
    state = replace(state, players=players, cooldowns={impostor: 0})
    service = ObservationService(
        game_map=ENGINE_MAP, audit_log_path=tmp_path / "audit.jsonl"
    )
    memory = MemoryStore()
    ingest_packet(
        packet=service.build_packet(
            world_state=state, agent_id=impostor, engine_events=()
        ),
        memory=memory,
    )
    kill_tick = state.tick
    actions: list[Action] = [
        KillAction.model_validate(
            {"type": "kill", "actor": impostor, "payload": {"target": victim}}
        ),
        *(
            WaitAction.model_validate({"type": "wait", "actor": pid, "payload": {}})
            for pid in sorted(state.players)
            if pid not in (impostor, victim)
        ),
    ]
    memories: dict[int, MemoryStore] = {}
    for _ in range(ticks_after):
        state, events = advance_tick(state, actions, game_map=ENGINE_MAP)
        ingest_packet(
            packet=service.build_packet(
                world_state=state, agent_id=impostor, engine_events=events
            ),
            memory=memory,
        )
        snapshot = MemoryStore()
        for event in memory.recent(since_tick=0):
            snapshot.append(event)
        memories[state.tick] = snapshot
        actions = [
            WaitAction.model_validate({"type": "wait", "actor": pid, "payload": {}})
            for pid, player in sorted(state.players.items())
            if player.alive
        ]
    service.close()
    return _EngineKill(kill_tick=kill_tick, memories=memories, impostor=impostor)


def test_the_fresh_kill_window_counts_from_the_engines_kill_tick(
    tmp_path: Path,
) -> None:
    run = _engine_kill(tmp_path, ticks_after=FRESH_KILL_WINDOW_TICKS + 1)
    policy = ExperimentalImpostorPolicy(
        agent_id=run.impostor,
        options=TacticalExperimentOptions(vent_entry_policy="own_fresh_kill"),
    )
    anchor = ExperimentalImpostorPolicy(
        agent_id=run.impostor, options=TacticalExperimentOptions()
    )
    for entry_tick, memory in sorted(run.memories.items()):
        # An entry decided at this observation tick resolves at this engine tick.
        age = entry_tick - run.kill_tick
        assert _vent(anchor.decide(memory, MAP)) == "STORAGE_VENT"
        decided = policy.decide(memory, MAP)
        if age <= FRESH_KILL_WINDOW_TICKS:
            assert _vent(decided) == "STORAGE_VENT", age
        else:
            assert decided.type == "move", age
    assert max(run.memories) - run.kill_tick == FRESH_KILL_WINDOW_TICKS + 1


def test_the_policys_window_and_cap_are_the_censuss() -> None:
    assert FRESH_KILL_WINDOW_TICKS == census.FRESH_KILL_WINDOW_TICKS == 3
    assert IN_VENT_CAP_TICKS == census.IN_VENT_CAP_TICKS == 4
    assert experimental._MEETING_BOUNDARY_EVENT == _EVENT_MEETING_BOUNDARY


# --------------------------------------------------------------------------- #
# Refusals                                                                     #
# --------------------------------------------------------------------------- #


def test_an_in_vent_memory_without_a_cooldown_reading_raises() -> None:
    memory = MemoryStore()
    _tick(memory, tick=20, room="STORAGE", in_vent=False)
    _row(
        memory,
        21,
        "self_state",
        agent_id=ME,
        room="STORAGE",
        role="IMPOSTOR",
        fellow_impostor_ids=(TEAMMATE,),
        in_vent=True,
    )
    with pytest.raises(ValueError, match="cooldown_status"):
        _policy().decide(memory, MAP)


def test_an_in_vent_impostor_in_a_room_with_no_vent_raises() -> None:
    memory = _inside("CAFETERIA")
    with pytest.raises(ValueError, match="no vent maps to its room: 'CAFETERIA'"):
        _policy().decide(memory, MAP)


def test_a_connected_vent_with_no_room_raises() -> None:
    broken = MAP.model_copy(
        update={
            "vent_graph": {
                **MAP.vent_graph,
                "STORAGE_VENT": (*MAP.vent_graph["STORAGE_VENT"], "GHOST_VENT"),
            }
        }
    )
    with pytest.raises(ValueError, match="GHOST_VENT"):
        _policy().decide(_inside("STORAGE"), broken)


def test_memory_the_anchor_refuses_is_refused() -> None:
    with pytest.raises(ValueError, match="at least one episodic event"):
        _policy().decide(MemoryStore(), MAP)


def test_both_values_build_a_policy_now() -> None:
    assert experimental.UNBUILT_OPTION_VALUES == {}
    for options in (
        TacticalExperimentOptions(vent_exit_policy="look_and_wait"),
        TacticalExperimentOptions(vent_entry_policy="own_fresh_kill"),
    ):
        assert ExperimentalImpostorPolicy(agent_id=ME, options=options)


# --------------------------------------------------------------------------- #
# Never stuck, and deterministic                                               #
# --------------------------------------------------------------------------- #

_VENT_ROOMS: tuple[str, ...] = tuple(sorted(set(MAP.vent_rooms.values())))
_ROOMS: tuple[str, ...] = MAP.room_ids
_PLAYERS: tuple[str, ...] = (TEAMMATE, "p-3", "p-4", CREW, OTHER_CREW, VICTIM)
_SABOTAGES: tuple[Sabotage, ...] = (None, "reactor", "lights")


@st.composite
def _in_vent_memories(draw: st.DrawFn) -> tuple[MemoryStore, str, int]:
    room = draw(st.sampled_from(_VENT_ROOMS))
    streak = draw(st.integers(min_value=1, max_value=6))
    boundary = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=streak)))
    memory = MemoryStore()
    _tick(memory, tick=10, room=room, in_vent=False)
    for tick in range(11, 11 + streak):
        if boundary is not None and tick == 11 + streak - boundary:
            _boundary(memory, tick)
        seen = draw(
            st.lists(
                st.tuples(st.sampled_from(_PLAYERS), st.sampled_from(_ROOMS)),
                max_size=4,
                unique_by=lambda pair: pair[0],
            )
        )
        bodies = draw(
            st.lists(
                st.tuples(st.sampled_from(("p-8", "p-9")), st.sampled_from(_ROOMS)),
                max_size=2,
                unique_by=lambda pair: pair[0],
            )
        )
        sabotage: Sabotage = draw(st.sampled_from(_SABOTAGES))
        _tick(
            memory,
            tick=tick,
            room=room,
            in_vent=True,
            seen=seen,
            bodies=bodies,
            sabotage=sabotage,
        )
    inside = streak if boundary is None else boundary
    return memory, room, inside


def _permuted(public_map: PublicMapView, rotate: int) -> PublicMapView:
    def turn(values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            return values
        shift = rotate % len(values)
        return tuple(reversed(values[shift:] + values[:shift]))

    return public_map.model_copy(
        update={
            "room_neighbors": {
                room: turn(tuple(values))
                for room, values in reversed(list(public_map.room_neighbors.items()))
            },
            "vent_graph": {
                vent: turn(tuple(values))
                for vent, values in reversed(list(public_map.vent_graph.items()))
            },
        }
    )


def _check_never_stuck(
    memory: MemoryStore, room: str, inside: int, rotate: int
) -> None:
    """The universal guarantees, each computed here from the memory alone."""

    events = memory.recent(since_tick=0)
    latest = [event for event in events if event.tick == events[-1].tick]
    sabotage = next(
        event.payload["sabotage_active"]
        for event in reversed(events)
        if event.type == "global_status"
    )
    sight = inferred_visible_rooms(MAP, room, sabotage_active=sabotage)
    watched = any(
        event.type == "saw_player"
        and event.payload["player_id"] not in (ME, TEAMMATE)
        and event.payload["room"] in sight
        for event in latest
    )
    policy = _policy()
    intent = policy.decide(memory, MAP)
    assert intent.type in ("vent", "wait")
    if inside >= IN_VENT_CAP_TICKS:
        assert intent.type == "vent"
    else:
        # Before the cap it surfaces exactly when nobody but a teammate is in
        # sight, and never into a room it cannot see.
        assert (intent.type == "vent") == (not watched)
    if intent.type == "vent":
        current = next(v for v, r in MAP.vent_rooms.items() if r == room)
        assert intent.payload.vent_id in (current, *MAP.vent_graph[current])
        if inside < IN_VENT_CAP_TICKS:
            assert MAP.vent_rooms[intent.payload.vent_id] in sight
    assert policy.decide(memory, MAP) == intent
    assert _policy().decide(memory, _permuted(MAP, rotate)) == intent


@settings(deadline=None, max_examples=300)
@given(case=_in_vent_memories(), rotate=st.integers(min_value=0, max_value=5))
def test_it_is_never_stuck_and_always_deterministic(
    case: tuple[MemoryStore, str, int], rotate: int
) -> None:
    memory, room, inside = case
    _check_never_stuck(memory, room, inside, rotate)


def test_a_policy_without_the_cap_fails_the_property(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Perturbed: the cap check removed (a cap no count reaches)."""

    memory = _inside("STORAGE", inside=IN_VENT_CAP_TICKS, seen=((CREW, "ENGINEERING"),))
    _check_never_stuck(memory, "STORAGE", IN_VENT_CAP_TICKS, 0)
    monkeypatch.setattr(experimental, "IN_VENT_CAP_TICKS", 10**9)
    with pytest.raises(AssertionError):
        _check_never_stuck(memory, "STORAGE", IN_VENT_CAP_TICKS, 0)
