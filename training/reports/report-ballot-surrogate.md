# The ballot-predictor surrogate — the GO/NO-GO verdict, the fallback ladder, the staleness doctrine

> Task 15.13 built this surrogate and this report; Task 17.10 re-grounded both on
> the baseline-5 corpus and read a GO; **Task 18.14 (`tasks/phase-18.md`)
> RE-GROUNDS them again on the adopted baseline-6 corpus** and re-states the
> verdict on the same owner-ratified bar (locked decision 4 travels: re-fit +
> re-verdict on the recorded bar, the 6-feature live-parity fence kept). Anchored
> to `audits/post-phase-14-ML-training-signal.md` §5.3 (predict ballots, feed the
> real tally), §5.5 (the four-channel fidelity protocol + the honest ceiling),
> §5.6 (the re-grounding / model-exploitation doctrine). Code:
> `training/surrogate/ballots.py` (the predictor + training entry),
> `training/surrogate/runner.py` (the `MeetingRunner` implementation + the Task-18.14
> fit-corpus fence), `training/surrogate/fidelity.py` (the GO/NO-GO region — 15.11
> owns the metrics core), `training/surrogate/dataset.py` (the table + the
> re-validation instrument), `eval/balance_eval.py:241` (the additive
> `meeting_runner_factory` keyword). This report sits beside the 15.11 harness
> report (`report-meeting-table.md`) — the table is the substrate every number
> below is measured on.
>
> **Date:** 2026-07-21 (baseline-5: 2026-07-16; baseline-3 original: 2026-07-09).
> **Corpus:** `replays/ml_corpus/9p2i` — 150 games, re-recorded at **baseline 6**
> (Task 18.13: `Qwen/Qwen3.6-27B` on Featherless, `qwen3_6_27b` v3 prompt set, the
> baseline-6 lever slate — the thirteen retired always-on levers including the four
> meeting-layer graduations, `impostor_roll_call` stay-OFF (crew-only ruling),
> `fsm-default` stamp, `$0`), committed `splits.json` **seed mod 5:
> {0,1,2}=train, {3}=val, {4}=test** → **fit side 120 games / held-out test 30
> games** = **367 fit-side meetings / 96 held-out test meetings**.
> **Committed artifact:** `training/artifacts/surrogate/ballot-predictor.json`,
> sha256 `611771a4853d2c4fe0ff9ebcc5811788a5a5c235ba8fc7061f4f9fe06dbf40c5`,
> staleness cap **52481 meetings** (`max-uses.json`, = 143 × the 367 fit-side
> meetings — the ~143× rule re-derived, §7), fit-corpus provenance
> `fit-corpus.json` binding the weights to the baseline-6 corpus identity (§7).
>
> Reproduce every figure with the one-liners in §9 — each is a pure function of the
> committed bytes and writes nothing.

The 15.11 harness measured the honest ceiling and re-baselined FO-6; 15.13 built the
surrogate inside that ceiling, stated the bar **before** training, and reported a
baseline-3 **NO-GO**; the baseline-5 re-ground flipped to **GO** because that
substrate went skip-majority. Task 18.13 re-recorded the corpus at the adopted
baseline-6 meeting layer, so every anchor below is **re-measured on the new bytes —
never copied** (honest ceiling 0.8200 → 0.8500; FO-6 top-1 0.2200 → 0.6500; the
always-eject constant 0.4808 → 0.6250). On the re-measured bar the verdict is
**NO-GO** — axes 1 and 2 pass but axis 3 fails on the held-out test split (§5) — with
the honest diagnosis stated beside it: the baseline-6 meeting economy REVERTED to
eject-majority, so the surrogate's unchanged all-SKIP decision head now scores below
the trivial always-eject constant (§5). Its consequence is pre-committed: the
surrogate ships **diagnostic-only**, the fake-provider MeetingManager stays the
training-time runner, and the bake-off is never blocked (§6).

---

## 1. The pre-stated GO/NO-GO bar (OWNER-RATIFIED 2026-07-09, mid-wave review Q1)

The bar was stated **before** the original surrogate was trained, committed in code
as `training.surrogate.fidelity.GO_TOP1_CEILING_RATIO` (= 0.75) + `decide_go_no_go`,
and is UNCHANGED by this re-ground (locked decision 4 re-measures the same bar,
honestly). It is **population-relative on all three axes, with no absolute
constants** — because every absolute number in this project's history moved when the
population changed (FO-6 top-1 64% → 26% → 22% → 65%; the honest ceiling 65.1% →
70.6% → 82.0% → 85.0%; the always-eject constant 80.2% → 48.1% → 62.5%), an absolute
threshold is a trap. Each axis is measured by the 15.11 harness **on the same scored
held-out population** as the surrogate's own numbers:

> **GO ⇔** held-out top-1 **≥ 0.75 × the honest ceiling measured on the same scored
> population** by the 15.11 harness **AND** held-out top-1 **>** the
> corpus-re-baselined FO-6 logistic **AND** SKIP-vs-eject accuracy **>** the scored
> population's own `always_eject_baseline` (on this corpus test split that trivial
> constant is **0.6250** — the eject-majority substrate restores it at FULL strength,
> exactly as the ratified wording predicted).

Pre-committed **in the same breath**: **NO-GO ⇒ fallback (a)** — the fake-provider
MeetingManager stays the bake-off's training-time runner and the surrogate ships as
a **DIAGNOSTIC only**. `decide_go_no_go` returns
`training_time_runner="fake-provider-meeting-manager"`,
`surrogate_role="diagnostic-only"` — the machine-readable mapping the bake-off
consumes, never a prose reading. Either way: final champion numbers are **never
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
agrees only to float ULP (numpy's SIMD summation grouping varies by machine — a
convex 300-epoch descent converges to the same optimum within the round-trip test's
`rel=1e-9` tolerance, unlike the chaotic ES artifacts whose byte-identity holds only
per-platform), so the **committed bytes are the frozen ground truth** the sha pins
and the bake-off reloads — the round-trip test asserts refit parameter-equivalence
plus frozen-weights reproduction of every reported number.

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
runner never sees. Baseline-6 channels a training-time runner cannot reconstruct
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

### 2.1 The baseline-6 re-validation (Task 18.14 — measured, never assumed)

Three load-bearing validations ran on the new bytes **before the fit was trusted**
(the 16.10 walk precedent), via `training.surrogate.dataset.
measure_belief_render_parity` — the end-to-end cross-check of the table's
hand-mirrored belief fold against the **production fold** (`eval.funnel`'s
memory-augmented walk: real `TacticalAgent`s fed reconstructed packets, read through
the exact `suspicion_graph_for_meeting()` accessor a live meeting consumes):

| Gauge | 9p2i | 4p1i |
|---|---:|---:|
| non-self (meeting, voter, candidate) cells compared | 14 326 | 240 |
| **fold fidelity** — raw `belief_suspicion` vs the production raw scalar | **0 mismatches** | **0 mismatches** |
| **fold fidelity** — `belief_trust` vs production trust | 0 mismatches | 0 mismatches |
| **J1 live-parity divergence** — cells where the CLAMPED live render ≠ the raw column | **141 (0.98%)** | 0 |
| — rows carrying ≥ 1 divergent cell | 130 of 2726 (4.8%) | 0 |
| — divergent cells on the fit side (train ∪ val) / the test side | 113 / 28 | 0 / 0 |
| — max abs divergence | 0.06 | 0.0 |

1. **The dataset walk re-validates on the new bytes.** The baseline-6 corpus carries
   whereabouts turns, observation-cited ballots, and marker-prefixed rationales;
   both sets reconstruct with every per-tick `state_hash` and per-meeting
   `state_hash_before`/`state_hash_after` verified, 100% ballot join, and the
   hand-mirrored perception→belief pins (`_WindowStats`) **exactly reproduce the
   production fold** — 0 raw mismatches over 14 566 cells across both sets. The
   integration risk (silent `belief_suspicion` corruption) is discharged by
   measurement; the fidelity INVARIANTS are pinned LIVE in
   `test_j1_fold_fidelity_is_exact_on_the_9p2i_corpus`, not behind the census.

2. **The J1 live-parity divergence is measured and recorded.** The graduated
   Task-16.4 hard-evidence gate (unconditional since the baseline-5 record) clamps
   an entirely-soft conviction-grade row to 0.59 at the two belief-render read-sites
   — including `suspicion_graph_for_meeting()`, the exact channel the live
   `SurrogateMeetingRunner` reads. The table's `belief_suspicion` column is the RAW
   stored scalar, so raw-vs-served diverges on exactly the clamped cells: **141 of
   14 326 cells (0.98%), 130 of 2726 rows, max 0.06** — the skew SHRANK again on the
   baseline-6 meeting layer (280/1.73%/0.11 at baseline 5). **The fit reads the RAW
   column**, for three stated reasons: (a) production doctrine — every non-render
   consumer reads the raw stored scalar, and the table's belief columns also feed the
   fidelity instruments (`public_suspicion`, `recon_suspicion`, the ceiling's
   belief-lead), which are defined on the true belief graph; (b) the divergence is
   measured and bounded (0.98% of cells, ≤ 0.06); (c) the live runner IS served the
   clamped value, so the promoted-or-diagnostic runner carries a **known,
   conservative** train/serve skew on those cells — live suspicion never exceeds the
   fit-time value, which pushes marginal meetings toward SKIP, the direction the
   decision head already sits at (§5). Moving the fit onto the render channel would
   change the instrument semantics mid-re-ground and is a substrate decision for a
   future contract, not a silent side effect here.

   **The runner-path fidelity replay (the measured consequence).** Re-scoring the
   FROZEN committed artifact over the held-out test split with every divergent cell
   replaced by the live-served CLAMPED value (all 28 held-out cells — the same census
   as above, the two instruments cross-validating) reproduces the §5 verdict inputs
   **exactly**: the same decision and the same top-1 target on **every one of the 96
   meetings** (46/60 top-1, all-SKIP census, 36 correct skips); the only movement is
   a decision-irrelevant sub-top-rank reorder on a handful of meetings
   (libm/ULP-sensitive across CPUs, the same platform variance the artifact
   round-trip tolerates). All three verdict axes — the two that PASS and the one that
   FAILS — hold unchanged on the features the diagnostic runner actually serves,
   pinned by `test_no_go_verdict_holds_on_live_served_clamped_features`.

3. **Coerced-SKIP rows are excluded from the fit and counted.** A J2 citation-gate
   coerced ballot records `target="SKIP"` with
   `meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER` prefixed to its
   `rationale_text` — a **forced eject, not a chosen skip** (designer ruling,
   `tasks/phase-17.md`), poison for the decision channel. The table carries
   `ballot_coerced_skip` per row (the anchored repr-aware marker parse, the
   `api.replay_loader._marker_pattern` convention) and **both fit paths drop flagged
   rows**; the fidelity replay scores recorded bytes unfiltered. On this corpus the
   count is **1 of 2726 rows (9p2i), 1 of them fit-side, and 0 of 120 (4p1i)** — the
   single dropped row is seed 1027, `headless-seed-1027:meeting-4`, voter `p-8`:
   unlike the baseline-5 zero-count fixture, the exclusion now removes a real
   poisoned row from the fit. (The other rationale markers on the corpus are *not* in
   the exclusion:
   teammate-coerced SKIPs — the §7.12 by-design skip the runner mirrors by candidate
   exclusion — under-gate redirects, and parse-defaults; only the J2 coercion marker
   records a vote the voter never chose as a skip.)

   > **2026-08-27 — the exclusion widened; the next fit applies it.** The
   > per-kind list above reasons about the SKIP DECISION label, which the
   > under-gate redirects never touch: they keep the voter's authored EJECT and
   > rewrite only the TARGET. `BallotExample` carries ONE `target` field feeding
   > both the ranking softmax and the SKIP alternative, so a rewritten target is
   > a poisoned label for the whole example. Both fit paths now drop every row
   > whose recorded target is not the voter's authored choice — the five-member
   > class `meetings.schemas.BallotTargetRewriteReason` names, read from that
   > union rather than re-spelled — while the two citation-only rewrites stay in
   > the fit, labelled and counted, because they null a reference and leave the
   > target intact. On the corpus now on disk the whole-table census moves from
   > 7 rows to 102 (9p2i) and from 0 to 2 (4p1i); what a fit actually drops is
   > the `train ∪ val` share of that — **7 → 82** on 9p2i and 0 → 2 on 4p1i, the
   > other 20 being held-out rows no fit path ever consumed. Over the same
   > window the `is_reporter`
   > slot is masked to a constant on the fit and the serve side alike: the
   > reporter is a crewmate on all 3,602 recorded ballots across the four
   > committed sets, so a fit that reads it learns roles ground truth rather than
   > a ballot. **Every number in this report is the baseline-6 fit's, taken
   > before both changes** — they are the record of that evaluation, and the ML
   > re-ground re-states them.

---

## 3. Held-out fidelity vs the ceiling (the four channels together)

Scored population: the **9p2i corpus test split** — 30 games / **96 meetings** /
**60 ejections** / **36 skips**. The baseline-6 meeting economy REVERTED to
**eject-majority** (302 of 463 corpus meetings eject = 65.2%; recorded voters cast
SKIP on 42.1% of all ballots, down from 58.4% on baseline 5) — the single biggest
substrate shift under every number below. Every channel (ranking, decision,
calibration, the ceiling) is measured on **this one distribution**, so they describe
the same games.

**Surrogate `ballot-surrogate.v1`:**

| Channel | Value |
|---|---|
| top-1 (ejected target ranked first) | **76.7%** (46/60) |
| top-2 | **91.7%** (55/60) |
| SKIP-vs-eject decision accuracy | **37.5%** (36/96) |
| — correct ejects / correct skips | **0** correct ejects · 36 correct skips |
| always-eject baseline (population constant) | **62.5%** (60/96) |
| decision census (predicted) | **0 ejections · 96 skips** |
| `degenerates_to_skip` | **True** (accuracy 0.375 ≤ always-eject 0.625 — the eject-era flag fires) |
| ejection-confidence Brier / ECE | 0.0679 / 0.0948 |

**The honest ceiling on the SAME population** (a measurement, not a target):

| Ceiling channel | Value |
|---|---|
| max achievable top-1 (strict-argmax recipe) | **85.0%** (reachable 51/60) |
| flag on target | 57/60 |
| proximity/eyewitness on target | 49/60 |
| strict belief-lead on target | 43/60 |
| voice-driven share (the complement) | **15.0%** |

The surrogate's top-1 (76.7%) sits **comfortably below** the measured 85.0% ceiling —
the eject-majority substrate no longer lets the learned ranker exceed the
strict-argmax recipe the way baseline 5 did. The ceiling is the honest measure of the
**voice-driven share** (15.0% of ejections formed from the current meeting's spoken
narrative — down from 18.0% on baseline 5), not a hard information bound on the
learned ranker; axis 1 of the bar reads it as its denominator exactly as ratified.

**FO-6 re-baseline on the SAME population** (`fo6_rebaseline`, the floor to beat):

| FO-6 channel | Value |
|---|---|
| top-1 | **65.0%** (39/60) |
| top-2 | 70.0% |
| SKIP-vs-eject decision accuracy | 62.5% |
| decision census (predicted) | 96 ejections · 0 skips (all 96 meetings called EJECT) |
| `degenerates_to_skip` | **False** — the head degenerates the OTHER way (all-EJECT), which on an eject-majority mix ties the always-eject constant, so the skip-era flag reads False by its own formula |

**Recorded-ballot reference calibration (the WOLF channel, model-INDEPENDENT).** Over
the scored split's **323** recorded ballot rows, each real voter's stated confidence
vs whether its named target was ejected: **ballot Brier 0.1242 / ballot ECE 0.0489**.
This is a property of the committed ballots — it is *not* the surrogate's calibration
(§4), and the harness reports it for every model as the ground-truth reference
(arXiv:2512.09187 WOLF ~0.26–0.29).

---

## 4. The surrogate's PREDICTED-ballot calibration (its OWN channel)

Distinct by construction from the recorded reference in §3. Fitting
`BallotSurrogateModel` on the non-test views and scoring the predicted **non-SKIP**
ballot confidences on the test views against whether the predicted target was
actually ejected:

| Predicted-ballot calibration | Value |
|---|---|
| Brier | **0.2542** |
| ECE | **0.2465** |
| predicted ballots (non-SKIP) | 100 |
| predicted SKIP ballots | 457 |

**State it plainly:** the harness's committed `ballot_brier` (0.1242) / `ballot_ece`
(0.0489) are the **model-independent RECORDED-ballot reference**; the numbers in
this section are the **surrogate's own predicted-confidence calibration** and are
**markedly worse**. The predictor casts SKIP on 82% of individual ballots (457 of
557), and its 100 non-SKIP ballots are spread too thin for any plurality to clear the
0.60 tally gate — which is why the meeting-level decision census in §3 is all-SKIP,
even on an eject-majority corpus.

---

## 5. THE VERDICT: NO-GO

`decide_go_no_go(surrogate, fo6)` on the shared 96-meeting / 60-ejection
population:

| # | Axis | Surrogate | Bar | Result |
|---|---|---:|---:|:---:|
| 1 | top-1 ≥ 0.75 × ceiling | 0.7667 | 0.6375 (= 0.75 × 0.8500) | **PASS** |
| 2 | top-1 > FO-6 re-baseline | 0.7667 | 0.6500 | **PASS** |
| 3 | SKIP-vs-eject > always-eject | 0.3750 | 0.6250 | **FAIL** |

Axes 1 and 2 pass but axis 3 fails, so the conjunction is **NO-GO** — the substrate
flipped the baseline-5 GO back (baseline 3 also read NO-GO, on a different failing
axis). Per the pre-committed mapping, `decide_go_no_go` returns
`training_time_runner="fake-provider-meeting-manager"`,
`surrogate_role="diagnostic-only"`: the surrogate ships as a **DIAGNOSTIC** and the
fake-provider MeetingManager stays the bake-off's training-time runner (locked
decision 4 — promotion iff the bar passes; here it does not). The two
verdict-independent rules hold unchanged: **final champion numbers are never
surrogate-scored**, and the bake-off is **not blocked in either direction** — a
NO-GO keeps the default fake-provider runner, it re-plans nothing downstream, and
Task 18.15's conviction-economy model carries its own independent GO bar.

**Honest diagnosis (read beside the verdict, not instead of it).** The ranking
channel is genuinely competent: 76.7% top-1 against FO-6's 65.0%, clearing both the
ceiling ratio and the FO-6 floor — the pre-meeting belief fold plus the vent pin
identify the ejected target well on the citation-era bytes. What fails is the
**decision channel**: the predictor casts SKIP-heavy ballots whose tally skips
**every** test meeting (0 correct ejects; all 60 true ejections called SKIP), and its
37.5% decision accuracy is exactly the trivial **always-SKIP** constant — which now
scores BELOW axis 3's always-EJECT constant (62.5%) because the baseline-6 economy is
eject-majority (60/96). This is the honest inverse of the baseline-5 GO: there, the
same all-SKIP head *beat* always-eject only because the substrate was skip-majority;
the ratified bar named always-eject as axis 3's constant and warned it was the
STRONGER trivial constant on every substrate it was ratified on. Baseline 6 restores
it at full strength, and the surrogate's decision head — unchanged in behavior — falls
under it. The J1 train/serve skew (§2.1) points the same way: live-served suspicion on
clamped cells is ≤ the fit-time value, a conservative, SKIP-ward bias on 0.98% of
cells.

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
| predicted-ballot calib Brier / ECE | 0.2421 / 0.3125 (n=6) | — |

The 4p1i secondary reads **GO** (all three axes pass on a 50/50 skip-majority mix),
but it is a **corroborating diagnostic only** and does NOT change the shipped verdict:
the primary scored population is the 9p2i corpus, whose **NO-GO governs**. The split
is itself the honest reading — a tiny skip-majority set flatters exactly the axis the
large eject-majority set fails.

---

## 6. The fallback ladder as shipped (all three stay in-contract)

The ladder shipped with the baseline-3 NO-GO, held under the baseline-5 GO, and is
**what this baseline-6 NO-GO falls back to** — (a) is the training env's default
wiring and the surrogate is now diagnostic-only, exactly the pre-committed
consequence:

- **(a) fake-provider MeetingManager as the training-time runner** — the training
  env's **DEFAULT** (a runner is always installed; `MEETING_PHASE_REACHED` truncation
  is structurally unreachable on this path). Exercised by committed test **regardless
  of the verdict**, so no verdict can ever block the bake-off. Under this NO-GO it is
  what the bake-off runs; the surrogate remains available as a diagnostic.
- **(b) the 15.8 env's explicit `episode_boundary="first_meeting"` opt-in** with
  meeting-free fitness terms — episodes are marked **truncated** and
  `compute_shaped_reward` refuses to score them as full games (the deliberate
  boundary mode 15.8 contracts, **not** silent truncation).
- **(c) periodic real-LLM re-grounding recordings** — operator-run, `$0` on
  flat-rate Featherless (the 15.12 recorder; Task 18.13 is exactly this rung,
  executed). This is also the staleness-cap escape hatch (§7–§8).

---

## 7. The staleness doctrine (ships regardless of verdict)

Committed cap file `training/artifacts/surrogate/max-uses.json`:

```json
{ "max_uses": 52481, "unit": "meetings",
  "weights_sha256": "611771a4853d2c4fe0ff9ebcc5811788a5a5c235ba8fc7061f4f9fe06dbf40c5" }
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

**Rationale for 52481 — the ~143× rule, mechanical.** The fit is grounded on **367
fit-side meetings** (the 2726-row table, 120 fit games), and the committed cap is
`training.surrogate.ballots.derive_max_uses(367)` = 143 × 367 = **52481** simulated
meetings ≈ 143× the grounding data — the same ratio every prior cap encoded (62491 ≈
143 × 437; 50 000 ≈ 143 × 349), RE-DERIVED from this corpus. The headroom arithmetic
is unchanged: a mid-size ES bake-off sweep (~24 pop × ~30 gens × ~5 seeds × ~2–3
meetings/game ≈ 7–11k simulated meetings) fits several times over while **forcing
re-grounding before unbounded optimization against a frozen model** (the
MBPO/Dreamer model-exploitation failure, audit §5.6). The cap is
**operator-tunable** by editing the committed file — which re-keys review to the
artifact hash (the sidecar + cap must agree with the weights, checked on load).

**The fit-corpus fence (Task 18.14 — new).** `SurrogateStalenessCap` keys only on
`weights_sha256`, so `load_surrogate_runner_factory` failed loud on WEIGHTS drift but
was BLIND to SUBSTRATE drift — a bake-off could load these weights against a
re-recorded corpus while nothing raised, optimizing a policy against a model fitted on
different games. The committed `fit-corpus.json`
(`training.surrogate.runner.SurrogateFitCorpus`) closes that gap: it records the fit
corpus's identity (`corpus_set`, `fit_side_meetings`, a `corpus_sha256` fingerprint
over the recorded replay bytes + `splits.json` + `MANIFEST.md`) keyed to
`weights_sha256`. `load_surrogate_runner_factory` cross-checks that key
UNCONDITIONALLY (a botched re-fit that moved the weights but not the corpus record
fails loud) and, when a caller passes `corpus_dir`, verifies the live corpus
fingerprint matches (recomputing it reads every replay, so it is opt-in). Re-recording
the corpus and re-fitting the weights TOGETHER (the §8 recipe) keeps this record
current.

---

## 8. The re-grounding recipe (operator, `$0`, step-by-step)

Mandatory after **any mover (tactical policy) change**, **any meeting-layer/prompt
change**, or when a bake-off run **hits the cap**. The corpus README's freeze
doctrine applies throughout (never re-record without re-freezing). Task 18.13 + this
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
   max_uses=derive_max_uses(<fit-side meeting count>))`, and write the
   `fit-corpus.json` provenance (`SurrogateFitCorpus` with
   `corpus_sha256=fit_corpus_fingerprint(<new corpus dir>)`, §7). A new sha256 is
   written; the use-counter and the fit-corpus fence **re-key automatically**.
4. **Re-measure** — `run_surrogate_fidelity` + `fo6_rebaseline` + `decide_go_no_go`
   on the new table; the verdict **re-states itself** against the same
   population-relative bar (baseline 6: it read NO-GO).
5. **Commit together** — weights + sha256 sidecar + cap + fit-corpus provenance + the
   updated report in one change.

---

## 9. Reproduce

Every number above is a pure function of the committed bytes. Each one-liner writes
nothing.

- **Table** (463 meetings / 2726 rows; fit 367 meetings / 120 games, test 96
  meetings / 30 games):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); print(t.meetings_total, len(t.rows), t.games_total)"
  ```
- **The walk re-validation + J1 live-parity divergence** (§2.1 — fold fidelity 0
  mismatches; 141 divergent cells / 130 rows, fit 113 / test 28, max 0.06):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate.dataset import measure_belief_render_parity; print(measure_belief_render_parity(Path('replays/ml_corpus/9p2i')).model_dump_json(indent=2))"
  ```
- **The coerced-SKIP census** (§2.1 — 1 row, 1 fit-side):
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
- **The verdict** (§5 — NO-GO):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, run_surrogate_fidelity, fo6_rebaseline; from training.surrogate.fidelity import decide_go_no_go; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); s=run_surrogate_fidelity(t, lambda: BallotSurrogateModel(t), model_name='ballot-surrogate.v1'); f=fo6_rebaseline(t); print(decide_go_no_go(s, f).model_dump_json(indent=2))"
  ```
- **Artifact provenance + frozen-weights reproduction** (refit is ULP-equivalent
  to the committed weights — byte-identical only on the recording platform — and
  the LOADED artifact reproduces the reported numbers):
  ```
  uv run pytest tests/training/test_surrogate_runner.py::test_committed_artifact_round_trips_and_provenance_holds tests/training/test_surrogate_runner.py::test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers -q
  ```
- **The runner-path fidelity replay** (§2.1 — the NO-GO verdict inputs reproduce
  exactly on live-served J1-clamped features):
  ```
  uv run pytest tests/training/test_surrogate_runner.py::test_no_go_verdict_holds_on_live_served_clamped_features -q
  ```
- **The fit-corpus fence** (§7 — the loader catches substrate drift):
  ```
  uv run pytest tests/training/test_surrogate_runner.py::test_fit_corpus_fence_fails_loud_on_substrate_and_key_drift -q
  ```
- **Predicted-ballot calibration** (§4, the surrogate's OWN channel):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; from training.surrogate.fidelity import build_meeting_views; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); test=frozenset(t.splits.test); v=build_meeting_views(t); m=BallotSurrogateModel(t); m.fit([x for x in v if x.seed not in test]); print(m.predicted_ballot_calibration([x for x in v if x.seed in test]).model_dump_json(indent=2))"
  ```

---

## 10. How downstream consumes this

- **The impostor bake-off** (17.12 and its Phase-18 successors): under this **NO-GO**,
  the surrogate is **NOT** promoted — the fake-provider MeetingManager stays the
  bake-off's training-time runner (fallback (a)), and the surrogate is available as a
  **diagnostic only**. The verdict-independent rules hold: **every reported number is
  re-scored on a real meeting path**, and the bake-off is not blocked. The
  decision-channel caveat (§5: all-SKIP, below always-eject on the eject-majority
  split) and the J1 skew (§2.1: SKIP-ward on 0.98% of cells) travel WITH the diagnostic.
- **The Goodhart re-probe** runs under whichever meeting path the verdict selects;
  under NO-GO that is the fake-provider path, and a future surrogate-path re-run (if a
  later re-ground reads GO) would report the surrogate's ejection/SKIP rate alongside
  its verdict — this surrogate **under-ejects** (0 of 60 held-out ejection meetings
  recognized by the decision head).
- **Task 18.15's conviction-economy model** carries its own INDEPENDENT GO bar — this
  NO-GO neither blocks nor pre-empts it; the two are separate training signals.
- The additive `meeting_runner_factory` keyword on `run_tournament_eval`
  (`eval/balance_eval.py:241`) remains the seam: surrogate-driven tournaments
  produce standard reports at `$0`, with the default path byte-identical (existing
  balance-eval tests stay green untouched).

The mitigations are **all structural and all shipped**: the staleness cap
(re-derived, §7), the fit-corpus fence (new, §7), the pre-stated GO/NO-GO with the
honest ceiling as denominator, re-grounding as an executed operator recipe (§8), the
measured walk/live-parity re-validation (§2.1), and the bake-off's rule that final
numbers are never surrogate-scored — none weakened to make the verdict look better,
and the verdict's failing axis is named in the same section that reports it.

---

## 11. Errata (coordination, 2026-08-04 — the Task 19.20 report-honesty pass; additive, no in-place rewrites)

Anchor: `audits/audit-phase-19-triage.md` §7 item 20 [S-Codex/S-Claude], with §8 row 4
VERIFIED exactly, and the triage's contradiction rulings **C2** and **C9**; **C9 is the
one that reaches this report.** The item below is **additive** — no recorded byte, no
table cell, and no verdict above this section is rewritten — and it **overturns no
conclusion**: the NO-GO stands, and the figure it discusses is this report's own,
correctly labelled where it is recorded. The erratum pins the channel so the figure
cannot be conflated with two others that share the phrase "decision accuracy".

1. **"Decision accuracy" in this report names the SURROGATE's own channel, and only
   that.** §3 records the cell verbatim as:

   > `| SKIP-vs-eject decision accuracy | **37.5%** (36/96) |`

   (:242, in the `ballot-surrogate.v1` channel table over 30 test games / 96 meetings /
   60 ejections / 36 skips). Read in context that label is exact: it is the surrogate's
   **SKIP-vs-eject channel** — **0.375**, the degenerate all-SKIP constant (0 correct
   ejects, 36 correct skips, `degenerates_to_skip` **True**), and it is the measurement
   that produces this report's honest **NO-GO**.

   **What it is NOT.** It is **not** the program's meeting-decision figure. That figure
   is the composed runner's **0.8646 (83/96)** — `report-composed-runner.md` §3-4, the
   cell that gates its GO and is identical under the live candidate views. And neither
   of those is the conviction model's **0.9375 (90/96)**, which is accuracy on the
   testimony-backed **CONVERSION label** (`report-conviction-model.md` §4) and has been
   mis-cited downstream as "decision accuracy" — the triage's **C9** finding.

   **Three different figures, three different channels:** 0.375 = this surrogate's own
   SKIP-vs-eject decision channel (the honest NO-GO); 0.8646 = the composed runner's
   meeting-decision accuracy; 0.9375 = the conviction model's conversion-label accuracy.
   This note exists so that they cannot be conflated when quoted. Nothing in §3, §4 or
   §5 changes; the NO-GO and the fallback ladder stand exactly as recorded.
