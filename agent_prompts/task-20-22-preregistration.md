# Agent Prompt — 20.22 THE PRE-REGISTRATION (owner): bars, instruments and the decision rule, pinned from committed cells

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.22 — THE PRE-REGISTRATION (owner): bars, instruments and the decision rule, pinned from committed cells, anchored to audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 — the day-1 rule "Day 1, before any code: pre-register" (:239-241), the pre-registered primary bar (:282-287) and the record order (:272-276); audits/review-2026-08-19/A/verdicts.md — the G-1 block (crew whereabouts false at neither tick N nor N−1: 148/723 = 20.5% samples/9p2i, 402/2038 = 19.7% ml_corpus/9p2i, 7/78, 11/79), the G-2 block (sole-`alibi_vs_sighting` convicting precision 12 right / 70 wrong = 14.6%; 63.5% of resolvable sighting sides never perceived by the speaker; the review's anchors corrected at HEAD — `_iter_sightings` at `meetings/transcript.py:2170-2179` yields every `SawPlayerObservation` unfiltered, and `_detect_alibi_vs_sightings` at `:2380-2494` never inspects the sighter's own record), the G-3 block (fabricated "You completed" lines 53/529 = 10.0% samples/9p2i, 15/65 = 23.1% samples/4p1i), and the G-5 / G-9 / G-12 / G-25 blocks; audits/review-2026-08-19/B/verdicts.md C-2 and C-3 (`kill_available_ticks=415 intent_kill=225 MISSED_KILL=190`, 45.8% of free zero-witness opportunities declined); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1 (the zero-LLM deduction oracle over 626 body meetings; 61 of 354 ejections landed on someone the crew's pooled perception had already cleared) and §D2 (adjacent-room STRONG share 148/234 = 63.2%); audits/audit-phase-19-close.md §4.1 (the committed 19.14 cells: 310/310 = 1.000 with ejectee-specific proof, 46/125 = 0.368 without, 79/79 innocent ejections inside the non-direct cell) and §4.4 (the owner's Option-A ruling that chartered this phase); tests/eval/test_deduction_metrics.py:178 and :224 (`non_direct_ejections == 33`, samples/9p2i), :256 (`(35, 89)` corpus 9p2i), :295-296 (samples/4p1i), :309-310 (the corpus-4p1i no-cell) — the pins re-verified at HEAD; tests/api/test_evidence_mechanisms.py:173, :194, :220, :249 (the four 19.11 injustice fixtures, served through the real `ReplayLoader`); eval/deduction_metrics.py:852 (`_wilson_interval` — the only interval producer any cell may quote); scripts/check_doc_facts.py:172 (`check_sample_provenance` — the win split re-derived from `replays/samples/<set>/MANIFEST.md`, the committed source for the secondary band); orchestrator/replay.py:531 (`_RETIRED_ALWAYS_ON_LEVERS`) and :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS` — `impostor_roll_call`, the one live toggle at HEAD); audits/audit-phase-18-emergence-preregistration.md:23-25 (the label key), §6 (the claim-discipline shape), §8 (THE RATIFIED DECISION section), §9 (the amendment log); audits/audit-phase-20-preregistration.md §§0-10 (the provisional memo this task pins); AGENTS.md:106-110 (craft rule 7 — record impact and measurement on every contract). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-preregistration`
**Depends on:** 20.14, 20.15 — the solvability instrument must merge first because the y-axis cells this memo quotes are its committed pins; the evidence-honesty instrument set must merge first because seven of the eight primary bars read cells only that module computes, and a bar whose "before" number lives in an uncommitted review script is a bar nobody can re-run
**Section refs:** audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 — the day-1 rule "Day 1, before any code: pre-register" (:239-241), the pre-registered primary bar (:282-287) and the record order (:272-276); audits/review-2026-08-19/A/verdicts.md — the G-1 block (crew whereabouts false at neither tick N nor N−1: 148/723 = 20.5% samples/9p2i, 402/2038 = 19.7% ml_corpus/9p2i, 7/78, 11/79), the G-2 block (sole-`alibi_vs_sighting` convicting precision 12 right / 70 wrong = 14.6%; 63.5% of resolvable sighting sides never perceived by the speaker; the review's anchors corrected at HEAD — `_iter_sightings` at `meetings/transcript.py:2170-2179` yields every `SawPlayerObservation` unfiltered, and `_detect_alibi_vs_sightings` at `:2380-2494` never inspects the sighter's own record), the G-3 block (fabricated "You completed" lines 53/529 = 10.0% samples/9p2i, 15/65 = 23.1% samples/4p1i), and the G-5 / G-9 / G-12 / G-25 blocks; audits/review-2026-08-19/B/verdicts.md C-2 and C-3 (`kill_available_ticks=415 intent_kill=225 MISSED_KILL=190`, 45.8% of free zero-witness opportunities declined); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1 (the zero-LLM deduction oracle over 626 body meetings; 61 of 354 ejections landed on someone the crew's pooled perception had already cleared) and §D2 (adjacent-room STRONG share 148/234 = 63.2%); audits/audit-phase-19-close.md §4.1 (the committed 19.14 cells: 310/310 = 1.000 with ejectee-specific proof, 46/125 = 0.368 without, 79/79 innocent ejections inside the non-direct cell) and §4.4 (the owner's Option-A ruling that chartered this phase); tests/eval/test_deduction_metrics.py:178 and :224 (`non_direct_ejections == 33`, samples/9p2i), :256 (`(35, 89)` corpus 9p2i), :295-296 (samples/4p1i), :309-310 (the corpus-4p1i no-cell) — the pins re-verified at HEAD; tests/api/test_evidence_mechanisms.py:173, :194, :220, :249 (the four 19.11 injustice fixtures, served through the real `ReplayLoader`); eval/deduction_metrics.py:852 (`_wilson_interval` — the only interval producer any cell may quote); scripts/check_doc_facts.py:172 (`check_sample_provenance` — the win split re-derived from `replays/samples/<set>/MANIFEST.md`, the committed source for the secondary band); orchestrator/replay.py:531 (`_RETIRED_ALWAYS_ON_LEVERS`) and :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS` — `impostor_roll_call`, the one live toggle at HEAD); audits/audit-phase-18-emergence-preregistration.md:23-25 (the label key), §6 (the claim-discipline shape), §8 (THE RATIFIED DECISION section), §9 (the amendment log); audits/audit-phase-20-preregistration.md §§0-10 (the provisional memo this task pins); AGENTS.md:106-110 (craft rule 7 — record impact and measurement on every contract)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run pytest -q -k "evidence_honesty or solvability or deduction_metrics"` green — every pin the memo cites resolves at this HEAD; plus an inline `python3 - <<'EOF'` reader pasted into the PR Summary that loads each cited pin and diffs it against the memo's stated cell, printing `0 mismatches` across all cells and naming any deliberate difference with its recorded cause.

The phase's whole credibility rests on one ordering: the bars exist, in the tree, before the
first fix does. The review states the rule as the wave's day-1 item
(`audits/review-2026-08-19/D/FINAL-synthesis.md` §4, :239-241), and the repo has done it once
already — the 18.4 memo, where every baseline cell was quoted from a committed pin and the
owner ratified definitions and bars by merge. This task is that gate for Phase 20. The
planning PR shipped `audits/audit-phase-20-preregistration.md` in PROVISIONAL form: the
instrument list, the bars, the decision rule and the record order are all drafted, but nearly
every baseline cell is labelled [REVIEW-DERIVED] — measured by the 2026-08-19 review's session
scripts, which were deliberately NOT committed. Today, therefore, seven of the eight primary
bars have a "before" number that nobody in this repository can re-run. That is exactly the
defect the phase is elsewhere fixing in documentation, and it would be fatal here: a bar
anchored to an unreproducible figure cannot judge a record.

The pinning is now possible because the two instrument tasks have merged. `eval/solvability.py`
owns the y-axis cells — the zero-LLM candidate-set oracle over the 626 body meetings, the
singleton rate and correctness, and the 61-of-354 ejections that landed on an already-cleared
player (`audits/review-2026-08-19/A/ideas-multi-agent-researcher.md` §D1).
`eval/evidence_honesty.py` owns the honesty and bug-class cells: false crew self-placement
(20.5% samples/9p2i, `A/verdicts.md` G-1), sole-flag convicting precision (12 right / 70 wrong
= 14.6%) and grounded sighting side (36.5% of resolvable sides; `A/verdicts.md` G-2),
fabricated completion lines (53/529 = 10.0% samples/9p2i, 15/65 = 23.1% samples/4p1i;
`A/verdicts.md` G-3, `B/verdicts.md` C-2), the adjacent-room STRONG share (148/234 = 63.2%;
`A/ideas-multi-agent-researcher.md` §D2), and the context and co-intervention cells
(G-5, G-9, G-12, G-25; `B/verdicts.md` C-3's 190/415 declined free kills). The two cells that
were already committed stay where they are: the I-1 proof-vs-inference partition is quoted
from `tests/eval/test_deduction_metrics.py` (non-direct 33 at samples/9p2i, 35/89 at corpus
9p2i, 3 at samples/4p1i, the corpus-4p1i no-cell — pooled 46/125 = 0.368 with 79/79 of the
innocent ejections, restated in `audits/audit-phase-19-close.md` §4.1), and the I-13 injustice
exhibits from `tests/api/test_evidence_mechanisms.py`. After this task every cell in the memo
names a file that a stranger can run.

What the owner ratifies, and what re-anchors without ratification, follows the standing rule
this repo set at 18.4: the DEFINITIONS, the statistical conventions, the BARS and the decision
rule are the ratified content; the quoted baseline CELLS are evidence and re-anchor
mechanically at the adopting record. One consequence is load-bearing and must be stated in the
memo: where a pinned re-derivation differs from the review-measured figure, the PIN replaces
the cell and the bar's TARGET does not move with it. The targets — non-direct conviction
accuracy at least 0.60, innocent ejections under 35, false crew whereabouts under 5%,
sole-flag precision at least 50%, grounded sighting side 100%, fabricated completions 0,
adjacent-room STRONG share about 0, and the four fixtures each flipping — are ratified as
written, not recomputed from whatever the pin turns out to say. A bar that follows its own
baseline is not a bar.

The memo also fixes three things the record cannot renegotiate later. The co-intervention is
declared by name: task 20.32 repairs the scripted impostor mover before the freeze, and that
repair changes game dynamics inside the same record, so attribution of the honesty bars rests
on the offline counterfactual plus the record, never on the win split — which is reported
inside a pre-registered band and never gated. The offline-counterfactual protocol names its
command, the cells it can predict from frozen baseline-6 bytes, the cells it explicitly
cannot, and the abandon criteria. The record order is fixed as `replays/samples/9p2i` →
`replays/ml_corpus/9p2i` → `replays/samples/4p1i` → `replays/ml_corpus/4p1i`, corpus 9p2i
before any 4p1i leg because the non-direct cell has n=89 there against n=33 in the samples and
a delta on n=33 will not separate. The DAG enforces the ordering the memo claims: every lever
contract and the co-intervention depend on this task, so no substrate change can merge before
the bars are ratified. Ratification is the owner's merge of this PR; anything after it is
dated errata in the amendment log.

**Files in scope:**
- audits/audit-phase-20-preregistration.md; (the pinned version: every cell cites tests/eval/test_evidence_honesty.py / test_solvability.py / test_deduction_metrics.py; bars and decision rules as [PROPOSED — ratified at merge])
- tasks/phase-20.md; (the 'Pre-registration' preamble section points at the ratified memo — one paragraph)

**Files NOT in scope:**
- eval/ (the instruments belong to the two upstream tasks; this memo quotes them and never redefines a cell)
- replays/ (bytes never move at a pre-registration gate)
- any production or test code (a defect found while pinning routes back as its own contract, exactly as the 18.4 batch findings did)
- the STATUS line of tasks/phase-20.md (the phase close owns it)
- agents/strategic/prompts/ (prompt templates are substrate; the single prompt-set bump is task 20.31's alone)

**Definition of done:**
- [ ] Every cell in the memo's baseline table names its committed source beside it — `tests/eval/test_deduction_metrics.py` for the I-1 partition, `tests/eval/test_solvability.py` for the I-12 y-axis, `tests/eval/test_evidence_honesty.py` for I-2 through I-11, `tests/api/test_evidence_mechanisms.py` for the I-13 fixtures, and `scripts/check_doc_facts.py::check_sample_provenance` over `replays/samples/<set>/MANIFEST.md` for the secondary win split; a grep for `[REVIEW-DERIVED]` in the memo returns zero hits, and the label key is the 18.4 one — [VERIFIED] quoted from a committed pin, [INFERRED] arithmetic over quoted cells with inputs shown, [PROPOSED — ratified at merge] for every bar and rule.
- [ ] Where a pinned re-derivation differs from the review-measured figure, the memo keeps BOTH numbers, marks the pin authoritative, and states the cause in one sentence quoted from the instrument task's test comment; a silent replacement fails this item. No cell is computed by hand: every interval quoted comes from `eval.deduction_metrics._wilson_interval`, as the 18.4 memo's §10 convention requires.
- [ ] The eight primary bars are stated verbatim with the per-set cells beside the pooled figure: non-direct-cell conviction accuracy 0.368 → ≥ 0.60 pooled, no set < 0.50; corpus innocent ejections 79 → < 35; false crew whereabouts 20.5% → < 5%, every set < 8%; sole-`alibi_vs_sighting` convicting precision 14.6% → ≥ 50% with the class impostor share above the base rate; grounded sighting side → 100% of surviving STRONG sighting sides; fabricated completion lines → 0 on every set; adjacent-room STRONG share 63.2% → ~0; and each of the four 19.11 injustice fixtures stated pass/fail individually.
- [ ] The secondary cells are stated as observed-and-reported, never gated: the win split inside its pre-registered band with the baseline-6 rates re-derived from the MANIFESTs rather than quoted from prose, the solvability y-axis, and the movement-origin, marker-contamination, singular-persona, context and co-intervention cells.
- [ ] The decision rule is written in ADOPTED / FINDING / partial-adoption form, naming the exact subset of bars each verdict requires and the eligibility test for a partially adopted lever; the memo states that no bar may be re-priced after this merge and that a miss is reported as a miss.
- [ ] The co-intervention is declared by name with its attribution consequence; the offline-counterfactual protocol names its command, the cells predictable from frozen baseline-6 bytes, the cells explicitly not predictable with the reason, and the abandon criteria; the record order and the freeze list are fixed, with the power argument for the corpus-9p2i leg preceding either 4p1i leg.
- [ ] A sign-off section records that ratification is the owner's merge of this PR, and an amendment log section exists and is empty at merge; the memo's status line no longer says PROVISIONAL.
- [ ] The `tasks/phase-20.md` preamble gains one paragraph naming the ratified memo as the document the counterfactual and the record read verbatim; the STATUS line is untouched.
- [ ] The PR Summary carries the pin-diff reader's output showing `0 mismatches` and the green `pytest -k` run from Measurement.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`

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
Open a PR from branch `phase-20-preregistration` with a title like `task 20.22: the pre-registration (owner): bars, instruments and the decision rule, pinned from committed cells`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave 2 — the day-1 rule "Day 1, before any code: pre-register" (:239-241), the pre-registered primary bar (:282-287) and the record order (:272-276); audits/review-2026-08-19/A/verdicts.md — the G-1 block (crew whereabouts false at neither tick N nor N−1: 148/723 = 20.5% samples/9p2i, 402/2038 = 19.7% ml_corpus/9p2i, 7/78, 11/79), the G-2 block (sole-`alibi_vs_sighting` convicting precision 12 right / 70 wrong = 14.6%; 63.5% of resolvable sighting sides never perceived by the speaker; the review's anchors corrected at HEAD — `_iter_sightings` at `meetings/transcript.py:2170-2179` yields every `SawPlayerObservation` unfiltered, and `_detect_alibi_vs_sightings` at `:2380-2494` never inspects the sighter's own record), the G-3 block (fabricated "You completed" lines 53/529 = 10.0% samples/9p2i, 15/65 = 23.1% samples/4p1i), and the G-5 / G-9 / G-12 / G-25 blocks; audits/review-2026-08-19/B/verdicts.md C-2 and C-3 (`kill_available_ticks=415 intent_kill=225 MISSED_KILL=190`, 45.8% of free zero-witness opportunities declined); audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1 (the zero-LLM deduction oracle over 626 body meetings; 61 of 354 ejections landed on someone the crew's pooled perception had already cleared) and §D2 (adjacent-room STRONG share 148/234 = 63.2%); audits/audit-phase-19-close.md §4.1 (the committed 19.14 cells: 310/310 = 1.000 with ejectee-specific proof, 46/125 = 0.368 without, 79/79 innocent ejections inside the non-direct cell) and §4.4 (the owner's Option-A ruling that chartered this phase); tests/eval/test_deduction_metrics.py:178 and :224 (`non_direct_ejections == 33`, samples/9p2i), :256 (`(35, 89)` corpus 9p2i), :295-296 (samples/4p1i), :309-310 (the corpus-4p1i no-cell) — the pins re-verified at HEAD; tests/api/test_evidence_mechanisms.py:173, :194, :220, :249 (the four 19.11 injustice fixtures, served through the real `ReplayLoader`); eval/deduction_metrics.py:852 (`_wilson_interval` — the only interval producer any cell may quote); scripts/check_doc_facts.py:172 (`check_sample_provenance` — the win split re-derived from `replays/samples/<set>/MANIFEST.md`, the committed source for the secondary band); orchestrator/replay.py:531 (`_RETIRED_ALWAYS_ON_LEVERS`) and :570-572 (`_TOGGLEABLE_LEVER_RESOLVERS` — `impostor_roll_call`, the one live toggle at HEAD); audits/audit-phase-18-emergence-preregistration.md:23-25 (the label key), §6 (the claim-discipline shape), §8 (THE RATIFIED DECISION section), §9 (the amendment log); audits/audit-phase-20-preregistration.md §§0-10 (the provisional memo this task pins); AGENTS.md:106-110 (craft rule 7 — record impact and measurement on every contract)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
