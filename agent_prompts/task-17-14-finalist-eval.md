# Agent Prompt — 17.14 The multi-finalist recorder + the real-LLM finalist eval (operator, $0)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.14 — The multi-finalist recorder + the real-LLM finalist eval (operator, $0), anchored to audits/audit-phase-15-pause.md:145-184 (the uncommitted per-finalist driver this task productizes); scripts/run_tournament.py:244-265 (`--agent-factory learned-champion` — loads only the ONE committed artifact today); tasks/phase-16.md 16.14 §5 (the stamp-proven champion-row precedent); audits/audit-phase-16-close.md §0.5 (operator concurrency notes). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-finalist-eval`
**Depends on:** 17.12
**Section refs:** audits/audit-phase-15-pause.md:145-184 (the uncommitted per-finalist driver this task productizes); scripts/run_tournament.py:244-265 (`--agent-factory learned-champion` — loads only the ONE committed artifact today); tasks/phase-16.md 16.14 §5 (the stamp-proven champion-row precedent); audits/audit-phase-16-close.md §0.5 (operator concurrency notes)
**Complexity:** Integration

Close the tooling gap the pause left: the CLI can only run the committed champion, so
evaluating MULTIPLE new finalists on the real Featherless path needs a productized
multi-finalist recorder — extend `run_tournament.py` (or a sibling entry point) to load
a named candidate artifact by path with full provenance stamping (the 15.9 stamp,
sha-verified against the artifact sidecar), never touching the committed champion
surface. Then the operator leg: each finalist runs the 50-seed 9p2i real-path eval at
the current substrate, rows stamp-proven (the 16.14 discipline), validity-gated, $0.
The output table — win edge vs the same-substrate scripted baseline + referee scoring
per finalist — is 17.16's evidence.

**Files in scope:**
- scripts/run_tournament.py (the candidate-artifact loading path + stamping)
- training/reports/results-finalist-eval.jsonl (new: stamp-proven finalist rows)
- training/reports/report-finalist-eval.md (the evidence table)
- tests/scripts/ (loader fixtures: sha mismatch fails loud; stamp fields exact)

**Files NOT in scope:**
- agents/tactical/learned/ (the committed champion is untouched until 17.16)
- training/bakeoff/ (selection already happened; this is the real-path check)

**Definition of done:**
- [ ] The recorder loads an arbitrary candidate artifact with sha verification (mismatch fails loud before any spend) and stamps every game row with the full 15.9 provenance; fixture-pinned.
- [ ] Every finalist's 50-seed eval is committed with stamp-proof rows, validity gate PASS, and the evidence table (win edge, referee scoring, floor sensitivity) in the report.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Productize the pause's driver as a thin loader parameter on the existing tournament
path — the champion factory already does artifact-loading + sha verification; generalize
its entry point rather than writing a second loader. Stamp fields come from the
candidate's own config, never from the committed champion's constants.

## Integration risk

Two learned movers must never be conflated in one recording: the loader binds ONE
candidate per tournament invocation and the stamp names it — assert no ambient state
leaks between runs. Real-path concurrency: champion games collide in ballot phases
(the 16.14 finding) — single-worker tails or staggering, attempts ≥8.

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
Open a PR from branch `phase-17-finalist-eval` with a title like `task 17.14: the multi-finalist recorder + the real-llm finalist eval (operator, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-15-pause.md:145-184 (the uncommitted per-finalist driver this task productizes); scripts/run_tournament.py:244-265 (`--agent-factory learned-champion` — loads only the ONE committed artifact today); tasks/phase-16.md 16.14 §5 (the stamp-proven champion-row precedent); audits/audit-phase-16-close.md §0.5 (operator concurrency notes)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
