"""Property-based observation-purity sweep (DESIGN.md §11.2, audit I-I-2).

DESIGN.md §11.2 calls the leak test "the most important test" and mandates a
many-seeds / property-based purity sweep. The fixture-driven check in
``eval/leak_test.py`` walks exactly three hand-authored scripted games, so a
leak that only manifests under an unseen packet shape would slip through
(audit I-I-2). This module closes that gap: it drives ``ObservationService``
over every living agent on every tick across many Hypothesis-generated games
and feeds each packet through the EXISTING scanners from ``eval/leak_test.py``.

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

The action vocabulary mirrors the role-aware strategy from
``tests/engine/test_tick_properties.py`` but is generalized off that module's
single-impostor roster so the sweep exercises kills, vents, and reports across
the whole multi-impostor roster -- the events that populate ``visible_players``
/ ``visible_bodies`` / ``audible_events`` where a leak would surface.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import cast

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import PlayerId, PlayerState, SabotageState, TaskId, TaskState
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
from eval.leak_test import (
    _FORBIDDEN_VISIBLE_PLAYER_ACTIONS,
    JsonValue,
    _action_is_permitted_by_witness_event,
    _assert_no_recursive_hidden_fields,
    _assert_no_role_bearing_values,
    _walk_json,
)
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
            if packet.self_state.role == "IMPOSTOR":
                expected_pending = impostor_pretend_task_id(
                    game_map=game_map,
                    agent_id=player_id,
                    impostor_ids=impostor_ids_now,
                    tick=state.tick,
                )
            else:
                expected_pending = task_assignment[player_id]
            assert packet.self_state.pending_task_id == expected_pending
            assert ":" not in (packet.self_state.pending_task_id or "")
            if packet.self_state.role == "CREWMATE":
                assert packet.self_state.fellow_impostor_ids == ()
                # A crewmate never kills, so it never carries an ``own_kill`` --
                # the privileged self-channel field is impostor-act only.
                assert packet.self_state.own_kill is None
                # No OTHER owner's task id appears anywhere in a crew packet
                # (distinct ids make the owner-scope leak unambiguous). The only
                # task id a packet legitimately carries is the recipient's own
                # ``pending_task_id``, asserted above.
                dumped = json.dumps(packet_dump)
                for other_id, other_map_id in task_assignment.items():
                    if other_id == player_id:
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
