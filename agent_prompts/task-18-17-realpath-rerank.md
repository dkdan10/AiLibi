# Agent Prompt — 18.17 The real-path re-rank recorder (selection designs B/C, productized)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.17 — The real-path re-rank recorder (selection designs B/C, productized), anchored to audits/audit-phase-18-planning.md §2.2 (the cost table; design B ~2 h/gen, design C ~21 h/run); eval/balance_eval.py:241 (the `meeting_runner_factory` seam); training/bakeoff/es.py:154 (`champion_trace`); scripts/run_tournament.py --candidate-artifact (the 17.14 recorder whose stamp discipline this inherits); orchestrator/game.py:397-399 (deadline-free headless meetings — the timeout gap). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-realpath-rerank`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §2.2 (the cost table; design B ~2 h/gen, design C ~21 h/run); eval/balance_eval.py:241 (the `meeting_runner_factory` seam); training/bakeoff/es.py:154 (`champion_trace`); scripts/run_tournament.py --candidate-artifact (the 17.14 recorder whose stamp discipline this inherits); orchestrator/game.py:397-399 (deadline-free headless meetings — the timeout gap)
**Complexity:** Medium

Productize the two real-path selection loops the training-signal decision adopted: (B)
per-generation top-K re-rank — given K candidate genomes and a seed list, record each on the
real provider path, score through the committed CLIs, and emit a machine-readable ranking
row; (C) champion-trace re-rank — the same over an `ESResult.champion_trace`. Library-first
(a `training/realpath.py` module the 18.21 driver calls), with per-candidate provenance
stamps read back from bytes (the 17.14 discipline), per-seed crash-retry, and the missing
wall-clock guard: a per-meeting timeout wrapping the runner so a hung provider fails the
seed loudly instead of stalling the loop (headless meetings are deadline-free today).
Recordings are working artifacts outside the tree; the committed truth is the ranking jsonl.

**Files in scope:**
- training/realpath.py
- tests/training/test_realpath.py (fake-provider protocol tests: ranking rows, stamp read-back, timeout fail-loud, retry budget)

**Files NOT in scope:**
- scripts/run_tournament.py; (the CLI recorder is 17.14's; this is the library loop — no CLI change)
- training/bakeoff/es.py + harness.py (consumed, never edited)

**Definition of done:**
- [ ] The re-rank loop records K candidates × N seeds through the real seam (exercised in tests via the fake provider), scores each with the committed validity/core/watchability CLIs' library entry points, and emits ranking rows carrying the full candidate stamp read back from bytes plus per-seed retry/timeout telemetry.
- [ ] A hung meeting (simulated in tests) fails that seed loudly within the configured timeout and the retry budget re-records it; nothing hangs the loop.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The provider-nondeterminism honesty note belongs in the module docstring: real-path ranks
are selection signal, not fitness — two runs of the same genome may differ, which selection
tolerates and the ES fitness contract does not. Never write these scores into an ES fitness
channel.

## Public types this task introduces
- `training.realpath.RealPathRerankResult`
- `training.realpath.run_realpath_rerank`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-18-realpath-rerank` with a title like `task 18.17: the real-path re-rank recorder (selection designs b/c, productized)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §2.2 (the cost table; design B ~2 h/gen, design C ~21 h/run); eval/balance_eval.py:241 (the `meeting_runner_factory` seam); training/bakeoff/es.py:154 (`champion_trace`); scripts/run_tournament.py --candidate-artifact (the 17.14 recorder whose stamp discipline this inherits); orchestrator/game.py:397-399 (deadline-free headless meetings — the timeout gap)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
