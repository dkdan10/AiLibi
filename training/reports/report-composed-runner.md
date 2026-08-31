# The composed meeting-outcome runner — manifest, first held-out verdict, Goodhart leg (Task 18.29)

**Task:** 18.29 (tasks/phase-18.md) — conviction-gated ejections in training
rollouts, composed from the two committed instruments (the 18.15/18.16
conviction model and the 15.13/18.14 ballot surrogate), no new weights.
**Code:** `training/composed_runner.py`; tests in
`tests/training/test_composed_runner.py`.
**Date:** 2026-07-22.
**Corpus:** `replays/ml_corpus/9p2i` — the baseline-6 re-record (Task 18.13):
committed `splits.json`, held-out test side **96 meetings / 60 ejections** (the
same population both component verdicts were taken on).
**Committed artifact:** `training/artifacts/composed/` — `manifest.json` (the
component-sha manifest: conviction
`4841f8e02eb7b587237c5b88bc2d350c12c7a5b5ac5c7ae1481069235c7b2a47`, surrogate
`611771a4853d2c4fe0ff9ebcc5811788a5a5c235ba8fc7061f4f9fe06dbf40c5`) +
`verdict.json` (the bar verdict). The composed artifact carries **no weights** —
it is the manifest pinning both component shas plus the verdict.

**Verdict summary:** **GO**, taken on the FIRST held-out evaluation against the
pre-registered bar. Meeting-level decision accuracy **83/96 = 0.8646 > 0.625**
(the strictest trivial constant on this split — always-eject), convicting-meeting
ejected-target top-1 **46/60 = 0.7667 ≥ 0.6375** (= 0.75 × the 0.8500 honest
ceiling, the standing axis-1 form), exact-outcome match **76/96 = 0.7917**
reported informationally. Consequence (pre-committed, machine-readable in
`verdict.json`): `composed_role: "optional-campaign-configuration"` — the runner
MAY be adopted through 18.21's runner-factory seam, only at a swap boundary (the
18.24 note), with the standing rules untouched: **final champion numbers are
never composed-runner-scored, and both component staleness counters meter every
composed meeting.** The composed-path Goodhart leg ran before any adoption
(§6): machinery verdict **HELD, zero machinery blockers** — with three named
adoption constraints stated in §6.3 (never silent caveats).

---

## 1. The pre-registered GO bar

Committed in the task contract (tasks/phase-18.md, Task 18.29) BEFORE any
measurement, on the held-out corpus test split (96 meetings / 60 ejections):

1. **Meeting-level decision accuracy > 0.625** — strictly greater than the
   always-eject constant (60/96), the strictest trivial constant on this split.
   Computed population-relative (`always_eject_baseline = test_ejections /
   test_meetings`), never a hard-coded absolute.
2. **Among convicting meetings, ejected-target top-1 ≥ 0.6375** — the standing
   axis-1 form: `GO_TOP1_CEILING_RATIO` (0.75, imported from
   `training/surrogate/fidelity.py`) × the honest ceiling measured on the same
   scored population (0.8500, `compute_honest_ceiling` over the test views).
3. **Exact-outcome match (ejected id or skip) REPORTED beside the verdict** —
   informational, never gating.

Pre-committed in the same breath: **NO-GO ⇒ diagnostic-only** — the campaigns
run the standing plan (fake provider + conviction term) unchanged, and nothing
downstream re-plans. The bar arithmetic lives in
`training/composed_runner.py::decide_composed_go` (strict `>` on axis 1,
inclusive `≥` on axis 2; axis 3 never flips a verdict).

## 2. The composition (no weights of its own)

`ComposedMeetingRunner` implements the `orchestrator.game.MeetingRunner`
protocol and composes, never re-fits:

* **WHETHER** — the committed conviction model's conversion head at the pinned
  fidelity operating point: `predict(features).conversion_prob ≥
  CONVICTION_CONVERSION_DECISION_THRESHOLD` (0.5, imported from
  `training/conviction/fidelity.py`, never re-tuned). Features are the live
  12-vector from the 18.30 serving assembler
  (`training.conviction.serving.assemble_live_conviction_features` — the
  parity-pinned live path).
* **WHO** — the committed ballot surrogate's ranking channel, computed live:
  per-voter `BallotPredictor.predict_ballot(...).target_probs`, aggregated to
  expected vote shares (mean over the candidate's non-self voters, ties to
  smallest id) — the exact `BallotSurrogateModel.predict` recipe
  (`training/surrogate/ballots.py:860-878`). `ranking[0]` names the target.
* **The outcome** — always the REAL `meetings.voting.tally_ballots` at
  `DEFAULT_SKIP_CONFIDENCE_THRESHOLD` (0.6) over the synthesized ballots, never
  hand-set. Under a convict decision the surrogate's predicted ballots are
  re-anchored (deterministic, minimal: flip eligible voters in descending
  target-mass order, re-tallying after every step; a single confidence anchor
  raised to exactly the 0.6 gate when plurality holds but no target ballot
  reaches it; a deterministic spread of the non-namer ballots only if flipping
  every eligible voter still does not eject) until the tally returns
  `("EJECTED", ranking[0])` — un-landable ejections raise
  `ComposedBallotSynthesisError`, never a silent downgrade. Under skip the
  surrogate's ballots pass through unchanged and the tally's own output stands.
* **The §7.12 teammate firewall** is inherited from the surrogate runner
  untouched (candidate-set exclusion), and re-anchoring can only place the
  target on voters allowed to name it — an impostor's ballot never names a
  fellow impostor, before or after re-anchoring. In-loop measurement (§6):
  0 betrayal ballots over 162 multi-impostor ballots on the composed substrate.
* **Both fences load committed.** The surrogate side loads through
  `load_surrogate_runner_factory`'s fence semantics (weights-sha sidecar, cap
  cross-check, fit-corpus cross-check, counter validation); the predictor is
  read back off the same sha-verified artifact because the composition needs
  the per-voter `target_probs` the runner class keeps private. The conviction
  side is the sha-verified model + committed cap + committed **GO** verdict —
  under a NO-GO conviction verdict the composed runner is structurally
  unbuildable (fail-loud in `load_composed_components`).
* **Both counters meter every composed meeting**: the surrogate counter at
  meeting entry (the `SurrogateMeetingRunner` doctrine — one `run_meeting` is
  one use), the conviction counter on delivered prediction (the
  `ConvictionFitnessTerm.predict_meeting` doctrine — a failed assembly never
  burns quota). One shared counter per component per run; a fresh runner per
  game never resets either.

## 3. Held-out fidelity — the first evaluation

Development discipline: both components were frozen long before this task (the
surrogate weights at 15.13/18.14, the conviction weights at 18.15), the
composition holds no parameters, the decision threshold is the pinned 0.5
operating point, and the bar was pre-registered in the task contract. The
committed test split was then evaluated ONCE through
`run_composed_fidelity(Path("replays/ml_corpus/9p2i"))` (split discipline
mirrors `run_surrogate_fidelity`: committed `splits.json` honored, fit side
never scored) — and the same cells were independently re-derived from the
component public APIs alone (no `training.composed_runner` import) as an
adversarial cross-check; the two computations agree cell-for-cell.

| channel | held-out (30 test games, 91 meetings) |
|---|---|
| decision accuracy | **82/91 = 0.9011** (bar > 0.6264) |
| convicting-meeting top-1 | **47/57 = 0.8246** (bar ≥ 0.6184) |
| exact-outcome match | 76/91 = 0.8352 (informational) |
| gate convictions | 52 of 91 |
| gate confusion vs the ejection label (tp/fp/fn/tn) | 50 / 2 / 7 / 32 |
| top-1 among gate-convicted ejections | 44/50 = 0.8800 (informational) |
| surrogate tally census (the composed skip branch) | 2 ejections / 89 skips |
| honest ceiling on this population | 0.8246 (57 ejections, 47 reachable) |

The surrogate-tally row restates the NO-GO fact this composes around: the
surrogate's own decision channel skips 89 of the 91 test meetings (its 0.396
decision accuracy, barely off the always-SKIP constant), so on the composed skip
branch the pass-through tally is in practice always SKIPPED and the decision
channel is carried almost entirely by the conviction gate.

> **Erratum (Task 21.17, the baseline-8 re-ground).** §3, §4 and §6 were
> re-measured from components re-fit on `replays/ml_corpus/9p2i` at the
> baseline-8 record. The baseline-6 record read 96 held-out meetings / 60
> ejections, decision accuracy **83/96 = 0.8646** against a 0.625 bar,
> convicting top-1 **46/60 = 0.7667** against 0.6375, exact-outcome 0.7917, gate
> confusion 48/1/12/35, and an all-SKIP surrogate tally on a 0.8500 ceiling.
> Those are a record of bytes this checkout no longer holds.

**The live candidate-view variant (measured, never assumed away — Codex review
on PR #310).** The top-1 cell above is the STANDING axis-1 recipe: the
surrogate fidelity harness's self-only candidate views, the exact channel the
committed 0.8246 was measured on. The live runner additionally drops an
impostor voter's fellow impostors from its candidate set (the §7.12 firewall),
which shifts the softmax denominator on multi-impostor meetings. Re-scoring
the whole held-out split through the LIVE views: decision accuracy **82/91 =
0.9011 (identical)**, convicting top-1 **45/57 = 0.7895** (two hits lower),
exact-outcome **74/91 = 0.8132**, surrogate tally 2 ejections of 91. Every
gating cell still clears its bar (0.9011 > 0.6264; 0.7895 ≥ 0.6184), so **the
GO verdict is invariant to the live channel** — pinned by the committed test
`test_go_verdict_holds_under_the_live_teammate_exclusion_ranking` (the
surrogate's own live-parity idiom, `test_no_go_verdict_holds_on_live_served_
clamped_features`). The verdict itself stays on the standing recipe: the
pre-registered bar names the standing axis-1 form, and re-cutting the recipe
after the first evaluation would be exactly the peeking the discipline
forbids.

## 4. THE VERDICT: GO

| axis | measured | bar | pass |
|---|---|---|---|
| 1. decision accuracy | 0.9011 | > 0.6264 (always-eject) | **yes** |
| 2. convicting top-1 | 0.8246 | ≥ 0.6184 = 0.75 × 0.8246 | **yes** |
| 3. exact-outcome match | 0.8352 | informational, never gates | reported |

**GO.** Honest notes: (a) the decision channel is the conviction model's
CONVERSION head consumed as an eject/skip gate — its label was
testimony-backed conversion, not ejection, so the 7 false negatives are
mostly ejections that carried no testimony-backed conversion (57 ejections vs
51 conversions on this split); the 0.9011 is the honest measurement of that
re-use, well clear of the 0.6264 constant and now just below the model's 0.9451
accuracy on its own conversion label; (b) the top-1 cell is the surrogate's
retained ranking channel measured in the standing axis-1 form — identical to the
surrogate's own 0.8246, confirming the composition preserves the WHO channel
unchanged; the verdict is also invariant to the gate-conditioned reading of
"among convicting meetings" (top-1 among gate-convicted ejections = 44/50 =
0.8800 ≥ 0.6184) AND to the live candidate-view variant (§3: 45/57 = 0.7895 ≥
0.6184), so no interpretation of axis 2 flips it; (c) exact-outcome (0.8352)
compounds both channels and is quoted informationally per the
pre-registration; (d) every number here is a baseline-8 population
measurement — nothing transfers as an absolute (population-relative
doctrine), and any substrate change re-runs §8.

## 5. What the composed path changes inside training rollouts

On the composed substrate (8 scripted-FSM games, seeds 0–7, 9p2i), **28
meetings resolved 13 ejections (46.4%)** — against 0% on the fake path (the
verdict pair's opening: fake meetings convict nobody) and 65.2% on the real
baseline-6 path. Games reach game-over with a consistent win condition (7
crew / 1 impostor on those seeds), rosters actually shrink, and replays remain
byte-identical across re-runs (the validity gate's reconstruction check, §6.3).

## 6. The composed-path Goodhart leg (the standing rule — run before any adoption)

18.18's machinery over the composed runner as the meeting path:
`run_composed_goodhart_leg` drives `run_conviction_path_probe` with the
composed factory through its `meeting_runner_factory` seam — the arm shapes
(scripted-FSM baseline, the five forced levers, the ES champion), the
baseline-relative gate split, the `_signed_relative_gain` laundering
convention, and the one-shared-counter discipline are reused import-only,
`goodhart.py` untouched. Budget: the committed 18.18 shape (`generations=6`,
`population=6`, σ=0.5, seed=0, K=8 fitness seeds, `init_scale=0.5`), roster
9p2i, baseline-6, materiality bar 0.25.

### 6.1 Machine verdict

**HELD; machinery blockers: none; findings: none.** The embedded standing probe:
baseline mean score 3.42, ES champion 0.65, relative gain **−0.8102** (the
champion scores well BELOW the honest baseline — no exploit); every lever's
score gain is negative or small (emergency +0.1423 on the score axis, report
+0.0474, wait −0.9708 with a zero-meeting set, kill +0.1204, sabotage −0.1058).

### 6.2 The delta per forced lever against the standing bars

Predicted-supply gain per arm (the `_signed_relative_gain` convention vs the
scripted-FSM baseline; recorded-flags gain beside it; materiality bar 0.25):

| arm | meetings | predicted supply gain | recorded flags gain | predicted flags/meeting | recorded flags/meeting | predicted converting share | recorded converting share |
|---|---|---|---|---|---|---|---|
| scripted-FSM baseline | 23 | (anchor) 0.0 | 0.0 | 0.8523 | 0.000 | 0.4783 | 0.000 |
| forced-emergency | 39 | **+0.0171** | 0.0 | 0.8399 | 0.000 | 0.3333 | 0.000 |
| forced-report | 32 | −0.5091 | 0.0 | 0.4212 | 0.000 | 0.0312 | 0.000 |
| forced-wait | 0 | −1.0000 | 0.0 | 0.0000 | 0.000 | 0.0000 | 0.000 |
| forced-kill | 24 | −0.3700 | 0.0 | 0.4812 | 0.000 | 0.3750 | 0.000 |
| forced-sabotage | 23 | +0.0326 | 0.0 | 0.8386 | 0.000 | 0.4348 | 0.000 |
| ES champion | 28 | −0.0268 | 0.0 | 0.8057 | 0.000 | 0.0714 | 0.000 |

**No arm reaches the 0.25 materiality bar on the predicted-supply axis** — the
largest positive delta is the sabotage arm's +3.3%, and the emergency arm, which
carried +29.5% on the baseline-6 record, comes in at **+1.7%**. Every arm's
`validity_passed` is **False** on the composed substrate, so the gate-check
buckets (`laundered` / `substrate_divergent` / `false_blocked`) are empty
**by construction** — diagnosed in §6.3, named, never silent.

### 6.3 The honest diagnosis + the named adoption constraints

Re-running the validity gate on a probe-identical composed replay set (8 games,
roster sidecar written exactly as the arm reader writes it) isolates the
failure to **exactly one check**: `cost_and_provenance_exact` — "model=None, 0
prompt versions, substrate stamped exact on 8 games". A composed meeting makes
zero LLM calls (`llm_calls=()`), so no model row exists to stamp — structural
for ANY zero-LLM meeting path, not behavioral. Every behavioral check passes on
the same set: all 8 games reach game-over, meeting rate 1.0 (23 resolved
meetings), 0 duplicate meeting rows, 0 tick-≤1 kills over 31 kills, 0
friendly-fire kills, **0 teammate-betrayal ballots over 136 multi-impostor
ballots** (the §7.12 firewall held in-loop), 0 railroaded crew ejections, 0
dangling reason ids, byte-identical reconstruction (0 drifted samples).

Because the validity fail-close empties the machinery's blocker tuple, the
following are NAMED here as adoption constraints (the task's rule: any
above-bar finding is a named blocker for campaign adoption, never a silent
caveat):

1. **`composed-provenance-validity[all-arms,9p2i]`** — every composed-path arm
   fails the recorded validity gate on `cost_and_provenance_exact` (model=None
   on a zero-LLM meeting path), so composed-path probe reads are never
   validity-passing evidence at this scale. A campaign adopting the composed
   runner must carry this in its meters: composed-substrate probe reads are
   diagnostic-grade until the provenance check has a stamped-substrate answer
   for LLM-free meeting paths (an eval-side question, out of 18.29's scope —
   `eval/` never moves here).
2. **`composed-substrate-mints-no-recorded-flags[all-arms,9p2i]`** — every
   composed-path arm records **0.0000 flags/meeting in bytes** (empty
   transcripts — the runner synthesizes ballots, not talk), so **no
   recorded-floor read exists on this substrate at all**. A composed pre-screen
   read is therefore real-path spend advice ONLY, and every gating use must be
   paired with a recorded-bytes floor read (the pairing the arm reader performs
   structurally: both sides are computed on the same replay bytes; this leg's
   recorded side is the 0.000 column above).

Both ride with the GO rather than overturning it — the pre-committed consequence
stands (optional campaign configuration, swap-boundary adoption) — and an
adopting campaign consumes the composed pre-screen as spend advice only, pairs
every gating use with a recorded-bytes read, treats composed-substrate probe
reads as diagnostic-grade, and never lets a champion number be
composed-runner-scored (the standing rule). Both are ALSO committed
machine-readably as `adoption_constraints` in
`training/artifacts/composed/verdict.json` (Codex review on PR #310), so a
driver that branches on the verdict alone still sees them — never only this
report's prose.

> **Erratum (Task 21.17, the baseline-8 re-ground — the constraint set moved
> from three to two).** The baseline-6 record named a third constraint and
> worded the second differently; the re-run leg measures neither shape, so both
> are recorded here as history rather than carried as claims.
>
> * `prescreen-substrate-divergence-shape[fsm-baseline+emergency,9p2i]` asserted
>   that the honest baseline's and the emergency lever's PREDICTED floors PASS
>   (baseline predicted 1.169 flags/meeting against the 180/165 floor) while the
>   recorded floors fail. On these bytes the predicted floors **fail too**
>   (baseline predicted 0.8523 against the floor), so the divergence SHAPE is
>   absent. What survives is the recorded half, which is why constraint 2 above
>   is re-worded to the fact the leg actually measures.
> * `emergency-predicted-supply-above-bar[emergency,9p2i]` asserted a
>   forced-emergency predicted-supply delta of **+29.5% ≥ the 25% materiality
>   bar** with recorded 0.0 — the laundering shape. It re-measures at **+1.7%**,
>   far under the bar, so it is retired rather than restated. Its warning
>   remains true as doctrine (an empty `laundered` bucket is not a measured
>   all-clear), and constraint 1 is what carries that warning now.

### 6.4 Component consumption (metered and quoted)

**1175 composed meetings ran** across the leg. The ONE shared sha-keyed
conviction counter (`7e764b89…`) charged **1513** predicted meetings of the
committed cap **49 764** (**3.04%**): 1175 composed-runner gate reads (one per
composed meeting) + 338 probe reads (169 recorded meetings × the 2 committed
consumption paths — the fitness-term read and the composed-gate pre-screen
read). The shared surrogate counter (`06b20508…`) charged **1175** simulated
meetings of its committed cap **49 764** (**2.36%**) — one per composed
meeting. No prediction ran unmetered.

## 7. The consequence mapping (machine-readable)

`training/artifacts/composed/verdict.json` — the committed `ComposedGoVerdict`,
keyed to BOTH component shas. Downstream branches on its fields, never on this
report's prose:

* `verdict: "GO"`
* `composed_role: "optional-campaign-configuration"` — the runner MAY be
  passed through 18.21's runner-factory seam as a campaign configuration,
  adopted only at a swap boundary (the 18.24 note), with both component
  use-counters quoted in the campaign meters; under `"diagnostic-only"` the
  campaigns run the standing plan unchanged.
* `meets_decision_bar: true`, `meets_top1_bar: true`, every cell beside its
  bar (`decision_accuracy_bar: 0.625`, `top1_bar: 0.6375`,
  `top1_ceiling: 0.85`, `top1_ceiling_ratio: 0.75`),
  `exact_outcome_match: 0.7917` informational.
* `adoption_constraints`: the §6.3 named constraints, machine-readable beside
  the consequence — they ride with adoption and never flip the pre-committed
  GO/NO-GO mapping.

`manifest.json` pins the component pair + the pinned thresholds
(`decision_threshold: 0.5`, `skip_confidence_threshold: 0.6`) + the bar
verdict — the composed artifact is this manifest, never weights.

## 8. Staleness + re-grounding (the standing recipes, both components)

The composed runner adds no cap of its own — it meters BOTH committed caps per
meeting (conviction 52 481, surrogate 52 481, each 143 × 367 fit-side
meetings). A run that spends either cap re-grounds per that component's own
committed recipe (`training/reports/report-conviction-model.md` §8 /
`report-ballot-surrogate.md` §8: re-record, re-validate the walk, re-fit,
re-measure, commit together) — and any substrate change re-runs BOTH component
verdicts and then THIS evaluation (a fresh `run_composed_fidelity` +
`decide_composed_go` + re-committed manifest/verdict + a fresh Goodhart leg),
the same first-eval discipline either way.

## 9. Reproduce

Every figure re-derives from committed bytes (the first two write nothing):

```
uv run python -c "from pathlib import Path; from training.composed_runner import run_composed_fidelity; print(run_composed_fidelity(Path('replays/ml_corpus/9p2i')).model_dump_json(indent=2))"
uv run python -c "from pathlib import Path; from training.composed_runner import load_composed_manifest, load_composed_verdict; d = Path('training/artifacts/composed'); print(load_composed_manifest(d).model_dump_json(indent=2)); print(load_composed_verdict(d).model_dump_json(indent=2))"
uv run python -c "
from training.bakeoff.es import ESConfig
from training.composed_runner import run_composed_goodhart_leg
cfg = ESConfig(generations=6, population=6, sigma=0.5, seed=0, fitness_seeds=tuple(range(8)), init_scale=0.5)
print(run_composed_goodhart_leg(config=cfg).to_json())"
uv run pytest tests/training/test_composed_runner.py -q
```

## 10. How downstream consumes this

* **18.21's driver** (when it lands) takes
  `load_composed_runner_factory(conviction_use_counter=…,
  surrogate_use_counter=…)` as an OPTIONAL campaign configuration — only under
  this committed GO verdict, only at a swap boundary (18.24), with both
  counters quoted in the campaign meters and the §6.3 constraints carried. The
  18.24 rule is structural: the factory's DEFAULT path loads the committed
  composed verdict, cross-checks both component shas, and refuses anything but
  GO (`composed_artifact_dir=None` is the diagnostic escape for the Goodhart
  leg / re-evaluation machinery, never for campaign wiring). The default
  campaign meeting path remains the fake provider; nothing adopts
  automatically.
* **The standing rules bind regardless:** final champion numbers are never
  composed-runner-scored; the Goodhart probe re-runs when the composed
  runner's training-signal role grows further (the standing rule this leg
  instantiated); NO-GO or a fired probe would have left the campaigns on the
  standing plan with nothing re-planned — the fallback is always live.
* Any substrate change re-runs §8 — every number here is a baseline-6
  measurement, not a transferable constant.

## 11. Errata (coordination, 2026-08-04 — the Task 19.20 report-honesty pass; additive, no in-place rewrites)

Anchor: `audits/audit-phase-19-triage.md` §7 item 20 [S-Codex/S-Claude], with §8
row 4 VERIFIED exactly, and the triage's contradiction rulings **C2** and **C9**;
**C9 is the one that reaches this report.** The item below is **additive** — no
recorded byte, no table cell, and no verdict above this section is rewritten — and
it **overturns no conclusion**: this report already draws the distinction
correctly. The erratum exists because external citations collapsed it.

1. **The report's own qualification is correct; the guard is against citations
   that drop it.** §4's honest note (a) already separates the two figures, in
   these words:

   > "well clear of the 0.625 constant but below the model's 0.9375 accuracy on
   > its own conversion label"

   (:166, closing the sentence that reports the 0.8646 decision cell). That
   clause is accurate as written and needs no change. Downstream citations,
   however, quoted the conviction model's 0.9375 as "decision accuracy" — the
   triage's **C9** finding, whose ruling is that the source reports are right and
   the mislabel is the citation's.

   **The three figures, pinned, with their channels:**
   - **0.8646 (83/96) — meeting DECISION accuracy.** This report's gating cell
     (§3 table; axis 1 of §4's verdict), and **identical under the live candidate
     views** (§3's live-view re-score: "decision accuracy **83/96 = 0.8646
     (identical)**"). This is the program's meeting-decision figure.
   - **0.7917 (76/96) — exact-outcome match.** Informational by
     pre-registration, **never gates** (§4 axis 3: "informational, never gates").
     It compounds both channels and is not a decision accuracy.
   - **0.9375 (90/96) — the conviction model's CONVERSION-label accuracy**
     (`report-conviction-model.md` §4). It is **not a decision figure and must
     not be quoted as one**; it measures the conversion head against its own
     testimony-backed conversion label, on the same 96 held-out meetings.

   The GO verdict, all three axes, and every cell in §3 stand exactly as
   recorded.
