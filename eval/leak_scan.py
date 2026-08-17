"""The packet leak scanners, as a library (Task 19.24).

DESIGN.md §11.2 calls the leak test "the most important test", and its scanners
had grown a second job: the ML champion gate imports them. Until this module,
that import went through ``eval/leak_test.py``, whose module-level ``import
pytest`` dragged a dev-only dependency onto a production path
(``training/bakeoff/harness.py``, ``training/crew/scorer.py`` — both reachable
from ``scripts/run_tournament.py`` and the co-evolution driver) and kept
``training/`` and ``eval/`` outside the runtime/dev dependency partition
``pyproject.toml`` states.

So the split is by DEPENDENCY, not by taste: this module holds the scanners and
the reconstruction walk ``scan_factory_packets`` needs and imports NO pytest;
``eval/leak_test.py`` is the pytest wrapper that owns the scripted-fixture sweep
and every planted-leak self-test, importing what it asserts on from here. The
scanners moved VERBATIM — same predicates, same failure messages, same
``AssertionError`` contract — because the property that makes them worth keeping
is that they demonstrably BITE, and every planted-leak self-test in the wrapper
proves it still does.

``assert`` (not ``raise``) is deliberate and load-bearing: two production callers
catch ``AssertionError`` to record a champion-gate verdict
(``leak_test_passed``), and the wrapper's self-tests match on the assertion
text. Nothing here runs under ``python -O``, where asserts are stripped — the
gate paths run under a plain interpreter.
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Collection, Iterator, Sequence
from pathlib import Path
from typing import TypeAlias, cast

from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import RoomId
from engine.events import (
    EngineEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    MovedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from meetings.schemas import MeetingResult
from observation.packet import ObservationPacket
from observation.service import ObservationService, impostor_pretend_task_set
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    AgentFactory,
    HeadlessGame,
    apply_meeting_result,
    build_default_meeting_runner,
)
from orchestrator.replay import MeetingReplayEntry, ReplayEntry, read_all_entries
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

_FORBIDDEN_VISIBLE_PLAYER_FIELDS = frozenset({"role", "kill_attribution", "killed_by"})
_FORBIDDEN_BODY_FIELDS = frozenset({"killed_by", "kill_attribution", "player_id"})
_FORBIDDEN_VISIBLE_PLAYER_ACTIONS = frozenset({"sabotage"})
_FORBIDDEN_RECURSIVE_FIELD_NAMES = frozenset(
    {"killed_by", "kill_attribution", "player_id"}
)
_ALLOWED_RECURSIVE_FIELD_PATHS = frozenset({("self_state", "role")})
_FORBIDDEN_VALUE_SUBSTRINGS = ("impostor", "crewmate", "crew")
_ALLOWED_VALUE_PATHS = frozenset({("self_state", "role")})
_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonPathPart: TypeAlias = str | int
JsonPath: TypeAlias = tuple[JsonPathPart, ...]


def _action_is_permitted_by_witness_event(
    *,
    action: str | None,
    actor_id: str,
    agent_id: str,
    engine_events: list[EngineEvent],
) -> bool:
    if action is None:
        return False
    for event in engine_events:
        if action == "kill" and isinstance(event, KilledEvent):
            if event.actor == actor_id:
                return agent_id in event.witnesses
        elif action == "vent" and isinstance(
            event, (VentEnteredEvent, VentExitedEvent)
        ):
            if event.actor == actor_id:
                return agent_id in event.witnesses
    return False


def _walk_json(
    value: JsonValue, path: JsonPath = ()
) -> Iterator[tuple[JsonPath, JsonValue]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_json(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_json(child, (*path, index))


def _format_json_path(path: JsonPath) -> str:
    formatted_path = "$"
    for part in path:
        if isinstance(part, int):
            formatted_path = f"{formatted_path}[{part}]"
        else:
            formatted_path = f"{formatted_path}.{part}"
    return formatted_path


def _assert_no_recursive_hidden_fields(packet_dump: JsonValue) -> None:
    for path, _ in _walk_json(packet_dump):
        if not path:
            continue
        field_name = path[-1]
        if not isinstance(field_name, str):
            continue
        if field_name == "role" and path not in _ALLOWED_RECURSIVE_FIELD_PATHS:
            raise AssertionError(
                f"hidden field {field_name!r} leaked at {_format_json_path(path)}"
            )
        if field_name in _FORBIDDEN_RECURSIVE_FIELD_NAMES:
            raise AssertionError(
                f"hidden field {field_name!r} leaked at {_format_json_path(path)}"
            )


def _assert_no_role_bearing_values(packet_dump: JsonValue) -> None:
    """Scan every string value in the packet for role-bearing substrings.

    The recursive field-name scanner catches keys named ``role``,
    ``killed_by``, ``kill_attribution`` and ``player_id``. This pass
    complements it by catching role information that leaks through a
    value — most notably player ids that encode the role inline (e.g.
    a sentinel such as ``"crew_role_leak_fixture"`` planted into
    ``visible_players[].id``), which the field-name scanner cannot see
    because the leaky string sits in an ``id`` slot a packet legitimately
    uses for non-role-bearing ids. ``self_state.role`` is the single
    value path allowed to contain the role string because the agent is
    allowed to know its own role.
    """

    for path, value in _walk_json(packet_dump):
        if not isinstance(value, str):
            continue
        if path in _ALLOWED_VALUE_PATHS:
            continue
        lowered = value.lower()
        for forbidden in _FORBIDDEN_VALUE_SUBSTRINGS:
            if forbidden in lowered:
                raise AssertionError(
                    f"role-bearing value {value!r} leaked at {_format_json_path(path)}"
                )


# --------------------------------------------------------------------------- #
# The movement-perception witness gate (Task 19.24).
#
# ``moved_players`` (``observation/service.py::_moved_players_for_agent``) was
# the one packet channel with ZERO leak-suite coverage, and it is the channel
# whose own docstring narrates a SHIPPED gating bug: gating on the post-advance
# ``visible_player_ids`` (the actor's ARRIVAL room) attributed a transition's
# ORIGIN to an observer who only saw the actor arrive — a ``from_room`` leak —
# and dropped the departure for the observer left behind who actually saw it
# leave. The fix made SEEING THE SOURCE ROOM the witness condition. This scanner
# is that condition, restated independently of the code that implements it.
# --------------------------------------------------------------------------- #


def assert_moved_players_are_witness_gated(
    packet: ObservationPacket,
    *,
    engine_events: Sequence[EngineEvent],
    visible_rooms: Collection[RoomId],
    departure_visible_rooms: Collection[RoomId] | None = None,
) -> None:
    """Assert every ``moved_players`` entry is a transition the observer WITNESSED.

    Four properties, each a way the channel could leak or drift:

    1. **Departure-witnessed.** ``from_room`` is in the gating room set — the
       observer could see the room the actor LEFT. This is the exact predicate
       the prior bug got wrong (it gated on the arrival instead), so a packet
       built by arrival-gating trips here.
    2. **Traceable.** The entry matches a real ``MovedEvent`` of this tick on
       actor AND both rooms — no fabricated transition, and no stale origin
       stitched onto a current arrival.
    3. **Not a no-op.** ``from_room != to_room`` is not a transition and must
       never be surfaced as one.
    4. **Replay-stable byte shape.** Sorted ascending by ``id``, no duplicate
       actor — the packet ordering the service promises.

    Takes the room sets as arguments rather than recomputing them: the caller
    supplies them from ``engine.visibility.compute_visibility_for_player``, so
    the check is INDEPENDENT of the service's own gating (the point — a scanner
    that reused the code under test would prove nothing). That is also why this
    is not folded into :func:`assert_packet_is_leak_clean`, whose factory-mode
    callers hold packets and events but no world state.

    WHICH ROOM SET GATES PROPERTY 1 — the tick-interior question (Codex P1 review
    on PR #345, reproduced before this text was written). A tick is atomic: the
    engine applies every move at once and emits no intra-tick ordering, so
    "visible when the actor left" is not a state the engine ever holds. There are
    only two states to gate against, and they differ for exactly one population —
    players who moved this tick:

    * ``visible_rooms`` (POST-move, what ``observation/service.py`` gates on
      today): an observer that ARRIVED in ``from_room`` this tick receives the
      departure of an actor that left it in the same tick; an observer that stood
      there and LEFT in the same tick receives nothing.
    * ``departure_visible_rooms`` (PRE-move): the mirror image — the same-tick
      leaver is served, the same-tick arriver is not.

    Neither slice is uniformly stricter, so which one is right is a MODELING
    choice about the interior of a tick, and it belongs to
    ``observation/service.py`` — the packet channel this task covers but does not
    change (agent perception feeds memory feeds actions feeds replay bytes, so a
    flip is a substrate lever with a baseline re-adoption, not a test change).
    Passing ``departure_visible_rooms`` therefore asserts the STRICTER pre-move
    rule and is how a future task would gate a flip; leaving it ``None`` asserts
    the rule the service implements today. Both are exercised by planted
    self-tests in ``eval/leak_test.py``, and
    ``tests/observation/test_leak_property.py`` pins the two real-service answers
    so a silent flip fails.

    Raises ``AssertionError`` on any violation.
    """

    moved = packet.moved_players
    if not moved:
        return
    agent = packet.agent_id
    transitions = {
        (event.actor, event.from_room, event.to_room)
        for event in engine_events
        if isinstance(event, MovedEvent)
    }
    gating_rooms = (
        visible_rooms if departure_visible_rooms is None else departure_visible_rooms
    )
    when = "at the departure" if departure_visible_rooms is not None else "now"
    visible = set(gating_rooms)
    for entry in moved:
        assert entry.from_room != entry.to_room, (
            f"{agent} packet carries a no-op move for {entry.id!r} "
            f"({entry.from_room!r} -> {entry.to_room!r})"
        )
        assert (entry.id, entry.from_room, entry.to_room) in transitions, (
            f"{agent} packet carries a move for {entry.id!r} "
            f"({entry.from_room!r} -> {entry.to_room!r}) with no matching "
            f"MovedEvent this tick"
        )
        assert entry.from_room in visible, (
            f"{agent} packet leaked an unwitnessed departure: {entry.id!r} left "
            f"{entry.from_room!r}, which {agent} cannot see {when}"
        )
    ids = [entry.id for entry in moved]
    assert ids == sorted(set(ids)), (
        f"{agent} moved_players {ids} must be sorted ascending by id with no "
        f"duplicate actor (replay-stable byte shape)"
    )


# --------------------------------------------------------------------------- #
# The owned-task leak assertions (Task 15.22).
#
# ``SelfView.owned_task_ids`` widens the privileged self channel with the
# recipient's OWN unfinished map task ids (crewmate) / its per-seat camouflage
# pretend window (impostor), assembled owner-scoped by ``ObservationService`` so
# no packet ever carries another player's task (DESIGN.md §1.3;
# audit-phase-15-pause decision 5). This region extends the leak suite with the
# four-item review's item (2) -- absence of foreign task ids in EVERY packet
# field -- and the byte discipline: a stable, "versioned" SelfView key set the
# next widening must extend deliberately.
# --------------------------------------------------------------------------- #

# The deliberate SelfView byte-shape pin (the packet-discipline "versioned"
# guard): a future SelfView widening must extend this pin deliberately, so an
# accidental field add or drop trips the discipline assertion below.
_SELF_STATE_KEY_SET = frozenset(
    {
        "room",
        "role",
        "pending_task_id",
        "owned_task_ids",
        "fellow_impostor_ids",
        "in_vent",
        "own_kill",
    }
)


def _assert_owned_task_discipline(packet: ObservationPacket) -> None:
    """Assert the ``owned_task_ids`` byte shape + role-blind consistency invariant.

    Role-blind by construction: every assertion below holds IDENTICALLY for a
    crewmate's owned frontier and an impostor's camouflage window, so none asserts
    a role bit. Each message names the packet's ``agent_id`` for a legible
    failure. Guards: (1) the SelfView key set is EXACTLY ``_SELF_STATE_KEY_SET``
    (byte-shape stability -- the packet discipline); (2) every owned id is a
    non-empty ``str`` containing NO ``":"`` (never a composite instance id, whose
    owner prefix would leak ownership); (3) the tuple is sorted ascending with no
    duplicates (replay-stable byte shape); (4) ``pending_task_id``, when set, is a
    member of ``owned_task_ids`` -- the role-blind consistency invariant, which
    holds identically for a crewmate's owned frontier (pending is its head) and an
    impostor's camouflage window (pending is the rotating pretend id).
    """

    agent = packet.agent_id
    self_state_keys = set(packet.self_state.model_dump(mode="json").keys())
    assert self_state_keys == _SELF_STATE_KEY_SET, (
        f"{agent} self_state key set {sorted(self_state_keys)} != pinned "
        f"{sorted(_SELF_STATE_KEY_SET)} (SelfView byte shape drifted)"
    )
    owned = packet.self_state.owned_task_ids
    for task_id in owned:
        assert isinstance(task_id, str) and task_id, (
            f"{agent} owned_task_ids carries a non-string/empty id {task_id!r}"
        )
        assert ":" not in task_id, (
            f"{agent} owned task id {task_id!r} is a composite instance id "
            f"(the owner prefix would leak ownership)"
        )
    assert list(owned) == sorted(set(owned)), (
        f"{agent} owned_task_ids {owned} must be sorted ascending with no "
        f"duplicates (replay-stable byte shape)"
    )
    pending = packet.self_state.pending_task_id
    assert pending is None or pending in owned, (
        f"{agent} pending_task_id {pending!r} is not a member of owned_task_ids "
        f"{owned} (the role-blind consistency invariant)"
    )


def _assert_owned_tasks_match_engine_truth(
    packet: ObservationPacket, *, state: WorldState, game_map: Map
) -> None:
    """Cross-player engine-truth check: ``owned_task_ids`` == the recipient's OWN set.

    The STRONG scripted-sweep guard (Task 15.22, four-item review item (2)): the
    owned set is verified against per-tick engine truth INDEPENDENTLY of the code
    under test, and no foreign task id appears in ANY packet field.

    * CREWMATE: ``owned_task_ids`` equals EXACTLY the recipient's OWN unfinished
      map ids -- nothing else. Kills redistribute tasks mid-game, so per-tick
      ``state`` truth is the right side (a crewmate may now own an inherited
      re-keyed instance).
    * IMPOSTOR: equals its per-seat ``impostor_pretend_task_set`` camouflage
      window, and the impostor owns ZERO ``state.tasks`` instance.
    * Foreign absence: no OTHER player's owned unfinished map id and no OTHER
      impostor's pretend window id (minus the recipient's own owned set) appears
      as a substring of the whole-packet JSON -- mirroring
      ``test_service.py::test_multi_impostor_packets_carry_no_foreign_task_ownership``.
    """

    agent = packet.agent_id
    impostor_ids = sorted(
        pid for pid, player in state.players.items() if player.role == "IMPOSTOR"
    )
    if state.players[agent].role == "CREWMATE":
        expected = tuple(
            sorted(
                task.map_task_id
                for task in state.tasks.values()
                if task.owner == agent and not task.completed
            )
        )
        assert packet.self_state.owned_task_ids == expected, (
            f"{agent} owned_task_ids {packet.self_state.owned_task_ids} != "
            f"engine-truth own unfinished set {expected}"
        )
    else:
        expected = impostor_pretend_task_set(
            game_map=game_map, agent_id=agent, impostor_ids=impostor_ids
        )
        assert packet.self_state.owned_task_ids == expected, (
            f"{agent} impostor owned_task_ids {packet.self_state.owned_task_ids} "
            f"!= camouflage window {expected}"
        )
        assert not any(task.owner == agent for task in state.tasks.values()), (
            f"impostor {agent} unexpectedly owns a WorldState.tasks instance"
        )

    foreign: set[str] = set()
    for other_id in state.players:
        if other_id == agent:
            continue
        foreign |= {
            task.map_task_id
            for task in state.tasks.values()
            if task.owner == other_id and not task.completed
        }
    for other_impostor in impostor_ids:
        if other_impostor == agent:
            continue
        foreign |= set(
            impostor_pretend_task_set(
                game_map=game_map,
                agent_id=other_impostor,
                impostor_ids=impostor_ids,
            )
        )
    foreign -= set(packet.self_state.owned_task_ids)
    dumped = json.dumps(packet.model_dump(mode="json"), sort_keys=True)
    for foreign_id in sorted(foreign):
        assert foreign_id not in dumped, (
            f"{agent} packet leaked foreign task id {foreign_id!r}"
        )


# --------------------------------------------------------------------------- #
# Agent-factory mode (Task 15.10).
#
# The scripted-fixture sweep in ``eval/leak_test.py`` walks 3 hand-authored games
# with NO factory parameter. A learned mover (Encoder v2 + a policy head) drives
# the engine into regions those fixtures never reach — so packets from those
# regions were UNSCANNED (the ml-spike Gap #7). This region adds a factory mode:
# run factory-built agents through FULL production games and apply the SAME leak
# scanners — the recursive role-leak scanners
# (:func:`_assert_no_recursive_hidden_fields` + :func:`_assert_no_role_bearing_values`)
# AND the witness-permission check (:func:`_action_is_permitted_by_witness_event`)
# — to every packet the encoder consumes. To run the witness check, each factory
# game is RECONSTRUCTED (re-seeded + re-fed its recorded actions) so the per-tick
# engine events are recovered alongside the packets; the reconstructed packets are
# byte-identical to the ones the live game handed the agents (the engine is a
# deterministic function of state + actions). The 3 scripted fixtures stay
# byte-identical; this is purely additive.
# --------------------------------------------------------------------------- #

# 9p/2i is the primary preset the committed corpora use: two impostors reliably
# reach kills → bodies → reports → meetings → vents (the leak-prone regions), so
# the scan actually covers what it claims to. A coverage assertion fails the test
# loud if the games never reach a body.
_FACTORY_MODE_SEEDS: tuple[int, ...] = (0, 1)
_FACTORY_NUM_PLAYERS = 9
_FACTORY_NUM_IMPOSTORS = 2
_FACTORY_TASKS_PER_CREWMATE = 2

# A factory-consumed packet paired with the engine events of the tick it was
# built on (needed for the witness-permission check).
PacketRecord: TypeAlias = tuple[ObservationPacket, list[EngineEvent]]


def _meeting_result_from_entry(entry: MeetingReplayEntry) -> MeetingResult:
    return MeetingResult(
        meeting_id=entry.meeting_id,
        triggered_by=entry.triggered_by,
        trigger_tick=entry.tick,
        outcome=entry.outcome,
        ejected_player_id=entry.ejected_player_id,
        ballots=entry.ballots,
        contradictions=entry.contradictions,
        transcript=entry.transcript,
    )


def _reconstruct_factory_records(
    replay_path: Path,
    *,
    game_map: Map,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    audit_dir: Path,
) -> list[PacketRecord]:
    """Re-seed + replay one factory game, yielding (packet, engine_events) records.

    Mirrors ``HeadlessGame._run_loop`` EXACTLY (``orchestrator/game.py``): each
    iteration builds every living agent's packet from the CURRENT (pre-advance)
    state plus the PRIOR tick's events (``last_events``) — the same
    ``build_packet(engine_events=last_events)`` the live loop hands the agents —
    THEN translates and advances that tick's recorded actions, THEN applies any
    meeting. So the scanned stream is exactly the packets the encoder consumed:
    it includes the tick-0 opening packet and every post-meeting resume packet,
    and excludes the terminal GAME_OVER state (no agent decides there). Each packet
    is paired with the events it was BUILT with, so the witness-permission check
    reads the right events.
    """

    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    records: list[PacketRecord] = []
    audit_path = audit_dir / f"_leak_audit_{replay_path.stem}.jsonl"
    service = ObservationService(game_map=game_map, audit_log_path=audit_path)
    last_events: tuple[EngineEvent, ...] = ()
    try:
        for entry in tick_entries:
            # Build packets from the PRE-advance state + prior events (the live
            # loop's exact contract), before applying this tick's actions.
            events_for_packets = list(last_events)
            for player_id in sorted(state.players):
                if state.players[player_id].alive:
                    packet = service.build_packet(
                        world_state=state,
                        agent_id=player_id,
                        engine_events=last_events,
                    )
                    records.append((packet, events_for_packets))
            actions = [
                _ACTION_ADAPTER.validate_python(dict(raw)) for raw in entry.actions
            ]
            state, events = advance_tick(state, actions, game_map=game_map)
            last_events = tuple(events)
            if state.phase == "MEETING":
                trigger = next(
                    e for e in events if isinstance(e, MeetingTriggeredEvent)
                )
                pre_meeting_events = last_events
                state, post_events = apply_meeting_result(
                    state,
                    _meeting_result_from_entry(meeting_by_tick[entry.tick]),
                    game_map=game_map,
                    triggering_body_id=trigger.body_id,
                )
                # Mirror the live loop: the resume packet sees the pre-meeting
                # events (a same-tick kill) plus the meeting's post events.
                last_events = pre_meeting_events + tuple(post_events)
            if state.phase == "GAME_OVER":
                break
    finally:
        service.close()
        audit_path.unlink(missing_ok=True)
    return records


def collect_factory_packet_records(
    agent_factory: AgentFactory,
    *,
    seeds: Sequence[int] = _FACTORY_MODE_SEEDS,
    num_players: int = _FACTORY_NUM_PLAYERS,
    num_impostors: int = _FACTORY_NUM_IMPOSTORS,
    tasks_per_crewmate: int = _FACTORY_TASKS_PER_CREWMATE,
) -> list[PacketRecord]:
    """Run ``agent_factory`` through full games; return (packet, events) records.

    Each game runs the REAL production loop (:class:`orchestrator.game.HeadlessGame`
    on the deterministic fake provider) to write a replay reflecting the factory's
    trajectory, then reconstructs that replay to recover the per-tick packets +
    engine events.
    """

    game_map = load_canonical_map()
    records: list[PacketRecord] = []
    with tempfile.TemporaryDirectory(prefix="ailibi-leak-factory-") as tmp:
        directory = Path(tmp)
        for seed in seeds:
            replay_path = directory / f"replay-seed-{seed}.jsonl"
            game = HeadlessGame(
                seed=seed,
                game_map=game_map,
                agent_factory=agent_factory,
                replay_path=replay_path,
                num_players=num_players,
                num_impostors=num_impostors,
                tasks_per_crewmate=tasks_per_crewmate,
                scheduler=TickScheduler(max_ticks=DEFAULT_MAX_TICKS),
                meeting_runner=build_default_meeting_runner(
                    llm_client=build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})
                ),
                force=True,
            )
            game.run()
            records.extend(
                _reconstruct_factory_records(
                    replay_path,
                    game_map=game_map,
                    seed=seed,
                    num_players=num_players,
                    num_impostors=num_impostors,
                    tasks_per_crewmate=tasks_per_crewmate,
                    audit_dir=directory,
                )
            )
    return records


def assert_packet_is_leak_clean(
    packet: ObservationPacket, engine_events: Sequence[EngineEvent] = ()
) -> None:
    """Apply the full leak scan to one packet — the SAME checks the scripted sweep runs.

    The recursive hidden-field scanner, the role-bearing value scanner, the
    ``visible_players`` key-set + forbidden-action pin, the ``visible_bodies``
    key-set pin, the crew ``fellow_impostor_ids`` firewall, AND — critically for
    the factory extension — the witness-permission check: a ``PlayerView`` stamped
    with a ``kill`` / ``vent`` action must be backed by a witness-permitted engine
    event for THIS observer. Raises ``AssertionError`` on any leak.
    """

    packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
    _assert_no_recursive_hidden_fields(packet_dump)
    _assert_no_role_bearing_values(packet_dump)
    events = list(engine_events)
    for visible_player in packet.visible_players:
        visible_player_dump = visible_player.model_dump(mode="json")
        assert set(visible_player_dump.keys()) == {"id", "room", "action"}
        assert _FORBIDDEN_VISIBLE_PLAYER_FIELDS.isdisjoint(visible_player_dump.keys())
        assert visible_player.action not in _FORBIDDEN_VISIBLE_PLAYER_ACTIONS
        if visible_player.action in {"kill", "vent"}:
            assert _action_is_permitted_by_witness_event(
                action=visible_player.action,
                actor_id=visible_player.id,
                agent_id=packet.agent_id,
                engine_events=events,
            ), (
                f"unwitnessed {visible_player.action!r} action stamped on "
                f"{visible_player.id!r} in {packet.agent_id!r}'s packet"
            )
    for visible_body in packet.visible_bodies:
        visible_body_dump = visible_body.model_dump(mode="json")
        assert set(visible_body_dump.keys()) == {"id", "room", "victim_id"}
        assert _FORBIDDEN_BODY_FIELDS.isdisjoint(visible_body_dump.keys())
    if packet.self_state.role == "CREWMATE":
        assert packet.cooldown is None
        assert packet.self_state.fellow_impostor_ids == ()
    # The owned-task byte-shape + role-blind consistency discipline (Task 15.22),
    # scanned on EVERY factory-mode packet.
    _assert_owned_task_discipline(packet)


def assert_no_factory_packet_leaks(records: Sequence[PacketRecord]) -> None:
    """Scan a reconstructed (packet, events) stream; raise on the first leak."""

    for packet, engine_events in records:
        assert_packet_is_leak_clean(packet, engine_events)


def scan_factory_packets(
    agent_factory: AgentFactory,
    *,
    seeds: Sequence[int] = _FACTORY_MODE_SEEDS,
    num_players: int = _FACTORY_NUM_PLAYERS,
    num_impostors: int = _FACTORY_NUM_IMPOSTORS,
    tasks_per_crewmate: int = _FACTORY_TASKS_PER_CREWMATE,
) -> int:
    """Run a factory through full games and leak-scan every packet it consumed.

    Returns the number of packets scanned. Asserts COVERAGE — the games must reach
    at least one body (proof they got past task-rush into the kill → body → report
    → meeting → vent regions the scan claims to cover), so a config that
    task-rushes to a win cannot pass on thin early-game packets. Raises
    ``AssertionError`` on a leak.
    """

    records = collect_factory_packet_records(
        agent_factory,
        seeds=seeds,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    assert records, "factory mode captured no packets"
    assert_no_factory_packet_leaks(records)
    bodies_seen = sum(len(packet.visible_bodies) for packet, _ in records)
    assert bodies_seen > 0, (
        "factory games never reached a body — the kill → body → meeting regions "
        "the factory leak scan exists to cover went unexercised"
    )
    return len(records)
