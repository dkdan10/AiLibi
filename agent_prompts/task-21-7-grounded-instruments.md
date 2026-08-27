# Agent Prompt — 21.7 The instruments read the recorded game: the flag census comes off the record, not a re-derivation

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.7 — The instruments read the recorded game: the flag census comes off the record, not a re-derivation, anchored to B-6 [CONFIRMED, P1 — the centrepiece] and B-10 [ADJUSTED, P2] of `audits/review-2026-08-26/B/collated-findings.md` (B-6 at :477-563, both merged finder blocks plus the verifier's exact re-run and its two precision notes; B-10 at :748-791, including the verifier's WHY-ADJUSTED paragraph that refutes the "composition unstated" framing and re-homes the surviving items — the stale docstring sentence and the gauge split — to this contract); the declared carry this task executes, `tasks/phase-20.md:4251-4260` (Task 20.26 Integration risk 4: "the phase's own instruments must read RECORDED flags or reconstruct the records, never the record-free re-derivation, or they will measure the old substrate on new bytes"); `audits/audit-phase-20-baseline-7.md:789-812` §10.3, which declares the same loss for three TEST mirrors and names no live consumer, and :624-628 §8, whose gauge table publishes the split this task re-derives. Anchors re-verified at HEAD `4002f19b` (the registers were written at `d8ec0a1c`, its parent; every line below was re-read, not carried): the four roster-only call sites reproduce exactly — `training/conviction/dataset.py:491`, `eval/meeting_quality.py:2382`, `eval/watchability.py:1470`, `eval/vote_correctness.py:595`; production threads all four channels at `meetings/manager.py:1225-1232`; the signature with three defaulted-None record channels plus `trigger_kind` is `meetings/transcript.py:1490-1500`. TWO FURTHER SITES the register did not name, both inside a module already in scope, found by a fresh repo-wide grep: `eval/meeting_quality.py:1798` (the sub-gate shelter census inside `compute_gate_metrics`) and `:1982` (the per-ejection channel decomposition) — same defect, same bytes, handled here. Structure anchors: `eval/watchability.py:429` `SupplyFloors`, :538 `_BASELINE_SUPPLY_FLOORS`, :841-901 the baseline-7 block (:850-852 the 9p2i split comment, :866-874 the pins, :890-892 the in-module contradiction of the stale docstring), :914 `_DEFAULT_BASELINE_ID`, :961 `evaluate_supply_floors`, :1400 `_meeting_facts`, :1976 `_game_facts`, :2000-2012 `_persisted_vent_flag_count`, :2050-2065 `_supply_gauge_values` with the false sentence at :2062, :268-272 the false identity claim; `eval/meeting_quality.py:2351` `compute_supply_gauges`; `training/conviction/dataset.py:255-310` the row schema and its disjointness validator at :303. The in-repo reconstructions the fix sketch cites: `eval/funnel.py:1230-1263`, `scripts/counterfactual_phase20.py:744-787` (three channels threaded, `off_flags_match_recorded` self-checked at :784-785 — it does NOT thread `trigger_kind`), `tests/_helpers/committed.py:122-166`, `audits/workflows/extract_gameplay_facts.py:532-560`.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-grounded-instruments`
**Depends on:** none (root)
**Section refs:** B-6 [CONFIRMED, P1 — the centrepiece] and B-10 [ADJUSTED, P2] of `audits/review-2026-08-26/B/collated-findings.md` (B-6 at :477-563, both merged finder blocks plus the verifier's exact re-run and its two precision notes; B-10 at :748-791, including the verifier's WHY-ADJUSTED paragraph that refutes the "composition unstated" framing and re-homes the surviving items — the stale docstring sentence and the gauge split — to this contract); the declared carry this task executes, `tasks/phase-20.md:4251-4260` (Task 20.26 Integration risk 4: "the phase's own instruments must read RECORDED flags or reconstruct the records, never the record-free re-derivation, or they will measure the old substrate on new bytes"); `audits/audit-phase-20-baseline-7.md:789-812` §10.3, which declares the same loss for three TEST mirrors and names no live consumer, and :624-628 §8, whose gauge table publishes the split this task re-derives. Anchors re-verified at HEAD `4002f19b` (the registers were written at `d8ec0a1c`, its parent; every line below was re-read, not carried): the four roster-only call sites reproduce exactly — `training/conviction/dataset.py:491`, `eval/meeting_quality.py:2382`, `eval/watchability.py:1470`, `eval/vote_correctness.py:595`; production threads all four channels at `meetings/manager.py:1225-1232`; the signature with three defaulted-None record channels plus `trigger_kind` is `meetings/transcript.py:1490-1500`. TWO FURTHER SITES the register did not name, both inside a module already in scope, found by a fresh repo-wide grep: `eval/meeting_quality.py:1798` (the sub-gate shelter census inside `compute_gate_metrics`) and `:1982` (the per-ejection channel decomposition) — same defect, same bytes, handled here. Structure anchors: `eval/watchability.py:429` `SupplyFloors`, :538 `_BASELINE_SUPPLY_FLOORS`, :841-901 the baseline-7 block (:850-852 the 9p2i split comment, :866-874 the pins, :890-892 the in-module contradiction of the stale docstring), :914 `_DEFAULT_BASELINE_ID`, :961 `evaluate_supply_floors`, :1400 `_meeting_facts`, :1976 `_game_facts`, :2000-2012 `_persisted_vent_flag_count`, :2050-2065 `_supply_gauge_values` with the false sentence at :2062, :268-272 the false identity claim; `eval/meeting_quality.py:2351` `compute_supply_gauges`; `training/conviction/dataset.py:255-310` the row schema and its disjointness validator at :303. The in-repo reconstructions the fix sketch cites: `eval/funnel.py:1230-1263`, `scripts/counterfactual_phase20.py:744-787` (three channels threaded, `off_flags_match_recorded` self-checked at :784-785 — it does NOT thread `trigger_kind`), `tests/_helpers/committed.py:122-166`, `audits/workflows/extract_gameplay_facts.py:532-560`.
**Complexity:** Integration
**Record impact:** none — no committed replay byte moves; the derived pins re-derive and the referee's targets stay at their measured values.
**Measurement:** `uv run pytest tests/eval/test_watchability.py tests/eval/test_meeting_quality.py tests/eval/test_vote_correctness.py tests/eval/test_gate_spec_metrics.py tests/training/test_conviction_model.py -q` green; the PR Summary quotes the four corrected censuses re-derived by the command in the DoD — `samples/9p2i` 144/152, `samples/4p1i` 20/40, `ml_corpus/9p2i` 428/432, `ml_corpus/4p1i` 29/44 — beside the numbers they replace, and `bash scripts/verify_samples.sh` reports 100/100 to prove no recorded byte moved.

Four live instruments re-derive the meeting's contradiction flags from the recorded
transcript alone and call the result the evidence supply. Production does not do that.
`meetings/manager.py:1225-1232` hands `detect_contradictions` the meeting's
`trigger_kind` and all three private grounding channels — vent witness records, move
witness records, per-speaker sighting records — and the flag set it returns is what the
meeting priced, what the ballots cited, and what the replay persisted. The four
consumers call the same function with `roster=` and nothing else, so they price a
different game: one where no speaker's private record exists, where the Task-18.9
interior exemption re-arms because no sighting records were supplied
(`meetings/transcript.py:2765`), and where the vent channel cannot be minted at all.

The cost is measured, and it reproduced digit for digit three times — the two blind
finders, the adversarial verifier, and again in this contract's own census over the
committed bytes. On `replays/ml_corpus/9p2i` the re-derivation loses 43 of the 120
recorded non-vent flags and mints 46 the game never had; 61 of the 476 corpus meetings
carry a different flag id-set than the one recorded (12.8%); and the whole
`alibi_vs_sighting` STRONG cell inverts, 0 recorded against 8 re-derived. On
`replays/samples/9p2i` it loses 19 and mints 9. The consumers are not diagnostics: this
census is the `flags_per_meeting` Layer-1 selection floor, the referee's supply gauge,
the `contradictions_by_subject` map the watchability D2 leg reads, the genuine-class
census in `vote_correctness`, and — the one that decides the phase — the
`flags_minted` label the conviction model is fit on. A label wrong on 12.8% of rows,
with a whole STRONG class inverted, is fit noise the model will chase, and 21.17 re-fits
on it. That is why this lands in Wave 1b, before the record and before the re-ground.

The repair is to read the record. It is not a preference: reconstruction provably cannot
reach the same answer. `tests/_helpers/committed.py:135-141` — the repo's own best
inversion, written at the baseline-7 record — states that `vent_witness_records` embeds a
tick the replay drops and that the movement channel "is not recoverable at all", and
`audits/audit-phase-20-baseline-7.md:798-806` prices that loss: the inverting walk
recovers 598 of 668 meetings exactly and 70 diverge on the movement channel alone. So a
threaded re-derivation would swap one counterfactual for a smaller one. The recorded
`contradictions` array on every meeting row is the byte-exact output of the production
call that held all four channels, and both fix sketches converge on it (B-6 collation
note at :563). Reading it makes the instruments exact rather than approximately less
wrong, and it is what the task title claims.

One structural rule keeps the change small: the recorded read is filtered to
`kind != "vent_sighting"` at every site that today re-derives. The modules already model
the census as two disjoint sources — the transcript census plus
`_persisted_vent_flag_count` (`eval/watchability.py:2000-2012`), and the
`flags_minted == rederived_flags + persisted_vent_flags` validator at
`training/conviction/dataset.py:303`. Keeping that decomposition means only the content
of one term changes, the vent term is never double-counted, and every corrected pin is
plain arithmetic a reader can check: recorded total minus recorded vent.

B-10 lands on the same surface, and its two surviving items are both about that
decomposition. First, `_supply_gauge_values`'s docstring (`eval/watchability.py:2062`)
says the merged persisted-vent component is "Zero on the committed v4 sets (no vent
turns)" — a scoped baseline-2-era sentence now read as a general claim, and false on
these bytes, where vent flags are 92 of 144 on `samples/9p2i` and 308 of 428 on the fit
corpus. The same module contradicts it 1,170 lines earlier at :890-892. Second,
`flags_per_meeting` is one merged number, so a candidate could clear the evidence floor
by minting vent sightings while its deduction-flag supply collapsed to nothing. The
verifier is explicit that the composition is NOT undisclosed — the pin comments at
:850-852 and :787-789 and the record audit's §8 table all publish the split — so the
work is a floor on each component, decided now, before `BAKEOFF_BASELINE_ID` moves to
this block at 21.17. `eval/watchability.py:269-272`'s companion claim goes in the same
pass: it asserts that on the committed set "recorded == re-derived, verified by the
parity test", and neither half holds — the identity is false on 61 of 476 corpus
meetings, and the only parity test in the file is a geomean roll-up that never compares
flag identity.

The record these instruments read is baseline 7, which is canon by explicit owner
override of a FINDING verdict — bars 1 and 2 were missed. Nothing here re-opens that:
this task changes what the gauges read, never what they demand. Every corrected pin is
the same bytes measured correctly, so the baseline still passes its own floors at exact
equality, and no target moves. The committed `tournament-eval-report.json` sidecars were
built by the old census and are NOT rebuilt here — they are outputs of a record, and
21.15 rebuilds them, which is why 21.15 depends on this task.

**Files in scope:**
- eval/meeting_quality.py; (the recorded-census reader; the three call sites at :1798, :1982, :2382 read it; `compute_supply_gauges`'s docstring stops describing a re-derivation)
- eval/watchability.py; (:1470 `contradictions_by_subject` off the recorded non-vent flags; the :268-272 identity claim removed; the :2062 stale sentence corrected; the two component floors on the baseline-7 block; `_persisted_vent_flag_count`'s docstring restated now that its sibling reads the record)
- eval/vote_correctness.py; (:595 genuine-class census off the recorded flags; the FROZEN weak-reason substring comment at :592-595 is preserved verbatim — the search is unchanged, only its input)
- training/conviction/dataset.py; (:491 the mirrored label off the recorded non-vent census; the module docstring at :78-85 and the row docstring at :265-267 corrected; the disjointness validator at :303 unchanged and still true)
- tests/eval/test_watchability.py; (the re-derived gauge pins at :737-742; the component-floor tests and their planted case; the frozen-parity measurement recorded)
- tests/eval/test_meeting_quality.py; (the census reader's own coverage)
- tests/eval/test_vote_correctness.py; (the genuine-class census on the corrected input — `test_committed_9p2i_report_pins_the_successor_instrument` moves: the recorded `alibi_vs_sighting` flags surviving the three frozen weak-reason exclusions are 1 in 1 meeting against the re-derivation's 15 in 10, so the genuine-class and supplied-channel cells drop hard and are re-pinned in the file's existing `# was N` style)
- tests/eval/test_gate_spec_metrics.py; (`compute_supply_gauges` folds and their fail-loud validators, :679-956; PLUS the committed-bytes pins this task moves and must re-derive in the file's existing `# was N` style — `test_supply_gauges_read_the_corrected_instrument`'s census at :958-967, `test_multi_signal_conversion_reads_18_of_64`'s split at :938-942, and `test_committed_ejections_decompose_as_the_w2_baseline` at :921-924, which reads the regenerated W2 fixture below)
- tests/fixtures/phase10/corrected_w2_baseline.json; (REGENERATED, never hand-edited — the CURRENT-era W2 baseline whose byte-identical re-derivation `test_corrected_w2_baseline_matches_a_rederivation` pins at :969-989; its `supply_gauges`, `multi_signal_conversion` and `impostor_ejection_channels` blocks all move with the corrected census, because `scripts/build_sample_report.py::corrected_baseline_from_report` is built from `compute_supply_gauges` at :386 and `decompose_ejection_channels` at :392-396. The frozen W0/W1 anchor fixtures are NOT regenerated)
- tests/eval/test_gate_metrics.py; (`test_committed_9p2i_report_pins_the_audited_gate_metrics` reads `compute_gate_metrics`, whose sub-gate shelter census is the :1798 site — its genuine-class, supplied-channel and survival-partition pins re-derive)
- tests/eval/test_watchability_reanchor.py; (`test_fsm_baseline_sets_pass_at_exact_equality_under_the_reanchor` and `test_remeasured_corpus_sets_at_baseline6_referee_verdicts` both read `flags_per_meeting` off the corrected census)
- tests/scripts/test_measure_baseline_cli.py; (`test_9p2i_reproduces_baseline_6_exactly` reproduces the CLI's gauge row and moves with the census)
- tests/training/test_conviction_model.py; (`test_flag_labels_reproduce_the_referee_census` at :257 stays integer-exact with both sides moved; `test_corpus_census_pins` at :775 re-derived)
- tests/eval/test_recorded_flag_census.py; (new: the structural gate that no eval or training module re-derives a recorded meeting's flags, with its planted case)
- tests/scripts/test_verify_ml_evidence.py; (the corpus-dependent "conviction flag-count Spearman" recompute pin at :417 re-derived — 0.6991081… → 0.7145778975…, the fit gets BETTER on the corrected label; the row itself, scripts/verify_ml_evidence.py:1554-1566, is unchanged)

**Files NOT in scope:**
- meetings/transcript.py, meetings/manager.py (the detector and the production call site are correct today — this task changes only who reads what they produced; a detector edit here would move recorded bytes and is the one thing **Record impact: none** forbids)
- replays/ (no recorded byte moves; `bash scripts/verify_samples.sh` is the proof, not an output — and the committed `tournament-eval-report.json` sidecars are rebuilt at 21.15, never here)
- experiments/lab/results-rubric-geomean.json, experiments/lab/rubric_score.py (the frozen 15.2 cross-implementation fixture and the lab scorer that produced it; the parity pin is measured here and preserved, never regenerated — a fixture rebuild is a record-side action)
- audits/workflows/extract_gameplay_facts.py (:532-560 already threads `trigger_kind` and an inverted vent channel; its own "recorded == re-derived" docstring claim at :539-541 is the same false class and is REPORTED in the PR, not edited — the extractor feeds the frozen lab fixture, and moving it would move that fixture)
- eval/funnel.py, eval/deception_instruments.py (read as feasibility evidence; their `sighting_records` calls go to `grounded_vouch_subjects`, not to the detector — the verifier's precision note 2)
- training/bakeoff/harness.py (`BAKEOFF_BASELINE_ID` stays `baseline-6`; §10.2 declares that value correct today and 21.17 owns the move)
- training/conviction/model.py, training/conviction/fidelity.py, training/artifacts/ (no fit runs here and no artifact is re-stamped; the label moves, the committed model does not, and 21.17 re-fits)
- eval/watchability.py:908-914 (the stale `BAKEOFF_BASELINE_ID` comment block is B-47 and belongs to Task 21.17, which moves the constant it describes — left untouched here so the note and its value change in one commit; see the orchestrator note in the PR body about the file-level ordering this implies)

**Definition of done:**
- [ ] One home for the census: a single documented reader in `eval/meeting_quality.py` returns a meeting's RECORDED contradiction flags filtered to `kind != "vent_sighting"`, takes the meeting row rather than a transcript so it cannot be handed a record-free object by accident, and states in its docstring that the vent term rides `_persisted_vent_flag_count` and that the two sets stay disjoint by construction.
- [ ] `eval/meeting_quality.py` uses it at all three sites — :2382 (`compute_supply_gauges`), :1798 (the sub-gate shelter census) and :1982 (the per-ejection channel decomposition) — and no roster-only `detect_contradictions` call remains in the module; the docstrings at :1711-1712 and :1798's region stop saying the flags are re-derived.
- [ ] `eval/watchability.py:1470` builds `contradictions_by_subject` from the same recorded non-vent flags with the strong/weak bit read from each recorded flag's own description via the unchanged `is_weak_contradiction`, so the D2 leg's `m.contradictions_by_subject or m.persisted_vent_flags` composition at :1713 keeps exactly its present meaning and no vent flag enters both terms.
- [ ] `eval/vote_correctness.py:595` reads the recorded flags; the FROZEN Phase-19 comment and the three weak-reason substring exclusions are byte-identical afterwards, and the PR states the resulting `genuine_class_conversion` cells before and after.
- [ ] `training/conviction/dataset.py:491` reads the recorded non-vent census; `flags_minted` becomes exactly `len(entry.contradictions)` on every row; the :303 validator is unchanged and still passes; and the module docstring at :78-85 no longer describes the label as transcript-re-derived. The field name `rederived_flags` is deliberately NOT renamed — the row is the frozen 18.15 artifact contract and the keyword is constructed in three test modules owned by parallel Wave-1b tasks; the docstring says what the field now holds, and the PR names the rename as routed, not forgotten.
- [ ] `tests/training/test_conviction_model.py::test_flag_labels_reproduce_the_referee_census` stays integer-exact with BOTH sides moved (it is the mirror invariant, not a value pin), and `test_corpus_census_pins` re-derives `flags_minted_total` from 431 to 428 with the delta explained in a trailing comment in the file's existing `# was N` style.
- [ ] The stale docstring goes: `eval/watchability.py:2062`'s "Zero on the committed v4 sets (no vent turns)" sentence is replaced by the measured split on the committed bytes, and `:268-272`'s "on the committed set recorded == re-derived, verified by the parity test" is deleted rather than softened — the map is now READ from the record, so the sentence that made a false identity claim has nothing left to claim.
- [ ] `flags_per_meeting` splits: `SupplyFloors` (`eval/watchability.py:429`) gains two optional component pins — the transcript-flag rate and the persisted-vent rate — populated on the baseline-7 block only, with `evaluate_supply_floors` emitting a gauge row per populated component and skipping absent ones, so blocks whose bytes left the tree stay evaluable exactly as today.
- [ ] The split can fail (craft rule 2): a planted case in `tests/eval/test_watchability.py` drives a candidate whose MERGED `flags_per_meeting` clears the baseline-7 floor entirely on persisted vent flags while its transcript component collapses below the component pin, and asserts `supply_floors_passed is False` naming the component row that bit — the exact Goodhart shape B-10 describes.
- [ ] The four censuses are re-derived from committed bytes, not asserted from the register, and the command's output is pasted in the PR: `samples/9p2i` 144/152 = 0.9473684210526315 (92 vent + 52 transcript, was 134/152 = 0.881578947368421), `samples/4p1i` 20/40 = 0.5 UNCHANGED (20 vent + 0 transcript), `ml_corpus/9p2i` 428/432 = 0.9907407407407407 (308 + 120, was 431/432), `ml_corpus/4p1i` 29/44 = 0.6590909090909091 UNCHANGED (28 + 1); the baseline-7 pin comment at :850-852 and the pin at :866-874 both carry the new numerator, and the `testimony_backed_conversion` pin 80/115 = 0.6956521739130435 is untouched — at the baseline the flags ratio is exactly 1.0, so the population-relative derivation still lands on the pin and the set still passes at equality.
- [ ] `tests/eval/test_watchability.py::test_baseline_7_floor_pins_equal_the_measured_bytes` (the :721-755 block, whose `expected` fraction table is at :734-745) asserts the new fractions and the new gauge-name set, and `test_a_gauge_below_a_baseline_7_floor_is_rejected` (:758) keeps biting on the conversion axis with its flag census held at the corrected pin.
- [ ] The frozen geomean parity pin is MEASURED, not assumed: run `tests/eval/test_watchability.py::test_historical_15_2_geomean_parity_frozen_pin_on_9p2i` after the :1470 change and record the result in the PR. If it stays green, say so and change nothing. If it moves, `_meeting_facts` / `_game_facts` gain one keyword-only frozen-basis flag, set ONLY by the test's `_score_committed_set` helper (:80-122) alongside the existing `historical_15_2`, so the pre-15.19 spec keeps reproducing the 2026 lab artifact it exists to reproduce while the live referee reads the record; the flag's docstring says that in one line, and the live path never sets it.
- [ ] A gate that cannot be re-opened: `tests/eval/test_recorded_flag_census.py` walks `eval/` and `training/` with `ast` — the `tests/meetings/test_lever_registry.py` precedent — and fails on any call to `detect_contradictions` whose keywords are `roster` alone, with an allowlist that is empty at HEAD or carries only the frozen-basis site if the previous item created one; a planted module fixture in a temp tree proves the walk bites.
- [ ] The PR Summary states the blast radius from a fresh grep, in the shape craft rule 6 asks for: which modules call the detector, which now read the record, and that `scripts/counterfactual_phase20.py` and `audits/workflows/extract_gameplay_facts.py` are deliberately left re-deriving because a counterfactual is exactly what they want — plus the one-line note that the extractor's own "recorded == re-derived" docstring claim (:539-541) is the same false class, reported and routed, not silently fixed inside a task that must not move the frozen lab fixture.
- [ ] The current-era W2 baseline fixture is REGENERATED, never hand-edited: `uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --baseline-out tests/fixtures/phase10/corrected_w2_baseline.json` (the command its own test names at :972-978) re-derives `tests/fixtures/phase10/corrected_w2_baseline.json` so `test_corrected_w2_baseline_matches_a_rederivation` stays byte-exact, and the PR quotes every cell it moves — the `supply_gauges` census, the `multi_signal_conversion` split, and the one `impostor_ejection_channels` site that gains `contradiction_flag`. The frozen W0/W1 anchor fixtures are pre-record A/B anchors and are NOT regenerated.
- [ ] The pins OUTSIDE the five Measurement modules move with the census and are re-derived from bytes rather than deleted or weakened, each with a trailing `# was N` comment in its own file's existing style: `tests/eval/test_gate_metrics.py::test_committed_9p2i_report_pins_the_audited_gate_metrics`, `tests/eval/test_watchability_reanchor.py`'s two committed-set verdicts, `tests/scripts/test_measure_baseline_cli.py::test_9p2i_reproduces_baseline_6_exactly`, and — inside `tests/training/test_conviction_model.py` — `test_the_committed_verdict_is_baseline6_and_the_weights_still_clear_the_bar`'s RE-DERIVED `flag_spearman` half, whose committed-verdict-is-baseline-6 half must NOT move (that is the pin 21.8 leans on).
- [ ] `bash scripts/verify_samples.sh` reports 100/100 committed samples reconstructing byte-identically, and the PR states the conclusion it supports: this task moved no recorded byte, which is what **Record impact: none** means here.
- [ ] `uv run pytest -m campaign -q` is run and the PR records either that no pinned ML value moved or exactly which moved and why; the committed conviction artifact is NOT re-fit, and `test_committed_artifact_round_trips_and_the_refit_no_longer_matches` (:792) must stay green on its "the refit DIVERGES" assertion — a corrected label makes the divergence larger, never smaller.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

BLOCK 1 — measure first, then change. Before editing anything, re-derive the four
censuses and paste them into the PR draft. A json walk over each set's meeting rows
counting `contradictions` by kind reproduces the register exactly (it was re-run at
`4002f19b` while this contract was written): `samples/9p2i` 144 total / 92 vent,
`samples/4p1i` 20 / 20, `ml_corpus/9p2i` 428 / 308, `ml_corpus/4p1i` 29 / 28. These are
the numbers every corrected pin is arithmetic over; deriving them once, from bytes,
means no later step quotes a memory. Then run the five test modules in scope at HEAD so
you know which assertions were green before you touched them.

BLOCK 2 — one reader, not four patches. Put the recorded-census helper in
`eval/meeting_quality.py` beside `compute_supply_gauges` (:2351) and import it from the
other three modules; `eval/vote_correctness.py:564` already documents that it and the
supply gauge "read the identical" definition, so a shared home turns that sentence from
a promise into a mechanism. Take the meeting row, return the recorded flags filtered to
`kind != "vent_sighting"`, and keep the return type the same tuple of
`ContradictionRef` the detector returns so every downstream loop — the strong/weak
banding, the `flag.subjects` fan-out, `vote_correctness`'s substring exclusions — is
unchanged below the call. `training/conviction/dataset.py` must NOT import it: the
committed firewall test at `tests/training/test_conviction_model.py:145` fails on any
`eval.*` import from that package, so mirror the two-line filter there and say in the
docstring that it is mirrored, the convention that module already follows for the label.

BLOCK 3 — the disjointness is the safety rail. Every site that today merges a
transcript census with `_persisted_vent_flag_count` keeps doing exactly that; only the
first term's source changes. That is why the vent filter is not optional: drop it and
`flags_minted` double-counts 92 flags on `samples/9p2i`, the :303 validator fires, and
the referee's floor inflates by 60% with no reader able to see why. `vote_correctness`
filters `kind == "alibi_vs_sighting"` before anything else, so the vent exclusion is
structurally redundant there — apply it anyway, through the shared reader, so no site
carries a local rule.

BLOCK 4 — the component floors. Add two `FloorPin | None` fields to `SupplyFloors` and
default them to `None`; only the baseline-7 block gets values, because the earlier
blocks' sample sets are no longer in the tree and their pins were measured under the old
merge — annotate each of those blocks with one line saying so rather than inventing a
component for bytes nobody can re-derive. `evaluate_supply_floors` (:961) already skips
a `None` conversion pin as vacuously cleared; give the components the same shape so
`_BASELINE_SUPPLY_FLOORS` stays uniform. Leave `population_relative_conversion_floor`
alone: it reads the MERGED `flags_per_meeting`, the baseline's ratio is exactly 1.0 at
the pin, and touching it would move a target this task promises not to move.

BLOCK 5 — the planted case is the point, not the pin. Build the starving candidate as a
`SupplyGaugeValues` literal in the style already at :757-780: merged flags at or above
the baseline-7 floor, `persisted_vent_flags` carrying nearly all of them, the transcript
component below its own pin. Assert `passed is False` AND assert which row failed, so a
future change that silently drops the component gauges turns this test red instead of
leaving it vacuously green. Then perturb it once in the other direction — the same
merged rate with a healthy transcript component — and assert it passes, which is what
proves the component is doing the work rather than the merged floor.

BLOCK 6 — the frozen parity path. Run the parity test before you decide anything about
it. `_score_committed_set` (:80-122) replicates `compute_watchability`'s facts assembly
so the frozen spec can be scored without exposing a parity-only mode on the public
referee; if the pin moves, extend that same seam — a keyword-only flag on `_game_facts`
and `_meeting_facts`, threaded from that helper alone — and never by regenerating
`experiments/lab/results-rubric-geomean.json`, which is a record-side artifact and whose
rebuild would drag `audits/workflows/extract_gameplay_facts.py` in behind it. Say in one
docstring line why history keeps the old basis: the pin's job is cross-implementation
agreement on a spec frozen in 2026, and its own docstring at :133 already says it "pins
history and must never gate a champion".

BLOCK 7 — the structural gate. `tests/meetings/test_lever_registry.py` is the working
precedent for an `ast` walk over source directories that fails on a shape rather than a
value; copy its traversal and its temp-tree planted case. Match `ast.Call` nodes whose
func resolves to `detect_contradictions` and whose keyword set is exactly `{"roster"}`,
restricted to `eval/` and `training/`, so the counterfactual script and the audit
workflow — both of which want a counterfactual and both of which live elsewhere — are
outside the walk by construction rather than by an allowlist entry that will rot.

## Public types this task introduces
- `eval.meeting_quality.recorded_contradiction_flags`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This task changes what five instruments measure without changing one recorded byte, and
the whole risk surface is the gap between those two statements.

Risk 1 — the double count. The single largest failure mode is dropping the
`vent_sighting` filter from the recorded read. On `samples/9p2i` that adds 92 flags to a
census already merging them, inflating `flags_per_meeting` from 144/152 to 236/152,
tripping the conviction row's own disjointness validator, and re-basing a selection
floor on a term counted twice. The filter belongs in the one shared reader, never at the
four call sites, and the conviction mirror's :303 validator is the tripwire that catches
it in `training/` where the firewall forbids importing the reader.

Risk 2 — the frozen parity pin is not a value pin. It asserts that this module still
reproduces an independent lab implementation on a spec frozen in 2026, per-seed, to
1e-6, across eleven score components. If it moves and the response is to regenerate the
fixture, the test stops being cross-implementation evidence and becomes a snapshot of
this module against itself — the exact evidentiary collapse Task 20.26 Risk 3 refused for
the 19.11 fixtures. Measure, then preserve the frozen basis; never rebuild the artifact.

Risk 3 — the conviction label moves and nothing here re-fits it. After this task the
committed conviction model was fit on labels the corrected census no longer produces,
which is a KNOWN and declared state: `audits/audit-phase-20-baseline-7.md` §10.2 already
routes the re-fit, and the tripwire at `tests/training/test_conviction_model.py:792`
exists to assert the divergence rather than hide it. The failure mode is a well-meant
re-fit inside this PR — it would re-stamp an artifact whose fit corpus 21.15 is about to
replace, and it would consume the §10.2 re-ground that 21.17 owns. No fit runs here.

Risk 4 — the downstream sidecars are now behind the code. The committed
`tournament-eval-report.json` files under `replays/samples/` were built with the old
census and are not regenerated here; rebuilding them would move committed bytes and
contradict this contract's declared record impact. 21.15 rebuilds them, which is exactly
why the DAG has 21.15 depend on this task. The PR must say this in one line so a reader
comparing a corrected gauge against a committed sidecar knows which one is stale and
why.

Risk 5 — file-level contention in Wave 1b. `eval/watchability.py` is also named by
21.9 (B-9's first-hand vocabulary sits at :1353) and, from Wave 1d, by 21.17 (B-47's stale
`BAKEOFF_BASELINE_ID` comment block at :908-914, routed there at assembly so it travels
with the constant), and `training/conviction/dataset.py` sits
next to 21.8's conviction work. This contract leaves both of those specific lines
untouched so the other contracts keep their items intact, but the collision is at the
FILE level: `scripts/validate_task_docs.py::validate_parallel_file_scope` fails
assembly when two tasks in one phase list the same file and neither depends on the
other. The orchestrator resolves it at assembly by ordering, not this task by widening.
ONE such collision needed an orchestrator ruling and HAS one, recorded at the day-one
reverification (`audits/audit-phase-21-planning.md` §2.2). Correcting the census moves the
`conviction flag-count Spearman` recompute row, whose measured prefix is pinned at
`tests/scripts/test_verify_ml_evidence.py:417` — `0.6991081` becomes `0.7145778975`, i.e.
the fit gets BETTER on the corrected label. That file is listed by 21.8, which reaches
this task through 21.9 and was therefore already ordered, and ALSO by 21.10, whose
dependency was 21.3 alone. The ruling: **21.10 now depends on 21.7** (among others), so
the pair is ordered and the file JOINS this task's Files-in-scope above, where the
one-line re-pin lands. `validate_parallel_file_scope` is satisfied by the edge, not by
omission — which matters, because omitting the file would have left this PR's own
`uv run pytest` red. Re-pin the row from bytes in the file's existing style; do not
weaken it, and do not touch the row's producer at
`scripts/verify_ml_evidence.py:1554-1566`, which is unchanged by this task.

Risk 6 — the gate that cannot fail. A structural walk that matches nothing, or an
allowlist that grows to cover the sites it was written to forbid, is prose. The planted
temp-tree case is what makes it a gate; it ships in the same commit, and the allowlist
starts empty.

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
Open a PR from branch `phase-21-grounded-instruments` with a title like `task 21.7: the instruments read the recorded game: the flag census comes off the record, not a re-derivation`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing B-6 [CONFIRMED, P1 — the centrepiece] and B-10 [ADJUSTED, P2] of `audits/review-2026-08-26/B/collated-findings.md` (B-6 at :477-563, both merged finder blocks plus the verifier's exact re-run and its two precision notes; B-10 at :748-791, including the verifier's WHY-ADJUSTED paragraph that refutes the "composition unstated" framing and re-homes the surviving items — the stale docstring sentence and the gauge split — to this contract); the declared carry this task executes, `tasks/phase-20.md:4251-4260` (Task 20.26 Integration risk 4: "the phase's own instruments must read RECORDED flags or reconstruct the records, never the record-free re-derivation, or they will measure the old substrate on new bytes"); `audits/audit-phase-20-baseline-7.md:789-812` §10.3, which declares the same loss for three TEST mirrors and names no live consumer, and :624-628 §8, whose gauge table publishes the split this task re-derives. Anchors re-verified at HEAD `4002f19b` (the registers were written at `d8ec0a1c`, its parent; every line below was re-read, not carried): the four roster-only call sites reproduce exactly — `training/conviction/dataset.py:491`, `eval/meeting_quality.py:2382`, `eval/watchability.py:1470`, `eval/vote_correctness.py:595`; production threads all four channels at `meetings/manager.py:1225-1232`; the signature with three defaulted-None record channels plus `trigger_kind` is `meetings/transcript.py:1490-1500`. TWO FURTHER SITES the register did not name, both inside a module already in scope, found by a fresh repo-wide grep: `eval/meeting_quality.py:1798` (the sub-gate shelter census inside `compute_gate_metrics`) and `:1982` (the per-ejection channel decomposition) — same defect, same bytes, handled here. Structure anchors: `eval/watchability.py:429` `SupplyFloors`, :538 `_BASELINE_SUPPLY_FLOORS`, :841-901 the baseline-7 block (:850-852 the 9p2i split comment, :866-874 the pins, :890-892 the in-module contradiction of the stale docstring), :914 `_DEFAULT_BASELINE_ID`, :961 `evaluate_supply_floors`, :1400 `_meeting_facts`, :1976 `_game_facts`, :2000-2012 `_persisted_vent_flag_count`, :2050-2065 `_supply_gauge_values` with the false sentence at :2062, :268-272 the false identity claim; `eval/meeting_quality.py:2351` `compute_supply_gauges`; `training/conviction/dataset.py:255-310` the row schema and its disjointness validator at :303. The in-repo reconstructions the fix sketch cites: `eval/funnel.py:1230-1263`, `scripts/counterfactual_phase20.py:744-787` (three channels threaded, `off_flags_match_recorded` self-checked at :784-785 — it does NOT thread `trigger_kind`), `tests/_helpers/committed.py:122-166`, `audits/workflows/extract_gameplay_facts.py:532-560`.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
