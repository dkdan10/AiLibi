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
import hypothesis
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


def test_before_the_cap_the_pick_follows_the_loaded_map() -> None:
    # From H on the two-link map, VA, VB and VH2 are visible and clear and VC's
    # room is unseen. The room fled (H, also VH2's) loses, then the vent id
    # takes VA. No canonical vent or room appears here.
    two_links = _two_link_map()
    clear = _custom_inside(inside=1, seen=())
    assert _vent(_policy().decide(clear, two_links)) == "VA"
    # A body in A, VA's room on this map, moves the pick to VB.
    body_in_a = _custom_inside(inside=1, seen=(), bodies=(("p-8", "A"),))
    assert _vent(_policy().decide(body_in_a, two_links)) == "VB"
    # With VA moved to the unseen C, VA is no candidate before the cap: VB.
    moved = two_links.model_copy(
        update={"vent_rooms": {**two_links.vent_rooms, "VA": "C"}}
    )
    assert _vent(_policy().decide(clear, moved)) == "VB"


# --------------------------------------------------------------------------- #
# Only this tick's bodies                                                      #
# --------------------------------------------------------------------------- #


def _after_a_report(
    room: str,
    *,
    inside: int,
    reported: str,
    now: tuple[tuple[str, str], ...],
    seen: tuple[tuple[str, str], ...] = (),
) -> MemoryStore:
    """A body seen in ``reported`` before a meeting, reported at that meeting.

    The engine hides a reported body, so after the boundary its ``saw_body``
    rows remain only at earlier ticks. The impostor stays inside through the
    meeting (no regroup), and ``inside`` rows follow the boundary, each seeing
    the bodies in ``now``; the last also carries ``seen``.
    """

    memory = MemoryStore()
    before = ((VICTIM, reported),)
    _tick(memory, tick=20, room=room, in_vent=False, bodies=before)
    _tick(memory, tick=21, room=room, in_vent=True, bodies=before)
    _boundary(memory, 22)
    for tick in range(22, 22 + inside):
        last = tick == 21 + inside
        _tick(
            memory,
            tick=tick,
            room=room,
            in_vent=True,
            bodies=now,
            seen=seen if last else (),
        )
    return memory


@pytest.mark.parametrize(
    ("room", "inside", "reported", "now", "seen", "chosen", "if_still_seen"),
    [
        pytest.param(
            "STORAGE",
            1,
            "STORAGE",
            ((OTHER_CREW, "ENGINEERING"),),
            (),
            "STORAGE_VENT",
            "ENGINEERING_VENT",
            id="before-the-cap-own-room-reported",
        ),
        pytest.param(
            "STORAGE",
            1,
            "ENGINEERING",
            (),
            (),
            "ENGINEERING_VENT",
            "STORAGE_VENT",
            id="before-the-cap-connected-room-reported",
        ),
        pytest.param(
            "ENGINEERING",
            IN_VENT_CAP_TICKS,
            "STORAGE",
            (),
            ((CREW, "EAST_HALL"),),
            "STORAGE_VENT",
            "ENGINEERING_VENT",
            id="at-the-cap-connected-room-reported",
        ),
        pytest.param(
            "ENGINEERING",
            IN_VENT_CAP_TICKS,
            "ENGINEERING",
            ((OTHER_CREW, "STORAGE"),),
            ((CREW, "EAST_HALL"),),
            "ENGINEERING_VENT",
            "STORAGE_VENT",
            id="at-the-cap-own-room-reported",
        ),
    ],
)
def test_a_body_seen_only_before_this_tick_is_not_in_the_exit_key(
    room: str,
    inside: int,
    reported: str,
    now: tuple[tuple[str, str], ...],
    seen: tuple[tuple[str, str], ...],
    chosen: str,
    if_still_seen: str,
) -> None:
    memory = _after_a_report(room, inside=inside, reported=reported, now=now, seen=seen)
    assert ExperimentalImpostorPolicy._ticks_inside(memory.recent(since_tick=0)) == (
        inside
    )
    if inside >= IN_VENT_CAP_TICKS:
        # A crewmate in EAST_HALL is in view, so only the cap key surfaces it.
        early = _after_a_report(room, inside=1, reported=reported, now=now, seen=seen)
        assert _policy().decide(early, MAP).type == "wait"
    assert _vent(_policy().decide(memory, MAP)) == chosen
    # The same memory with the reported body still in view this tick picks the
    # other vent, so the earlier rows would change the pick if they were read.
    still = _after_a_report(
        room,
        inside=inside,
        reported=reported,
        now=(*now, (VICTIM, reported)),
        seen=seen,
    )
    assert _vent(_policy().decide(still, MAP)) == if_still_seen


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


_ENTRY_POLICIES: tuple[EntryPolicy, ...] = ("any_body", "own_fresh_kill")


def test_self_report_runs_before_the_entry_gate() -> None:
    # A teammate's victim and no witness: the gate alone walks away, and with
    # self_report on the impostor reports first whether or not the gate is on.
    memory = _entry_memory(own_kill=None)
    assert _entry(memory, "own_fresh_kill").type == "move"
    reported = [
        ExperimentalImpostorPolicy(
            agent_id=ME,
            options=TacticalExperimentOptions(
                self_report=True, vent_entry_policy=entry_policy
            ),
        ).decide(memory, MAP)
        for entry_policy in _ENTRY_POLICIES
    ]
    assert reported[0] == reported[1]
    assert reported[1].type == "report"
    assert reported[1].payload.body_id == f"body-{VICTIM}"


def test_the_entry_gate_allows_one_re_entry_per_kill_after_an_in_place_exit() -> None:
    # A kill in REACTOR at engine tick 10, perceived at 11. REACTOR sees neither
    # connected vent's room, so each trip surfaces in place beside the body.
    # Under the gate it enters at 11 and again at 13 (kill age 3), then walks
    # away at 15 (age 5); under any_body it would enter again at 15.
    body = ((VICTIM, "REACTOR"),)
    memory = MemoryStore()
    _tick(memory, tick=10, room="REACTOR", in_vent=False, cooldown=0)
    gated = _policy("look_and_wait", "own_fresh_kill")
    intents: list[ActionIntent] = []
    for tick, in_vent, cooldown in ((11, False, 4), (12, True, 3), (13, False, 2)):
        _tick(
            memory,
            tick=tick,
            room="REACTOR",
            in_vent=in_vent,
            cooldown=cooldown,
            own_kill=(VICTIM, "REACTOR") if tick == 11 else None,
            bodies=body,
        )
        intents.append(gated.decide(memory, MAP))
    for tick, in_vent, cooldown in ((14, True, 1), (15, False, 0)):
        _tick(
            memory,
            tick=tick,
            room="REACTOR",
            in_vent=in_vent,
            cooldown=cooldown,
            bodies=body,
        )
        intents.append(gated.decide(memory, MAP))
    assert [_vent(intent) for intent in intents[:4]] == ["REACTOR_VENT"] * 4
    assert intents[4] == ImpostorPolicy(agent_id=ME)._cover(
        public_map=MAP, own_room="REACTOR"
    )
    assert _vent(_policy("look_and_wait", "any_body").decide(memory, MAP)) == (
        "REACTOR_VENT"
    )


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


@pytest.mark.parametrize("ghost_is_a_graph_key", [False, True])
def test_a_connected_vent_with_no_room_raises(ghost_is_a_graph_key: bool) -> None:
    graph = {
        **MAP.vent_graph,
        "STORAGE_VENT": (*MAP.vent_graph["STORAGE_VENT"], "GHOST_VENT"),
    }
    if ghost_is_a_graph_key:
        # Listed with links of its own, the vent still has no room.
        graph["GHOST_VENT"] = ("STORAGE_VENT",)
    broken = MAP.model_copy(update={"vent_graph": graph})
    with pytest.raises(ValueError, match="GHOST_VENT"):
        _policy().decide(_inside("STORAGE"), broken)


def test_memory_the_anchor_refuses_is_refused() -> None:
    with pytest.raises(ValueError, match="at least one episodic event"):
        _policy().decide(MemoryStore(), MAP)


def _rebuilt(rows: Iterable[EpisodicEvent]) -> MemoryStore:
    memory = MemoryStore()
    for row in rows:
        memory.append(row)
    return memory


def _edited(
    memory: MemoryStore, *, kind: str, tick: int | None, **changes: object
) -> MemoryStore:
    """``memory`` with the last ``kind`` row (at ``tick`` if given) edited.

    A change whose value is ``_ABSENT`` deletes that key.
    """

    rows = list(memory.recent(since_tick=0))
    index = max(
        position
        for position, row in enumerate(rows)
        if row.type == kind and (tick is None or row.tick == tick)
    )
    payload = {**rows[index].payload, **changes}
    rows[index] = replace(
        rows[index],
        payload={key: value for key, value in payload.items() if value is not _ABSENT},
    )
    return _rebuilt(rows)


def _with_row(
    memory: MemoryStore, *, at: int, kind: str, provenance: str, **payload: object
) -> MemoryStore:
    """``memory`` with one row inserted before position ``at``, at its tick."""

    rows = list(memory.recent(since_tick=0))
    tick = rows[at - 1].tick
    rows.insert(
        at, EpisodicEvent(tick=tick, type=kind, provenance=provenance, payload=payload)
    )
    return _rebuilt(rows)


_ABSENT = object()


def _planted_malformed(kind: str) -> MemoryStore:
    """An in-vent memory with one row that only the anchor's row checks meet.

    Each row is one the anchor refuses before its in-vent exit and that the
    look's own reads never touch: an earlier tick, a pending task, or a
    sighting that is not first-hand.
    """

    base = _inside("STORAGE", inside=2)
    if kind == "pending task":
        return _edited(base, kind="self_state", tick=None, pending_task_id=5)
    if kind == "earlier self_state room":
        return _edited(base, kind="self_state", tick=20, room=7)
    if kind == "earlier saw_body victim":
        return _with_row(
            base,
            at=1,
            kind="saw_body",
            provenance="observed",
            body_id="b",
            room="ADMIN",
        )
    if kind == "earlier saw_player subject":
        return _with_row(
            base,
            at=1,
            kind="saw_player",
            provenance="observed",
            player_id=5,
            room="ADMIN",
            action=None,
        )
    if kind == "earlier saw_player room":
        return _with_row(
            base,
            at=1,
            kind="saw_player",
            provenance="observed",
            player_id=CREW,
            action=None,
        )
    assert kind == "reported saw_player room this tick"
    return _with_row(
        base,
        at=len(base.recent(since_tick=0)),
        kind="saw_player",
        provenance="reported",
        player_id=CREW,
        action=None,
    )


_PLANTED_KINDS: tuple[tuple[str, str], ...] = (
    ("pending task", "non-string pending_task_id"),
    ("earlier self_state room", "self_state event missing string 'room' field"),
    ("earlier saw_body victim", "saw_body event missing string 'victim_id'"),
    ("earlier saw_player subject", "saw_player event missing string 'player_id'"),
    ("earlier saw_player room", "saw_player event missing string 'room'"),
    ("reported saw_player room this tick", "saw_player event missing string 'room'"),
)


@pytest.mark.parametrize(("kind", "message"), _PLANTED_KINDS)
def test_a_row_the_anchor_refuses_is_refused_inside_a_vent(
    kind: str, message: str
) -> None:
    memory = _planted_malformed(kind)
    with pytest.raises(ValueError, match=message) as anchor:
        ImpostorPolicy(agent_id=ME).decide(memory, MAP)
    with pytest.raises(ValueError) as look:
        _policy().decide(memory, MAP)
    assert str(look.value) == str(anchor.value)


def _check_refused_like_the_anchor(memory: MemoryStore) -> None:
    """The anchor refuses ``memory`` and the look refuses it with the same message."""

    with pytest.raises(ValueError) as anchor:
        ImpostorPolicy(agent_id=ME).decide(memory, MAP)
    with pytest.raises(ValueError) as look:
        _policy().decide(memory, MAP)
    assert str(look.value) == str(anchor.value)


@pytest.mark.parametrize("kind", [kind for kind, _ in _PLANTED_KINDS])
def test_without_the_row_checks_each_planted_row_fails_the_check(
    kind: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Perturbed: with the anchor's row checks removed, the look decides."""

    def accept(events: tuple[EpisodicEvent, ...], *, state: EpisodicEvent) -> None:
        return None

    memory = _planted_malformed(kind)
    _check_refused_like_the_anchor(memory)
    monkeypatch.setattr(
        ExperimentalImpostorPolicy,
        "_refuse_rows_the_anchor_refuses",
        staticmethod(accept),
    )
    assert _policy().decide(memory, MAP).type in ("vent", "wait")
    with pytest.raises(pytest.fail.Exception, match="DID NOT RAISE"):
        _check_refused_like_the_anchor(memory)


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


# --------------------------------------------------------------------------- #
# Every row the anchor refuses in a vent is refused by the look                #
# --------------------------------------------------------------------------- #

#: Every way ``ImpostorPolicy.decide`` refuses an in-vent memory with a
#: self_state before it returns its exit: each names one malformed row.
_ANCHOR_REFUSALS: tuple[str, ...] = (
    "pending task",
    "self_state room",
    "fellow ids",
    "in_vent flag",
    "no cooldown row",
    "cooldown value",
    "body room this tick",
    "body victim",
    "sighting subject",
    "sighting room",
    "room with no vent",
)


@st.composite
def _anchor_refused_memories(draw: st.DrawFn) -> tuple[MemoryStore, str]:
    """An in-vent memory from the never-stuck family with one malformed row."""

    base, _, _ = draw(_in_vent_memories())
    rows = list(base.recent(since_tick=0))
    latest = rows[-1].tick
    refusal = draw(st.sampled_from(_ANCHOR_REFUSALS))
    if refusal == "pending task":
        memory = _edited(
            base,
            kind="self_state",
            tick=None,
            pending_task_id=draw(st.sampled_from((5, ("task-1",)))),
        )
    elif refusal == "self_state room":
        tick = draw(
            st.sampled_from(
                sorted({row.tick for row in rows if row.type == "self_state"})
            )
        )
        memory = _edited(
            base, kind="self_state", tick=tick, room=draw(st.sampled_from((7, _ABSENT)))
        )
    elif refusal == "fellow ids":
        memory = _edited(
            base,
            kind="self_state",
            tick=None,
            fellow_impostor_ids=draw(st.sampled_from(("p-2", (2,), 5))),
        )
    elif refusal == "in_vent flag":
        memory = _edited(
            base,
            kind="self_state",
            tick=None,
            in_vent=draw(st.sampled_from(("yes", 1))),
        )
    elif refusal == "no cooldown row":
        memory = _rebuilt(
            row
            for row in rows
            if not (row.type == "cooldown_status" and row.tick == latest)
        )
    elif refusal == "cooldown value":
        memory = _edited(
            base,
            kind="cooldown_status",
            tick=latest,
            cooldown=draw(st.sampled_from(("3", None, 2.5))),
        )
    elif refusal == "body room this tick":
        memory = _with_row(
            base,
            at=len(rows),
            kind="saw_body",
            provenance="observed",
            body_id="body-p-9",
            victim_id="p-9",
            **({} if draw(st.booleans()) else {"room": 3}),
        )
    elif refusal in ("body victim", "sighting subject", "sighting room"):
        at = draw(st.integers(min_value=1, max_value=len(rows)))
        bad = draw(st.sampled_from((_ABSENT, 5)))
        room = draw(st.sampled_from(_ROOMS))
        if refusal == "body victim":
            payload: dict[str, object] = {
                "body_id": "b",
                "room": room,
                "victim_id": bad,
            }
            kind = "saw_body"
        elif refusal == "sighting subject":
            payload = {"player_id": bad, "room": room, "action": None}
            kind = "saw_player"
        else:
            payload = {"player_id": CREW, "room": bad, "action": None}
            kind = "saw_player"
        memory = _with_row(
            base,
            at=at,
            kind=kind,
            provenance=draw(st.sampled_from(("observed", "reported", "inferred"))),
            **{key: value for key, value in payload.items() if value is not _ABSENT},
        )
    else:
        assert refusal == "room with no vent"
        memory = _edited(
            base,
            kind="self_state",
            tick=None,
            room=draw(
                st.sampled_from(
                    tuple(
                        room for room in _ROOMS if room not in MAP.vent_rooms.values()
                    )
                )
            ),
        )
    return memory, refusal


@settings(deadline=None, max_examples=300)
@given(case=_anchor_refused_memories())
def test_every_row_the_anchor_refuses_in_a_vent_is_refused_by_the_look(
    case: tuple[MemoryStore, str],
) -> None:
    memory, refusal = case
    hypothesis.event(refusal)
    _check_refused_like_the_anchor(memory)
