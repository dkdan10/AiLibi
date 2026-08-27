# Agent Prompt — 21.8 The fit reads honest rows: rewritten targets, memory at speech time, a precision axis, and the missing fingerprints

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.8 — The fit reads honest rows: rewritten targets, memory at speech time, a precision axis, and the missing fingerprints, anchored to A-26 [ADJUSTED, P2, defect] — audits/review-2026-08-26/A/collated-findings.md §A-26 (the fit-side marker gap; the verifier's three corrections BIND this contract: the exclusion list is a DECLARED scope, not a contradicted ruling; the actionable residue is the 120 under-gate redirects, which leave the EJECT decision label authored and rewrite only the TARGET, i.e. they poison the RANKING channel the declared rationale never reaches; severity P1→P2 because the committed fit is baseline-6 and no shipped number is currently wrong). B-40 [CONFIRMED, P2, defect] — audits/review-2026-08-26/B/collated-findings.md §B-40 (I-4 reads end-of-game memory; the verifier's scope narrowing BINDS: the look-ahead is bounded by the ±2 tolerance, and hearsay cannot contaminate the cell because `_supports_placement` admits only first-hand rows). B-15 [ADJUSTED, P2, design-limitation] — §B-15 (recall-only axis 2; the verifier's corrections BIND: the recall-only choice is SPECIFIED with a written rationale, precision/accuracy/confusion are already reported beside it, and a degenerate head passes AXIS 2 only — the conjunction still needs the Spearman axis; the residual value is the undeclared asymmetry with the surrogate's own trivial-constant axis, and the fix must be PRE-REGISTERED because the verdict is taken on the FIRST held-out evaluation). B-16 [ADJUSTED, P2, design-limitation] — §B-16 (no conviction fit-corpus record; the verifier's correction BINDS: every path that actually SCORES is fenced today, transitively through the surrogate leg, so the live gap is a missing provenance RECORD plus an unmeasured transitivity assumption, not an unfenced scoring path). B-17 [ADJUSTED, P3, design-limitation] — §B-17 (no committed surrogate verdict and no loader that refuses a NO-GO surrogate; the verifier's correction BINDS: "enforced by convention" is overstated — the value, the consequence mapping and the recorded consequence are all pinned by green default-tier tests, and only the WIRING is ungated). Anchors re-verified at HEAD 4002f19b by reading the files: training/surrogate/dataset.py:170-199 (`_MARKER_REPR_VALUE`, `_UNCITED_ZERO_FLAG_MARKER_PATTERN`, `_ballot_is_coerced_skip`), :133 (the single imported marker literal), :306-313 (the `ballot_coerced_skip` column and its comment), :997 (the one construction site); training/surrogate/ballots.py:195-205 (`BallotExample` — one `target` label serves ranking AND decision), :295-307 (`ballot_example_from_row`), :798-831 and :930-948 (the two fit paths, both filtering on `not row.ballot_coerced_skip` and nothing else); api/replay_loader.py:253-261 (`_TARGET_REWRITE_LABELS`, the canonical five-member class, with :244-252 stating why the two citation-only labels are deliberately excluded), :2878-2886 (`_BALLOT_PREFIX_MARKERS`, the six label/marker pairs), :2899-2917 (`_marker_pattern` and the precompiled chain), :2973-3003 (`_parse_rewrite_reasons`, the front-to-back stacked strip); meetings/manager.py:200, :211, :274, :296, :309, :326, :354 (the seven audit-marker literals) and meetings/voting.py:90 (`INVALID_VOTE_TARGET_MARKER`); eval/evidence_honesty.py:308-317 (the I-4 definition, "whether the speaker could have seen it"), :1383-1437 (the walk loop and its `finally`), :1392-1393 (`_perceive_tick` mutating `memories`), :1415-1429 (the MeetingOpened branch that builds `_MeetingFacts`), :1450 (`_fold_meetings` running AFTER the whole walk), :1165-1172 (`_MeetingFacts`), :2081 (`_fold_flags`), :2151 and :2157 (the two fold call sites), :2307-2341 (`_supports_placement`), :2344-2370 (`_fold_grounding`, scanning `memory.recent(since_tick=0)`), :2373-2400 (`_fold_movement_origin`, same whole-log scan); agents/memory/episodic.py:77-150 (`MemoryStore.__len__`, `append`'s non-decreasing-tick guard, `recent`); training/conviction/fidelity.py:15-24 (the recall-only rationale), :73-74 (the two bar constants), :141-179 (`ConvictionFidelityReport` including `conversion_precision` / `conversion_accuracy` / the confusion census), :280-292 (where they are computed), :301-343 (`ConvictionGoVerdict`), :346-386 (`decide_conviction_go`), :388-412 (the writer and loader); training/artifacts/conviction/verdict.json (18 keys, GO, baseline-6 numbers, no accuracy or precision field); training/conviction/model.py:452-479 (`load_conviction_model_artifact` verifies the sha sidecar and nothing else), :481-492 (`load_conviction_staleness_cap`); training/composed_runner.py:277-282 (the only `corpus_dir` pass-through, into the surrogate loader), :288-315 (the conviction block: sha, cap, GO — nothing corpus-related); training/surrogate/runner.py:133 (`FIT_CORPUS_FILENAME`), :365-386 (`SurrogateFitCorpus`), :388-416 (`fit_corpus_fingerprint`), :418-429 (`load_fit_corpus_record`, whose message names "the surrogate" though the loader is generic over an artifact dir), :432-469 (`load_surrogate_runner_factory` and its fence docstring), :523-533 (`__all__`); training/surrogate/fidelity.py:895-941 (`GoNoGoVerdict` and its three axes, the third being `always_eject_baseline`, the trivial constant the conviction bar lacks) and :942 + :1037 (`decide_go_no_go`'s definition and its `__all__` entry — no production call site anywhere); training/bakeoff/harness.py:733-790 (`_load_conviction_bundle`, no corpus parameter), :1437 (`surrogate_artifact_dir` defaulting unconditionally); scripts/verify_ml_evidence.py:114-116 (the three artifact dirs), :1554-1566 (`_CORPUS_DEPENDENT_RECOMPUTE_ROWS`, nine names, none of them surrogate-verdict), :1577-1615 (`_grounding_row` and its one-question docstring), :1925-1940 (the amnesty downgrade); tests/training/test_surrogate_runner.py:496 and :792 (the two default-tier pins B-17's verifier adds), tests/training/test_bakeoff_harness.py:1758 (the AST pin that every harness surrogate load wires `corpus_dir`), tests/training/test_conviction_model.py:860 (the committed-verdict-is-baseline-6 pin), tests/eval/test_evidence_honesty.py:51-76 (the private folds the module already imports), :1346-1365 (`test_i4_grounded_sighting_side_pins`, `sides == [0, 0, 0, 0]`), :1454-1472 (the I-7 pins, `backed_by_move_line == 16`); tests/training/_regrounding.py:1-21 (the named interim seam and what it is careful not to be); training/reports/report-ballot-surrogate.md:207-222 (the declared per-kind exclusion list); audits/audit-phase-20-baseline-7.md §10.2 (the re-ground this task pre-registers for) and audits/audit-phase-20-close.md:33 and :357 (baseline 7 is canon by explicit owner override of a FINDING verdict — bars 1 and 2 were missed).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-fit-hygiene`
**Depends on:** 21.9, 21.10, 21.16
**Section refs:** A-26 [ADJUSTED, P2, defect] — audits/review-2026-08-26/A/collated-findings.md §A-26 (the fit-side marker gap; the verifier's three corrections BIND this contract: the exclusion list is a DECLARED scope, not a contradicted ruling; the actionable residue is the 120 under-gate redirects, which leave the EJECT decision label authored and rewrite only the TARGET, i.e. they poison the RANKING channel the declared rationale never reaches; severity P1→P2 because the committed fit is baseline-6 and no shipped number is currently wrong). B-40 [CONFIRMED, P2, defect] — audits/review-2026-08-26/B/collated-findings.md §B-40 (I-4 reads end-of-game memory; the verifier's scope narrowing BINDS: the look-ahead is bounded by the ±2 tolerance, and hearsay cannot contaminate the cell because `_supports_placement` admits only first-hand rows). B-15 [ADJUSTED, P2, design-limitation] — §B-15 (recall-only axis 2; the verifier's corrections BIND: the recall-only choice is SPECIFIED with a written rationale, precision/accuracy/confusion are already reported beside it, and a degenerate head passes AXIS 2 only — the conjunction still needs the Spearman axis; the residual value is the undeclared asymmetry with the surrogate's own trivial-constant axis, and the fix must be PRE-REGISTERED because the verdict is taken on the FIRST held-out evaluation). B-16 [ADJUSTED, P2, design-limitation] — §B-16 (no conviction fit-corpus record; the verifier's correction BINDS: every path that actually SCORES is fenced today, transitively through the surrogate leg, so the live gap is a missing provenance RECORD plus an unmeasured transitivity assumption, not an unfenced scoring path). B-17 [ADJUSTED, P3, design-limitation] — §B-17 (no committed surrogate verdict and no loader that refuses a NO-GO surrogate; the verifier's correction BINDS: "enforced by convention" is overstated — the value, the consequence mapping and the recorded consequence are all pinned by green default-tier tests, and only the WIRING is ungated). Anchors re-verified at HEAD 4002f19b by reading the files: training/surrogate/dataset.py:170-199 (`_MARKER_REPR_VALUE`, `_UNCITED_ZERO_FLAG_MARKER_PATTERN`, `_ballot_is_coerced_skip`), :133 (the single imported marker literal), :306-313 (the `ballot_coerced_skip` column and its comment), :997 (the one construction site); training/surrogate/ballots.py:195-205 (`BallotExample` — one `target` label serves ranking AND decision), :295-307 (`ballot_example_from_row`), :798-831 and :930-948 (the two fit paths, both filtering on `not row.ballot_coerced_skip` and nothing else); api/replay_loader.py:253-261 (`_TARGET_REWRITE_LABELS`, the canonical five-member class, with :244-252 stating why the two citation-only labels are deliberately excluded), :2878-2886 (`_BALLOT_PREFIX_MARKERS`, the six label/marker pairs), :2899-2917 (`_marker_pattern` and the precompiled chain), :2973-3003 (`_parse_rewrite_reasons`, the front-to-back stacked strip); meetings/manager.py:200, :211, :274, :296, :309, :326, :354 (the seven audit-marker literals) and meetings/voting.py:90 (`INVALID_VOTE_TARGET_MARKER`); eval/evidence_honesty.py:308-317 (the I-4 definition, "whether the speaker could have seen it"), :1383-1437 (the walk loop and its `finally`), :1392-1393 (`_perceive_tick` mutating `memories`), :1415-1429 (the MeetingOpened branch that builds `_MeetingFacts`), :1450 (`_fold_meetings` running AFTER the whole walk), :1165-1172 (`_MeetingFacts`), :2081 (`_fold_flags`), :2151 and :2157 (the two fold call sites), :2307-2341 (`_supports_placement`), :2344-2370 (`_fold_grounding`, scanning `memory.recent(since_tick=0)`), :2373-2400 (`_fold_movement_origin`, same whole-log scan); agents/memory/episodic.py:77-150 (`MemoryStore.__len__`, `append`'s non-decreasing-tick guard, `recent`); training/conviction/fidelity.py:15-24 (the recall-only rationale), :73-74 (the two bar constants), :141-179 (`ConvictionFidelityReport` including `conversion_precision` / `conversion_accuracy` / the confusion census), :280-292 (where they are computed), :301-343 (`ConvictionGoVerdict`), :346-386 (`decide_conviction_go`), :388-412 (the writer and loader); training/artifacts/conviction/verdict.json (18 keys, GO, baseline-6 numbers, no accuracy or precision field); training/conviction/model.py:452-479 (`load_conviction_model_artifact` verifies the sha sidecar and nothing else), :481-492 (`load_conviction_staleness_cap`); training/composed_runner.py:277-282 (the only `corpus_dir` pass-through, into the surrogate loader), :288-315 (the conviction block: sha, cap, GO — nothing corpus-related); training/surrogate/runner.py:133 (`FIT_CORPUS_FILENAME`), :365-386 (`SurrogateFitCorpus`), :388-416 (`fit_corpus_fingerprint`), :418-429 (`load_fit_corpus_record`, whose message names "the surrogate" though the loader is generic over an artifact dir), :432-469 (`load_surrogate_runner_factory` and its fence docstring), :523-533 (`__all__`); training/surrogate/fidelity.py:895-941 (`GoNoGoVerdict` and its three axes, the third being `always_eject_baseline`, the trivial constant the conviction bar lacks) and :942 + :1037 (`decide_go_no_go`'s definition and its `__all__` entry — no production call site anywhere); training/bakeoff/harness.py:733-790 (`_load_conviction_bundle`, no corpus parameter), :1437 (`surrogate_artifact_dir` defaulting unconditionally); scripts/verify_ml_evidence.py:114-116 (the three artifact dirs), :1554-1566 (`_CORPUS_DEPENDENT_RECOMPUTE_ROWS`, nine names, none of them surrogate-verdict), :1577-1615 (`_grounding_row` and its one-question docstring), :1925-1940 (the amnesty downgrade); tests/training/test_surrogate_runner.py:496 and :792 (the two default-tier pins B-17's verifier adds), tests/training/test_bakeoff_harness.py:1758 (the AST pin that every harness surrogate load wires `corpus_dir`), tests/training/test_conviction_model.py:860 (the committed-verdict-is-baseline-6 pin), tests/eval/test_evidence_honesty.py:51-76 (the private folds the module already imports), :1346-1365 (`test_i4_grounded_sighting_side_pins`, `sides == [0, 0, 0, 0]`), :1454-1472 (the I-7 pins, `backed_by_move_line == 16`); tests/training/_regrounding.py:1-21 (the named interim seam and what it is careful not to be); training/reports/report-ballot-surrogate.md:207-222 (the declared per-kind exclusion list); audits/audit-phase-20-baseline-7.md §10.2 (the re-ground this task pre-registers for) and audits/audit-phase-20-close.md:33 and :357 (baseline 7 is canon by explicit owner override of a FINDING verdict — bars 1 and 2 were missed).
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run pytest tests/training/test_surrogate_dataset.py tests/training/test_surrogate_runner.py tests/training/test_conviction_model.py tests/training/test_composed_runner.py tests/eval/test_evidence_honesty.py tests/scripts/test_verify_ml_evidence.py -q` green; the census test reads 204 markers in 94 of 300 games and 150 target-rewritten ballots of 3,602 over the four committed sets, and the three committed flagged-row pins move together — `replays/ml_corpus/9p2i` 7 → 102 and `replays/ml_corpus/4p1i` 0 → 2 in both modules that pin it; `uv run python scripts/verify_ml_evidence.py --only recompute` exits as it does at HEAD with the new surrogate-verdict row present; the PR quotes the I-4 and I-7 cells before and after the memory-prefix bound, recomputed, not remembered.

Three ML instruments, one evidence instrument and one dataset builder are about to be re-ground on the
corrected corpus (Task 21.17, executing audits/audit-phase-20-baseline-7.md §10.2). Every item in this task is
a defect in what one of them READS or
in what their verdicts can distinguish, and every one of them is invisible today precisely because the fit is
frozen: the committed surrogate and conviction artifacts are baseline-6 fits sitting on a baseline-7 corpus,
and `tests/training/_regrounding.py` exists to say so out loud. That is the whole window. A hygiene fix that
lands after the re-fit is a second re-fit; a hygiene fix that lands before it is free.

The dataset builder reads a rewritten target as if the voter had chosen it. `_ballot_is_coerced_skip`
(training/surrogate/dataset.py:185-199) recognises exactly one audit marker — the J2 citation-gate coercion —
and the two fit paths filter on that one flag and nothing else (training/surrogate/ballots.py:831, :946). The
review's census, re-run for this contract over all four committed sets, reproduces to the digit: 3,602
recorded ballots carry 204 bracketed audit markers across 94 of 300 games — 120 `under-gate eject target …
redirected`, 27 `invalid primary_reason_observation_id … nulled`, 18 `teammate target … coerced to SKIP`, 18
vote-guard rationale redactions, 9 `invalid primary_reason_id … nulled`, 8 `uncited zero-flag eject target …
coerced to SKIP`, 4 `invalid target … normalized to SKIP`. Six of those are prefix markers the meeting layer
prepends; the redaction is a replacement body and belongs to the sibling ballot-render task, not this one.
150 of those ballots record a target the voter did
not author; 8 are already dropped; **142 ride into the fit** as the voter's own choice. The verifier's
correction is what makes this actionable and also what bounds it: the exclusion list is DECLARED, kind by
kind, in a committed report (training/reports/report-ballot-surrogate.md:218-222), and that declaration
reasons entirely about the SKIP DECISION label. The 120 under-gate redirects keep the authored EJECT decision
and rewrite only the target — the RANKING channel — which the stated rationale never reaches. And because
`BallotExample` carries one `target` field that serves both the ranking softmax and the SKIP alternative
(training/surrogate/ballots.py:195-205), there is no channel to poison in isolation: a rewritten target is a
poisoned label, full stop.

The repo already holds the canonical name for the class and it has five members, not one: `_TARGET_REWRITE_LABELS`
(api/replay_loader.py:253-261), defined as exactly "the labels under which a recorded ballot's TARGET is not the
voter's authored choice", with the two citation-only labels deliberately excluded because they null a reference
and leave the authored target intact. The display layer and the eval layer both handle all five; the training
layer handles one. This task closes that asymmetry with the repo's own definition rather than a new one, and
pins the two tables against each other so they cannot drift apart again.

The evidence-honesty instrument reads a memory the speaker did not yet hold. `_fold_meetings` runs after the
walk closes (eval/evidence_honesty.py:1450), so `_fold_grounding` scans `memory.recent(since_tick=0)` — the
whole game's log — for a row supporting a spoken sighting (:2358-2364), and admits any row within ±2 ticks
(:2367-2370). The cell's own definition at :308-317 says it measures "only whether the speaker could have seen
it". A perception acquired after the meeting is not that. The blast radius today is zero and independently
corroborated twice: every `alibi_vs_sighting` flag in all four committed sets is WEAK, so I-4 reads 0/0 and
`tests/eval/test_evidence_honesty.py:1359` pins `sides == [0, 0, 0, 0]`. That is exactly why it must be fixed
now and not later — the first lever that repopulates the STRONG class publishes an inflated grounded rate with
no earlier number to compare it against, and Wave 2 of this phase is a lever wave. The verifier's narrowing is
kept: the look-ahead is bounded by the tolerance, not open-ended, and hearsay cannot contaminate the cell
because `_supports_placement` (:2307-2341) admits only first-hand `saw_player` / `saw_player_move` rows while
absorbed testimony lands under a different event type.

The conviction verdict cannot see a degenerate head. `decide_conviction_go` (training/conviction/fidelity.py:358-362)
tests `conversion_recall` against `0.75 × (1 − voice_driven_share)`, which is at most 0.75; an always-positive
head has zero false negatives, recall 1.0, and clears axis 2 on any corpus. The verifier is right that this is
SPECIFIED — the module docstring at :15-24 states the recall-bound rationale and says precision and accuracy
are "reported beside it, NEVER SUBSTITUTED FOR IT" — and right that the conjunction still requires the Spearman
axis. The residual, which is neither specified nor declared, is the asymmetry with the surrogate's own bar:
`decide_go_no_go` carries `always_eject_baseline`, a trivial-constant comparator, precisely to defeat a
degenerate head (training/surrogate/fidelity.py, axis 3), and the conviction bar carries none even though the
full confusion census is already computed at :280-292. The fix is a third axis, and it has to land here rather
than inside 21.17 because :352-355 records the discipline that the verdict is taken on the FIRST held-out
evaluation: a bar written after seeing the number it judges is not a bar.

Two of the three instruments cannot say what corpus they were fitted on. Only the surrogate commits a
`fit-corpus.json`; `training/artifacts/conviction/` holds weights, a sidecar, a cap and a verdict whose
`replay_set_dir` is a PATH with no digest. `scripts/verify_ml_evidence.py:1577-1615` therefore answers one
question from the surrogate's record and uses that one answer to read nine rows, three of them conviction and
three composed — a documented rationale ("Everything this leg re-derives reads the SAME corpus and the SAME
frozen weights") that is an assumption, not a measurement. And the surrogate is the mirror-image gap: it is the
only one of the three verdicts with no committed artifact and no loader that refuses it, so nothing mechanically
stops a future caller installing a NO-GO surrogate as a training-time meeting runner. Both are cheap to close
while the artifacts are about to be rewritten and expensive to retrofit onto weights nobody can re-derive.

Nothing here moves a recorded byte. No prompt template, no meeting-layer guard, no marker literal and no
recorded ballot changes: the markers are a deliberate, documented, display-stripped design and this task does
not touch their production side. The corpus these numbers are measured on is the baseline-7 record, which is
canon by an explicit owner override of a FINDING verdict — bars 1 and 2 were missed, and no line this task
writes may imply otherwise (audits/audit-phase-20-close.md:33, :357). The two artifacts this task cannot write
truthfully — the conviction fit-corpus record, whose corpus no longer exists on disk, and any re-taken verdict
— are named as 21.17's, not silently deferred.

**Files in scope:**
- training/surrogate/dataset.py; (the six-kind marker chain table built from the imported literals, the per-row rewrite labels, the widened drop predicate, and A-4's `is_reporter` mask at `:240` / `:831` — the feature is BUILT and then withheld from the fit-side vector, not deleted from the row)
- training/surrogate/ballots.py; (both fit paths filter on the new predicate; the dropped-row census the report quotes)
- tests/training/test_surrogate_dataset.py; (the census pin over the four committed sets, the cross-module agreement gate, the samples/4p1i flagged-row pin)
- eval/evidence_honesty.py; (the per-meeting memory prefix on `_MeetingFacts` and the two folds that read it)
- tests/eval/test_evidence_honesty.py; (the planted post-meeting-perception case; the I-4 and I-7 pins re-read)
- training/conviction/fidelity.py; (axis 3, its constant, and the three verdict fields)
- training/conviction/model.py; (`load_conviction_model_artifact` gains the opt-in fit-corpus fence)
- tests/training/test_conviction_model.py; (the degenerate-head planted case, the axis-3-always-populated gate, the conviction fence's planted case, the baseline-6 verdict pin re-read)
- training/composed_runner.py; (the corpus_dir pass-through to the conviction loader)
- tests/training/test_composed_runner.py; (fence ordering pinned on a temp artifact dir)
- training/surrogate/runner.py; (the surrogate verdict writer, loader and the training-time install gate; `load_fit_corpus_record`'s message made generic)
- tests/training/test_surrogate_runner.py; (the NO-GO install refusal and the round-trip)
- training/artifacts/surrogate/verdict.json; (the committed surrogate verdict, keyed on the committed weights sha)
- scripts/verify_ml_evidence.py; (the surrogate-verdict recompute row and the declared per-instrument grounding coverage)
- tests/scripts/test_verify_ml_evidence.py; (the new row asserted, and the shrink-when-recorded gate on the extrapolation list)
- training/reports/report-ballot-surrogate.md; (one dated note: the exclusion set widened, the next fit applies it)

**Files NOT in scope:**
- meetings/manager.py, meetings/voting.py (the marker literals are the input this task reads; the marker DESIGN is deliberate, self-declaring and correctly stripped on both the display and eval sides — nothing about it changes)
- api/replay_loader.py (`_TARGET_REWRITE_LABELS` and `_BALLOT_PREFIX_MARKERS` are read as the canonical definition and pinned against, never edited or imported into production training code)
- eval/deduction_metrics.py, eval/vj_instruments.py (the eval-side unwind and strip already handle all five labels; they are cited as the precedent, not touched)
- training/artifacts/conviction/ (its `verdict.json` stays the baseline-6 record — `tests/training/test_conviction_model.py:860` pins that it is — and its `fit-corpus.json` cannot be written truthfully here because the corpus it was fitted on is not on disk; 21.17 writes both)
- training/bakeoff/harness.py, training/crew/scorer.py, training/coevo/driver.py (wiring `corpus_dir` through `_load_conviction_bundle` would fail loud today for want of a record that does not exist yet; the fence is built here and wired at 21.17)
- replays/ (no recording moves; this task is measured on the committed bytes exactly as they stand)
- training/surrogate/fidelity.py (`decide_go_no_go` and the three GO axes are read and called, never edited — the surrogate bars themselves are the sibling harness-reshape task's subject)
- docs/ml-program.md, training/README.md (the arms and the role census are re-published from the re-ground, not from a hygiene PR)

**Definition of done:**
- [ ] `training/surrogate/dataset.py` carries a table of all six ballot audit-marker kinds as `(label, marker)` pairs built from the imported `meetings.manager` / `meetings.voting` constants — never a re-spelled literal — mirroring `api.replay_loader._BALLOT_PREFIX_MARKERS`, with repr-aware anchored patterns in the `_marker_pattern` shape already used at :177-183.
- [ ] The scan walks the WHOLE leading marker chain front-to-back, not a single `.match()`, so a stacked ordering cannot evade it; a unit test plants `[under-gate …] [uncited zero-flag …]` in that order — an ordering that occurs on no committed byte, which is exactly why it must be planted — and asserts both labels are recovered.
- [ ] `MeetingTableRow` carries the recovered labels for every row beside the existing `ballot_coerced_skip`, and the fit-side drop predicate is the intersection with the repo's canonical five-member target-rewrite class; the two citation-only labels leave the row in the fit, labelled and counted, because they null a reference and leave the authored target intact.
- [ ] Both fit paths (`BallotSurrogateModel.fit` and the corpus fit entry) filter on the new predicate, and their docstrings state the widened rule in one sentence each without narrating its history; the fidelity replay still scores recorded bytes unfiltered, unchanged and asserted so.
- [ ] A cross-module agreement test fails if the training table's label set ever diverges from `api.replay_loader._BALLOT_PREFIX_MARKERS`' labels, or the drop set from `api.replay_loader._TARGET_REWRITE_LABELS`; it is proved to bite by a perturbed copy of the table in the test itself.
- [ ] A census test over the four committed sets pins 3,602 ballots and 204 bracketed annotations in 94 games with the kind split 120/27/18/18/9/8/4, and the per-set target-rewritten ballot counts 45 / 102 / 1 / 2 in the order samples-9p2i, ml_corpus-9p2i, samples-4p1i, ml_corpus-4p1i — so a future re-record cannot silently change what the fit consumes. Six of the seven kinds are the prefix markers this task's table parses; the seventh, the vote-guard rationale redaction, is a replacement BODY rather than a prefix and is the sibling ballot-render task's subject, so the census counts it and the parser does not claim it.
- [ ] A-4's exclusion oracle leaves the fit-side feature vector: `is_reporter` (`training/surrogate/dataset.py:240`, consumed at `:831`) is MASKED OUT of the vector the surrogate fits on, and the PR quotes the census that makes it an oracle rather than a feature — reporter ⇒ CREWMATE is 0 of 618 on the committed sets, a perfect exclusion the model can learn instead of learning a ballot. The column stays on `MeetingTableRow`, computed and available to diagnostics and to the fidelity replay, because the finding is that a fit MAY NOT READ it, not that the fact does not exist; masking rather than deleting also keeps the row schema and every recorded artifact's field set unchanged. A perturbation test fits a head with the feature restored and asserts it separates the two roles perfectly on the committed rows, so the reason for the mask is demonstrated and not asserted. A-4's verifier says to carry this regardless of what the census reads on the NEXT corpus, and the PR records that: the mask does not expire when the number moves.
- [ ] The three committed flagged-row pins move with the rule and none is weakened: `tests/training/test_surrogate_runner.py:1424` 7 → 102 on `replays/ml_corpus/9p2i`, and :1426 plus `tests/training/test_surrogate_dataset.py:337` 0 → 2 on `replays/ml_corpus/4p1i` (both pin the same set); the dropped-row count is reported, never silently absorbed, and `training/reports/report-ballot-surrogate.md` gains one dated note stating that the exclusion widened to the whole target-rewrite class and that the next fit applies it, with its baseline-6 numbers left as the historical record they are.
- [ ] `_MeetingFacts` carries each speaker's episodic-log length captured at `MeetingOpened` (the branch at eval/evidence_honesty.py:1415-1429 already visits it), and `_fold_grounding` and `_fold_movement_origin` scan only that prefix; a player with no captured prefix raises rather than falling back to the whole log.
- [ ] A planted case proves the bound bites: a hand-built memory whose ONLY supporting `saw_player` row lands after the meeting but within ±2 ticks of the spoken sighting scores ungrounded under the prefix and grounded without it, asserted both ways in one test.
- [ ] `tests/eval/test_evidence_honesty.py`'s I-4 pins stay green at `sides == [0, 0, 0, 0]`, and the I-7 pins (`backed_by_move_line`, `spoke_destination`) are re-run over the four committed sets — if any moves, the pin moves with the measured before/after in the PR, and if none moves the PR says so as a measured result rather than an assumption.
- [ ] `decide_conviction_go` gains a third axis — held-out `conversion_accuracy` strictly above the population's own trivial constant, `max(base_rate, 1 − base_rate)` over `conversions_test / test_meetings`, computed by one named helper beside the bar constants so tests and `verify_ml_evidence` read the same definition — and `is_go` becomes the three-way conjunction. Like the surrogate's `always_eject_baseline` axis it is a strict inequality against a measured constant, so it introduces no tunable threshold.
- [ ] The three axis-3 fields on `ConvictionGoVerdict` are optional with a `None` that means exactly "this verdict predates axis 3", documented in the model docstring; `decide_conviction_go` always populates them, pinned by a test, so the only artifact that can read `None` is the committed baseline-6 one — which still loads, keeping `tests/training/test_conviction_model.py:860` and the composed runner's GO gate green.
- [ ] The degenerate head is planted: a hand-built report with recall 1.0, accuracy at the base rate and a passing Spearman returns NO-GO on axis 3 alone, and the live frozen re-derivation (recall 0.9362, precision 0.9362, accuracy 0.9310, base rate 47/87) is asserted to still pass all three — the axis is a floor the real model clears, not a re-verdict.
- [ ] `load_conviction_model_artifact` takes an optional `corpus_dir`; when given, the conviction `fit-corpus.json` is REQUIRED (missing raises, naming 21.17 as the writer), its `weights_sha256` is cross-checked against the loaded weights, and its `corpus_sha256` against `fit_corpus_fingerprint(corpus_dir)`. `load_composed_components` passes its `corpus_dir` through to it. With `corpus_dir` unset every path behaves exactly as at HEAD.
- [ ] The conviction fence is proved to bite in a temp artifact dir holding a MATCHING surrogate record and a mismatched (and separately, an absent) conviction record, so the refusal is attributable to the conviction leg and not to the surrogate fence raising first.
- [ ] `training/surrogate/runner.py` gains a verdict writer and loader mirroring `write_conviction_verdict_artifact` / `load_conviction_verdict`, and `load_surrogate_runner_factory` gains an install-role keyword whose training-time value loads the committed verdict and refuses anything but GO; the default leaves all three production call sites and every existing test call site unedited, and both directions are pinned — the NO-GO refusal AND the eval-time diagnostic path staying legal.
- [ ] `training/artifacts/surrogate/verdict.json` is committed from `decide_go_no_go`, keyed on the committed `weights_sha256`, sorted keys and one trailing newline like the conviction verdict; the PR body carries the exact command that regenerates it byte-for-byte.
- [ ] `scripts/verify_ml_evidence.py` emits a "surrogate verdict.json reproduces" recompute row re-deriving the verdict from the same two fidelity reports the leg already builds, enrolled in `_CORPUS_DEPENDENT_RECOMPUTE_ROWS` beside its conviction and composed siblings so it reads under the same declared grounding gap.
- [ ] `_grounding_row`'s one-question assumption stops being implicit: the instruments whose grounding is EXTRAPOLATED from the surrogate's record are a named frozenset with the reason stated, and a test fails if an instrument gains a committed `fit-corpus.json` while still listed as extrapolated — so 21.17 cannot write the conviction record and leave the row lying. Today's exit code is unchanged.
- [ ] `load_fit_corpus_record`'s FileNotFoundError message names the artifact directory it was asked for rather than "the surrogate", since it is now the loader for two instruments; no other behaviour of that function moves.
- [ ] The PR states the blast radius from a fresh grep of every consumer of `ballot_coerced_skip`, `load_conviction_model_artifact` and `load_surrogate_runner_factory`, and confirms that `tests/training/test_bakeoff_harness.py:1758`'s AST pin still passes unchanged.
- [ ] `uv run pytest tests/training tests/eval/test_evidence_honesty.py tests/scripts/test_verify_ml_evidence.py -q` passes.
- [ ] `uv run pytest -m campaign -q` is run and the PR records either that no pinned ML value moved or which one did and why.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — the census first, as a failing test. Write the four-set census over the committed replays before
touching the builder, and watch it disagree with what the fit currently drops (8). The re-run for this contract
used an anchored leading-bracket-chain regex over every recorded ballot's `rationale_text` and reproduced the
register digit for digit: 3,602 ballots, 204 markers, 94 games, 120/27/18/18/9/8/4, per-set target-rewritten
45 / 102 / 1 / 2, of which 1 / 7 / 0 / 0 are the already-dropped uncited-coerced kind. Keep that census as the
regression pin; it is the thing a future re-record must not move silently.

Step 2 — the table. Build it from the imported constants exactly as `api.replay_loader` does: partition each
marker on `{`, escape head and tail, and put `_MARKER_REPR_VALUE` between them. The existing
`_UNCITED_ZERO_FLAG_MARKER_PATTERN` at training/surrogate/dataset.py:177-183 is that construction already —
generalise it into a helper rather than adding a second idiom. Strip front-to-back in a loop like
`_parse_rewrite_reasons` (api/replay_loader.py:2988-3002); a single `.match()` anchors at position 0 and a
stacked ordering would evade it. That evasion is latent on today's bytes — all 8 uncited markers are leading —
so plant it in the test rather than waiting for a recording to produce one.

Step 3 — the drop rule, and why it is one rule. `BallotExample` has a single `target` field feeding both the
per-candidate softmax and the SKIP alternative, so there is no way to poison the ranking channel alone: a row
whose recorded target is not the voter's authored choice is a poisoned label for the whole example. Take the
repo's own definition of that class — the five members of `api.replay_loader._TARGET_REWRITE_LABELS` — as the
drop set, and leave the two citation-only labels in. Do NOT import the private constant across the package
boundary; rebuild the table in training from the same `meetings.*` literals and let a test assert the two agree.
No import-linter contract forbids training→api, but a private cross-package import is not the craft here and the
agreement test is the stronger guarantee anyway.

Step 4 — the memory prefix. The MeetingOpened branch at eval/evidence_honesty.py:1415-1429 already builds
`_MeetingFacts` and already has `memories` in hand, so capture `len(memories[pid])` for every player there;
`MemoryStore.__len__` exists (agents/memory/episodic.py:106-107) and `recent(since_tick=0)` returns append-order
events, so the prefix is a plain slice of that tuple. Thread the mapping through `_fold_flags` (:2081) into both
`_fold_grounding` (:2344) and `_fold_movement_origin` (:2373) — I-7 reads the same whole log with the same
look-ahead and must move with it. Raise on a missing entry; every living player is in `memories` and a gap is a
wiring bug, not a normal state. Note for the PR that this is why the fix is safe today: the cell is 0/0 on every
committed set, so the correction publishes no new number and buys the first STRONG-populating lever an honest
baseline.

Step 5 — axis 3. Compute the trivial constant from quantities the report already carries —
`conversions_test / test_meetings` gives the base rate, and `conversion_accuracy` is computed at
training/conviction/fidelity.py:292 — so no new measurement is needed, only a bar that reads them. Put the
trivial constant in one small helper beside `CONVICTION_SPEARMAN_BAR` and state in one line why the axis exists:
the surrogate's bar has carried a trivial-constant comparator since 15.13 and the conviction bar has not. The
committed `verdict.json` has 18 keys
and no accuracy field, and the corpus it was taken on is not in this checkout, so the three new fields MUST be
optional — a required field would make `load_conviction_verdict` raise on the committed artifact and take the
composed runner's GO gate down with it. Optional here is not a silent fallback: `decide_conviction_go` never
emits `None`, a test pins that, and the docstring says a `None` means the verdict predates the axis.

Step 6 — the two fingerprints. `load_fit_corpus_record` and `fit_corpus_fingerprint` are already generic over an
artifact directory, so the conviction side needs no new model type — only the opt-in `corpus_dir` on
`load_conviction_model_artifact` and the pass-through at training/composed_runner.py:288. Do not wire the harness
bundle loader: `_load_conviction_bundle` at training/bakeoff/harness.py:733 feeds the campaign tier, and demanding
a record that 21.17 has not written yet would turn that tier red for no gain. Say that hand-off in the PR in one
line so the phase ledger can check it. For the surrogate verdict, mirror the conviction pair byte for byte in
`training/surrogate/runner.py` — that module already owns `FIT_CORPUS_FILENAME`, the fit-corpus loader and
`load_surrogate_runner_factory`, and the gate belongs beside the install path it guards. Give the install-role
keyword a default that matches every existing call site so none of them needs editing, then pin BOTH
directions: the training-time value refuses the committed NO-GO, and the diagnostic value still loads it.

Step 7 — before pushing. Run the campaign tier as well as the default gate: `_load_conviction_bundle`,
`training/crew/scorer.py` and `training/coevo/driver.py` all reach the conviction artifacts and only the campaign
marker exercises them. Re-read `tests/training/_regrounding.py` before you assume any composed path is loadable
at HEAD — the committed surrogate is a baseline-6 fit on a baseline-7 corpus and the fence refuses it by design,
which is a state to work with, not around. And keep every claim recomputed: the numbers in this contract came
from a fresh census and a fresh code read at HEAD 4002f19b, and the PR's numbers must come from the same place.

## Public types this task introduces
- `training.surrogate.dataset.BALLOT_AUDIT_MARKERS`
- `training.surrogate.dataset.TARGET_REWRITE_LABELS`
- `training.surrogate.dataset.ballot_rewrite_labels`
- `training.surrogate.runner.SURROGATE_VERDICT_FILENAME`
- `training.surrogate.runner.write_surrogate_verdict_artifact`
- `training.surrogate.runner.load_surrogate_verdict`
- `training.conviction.fidelity.conversion_trivial_baseline`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.transcript"`
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
Open a PR from branch `phase-21-fit-hygiene` with a title like `task 21.8: the fit reads honest rows: rewritten targets, memory at speech time, a precision axis, and the missing fingerprints`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing A-26 [ADJUSTED, P2, defect] — audits/review-2026-08-26/A/collated-findings.md §A-26 (the fit-side marker gap; the verifier's three corrections BIND this contract: the exclusion list is a DECLARED scope, not a contradicted ruling; the actionable residue is the 120 under-gate redirects, which leave the EJECT decision label authored and rewrite only the TARGET, i.e. they poison the RANKING channel the declared rationale never reaches; severity P1→P2 because the committed fit is baseline-6 and no shipped number is currently wrong). B-40 [CONFIRMED, P2, defect] — audits/review-2026-08-26/B/collated-findings.md §B-40 (I-4 reads end-of-game memory; the verifier's scope narrowing BINDS: the look-ahead is bounded by the ±2 tolerance, and hearsay cannot contaminate the cell because `_supports_placement` admits only first-hand rows). B-15 [ADJUSTED, P2, design-limitation] — §B-15 (recall-only axis 2; the verifier's corrections BIND: the recall-only choice is SPECIFIED with a written rationale, precision/accuracy/confusion are already reported beside it, and a degenerate head passes AXIS 2 only — the conjunction still needs the Spearman axis; the residual value is the undeclared asymmetry with the surrogate's own trivial-constant axis, and the fix must be PRE-REGISTERED because the verdict is taken on the FIRST held-out evaluation). B-16 [ADJUSTED, P2, design-limitation] — §B-16 (no conviction fit-corpus record; the verifier's correction BINDS: every path that actually SCORES is fenced today, transitively through the surrogate leg, so the live gap is a missing provenance RECORD plus an unmeasured transitivity assumption, not an unfenced scoring path). B-17 [ADJUSTED, P3, design-limitation] — §B-17 (no committed surrogate verdict and no loader that refuses a NO-GO surrogate; the verifier's correction BINDS: "enforced by convention" is overstated — the value, the consequence mapping and the recorded consequence are all pinned by green default-tier tests, and only the WIRING is ungated). Anchors re-verified at HEAD 4002f19b by reading the files: training/surrogate/dataset.py:170-199 (`_MARKER_REPR_VALUE`, `_UNCITED_ZERO_FLAG_MARKER_PATTERN`, `_ballot_is_coerced_skip`), :133 (the single imported marker literal), :306-313 (the `ballot_coerced_skip` column and its comment), :997 (the one construction site); training/surrogate/ballots.py:195-205 (`BallotExample` — one `target` label serves ranking AND decision), :295-307 (`ballot_example_from_row`), :798-831 and :930-948 (the two fit paths, both filtering on `not row.ballot_coerced_skip` and nothing else); api/replay_loader.py:253-261 (`_TARGET_REWRITE_LABELS`, the canonical five-member class, with :244-252 stating why the two citation-only labels are deliberately excluded), :2878-2886 (`_BALLOT_PREFIX_MARKERS`, the six label/marker pairs), :2899-2917 (`_marker_pattern` and the precompiled chain), :2973-3003 (`_parse_rewrite_reasons`, the front-to-back stacked strip); meetings/manager.py:200, :211, :274, :296, :309, :326, :354 (the seven audit-marker literals) and meetings/voting.py:90 (`INVALID_VOTE_TARGET_MARKER`); eval/evidence_honesty.py:308-317 (the I-4 definition, "whether the speaker could have seen it"), :1383-1437 (the walk loop and its `finally`), :1392-1393 (`_perceive_tick` mutating `memories`), :1415-1429 (the MeetingOpened branch that builds `_MeetingFacts`), :1450 (`_fold_meetings` running AFTER the whole walk), :1165-1172 (`_MeetingFacts`), :2081 (`_fold_flags`), :2151 and :2157 (the two fold call sites), :2307-2341 (`_supports_placement`), :2344-2370 (`_fold_grounding`, scanning `memory.recent(since_tick=0)`), :2373-2400 (`_fold_movement_origin`, same whole-log scan); agents/memory/episodic.py:77-150 (`MemoryStore.__len__`, `append`'s non-decreasing-tick guard, `recent`); training/conviction/fidelity.py:15-24 (the recall-only rationale), :73-74 (the two bar constants), :141-179 (`ConvictionFidelityReport` including `conversion_precision` / `conversion_accuracy` / the confusion census), :280-292 (where they are computed), :301-343 (`ConvictionGoVerdict`), :346-386 (`decide_conviction_go`), :388-412 (the writer and loader); training/artifacts/conviction/verdict.json (18 keys, GO, baseline-6 numbers, no accuracy or precision field); training/conviction/model.py:452-479 (`load_conviction_model_artifact` verifies the sha sidecar and nothing else), :481-492 (`load_conviction_staleness_cap`); training/composed_runner.py:277-282 (the only `corpus_dir` pass-through, into the surrogate loader), :288-315 (the conviction block: sha, cap, GO — nothing corpus-related); training/surrogate/runner.py:133 (`FIT_CORPUS_FILENAME`), :365-386 (`SurrogateFitCorpus`), :388-416 (`fit_corpus_fingerprint`), :418-429 (`load_fit_corpus_record`, whose message names "the surrogate" though the loader is generic over an artifact dir), :432-469 (`load_surrogate_runner_factory` and its fence docstring), :523-533 (`__all__`); training/surrogate/fidelity.py:895-941 (`GoNoGoVerdict` and its three axes, the third being `always_eject_baseline`, the trivial constant the conviction bar lacks) and :942 + :1037 (`decide_go_no_go`'s definition and its `__all__` entry — no production call site anywhere); training/bakeoff/harness.py:733-790 (`_load_conviction_bundle`, no corpus parameter), :1437 (`surrogate_artifact_dir` defaulting unconditionally); scripts/verify_ml_evidence.py:114-116 (the three artifact dirs), :1554-1566 (`_CORPUS_DEPENDENT_RECOMPUTE_ROWS`, nine names, none of them surrogate-verdict), :1577-1615 (`_grounding_row` and its one-question docstring), :1925-1940 (the amnesty downgrade); tests/training/test_surrogate_runner.py:496 and :792 (the two default-tier pins B-17's verifier adds), tests/training/test_bakeoff_harness.py:1758 (the AST pin that every harness surrogate load wires `corpus_dir`), tests/training/test_conviction_model.py:860 (the committed-verdict-is-baseline-6 pin), tests/eval/test_evidence_honesty.py:51-76 (the private folds the module already imports), :1346-1365 (`test_i4_grounded_sighting_side_pins`, `sides == [0, 0, 0, 0]`), :1454-1472 (the I-7 pins, `backed_by_move_line == 16`); tests/training/_regrounding.py:1-21 (the named interim seam and what it is careful not to be); training/reports/report-ballot-surrogate.md:207-222 (the declared per-kind exclusion list); audits/audit-phase-20-baseline-7.md §10.2 (the re-ground this task pre-registers for) and audits/audit-phase-20-close.md:33 and :357 (baseline 7 is canon by explicit owner override of a FINDING verdict — bars 1 and 2 were missed).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
