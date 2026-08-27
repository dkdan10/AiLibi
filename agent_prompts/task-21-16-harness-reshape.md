# Agent Prompt — 21.16 The harness can say something new: bars that discriminate, a comparator told what it measures, objectives that rank a win above a loss

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.16 — The harness can say something new: bars that discriminate, a comparator told what it measures, objectives that rank a win above a loss, anchored to audits/review-2026-08-26/B/collated-findings.md §B-11 [ADJUSTED, P2] (the live re-fit on `replays/ml_corpus/9p2i` reproduces NO-GO before the re-ground begins; the verifier's two corrections BIND this contract — the "frozen weights" label is inoperative because `run_surrogate_fidelity` re-fits per fold, and axis 1 is saturated in HEADROOM, not in discriminative power), §B-12 [ADJUSTED, P3] (the FO-6 tau plateau IS the fit-side SKIP count; the verifier REFUTED the impact half — FO-6's top-1 is threshold-independent and its tuned head enters no axis of the bar, so this task must not "repair" a gate that does not exist), §B-13 [ADJUSTED, P2] (crew LOSS 12.829131652661065 outranks every crew WIN with ≤7 tasks; the verifier's tighter bound replaces the filing's illustrative one, and the "undisclosed" sub-claim is REFUTED — docs/ml-program.md:32-39 already discloses non-invariance), §B-14 [ADJUSTED, P2] (kill-derived terms 15/22 = 68%, win term 1/22 = 4.5%; the verifier corrected the filing's FSM-agreement prose, which this contract does not repeat), §B-43 [CONFIRMED, P2] (`TRUNCATED_EPISODE_FITNESS` is not below every reachable full-game fitness; no test pins the ordering the comment asserts), §B-26 [CONFIRMED, P2] (the per-tick discarded `random.Random()` seeding; the verifier's state-hash walk over 20 committed replays proves the substitution is chain-identical, and names the `gauss_next` gotcha the fix sketch omits); audits/audit-phase-20-baseline-7.md §10.2 (the routed ML re-ground this task prepares and does not execute; the "FO-6 has flipped three records running … should not be read as a physical baseline" ruling this task implements). Anchors re-verified at HEAD: training/surrogate/fidelity.py:390-402 `_tune_threshold` (ascending scan, strict `correct > best_acc`), :405-414 `_decide`, :416-422 `predict` (ranking sorted by `(-prob, cand)`; tau touches only `ejected`), :726 `model.fit(train_views)` per fold, :748-749 `top1_hits` off `ranking[0]`, :857-877 `fo6_rebaseline`, :892 `GO_TOP1_CEILING_RATIO = 0.75` under its owner-ratified note at :883-891, :895-939 `GoNoGoVerdict`, :942-1021 `decide_go_no_go` (:992-998 the three axes and the conjunction); training/surrogate/ballots.py:833-835 (`fit` REPLACES a pre-installed predictor), :862-866 ("The DECISION is the real tally on the predicted ballots … Never re-implemented, never a tuned threshold"); training/rewards.py:26-45 (the documented falsification), :99-118 `_side_potential`, :120-179 `PotentialShaper`, :182-211 `ShapedReward` (:199-201 the three weights, :203-210 `total`), :214-233 `_impostor_terms`, :236-277 `_crew_terms`, :294-299 `_terminal_reward`, :301-341 `compute_shaped_reward`; training/bakeoff/harness.py:186-194 `ANCHOR_CE_CEILING = 2.0` (FLAGGED, never dropped), :195-199 `ANCHOR_CE_EPSILON = 1e-6`, :201-205 `DEFAULT_ANCHOR_PENALTY_WEIGHT = 1.0`, :207-212 `TRUNCATED_EPISODE_FITNESS = -10.0` with the false invariant in its comment, :486-491 the CE clamp, :911-948 `inner_episode_fitness` (:943-945 the truncation branch and the un-weighted `.total()`); training/crew/scorer.py:961-1000 `crew_inner_episode_fitness` (:997-999 the same shape); engine/rng.py:100 and :114 (`inner = random.Random()` immediately overwritten by `setstate`), engine/tick.py:648 and orchestrator/game.py:1351 (the two call sites); tests/training/test_rewards.py:465-489 (the exact `==` literals both objective findings rest on — `impostor.total() == 22.0` at :476 and `crew.total() == 12.829131652661065` at :489); tests/training/test_surrogate_runner.py:792-819 (`test_go_no_go_reproduces_the_re_measured_no_go_verdict`, which pins `top1_bar == 0.6000000000000001`); training/artifacts/coevo/provenance/harnesses/harness_run_c1.py.txt:47 and harness_run_c2.py.txt:40 (`anchor_weight=4.0` — the largest weight any committed harness uses).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-harness-reshape`
**Depends on:** 21.13
**Section refs:** audits/review-2026-08-26/B/collated-findings.md §B-11 [ADJUSTED, P2] (the live re-fit on `replays/ml_corpus/9p2i` reproduces NO-GO before the re-ground begins; the verifier's two corrections BIND this contract — the "frozen weights" label is inoperative because `run_surrogate_fidelity` re-fits per fold, and axis 1 is saturated in HEADROOM, not in discriminative power), §B-12 [ADJUSTED, P3] (the FO-6 tau plateau IS the fit-side SKIP count; the verifier REFUTED the impact half — FO-6's top-1 is threshold-independent and its tuned head enters no axis of the bar, so this task must not "repair" a gate that does not exist), §B-13 [ADJUSTED, P2] (crew LOSS 12.829131652661065 outranks every crew WIN with ≤7 tasks; the verifier's tighter bound replaces the filing's illustrative one, and the "undisclosed" sub-claim is REFUTED — docs/ml-program.md:32-39 already discloses non-invariance), §B-14 [ADJUSTED, P2] (kill-derived terms 15/22 = 68%, win term 1/22 = 4.5%; the verifier corrected the filing's FSM-agreement prose, which this contract does not repeat), §B-43 [CONFIRMED, P2] (`TRUNCATED_EPISODE_FITNESS` is not below every reachable full-game fitness; no test pins the ordering the comment asserts), §B-26 [CONFIRMED, P2] (the per-tick discarded `random.Random()` seeding; the verifier's state-hash walk over 20 committed replays proves the substitution is chain-identical, and names the `gauss_next` gotcha the fix sketch omits); audits/audit-phase-20-baseline-7.md §10.2 (the routed ML re-ground this task prepares and does not execute; the "FO-6 has flipped three records running … should not be read as a physical baseline" ruling this task implements). Anchors re-verified at HEAD: training/surrogate/fidelity.py:390-402 `_tune_threshold` (ascending scan, strict `correct > best_acc`), :405-414 `_decide`, :416-422 `predict` (ranking sorted by `(-prob, cand)`; tau touches only `ejected`), :726 `model.fit(train_views)` per fold, :748-749 `top1_hits` off `ranking[0]`, :857-877 `fo6_rebaseline`, :892 `GO_TOP1_CEILING_RATIO = 0.75` under its owner-ratified note at :883-891, :895-939 `GoNoGoVerdict`, :942-1021 `decide_go_no_go` (:992-998 the three axes and the conjunction); training/surrogate/ballots.py:833-835 (`fit` REPLACES a pre-installed predictor), :862-866 ("The DECISION is the real tally on the predicted ballots … Never re-implemented, never a tuned threshold"); training/rewards.py:26-45 (the documented falsification), :99-118 `_side_potential`, :120-179 `PotentialShaper`, :182-211 `ShapedReward` (:199-201 the three weights, :203-210 `total`), :214-233 `_impostor_terms`, :236-277 `_crew_terms`, :294-299 `_terminal_reward`, :301-341 `compute_shaped_reward`; training/bakeoff/harness.py:186-194 `ANCHOR_CE_CEILING = 2.0` (FLAGGED, never dropped), :195-199 `ANCHOR_CE_EPSILON = 1e-6`, :201-205 `DEFAULT_ANCHOR_PENALTY_WEIGHT = 1.0`, :207-212 `TRUNCATED_EPISODE_FITNESS = -10.0` with the false invariant in its comment, :486-491 the CE clamp, :911-948 `inner_episode_fitness` (:943-945 the truncation branch and the un-weighted `.total()`); training/crew/scorer.py:961-1000 `crew_inner_episode_fitness` (:997-999 the same shape); engine/rng.py:100 and :114 (`inner = random.Random()` immediately overwritten by `setstate`), engine/tick.py:648 and orchestrator/game.py:1351 (the two call sites); tests/training/test_rewards.py:465-489 (the exact `==` literals both objective findings rest on — `impostor.total() == 22.0` at :476 and `crew.total() == 12.829131652661065` at :489); tests/training/test_surrogate_runner.py:792-819 (`test_go_no_go_reproduces_the_re_measured_no_go_verdict`, which pins `top1_bar == 0.6000000000000001`); training/artifacts/coevo/provenance/harnesses/harness_run_c1.py.txt:47 and harness_run_c2.py.txt:40 (`anchor_weight=4.0` — the largest weight any committed harness uses).
**Complexity:** Integration
**Record impact:** none
**Measurement:** `uv run pytest tests/training/test_rewards.py tests/training/test_bakeoff_harness.py tests/training/test_crew_scorer.py tests/training/test_coevo_rollout.py tests/training/test_surrogate_fidelity.py tests/training/test_surrogate_runner.py tests/engine/test_rng.py -q` green — but that command's default `-m 'not campaign'` filter DESELECTS 61 of these 169 tests, the whole campaign halves of `test_crew_scorer.py`, `test_coevo_rollout.py` and `test_surrogate_fidelity.py` (re-measured at HEAD: `108/169 tests collected (61 deselected)`), so the same seven files are ALSO run under `-m "campaign or not campaign"` for all 169 and read against exactly ONE expected failure — `tests/training/test_surrogate_fidelity.py::test_fo6_rebaseline_collapses_to_always_skip_on_the_big_set`, one of the eight §10.2 residuals below and Task 21.17's to re-ground — with every other test passing; `uv run pytest -m campaign -q` shows EXACTLY the eight residual §10.2 failures Task 21.17 owns and no others — `tests/training/test_anchor_study.py` 1, `test_coevo_driver.py` 2, `test_composed_runner.py` 4, `test_surrogate_fidelity.py` 1 (re-measured at HEAD `94c09fbb`, the 21.13 merge: `8 failed, 310 passed, 5327 deselected in 1312.77s`, exit 1 — unchanged at `99459dd7`, whose only delta is 21.12's frontend-only merge; the whole tier read `9 failed, 308 passed` at close HEAD per audits/audit-phase-20-close.md F1, and Task 21.13 removed the ninth, which is exactly why this task sits behind it) — with the PR recording the exit code, the failure list verbatim and the count, and ZERO new failures beyond those eight; `bash scripts/verify_samples.sh` reports 100/100 reconstructing byte-identically (the rng substitution's chain proof); the PR Summary quotes the before/after of every cell this task moves — the split verdict on the current corpus, the FO-6 tau curve with its tuned tau, the re-derived reward literals, and the measured engine tick cost.

The ML re-ground (Task 21.17) is scoped by audits/audit-phase-20-baseline-7.md §10.2 as a
re-fit, a re-stamp and a re-publication. Track B measured what that scope produces, on the
exact corpus the re-fit targets, and the answer is already known: NO-GO. On
`replays/ml_corpus/9p2i` a genuine held-out re-fit of the ballot surrogate scores top-1
**0.8000 against a measured honest ceiling of 0.8000** (44 of 55 ejection meetings — the
ceiling's own decomposition is flag_present 45, proximity_present 48, belief_lead 43,
reachable 44, voice_driven_share 0.2), beats the FO-6 re-baseline **0.4182 (23/55)**, and
fails axis 3 at **0.3908 against an always-eject constant of 0.6322** because the decision
channel is the real tally over predicted ballots and the predictor casts SKIP on **85 of 87**
meetings. Re-fitting against that bar is a bookkeeping exercise with a pre-known verdict.
This task is the reshape that has to land BEFORE the re-fit, so the re-fit can return an
answer nobody could have written down in advance.

Two of the register's corrections shape what "reshape" is allowed to mean here. First, the
bar's axis 1 is **not** dead: the floor is 0.75 × ceiling = 0.6000 and a weaker candidate
still fails it, so what is saturated is the surrogate's headroom, not the axis. Second, and
decisively, **the verdict's consequence mapping must not get easier**. Retiring the failing
axis 3 from the conjunction would flip today's NO-GO to GO and promote the surrogate from
diagnostic to training-time runner on no new evidence at all — the purest Goodhart move
available in this repo. So the reshape SPLITS rather than loosens: the verdict publishes a
`ranking_verdict` (axes 1 and 2 — the claim the surrogate actually supports) and a
`decision_verdict` (axis 3, unchanged constant, unchanged strictness), and the composed
`verdict` that drives `training_time_runner` / `surrogate_role` stays their conjunction. The
committed pre-registered mapping in `GoNoGoVerdict`'s docstring — NO-GO ⇒ fallback (a), the
fake-provider MeetingManager stays the runner — does not move. What is new is that the
harness can now say "the ranking instrument cleared its bar and the decision channel did
not" instead of one flat NO-GO that reads as a broken model, and it can say it with a
reachability diagnostic beside it: how many meetings' predicted plurality confidence clears
`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD` at all. That number tells 21.17
whether the decision channel is reachable before anyone spends a fit on it. Neither B-11's
option (a) nor (b) — re-targeting or re-calibrating the predictor — is taken here: those are
model changes, and a model change made in the same breath as a bar change is untestable.

The comparator gets told what it measures. `Fo6Logistic._tune_threshold` maximises
exact-target accuracy over ALL meetings including SKIPs, so across tau ∈ [0.40, 0.95] its
score is **flat at 120 — exactly the fit-side SKIP count** (345 fit-side meetings, 120 skip,
225 eject); the winning tau=0.20 beats that trivial always-SKIP constant by **7 meetings
(2.0%)**, and the strict ascending scan breaks the 0.20/0.25 tie toward the LOWER tau, i.e.
toward the all-EJECT pole. §10.2 already ruled on the consequence — the head "has now flipped
three records running (SKIP → all-EJECT → SKIP), which says it tracks the meeting mix rather
than the physics and should not be read as a physical baseline" — and this task executes that
ruling. Note carefully what is NOT wrong: the verifier refuted the filing's impact claim.
FO-6's top-1 comes from `ranking[0]` (fidelity.py:748) and `ranking` is a probability sort
that never sees tau (:416-422), so **axis 2 is threshold-independent and the tuned head enters
no axis of the bar**. There is no gate to repair. The defect is a published diagnostic
presented as a physical baseline, so the fix is presentational and exact: keep FO-6 as the
ranking floor it validly is, demote its decision head to a declared meeting-mix tracker
published beside the population's two trivial constants (`always_eject_baseline` and the new
`always_skip_baseline`), publish the tau curve so a 7-of-345 margin is visible, and document
the tie-break toward the HIGHER (more conservative) tau instead of silently taking the
all-EJECT end.

The objectives are the half that has been declared and never priced. `training/rewards.py:26-45`
records at length that the shaping is not policy-invariant — "the prior claim here ('so it
cannot change the optimal policy') was mathematically FALSE … DOCUMENTED, NOT REPAIRED. The
ML program is frozen" — and docs/ml-program.md:32-39 discloses it to readers. What no
document states is the consequence. Because `crew_inner_episode_fitness` calls
`compute_shaped_reward(rollout, "CREWMATE").total()` with no weights (scorer.py:998, defaults
1/1/1), the γ=1 shaping sum is the raw unnormalised completed-task COUNT, and the repo's own
pinned real-engine literals give a crew **LOSS scoring 12.829131652661065, of which 12.0
(93.5%) is shaping**. The bound is rigorous, not illustrative: a crew WIN with k of 14 tasks
scores at most 5 + k + k/14, so every crew WIN with k ≤ 7 (k=7 → 12.500) ranks strictly below
that recorded LOSS. On the impostor side the pinned decomposition is terminal 1.0 + dense
{kills 5.0, unwitnessed_kills 5.0, survival 1.0, meetings_survived 5.0} + shaping 5.0 = 22.0:
kill volume is paid twice unconditionally and a third time when unwitnessed, **15 of 22 (68%)**,
while the win term is **1 of 22 (4.5%)**. Three of the four recorded bake-off arms sit at or
near the win-rate ceiling (1.0 / 1.0 / 0.9333) with a fitness spread of 18.198 / 18.671 /
19.066 — so that spread is a kill-volume ordering and cannot be read as "better at winning".
The re-ground's whole point is to demonstrate something on these arms; an objective that
cannot discriminate them makes that impossible before the first rollout.

The repair is three-part and structural. The weight seam already exists at module level
(`compute_shaped_reward` takes all three weights, `ShapedReward` carries them) and is simply
never forwarded — so the two fitness functions gain an explicit objective profile instead of
a hard-wired 1/1/1. Φ becomes a bounded fraction of the side's win condition (completed
tasks / total tasks; resolved kills / initial crew), which preserves the telescoping identity
exactly — a per-episode constant scale factors straight through `Φ(terminal) − Φ(initial)` —
while stopping the shaping from re-paying `task_progress` fourteen times over. The impostor's
duplicate raw `kills` term is deleted (the shaping already pays exactly the kill count),
`unwitnessed_kills` becomes the bounded stealth SHARE it was always meant to be, and
`meetings_survived` becomes a share of meetings held. With every dense term and the shaping in
[0, 1], the terminal weight can be DERIVED rather than guessed: at `bounded_term_count + 1`
the worst WIN outranks the best LOSS by `bounded_term_count + 2`, and that ordering is pinned
by a test computed from the declared bounds rather than asserted in a comment. Which is
exactly the defect B-43 names one constant away: `TRUNCATED_EPISODE_FITNESS = -10.0` says in
its own comment that it sits "well below any reachable full-game fitness", and it does not —
the anchor CE is clamped at −log(1e-6) = 13.815510557964274 nats and subtracted at weight 1.0,
so a complete episode can reach −14.8155. Nothing pins the ordering; the two tests that
name the constant assert only that the sentinel is returned — three assertions between them,
tests/training/test_crew_scorer.py:617 and tests/training/test_coevo_rollout.py:247-248. Zero realized exposure (max
recorded `anchor_cross_entropy` is 2.0157, and `anchor_offmenu_decisions` is 0 on every
committed row) is not safety here, because off-menu is a step function: a re-ground with a
moved intent vocabulary jumps straight to the clamp. So the constant is derived from the
reachable floor at a documented maximum anchor weight — 4.0, the value the committed C1/C2
campaign harnesses actually use — and the functions refuse a weight above it rather than
silently re-opening the inversion.

Last and smallest, the change that pays for the re-fit's compute. `EngineRng.from_state`
constructs `random.Random()` on both branches (engine/rng.py:100, :114) — seeding a 624-word
Mersenne state it discards one line later with `setstate` — once per tick (engine/tick.py:648)
and once per meeting (orchestrator/game.py:1351). `random.Random.__new__(random.Random)` costs
0.118 µs against 17.99 µs and produces provably identical draws; the verifier measured the
discarded seeding at 31% of the FULL restore and 66% of the TRAINING_FAST restore, an
end-to-end engine gain of 10–20% depending on harness, and re-walked 20 committed
`replays/ml_corpus/9p2i` replays with tick, meeting-pre and meeting-post hash verification all
on: 20/20 clean. It is behaviour-identical and it multiplies into every LLM-free ES /
MAP-Elites rollout the re-ground funds. B-26's second half — the `MappingProxyType`
short-circuit in `engine/world.py::_readonly_mapping` — is deliberately NOT taken here: it is
an independent engine-core micro-optimisation with its own safety argument, it is not on the
re-fit's critical path, and it stays open residue for the phase close's ledger.

Nothing in this task re-fits, re-stamps or re-runs anything. No committed replay byte, no
rendered prompt byte and no detector output moves. What moves is a set of unit-level pins,
and each one is re-derived on the CURRENT committed corpus here and re-derived again on the
21.15 bytes by 21.17 — the standing "pins re-derive, targets never move" shape. Baseline 7 is
canon by explicit owner override of a FINDING verdict, so the bar this task reshapes is being
carried onto a substrate whose adopting record did not clear its bars; that is precisely why
the successor bar must be able to fail, and why the reshape is committed BEFORE the corpus it
will judge exists.

**Files in scope:**
- training/rewards.py; (the bounded Φ with its required per-episode scale, the objective-weights profile and the derived terminal weights, the re-shaped side terms, the objective id, the docstring truth-up)
- training/bakeoff/harness.py; (the weight seam on `inner_episode_fitness`, `MAX_ANCHOR_PENALTY_WEIGHT`, the derived `MIN_FULL_GAME_FITNESS` and `TRUNCATED_EPISODE_FITNESS`, the anchor-weight refusal)
- training/crew/scorer.py; (the identical seam and refusal on `crew_inner_episode_fitness` — call-site and signature only; the crew campaign machinery above it is untouched)
- training/surrogate/fidelity.py; (the split verdict + `bar_id` + the reachability and ceiling-gap cells; the FO-6 head demoted to a mix tracker with its tau curve, the higher-tau tie-break, `always_skip_baseline`; the docstring correction that `run_surrogate_fidelity` re-fits per fold)
- experiments/lab/torch_probe/entrant.py; (constructs its own `PotentialShaper` and asserts the per-decision sum identity against `compute_shaped_reward` — a defaulted scale would break that identity silently, so the scale is required and this call site moves in the same commit)
- training/surrogate/ballots.py; (ONE additive line in `predict` at :860-878 — it sets the new `MeetingPrediction.plurality_confidence` from the tally it already runs; no feature, no fit path, no dropped-row predicate and no threshold moves, and Task 21.8 owns everything else in this file)
- engine/rng.py; (BLOCK E's two lines, :100 and :114 — `random.Random.__new__(random.Random)` before each `setstate`, with the one-line reason above the first)
- docs/ml-program.md; (ONLY the reward/shaping paragraph at :32-39 and the fitness clause at :61-62, re-stated for the new objective, plus one clause recording that the committed arm table was produced under the previous objective — the arm table's rows and every published number are untouched)
- tests/training/test_rewards.py; (the re-derived literals, the win-outranks-loss ordering property, the telescoping identity under the scale)
- tests/training/test_bakeoff_harness.py; (the seam, the derived floor and its planted perturbation, the anchor-weight refusal, the objective-id fence over the committed results rows)
- tests/training/test_crew_scorer.py; (the crew seam and refusal; the truncation sentinel pin re-derived)
- tests/training/test_coevo_rollout.py; (the two sentinel pins and the `anchor_weight=0.0` decompositions re-derived)
- tests/training/test_surrogate_fidelity.py; (the FO-6 census pins, the tau curve, the tie-break, `always_skip_baseline` — and note `test_fo6_rebaseline_collapses_to_always_skip_on_the_big_set` in this file IS one of the eight §10.2 residuals: its `top1 == 20/101` assertion at :406 is Task 21.17's to re-ground and must STILL FAIL after the decision-census pins around it are re-derived, or the eight silently become seven)
- tests/training/test_surrogate_runner.py; (the split verdict pins, the re-fit-not-frozen control, the reachability cell)
- tests/engine/test_rng.py; (draw-equality, `getstate` equality, and the `gauss_next` gotcha)

**Files NOT in scope:**
- engine/world.py (B-26's `MappingProxyType` short-circuit; deliberately deferred — see the rationale's last paragraph, and the PR states it as open residue rather than silently dropping it)
- training/surrogate/dataset.py, training/conviction/, and every other line of training/surrogate/ballots.py (Task 21.8 owns the fit-hygiene half — marker kinds, the memory-timing fix, the conviction precision guard, the fingerprints and the verdict artifact; this task changes the BAR, never the fit or its rows)
- replays/ and training/artifacts/ (no re-fit, no re-stamp, no artifact rewritten: §10.2's re-ground is Task 21.17's)
- training/reports/*.jsonl and training/reports/*.md (the recorded arms are provenance of a run under the previous objective and stay exactly as recorded; re-publication is 21.17's)
- training/bakeoff/{policy_es,utility_es,map_elites,goodhart}.py, training/coevo/{driver,rollout}.py (pure consumers of the two fitness functions; the seam is keyword-only with defaults so they compile unchanged — grep-verified and re-run under `-m campaign`, not edited)
- eval/watchability.py (B-47's bake-off-lag note — at `:959-964` since the 21.7 merge shifted the file — and `BAKEOFF_BASELINE_ID` itself both move at Task 21.17; this task edits no line of this file — the merged floor block is Task 21.7's work and `_BASELINE_SUPPLY_FLOORS` / `_DEFAULT_BASELINE_ID` are Task 21.15's)
- meetings/ and agents/ (`DEFAULT_SKIP_CONFIDENCE_THRESHOLD` is read, never changed: re-calibrating the ballot confidences is a model change this task explicitly declines)

**Definition of done:**
- [ ] `GoNoGoVerdict` gains `ranking_verdict` (axes 1 ∧ 2), `decision_verdict` (axis 3, the unchanged `skip_vs_eject_accuracy > always_eject_baseline` comparison) and `bar_id`, while `verdict`, `training_time_runner` and `surrogate_role` stay the conjunction of the two and its pre-committed fallback mapping — a test asserts that no input which produced NO-GO under the previous bar produces GO under this one, so the reshape provably cannot manufacture a promotion.
- [ ] The verdict publishes two new measured cells and a decomposition: `top1_ceiling_gap` (= `ceiling_top1 − surrogate_top1`, 0.0 on the current corpus and named as at-the-ceiling rather than above-a-floor), and `decision_reachability` — the count and share of scored meetings whose predicted plurality ballot confidence clears `DEFAULT_SKIP_CONFIDENCE_THRESHOLD`, meaning the tally's OWN gate quantity (meetings/voting.py:145-191 rule 4: the MAX confidence among the ballots naming the plurality target) and NOT `MeetingPrediction.ejection_prob`, which is a mean of per-voter target-probability mass and a different number; `MeetingPrediction` therefore gains one additive optional `plurality_confidence: float | None` defaulting to `None` for every ballot-free model, FO-6 included, and `BallotSurrogateModel.predict` populates it — with the honest ceiling's channel counts carried onto the verdict object so a reader sees WHY the ceiling sits where it does.
- [ ] The bar's own re-derivation is pinned on the current committed corpus in `tests/training/test_surrogate_runner.py`: ranking GO, decision NO-GO, composed NO-GO, `surrogate_role == "diagnostic-only"`, `top1_bar == 0.6000000000000001`, `top1_ceiling_gap == 0.0` — each value re-measured, none carried over from the previous bar by assumption.
- [ ] The "frozen weights" reading is closed at the source: `run_surrogate_fidelity`'s docstring states that it calls `model.fit(train_views)` on every fold and that `BallotSurrogateModel.fit` REPLACES a pre-installed predictor, and a test reproduces the verifier's own control — a factory WITH an artifact-loaded predictor and one WITHOUT produce byte-identical reports on the same table.
- [ ] FO-6's decision head is demoted, not deleted: `fo6_rebaseline`'s report labels the head a meeting-mix tracker, publishes `always_skip_baseline` (= skip meetings / meetings scored) beside `always_eject_baseline`, and carries the full tau → score curve; `_tune_threshold` breaks ties toward the HIGHER tau with the reason in one line of prose, and a test pins that on the current corpus the plateau equals the fit-side SKIP count (120 of 345) and the tuned tau's margin over it is 7 meetings.
- [ ] Axis 2 is proven untouched by that demotion: a test asserts FO-6's `top1` is identical under both tie-breaks (it is computed from `ranking[0]`, which never sees tau), so the comparator floor the bar reads did not move when its decision census did.
- [ ] Φ is bounded and the telescoping identity survives: `PotentialShaper` takes a REQUIRED keyword-only `scale`, `potential_scale(rollout, side)` returns the side's episode constant (crew: total task instances; impostor: initial crew count), and the existing telescoping test still holds exactly with `shaping_sum == (Φ_terminal − Φ_initial)` — asserted with `==`, not `approx`, and with a second case proving the sum lies in [0, 1].
- [ ] The impostor objective stops paying kills twice: the raw `kills` dense term is removed, `unwitnessed_kills` becomes the bounded share `unwitnessed / max(1, kills)`, `meetings_survived` becomes a share of meetings held, and `tests/training/test_rewards.py`'s pinned real-engine decomposition is re-derived with `==` literals — the PR quotes the old 22.0 total and the new one side by side.
- [ ] The crew objective stops re-paying task completion: `correct_reports` becomes a share of `num_impostors`, every crew dense term is in [0, 1], and the recorded seed-0 crew LOSS no longer outranks a WIN — the PR quotes 12.829131652661065 and its replacement.
- [ ] The ordering invariant is a gate, not a comment: a test derives each side's worst reachable WIN total and best reachable LOSS total from the declared per-term bounds and asserts strict dominance, and it FAILS when a term's bound is perturbed (add an unbounded term in a fixture and watch it bite) — the planted case ships with it.
- [ ] The weight seam is real: `inner_episode_fitness` and `crew_inner_episode_fitness` take a keyword-only objective-weights profile defaulting to their side's derived profile and forward it to `compute_shaped_reward`; a test expresses a non-default profile through the parameter alone, with no edit to either function, and pins that the default profile reproduces the function's own composed value.
- [ ] `TRUNCATED_EPISODE_FITNESS` is derived, not asserted: `MIN_FULL_GAME_FITNESS` is computed from the minimum terminal total and `MAX_ANCHOR_PENALTY_WEIGHT × −log(ANCHOR_CE_EPSILON)`, the sentinel sits strictly below it, the comment at :207-212 is rewritten to state the derivation instead of the invariant it used to claim, and a test asserts the ordering for BOTH sides — the exact pin B-43 records as absent.
- [ ] `MAX_ANCHOR_PENALTY_WEIGHT = 4.0` is documented against the committed C1/C2 campaign harnesses that use it, and both fitness functions raise `ValueError` naming the constant on a larger (or negative) `anchor_weight` rather than silently re-opening the inversion; a planted case at 4.0001 pins the refusal and a fresh grep in the PR shows no committed config or harness exceeds it.
- [ ] `training.rewards.FITNESS_OBJECTIVE_ID` names the objective the live code computes, and a test over `training/reports/results-*.jsonl` asserts every committed row is NOT stamped with it (rows carry no objective id, so they read as the previous objective) — the fence that stops a re-ground comparing a new fitness against numbers produced by a different one.
- [ ] `engine/rng.py`'s two `random.Random()` constructions become `random.Random.__new__(random.Random)` before their `setstate`, and `tests/engine/test_rng.py` pins all three properties the verifier named: 1000 identical draws from a FULL-restored and a `__new__`-restored generator, `getstate()` equality after those draws, and that `getstate()` on a bare `__new__` object raises `AttributeError` (no `gauss_next`) — so the "safe only because both call sites setstate immediately" argument is pinned rather than trusted.
- [ ] `bash scripts/verify_samples.sh` reports all 100 committed samples reconstructing byte-identically, and `uv run pytest -m campaign -q` is run with its exit code and full failure list pasted into the PR. Green is NOT the bar and must not be attempted here: the tier still exits 1 on the eight residual §10.2 failures — `tests/training/test_anchor_study.py` 1, `test_coevo_driver.py` 2, `test_composed_runner.py` 4, `test_surrogate_fidelity.py` 1 — which are Task 21.17's to re-ground and which this task is upstream of. The bar is that those eight are the ONLY failures: the PR names each one, states the count, and confirms zero new failures. A ninth failure means this task moved a campaign pin and the PR says which and why (every legitimate move here is a unit-level re-derivation, never a re-fit). The PR also records the measured per-tick engine cost before and after.
- [ ] `docs/ml-program.md`'s reward paragraph is true at HEAD: the dense terms named match `_impostor_terms`/`_crew_terms` as reshaped, the shaping is described as a bounded fraction, the non-invariance disclosure is KEPT (it is still true — Φ remains trajectory-dependent, now at 1/tasks_total per task), and one clause records that the published arm table was produced under the previous objective and is re-published by the ML re-ground; `uv run python scripts/check_doc_facts.py` passes and no arm-table number is edited.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

BLOCK A — the bar (training/surrogate/fidelity.py). Do this first and alone; it touches no
reward code. In `decide_go_no_go` (:942) compute the three axis booleans exactly as today
(:992-998), then assemble `ranking_verdict = meets_ceiling_bar and beats_prior_baseline`,
`decision_verdict = beats_always_eject`, and leave `is_go` as their conjunction so the
`training_time_runner` / `surrogate_role` mapping at :1017-1020 is untouched. `bar_id` is a
module `Final[str]` beside `GO_TOP1_CEILING_RATIO` (:892) — the ratio itself does not move,
and the docstring at :896-915 gains the split's reading, not a new bar. `top1_ceiling_gap` is
arithmetic on fields already present. `decision_reachability` is not: the per-meeting plurality
confidence the tally gates on is nowhere on `MeetingPrediction` today — `ejection_prob` (:125)
is a mean of per-voter target-probability mass, while the tally's rule is the MAX confidence
among the ballots naming the plurality target (meetings/voting.py:176-186). So add an optional
`plurality_confidence: float | None = None` to `MeetingPrediction` (:113-125; `_validate_prediction`
at :128-163 needs no new rule and `Fo6Logistic.predict` at :416-422 keeps returning `None`), set
it in `BallotSurrogateModel.predict` (ballots.py:860-878) from the ballots it already tallies,
and accumulate it in `run_surrogate_fidelity`'s existing prediction walk (:727-758) onto
`SurrogateFidelityReport` rather than re-running the model — a second pass over predictions
would drift from the first the moment folds change.

BLOCK B — the comparator (same file, separate commit). `_tune_threshold` (:390-402): keep the
exact-target objective and the tau grid; record `(tau, correct)` pairs as you scan and change
the selection to `correct >= best_acc` so the ascending scan lands on the HIGHEST tied tau,
with one line of prose saying why (the higher tau is the conservative pole; the lower one is
all-EJECT). Carry the curve onto the report through `fo6_rebaseline` (:857) so it is published
where the census already is. `always_skip_baseline` is `skip_meetings / meetings_scored` over
the same scored population — derive it in `run_surrogate_fidelity` beside
`always_eject_baseline`, never in the caller. Expect the FO-6 decision census to move (tuned
tau 0.20 → 0.25 on the current corpus) and `top1` NOT to move; that asymmetry is the test in
the DoD, and it is the whole content of the verifier's refutation.

BLOCK C — Φ and the terms (training/rewards.py). `_side_potential` (:99) gains a `scale`
argument and divides; `PotentialShaper.__init__` (:133) takes `scale` keyword-only and
REQUIRED — no default, deliberately. Note what will NOT catch a missed update:
`experiments/lab/torch_probe/` is mypy-EXCLUDED (pyproject.toml:68), so `uv run mypy .` never
reads `entrant.py:550` and the required parameter buys a loud `TypeError` the next time the
probe runs, not a gate. That is precisely why the call site is IN SCOPE and moves in the same
commit; a defaulted scale would instead let it silently diverge from `compute_shaped_reward`'s
own shaper and break the per-decision sum identity its docstring (:422-424) asserts. Add
`potential_scale(rollout, side)` and call it from both places; in `entrant.py` move the shaper
construction inside the per-episode loop where the rollout is in hand. `_impostor_terms`
(:214) and `_crew_terms` (:236) already hold every denominator they need
(`rollout.num_players`, `rollout.num_impostors`, `len(rollout.meetings)`,
`last.tasks_total`); guard each with `max(1, …)` in the module's existing style (:231, :239, :242).
Do NOT touch `_terminal_reward` (:294) — it stays exactly ±1.0 and the dominance comes from
the weight, which is where an objective's shape belongs.

BLOCK D — the weights and the floor. `ObjectiveWeights` is a frozen dataclass in
`training/rewards.py` beside `ShapedReward`, with `DEFAULT_OBJECTIVE_WEIGHTS` a mapping from
side to profile; derive each side's `terminal_weight` from its own term count
(`len(dense_terms) + 1 + 1`) in a module-level function so the ordering test can call the same
derivation the constant came from — a hand-typed 5 and 6 would make the gate tautological.
`inner_episode_fitness` (harness.py:911) and `crew_inner_episode_fitness` (scorer.py:961) gain
`weights: ObjectiveWeights | None = None` and forward it; the truncation branch (:943, :997)
returns before any weighting and stays first. `MIN_FULL_GAME_FITNESS` and the derived
`TRUNCATED_EPISODE_FITNESS` live at harness.py:207 where the constant is now, computed from
`ANCHOR_CE_EPSILON` (:199) with `math.log` — and crew/scorer.py keeps importing the symbol
(:143) rather than re-deriving it.

BLOCK E — the rng (engine/rng.py, its own commit). Two lines, :100 and :114. Write the three
tests first and watch the third one fail in the interesting way: `getstate()` on
`random.Random.__new__(random.Random)` raises `AttributeError` because `gauss_next` is unset,
which is exactly why the substitution is safe ONLY where `setstate` follows immediately — put
that sentence in the code, one line, above the first call. Then re-walk the committed corpus
with hash verification on before you trust the microbenchmark: `scripts/verify_samples.sh` is
the committed gate, and `eval/replay_walk.py` with tick and meeting hash verification is the
finer instrument the verifier used over `replays/ml_corpus/9p2i`.

BLOCK F — before pushing. `uv run pytest -m campaign` is not optional here: the default filter
is `-m 'not campaign'`, and every consumer of the two fitness functions
(`training/bakeoff/{policy_es,utility_es,map_elites,goodhart}.py`,
`training/coevo/{driver,rollout}.py`) lives behind that marker. Read the run against the
EIGHT-failure baseline, not against green: the tier has been red since before the Phase-20
close, `audits/audit-phase-20-close.md` §F1 routed those failures to the ML re-ground, and
Task 21.17 — which depends on this one — is what closes them. A green tier is not reachable
here, and reaching for it means doing 21.17's re-fit early, out of scope and before its own
bars exist. So diff the failure LIST rather than the exit code: if a ninth appears, a campaign
pin moved because the objective changed — record which one and by how much in the PR; do not
re-pin a value you cannot explain, and do not re-fit anything to make one green.

## Public types this task introduces
- `training.rewards.ObjectiveWeights`
- `training.rewards.DEFAULT_OBJECTIVE_WEIGHTS`
- `training.rewards.FITNESS_OBJECTIVE_ID`
- `training.rewards.potential_scale`
- `training.bakeoff.harness.MAX_ANCHOR_PENALTY_WEIGHT`
- `training.bakeoff.harness.MIN_FULL_GAME_FITNESS`
- `training.surrogate.fidelity.GO_BAR_ID`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Risk 1 — a reshaped bar that manufactures a GO. This is the one failure mode that would
discredit the entire re-ground, and the contract is built against it: axis 3's comparison, its
constant and its strictness are unchanged, and the composed `verdict` remains the conjunction
of all three axes. The DoD's "no NO-GO input becomes GO" test is the gate. If implementing the
split tempts you to drop axis 3 from the conjunction because "the surrogate is a ranking
instrument now", stop and open a question in the PR — that is a pre-registration change and it
belongs to an owner, not to this task.

Risk 2 — the objective change invalidates recorded comparisons silently. Every committed
fitness number in `training/reports/` was produced under the previous objective; a re-ground
that compares a new arm's fitness against those rows would be comparing two different
questions. `FITNESS_OBJECTIVE_ID` plus the results-row fence is the mechanism, and the rows
themselves are NOT rewritten — they are correct provenance of a real run. The PR must state
this in one sentence and 21.17 must re-publish from its own run, never by editing a recorded
row.

Risk 3 — the required `scale` breaks a consumer outside `training/`.
`experiments/lab/torch_probe/entrant.py` is the only site that builds its own
`PotentialShaper` and asserts a sum identity against `compute_shaped_reward`; it is in scope
for exactly that reason. Requiring the parameter is the point — a default would let the
identity rot silently, which is the failure this repo's "no silent fallbacks" rule exists to
prevent. Re-grep before pushing; if a second such site appears, name it in the PR rather than
widening scope quietly.

Risk 4 — the anchor-weight refusal breaks a campaign path. The committed C1/C2 provenance
harnesses run at `anchor_weight=4.0`, which is why the cap is 4.0 and not
`DEFAULT_ANCHOR_PENALTY_WEIGHT`. Run `-m campaign` and grep the coevo config surface
(`training/coevo/driver.py:1611-1612`, `:1931-1932`, `:2089-2090`) before assuming no caller
exceeds it; a refusal that fires inside a multi-hour campaign is worse than the inversion it
prevents.

Risk 5 — the rng substitution reads as a determinism change. It is not, and the proof must be
in the PR rather than in the reasoning: 100/100 samples reconstructing byte-identically plus
the hash-verified corpus walk. Note also that recorded paths see roughly half the headline
percentage (`_state_hash` costs about as much as the tick itself); quote the measurement you
took, not the register's, and do not claim a rollout-budget number this task did not measure.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-harness-reshape` with a title like `task 21.16: the harness can say something new: bars that discriminate, a comparator told what it measures, objectives that rank a win above a loss`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-26/B/collated-findings.md §B-11 [ADJUSTED, P2] (the live re-fit on `replays/ml_corpus/9p2i` reproduces NO-GO before the re-ground begins; the verifier's two corrections BIND this contract — the "frozen weights" label is inoperative because `run_surrogate_fidelity` re-fits per fold, and axis 1 is saturated in HEADROOM, not in discriminative power), §B-12 [ADJUSTED, P3] (the FO-6 tau plateau IS the fit-side SKIP count; the verifier REFUTED the impact half — FO-6's top-1 is threshold-independent and its tuned head enters no axis of the bar, so this task must not "repair" a gate that does not exist), §B-13 [ADJUSTED, P2] (crew LOSS 12.829131652661065 outranks every crew WIN with ≤7 tasks; the verifier's tighter bound replaces the filing's illustrative one, and the "undisclosed" sub-claim is REFUTED — docs/ml-program.md:32-39 already discloses non-invariance), §B-14 [ADJUSTED, P2] (kill-derived terms 15/22 = 68%, win term 1/22 = 4.5%; the verifier corrected the filing's FSM-agreement prose, which this contract does not repeat), §B-43 [CONFIRMED, P2] (`TRUNCATED_EPISODE_FITNESS` is not below every reachable full-game fitness; no test pins the ordering the comment asserts), §B-26 [CONFIRMED, P2] (the per-tick discarded `random.Random()` seeding; the verifier's state-hash walk over 20 committed replays proves the substitution is chain-identical, and names the `gauss_next` gotcha the fix sketch omits); audits/audit-phase-20-baseline-7.md §10.2 (the routed ML re-ground this task prepares and does not execute; the "FO-6 has flipped three records running … should not be read as a physical baseline" ruling this task implements). Anchors re-verified at HEAD: training/surrogate/fidelity.py:390-402 `_tune_threshold` (ascending scan, strict `correct > best_acc`), :405-414 `_decide`, :416-422 `predict` (ranking sorted by `(-prob, cand)`; tau touches only `ejected`), :726 `model.fit(train_views)` per fold, :748-749 `top1_hits` off `ranking[0]`, :857-877 `fo6_rebaseline`, :892 `GO_TOP1_CEILING_RATIO = 0.75` under its owner-ratified note at :883-891, :895-939 `GoNoGoVerdict`, :942-1021 `decide_go_no_go` (:992-998 the three axes and the conjunction); training/surrogate/ballots.py:833-835 (`fit` REPLACES a pre-installed predictor), :862-866 ("The DECISION is the real tally on the predicted ballots … Never re-implemented, never a tuned threshold"); training/rewards.py:26-45 (the documented falsification), :99-118 `_side_potential`, :120-179 `PotentialShaper`, :182-211 `ShapedReward` (:199-201 the three weights, :203-210 `total`), :214-233 `_impostor_terms`, :236-277 `_crew_terms`, :294-299 `_terminal_reward`, :301-341 `compute_shaped_reward`; training/bakeoff/harness.py:186-194 `ANCHOR_CE_CEILING = 2.0` (FLAGGED, never dropped), :195-199 `ANCHOR_CE_EPSILON = 1e-6`, :201-205 `DEFAULT_ANCHOR_PENALTY_WEIGHT = 1.0`, :207-212 `TRUNCATED_EPISODE_FITNESS = -10.0` with the false invariant in its comment, :486-491 the CE clamp, :911-948 `inner_episode_fitness` (:943-945 the truncation branch and the un-weighted `.total()`); training/crew/scorer.py:961-1000 `crew_inner_episode_fitness` (:997-999 the same shape); engine/rng.py:100 and :114 (`inner = random.Random()` immediately overwritten by `setstate`), engine/tick.py:648 and orchestrator/game.py:1351 (the two call sites); tests/training/test_rewards.py:465-489 (the exact `==` literals both objective findings rest on — `impostor.total() == 22.0` at :476 and `crew.total() == 12.829131652661065` at :489); tests/training/test_surrogate_runner.py:792-819 (`test_go_no_go_reproduces_the_re_measured_no_go_verdict`, which pins `top1_bar == 0.6000000000000001`); training/artifacts/coevo/provenance/harnesses/harness_run_c1.py.txt:47 and harness_run_c2.py.txt:40 (`anchor_weight=4.0` — the largest weight any committed harness uses).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
