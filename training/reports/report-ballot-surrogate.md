# The ballot-predictor surrogate — the GO/NO-GO verdict, the fallback ladder, the staleness doctrine

> Task 15.13 built this surrogate and this report; Task 17.10 re-grounded both on
> the baseline-5 corpus and read a GO; Task 18.14 re-ground them on baseline 6 and
> read a NO-GO; Task 21.17 re-ground them on the baseline-8 corpus; **the
> baseline-9 re-ground (2026-09-23) re-fits them again, on the corpus the
> 2026-09-22 record left in the tree,** and re-states the verdict on the same
> owner-ratified bar (locked decision 4 travels: re-fit + re-verdict on the
> recorded bar, the 6-feature live-parity fence kept). Anchored
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
> **Date:** 2026-09-23 (baseline-8: 2026-08-31; baseline-6: 2026-07-21;
> baseline-5: 2026-07-16; baseline-3 original: 2026-07-09).
> **Corpus:** `replays/ml_corpus/9p2i` — 150 games, re-recorded at **baseline 9**
> (the 2026-09-22 record: `Qwen/Qwen3.6-27B`, the `qwen3_6_27b` prompt set with
> the three bespoke templates at v6 and the ballot at v8, the route claim, the
> grounded SKIP with its labelling guards and the weighing channel shipped
> unconditional, `fsm-default` stamp), committed `splits.json` **seed mod 5:
> {0,1,2}=train, {3}=val, {4}=test** → **fit side 120 games / held-out test 30
> games** = **355 fit-side meetings / 94 held-out test meetings**.
> **Committed artifact:** `training/artifacts/surrogate/ballot-predictor.json`,
> sha256 `f89016200e94e1f136c26ba6bc4293a7fe9ad9b1b7406ff7f973ed342ccfa1d4`,
> staleness cap **50765 meetings** (`max-uses.json`, = 143 × the 355 fit-side
> meetings — the ~143× rule re-derived, §7), fit-corpus provenance
> `fit-corpus.json` binding the weights to the baseline-9 corpus identity
> (`6536c68c…`, the version-one identity: replay, split and manifest bytes; §7),
> and the machine-readable `verdict.json` + `verdict.json.sha256` beside them.
> Fitted on Darwin 24.6.0 arm64 (macOS 15.7.3, Apple M1 Pro), CPython 3.11.15,
> numpy 2.2.6; the same host reproduced the baseline-8 weights byte for byte from
> this recipe before the re-fit.
>
> Reproduce every figure with the one-liners in §9 — each is a pure function of the
> committed bytes and writes nothing.

The 15.11 harness measured the honest ceiling and re-baselined FO-6; 15.13 built the
surrogate inside that ceiling, stated the bar **before** training, and reported a
baseline-3 **NO-GO**; the baseline-5 re-ground flipped to **GO** because that
substrate went skip-majority, and baseline 6 flipped it back. The corpus has been
re-recorded twice since (baselines 8 and 9), so every anchor below is **re-measured
on the new bytes — never copied** (honest ceiling 0.8246 → 0.7885; FO-6 top-1
0.2456 → 0.3077; the always-eject constant 0.6264 → 0.5532). On the re-measured bar
the verdict is **NO-GO** — axes 1 and 2 pass but axis 3 fails on the held-out test
split (§5) — with the honest diagnosis stated beside it: the meeting economy stays
eject-majority, so the surrogate's SKIP-heavy decision head scores below the trivial
always-eject constant (§5). The ranking channel now reads ABOVE the documented
honest ceiling (46/52 against 41/52); §3 gives the per-meeting census of why, and
leaves the ruling on the ceiling's wording to the owner. Its consequence is
pre-committed: the
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
| non-self (meeting, voter, candidate) cells compared | 12 760 | 258 |
| **fold fidelity** — raw `belief_suspicion` vs the production raw scalar | **0 mismatches** | **0 mismatches** |
| **fold fidelity** — `belief_trust` vs production trust | 0 mismatches | 0 mismatches |
| **J1 live-parity divergence** — cells where the CLAMPED live render ≠ the raw column | **82 (0.64%)** | 0 |
| — rows carrying ≥ 1 divergent cell | 80 of 2539 (3.2%) | 0 |
| — divergent cells on the fit side (train ∪ val) / the test side | 61 / 21 | 0 / 0 |
| — max abs divergence | 0.11 | 0.0 |

1. **The dataset walk re-validates on the new bytes.** The baseline-6 corpus carries
   whereabouts turns, observation-cited ballots, and marker-prefixed rationales;
   both sets reconstruct with every per-tick `state_hash` and per-meeting
   `state_hash_before`/`state_hash_after` verified, 100% ballot join, and the
   hand-mirrored perception→belief pins (`_WindowStats`) **exactly reproduce the
   production fold** — 0 raw mismatches over 13 018 cells across both sets
   (13 030 on the baseline-8 bytes). The
   integration risk (silent `belief_suspicion` corruption) is discharged by
   measurement; the fidelity INVARIANTS are pinned LIVE in
   `test_j1_fold_fidelity_is_exact_on_the_9p2i_corpus`, not behind the census.

2. **The J1 live-parity divergence is measured and recorded.** The graduated
   Task-16.4 hard-evidence gate (unconditional since the baseline-5 record) clamps
   an entirely-soft conviction-grade row to 0.59 at the two belief-render read-sites
   — including `suspicion_graph_for_meeting()`, the exact channel the live
   `SurrogateMeetingRunner` reads. The table's `belief_suspicion` column is the RAW
   stored scalar, so raw-vs-served diverges on exactly the clamped cells: **82 of
   12 760 cells (0.64%), 80 of 2539 rows, max 0.11** on the baseline-9 bytes — the
   cell share shrank again (102/0.80%/0.11 at baseline 8, 141/0.98%/0.06 at baseline
   6, 280/1.73%/0.11 at baseline 5). **The fit reads the RAW
   column**, for three stated reasons: (a) production doctrine — every non-render
   consumer reads the raw stored scalar, and the table's belief columns also feed the
   fidelity instruments (`public_suspicion`, `recon_suspicion`, the ceiling's
   belief-lead), which are defined on the true belief graph; (b) the divergence is
   measured and bounded (0.64% of cells, ≤ 0.11); (c) the live runner IS served the
   clamped value, so the promoted-or-diagnostic runner carries a **known,
   conservative** train/serve skew on those cells — live suspicion never exceeds the
   fit-time value, which pushes marginal meetings toward SKIP, the direction the
   decision head already sits at (§5). Moving the fit onto the render channel would
   change the instrument semantics mid-re-ground and is a substrate decision for a
   future contract, not a silent side effect here.

   **The runner-path fidelity replay (the measured consequence).** Re-scoring the
   FROZEN committed artifact over the held-out test split with every divergent cell
   replaced by the live-served CLAMPED value (all 21 held-out cells — the same census
   as above, the two instruments cross-validating) reproduces the §5 verdict inputs
   **exactly**: the same decision and the same top-1 target on **every one of the 94
   meetings** (46/52 top-1, 92 predicted skips, 42 correct skips); on these weights no
   ranking moved at all, where the baseline-8 fit showed a decision-irrelevant
   sub-top-rank reorder on a handful of meetings (libm/ULP-sensitive across CPUs, the
   same platform variance the artifact round-trip tolerates). All three verdict axes
   — the two that PASS and the one that
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
   count is **0 of 2539 rows (9p2i) and 0 of 129 (4p1i)** on the baseline-9 bytes, so
   the exclusion removes nothing from this fit. (Baseline-8 record: 6 of 2516, 5
   fit-side, the first at seed 1016 `meeting-1`; baseline-6 record: 1 of 2726, 1
   fit-side.) (The other rationale markers on the corpus are *not* in
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
   > target intact. On the baseline-9 corpus the whole-table census of rows
   > carrying a rewrite label is **20 rows (9p2i), 14 of them fit-side, and 0
   > (4p1i)** (baseline 8: 80, 67 and 2). Over the same
   > window the `is_reporter`
   > slot is masked to a constant on the fit and the serve side alike: the
   > reporter is a crewmate on every recorded ballot across the four
   > committed sets, so a fit that reads it learns roles ground truth rather than
   > a ballot. **Both changes are IN the committed fit**: the weights this report
   > ships (`f8901620…`, as the baseline-8 `06b20508…` before them) were fitted
   > with the widened exclusion applied and the reporter slot masked, and §§3–5
   > are that fit's held-out evaluation. The baseline-6 figures this note was written beside —
   > a 7-row census, and every cell in the report at the time — are history.

---

## 3. Held-out fidelity vs the ceiling (the four channels together)

Scored population: the **9p2i corpus test split** — 30 games / **94 meetings** /
**52 ejections** / **42 skips**. The baseline-9 meeting economy stays
**eject-majority** (273 of 449 corpus meetings eject = 60.8%; recorded voters cast
SKIP on 41.4% of all ballots) — the distribution under every number below. Every
channel (ranking, decision, calibration, the ceiling) is measured on **this one
distribution**, so they describe the same games.

**Surrogate `ballot-surrogate.v1`:**

| Channel | Value |
|---|---|
| top-1 (ejected target ranked first) | **88.5%** (46/52) |
| top-2 | **90.4%** (47/52) |
| SKIP-vs-eject decision accuracy | **46.8%** (44/94) |
| — correct ejects / correct skips | **2** correct ejects · 42 correct skips |
| always-eject baseline (population constant) | **55.3%** (52/94) |
| decision census (predicted) | **2 ejections · 92 skips** |
| `degenerates_to_skip` | **True** (accuracy 0.468 ≤ always-eject 0.553 — the eject-era flag fires) |
| ejection-confidence Brier / ECE | 0.0616 / 0.1163 |

**The honest ceiling on the SAME population** (a measurement, not a target):

| Ceiling channel | Value |
|---|---|
| max achievable top-1 (strict-argmax recipe) | **78.8%** (reachable 41/52) |
| flag on target | 41/52 |
| proximity/eyewitness on target | 44/52 |
| strict belief-lead on target | 41/52 |
| voice-driven share (the complement) | **21.2%** |

The surrogate's top-1 (88.5%) now sits **above** the measured 78.8% ceiling, so the
committed verdict's `top1_ceiling_gap` reads −0.0962. The ceiling is the honest
measure of the **voice-driven share** (21.2% of ejections formed from the current
meeting's spoken narrative); axis 1 of the bar reads it as its denominator exactly
as ratified, and passes either way. What the gap contradicts is the ceiling's own
wording, which calls the headline the most any physical+belief surrogate could
reach. A per-meeting census settles where the extra hits come from:

| held-out ejections | ceiling-reachable | not reachable | total |
|---|---:|---:|---:|
| surrogate top-1 hit | 40 | 6 | 46 |
| surrogate top-1 miss | 1 | 5 | 6 |
| total | 41 | 11 | 52 |

All six hits the ceiling counts unreachable are **ties at the top of the best-case
score**: the ejected player shares the saturated 1.0 with one other candidate, so it
is not the *strict* leader the ceiling requires, and in every one of the six the
ejected player carries a witnessed-vent sighting and a contradiction flag. The
ceiling reads only the strongest voter's score for each candidate, while the
surrogate's ranking sums every voter's predicted ballot, each read off that voter's
own belief row and witnessed-vent pin; in five of the six the sum favours the ejected
player, with one to three voters' own rows leading it: seed 1029 meeting 2 (`p-1`
over `p-8`), 1069 meeting 1 (`p-8` over `p-2`), 1094 meeting 0 (`p-5` over `p-3`),
1144 meeting 0 (`p-3` over `p-6`) and 1149 meeting 0 (`p-8` over `p-1`). The sixth,
seed 1084 meeting 0 (`p-3` against `p-6`), is an exact tie in the surrogate's own
shares as well, and the ranking's lowest-id rule puts the ejected `p-3` first. So on
tied meetings the ceiling's strict-leader rule is not a maximum for a ranker that
breaks ties; the frozen baseline-8 weights read the same 46 of 52 against the same
41, with the same six meetings. Whether the ceiling's wording is restated or its rule
changed is the owner's ruling; nothing in `training/surrogate/fidelity.py` was
edited. (Baseline 8: the fit reached its ceiling exactly, 47/57 against 47/57.)

**FO-6 re-baseline on the SAME population** (`fo6_rebaseline`, the floor to beat):

| FO-6 channel | Value |
|---|---|
| top-1 | **30.8%** (16/52) |
| top-2 | 57.7% |
| SKIP-vs-eject decision accuracy | 44.7% |
| decision census (predicted) | 0 ejections · 94 skips (all 94 meetings called SKIP) |
| `degenerates_to_skip` | **True** — the comparator collapses to the always-SKIP constant on this population, its fourth such reading in five records |

The comparator's decision head takes the highest tau on its tied plateau. On this
test side that choice scores better than the lowest tied tau (0.4468, 42/94,
against 0.4362, 41/94: the low tau's 5 ejections catch 2 true ejections and cost 3
correct skips), re-measured on all four committed sets at the re-ground:

| set | predicted ejections, low / high tau | ejection meetings predicted SKIP, low / high | skip-vs-eject accuracy, low / high | ranking and calibration |
|---|---|---|---|---|
| `samples/9p2i` | 7 / 7 | 86 / 86 | 0.3862 / 0.3862 | identical |
| `samples/4p1i` | 18 / 16 | 9 / 10 | 0.5897 / 0.5897 | identical |
| `ml_corpus/9p2i`, test side | 5 / 0 | 50 / 52 | 0.4362 / 0.4468 | identical |
| `ml_corpus/4p1i`, test side | 5 / 5 | 1 / 1 | 0.7500 / 0.7500 | identical |

The comparator is fitted fresh on the committed table, and the surrogate verdict
reads only its ranking, which the tie-break leaves identical, so the reversal
belongs to the bytes and no re-fit can move it; whether the higher-tau rule stands
is the owner's ruling.

**Recorded-ballot reference calibration (the WOLF channel, model-INDEPENDENT).** Over
the scored split's **286** non-SKIP recorded ballot rows, each real voter's stated
confidence vs whether its named target was ejected: **ballot Brier 0.1699 / ballot
ECE 0.1488**. This is a property of the committed ballots — it is *not* the
surrogate's calibration (§4), and the harness reports it for every model as the
ground-truth reference (arXiv:2512.09187 WOLF ~0.26–0.29).

> **Erratum (Task 21.17, the baseline-8 re-ground).** Every cell in §3–§5 was
> re-measured on `replays/ml_corpus/9p2i` at the baseline-8 record. The
> baseline-6 record read 96 meetings / 60 ejections / 36 skips, top-1 76.7%
> (46/60), decision accuracy 37.5% (36/96), ceiling 85.0% with a 15.0%
> voice-driven share, and an FO-6 comparator that degenerated the OTHER way
> (all-EJECT, top-1 65.0%). Those are a record of bytes this checkout no longer
> holds; they are history, not a target, and the verdict below re-states itself
> against the population-relative bar rather than against them.

> **Erratum (the baseline-9 re-ground, 2026-09-23).** Every cell in §2.1 and
> §3–§5 was re-measured again on `replays/ml_corpus/9p2i` as the 2026-09-22 record
> left it. The baseline-8 fit (`06b20508…`) read 91 meetings / 57 ejections / 34
> skips, top-1 82.5% (47/57) at its own ceiling of 82.5%, top-2 94.7%, decision
> accuracy 39.6% (36/91) against always-eject 62.6%, Brier / ECE 0.0646 / 0.1078,
> recorded-ballot Brier / ECE 0.1225 / 0.1196 over 289 rows, and an FO-6 comparator
> at top-1 24.6% (14/57) that called all 91 meetings SKIP; its predicted-ballot
> calibration read Brier 0.3278 / ECE 0.3408 over 110 ballots and 406 SKIPs; and the
> 4p1i secondary read 8 meetings / 6 ejections at top-1 83.3%. That fit is still
> reachable at the last baseline-8 `main` (`39a568c6`); the figures are history, and
> the verdict below re-states itself against the same bar.

---

## 4. The surrogate's PREDICTED-ballot calibration (its OWN channel)

Distinct by construction from the recorded reference in §3. Fitting
`BallotSurrogateModel` on the non-test views and scoring the predicted **non-SKIP**
ballot confidences on the test views against whether the predicted target was
actually ejected:

| Predicted-ballot calibration | Value |
|---|---|
| Brier | **0.2491** |
| ECE | **0.2429** |
| predicted ballots (non-SKIP) | 84 |
| predicted SKIP ballots | 442 |

**State it plainly:** the harness's committed `ballot_brier` (0.1699) / `ballot_ece`
(0.1488) are the **model-independent RECORDED-ballot reference**; the numbers in
this section are the **surrogate's own predicted-confidence calibration** and are
**markedly worse**. The predictor casts SKIP on 84% of individual ballots (442 of
526), and its 84 non-SKIP ballots are spread too thin for any plurality to clear the
0.60 tally gate on all but two meetings — which is why the meeting-level decision
census in §3 is 2 ejections against 92 skips, even on an eject-majority corpus.
(Baseline-6 record, for history: Brier 0.2542 / ECE 0.2465 over 100 predicted
ballots and 457 predicted SKIPs, with an all-SKIP meeting census.)

---

## 5. THE VERDICT: NO-GO

`decide_go_no_go(surrogate, fo6)` on the shared 94-meeting / 52-ejection
population:

| # | Axis | Surrogate | Bar | Result |
|---|---|---:|---:|:---:|
| 1 | top-1 ≥ 0.75 × ceiling | 0.8846 | 0.5913 (= 0.75 × 0.7885) | **PASS** |
| 2 | top-1 > FO-6 re-baseline | 0.8846 | 0.3077 | **PASS** |
| 3 | SKIP-vs-eject > always-eject | 0.4681 | 0.5532 | **FAIL** |

Axes 1 and 2 pass but axis 3 fails, so the conjunction is **NO-GO** — the same shape
the baseline-6 and baseline-8 records read, re-stated on the baseline-9 population
(no flip). Per the
pre-committed mapping, `decide_go_no_go` returns
`training_time_runner="fake-provider-meeting-manager"`,
`surrogate_role="diagnostic-only"`: the surrogate ships as a **DIAGNOSTIC** and the
fake-provider MeetingManager stays the bake-off's training-time runner (locked
decision 4 — promotion iff the bar passes; here it does not). The two
verdict-independent rules hold unchanged: **final champion numbers are never
surrogate-scored**, and the bake-off is **not blocked in either direction** — a
NO-GO keeps the default fake-provider runner, it re-plans nothing downstream, and
Task 18.15's conviction-economy model carries its own independent GO bar.

**Honest diagnosis (read beside the verdict, not instead of it).** The ranking
channel is genuinely competent, and on these bytes it sits above its own ceiling:
88.5% top-1 against FO-6's 30.8%, clearing both the ceiling ratio and the FO-6 floor —
the pre-meeting belief fold plus the vent pin identify the ejected target on 40 of the
41 reachable ejections and break six best-case ties besides (§3). What fails is the
**decision channel**: the predictor casts SKIP-heavy ballots whose tally skips 92 of
the 94 test meetings (2 correct ejects; 50 of the 52 true ejections called SKIP), and
its 46.8% decision accuracy sits barely above the trivial **always-SKIP** constant
(44.7%) and below axis 3's always-EJECT constant (55.3%), because the baseline-9
economy is eject-majority (52/94). The ratified bar named always-eject as axis 3's constant and warned it was
the STRONGER trivial constant on every eject-majority substrate; the surrogate's
decision head — unchanged in behavior — falls under it. The J1 train/serve skew
(§2.1) points the same way: live-served suspicion on clamped cells is ≤ the fit-time
value, a conservative, SKIP-ward bias on 0.64% of cells (82 of 12 760).

**The verdict was taken on the FIRST held-out evaluation.** The model was **not**
iterated against the test split — doing so would corrupt the held-out claim. The
**val** split exists for any future model iteration, and any re-fit re-states its
verdict against **this same population-relative bar** (§9 reproduces it end-to-end).

**Secondary diagnostic — 4p1i corpus test split** (tiny, noise-dominated: 8
meetings / 5 ejections / 3 skips):

| Channel | Surrogate | Reference |
|---|---:|---:|
| top-1 | 100.0% (5/5) | ceiling 100.0%; FO-6 80.0% |
| SKIP-vs-eject | 50.0% | always-eject 62.5% → axis 3 fails |
| predicted-ballot calib Brier / ECE | 0.0003 / 0.0182 (n=6) | — |

The 4p1i secondary reads **NO-GO** on axis 3 alone (the ranking clears both the
ceiling ratio and the FO-6 floor), but it remains a **corroborating diagnostic only**
and does not decide anything: the primary scored population is the 9p2i corpus, whose
**NO-GO governs** either way. At baseline 6 this set read GO on a 10-meeting,
skip-majority mix, and at baseline 8 NO-GO on every axis; a set this size settles
little.

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
{ "max_uses": 50765, "unit": "meetings",
  "weights_sha256": "f89016200e94e1f136c26ba6bc4293a7fe9ad9b1b7406ff7f973ed342ccfa1d4" }
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

**Rationale for 50765 — the ~143× rule, mechanical.** The fit is grounded on **355
fit-side meetings** (the 2539-row table, 120 fit games), and the committed cap is
`training.surrogate.ballots.derive_max_uses(355)` = 143 × 355 = **50765** simulated
meetings ≈ 143× the grounding data — the same ratio every prior cap encoded (49764 =
143 × 348; 52481 ≈ 143 × 367; 62491 ≈ 143 × 437), RE-DERIVED from this corpus. The headroom arithmetic
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
current. The record carries the **version-one** corpus identity
(`training.provenance.historical_fit_corpus_fingerprint`: the replay bytes, the split
and the manifest), and it restores only through the explicit historical diagnostics;
whether the fit still derives from today's code is checked by measurement, not by a
source digest, by the refit-equivalence pin in
`tests/training/test_surrogate_runner.py` and the offline recompute rows of
`scripts/verify_ml_evidence.py` (`training/README.md`).

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
   `fit-corpus.json` provenance, `SurrogateFitCorpus(corpus_set=..., corpus_sha256=
   historical_fit_corpus_fingerprint(<new corpus dir>), fit_side_meetings=...,
   weights_sha256=<the new sha>)` with no `fingerprint_version` argument, serialized
   as `model_dump_json(indent=2)` plus one newline (§7). A new sha256 is written; the
   use-counter and the fit-corpus fence **re-key automatically**. (Naming
   `fit_corpus_fingerprint` here, as this step once did, writes a record labelled
   version one that carries a version-two digest, which every loader refuses.)
4. **Re-measure** — `run_surrogate_fidelity` + `fo6_rebaseline` + `decide_go_no_go(...,
   weights_sha256=<the new sha>)` on the new table, then
   `write_surrogate_verdict_artifact`, which writes `verdict.json` and its sidecar;
   the verdict **re-states itself** against the same population-relative bar
   (baselines 6, 8 and 9 all read NO-GO).
5. **Commit together** — weights + sha256 sidecar + cap + fit-corpus provenance +
   verdict + verdict sidecar + the updated report in one change.

---

## 9. Reproduce

Every number above is a pure function of the committed bytes. Each one-liner writes
nothing.

- **Table** (449 meetings / 2539 rows; fit 355 meetings / 120 games, test 94
  meetings / 30 games):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); print(t.meetings_total, len(t.rows), t.games_total)"
  ```
- **The walk re-validation + J1 live-parity divergence** (§2.1 — fold fidelity 0
  mismatches; 82 divergent cells / 80 rows, fit 61 / test 21, max 0.11):
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
- **The verdict** (§5 — NO-GO; the committed `verdict.json` adds
  `weights_sha256=` and is written by `write_surrogate_verdict_artifact`):
  ```
  uv run python -c "from pathlib import Path; from training.surrogate import build_meeting_table, run_surrogate_fidelity, fo6_rebaseline; from training.surrogate.fidelity import decide_go_no_go; from training.surrogate.ballots import BallotSurrogateModel; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); s=run_surrogate_fidelity(t, lambda: BallotSurrogateModel(t), model_name='ballot-surrogate.v1'); f=fo6_rebaseline(t); print(decide_go_no_go(s, f).model_dump_json(indent=2))"
  ```
- **Artifact provenance + frozen-weights reproduction** (refit is ULP-equivalent
  to the committed weights — byte-identical only on the recording platform — and
  the LOADED artifact reproduces the reported numbers):
  ```
  uv run pytest tests/training/test_surrogate_runner.py::test_committed_artifact_round_trips_and_the_refit_no_longer_matches tests/training/test_surrogate_runner.py::test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers -q
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
- **The ceiling census** (§3 — (hit, reachable) counts over the 52 held-out
  ejections: (True, True) 40, (True, False) 6, (False, True) 1, (False, False) 5;
  pointed at the baseline-8 weights it reads the same counts, the known-answer
  control):
  ```
  uv run python -c "from pathlib import Path; from collections import Counter; from training.surrogate import build_meeting_table; from training.surrogate.ballots import BallotSurrogateModel, load_ballot_predictor_artifact; from training.surrogate.fidelity import build_meeting_views, _is_strict_leader; t=build_meeting_table(Path('replays/ml_corpus/9p2i')); m=BallotSurrogateModel(t, predictor=load_ballot_predictor_artifact(Path('training/artifacts/surrogate'))[0]); c=Counter((m.predict(v).ranking[0]==v.ejected, _is_strict_leader(v, v.recon_suspicion, v.ejected)) for v in build_meeting_views(t) if v.seed in set(t.splits.test) and v.is_ejection); print(sorted(c.items()))"
  ```
- **The FO-6 tie-break table** (§3 — per set, the lowest tied tau then the shipped
  head: predicted ejections, ejection meetings predicted SKIP, skip-vs-eject
  accuracy, and whether ranking and calibration are identical):
  ```
  uv run python -c "from pathlib import Path; from tests.training.test_surrogate_fidelity import _LowestTiedTauFo6 as L; from training.surrogate import build_meeting_table, fo6_rebaseline, run_surrogate_fidelity as r; [print(s, *((x.predicted_ejections, x.ejection_predicted_skips, round(x.skip_vs_eject_accuracy, 4), (x.top1, x.top2, x.brier, x.ece) == (y.top1, y.top2, y.brier, y.ece)) for x, y in ((r(t, L, model_name='fo6-physical-logistic'), f), (f, f)))) for s in ('samples/9p2i', 'samples/4p1i', 'ml_corpus/9p2i', 'ml_corpus/4p1i') for t in [build_meeting_table(Path('replays') / s)] for f in [fo6_rebaseline(t)]]"
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
  its verdict — this surrogate **under-ejects** (2 of 52 held-out ejection meetings
  recognized by the decision head on the baseline-9 test split).
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
   that.** As of this erratum's date §3 recorded the cell verbatim as:

   > `| SKIP-vs-eject decision accuracy | **37.5%** (36/96) |`

   (in the `ballot-surrogate.v1` channel table over 30 test games / 96 meetings /
   60 ejections / 36 skips). Read in context that label is exact: it is the surrogate's
   **SKIP-vs-eject channel** — **0.375**, the degenerate all-SKIP constant (0 correct
   ejects, 36 correct skips, `degenerates_to_skip` **True**), and it is the measurement
   that produces this report's honest **NO-GO**. The Task-21.17 re-ground re-measured
   that cell to **39.6% (36/91)** on the baseline-8 corpus; the figures quoted through
   this item are the baseline-6 ones the erratum was written against, and the CHANNEL
   distinction it draws is what carries forward.

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
