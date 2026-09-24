# The composed meeting-outcome runner — manifest, first held-out verdict, Goodhart leg (Task 18.29)

**Task:** 18.29 (tasks/phase-18.md) — conviction-gated ejections in training
rollouts, composed from the two committed instruments (the 18.15/18.16
conviction model and the 15.13/18.14 ballot surrogate), no new weights.
**Code:** `training/composed_runner.py`; tests in
`tests/training/test_composed_runner.py`.
**Date:** 2026-07-22; re-ground on the baseline-8 corpus 2026-08-31 (Task 21.17);
re-ground on the baseline-9 corpus 2026-09-23.
**Corpus:** `replays/ml_corpus/9p2i` — the baseline-9 re-record (the 2026-09-22
record): committed `splits.json`, held-out test side **94 meetings / 52
ejections** (the same population both component verdicts were taken on).
**Committed artifact:** `training/artifacts/composed/` — `manifest.json` (the
component-sha manifest: conviction
`3a6fe4ca18cb0597d8df4e155be190f4601d8bfc5dae25490e9a3f3b821d762e`, surrogate
`f89016200e94e1f136c26ba6bc4293a7fe9ad9b1b7406ff7f973ed342ccfa1d4`) +
`verdict.json` (the bar verdict, with a `verdict.json.sha256` sidecar). The composed artifact carries **no weights** —
it is the manifest pinning both component shas plus the verdict. Both files were
written on Darwin 24.6.0 arm64 (macOS 15.7.3, Apple M1 Pro), CPython 3.11.15,
numpy 2.2.6: `manifest.json` sha256
`feb04d83c34358325e8582b9e18829aed78e52b3d7af2ee11b9a396d1e81794e`, `verdict.json`
sha256 `a2071c127fbdec300cef59ca0020eae5e402900456d108a2795cfb9e01503121`. The §6
Goodhart leg ran on that host and on Linux x86-64 (Intel Xeon at 2.10 GHz,
CPython 3.11.15, numpy 2.2.6), and the two runs printed byte-identical JSON
(sha256 `9b4e358a9ae3cb3b4f252e4d1238fa71994ec5692c50eb194bcaf5ea6f491d5f`).

**Verdict summary:** **GO**, taken on the FIRST held-out evaluation against the
pre-registered bar. Meeting-level decision accuracy **79/94 = 0.8404 > 0.5532**
(the strictest trivial constant on this split — always-eject), convicting-meeting
ejected-target top-1 **46/52 = 0.8846 ≥ 0.5913** (= 0.75 × the 0.7885 honest
ceiling, the standing axis-1 form), exact-outcome match **78/94 = 0.8298**
reported informationally. Consequence (pre-committed, machine-readable in
`verdict.json`): `composed_role: "optional-campaign-configuration"` — the runner
MAY be adopted through 18.21's runner-factory seam, only at a swap boundary (the
18.24 note), with the standing rules untouched: **final champion numbers are
never composed-runner-scored, and both component staleness counters meter every
composed meeting.** The composed-path Goodhart leg ran before any adoption
(§6): machinery verdict **HELD, zero machinery blockers** — with two named
adoption constraints stated in §6.3 (never silent caveats).

---

## 1. The pre-registered GO bar

Committed in the task contract (tasks/phase-18.md, Task 18.29) BEFORE any
measurement, on the held-out corpus test split (94 meetings / 52 ejections):

1. **Meeting-level decision accuracy > 0.5532** — strictly greater than the
   always-eject constant (52/94), the strictest trivial constant on this split.
   Computed population-relative (`always_eject_baseline = test_ejections /
   test_meetings`), never a hard-coded absolute.
2. **Among convicting meetings, ejected-target top-1 ≥ 0.5913** — the standing
   axis-1 form: `GO_TOP1_CEILING_RATIO` (0.75, imported from
   `training/surrogate/fidelity.py`) × the honest ceiling measured on the same
   scored population (0.7885, `compute_honest_ceiling` over the test views).
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
  0 betrayal ballots over 143 multi-impostor ballots on the composed substrate.
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

| channel | held-out (30 test games, 94 meetings) |
|---|---|
| decision accuracy | **79/94 = 0.8404** (bar > 0.5532) |
| convicting-meeting top-1 | **46/52 = 0.8846** (bar ≥ 0.5913) |
| exact-outcome match | 78/94 = 0.8298 (informational) |
| gate convictions | 47 of 94 |
| gate confusion vs the ejection label (tp/fp/fn/tn) | 42 / 5 / 10 / 37 |
| top-1 among gate-convicted ejections | 41/42 = 0.9762 (informational) |
| surrogate tally census (the composed skip branch) | 2 ejections / 92 skips |
| honest ceiling on this population | 0.7885 (52 ejections, 41 reachable) |

The surrogate-tally row restates the NO-GO fact this composes around: the
surrogate's own decision channel skips 92 of the 94 test meetings (its 0.468
decision accuracy, barely off the 0.447 always-SKIP constant), so on the composed
skip branch the pass-through tally is in practice always SKIPPED and the decision
channel is carried almost entirely by the conviction gate. The top-1 row reads
above the ceiling row beside it (46 hits against 41 reachable); §4 note (e) says
why.

> **Erratum (Task 21.17, the baseline-8 re-ground).** §3, §4 and §6 were
> re-measured from components re-fit on `replays/ml_corpus/9p2i` at the
> baseline-8 record. The baseline-6 record read 96 held-out meetings / 60
> ejections, decision accuracy **83/96 = 0.8646** against a 0.625 bar,
> convicting top-1 **46/60 = 0.7667** against 0.6375, exact-outcome 0.7917, gate
> confusion 48/1/12/35, and an all-SKIP surrogate tally on a 0.8500 ceiling.
> Those are a record of bytes this checkout no longer holds.

> **Erratum (the baseline-9 re-ground, 2026-09-23).** §1 to §8 were re-measured on
> `replays/ml_corpus/9p2i` as the 2026-09-22 record left it, from components re-fit
> on those bytes, and §6's leg was re-run on them. The baseline-8 components
> (conviction `7e764b89…`, surrogate `06b20508…`) read 91 held-out meetings / 57
> ejections, decision accuracy **82/91 = 0.9011** against a 0.6264 bar, convicting
> top-1 **47/57 = 0.8246** against 0.6184 on a 0.8246 ceiling (47 reachable),
> exact-outcome 76/91 = 0.8352, 52 gate convictions with confusion 50/2/7/32,
> 44/50 = 0.8800 among gate-convicted ejections and a tally of 2 ejections / 89
> skips; through the live candidate views they read 82/91, 45/57 and 74/91. In §5
> the composed games read 23 meetings with 11 ejections (47.8%) against 64.0% on
> the baseline-8 corpus, and §6.3's diagnosis 23 resolved meetings, 31 kills and
> 136 multi-impostor ballots. Those figures are history; that fit is still
> reachable at the last baseline-8 `main` (`39a568c6`). Scored on these bytes
> before the re-fit, the frozen baseline-8 components already read the decision,
> top-1 and exact-outcome cells the re-fit reads (0.8404, 0.8846 and 0.8298): the
> re-fit moved none of the three.

**The live candidate-view variant (measured, never assumed away — Codex review
on PR #310).** The top-1 cell above is the STANDING axis-1 recipe: the
surrogate fidelity harness's self-only candidate views, the exact channel the
committed 0.8846 was measured on. The live runner additionally drops an
impostor voter's fellow impostors from its candidate set (the §7.12 firewall),
which shifts the softmax denominator on multi-impostor meetings. Re-scoring
the whole held-out split through the LIVE views: decision accuracy **79/94 =
0.8404 (identical)**, convicting top-1 **46/52 = 0.8846 (identical)**,
exact-outcome **78/94 = 0.8298 (identical)**, surrogate tally 1 ejection of 94
(one fewer than the standard views). Every gating cell still clears its bar
(0.8404 > 0.5532; 0.8846 ≥ 0.5913), so **the GO verdict is invariant to the live
channel** — pinned by the committed test
`test_go_verdict_holds_under_the_live_teammate_exclusion_ranking` (the
surrogate's own live-parity idiom, `test_no_go_verdict_holds_on_live_served_
clamped_features`). The verdict itself stays on the standing recipe: the
pre-registered bar names the standing axis-1 form, and re-cutting the recipe
after the first evaluation would be exactly the peeking the discipline
forbids.

## 4. THE VERDICT: GO

| axis | measured | bar | pass |
|---|---|---|---|
| 1. decision accuracy | 0.8404 | > 0.5532 (always-eject) | **yes** |
| 2. convicting top-1 | 0.8846 | ≥ 0.5913 = 0.75 × 0.7885 | **yes** |
| 3. exact-outcome match | 0.8298 | informational, never gates | reported |

**GO.** Honest notes: (a) the decision channel is the conviction model's
CONVERSION head consumed as an eject/skip gate — its label was
testimony-backed conversion, not ejection, so the 10 false negatives are
mostly ejections that carried no testimony-backed conversion (8 of the 10; 52
ejections vs 44 conversions on this split); the 0.8404 is the honest measurement
of that re-use, well clear of the 0.5532 constant and below the model's 0.9255
accuracy on its own conversion label; (b) the top-1 cell is the surrogate's
retained ranking channel measured in the standing axis-1 form — identical to the
surrogate's own 0.8846, confirming the composition preserves the WHO channel
unchanged; the verdict is also invariant to the gate-conditioned reading of
"among convicting meetings" (top-1 among gate-convicted ejections = 41/42 =
0.9762 ≥ 0.5913) AND to the live candidate-view variant (§3: 46/52 = 0.8846 ≥
0.5913), so no interpretation of axis 2 flips it; (c) exact-outcome (0.8298)
compounds both channels and is quoted informationally per the
pre-registration; (d) every number here is a baseline-9 population
measurement — nothing transfers as an absolute (population-relative
doctrine), and any substrate change re-runs §8; (e) the top-1 cell reads above
the honest ceiling it is measured against: 46 hits against 41 reachable of the
52 ejections. The ceiling counts an ejection as reachable only when the ejected
player strictly leads on the best-case evidence; six of the 46 hits are meetings
where the ejected player ties for that lead and the surrogate's ranking breaks
the tie toward them (the per-meeting census is in `report-ballot-surrogate.md`
§3). For a ranker that breaks ties the ceiling is therefore not a maximum. The
bar is unchanged and passes either way; whether the ceiling's wording or its
rule changes is the owner's ruling.

## 5. What the composed path changes inside training rollouts

On the composed substrate (8 scripted-FSM games, seeds 0–7, 9p2i), **25
meetings resolved 11 ejections (44.0%)** — against 0% on the fake path (the
verdict pair's opening: fake meetings convict nobody) and 60.8% (273 of 449) on
the real baseline-9 corpus. Games reach game-over with a consistent win condition (5
crew / 3 impostor on those seeds), rosters actually shrink, and replays remain
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
9p2i, baseline-9 (baseline-8 before the 2026-09-23 re-ground), materiality
bar 0.25.

### 6.1 Machine verdict

**HELD; machinery blockers: none; findings: none.** The embedded standing probe:
baseline mean score 3.89, ES champion 0.65, relative gain **−0.8328** (the
champion scores well BELOW the honest baseline — no exploit); every lever's
score gain is negative or small (emergency +0.0064 on the score axis, report
−0.0772, wait −0.9743 with a zero-meeting set, kill −0.0611, sabotage −0.2122).
The ES trace is −1.0 in all seven generations with no improvement, so the
champion is the seed-0 starting genome, as on the baseline-8 leg.

### 6.2 The delta per forced lever against the standing bars

Predicted-supply gain per arm (the `_signed_relative_gain` convention vs the
scripted-FSM baseline; recorded-flags gain beside it; materiality bar 0.25):

| arm | meetings | predicted supply gain | recorded flags gain | predicted flags/meeting | recorded flags/meeting | predicted converting share | recorded converting share |
|---|---|---|---|---|---|---|---|
| scripted-FSM baseline | 25 | (anchor) 0.0 | 0.0 | 0.6052 | 0.000 | 0.4400 | 0.000 |
| forced-emergency | 39 | **+0.1661** | 0.0 | 0.6635 | 0.000 | 0.3333 | 0.000 |
| forced-report | 32 | −0.7009 | 0.0 | 0.1767 | 0.000 | 0.0312 | 0.000 |
| forced-wait | 0 | −1.0000 | 0.0 | 0.0000 | 0.000 | 0.0000 | 0.000 |
| forced-kill | 25 | −0.4303 | 0.0 | 0.2631 | 0.000 | 0.3200 | 0.000 |
| forced-sabotage | 23 | +0.0507 | 0.0 | 0.6023 | 0.000 | 0.4348 | 0.000 |
| ES champion | 28 | −0.2388 | 0.0 | 0.4463 | 0.000 | 0.0714 | 0.000 |

**No arm reaches the 0.25 materiality bar on the predicted-supply axis** — the
largest positive delta is the emergency arm's **+16.6%** (it carried +29.5% on
the baseline-6 record and +1.7% on the baseline-8 one). Every arm's
`validity_passed` is **False** on the composed substrate, so the gate-check
buckets (`laundered` / `substrate_divergent` / `false_blocked`) are empty
**by construction** — diagnosed in §6.3, named, never silent.

> **Baseline-8 leg, kept as history.** HELD, no blockers; baseline mean score
> 3.42, ES champion 0.65, relative gain −0.8102; lever score gains emergency
> +0.1423, report +0.0474, wait −0.9708, kill +0.1204, sabotage −0.1058. Per arm
> (meetings, predicted supply gain, predicted flags per meeting, predicted
> converting share): baseline 23, 0.0, 0.8523, 0.4783; emergency 39, +0.0171,
> 0.8399, 0.3333; report 32, −0.5091, 0.4212, 0.0312; wait 0, −1.0000, 0.0000,
> 0.0000; kill 24, −0.3700, 0.4812, 0.3750; sabotage 23, +0.0326, 0.8386, 0.4348;
> ES champion 28, −0.0268, 0.8057, 0.0714; every recorded column 0.000 and every
> arm's `validity_passed` False. That leg reproduces byte for byte at `39a568c6`
> on both hosts named in the header.

### 6.3 The honest diagnosis + the named adoption constraints

Re-running the validity gate on a probe-identical composed replay set (8 games,
roster sidecar written exactly as the arm reader writes it) isolates the
failure to **exactly one check**: `cost_and_provenance_exact` — "model=None, 0
prompt versions, substrate stamped exact on 8 games". A composed meeting makes
zero LLM calls (`llm_calls=()`), so no model row exists to stamp — structural
for ANY zero-LLM meeting path, not behavioral. Every behavioral check passes on
the same set: all 8 games reach game-over, meeting rate 1.0 (25 resolved
meetings), 0 duplicate meeting rows, 0 tick-≤1 kills over 32 kills, 0
friendly-fire kills, **0 teammate-betrayal ballots over 143 multi-impostor
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

> **Erratum (the baseline-9 re-ground, 2026-09-23 — the constraint set is
> unchanged).** Both constraints were read against the re-run leg and hold word for
> word: every arm's `validity_passed` is False, and every arm records 0.000 flags
> per meeting in bytes. Neither retired shape returns: every arm's predicted
> floors fail beside the recorded ones, and the largest predicted-supply delta is
> the emergency arm's +16.6%, under the 25% bar. The leg records only whether
> each arm passed validity; the name of the one failing check comes from the
> diagnosis above, re-run on the re-fit components (§9).

### 6.4 Component consumption (metered and quoted)

**1189 composed meetings ran** across the leg. The ONE shared sha-keyed
conviction counter (`3a6fe4ca…`) charged **1533** predicted meetings of the
committed cap **50 765** (**3.02%**): 1189 composed-runner gate reads (one per
composed meeting) + 344 probe reads (172 recorded meetings × the 2 committed
consumption paths — the fitness-term read and the composed-gate pre-screen
read). The shared surrogate counter (`f8901620…`) charged **1189** simulated
meetings of its committed cap **50 765** (**2.34%**) — one per composed
meeting. No prediction ran unmetered. (Baseline-8 leg: 1175 composed meetings;
conviction `7e764b89…` charged 1513 = 1175 + 338 of 49 764, surrogate
`06b20508…` 1175 of 49 764.)

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
  bar (`decision_accuracy_bar: 0.5531914893617021`,
  `top1_bar: 0.5913461538461539`, `top1_ceiling: 0.7884615384615384`,
  `top1_ceiling_ratio: 0.75`),
  `exact_outcome_match: 0.8297872340425532` informational. (For history: the
  baseline-8 record read bars 0.6264 / 0.6184, ceiling 0.8246, exact match
  0.8352; the baseline-6 record bars 0.625 / 0.6375, ceiling 0.85, exact match
  0.7917.)
* `adoption_constraints`: the §6.3 named constraints, machine-readable beside
  the consequence — they ride with adoption and never flip the pre-committed
  GO/NO-GO mapping.

`manifest.json` pins the component pair + the pinned thresholds
(`decision_threshold: 0.5`, `skip_confidence_threshold: 0.6`) + the bar
verdict — the composed artifact is this manifest, never weights.

## 8. Staleness + re-grounding (the standing recipes, both components)

The composed runner adds no cap of its own — it meters BOTH committed caps per
meeting (conviction 50 765, surrogate 50 765, each 143 × 355 fit-side
meetings). A run that spends either cap re-grounds per that component's own
committed recipe (`training/reports/report-conviction-model.md` §8 /
`report-ballot-surrogate.md` §8: re-record, re-validate the walk, re-fit,
re-measure, commit together) — and any substrate change re-runs BOTH component
verdicts and then THIS evaluation (a fresh `run_composed_fidelity` +
`decide_composed_go` + re-committed manifest/verdict + a fresh Goodhart leg),
the same first-eval discipline either way.

## 9. Reproduce

Every figure re-derives from committed bytes (none of the first four writes to
the tree):

```
uv run python -c "from pathlib import Path; from training.composed_runner import run_composed_fidelity; print(run_composed_fidelity(Path('replays/ml_corpus/9p2i')).model_dump_json(indent=2))"
uv run python -c "from pathlib import Path; from training.composed_runner import load_composed_manifest, load_composed_verdict; d = Path('training/artifacts/composed'); print(load_composed_manifest(d).model_dump_json(indent=2)); print(load_composed_verdict(d).model_dump_json(indent=2))"
uv run python -c "from training.bakeoff.es import ESConfig; from training.composed_runner import run_composed_goodhart_leg; c=ESConfig(generations=6, population=6, sigma=0.5, seed=0, fitness_seeds=tuple(range(8)), init_scale=0.5); print(run_composed_goodhart_leg(config=c, evidence_scope='historical').to_json())"
uv run python -c "import json, tempfile; from pathlib import Path; from eval.validity import run_validity_gate; from training.env import TacticalRolloutEnv; from training.composed_runner import load_composed_runner_factory; from training.conviction.model import ConvictionUseCounter, load_conviction_staleness_cap; from training.surrogate.runner import SurrogateUseCounter, load_staleness_cap; from training.surrogate import build_meeting_table; from training.surrogate.fidelity import build_meeting_views; c=Path('training/artifacts/conviction'); s=Path('training/artifacts/surrogate'); f=load_composed_runner_factory(conviction_artifact_dir=c, surrogate_artifact_dir=s, conviction_use_counter=ConvictionUseCounter(load_conviction_staleness_cap(c)), surrogate_use_counter=SurrogateUseCounter(load_staleness_cap(s)), composed_artifact_dir=None, evidence_scope='historical'); d=Path(tempfile.mkdtemp()); (d/'roster.json').write_text(json.dumps({'num_players': 9, 'num_impostors': 2, 'tasks_per_crewmate': 2})); e=TacticalRolloutEnv(num_players=9, num_impostors=2, tasks_per_crewmate=2, intent_selector=None, output_dir=d, meeting_runner_factory=f); [e.rollout(i) for i in range(8)]; [p.unlink() for p in d.glob('*.audit.jsonl')]; r=run_validity_gate(d); [print(k.passed, k.name, k.summary) for k in r.checks]; print('kills', dict(next(k for k in r.checks if k.name == 'no_tick_1_kills').facts)); v=build_meeting_views(build_meeting_table(d)); print(len(v), sum(x.ejected is not None for x in v), sorted(json.loads(p.read_text().splitlines()[-1])['winner'] for p in d.glob('replay-seed-*.jsonl')))"
uv run pytest -m campaign tests/training/test_composed_runner.py -q
```

The leg runs at historical scope because both components are version-one fits,
which a current-scope load refuses. The fourth line is the §5 / §6.3 diagnosis:
the scripted-FSM arm's eight games replayed into a scratch directory as the
probe writes them, then the validity gate and a count of meetings, ejections and
winners. The verdict and manifest were written by:

```
uv run python -c "from pathlib import Path; from training.composed_runner import run_composed_fidelity, decide_composed_go, build_composed_manifest, write_composed_manifest_artifact, write_composed_verdict_artifact, load_composed_verdict; from training.conviction.fidelity import load_conviction_verdict; from scripts.verify_ml_evidence import _COMPOSED_ADOPTION_CONSTRAINTS as K; a=Path('training/artifacts/composed'); ca=Path('training/artifacts/conviction'); k=load_composed_verdict(a).adoption_constraints; assert k == K; r=run_composed_fidelity(Path('replays/ml_corpus/9p2i')); v=decide_composed_go(r, conviction_weights_sha256=(ca/'conviction-model.json.sha256').read_text().split()[0], surrogate_weights_sha256=(Path('training/artifacts/surrogate')/'ballot-predictor.json.sha256').read_text().split()[0], adoption_constraints=k); write_composed_verdict_artifact(v, a); write_composed_manifest_artifact(build_composed_manifest(v, conviction_verdict=load_conviction_verdict(ca)), a); print(v.verdict, v.composed_role, v.meets_decision_bar, v.meets_top1_bar, v.decision_accuracy, v.decision_accuracy_bar, v.convicting_top1, v.top1_bar, v.top1_ceiling, v.exact_outcome_match)"
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
* Any substrate change re-runs §8 — every number here is a baseline-9
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
