# Torch PPO+recurrent probe — Results (Task 15.17)

> Code: `experiments/lab/torch_probe/`. Raw rows:
> `experiments/lab/torch_probe/results-torch-probe.jsonl`; frozen champions:
> `experiments/lab/torch_probe/artifacts/` (float-hex JSON + sha256).
> Experiment-tier, opt-in: run via `uv run --with torch` — torch is NOT in
> `pyproject.toml`/`uv.lock` and no CI job runs this. $0, local CPU.

**Decision informed:** the PAUSE's torch decision (owner decision 2026-07-05:
torch as probe only; promotion is a pause decision). One question: does
gradient RL with real POMDP memory (PPO + GRU) beat the pure-Python ES
ceiling by enough to justify torch's costs — dependency weight, cross-machine
float determinism, CI story (audits/post-phase-14-ML-training-signal.md §9;
audits/post-phase-14-ML-planning.md §9 Option 3)? **Date:** 2026-07-09.

## Headline

| Question | Result | Verdict |
|---|---|---|
| PPO+GRU vs the ES ceiling (same env, features, eval, ~same rollout budget) | inner fitness 10.96–11.05 vs policy-es 19.07 / utility-es 18.67; win rate 0.27 vs 1.00 | **NO — clean miss, all 3 seeds** |
| Determinism story | same-host double-run hash PASSED (tier stayed `candidate`); cross-machine bit-identity untestable and un-pinned (`--with` resolves fresh) | **doctrine cost stands** |
| Distillable into the pure-Python net (pre-stated bar ≥0.90) | held-out top-1 agreement **0.9709** (bar met on the 2nd, properly-tuned recipe; 1st attempt 0.7299) | **YES mechanically — but no capability worth taking** |

**Recommendation for the pause: KEEP EXPERIMENT-TIER, do not promote** (and
retire the torch track for Wave 2 unless the pause re-opens impostor reward
design — §Recommendation).

## Hypothesis

Option 3's claim (planning audit §9): recurrence is the natural POMDP memory
answer and gradient RL has the strongest asymptotics — worth torch's costs
only if Options 1–2 ceiling out. The 15.15 bake-off put the pure-Python
ceiling at inner fitness 19.07 (policy-es) / 18.67 (utility-es) with a 1.00
impostor win rate on the fixed eval set. The probe asks whether PPO + a GRU
(latent memory the explicit encoder cannot carry, e.g. meeting-fold residue)
clears that ceiling by a margin that prices in the dependency.

## Method — comparability is the design constraint

- **Rollouts:** `training.env.TacticalRolloutEnv` (the 15.8 seam), 9p2i,
  crew = frozen scripted FSM, fast no-replay training path (15.8.1 knobs;
  trajectories identical to the recording path). Train seeds = the first 24
  of the frozen corpus TRAIN split (`replays/ml_corpus/9p2i/splits.json`).
- **Features:** `agents.tactical.features.TacticalFeatureEncoder` (encoder
  v2, 111-dim), same as every 15.15 entrant.
- **Action space:** the 15.8 legal-action mask mapped to the exact
  `MaskedMlpPolicy` head vocabulary (10 room slots + 7 kind slots, vent-room
  addition, canonical intent-key tie-break, emergency excluded) — the torch
  head speaks the same language as the pure-Python family.
- **Eval:** every reported number is computed by
  **`training.bakeoff.harness.evaluate_candidate` under
  `default_protocol_config()`** — the committed 15.15 entrypoint on its fixed
  eval seed config (**`replays/ml_corpus/9p2i/splits.json` test split, 30
  seeds 1004…1149, `seed % 5 == 4`**, loaded by `load_eval_seeds`) — consumed
  read-only. Artifacts land under the probe dir, never `training/`.
- **Architecture:** encoder-v2 features → Linear(111→64) → tanh → GRU(64) →
  policy head (17) + value head; 33,298 parameters. PPO (clip 0.2, GAE
  λ=0.95, γ=1.0, Adam 3e-4, entropy 0.01, anchor-CE aux 0.3, 4 epochs/update,
  full-sequence BPTT), float64, CPU, `torch.set_num_threads(1)`.
- **Budget (honest, documented):** 100 updates × 12 episodes = **1,200
  training episodes per torch seed** — the same rollout-count band as the ES
  entrants (policy-es 840, utility-es 1,440 fitness rollouts). Three torch
  seeds (0, 1, 2). Training wall-clock 410–434 s per seed.

### Documented deviations

1. **Shadow memory at the selector seam.** The 15.8 `IntentSelector` seam is
   deliberately memory-blind (`training/determinism.py` docstring), so the
   memory-carrying encoder reads a shadow `AgentMemory` folded through the
   production `agents.perception.ingest_packet` — identical to the live
   memory tick-for-tick during play, missing only meeting-time belief folds
   (the absorb hooks). The frozen policy uses the same shadow at eval, so
   train/eval features are one distribution. Carrying the meeting-fold
   residue latently is exactly the recurrence question under test.
2. **Anchor as auxiliary loss.** The 15.15 anchor discipline enters training
   as a piKL-style auxiliary cross-entropy (weight 0.3) rather than a reward
   term; the EVAL-side anchor CE is computed by the harness identically for
   every entrant, so the reported fitness is comparable.
3. **Crew emergency canonicalization.** The documented 15.8 exact-equality
   mask gap (`eval/leak_test.py:608-616`; the fix is 15.16's env.py region)
   makes a selector delegating a crew FSM emergency raise. The probe remaps
   a crew delegation to the mask's same-`intent_key` object (and mirrors the
   engine's rejection no-op with WAIT for a spent-budget kill-witness
   emergency); neither changes an engine decision.

## Results

### The seeded-repeat story (no single-run claims)

Three independently seeded PPO runs, each scored once through the committed
protocol (rows 1–5 of `results-torch-probe.jsonl`; the s0 champion re-scored
3×):

| torch seed | validity | referee mean / median | supply floors | inner fitness (real) | inner fitness (surrogate) | shaped reward | win rate | anchor CE | take-rate (opps) | determinism | train s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | PASS | 3.04 / 1.05 | FAIL² | 10.963 | 6.899 | 12.93 | 0.267 | 2.035 ⚠ | 1.00 (226) | PASS | 434.0 |
| 1 | PASS | 3.04 / 1.05 | FAIL² | 11.050 | 6.977 | 12.93 | 0.267 | 1.937 | 1.00 (226) | PASS | 428.1 |
| 2 | PASS | 3.04 / 1.05 | FAIL² | 10.971 | 6.917 | 12.93 | 0.267 | 2.023 ⚠ | 1.00 (226) | PASS | 410.4 |
| **spread** | 3/3 PASS | 3.04 all | — | **min 10.963 / mean 10.995 / max 11.050** | 6.90–6.98 | 12.93 all | **0.267 all** | 1.94–2.04 | 1.00 all | 3/3 PASS | 410–434 |

² the same two structurally-failing fake-provider supply floors
(`flags_per_meeting` 0.0 < 1.863, `testimony_backed_conversion` None < 0.607)
every 15.15 entrant fails; the discriminating gauge, `witnessed_event_rate`,
is 0.149 — 2.2× the ES entrants' 0.067, i.e. maximally exposed play.

**The striking repeat finding:** all three seeds converge to *behaviorally
identical* greedy policies on the eval set — identical trajectories (shaped
reward 12.93, 226/226 clean kills taken, 8/30 wins, referee 3.04 in every
row); only the softmax margins differ (anchor CE 1.94–2.04). Training-seed
variance in outcome metrics is exactly zero; the spread that remains lives in
the anchor CE column. Additionally, the s0 champion re-scored 3× through
`evaluate_candidate` produced bit-identical rows, and a separate-process
artifact-reload re-run reproduced row 1 exactly (including the determinism
`frame_stream_sha256`).

**What PPO learned (the training-vs-eval gap):** the sampled training policy
plateaus at shaped reward ~17–18 on the train seeds (FSM parity is 20.33,
`training/reports/report-impostor-bakeoff.md` §7); the argmax-frozen policy
scores 12.93 on the test seeds. The learned behavior is reckless killing —
take-rate 1.00 vs the FSM's 0.47 and the ES entrants' 0.76–0.92, witnessed
exposure 2.2× the ES rows, win rate 0.27. PPO found the shaped reward's
degenerate maximum (kills are worth ~10–20 points, the terminal win ±1), a
maximum the same-fitness ES entrants never reached — they win 0.93–1.00.
This is a Goodhart data point for the reward channel, not evidence of missing
optimizer power: gradient RL exploited the objective *better* and the games
*worse*.

### Against the pure-Python ceiling (the committed 15.15 rows)

| Metric | bc-dagger | utility-es | policy-es | map-elites | **torch-ppo-gru (best, s1)** |
|---|---|---|---|---|---|
| Inner fitness (real) | 5.17 | 18.67 | 19.07 | 18.20 | **11.05** |
| Referee mean | 1.02 | 14.62 | 6.32 | 6.13 | **3.04** |
| Impostor win rate | 0.07 | 1.00 | 1.00 | 0.93 | **0.27** |
| Anchor CE (ceiling 2.0) | 1.96 | 1.00 | 2.02 ⚠ | 1.97 | **1.94** |
| Take-rate | 0.47 | 0.76 | 0.76 | 0.92 | **1.00** |
| Wall train (s) | 9.2 | 219.6 | 147.9 | 75.4 | **428.1** |

The probe's one question answers **NO**: at a comparable rollout budget,
recurrent PPO does not beat the utility-scorer+ES entrant on the same
features — it lands 7.6 fitness points and 0.73 win-rate points below it,
at ~2× the training wall-clock. The GRU's latent memory bought nothing
measurable: the three champions' converged behavior is indistinguishable
from a memoryless greedy kill policy.

### Determinism

The task contract expected the determinism-harness hash to FAIL for a torch
policy; the honest measured result is that it **PASSED on this host**: the
15.10 double-run (`run_policy_determinism`, seeds (1004, 1009)) produced
matching frame-stream and state-hash digests for all three champions and the
student, so every row kept `tier="candidate"` and the experiment-tier
`repeat_spread` path was never triggered by a real run. Single-threaded
float64 CPU torch was bit-stable within a process, across the 3 repeat
re-scores, and across separate processes (the artifact-reload re-run
reproduced `frame_stream_sha256` exactly).

What this does NOT establish: the doctrine cost was never same-host
repeatability — it is **cross-machine** bit-identity (FP non-associativity
across BLAS builds/ISAs, arXiv:2408.05148; planning audit §9 Option 3),
which one container cannot test. Worse for the CI story, the probe's
environment is deliberately unlocked: `uv run --with torch` resolves a fresh
torch at every invocation (2.13.0+cu130 today), so today's hashes are not
durable claims. The committed wiring test
(`tests/experiments/test_torch_probe_excluded.py`) pins the harness's
experiment-tier (determinism-FAIL-tolerant) row path with a deliberately
drifting CPU stub, so the seam the contract names stays exercised in
`uv run pytest` regardless.

### Distillation (the escape hatch)

**The bar, pre-stated before distillation** (mirroring the 15.15
`BC_INTENT_AGREEMENT_BAR` discipline): **≥ 0.90 held-out top-1
student-teacher intent agreement** (`distill_probe.DISTILL_AGREEMENT_BAR`).
Student = the pure-Python `MaskedMlpPolicy` family (encoder-v2 → tanh MLP
h=8 → the shared 17-slot head, genome 1049), trained by CE on teacher-driven
TRAIN-split decisions (live-memory features — what the student sees at its
own eval), measured on teacher-driven VAL-split games (722 held-out
decisions). Teacher: the s1 champion, reloaded from its committed artifact.

- Attempt 1 (30 harvest seeds ≈ 2.0k decisions, lr 0.05, 400 epochs):
  train accuracy saturated at 0.71, held-out agreement **0.7299 — below the
  bar**. Reported, not hidden.
- Attempt 2 (60 harvest seeds = 3,898 decisions, lr 0.01, 1,500 epochs — the
  committed script defaults): held-out agreement **0.9709 — bar MET**.

The student's own tuple row (row 6 of the jsonl): validity PASS, referee
mean 1.04, inner fitness **−2.58**, win rate **0.067**, anchor CE 11.7
(flagged), determinism PASS (pure-Python, as expected). High state-level
agreement did not survive closed-loop rollouts — the 3% disagreement
compounds when the student drives its own games (the classic BC shift). The
escape hatch is *mechanically real* (a torch policy this coarse distills
into the Wave-1 inference net above the bar) but there is no capability
worth taking this wave: the teacher itself sits far below the ES ceiling.

## Costs (what promotion would buy into)

- **Dependency weight:** `uv run --with torch` resolved 29 packages into a
  **4.5 GB** ephemeral overlay (torch 1.1 GB + NVIDIA CUDA runtime libs
  2.7 GB, unused on CPU; the CPU-only wheel index trims this but was
  unreachable through this environment's proxy). Against a lock that is
  pure-Python today, this is the heaviest dependency the project would ever
  carry.
- **Determinism doctrine:** same-host hashes held, but cross-machine
  bit-identity remains unverifiable and the unlocked `--with` resolution
  makes even the measured hashes time-fragile. Promotion would re-open the
  determinism doctrine for no measured benefit.
- **CI story:** the probe cannot run in CI without installing torch; the
  committed torch-free wiring test covers the comparability seam instead.
  Keeping it experiment-tier costs CI nothing.

## Recommendation for the pause

**Do not promote torch. Keep the probe experiment-tier** — and if the pause
does not re-open impostor reward design, **retire the torch track for
Wave 2**. Priced:

- **Measured gain: absent (negative).** Best torch fitness 11.05 vs the ES
  ceiling 19.07; win rate 0.27 vs 1.00; at ~2× ES wall-clock and the same
  rollout budget. Recurrence showed no measurable advantage on the one axis
  it was hired for.
- **The one confound is the objective, not the optimizer.** PPO maximized
  the shaped reward more effectively than ES did and lost the games doing
  it (take-rate 1.00, exposure 2.2×, terminal win worth ±1 against ~10–20
  kill points). If the pause re-weights the terminal/win term in
  `training/rewards.py`, THIS probe is the cheap pre-registered instrument
  to re-run — that is the only reason to keep it rather than retire it now.
- **Costs all point the same way:** 4.5 GB overlay, cross-machine
  determinism unverifiable, no CI path. The distillation hatch (0.97
  agreement) means even a future torch win could ship pure-Python — so
  promotion is unnecessary even in the probe's success branch.

**Wall-clock + hardware:** ~30 min total probe compute — 3 × ~7.1 min
training (410–434 s), 14–15 s per protocol eval row, ~4 min distillation —
on a 4-core x86_64 Linux container (Linux 6.18.5, glibc 2.39, 15 GB RAM),
Python 3.11.15, torch 2.13.0+cu130 (PyPI default resolution, CPU execution,
1 thread), $0.
