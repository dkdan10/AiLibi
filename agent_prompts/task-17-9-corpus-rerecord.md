# Agent Prompt — 17.9 The corpus re-record at the final meeting layer (operator, ~14–15h, $0)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.9 — The corpus re-record at the final meeting layer (operator, ~14–15h, $0), anchored to scripts/record_ml_corpus.sh (the pin block — already baseline-5-coupled: model + set + v3, moved by 16.17; its freeze-path guards refuse stale bytes); replays/ml_corpus/README.md (baseline-3 prose — stale against the script, refreshed here); tasks/phase-15.md 15.12 (the operator-session precedent); audits/audit-phase-16-close.md §0.5 (concurrency notes) + §8 (the staleness rule this task discharges). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-corpus-rerecord`
**Depends on:** 17.2, 17.7
**Section refs:** scripts/record_ml_corpus.sh (the pin block — already baseline-5-coupled: model + set + v3, moved by 16.17; its freeze-path guards refuse stale bytes); replays/ml_corpus/README.md (baseline-3 prose — stale against the script, refreshed here); tasks/phase-15.md 15.12 (the operator-session precedent); audits/audit-phase-16-close.md §0.5 (concurrency notes) + §8 (the staleness rule this task discharges)
**Complexity:** Integration

The long pole. Re-record `replays/ml_corpus/` (150-game 9p2i + the 4p1i set, seeds
1000+, same `seed % 5` split rule) at the FINAL Phase-17 meeting layer — the gate has
ruled, so this substrate is what movers train against, by construction. Duration
honesty: baseline-5 meetings run ~2× baseline-3; plan **~14–15h** with the 16.14/16.17
operator notes (staggered starts, jittered backoff, `AILIBI_SEED_MAX_ATTEMPTS=8`,
per-seed atomic staging). The recorder's guards enforce the substrate; add the one
missing positive gate if absent (assert the graduated-lever slate in recorded bytes,
not just the env refusal). Refresh the corpus README end-to-end (substrate, env, the
duration figure, `--expected-model`), regenerate `splits.json`, and RE-STATE the Q3
canary-denominator restoration: the corpus is again the canonical canary denominator,
samples the continuity anchor (the mid-Phase-15 ruling, DEGRADED through Phase 16,
operative again from this record).

**Files in scope:**
- replays/ml_corpus/9p2i/ + replays/ml_corpus/4p1i/ (the re-recorded bytes + MANIFESTs + splits.json)
- replays/ml_corpus/README.md (full substrate refresh)
- scripts/record_ml_corpus.sh (the duration note + the positive graduated-slate assertion if missing — never the pin block, which is already correct)
- tests/scripts/test_record_ml_corpus.py (the new assertion's fixtures)
- tests/training/ (corpus-derived number re-pins ONLY — the pinned cells this record moves; the constant flips stay 17.11's and the protocol re-pins 17.12's)

**Files NOT in scope:**
- replays/samples/ (the measurement sets — pinned)
- training/ (17.10 consumes; this task records)

**Definition of done:**
- [ ] Both corpus sets recorded at the final meeting layer and PASS the validity gate (`--expected-model Qwen/Qwen3.6-27B --require-zero-cost`); byte-identical reconstruction; MANIFEST provenance exact (model, v3 versions, flags, git_sha, $0); splits.json regenerated under the same rule with the eval/train/val partition non-degenerate.
- [ ] The recorder asserts the graduated-lever slate POSITIVELY in recorded bytes (the `substrate_flag_snapshot` stamp checked, not just env refusal), fixture-pinned.
- [ ] The corpus README agrees with the script on every operative line (model, set, versions, env, duration), and the Q3 restoration is stated in both the README and the PR.
- [ ] The conversion report (17.2's partition) over the new corpus is quoted in the PR — the coerced-SKIP bucket populated, inversions honest.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The recorder is already correct — resist editing its pin block. The session plan is the
15.12 runbook with doubled wall-clock: record 4p1i first (short, validates the pipeline
end-to-end), then the 9p2i long leg. Commit atomically only after both validity gates
pass; the freeze-path staging keeps partial runs off the tree.

## Integration risk

A ~14–15h operator session spanning UTC midnight — the 16.14 mixed-date MANIFEST
precedent applies (dates are honest, the gate checks coherence not uniformity).
Training tests that pin corpus-derived numbers (tests/training/test_bakeoff_harness.py,
test_surrogate_runner.py, test_crew_options.py, test_goodhart_probe.py) will move —
re-pin ONLY what this record moves, in this PR, so the suite is green at merge (the
17.11 constants stay 17.11's).

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
Open a PR from branch `phase-17-corpus-rerecord` with a title like `task 17.9: the corpus re-record at the final meeting layer (operator, ~14–15h, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing scripts/record_ml_corpus.sh (the pin block — already baseline-5-coupled: model + set + v3, moved by 16.17; its freeze-path guards refuse stale bytes); replays/ml_corpus/README.md (baseline-3 prose — stale against the script, refreshed here); tasks/phase-15.md 15.12 (the operator-session precedent); audits/audit-phase-16-close.md §0.5 (concurrency notes) + §8 (the staleness rule this task discharges)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
