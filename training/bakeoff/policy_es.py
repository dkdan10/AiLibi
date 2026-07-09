"""Entrant (3): direct masked policy net + ES (Task 15.15).

The higher-ceiling path of the paradigm comparison
(audits/post-phase-14-ML-planning.md §9 Option 2, the recommended optimizer):
the encoder-v2 memory-carrying feature vector
(:class:`agents.tactical.features.TacticalFeatureEncoder`) feeds a pure-Python
one-hidden-layer tanh MLP (:func:`agents.tactical.features.mlp_forward` — the
same inference kernel the Wave-1 deployment posture pins) whose output head
scores the FULL masked intent space, and the ``(1 + λ)`` ES core
(:mod:`training.bakeoff.es`) climbs the shared inner fitness
(:func:`training.bakeoff.harness.inner_episode_fitness` — tactically-reachable
impostor terms + potential shaping, minus the anchor-CE penalty toward the
frozen FSM).

The head layout (:data:`KIND_SLOTS`) is one score per map room (a
``move-to-room`` slot; moving to the own room realizes as WAIT-in-place is NOT
used — the explicit ``wait`` slot is) plus one score per intent KIND. At each
impostor decision the legal-action mask (:func:`training.env.build_action_mask`)
enumerates the submission-legal intents; each maps to its head slot — a VENT
candidate additionally adds the room slot of its vent's room, so the vent-EXIT
choice among connected vents is learned through the room head rather than a
lexical vent-id tie (see :meth:`MaskedMlpPolicy._scored_candidates`) — and the
argmax (score desc, canonical intent-key asc — the repo's lexical tie-break
idiom) realizes the intent. The mask is computed with ``emergency_uses_remaining=0``:
the emergency intent needs a stateful uses tracker that a pure
:class:`~training.determinism.FramePolicy` cannot carry, and the scripted
impostor FSM never calls emergencies, so the candidate vocabulary excludes it —
a documented scoping, not a silent drop (the Goodhart probe covers
meeting-farming separately).

This module also owns :class:`MaskedMlpPolicy` — the shared genome family the
BC entrant clones into and the MAP-Elites entrant mutates, so the BC-then-ES
warm start (the spike's check-2 lesson) is an exact shape match.

No ``eval.*`` import may appear here (the harness firewall test AST-scans this
module): the harness computes every reported metric.
"""

from __future__ import annotations

import math
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from agents.memory.store import AgentMemory
from agents.tactical.features import (
    TacticalFeatureEncoder,
    mlp_forward,
    mlp_genome_length,
)
from engine.world import Map, load_canonical_map
from observation.action_intent import ActionIntent, MoveIntent, VentIntent
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
from training.env import build_action_mask

# The non-room head slots, in fixed order after the R sorted room slots. Every
# submission-legal intent kind an impostor can emit maps to exactly one slot:
# moves index into the room block; everything else into this kind block. The
# emergency intent is structurally excluded (module docstring).
KIND_SLOTS: Final[tuple[str, ...]] = (
    "kill",
    "vent",
    "sabotage",
    "do_task",
    "report",
    "repair_sabotage",
    "wait",
)


def head_size(public_map: PublicMapView) -> int:
    """Output-head width: one slot per sorted room + one per intent kind."""

    return len(public_map.room_ids) + len(KIND_SLOTS)


def policy_genome_length(
    public_map: PublicMapView, *, hidden: int, encoder: TacticalFeatureEncoder
) -> int:
    """Flat genome length of the shared masked-MLP family on ``public_map``."""

    return mlp_genome_length(
        input_dim=encoder.feature_dimension(public_map),
        hidden=hidden,
        output=head_size(public_map),
    )


def head_slot_for_intent(
    intent: ActionIntent, *, room_index: Mapping[str, int]
) -> int | None:
    """The head slot scoring ``intent`` (``None`` for off-vocabulary intents).

    Shared with the BC entrant: the clone's class label for an FSM decision is
    exactly the slot the policy family scores that intent with.
    """

    if isinstance(intent, MoveIntent):
        slot = room_index.get(intent.payload.to_room)
        return slot
    if intent.type == "emergency":
        return None
    try:
        return len(room_index) + KIND_SLOTS.index(intent.type)
    except ValueError:
        return None


def _softmax(scores: Sequence[float]) -> list[float]:
    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = math.fsum(exps)
    return [value / total for value in exps]


class MaskedMlpPolicy:
    """The shared frozen masked-MLP candidate (encoder-v2 → tanh MLP → head).

    A pure function of ``(packet, public_map, memory, fsm_intent)`` — the
    genome is frozen, the encoder integer-quantizes its belief inputs, the
    forward pass is stdlib-math, and every tie breaks on the canonical intent
    key — so the 15.10 double-run digests agree. Crew decisions delegate to the
    scripted FSM (the crew side stays frozen this wave); the encoder + head
    still run on every decision so the recorded frames exercise the full
    inference path on both roles (the 15.10 reference-policy shape).
    """

    def __init__(
        self,
        *,
        genome: Sequence[float],
        public_map: PublicMapView,
        sabotage_kinds: Sequence[str],
        hidden: int,
        encoder: TacticalFeatureEncoder | None = None,
    ) -> None:
        self._encoder = encoder if encoder is not None else TacticalFeatureEncoder()
        self._rooms = tuple(sorted(public_map.room_ids))
        self._room_index: dict[str, int] = {
            room: index for index, room in enumerate(self._rooms)
        }
        self._sabotage_kinds = tuple(sabotage_kinds)
        self._hidden = hidden
        self._input_dim = self._encoder.feature_dimension(public_map)
        self._output = len(self._rooms) + len(KIND_SLOTS)
        expected = mlp_genome_length(
            input_dim=self._input_dim, hidden=hidden, output=self._output
        )
        if len(genome) != expected:
            raise ValueError(
                f"genome length {len(genome)} != expected {expected} for this map"
            )
        self._genome = tuple(float(gene) for gene in genome)

    @property
    def encoder_version(self) -> str:
        return self._encoder.version

    @property
    def genome(self) -> tuple[float, ...]:
        return self._genome

    def _forward(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        features = self._encoder.encode(packet, public_map, memory)
        logits = mlp_forward(
            self._genome,
            features,
            input_dim=self._input_dim,
            hidden=self._hidden,
            output=self._output,
        )
        return features, logits

    def _scored_candidates(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        logits: Sequence[float],
    ) -> list[tuple[ActionIntent, str, float]]:
        """Every submission-legal intent with its key and head score.

        A vent candidate scores its kind slot PLUS the room slot of the vent's
        room (`public_map.vent_rooms`): for an in-vent impostor the connected
        exits differ exactly by destination room, so the room head — which
        already means "prefer being in room X" — makes the vent-EXIT choice (a
        named 15.15 option lever) learnable instead of a lexical vent-id tie.
        For a vent ENTRY the vent's room is the impostor's own room, so the
        addition is a shared state-dependent shift, not a tie-break. Remaining
        same-kind ties — several co-located KILL targets, several bodies in one
        room to REPORT — still share one slot and break lexically on the
        canonical intent key: a documented expressiveness limit, not a
        reachability one (every submission-legal intent stays emittable). The
        FSM anchor offers no supervision inside those ties (it kills only at
        ``co_present == 0``, where the legal kill candidate is unique), so
        widening the head for them is deferred to the pause.
        """

        mask = build_action_mask(
            packet,
            public_map,
            sabotage_kinds=self._sabotage_kinds,
            emergency_uses_remaining=0,
        )
        scored: list[tuple[ActionIntent, str, float]] = []
        for intent in mask.submission_legal:
            slot = head_slot_for_intent(intent, room_index=self._room_index)
            if slot is None:
                continue
            score = logits[slot]
            if isinstance(intent, VentIntent):
                vent_room = public_map.vent_rooms.get(intent.payload.vent_id)
                room_slot = (
                    self._room_index.get(vent_room) if vent_room is not None else None
                )
                if room_slot is not None:
                    score += logits[room_slot]
            scored.append((intent, intent_key(intent), score))
        return scored

    def _select(
        self, candidates: Sequence[tuple[ActionIntent, str, float]]
    ) -> ActionIntent:
        best_intent, _, _ = min(candidates, key=lambda item: (-item[2], item[1]))
        return best_intent

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        features, logits = self._forward(packet, public_map, memory)
        if packet.self_state.role != "IMPOSTOR":
            intent = fsm_intent
        else:
            candidates = self._scored_candidates(packet, public_map, logits)
            # WAIT is always engine-legal for a live actor, so the candidate
            # list is never empty; fail loud if that invariant ever breaks.
            if not candidates:
                raise ValueError(
                    f"no head-scorable submission-legal intent for "
                    f"{packet.agent_id!r} at tick {packet.tick}"
                )
            intent = self._select(candidates)
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=features,
            logits=logits,
            intent=intent,
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
        _, logits = self._forward(packet, public_map, memory)
        candidates = self._scored_candidates(packet, public_map, logits)
        if not candidates:
            raise ValueError(
                f"no head-scorable submission-legal intent for "
                f"{packet.agent_id!r} at tick {packet.tick}"
            )
        probabilities = _softmax([score for _, _, score in candidates])
        distribution: dict[str, float] = {}
        for (_, key, _), probability in zip(candidates, probabilities, strict=True):
            distribution[key] = distribution.get(key, 0.0) + probability
        return distribution


def build_masked_mlp_policy(
    genome: Sequence[float],
    *,
    game_map: Map | None = None,
    hidden: int,
) -> MaskedMlpPolicy:
    """Construct the shared policy family around a flat genome (one seam).

    Used by this entrant, the BC clone, MAP-Elites, and the artifact-reload
    path — one constructor so the frozen weights always rebuild the exact
    policy.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    public_map = public_map_from_engine_map(resolved_map)
    return MaskedMlpPolicy(
        genome=genome,
        public_map=public_map,
        sabotage_kinds=tuple(sorted(resolved_map.sabotages)),
        hidden=hidden,
    )


@dataclass(frozen=True)
class PolicyEsConfig:
    """The policy-net+ES entrant budget (recorded verbatim in the report)."""

    es: ESConfig
    hidden: int = 8
    anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
    num_players: int = BAKEOFF_NUM_PLAYERS
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE


def policy_es_budget(
    budget: str, *, anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
) -> PolicyEsConfig:
    """The two committed budgets: ``ci`` (seconds-scale) and ``full``."""

    train_seeds = load_train_seeds()
    if budget == "ci":
        return PolicyEsConfig(
            es=ESConfig(
                generations=1,
                population=2,
                sigma=0.15,
                seed=0,
                fitness_seeds=train_seeds[:1],
            ),
            anchor_weight=anchor_weight,
        )
    if budget == "full":
        return PolicyEsConfig(
            es=ESConfig(
                generations=14,
                population=10,
                sigma=0.15,
                seed=0,
                fitness_seeds=train_seeds[:6],
            ),
            anchor_weight=anchor_weight,
        )
    raise ValueError(f"unknown budget {budget!r}; expected 'ci' or 'full'")


class PolicyEsEntrant:
    """Entrant (3): the masked policy net optimized by the shared ES core.

    ``warm_start`` is a zero-arg callable resolved AT TRAIN TIME (the CLI wires
    it to the BC entrant's champion — the spike's BC-then-ES lesson: BC alone
    caps below FSM parity, ES climbs from it); it returns ``None`` (or a
    genome of the wrong length, e.g. a different hidden width) to fall back to
    the ES core's seeded random init — recorded either way in the metadata.
    """

    def __init__(
        self,
        *,
        config: PolicyEsConfig,
        warm_start: Callable[[], tuple[float, ...] | None] | None = None,
        game_map: Map | None = None,
    ) -> None:
        self._config = config
        self._warm_start = warm_start
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._public_map = public_map_from_engine_map(self._game_map)

    @property
    def name(self) -> str:
        return "policy-es"

    def _genome_length(self) -> int:
        return policy_genome_length(
            self._public_map,
            hidden=self._config.hidden,
            encoder=TacticalFeatureEncoder(),
        )

    def _seed_fitness(self, genome: tuple[float, ...], seed: int) -> float:
        policy = MaskedMlpPolicy(
            genome=genome,
            public_map=self._public_map,
            sabotage_kinds=tuple(sorted(self._game_map.sabotages)),
            hidden=self._config.hidden,
        )
        trace = DecisionTrace()
        with tempfile.TemporaryDirectory(prefix="ailibi-policy-es-") as tmp:
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
        genome_length = self._genome_length()
        initial: tuple[float, ...] | None = None
        if self._warm_start is not None:
            candidate_genome = self._warm_start()
            if candidate_genome is not None and len(candidate_genome) == genome_length:
                initial = candidate_genome
        fitness = k_seed_mean(self._seed_fitness, self._config.es.fitness_seeds)
        result = evolve(
            fitness,
            genome_length=genome_length,
            config=self._config.es,
            initial_genome=initial,
        )
        policy = MaskedMlpPolicy(
            genome=result.champion,
            public_map=self._public_map,
            sabotage_kinds=tuple(sorted(self._game_map.sabotages)),
            hidden=self._config.hidden,
        )
        return TrainedCandidate(
            entrant=self.name,
            policy=policy,
            weights=result.champion,
            config={
                "entrant": self.name,
                "hidden": self._config.hidden,
                "anchor_weight": self._config.anchor_weight,
                "es": self._config.es.model_dump(mode="json"),
                "head": {
                    "rooms": sorted(self._public_map.room_ids),
                    "kind_slots": list(KIND_SLOTS),
                },
                "encoder_version": policy.encoder_version,
            },
            train_wall_clock_s=time.perf_counter() - started,
            train_metadata={
                "warm_start_used": initial is not None,
                "es_digest": result.digest(),
                "num_evaluations": result.num_evaluations,
                "fitness_trace": [round(value, 4) for value in result.fitness_trace],
                "champion_fitness": round(result.champion_fitness, 4),
            },
        )


__all__ = [
    "KIND_SLOTS",
    "MaskedMlpPolicy",
    "PolicyEsConfig",
    "PolicyEsEntrant",
    "build_masked_mlp_policy",
    "head_size",
    "head_slot_for_intent",
    "policy_es_budget",
    "policy_genome_length",
]
