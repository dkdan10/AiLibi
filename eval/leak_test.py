"""The pytest wrapper around the packet leak scanners (Task 19.24).

The scanners themselves live in :mod:`eval.leak_scan`, which imports no pytest
so the ML champion gate can call them without dragging a dev-only dependency
onto a production path. This module owns what only pytest can run: the
scripted-fixture sweep, the factory-mode sweeps, and — the crown jewel — the
PLANTED-LEAK self-tests, each of which asserts a scanner still BITES on a
deliberately poisoned packet. The move was import-path only; every test body
below is the one that guarded the boundary before it.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import cast

import pytest
from pydantic import BaseModel, ConfigDict

from agents.base import AgentInterface
from engine.actions import Action
from engine.entities import PlayerId, Role
from engine.events import EngineEvent, KilledEvent, MovedEvent
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from eval.leak_scan import (
    _ACTION_ADAPTER,
    _FORBIDDEN_BODY_FIELDS,
    _FORBIDDEN_VISIBLE_PLAYER_ACTIONS,
    _FORBIDDEN_VISIBLE_PLAYER_FIELDS,
    JsonValue,
    PacketContext,
    PacketRecord,
    _action_is_permitted_by_witness_event,
    _assert_no_recursive_hidden_fields,
    _assert_no_role_bearing_values,
    _assert_owned_task_discipline,
    _assert_owned_tasks_match_engine_truth,
    _format_json_path,
    _walk_json,
    assert_memory_render_role_disclosure_is_entitled,
    assert_moved_players_are_witness_gated,
    assert_no_factory_packet_leaks,
    assert_visible_entities_match_engine_truth,
    scan_factory_packets,
)
from observation.action_intent import ActionIntent, MoveIntent, WaitIntent
from observation.packet import (
    GlobalView,
    MovedPlayerView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.game import (
    AgentFactory,
    build_default_agent_factory,
)
from tests._helpers.world_state import scripted_initial_world_state

# Re-exports (Task 19.24). The scanners moved to :mod:`eval.leak_scan`, but this
# module remains the address several suites mirror the canonical leak scan from
# (``tests/api/test_leak.py``, ``tests/agents/test_memory_rendering.py``,
# ``tests/training/test_learned_factory_acceptance.py``). Naming them here keeps
# those imports resolving against the module the docs and docstrings point at,
# while the definitions live in the pytest-free library.
__all__ = [
    "JsonValue",
    "PacketContext",
    "_assert_no_recursive_hidden_fields",
    "_assert_no_role_bearing_values",
    "_format_json_path",
    "_walk_json",
    "assert_memory_render_role_disclosure_is_entitled",
    "assert_moved_players_are_witness_gated",
    "assert_no_factory_packet_leaks",
    "assert_visible_entities_match_engine_truth",
    "scan_factory_packets",
]

_SCRIPTED_GAMES = (
    "scripted_game_basic_tasks.json",
    "scripted_game_kill_report_meeting.json",
    "scripted_game_vent_and_emergency.json",
)


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
) -> list[PacketRecord]:
    fixture_path = Path("tests/fixtures") / fixture_name
    script = _ScriptedGame.model_validate_json(fixture_path.read_text(encoding="utf-8"))

    game_map = load_canonical_map()
    state: WorldState = scripted_initial_world_state(seed=script.seed)
    audit_path = tmp_path / f"audit_{fixture_name}.jsonl"
    observation_service = ObservationService(
        game_map=game_map, audit_log_path=audit_path
    )
    actions_by_tick = _fixture_actions(script)

    packet_records: list[PacketRecord] = []
    for tick in range(max(actions_by_tick, default=-1) + 1):
        assert state.tick == tick
        state, events = advance_tick(
            state,
            actions_by_tick.get(tick, []),
            game_map=game_map,
        )
        # The tick the packets below are built on, carried alongside them so the
        # sweep can ask the entitlement question as well as the shape ones.
        context = PacketContext(
            engine_events=events, world_state=state, game_map=game_map
        )
        for player_id, player in state.players.items():
            if player.alive:
                packet = observation_service.build_packet(
                    world_state=state,
                    agent_id=player_id,
                    engine_events=events,
                )
                # The STRONG cross-player engine-truth check (Task 15.22): the
                # recipient's owned_task_ids match per-tick engine truth and no
                # foreign task id appears anywhere in the packet.
                _assert_owned_tasks_match_engine_truth(
                    packet, state=state, game_map=game_map
                )
                packet_records.append((packet, context))
        if state.phase == "GAME_OVER":
            break

    audit_packets = [
        json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    assert audit_packets == [
        packet.model_dump(mode="json") for packet, _ in packet_records
    ]
    return packet_records


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

        for packet, context in packet_records:
            packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
            _assert_no_recursive_hidden_fields(packet_dump)
            _assert_no_role_bearing_values(packet_dump)
            _assert_owned_task_discipline(packet)
            # Entitlement: the recipient saw exactly the players and bodies the
            # tick's world state allows it to -- the presence question the shape
            # scanners below cannot ask.
            assert_visible_entities_match_engine_truth(
                packet,
                state=context.world_state,
                game_map=context.game_map,
                engine_events=context.engine_events,
            )
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
                        engine_events=list(context.engine_events),
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
# UNSCANNED (the ml-spike Gap #7). The factory mode runs factory-built agents
# through FULL production games and applies the SAME leak scanners to every
# packet the encoder consumes; the walk and the scan live in
# :mod:`eval.leak_scan` (:func:`eval.leak_scan.scan_factory_packets`) because the
# ML champion gate calls them outside pytest. What lives HERE is the pytest half:
# the two clean-factory sweeps and the planted-leak self-tests that prove the
# scanners still bite.
# --------------------------------------------------------------------------- #


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


def _planted_context(engine_events: list[EngineEvent]) -> PacketContext:
    """The tick a HAND-PLANTED packet is scanned against.

    A poisoned packet is minted by hand, so it has no game behind it; the
    scanner still needs a world to state entitlement against. The scripted
    fixtures' opening state (p-1..p-4 in the spawn room, p-3 the impostor) is
    that world, which also keeps the plant honest -- each test below trips on
    the channel it poisons, not on a context mismatch.
    """

    return PacketContext(
        engine_events=engine_events,
        world_state=scripted_initial_world_state(seed=0),
        game_map=load_canonical_map(),
    )


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
        assert_no_factory_packet_leaks([(poisoned, _planted_context([]))])


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
        assert_no_factory_packet_leaks([(poisoned, _planted_context([kill_event]))])


def test_owned_task_discipline_trips_on_composite_instance_id() -> None:
    # The owned-task discipline bites: an owned id carrying a ':' composite (the
    # owner prefix leaks ownership) must trip. Real packets never mint this; it is
    # planted here as a real ObservationPacket the scan sees.
    poisoned = ObservationPacket(
        tick=0,
        agent_id="p-2",
        self_state=SelfView(
            room="ADMIN",
            role="CREWMATE",
            pending_task_id=None,
            owned_task_ids=("p-2:swipe_card",),
        ),
        visible_players=(),
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
    with pytest.raises(AssertionError, match="composite instance id"):
        _assert_owned_task_discipline(poisoned)


def test_owned_task_discipline_trips_on_unsorted_tuple() -> None:
    # An unsorted owned tuple breaks the replay-stable byte shape and must trip.
    poisoned = ObservationPacket(
        tick=0,
        agent_id="p-3",
        self_state=SelfView(
            room="ADMIN",
            role="CREWMATE",
            pending_task_id=None,
            owned_task_ids=("swipe_card", "align_engine_output"),
        ),
        visible_players=(),
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
    with pytest.raises(AssertionError, match="must be sorted ascending"):
        _assert_owned_task_discipline(poisoned)


def test_owned_task_discipline_trips_on_pending_absent_from_owned() -> None:
    # A pending task set but ABSENT from owned_task_ids breaks the role-blind
    # consistency invariant -- both for a non-empty owned set that lacks it and
    # for the empty-owned edge (pending set, owned ()), which must trip identically.
    poisoned = ObservationPacket(
        tick=0,
        agent_id="p-4",
        self_state=SelfView(
            room="ADMIN",
            role="CREWMATE",
            pending_task_id="swipe_card",
            owned_task_ids=("submit_scan",),
        ),
        visible_players=(),
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
    with pytest.raises(AssertionError, match="is not a member of owned_task_ids"):
        _assert_owned_task_discipline(poisoned)

    poisoned_empty_owned = ObservationPacket(
        tick=0,
        agent_id="p-4",
        self_state=SelfView(
            room="ADMIN",
            role="CREWMATE",
            pending_task_id="swipe_card",
            owned_task_ids=(),
        ),
        visible_players=(),
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
    with pytest.raises(AssertionError, match="is not a member of owned_task_ids"):
        _assert_owned_task_discipline(poisoned_empty_owned)


# --------------------------------------------------------------------------- #
# The movement-perception witness gate (Task 19.24).
#
# ``moved_players`` was the one packet channel with ZERO leak-suite coverage,
# and it is the channel whose own docstring
# (``observation/service.py::_moved_players_for_agent``) narrates a SHIPPED
# gating bug: gating on the post-advance ``visible_player_ids`` — the actor's
# ARRIVAL room — leaked the transition's ORIGIN to an observer who only saw the
# actor arrive, and dropped the departure for the observer left behind who
# actually saw it leave. These planted-leak self-tests are the proof the new
# scanner detects exactly that bug class; the breadth sweep over real service
# packets lives in ``tests/observation/test_leak_property.py``.
# --------------------------------------------------------------------------- #


def _moved_packet(
    *,
    agent_id: PlayerId,
    room: str,
    moved: tuple[MovedPlayerView, ...],
) -> ObservationPacket:
    """A minimal packet for the observer ``agent_id``, carrying ``moved``."""

    return ObservationPacket(
        tick=4,
        agent_id=agent_id,
        self_state=SelfView(room=room, role="CREWMATE", pending_task_id=None),
        visible_players=(),
        visible_bodies=(),
        audible_events=(),
        moved_players=moved,
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )


_MOVE_EVENT = MovedEvent(
    type="Moved", tick=4, actor="p-3", from_room="STORAGE", to_room="ENGINEERING"
)


def test_moved_players_scanner_accepts_a_witnessed_departure() -> None:
    # The legitimate case the gate exists to permit: p-2 stayed behind in
    # STORAGE and SAW p-3 leave it, so the transition (origin included) is p-2's
    # to know. The scanner must not fire.
    witnessed = _moved_packet(
        agent_id="p-2",
        room="STORAGE",
        moved=(MovedPlayerView(id="p-3", from_room="STORAGE", to_room="ENGINEERING"),),
    )
    assert_moved_players_are_witness_gated(
        witnessed, engine_events=[_MOVE_EVENT], visible_rooms=("STORAGE",)
    )


def test_moved_players_scanner_trips_on_arrival_only_observer() -> None:
    # THE planted leak — the exact prior bug: an observer standing in the
    # ARRIVAL room (ENGINEERING) who never saw STORAGE is handed the origin it
    # could not witness. Arrival-gated code mints this packet; the departure
    # gate must reject it.
    poisoned = _moved_packet(
        agent_id="p-2",
        room="ENGINEERING",
        moved=(MovedPlayerView(id="p-3", from_room="STORAGE", to_room="ENGINEERING"),),
    )
    with pytest.raises(AssertionError, match="unwitnessed departure"):
        assert_moved_players_are_witness_gated(
            poisoned, engine_events=[_MOVE_EVENT], visible_rooms=("ENGINEERING",)
        )


def test_moved_players_scanner_trips_on_transition_with_no_engine_event() -> None:
    # A transition no ``MovedEvent`` backs is fabricated — either invented
    # wholesale or a STALE origin stitched onto a current arrival. Visibility
    # alone cannot catch it (the observer does see STORAGE), so the
    # traceability check is what bites.
    poisoned = _moved_packet(
        agent_id="p-2",
        room="STORAGE",
        moved=(MovedPlayerView(id="p-3", from_room="STORAGE", to_room="MEDBAY"),),
    )
    with pytest.raises(AssertionError, match="no matching MovedEvent this tick"):
        assert_moved_players_are_witness_gated(
            poisoned,
            engine_events=[_MOVE_EVENT],
            visible_rooms=("STORAGE", "MEDBAY"),
        )


def test_moved_players_scanner_trips_on_a_no_op_move() -> None:
    # ``from_room == to_room`` is not a transition; surfacing one would tell an
    # observer an actor "moved" when it stood still. The service skips these, so
    # a packet carrying one is planted here.
    poisoned = _moved_packet(
        agent_id="p-2",
        room="STORAGE",
        moved=(MovedPlayerView(id="p-3", from_room="STORAGE", to_room="STORAGE"),),
    )
    no_op_event = MovedEvent(
        type="Moved", tick=4, actor="p-3", from_room="STORAGE", to_room="STORAGE"
    )
    with pytest.raises(AssertionError, match="no-op move"):
        assert_moved_players_are_witness_gated(
            poisoned, engine_events=[no_op_event], visible_rooms=("STORAGE",)
        )


# --------------------------------------------------------------------------- #
# The dependency partition (Task 19.24).
#
# The whole point of splitting the scanners out is that the ML champion gate can
# reach them without pytest. That claim decays silently — someone adds a
# ``pytest.mark`` import to a module ``eval.leak_scan`` pulls in, and nothing
# fails until a runtime-only install breaks in production. So it is pinned here,
# in the pytest half, where a reader looking at the split finds the proof next to
# the thing it is about. The manual form is the 19.7 idiom
# (``uv run --no-dev --exact python -c "import ..."``, which needs a dev-free
# environment); this is the hermetic form of the same claim, and it runs every
# time.
# --------------------------------------------------------------------------- #

# Import the library and BOTH production consumers with the dev toolchain made
# unimportable, so a transitive dev import fails with a traceback naming the
# offender rather than a bare "pytest is in sys.modules" at the end.
_IMPORT_PURITY_PROBE = '''
import sys

_BLOCKED = ("pytest", "_pytest", "hypothesis", "mypy")


class _RefuseDevImports:
    """A meta-path finder that makes the dev toolchain unimportable."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in _BLOCKED:
            raise ImportError(
                f"{fullname} reached a production import path "
                "(the runtime/dev dependency partition forbids it)"
            )
        return None


sys.meta_path.insert(0, _RefuseDevImports())

import eval.leak_scan
import training.bakeoff.harness
import training.crew.scorer

assert callable(eval.leak_scan.scan_factory_packets)
assert training.bakeoff.harness.scan_factory_packets is (
    eval.leak_scan.scan_factory_packets
)
assert training.crew.scorer.scan_factory_packets is (
    eval.leak_scan.scan_factory_packets
)
leaked = sorted(name for name in sys.modules if name.split(".")[0] in _BLOCKED)
assert not leaked, f"dev modules on the production path: {leaked}"
print("PARTITION_OK")
'''


def test_leak_scan_and_its_production_consumers_import_without_pytest() -> None:
    # A SUBPROCESS is load-bearing: this very process is pytest, so an in-process
    # check would pass vacuously with pytest already in sys.modules.
    probe = subprocess.run(
        [sys.executable, "-c", _IMPORT_PURITY_PROBE],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )

    assert probe.returncode == 0, (
        "eval.leak_scan or one of its production consumers still reaches the dev "
        f"toolchain:\n{probe.stderr}"
    )
    assert "PARTITION_OK" in probe.stdout


def test_the_pytest_wrapper_is_the_half_that_needs_pytest() -> None:
    # The control for the test above: importing THIS module under the same block
    # must FAIL. Without it, a probe that silently stopped exercising the block
    # (a typo in the finder, say) would keep reporting a partition that is not
    # being enforced.
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            _IMPORT_PURITY_PROBE.replace(
                "import eval.leak_scan\n", "import eval.leak_test\n"
            ),
        ],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )

    assert probe.returncode != 0
    assert "reached a production import path" in probe.stderr


def test_moved_players_scanner_can_gate_on_departure_time_visibility() -> None:
    # The tick-interior case (Codex P1 on PR #345): p-8 walks INTO the room p-3
    # walks OUT of, in the same tick. Post-move, p-8 stands in STORAGE and "sees"
    # it; at the moment of departure it was still in ENGINEERING and saw nothing.
    #
    # Both answers are asserted here because the difference is a MODELING choice
    # about the interior of an atomic tick, not a bug with one right answer: the
    # service gates on the post-move set today, and this scanner can express the
    # stricter pre-move rule for whoever flips it. What must never happen is the
    # strict rule silently not biting.
    arrival_only = _moved_packet(
        agent_id="p-8",
        room="STORAGE",
        moved=(MovedPlayerView(id="p-3", from_room="STORAGE", to_room="ENGINEERING"),),
    )
    departure = MovedEvent(
        type="Moved", tick=4, actor="p-3", from_room="STORAGE", to_room="ENGINEERING"
    )

    # The rule observation/service.py implements: p-8 can see STORAGE now.
    assert_moved_players_are_witness_gated(
        arrival_only, engine_events=[departure], visible_rooms=("STORAGE",)
    )

    # The stricter rule: at the departure p-8 was still in ENGINEERING.
    with pytest.raises(AssertionError, match="cannot see at the departure"):
        assert_moved_players_are_witness_gated(
            arrival_only,
            engine_events=[departure],
            visible_rooms=("STORAGE",),
            departure_visible_rooms=("ENGINEERING",),
        )


# --------------------------------------------------------------------------- #
# Planted-leak self-tests for the memory-render role-disclosure gate.
#
# The allowance this gate carries is the narrowest one in the project: a role
# word may name an EJECTED player, from that player's ejection tick onward, and
# in no other case. Each leg below plants exactly one of the readings the gate
# must refuse, so the allowance cannot silently widen into "roles may appear in
# memory renders".
# --------------------------------------------------------------------------- #

_ENTITLED_RENDER = """## Your role: CREWMATE

## Meetings so far:
- Meeting 1 (tick 14): p-4 EJECTED 7-1 — p-4 was an IMPOSTOR. 1 impostor remains.
- Meeting 2 (tick 27): no ejection (6 skip). 1 impostor remains.

## Recent observations (most salient first):
- [tick 3] You saw p-4 in CAFETERIA.

## Open contradictions:
- p-3 witnessed p-8 vent in ENGINEERING at tick 22; venting is impostor-only.
"""


def test_memory_render_scanner_accepts_an_entitled_post_ejection_disclosure() -> None:
    # The confirm-ejects announcement, read after the ejection that made it
    # public. The own-role line and the lowercase rules prose ride along.
    assert_memory_render_role_disclosure_is_entitled(
        _ENTITLED_RENDER, ejection_ticks={"p-4": 14}, render_tick=30
    )


def test_memory_render_scanner_trips_on_a_pre_ejection_disclosure() -> None:
    with pytest.raises(AssertionError, match="before their ejection at tick 14"):
        assert_memory_render_role_disclosure_is_entitled(
            _ENTITLED_RENDER, ejection_ticks={"p-4": 14}, render_tick=13
        )


def test_memory_render_scanner_trips_on_a_living_players_role() -> None:
    # p-9 is alive: no ejection ever made their role public.
    planted = _ENTITLED_RENDER.replace(
        "p-4 EJECTED 7-1 — p-4 was an IMPOSTOR.",
        "p-9 EJECTED 7-1 — p-9 was an IMPOSTOR.",
    )
    with pytest.raises(AssertionError, match="who the table never ejected"):
        assert_memory_render_role_disclosure_is_entitled(
            planted, ejection_ticks={"p-4": 14}, render_tick=30
        )


def test_memory_render_scanner_trips_on_a_kill_victims_role() -> None:
    # A kill victim is absent from the ledger by construction — a kill reveals
    # nothing, which is exactly why their role may never render.
    planted = _ENTITLED_RENDER.replace(
        "p-4 EJECTED 7-1 — p-4 was an IMPOSTOR.",
        "p-2 EJECTED 7-1 — p-2 was a CREWMATE.",
    )
    with pytest.raises(AssertionError, match="who the table never ejected"):
        assert_memory_render_role_disclosure_is_entitled(
            planted, ejection_ticks={"p-4": 14}, render_tick=30
        )


def test_memory_render_scanner_trips_on_a_role_outside_the_entitled_grammar() -> None:
    # The same true fact, smuggled onto an observation line instead of the
    # meetings block: still a disclosure, still refused.
    planted = _ENTITLED_RENDER.replace(
        "- [tick 3] You saw p-4 in CAFETERIA.",
        "- [tick 3] You saw p-4 (IMPOSTOR) in CAFETERIA.",
    )
    with pytest.raises(AssertionError, match="outside the entitled grammar"):
        assert_memory_render_role_disclosure_is_entitled(
            planted, ejection_ticks={"p-4": 14}, render_tick=30
        )


def test_memory_render_scanner_accepts_the_agents_own_role_on_its_own_kill_line() -> (
    None
):
    # ``You (IMPOSTOR) killed …`` is the agent talking about ITSELF, the same
    # entitlement the ``## Your role:`` header carries.
    own_kill = _ENTITLED_RENDER.replace(
        "## Your role: CREWMATE", "## Your role: IMPOSTOR"
    ).replace(
        "- [tick 3] You saw p-4 in CAFETERIA.",
        "- [tick 6] You (IMPOSTOR) killed p-2 in STORAGE.",
    )
    assert_memory_render_role_disclosure_is_entitled(
        own_kill, ejection_ticks={"p-4": 14}, render_tick=30
    )


def test_memory_render_scanner_trips_on_the_same_shape_about_another_player() -> None:
    # The self-attributed form is entitled because it names the READER; the same
    # parenthetical about a third party is a disclosure and is refused.
    planted = _ENTITLED_RENDER.replace(
        "- [tick 3] You saw p-4 in CAFETERIA.",
        "- [tick 6] p-7 (IMPOSTOR) killed p-2 in STORAGE.",
    )
    with pytest.raises(AssertionError, match="outside the entitled grammar"):
        assert_memory_render_role_disclosure_is_entitled(
            planted, ejection_ticks={"p-4": 14}, render_tick=30
        )


def test_memory_render_scanner_trips_when_the_tally_and_the_role_disagree() -> None:
    # A line that ejects one player and announces ANOTHER's role fails the
    # back-reference: the disclosure must belong to the ejection that carried it.
    planted = _ENTITLED_RENDER.replace(
        "p-4 EJECTED 7-1 — p-4 was an IMPOSTOR.",
        "p-4 EJECTED 7-1 — p-6 was an IMPOSTOR.",
    )
    with pytest.raises(AssertionError, match="outside the entitled grammar"):
        assert_memory_render_role_disclosure_is_entitled(
            planted, ejection_ticks={"p-4": 14, "p-6": 14}, render_tick=30
        )
