# Agent Prompt — 3.15 Anthropic markdown-fence stripping + schema round-trip test

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.15 — Anthropic markdown-fence stripping + schema round-trip test, anchored to DESIGN.md §7, DESIGN.md §10.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-anthropic-fence-strip`
**Depends on:** 3.14 merged
**Section refs:** DESIGN.md §7, DESIGN.md §10.4
**Complexity:** Small

Close the single reproducible defect surfaced by the second
Pre-Phase-4 real-provider eval at
`audits/audit-2026-05-25-1539-pre-phase-4-real-provider-eval.md`,
which exited with verdict **Phase 3 blocked — eval crashed** when the
first live meeting fired (seed 22 of 50). Confirmed live spend on the
crashed run: $0.000105 (sanity call) plus an estimated $0.20–$0.50 of
unrecorded in-flight charges for the ~10 concurrent crashed-meeting
report calls. Total well under any cost gate; the crash is purely a
code defect at the adapter boundary.

**The defect:** `llm/provider.py::AnthropicClient.complete` calls
`schema.model_validate_json(raw.text)` at line 121 directly on the
SDK's text content. Anthropic Sonnet 4.6 (and Claude models in
general) wraps JSON output in markdown code fences (`` ```json … ``` ``)
by default for any structured-output text response. Pydantic rejects
the fenced text:

```
ValidationError: Invalid JSON: expected value at line 1 column 1
input_value='```json\n{\n  "agent_id"...}\n```'
```

The `FakeProvider` at `llm/fake_provider.py:61` hand-emits clean JSON,
which masked the gap until the first live meeting fired. **Not a
transient failure** — markdown fencing is the model's default and
reproduces on every meeting-report call.

This task introduces defensive fence-stripping at the Protocol-parsing
boundary so the adapter is responsible for producing schema-validatable
text. It does NOT migrate to Anthropic's tool-use forced-JSON mechanism
(structurally cleaner but a larger refactor that introduces
Anthropic-specific patterns; deferred to a separate Phase 4-or-later
optimization task if needed).

This task also adds the schema round-trip real-provider test that
would have caught the current crash before any tournament spend.

**Files in scope:**
- llm/provider.py
- tests/llm/test_real_provider.py

**Files NOT in scope:**
- llm/fake_provider.py
- llm/client.py
- llm/budget.py
- llm/budgeted_client.py
- llm/cache.py
- llm/README.md
- llm/__init__.py
- agents/strategic/prompts/
- agents/
- meetings/
- engine/
- observation/
- orchestrator/
- api/
- frontend/
- eval/
- scripts/
- pyproject.toml
- uv.lock
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/
- tests/engine/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/llm/test_client.py
- tests/llm/test_budget.py
- tests/llm/test_budgeted_client.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **Defensive fence-stripping in `complete()`.** In `llm/provider.py::AnthropicClient.complete`, immediately before the existing `schema.model_validate_json(raw.text)` call at line 121 (and only when `schema is not None`), strip surrounding markdown code fences from `raw.text` if present. The stripping is permissive within bounds:
  - Strip leading `` ```json\n`` or `` ```json `` (with or without trailing newline) or `` ```\n`` or just `` ``` `` openers — case-insensitive on the language tag.
  - Strip a matching trailing `` ``` `` (with or without preceding whitespace / newline).
  - Trim incidental whitespace.
  - Do NOT attempt to handle nested fences or fenced-inside-prose patterns; if the model emits multiple fenced blocks or fences inside prose, let Pydantic fail loud as it does today — those are different defects and warrant a separate audit.
  The implementation lives in a small private helper (e.g. `_strip_json_code_fences(text: str) -> str`) so it can be unit-tested independently. The fence-strip is provider-neutral in placement (it runs inside the Protocol's `complete()` method, not inside `_default_send`), so a future OpenAI / DeepSeek adapter that occasionally fences inherits the protection automatically.
- [ ] **`LLMResponse.text` reflects the stripped content.** The returned `LLMResponse` carries the post-strip text — not the original fenced text. Rationale: downstream replay records (`LLMCallRecord.response_text`) should record what the schema validator saw, not what arrived from the wire. This also makes the response usable for non-schema cost/transcript analysis (the fence noise has no semantic value).
- [ ] **Unit tests for the fence-strip helper.** `tests/llm/test_real_provider.py` (or a new helper-only test class within it) exercises the strip helper across the documented cases: (a) `` ```json\n{...}\n``` ``, (b) `` ```\n{...}\n``` ``, (c) `` ```json {...} ``` `` (no inner newlines), (d) plain `{...}` (no fences — passes through unchanged), (e) `{...}\n\n` (whitespace-only fringe — passes through unchanged), (f) text containing `` ``` `` characters but not as fences (passes through unchanged or whatever the chosen heuristic does — document the rule in `## Decisions`). These tests are NOT `@real_provider`-marked — they exercise pure string logic and must run in CI.
- [ ] **New real-provider schema round-trip test.** `tests/llm/test_real_provider.py` adds a new `@real_provider`-marked test that asks the live Anthropic provider to emit a `ReportDocument` (the canonical schema for meeting reports — import from `meetings/schemas.py`) for a trivial fixture meeting. The test:
  - Constructs `AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])`.
  - Calls `await client.complete(prompt=<short fixture prompt asking for a ReportDocument>, schema=ReportDocument, max_tokens=512, temperature=0.0)`.
  - Asserts the call returns without raising (i.e. fence stripping + Pydantic validation succeeds).
  - Asserts `response.cost_usd > 0` and the parsed text validates as a `ReportDocument` via a follow-up `ReportDocument.model_validate_json(response.text)` call.
  - The test is skipped in CI by default via the existing `@real_provider` marker keyed on `AILIBI_RUN_REAL_PROVIDER_TESTS=1` (per [tests/llm/test_client.py](tests/llm/test_client.py)).
  - The fixture prompt is short (≤ 200 tokens input) to keep the test cost ≤ $0.01 per run.
- [ ] **Post-merge local verification.** Before opening the PR, the implementing agent runs (with `AILIBI_LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` set in the shell session):
  - The eval prompt's direct sanity call (must still pass; this is a smoke for Task 3.14's transport).
  - `AILIBI_RUN_REAL_PROVIDER_TESTS=1 uv run pytest tests/llm/test_real_provider.py -v` (must pass; the new schema round-trip test exercises the fix).
  Paste the verbatim outputs into `## Decisions`. API key prefix only (8 chars), never the full key.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (with `tests/llm/test_real_provider.py` real-provider tests skipped by default; the fence-strip unit tests run in CI).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import agents.strategic.reasoner"`
- `uv run python -c "import llm.budgeted_client"`
- `uv run python -c "import meetings.manager"`

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
Open a PR from branch `phase-3-anthropic-fence-strip` with a title like `task 3.15: anthropic markdown-fence stripping + schema round-trip test`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §10.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
