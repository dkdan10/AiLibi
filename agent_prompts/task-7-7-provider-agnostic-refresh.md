# Agent Prompt — 7.7 Provider-agnostic refresh + parametrized per-game budget

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.7 — Provider-agnostic refresh + parametrized per-game budget, anchored to tasks/phase-7-plan.md W0.4, "Provider / eval-infra track"; the Phase 7 Ollama-enablement plan (refresh must select Ollama; 7-player meetings need a higher token budget); DESIGN.md §9, §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-provider-agnostic-refresh`
**Depends on:** 7.1 merged, 7.4 merged, 7.5 merged
**Section refs:** tasks/phase-7-plan.md W0.4, "Provider / eval-infra track"; the Phase 7 Ollama-enablement plan (refresh must select Ollama; 7-player meetings need a higher token budget); DESIGN.md §9, §11.4
**Complexity:** Medium

The sample-refresh path is hard-wired to Anthropic and to a tight per-game budget
that the diagnosis showed is too low for 7-player meetings. Task 7.8 runs the
meeting-heavy eval set on the local Ollama provider (7.5), so this task makes the
refresh provider-agnostic and parametrizes the per-game budget so a free, local,
higher-token run is possible without editing the script each time.

`scripts/refresh_samples.sh`: stop forcing `AILIBI_LLM_PROVIDER=anthropic`; allow
`ollama` (and keep `anthropic` working). Replace the hard `ANTHROPIC_API_KEY`
preflight with a **provider-aware** check: for `anthropic`, keep requiring the API
key; for `ollama`, instead ping `AILIBI_OLLAMA_HOST` for reachability AND confirm the
configured model (`qwen2.5:7b-instruct`) is actually pulled (fail loud with a clear
message if the server is down or the model is missing — AGENTS.md "no silent
fallbacks"). The `--dry-run` echo must show the selected provider and which
preflight ran. EXTEND Task 7.4's merged `--dry-run` echo block (the roster /
`SAMPLE_DIR` lines) with the provider + preflight lines — do NOT replace it (7.7
depends on 7.4, so it builds on the merged version).

Parametrize the per-game budget. Today `eval/balance_eval.py:221` constructs
`GameBudget(max_cost_usd=1.00)` with a fixed cost cap and token caps. Introduce an
env knob (e.g. `AILIBI_MAX_COST_USD`) read by `eval/balance_eval.py` so the per-game
USD cap is configurable, and scale the **token** caps to the roster (a 7-player
meeting needs more tokens than a 4-player one) via a named-constant LINEAR form:
`max_input_tokens = BASE_INPUT + PER_PLAYER_INPUT * num_players` and
`max_output_tokens = BASE_OUTPUT + PER_PLAYER_OUTPUT * num_players` with NAMED
constants (not magic numbers). Choose the constants so the **4p/1i preset
reproduces today's `GameBudget` caps exactly** (the frozen baseline path is
unchanged when the knob is unset); 7p/2i then resolves to a larger cap. For the
Ollama provider the USD cap is effectively disabled (per 7.5's zeroed cost
dimension), so on Ollama the token caps are the operative ceiling and must be large
enough to fit 7-player meetings.

This task consumes 7.1's roster/task flags (already threaded into the refresh by
7.4) and 7.5's Ollama provider; it does NOT add new CLI flags to
`scripts/run_tournament.py` (the budget is an env knob on the harness, not a new
tournament flag) and does NOT edit the Ollama client or the loader. It runs in
PARALLEL with 7.6 (disjoint files). No sample data is generated or committed here
(that is 7.8); the refresh changes are validated on the fake provider + dry-run.

**Files in scope:**
- scripts/refresh_samples.sh
- eval/balance_eval.py
- tests/scripts/test_refresh_samples.py
- tests/eval/test_balance_eval.py

**Files NOT in scope:**
- scripts/run_tournament.py (no new tournament CLI flag — the budget is an env knob on the harness; the roster/task flags are 7.1's)
- llm/ollama_client.py, llm/provider.py, llm/budgeted_client.py, llm/budget.py (the provider client + budget-dimension wiring are Task 7.5; this task only reads an env knob into the per-game `GameBudget` construction)
- api/replay_loader.py, scripts/_manifest_writer.py (the roster-aware loader + per-set manifest routing are Task 7.4; consume them, do not edit)
- replays/samples/ (no sample generation; that is Task 7.8)
- eval/meeting_quality.py (the `meeting_rate` metric is 7.3's)
- DESIGN.md (design-thread-owned)
- frontend/ (no frontend surface)

**Definition of done:**
- [ ] `scripts/refresh_samples.sh` no longer forces `AILIBI_LLM_PROVIDER=anthropic`; it honors `ollama` and `anthropic`, and the `--dry-run` echo shows the selected provider + the preflight that ran.
- [ ] The `ANTHROPIC_API_KEY` preflight is replaced by a provider-aware check: `anthropic` still requires the key; `ollama` instead pings `AILIBI_OLLAMA_HOST` for reachability AND confirms the configured model is pulled, failing loud (clear message, non-zero exit) when the server is down or the model is missing.
- [ ] `eval/balance_eval.py`'s per-game `GameBudget(max_cost_usd=1.00)` (line ~221) is parametrized via an env knob (e.g. `AILIBI_MAX_COST_USD`); the token caps follow the named-constant LINEAR form (`max_input_tokens = BASE_INPUT + PER_PLAYER_INPUT * num_players`, `max_output_tokens = BASE_OUTPUT + PER_PLAYER_OUTPUT * num_players`, no magic numbers) so a 7-player meeting fits; the constants are chosen so the 4p/1i preset reproduces today's `GameBudget` caps exactly, and when the knob is unset the 4p/1i defaults are byte-identical to today (the frozen baseline path is unchanged).
- [ ] On Ollama the USD cap is effectively disabled (per 7.5) and the roster-scaled token caps are the operative ceiling for 7-player meetings; on Anthropic the existing dollar + token caps still apply.
- [ ] `tests/scripts/test_refresh_samples.py` covers the provider-aware preflight (ollama reachable/model-present → proceeds; server-down or model-missing → fails loud; anthropic still requires the key) via `--dry-run`/mocked checks, without real spend.
- [ ] `tests/eval/test_balance_eval.py` covers the parametrized budget (env knob overrides the per-game USD cap; roster-scaled token caps; unset → 4p/1i default unchanged).
- [ ] No sample data is generated or committed (that is Task 7.8); the changes validate on the fake provider + dry-run.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `scripts/refresh_samples.sh` (the forced `AILIBI_LLM_PROVIDER=anthropic` around
line 282 and the `ANTHROPIC_API_KEY` preflight around lines 247-253) and
`eval/balance_eval.py` (the `GameBudget(max_cost_usd=1.00)` construction at line 221
and its token caps). For the preflight, branch on the resolved provider: keep the
key check for `anthropic`; for `ollama` do a reachability ping of
`AILIBI_OLLAMA_HOST` (a `curl`/HTTP GET to the server's tags endpoint) and grep the
pulled-model list for `qwen2.5:7b-instruct`, erroring with a clear remediation
message ("start `ollama serve` / `ollama pull qwen2.5:7b-instruct`") on failure. For
the budget, read `AILIBI_MAX_COST_USD` (falling back to the current `1.00` default
so the unset path is byte-identical) and derive the token caps from the roster size
already available in `balance_eval.py` via the named-constant LINEAR form (`BASE_* +
PER_PLAYER_* * num_players`), with the constants picked so 4p/1i reproduces today's
caps exactly, so 7-player meetings are not truncated. Note
that on Ollama the dollar cap is moot (7.5 zeroes the cost dimension), so the token
caps are what actually matter there — size them for 7p/2i. The `--dry-run` path in
the script is the testable surface (no spend), so assert the provider/preflight
branching there. Coordinate with 7.4 (already merged): the roster/task flags are
threaded by 7.4's refresh edits; this task adds the provider-aware preflight + budget
knob on top of that merged version, which is why it depends on 7.4.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.ollama_client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import observation.packet.SelfView"`
- `uv run python -c "import orchestrator.game"`

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
Open a PR from branch `phase-7-provider-agnostic-refresh` with a title like `task 7.7: provider-agnostic refresh + parametrized per-game budget`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-7-plan.md W0.4, "Provider / eval-infra track"; the Phase 7 Ollama-enablement plan (refresh must select Ollama; 7-player meetings need a higher token budget); DESIGN.md §9, §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
