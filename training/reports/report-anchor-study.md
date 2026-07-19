# The anchor study — λ sweep + filtered-BC anchor refinement (Task 18.5)

> **Task 18.5** (`tasks/phase-18.md`) — the two cheap levers on the exact
> gauges the champion failed (audits/audit-phase-18-planning.md §2.4; §6 the
> piKL reading).
> **Anchors:** training/bakeoff/harness.py `inner_episode_fitness` (:569-590,
> the anchor penalty seam); training/bakeoff/utility_es.py:708-718 (the full
> budget); replays/ml_corpus/9p2i/ (the filtered-BC source).
> **Substrate:** baseline-5; substrate sha `8b08fd1031744d770c7e863bcbe27dfe3d964d8909a005976f47877380db725f`
> (every frozen artifact under `training/artifacts/anchor_study/` carries it —
> the 18.24 stale-seed refusal reads it).
> **Committed artifacts:** `training/artifacts/anchor_study/<entrant>/`
> (float-hex `weights.json` + `weights.json.sha256` + `config.json` with the
> substrate sha) + `training/artifacts/anchor_study/study.json` (the
> deterministic index, the serialized `AnchorStudyReport`).
> **Command:** `uv run python -m training.anchor_study run --budget full`
> (exit 0, 1479 s training + 90 s
> scoring/walk = 1569 s wall-clock, CPU-only, $0).
> **Report-only:** no champion ships from this study; the ES leg under the
> refined anchor is deliberately NOT run here (the harness's anchor-CE is
> computed against the FSM's own choice; the anchor-policy seam lands at
> 18.16, and the refined-anchor ES leg is a named 18.24 campaign entrant).

**The determinism cross-check, stated first:** λ=1.0 reproduced the committed champion **byte-identically** (committed `6d327dcbde94` == sweep `6d327dcbde94`).

## 1. Protocol (fixed before any run)

- **Sweep grid:** λ ∈ {0.25, 0.5, 1.0, 2.0, 4.0} over
  the committed utility-es `full` budget
  (`utility_es_budget("full", anchor_weight=λ)` — ES 20 gen × 12 pop × 6 train seeds, σ 0.3, seed 0);
  every champion scored through the standing fake-path protocol
  (`evaluate_candidate`, the frozen 30-seed corpus test split
  1004…1149), one shared protocol instance
  (one cumulative surrogate-staleness counter).
- **Fitness column caveat:** the reported inner fitness is the STANDING
  protocol's gauge (anchor weight 1.0 for every row — a common axis); each
  row's own-λ training objective is the `train champion fitness` row. The
  Pareto reading below uses mean shaped reward (performance) vs anchor-CE
  (legibility), both reported per row.
- **Filtered-BC filter (stated):** a corpus game qualifies iff its recorded
  winner is CREWMATES (crew-winning: the games where the evidence economy
  actually convicted) OR its persisted contradiction rows per meeting reach
  the `flags_per_meeting` supply floor 0.502793
  (high-flag: the supply gauge the champion failed, read off the committed
  meeting rows — conservative vs the referee's set-level gauge, which
  additionally re-derives transcript flags). Games satisfying BOTH weigh
  2× in the fit (the purest "watchable winning
  play" exemplars).
- **Fit recipe:** numpy weighted conditional logit over the FSM option menu
  (grouped by canonical intent key, the anchor-CE semantics), standardized
  features, zeros init, 300 full-batch epochs at lr
  0.3, no RNG — the `Fo6Logistic`/`BallotPredictor`
  deterministic recipe. Deterministic on a given platform; a cross-CPU refit
  agrees to float ULP (numpy SIMD summation grouping), so the committed bytes
  + sha sidecar are the frozen ground truth (the surrogate precedent).
- **Walk verification:** every corpus game's decision stream is re-derived by
  walking the recorded actions through the pure engine with the production
  observation/perception path, and EVERY re-derived FSM intent is verified
  against the recorded action (plus every recorded state hash) — a single
  divergence fails the study loud.

## 2. The λ sweep (5 cells, standing 30-seed protocol)

| Metric | λ=0.25 | λ=0.5 | λ=1.0 | λ=2.0 | λ=4.0 |
|---|---|---|---|---|---|
| inner fitness (real path, standing λ=1.0 gauge) | 18.2537 | 18.2537 | 18.6707 | 18.6707 | 19.2181 |
| mean shaped reward (real path) | 19.3000 | 19.3000 | 19.6667 | 19.6667 | 19.8000 |
| anchor-CE (nats) | 1.0548 | 1.0548 | 0.9953 | 0.9953 | 0.6109 |
| anchor-CE flagged (> 2.0 ceiling) | False | False | False | False | False |
| FSM intent agreement | 0.3055 | 0.3055 | 0.3972 | 0.3972 | 0.7743 |
| impostor win rate | 0.9333 | 0.9333 | 1.0000 | 1.0000 | 1.0000 |
| take-rate (opportunities) | 0.7686 (242) | 0.7686 (242) | 0.7629 (232) | 0.7629 (232) | 0.8644 (236) |
| referee mean (passed) | 3.42 (False) | 3.42 (False) | 3.63 (False) | 3.63 (False) | 3.62 (False) |
| supply floors passed | False | False | False | False | False |
| validity / leak / determinism | True/True/True | True/True/True | True/True/True | True/True/True | True/True/True |
| train champion fitness (own λ) | 20.4102 | 20.1538 | 19.7483 | 18.8300 | 18.0083 |
| weights sha256 (12-hex) | `702ac797b50d` | `702ac797b50d` | `6d327dcbde94` | `6d327dcbde94` | `3cc4058be554` |

### 2.1 Descriptor footprint (per-game means over the eval set)

| Descriptor | λ=0.25 | λ=0.5 | λ=1.0 | λ=2.0 | λ=4.0 |
|---|---|---|---|---|---|
| do_task_cadence | 2.839 | 2.839 | 2.920 | 2.920 | 3.070 |
| do_task_emissions | 74.333 | 74.333 | 72.767 | 72.767 | 79.000 |
| kill_count | 4.933 | 4.933 | 5.000 | 5.000 | 5.033 |
| median_kill_tick | 12.917 | 12.917 | 13.933 | 13.933 | 12.600 |
| meeting_count | 3.400 | 3.400 | 3.367 | 3.367 | 3.433 |
| meeting_trigger_rate | 0.131 | 0.131 | 0.134 | 0.134 | 0.131 |
| vent_usage | 0.000 | 0.000 | 4.700 | 4.700 | 4.800 |
| witness_exposure_rate | 0.155 | 0.155 | 0.140 | 0.140 | 0.147 |

### 2.2 Reading

- **The dial has plateaus:** λ=0.25/λ=0.5 froze the SAME genome (`702ac797b50d`); λ=1.0/λ=2.0 froze the SAME genome (`6d327dcbde94`) — at this ES budget no accept/reject comparison flips anywhere inside those bands (the fitness gap the λ change makes never re-orders an offspring against the incumbent).
- **The Pareto front (mean shaped reward ↑, anchor-CE ↓) is `lambda-4.0`:** every other cell is weakly dominated — at this budget on the fake path a HEAVIER anchor did not cost shaped reward (λ=0.25 shaped 19.30 / CE 1.055 → λ=4.0 shaped 19.80 / CE 0.611). The fake path mints no convictions, so fitness and legibility are not yet in tension here — the tension the champion failed on lives in the referee gauges, and NO cell passes the supply floors (the flip bar stays open; this study only positions seeds).
- **The refined anchor vs the committed champion, on the corpus stream:** the
  filtered-BC anchor matches the FSM's choice on
  0.7970 of decisions (CE
  0.4589); the committed champion matches on
  0.4131 (CE
  1.0800) — the champion has
  drifted far from the legible anchor, which is the under-anchoring symptom
  the §2.4 reading predicts.
- **Structurally-zero anchor weights are expected:** a conditional logit over
  a menu can only learn from features that VARY within the menu; the
  decision-level constants (cooldown, sabotage state, crowd density …) carry
  exactly zero gradient and stay at their zeros init — not a degenerate fit.

## 3. The filtered-BC anchor

**Filter census:** 150 games walked, every state hash and
every re-derived FSM decision verified. Crew-winning 101,
high-flag 86, both 70 →
117 qualifying games, 5573 fit
decisions (weight total 8439) of
7693 total corpus decisions;
0 FSM decisions were off the option menu
(excluded from the fit, tallied here — never silently dropped).

### 3.1 Offline FSM agreement (per-decision, top-1 by the frozen arbitration)

| Stream | decisions | agreement | mean anchor-CE (nats) | FSM off-menu | CE-clamped |
|---|---:|---:|---:|---:|---:|
| all corpus games | 7693 | 0.7970 | 0.4589 | 0 | 0 |
| in-filter games | 5573 | 0.7936 | 0.4685 | 0 | 0 |
| out-of-filter games | 2120 | 0.8057 | 0.4337 | 0 | 0 |
| committed utility-es champion | 7693 | 0.4131 | 1.0800 | 0 | 0 |

### 3.2 Where the anchor agrees, by FSM intent kind (all corpus games)

| FSM intent kind | decisions | anchor hits | agreement |
|---|---:|---:|---:|
| do_task | 1183 | 1147 | 0.9696 |
| kill | 746 | 731 | 0.9799 |
| move | 4221 | 3234 | 0.7662 |
| sabotage | 114 | 114 | 1.0000 |
| vent | 957 | 714 | 0.7461 |
| wait | 472 | 191 | 0.4047 |

### 3.3 Where it diverges and toward what (top cells, all corpus games)

| FSM chose | anchor chose | count |
|---|---|---:|
| move | move | 533 |
| move | kill | 329 |
| vent | vent | 243 |
| wait | move | 182 |
| move | do_task | 123 |
| wait | do_task | 91 |
| do_task | move | 20 |
| do_task | kill | 16 |
| kill | sabotage | 15 |
| wait | kill | 8 |
| move | wait | 2 |

## 4. Which candidates 18.24 should seed with

- `lambda-4.0`
- `filtered-bc-anchor`

The λ cells above are the (mean shaped reward ↑, anchor-CE ↓) Pareto set —
the fitness/legibility front the piKL reading says the anchor weight trades
along; dominated cells stay frozen (byte-addressable) but are not named.
`filtered-bc-anchor` is named as the 18.16 anchor-policy seam's entrant
configuration (the refined-anchor ES leg 18.24 runs), not as a champion.

## Reproduce

Every quoted number is a pure function of the committed bytes; nothing was
hand-computed.

```bash
uv run python -m training.anchor_study run --budget full
```

- The λ=1.0 byte-identity + artifact integrity pins:
  `uv run pytest tests/training/test_anchor_study.py -q`
- The frozen index: `training/artifacts/anchor_study/study.json` (this
  report's tables are a rendering of it).

**Determinism caveat:** the sweep and the corpus walk are bit-deterministic
across platforms (pure-Python ES RNG + the deterministic engine + the fake
provider); the filtered-BC fit is numpy full-batch GD — byte-identical on the
recording platform, ULP-equivalent elsewhere. The committed artifact bytes are
the frozen ground truth the sha256 sidecars pin.

## How downstream consumes this

- **18.24 (the impostor campaign)** seeds entrants from
  `training/artifacts/anchor_study/<entrant>/weights.json` (sha-verified
  reload), refusing any artifact whose `config.json` `substrate_sha` !=
  `compute_substrate_sha()` at the campaign substrate without the cheap
  deterministic re-fit/re-run.
- **18.16 (fitness stack)** adds the additive anchor-policy seam;
  `filtered-bc-anchor` is that seam's first candidate anchor.
- **18.4 / the campaign reports** read the sweep Pareto as the λ prior.
