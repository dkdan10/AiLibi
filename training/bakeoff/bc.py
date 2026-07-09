"""Entrant (1): BC/DAgger from the frozen FSM oracle (Task 15.15).

The ENCODER-SUFFICIENCY test of the paradigm comparison
(audits/post-phase-14-ML-planning.md §9 Option 4 — "behavior cloning + DAgger
from the scripted expert", flagged warm-start-only, not standalone): behavior-
clone ``agents.tactical.impostor_policy.ImpostorPolicy.decide`` onto the
encoder-v2 memory-carrying feature vector
(:class:`agents.tactical.features.TacticalFeatureEncoder`), THROUGH the shared
:class:`training.bakeoff.policy_es.MaskedMlpPolicy` family so the ES/QD entrants
warm-start from this clone with an exact genome-shape match (the spike's
BC-then-ES lesson).

The spike's check-2 lesson is the framing: from-scratch BC on the memoryless
34-dim spike encoder capped BELOW FSM parity (13 clone kills < 27 FSM kills —
the FSM's stalk is history-dependent and a single-packet encoder structurally
cannot represent it, audits/post-phase-14-ML-planning.md §6.3). Encoder v2
carries the agent's OWN belief / last-seen memory into the vector, so the
reported held-out top-1 intent agreement against the pre-stated bar
:data:`training.bakeoff.harness.BC_INTENT_AGREEMENT_BAR` (0.90) is the direct
measurement of whether v2 closed that gap. If it misses, the per-kind
confusion table (:data:`per_kind_agreement` in the metadata) names the encoder
gaps by intent kind — the finding IS the gap, not a bare failure.

DAgger (Ross et al. 2011, arXiv:1011.0686) exploits the FSM as a free queryable
expert. The initial round harvests the pure scripted FSM (``policy=None``); each
subsequent round runs the CURRENT clone so states come from the LEARNER's own
distribution while the labels stay the FSM's proposal (the ``fsm_intent`` the
harness's ``on_decision`` callback hands over at every state). Aggregating those
corrected states across rounds and retraining from scratch is the correction
that turns BC's O(T^2 * eps) distribution-shift regret into O(T * eps).

numpy is permitted HERE (training-confined): the softmax-cross-entropy SGD runs
in float64 numpy, but the FROZEN artifact's inference stays pure-Python through
:class:`MaskedMlpPolicy` (the locked Wave-1 dependency posture), and the final
weights convert back to a plain ``tuple[float, ...]`` before they leave this
module. No ``eval.*`` import may appear here (the harness firewall test
AST-scans this module): the harness computes every reported metric.
"""

from __future__ import annotations

import tempfile
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from random import Random

import numpy as np
from numpy.typing import NDArray

from agents.memory.store import AgentMemory
from agents.tactical.features import TacticalFeatureEncoder
from engine.world import Map, load_canonical_map
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from training.bakeoff.es import derive_stream_seed, random_genome
from training.bakeoff.harness import (
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
    BC_INTENT_AGREEMENT_BAR,
    TrainedCandidate,
    intent_key,
    load_train_seeds,
    load_val_seeds,
    rollout_candidate,
)
from training.bakeoff.policy_es import (
    KIND_SLOTS,
    MaskedMlpPolicy,
    build_masked_mlp_policy,
    head_size,
    head_slot_for_intent,
    policy_genome_length,
)

# One labelled clone sample: the encoder-v2 feature vector at an impostor
# decision paired with the head slot the FSM's proposed intent maps to (the
# shared :func:`head_slot_for_intent` label the policy family scores that intent
# with — so the clone's class label is exactly a policy-family output slot).
_Sample = tuple[tuple[float, ...], int]


@dataclass(frozen=True)
class BcConfig:
    """The BC/DAgger entrant budget (recorded verbatim in the report row).

    Frozen so a config deserialized from the report cannot drift. Field order
    departs from the task's grouping only where Python's dataclass rule forces
    it: ``heldout_seeds`` is a required field, so it must precede the defaulted
    knobs (``hidden`` onward) — the field SET is unchanged and every caller
    constructs by keyword, so no caller is affected.

    ``dagger_seed_rounds`` is a tuple OF seed tuples — one entry per DAgger
    round, each round's seeds harvested through the clone trained on all
    prior rounds' aggregated data (the Ross et al. aggregation). ``init_seed``
    seeds BOTH the shared from-scratch init genome and every minibatch shuffle
    stream (via :func:`training.bakeoff.es.derive_stream_seed`).
    """

    harvest_seeds: tuple[int, ...]
    dagger_seed_rounds: tuple[tuple[int, ...], ...]
    epochs: int
    learning_rate: float
    heldout_seeds: tuple[int, ...]
    hidden: int = 8
    init_seed: int = 0
    num_players: int = BAKEOFF_NUM_PLAYERS
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE


def bc_budget(budget: str) -> BcConfig:
    """The two committed budgets: ``ci`` (seconds-scale) and ``full``.

    Seeds are drawn off the frozen corpus splits so the harvest / DAgger / held-
    out sets are disjoint by construction: the harvest + DAgger rounds pull the
    TRAIN split, the held-out agreement set pulls the VAL split (never the eval
    TEST split — that stays reserved for the fixed eval protocol).
    """

    train = load_train_seeds()
    val = load_val_seeds()
    if budget == "ci":
        return BcConfig(
            harvest_seeds=train[:1],
            dagger_seed_rounds=((train[1],),),
            epochs=2,
            learning_rate=0.2,
            heldout_seeds=val[:1],
        )
    if budget == "full":
        return BcConfig(
            harvest_seeds=train[:12],
            dagger_seed_rounds=(train[12:18], train[18:24]),
            epochs=30,
            learning_rate=0.2,
            heldout_seeds=val[:10],
        )
    raise ValueError(f"unknown budget {budget!r}; expected 'ci' or 'full'")


def _unpack_genome(
    genome: Sequence[float], *, input_dim: int, hidden: int, output: int
) -> tuple[
    NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]
]:
    """Split a flat genome into ``(W1, b1, W2, b2)`` matrices (float64 copies).

    The layout matches :func:`agents.tactical.features.mlp_forward` EXACTLY:
    ``W1`` row-major ``[j * input_dim + i]`` (shape ``hidden x input_dim``), then
    ``b1`` (``hidden``), then ``W2`` ``[k * hidden + j]`` (shape
    ``output x hidden``), then ``b2`` (``output``). Copies so in-place SGD never
    mutates the shared init genome the next round re-reads.
    """

    flat = np.asarray(genome, dtype=np.float64)
    w2_start = input_dim * hidden + hidden
    b2_start = w2_start + hidden * output
    w1 = flat[: input_dim * hidden].reshape(hidden, input_dim).copy()
    b1 = flat[input_dim * hidden : w2_start].copy()
    w2 = flat[w2_start:b2_start].reshape(output, hidden).copy()
    b2 = flat[b2_start:].copy()
    return w1, b1, w2, b2


def _pack_genome(
    w1: NDArray[np.float64],
    b1: NDArray[np.float64],
    w2: NDArray[np.float64],
    b2: NDArray[np.float64],
) -> tuple[float, ...]:
    """Flatten ``(W1, b1, W2, b2)`` back to the ``mlp_forward`` genome layout."""

    flat = np.concatenate([w1.reshape(-1), b1, w2.reshape(-1), b2])
    return tuple(float(value) for value in flat)


class BcDaggerEntrant:
    """Entrant (1): BC/DAgger cloning the FSM oracle onto the shared MLP family.

    ``train`` runs the from-FSM harvest, the DAgger rounds, the from-scratch
    retrains, and the held-out agreement measurement, then wraps the final
    genome in :func:`build_masked_mlp_policy` (the same family the ES/QD entrants
    mutate — an exact warm-start shape). It computes NO reported eval metric: the
    harness's :func:`evaluate_candidate` owns those. The held-out intent
    agreement + per-kind confusion table it DOES compute are training diagnostics
    against the pre-stated bar, carried verbatim into the row's metadata.
    """

    def __init__(self, *, config: BcConfig, game_map: Map | None = None) -> None:
        self._config = config
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._public_map = public_map_from_engine_map(self._game_map)
        self._encoder = TacticalFeatureEncoder()
        self._rooms = sorted(self._public_map.room_ids)
        self._room_index: dict[str, int] = {
            room: index for index, room in enumerate(self._rooms)
        }
        self._input_dim = self._encoder.feature_dimension(self._public_map)
        self._output = head_size(self._public_map)
        self._genome_length = policy_genome_length(
            self._public_map, hidden=config.hidden, encoder=self._encoder
        )

    @property
    def name(self) -> str:
        return "bc-dagger"

    def _harvest(
        self, policy: MaskedMlpPolicy | None, seeds: Sequence[int]
    ) -> list[_Sample]:
        """Collect (features, FSM-label) samples over ``seeds``.

        ``policy=None`` runs the pure scripted FSM (the iteration-0 on-policy-
        for-the-expert harvest); a clone runs the DAgger rounds so the states are
        drawn from the LEARNER's distribution. Either way the label is the FSM's
        ``fsm_intent`` the callback hands over — the DAgger correction. Off-
        vocabulary intents (the emergency the family cannot score) are skipped.
        """

        samples: list[_Sample] = []

        def on_decision(
            packet: ObservationPacket,
            public_map: PublicMapView,
            memory: AgentMemory,
            fsm_intent: ActionIntent,
            chosen: ActionIntent,
        ) -> None:
            label = head_slot_for_intent(fsm_intent, room_index=self._room_index)
            if label is None:
                return
            features = self._encoder.encode(packet, public_map, memory)
            samples.append((features, label))

        with tempfile.TemporaryDirectory(prefix="ailibi-bc-harvest-") as tmp:
            output_dir = Path(tmp)
            for seed in seeds:
                rollout_candidate(
                    policy,
                    seed,
                    output_dir=output_dir,
                    game_map=self._game_map,
                    num_players=self._config.num_players,
                    num_impostors=self._config.num_impostors,
                    tasks_per_crewmate=self._config.tasks_per_crewmate,
                    on_decision=on_decision,
                )
        return samples

    def _train_from_scratch(
        self,
        dataset: Sequence[_Sample],
        *,
        init_genome: tuple[float, ...],
        round_index: int,
    ) -> tuple[float, ...]:
        """Softmax-cross-entropy per-example SGD on the tanh MLP (float64 numpy).

        Retrains from the SHARED ``init_genome`` on the full aggregated dataset
        so the run is a deterministic function of the seeds (the DAgger rounds
        grow the dataset, never the initialization). Each epoch shuffles the
        example order through :func:`derive_stream_seed` fed to
        :class:`random.Random`, then updates once per example. Gradients are the
        exact backprop of the ``mlp_forward`` kernel, so the trained matrices
        repack into a genome the pure-Python inference path reproduces.
        """

        features = np.asarray([sample for sample, _ in dataset], dtype=np.float64)
        labels = np.asarray([label for _, label in dataset], dtype=np.int64)
        w1, b1, w2, b2 = _unpack_genome(
            init_genome,
            input_dim=self._input_dim,
            hidden=self._config.hidden,
            output=self._output,
        )
        learning_rate = self._config.learning_rate
        count = len(dataset)
        for epoch in range(self._config.epochs):
            order = list(range(count))
            Random(
                derive_stream_seed(self._config.init_seed, round_index, epoch)
            ).shuffle(order)
            for index in order:
                x = features[index]
                label = int(labels[index])
                a1 = np.tanh(w1 @ x + b1)
                z2 = w2 @ a1 + b2
                exp = np.exp(z2 - z2.max())
                probs = exp / exp.sum()
                grad_z2 = probs.copy()
                grad_z2[label] -= 1.0
                grad_a1 = w2.T @ grad_z2
                grad_z1 = grad_a1 * (1.0 - a1 * a1)
                w2 -= learning_rate * np.outer(grad_z2, a1)
                b2 -= learning_rate * grad_z2
                w1 -= learning_rate * np.outer(grad_z1, x)
                b1 -= learning_rate * grad_z1
        return _pack_genome(w1, b1, w2, b2)

    def _train_accuracy(
        self, genome: tuple[float, ...], dataset: Sequence[_Sample]
    ) -> float:
        """Top-1 accuracy of ``genome`` over the aggregated train set (unmasked).

        The argmax over the full head — the exact quantity the softmax-CE
        objective optimizes — so it reads as the clone's fit to its own labels
        (distinct from the masked, submission-legal argmax the frozen policy
        realizes at inference and the held-out agreement measures).
        """

        features = np.asarray([sample for sample, _ in dataset], dtype=np.float64)
        labels = np.asarray([label for _, label in dataset], dtype=np.int64)
        w1, b1, w2, b2 = _unpack_genome(
            genome,
            input_dim=self._input_dim,
            hidden=self._config.hidden,
            output=self._output,
        )
        hidden_act = np.tanh(features @ w1.T + b1)
        logits = hidden_act @ w2.T + b2
        predictions = np.argmax(logits, axis=1)
        correct = int(np.count_nonzero(predictions == labels))
        return correct / len(dataset)

    def _heldout_agreement(self, policy: MaskedMlpPolicy) -> dict[str, tuple[int, int]]:
        """Per-kind (total, hits) of the clone vs the FSM on the held-out set.

        Runs the pure FSM (``policy=None``) over the held-out seeds and, at every
        impostor decision it visits, evaluates the FINAL clone off the same live
        memory and scores ``intent_key`` agreement with the FSM's choice —
        bucketed by the FSM intent's kind so a miss names the encoder gap.
        """

        per_kind: dict[str, list[int]] = {}

        def on_decision(
            packet: ObservationPacket,
            public_map: PublicMapView,
            memory: AgentMemory,
            fsm_intent: ActionIntent,
            chosen: ActionIntent,
        ) -> None:
            frame = policy.evaluate(packet, public_map, memory, fsm_intent=fsm_intent)
            bucket = per_kind.setdefault(fsm_intent.type, [0, 0])
            bucket[0] += 1
            if intent_key(frame.intent) == intent_key(fsm_intent):
                bucket[1] += 1

        with tempfile.TemporaryDirectory(prefix="ailibi-bc-heldout-") as tmp:
            output_dir = Path(tmp)
            for seed in self._config.heldout_seeds:
                rollout_candidate(
                    None,
                    seed,
                    output_dir=output_dir,
                    game_map=self._game_map,
                    num_players=self._config.num_players,
                    num_impostors=self._config.num_impostors,
                    tasks_per_crewmate=self._config.tasks_per_crewmate,
                    on_decision=on_decision,
                )
        return {kind: (bucket[0], bucket[1]) for kind, bucket in per_kind.items()}

    def train(self) -> TrainedCandidate:
        started = time.perf_counter()
        init_genome = random_genome(
            self._genome_length, seed=self._config.init_seed, scale=0.1
        )

        dataset: list[_Sample] = []
        samples_per_round: list[int] = []

        # Iteration 0: harvest the pure scripted FSM at its OWN states.
        round_zero = self._harvest(None, self._config.harvest_seeds)
        dataset.extend(round_zero)
        samples_per_round.append(len(round_zero))
        if not dataset:
            raise ValueError(
                "BC harvest produced no head-scorable impostor decisions; the "
                "clone cannot be trained on an empty dataset"
            )
        genome = self._train_from_scratch(
            dataset, init_genome=init_genome, round_index=0
        )

        # DAgger rounds: harvest the CURRENT clone's states, keep the FSM labels,
        # aggregate, and retrain FROM SCRATCH (Ross et al. dataset aggregation).
        for round_offset, seeds in enumerate(self._config.dagger_seed_rounds):
            clone = build_masked_mlp_policy(
                genome, game_map=self._game_map, hidden=self._config.hidden
            )
            new_samples = self._harvest(clone, seeds)
            dataset.extend(new_samples)
            samples_per_round.append(len(new_samples))
            genome = self._train_from_scratch(
                dataset, init_genome=init_genome, round_index=round_offset + 1
            )

        final_genome = genome
        policy = build_masked_mlp_policy(
            final_genome, game_map=self._game_map, hidden=self._config.hidden
        )

        final_train_accuracy = self._train_accuracy(final_genome, dataset)
        per_kind = self._heldout_agreement(policy)
        total = sum(pair[0] for pair in per_kind.values())
        hits = sum(pair[1] for pair in per_kind.values())
        agreement = hits / total if total else 0.0
        per_kind_agreement: dict[str, dict[str, float]] = {
            kind: {
                "total": pair[0],
                "hits": pair[1],
                "agreement": pair[1] / pair[0] if pair[0] else 0.0,
            }
            for kind, pair in sorted(per_kind.items())
        }

        config: dict[str, object] = {
            "entrant": self.name,
            "hidden": self._config.hidden,
            "encoder_version": policy.encoder_version,
            "head": {
                "rooms": list(self._rooms),
                "kind_slots": list(KIND_SLOTS),
            },
            "harvest_seeds": list(self._config.harvest_seeds),
            "dagger_seed_rounds": [
                list(seeds) for seeds in self._config.dagger_seed_rounds
            ],
            "epochs": self._config.epochs,
            "learning_rate": self._config.learning_rate,
            "init_seed": self._config.init_seed,
        }
        metadata: dict[str, object] = {
            "heldout_intent_agreement": agreement,
            "intent_agreement_bar": BC_INTENT_AGREEMENT_BAR,
            "bar_met": agreement >= BC_INTENT_AGREEMENT_BAR,
            "per_kind_agreement": per_kind_agreement,
            "heldout_decisions": total,
            "dataset_size": len(dataset),
            "samples_per_round": samples_per_round,
            "dagger_rounds": len(self._config.dagger_seed_rounds),
            "epochs": self._config.epochs,
            "learning_rate": self._config.learning_rate,
            "final_train_accuracy": final_train_accuracy,
        }
        return TrainedCandidate(
            entrant=self.name,
            policy=policy,
            weights=final_genome,
            config=config,
            train_wall_clock_s=time.perf_counter() - started,
            train_metadata=metadata,
        )


__all__ = [
    "BcConfig",
    "BcDaggerEntrant",
    "bc_budget",
]
