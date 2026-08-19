# Agent Prompt — 5.5 Cost dashboard metric

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.5 — Cost dashboard metric, anchored to DESIGN.md §10.4, DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-cost-dashboard`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §10.4, DESIGN.md §11.3
**Complexity:** Medium

A pure analyzer over `eval.report_schema.TournamentReport` that produces the
cost-dashboard data (DESIGN.md §10.4 Cost bullet for the ~$0.20/game target;
§11.3 reporting; the per-game cost substrate is
`orchestrator.replay.compute_cost_usd` / `eval.report_schema.GameCostSummary`):
cost-per-game and cost-per-prompt-version, so a prompt change's cost impact
is legible alongside its quality impact. This is the cost half of the Phase 5
close loop — a prompt-template change should show both a metric delta (5.2–5.4)
and a cost delta here.

The inputs, all on the merged schema:

- `GameReport.cost: GameCostSummary` — per game: `total_cost_usd`,
  `total_input_tokens`, `total_output_tokens`, `by_model: Mapping[str,
  float]` (USD keyed by model id).
- `GameReport.prompt_versions: Mapping[str, str]` — template name → version
  marker in play for that game (templates load once per run, so this is
  game-granular).
- `GameReport.failed_calls: tuple[FailedCallReplayEntry, ...]` — meeting-
  aborting LLM calls whose `cost_usd` was still charged. `GameCostSummary.total_cost_usd`
  ALREADY includes this spend: the canonical reducer
  `orchestrator.replay.compute_cost_usd` sums meeting `llm_calls` cost PLUS
  every `failed_call` cost (replay.py:452-458), and the `GameReport.failed_calls`
  docstring states the total counts them. So the dashboard reads
  `total_cost_usd` as authoritative and must NOT add `failed_calls` cost again.
- `MeetingReport.llm_calls` — per-call `LLMCallRecord` (`model`, `cost_usd`,
  tokens) if finer-than-game slicing is needed.

**Files in scope:**
- eval/cost_dashboard.py
- tests/eval/test_cost_dashboard.py

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- scripts/run_tournament.py
- eval/report_schema.py
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/cost_dashboard.py` exposes a pure function from a `TournamentReport` to a frozen Pydantic result model with at least: total tournament cost, mean cost-per-game, and a cost-per-prompt-version breakdown.
- [ ] Cost-per-prompt-version is keyed by `(template_name, version)` drawn from each game's `prompt_versions`, summing the games that ran that version. A game runs several templates at once; bias: attribute the full game cost once under EACH `(template, version)` present (do NOT split it across templates). Document in the PR's `## Decisions` block that the per-version totals therefore OVERLAP and are NOT a partition — summing them across versions does not recover the tournament total and must not be presented as if it does.
- [ ] Within a single tournament run `prompt_versions` is constant across all games (one template set is loaded per run), so for a real one-run report the per-`(template, version)` breakdown collapses to one key equal to the tournament total. Its comparative value (version A vs version B) is therefore a CROSS-REPORT comparison — two runs, consumed by Task 5.8's regression loop — not a within-report delta. The result model should be cleanly comparable/mergeable across two `CostDashboard`s for that purpose, or the contract states that 5.8 computes the cross-run delta from two dashboards.
- [ ] The metric treats `GameCostSummary.total_cost_usd` as the authoritative complete per-game spend and does NOT add `sum(fc.cost_usd for fc in failed_calls)` on top — `total_cost_usd` already includes failed-call cost (via `orchestrator.replay.compute_cost_usd`; confirmed by the `GameReport.failed_calls` docstring). Note this no-double-count invariant in the PR's `## Decisions` block. (The matching loader-side obligation — Task 5.6 populates `total_cost_usd` via `compute_cost_usd` and does not double-add — is carried into 5.6's elaboration.)
- [ ] A per-model cost roll-up is available (aggregating `GameCostSummary.by_model` across games), so a mixed-tier tournament is auditable per model.
- [ ] Partial-replay robustness: a game with zero meetings/zero cost, an empty `prompt_versions`, or a tournament with one game all produce well-defined numbers (no division-by-zero, no NaN).
- [ ] `tests/eval/test_cost_dashboard.py` builds report fixtures directly covering: a structural/constructibility fixture with two prompt-versions present (verify per-version keying and summation — labelled as a constructibility test, since a real single run carries one version set); a single-version report that collapses to one key equal to the total cost; a game carrying `failed_calls` (verify the dashboard does NOT double-count failed-call spend); and a mixed-`by_model` game.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

See DESIGN.md §10.4. Aggregate over `report.games`: total cost is the sum of
each game's `cost.total_cost_usd` (which already includes failed-call spend —
do NOT add `failed_calls` again); cost-per-prompt-version groups games by
their `prompt_versions` entries. `orchestrator.replay.compute_cost_usd` is the
canonical file-level cost reducer (and is what already folds failed calls
in), but this metric works over the already-aggregated report, not raw JSONL —
do not re-read files. Build fixtures by instantiating the schema
models directly; this task does NOT wire the dashboard into tournament JSON
output (Task 5.6) and does NOT build the frontend (Task 5.7) — it produces
the typed data those consume.

## Public types this task introduces
- `eval.cost_dashboard.CostDashboard`
- `eval.cost_dashboard.PromptVersionCost`
- `eval.cost_dashboard.compute_cost_dashboard`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.report_schema"`
- `uv run python -c "import orchestrator.replay.ReplayLog"`
- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-5-cost-dashboard` with a title like `task 5.5: cost dashboard metric`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §10.4, DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
