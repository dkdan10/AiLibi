# The ballot-predictor surrogate — the GO/NO-GO verdict, the fallback ladder, the staleness doctrine

> Task 15.13 built this surrogate and this report; Task 17.10 (`tasks/phase-17.md`)
> RE-GROUNDS both on the baseline-5 corpus and re-states the verdict on the same
> owner-ratified bar (locked decision 4: re-fit + re-verdict on the recorded bar,
> the 6-feature live-parity fence kept). Anchored to
> `audits/post-phase-14-ML-training-signal.md` §5.3 (predict ballots, feed the real
> tally), §5.5 (the four-channel fidelity protocol + the honest ceiling), §5.6 (the
> re-grounding / model-exploitation doctrine). Code:
> `training/surrogate/ballots.py` (the predictor + training entry),
> `training/surrogate/runner.py` (the `MeetingRunner` implementation),
> `training/surrogate/fidelity.py` (the GO/NO-GO region — 15.11 owns the metrics
> core), `training/surrogate/dataset.py` (the table + the 17.10 re-validation
> instrument), `eval/balance_eval.py:241` (the additive `meeting_runner_factory`
> keyword). This report sits beside the 15.11 harness report
> (`report-meeting-table.md`) — the table is the substrate every number below is
> measured on.
>
> **Date:** 2026-07-16 (baseline-3 original: 2026-07-09).
> **Corpus:** `replays/ml_corpus/9p2i` — 150 games, re-recorded at **baseline 5**
> (Task 17.9: `Qwen/Qwen3.6-27B` on Featherless, `qwen3_6_27b` v3 prompt set, the
> 16.17 graduated lever slate, 15.9 `fsm-default` stamp, `$0`), committed
> `splits.json` **seed mod 5: {0,1,2}=train, {3}=val, {4}=test** → **fit side 120
> games / held-out test 30 games**.
> **Committed artifact:** `training/artifacts/surrogate/ballot-predictor.json`,
> sha256 `62d6cbfa3173bf9d56ccce7646c0722fd4e341e11c1ef2a6d2208b74c1408d28`,
> staleness cap **62491 meetings** (`max-uses.json`, = 143 × the 437 fit-side
> meetings — the ~143× rule re-derived, §7).
>
> Reproduce every figure with the one-liners in §9 — each is a pure function of the
> committed bytes and writes nothing.

The 15.11 harness measured the honest ceiling and re-baselined FO-6; 15.13 built the
surrogate inside that ceiling, stated the bar **before** training, and reported a
baseline-3 **NO-GO**. Task 17.9 re-recorded the corpus at the final baseline-5
meeting layer, so every anchor below is **re-measured on the new bytes — never
copied** (honest ceiling 0.6849 → 0.8200; FO-6 top-1 0.1781 → 0.2200; the
always-eject constant 0.8022 → 0.4808). On the re-measured bar the verdict is
**GO** — all three axes pass on the held-out test split (§5) — with the honest
diagnosis stated beside it: the decision channel passes because the baseline-5
meeting economy flipped to skip-majority, not because the surrogate learned to
discriminate SKIP from eject (§5).

---

## 1. The pre-stated GO/NO-GO bar (OWNER-RATIFIED 2026-07-09, mid-wave review Q1)

The bar was stated **before** the original surrogate was trained, committed in code
as `training.surrogate.fidelity.GO_TOP1_CEILING_RATIO` (= 0.75) + `decide_go_no_go`,
and is UNCHANGED by this re-ground (locked decision 4 re-measures the same bar,
honestly). It is **population-relative on all three axes, with no absolute
constants** — because every absolute number in this project's history moved when the
population changed (FO-6 top-1 64% → 26%; the honest ceiling 65.1% → 70.6% → 82.0%;
the always-eject constant 80.2% → 48.1%), an absolute threshold is a trap. Each axis
is measured by the 15.11 harness **on the same scored held-out population** as the
surrogate's own numbers:

> **GO ⇔** held-out top-1 **≥ 0.75 × the honest ceiling measured on the same scored
> population** by the 15.11 harness **AND** held-out top-1 **>** the
> corpus-re-baselined FO-6 logistic **AND** SKIP-vs-eject accuracy **>** the scored
> population's own `always_eject_baseline` (on this corpus test split that trivial
> constant is **0.4808** — the baseline-3 80.2% does not transfer, exactly as the
> ratified wording predicted).

Pre-committed **in the same breath**: **NO-GO ⇒ fallback (a)** — the fake-provider
MeetingManager stays the bake-off's training-time runner and the surrogate ships as
a **DIAGNOSTIC only**. GO ⇒ the surrogate is the bake-off's **training-time
runner** (`training_time_runner="surrogate"`, `surrogate_role="training-time-runner"`
— the machine-readable mapping `decide_go_no_go` encodes, consumed by the bake-off,
never a prose reading). Either way: final champion numbers are **never
surrogate-scored**, and the staleness cap (§7) ships regardless of the verdict.

---

## 2. The model + the live-parity feature decision

The predictor (`training.surrogate.ballots.BallotPredictor`) is a **standardized
conditional logit**: one shared weight vector over per-(voter, candidate) features
plus a **learned SKIP alternative** over per-voter aggregates, softmax over
`candidates + [SKIP]`, fit by full-batch gradient descent (zeros init, no RNG, 300
epochs, lr 0.3 — the `Fo6Logistic` deterministic recipe). The ballot **confidence**
is a ridge-solved linear head on the chosen target's standardized features, clipped
to [0, 1]. Weights serialize as **float-hex JSON** (lossless float64, the
`agents/tactical/features.py::weights_to_hex_json` convention) with a **sha256
sidecar**. Serialization is byte-stable (load → re-serialize is the identity),
and a refit is byte-identical **on the recording platform**; across CPUs a refit
agrees only to float ULP (numpy's SIMD summation grouping varies by machine), so
the **committed bytes are the frozen ground truth** the sha pins and the bake-off
reloads — the round-trip test asserts refit parameter-equivalence plus
frozen-weights reproduction of every reported number.

| Head | Features |
|---|---|
| Per-candidate choice utility | `belief_suspicion`, `belief_trust`, `is_reporter`, `witnessed_vent`, `meeting_index`, `alive_count` |
| Learned SKIP alternative | `max_belief_suspicion`, `meeting_index`, `alive_count` |
| Confidence head (ridge) | the chosen target's six standardized candidate features + bias |

**The live-parity feature decision (the load-bearing design call — KEPT by locked
decision 4).** The six per-candidate columns are *exactly* the subset a
`SurrogateMeetingRunner` can derive **identically at `run_meeting` time** from the
`MeetingRunner` protocol's trigger-time inputs (`trigger`, `state`, `agents`):
`belief_suspicion` / `belief_trust` off the agent's own
`suspicion_graph_for_meeting()`, `witnessed_vent` off its typed
`vent_witness_records_for_meeting()` channel, `is_reporter` from
`trigger.triggered_by`, `meeting_index` / `alive_count` from the orchestrator id and
the living roster. The columns a live runner **cannot** reconstruct are excluded **by
design, not oversight**: the contradiction-flag structure and `contradiction_lift`
need **this meeting's transcript** (a training-time surrogate has no LLM, hence no
transcript — the same structural blindness the honest ceiling measures), and the
physical window stats (`witnessed` / `isolation` / `seen_at_kill` / `body_proximity`
/ `task_submissions` / `move_count`) need the inter-meeting **event history** the
runner never sees. Baseline-5 channels a training-time runner cannot reconstruct
(whereabouts turns, observation citations, roll-call structure) **stay out on the
same grounds**. Training on features that would be identically zero (or
unobtainable) live would **inflate the offline fidelity number the GO/NO-GO verdict
reads while the deployed runner behaves worse** — exactly the "weaken a mitigation to
make the verdict look better" failure the task contract forbids.

The predicted ballots feed the **REAL** deterministic
`meetings.voting.tally_ballots` at the **explicit**
`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD` (0.60) — plurality +
SKIP-first-class + tie→SKIP + a confidence gate on the leader's ballot. The tally is
consumed **pure, never reimplemented** anywhere in `training/`; SKIP-vs-eject emerges
from the real tally, never from a tuned binary head (this is what eliminated FO-6's
always-SKIP collapse by construction, §5.2/§5.3). One ballot per living voter is
exactly the roster the cross-meeting belief fold reads off `result.ballots`.

**The §7.12 teammate-ballot firewall is preserved.** The real vote path coerces a
ballot naming a fellow impostor to SKIP before the tally
(`meetings.manager.coerce_teammate_ballot_to_skip`), so an impostor never supplies
the betrayal vote that ejects a teammate. The runner mirrors it as candidate-set
**exclusion**: an impostor voter's living teammates never enter its choice set —
which can never create a betrayal ballot and matches the fit distribution (the
recorded corpus ballots carry no teammate targets because production's guard ran
before recording).

### 2.1 The baseline-5 re-validation (Task 17.10 — measured, never assumed)

Three load-bearing validations ran on the new bytes **before the fit was trusted**
(the 16.10 walk precedent), via `training.surrogate.dataset.
measure_belief_render_parity` — the end-to-end cross-check of the table's
hand-mirrored belief fold against the **production fold** (`eval.funnel`'s
memory-augmented walk: real `TacticalAgent`s fed reconstructed packets, read through
the exact `suspicion_graph_for_meeting()` accessor a live meeting consumes):

| Gauge | 9p2i | 4p1i |
|---|---:|---:|
| non-self (meeting, voter, candidate) cells compared | 16 198 | 240 |
| **fold fidelity** — raw `belief_suspicion` vs the production raw scalar | **0 mismatches** | **0 mismatches** |
| **fold fidelity** — `belief_trust` vs production trust | 0 mismatches | 0 mismatches |
| **J1 live-parity divergence** — cells where the CLAMPED live render ≠ the raw column | **280 (1.73%)** | 0 |
| — rows carrying ≥ 1 divergent cell | 254 of 3131 (8.1%) | 0 |
| — divergent cells on the fit side (train ∪ val) / the test side | 251 / 29 | 0 / 0 |
| — max abs divergence | 0.11 | 0.0 |

1. **The dataset walk re-validates on the new bytes.** The 17.9 corpus carries
   whereabouts turns, observation-cited ballots, and marker-prefixed rationales;
   both sets reconstruct with every per-tick `state_hash` and per-meeting
   `state_hash_before`/`state_hash_after` verified, 100% ballot join, and the
   hand-mirrored perception→belief pins (`_WindowStats`) **exactly reproduce the
   production fold** — 0 raw mismatches over 16 438 cells across both sets. The
   integration risk (silent `belief_suspicion` corruption) is discharged by
   measurement.

2. **The J1 live-parity divergence is measured and recorded.** The graduated
   Task-16.4 hard-evidence gate (unconditional since the 16.17 baseline-5 record)
   clamps an entirely-soft conviction-grade row to 0.59 at the two belief-render
   read-sites — including `suspicion_graph_for_meeting()`, the exact channel the
   live `SurrogateMeetingRunner` reads. The table's `belief_suspicion` column is
   the RAW stored scalar, so raw-vs-served diverges on exactly the clamped cells:
   **280 of 16 198 cells (1.73%), 254 of 3131 rows, max 0.11** (a soft-only row at
   raw 0.70 renders 0.59 live). **The fit reads the RAW column**, for three stated
   reasons: (a) production doctrine — every non-render consumer reads the raw
   stored scalar, and the table's belief columns also feed the fidelity
   instruments (`public_suspicion`, `recon_suspicion`, the ceiling's belief-lead),
   which are defined on the true belief graph; (b) the divergence is measured and
   bounded (1.73% of cells, ≤ 0.11); (c) the live runner IS served the clamped
   value, so the promoted runner carries a **known, conservative** train/serve
   skew on those cells — live suspicion never exceeds the fit-time value, which
   pushes marginal meetings toward SKIP, the direction the decision head already
   sits at (§5). Moving the fit onto the render channel would change the
   instrument semantics mid-re-ground and is a substrate decision for a future
   contract, not a silent side effect here.

3. **Coerced-SKIP rows are excluded from the fit and counted.** A J2
   citation-gate coerced ballot records `target="SKIP"` with
   `meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER` prefixed to its
   `rationale_text` — a **forced eject, not a chosen skip** (designer ruling,
   `tasks/phase-17.md`), poison for the decision channel. The table now carries
   `ballot_coerced_skip` per row (the anchored repr-aware marker parse, the
   `api.replay_loader._marker_pattern` convention) and **both fit paths drop
   flagged rows**; the fidelity replay scores recorded bytes unfiltered. On this
   corpus the count is **0 of 3131 (9p2i) and 0 of 120 (4p1i) — 0 fit-side rows
   dropped** — so the exclusion is a fence proven by fixture, not a number mover.
   (The other rationale markers present on the corpus are *not* in the exclusion:
   5 teammate-coerced SKIPs — the §7.12 by-design skip the runner mirrors by
   candidate exclusion — 24+1 under-gate redirects, and 3 parse-defaults; only the
   J2 coercion marker records a vote the voter never chose as a skip.)

---

## 3. Held-out fidelity vs the ceiling (the four channels together)

Scored population: the **9p2i corpus test split** — 30 games / **104 meetings** /
**50 ejections** / **54 skips**. The baseline-5 meeting economy is
**skip-majority** (convictions demand citations; recorded voters cast SKIP on 58.4%
of all ballots vs ~5% on baseline 3) — the single biggest substrate shift under
every number below. Every channel (ranking, decision, calibration, the ceiling) is
measured on **this one distribution**, so they describe the same games.

**Surrogate `ballot-surrogate.v1`:**

| Channel | Value |
|---|---|
| top-1 (ejected target ranked first) | **86.0%** (43/50) |
| top-2 | **98.0%** (49/50) |
| SKIP-vs-eject decision accuracy | **51.9%** (54/104) |
| — correct ejects / correct skips | **0** correct ejects · 54 correct skips |
| always-eject baseline (population constant) | **48.1%** (50/104) |
| decision census (predicted) | **0 ejections · 104 skips** |
| `degenerates_to_skip` | **False** (the flag requires accuracy ≤ always-eject; see §5 for the honest reading) |
| ejection-confidence Brier / ECE | 0.0540 / 0.0692 |

**The honest ceiling on the SAME population** (a measurement, not a target):

| Ceiling channel | Value |
|---|---|
| max achievable top-1 (strict-argmax recipe) | **82.0%** (reachable 41/50) |
| flag on target | 44/50 |
| proximity/eyewitness on target | 43/50 |
| strict belief-lead on target | 38/50 |
| voice-driven share (the complement) | **18.0%** |

The surrogate's top-1 (86.0%) sits **above** the measured 82.0% ceiling headline.
State it honestly rather than quietly: the ceiling is the strict-argmax share of one
best-case reconstruction recipe (prior + capped rendered lift), while the learned
ranker also rides `is_reporter` / `belief_trust` / game-phase scalars — so it can
top-1 an ejection whose target was not the recipe's strict argmax (4 of its 43 hits
are exactly that; it also misses 2 of the 41 recipe-reachable ones). The ceiling
remains the honest measure of the **voice-driven share** (18.0% of ejections formed
from the current meeting's spoken narrative — down from 31.5% on baseline 3:
citations moved conviction evidence into channels a surrogate CAN see), not a hard
information bound on the learned ranker; axis 1 of the bar reads it as its
denominator exactly as ratified.

**FO-6 re-baseline on the SAME population** (`fo6_rebaseline`, the floor to beat):

| FO-6 channel | Value |
|---|---|
| top-1 | **22.0%** (11/50) |
| top-2 | 48.0% |
| SKIP-vs-eject decision accuracy | 51.9% |
| decision census (predicted) | 0 ejections · 104 skips (all 50 true ejections called SKIP) |
| `degenerates_to_skip` | **False** — the behavioral all-SKIP collapse is unchanged, but on a skip-majority mix the all-skip head now scores above always-eject, so the eject-era flag reads False by its own formula |

**Recorded-ballot reference calibration (the WOLF channel, model-INDEPENDENT).** Over
the scored split's **257** non-SKIP recorded ballots, each real voter's stated
confidence vs whether its named target was ejected: **ballot Brier 0.1297 / ballot
ECE 0.1063**. This is a property of the committed ballots — it is *not* the
surrogate's calibration (§4), and the harness reports it for every model as the
ground-truth reference (arXiv:2512.09187 WOLF ~0.26–0.29).

---

## 4. The surrogate's PREDICTED-ballot calibration (its OWN channel)

Distinct by construction from the recorded reference in §3. Fitting
`BallotSurrogateModel` on the non-test views and scoring the predicted **non-SKIP**
ballot confidences on the test views against whether the predicted target was
actually ejected:

| Predicted-ballot calibration | Value |
|---|---|
| Brier | **0.2775** |
| ECE | **0.2591** |
| predicted ballots (non-SKIP) | 84 |
| predicted SKIP ballots | 518 |

**State it plainly:** the harness's committed `ballot_brier` (0.1297) / `ballot_ece`
(0.1063) are the **model-independent RECORDED-ballot reference**; the numbers in
this section are the **surrogate's own predicted-confidence calibration** and are
**markedly worse**. The per-ballot behavior inverted against baseline 3: the
predictor now casts SKIP on 86% of individual ballots (518 of 602; the recorded
test-split voters: 57.3%), and
its 84 non-SKIP ballots are spread too thin for any plurality to clear the 0.60
tally gate — which is why the meeting-level decision census in §3 is all-SKIP. The
baseline-3 failure (over-confident argmax convergence, 0 predicted skips) did not
recur; its mirror image did.

---

## 5. THE VERDICT: GO

`decide_go_no_go(surrogate, fo6)` on the shared 104-meeting / 50-ejection
population:

| # | Axis | Surrogate | Bar | Result |
|---|---|---:|---:|:---:|
| 1 | top-1 ≥ 0.75 × ceiling | 0.8600 | 0.6150 (= 0.75 × 0.8200) | **PASS** |
| 2 | top-1 > FO-6 re-baseline | 0.8600 | 0.2200 | **PASS** |
| 3 | SKIP-vs-eject > always-eject | 0.5192 | 0.4808 | **PASS** |

All three axes pass, so the conjunction is **GO** — the first on any substrate
(baseline 3 read PASS/PASS/FAIL). Per the pre-committed mapping, `decide_go_no_go`
returns `training_time_runner="surrogate"`, `surrogate_role="training-time-runner"`:
the surrogate is **promoted to the bake-off's training-time runner tier** (locked
decision 4 — promotion iff the bar passes; the 17.12 bake-off consumes this verdict,
within the §7 staleness cap). The two verdict-independent rules hold unchanged:
**final champion numbers are never surrogate-scored** (every reported number is
re-scored on a real meeting path; surrogate-vs-real divergence is reported, never
collapsed), and the bake-off is **not blocked in either direction** — a GO promotes
the runner tier, it re-plans nothing downstream.

**Honest diagnosis (read beside the verdict, not instead of it).** The ranking
channel earns this GO: 86.0% top-1 against FO-6's 22.0%, above even the strict-argmax
ceiling recipe — the pre-meeting belief fold plus the vent pin genuinely identify the
ejected target on the citation-era bytes. The decision channel does **not**: the
predictor casts SKIP-heavy ballots whose tally skips **every** test meeting (0
correct ejects; all 50 true ejections called SKIP), and its 51.9% decision accuracy
is exactly the trivial **always-SKIP** constant — it beats axis 3's always-EJECT
constant (48.1%) only because the baseline-5 economy is skip-majority (54/104). The
ratified bar names always-eject as axis 3's constant and the bar is the bar (it was
also the STRONGER trivial constant on every substrate it was ratified on); this
report states the flip so the 17.12 bake-off reads the decision channel as
population-prior-shaped, not learned. The J1 train/serve skew (§2.1) points the same
way: live-served suspicion on clamped cells is ≤ the fit-time value, a conservative,
SKIP-ward bias on 1.73% of cells. A future re-ground on an eject-majority substrate
would face axis 3 at full strength again.

**The verdict was taken on the FIRST held-out evaluation.** The model was **not**
iterated against the test split — doing so would corrupt the held-out claim. The
**val** split exists for any future model iteration, and any re-fit re-states its
verdict against **this same population-relative bar** (§9 reproduces it end-to-end).

**Secondary diagnostic — 4p1i corpus test split** (tiny, noise-dominated: 10
meetings / 4 ejections / 6 skips):

| Channel | Surrogate | Reference |
|---|---:|---:|
| top-1 | 100% (4/4) | ceiling 100%; FO-6 50.0% |
| SKIP-vs-eject | 60.0% | always-eject 40.0% → axis 3 passes (strict `>`) |
| predicted-ballot calib Brier / ECE | 0.1888 / 0.2792 (n=6) | — |

**GO on both populations** (the 4p1i figures are a corroborating diagnostic only).
One committed artifact — the **9p2i corpus fit**, the primary scored population.

---

## 6. The fallback ladder as shipped (all three stay in-contract)

The ladder shipped with the baseline-3 NO-GO and **stays in place under the GO** —
it is what a future NO-GO (or a staleness-cap hit, §7–§8) falls back to, and (a)
remains the training env's default wiring until the 17.12 bake-off consumes this
verdict through the factory seam:

- **(a) fake-provider MeetingManager as the training-time runner** — the training
  env's **DEFAULT** (a runner is always installed; `MEETING_PHASE_REACHED` truncation
  is structurally unreachable on this path). Exercised by committed test **regardless
  of the verdict**, so no verdict can ever block the bake-off.
- **(b) the 15.8 env's explicit `episode_boundary="first_meeting"` opt-in** with
  meeting-free fitness terms — episodes are marked **truncated** and
  `compute_shaped_reward` refuses to score them as full games (the deliberate
  boundary mode 15.8 contracts, **not** silent truncation).
- **(c) periodic real-LLM re-grounding recordings** — operator-run, `$0` on
  flat-rate Featherless (the 15.12 recorder; Task 17.9 is exactly this rung,
  executed). This is also the staleness-cap escape hatch (§7–§8).

---

## 7. The staleness doctrine (ships regardless of verdict)

Committed cap file `training/artifacts/surrogate/max-uses.json`:

```json
{ "max_uses": 62491, "unit": "meetings",
  "weights_sha256": "62d6cbfa3173bf9d56ccce7646c0722fd4e341e11c1ef2a6d2208b74c1408d28" }
```

- **Unit:** surrogate-simulated **MEETINGS** — one `SurrogateMeetingRunner.run_meeting`
  call is one use.
- **Keyed on the weights sha256:** `SurrogateUseCounter.record_use` refuses to meter a
  different artifact against the same counter.
- **CUMULATIVE across a bake-off run:** the bake-off owns **ONE**
  `SurrogateUseCounter` and threads it through every runner factory; constructing a
  fresh runner **never** resets it; exceeding the cap raises
  `SurrogateStalenessExceededError` (deliberately not silently recoverable — a trainer
  at the cap must re-ground, §8).

**Rationale for 62491 — the ~143× rule, now mechanical.** The fit is grounded on
**437 fit-side meetings** (the 3131-row table, 120 fit games), and the committed cap
is `training.surrogate.ballots.derive_max_uses(437)` = 143 × 437 = **62491**
simulated meetings ≈ 143× the grounding data — the same ratio the baseline-3 cap
encoded (50 000 ≈ 143 × 349), RE-DERIVED from this corpus per the Task-17.10
designer ruling (*"not held at 50000 by habit"*; the old `DEFAULT_MAX_USES`
constant is retired — `write_ballot_predictor_artifact` now requires an explicit
cap). The headroom arithmetic is unchanged: a mid-size ES bake-off sweep (~24 pop ×
~30 gens × ~5 seeds × ~2–3 meetings/game ≈ 7–11k simulated meetings) fits several
times over while **forcing re-grounding before unbounded optimization against a
frozen model** (the MBPO/Dreamer model-exploitation failure, audit §5.6). The cap is
**operator-tunable** by editing the committed file — which re-keys review to the
artifact hash (the sidecar + cap must agree with the weights, checked on load).

---

## 8. The re-grounding recipe (operator, `$0`, step-by-step)

Mandatory after **any mover (tactical policy) change**, **any meeting-layer/prompt
change**, or when a bake-off run **hits the cap**. The corpus README's freeze
doctrine applies throughout (never re-record without re-freezing). Task 17.9 + this
task ARE one full turn of this recipe — executed, not hypothetical.

1. **Record** a fresh real-LLM corpus slice at the current mover/meeting config —
   `bash scripts/record_ml_corpus.sh --set 9p2i` (Featherless, frozen prompt
   registry, `fsm-default` stamp — or the future champion's stamp) into a **NEW seed
   range**.
2. **Re-validate the walk BEFORE trusting any fit** —
   `measure_belief_render_parity(Path(<new corpus dir>))`: fold fidelity
   (`raw_mismatches`) must be 0, and the J1 divergence is re-measured and recorded
   (§2.1). Then rebuild the table — `build_meeting_table(Path(<new corpus dir>))`
   (it reads the recorder-written committed `splits.json`) — and read the
   coerced-SKIP count off the `ballot_coerced_skip` column.
3. **Re-fit + commit weights** — `fit_corpus_ballot_predictor(table)` (coerced-SKIP
   rows are dropped by the fit, §2.1) then
   `write_ballot_predictor_artifact(predictor, Path("training/artifacts/surrogate"),
   max_uses=derive_max_uses(<fit-side meeting count>))` — the ~143× rule re-derives
   the cap from the new corpus. A new sha256 is written; the use-counter **re-keys
   automatically**.
4. **Re-measure** — `run_surrogate_fidelity` + `fo6_rebaseline` + `decide_go_no_go`
   on the new table; the verdict **re-states itself** against the same
   population-relative bar.
5. **Commit together** — weights + sha256 sidecar + cap + the updated report in one
   change.

---

## 9. Reproduce

Every number above is a pure function of the committed bytes. Each one-liner writes
nothing.

- **Table** (541 meetings / 3131 rows; fit 437 meetings / 120 games, test 104
  meetings / 30 games):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); print(t.meetings_total, len(t.rows), t.games_total)"
  ```
- **The walk re-validation + J1 live-parity divergence** (§2.1 — fold fidelity 0
  mismatches; 280 divergent cells / 254 rows, fit 251 / test 29, max 0.11):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate.dataset import measure_belief_render_parity; print(measure_belief_render_parity(Path('replays/ml_corpus/9p2i')).model_dump_json(indent=2))"
  ```
- **The coerced-SKIP census** (§2.1 — 0 rows, 0 fit-side):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); fit=set(t.splits.train)|set(t.splits.val); print(sum(r.ballot_coerced_skip for r in t.rows), sum(r.ballot_coerced_skip for r in t.rows if r.seed in fit))"
  ```
- **Surrogate fidelity report** (§3, §4-recorded-ref):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, run_surrogate_fidelity; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); print(run_surrogate_fidelity(t, lambda: BallotSurrogateModel(t), model_name='ballot-surrogate.v1').model_dump_json(indent=2))"
  ```
- **FO-6 re-baseline** (§3 floor):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, fo6_rebaseline; print(fo6_rebaseline(build_meeting_table(Path('replays/ml_corpus/9p2i'))).model_dump_json(indent=2))"
  ```
- **The verdict** (§5):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, run_surrogate_fidelity, fo6_rebaseline; from training.surrogate.fidelity import decide_go_no_go; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); s=run_surrogate_fidelity(t, lambda: BallotSurrogateModel(t), model_name='ballot-surrogate.v1'); f=fo6_rebaseline(t); print(decide_go_no_go(s, f).model_dump_json(indent=2))"
  ```
- **Artifact provenance + frozen-weights reproduction** (refit is ULP-equivalent
  to the committed weights — byte-identical only on the recording platform — and
  the LOADED artifact reproduces the reported numbers):
  ```
  uv run pytest tests/training/test_surrogate_runner.py::test_committed_artifact_round_trips_and_provenance_holds tests/training/test_surrogate_runner.py::test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers -q
  ```
- **Predicted-ballot calibration** (§4, the surrogate's OWN channel):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; from training.surrogate.fidelity import build_meeting_views; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); test=frozenset(t.splits.test); v=build_meeting_views(t); m=BallotSurrogateModel(t); m.fit([x for x in v if x.seed not in test]); print(m.predicted_ballot_calibration([x for x in v if x.seed in test]).model_dump_json(indent=2))"
  ```

---

## 10. How downstream consumes this

- **Task 17.12** (the impostor bake-off re-run): under this **GO**, the surrogate is
  the bake-off's **training-time runner** — reached via `run_tournament_eval`'s
  `meeting_runner_factory` and the env's `meeting_runner_factory` seam, metered by
  the §7 cap through ONE `SurrogateUseCounter` the bake-off owns. The
  verdict-independent rules hold: **every reported number is re-scored on a real
  meeting path** — surrogate-scored vs real-rescored columns are reported
  side-by-side where they diverge, and divergence is data, never collapsed. The
  decision-channel caveat (§5: population-prior-shaped, all-SKIP on the test split)
  and the J1 skew (§2.1: SKIP-ward on 1.73% of cells) travel WITH the promotion.
- **Task 17.15** re-runs the Goodhart probe **under the surrogate meeting path** — a
  mis-calibrated SKIP/eject rate can hold the meeting-driven floors for the wrong
  reason (this surrogate **under-ejects**: 0 of 50 held-out ejection meetings
  recognized by the decision head), so the probe reports the surrogate's
  ejection/SKIP rate alongside its verdict.
- The additive `meeting_runner_factory` keyword on `run_tournament_eval`
  (`eval/balance_eval.py:241`) remains the seam: surrogate-driven tournaments
  produce standard reports at `$0`, with the default path byte-identical (existing
  balance-eval tests stay green untouched).

The mitigations are **all structural and all shipped**: the staleness cap
(re-derived, §7), the pre-stated GO/NO-GO with the honest ceiling as denominator,
re-grounding as an executed operator recipe (§8), the measured walk/live-parity
re-validation (§2.1), and the bake-off's rule that final numbers are never
surrogate-scored — none weakened to make the verdict look better, and the verdict's
weak channel is named in the same section that reports it.
