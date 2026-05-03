# Agent Prompt — 3.1 LLM client

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.1 — LLM client, anchored to DESIGN.md §4.4, DESIGN.md §7, DESIGN.md §10.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-llm-client`
**Depends on:** Phase 2 merged
**Section refs:** DESIGN.md §4.4, DESIGN.md §7, DESIGN.md §10.4
**Complexity:** Medium

llm/client.py, provider adapter, fake provider, cache, and budget.

**Files in scope:**
- llm/client.py
- llm/provider.py
- llm/fake_provider.py
- llm/cache.py
- llm/budget.py
- tests/llm/test_client.py
- tests/llm/test_budget.py

**Files NOT in scope:**
- agents/tactical/
- engine/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `LLMClient` protocol exists.
- [ ] Real provider adapter is behind `LLMClient` protocol.
- [ ] Fake deterministic provider exists for tests and CI.
- [ ] Prompt cache and per-game budget support exist.
- [ ] CI tests use the fake provider and make no network calls.
- [ ] No LLM calls are added to agents/tactical/.
- [ ] `uv run mypy --strict llm agents` passes.
- [ ] `uv run ruff check .` passes.

## Implementation hint

See DESIGN.md §7 + §10.4 for the LLM-client surface. The fake deterministic provider is the most important piece — it is what every test in CI calls. `LLMClient` is a Protocol; the real and fake providers both implement it. Cache and budget are layered on.

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
Open a PR from branch `phase-3-llm-client` with a title like `task 3.1: llm client`.
The PR description must reference DESIGN.md §4.4, DESIGN.md §7, DESIGN.md §10.4, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
