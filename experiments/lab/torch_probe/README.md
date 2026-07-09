# The torch PPO+recurrent probe (Task 15.17 — experiment-tier, opt-in)

The owner's torch experiment, run where it cannot leak into the production
posture (owner decision 2026-07-05: torch as probe only; promotion is a pause
decision). One question for the pause: **does gradient RL with real POMDP
memory (PPO + GRU) beat the pure-Python ES ceiling by enough to justify
torch's costs** (dependency weight, cross-machine float determinism, CI
story)? Findings + the promotion recommendation live in
`experiments/lab/report-torch-probe.md`.

## Posture

- **torch never enters the project.** Not in `pyproject.toml`, not in
  `uv.lock`; the operator runs scripts with `uv run --with torch` (an
  ephemeral overlay environment). No CI job runs the probe.
- **mypy-excluded** (the ml_spike posture): this directory is on the
  `[tool.mypy] exclude` regex; `uv run mypy .` stays green without torch
  installed. ruff check + format still apply.
- **`entrant.py` is torch-free** — it is the comparability plumbing
  (TacticalRolloutEnv + encoder-v2 + the 15.15 `BakeoffPolicy`/
  `BakeoffEntrant` seam) and is exercised by the committed test
  `tests/experiments/test_torch_probe_excluded.py` with a CPU stub, so
  `uv run pytest` pins the wiring without torch.
- Production code never imports this directory (pinned by the same test).

## Comparability (the design constraint)

Same env, same features, same eval protocol as the 15.15 bake-off:

- **Rollouts:** `training.env.TacticalRolloutEnv` (the 15.8 seam), fast
  no-replay training path (15.8.1 knobs; trajectories identical to the
  recording path). Crew stays the frozen scripted FSM.
- **Features:** `agents.tactical.features.TacticalFeatureEncoder`
  (encoder v2, 111-dim on the canonical map).
- **Action space:** the 15.8 legal-action mask, mapped to the exact
  `MaskedMlpPolicy` head vocabulary (10 room slots + 7 kind slots,
  vent-room addition, canonical intent-key tie-break, emergency excluded).
- **Eval:** `training.bakeoff.harness.evaluate_candidate` under
  `default_protocol_config()` — the committed fixed eval seed config
  (`replays/ml_corpus/9p2i/splits.json` test split, `seed % 5 == 4`),
  consumed read-only. Rows land in `results-torch-probe.jsonl` here (the
  15.15 row schema); artifacts freeze under `artifacts/` (float-hex JSON +
  sha256). Nothing ships into `training/`.

Documented deviations (full discussion in the report): the memory-blind
`IntentSelector` seam means encoder features read a shadow `AgentMemory`
maintained through the production `agents.perception.ingest_packet` (meeting
belief-folds absent — the GRU's latent memory is the compensating mechanism
under test); the 15.15 anchor penalty enters training as a piKL-style
auxiliary loss rather than a reward term (eval-side anchor CE is charged by
the harness identically for every entrant).

## Running it

```bash
# Train one champion + score it through the committed harness protocol
# (local CPU, $0; the committed budget — wall-clock documented in the report):
uv run --with torch python experiments/lab/torch_probe/train_probe.py \
    --updates 100 --episodes-per-update 12 --torch-seed 0 --eval-repeats 3

# The seeded-run variance story: repeat with fresh torch seeds
uv run --with torch python experiments/lab/torch_probe/train_probe.py \
    --updates 100 --episodes-per-update 12 --torch-seed 1
uv run --with torch python experiments/lab/torch_probe/train_probe.py \
    --updates 100 --episodes-per-update 12 --torch-seed 2

# Distill the champion into the pure-Python MaskedMlpPolicy family
# (the escape hatch: capability without the dependency), agreement vs the
# pre-stated 0.90 bar + the student's own harness row:
uv run --with torch python experiments/lab/torch_probe/distill_probe.py \
    --teacher-artifact experiments/lab/torch_probe/artifacts/torch-ppo-gru-s1
```

If the default PyPI index is unreachable (or you want the small CPU-only
wheel), add `--index https://download.pytorch.org/whl/cpu` to the `uv run`
invocation.

## Files

- `entrant.py` — torch-free: shadow-memory featurizer, candidate/head-slot
  enumeration, `TorchProbePolicy` (the frozen `BakeoffPolicy` adapter),
  `TorchProbeEntrant` (the `BakeoffEntrant` adapter), per-decision reward
  split.
- `ppo_gru.py` — torch: the GRU policy/value net, the PPO learner, frozen
  scorer + artifact reload.
- `train_probe.py` / `distill_probe.py` — operator entry points (above).
- `results-torch-probe.jsonl` — one 15.15-schema row per champion / repeat /
  student.
- `artifacts/<entrant>/` — frozen weights (float-hex JSON + sha256 sidecar +
  config), reloadable via `training.bakeoff.harness.load_candidate_weights`.
