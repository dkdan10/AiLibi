from __future__ import annotations

import json
import tempfile
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import TypeAlias, cast

import pytest
from pydantic import BaseModel, ConfigDict, TypeAdapter

from agents.base import AgentInterface
from engine.actions import Action
from engine.entities import PlayerId, Role
from engine.events import (
    EngineEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from meetings.schemas import MeetingResult
from observation.action_intent import ActionIntent, MoveIntent, WaitIntent
from observation.packet import (
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    AgentFactory,
    HeadlessGame,
    apply_meeting_result,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import MeetingReplayEntry, ReplayEntry, read_all_entries
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state
from tests._helpers.world_state import scripted_initial_world_state

_SCRIPTED_GAMES = (
    "scripted_game_basic_tasks.json",
    "scripted_game_kill_report_meeting.json",
    "scripted_game_vent_and_emergency.json",
)
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


class _ScriptedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tick: int
    type: str
    actor: str
    payload: dict[str, object]


class _ScriptedGame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    seed: int
    actions: list[_ScriptedAction]


def _fixture_actions(script: _ScriptedGame) -> dict[int, list[Action]]:
    actions_by_tick: dict[int, list[Action]] = {}
    for raw_action in script.actions:
        action_data = raw_action.model_dump(exclude={"tick"})
        action = _ACTION_ADAPTER.validate_python(action_data)
        actions_by_tick.setdefault(raw_action.tick, []).append(action)
    return actions_by_tick


def _run_scripted_game(
    fixture_name: str,
    tmp_path: Path,
) -> list[tuple[ObservationPacket, list[EngineEvent]]]:
    fixture_path = Path("tests/fixtures") / fixture_name
    script = _ScriptedGame.model_validate_json(fixture_path.read_text(encoding="utf-8"))

    game_map = load_canonical_map()
    state: WorldState = scripted_initial_world_state(seed=script.seed)
    audit_path = tmp_path / f"audit_{fixture_name}.jsonl"
    observation_service = ObservationService(
        game_map=game_map, audit_log_path=audit_path
    )
    actions_by_tick = _fixture_actions(script)

    packet_records: list[tuple[ObservationPacket, list[EngineEvent]]] = []
    for tick in range(max(actions_by_tick, default=-1) + 1):
        assert state.tick == tick
        state, events = advance_tick(
            state,
            actions_by_tick.get(tick, []),
            game_map=game_map,
        )
        for player_id, player in state.players.items():
            if player.alive:
                packet = observation_service.build_packet(
                    world_state=state,
                    agent_id=player_id,
                    engine_events=events,
                )
                packet_records.append((packet, events))
        if state.phase == "GAME_OVER":
            break

    audit_packets = [
        json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    assert audit_packets == [
        packet.model_dump(mode="json") for packet, _ in packet_records
    ]
    return packet_records


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


def test_recursive_hidden_field_scanner_reports_nested_path() -> None:
    packet_dump: JsonValue = {
        "self_state": {"role": "CREWMATE"},
        "visible_bodies": [
            {
                "id": "body-p-1-3",
                "room": "STORAGE",
                "details": {"killed_by": "p-3"},
            }
        ],
    }

    with pytest.raises(
        AssertionError,
        match=r"\$\.visible_bodies\[0\]\.details\.killed_by",
    ):
        _assert_no_recursive_hidden_fields(packet_dump)


def test_role_bearing_value_scanner_trips_on_planted_visible_player_id() -> None:
    # Planted leak: a crewmate's packet whose visible_players carries the
    # impostor's role inside the id. The recursive field-name scanner does
    # not see this because the leaky string lives in an ``id`` value.
    packet_dump: JsonValue = {
        "self_state": {"role": "CREWMATE"},
        "visible_players": [
            {"id": "crew_role_leak_fixture", "room": "STORAGE", "action": None},
        ],
    }

    with pytest.raises(
        AssertionError,
        match=r"\$\.visible_players\[0\]\.id",
    ):
        _assert_no_role_bearing_values(packet_dump)


def test_role_bearing_value_scanner_allows_self_state_role() -> None:
    # The single allowed value path is `self_state.role` — the agent is
    # entitled to know its own role.
    packet_dump: JsonValue = {
        "self_state": {"role": "CREWMATE"},
        "visible_players": [
            {"id": "p-1", "room": "STORAGE", "action": None},
        ],
    }

    _assert_no_role_bearing_values(packet_dump)


def test_role_bearing_value_scanner_trips_on_nested_path() -> None:
    # A role-bearing substring inside a free-text field anywhere in the
    # packet should still trip the scanner — the audit log surfaces those
    # strings to downstream consumers verbatim.
    packet_dump: JsonValue = {
        "self_state": {"role": "CREWMATE"},
        "audible_events": [
            {"kind": "sabotage_alarm", "room": None, "extra": "crewmate radio chatter"},
        ],
    }

    with pytest.raises(
        AssertionError,
        match=r"\$\.audible_events\[0\]\.extra",
    ):
        _assert_no_role_bearing_values(packet_dump)


def test_no_observation_leaks_hidden_information(tmp_path: Path) -> None:
    for fixture_name in _SCRIPTED_GAMES:
        packet_records = _run_scripted_game(fixture_name, tmp_path)
        assert packet_records, f"no packets captured for {fixture_name}"

        for packet, engine_events in packet_records:
            packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
            _assert_no_recursive_hidden_fields(packet_dump)
            _assert_no_role_bearing_values(packet_dump)
            for visible_player in packet.visible_players:
                visible_player_dump = visible_player.model_dump(mode="json")
                assert set(visible_player_dump.keys()) == {"id", "room", "action"}
                assert _FORBIDDEN_VISIBLE_PLAYER_FIELDS.isdisjoint(
                    visible_player_dump.keys()
                )
                assert visible_player.action not in _FORBIDDEN_VISIBLE_PLAYER_ACTIONS
                if visible_player.action in {"kill", "vent"}:
                    assert _action_is_permitted_by_witness_event(
                        action=visible_player.action,
                        actor_id=visible_player.id,
                        agent_id=packet.agent_id,
                        engine_events=engine_events,
                    )
            for visible_body in packet.visible_bodies:
                visible_body_dump = visible_body.model_dump(mode="json")
                assert set(visible_body_dump.keys()) == {"id", "room", "victim_id"}
                assert _FORBIDDEN_BODY_FIELDS.isdisjoint(visible_body_dump.keys())
            if packet.self_state.role == "CREWMATE":
                assert packet.cooldown is None
                # Task 7.2 firewall invariant: the impostor-only
                # ``fellow_impostor_ids`` self-channel field must never reach a
                # crewmate recipient. The generic scanners cannot catch this --
                # role-neutral ids (``p-2``) do not trip the value scanner and
                # the field name is not in the recursive scanner's set -- so
                # this explicit assertion is the guard. The three committed
                # fixtures are 4p/1i, so every impostor's tuple is also ``()``
                # here; the impostor-sees-teammate path and a multi-impostor
                # crew-misroute are exercised by tests/observation/test_service
                # .py and the extended property sweep in test_leak_property.py.
                assert packet.self_state.fellow_impostor_ids == ()


# --------------------------------------------------------------------------- #
# Agent-factory mode (Task 15.10).
#
# The scripted-fixture sweep above walks 3 hand-authored games with NO factory
# parameter. A learned mover (Encoder v2 + a policy head) drives the engine into
# regions those fixtures never reach — so packets from those regions were
# UNSCANNED (the ml-spike Gap #7). This region adds a factory mode: run
# factory-built agents through FULL production games and apply the SAME leak
# scanners — the recursive role-leak scanners
# (:func:`_assert_no_recursive_hidden_fields` + :func:`_assert_no_role_bearing_values`)
# AND the witness-permission check (:func:`_action_is_permitted_by_witness_event`)
# — to every packet the encoder consumes. To run the witness check, each factory
# game is RECONSTRUCTED (re-seeded + re-fed its recorded actions) so the per-tick
# engine events are recovered alongside the packets; the reconstructed packets are
# byte-identical to the ones the live game handed the agents (the engine is a
# deterministic function of state + actions). The 3 scripted fixtures above stay
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


class _IdleExploreAgent:
    """A learned-style wrapper that turns a crew's idle WAIT into exploration.

    Gently perturbs the FSM: only when a CREWMATE would otherwise idle (the FSM
    returns a ``Wait`` — ~13% of crew actions, concentrated late-game) does this
    redirect it to an always-legal adjacent-room move, spread deterministically
    per-agent so idle crew WALK into rooms the FSM would leave unvisited. Active
    crew (routing to tasks, fleeing, reporting, calling meetings) and the whole
    IMPOSTOR side keep their FSM intent, so the game still produces the kills →
    bodies → meetings → vents the scan must cover. The full ``MeetingAwareAgent``
    protocol delegates to the wrapped agent via ``__getattr__``.

    Self-contained rather than built on ``training.env.build_interposition_factory``:
    that 15.8 seam validates a selector's returned intent against
    ``build_action_mask``, whose ``EmergencyMeetingIntent`` carries a DEFAULT
    payload and so does not equal the crew FSM's emergency (which carries
    ``reason='suspicion_accumulation'``), making any selector that delegates a
    crew emergency raise — a latent 15.8 mask gap out of scope for this task. This
    wrapper emits only always-legal moves and delegates everything else, so it
    exercises the learned-interposition shape without tripping that gap.
    """

    def __init__(self, inner: AgentInterface) -> None:
        self._inner = inner

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        intent = self._inner.decide(packet, public_map)
        if (
            packet.self_state.role == "CREWMATE"
            and isinstance(intent, WaitIntent)
            and not packet.self_state.in_vent
        ):
            neighbors = sorted(
                set(public_map.room_neighbors.get(packet.self_state.room, ()))
            )
            if neighbors:
                spread = sum(ord(char) for char in packet.agent_id) % len(neighbors)
                return MoveIntent.model_validate(
                    {
                        "type": "move",
                        "actor": packet.agent_id,
                        "payload": {"to_room": neighbors[spread]},
                    }
                )
        return intent

    def __getattr__(self, name: str) -> object:
        return getattr(self._inner, name)


def _learned_wrapper_factory() -> AgentFactory:
    """A learned-wrapper factory: real agents wrapped with the idle-explore policy."""

    inner_factory = build_default_agent_factory()

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        return _IdleExploreAgent(inner_factory(agent_id, role))

    return factory


def test_leak_factory_mode_fsm_default_factory_is_clean() -> None:
    # The FSM default factory (the anchor / BC oracle) driven through full games:
    # every packet it consumes must be leak-clean, and the games must reach the
    # leak-prone regions (asserted inside scan_factory_packets).
    scanned = scan_factory_packets(build_default_agent_factory())
    assert scanned > 0, "factory mode captured no packets"


def test_leak_factory_mode_learned_wrapper_factory_is_clean() -> None:
    # A learned-wrapper factory (a policy interposition that drives idle crew into
    # new regions) must be just as leak-clean as the FSM default.
    scanned = scan_factory_packets(_learned_wrapper_factory())
    assert scanned > 0, "learned-wrapper factory mode captured no packets"


def test_leak_factory_mode_planted_role_leak_trips() -> None:
    # The scanner still bites: a factory-consumed packet carrying the impostor's
    # role inside a visible-player id (the class the recursive value scanner
    # exists for) must trip the factory-mode scan. Real games never mint such a
    # packet, so it is planted here as a real ObservationPacket the scan sees.
    poisoned = ObservationPacket(
        tick=0,
        agent_id="p-1",
        self_state=SelfView(room="STORAGE", role="CREWMATE", pending_task_id=None),
        visible_players=(
            PlayerView(id="crew_role_leak_fixture", room="STORAGE", action=None),
        ),
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )
    with pytest.raises(AssertionError, match=r"\$\.visible_players\[0\]\.id"):
        assert_no_factory_packet_leaks([(poisoned, [])])


def test_leak_factory_mode_witness_check_trips_on_unwitnessed_kill() -> None:
    # The witness-permission check bites in factory mode too: a PlayerView stamped
    # with a `kill` action for an observer who is NOT in the KilledEvent's
    # witnesses must trip, catching an unwitnessed-kill leak a learned mover could
    # reach. (Real packets never do this; it is planted here.)
    poisoned = ObservationPacket(
        tick=3,
        agent_id="p-2",
        self_state=SelfView(room="STORAGE", role="CREWMATE", pending_task_id=None),
        visible_players=(PlayerView(id="p-3", room="STORAGE", action="kill"),),
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )
    # A KilledEvent by p-3 whose witnesses do NOT include the observer p-2.
    kill_event = KilledEvent(
        type="Killed",
        tick=3,
        actor="p-3",
        target="p-1",
        room="STORAGE",
        witnesses=("p-4",),
    )
    with pytest.raises(AssertionError, match="unwitnessed 'kill'"):
        assert_no_factory_packet_leaks([(poisoned, [kill_event])])
