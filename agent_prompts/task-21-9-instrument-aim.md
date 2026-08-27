# Agent Prompt — 21.9 Two instruments re-aimed: calibration without the firewall artifact, a dialect gauge that overlaps the dialect

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.9 — Two instruments re-aimed: calibration without the firewall artifact, a dialect gauge that overlaps the dialect, anchored to A-8 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md:936-1026 (the pooled and split ECEs reproduced to 4dp against the committed cells, the 708-accusation / 0-hit census, the measured mean confidence 0.673, and the verifier note's two BINDING corrections: the mid-range inversion is roughly a FIFTH the impostor block and not half, and the pooled accusation base rate is 0.500 on ml_corpus/9p2i, not the 0.22 chance prior the finder quoted); A-9 [CONFIRMED, P1] — :1028-1136 (the two-word net at :1040, the four committed cells, the 0/39 overlap reproduced independently, the free_text hole, and the verifier's corrections: the unmeasured spoken surface is 39 utterances rather than 28 because 11 further hits sit on `claims[].reason`, and the finding reads as a COVERAGE GAP — no shipped cell computes a wrong number); A-6 [CONFIRMED, P1] — :693-838, the net this task must overlap (78 utterances across 44 of 300 games; by surface ballot_rationale 39 / free_text 28 / claim_reason 11; 17 in-fiction uses of "engine" excluded BY HAND; the verifier's own census of the 78 and its "exactly ONE in-fiction survivor" note); B-9 [ADJUSTED, P1] — audits/review-2026-08-26/B/collated-findings.md:706-746 (the site list, the saw_player 2722 / saw_move 1136 / saw_vent 363 channel census, the 336→373 attempted / 239→249 converted delta, and the verifier's BINDING scope correction that `has_observation` / `observation_backed_any` is a declared frozen parity bit whose widening is the regression the 16.14 pin exists to catch); B-55 [ADJUSTED, P3] — :2892-2928 (with the rationale correction: the emergency caller is fully countable, `triggered_by` is required on every meeting row, so restricting the denominator and extending the numerator are BOTH available); B-56 [CONFIRMED, P3] — :2930-2953 (the raw compare, the four canonicalising siblings, the verifier's behavioural repro in which 'labs' / 'Labs' / 'LABS_TRANSITION' / 'LABS/MEDBAY' each score as a crewmate lie against a true LABS placement). Anchors re-verified at HEAD by reading the current tree: eval/accusation_calibration.py:200-225 `_is_impostor` (its single `roles[...]` read is at :217 and it is on the TARGET), :227-243 `_iter_accusation_claims` (yields claims and drops the speaker), :245-260 `_accusation_claim_samples`, :285-328 `_bin_samples`, :331-375 `compute_accusation_calibration`, :83 `MIN_POPULATED_BINS_FOR_POWER = 5`; the firewall that sets the impostor ceiling on a 2-impostor roster at meetings/manager.py:1444 `_guard_teammate_turn_claims` and :1456 `exclude_teammate_vent_observations`, with the guard body at :3335 calling `exclude_teammate_accusation_claims` (:2866) and the `drop_teammate_statement_target` backstop (:2925); the four committed pooled cells read straight out of the reports — samples/9p2i 0.30033244680851046 over 752, ml_corpus/9p2i 0.28170283018867964 over 2120, samples/4p1i 0.24866071428571437 over 112, ml_corpus/4p1i 0.26585365853658544 over 123; eval/deduction_metrics.py:540 `MACHINERY_VOCABULARY` and :541-546 its explicit UPPER BOUND label, :531 `MACHINERY_DECIMAL_PATTERN`, :1567-1575 the "over ALL ballots" scoping, :2332-2351 the ONLY loop over `transcript.turns` (its one net, `PARTNER_PHRASES` over `free_text`, at :2350), :2416-2419 the two ballot machinery nets over the PRE-GUARD `model_body`, :1610-1630 the cell field block and :2588-2607 its construction; tests/eval/test_deduction_metrics.py:106-109 `_committed` (the committed reports are parsed with `model_validate_json`, so a new required cell fails there until the reports are rebuilt) and :1289-1304 (the 8 / 23 vocabulary pins); meetings/schemas.py:323-335 `AccusationClaim.reason`, :337-344 `CorroborationClaim.reason`, :306-311 `AlibiClaim` (which carries `evidence`, not `reason`), :455-496 `MeetingTurn`; eval/evidence_honesty.py:2181-2209 `_sighting_placement` (the ONE fixed site), :1952 the raw I-2 compare and :1956-1958 its untouched sibling on the agent frame, :1762-1766 the I-10 numerator's `facts.body_triggered` gate, :1032-1039 the `MeetingPhysicalityCells` construction with `body_triggered_meetings` already emitted at :1034, :352-359 `CELL_DEFINITIONS['I-10']`, :294-299 the I-2 definition sentence, :202 the `canonical_rooms` import and :2278-2285 / :2335 / :2339 / :2359 / :2399-2403 the four siblings that route through it; eval/watchability.py:1311-1361 `_testimony_vehicle` — the FROZEN `has_observation` at :1353-1356 with its 16.14 drift history at :1338-1352, the LIVE `subject_observed` at :1357-1361 — :845-877 the baseline-7 9p2i `SupplyFloors` block (`testimony_backed_conversion=FloorPin(value=0.6956521739130435, numerator=80)` at :873-875) and :914 `_DEFAULT_BASELINE_ID = "baseline-7"`; tests/eval/test_watchability.py:125-150 the frozen 15.2 parity pin that bites when the frozen bit widens; training/conviction/dataset.py:431-470 `_observation_backed_impostor_subjects` (its declared-mirror docstring at :434-445, its isinstance tuple at :466) and tests/training/test_conviction_model.py:356-370; the four LIVE sites this task deliberately does not widen — eval/vote_correctness.py:440-466 `_has_kill_witness_chain`, eval/funnel.py:777-784 `_killer_placed_at_scene` and :1355-1367 `_spoken_vouches`, eval/deception_instruments.py:582-595 and :679-694; meetings/transcript.py:2455 and :2493-2510 `_iter_move_placements` (which already builds exactly the placement this task lifts), :2112 (the detector's own skip of the two shapes it re-places) and :1365 / :2303 (the same spoken label canonicalised); the report plumbing eval/meeting_quality.py:3020, eval/report_schema.py:110-124 (the standing precedent: a wrapper-level aggregate keeps `format_version` 2 *because* every committed report is regenerated in the same PR), api/routes/eval.py:142, scripts/gen_frontend_types.py:26-36 (the eval wrapper IS generated), tests/api/test_leak.py:447-452 `EXPECTED_EVAL_REPORT_FIELDS`, tests/scripts/test_build_sample_report.py:40-50. Three censuses re-measured at HEAD for this contract: the A-6 utterance surface is exactly 11,727 (`turns[].free_text` + `turns[].claims[].reason` + `ballots[].rationale_text` over the four sets, matching A-6's own denominator), zero oracle hits land on `AlibiClaim.evidence`, and the whereabouts census reproduces B-56's numbers exactly (3,117 labels, 9 distinct, per set 763 / 2,177 / 85 / 92, every one self-canonical).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-instrument-aim`
**Depends on:** 21.7
**Section refs:** A-8 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md:936-1026 (the pooled and split ECEs reproduced to 4dp against the committed cells, the 708-accusation / 0-hit census, the measured mean confidence 0.673, and the verifier note's two BINDING corrections: the mid-range inversion is roughly a FIFTH the impostor block and not half, and the pooled accusation base rate is 0.500 on ml_corpus/9p2i, not the 0.22 chance prior the finder quoted); A-9 [CONFIRMED, P1] — :1028-1136 (the two-word net at :1040, the four committed cells, the 0/39 overlap reproduced independently, the free_text hole, and the verifier's corrections: the unmeasured spoken surface is 39 utterances rather than 28 because 11 further hits sit on `claims[].reason`, and the finding reads as a COVERAGE GAP — no shipped cell computes a wrong number); A-6 [CONFIRMED, P1] — :693-838, the net this task must overlap (78 utterances across 44 of 300 games; by surface ballot_rationale 39 / free_text 28 / claim_reason 11; 17 in-fiction uses of "engine" excluded BY HAND; the verifier's own census of the 78 and its "exactly ONE in-fiction survivor" note); B-9 [ADJUSTED, P1] — audits/review-2026-08-26/B/collated-findings.md:706-746 (the site list, the saw_player 2722 / saw_move 1136 / saw_vent 363 channel census, the 336→373 attempted / 239→249 converted delta, and the verifier's BINDING scope correction that `has_observation` / `observation_backed_any` is a declared frozen parity bit whose widening is the regression the 16.14 pin exists to catch); B-55 [ADJUSTED, P3] — :2892-2928 (with the rationale correction: the emergency caller is fully countable, `triggered_by` is required on every meeting row, so restricting the denominator and extending the numerator are BOTH available); B-56 [CONFIRMED, P3] — :2930-2953 (the raw compare, the four canonicalising siblings, the verifier's behavioural repro in which 'labs' / 'Labs' / 'LABS_TRANSITION' / 'LABS/MEDBAY' each score as a crewmate lie against a true LABS placement). Anchors re-verified at HEAD by reading the current tree: eval/accusation_calibration.py:200-225 `_is_impostor` (its single `roles[...]` read is at :217 and it is on the TARGET), :227-243 `_iter_accusation_claims` (yields claims and drops the speaker), :245-260 `_accusation_claim_samples`, :285-328 `_bin_samples`, :331-375 `compute_accusation_calibration`, :83 `MIN_POPULATED_BINS_FOR_POWER = 5`; the firewall that sets the impostor ceiling on a 2-impostor roster at meetings/manager.py:1444 `_guard_teammate_turn_claims` and :1456 `exclude_teammate_vent_observations`, with the guard body at :3335 calling `exclude_teammate_accusation_claims` (:2866) and the `drop_teammate_statement_target` backstop (:2925); the four committed pooled cells read straight out of the reports — samples/9p2i 0.30033244680851046 over 752, ml_corpus/9p2i 0.28170283018867964 over 2120, samples/4p1i 0.24866071428571437 over 112, ml_corpus/4p1i 0.26585365853658544 over 123; eval/deduction_metrics.py:540 `MACHINERY_VOCABULARY` and :541-546 its explicit UPPER BOUND label, :531 `MACHINERY_DECIMAL_PATTERN`, :1567-1575 the "over ALL ballots" scoping, :2332-2351 the ONLY loop over `transcript.turns` (its one net, `PARTNER_PHRASES` over `free_text`, at :2350), :2416-2419 the two ballot machinery nets over the PRE-GUARD `model_body`, :1610-1630 the cell field block and :2588-2607 its construction; tests/eval/test_deduction_metrics.py:106-109 `_committed` (the committed reports are parsed with `model_validate_json`, so a new required cell fails there until the reports are rebuilt) and :1289-1304 (the 8 / 23 vocabulary pins); meetings/schemas.py:323-335 `AccusationClaim.reason`, :337-344 `CorroborationClaim.reason`, :306-311 `AlibiClaim` (which carries `evidence`, not `reason`), :455-496 `MeetingTurn`; eval/evidence_honesty.py:2181-2209 `_sighting_placement` (the ONE fixed site), :1952 the raw I-2 compare and :1956-1958 its untouched sibling on the agent frame, :1762-1766 the I-10 numerator's `facts.body_triggered` gate, :1032-1039 the `MeetingPhysicalityCells` construction with `body_triggered_meetings` already emitted at :1034, :352-359 `CELL_DEFINITIONS['I-10']`, :294-299 the I-2 definition sentence, :202 the `canonical_rooms` import and :2278-2285 / :2335 / :2339 / :2359 / :2399-2403 the four siblings that route through it; eval/watchability.py:1311-1361 `_testimony_vehicle` — the FROZEN `has_observation` at :1353-1356 with its 16.14 drift history at :1338-1352, the LIVE `subject_observed` at :1357-1361 — :845-877 the baseline-7 9p2i `SupplyFloors` block (`testimony_backed_conversion=FloorPin(value=0.6956521739130435, numerator=80)` at :873-875) and :914 `_DEFAULT_BASELINE_ID = "baseline-7"`; tests/eval/test_watchability.py:125-150 the frozen 15.2 parity pin that bites when the frozen bit widens; training/conviction/dataset.py:431-470 `_observation_backed_impostor_subjects` (its declared-mirror docstring at :434-445, its isinstance tuple at :466) and tests/training/test_conviction_model.py:356-370; the four LIVE sites this task deliberately does not widen — eval/vote_correctness.py:440-466 `_has_kill_witness_chain`, eval/funnel.py:777-784 `_killer_placed_at_scene` and :1355-1367 `_spoken_vouches`, eval/deception_instruments.py:582-595 and :679-694; meetings/transcript.py:2455 and :2493-2510 `_iter_move_placements` (which already builds exactly the placement this task lifts), :2112 (the detector's own skip of the two shapes it re-places) and :1365 / :2303 (the same spoken label canonicalised); the report plumbing eval/meeting_quality.py:3020, eval/report_schema.py:110-124 (the standing precedent: a wrapper-level aggregate keeps `format_version` 2 *because* every committed report is regenerated in the same PR), api/routes/eval.py:142, scripts/gen_frontend_types.py:26-36 (the eval wrapper IS generated), tests/api/test_leak.py:447-452 `EXPECTED_EVAL_REPORT_FIELDS`, tests/scripts/test_build_sample_report.py:40-50. Three censuses re-measured at HEAD for this contract: the A-6 utterance surface is exactly 11,727 (`turns[].free_text` + `turns[].claims[].reason` + `ballots[].rationale_text` over the four sets, matching A-6's own denominator), zero oracle hits land on `AlibiClaim.evidence`, and the whereabouts census reproduces B-56's numbers exactly (3,117 labels, 9 distinct, per set 763 / 2,177 / 85 / 92, every one self-canonical).
**Complexity:** Medium
**Record impact:** none — not one recorded replay byte moves (`replays/**/replay-seed-*.jsonl` is untouched and `bash scripts/verify_samples.sh` still reports 100/100); the four derived `tournament-eval-report.json` views ARE rebuilt in this PR from those same bytes by the deterministic $0 offline builder, which is exactly what eval/report_schema.py:110-118's wrapper-aggregate precedent requires of a task that adds a cell.
**Measurement:** `uv run pytest tests/eval/test_accusation_calibration.py tests/eval/test_deduction_metrics.py tests/eval/test_watchability.py tests/eval/test_evidence_honesty.py tests/meetings/test_transcript.py tests/training/test_conviction_model.py -q` green; `uv run python scripts/build_sample_report.py --check --sample-dir <each of the four sets>` exits 0 after the rebuild; `uv run python scripts/gen_frontend_types.py --check` and `uv run python scripts/check_doc_facts.py` pass; `uv run pytest -m campaign` is run and every moved row named in the PR; and the PR carries a before/after table of every instrument cell this task moves, each number recomputed from committed bytes with its command.

Five findings, one failure mode: an instrument aimed a few degrees off the thing it
names, publishing a number that reads as a fact about the agents when it is a fact
about the machinery. None of them miscomputes anything — every cell A-8 and A-9 name
reproduces to four decimal places — and that is the point. They are aiming errors, and
the re-ground in 21.17 fits on what these instruments say.

The calibration curve is the loudest. `accusation_claim_ece` pools crew and impostor
accusations, but the Task 7.12 / 15.4 teammate firewall deletes a teammate accusation
at the per-turn chokepoint (meetings/manager.py:1444, :1456), and on a 2-impostor
roster a teammate is the ONLY target an impostor could name that scores as a hit. So
708 impostor accusations across the two 9p2i sets carry 0 hits, at a measured mean
confidence of 0.673, and every one of them is scored as agent overconfidence. Split by
accuser role and re-derived at HEAD, the arithmetic is unambiguous: samples/9p2i
pooled 0.30033244680851046 over 752 splits into crew 0.18190730837789656 over 561 and
impostor 0.6769633507853406 over 191; ml_corpus/9p2i pooled 0.28170283018867964 over
2120 splits into crew 0.17446038677479642 over 1603 and impostor 0.671856866537717
over 517. The artifact share is 39.4 % and 38.1 %. Two things the finder said are
wrong and the verifier corrected, and this contract's prose must not repeat either:
the mid-range inversion is only about a FIFTH the impostor block (the crew-only curve
falls 0.618 → 0.293 by itself — the rest is genuine turn-order herding), and the
pooled accusation base rate is 0.500 on ml_corpus/9p2i, not 0.22. The 4p1i sets add a
detail neither the finder nor the verifier published, measured here: impostor
accusations are 0/39 and 0/44 there too, and the mechanism is different — with a
single impostor on the roster the only scoring-correct target is the speaker, and a
self-accusation is not a lawful accusation. The docstring must name the ceiling
per roster rather than blaming the firewall for a case the firewall never touches.

The dialect gauge is the mirror image: it fires, and it fires somewhere else.
`MACHINERY_VOCABULARY` is two words, "threshold" and "suspicion"; re-implemented
verbatim it hits 32 of 3,602 ballots and overlaps the 39 oracle-dialect utterances A-6
found in exactly 0 places. Worse, both machinery nets are scoped over ballots
(eval/deduction_metrics.py:1567-1575, :2416-2419), and the only loop over spoken turns
(:2332-2351) applies one net, the omniscience one. So the 28 free_text and 11
claim_reason utterances in which a player says "the engine flagged it" are counted by
no instrument in the fold — which is why the leak A-6 traces to two template lines
survived to baseline 7 unnoticed. The fix is a pure addition and it must stay one:
`MACHINERY_VOCABULARY` keeps its Task-19.8 upper-bound label and its 8 / 23 committed
pins, and the oracle register — which, unlike "suspicion", has no innocent in-world
reading — ships as its own high-precision cell over all three spoken surfaces.

That precision is the whole difficulty, and this contract measured the trap so the
implementer does not have to discover it in review: a naive `the engine` net run over
the committed bytes returns 100 hits against A-6's 78, and the excess is overwhelmingly
"the Engineering group", "the Engineering scene", "the Engineering chaos" and "tending
to the engines in Engineering" — the ship's wing and its `align_engine_output` task
(engine/maps/canonical_1.yaml:288), which are correct in-world speech. A word boundary
and an explicit in-fiction exclusion are load-bearing, and the gate ships with both
directions planted.

B-9 is the half that must land before 21.17 re-fits. Task 20.43 taught
eval/evidence_honesty.py:2181-2209 to read a `saw_move` as a placement at its
destination; every other live first-hand-sighting predicate still isinstance-checks a
tuple that omits it, and `grep -rn "SawMoveObservation" --include="*.py" eval/
training/ scripts/` returns hits in that one module and the type generator alone —
re-run at HEAD, unchanged. The corpus carries 1,136 saw_move observations against
2,722 saw_player on ml_corpus/9p2i, so the referee's LIVE subject-aware bit
(eval/watchability.py:1357-1361) and its declared mirror in the conviction label
(training/conviction/dataset.py:466) are blind to 29 % of spoken placements. The
verifier's scope correction is binding and is the reason this is surgery rather than a
sweep: the sibling `has_observation` bit at :1353-1356 is a FROZEN pre-15.19 parity
artefact, re-narrowed by Task 16.14 after it silently widened to the 15.4 vent type and
broke bit-exact geomean parity on seeds 5 and 22. It stays exactly as written, and the
test at tests/eval/test_watchability.py:125 that catches its widening stays green and
unedited. The widening moves the pinned `testimony_backed_conversion` floor — the
finder measured samples/9p2i 80/115 → 84/132 — so the floor is re-derived from the
corrected gauge over the same committed bytes, which is a pin catching up with its own
instrument, not a target moving.

The four remaining live sites — `_has_kill_witness_chain`, funnel's two, deception's
two — are deliberately NOT widened here. They gate nothing (eval/funnel.py:1045 says so
in its own comment), while the referee's floor and the conviction label do, and
`vote_correctness_rate` is a doc-fact-gated published number whose movement belongs in
a task that owns its docstring, its seed-by-seed census and its perturbation test.
Deferring silently is how this vocabulary drifted in the first place, so the deferral
is made structural: a walk over `eval/` and `training/` fails on any first-hand-sighting
isinstance tuple that is neither the shared helper, the named frozen bit, nor one of
the four dated entries on an explicit allow-list. The remainder becomes countable, and
it cannot grow.

B-55 and B-56 are small and honest. I-10's reporter cell gates its numerator on
body-triggered meetings and divides by all resolved ones, understating itself by the
emergency share — 60/432 published against a coherent 60/400, 7.4 % relative. The
finding's rationale is wrong in a way that matters: an emergency caller is not
structurally uncountable, `triggered_by` is required on every meeting row, so the
editorial choice is which denominator to publish, and both inputs are already fields.
I-2 decides whether a spoken whereabouts is a lie with a bare string compare against
engine room ids, in the one module whose four sibling comparisons route through
`canonical_rooms` precisely because "a raw string compare would move this cell on
formatting alone". It is inert today — all 3,117 committed labels are self-canonical
uppercase single rooms, re-counted here — and latent tomorrow: I-2 sits under a
pre-registered bar, and the first prompt-set or parser change that lets 'labs' or a
compound 'LABS/MEDBAY' through scores a truthful crewmate as a liar.

What this task does not do. It does not re-fit anything: the surrogate, the conviction
model and the composed verdict are 21.17's, on the 21.15 corpus, and the conviction
artifact committed today stays as recorded even though this PR corrects the label it
was fitted against — that gap is the reason 21.17 runs after 21.15 and 21.8. It writes
no bar and reads none. It moves no recorded byte. And nothing it publishes may imply
the phase-20 record passed its own bars: baseline 7 is canon by explicit owner override
of a FINDING verdict — bars 1 and 2 were missed — which is the phrasing
eval/vote_correctness.py:29-33 already uses and the phrasing any docstring this task
touches must keep.

**Files in scope:**
- eval/accusation_calibration.py; (the accuser-role split, the new curve model, the docstring's ceiling explanation)
- tests/eval/test_accusation_calibration.py; (the eight re-derived split cells, the pooled invariance, a synthetic role-mix case)
- eval/deduction_metrics.py; (the oracle net + its three surface cells + the claim-reason denominator; MACHINERY_VOCABULARY untouched; plus the `crew_omniscient_control_ballots` docstrings at `:257-258` and `:1562-1563` truthed up — comment text only, no cell definition moves)
- tests/eval/test_deduction_metrics.py; (the oracle census, the true-positive exhibits, the in-fiction controls, the 8 / 23 pins unchanged)
- meetings/transcript.py; (the shared `sighting_placement` helper the detector's own normalisation already implies)
- tests/meetings/test_transcript.py; (the helper's unit pins, both shapes and the None case)
- eval/evidence_honesty.py; (delegate `_sighting_placement`; the I-10 body-restricted cell + its definition sentence; the I-2 canonicalisation and its agent-frame sibling)
- tests/eval/test_evidence_honesty.py; (the new I-10 cell, the planted I-2 label variants, every existing committed pin held)
- eval/watchability.py; (the LIVE subject-aware bit routed through the helper; the baseline-7 `testimony_backed_conversion` floor re-derived)
- tests/eval/test_watchability.py; (the live/frozen split pinned directly; the re-derived floor; the 15.2 parity test left as written)
- training/conviction/dataset.py; (the declared mirror widened in lockstep with the referee)
- tests/training/test_conviction_model.py; (the mirror's re-derived rows)
- tests/eval/test_sighting_vocabulary.py; (NEW — the ast walk that counts the un-widened remainder and fails on a new one)
- tests/api/test_leak.py; (the eval-report field-set snapshot gains the new cells)
- frontend/src/types/api.ts; (regenerated, never hand-edited)
- replays/samples/9p2i/tournament-eval-report.json; (rebuilt from the unchanged replays)
- replays/samples/4p1i/tournament-eval-report.json; (rebuilt from the unchanged replays)
- replays/ml_corpus/9p2i/tournament-eval-report.json; (rebuilt from the unchanged replays)
- replays/ml_corpus/4p1i/tournament-eval-report.json; (rebuilt from the unchanged replays)

**Files NOT in scope:**
- eval/vote_correctness.py, eval/funnel.py, eval/deception_instruments.py (the four un-widened live sites: they gate nothing, and `vote_correctness_rate`'s four doc-fact-gated rates, its seed-by-seed census and its perturbation literal belong to a task that owns them — the allow-list in the new walk test names all four with this task id, so they are counted, not forgotten)
- replays/**/replay-seed-*.jsonl and replays/**/MANIFEST.md (no re-record; `verify_samples.sh` 100/100 is the gate, and 21.15 owns the next recording)
- agents/strategic/prompts/ (21.1 owns the template lines that teach the dialect; this task only measures them — the gauge must read the leak on the CURRENT committed bytes, which are v4)
- training/surrogate/, training/bakeoff/, docs/ml-program.md, scripts/verify_ml_evidence.py (no re-fit, no re-stamp, no fingerprint moves here — 21.16 and 21.17)
- eval/prompt_regression.py and tests/fixtures/prompt_regression/baseline.json (`PromptRegressionMetrics` carries a fixed scalar summary; no new cell joins it, so the committed baseline does not move)
- eval/report_schema.py (`CURRENT_FORMAT_VERSION` stays 2 — every cell added here is wrapper-level and every committed report is regenerated in this same PR, which is the rule the marker's own comment block states)
- audits/ (the historical measure artifacts and the baseline-7 audit are records of what was measured then; they are cited, never rewritten)

**Definition of done:**
- [ ] `eval/accusation_calibration.py` collects the accusation SPEAKER alongside the claim and emits two role-conditioned curves beside the pooled one; the pooled `accusation_claim_*` fields are untouched in name, value and position, and the four committed pooled cells still read 0.30033244680851046 / 0.28170283018867964 / 0.24866071428571437 / 0.26585365853658544 after the rebuild.
- [ ] The split reproduces the re-derived table exactly, pinned per set in `tests/eval/test_accusation_calibration.py` against the committed reports: samples/9p2i crew (0.18190730837789656, n=561) and impostor (0.6769633507853406, n=191); ml_corpus/9p2i crew (0.17446038677479642, n=1603) and impostor (0.671856866537717, n=517); samples/4p1i crew (0.06506849315068489, n=73) and impostor (0.6282051282051283, n=39); ml_corpus/4p1i crew (0.09493670886075953, n=79) and impostor (0.6409090909090909, n=44) — with each pair's totals asserted to sum to the pooled total, and the impostor hit rate asserted to be exactly 0.0 on all four.
- [ ] The module docstring states the ceiling correctly per roster and cites the mechanism: on a 2-impostor roster the teammate firewall (`meetings/manager.py:1444`, `:1456`) deletes the impostor's only scoring-correct target; on a 1-impostor roster the roster itself does, since the sole impostor cannot lawfully accuse themselves. It does NOT repeat the two corrected over-statements — the mid-range inversion is roughly a fifth attributable to the impostor block, and the pooled accusation base rate is ~0.50, not 0.22.
- [ ] One stale claim in the same module is truthed up while this task is in it, because it is the same defect class and the file is already open: `eval/deduction_metrics.py:257-258` and `:1562-1563` say `crew_omniscient_control_ballots` reads "both 0 on every committed set". Re-derived at HEAD it reads **1 on each 9p2i set**. Both docstrings state the re-derived numbers with the command that produced them, and the PR quotes that command's output. This is a comment-only edit: the cell's definition, its computation and every assertion over it are untouched, and the A-16 cells that read this control stay with the task that owns them.
- [ ] A synthetic report in `tests/eval/test_accusation_calibration.py` with a hand-built role mix asserts the split is a partition — crew total + impostor total == pooled total, and one accusation moved between speakers changes exactly one curve — so the conditioning is pinned on constructed data and not only on the corpus.
- [ ] `eval/deduction_metrics.py` gains a high-precision oracle-register net as its own module constant, applied to three surfaces: the pre-guard ballot body (the surface the existing machinery nets already read at :2416-2419), `turns[].free_text`, and `turns[].claims[].reason`. `MACHINERY_VOCABULARY` is unchanged, keeps its UPPER BOUND docstring, and `tests/eval/test_deduction_metrics.py:1289-1304`'s 8 and 23 still pass unedited.
- [ ] The claim surface is decided in the code and stated in the docstring: `AccusationClaim.reason` and `CorroborationClaim.reason` are scanned; `AlibiClaim` carries `evidence`, not `reason`, and is not scanned — a ruling backed by a measurement in the PR (zero oracle hits on any `evidence` string across the four sets). A `claim_reasons_total` denominator ships with the cell so no count is published without its base, mirroring how `player_visible_leak_turns` sits against `turns_total`.
- [ ] The gate bites in BOTH directions, planted in `tests/eval/test_deduction_metrics.py`: the net matches five utterances taken verbatim from the committed bytes and re-verified at HEAD — "the engine has already flagged" (samples/9p2i seed 20), "engine certified the vent sighting" (samples/9p2i seeds 0 and 19), "The system flagged the vent" (ml_corpus/9p2i seed 1072), "certified by the system flags" (samples/4p1i seed 6), "The engine flagged it as a certifiable impostor action" (ml_corpus/4p1i seed 1035) — and scores ZERO on the in-fiction controls "p-1 broke away from the Engineering group", "I cannot speak to the Engineering scene directly", "far from the Engineering chaos", "I was busy tending to the engines in Engineering", "aligning engine output in Engineering" and "down in the engine room".
- [ ] The PR publishes the per-set, per-surface census the shipped net actually reads and reconciles it against A-6's 78 utterances / 39 ballot / 28 free_text / 11 claim_reason, attributing every difference to a stated cause (the ballot cell reads the PRE-GUARD body while A-6 read the recorded `rationale_text` — the same one-ballot class that explains 32 against 33 on the vocabulary net — and A-6's 17 in-fiction exclusions were made by hand). A residual with no attribution is a defect in the net, not a rounding note.
- [ ] `meetings/transcript.py` exposes one public placement helper returning the `SawPlayerObservation` a spoken artifact puts on the record — the `saw_player` itself, or a `saw_move` re-placed at its DESTINATION `(to_room, tick)` — and `eval/evidence_honesty.py::_sighting_placement` delegates to it with its documented reasoning kept. Every committed I-4 / I-6 / I-7 cell is byte-identical before and after, proved by a re-run in the PR: the delegation is a move, not a behaviour change.
- [ ] `eval/watchability.py`'s LIVE `subject_observed` bit (:1357-1361) admits a saw_move placement through the shared helper, while the FROZEN `has_observation` tuple (:1353-1356) is untouched, and `tests/eval/test_watchability.py` gains a direct unit case asserting the split on one turn — a saw_move of the accused sets `observation_backed` and leaves `observation_backed_any` False. `test_historical_15_2_geomean_parity_frozen_pin_on_9p2i` (:125) is neither edited nor skipped and stays green.
- [ ] The `testimony_backed_conversion` floor for `baseline-7` is re-derived from the corrected gauge over the same committed bytes and re-pinned with its numerator, for both sets, and the pin comment records that the value moved because the vocabulary was corrected and NOT because supply changed. The `baseline-6` block is left exactly as written — it pins a different record's supply — and the PR states the measured before/after pair (the finder measured samples/9p2i 80/115 = 0.6956521739130435 → 84/132; the committed number is whatever the re-run reports, never the finder's estimate copied).
- [ ] `training/conviction/dataset.py::_observation_backed_impostor_subjects` moves through the same helper in the same commit, its docstring still truthfully describes itself as the referee's mirror, and `tests/training/test_conviction_model.py`'s affected rows are re-derived rather than relaxed.
- [ ] `tests/eval/test_sighting_vocabulary.py` walks `eval/` and `training/` with `ast` and fails on any isinstance check over the first-hand sighting types that is not the shared helper, the named frozen parity bit, or one of exactly four allow-listed entries (`eval/vote_correctness.py::_has_kill_witness_chain`, `eval/funnel.py::_killer_placed_at_scene`, `eval/funnel.py::_spoken_vouches`, `eval/deception_instruments.py`'s two impostor-vouch folds), each carrying this task id as the reason it is still narrow. A planted new site in a temp tree proves the walk bites, and the allow-list is asserted to have exactly four entries so shrinking it is a deliberate edit.
- [ ] `eval/evidence_honesty.py` emits the body-restricted reporter rate beside the existing all-meetings cell, both denominators already being fields, and `CELL_DEFINITIONS['I-10']` says which of the two a bar is stated on. The existing per-set pairs [(17,152),(60,432),(1,40),(2,44)] and their (80,668) sum are unchanged and still asserted; the new cell's four pairs are pinned beside them (60/400 = 0.15 and 17/144 = 0.1181 are the two the register verified).
- [ ] I-2 routes its truth decision through `canonical_rooms`, as its four siblings do, and so does the agent-frame compare two lines below it — named here because the register did not, and it is the same class: a model-written label compared raw against engine rooms. Every committed I-2 cell is byte-identical after the change (crew_false (3,659) / (17,1892) / (1,80) / (0,91), crew_false_agent_frame (2,659), impostor_false (1,104)), and planted cases pin the behaviour the change buys: 'labs', 'Labs', 'LABS_TRANSITION' and 'LABS/MEDBAY' against a true LABS placement now score TRUTHFUL, where each scores as a crewmate lie at HEAD.
- [ ] All four `tournament-eval-report.json` views are rebuilt with `scripts/build_sample_report.py` and committed, `--check` exits 0 on each, and `git diff --name-only` shows no `replay-seed-*.jsonl` and no `MANIFEST.md` — the derived views move, the record does not. `bash scripts/verify_samples.sh` still reports 100/100.
- [ ] `frontend/src/types/api.ts` is REGENERATED (never hand-edited) and `tests/api/test_leak.py::EXPECTED_EVAL_REPORT_FIELDS` gains every new field name, with the firewall note extended to cover them: each new cell is an aggregate count, a rate or a bool, and the accusation split is a role-partition of an already-served post-game GM surface.
- [ ] `uv run pytest -m campaign` is run and the PR records, row by row, which pins moved. Every mover must be inside the corpus-fit class the phase-20 close records as F1 and 21.17 re-grounds; a red row outside that class stops the PR with a Questions section rather than being re-pinned here.
- [ ] `uv run python scripts/check_doc_facts.py` passes and the PR states which doc facts were re-derived versus untouched.
- [ ] `uv run python scripts/gen_frontend_types.py --check` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — reproduce before you change anything. Re-run the three censuses this contract
quotes and keep the scripts in your scratchpad: the role-split ECE table (walk
`report.games[*].meetings[*].transcript.turns[*].claims` from each committed
`tournament-eval-report.json`, take `roles[turn.speaker]` for the split and
`roles[claim.against]` for the hit, and bin with `min(int(c*10), 9)` exactly as
`_bin_samples` does); the oracle-net census over the 11,727-utterance surface; and the
3,117-label whereabouts census. If your pooled ECE does not reproduce the committed
cell to the digit, your walk is wrong, not the instrument.

Step 2 — the calibration split. `_iter_accusation_claims` drops the speaker, so give
the sample collector the `(confidence, hit, speaker_role)` triple rather than
threading a second parallel iterator. Add ONE new frozen result model holding a
curve's `(bins, total, ece, populated_bins, low_power)` and use it for the two new
fields only: refactoring the existing three curves into it would change the served
wire shape and break the dashboard and the field-set snapshot for no gain. Watch the
low-power flag — the 4p1i impostor curves populate 4 bins against
`MIN_POPULATED_BINS_FOR_POWER = 5`, so they legitimately flag, and that is signal
about the roster, not a bug to suppress.

Step 3 — the oracle net. Compiled regexes, not the substring `_matches` helper: you
need `\b` word boundaries and a negative lookahead, because `the engine` matches
`the Engineering group` without them and that single mistake produces most of the 22
excess hits a naive net returns. Build it against the planted lists in both directions
before you measure the corpus. Keep it a SEPARATE constant and separate cells beside
`MACHINERY_VOCABULARY` — the vocabulary net's 8 / 23 are Task 19.8's carried
disclosure and the module's own docstring calls it an upper bound; folding oracle terms
into it would destroy that continuity and move a committed pin for no reason. For the
turn surface, extend the loop that already exists at :2332-2351 rather than adding a
second walk.

Step 4 — the placement helper. Lift `eval/evidence_honesty.py::_sighting_placement`
into `meetings/transcript.py` beside `_iter_move_placements`, which builds the exact
same `SawPlayerObservation` from a transition, and re-export it; every consumer already
imports from that module, so no new import edge appears and `lint-imports` has nothing
to say. Then the two call sites: `subject_observed` becomes "the placement this
artifact makes, if any, names the subject" (keep the `SawVentObservation` arm — a vent
sighting is a first-hand sighting but not a placement, so it stays an explicit second
condition), and the conviction mirror takes the identical shape. Do NOT touch the line
above it: `has_observation` is frozen, the 16.14 note at :1338-1352 explains what
happened last time someone widened it, and the parity test at
tests/eval/test_watchability.py:125 will tell you immediately if you did.

Step 5 — the floor re-pin, in this order. Widen the bit, run
`compute_watchability(Path('replays/samples/9p2i'))` and read the measured
`testimony_backed_conversion`, then write that number and its numerator into the
`baseline-7` block with a comment recording why it moved. The pin is self-consistent by
construction (measured == floor on the set it was derived from), so a floor left at
0.6956521739130435 will fail loudly rather than silently — which is the correct
behaviour and your proof that the widening reached the gauge. Note the shape of the
derived floor: `population_relative_conversion=True` scales it by the flags ratio, so
re-derive with the same recipe the comment block at :845-869 spells out, and leave the
`flags_per_meeting` line alone.

Step 6 — the rebuild and the blast radius, last. Adding a cell to a report model breaks
the committed reports for every reader that parses them (`_committed` in
tests/eval/test_deduction_metrics.py is the first one you will hit), so run
`scripts/build_sample_report.py --sample-dir` for all four sets, then
`gen_frontend_types.py`, then the leak snapshot. `CURRENT_FORMAT_VERSION` stays 2: read
eval/report_schema.py:110-124 and follow the 9.6 / 10.4 precedent, whose whole
justification is that the same PR regenerates every committed report. Before pushing,
`grep -rn` each new field name and confirm nothing outside your scope reads it, and run
`uv run pytest -m campaign` — the default filter deselects it, and the conviction
mirror you changed is exactly what it pins.

## Public types this task introduces
- `eval.accusation_calibration.CalibrationCurve`
- `eval.deduction_metrics.MACHINERY_ORACLE_PATTERNS`
- `meetings.transcript.sighting_placement`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`

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
Open a PR from branch `phase-21-instrument-aim` with a title like `task 21.9: two instruments re-aimed: calibration without the firewall artifact, a dialect gauge that overlaps the dialect`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing A-8 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md:936-1026 (the pooled and split ECEs reproduced to 4dp against the committed cells, the 708-accusation / 0-hit census, the measured mean confidence 0.673, and the verifier note's two BINDING corrections: the mid-range inversion is roughly a FIFTH the impostor block and not half, and the pooled accusation base rate is 0.500 on ml_corpus/9p2i, not the 0.22 chance prior the finder quoted); A-9 [CONFIRMED, P1] — :1028-1136 (the two-word net at :1040, the four committed cells, the 0/39 overlap reproduced independently, the free_text hole, and the verifier's corrections: the unmeasured spoken surface is 39 utterances rather than 28 because 11 further hits sit on `claims[].reason`, and the finding reads as a COVERAGE GAP — no shipped cell computes a wrong number); A-6 [CONFIRMED, P1] — :693-838, the net this task must overlap (78 utterances across 44 of 300 games; by surface ballot_rationale 39 / free_text 28 / claim_reason 11; 17 in-fiction uses of "engine" excluded BY HAND; the verifier's own census of the 78 and its "exactly ONE in-fiction survivor" note); B-9 [ADJUSTED, P1] — audits/review-2026-08-26/B/collated-findings.md:706-746 (the site list, the saw_player 2722 / saw_move 1136 / saw_vent 363 channel census, the 336→373 attempted / 239→249 converted delta, and the verifier's BINDING scope correction that `has_observation` / `observation_backed_any` is a declared frozen parity bit whose widening is the regression the 16.14 pin exists to catch); B-55 [ADJUSTED, P3] — :2892-2928 (with the rationale correction: the emergency caller is fully countable, `triggered_by` is required on every meeting row, so restricting the denominator and extending the numerator are BOTH available); B-56 [CONFIRMED, P3] — :2930-2953 (the raw compare, the four canonicalising siblings, the verifier's behavioural repro in which 'labs' / 'Labs' / 'LABS_TRANSITION' / 'LABS/MEDBAY' each score as a crewmate lie against a true LABS placement). Anchors re-verified at HEAD by reading the current tree: eval/accusation_calibration.py:200-225 `_is_impostor` (its single `roles[...]` read is at :217 and it is on the TARGET), :227-243 `_iter_accusation_claims` (yields claims and drops the speaker), :245-260 `_accusation_claim_samples`, :285-328 `_bin_samples`, :331-375 `compute_accusation_calibration`, :83 `MIN_POPULATED_BINS_FOR_POWER = 5`; the firewall that sets the impostor ceiling on a 2-impostor roster at meetings/manager.py:1444 `_guard_teammate_turn_claims` and :1456 `exclude_teammate_vent_observations`, with the guard body at :3335 calling `exclude_teammate_accusation_claims` (:2866) and the `drop_teammate_statement_target` backstop (:2925); the four committed pooled cells read straight out of the reports — samples/9p2i 0.30033244680851046 over 752, ml_corpus/9p2i 0.28170283018867964 over 2120, samples/4p1i 0.24866071428571437 over 112, ml_corpus/4p1i 0.26585365853658544 over 123; eval/deduction_metrics.py:540 `MACHINERY_VOCABULARY` and :541-546 its explicit UPPER BOUND label, :531 `MACHINERY_DECIMAL_PATTERN`, :1567-1575 the "over ALL ballots" scoping, :2332-2351 the ONLY loop over `transcript.turns` (its one net, `PARTNER_PHRASES` over `free_text`, at :2350), :2416-2419 the two ballot machinery nets over the PRE-GUARD `model_body`, :1610-1630 the cell field block and :2588-2607 its construction; tests/eval/test_deduction_metrics.py:106-109 `_committed` (the committed reports are parsed with `model_validate_json`, so a new required cell fails there until the reports are rebuilt) and :1289-1304 (the 8 / 23 vocabulary pins); meetings/schemas.py:323-335 `AccusationClaim.reason`, :337-344 `CorroborationClaim.reason`, :306-311 `AlibiClaim` (which carries `evidence`, not `reason`), :455-496 `MeetingTurn`; eval/evidence_honesty.py:2181-2209 `_sighting_placement` (the ONE fixed site), :1952 the raw I-2 compare and :1956-1958 its untouched sibling on the agent frame, :1762-1766 the I-10 numerator's `facts.body_triggered` gate, :1032-1039 the `MeetingPhysicalityCells` construction with `body_triggered_meetings` already emitted at :1034, :352-359 `CELL_DEFINITIONS['I-10']`, :294-299 the I-2 definition sentence, :202 the `canonical_rooms` import and :2278-2285 / :2335 / :2339 / :2359 / :2399-2403 the four siblings that route through it; eval/watchability.py:1311-1361 `_testimony_vehicle` — the FROZEN `has_observation` at :1353-1356 with its 16.14 drift history at :1338-1352, the LIVE `subject_observed` at :1357-1361 — :845-877 the baseline-7 9p2i `SupplyFloors` block (`testimony_backed_conversion=FloorPin(value=0.6956521739130435, numerator=80)` at :873-875) and :914 `_DEFAULT_BASELINE_ID = "baseline-7"`; tests/eval/test_watchability.py:125-150 the frozen 15.2 parity pin that bites when the frozen bit widens; training/conviction/dataset.py:431-470 `_observation_backed_impostor_subjects` (its declared-mirror docstring at :434-445, its isinstance tuple at :466) and tests/training/test_conviction_model.py:356-370; the four LIVE sites this task deliberately does not widen — eval/vote_correctness.py:440-466 `_has_kill_witness_chain`, eval/funnel.py:777-784 `_killer_placed_at_scene` and :1355-1367 `_spoken_vouches`, eval/deception_instruments.py:582-595 and :679-694; meetings/transcript.py:2455 and :2493-2510 `_iter_move_placements` (which already builds exactly the placement this task lifts), :2112 (the detector's own skip of the two shapes it re-places) and :1365 / :2303 (the same spoken label canonicalised); the report plumbing eval/meeting_quality.py:3020, eval/report_schema.py:110-124 (the standing precedent: a wrapper-level aggregate keeps `format_version` 2 *because* every committed report is regenerated in the same PR), api/routes/eval.py:142, scripts/gen_frontend_types.py:26-36 (the eval wrapper IS generated), tests/api/test_leak.py:447-452 `EXPECTED_EVAL_REPORT_FIELDS`, tests/scripts/test_build_sample_report.py:40-50. Three censuses re-measured at HEAD for this contract: the A-6 utterance surface is exactly 11,727 (`turns[].free_text` + `turns[].claims[].reason` + `ballots[].rationale_text` over the four sets, matching A-6's own denominator), zero oracle hits land on `AlibiClaim.evidence`, and the whereabouts census reproduces B-56's numbers exactly (3,117 labels, 9 distinct, per set 763 / 2,177 / 85 / 92, every one self-canonical).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
