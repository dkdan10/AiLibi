# Agent Prompt — 3.9 Strategic reasoner + sub-phase C integration substrate

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.9 — Strategic reasoner + sub-phase C integration substrate, anchored to DESIGN.md §4.4, DESIGN.md §6.6. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-strategic-reasoner`
**Depends on:** 3.8 merged
**Section refs:** DESIGN.md §4.4, DESIGN.md §6.6
**Complexity:** Integration

Wire the strategic reasoner (`render_for_prompt` → `LLMClient` → parsed
structured output) AND land four integration-substrate deliverables that
the post-3.8 audit identified as required infrastructure for sub-phase C:

1. **Strategic reasoner** at `agents/strategic/reasoner.py` — the
   primary deliverable. Wraps the rendered memory, the four prompt
   templates from Tasks 3.4–3.7, and the LLM client into a single
   reasoner that produces `ReportDocument`, `Statement`, or `VoteBallot`.
2. **Jinja loader for the four `.j2` templates (C-4 from
   `audits/audit-2026-05-16-2239-claude.md`).** The four prompt
   templates at `agents/strategic/prompts/*.j2` currently have zero CI
   coverage. This task introduces a strict-undefined Jinja loader plus
   per-template smoke tests so a `{% endfor %}` typo or wrong-kwarg-name
   regression is caught in CI rather than at the first live-provider
   meeting.
3. **`BudgetedLLMClient` adapter (C-5 from
   `audits/audit-2026-05-16-2239-claude.md`).** `MeetingManager`
   currently takes a raw `LLMClient` with no budget tracking. This task
   introduces an adapter at `llm/budgeted_client.py` that wraps any
   `LLMClient` and enforces `GameBudget.preflight()` +
   `GameBudget.charge_response()` around every `complete()` call. The
   strategic reasoner uses the adapter by default; `MeetingManager` is
   constructed with it where Task 3.9 wires the meeting flow.
4. **Two carried-over coverage pins (L-1 and L-2 from the post-3.3
   audit, still open after sub-phase B).** L-1: budget cap-slack
   boundary test. L-2: `last_seen` suffix on confirmed-dead player.
   Both land in this task because the work touches budget and
   rendered-memory surfaces.
5. **Token-budget contract awareness (C-2 from the post-3.3 audit,
   resolved via DESIGN.md edit before dispatch).** DESIGN.md §6.6 now
   documents the non-elastic carve-out (role + tasks-completed +
   beliefs + contradictions always retained; only observations are
   elastic). The reasoner must respect this documented contract; no
   DESIGN.md edits required from the implementing agent.

The C-1 R-10 scanner-reuse hedge from the post-3.3 audit is closed by
this task's existing R-10 acceptance gate (which already requires
direct import of `_assert_no_recursive_hidden_fields` and
`_assert_no_role_bearing_values` from `eval/leak_test.py`). The
implementing agent must NOT re-implement the scanners; direct import
only.

**Files in scope:**
- agents/strategic/reasoner.py
- agents/strategic/prompts/__init__.py
- agents/strategic/prompts/loader.py
- llm/budgeted_client.py
- tests/agents/test_strategic_reasoner.py
- tests/agents/test_strategic_prompts.py
- tests/llm/test_budgeted_client.py
- tests/llm/test_budget.py
- tests/agents/test_memory_rendering.py

**Files NOT in scope:**
- engine/
- engine/maps/
- observation/
- orchestrator/
- agents/tactical/
- agents/perception.py
- agents/runtime.py
- agents/base.py
- agents/memory/store.py
- agents/memory/episodic.py
- agents/memory/working.py
- agents/memory/beliefs.py
- agents/strategic/prompts/crewmate_report.j2
- agents/strategic/prompts/impostor_report.j2
- agents/strategic/prompts/accusation_round.j2
- agents/strategic/prompts/vote_ballot.j2
- agents/strategic/output_schemas.py
- meetings/
- llm/client.py
- llm/provider.py
- llm/fake_provider.py
- llm/cache.py
- llm/budget.py
- api/
- frontend/
- eval/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/test_crewmate_policy.py
- tests/agents/test_impostor_policy.py
- tests/agents/test_pathing.py
- tests/agents/test_perception.py
- tests/agents/test_memory.py
- tests/agents/test_runtime.py
- tests/llm/test_client.py
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/engine/
- tests/eval/
- tests/test_firewall.py

**Definition of done:**
- [ ] **Strategic reasoner — primary deliverable.** `agents/strategic/reasoner.py` exposes a `StrategicReasoner` class (or equivalent) that takes an `AgentMemory`, an `LLMClient` (typically wrapped by `BudgetedLLMClient`), and the four prompt callables. It produces `ReportDocument`, `Statement`, or `VoteBallot` instances via the pipeline `render_for_prompt(memory) → load_template(...).render(...) → llm_client.complete(prompt, schema=...) → parsed_output`. Strategic calls occur only at meetings or specified trigger points (kill-witnessed, body-found); never inside `agents/tactical/`.
- [ ] **C-4 — Jinja loader with strict-undefined behavior.** `agents/strategic/prompts/loader.py` (or `__init__.py`) exposes a Jinja `Environment` configured with `autoescape=False, undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True`. It loads templates from the `agents/strategic/prompts/` directory and exposes one named callable per template (e.g. `crewmate_report_prompt`, `impostor_report_prompt`, `accusation_round_prompt`, `vote_ballot_prompt`). Strict-undefined ensures a typo'd variable name raises at render time rather than silently producing an empty string.
- [ ] **C-4 — Per-template smoke tests with Pydantic validation.** `tests/agents/test_strategic_prompts.py` exercises each of the four templates with realistic inputs (a stub rendered-memory string, stub transcript, stub schema). Each test asserts the rendered output (a) is non-empty, (b) contains the expected version-marker substring, and (c) parses cleanly through the corresponding Pydantic schema using `FakeProvider` for the LLM call. A `{% endfor %}` typo, missing kwarg, or schema-incompatible output must cause the test to fail.
- [ ] **C-5 — `BudgetedLLMClient` adapter.** `llm/budgeted_client.py` defines a `BudgetedLLMClient` class wrapping any `LLMClient` plus a `GameBudget`. Each `complete()` call invokes `budget.preflight(estimated_cost_usd)` before the underlying call and `budget.charge_response(actual_cost_usd)` after. If `preflight` raises `BudgetExceededError`, the error propagates without invoking the underlying client. The adapter conforms to the same `LLMClient` Protocol so consumers (including `MeetingManager`) accept it without signature changes.
- [ ] **C-5 — Meeting-ceiling budget test.** `tests/llm/test_budgeted_client.py` exercises a sequence of `complete()` calls whose cumulative cost approaches and then exceeds a configured budget cap. The test asserts `BudgetExceededError` propagates from the `preflight` check, NOT from silent truncation, and NOT after the underlying client has been called. At least one of these tests drives the adapter through a `MeetingManager`-shaped flow (multiple calls in sequence, fake provider, cumulative spend tracked) to confirm the integration path works end-to-end.
- [ ] **C-2 — Reasoner respects DESIGN.md §6.6 non-elastic carve-out.** DESIGN.md §6.6 was updated before dispatch to document that role + tasks-completed + beliefs + contradictions are always retained (non-elastic); only observations are elastic and drop salience-sorted. The reasoner must read this documented contract — it does NOT need to re-implement elasticity for beliefs/contradictions. If a meeting prompt would push past the model's context window, that is a sub-phase C operational concern (handled by the orchestrator passing a sane budget), not a reasoner-side defect. The implementing agent does NOT edit DESIGN.md.
- [ ] **L-1 — Budget cap-slack boundary pin.** `tests/llm/test_budget.py` gains ~10 LOC of regression: assert `cap=0.30, charge=0.30 + 1e-3` raises and `cap=0.30, charge=0.30 + 1e-9` does not. The test names the slack constant by inspection and pins the documented behavior so a future silent slack-widening (e.g. `1e-6` → `1e-3`) cannot pass CI.
- [ ] **L-2 — `last_seen` confirmed-dead suffix pin.** `tests/agents/test_memory_rendering.py` gains ~15 LOC of regression: record a `saw_player` event plus a `saw_body` event for the same player id, render via `render_for_prompt`, assert the `(last seen in ROOM at tick N)` suffix appears on the dead player's belief line. The test must fail if a future refactor silently suppresses `last_seen` for confirmed-dead players.
- [ ] **R-10 acceptance gate for strategic prompt inputs (per `audits/audit-2026-05-15-0225-reconciled.md` §R-10 and closing C-1 from `audits/audit-2026-05-16-2239-claude.md`):** The packet field/value leak scanners from `eval/leak_test.py` (`_assert_no_recursive_hidden_fields` and `_assert_no_role_bearing_values`) are imported **directly** and reused against the strategic prompt inputs the reasoner assembles before they reach `LLMClient`. Do NOT re-implement the scanners — direct import only. `tests/agents/test_strategic_reasoner.py` includes at least one planted negative test pinning that the scanner trips on a forbidden role-bearing string injected into a prompt input.
- [ ] Strategic calls occur only at meetings or specified trigger points.
- [ ] Tests use `llm.fake_provider` and make no network calls.
- [ ] No imports from `engine/` under `agents/`.
- [ ] No LLM calls in `agents/tactical/`.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

See DESIGN.md §4.4 + §6.6 for the strategic-reasoner shape. The pipeline is `render_for_prompt(memory) → load_template(...).render(...) → llm_client.complete(prompt) → parse_structured_output(...) → ReportDocument | Statement | VoteBallot`. All five new deliverables compose:

```
                   ┌────────────────────────────────────┐
                   │  StrategicReasoner                 │
                   │  ┌──────────────────────────────┐  │
                   │  │ render_for_prompt(memory)    │  │  ← reads composite memory
                   │  └──────────────┬───────────────┘  │
                   │                 ▼                  │
                   │  ┌──────────────────────────────┐  │
                   │  │ load_template(name)          │  │  ← Jinja loader (C-4)
                   │  │   .render(memory, ctx, ...)  │  │
                   │  └──────────────┬───────────────┘  │
                   │                 ▼                  │
                   │  ┌──────────────────────────────┐  │
                   │  │ BudgetedLLMClient.complete   │  │  ← C-5 adapter
                   │  │   (preflight + charge)       │  │
                   │  └──────────────┬───────────────┘  │
                   │                 ▼                  │
                   │  ┌──────────────────────────────┐  │
                   │  │ Pydantic parse → schema      │  │  ← schemas from 3.2
                   │  └──────────────────────────────┘  │
                   └────────────────────────────────────┘
```

## Public types this task introduces
- `agents.strategic.reasoner.StrategicReasoner`
- `llm.budgeted_client.BudgetedLLMClient`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This task is the convergence point for sub-phase C. It wires composite memory + four prompt templates + LLM client + budget into one reasoner.

- **Determinism.** The reasoner runs against the fake provider in CI. Same memory state + same prompt template + same fake provider → same parsed output. Verify with at least one test that runs the same reasoning twice and asserts byte-identical outputs.
- **Engine isolation.** `agents/strategic/reasoner.py` does NOT import from `engine/`. The reasoner consumes shapes already inside `agents/memory/`, `meetings/schemas.py`, and `llm/`. Confirm with `uv run lint-imports`.
- **Cross-provider portability preserved.** `BudgetedLLMClient` implements the same `LLMClient` Protocol as `AnthropicClient` and `FakeProvider`. It does not leak Anthropic-specific concepts. Verify with `git grep -nE "anthropic|cache_control|extended_thinking" llm/budgeted_client.py tests/llm/test_budgeted_client.py` returning empty.
- **`MeetingManager` integration.** Task 3.8 constructed `MeetingManager` with a raw `LLMClient`. After Task 3.9, the reasoner constructs `MeetingManager` with a `BudgetedLLMClient` instance. The `MeetingManager.__init__` signature does not change — the budget is transparent to it. If the implementing agent finds they need to change `meetings/manager.py`, that is out-of-scope drift; stop and surface in `## Questions`.
- **`.j2` templates remain frozen.** The four `.j2` files at `agents/strategic/prompts/` are out of scope. The Jinja loader reads them as-is; do not edit the templates to make kwarg names align. If a kwarg drift exists, surface in `## Decisions` so the next hygiene task can address it.
- **Token-budget contract documented in DESIGN.md §6.6 before dispatch.** The implementing agent reads the carve-out and respects it; no DESIGN.md edits. If the documented contract appears wrong during implementation, stop and surface in `## Questions`.
- **`audits/*` are read-only artifacts.** Do not edit any audit report.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-3-strategic-reasoner` with a title like `task 3.9: strategic reasoner + sub-phase c integration substrate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §4.4, DESIGN.md §6.6), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
