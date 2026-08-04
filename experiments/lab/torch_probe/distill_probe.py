"""FROZEN (Phase 19 tier map, training/README.md): the torch probe, a clean negative.
Bug fixes and evidence readers only; no new search.

Operator script: distill the torch champion into the pure-Python net.

The escape hatch the task contract prices: behavior-clone the frozen
PPO+GRU champion into the 15.15 ``MaskedMlpPolicy`` family (encoder-v2 ->
pure-Python tanh MLP -> the shared 17-slot head), so Wave 2 could take the
capability without the torch dependency. Run:

    uv run --with torch python experiments/lab/torch_probe/distill_probe.py \
        --teacher-artifact experiments/lab/torch_probe/artifacts/torch-ppo-gru-s0

The student-teacher agreement bar is PRE-STATED here as a constant
(:data:`DISTILL_AGREEMENT_BAR` = 0.90 top-1 on held-out teacher decisions —
mirroring the 15.15 ``BC_INTENT_AGREEMENT_BAR`` discipline) and the student
gets its OWN full row through the committed 15.15 eval protocol.

Teacher labels are harvested on the corpus TRAIN split (the teacher's intents
drive the games — on-policy for the teacher); agreement is measured on the
corpus VAL split (games the student never trained on). Student inputs are the
encoder-v2 features off the inner agent's LIVE memory — exactly what the
pure-Python family sees at its own eval time.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LAB_ROOT = Path(__file__).resolve().parents[1]
for _path in (str(_REPO_ROOT), str(_LAB_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import argparse  # noqa: E402
import json  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from collections.abc import Sequence  # noqa: E402

from agents.memory.store import AgentMemory  # noqa: E402
from agents.tactical.features import (  # noqa: E402
    TacticalFeatureEncoder,
    mlp_genome_length,
)
from engine.world import load_canonical_map  # noqa: E402
from observation.action_intent import ActionIntent  # noqa: E402
from observation.packet import ObservationPacket  # noqa: E402
from observation.public_map import PublicMapView  # noqa: E402
from orchestrator.boundary import public_map_from_engine_map  # noqa: E402
from torch_probe.entrant import TorchProbePolicy  # noqa: E402
from torch_probe.ppo_gru import scorer_from_artifact  # noqa: E402
from training.bakeoff.harness import (  # noqa: E402
    TrainedCandidate,
    default_protocol_config,
    evaluate_candidate,
    intent_key,
    load_candidate_weights,
    load_train_seeds,
    load_val_seeds,
    rollout_candidate,
)
from training.bakeoff.policy_es import (  # noqa: E402
    build_masked_mlp_policy,
    head_size,
    head_slot_for_intent,
)

# The PRE-STATED distillation bar (the 15.15 BC bar discipline): held-out
# top-1 intent agreement between the pure-Python student and its torch
# teacher. Stated here, before any distillation run.
DISTILL_AGREEMENT_BAR = 0.90

_PROBE_DIR = Path(__file__).resolve().parent
DEFAULT_RESULTS_PATH = _PROBE_DIR / "results-torch-probe.jsonl"
DEFAULT_ARTIFACT_ROOT = _PROBE_DIR / "artifacts"
# The committed student row/artifact was distilled from the s1 champion (the
# best inner fitness of the three seeds) — the default must point there so a
# default rerun regenerates the published student instead of clobbering it
# with a different teacher's clone.
DEFAULT_TEACHER = DEFAULT_ARTIFACT_ROOT / "torch-ppo-gru-s1"


def _load_teacher(artifact_dir: Path) -> TorchProbePolicy:
    config = json.loads((artifact_dir / "config.json").read_text())
    weights = load_candidate_weights(artifact_dir)
    game_map = load_canonical_map()
    return TorchProbePolicy(
        scorer=scorer_from_artifact(config, weights),
        public_map=public_map_from_engine_map(game_map),
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
    )


def _harvest(
    teacher: TorchProbePolicy,
    seeds: Sequence[int],
    *,
    room_index: dict[str, int],
    encoder: TacticalFeatureEncoder,
) -> tuple[list[tuple[float, ...]], list[int], int]:
    """Teacher-driven rollouts -> (live-memory features, head-slot label)."""

    features: list[tuple[float, ...]] = []
    labels: list[int] = []
    skipped = 0

    def on_decision(
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        fsm_intent: ActionIntent,
        chosen: ActionIntent,
    ) -> None:
        nonlocal skipped
        slot = head_slot_for_intent(chosen, room_index=room_index)
        if slot is None:
            skipped += 1
            return
        features.append(encoder.encode(packet, public_map, memory))
        labels.append(slot)

    with tempfile.TemporaryDirectory(prefix="ailibi-torch-distill-") as tmp:
        for seed in seeds:
            rollout_candidate(
                teacher, seed, output_dir=Path(tmp), on_decision=on_decision
            )
    return features, labels, skipped


def _train_student_genome(
    features: Sequence[tuple[float, ...]],
    labels: Sequence[int],
    *,
    input_dim: int,
    hidden: int,
    head: int,
    epochs: int,
    learning_rate: float,
    torch_seed: int,
) -> tuple[float, ...]:
    """Fit the pure-Python family's MLP by CE in torch, export the flat genome.

    The genome layout is exactly ``agents.tactical.features.mlp_forward``'s
    ``[W1 | b1 | W2 | b2]`` (row-major), so ``build_masked_mlp_policy``
    reconstructs the identical function in stdlib Python.
    """

    import torch
    from torch import nn

    torch.set_num_threads(1)
    torch.manual_seed(torch_seed)
    net = nn.Sequential(
        nn.Linear(input_dim, hidden), nn.Tanh(), nn.Linear(hidden, head)
    ).to(torch.float64)
    x = torch.tensor([list(row) for row in features], dtype=torch.float64)
    y = torch.tensor(list(labels), dtype=torch.long)
    optimizer = torch.optim.Adam(net.parameters(), lr=learning_rate)
    loss_fn = nn.CrossEntropyLoss()
    for epoch in range(epochs):
        optimizer.zero_grad()
        loss = loss_fn(net(x), y)
        loss.backward()
        optimizer.step()
        if epoch % max(1, epochs // 10) == 0 or epoch == epochs - 1:
            accuracy = float((net(x).argmax(dim=1) == y).double().mean().item())
            print(
                json.dumps(
                    {
                        "epoch": epoch,
                        "ce_loss": round(float(loss.item()), 4),
                        "train_accuracy": round(accuracy, 4),
                    }
                )
            )
    fc1, fc2 = net[0], net[2]
    genome: list[float] = []
    genome.extend(float(v) for v in fc1.weight.detach().reshape(-1).tolist())
    genome.extend(float(v) for v in fc1.bias.detach().tolist())
    genome.extend(float(v) for v in fc2.weight.detach().reshape(-1).tolist())
    genome.extend(float(v) for v in fc2.bias.detach().tolist())
    expected = mlp_genome_length(input_dim=input_dim, hidden=hidden, output=head)
    if len(genome) != expected:
        raise ValueError(f"exported genome {len(genome)} != expected {expected}")
    return tuple(genome)


def _heldout_agreement(
    teacher: TorchProbePolicy,
    student_policy: object,
    seeds: Sequence[int],
) -> tuple[float, int]:
    """Top-1 intent agreement on held-out teacher-driven decisions."""

    matches = 0
    total = 0

    def on_decision(
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        fsm_intent: ActionIntent,
        chosen: ActionIntent,
    ) -> None:
        nonlocal matches, total
        frame = student_policy.evaluate(  # type: ignore[attr-defined]
            packet, public_map, memory, fsm_intent=fsm_intent
        )
        total += 1
        if intent_key(frame.intent) == intent_key(chosen):
            matches += 1

    with tempfile.TemporaryDirectory(prefix="ailibi-torch-agree-") as tmp:
        for seed in seeds:
            rollout_candidate(
                teacher, seed, output_dir=Path(tmp), on_decision=on_decision
            )
    return (matches / total if total else 0.0), total


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=(
            "uv run --with torch python experiments/lab/torch_probe/distill_probe.py"
        ),
        description="Task 15.17: distill the torch champion into MaskedMlpPolicy.",
    )
    parser.add_argument("--teacher-artifact", type=Path, default=DEFAULT_TEACHER)
    parser.add_argument("--harvest-seed-count", type=int, default=60)
    parser.add_argument("--heldout-seed-count", type=int, default=10)
    parser.add_argument("--hidden", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=1500)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--torch-seed", type=int, default=0)
    parser.add_argument("--student-name", default="torch-distill-student")
    parser.add_argument("--skip-eval", action="store_true")
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS_PATH)
    parser.add_argument("--artifacts", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    args = parser.parse_args(argv)

    started = time.perf_counter()
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    encoder = TacticalFeatureEncoder()
    room_index = {room: i for i, room in enumerate(sorted(public_map.room_ids))}
    input_dim = encoder.feature_dimension(public_map)
    head = head_size(public_map)

    teacher = _load_teacher(args.teacher_artifact)
    harvest_seeds = load_train_seeds()[: args.harvest_seed_count]
    heldout_seeds = load_val_seeds()[: args.heldout_seed_count]

    features, labels, skipped = _harvest(
        teacher, harvest_seeds, room_index=room_index, encoder=encoder
    )
    print(
        json.dumps(
            {
                "harvest_decisions": len(labels),
                "harvest_seeds": len(harvest_seeds),
                "off_vocabulary_skipped": skipped,
                "agreement_bar_prestated": DISTILL_AGREEMENT_BAR,
            }
        )
    )

    genome = _train_student_genome(
        features,
        labels,
        input_dim=input_dim,
        hidden=args.hidden,
        head=head,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        torch_seed=args.torch_seed,
    )
    student = build_masked_mlp_policy(genome, game_map=game_map, hidden=args.hidden)

    # A fresh teacher instance for the held-out pass: recurrent state must not
    # carry over from the harvest games.
    agreement_teacher = _load_teacher(args.teacher_artifact)
    agreement, decisions = _heldout_agreement(agreement_teacher, student, heldout_seeds)
    bar_met = agreement >= DISTILL_AGREEMENT_BAR
    print(
        json.dumps(
            {
                "heldout_agreement": round(agreement, 4),
                "heldout_decisions": decisions,
                "bar": DISTILL_AGREEMENT_BAR,
                "bar_met": bar_met,
            }
        )
    )

    if args.skip_eval:
        return 0

    candidate = TrainedCandidate(
        entrant=args.student_name,
        policy=student,
        weights=genome,
        config={
            "entrant": args.student_name,
            "teacher_artifact": str(args.teacher_artifact),
            "hidden": args.hidden,
            "epochs": args.epochs,
            "learning_rate": args.learning_rate,
            "torch_seed": args.torch_seed,
            "encoder_version": student.encoder_version,
        },
        train_wall_clock_s=time.perf_counter() - started,
        train_metadata={
            "heldout_agreement": round(agreement, 4),
            "heldout_decisions": decisions,
            "agreement_bar": DISTILL_AGREEMENT_BAR,
            "bar_met": bar_met,
            "harvest_decisions": len(labels),
            "off_vocabulary_skipped": skipped,
        },
    )
    row = evaluate_candidate(
        candidate, default_protocol_config(), artifact_root=args.artifacts
    )
    args.results.parent.mkdir(parents=True, exist_ok=True)
    with args.results.open("a") as handle:
        handle.write(row.to_json_line() + "\n")
    print(
        json.dumps(
            {
                "student_row": args.student_name,
                "tier": row.tier,
                "deterministic": row.determinism.deterministic,
                "validity_passed": row.validity_passed,
                "referee_mean_score": row.referee_mean_score,
                "inner_fitness_real": row.inner_fitness_real,
                "impostor_win_rate": row.impostor_win_rate,
                "anchor_cross_entropy": row.anchor_cross_entropy,
                "wall_clock_eval_s": round(row.wall_clock_eval_s, 1),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
