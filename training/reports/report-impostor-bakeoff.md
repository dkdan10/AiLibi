# The impostor bake-off — four training methods, one harness, one seed set, one report

> **Task 15.15** (`tasks/phase-15.md`) — the wave's centerpiece: BC/DAgger,
> utility-scorer+ES, direct policy-net+ES, and MAP-Elites, all impostor-side, all
> trained and evaluated against the baseline-3 substrate through ONE harness so
> the mid-phase pause compares METHODS, not evaluation protocols.
> Anchors: `audits/post-phase-14-ML-planning.md` §5.2 (the option vocabulary),
> §9 (the paradigm comparison); `audits/post-phase-14-ML-training-signal.md` §4
> (the objective spine: competence + anchor-KL + QD; referee as GATE);
> `agents/tactical/impostor_policy.py` (`_scored_targets` :937-1009, the decide
> ladder :261 — the frozen anchor and oracle, read-only);
> `experiments/lab/ml_spike/check2_learnability.py` + `fo9_diversity.py` (the ES
> priors).
> Code: `training/bakeoff/harness.py` (entrant protocol + fixed eval protocol +
> report emitter), `training/bakeoff/{bc,utility_es,policy_es,map_elites}.py`
> (the entrants), `training/bakeoff/es.py` (shared-core extensions).
> **Date:** 2026-07-09. **Corpus:** `replays/ml_corpus/9p2i` (150 games, FROZEN
> at `fd531d4`; splits committed by 15.12).
> **Committed artifacts:** `training/artifacts/impostor/<entrant>/weights.json`
> (float-hex JSON) + `weights.json.sha256` + `config.json`, one per entrant;
> machine-readable rows in `training/reports/results-impostor-bakeoff.jsonl`
> (the 15.18 input). **Cost:** $0, CPU-only; wall-clocks in §3.

---

## 1. The fixed protocol (stated before any training ran)

- **One harness.** Every entrant trains through
  `training.bakeoff.harness.rollout_candidate` (the real production loop —
  `HeadlessGame` through the candidate's own agent factory) and is scored ONLY
  by `harness.evaluate_candidate`. A committed AST firewall test
  (`tests/training/test_bakeoff_harness.py::test_entrant_modules_never_import_eval`)
  proves no entrant module imports `eval.*` — the harness is the only module
  that computes reported metrics.
- **Fixed eval seed set.** The frozen corpus TEST split —
  `replays/ml_corpus/9p2i/splits.json`, the 30 seeds with `seed % 5 == 4`
  (1004 … 1149) — asserted by a committed test. Training draws only TRAIN-split
  seeds; the BC held-out agreement set draws the VAL split.
- **Training meeting path.** The deterministic fake-provider meeting path. The
  committed 15.13 GO/NO-GO verdict is **NO-GO**
  (`training_time_runner="fake-provider-meeting-manager"`,
  `training/reports/report-ballot-surrogate.md`), so per the fallback ladder the
  fake-provider MeetingManager is the training-time runner and the surrogate is
  consumed as an EVAL divergence column (within its staleness cap) and for the
  §6 Goodhart re-run. `surrogate_uses_training = 0` on every row.
- **The shared inner fitness** (every ES/QD entrant, identical): the
  tactically-reachable side-specific impostor terms + potential shaping
  (`training.rewards.compute_shaped_reward(..., "IMPOSTOR").total()`) MINUS an
  anchor-KL penalty toward the frozen FSM, weight 1.0 — measured as the anchor
  cross-entropy, the mean per-decision log-loss of the candidate's choice
  distribution at the FSM's deterministic choice (the piKL-style penalty; a
  literal KL against a deterministic anchor's delta distribution is
  degenerate). A tick-budget-truncated episode scores the documented constant
  −10.0, never a full-game read. The validity gate and the 15.2 referee are
  SELECTION filters applied after training — never fitness terms.
- **Pre-stated bars.** BC held-out top-1 intent agreement bar: **≥ 0.90**
  (`harness.BC_INTENT_AGREEMENT_BAR`, the contract default — no different bar
  was documented before training). Anchor-CE ceiling: **2.0 nats** mean
  (`harness.ANCHOR_CE_CEILING`, documented in code before the runs; no audit
  commits a numeric ceiling, so this report's ceiling is the committed one).
  Rows above the ceiling are FLAGGED, never dropped.
- **Per-candidate gates, all through the candidate's OWN policy factory:** the
  15.10 determinism harness (`run_policy_determinism`, double-run over seeds
  1004/1009 at 9p2i — a FAIL demotes the row to experiment-tier and attaches
  the full `PolicyDeterminismReport` + an N-repeat metric spread, the seam the
  15.17 torch entrant reports through) and the leak-test factory mode
  (`eval.leak_test.scan_factory_packets` — the 15.10 `_IdleExploreAgent`
  reference wrapper runs no encoder and does not count; these factories run the
  candidate's real encoder + head on every impostor decision).

---

## 2. The entrants and their budgets

| Entrant | Method | Genome | Budget (recorded) | Train wall-clock |
|---|---|---|---|---|
| `bc-dagger` | Behavior-clone `ImpostorPolicy.decide` on encoder-v2 features + DAgger | 1049 (encoder-v2 111 → tanh 8 → 17-slot masked head) | harvest 12 train seeds, 2 DAgger rounds × 6 seeds, 30 epochs, lr 0.2, from-scratch retrain per round | 9.2 s |
| `utility-es` | Learned linear utility over the FSM's own option menu + (1+λ)-ES | 19 (18 option features + bias) | ES 20 gen × 12 pop × 6 train seeds, σ 0.3 (1446 games) | 219.6 s |
| `policy-es` | Direct masked policy net (full masked intent space) + (1+λ)-ES, warm-started from the BC clone | 1049 (same family as BC) | ES 14 gen × 10 pop × 6 train seeds, σ 0.15 (846 games) | 147.9 s |
| `map-elites` | MAP-Elites over three named 15.8 descriptors, competence as cell quality, warm-started from the BC clone | 1049 (same family) | 120 iterations + 6 inits × 4 train seeds (504 games) | 75.4 s |

The crew side stayed the frozen scripted FSM throughout (no co-evolution this
wave). The ES priors (σ, population shape, elitist (1+λ), K-seed averaging,
BC warm-start) inherit the ml-spike's check-2/fo9 settings. In the shared MLP
family a vent candidate scores its kind slot plus the room slot of its vent's
room, so the vent-EXIT choice is learned through the room head rather than a
lexical vent-id tie; the utility menu mirrors the FSM's lower-id-fellow kill
DEFERRAL as a hard invariant while leaving the witness gate to the learned
ranking it replaces (both from the PR #242 review). Everything ran on CPU at
$0; the whole `run --budget full` pass (train + eval, all four) took
**8 m 28 s**.

---

## 3. Results — the single metric tuple (one row per entrant)

Every number regenerates from `results-impostor-bakeoff.jsonl` (committed) or
by re-running the CLI in §8. Fitness columns are the SHARED inner fitness on
the 30 fixed eval seeds; "real" is the fake-provider meeting path, "surrogate"
the 15.13 ballot-predictor path — both reported, divergence is data.

| Metric | bc-dagger | utility-es | policy-es | map-elites |
|---|---|---|---|---|
| Validity gate | PASS | PASS | PASS | PASS |
| Referee `referee_passed` | False | False | False | False |
| Referee mean / median score | 1.02 / 0.20 | **14.62 / 16.80** | 6.32 / 3.70 | 6.13 / 3.70 |
| Floor-trip rate | 0.00 | 0.00 | 0.00 | 0.00 |
| Inner fitness (real path) | 5.17 | 18.67 | **19.07** | 18.20 |
| Inner fitness (surrogate path) | 3.10 | **11.32** | 7.26 | 7.86 |
| Surrogate − real divergence | −2.07 | −7.36 | −11.81 | −10.34 |
| Anchor cross-entropy (ceiling 2.0) | 1.96 | **0.99** | 2.02 ⚠ FLAGGED | 1.97 |
| Impostor win rate (reported, never gated) | 0.07 | **1.00** | **1.00** | 0.93 |
| Take-rate (kills / clean opportunities) | 0.47 (281 opps) | 0.76 (232) | 0.76 (365) | 0.92 (304) |
| Determinism (double-run) | PASS | PASS | PASS | PASS |
| Leak test (own factory) | PASS (381 pkts) | PASS (538) | PASS (541) | PASS (565) |
| Surrogate staleness uses (train / eval) | 0 / 37 | 0 / 74 | 0 / 99 | 0 / 88 |
| Wall-clock train / eval (s) | 9.2 / 12.1 | 219.6 / 10.2 | 147.9 / 16.7 | 75.4 / 15.6 |
| Weights sha256 (prefix) | `ddb1e706ae1a` | `6d327dcbde94` | `561e5ff36478` | `b4469dec6f95` |

Supply floors (baseline-3, 9p2i) on every candidate's eval set:
`witnessed_event_rate` PASSES for all four (0.067–0.155 vs floor 0.032);
`flags_per_meeting` (floor 1.863) and `testimony_backed_conversion` (floor
0.607) FAIL for all four — under fake-provider meetings the meeting-driven
evidence supply is structurally absent (no contradiction flags, no
observation-backed accusations), so `referee_passed=False` for every candidate
by the two-layer design, exactly as the 15.14 probe documented. The referee
gate therefore does not yet DISCRIMINATE among these candidates; its geomean
column does.

All four rows are `tier="candidate"` (determinism PASS), so no N-repeat spread
was attached; the experiment-tier path is exercised by a committed test
(`test_experiment_tier_carries_spread`) — the 15.17 torch entrant reports
through it.

---

## 4. The BC entrant vs its pre-stated bar — the encoder-sufficiency finding

**Held-out top-1 intent agreement: 0.365 (794 held-out FSM decisions, VAL
split) vs the pre-stated bar 0.90 — the bar is MISSED decisively**, so the
encoder gaps are the finding (task contract). Per-kind confusion (from the
committed row's `train_metadata.per_kind_agreement`):

| FSM intent kind | decisions | clone agreement |
|---|---|---|
| kill | 65 | **0.708** |
| vent | 77 | 0.545 |
| move | 479 | 0.415 |
| do_task | 97 | 0.031 |
| wait | 61 | 0.000 |
| sabotage | 15 | 0.000 |

Named gaps, in order of mass:

1. **`move` (60% of all FSM decisions, 41.5% cloned)** — the stalk/route
   DIRECTION. The FSM's move is `find_path(own_room → best target's sighting
   room)[1]` — a function of the scored-target ranking plus A* topology.
   Encoder v2 carries per-room last-seen occupancy and per-slot last-seen
   ages, but NOT a "next-hop-toward-X" representation: a linear-in-features
   head over room slots has to re-derive shortest-path routing from raw
   occupancy, which a 1049-parameter tanh MLP learns only partially at this
   budget. This is the same history/structure gap the planning audit §6.3
   named for the spike encoder — v2 closes the memory HALF (the clone finds
   the right ACTION kind: kill agreement is 0.71), not the routing half.
2. **`do_task` / `wait` (3.1% / 0%)** — the blend/hold discipline. Both are
   low-salience "null" actions whose trigger is the ABSENCE of targets plus
   task-room co-location; the softmax head systematically prefers a move
   slot. A candidate-conditioned head (score the legal intent list, as the
   utility-scorer does) rather than a fixed 17-slot head is the structural
   fix.
3. **`sabotage` (15 decisions, 0%)** — pure class imbalance: 15 labels in a
   1612-sample dataset cannot move a CE objective. The predicate is trivially
   computable from `global_status` features the encoder already carries.

Consistent with the spike's check-2 lesson (BC alone caps below FSM parity; ES
climbs from it), the clone still functioned as the warm start: `policy-es`
seeded from this genome opened at fitness 6.58 vs its random-init sibling's
sub-1 starts and reached 18.96 (`train_metadata.fitness_trace`).

---

## 5. MAP-Elites — measured archive coverage; descriptor footprints for the single-objective entrants

Archive: 6×4×4 = 96 cells over (`kill_count`, `witness_exposure_rate`,
`vent_usage`) — three of the named 15.8 descriptors
(`training.rollout.DESCRIPTOR_VECTOR_FIELDS`). **Coverage: 30/96 cells =
0.3125** after 126 evaluations (120 iterations + 6 seeds/inits at 4 train
seeds each). Champion cell [5, 0, 3] (5+ kills, zero witnessed exposure,
heavy venting) at cell quality 18.86. Best-per-cell quality spans −2.61 (the
0-kill corner) to 18.86, and the archive now spreads across the vent axis
(16/5/2/7 cells in vent bins 0–3): making the vent-exit choice learnable
through the room head (PR #242 review; §2) opened the axis that the
pre-review archive left almost entirely unexplored — coverage more than
doubled at the identical budget.

Descriptor footprints (mean over the 30 eval seeds, from each row's
`descriptor_footprint`) — the one-point comparison for the single-objective
entrants:

| Entrant | kill_count | witness_exposure | vent_usage | meeting_count | do_task_emissions |
|---|---|---|---|---|---|
| bc-dagger | 1.93 | 0.12 | 0.0 | 1.47 | 85.4 |
| utility-es | 5.00 | 0.14 | 4.7 | 3.37 | 72.8 |
| policy-es | 5.00 | 0.07 | 20.3 | 4.43 | 76.9 |
| map-elites (champion) | 4.87 | 0.08 | 22.3 | 4.10 | 74.8 |
| scripted FSM (measured through the same protocol, §8) | 4.93 | 0.03 | 7.3 | 3.87 | 81.8 |

The two direct-policy champions (policy-es and the map-elites champion)
CONVERGE on the same low-exposure heavy-vent region of the grid (~20+ vent
submissions/game vs the FSM's 7.3) — vent-heavy movement is what the shared
fitness rewards once the vent choice is learnable — while utility-es reaches
the same kill count at near-FSM vent usage (4.7) because its bounded menu
only offers the vents the FSM ladder itself would generate. The archive's
value is exactly this map: it shows the monoculture direction the
single-objective optimizers pull toward and holds 29 other filled cells the
pause can inspect.

---

## 6. The 15.14 obligation — the Goodhart probe under the surrogate meeting path

Discharged through the probe's OWN entry point —
`run_goodhart_probe(meeting_runner_factory=load_surrogate_runner_factory(...))`
— INCLUDING the forced single-tactic reachability sweep (the net that found the
15.14 exploit; the committed 15.14 ES budget alone only recovered to baseline,
+1.7%). Budget: the committed 15.14 shape (6 generations × 6 population, σ 0.5,
seed 0) re-anchored on the fixed eval seed set (all 30 test-split seeds as
fitness seeds — 37 genome evaluations + 5 sweep levers ≈ 1,320 games).
Surrogate staleness usage: 2,344 simulated meetings (cap 50,000). Wall-clock
241 s. Regenerate with the §8 `goodhart-surrogate` command.

**Delta verdict (appended to the 15.14 findings):** 15.14 fake-provider
verdict **EXPLOITS_FOUND** (strongest reachable 16.62, +155%, via the forced
`kill` lever's D2-separation "suspicion theater") → surrogate-path verdict
**HELD** (champion 0.0, strongest reachable 0.53, `referee_passed=False`
everywhere). **A HELD here must NOT be read as exploit-caught** — it is held
for a disqualifying, structural reason, exactly the wrong-reason regime the
task contract warns about:

1. **The validity gate fail-closes EVERY surrogate-path set, including the
   scripted-FSM baseline** (`baseline_validity_passed=false`; the ES fitness
   trace is pinned at the invalid sentinel −1.0 for all 6 generations, so the
   probe searched a flat all-invalid landscape and decomposed zero
   improvements). The failing check is `cost_and_provenance_exact` — surrogate
   meetings return empty LLM metadata (`llm_calls=()`, `prompt_versions={}`),
   so the recorded replays carry no model provenance row ("no model recorded on
   any game cost row"). The 15.2 geomean gate never even engaged.
2. **The surrogate's ejection/SKIP rate, alongside the verdict** (the
   scripted-FSM baseline on the same 30 eval seeds): the surrogate resolves
   **73/79 meetings with an ejection (ejection rate 0.924, SKIP rate 0.076)**;
   the fake-provider path on the same seeds resolves **0/116 with an ejection
   (rate 0.000)**. The contract warned an UNDER-ejecting surrogate could hold
   the meeting-driven floors for the wrong reason; the measured failure is the
   mirror image — an OVER-ejecting surrogate ends games so fast that the
   champion set's `witnessed_event_rate` (0.020) falls below its floor (0.032)
   and the two meeting-driven floors still never clear
   (`flags_per_meeting=0.0`: the surrogate synthesizes ballots, not the
   contradiction flags the gauge counts). Either way the floors hold for
   supply reasons, not because the referee caught an exploit.
3. **What the sweep DID show:** the 15.14 kill-lever exploit does not
   reproduce under a meeting model that actually ejects — the forced `kill`
   lever scores 0.57 vs baseline 0.53 (**+7.5%**, vs +155% under fake
   meetings; both far under the 25% materiality bar), because ejections
   convert the "suspicion theater" into resolved games instead of letting D2
   separation inflate unpunished. `wait` (stall-to-clock) remains
   self-defeating (0.1, floor-tripped), `emergency`/`report` meeting-farming
   remain null (0.0).

**Routed to the pause:** (a) before the surrogate can serve as a
referee-attack substrate, either the provenance check needs an explicit
surrogate-path mode or the surrogate runner needs a declared synthetic
provenance stamp — today the validity gate (correctly, fail-closed) makes
every surrogate-scored set invalid; the over-ejection itself (not the
provenance check) is what drives the one-signed surrogate-vs-real fitness
divergence in §3 — ejected impostors stop killing; (b) the two committed meeting
models BRACKET the real-LLM path from opposite sides (fake: 0% ejections,
evidence-starved; surrogate: 92% ejections, evidence-free ballots) — neither
is a trustworthy referee substrate alone, so the pause's exploit adjudication
should rest on the 15.14 fake-path findings plus a real-LLM spot-check, not on
this HELD.

---

## 7. Ranked recommendation + open risks — FOR THE PAUSE

This ranking is an INPUT to the 15.18 pause, explicitly not a self-declared
winner: the referee gate cannot yet discriminate (§3), the surrogate/real
divergence is unresolved (risk 1), and the finalist evaluation runs on the
real-LLM path the pause owns.

1. **`utility-es` — recommended first candidate for Wave-2 productization
   consideration.** Within 2% of the best inner fitness (18.67 vs 19.07),
   tied-best win rate (1.00), the LOWEST anchor cross-entropy (0.99 — the
   most FSM-legible champion), the best referee geomean (14.62 mean / 16.80
   median), the best surrogate-path fitness (11.32 — most robust to the
   meeting-model swap), a 19-weight interpretable genome, and a structural
   no-illegal/off-menu-actions guarantee (the menu is pinned by test, and the
   FSM's kill-deferral coordination invariant is mirrored). Its ceiling is
   the FSM's option menu — it cannot discover an off-menu behavior.
2. **`policy-es` — the higher-ceiling path; carries the higher Goodhart-shaped
   risk.** Best real-path fitness (19.07) and the only entrant to EDGE PAST
   the scripted FSM on raw shaped reward through the same protocol (21.10 vs
   the FSM's 20.33 — FSM-parity crossed). But it is the one anchor-CE-FLAGGED
   row (2.02 > the 2.0 ceiling, marginal), carries the LARGEST surrogate
   divergence (−11.81), and shows the vent tell: 20.3 vent submissions/game
   vs the FSM's 7.3 — it leans on the vent channel the fake meeting path
   never punishes. Treat its real-path numbers as upper bounds pending the
   pause's real-LLM eval.
3. **`map-elites` — the diversity instrument, now within reach of the
   specialists.** Champion at 18.20 (0.9 behind the best) and the only
   measured behavioral map (30/96 cells); its champion converges on
   policy-es's low-exposure heavy-vent region, which is itself the finding —
   the archive names the monoculture direction. Scale iterations before
   judging QD's ceiling.
4. **`bc-dagger` — a warm start and a measurement, not a candidate.** Missed
   its 0.90 bar at 0.365 (§4). Its value was proven as the ES seed (the
   BC-then-ES climb from 6.58 to 18.96) and as the encoder-gap finding.

**Open risks for the pause:**

- **Surrogate/real divergence is large and one-signed** (−2.1 … −11.8 on every
  row): the surrogate path ejects learned aggression far more than the
  fake-provider path (§6 ejection rates). Until one of the two meeting models
  is validated against the real-LLM path, any champion ranking is
  meeting-model-conditional; the pause's finalist eval must re-score on real
  meetings before trusting either column.
- **The referee gate is non-discriminating under fake meetings** — every
  candidate fails the same two meeting-driven supply floors. The gate becomes
  meaningful only on a meeting path that supplies evidence (surrogate §6, or
  real LLM); a Wave-2 selection that gates on `referee_passed` under fake
  meetings would select on noise.
- **Take-rates of 0.76–0.92** for the ES/QD champions sit well above the
  scripted FSM's — 0.55 measured through this protocol on the eval seeds (§8;
  the planning audit §4.3 measured ≈0.48 on the committed corpus). More
  decisive play was the objective, but a high-take impostor is the shape the
  watchability floors exist to catch — re-check under the pause's
  real-meeting referee, where the crew can actually convict.
- **Anchor-CE ceiling (2.0) is this report's documented choice**, not an
  audit-committed number — and policy-es sits ON it (2.02, flagged). The
  pause should ratify or move the ceiling before Wave-2 uses it as anything
  stronger than a flag.
- **Ranking stability:** utility-es and policy-es are 0.4 fitness apart on a
  30-seed set with per-game fitness variance far larger than that gap; the
  pause should not read rank 1 vs rank 2 as significant without the real-LLM
  re-score.
- **Within-kind target ties in the direct-policy family** remain lexical
  (several co-located kill targets; several bodies in one room — PR #242
  review): every submission-legal intent stays reachable, but the policy
  cannot yet express a preference inside those ties, and the FSM anchor
  offers no supervision there (it only kills unwitnessed, where the candidate
  is unique). If Wave-2 productizes the direct-policy path, widen the head
  (e.g. per-roster-slot kill preferences) before scaling budgets.

---

## 8. Reproduce

Every quoted number is a pure function of the committed bytes (weights,
corpus, splits) and these commands; nothing here was hand-computed.

```bash
# The full bake-off: trains all four entrants at the recorded budgets,
# re-evaluates them through the fixed protocol, rewrites the jsonl + artifacts.
uv run python -m training.bakeoff.harness run --budget full

# The machine-readable rows this report quotes (§2, §3, §4, §5):
cat training/reports/results-impostor-bakeoff.jsonl

# The Goodhart probe under the surrogate meeting path (§6),
# committed 15.14 ES budget on the fixed eval seed set:
uv run python -m training.bakeoff.harness goodhart-surrogate --budget committed

# The committed tests that pin the protocol (eval seed set, entrant firewall,
# option menu, experiment tier, artifact round-trip):
uv run pytest tests/training/test_bakeoff_harness.py tests/training/test_bakeoff_methods.py -q

# The scripted-FSM reference row (§5 footprints; §7 parity numbers):
uv run python -c "
import tempfile, math
from pathlib import Path
from training.bakeoff.harness import DecisionTrace, rollout_candidate, load_eval_seeds
from training.rewards import compute_shaped_reward
from training.rollout import DESCRIPTOR_VECTOR_FIELDS
seeds = load_eval_seeds(); sums = [0.0] * len(DESCRIPTOR_VECTOR_FIELDS)
wins = opps = kills = 0; shaped = []
with tempfile.TemporaryDirectory() as tmp:
    for seed in seeds:
        tr = DecisionTrace()
        r = rollout_candidate(None, seed, output_dir=Path(tmp), trace=tr)
        v = r.descriptors.vector()
        for i in range(len(sums)): sums[i] += float(v[i])
        wins += r.winner == 'IMPOSTORS'; opps += tr.opportunities; kills += tr.kills_taken
        shaped.append(compute_shaped_reward(r, 'IMPOSTOR').total())
n = len(seeds)
print({name: round(sums[i] / n, 3) for i, name in enumerate(DESCRIPTOR_VECTOR_FIELDS)})
print('win_rate', wins / n, 'take_rate', round(kills / opps, 3), 'shaped', round(math.fsum(shaped) / n, 3))
"
```

Determinism caveat (the surrogate-artifact precedent): the ES/QD training loops
and every evaluation are bit-deterministic under their seeds on one platform;
the BC entrant's numpy SGD is deterministic on the recording platform and
ULP-equivalent across CPUs. The committed weights + sha256 sidecars are the
frozen ground truth; `harness.load_candidate_weights` verifies them on reload.

## 9. How downstream consumes this

- **15.18 (the pause)** reads `results-impostor-bakeoff.jsonl` (one row per
  entrant, the full metric tuple) + this report's §7 ranking, reloads the exact
  champion artifacts from `training/artifacts/impostor/<entrant>/` (sha256
  verified) for the real-LLM finalist evaluation, and adjudicates the §6
  Goodhart delta.
- **15.16 (the crew track)** consumes `training/bakeoff/harness.py` + `es.py`
  read-only and reports in the SAME tuple shape.
- **15.17 (the torch probe)** adapts into `BakeoffEntrant` and reports through
  the experiment-tier (determinism-FAIL-tolerant) row path with the N-repeat
  spread.
