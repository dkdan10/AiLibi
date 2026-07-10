"""The champion's pure-Python forward pass (Task 15.20).

The shipped inference path for the pause's champion — the ``utility-es``
learned utility scorer over the FSM's own impostor option menu
(audits/audit-phase-15-pause.md decision 1) — ported from the training-side
reference ``training/bakeoff/utility_es.py`` under the firewall contract:

- **No engine import.** The reference module's one live ``engine.world`` import
  fed only a ``_sabotage_kinds`` tuple that ``enumerate_options`` immediately
  discarded, so the port drops it entirely (the task-15.20 hint's snag (a)).
- **No training import.** The argmax tie-break key
  (``training.bakeoff.harness.intent_key``) is reimplemented verbatim below
  (snag (b)); everything else the menu needs is already ``agents/``-side.
- **No numpy / torch.** The forward pass is a 19-weight LINEAR scorer — a
  ``math.fsum`` dot product plus bias per option, no activation, no
  transcendental — so the decision-6 libm scope note is discharged by
  construction, and the decision-6 Q4 gate (a committed test, not an
  architecture change) pins BIT-EXACT equality of this pass against the
  training-side reference over the committed float-hex weights.

The accumulation is ported VERBATIM: ``math.fsum`` is correctly rounded and
order-independent, so the bit-exact hazard is not summation order — it is
substituting a naive ``sum()`` loop (or numpy) for ``fsum``, which diverges in
the last ULP. Do not "simplify" the ``fsum`` expression.

Zero reimplementation drift on the menu: exactly like the reference, option
generation calls the FSM's own pure static helpers
(``ImpostorPolicy._scored_targets`` / ``_confirmed_dead_from_bodies`` /
``_body_visible_rooms`` / ``_target_colocated_now`` /
``_non_teammate_witness_present`` / ``_crew_near_task_win`` /
``_sabotage_window_open`` / ``_active_sabotage`` / ``_vent_in_room``) and the
module constant ``_REACTOR_SABOTAGE_KIND``, so the menu stays byte-faithful to
the scripted ladder — only the ARBITRATION (which option to take) is learned.
The scripted FSM itself stays in-tree untouched as the default, the anchor,
the BC oracle, and the fallback.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import chain
from typing import Final, Literal, TypeAlias

from agents.memory.store import AgentMemory
from agents.tactical.impostor_policy import _REACTOR_SABOTAGE_KIND, ImpostorPolicy
from agents.tactical.pathing import find_path
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    KillIntent,
    MoveIntent,
    SabotageIntent,
    VentIntent,
    WaitIntent,
)
from observation.packet import ObservationPacket, PlayerId
from observation.public_map import PublicMapView

# The impostor option alphabet, in fixed order (the kind one-hot block order
# keys off this tuple). Ported verbatim from the training-side reference: each
# kind mirrors one lever the FSM's decide() ladder generates; the learned
# utility arbitrates between them where the ladder used a fixed priority.
OptionKind: TypeAlias = Literal[
    "kill_now",
    "stalk_toward",
    "vent_exit",
    "cover_vent",
    "cover_move",
    "sabotage",
    "fake_task",
    "reposition",
    "wait",
]
OPTION_KINDS: Final[tuple[OptionKind, ...]] = (
    "kill_now",
    "stalk_toward",
    "vent_exit",
    "cover_vent",
    "cover_move",
    "sabotage",
    "fake_task",
    "reposition",
    "wait",
)

# The per-option feature vector, in fixed order: the nine kind one-hots (in
# OPTION_KINDS order) then nine scalars — the ``impostor-option-features-v1``
# basis the committed champion's 19-weight genome (18 features + bias) dots
# against. The layout is FROZEN: it must equal the training-side
# ``OPTION_FEATURE_NAMES`` and the committed artifact's ``config.json``
# feature_names byte-for-byte, or the committed weights silently mean
# something else (the Q4 gate makes any drift loud).
OPTION_FEATURE_NAMES: Final[tuple[str, ...]] = tuple(
    f"kind_{kind}" for kind in OPTION_KINDS
) + (
    "isolation",
    "witness_risk",
    "cooldown_ready",
    "cooldown_norm",
    "path_hops_norm",
    "body_in_own_room",
    "task_completion_percent",
    "sabotage_active",
    "visible_players_norm",
)

# The champion's encoder tag — the per-option featurizer above, NOT the shared
# encoder-v2 memory vector — recorded verbatim in the provenance stamp.
ENCODER_VERSION: Final[str] = "impostor-option-features-v1"

# Flat genome length: one weight per option feature + a trailing bias.
GENOME_LENGTH: Final[int] = len(OPTION_FEATURE_NAMES) + 1

# Distance normalizers: A* hop counts divide by this before the cap at 1.0, and
# the visible-player count divides by this crowd cap. Both keep the linear
# head's inputs in a bounded, roster-robust range (verbatim reference values).
_PATH_HOPS_CAP: Final[float] = 10.0
_VISIBLE_PLAYERS_CAP: Final[float] = 8.0


@dataclass(frozen=True)
class ImpostorOption:
    """One FSM-generated option the learned utility ranks (ported, Task 15.20).

    ``kind`` is the menu slot (an :data:`OPTION_KINDS` member), ``intent`` the
    concrete submission-legal :class:`~observation.action_intent.ActionIntent`
    the FSM would emit for it, ``target_id`` the scored crewmate for the
    target-bearing kinds (``kill_now`` / ``stalk_toward``) or ``None``, and
    ``features`` the fixed-order :data:`OPTION_FEATURE_NAMES` vector the scorer
    dots its weights against.
    """

    kind: OptionKind
    intent: ActionIntent
    target_id: str | None
    features: tuple[float, ...]


@dataclass(frozen=True)
class LearnedDecisionFrame:
    """One learned-scorer decision: the option features, scores, and intent.

    The engine-free record of the ``(feature, score, intent)`` stream the 15.10
    determinism harness double-runs: ``features`` is the concatenation of every
    menu option's feature vector (menu order), ``scores`` the per-option utility
    scores in the same order, ``intent`` the realized argmax. For a non-impostor
    decision the streams are empty and ``intent`` is the FSM's own choice.
    """

    agent_id: PlayerId
    tick: int
    features: tuple[float, ...]
    scores: tuple[float, ...]
    intent: ActionIntent


def intent_key(intent: ActionIntent) -> str:
    """Canonical string key for one intent (the argmax tie-break alphabet).

    Reimplemented verbatim from ``training.bakeoff.harness.intent_key`` — a
    pure ``ActionIntent.model_dump`` serialization ``agents/`` may not import
    from ``training/`` (the firewall posture): ``type`` plus the salient
    payload field, so two intents compare equal iff they would drive the
    engine identically: ``move:STORAGE``, ``kill:p-3``, ``vent:v-1``,
    ``do_task:t-5``, ``report:b-1``, ``sabotage:reactor``, ``repair:reactor``,
    ``emergency``, ``wait``.
    """

    payload = intent.model_dump(mode="json").get("payload") or {}
    kind = intent.type
    if kind == "move":
        return f"move:{payload['to_room']}"
    if kind == "kill":
        return f"kill:{payload['target']}"
    if kind == "vent":
        return f"vent:{payload['vent_id']}"
    if kind == "do_task":
        return f"do_task:{payload['task_id']}"
    if kind == "report":
        return f"report:{payload['body_id']}"
    if kind == "sabotage":
        return f"sabotage:{payload['kind']}"
    if kind == "repair_sabotage":
        return f"repair:{payload['kind']}"
    return kind  # wait / emergency carry no distinguishing payload


def _path_hops(public_map: PublicMapView, start: str, goal: str) -> int:
    """A* hop count from ``start`` to ``goal`` (unreachable = sentinel).

    Mirrors the FSM's ``_vent_distance``: an unreachable or unknown room sorts
    to a sentinel one larger than any possible path length, which the feature
    normalizer then caps at 1.0 — a disconnected topology never raises out of
    the featurizer.
    """

    try:
        return len(find_path(public_map=public_map, start=start, goal=goal)) - 1
    except ValueError:
        return len(public_map.room_ids) + 1


def _movement_step(
    public_map: PublicMapView, start: str, goal: str
) -> tuple[str, int] | None:
    """The next-hop room and full A* distance toward ``goal`` (``None`` if none).

    ``goal`` must differ from ``start`` (the caller guards this); returns the
    first step (the FSM's ``_move_toward`` ``path[1]``) plus ``len(path) - 1``
    so the emitted ``MoveIntent`` is one hop while ``path_hops_norm`` carries
    the full distance. A ``find_path`` ValueError (unreachable / unknown goal)
    maps to ``None`` so the caller SKIPS the option — exactly the FSM's
    fall-through.
    """

    try:
        path = find_path(public_map=public_map, start=start, goal=goal)
    except ValueError:
        return None
    if len(path) < 2:
        return None
    return path[1], len(path) - 1


def enumerate_options(
    packet: ObservationPacket,
    public_map: PublicMapView,
    memory: AgentMemory,
) -> tuple[ImpostorOption, ...]:
    """The impostor option menu — the FSM's option GENERATION, arbitration removed.

    Ported verbatim from the training-side reference
    (``training/bakeoff/utility_es.py::enumerate_options``), whose docstring
    documents the branch-for-branch mirror of the decide() ladder; the one
    departure is the dropped ``sabotage_kinds`` parameter — the reference
    accepted it for API symmetry, fed it from an ``engine.world`` map, and then
    immediately discarded it (the sabotage option's kind is fixed to the FSM's
    :data:`_REACTOR_SABOTAGE_KIND` constant), so the firewall-clean port has no
    caller for it. Behavior is bit-identical; the Q4 gate drives both
    implementations over a recorded decision stream and asserts it.

    Self facts come from the PACKET (the observable self surface); target
    scoring, dead/body/witness facts, and the sabotage predicates come from the
    FSM's own pure static helpers over the agent's live episodic events, so the
    menu is byte-faithful to the scripted ladder with zero reimplementation
    drift. Raises :class:`ValueError` on empty memory or a missing cooldown,
    exactly like the reference (no silent fallbacks).
    """

    events = memory.episodic.recent(since_tick=0)
    if not events:
        raise ValueError(
            "utility-es option menu requires at least one episodic event in memory"
        )
    latest_tick = packet.tick
    latest_events = tuple(event for event in events if event.tick == events[-1].tick)

    self_state = packet.self_state
    own_room = self_state.room
    in_vent = self_state.in_vent
    pending_task_id = self_state.pending_task_id
    fellow_impostor_ids = frozenset(self_state.fellow_impostor_ids)
    cooldown = packet.cooldown
    if cooldown is None:
        raise ValueError(
            "utility-es option menu requires an integer cooldown on the packet"
        )
    actor = packet.agent_id

    body_rooms = ImpostorPolicy._body_visible_rooms(latest_events)

    # Decision-level feature constants (identical across every option this tick).
    cooldown_ready = 1.0 if cooldown == 0 else 0.0
    cooldown_norm = min(cooldown, int(_PATH_HOPS_CAP)) / _PATH_HOPS_CAP
    body_in_own_room = 1.0 if own_room in body_rooms else 0.0
    task_completion = packet.global_state.task_completion_percent
    sabotage_active = 1.0 if packet.global_state.sabotage_active else 0.0
    visible_players_norm = len(packet.visible_players) / _VISIBLE_PLAYERS_CAP

    def features_for(
        kind: OptionKind, *, co_present: int | None, path_hops: int | None
    ) -> tuple[float, ...]:
        one_hots = tuple(
            1.0 if kind == candidate else 0.0 for candidate in OPTION_KINDS
        )
        isolation = 1.0 / (1.0 + co_present) if co_present is not None else 0.0
        witness_risk = (
            co_present / (1.0 + co_present) if co_present is not None else 0.0
        )
        hops_norm = (
            min(path_hops / _PATH_HOPS_CAP, 1.0) if path_hops is not None else 0.0
        )
        return one_hots + (
            isolation,
            witness_risk,
            cooldown_ready,
            cooldown_norm,
            hops_norm,
            body_in_own_room,
            task_completion,
            sabotage_active,
            visible_players_norm,
        )

    def vent_exit_option(vent_id: str) -> ImpostorOption:
        vent_room = public_map.vent_rooms[vent_id]
        intent = VentIntent.model_validate(
            {"type": "vent", "actor": actor, "payload": {"vent_id": vent_id}}
        )
        return ImpostorOption(
            kind="vent_exit",
            intent=intent,
            target_id=None,
            features=features_for(
                "vent_exit",
                co_present=None,
                path_hops=_path_hops(public_map, own_room, vent_room),
            ),
        )

    # VENT_EXIT — an in-vent impostor is never left stuck; ONLY exit options, then
    # return (mirrors _vent_exit / _choose_exit_vent's POOL construction).
    if in_vent:
        current_vent = ImpostorPolicy._vent_in_room(public_map, own_room)
        if current_vent is None:
            raise ValueError(
                f"impostor is in_vent but no vent maps to its room: {own_room!r}"
            )
        connected = tuple(
            vent_id
            for vent_id in sorted(public_map.vent_graph.get(current_vent, ()))
            if vent_id in public_map.vent_rooms
        )
        if not connected:
            return (vent_exit_option(current_vent),)
        body_free = tuple(
            vent_id
            for vent_id in connected
            if public_map.vent_rooms[vent_id] not in body_rooms
        )
        pool = body_free if body_free else connected
        return tuple(vent_exit_option(vent_id) for vent_id in pool)

    options: list[ImpostorOption] = []

    # COVER — a body in the impostor's own room (KILL→COVER). Vent iff a vent is
    # here and no non-teammate witness; and a one-step move to the first neighbor.
    if own_room in body_rooms:
        vent_id = ImpostorPolicy._vent_in_room(public_map, own_room)
        if vent_id is not None and not ImpostorPolicy._non_teammate_witness_present(
            latest_events,
            own_room=own_room,
            fellow_impostor_ids=fellow_impostor_ids,
        ):
            options.append(
                ImpostorOption(
                    kind="cover_vent",
                    intent=VentIntent.model_validate(
                        {
                            "type": "vent",
                            "actor": actor,
                            "payload": {"vent_id": vent_id},
                        }
                    ),
                    target_id=None,
                    features=features_for(
                        "cover_vent", co_present=None, path_hops=None
                    ),
                )
            )
        neighbors = sorted(public_map.room_neighbors.get(own_room, ()))
        if neighbors:
            neighbor = neighbors[0]
            options.append(
                ImpostorOption(
                    kind="cover_move",
                    intent=MoveIntent.model_validate(
                        {
                            "type": "move",
                            "actor": actor,
                            "payload": {"to_room": neighbor},
                        }
                    ),
                    target_id=None,
                    features=features_for(
                        "cover_move",
                        co_present=None,
                        path_hops=_path_hops(public_map, own_room, neighbor),
                    ),
                )
            )

    # KILL / STALK — over the FSM's scored targets, whose .score is ignored (the
    # learned utility re-ranks). Kill iff co-located THIS tick; stalk otherwise.
    # The FSM's coordination INVARIANT is mirrored, its RANKING is not: when a
    # lower-id fellow impostor is co-located this tick the FSM structurally
    # never kills (``_defers_to_colocated_fellow`` — an id-ordered invariant,
    # not a preference), so no ``kill_now`` is generated; the witness gate
    # (``best.co_present == 0``) is NOT mirrored — it is one factor of the
    # ranking the learned utility replaces, so witnessed targets stay on the
    # menu with their ``witness_risk`` feature carrying the signal.
    defers_to_fellow = ImpostorPolicy(agent_id=actor)._defers_to_colocated_fellow(
        latest_events, own_room=own_room, fellow_impostor_ids=fellow_impostor_ids
    )
    targets = ImpostorPolicy._scored_targets(
        events,
        cooldown=cooldown,
        current_tick=latest_tick,
        confirmed_dead=ImpostorPolicy._confirmed_dead_from_bodies(events),
        fellow_impostor_ids=fellow_impostor_ids,
    )
    for target in targets:
        if (
            cooldown == 0
            and not defers_to_fellow
            and ImpostorPolicy._target_colocated_now(
                latest_events, target_id=target.player_id, own_room=own_room
            )
        ):
            options.append(
                ImpostorOption(
                    kind="kill_now",
                    intent=KillIntent.model_validate(
                        {
                            "type": "kill",
                            "actor": actor,
                            "payload": {"target": target.player_id},
                        }
                    ),
                    target_id=target.player_id,
                    features=features_for(
                        "kill_now", co_present=target.co_present, path_hops=None
                    ),
                )
            )
        if (
            cooldown == 0
            and target.room != own_room
            and target.room in public_map.room_ids
        ):
            step = _movement_step(public_map, own_room, target.room)
            if step is not None:
                next_room, hops = step
                options.append(
                    ImpostorOption(
                        kind="stalk_toward",
                        intent=MoveIntent.model_validate(
                            {
                                "type": "move",
                                "actor": actor,
                                "payload": {"to_room": next_room},
                            }
                        ),
                        target_id=target.player_id,
                        features=features_for(
                            "stalk_toward", co_present=target.co_present, path_hops=hops
                        ),
                    )
                )

    # SABOTAGE — the reactor lever, gated on the FSM's OWN trigger predicates only
    # (the kill-available arbitration is what the learned utility replaces).
    if (
        ImpostorPolicy._crew_near_task_win(events)
        and ImpostorPolicy._sabotage_window_open(events)
        and not ImpostorPolicy._active_sabotage(events)
    ):
        options.append(
            ImpostorOption(
                kind="sabotage",
                intent=SabotageIntent.model_validate(
                    {
                        "type": "sabotage",
                        "actor": actor,
                        "payload": {"kind": _REACTOR_SABOTAGE_KIND},
                    }
                ),
                target_id=None,
                features=features_for("sabotage", co_present=None, path_hops=None),
            )
        )

    # FAKE_TASK / REPOSITION — the _idle blend, cover-discipline gated (never route
    # onto a body). Generated regardless of cooldown, like the _idle fall-through.
    if pending_task_id is not None:
        task_room = public_map.task_locations.get(pending_task_id)
        if task_room is not None and task_room not in body_rooms:
            if own_room == task_room:
                options.append(
                    ImpostorOption(
                        kind="fake_task",
                        intent=DoTaskIntent.model_validate(
                            {
                                "type": "do_task",
                                "actor": actor,
                                "payload": {"task_id": pending_task_id},
                            }
                        ),
                        target_id=None,
                        features=features_for(
                            "fake_task", co_present=None, path_hops=None
                        ),
                    )
                )
            else:
                step = _movement_step(public_map, own_room, task_room)
                if step is not None:
                    next_room, hops = step
                    options.append(
                        ImpostorOption(
                            kind="reposition",
                            intent=MoveIntent.model_validate(
                                {
                                    "type": "move",
                                    "actor": actor,
                                    "payload": {"to_room": next_room},
                                }
                            ),
                            target_id=None,
                            features=features_for(
                                "reposition", co_present=None, path_hops=hops
                            ),
                        )
                    )

    # WAIT — always available (the _idle terminal fall-through).
    options.append(
        ImpostorOption(
            kind="wait",
            intent=WaitIntent.model_validate(
                {"type": "wait", "actor": actor, "payload": {}}
            ),
            target_id=None,
            features=features_for("wait", co_present=None, path_hops=None),
        )
    )
    return tuple(options)


class LearnedImpostorScorer:
    """The shipped champion forward pass (Task 15.20 public type).

    A pure function of ``(packet, public_map, memory, fsm_intent)``: crew
    decisions delegate to the scripted FSM (the crew side stays frozen this
    wave); impostor decisions enumerate the FSM option menu
    (:func:`enumerate_options`), score each option with the linear head
    (``fsum(weights[:-1] · features) + weights[-1]``), and realize the argmax
    (score DESC, canonical intent-key ASC — the repo's lexical tie-break
    idiom). Every tie is lexical and the arithmetic is stdlib ``math`` only, so
    the 15.10 double-run digests agree and the decision-6 Q4 gate can pin
    bit-exact equality against the training-side reference
    (``training/bakeoff/utility_es.py::UtilityScorerPolicy``).
    """

    def __init__(self, *, weights: Sequence[float]) -> None:
        if len(weights) != GENOME_LENGTH:
            raise ValueError(
                f"weights length {len(weights)} != expected {GENOME_LENGTH}"
            )
        self._weights = tuple(float(weight) for weight in weights)

    @property
    def encoder_version(self) -> str:
        return ENCODER_VERSION

    @property
    def weights(self) -> tuple[float, ...]:
        return self._weights

    def score(self, option: ImpostorOption) -> float:
        # VERBATIM port of the reference ``_score``: ``math.fsum`` is correctly
        # rounded, so this is the one expression a naive ``sum()`` or a float32
        # intermediate would silently diverge from in the last ULP.
        head = self._weights[:-1]
        bias = self._weights[-1]
        return (
            math.fsum(
                weight * feature
                for weight, feature in zip(head, option.features, strict=True)
            )
            + bias
        )

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> LearnedDecisionFrame:
        if packet.self_state.role != "IMPOSTOR":
            return LearnedDecisionFrame(
                agent_id=packet.agent_id,
                tick=packet.tick,
                features=(),
                scores=(),
                intent=fsm_intent,
            )
        options = enumerate_options(packet, public_map, memory)
        scores = [self.score(option) for option in options]
        best_option, _ = min(
            zip(options, scores, strict=True),
            key=lambda pair: (-pair[1], intent_key(pair[0].intent)),
        )
        features = tuple(chain.from_iterable(option.features for option in options))
        return LearnedDecisionFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=features,
            scores=tuple(scores),
            intent=best_option.intent,
        )


__all__ = [
    "ENCODER_VERSION",
    "GENOME_LENGTH",
    "OPTION_FEATURE_NAMES",
    "OPTION_KINDS",
    "ImpostorOption",
    "LearnedDecisionFrame",
    "LearnedImpostorScorer",
    "OptionKind",
    "enumerate_options",
    "intent_key",
]
