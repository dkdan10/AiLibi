# Agent Prompt — 3.1 LLM client

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

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
- [ ] **`LLMClient` Protocol exists and is provider-neutral.** The Protocol's public surface does not expose Anthropic-specific concepts (extended thinking, `cache_control`, prompt-caching beta headers, message-shape internals). Anthropic-specific behaviors live as private implementation details inside `AnthropicClient`. The Protocol is tight enough that adding a second provider (OpenAI, DeepSeek, local) is a new-file change — no edits required to call sites in `agents/`, `meetings/`, or `orchestrator/`.
- [ ] **Real provider adapter (`AnthropicClient`) is behind the Protocol.** Defaults to `claude-sonnet-4-6` for meeting-strength calls and `claude-haiku-4-5-20251001` for triggered-check calls. The model id is a constructor parameter (not a hardcoded literal); the default selection is by call type and overridable per-call.
- [ ] **Runtime provider/model selection.** The active provider and model are selected at construction time from configuration (environment variables like `AILIBI_LLM_PROVIDER=anthropic`, `AILIBI_LLM_MEETING_MODEL`, `AILIBI_LLM_TRIGGER_MODEL`, or an equivalent config object passed by the orchestrator). Document the chosen mechanism in the PR's `## Decisions` block.
- [ ] **Cross-provider portability is documented.** A `llm/README.md` (or top-of-file docstring in `llm/client.py`) describes the minimum surface a hypothetical second-provider adapter must implement, with one worked sketch (10–20 lines, no real SDK calls) showing what an OpenAI or DeepSeek adapter would look like. You do not ship the second adapter — you show that it would slot in cleanly.
- [ ] **Fake deterministic provider** exists for tests and CI; it produces schema-valid responses without recording or hashing. Tests pass the same prompt and always get the same response shape. The fake is the default for CI; the real provider is only invoked in explicit local/eval runs.
- [ ] **Prompt cache and per-game budget support exist.** Cache key is provider-neutral (does not bake in Anthropic message structure). Budget enforcement is fail-loud on overrun (raises a typed exception), not silent truncation.
- [ ] CI tests use the fake provider and make no network calls. The real provider adapter is exercised only by tests marked with an explicit `pytest.mark.real_provider` (or equivalent) that CI skips by default.
- [ ] No LLM calls are added to `agents/tactical/`.
- [ ] `uv run mypy --strict llm agents` passes.
- [ ] `uv run ruff check .` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

See DESIGN.md §7 + §10.4 for the LLM-client surface. The fake deterministic provider is the most important piece — it is what every test in CI calls. `LLMClient` is a Protocol; the real and fake providers both implement it. Cache and budget are layered on top.

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
Open a PR from branch `phase-3-llm-client` with a title like `task 3.1: llm client`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §4.4, DESIGN.md §7, DESIGN.md §10.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
