# Agent Prompt — 9.4 qwen3.5:9b client compat (think:false, fail-loud)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.4 — qwen3.5:9b client compat (think:false, fail-loud), anchored to DESIGN.md §11.4 (recording provenance); owner decision 2026-06-07 (canonical model qwen2.5:7b-instruct → qwen3.5:9b, thinking disabled). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-qwen35-client`
**Depends on:** none (migration-prep root)
**Section refs:** DESIGN.md §11.4 (recording provenance); owner decision 2026-06-07 (canonical model qwen2.5:7b-instruct → qwen3.5:9b, thinking disabled)
**Complexity:** Medium

Migrate the canonical local provider to `qwen3.5:9b`. Qwen3.5 thinks by default; Ollama supports
disabling per request (`"think": false` in the API payload). The client must send it on every sim
call and FAIL LOUD if a response nonetheless carries populated thinking content (a silently
half-thinking run would record at multiplied latency with un-audited reasoning text). Update the
default-model constants and revalidate the parse-tolerance layer against the new chat template.

**Files in scope:**
- llm/ollama_client.py (`DEFAULT_OLLAMA_MODEL` → `"qwen3.5:9b"`; `think: false` in every request payload; the fail-loud guard: a response with non-empty thinking raises, mirroring the no-silent-fallbacks rule; docstring model references)
- llm/provider.py (the qwen2.5 docstring references; no behavior change beyond what the client carries)
- scripts/refresh_samples.sh (`DEFAULT_OLLAMA_MODEL` literal → `qwen3.5:9b`; the preflight pulls/validates the new model name)
- tests/llm/ (unit: payload carries think:false, the thinking-populated fail-loud case, model-constant pins; the skip-gated real-provider round-trips re-pointed at qwen3.5:9b — they run in 9.5's operator session, not CI)
- AGENT_IMPLEMENTATION.md + README.md (the canonical-model one-liners — swept here; this wave has no separate docs task)

**Files NOT in scope:**
- agents/**, meetings/** (prompts and protocol are model-agnostic; no prompt-version bump — the templates are unchanged)
- replays/samples/** + MANIFESTs (the model row changes only when 9.5 re-records; provenance rides the recorded git_sha)
- `_ollama_num_ctx_from_env` default (keep 8192; 9.5's smoke watches for truncation before any change)

**Definition of done:**
- [ ] Every Ollama request carries `think: false`; a response with populated thinking raises a descriptive error (fail-loud, no silent strip); `DEFAULT_OLLAMA_MODEL == "qwen3.5:9b"` in both the client and refresh_samples.sh.
- [ ] The parse-tolerance suites (the 7.6/8.9 lineage in tests/llm/) pass against the new template assumptions; the env-gated real-provider tests are re-pointed and documented as 9.5-operator-verified.
- [ ] No prompt template, prompt version, or meeting-protocol change.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The payload assembly already sets `options` (num_ctx, seed) — `think` is a TOP-LEVEL request field
in the Ollama API, not an options entry; place it accordingly. The fail-loud guard checks the
response's thinking field (Ollama surfaces it separately when enabled) — assert absent-or-empty.
CLI spot-check for the operator: `ollama run qwen3.5:9b --think=false`. Mock-based tests carry CI;
the real round-trip is 9.5's smoke. Before declaring done, grep `qwen2.5:7b` across the WHOLE repo
and sweep every stale reference in source, docs, and test pins — with one deliberate carve-out:
committed provenance (replays/samples/** MANIFEST model rows, replay JSONL llm_calls, the committed
tournament reports, and the tests/scripts pins that assert those committed rows) correctly keeps
the old model string until 9.5 re-records; that is provenance, not staleness. Leave those for 9.5.

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
Open a PR from branch `phase-9-qwen35-client` with a title like `task 9.4: qwen3.5:9b client compat (think:false, fail-loud)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4 (recording provenance); owner decision 2026-06-07 (canonical model qwen2.5:7b-instruct → qwen3.5:9b, thinking disabled)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
