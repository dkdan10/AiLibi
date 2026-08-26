"""Property-based observation-purity sweep (DESIGN.md §11.2, audit I-I-2).

DESIGN.md §11.2 calls the leak test "the most important test" and mandates a
many-seeds / property-based purity sweep. The fixture-driven check in
``eval/leak_test.py`` walks exactly three hand-authored scripted games, so a
leak that only manifests under an unseen packet shape would slip through
(audit I-I-2). This module closes that gap: it drives ``ObservationService``
over every living agent on every tick across many Hypothesis-generated games
and feeds each packet through the EXISTING scanners from ``eval/leak_scan.py``
(the pytest-free scanner library the leak suite and the ML champion gate share
since Task 19.24).

The scanners are imported, not reimplemented -- the value here is breadth of
inputs. Task 7.2 parametrizes the sweep over ``num_impostors`` and asserts the
crew-empty firewall invariant -- ``self_state.fellow_impostor_ids == ()`` for
every crewmate-recipient packet -- inside the per-packet loop. Task 8.6 widens
the roster to the canonical **9 players** at **2 and 3** impostors (the 2-of-9
substrate, DESIGN.md §3.5) and deals every player a per-player task instance so
the loop also sweeps ``SelfView.pending_task_id`` under the new
``"{owner}:{map_task_id}"`` keyspace (DESIGN.md §3.2) -- the old ``tasks={}``
roster never exercised it. This is the project's strongest leak test guarding
the self-channel fields beyond ``role``: the generic scanners cannot catch a
crewmate erroneously receiving a teammate id or another owner's task
(role-neutral ids like ``p-2`` and bare map ids like ``swipe_card`` do not trip
the value scanner, and neither field name is in the recursive scanner's set),
and the single-impostor scripted fixtures cannot surface a crew-tuple misroute
(every impostor's tuple is also empty there), so a multi-impostor roster is
required to exercise it. Single-impostor coverage stays with the 4p/1i scripted
fixtures in ``eval/leak_test.py``.

The base sweep and the movement sweep also ask the ENTITLEMENT question: not "is
this packet shaped right" but "was this observer allowed to SEE these players and
these bodies", re-derived from ``WorldState`` by
``eval.leak_scan.assert_visible_entities_match_engine_truth``. Four engine rules
decide the answer, and the hand-built observer-class legs at the end of this
module pin each one because a random sweep states them only implicitly: a
CREWMATE sees its own room, an IMPOSTOR its room and the map neighbours, a VENTED
observer keeps the room set its role and position would give it either way --
venting hides you FROM others, it does not blind you -- and a DEAD observer is
entitled to nothing at all.

The action vocabulary mirrors the role-aware strategy from
``tests/engine/test_tick_properties.py`` but is generalized off that module's
single-impostor roster so the sweep exercises kills, vents, and reports across
the whole multi-impostor roster -- the events that populate ``visible_players``
/ ``visible_bodies`` / ``audible_events`` where a leak would surface. Task 19.24
adds a third vocabulary that MOVES players, because none of the earlier ones
did: ``moved_players`` scanned vacuously (always empty) until packets carried
transitions, and that channel's witness gate is the one the audits flagged as
uncovered.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import cast

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import (
    BodyState,
    PlayerId,
    PlayerState,
    SabotageState,
    TaskId,
    TaskState,
)
from engine.events import (
    ActionRejectedEvent,
    KilledEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
)
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.visibility import compute_visibility_for_player
from engine.world import Map, WorldState, load_canonical_map
from eval.leak_scan import (
    _FORBIDDEN_VISIBLE_PLAYER_ACTIONS,
    JsonValue,
    _action_is_permitted_by_witness_event,
    _assert_no_recursive_hidden_fields,
    _assert_no_role_bearing_values,
    _walk_json,
    assert_moved_players_are_witness_gated,
    assert_visible_entities_match_engine_truth,
)
from observation.packet import BodyView, PlayerView
from observation.service import ObservationService, impostor_pretend_task_id
from tests.engine.test_tick_properties import _unique_actions_per_actor

# Every canonical map task id, so the do_task sweep below draws a mix of the
# actor's OWN task (resolves -> TaskProgressed/TaskCompleted) and a FOREIGN one
# (rejected -> ActionRejected[do_task]); both must stamp ``action="task"``
# identically, exercising the role-blind fake-task lever (Task 13.9).
_ROSTER_MAP_TASK_IDS = tuple(sorted(load_canonical_map().tasks))

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# Canonical nine-player roster (p-1 .. p-9) -- the 9p/2i substrate (DESIGN.md
# §3.5, §8.1). The valid impostor counts keep crewmates in the majority at game
# start -- impostor parity is an immediate win (engine/win_conditions.py) -- so
# both 2 and 3 impostors begin in a non-terminal PLAY state (9p/2i parity is 5
# crew deaths; impostors are never valid kill targets so they never die here).
# The first ``num_impostors`` ids are the impostors. Single-impostor leak
# coverage stays with the 4p/1i scripted fixtures in ``eval/leak_test.py``; this
# sweep guards the multi-impostor crew-misroute that those cannot reach.
_ROSTER_PLAYER_IDS = tuple(f"p-{index}" for index in range(1, 10))
_VALID_IMPOSTOR_COUNTS = (2, 3)

# Canonical_1 vent ids and a mix of plausible / missing body ids, mirroring
# ``tests/engine/test_tick_properties.py``. The engine rejects role-invalid,
# dead-actor, unknown-vent, and missing-body attempts via ``ActionRejectedEvent``
# (never an exception), so any drawn action is safe to feed to ``advance_tick``.
_ROSTER_VENT_IDS = (
    "REACTOR_VENT",
    "STORAGE_VENT",
    "ENGINEERING_VENT",
    "ADMIN_VENT",
    "MEDBAY_VENT",
    "LABS_VENT",
)
_ROSTER_BODY_ID_DRAWS = ("body-p-1-0", "body-p-2-0", "missing-body")


def _roster_task_assignment(game_map: Map) -> dict[PlayerId, TaskId]:
    """Deal each roster player one DISTINCT canonical map task (DESIGN.md §3.2).

    The own-task-only invariant is sharpest when every player owns a *different*
    map id: if ``ObservationService._pending_task_id_for_agent`` ever dropped its
    ``owner`` filter it would surface a FOREIGN map id (the global
    lexicographic-min owned task), which the per-packet assertion in the sweep
    catches. Overlap (two crewmates holding the same map task) would instead hide
    such a misroute behind an identical value, so distinct ids are the stronger
    fixture -- the same rationale as
    ``test_service.py::test_multi_impostor_packets_carry_no_foreign_task_ownership``.

    The deal is a pure function of the map (a deterministic ``sorted`` slice), so
    it adds no nondeterminism to the replay-able sweep. The 12-task canonical map
    comfortably covers the 9-player roster.
    """

    map_task_ids = sorted(game_map.tasks)
    if len(map_task_ids) < len(_ROSTER_PLAYER_IDS):
        raise AssertionError(
            "canonical_1 must define at least one map task per roster player "
            f"({len(_ROSTER_PLAYER_IDS)} needed, {len(map_task_ids)} available)"
        )
    return dict(zip(_ROSTER_PLAYER_IDS, map_task_ids))


def _roster_initial_state(
    *, seed: int, num_impostors: int, game_map: Map
) -> WorldState:
    """Build a 9-player ``PLAY`` state with ``num_impostors`` impostors.

    The first ``num_impostors`` ids are impostors; the rest are crewmates.
    Everyone spawns in CAFETERIA. Each player owns ONE distinct per-player task
    *instance* keyed ``"{owner}:{map_task_id}"`` (DESIGN.md §3.2) -- replacing the
    old ``tasks={}`` -- so the sweep exercises ``SelfView.pending_task_id`` under
    the per-player keyspace. The sweep issues no ``do_task`` (its vocabulary is
    kill/vent/report/wait), so no instance ever progresses or completes and the
    win check only ends on impostor parity (guarded by the crew majority); the
    game runs until the drawn action batches drive it out of ``PLAY``.
    Generalizes ``test_tick_properties._initial_state`` off its single-impostor,
    task-less roster so the sweep can exercise multi-impostor games with tasks.
    """

    impostor_ids = set(_ROSTER_PLAYER_IDS[:num_impostors])
    players = {
        player_id: PlayerState(
            id=player_id,
            role="IMPOSTOR" if player_id in impostor_ids else "CREWMATE",
            alive=True,
            room="CAFETERIA",
            position=(0.0, 0.0),
            last_action=None,
            in_vent=False,
        )
        for player_id in _ROSTER_PLAYER_IDS
    }
    tasks = {
        f"{owner}:{map_task_id}": TaskState(
            id=f"{owner}:{map_task_id}",
            owner=owner,
            map_task_id=map_task_id,
            room=game_map.tasks[map_task_id].room,
            progress=0,
            required_ticks=game_map.tasks[map_task_id].duration_ticks,
            completed=False,
        )
        for owner, map_task_id in _roster_task_assignment(game_map).items()
    }
    return WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players=players,
        bodies={},
        tasks=tasks,
        sabotage=None,
        cooldowns={impostor_id: 0 for impostor_id in impostor_ids},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


@st.composite
def _roster_action(draw: st.DrawFn) -> Action:
    """Draw a role-aware kill / vent / report / wait action over the full
    9-player roster. Actor and kill target are drawn from the whole roster; the
    engine rejects role-invalid or dead attempts, so kills land only when the
    drawn actor is a living impostor -- exactly the multi-impostor coverage this
    sweep adds over the single-impostor engine strategy.
    """

    kind = draw(st.sampled_from(("kill", "vent", "report", "wait")))
    actor = draw(st.sampled_from(_ROSTER_PLAYER_IDS))
    if kind == "kill":
        # ``KillAction`` rejects a self-target at construction, so draw the
        # target from the roster minus the actor (8 ids, always non-empty).
        target = draw(
            st.sampled_from(tuple(pid for pid in _ROSTER_PLAYER_IDS if pid != actor))
        )
        return _ACTION_ADAPTER.validate_python(
            {"type": "kill", "actor": actor, "payload": {"target": target}}
        )
    if kind == "vent":
        vent_id = draw(st.sampled_from(_ROSTER_VENT_IDS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "vent", "actor": actor, "payload": {"vent_id": vent_id}}
        )
    if kind == "report":
        body_id = draw(st.sampled_from(_ROSTER_BODY_ID_DRAWS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "report", "actor": actor, "payload": {"body_id": body_id}}
        )
    return _ACTION_ADAPTER.validate_python(
        {"type": "wait", "actor": actor, "payload": {}}
    )


@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    num_impostors=st.sampled_from(_VALID_IMPOSTOR_COUNTS),
    action_batches=st.lists(st.lists(_roster_action(), max_size=3), max_size=10),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_observation_packets_never_leak_hidden_information(
    seed: int,
    num_impostors: int,
    action_batches: list[list[Action]],
    tmp_path: Path,
) -> None:
    """No packet for any living agent on any tick leaks hidden information, no
    crewmate-recipient packet ever carries a non-empty ``fellow_impostor_ids``,
    and every recipient sees only its OWN per-player task -- across many seeds and
    2/3-impostor rosters on the 9-player substrate.

    Runs ``ObservationService`` exactly as the orchestrator does -- one packet
    per living agent per tick -- and applies the imported leak scanners plus the
    Task 7.2 crew-empty invariant and the Task 8.6 own-task-only invariant to each
    packet. ``advance_tick`` is only ever called on a ``PLAY`` state (it raises
    otherwise), and the loop stops once the game leaves ``PLAY``, mirroring
    ``eval/leak_test._run_scripted_game``.
    """

    game_map = load_canonical_map()
    task_assignment = _roster_task_assignment(game_map)
    state = _roster_initial_state(
        seed=seed, num_impostors=num_impostors, game_map=game_map
    )
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    for batch in action_batches:
        if state.phase != "PLAY":
            break
        state, events = advance_tick(
            state, _unique_actions_per_actor(batch), game_map=game_map
        )
        # The living + dead impostor roster the service derives its pretend-task
        # seat ordering from (role-filtered, never visibility-filtered).
        impostor_ids_now = [
            pid for pid, p in state.players.items() if p.role == "IMPOSTOR"
        ]
        for player_id, player in state.players.items():
            if not player.alive:
                continue
            packet = service.build_packet(
                world_state=state,
                agent_id=player_id,
                engine_events=events,
            )
            packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
            _assert_no_recursive_hidden_fields(packet_dump)
            _assert_no_role_bearing_values(packet_dump)
            # Entitlement: the recipient saw EXACTLY the players and bodies this
            # tick's world state allows it -- re-derived from ``WorldState``, so a
            # widened entity filter in ``engine.visibility`` trips here.
            assert_visible_entities_match_engine_truth(
                packet, state=state, game_map=game_map, engine_events=events
            )
            # ``SelfView.in_vent`` firewall (Task 11.1, DESIGN.md §1.3, §3.4): the
            # self-position bool rides ONLY the privileged self channel. A vented
            # player is hidden from every other agent's ``visible_players``, so
            # ``in_vent`` must appear at exactly one path -- the recipient's own
            # ``self_state`` -- and never on the crew-visible channel.
            in_vent_paths = [
                path
                for path, _ in _walk_json(packet_dump)
                if path and path[-1] == "in_vent"
            ]
            assert in_vent_paths == [("self_state", "in_vent")]
            # ``SelfView.own_kill`` firewall (Task 11.3, DESIGN.md §1.3, §6.2):
            # the killer's own kill rides ONLY the privileged self channel. The
            # engine excludes a killer from its own kill's witnesses, so a
            # ``PlayerView`` kill action would fail the leak test -- ``own_kill``
            # must appear at exactly one path, the recipient's own
            # ``self_state``, and never on the crew-visible channel. The nested
            # ``victim_id`` / ``room`` carry no role string (the value scanner
            # above already guards that), so the kill verb "(IMPOSTOR) killed"
            # exists only in the store render, never in packet JSON.
            own_kill_paths = [
                path
                for path, _ in _walk_json(packet_dump)
                if path and path[-1] == "own_kill"
            ]
            assert own_kill_paths == [("self_state", "own_kill")]
            # When populated, it is by construction the recipient's OWN kill:
            # the service writes it only when ``event.actor == player_id``, so a
            # populated ``own_kill`` must correspond to a KilledEvent this agent
            # committed this tick -- never a crewmate's or a fellow impostor's.
            own_kill = packet.self_state.own_kill
            if own_kill is not None:
                assert any(
                    isinstance(event, KilledEvent)
                    and event.actor == player_id
                    and event.target == own_kill.victim_id
                    and event.room == own_kill.room
                    for event in events
                )
            # Own-task-only firewall (DESIGN.md §1.3, §3.2): under the per-player
            # ``"{owner}:{map_task_id}"`` keyspace, a CREWMATE's
            # ``pending_task_id`` is its OWN map id -- never the composite instance
            # id, never another owner's task. A dropped ``owner`` filter in
            # ``_pending_task_id_for_agent`` would surface a FOREIGN map id here.
            # An IMPOSTOR owns no instance, so it carries the deterministic PRETEND
            # map id instead (Task 10.14): still a bare map id (no owner prefix to
            # leak), the impostor's own per-seat blend target, never a dropped-filter
            # foreign min. The pretend selection is a pure function of map + seat +
            # tick, so the swept value stays deterministic and replay-safe.
            #
            # Task 13.12 (redistribute): the canonical map now re-keys a dead
            # crewmate's incomplete instances to a LIVING crewmate, so a crewmate's
            # pending task is no longer its STATIC initial assignment -- it may be an
            # INHERITED instance it now owns. The firewall is unchanged (the packet
            # still surfaces only a bare map id of a task this crewmate OWNS), so the
            # expectation is re-derived from CURRENT ownership (``task.owner ==
            # player_id``) INDEPENDENTLY of the function under test: the lexico-
            # graphically-first owned, unfinished map id, exactly mirroring
            # ``_pending_task_id_for_agent``'s crewmate contract. A dropped owner
            # filter (surfacing a FOREIGN / global-min task this crewmate does not
            # own) still mismatches here and is caught.
            if packet.self_state.role == "IMPOSTOR":
                expected_pending = impostor_pretend_task_id(
                    game_map=game_map,
                    agent_id=player_id,
                    impostor_ids=impostor_ids_now,
                    tick=state.tick,
                )
            else:
                owned_map_ids = sorted(
                    task.map_task_id
                    for task in state.tasks.values()
                    if task.owner == player_id and not task.completed
                )
                expected_pending = owned_map_ids[0] if owned_map_ids else None
            assert packet.self_state.pending_task_id == expected_pending
            assert ":" not in (packet.self_state.pending_task_id or "")
            if packet.self_state.role == "CREWMATE":
                assert packet.self_state.fellow_impostor_ids == ()
                # A crewmate never kills, so it never carries an ``own_kill`` --
                # the privileged self-channel field is impostor-act only.
                assert packet.self_state.own_kill is None
                # No task this crewmate does NOT currently own appears anywhere in
                # its packet (distinct ids make the owner-scope leak unambiguous).
                # "Foreign" is scoped to CURRENT ownership, not the static initial
                # deal: under redistribute a crewmate may now own an INHERITED
                # re-keyed instance (a task another player held at seed time), which
                # is its own and legitimately present -- so a static-assignment id
                # the crewmate now owns is exempt, while any task it does NOT own
                # (a living other's, or a global-min foreign min) still must not
                # leak.
                dumped = json.dumps(packet_dump)
                owned_now = {
                    task.map_task_id
                    for task in state.tasks.values()
                    if task.owner == player_id
                }
                for other_id, other_map_id in task_assignment.items():
                    if other_id == player_id or other_map_id in owned_now:
                        continue
                    assert other_map_id not in dumped, (
                        f"{player_id} packet leaked {other_id}'s task {other_map_id!r}"
                    )
        if state.phase != "PLAY":
            break

    service.close()


@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    num_impostors=st.sampled_from(_VALID_IMPOSTOR_COUNTS),
    sabotage_kind=st.sampled_from(("reactor", "lights")),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_global_view_sabotage_fields_are_role_invariant(
    seed: int,
    num_impostors: int,
    sabotage_kind: str,
    tmp_path: Path,
) -> None:
    """The public repair channel (Task 11.5 / 11.6) never differs by role.

    ``GlobalView.sabotage_repair_rooms`` / ``sabotage_is_gating`` are read from
    the map's ``SabotageDefinition`` independent of the recipient, so every living
    agent -- crewmate AND impostor, across 2/3-impostor rosters -- must see an
    IDENTICAL repair channel while a sabotage is active (DESIGN.md §1.3, §8.3).
    The kill/vent/report/wait sweep above never starts a sabotage, so this injects
    an active one into the initial state and asserts the two new fields are
    byte-identical across roles and carry no role-bearing substring (the repair
    rooms are bare room ids -- the imported value scanner trips on any
    ``impostor`` / ``crewmate`` / ``crew`` leak).
    """

    game_map = load_canonical_map()
    state = dataclasses.replace(
        _roster_initial_state(
            seed=seed, num_impostors=num_impostors, game_map=game_map
        ),
        sabotage=SabotageState(
            kind=sabotage_kind,
            remaining_ticks=5,
            affected_rooms=(),
            active=True,
        ),
    )
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    expected = game_map.sabotages[sabotage_kind]
    channels: set[tuple[tuple[str, ...], bool]] = set()
    for player_id, player in state.players.items():
        if not player.alive:
            continue
        packet = service.build_packet(
            world_state=state, agent_id=player_id, engine_events=[]
        )
        packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
        _assert_no_role_bearing_values(packet_dump)
        global_view = packet.global_state
        assert global_view.sabotage_active is True
        channels.add(
            (global_view.sabotage_repair_rooms, global_view.sabotage_is_gating)
        )

    # One distinct channel across every role recipient (public / role-blind), and
    # it matches the map definition the service projected.
    assert channels == {(expected.repair_rooms, expected.gates_tasks)}
    service.close()


@st.composite
def _roster_activity_action(draw: st.DrawFn) -> Action:
    """Draw the leak-sweep vocabulary EXTENDED with ``do_task`` and ``sabotage``.

    The kill/vent/report/wait draws mirror :func:`_roster_action`; ``do_task``
    draws any canonical map task (the actor's own resolves, a foreign one is
    rejected -- both stamp ``action="task"`` for visible observers, Task 13.9),
    and ``sabotage`` exercises the never-observable path (it must never reach
    ``visible_players`` as an action). The engine rejects role-invalid attempts
    via ``ActionRejectedEvent`` rather than raising, so every draw is safe.
    """

    kind = draw(
        st.sampled_from(("kill", "vent", "report", "wait", "do_task", "sabotage"))
    )
    actor = draw(st.sampled_from(_ROSTER_PLAYER_IDS))
    if kind == "kill":
        target = draw(
            st.sampled_from(tuple(pid for pid in _ROSTER_PLAYER_IDS if pid != actor))
        )
        return _ACTION_ADAPTER.validate_python(
            {"type": "kill", "actor": actor, "payload": {"target": target}}
        )
    if kind == "vent":
        vent_id = draw(st.sampled_from(_ROSTER_VENT_IDS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "vent", "actor": actor, "payload": {"vent_id": vent_id}}
        )
    if kind == "report":
        body_id = draw(st.sampled_from(_ROSTER_BODY_ID_DRAWS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "report", "actor": actor, "payload": {"body_id": body_id}}
        )
    if kind == "do_task":
        task_id = draw(st.sampled_from(_ROSTER_MAP_TASK_IDS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "do_task", "actor": actor, "payload": {"task_id": task_id}}
        )
    if kind == "sabotage":
        sabotage_kind = draw(st.sampled_from(("reactor", "lights")))
        return _ACTION_ADAPTER.validate_python(
            {"type": "sabotage", "actor": actor, "payload": {"kind": sabotage_kind}}
        )
    return _ACTION_ADAPTER.validate_python(
        {"type": "wait", "actor": actor, "payload": {}}
    )


@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    num_impostors=st.sampled_from(_VALID_IMPOSTOR_COUNTS),
    action_batches=st.lists(
        st.lists(_roster_activity_action(), max_size=3), max_size=10
    ),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_observed_task_annotation_never_leaks_hidden_information(
    seed: int,
    num_impostors: int,
    action_batches: list[list[Action]],
    tmp_path: Path,
) -> None:
    """The Task 13.9 ``action="task"`` annotation never leaks hidden info.

    Extends the purity sweep with ``do_task`` + ``sabotage`` in the action
    vocabulary so every packet exercises the new observed-activity stamp across
    many seeds and 2/3-impostor rosters. Per packet, beyond the imported leak
    scanners:

    * every ``visible_player`` carries EXACTLY ``{id, room, action}`` -- the
      annotation reuses the ``action`` field and adds no key;
    * ``sabotage`` NEVER surfaces as a visible action (the forbidden-action set);
    * a ``kill`` / ``vent`` action is witness-permitted -- so a REJECTED kill or
      vent (an ``ActionRejectedEvent`` the new code must ignore) can never leak;
    * every ``task`` annotation is VISION-gated (the actor is in the observer's
      independently-recomputed ``visible_player_ids``) and TRACEABLE to a do_task
      event this tick (resolved ``TaskProgressed`` / ``TaskCompleted`` OR rejected
      ``ActionRejected[do_task]``) -- no spurious or unseen task ever appears.
    """

    game_map = load_canonical_map()
    state = _roster_initial_state(
        seed=seed, num_impostors=num_impostors, game_map=game_map
    )
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    for batch in action_batches:
        if state.phase != "PLAY":
            break
        state, events = advance_tick(
            state, _unique_actions_per_actor(batch), game_map=game_map
        )
        task_event_actors: set[PlayerId] = set()
        for event in events:
            if isinstance(event, (TaskProgressedEvent, TaskCompletedEvent)):
                task_event_actors.add(event.actor)
            elif isinstance(event, ActionRejectedEvent) and event.action == "do_task":
                task_event_actors.add(event.actor)
        for player_id, player in state.players.items():
            if not player.alive:
                continue
            packet = service.build_packet(
                world_state=state,
                agent_id=player_id,
                engine_events=events,
            )
            packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
            _assert_no_recursive_hidden_fields(packet_dump)
            _assert_no_role_bearing_values(packet_dump)
            visible_now = set(
                compute_visibility_for_player(
                    observer_id=player_id, world_state=state, game_map=game_map
                ).visible_player_ids
            )
            for visible_player in packet.visible_players:
                visible_player_dump = visible_player.model_dump(mode="json")
                assert set(visible_player_dump.keys()) == {"id", "room", "action"}
                assert visible_player.action not in _FORBIDDEN_VISIBLE_PLAYER_ACTIONS
                if visible_player.action in {"kill", "vent"}:
                    assert _action_is_permitted_by_witness_event(
                        action=visible_player.action,
                        actor_id=visible_player.id,
                        agent_id=player_id,
                        engine_events=list(events),
                    )
                if visible_player.action == "task":
                    # Vision-gated: a task stamp only ever rides a player the
                    # observer can currently SEE (never the witness-only channel).
                    assert visible_player.id in visible_now
                    # Traceable: it corresponds to a real do_task this tick.
                    assert visible_player.id in task_event_actors
        if state.phase != "PLAY":
            break

    service.close()


# --------------------------------------------------------------------------- #
# The movement-perception witness gate (Task 19.24).
#
# ``moved_players`` (``observation/service.py::_moved_players_for_agent``) was
# the one packet channel with ZERO leak-suite coverage — and it is the channel
# whose own docstring narrates a SHIPPED gating bug: gating on the post-advance
# ``visible_player_ids`` (the actor's ARRIVAL room) handed the transition's
# ORIGIN to an observer who only saw the actor arrive, and dropped the departure
# for the observer left behind who actually saw it leave. The sweeps above never
# issue a ``move``, so every packet they scan carries an EMPTY ``moved_players``:
# the gap was structural, not incidental. This region closes it with a sweep
# whose vocabulary moves players, plus a deterministic case that proves the
# sweep is not vacuous (a real witnessed transition really does reach a packet).
# The planted-leak proofs that the scanner BITES live in ``eval/leak_test.py``.
# --------------------------------------------------------------------------- #

# CAFETERIA (the spawn room, ``_roster_initial_state``) and its neighbors. Draws
# from the full room list would make almost every move a rejected non-adjacent
# attempt; drawing the hub's neighbors keeps a healthy share of the sweep's moves
# RESOLVING into real ``MovedEvent``s while the strategy still emits
# out-of-range destinations (a room the actor is not adjacent to once it has
# walked away), which the engine rejects via ``ActionRejectedEvent``.
_ROSTER_MOVE_ROOMS = ("CAFETERIA", "EAST_HALL", "UPPER_HALL", "WEST_HALL")


@st.composite
def _roster_movement_action(draw: st.DrawFn) -> Action:
    """Draw the leak-sweep vocabulary EXTENDED with ``move``.

    The kill/vent/report/wait draws mirror :func:`_roster_action`; ``move`` draws
    a destination from the spawn hub's neighborhood so transitions actually
    resolve. Movement is weighted (``move`` is drawn twice as often as any other
    verb) because an empty ``moved_players`` scans vacuously — the sweep is only
    worth its runtime when packets carry transitions.
    """

    kind = draw(st.sampled_from(("move", "move", "kill", "vent", "report", "wait")))
    actor = draw(st.sampled_from(_ROSTER_PLAYER_IDS))
    if kind == "move":
        to_room = draw(st.sampled_from(_ROSTER_MOVE_ROOMS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "move", "actor": actor, "payload": {"to_room": to_room}}
        )
    if kind == "kill":
        target = draw(
            st.sampled_from(tuple(pid for pid in _ROSTER_PLAYER_IDS if pid != actor))
        )
        return _ACTION_ADAPTER.validate_python(
            {"type": "kill", "actor": actor, "payload": {"target": target}}
        )
    if kind == "vent":
        vent_id = draw(st.sampled_from(_ROSTER_VENT_IDS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "vent", "actor": actor, "payload": {"vent_id": vent_id}}
        )
    if kind == "report":
        body_id = draw(st.sampled_from(_ROSTER_BODY_ID_DRAWS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "report", "actor": actor, "payload": {"body_id": body_id}}
        )
    return _ACTION_ADAPTER.validate_python(
        {"type": "wait", "actor": actor, "payload": {}}
    )


@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    num_impostors=st.sampled_from(_VALID_IMPOSTOR_COUNTS),
    action_batches=st.lists(
        st.lists(_roster_movement_action(), max_size=3), max_size=10
    ),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_moved_players_are_departure_witness_gated(
    seed: int,
    num_impostors: int,
    action_batches: list[list[Action]],
    tmp_path: Path,
) -> None:
    """No packet carries a transition, or an entity, its recipient could not witness.

    Per packet, on top of the imported leak scanners: every ``moved_players``
    entry is departure-witnessed (``from_room`` is in the observer's
    INDEPENDENTLY recomputed ``visible_rooms`` — never merely the arrival),
    traceable to a real ``MovedEvent`` of this tick on actor AND both rooms, not
    a no-op, and sorted by actor id; and the packet's visible players and bodies
    EQUAL what the world state entitles the recipient to. Visibility is
    recomputed here through ``engine.visibility.compute_visibility_for_player``
    rather than read back off the service, so the gate is checked against engine
    truth and not against the code that implemented it — the same independence
    the task-annotation sweep above uses.

    NON-VACUITY (the counter). This is the one sweep whose vocabulary SEPARATES
    players; the others leave everyone standing in the spawn room, where every
    observer is entitled to every other and the entitlement equality proves
    nothing about a dropped room filter. So the example counts packets whose
    entitled-player set is a PROPER SUBSET of the living others, and requires at
    least one whenever the living roster ever stood in more than one room with a
    crewmate alive — a crewmate's room set is exactly its own room, so a split
    roster necessarily hides someone from someone.
    """

    game_map = load_canonical_map()
    state = _roster_initial_state(
        seed=seed, num_impostors=num_impostors, game_map=game_map
    )
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    separated_packets = 0
    roster_ever_split = False
    for batch in action_batches:
        if state.phase != "PLAY":
            break
        state, events = advance_tick(
            state, _unique_actions_per_actor(batch), game_map=game_map
        )
        living = [player for player in state.players.values() if player.alive]
        if len({player.room for player in living}) > 1 and any(
            player.role == "CREWMATE" for player in living
        ):
            roster_ever_split = True
        for player_id, player in state.players.items():
            if not player.alive:
                continue
            packet = service.build_packet(
                world_state=state,
                agent_id=player_id,
                engine_events=events,
            )
            packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
            _assert_no_recursive_hidden_fields(packet_dump)
            _assert_no_role_bearing_values(packet_dump)
            visibility = compute_visibility_for_player(
                observer_id=player_id, world_state=state, game_map=game_map
            )
            assert_moved_players_are_witness_gated(
                packet,
                engine_events=events,
                visible_rooms=visibility.visible_rooms,
            )
            assert_visible_entities_match_engine_truth(
                packet, state=state, game_map=game_map, engine_events=events
            )
            living_others = {
                other_id
                for other_id, other in state.players.items()
                if other_id != player_id and other.alive
            }
            entitled = {
                other_id
                for other_id, other in state.players.items()
                if other_id != player_id
                and other.alive
                and not other.in_vent
                and other.room in set(visibility.visible_rooms)
            }
            if entitled < living_others:
                separated_packets += 1
        if state.phase != "PLAY":
            break

    service.close()

    assert separated_packets > 0 or not roster_ever_split, (
        "the living roster stood in more than one room, yet no scanned packet "
        "had an entitled-player set smaller than the living others — the "
        "entitlement equality ran vacuously over a co-located roster"
    )


def test_a_witnessed_transition_really_does_reach_a_packet(tmp_path: Path) -> None:
    """The sweep above is not vacuous, and the gate cuts BOTH ways.

    A property sweep that never populates ``moved_players`` would pass on empty
    tuples forever, so this pins the channel deterministically on real service
    packets — and it pins the exact pair the prior bug got backwards:

    * ``p-9`` walks CAFETERIA -> WEST_HALL;
    * ``p-8`` stays behind in CAFETERIA (the DEPARTURE room) and receives the
      transition, which the scanner accepts;
    * ``p-7`` is standing in WEST_HALL (the ARRIVAL room) and receives NOTHING —
      arrival-gated code would hand it the origin it never saw.

    Both observers are crewmates, whose base visibility is ``same_room_only``
    (Task 13.8), so "the room I am in" is exactly "what I can witness" and the
    two sides of the gate are unambiguous.
    """

    game_map = load_canonical_map()
    state = _roster_initial_state(seed=7, num_impostors=2, game_map=game_map)
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    # Tick 0: p-7 walks ahead into WEST_HALL, so it occupies the ARRIVAL room
    # before the transition under test happens.
    state, _events = advance_tick(
        state,
        [
            _ACTION_ADAPTER.validate_python(
                {"type": "move", "actor": "p-7", "payload": {"to_room": "WEST_HALL"}}
            )
        ],
        game_map=game_map,
    )
    assert state.players["p-7"].room == "WEST_HALL"

    # Tick 1: p-9 leaves CAFETERIA for WEST_HALL, watched by p-8 who stays put.
    state, events = advance_tick(
        state,
        [
            _ACTION_ADAPTER.validate_python(
                {"type": "move", "actor": "p-9", "payload": {"to_room": "WEST_HALL"}}
            )
        ],
        game_map=game_map,
    )
    assert state.players["p-8"].room == "CAFETERIA"

    packets = {
        agent_id: service.build_packet(
            world_state=state, agent_id=agent_id, engine_events=events
        )
        for agent_id in ("p-7", "p-8", "p-9")
    }
    service.close()

    # The witness gets the transition — origin included — and it scans clean.
    left_behind = packets["p-8"]
    assert [
        (moved.id, moved.from_room, moved.to_room)
        for moved in left_behind.moved_players
    ] == [("p-9", "CAFETERIA", "WEST_HALL")]
    assert_moved_players_are_witness_gated(
        left_behind,
        engine_events=events,
        visible_rooms=compute_visibility_for_player(
            observer_id="p-8", world_state=state, game_map=game_map
        ).visible_rooms,
    )

    # p-7, standing in the ARRIVAL room, is told nothing about where p-9 came
    # from — the leak the prior arrival-gated code shipped. The mover itself is
    # the same rule's other side: it walked, it did not watch.
    assert packets["p-7"].moved_players == ()
    assert packets["p-9"].moved_players == ()


def test_the_tick_interior_choice_is_pinned_on_both_sides(tmp_path: Path) -> None:
    """A tick is atomic, so "witnessed the departure" has TWO defensible answers.

    Raised as a P1 on PR #345 and reproduced before this test was written. Inside
    one ``advance_tick`` every move applies at once and the engine emits no
    intra-tick ordering, so there is no state in which "the moment p-3 left" is a
    thing the code can consult. Only two states exist to gate on, and they differ
    for exactly the players who moved this tick:

    * POST-move (what ``_moved_players_for_agent`` gates on today): the observer
      that ARRIVED in the departure room this tick is served; the observer that
      stood there and LEFT in the same tick is not.
    * PRE-move: the mirror image.

    Neither is uniformly stricter, so this is a modelling choice about the
    interior of a tick, owned by ``observation/service.py`` — which Task 19.24
    covers but does not change (perception feeds memory feeds actions feeds
    replay bytes, so flipping it is a substrate lever with a baseline
    re-adoption). Both real answers are pinned here so that flip cannot happen
    silently, and ``eval/leak_scan`` can express the stricter rule
    (``departure_visible_rooms``) for whoever makes it.
    """

    game_map = load_canonical_map()
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    def _move(actor: PlayerId, to_room: str) -> Action:
        return _ACTION_ADAPTER.validate_python(
            {"type": "move", "actor": actor, "payload": {"to_room": to_room}}
        )

    # ── the same-tick ARRIVER: served today ──────────────────────────────────
    state = _roster_initial_state(seed=1, num_impostors=2, game_map=game_map)
    state, _ = advance_tick(state, [_move("p-3", "WEST_HALL")], game_map=game_map)
    # p-3 leaves WEST_HALL for MEDBAY exactly as p-8 arrives from CAFETERIA.
    state, events = advance_tick(
        state, [_move("p-3", "MEDBAY"), _move("p-8", "WEST_HALL")], game_map=game_map
    )
    arriver = service.build_packet(
        world_state=state, agent_id="p-8", engine_events=events
    )
    assert [(m.id, m.from_room) for m in arriver.moved_players] == [
        ("p-3", "WEST_HALL")
    ], "the same-tick arriver stopped receiving the departure — the gate flipped"
    # The sweep's rule (the service's) accepts it; the strict rule rejects it,
    # p-8 having been in CAFETERIA when p-3 left.
    assert_moved_players_are_witness_gated(
        arriver,
        engine_events=events,
        visible_rooms=compute_visibility_for_player(
            observer_id="p-8", world_state=state, game_map=game_map
        ).visible_rooms,
    )
    with pytest.raises(AssertionError, match="cannot see at the departure"):
        assert_moved_players_are_witness_gated(
            arriver,
            engine_events=events,
            visible_rooms=("WEST_HALL",),
            departure_visible_rooms=("CAFETERIA",),
        )

    # ── the same-tick LEAVER: NOT served today ───────────────────────────────
    state = _roster_initial_state(seed=1, num_impostors=2, game_map=game_map)
    state, _ = advance_tick(
        state,
        [_move("p-3", "WEST_HALL"), _move("p-8", "WEST_HALL")],
        game_map=game_map,
    )
    # p-8 stood in WEST_HALL WITH p-3 and walks back to CAFETERIA as p-3 leaves.
    state, events = advance_tick(
        state, [_move("p-3", "MEDBAY"), _move("p-8", "CAFETERIA")], game_map=game_map
    )
    leaver = service.build_packet(
        world_state=state, agent_id="p-8", engine_events=events
    )
    service.close()
    assert leaver.moved_players == (), (
        "the same-tick leaver started receiving the departure — the gate flipped"
    )


# --------------------------------------------------------------------------- #
# The four observer classes.
#
# The sweeps above draw random rosters, so they state the entitlement rule only
# implicitly and never guarantee a given class is reached. These legs build one
# world by hand and pin what each class of observer may see: a CREWMATE its own
# room, an IMPOSTOR its room plus map neighbours, a VENTED observer the room set
# it would have had anyway, and a DEAD observer nothing. The vented case is the
# one that reads like an accident and is not: ``compute_visibility_for_player``
# never consults the observer's own ``in_vent``, because venting hides you FROM
# others (``_visible_player_ids`` filters vented players out of everyone else's
# packet) rather than blinding you.
# --------------------------------------------------------------------------- #

# room, in_vent, alive -- one world separating every class. p-1/p-2 are the
# impostors (``_roster_initial_state`` assigns the first ``num_impostors`` ids).
_OBSERVER_CLASS_PLACEMENTS: dict[PlayerId, tuple[str, bool, bool]] = {
    "p-1": ("CAFETERIA", False, True),
    "p-2": ("LABS", True, True),
    "p-3": ("CAFETERIA", False, True),
    "p-4": ("WEST_HALL", False, True),
    "p-5": ("LABS", False, True),
    "p-6": ("CAFETERIA", False, False),
    "p-7": ("CAFETERIA", False, True),
    "p-8": ("UPPER_HALL", False, True),
    "p-9": ("MEDBAY", False, False),
}


def _observer_class_state(game_map: Map) -> WorldState:
    """One world holding all four observer classes at once.

    CAFETERIA neighbours EAST_HALL / UPPER_HALL / WEST_HALL but not MEDBAY, and
    LABS neighbours only MEDBAY, so every expectation below is a strict subset
    of the roster and a dropped room filter cannot pass by coincidence. Two
    undiscovered bodies sit on opposite sides of that divide, and p-5 stands in
    LABS beside the vented p-2 so the vent filter has a witness to hide from.
    """

    base = _roster_initial_state(seed=20, num_impostors=2, game_map=game_map)
    players = {
        player_id: dataclasses.replace(
            base.players[player_id], room=room, in_vent=in_vent, alive=alive
        )
        for player_id, (room, in_vent, alive) in _OBSERVER_CLASS_PLACEMENTS.items()
    }
    bodies = {
        "body-p-6-0": BodyState(
            id="body-p-6-0",
            player_id="p-6",
            room="CAFETERIA",
            position=(0.0, 0.0),
            killed_by="p-1",
            discovered_by=None,
        ),
        "body-p-9-0": BodyState(
            id="body-p-9-0",
            player_id="p-9",
            room="MEDBAY",
            position=(0.0, 0.0),
            killed_by="p-2",
            discovered_by=None,
        ),
    }
    return dataclasses.replace(base, players=players, bodies=bodies)


@pytest.mark.parametrize(
    ("observer", "expected_players", "expected_bodies"),
    [
        # CREWMATE: its own room only.
        ("p-3", ("p-1", "p-7"), ("body-p-6-0",)),
        # IMPOSTOR: its room plus the map neighbours (WEST_HALL, UPPER_HALL).
        ("p-1", ("p-3", "p-4", "p-7", "p-8"), ("body-p-6-0",)),
        # VENTED (impostor in a LABS vent): still LABS + MEDBAY.
        ("p-2", ("p-5",), ("body-p-9-0",)),
        # The vented player's neighbour: p-2 shares LABS with p-5 and is
        # invisible to it -- venting is one-directional.
        ("p-5", (), ()),
        # DEAD: nothing at all.
        ("p-6", (), ()),
    ],
)
def test_each_observer_class_sees_exactly_its_entitlement(
    observer: PlayerId,
    expected_players: tuple[PlayerId, ...],
    expected_bodies: tuple[str, ...],
    tmp_path: Path,
) -> None:
    """The real service packet for each observer class matches a hand-written
    expectation, and the entitlement scanner accepts it."""

    game_map = load_canonical_map()
    state = _observer_class_state(game_map)
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )
    try:
        packet = service.build_packet(
            world_state=state, agent_id=observer, engine_events=[]
        )
    finally:
        service.close()

    assert tuple(view.id for view in packet.visible_players) == expected_players
    assert tuple(view.id for view in packet.visible_bodies) == expected_bodies
    assert_visible_entities_match_engine_truth(
        packet, state=state, game_map=game_map, engine_events=[]
    )


def test_a_dead_observer_is_entitled_to_nothing(tmp_path: Path) -> None:
    """The DEAD leg's other half: the empty packet is not vacuous acceptance.

    A dead observer's real packet carries no player and no body, so the leg
    above would pass just as well against a scanner that checked nothing. Here
    the same packet is poisoned with one entitled-looking entry at a time — a
    living crewmate standing in the room the corpse is in, and the corpse
    itself — and each must trip.
    """

    game_map = load_canonical_map()
    state = _observer_class_state(game_map)
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )
    try:
        packet = service.build_packet(
            world_state=state, agent_id="p-6", engine_events=[]
        )
    finally:
        service.close()

    assert packet.visible_players == ()
    assert packet.visible_bodies == ()

    with pytest.raises(AssertionError, match=r"p-6 visible_players .*'p-7'"):
        assert_visible_entities_match_engine_truth(
            packet.model_copy(
                update={
                    "visible_players": (
                        PlayerView(id="p-7", room="CAFETERIA", action=None),
                    )
                }
            ),
            state=state,
            game_map=game_map,
            engine_events=[],
        )

    with pytest.raises(AssertionError, match=r"p-6 visible_bodies .*body-p-6-0"):
        assert_visible_entities_match_engine_truth(
            packet.model_copy(
                update={
                    "visible_bodies": (
                        BodyView(id="body-p-6-0", room="CAFETERIA", victim_id="p-6"),
                    )
                }
            ),
            state=state,
            game_map=game_map,
            engine_events=[],
        )


# --------------------------------------------------------------------------- #
# The meeting-outcome memory lever never travels through perception.
#
# That lever widens what a MEMORY RENDER may state about an ejected player's
# role. Perception is a different surface with a different rule, and this sweep
# is the other direction of the same assertion: turning the lever ON must not
# move one byte of one observation packet, so the disclosure cannot reach an
# agent by riding the packet channel the scanners above guard.
# --------------------------------------------------------------------------- #
