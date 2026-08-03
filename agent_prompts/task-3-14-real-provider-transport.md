# Agent Prompt — 3.14 Real-provider transport wire-up

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.14 — Real-provider transport wire-up, anchored to DESIGN.md §7, DESIGN.md §10.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-real-provider-transport`
**Depends on:** 3.13 merged
**Section refs:** DESIGN.md §7, DESIGN.md §10.4
**Complexity:** Medium

Close the two compounding gaps surfaced by the Pre-Phase-4 real-provider
eval report (`audits/audit-2026-05-25-0547-pre-phase-4-real-provider-eval.md`),
which exited at pre-flight with verdict **Pre-flight failed — live
provider unreachable**. Total eval spend so far: $0.00. The eval's new
direct-sanity-call gate caught the failure before any tournament-wrapped
API spend.

**Gap A — `AILIBI_LLM_PROVIDER` is ignored by the production path.**
`orchestrator/game.py::build_default_meeting_runner` at line 342 defaults
a missing `llm_client` to `FakeProvider()` rather than to
`build_default_client()`. The public scripts (`scripts/run_game.py`,
`scripts/run_tournament.py`) and `eval/balance_eval.py::run_balance_eval`
all call the factory without `llm_client=`, so the env-var selector
exists but never flows through the public CLI.

**Gap B — `AnthropicClient` has no real transport.**
`llm/provider.py::_default_send` is a one-line
`raise RuntimeError("...real Anthropic SDK is not wired in this build...")`.
`grep -rn "import anthropic" --include='*.py'` returns zero hits outside
`.venv`; the `anthropic` SDK is not declared in `pyproject.toml`
dependencies. The adapter scaffold exists from Task 3.1, but the SDK
transport was never wired in — CI never noticed because every test uses
`FakeProvider`, and prior audits explicitly forbade real-provider calls.

This task closes both gaps so the real-provider eval can be re-attempted.
No new merge criteria are introduced; the existing Phase 3 Merge
Criteria become *measurable* after this task lands.

**Files in scope:**
- pyproject.toml
- uv.lock
- llm/provider.py
- orchestrator/game.py
- tests/llm/test_real_provider.py

**Files NOT in scope:**
- engine/
- observation/
- agents/
- meetings/
- llm/client.py
- llm/budget.py
- llm/budgeted_client.py
- llm/cache.py
- llm/fake_provider.py
- llm/README.md
- llm/__init__.py
- orchestrator/replay.py
- orchestrator/scheduler.py
- orchestrator/boundary.py
- orchestrator/action_ordering.py
- orchestrator/seeder.py
- scripts/run_game.py
- scripts/run_tournament.py
- eval/
- api/
- frontend/
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
- [ ] **Gap B step 1 — `anthropic` declared as a dependency.** Add the `anthropic` Python SDK to `pyproject.toml` `dependencies` using an **exact version pin** to match the project's existing convention (every other dep in the block is exact-pinned, e.g. `fastapi==0.136.1`). Choose a current stable version that supports the `claude-sonnet-4-6` and `claude-haiku-4-5-20251001` model ids. Regenerate `uv.lock` with `uv lock` and commit both files. Document the chosen version + reasoning in `## Decisions`.
- [ ] **Gap B step 2 — `_default_send` implements the real SDK call.** `llm/provider.py::_default_send` becomes a real implementation, NOT a `RuntimeError` stub. The implementation:
  - **Lazy-imports** the `anthropic` package inside the function body (not at module top-level). The existing module docstring at `llm/provider.py:9-11` describes this lazy-import design; honor it. Lazy import keeps the `anthropic` dependency optional at module load time so `FakeProvider`-only test runs and `bash scripts/check.sh` don't require the SDK to be installed (though it will be installed via `uv sync` after `pyproject.toml` changes).
  - Constructs an `anthropic.AsyncAnthropic(api_key=api_key)` client. Reuses the function-scoped client; do not introduce module-level state.
  - Calls `messages.create(model=..., max_tokens=..., temperature=..., messages=[{"role": "user", "content": prompt}])`. Use a single `user` message; the `LLMClient.complete` Protocol surface does not currently carry a system prompt parameter (DESIGN.md §7 / `llm/client.py`).
  - Translates the response into `AnthropicRawResponse(model=..., text=..., input_tokens=..., output_tokens=...)`. The text is the first content block's text. Token counts come from `response.usage.input_tokens` / `response.usage.output_tokens`.
  - The `extended_thinking` and `prompt_caching_beta` parameters are already plumbed through the call signature but stay **no-ops** in this task — wiring them through to the SDK is a separate concern. Document the no-op decision in `## Decisions`.
- [ ] **Gap A — `build_default_meeting_runner` honors `AILIBI_LLM_PROVIDER`.** In `orchestrator/game.py::build_default_meeting_runner`, change the `llm_client=None` fallback from `FakeProvider()` to `build_default_client()` (imported from `llm.provider`). Single-line behavior change: the env-var selector now flows through whenever the factory is called without an explicit `llm_client`. The default case (`AILIBI_LLM_PROVIDER` unset) still produces a `FakeProvider` via `build_default_client`'s own default, so existing tests that rely on the FakeProvider fallback continue to pass without modification. Remove the unused `FakeProvider` import from `orchestrator/game.py` if it becomes unused after the change.
- [ ] **Real-provider round-trip test.** `tests/llm/test_real_provider.py` is a new test file containing at least one test decorated with `@real_provider` (the existing marker defined in `tests/llm/test_client.py`, which wraps `pytest.mark.skipif` keyed on `os.environ.get("AILIBI_RUN_REAL_PROVIDER_TESTS") != "1"`). The test:
  - Imports `real_provider` from `tests.llm.test_client` (or re-defines the same marker locally; either is acceptable).
  - Constructs `AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])` directly (not via `build_default_client`) so the test is self-contained.
  - Calls `await client.complete(prompt="Respond with the single token: OK", schema=None, max_tokens=8, temperature=0.0)`.
  - Asserts `response.text` is a non-empty string, `response.usage.input_tokens > 0`, `response.usage.output_tokens > 0`, `response.cost_usd > 0.0`, `response.model` is a non-empty string. The exact response text is not asserted (LLM output varies).
  - CI continues to skip the test by default (the env-var gate is unset in CI per `llm/README.md`).
- [ ] **Static gates pass without the env var set.** `bash scripts/check.sh` passes on a fresh checkout with `AILIBI_LLM_PROVIDER` unset (and `AILIBI_RUN_REAL_PROVIDER_TESTS` unset). All 667+ existing tests continue to pass; the new `tests/llm/test_real_provider.py` test reports as skipped.
- [ ] **Post-merge sanity check (developer-only; not a CI gate).** After merge, run the direct sanity call from `audits/prompts/pre-phase-4-real-provider-eval-prompt.md` §2 with `AILIBI_LLM_PROVIDER=anthropic` and a real `ANTHROPIC_API_KEY` set. Expected outcome: non-zero `cost_usd`, sensible response text, model id matches `AILIBI_LLM_MEETING_MODEL`. The PR description's `## Decisions` block records the post-merge sanity-call output verbatim (model + cost + response text), with the API key NOT printed.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (with the new test skipped).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The Anthropic Python SDK exposes an async client (`anthropic.AsyncAnthropic`) and a `messages.create` method that returns a typed response. The minimal call shape:

```python
# llm/provider.py — illustrative; pick exact names matching the SDK version chosen
async def _default_send(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    extended_thinking: bool,
    prompt_caching_beta: bool,
) -> AnthropicRawResponse:
    # Lazy import per the design intent at llm/provider.py:9-11. Keeps
    # the SDK optional at module-load time; tests that never touch the
    # real provider don't import it.
    import anthropic

    # extended_thinking and prompt_caching_beta are plumbed through the
    # signature but unused in this task. Wiring them through is a
    # separate concern; document in ## Decisions.
    _ = extended_thinking
    _ = prompt_caching_beta

    client = anthropic.AsyncAnthropic(api_key=api_key)
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    text_blocks = [
        block.text for block in response.content
        if getattr(block, "type", None) == "text"
    ]
    if not text_blocks:
        raise RuntimeError(
            f"Anthropic returned no text content blocks (model={model!r})"
        )

    return AnthropicRawResponse(
        model=response.model,
        text="".join(text_blocks),
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
```

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
Open a PR from branch `phase-3-real-provider-transport` with a title like `task 3.14: real-provider transport wire-up`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §10.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
