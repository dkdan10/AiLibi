"""Entrant (2): learned utility scorer over the FSM's own options + ES (Task 15.15).

The conservative, bounded path of the paradigm comparison
(audits/post-phase-14-ML-planning.md §5.2 — the option vocabulary; §9 Option 1,
the RECOMMENDED bounded entry point): keep the scripted impostor FSM's option
GENERATION verbatim and replace exactly the arbitration it performs — the
``_scored_targets`` ranking (isolation × (1 − witness_risk) × cooldown, lexical
tie-break — agents/tactical/impostor_policy.py:937-1009) plus the option-level
choices the ladder makes (kill-now / stalk-toward / vent-exit choice /
cover-vent-or-move / fake-task / reposition-during-cooldown, the decide() ladder
at :261). A learned linear utility over a per-option feature vector re-ranks the
menu; the ``(1 + λ)`` ES core (:mod:`training.bakeoff.es`) climbs the shared
inner fitness (:func:`training.bakeoff.harness.inner_episode_fitness` —
tactically-reachable impostor terms + potential shaping, minus the anchor-CE
penalty toward the frozen FSM).

The entrant is STRUCTURALLY unable to emit an illegal or off-menu action:
:func:`enumerate_options` only ever materializes intents the FSM itself would
generate in the same state, and every one is submission-legal under
:func:`training.env.build_action_mask` (the harness re-validates the chosen
intent with the same emergency-free mask). The menu is a clean public function
so a committed test can enumerate it on fixture states and pin it.

Zero reimplementation drift: the option generation calls the FSM's own pure
STATIC helpers directly (``ImpostorPolicy._scored_targets`` /
``_confirmed_dead_from_bodies`` / ``_body_visible_rooms`` /
``_target_colocated_now`` / ``_non_teammate_witness_present`` /
``_crew_near_task_win`` / ``_sabotage_window_open`` / ``_active_sabotage`` /
``_vent_in_room``) and the module constant ``_REACTOR_SABOTAGE_KIND``, so the
menu stays byte-faithful to the scripted ladder — only the ARBITRATION (which
option to take) is learned. What the FSM computes with a fixed formula and a
short-circuiting priority ladder, the scorer computes with a learned linear head
over the option features and a single argmax.

Unlike entrant (3) this policy carries NO encoder-v2 / MLP genome: its feature
basis is the per-option :data:`OPTION_FEATURE_NAMES` vector, so there is no warm
start from the BC / policy-net family (the shapes do not align) — the ES core
seeds from its own deterministic Gaussian init.

No ``eval.*`` import may appear here (the harness firewall test AST-scans this
module): the harness computes every reported metric.
"""

from __future__ import annotations

import math
import tempfile
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Final, Literal, TypeAlias

from agents.memory.store import AgentMemory
from agents.tactical.impostor_policy import _REACTOR_SABOTAGE_KIND, ImpostorPolicy
from agents.tactical.pathing import find_path
from engine.world import Map, load_canonical_map
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    KillIntent,
    MoveIntent,
    SabotageIntent,
    VentIntent,
    WaitIntent,
)
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from training.bakeoff.es import ESConfig, evolve, k_seed_mean
from training.bakeoff.harness import (
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
    DEFAULT_ANCHOR_PENALTY_WEIGHT,
    DecisionTrace,
    TrainedCandidate,
    inner_episode_fitness,
    intent_key,
    load_train_seeds,
    rollout_candidate,
)
from training.determinism import PolicyFrame

# The impostor option alphabet, in fixed order (the kind one-hot block order and
# the OPTION_KINDS-indexed head layout below both key off this tuple). Each kind
# mirrors one lever the FSM's decide() ladder generates; the learned utility
# arbitrates between them where the ladder used a fixed priority.
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
# OPTION_KINDS order) then nine scalars. The scalars carry exactly the signal the
# FSM's own arbitration reads — ``isolation`` / ``witness_risk`` reproduce the
# ``_scored_targets`` score's two factors, ``cooldown_ready`` / ``cooldown_norm``
# gate the kill lever, ``path_hops_norm`` is the A* distance the FSM uses to pick
# a stalk step / exit vent, ``body_in_own_room`` is the COVER trigger,
# ``task_completion_percent`` / ``sabotage_active`` are the sabotage-lever
# context, and ``visible_players_norm`` is the crowd density — so a linear head
# can express (and re-weight) the scripted ladder's decisions.
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

# The policy encoder tag reported in the row and hashed by the 15.10 determinism
# harness. This entrant's feature basis is the per-option featurizer above — NOT
# the shared encoder-v2 memory vector the BC / policy-net / MAP-Elites family
# rides — so it carries its own version string.
ENCODER_VERSION: Final[str] = "impostor-option-features-v1"

# Distance normalizers: A* hop counts divide by this before the cap at 1.0, and
# the visible-player count divides by this crowd cap. Both keep the linear head's
# inputs in a bounded, roster-robust range.
_PATH_HOPS_CAP: Final[float] = 10.0
_VISIBLE_PLAYERS_CAP: Final[float] = 8.0


def utility_genome_length() -> int:
    """Flat genome length: one weight per option feature + a trailing bias."""

    return len(OPTION_FEATURE_NAMES) + 1


@dataclass(frozen=True)
class ImpostorOption:
    """One FSM-generated option the learned utility ranks (Task 15.15).

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


def _path_hops(public_map: PublicMapView, start: str, goal: str) -> int:
    """A* hop count from ``start`` to ``goal`` (unreachable = sentinel).

    Mirrors the FSM's ``_vent_distance``: an unreachable or unknown room sorts to
    a sentinel one larger than any possible path length, which the feature
    normalizer then caps at 1.0 — a disconnected topology never raises out of the
    featurizer.
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
    first step (the FSM's ``_move_toward`` ``path[1]``) plus ``len(path) - 1`` so
    the emitted ``MoveIntent`` is one hop while ``path_hops_norm`` carries the
    full distance. A ``find_path`` ValueError (unreachable / unknown goal) maps to
    ``None`` so the caller SKIPS the option — exactly the FSM's fall-through.
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
    *,
    sabotage_kinds: Sequence[str] = (),
) -> tuple[ImpostorOption, ...]:
    """The impostor option menu — the FSM's option GENERATION, arbitration removed.

    Mirrors the decide() ladder's structure (impostor_policy.py:261) but keeps
    EVERY option the state admits instead of short-circuiting on the ladder's
    fixed priority, so the learned utility (:class:`UtilityScorerPolicy`) does the
    arbitration the ladder hard-coded. Self facts come from the PACKET (the
    observable self surface): ``room`` / ``in_vent`` / ``pending_task_id`` /
    ``fellow_impostor_ids`` / ``cooldown``. Target scoring, dead/body/witness
    facts, and the sabotage predicates come from the FSM's own pure static
    helpers over the agent's live episodic events, so the menu is byte-faithful to
    the scripted ladder with zero reimplementation drift.

    The menu, mirroring the ladder branch-for-branch:

    * ``in_vent`` → ONLY ``vent_exit`` options, returned immediately (the ladder's
      highest-priority VENT_EXIT branch): the pool is ``_vent_exit``'s exact POOL
      construction — the current vent's connected + vent-roomed neighbors, filtered
      to body-free rooms (falling back to all connected), or a single exit-in-place
      option when the current vent has no connection. The learned scorer replaces
      ``_choose_exit_vent``'s nearest-target pick.
    * ``cover_vent`` / ``cover_move`` when a body sits in the impostor's own room
      (the KILL→COVER edge, ``_cover_or_vent`` / ``_cover``): vent iff a vent is
      here AND no non-teammate witness is co-present, and a one-step move to the
      alphabetically-first neighbor. These are ADDED to the menu (not returned):
      the ladder covers unconditionally, the scorer arbitrates cover-vs-hunt.
    * ``kill_now`` / ``stalk_toward`` per scored target: kill iff cooldown is 0,
      the target is co-located THIS tick, and the FSM's coordination invariant
      does not defer (``_defers_to_colocated_fellow`` — a lower-id co-located
      fellow impostor takes the kill; an id-ordered INVARIANT the menu mirrors,
      never a preference the scorer may override); stalk (one hop toward the
      sighting room) iff cooldown is 0 and the target is in another known room.
      The ``_scored_targets`` score is IGNORED — the learned utility re-ranks
      via ``isolation`` / ``witness_risk`` / ``path_hops_norm``. The FSM's
      witness gate (``co_present == 0``) is deliberately NOT mirrored: it is one
      factor of the exact ranking this entrant replaces, so witnessed targets
      stay on the menu with ``witness_risk`` carrying the signal.
    * ``sabotage`` iff the FSM's OWN trigger predicates hold (``_crew_near_task_win``
      AND ``_sabotage_window_open`` AND not ``_active_sabotage``) — the ``reactor``
      lever. The ladder's kill-available guard is arbitration, so it is dropped.
    * ``fake_task`` / ``reposition`` iff a pending pretend-task's room exists and
      holds no body (the ``_idle`` cover-discipline): do-task in place, else one hop
      toward it — generated regardless of cooldown, exactly like the ``_idle``
      fall-through (so ``reposition`` covers the reposition-during-cooldown lever).
    * ``wait`` — always, unless the in-vent branch returned first.

    ``sabotage_kinds`` is accepted for API symmetry with the policy's stored map
    facts and :func:`build_action_mask`, but the sabotage option's kind is fixed
    to the FSM's :data:`_REACTOR_SABOTAGE_KIND` constant (the ladder emits reactor
    unconditionally), so the parameter is not otherwise read. Raises
    :class:`ValueError` on empty memory, exactly like the FSM.
    """

    del sabotage_kinds  # covered by the FSM's _REACTOR_SABOTAGE_KIND constant.

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
    # never kills (``_defers_to_colocated_fellow`` — the two-impostors-one-tick
    # tie-break, an id-ordered invariant, not a preference), so no ``kill_now``
    # is generated; the witness gate (``best.co_present == 0``) is NOT mirrored
    # — it is one factor of the ``isolation × (1 − witness_risk)`` ranking this
    # entrant exists to replace, so witnessed targets stay on the menu with
    # their ``witness_risk`` feature carrying the signal.
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


def _softmax(scores: Sequence[float]) -> list[float]:
    """Numerically-stable softmax (peak-shifted), pure stdlib math."""

    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = math.fsum(exps)
    return [value / total for value in exps]


class UtilityScorerPolicy:
    """The frozen learned-utility candidate over the FSM option menu (Task 15.15).

    A pure function of ``(packet, public_map, memory, fsm_intent)``: crew
    decisions delegate to the scripted FSM (the crew side stays frozen this wave);
    impostor decisions enumerate the FSM option menu (:func:`enumerate_options`),
    score each option with a linear head (``dot(weights[:-1], features) +
    weights[-1]``), and realize the argmax (score DESC, canonical intent-key ASC —
    the repo's lexical tie-break idiom). Every tie is lexical and the arithmetic is
    stdlib ``math`` only, so the 15.10 double-run digests agree.

    ``encoder_version`` is :data:`ENCODER_VERSION`: this candidate's feature basis
    is the per-option featurizer, NOT the shared encoder-v2 memory vector, so it
    reports its own tag rather than a :class:`TacticalFeatureEncoder` version.
    """

    def __init__(
        self, *, weights: Sequence[float], game_map: Map | None = None
    ) -> None:
        expected = utility_genome_length()
        if len(weights) != expected:
            raise ValueError(f"weights length {len(weights)} != expected {expected}")
        self._weights = tuple(float(weight) for weight in weights)
        resolved_map = game_map if game_map is not None else load_canonical_map()
        # The map's sabotage vocabulary, kept for API symmetry with the menu /
        # the action mask (sorted for replay stability).
        self._sabotage_kinds = tuple(sorted(resolved_map.sabotages))

    @property
    def encoder_version(self) -> str:
        return ENCODER_VERSION

    @property
    def weights(self) -> tuple[float, ...]:
        return self._weights

    def _score(self, option: ImpostorOption) -> float:
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
    ) -> PolicyFrame:
        if packet.self_state.role != "IMPOSTOR":
            return PolicyFrame(
                agent_id=packet.agent_id,
                tick=packet.tick,
                features=(),
                logits=(),
                intent=fsm_intent,
            )
        options = enumerate_options(
            packet, public_map, memory, sabotage_kinds=self._sabotage_kinds
        )
        scores = [self._score(option) for option in options]
        best_option, _ = min(
            zip(options, scores, strict=True),
            key=lambda pair: (-pair[1], intent_key(pair[0].intent)),
        )
        features = tuple(chain.from_iterable(option.features for option in options))
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=features,
            logits=tuple(scores),
            intent=best_option.intent,
        )

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> Mapping[str, float]:
        if packet.self_state.role != "IMPOSTOR":
            return {intent_key(fsm_intent): 1.0}
        options = enumerate_options(
            packet, public_map, memory, sabotage_kinds=self._sabotage_kinds
        )
        scores = [self._score(option) for option in options]
        probabilities = _softmax(scores)
        distribution: dict[str, float] = {}
        for option, probability in zip(options, probabilities, strict=True):
            key = intent_key(option.intent)
            distribution[key] = distribution.get(key, 0.0) + probability
        return distribution


def build_utility_scorer_policy(
    weights: Sequence[float], *, game_map: Map | None = None
) -> UtilityScorerPolicy:
    """Construct the frozen policy around a flat genome (the artifact-reload seam)."""

    return UtilityScorerPolicy(weights=weights, game_map=game_map)


@dataclass(frozen=True)
class UtilityEsConfig:
    """The utility-scorer+ES entrant budget (recorded verbatim in the report)."""

    es: ESConfig
    anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
    num_players: int = BAKEOFF_NUM_PLAYERS
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE


def utility_es_budget(
    budget: str, *, anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
) -> UtilityEsConfig:
    """The two committed budgets: ``ci`` (seconds-scale) and ``full``."""

    train_seeds = load_train_seeds()
    if budget == "ci":
        return UtilityEsConfig(
            es=ESConfig(
                generations=1,
                population=2,
                sigma=0.3,
                seed=0,
                fitness_seeds=train_seeds[:1],
            ),
            anchor_weight=anchor_weight,
        )
    if budget == "full":
        return UtilityEsConfig(
            es=ESConfig(
                generations=20,
                population=12,
                sigma=0.3,
                seed=0,
                fitness_seeds=train_seeds[:6],
            ),
            anchor_weight=anchor_weight,
        )
    raise ValueError(f"unknown budget {budget!r}; expected 'ci' or 'full'")


class UtilityEsEntrant:
    """Entrant (2): the bounded utility scorer optimized by the shared ES core.

    Mirrors :class:`PolicyEsEntrant` but carries NO warm start: the option-feature
    genome (:data:`OPTION_FEATURE_NAMES` + bias) does not share a shape with the
    encoder-v2 MLP family, so the BC / policy-net champion cannot seed it — the ES
    core draws its own deterministic Gaussian init. Every generation's fitness is
    the shared inner fitness (:func:`inner_episode_fitness`) K-seed-averaged over
    the config's train seeds through :func:`rollout_candidate`, so this entrant
    optimizes the identical objective the other ES/QD entrants do (integration
    guard (a): one runner, one fitness, no protocol drift).
    """

    def __init__(self, *, config: UtilityEsConfig, game_map: Map | None = None) -> None:
        self._config = config
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._public_map = public_map_from_engine_map(self._game_map)

    @property
    def name(self) -> str:
        return "utility-es"

    def _seed_fitness(self, genome: tuple[float, ...], seed: int) -> float:
        policy = UtilityScorerPolicy(weights=genome, game_map=self._game_map)
        trace = DecisionTrace()
        with tempfile.TemporaryDirectory(prefix="ailibi-utility-es-") as tmp:
            rollout = rollout_candidate(
                policy,
                seed,
                output_dir=Path(tmp),
                game_map=self._game_map,
                num_players=self._config.num_players,
                num_impostors=self._config.num_impostors,
                tasks_per_crewmate=self._config.tasks_per_crewmate,
                trace=trace,
            )
        return inner_episode_fitness(
            rollout, trace, anchor_weight=self._config.anchor_weight
        )

    def train(self) -> TrainedCandidate:
        started = time.perf_counter()
        genome_length = utility_genome_length()
        fitness = k_seed_mean(self._seed_fitness, self._config.es.fitness_seeds)
        result = evolve(fitness, genome_length=genome_length, config=self._config.es)
        policy = UtilityScorerPolicy(weights=result.champion, game_map=self._game_map)
        return TrainedCandidate(
            entrant=self.name,
            policy=policy,
            weights=result.champion,
            config={
                "entrant": self.name,
                "anchor_weight": self._config.anchor_weight,
                "es": self._config.es.model_dump(mode="json"),
                "feature_names": list(OPTION_FEATURE_NAMES),
                "genome_length": genome_length,
                "encoder_version": policy.encoder_version,
            },
            train_wall_clock_s=time.perf_counter() - started,
            train_metadata={
                "warm_start_used": False,
                "es_digest": result.digest(),
                "num_evaluations": result.num_evaluations,
                "fitness_trace": [round(value, 4) for value in result.fitness_trace],
                "champion_fitness": round(result.champion_fitness, 4),
            },
        )


__all__ = [
    "ENCODER_VERSION",
    "OPTION_FEATURE_NAMES",
    "OPTION_KINDS",
    "ImpostorOption",
    "OptionKind",
    "UtilityEsConfig",
    "UtilityEsEntrant",
    "UtilityScorerPolicy",
    "build_utility_scorer_policy",
    "enumerate_options",
    "utility_es_budget",
    "utility_genome_length",
]
