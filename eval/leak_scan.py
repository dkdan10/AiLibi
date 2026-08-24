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
import re
import tempfile
from collections.abc import Collection, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, TypeAlias, cast

from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import RoomId
from engine.events import (
    EngineEvent,
    KilledEvent,
    MovedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.visibility import compute_visibility_for_player
from engine.world import Map, WorldState, load_canonical_map
from eval.replay_walk import (
    MeetingOpened,
    ReplayWalkConfig,
    TickOpened,
    WalkViolation,
    walk_replay,
)
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from observation.packet import ObservationPacket
from observation.service import ObservationService, impostor_pretend_task_set
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    AgentFactory,
    HeadlessGame,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler

_FORBIDDEN_VISIBLE_PLAYER_FIELDS = frozenset({"role", "kill_attribution", "killed_by"})
_FORBIDDEN_BODY_FIELDS = frozenset({"killed_by", "kill_attribution", "player_id"})
_FORBIDDEN_VISIBLE_PLAYER_ACTIONS = frozenset({"sabotage"})
_FORBIDDEN_RECURSIVE_FIELD_NAMES = frozenset(
    {"killed_by", "kill_attribution", "player_id"}
)
_ALLOWED_RECURSIVE_FIELD_PATHS = frozenset({("self_state", "role")})
_FORBIDDEN_VALUE_SUBSTRINGS = ("impostor", "crewmate", "crew")
_ALLOWED_VALUE_PATHS = frozenset({("self_state", "role")})
# The recorded-action validator. The 19.25 walker deserializes for the factory
# walk below; this stays exported because the ``eval/leak_test.py`` wrapper's
# scripted-fixture runner validates its fixture actions through the same
# adapter (the 19.24 library surface).
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


def _witnessed_action_rooms(
    *,
    action: str | None,
    actor_id: str,
    agent_id: str,
    engine_events: Sequence[EngineEvent],
) -> frozenset[RoomId]:
    """The rooms an observer may be TOLD about for a witnessed ``kill`` / ``vent``.

    The room half of the witness allowance. ``observation/service.py`` stamps a
    witnessed action with the room of the EVENT, not the actor's current room,
    and a tick applies its actions in sequence — so an observer that witnessed a
    kill and then walked away in the same tick legitimately carries a room it can
    no longer see. Empty when the observer witnessed nothing, which is also the
    "not permitted" answer.
    """

    if action is None:
        return frozenset()
    rooms: set[RoomId] = set()
    for event in engine_events:
        if action == "kill" and isinstance(event, KilledEvent):
            if event.actor == actor_id and agent_id in event.witnesses:
                rooms.add(event.room)
        elif action == "vent" and isinstance(
            event, (VentEnteredEvent, VentExitedEvent)
        ):
            if event.actor != actor_id:
                continue
            if agent_id in event.source_witnesses:
                rooms.add(event.source_room)
            if agent_id in event.destination_witnesses:
                rooms.add(event.destination_room)
    return frozenset(rooms)


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
# The memory-render role-disclosure gate.
#
# The packet scanners above keep roles OUT of perception entirely. A rendered
# memory is the one surface where a role may legitimately appear, and it may
# appear in exactly two places: the agent's own ``## Your role:`` line, and the
# ``## Meetings so far:`` block's confirm-ejects announcement — which is public
# at the table on the same footing as ``dead_ids`` (DESIGN.md §4.7), but ONLY
# for a player the table actually ejected and ONLY from that meeting onward.
#
# The allowance is written as an ENTITLEMENT CHECK, not as "roles may appear in
# renders": a living player's role, a kill victim's role (nobody saw it) and any
# disclosure dated before its own ejection all fail. This restates the rule
# independently of the code that renders it, which is the only reason it is a
# gate rather than prose.
# --------------------------------------------------------------------------- #

#: A role VALUE as every render writes one — uppercase, exactly as
#: ``## Your role: CREWMATE`` does. Lowercase prose about the rules ("venting is
#: impostor-only", the wording open-contradiction summaries carry) states no
#: player's role and is not a disclosure.
_MEMORY_ROLE_TOKEN = re.compile(r"IMPOSTOR|CREWMATE")

#: The two SELF-attributed forms, matched WHOLE-LINE. An agent is always
#: entitled to its own role, and both name the reader rather than a third party.
#: Whole-line matching is the load-bearing part: a line may carry the entitled
#: form and nothing else, so ``You (IMPOSTOR) killed p-2 (CREWMATE)`` is refused
#: rather than exempted by its entitled half.
_OWN_ROLE_LINES = (
    re.compile(r"## Your role: (?:IMPOSTOR|CREWMATE)"),
    re.compile(
        r"(?:- )?(?:\[obs [^\]]+\] )?\[tick \d+\] "
        r"You \((?:IMPOSTOR|CREWMATE)\) killed \S+ in \S+\."
    ),
)

#: The one entitled disclosure grammar, likewise matched WHOLE-LINE. The
#: back-reference is load-bearing too: the role must be announced for the SAME
#: player the tally ejected, so a line that ejects one player and reveals
#: another's role fails.
_ENTITLED_EJECTION_LINE = re.compile(
    r"(?:- )?Meeting \d+ \(tick \d+\): (?P<player>\S+) EJECTED(?: \d+-\d+)? — "
    r"(?P=player) was an? (?:IMPOSTOR|CREWMATE)\.(?: \d+ impostors? remains?\.)?"
)


def assert_memory_render_role_disclosure_is_entitled(
    render: str,
    *,
    ejection_ticks: Mapping[str, int],
    render_tick: int,
) -> None:
    """Assert every role a rendered memory states is one this agent may know.

    ``render`` is the output of ``agents.memory.store.render_for_prompt``;
    ``ejection_ticks`` maps a player id to the tick the table ejected them at
    (a KILLED player is absent — a kill reveals nothing); ``render_tick`` is the
    tick the render was taken at.

    A line carrying a role token must match ONE allowed grammar in full: a
    SELF-attributed form (the agent's own ``## Your role:`` header, or the
    own-kill line's ``You (IMPOSTOR) killed …``), or an entitled
    ``## Meetings so far:`` ejection line naming a player in ``ejection_ticks``
    whose ejection tick is at or before ``render_tick``. Each allowed grammar
    admits exactly ONE role token, so a line cannot buy an exemption for a
    smuggled second disclosure with an entitled first one. Anything else raises
    ``AssertionError`` quoting the offending line.
    """

    for line in render.splitlines():
        tokens = _MEMORY_ROLE_TOKEN.findall(line)
        if not tokens:
            continue
        assert len(tokens) == 1, (
            f"line states {len(tokens)} roles; every allowed grammar states one, "
            f"at tick {render_tick}: {line!r}"
        )
        if any(form.fullmatch(line) for form in _OWN_ROLE_LINES):
            continue
        match = _ENTITLED_EJECTION_LINE.fullmatch(line)
        assert match is not None, (
            f"role disclosed outside the entitled grammar at tick {render_tick}: "
            f"{line!r}"
        )
        player = match.group("player")
        ejected_at = ejection_ticks.get(player)
        assert ejected_at is not None, (
            f"role disclosed for {player!r}, who the table never ejected, "
            f"at tick {render_tick}: {line!r}"
        )
        assert ejected_at <= render_tick, (
            f"role disclosed for {player!r} at tick {render_tick}, before their "
            f"ejection at tick {ejected_at}: {line!r}"
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
    that reused the code under test would prove nothing).
    :func:`assert_packet_is_leak_clean` calls this on every packet it scans,
    reading the room set off the :class:`PacketContext` every caller now
    carries — so the ML champion gate scans ``moved_players`` as well.

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
# The entitlement oracle.
#
# Packet SHAPE, packet STRINGS and kill/vent witness PERMISSION are all a
# scanner can ask of a packet alone, and none of them answers the question the
# firewall is about: was this observer allowed to SEE these players and these
# bodies? A body filter that lost its room clause — every undiscovered corpse
# visible to everyone — leaves the packet perfectly well-shaped, so only world
# truth can catch it. Hence :class:`PacketContext`, and an entitlement rule
# re-derived from ``WorldState`` here.
#
# Independence is the whole design: the observer's ROOM SET comes from the
# engine (bounded here by a map-adjacency check of our own, so a widened room
# rule is caught), but the ENTITY filters are recomputed from ``WorldState``
# rather than read off ``VisibilityResult`` — a scanner that compared against
# ``visible_player_ids`` / ``visible_body_ids`` would inherit any mutation of
# the private filters that produce them and catch nothing.
#
# Provenance: audits/review-2026-08-19/B/verdicts.md claim 2.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class PacketContext:
    """The tick a packet was built on: its engine events plus the world behind them.

    Every packet producer already holds all three — the scripted runner, the
    property sweeps and the factory reconstruction each build the context where
    they build the packet — and the scanner needs all three to state
    entitlement. ``engine_events`` are the events the packet was BUILT with
    (the live loop hands agents the prior tick's events alongside the current
    state), and ``world_state`` is the state it was built from.
    """

    engine_events: Sequence[EngineEvent]
    world_state: WorldState
    game_map: Map


def assert_visible_entities_match_engine_truth(
    packet: ObservationPacket,
    *,
    state: WorldState,
    game_map: Map,
    engine_events: Sequence[EngineEvent],
) -> None:
    """Cross-player engine-truth check: the observer saw EXACTLY what it may see.

    Four properties, each derived from ``WorldState`` rather than from
    ``engine.visibility``'s private entity filters:

    1. **The room set is bounded.** The observer's engine-reported
       ``visible_rooms`` contains its own room and nothing beyond that room's map
       neighbours — an independent adjacency bound, so a widened room rule trips
       here even though the room set itself is read from the engine.
    2. **Players are an EQUALITY.** ``visible_players`` equals the alive,
       non-vented, in-visible-room others, PLUS the named witness allowance
       below — never a superset, so an extra player is a leak, and never a
       subset, so a dropped one is a regression.
    3. **Bodies are an equality with NO allowance.** ``visible_bodies`` equals
       the undiscovered bodies standing in visible rooms.
    4. **Rooms are entitled too.** Every ``PlayerView.room`` and
       ``BodyView.room`` lies inside ``visible_rooms``, so a leak cannot ride an
       entitled id carrying an unentitled location — except for an allowance
       member, whose room must be a room it was WITNESSED in
       (:func:`_witnessed_action_rooms`), because a tick applies its actions in
       sequence and an observer can witness a kill and then walk away before the
       packet is built.

    THE WITNESS ALLOWANCE is real, named, and REQUIRED:
    ``observation/service.py::_visible_players`` adds any actor carrying an
    observed ``kill`` or ``vent`` to the packet even when the actor is not in the
    engine's ``visible_player_ids`` — a vented killer surfaces as
    ``('p-3', 'ADMIN', 'kill')``. That is intended kill attribution. The set is
    derived from the tick's events (every ``kill``/``vent`` actor whose event
    names this observer as a witness), never from the packet: reading it off
    ``visible_players`` would make the equality unable to see an OMISSION, since
    dropping the view would shrink both sides at once. Each member is then
    checked to carry the action the event justifies, to pass
    :func:`_action_is_permitted_by_witness_event`, and to name a room it was
    witnessed in — and the allowance is spelled out in the failure message so a
    future widening reads as a decision. A dead observer is entitled to nothing
    at all: its sets are empty by rule here, not by reading the engine's empty
    room tuple back.

    Raises ``AssertionError`` naming the observer and the offending ids.
    """

    agent = packet.agent_id
    observer = state.players.get(agent)
    assert observer is not None, (
        f"packet recipient {agent!r} is not a player in the world state it was "
        f"scanned against"
    )

    visible_rooms = compute_visibility_for_player(
        observer_id=agent, world_state=state, game_map=game_map
    ).visible_rooms
    room_set = set(visible_rooms)
    entitled_players: set[str] = set()
    entitled_bodies: set[str] = set()
    if observer.alive:
        adjacency_bound = {observer.room, *game_map.room_neighbors(observer.room)}
        assert observer.room in room_set, (
            f"{agent} visible_rooms {sorted(room_set)} omits its own room "
            f"{observer.room!r}"
        )
        assert room_set <= adjacency_bound, (
            f"{agent} visible_rooms {sorted(room_set)} reaches past "
            f"{observer.room!r} and its map neighbours "
            f"{sorted(adjacency_bound)}: {sorted(room_set - adjacency_bound)}"
        )
        entitled_players = {
            player_id
            for player_id, player in state.players.items()
            if player_id != agent
            and player.alive
            and not player.in_vent
            and player.room in room_set
        }
        entitled_bodies = {
            body_id
            for body_id, body in state.bodies.items()
            if body.discovered_by is None and body.room in room_set
        }

    events = list(engine_events)
    # The allowance is derived from the EVENTS, not from the packet. A
    # packet-derived set would be blind in one direction: drop a witnessed
    # actor's ``PlayerView`` and both sides of the equality shrink together, so
    # the observer silently loses first-hand evidence and the gate says nothing.
    witness_allowance = {
        event.actor
        for event in events
        if isinstance(event, (KilledEvent, VentEnteredEvent, VentExitedEvent))
        and agent in event.witnesses
    } - {agent}
    seen_players = {view.id for view in packet.visible_players}
    permitted_players = entitled_players | witness_allowance
    assert seen_players == permitted_players, (
        f"{agent} visible_players {sorted(seen_players)} != entitled "
        f"{sorted(entitled_players)} + witnessed kill/vent allowance "
        f"{sorted(witness_allowance)} — unentitled "
        f"{sorted(seen_players - permitted_players)}, missing "
        f"{sorted(permitted_players - seen_players)}"
    )

    seen_bodies = {view.id for view in packet.visible_bodies}
    assert seen_bodies == entitled_bodies, (
        f"{agent} visible_bodies {sorted(seen_bodies)} != undiscovered bodies in "
        f"{sorted(room_set)} {sorted(entitled_bodies)} — unentitled "
        f"{sorted(seen_bodies - entitled_bodies)}, missing "
        f"{sorted(entitled_bodies - seen_bodies)}"
    )

    for view in packet.visible_players:
        if view.id in witness_allowance:
            assert view.action in {"kill", "vent"}, (
                f"{agent} witnessed a kill/vent by {view.id!r} but the packet "
                f"stamps it {view.action!r} — the attribution is lost"
            )
            assert _action_is_permitted_by_witness_event(
                action=view.action,
                actor_id=view.id,
                agent_id=agent,
                engine_events=events,
            ), (
                f"{agent} allowance member {view.id!r} carries "
                f"{view.action!r}, which no engine event permits it"
            )
            witnessed_rooms = _witnessed_action_rooms(
                action=view.action,
                actor_id=view.id,
                agent_id=agent,
                engine_events=events,
            )
            assert view.room in witnessed_rooms, (
                f"{agent} packet places the witnessed {view.action!r} by "
                f"{view.id!r} in {view.room!r}, which is not a room {agent} "
                f"witnessed it in {sorted(witnessed_rooms)}"
            )
            continue
        assert view.room in room_set, (
            f"{agent} packet places {view.id!r} in {view.room!r}, outside its "
            f"visible rooms {sorted(room_set)}"
        )
    for body_view in packet.visible_bodies:
        assert body_view.room in room_set, (
            f"{agent} packet places body {body_view.id!r} in "
            f"{body_view.room!r}, outside its visible rooms {sorted(room_set)}"
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

# A factory-consumed packet paired with the tick it was built on — the engine
# events for the witness gates, the world state and map for entitlement. Two
# elements, not three: ``tests/eval/test_replay_walk.py`` unpacks these records
# as ``for packet, _ in records``, so the context rides as the second slot.
PacketRecord: TypeAlias = tuple[ObservationPacket, PacketContext]


def _raise_factory_walk_violation(violation: WalkViolation) -> NoReturn:
    """The ``leak-scan-factory`` profile's one declared policy, byte-preserved.

    The pre-19.25 walk indexed ``meeting_by_tick[entry.tick]`` directly, so a
    MEETING tick with no meeting row raised ``KeyError(tick)`` — impossible for
    a replay the harness itself just recorded, but preserved exactly.
    """

    raise KeyError(violation.tick)


# The named Task 19.25 profile (see eval/replay_walk.py's drift record): NO
# checks, deliberately — the factory walk scans packets from replays recorded
# moments earlier in the same process, and it performed neither hash
# verification nor doubled-record detection before 19.25; enabling either
# would change what it accepts.
_FACTORY_WALK_CONFIG: ReplayWalkConfig = ReplayWalkConfig(
    profile="leak-scan-factory",
    on_violation=_raise_factory_walk_violation,
    missing_meeting_row="violation",
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
    """Re-seed + replay one factory game, yielding (packet, context) records.

    :func:`eval.replay_walk.walk_replay` (the ``leak-scan-factory`` profile)
    threads ``last_events`` EXACTLY as ``HeadlessGame._run_loop`` does
    (``orchestrator/game.py``): each ``TickOpened`` carries the CURRENT
    (pre-advance) state plus the PRIOR tick's events — the same
    ``build_packet(engine_events=last_events)`` the live loop hands the agents —
    before that tick's recorded actions advance and any meeting applies. So the
    scanned stream is exactly the packets the encoder consumed: it includes the
    tick-0 opening packet and every post-meeting resume packet, and excludes
    the terminal GAME_OVER state (no agent decides there). Each packet is
    paired with the :class:`PacketContext` it was BUILT from — that tick's
    pre-advance state, its map, and the prior tick's events — so the witness
    gates read the right events and the entitlement oracle the right world.
    """

    records: list[PacketRecord] = []
    audit_path = audit_dir / f"_leak_audit_{replay_path.stem}.jsonl"
    service = ObservationService(game_map=game_map, audit_log_path=audit_path)
    try:
        for walk_event in walk_replay(
            replay_path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
            config=_FACTORY_WALK_CONFIG,
        ):
            if isinstance(walk_event, MeetingOpened):
                if walk_event.trigger is None:  # pragma: no cover - engine invariant
                    # Pre-19.25 this path crashed as a bare StopIteration from a
                    # ``next()`` with no default; StopIteration cannot propagate
                    # through the walker generator (PEP 479), so the fail-loud
                    # shape is an explicit error. Continuing would scan packets
                    # from a walk the engine contract does not cover.
                    raise RuntimeError(
                        f"{replay_path.name}: tick {walk_event.entry.tick} "
                        "entered MEETING without a MeetingTriggeredEvent "
                        "(engine invariant violation) — refusing to scan "
                        "packets reconstructed past it"
                    )
                continue
            if not isinstance(walk_event, TickOpened):
                continue
            # Build packets from the PRE-advance state + prior events (the live
            # loop's exact contract), before this tick's actions apply.
            state = walk_event.state
            context = PacketContext(
                engine_events=list(walk_event.last_events),
                world_state=state,
                game_map=game_map,
            )
            for player_id in sorted(state.players):
                if state.players[player_id].alive:
                    packet = service.build_packet(
                        world_state=state,
                        agent_id=player_id,
                        engine_events=walk_event.last_events,
                    )
                    records.append((packet, context))
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
    """Run ``agent_factory`` through full games; return (packet, context) records.

    Each game runs the REAL production loop (:class:`orchestrator.game.HeadlessGame`
    on the deterministic fake provider) to write a replay reflecting the factory's
    trajectory, then reconstructs that replay to recover the per-tick packets +
    the :class:`PacketContext` each was built from.
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
    packet: ObservationPacket, context: PacketContext
) -> None:
    """Apply the full leak scan to one packet — every channel, on one call.

    Five families of check, in the order they run:

    * **SHAPE** — the recursive hidden-field scanner, the ``visible_players`` /
      ``visible_bodies`` key-set + forbidden-action pins, the crew
      ``fellow_impostor_ids`` firewall, and the ``owned_task_ids`` discipline.
    * **STRINGS** — no role-bearing substring outside ``self_state.role``.
    * **WITNESS PERMISSION** — a ``PlayerView`` stamped ``kill`` / ``vent`` is
      backed by an engine event that names THIS observer as a witness.
    * **ENTITLEMENT** — the observer saw exactly the players and bodies the world
      state entitles it to
      (:func:`assert_visible_entities_match_engine_truth`): the presence check
      that shape alone cannot express.
    * **MOVEMENT GATING** — every ``moved_players`` entry is a transition whose
      departure room the observer could see
      (:func:`assert_moved_players_are_witness_gated`).

    ``context`` is REQUIRED: a caller that could omit the tick would silently
    reduce this to a shape scan, which is the gap the entitlement oracle exists
    to close. Raises ``AssertionError`` on any leak.
    """

    packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
    _assert_no_recursive_hidden_fields(packet_dump)
    _assert_no_role_bearing_values(packet_dump)
    events = list(context.engine_events)
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
    assert_visible_entities_match_engine_truth(
        packet,
        state=context.world_state,
        game_map=context.game_map,
        engine_events=context.engine_events,
    )
    # ``departure_visible_rooms=None`` asserts the rule observation/service.py
    # implements today (post-move rooms gate the departure); the stricter
    # pre-move rule is the parameter a future flip would pass.
    assert_moved_players_are_witness_gated(
        packet,
        engine_events=context.engine_events,
        visible_rooms=compute_visibility_for_player(
            observer_id=packet.agent_id,
            world_state=context.world_state,
            game_map=context.game_map,
        ).visible_rooms,
    )


def assert_no_factory_packet_leaks(records: Sequence[PacketRecord]) -> None:
    """Scan a reconstructed (packet, context) stream; raise on the first leak."""

    for packet, context in records:
        assert_packet_is_leak_clean(packet, context)


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
