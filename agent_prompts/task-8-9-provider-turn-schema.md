# Agent Prompt — 8.9 LLM provider parse-tolerance under the new turn schema

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.9 — LLM provider parse-tolerance under the new turn schema, anchored to DESIGN.md §7 (provider), §5.3; audits/restructure-impact-map-2026-06-04-0223.md §2e, §4 coupling 2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-provider-turn-schema`
**Depends on:** 8.7, 8.8
**Section refs:** DESIGN.md §7 (provider), §5.3; audits/restructure-impact-map-2026-06-04-0223.md §2e, §4 coupling 2
**Complexity:** Small

The meeting-record schema (`MeetingTurn`, 8.7) is also the structured-output schema fed to the provider (`reasoner.py schema=... → ollama_client.model_json_schema() → format=`), so the `tests/llm` parse-tolerance suite pins the old `Statement` shape and must move. Update the meeting-schema fixtures + the `format=schema` round-trips. `llm/report_normalize.py` is discriminator-**aware** (it keys off the union variant's discriminator literal), so verify the discriminator field name it keys off still matches `MeetingTurn` (and the observation/claim leaves) after 8.7's reshape — a small adjustment is OK if the discriminator field moved — then confirm it still no-ops valid turns and repairs near-misses.

**Files in scope:**
- llm/report_normalize.py (verify the discriminator field name it keys off matches `MeetingTurn`; a small adjustment is OK if 8.7's reshape moved it — no schema relaxation)
- tests/llm/test_provider.py (`_MEETING_SCHEMAS` set; the `round_index`-pinned bad-payload fixtures; the structured-output kinds set)
- tests/llm/test_report_normalize.py (the `Statement` payload fixtures → `MeetingTurn`)
- tests/llm/test_real_provider.py (the skip-gated Ollama round-trips against the reshaped templates/schema)

**Files NOT in scope:**
- meetings/, agents/strategic/ (8.7 / 8.8)

**Definition of done:**
- [ ] `tests/llm` validates against `MeetingTurn` (not `Statement`): the `format=schema` JSON the provider is constrained by matches the new turn shape, and the parse-tolerance + fence-strip round-trips pass.
- [ ] `llm/report_normalize.py`'s discriminator field still matches `MeetingTurn` (a small adjustment if 8.7's reshape moved it); it no-ops an already-valid turn and still repairs a near-miss (a discriminator-mismatched key); no schema relaxation.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-8-provider-turn-schema` with a title like `task 8.9: llm provider parse-tolerance under the new turn schema`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7 (provider), §5.3; audits/restructure-impact-map-2026-06-04-0223.md §2e, §4 coupling 2), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
