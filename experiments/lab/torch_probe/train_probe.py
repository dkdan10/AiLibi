"""FROZEN (Phase 19 tier map, training/README.md): the torch probe, a clean negative.
Bug fixes and evidence readers only; no new search.

Operator script: train the PPO+GRU probe and score it through the harness.

Run (torch never enters the project environment; the defaults ARE the
recorded budget, so a bare run regenerates the committed champions):

    uv run --with torch python experiments/lab/torch_probe/train_probe.py \
        --torch-seed 0 --eval-repeats 3

Training rides ``training.env.TacticalRolloutEnv`` (fast no-replay path) on
the frozen corpus TRAIN split; evaluation is EXACTLY the committed 15.15
protocol — ``training.bakeoff.harness.evaluate_candidate`` under
``default_protocol_config()`` (the fixed eval seed config:
``replays/ml_corpus/9p2i/splits.json`` test split, ``seed % 5 == 4``) —
consumed read-only. Rows append to
``experiments/lab/torch_probe/results-torch-probe.jsonl`` and artifacts
freeze under ``experiments/lab/torch_probe/artifacts/`` (float-hex JSON +
sha256, the 15.15 format); nothing is written under ``training/``.

The seeded-run variance story comes from re-running this script with
different ``--torch-seed`` values (one row per champion) plus
``--eval-repeats`` re-scores of one frozen champion (eval-path stability).
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
import platform  # noqa: E402
import time  # noqa: E402
from collections.abc import Sequence  # noqa: E402

from agents.tactical.features import TacticalFeatureEncoder  # noqa: E402
from engine.world import load_canonical_map  # noqa: E402
from orchestrator.boundary import public_map_from_engine_map  # noqa: E402
from torch_probe.entrant import (  # noqa: E402
    ENTRANT_NAME,
    TorchProbeConfig,
    TorchProbeEntrant,
)
from torch_probe.ppo_gru import PpoConfig, PpoGruLearner  # noqa: E402
from training.bakeoff.harness import (  # noqa: E402
    default_protocol_config,
    evaluate_candidate,
    load_train_seeds,
)

_PROBE_DIR = Path(__file__).resolve().parent
DEFAULT_RESULTS_PATH = _PROBE_DIR / "results-torch-probe.jsonl"
DEFAULT_ARTIFACT_ROOT = _PROBE_DIR / "artifacts"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uv run --with torch python experiments/lab/torch_probe/train_probe.py",
        description="Task 15.17: train the PPO+GRU probe, score via the harness.",
    )
    # Defaults are the RECORDED budget (100 x 12 = 1,200 episodes, the
    # committed results' recipe): a default rerun regenerates the published
    # champions rather than silently overwriting them with a smaller probe.
    parser.add_argument("--updates", type=int, default=100)
    parser.add_argument("--episodes-per-update", type=int, default=12)
    parser.add_argument("--train-seed-count", type=int, default=24)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--entropy-coef", type=float, default=0.01)
    parser.add_argument("--anchor-coef", type=float, default=0.3)
    parser.add_argument("--torch-seed", type=int, default=0)
    parser.add_argument("--eval-repeats", type=int, default=1)
    parser.add_argument("--skip-eval", action="store_true")
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS_PATH)
    parser.add_argument("--artifacts", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    args = parser.parse_args(argv)

    import torch

    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    encoder = TacticalFeatureEncoder()
    from training.bakeoff.policy_es import head_size

    input_dim = encoder.feature_dimension(public_map)
    head = head_size(public_map)
    train_seeds = load_train_seeds()[: args.train_seed_count]

    print(
        json.dumps(
            {
                "host": platform.platform(),
                "processor": platform.processor() or "unknown",
                "python": platform.python_version(),
                "torch": torch.__version__,
                "input_dim": input_dim,
                "head": head,
                "train_seeds": len(train_seeds),
            }
        )
    )

    learner = PpoGruLearner(
        PpoConfig(
            input_dim=input_dim,
            head=head,
            hidden=args.hidden,
            learning_rate=args.learning_rate,
            entropy_coef=args.entropy_coef,
            anchor_coef=args.anchor_coef,
            torch_seed=args.torch_seed,
        )
    )
    entrant = TorchProbeEntrant(
        learner=learner,
        config=TorchProbeConfig(
            train_seeds=train_seeds,
            updates=args.updates,
            episodes_per_update=args.episodes_per_update,
            extra={"torch_seed": args.torch_seed},
        ),
        game_map=game_map,
        name=f"{ENTRANT_NAME}-s{args.torch_seed}",
    )

    started = time.perf_counter()
    candidate = entrant.train()
    train_seconds = time.perf_counter() - started
    print(
        json.dumps(
            {
                "trained": candidate.entrant,
                "train_wall_clock_s": round(train_seconds, 1),
                "genome_length": len(candidate.weights),
                "shaped_reward_trace": entrant.fitness_trace,
            }
        )
    )

    if args.skip_eval:
        return 0

    protocol = default_protocol_config()
    args.results.parent.mkdir(parents=True, exist_ok=True)
    for repeat in range(args.eval_repeats):
        row = evaluate_candidate(candidate, protocol, artifact_root=args.artifacts)
        with args.results.open("a") as handle:
            handle.write(row.to_json_line() + "\n")
        print(
            json.dumps(
                {
                    "eval_repeat": repeat,
                    "tier": row.tier,
                    "deterministic": row.determinism.deterministic,
                    "validity_passed": row.validity_passed,
                    "referee_mean_score": row.referee_mean_score,
                    "inner_fitness_real": row.inner_fitness_real,
                    "inner_fitness_surrogate": row.inner_fitness_surrogate,
                    "impostor_win_rate": row.impostor_win_rate,
                    "anchor_cross_entropy": row.anchor_cross_entropy,
                    "take_rate": row.take_rate,
                    "leak_test_passed": row.leak_test_passed,
                    "wall_clock_eval_s": round(row.wall_clock_eval_s, 1),
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
