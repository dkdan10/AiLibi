# Agent Prompt — 3.17 Meeting-report max_tokens raise + unclosed-fence strip

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.17 — Meeting-report max_tokens raise + unclosed-fence strip, anchored to DESIGN.md §7, DESIGN.md §10.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-truncation-fence-handling`
**Depends on:** 3.16 merged
**Section refs:** DESIGN.md §7, DESIGN.md §10.4
**Complexity:** Small

Close the defect surfaced by the fourth Pre-Phase-4 real-provider eval
at `audits/audit-2026-05-25-2138-pre-phase-4-real-provider-eval.md`,
which exited with verdict **Phase 3 blocked — tournament crashed** when
the first live meeting fired (seed 23 of 50). Confirmed live spend on
the crashed run: ~$0.0001 (sanity call) + 1 truncated meeting call
(~$0.02–$0.05 estimated, never returned). The eval pre-flight, smoke,
and the 23 pre-meeting games all completed cleanly; the crash is in a
narrow new defect class that prior tasks did not surface.

**The defect — truncation produces an unclosed markdown fence.** Live
Anthropic Sonnet 4.6 emits a `ReportDocument` that:
1. Opens with `` ```json\n `` (the documented markdown-fenced shape).
2. Contains a JSON body.
3. Gets truncated at `DEFAULT_REPORT_MAX_TOKENS=1024` mid-output (the
   audit's stack-trace input value ends mid-prose with `"…of p-2 after"`).
4. Never emits the closing `` ``` `` fence.

Task 3.15's `_strip_json_code_fences` is intentionally conservative —
it strips only when BOTH an opening AND a closing fence are present at
string edges (`^\s*```(?:json)?\s*` matched, `\s*```\s*$` matched). The
unclosed-open case falls through unchanged; `model_validate_json` then
fails with `Invalid JSON: expected value at line 1 column 1` on the
leading backtick.

This task closes two compounding root causes:

- **`report_max_tokens=1024` is too tight** for typical Sonnet 4.6
  meeting-report outputs (observed: the model had time for opener +
  several observations + multiple claims + the start of another
  sentence before truncating). Raising to **2048** doubles the
  headroom while staying comfortably under Task 3.16's $1.00 per-game
  budget cap (2048 output tokens × $15/Mtok = $0.031/call cap;
  ~20 calls/meeting = up to $0.62/meeting at the new cap; empirically
  meetings won't approach the cap because the model stops when it's
  done).
- **`_strip_json_code_fences` is too conservative** for the
  truncated-response case. Even after raising max_tokens, a future
  longer report could still hit the cap; the stripper should
  defensively strip an unmatched-open fence so the failure mode is
  "JSON incomplete — Pydantic ValidationError on missing fields" (a
  clear, actionable signal) rather than "Invalid JSON at column 1
  because of a leading backtick" (a misleading symptom).

**Out of scope** (explicit decisions deferred):

- **`DEFAULT_STATEMENT_MAX_TOKENS=512` and `DEFAULT_VOTE_MAX_TOKENS=384`
  stay at their current values.** The audit's evidence is for report
  truncation only; statement and vote outputs are inherently smaller
  schemas. The unclosed-fence strip below provides the defense-in-depth
  if either ever truncates in a future eval. If a future eval surfaces
  truncation on statement or vote, raise those constants in a follow-up
  task.
- **Permissive trailing-partial-fence stripping** (e.g. trimming a
  trailing `` `` `` or `` ` ``) is NOT in scope. Risk of stripping
  legitimate content. The Pydantic error from a truly-truncated
  response (`Field required`, etc.) is the right failure mode.
- **Migration to Anthropic's tool-use forced-JSON mechanism** (which
  would structurally eliminate the fence class entirely) is deferred to
  a Phase 4-or-later optimization task. Larger refactor of
  `_default_send`; introduces Anthropic-specific patterns that don't
  translate cleanly to OpenAI/DeepSeek. Revisit only if the
  fence-class keeps recurring after 3.17.

**Files in scope:**
- meetings/manager.py
- llm/provider.py
- tests/llm/test_real_provider.py

**Files NOT in scope:**
- meetings/schemas.py
- meetings/transcript.py
- meetings/voting.py
- meetings/__init__.py
- llm/client.py
- llm/budget.py
- llm/budgeted_client.py
- llm/cache.py
- llm/fake_provider.py
- llm/README.md
- llm/__init__.py
- agents/strategic/prompts/
- agents/strategic/reasoner.py
- agents/strategic/output_schemas.py
- agents/
- engine/
- observation/
- orchestrator/
- api/
- frontend/
- eval/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- pyproject.toml
- uv.lock
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
- [ ] **`DEFAULT_REPORT_MAX_TOKENS` raised from 1024 to 2048** at `meetings/manager.py:73`. The other two constants (`DEFAULT_STATEMENT_MAX_TOKENS=512` at line 75, `DEFAULT_VOTE_MAX_TOKENS=384` at line 77) are NOT changed — the audit's evidence is for report truncation only, and statement / vote outputs are inherently smaller. Document the unchanged constants in `## Decisions` with a one-sentence rationale referencing the audit.
- [ ] **`_strip_json_code_fences` strips unmatched-open fences.** At `llm/provider.py:211-234`, extend the helper so that when an opening fence is found (`_FENCE_OPEN_PATTERN` matches) but no matching closing fence is present, the opening fence is still stripped and the remainder of the text is returned trimmed. The behavior matrix becomes:
  - Both opening and closing fences present → strip both (current behavior; unchanged).
  - Only opening fence present (truncated response) → strip opener; return remainder trimmed.
  - Only closing fence present (extremely unusual; not observed) → return text unchanged (no opener to strip; passing through is safe).
  - No fences present → return text unchanged (current behavior; unchanged).
  - Empty / whitespace-only text → return unchanged (current behavior; unchanged).
  The strict variant: only strip the opening fence, not trailing partial fences. Risk of stripping legitimate content outweighs the benefit.
- [ ] **Unit test for the unclosed-open-fence case in `_strip_json_code_fences`** (NOT `@real_provider`-marked; runs in CI). Add to the existing `TestStripJsonCodeFences` class at `tests/llm/test_real_provider.py:70`:
  - **Required test**: a truncated JSON-fenced response with no closing fence (e.g. `` ```json\n{"agent_id": "p-1", "incomplete": ``) returns the post-opener content trimmed.
  - **Required test**: an opening fence without a `json` language tag also strips correctly (e.g. `` ```\n{"foo": `` → `{"foo":`).
  - **Required test**: the existing both-fences-present case STILL works (regression pin).
  - **Required test**: the existing no-fences case STILL passes through unchanged (regression pin).
- [ ] **`@real_provider` truncation test** in `tests/llm/test_real_provider.py`. Add a new test that exercises the truncation scenario end-to-end:
  - Constructs `AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])` directly.
  - Calls `await client.complete(prompt=<a short prompt asking for a ReportDocument>, schema=ReportDocument, max_tokens=50, temperature=0.0)`. The deliberately tight `max_tokens=50` forces truncation.
  - Asserts the call raises `pydantic_core.ValidationError` (the truncated JSON is incomplete after fence stripping; Pydantic correctly fails on missing required fields).
  - Asserts the ValidationError message does NOT contain "expected value at line 1 column 1" (which would indicate the leading-backtick failure mode). Use a substring check like `"line 1 column 1" not in str(exc.value)` to pin the desired failure mode.
  - Skipped in CI by default via the existing `@real_provider` marker. Per-invocation cost ~$0.001 (the call is tiny by design).
- [ ] **Post-merge local verification.** Before opening the PR, with `AILIBI_LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` set:
  - Run `AILIBI_RUN_REAL_PROVIDER_TESTS=1 uv run pytest tests/llm/test_real_provider.py -v` — all existing `@real_provider` tests (including Task 3.16's 4 production-template tests) must still pass; the new truncation test must pass with the expected failure-mode assertion.
  - Re-run the eval prompt's direct sanity call — must still pass (this confirms the raised report budget didn't break the simple-call path).
  - Paste verbatim outputs (model + cost_usd + first 100 chars of response for each test) into `## Decisions`. API key 8-char prefix only.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (with the new `@real_provider` test skipped by default in CI; the new unit tests for `_strip_json_code_fences` run in CI).
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
Open a PR from branch `phase-3-truncation-fence-handling` with a title like `task 3.17: meeting-report max_tokens raise + unclosed-fence strip`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §10.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
