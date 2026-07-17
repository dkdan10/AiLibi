# The impostor bake-off — the baseline-5 re-run: same four candidates, flipped floors, re-grounded surrogate

> **Task 17.12** (`tasks/phase-17.md`) — the Phase-15 15.15 recipe re-run
> VERBATIM on the re-recorded corpus: BC/DAgger, utility-scorer+ES, direct
> policy-net+ES, and MAP-Elites, all impostor-side, all trained and evaluated
> through ONE harness, now against the baseline-5 substrate and the flipped
> selection floors so the phase re-selects METHODS on the co-adapted economy,
> not on a stale one. Locked decision 1 (full slate); locked decision 4 (the
> re-grounded surrogate); the 16.11 referee floors via 17.11's constants.
> Anchors: `tasks/phase-15.md` 15.15 (the recipe); `audits/audit-phase-15-pause.md`
> §2.1 + decision 1 (the recorded referee-gated ranking rule this re-run applies);
> `training/reports/report-ballot-surrogate.md` §5 (the 17.10 GO) + §7 (the cap);
> `eval/watchability.py:732-762` (the baseline-5 floor pins).
> Code (out of scope, re-run verbatim): `training/bakeoff/harness.py` (entrant
> protocol + fixed eval protocol + report emitter),
> `training/bakeoff/{bc,utility_es,policy_es,map_elites}.py`, `es.py`.
> **Date:** 2026-07-16 (Phase-15 original: 2026-07-09). **Corpus:**
> `replays/ml_corpus/9p2i` — 150 games re-recorded at baseline 5 by Task 17.9
> (`Qwen/Qwen3.6-27B` on Featherless, `qwen3_6_27b` v3 prompt set, the 16.17
> graduated lever slate, `absence_prior` OFF, `fsm-default` stamp, `$0`), splits
> regenerated in place (the `seed % 5` rule structurally identical). **Substrate:**
> baseline 5. **Committed artifacts:** `training/artifacts/impostor/<entrant>/`
> (`weights.json` float-hex + `weights.json.sha256` + `config.json`); rows in
> `training/reports/results-impostor-bakeoff.jsonl`. **Command:**
> `uv run python -m training.bakeoff.harness run --budget full --entrant all`
> (exit 0, **10 m 57 s** wall-clock, CPU-only, **$0**).

**The finding, stated first because it IS the finding, not an omission.**
Training is deterministic and touches neither `baseline_id` nor the surrogate, so
the re-run reproduced the exact Phase-15 genomes: every entrant's committed
`weights.json`, its sha256 sidecar, and its `config.json` are **byte-identical**
to the Phase-15 tree — `git status` shows no change under
`training/artifacts/impostor/`, the four weights shas are unchanged
(`ddb1e706…`, `6d327dcb…`, `561e5ff3…`, `b4469dec…`), and only
`results-impostor-bakeoff.jsonl` moved (four rows). This re-run is therefore a
**re-VERDICT of the same four candidates** under the flipped selection bar
(baseline-5 floors, 17.11) and the re-grounded surrogate (17.10 GO), not a
re-training. Everything training-side and everything the real (fake-provider)
meeting path produces is unchanged by construction; what moved is the reading:
the referee geomean, the surrogate divergence column, and the floor distances.
The artifact tree being unchanged by content is the correct outcome of a
verbatim re-run on identical training bytes — the phase re-scores those bytes
against the co-adapted economy.

---

## 1. The fixed protocol (stated before any training ran — restated verbatim)

- **One harness.** Every entrant trains through
  `training.bakeoff.harness.rollout_candidate` (the production loop —
  `HeadlessGame` through the candidate's own agent factory) and is scored ONLY
  by `harness.evaluate_candidate`. A committed AST firewall test
  (`tests/training/test_bakeoff_harness.py::test_entrant_modules_do_not_import_eval`)
  proves no entrant module imports `eval.*` — the harness is the only module
  that computes reported metrics.
- **Fixed eval seed set.** The frozen corpus TEST split —
  `replays/ml_corpus/9p2i/splits.json`, the 30 seeds with `seed % 5 == 4`
  (1004 … 1149), regenerated in place by 17.9 at the identical `seed % 5` rule
  — asserted by `test_eval_seeds_are_the_frozen_corpus_test_split`. Training
  draws only TRAIN-split seeds; the BC held-out agreement set draws the VAL split.
- **Training meeting path — the fake provider, unchanged by the GO.** The
  recorded 15.15 protocol trains on the deterministic fake-provider meeting path,
  and this re-run executes that same code path: `surrogate_uses_training = 0` on
  every row. The 15.13 baseline-3 NO-GO is now **superseded by the 17.10 GO** on
  the re-grounded artifact (`report-ballot-surrogate.md` §5: top-1 0.86 ≥ the
  0.615 bar = 0.75 × the 0.82 honest ceiling, > FO-6's 0.22, SKIP-vs-eject
  0.5192 > the always-eject constant 0.4808 — the first GO on any substrate). The
  GO **promotes the surrogate to the training-time-runner tier**, but the 15.15
  recipe this task re-runs verbatim still installs the fake provider as the
  training runner; the surrogate is consumed here as the **eval divergence
  column** (§3), metered within the re-derived staleness cap: `max_uses = 62491`
  (`training/artifacts/surrogate/max-uses.json`, unit meetings, sha-keyed
  `62d6cbfa…`; = 143 × the 437 baseline-5 fit-side meetings — the ~143× rule
  re-derived, not held at 50 000 by habit). One cumulative in-process
  `SurrogateUseCounter` threads through all four entrants (sha-verified against
  the artifact; a mismatch raises); this run metered **403 of 62 491 (0.64%)**.
- **The 17.10 caveat travels WITH the GO (quoted in substance).** The GO is
  earned by the RANKING channel (86.0% top-1 vs FO-6's 22.0%, above even the
  strict-argmax ceiling recipe); the DECISION channel does not — the predictor
  casts SKIP on every test meeting (0 correct ejects; all 50 true ejections
  called SKIP), and its 51.9% decision accuracy is exactly the trivial
  always-SKIP constant, clearing axis 3's always-eject constant (48.1%) only
  because the baseline-5 economy is **skip-majority** (recorded voters SKIP on
  58.4% of ballots; 54 of 104 test meetings resolve SKIP). This is the
  skip-majority baseline-5 economy, and it is the mechanism behind the flat
  divergence column in §3/§7.
- **The shared inner fitness** (every ES/QD entrant, identical): the
  tactically-reachable side-specific impostor terms + potential shaping
  (`training.rewards.compute_shaped_reward(..., "IMPOSTOR").total()`) MINUS an
  anchor-KL penalty toward the frozen FSM, weight 1.0 — measured as the anchor
  cross-entropy (mean per-decision log-loss at the FSM's deterministic choice;
  the piKL-style penalty). A tick-budget-truncated episode scores the documented
  constant −10.0. The validity gate and the referee are SELECTION filters applied
  after training — **never fitness terms**.
- **Pre-stated bars.** BC held-out top-1 intent agreement bar **≥ 0.90**
  (`harness.BC_INTENT_AGREEMENT_BAR`). Anchor-CE ceiling **2.0 nats** mean
  (`harness.ANCHOR_CE_CEILING`, ratified by pause decision 1 as a flag, never a
  drop). Rows above the ceiling are FLAGGED, never dropped.
- **Per-candidate gates, all through the candidate's OWN policy factory:** the
  15.10 determinism harness (`run_policy_determinism`, double-run over seeds
  1004/1009 at 9p2i — a FAIL demotes to experiment-tier and attaches the full
  `PolicyDeterminismReport` + an N-repeat spread, the 15.17 torch seam) and the
  leak-test factory mode (`eval.leak_test.scan_factory_packets`).

---

## 2. The entrants and their budgets

The budgets are the recorded 15.15 budgets, re-run verbatim; only the wall-clocks
are this box's.

| Entrant | Method | Genome | Budget (recorded) | Train wall-clock |
|---|---|---|---|---|
| `bc-dagger` | Behavior-clone `ImpostorPolicy.decide` on encoder-v2 features + DAgger | 1049 (encoder-v2 111 → tanh 8 → 17-slot masked head) | harvest 12 train seeds, 2 DAgger rounds × 6 seeds, 30 epochs, lr 0.2, from-scratch retrain per round | **11.4 s** |
| `utility-es` | Learned linear utility over the FSM's own option menu + (1+λ)-ES | 19 (18 option features + bias) | ES 20 gen × 12 pop × 6 train seeds, σ 0.3 | **285.3 s** |
| `policy-es` | Direct masked policy net (full masked intent space) + (1+λ)-ES, warm-started from the BC clone | 1049 (same family as BC) | ES 14 gen × 10 pop × 6 train seeds, σ 0.15 | **192.0 s** |
| `map-elites` | MAP-Elites over three named 15.8 descriptors, competence as cell quality, warm-started from the BC clone | 1049 (same family) | 120 iterations + 6 inits × 4 train seeds | **93.8 s** |

The crew side stayed the frozen scripted FSM throughout (no co-evolution this
wave; the crew track re-runs measurement-only in 17.13). Eval wall-clocks (each,
the fixed 30-seed protocol scored on both meeting paths): **15.1 / 15.1 / 22.1 /
20.7 s**. Everything ran on CPU at $0; the whole `run --budget full --entrant all`
pass (train + both eval passes, all four) took **10 m 57 s**.

---

## 3. Results — the single metric tuple + FLOOR SENSITIVITY (one row per entrant)

Every number regenerates from `results-impostor-bakeoff.jsonl` (committed) or by
re-running the CLI in §8. "Real" is the fake-provider meeting path; "surrogate"
is the 17.10-GO ballot-predictor path (promoted tier, consumed here as the eval
divergence column). Divergence is data, reported never collapsed.

| Metric | bc-dagger | utility-es | policy-es | map-elites |
|---|---|---|---|---|
| Validity gate | PASS | PASS | PASS | PASS |
| Referee `referee_passed` | False | False | False | False |
| Referee mean / median score | 0.42 / 0.10 | 3.63 / 3.70 | **3.65 / 3.70** | 3.41 / 3.70 |
| Floor-trip rate | 0.00 | 0.00 | 0.00 | 0.00 |
| Inner fitness (real path) | 5.17 | 18.67 | **19.07** | 18.20 |
| Inner fitness (surrogate path) | 5.17 | 18.80 | 19.07 | 18.16 |
| Surrogate − real divergence | 0.00 | +0.13 | 0.00 | −0.03 |
| Mean shaped reward (real) | 7.10 | 19.67 | **21.10** | 20.17 |
| Anchor cross-entropy (ceiling 2.0) | 1.96 | **1.00** | 2.02 ⚠ FLAGGED | 1.97 |
| Impostor win rate (reported, never gated) | 0.07 | **1.00** | **1.00** | 0.93 |
| Take-rate (kills / clean opportunities) | 0.47 (281 opps) | 0.76 (232) | 0.76 (365) | 0.92 (304) |
| Determinism (double-run) | PASS | PASS | PASS | PASS |
| Leak test (own factory) | PASS (381 pkts) | PASS (538) | PASS (541) | PASS (565) |
| Surrogate staleness uses (train / eval) | 0 / 44 | 0 / 103 | 0 / 133 | 0 / 123 |
| Wall-clock train / eval (s) | 11.4 / 15.1 | 285.3 / 15.1 | 192.0 / 22.1 | 93.8 / 20.7 |
| Weights sha256 (prefix) | `ddb1e706ae1a` | `6d327dcbde94` | `561e5ff36478` | `b4469dec6f95` |

**UNCHANGED vs Phase 15** (identical genomes, identical fake-provider real-path
rollouts): every training-side and real-path field — inner fitness (real), mean
shaped reward, impostor win rate, take-rate + opportunities, anchor cross-entropy
and its flag, determinism digests, leak packet counts, descriptor footprints (§5),
genome length, encoder version, weights sha256. **MOVED:** the referee mean/median
and per-game scores (§7 delta a), the surrogate-path fitness + the divergence
column (§7 delta b), and the floor distances (§7 delta c; the floor VALUES moved
with the baseline flip, the measured supply did not). The four eval surrogate-use
counts (44/103/133/123, total 403) are new because the surrogate path is now
run — metered within the cap.

Two divergence rows are **exactly 0.0** (bc-dagger, policy-es): the re-grounded
surrogate resolves their meetings identically to the fake provider. The referee
`referee_passed=False` on every row is the fake-provider **structural** artifact,
not discrimination — fake meetings mint no contradiction flags and no
observation-backed accusations, so the two meeting-driven floors fail identically
(the starved-economy rejection made legible below). The geomean column still
carries the coarse-grain ordering the pause's ranking rule reads (§7).

### 3.1 Floor sensitivity — every candidate against every baseline-5 floor

The designer ruling on selection-bar honesty (`tasks/phase-17.md` §"Designer
rulings", 17.12/17.17): a co-adapted impostor's job is to make convictions
harder — the exact direction the baseline-5 conversion floor prices — so a
starved-economy rejection must be **legible as the instrument working**, never
silent. All four candidates are shown because the finalists are cut FROM this
table (§7). Floors are the baseline-5 9p2i pins (`eval/watchability.py:755-762`).
The raw counts `x/n` regenerate from committed bytes by the §8 driver (the jsonl
persists rates, not counts).

| Entrant | Floor | Measured (raw) | Floor (pin) | Distance | Verdict | Noise / clearance |
|---|---|---|---|---|---|---|
| **bc-dagger** | witnessed_event_rate | 0.1552 (9/58) | 0.03448 (7/203) | +0.1207 | **PASS** | z = **+3.38σ** |
| | flags_per_meeting | 0.0000 (0/44) | 0.50279 (90/179) | −0.5028 | **FAIL** | starved (no flags minted) |
| | testimony_backed_conversion | null (0/0 backed) | 1.0 (derived) | — | **FAIL** | null supply → derived floor 1.0 |
| **utility-es** | witnessed_event_rate | 0.1400 (21/150) | 0.03448 (7/203) | +0.1055 | **PASS** | z = **+3.63σ** |
| | flags_per_meeting | 0.0000 (0/101) | 0.50279 (90/179) | −0.5028 | **FAIL** | starved (no flags minted) |
| | testimony_backed_conversion | null (0/0 backed) | 1.0 (derived) | — | **FAIL** | null supply → derived floor 1.0 |
| **policy-es** | witnessed_event_rate | 0.0667 (10/150) | 0.03448 (7/203) | +0.0322 | **PASS** | z = **+1.40σ** (thin margin) |
| | flags_per_meeting | 0.0000 (0/133) | 0.50279 (90/179) | −0.5028 | **FAIL** | starved (no flags minted) |
| | testimony_backed_conversion | null (0/0 backed) | 1.0 (derived) | — | **FAIL** | null supply → derived floor 1.0 |
| **map-elites** | witnessed_event_rate | 0.0822 (12/146) | 0.03448 (7/203) | +0.0477 | **PASS** | z = **+1.94σ** |
| | flags_per_meeting | 0.0000 (0/123) | 0.50279 (90/179) | −0.5028 | **FAIL** | starved (no flags minted) |
| | testimony_backed_conversion | null (0/0 backed) | 1.0 (derived) | — | **FAIL** | null supply → derived floor 1.0 |

**How each floor reads.**

- **`witnessed_event_rate` — the rare-event floor, read statistically.** Its
  baseline-5 pin is a **7/203 point estimate** (SE ≈ 0.0128 = √(p₀(1−p₀)/203)),
  so a distance alone under-reads it; each cell carries the **two-proportion z**
  against the pinned numerator/denominator: `z = (p₁ − p₀) / √(p̂(1−p̂)(1/n₁ +
  1/n₀))`, `p̂ = (x₁+x₀)/(n₁+n₀)`, floor side `x₀ = 7`, `n₀ = 203`, candidate side
  `x₁` = crew-witnessed kills, `n₁` = total kills over the 30-seed eval set. All
  four candidates PASS, so the z values are positive clearances (a reading aid,
  not a gate change): bc-dagger **+3.38σ**, utility-es **+3.63σ**, map-elites
  **+1.94σ**, policy-es **+1.40σ** — policy-es clears by only ≈1.4σ (its 10/150
  witnessed rate is the thinnest margin of the four, a fact the 50-seed real-path
  eval must re-read; §7). Convention (15.19 rare-event rule, contract §): a
  sub-1σ miss would be labelled **within-noise** and the floor would still gate;
  the noise column and the verdict column sit side by side so the 17.16/17.17
  owner readings can weigh a coin-flip rejection for what it is. **Calibration
  the contract asks be quoted:** the floor's own SE ≈ 0.0128, and the 17.9
  corpus's own 0.0334 witnessed measure sits (0.034483 − 0.0334)/0.0128 ≈ 0.08σ
  below the pin — sampling noise (the designer ruling's ~0.07σ read), quoted so
  a coin-flip rejection near this floor is read as variance, not signal.
- **`flags_per_meeting` — the starved-economy rejection, made legible.** Every
  candidate measures **0.0** (0 flags over 44/101/133/123 meetings) against the
  0.50279 floor (90/179). Fake-provider meetings mint **no contradiction flags**:
  the meeting layer resolves without an LLM, so there is no transcript to
  re-derive flags from and no grounded vent-sighting channel. The FAIL is the
  instrument working — a co-adapted floor rejecting a candidate whose games
  supply structurally less evidence than the baseline.
- **`testimony_backed_conversion` — population-relative, derived to 1.0.** The
  baseline-5 pin is 64/135 = 0.474074, evaluated **population-relative**
  (16.11, `population_relative_conversion=True`): the per-candidate floor is
  `min(1.0, 0.474074 × (0.502793 / measured flags_per_meeting))`. With measured
  flags_per_meeting = 0.0 the ratio diverges and the floor caps at **1.0**;
  measured conversion is **null** (0 observation-backed attempts, 0 converted),
  so the gate FAILs. This is the citation-era design pricing the exact starved
  meeting layer — no flags ⇒ the hardest possible conversion floor ⇒ a null
  supply cannot clear it.

Consequently `supply_floors_passed = False` and `referee_passed = False` for all
four, and `floor_trip_rate = 0.0` on every row (no game trips a floor because no
game supplies the evidence a floor measures). The referee gate does not
DISCRIMINATE among these candidates under fake meetings — its geomean column
does, at the coarse grain the pause's ranking rule reads (§7). All four rows are
`tier="candidate"` (determinism PASS), so no N-repeat spread is attached; the
experiment-tier path is exercised by
`test_evaluate_candidate_experiment_tier` (the 15.17 torch seam).

---

## 4. The BC entrant vs its pre-stated bar — the encoder-sufficiency finding (unchanged)

Same genome, same VAL-split held-out set, so this finding stands byte-for-byte on
the re-run. **Held-out top-1 intent agreement: 0.365 (794 held-out FSM
decisions) vs the 0.90 bar — MISSED decisively.** Per-kind confusion (from the
row's `train_metadata.per_kind_agreement`):

| FSM intent kind | decisions | clone agreement |
|---|---|---|
| kill | 65 | **0.708** |
| vent | 77 | 0.545 |
| move | 479 | 0.415 |
| do_task | 97 | 0.031 |
| wait | 61 | 0.000 |
| sabotage | 15 | 0.000 |

The named gaps are the same three: **`move`** (60% of decisions, 41.5% cloned)
— encoder-v2 carries per-room last-seen occupancy but no "next-hop-toward-X"
representation, so a 1049-parameter tanh MLP re-derives shortest-path routing only
partially at this budget (the clone finds the right ACTION kind — kill agreement
0.71 — not the routing half); **`do_task` / `wait`** (3.1% / 0%) — low-salience
null actions a fixed 17-slot head systematically loses to a move slot (a
candidate-conditioned head is the structural fix, which is exactly the utility
scorer); **`sabotage`** (15 held-out labels of 794, 0%) — pure class imbalance.
The clone still functioned as the ES warm start: `policy-es` seeded from this
genome opened at fitness **6.58** vs a random init's sub-1 starts and reached
**18.96** (`train_metadata.fitness_trace`). The encoder-sufficiency finding is
therefore unchanged by the re-run: the encoder gaps are a property of the
committed genome and the VAL bytes, both of which are identical.

---

## 5. MAP-Elites — archive coverage + descriptor footprints (unchanged)

The archive is over the same three named 15.8 descriptors and the same warm-started
run, so it stands unchanged: **6×4×4 = 96 cells** over (`kill_count`,
`witness_exposure_rate`, `vent_usage`); **coverage 30/96 = 0.3125** after 126
evaluations; champion cell **[5, 0, 3]** (5+ kills, zero witnessed exposure, heavy
venting) at cell quality **18.86**; best-per-cell quality spans **−2.61** (the
0-kill corner) to **18.86**; the vent axis holds 16/5/2/7 filled cells in bins
0–3. Making the vent-exit choice learnable through the room head (PR #242 review)
is what opened that axis.

Descriptor footprints (mean over the 30 eval seeds, from each row's
`descriptor_footprint`), byte-identical to Phase 15 because they are measured on
the same fake-provider real-path rollouts:

| Entrant | kill_count | witness_exposure | vent_usage | meeting_count | do_task_emissions |
|---|---|---|---|---|---|
| bc-dagger | 1.93 | 0.12 | 0.0 | 1.47 | 85.4 |
| utility-es | 5.00 | 0.14 | 4.7 | 3.37 | 72.8 |
| policy-es | 5.00 | 0.07 | 20.3 | 4.43 | 76.9 |
| map-elites (champion) | 4.87 | 0.08 | 22.3 | 4.10 | 74.8 |
| scripted FSM (fake-provider reference, §8) | 4.93 | 0.03 | 7.3 | 3.87 | 81.8 |

The two direct-policy champions (policy-es and the map-elites champion) still
CONVERGE on the same low-exposure heavy-vent region (~20+ vent submissions/game vs
the FSM's 7.3), while utility-es reaches the same kill count at near-FSM vent usage
(4.7) because its bounded menu only offers the vents the FSM ladder would generate.
The archive's value is exactly this map of the monoculture direction the
single-objective optimizers pull toward, plus 29 other filled cells the phase can
inspect. Both the encoder-sufficiency finding (§4) and this archive map stand
**unchanged** on the re-run — they are properties of the frozen genomes and the
baseline-independent fake-provider rollouts.

---

## 6. The Goodhart obligation — DISPOSITION (no re-run here; 17.15 owns it)

No Goodhart probe runs in this task. The 15.15 obligation — run the probe under
the meeting model the bake-off scores on — was **discharged in Phase 15**: the
delta verdict moved **EXPLOITS_FOUND** (the 15.14 fake-provider run: strongest
reachable 16.62, +155%, via the forced `kill` lever's D2-separation "suspicion
theater") → **HELD** under the surrogate path, and the Phase-15 report recorded
that the HELD was **for a disqualifying structural reason** (an over-ejecting,
evidence-free surrogate that fail-closes the validity gate), never read as
exploit-caught.

The Phase-17 probe re-run **on the re-grounded surrogate** is Task **17.15's**
deliverable (`training/reports/report-goodhart-probe.md` + its test re-pins), not
this report's. What this report records as the bar 17.15 runs against is the
17.11-re-measured fake-provider baseline for the flipped economy, pinned in
`training/bakeoff/harness.py:174-181` as `GOODHART_9P2I_BASELINE`:

| constant | value |
|---|---|
| `baseline_mean_score` | **3.28** |
| `champion_mean_score` | **3.7** |
| `relative_gain` | **0.1298** |
| `strongest_reachable_score` | **3.7** (tactic `report`) |
| `verdict` | **HELD** |

These are the post-hardening fake-provider ceiling constants (the ES champion and
the forced-`report` lever tie at 3.7 — the same D1×D4 lattice §7 explains), the
bar 17.15's surrogate-path re-run reports its delta against. Note the Phase-15
report's "cap 50,000" is **superseded by 62,491** (the re-derived staleness cap,
§1).

---

## 7. Ranked recommendation + FINALIST SELECTION — FOR THE PAUSE→17.14

The ranking applies the **recorded** referee-gated rule the Phase-15 pause
consumed and ratified (`audits/audit-phase-15-pause.md` decision 1; the Phase-15
§7 rule): the referee is a **GATE at coarse grain only** (its geomean as a score,
never the fine D2-conversion differences the un-hardened instrument could not
support), and candidates are ranked on the tuple {gate-cleanliness, real-path
fitness, anchor-CE + ceiling flag, win/take shape, robustness to the meeting-model
swap}. The top-2 are the finalists the real-LLM eval consumes.

**Ranking (ordinally UNCHANGED vs Phase 15):**

1. **`utility-es`** — within ~2% of the best inner fitness (18.67 vs 19.07),
   tied-best win rate (1.00), the LOWEST anchor cross-entropy (1.00 — the most
   FSM-legible champion, unflagged), a 19-weight interpretable genome, and a
   structural no-off-menu guarantee (the menu is the FSM's own option ladder,
   pinned by test; off-menu behavior is unreachable). Its ceiling is that menu.
2. **`policy-es`** — best real-path fitness (19.07) and the only entrant to edge
   the scripted FSM on raw shaped reward through this protocol (21.10 vs 20.33).
   But it is the one anchor-CE-FLAGGED row (2.02 > 2.0, marginal), shows the vent
   tell (20.3 vent submissions/game vs the FSM's 7.3 — a channel fake meetings
   never punish), and its witnessed-rate margin is the thinnest of the four
   (+1.40σ, §3.1). Treat its real-path numbers as upper bounds pending 17.14.
3. **`map-elites`** — the diversity instrument (30/96 cells), champion 18.20 (0.9
   behind the best), converging on policy-es's low-exposure heavy-vent region
   (the monoculture direction is itself the finding).
4. **`bc-dagger`** — a warm start and a measurement, not a candidate (0.365 vs
   the 0.90 bar; §4).

**FINALISTS: `utility-es` and `policy-es`** (top-2, the recorded cut). Task
**17.14** (the multi-finalist recorder + real-LLM eval) consumes these two named
finalists and their committed artifacts.

### 7.1 The Phase-15 → Phase-17 ranking delta — findings to explain, one per mover

The ordinal ranking held, but three channels moved under the baseline-5 economy.
These are findings the co-adapted substrate produced, not anomalies to smooth.

**(a) The referee-geomean channel COLLAPSED — and no longer discriminates under
fake meetings at all.** utility-es fell **14.62 → 3.63** mean; the Phase-15
13.1–17.6-scoring game cluster is gone; every entrant now sits on the same D1×D4
lattice **{3.7, 3.2, 0.3, 0.1}** (3.7 = D1 .6 × D4 .20; 3.2 = D1 .6 × D4 .10;
0.3 = D1 ε × D4 .20; 0.1 = everything dead). The new means are so compressed that
**policy-es 3.65 now nominally edges utility-es 3.63** — a 0.02 gap on identical
3.7 medians, far inside seed noise; the geomean channel no longer discriminates
these candidates. The verified mover (`git log --follow eval/watchability.py`):
**Task 15.19's conversion-coupled D2 separation gate** (commit `ee3948a`,
`eval/watchability.py:1667-1672`), which landed **2026-07-10 — one day after the
Phase-15 bake-off report**. Pre-15.19, `_d2_crew_deduction` returned
`separation_norm` unconditionally, so under fake-provider meetings that never
eject, aggressive impostor play inflated rendered suspicion toward the killer
without any conviction — "suspicion theater" — and the old instrument credited
D2 ≈ 0.5 with zero conversions, lifting the geomean to ~17.6. Post-15.19, with
zero backed conversions and no contradiction/vent flag, `separation_norm` floors
to 0, D2 collapses to ε inside the weighted geomean, and the score caps at ≈3.7.
The replay bytes are identical (same weights sha AND identical
`witnessed_event_rate` per entrant, both measured by the referee's own
`_reconstruct_kills` walk over the bytes — if any meeting artifact had changed,
witnessed rate and fitness would differ); only the instrument reading them
hardened. The delta old→new is the single D2 term 0.5→ε:
`exp(0.25·(ln 0.5 − ln 1e-3)) = 4.73×`, vs the observed 17.6/3.7 = **4.76×**
(rounding); D1/D3/D4/floor byte-identical. `harness.py:174-181` already documents
the post-hardening ceiling: fake games cap at 3.7 with the D4 contest term the
only reachable lever (§6).

**(b) The surrogate divergence column went FLAT — and stops providing an
independent early warning this phase.** The Phase-15 divergences (−2.1 … −11.8 on
every row) collapsed to **−0.03 … +0.13, with two rows exactly 0.0** (bc-dagger,
policy-es: identical trajectories). The re-grounded predictor is trained on the
skip-majority (58.4% SKIP) baseline-5 economy and its decision channel casts SKIP
on every meeting (0/50 true ejections called — `report-ballot-surrogate.md` §5);
a SKIP-everything surrogate resolves meetings like the fake provider (which never
ejects), so the two meeting paths now produce near-identical rollouts. The
Phase-15 bracket — fake 0% ejections vs the OLD baseline-3 surrogate's 92%
ejections — has **collapsed onto one side**. In Phase 15 the surrogate's
one-signed divergence was the correct early warning (it predicted policy-es's
real-path collapse); this phase the column is flat and provides no such
independent signal, so the only discriminating meeting model left is the
**real-LLM path (17.14)**. This is the 17.10 decision-channel caveat traveling
with the GO, exactly as the promotion recorded.

**(c) The floors FLIPPED under the citation-era economy — the distances moved,
the fake-path verdicts did not.** The baseline itself supplies less evidence now
(convictions demand citations), so the meeting-driven floors eased and the rare
floor rose: `flags_per_meeting` **1.863 → 0.503** (baseline-3 259/139 →
baseline-5 90/179), the `testimony_backed_conversion` pin **0.664 → 0.474**
(71/107 → 64/135; the evaluated floor is now the population-relative derived
**1.0** at zero flags, where baseline-3 evaluated it flat at 0.6068),
`witnessed_event_rate` **0.0325 → 0.0345** (5/154 → 7/203). Yet fake meetings
still mint zero flags and zero conversions, so the two meeting-driven floors FAIL
identically and witnessed still PASSES for all four (§3.1). The flip changes the
measured DISTANCES — witnessed clearances tightened as the floor rose, the flags
FAIL is now against 0.503 rather than 1.863 — not the fake-path verdicts.

### 7.2 Open risks for the pause → 17.14 / 17.16 consumers

- **The referee discriminates only on evidence-supplying meeting paths.** Under
  fake meetings every candidate fails the same two supply floors and the geomean
  no longer separates the top two (0.02 apart). The gate becomes meaningful only
  on the real-LLM path (17.14); a selection that gated on `referee_passed` or on
  fine geomean differences under fake meetings would select on noise.
- **The surrogate divergence column is no early warning this phase** (delta b):
  flat by construction of the skip-majority predictor. 17.14's real-meeting eval
  is the only remaining discriminating meeting model — the finalist ranking is
  meeting-model-conditional until it re-scores.
- **Take-rates (0.76–0.92) for the ES/QD champions** are unchanged and sit well
  above the FSM's ~0.55; a high-take impostor is the shape the watchability
  floors exist to catch, so re-check under 17.14's real-meeting referee, where
  the crew can actually convict.
- **The anchor-CE flag on policy-es stands** (2.02 > the ratified 2.0 ceiling,
  marginal). In Phase 15 the one anchor-CE-flagged candidate was the one that
  collapsed on the real path; the flag travels to 17.14 as a live caution.
- **policy-es's witnessed clearance is thin** (+1.40σ, the tightest of the four;
  §3.1) — a margin the 50-seed real-path eval must re-read, not a rejection.
- **Within-kind target ties in the direct-policy family** remain lexical (PR #242
  review): every submission-legal intent is reachable but the policy cannot
  express a preference inside a tie, and the FSM anchor gives no supervision
  there. Widen the head (per-roster-slot kill preferences) before any 17.16
  productization scales the direct-policy path.

---

## Provenance — the 15.9 stamp, per entrant (persisted with the artifacts)

The five 15.9 stamp fields are **persisted machine-readably** beside each
entrant's weights: `training/artifacts/impostor/<entrant>/stamp.json` carries
exactly `{policy_id, method, encoder_version, weights_sha256, anchor_policy}` —
the committed source Task 17.14's multi-finalist recorder stamps games from
("stamp fields come from the candidate's own config, never from the committed
champion's constants"). The table below mirrors those files. Every value closes
against committed bytes: `policy_id` = the entrant id, `encoder_version` /
`weights_sha256` equal the jsonl row's fields and the sha256 sidecar,
`anchor_policy = "fsm-default"` (the frozen FSM anchor all four entrants
regularize toward). The `method` strings are the productized single-line tokens;
utility-es carries the SAME token as the shipped champion's production stamp
(`agents/tactical/learned/factory.py::CHAMPION_METHOD = "utility-scorer-es"`),
so one policy never wears two stamps — the 17.14 conflation guard. The stamp
files are pinned by `test_rerun_artifacts_carry_the_15_9_provenance_stamp`
(stamp sha == row sha == sidecar sha, and the utility-es stamp == the champion
constants), so a future regeneration that moves the weights without refreshing
the stamps trips loudly. The harness itself writes only the
weights/sidecar/config triplet (out of scope; the jsonl row schema is frozen,
`extra="forbid"`). The artifact tree is the Phase-15 tree **re-verified** —
every sha256 is unchanged.

| policy_id | method (stamp token — family) | encoder_version | anchor_policy | weights sha256 (full 64-hex) |
|---|---|---|---|---|
| bc-dagger | `bc-dagger` — behavior-cloning + DAgger | v2 | fsm-default | `ddb1e706ae1a827e68b359f1bd4d491e77d1761f6d8ccf66571987b06d784d94` |
| utility-es | `utility-scorer-es` — learned utility scorer + (1+λ)-ES | impostor-option-features-v1 | fsm-default | `6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0` |
| policy-es | `policy-net-es` — masked policy net + (1+λ)-ES | v2 | fsm-default | `561e5ff36478dacf4806782e57f3411fc8a6c38a5a52f22bb85b3abd1e86ca89` |
| map-elites | `map-elites` — quality-diversity / MAP-Elites | v2 | fsm-default | `b4469dec6f95def6ba53b9ca37b81b4285b02501374047f290c6a579de0f84bb` |

---

## 8. Reproduce

Every quoted number is a pure function of the committed bytes (weights, corpus,
splits) and these commands; nothing was hand-computed.

```bash
# The full re-run: trains all four entrants at the recorded budgets, re-evaluates
# them through the fixed protocol on both meeting paths, rewrites the jsonl.
# Training is deterministic -> the artifacts round-trip byte-identical.
uv run python -m training.bakeoff.harness run --budget full --entrant all

# The machine-readable rows this report quotes (§2, §3, §4, §5):
cat training/reports/results-impostor-bakeoff.jsonl

# The committed tests that pin the protocol (eval seed set, baseline-5 floor +
# goodhart-default pin, entrant firewall, full/experiment tiers, artifact round
# trip, the Goodhart surrogate re-run seam, the warm-start closure):
uv run pytest tests/training/test_bakeoff_harness.py tests/training/test_bakeoff_methods.py -q
```

**The scripted-FSM fake-provider reference row (§5 footprints).** Baseline-independent
(the FSM rollout does not read `baseline_id`; only the referee floor lookup does),
so it is carried from Phase 15 and regenerated here:

```bash
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

**The floor-sensitivity derivation (§3.1) — so every quoted `x/n` and z
regenerates.** Reload each committed artifact, replay the real (fake-provider)
eval pass on the fixed seeds into a temp dir, then read the raw gauge counts off
the same `_supply_gauge_values` seam the harness uses and compute the
two-proportion z (`x₀=7, n₀=203`):

```bash
uv run python -c "
import math, tempfile
from pathlib import Path
from engine.world import load_canonical_map
from training.bakeoff.harness import (
    BakeoffProtocolConfig, load_candidate_weights, load_eval_seeds,
    _score_eval_pass, _write_roster_json, _drop_audit_sidecars,
)
from training.bakeoff import utility_es, policy_es
from eval.validity import assemble_tournament_report, roles_by_seed
from eval.watchability import _reconstruct_kills, _game_facts, _supply_gauge_values

game_map = load_canonical_map()
seeds = load_eval_seeds()                         # the 30-seed frozen test split
protocol = BakeoffProtocolConfig(eval_seeds=seeds, surrogate_artifact_dir=None)
x0, n0 = 7, 203; p0 = x0 / n0                     # the baseline-5 witnessed pin

def rebuild(entrant, weights):
    if entrant == 'utility-es':
        return utility_es.build_utility_scorer_policy(weights, game_map=game_map)
    return policy_es.build_masked_mlp_policy(weights, game_map=game_map, hidden=8)

for entrant in ('bc-dagger', 'utility-es', 'policy-es', 'map-elites'):
    weights = load_candidate_weights(Path(f'training/artifacts/impostor/{entrant}'))
    policy = rebuild(entrant, weights)
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        _score_eval_pass(policy, protocol=protocol, game_map=game_map,
                         output_dir=d, meeting_runner_factory=None)   # the REAL pass
        _write_roster_json(d, num_players=9, num_impostors=2, tasks_per_crewmate=2)
        _drop_audit_sidecars(d)
        report = assemble_tournament_report(d)
        recon = _reconstruct_kills(d)
        roles = roles_by_seed(d, num_players=9, num_impostors=2,
                              tasks_per_crewmate=2, game_map=game_map)
        by_seed = {}
        for k in recon.kills: by_seed.setdefault(k.seed, []).append(k)
        facts = [_game_facts(g, roles[g.seed],
                             [k.victim_role for k in by_seed.get(g.seed, [])],
                             integrity_ok=recon.integrity_ok) for g in report.games]
        gauges = _supply_gauge_values(report, recon.kills, facts)
    x1, n1 = gauges.crew_witnessed_kills, gauges.total_kills
    p1 = x1 / n1; ph = (x1 + x0) / (n1 + n0)
    z = (p1 - p0) / math.sqrt(ph * (1 - ph) * (1 / n1 + 1 / n0))
    print(entrant, f'witnessed {x1}/{n1}={p1:.4f} z={z:+.3f}',
          f'flags {gauges.total_flags}/{gauges.meetings_total}',
          f'backed {gauges.backed_conversion_converted}/{gauges.backed_conversion_attempted}')
"
```

Determinism caveat: the ES/QD training loops and every evaluation are
bit-deterministic under their seeds on one platform; the BC entrant's numpy SGD is
deterministic on the recording platform and ULP-equivalent across CPUs. The
committed weights + sha256 sidecars are the frozen ground truth;
`harness.load_candidate_weights` verifies them on reload (a corrupted
`weights.json` fails loud). The surrogate use-counter is sha-keyed against
`max-uses.json` and refuses to meter a different artifact.

---

## 9. How downstream consumes this

- **Task 17.14 (the multi-finalist recorder + real-LLM eval)** consumes the two
  named finalists — **`utility-es` and `policy-es`** — and reloads their exact
  committed artifacts from `training/artifacts/impostor/<entrant>/` (sha256
  verified) for the real-LLM finalist evaluation, the only meeting model left that
  discriminates them (§7). Each finalist dir carries its five-field 15.9
  `stamp.json` (the Provenance section) — the recorder's committed stamp source,
  so finalist recordings stamp from the candidate's own artifact, never from the
  champion's constants. It carries forward the open risks: the anchor-CE flag
  on policy-es, the thin +1.40σ witnessed margin, the take-rate shape.
- **Task 17.15 (the Goodhart re-run)** runs the probe under the re-grounded
  surrogate meeting path and reports its delta against this report's §6 bar
  (`GOODHART_9P2I_BASELINE`: baseline 3.28, champion 3.7, HELD), plus the
  surrogate's own SKIP/eject rate (it under-ejects — 0 of 50 held-out ejection
  meetings recognized), and re-pins its own tests.
- **Tasks 17.16 / 17.17 (the owner readings)** consume the §3.1 verdict and noise
  columns **side by side** — the witnessed z clearances (and the within-noise
  convention for any sub-1σ miss), the starved-economy flags/conversion FAILs read
  as the instrument working, and the floor-sensitivity distances beside the ranking
  — so a starved-economy rejection is legible, never silent (the selection-bar
  honesty ruling, `tasks/phase-17.md` §"Designer rulings").
