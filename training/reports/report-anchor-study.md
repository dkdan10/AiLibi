# The anchor study — λ sweep + filtered-BC anchor refinement (Task 18.5)

> **Task 18.5** (`tasks/phase-18.md`) — the two cheap levers on the exact
> gauges the champion failed (audits/audit-phase-18-planning.md §2.4; §6 the
> piKL reading).
> **Anchors:** training/bakeoff/harness.py `inner_episode_fitness` (:569-590,
> the anchor penalty seam); training/bakeoff/utility_es.py:708-718 (the full
> budget); replays/ml_corpus/9p2i/ (the filtered-BC source).
> **Substrate:** baseline-8; substrate sha `c845602d7e58f84920699d3d56aa12142b1b6b0f1a1cbfc1c1f3a0c287bd1677`
> (every frozen artifact under `training/artifacts/anchor_study/` carries it —
> the 18.24 stale-seed refusal reads it).
> **Committed artifacts:** `training/artifacts/anchor_study/<entrant>/`
> (float-hex `weights.json` + `weights.json.sha256` + `config.json` with the
> substrate sha) + `training/artifacts/anchor_study/study.json` (the
> deterministic index, the serialized `AnchorStudyReport`).
> **Command:** the λ sweep below is a RECORDING (§1.1); the corpus-derived
> half was re-run at Task 21.17 as `walk_corpus` + `fit_filtered_bc_anchor` +
> the substrate re-stamp, CPU-only, `$0`. The sweep's own budget, when it was
> searched, cost 1693 s training + 97 s scoring/walk = 1790 s wall-clock.
> **Report-only:** no champion ships from this study; the ES leg under the
> refined anchor is deliberately NOT run here (the harness's anchor-CE is
> computed against the FSM's own choice; the anchor-policy seam lands at
> 18.16, and the refined-anchor ES leg is a named 18.24 campaign entrant).

**The determinism cross-check, stated first:** λ=1.0 reproduced the committed champion **byte-identically** (committed `6d327dcbde94` == sweep `6d327dcbde94`).

## 1. Protocol (fixed before any run)

### 1.1 What was re-run at the baseline-8 re-ground, and what was not

The substrate this study binds to moved twice — the corpus was re-recorded, and
the selection floor it filters against was re-pinned to the adopted baseline. At
Task 21.17 the study was re-ground on those bytes, and the re-ground is
deliberately partial:

- **Re-run.** The corpus walk, the filtered-BC anchor fit, the offline agreement
  evaluation, and every artifact's substrate stamp. Every figure in §3 and §4
  below, and the `filtered-bc-anchor` weights, come from that run. The walk now
  replays the post-meeting absorb fold impostor-side, exactly as the live loop
  and `eval/off_menu.py` do; without it the impostor's resume-tick decision is
  taken against a memory the live agent never had, and 55 of the 150 committed
  games refused to re-derive.
- **NOT re-run: the λ grid.** The sweep rows, the champion genomes under each λ,
  and the λ=1.0 byte-identity cross-check are a RECORDING of a search made under
  the impostor fitness objective as it stood before Task 21.16 repaired it.
  Re-searching under a changed objective produces a new study, not a re-ground,
  and it would silently re-price a recorded result — so the cells are carried
  forward unchanged and only their substrate stamp moves.

That leaves one limitation worth meeting here rather than inferring: the
substrate sha `compute_substrate_sha` writes covers the corpus, the baseline id
and the flag floor, and **not the fitness objective**. Task 21.16's repair is
therefore invisible to the stale-seed fence — a λ cell whose search ran under
the prior objective ingests cleanly at the current sha. Re-searching the λ grid
(and the campaign that consumed it) under the repaired objective is a
campaign-scale decision, routed to the owner, not a documentation edit.

**Where a number below is a record of the prior corpus rather than a current
measurement, it is labelled as such.** The baseline-6 study read 6663 total
corpus decisions (5396 fit-side, weight total 7781) against 129 qualifying
games, with overall FSM agreement 0.7971 at anchor-CE 0.4568; those are history
and are not re-derivable from the committed bytes.

### 1.2 The fixed protocol

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
  the `flags_per_meeting` supply floor 0.973510
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
  0.8660 of decisions (CE
  0.4530); the committed champion matches on
  0.4133 (CE
  1.0121) — the champion has
  drifted far from the legible anchor, which is the under-anchoring symptom
  the §2.4 reading predicts.
- **Structurally-zero anchor weights are expected:** a conditional logit over
  a menu can only learn from features that VARY within the menu; the
  decision-level constants (cooldown, sabotage state, crowd density …) carry
  exactly zero gradient and stay at their zeros init — not a degenerate fit.

## 3. The filtered-BC anchor

**Filter census:** 150 games walked, every state hash and
every re-derived FSM decision verified. Crew-winning 114,
high-flag 82, both 71 →
125 qualifying games, 4375 fit
decisions (weight total 6523) of
5584 total corpus decisions;
0 FSM decisions were off the option menu
(excluded from the fit, tallied here — never silently dropped).

### 3.1 Offline FSM agreement (per-decision, top-1 by the frozen arbitration)

| Stream | decisions | agreement | mean anchor-CE (nats) | FSM off-menu | CE-clamped |
|---|---:|---:|---:|---:|---:|
| all corpus games | 5584 | 0.8660 | 0.4530 | 0 | 0 |
| in-filter games | 4375 | 0.8599 | 0.4706 | 0 | 0 |
| out-of-filter games | 1209 | 0.8883 | 0.3895 | 0 | 0 |
| committed utility-es champion | 5584 | 0.4133 | 1.0121 | 0 | 0 |

### 3.2 Where the anchor agrees, by FSM intent kind (all corpus games)

| FSM intent kind | decisions | anchor hits | agreement |
|---|---:|---:|---:|
| do_task | 1097 | 1062 | 0.9681 |
| kill | 678 | 674 | 0.9941 |
| move | 2418 | 2119 | 0.8763 |
| sabotage | 26 | 26 | 1.0000 |
| vent | 809 | 716 | 0.8850 |
| wait | 556 | 239 | 0.4299 |

### 3.3 Where it diverges and toward what (top cells, all corpus games)

| FSM chose | anchor chose | count |
|---|---|---:|
| move | move | 245 |
| wait | move | 180 |
| wait | do_task | 117 |
| vent | vent | 93 |
| move | do_task | 49 |
| do_task | move | 35 |
| wait | kill | 20 |
| move | wait | 5 |
| kill | sabotage | 4 |

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
