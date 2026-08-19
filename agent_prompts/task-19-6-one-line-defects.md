# Agent Prompt — 19.6 The one-line defects

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.6 — The one-line defects, anchored to audits/audit-phase-19-triage.md §7 item 7 [S-Claude; VERIFIED §8 row 9]; pyproject.toml (zero `httpx`) vs llm/featherless_client.py:764 (the lazy `import httpx`); llm/provider.py:52 (`_FALLBACK_PRICING_USD_PER_MTOK = (3.00, 15.00)`) + :659-662 (the silent `.get` fallback); frontend/src/tokens.ts:39-47 (the ink ramp: 900/700/500/400/300/200/100 — no 600) vs frontend/src/components/MeetingView.tsx:517 + HighlightCard.tsx:60 (`text-ink-600` used); agents/strategic/prompts/loader.py:119 (`DEFAULT_PROMPT_SET = "qwen3_5_9b"` — two generations behind the operational baseline). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-one-line-defects`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 7 [S-Claude; VERIFIED §8 row 9]; pyproject.toml (zero `httpx`) vs llm/featherless_client.py:764 (the lazy `import httpx`); llm/provider.py:52 (`_FALLBACK_PRICING_USD_PER_MTOK = (3.00, 15.00)`) + :659-662 (the silent `.get` fallback); frontend/src/tokens.ts:39-47 (the ink ramp: 900/700/500/400/300/200/100 — no 600) vs frontend/src/components/MeetingView.tsx:517 + HighlightCard.tsx:60 (`text-ink-600` used); agents/strategic/prompts/loader.py:119 (`DEFAULT_PROMPT_SET = "qwen3_5_9b"` — two generations behind the operational baseline)
**Complexity:** Small

Four verified one-line-class defects, fixed loud: declare `httpx` as a direct dependency
(the canonical provider currently rides transitive luck); make unknown-model pricing fail
loud (raise with the model name) instead of silently billing at $3/$15 — cost accounting
is exactly where the no-silent-fallback doctrine matters; add `ink-600` to the token ramp
(or remap the two call sites to an existing step if the design ramp intends seven stops)
plus a token-exists check; and make the bare-environment prompt-set fallback LOUD — the
default stays `qwen3_5_9b` for byte-identity (a documented owner decision), but falling
back without the env override now emits a one-line stderr notice naming the operational
baseline variable. No prompt bytes move (the byte-golden proves it).

**Files in scope:**
- pyproject.toml; (the httpx declaration)
- uv.lock; (regenerated for the new declaration)
- llm/provider.py
- frontend/src/tokens.ts
- frontend/src/index.css; (regenerated — tokens.ts is only the SOURCE; `frontend/scripts/gen-tokens-css.ts` writes the `@theme` variables here, and `--color-ink-600` does not exist in the generated block today)
- agents/strategic/prompts/loader.py
- tests/llm/test_provider.py
- tests/llm/test_client.py; (the existing `test_unknown_model_uses_fallback_pricing` at :481-503 asserts the behavior this task removes — it flips to asserting the raise)
- tests/agents/test_prompt_loader.py; (or the loader's actual test home — locate by grep, name it in the PR)

**Files NOT in scope:**
- llm/featherless_client.py (the import stays lazy; only the declaration moves)
- frontend/src/components/MeetingView.tsx + HighlightCard.tsx (call sites stand; the token appears under them)
- .env.example (19.1's file — the env-var documentation rides there)

**Definition of done:**
- [ ] Unknown-model pricing raises with the model name (test-pinned); known models unchanged.
- [ ] `httpx` is a declared dependency and the lock regenerates cleanly.
- [ ] `text-ink-600` resolves to a real token: the ramp entry lands in tokens.ts AND the regenerated `index.css` carries `--color-ink-600` (grep-proven in the PR; `tsc:check` + build green). The durable ramp-integrity vitest rides 19.12's baseline — this task has no frontend test surface yet and says so rather than promising one.
- [ ] The loader emits the fallback notice exactly when the env override is absent (test-pinned) and prompt bytes are unchanged (byte-golden green).
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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-19-one-line-defects` with a title like `task 19.6: the one-line defects`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 7 [S-Claude; VERIFIED §8 row 9]; pyproject.toml (zero `httpx`) vs llm/featherless_client.py:764 (the lazy `import httpx`); llm/provider.py:52 (`_FALLBACK_PRICING_USD_PER_MTOK = (3.00, 15.00)`) + :659-662 (the silent `.get` fallback); frontend/src/tokens.ts:39-47 (the ink ramp: 900/700/500/400/300/200/100 — no 600) vs frontend/src/components/MeetingView.tsx:517 + HighlightCard.tsx:60 (`text-ink-600` used); agents/strategic/prompts/loader.py:119 (`DEFAULT_PROMPT_SET = "qwen3_5_9b"` — two generations behind the operational baseline)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
