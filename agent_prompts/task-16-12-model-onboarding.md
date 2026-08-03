# Agent Prompt — 16.12 Model onboarding: the production client, the locked literals, the doctrine docs

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.12 — Model onboarding: the production client, the locked literals, the doctrine docs, anchored to audits/audit-phase-16-model-lock.md (the decision this implements); llm/featherless_client.py:135 (DEFAULT_FEATHERLESS_MODEL) + :556-592 (_THINKING_KWARG_BY_MODEL — the fail-loud exact-id registry) + :18-32 (response_format_mode posture); llm/provider.py:64-73 (the $0 provider-keyed pricing — assert, don't touch); scripts/refresh_samples.sh + scripts/record_ml_corpus.sh (the locked literals). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-model-onboarding`
**Depends on:** 16.2
**Section refs:** audits/audit-phase-16-model-lock.md (the decision this implements); llm/featherless_client.py:135 (DEFAULT_FEATHERLESS_MODEL) + :556-592 (_THINKING_KWARG_BY_MODEL — the fail-loud exact-id registry) + :18-32 (response_format_mode posture); llm/provider.py:64-73 (the $0 provider-keyed pricing — assert, don't touch); scripts/refresh_samples.sh + scripts/record_ml_corpus.sh (the locked literals)
**Complexity:** Small

GO-path only. Make the locked model — **`Qwen/Qwen3.6-27B`** (the exact served id, locked
2026-07-12) — the production default, everywhere the incumbent is pinned:
the `_THINKING_KWARG_BY_MODEL` entry (that served id verbatim, with the
thinking-kwarg boolean the 16.1 probe verified — an unregistered id fails loud on every call, by
design; NOTE the probe's operational finding: this generation REASONS BY DEFAULT, so the
production entry must PIN non-thinking (`enable_thinking` false) — the scratch ladder's viable
profile is non-thinking-only, and unpinned reasoning would leak think-text into recorded state), `DEFAULT_FEATHERLESS_MODEL`, the `refresh_samples.sh` model literal, a loud
comment in `record_ml_corpus.sh` that the committed corpus remains baseline-3/old-model substrate
pending Phase-17 re-grounding — the corpus script's PIN BLOCK (model + set + versions) is NOT
edited: its preflight couples the three, and the pins coherently describe the frozen artifacts
they guard; 16.17 re-pins the whole block to the baseline-5 substrate — the `response_format_mode`
posture if the probe's verdict differs from `json_object`, the client test pins, and the doctrine
docs (AGENTS.md provider section, README provider table, .env.example). The $0 cost path needs NO
change (provider-keyed empty pricing dict — every Featherless model resolves to the 0.0 fallback);
assert it in a test rather than re-implementing anything.

**Files in scope:**
- llm/featherless_client.py (the registry entry + DEFAULT_FEATHERLESS_MODEL + response_format posture region)
- scripts/refresh_samples.sh (the model-literal lines — disjoint from 16.13's prompt-set-literal lines)
- scripts/record_ml_corpus.sh (the stale-corpus COMMENT only — the model/set/versions pin block is untouched; 16.17 owns it)
- tests/llm/test_featherless_client.py (default-model + registry pins)
- tests/scripts/test_refresh_samples.py (model-literal pin region — disjoint from 16.13's set-gate pin region)
- AGENTS.md (provider doctrine region)
- README.md (provider table region — the sample-provenance paragraph is 16.14's)
- .env.example (the featherless model lines — disjoint from the lever lines)

**Files NOT in scope:**
- llm/provider.py (the $0 table is provider-keyed and correct as-is — a test asserts the new id resolves to $0; no edit)
- agents/strategic/prompts/ (the bespoke set is 16.13's)
- replays/ (committed sets untouched; they verify regardless of the default — reconstruction never re-invokes a model)

**Definition of done:**
- [ ] The locked served id is registered in `_THINKING_KWARG_BY_MODEL` with the probe-verified boolean, is the `DEFAULT_FEATHERLESS_MODEL`, and a payload-construction test exercises it (the fail-loud path proven by a deliberate unknown-id fixture).
- [ ] A test asserts the new id resolves to $0 under `_compute_cost_usd` (provider-keyed fallback — asserted, not re-implemented).
- [ ] `refresh_samples.sh` carries the new model literal with its script-test pins updated in this task; `record_ml_corpus.sh` carries the stale-corpus comment with its pin block UNCHANGED (`tests/scripts/test_record_ml_corpus.py` stays green untouched — asserted); committed sets still byte-verify (`bash scripts/verify_samples.sh` green — the default swap cannot touch recorded bytes).
- [ ] AGENTS.md / README / .env.example name the new canonical model with the lock-audit citation.
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
Open a PR from branch `phase-16-model-onboarding` with a title like `task 16.12: model onboarding: the production client, the locked literals, the doctrine docs`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-model-lock.md (the decision this implements); llm/featherless_client.py:135 (DEFAULT_FEATHERLESS_MODEL) + :556-592 (_THINKING_KWARG_BY_MODEL — the fail-loud exact-id registry) + :18-32 (response_format_mode posture); llm/provider.py:64-73 (the $0 provider-keyed pricing — assert, don't touch); scripts/refresh_samples.sh + scripts/record_ml_corpus.sh (the locked literals)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
