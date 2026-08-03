# Agent Prompt — 19.17 The event ticker + cost chips (the gated tail)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.17 — The event ticker + cost chips (the gated tail), anchored to audits/audit-phase-19-triage.md §7 item 18 + singleton 29 [S-Claude — "subordinate to pause/finale/temporal-coherence work, not silently discarded"]; the per-call token counts already recorded in replay bytes and served client-side. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-ticker-cost`
**Depends on:** 19.10, 19.12
**Section refs:** audits/audit-phase-19-triage.md §7 item 18 + singleton 29 [S-Claude — "subordinate to pause/finale/temporal-coherence work, not silently discarded"]; the per-call token counts already recorded in replay bytes and served client-side
**Complexity:** Small

The two cheap visible wins, landed deliberately LAST in the frontend chain (the
dependency edges are the point: narrative correctness shipped first). An event ticker
(kills, reports, meetings, ejections as they play) and cost/token chips (per-meeting and
cumulative LLM token counts — the data is already client-side). Both are additive chrome;
neither may regress the pause/finale flow, and both extend the existing test baseline.

**Files in scope:**
- frontend/src/components/EventTicker.tsx (new)
- frontend/src/components/CostChips.tsx (new)
- frontend/src/App.tsx; (mounting only)
- frontend/e2e/; (extend the journey's assertions)

**Files NOT in scope:**
- api/ (no new server data — client-side data only)
- frontend/src/hooks/usePlayback.ts (consumed, not edited)

**Definition of done:**
- [ ] Ticker and chips render from already-served data, respect unspoiled mode (no outcome leakage before the finale), and the extended journey still passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-19-ticker-cost` with a title like `task 19.17: the event ticker + cost chips (the gated tail)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 18 + singleton 29 [S-Claude — "subordinate to pause/finale/temporal-coherence work, not silently discarded"]; the per-call token counts already recorded in replay bytes and served client-side), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
