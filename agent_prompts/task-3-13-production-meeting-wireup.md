# Agent Prompt — 3.13 Production meeting wire-up (close R-1 + R-2 from the Pre-Phase-4 reconciled audit)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.13 — Production meeting wire-up (close R-1 + R-2 from the Pre-Phase-4 reconciled audit), anchored to DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-public-meeting-wireup`
**Depends on:** 3.12 merged
**Section refs:** DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4
**Complexity:** Medium

Close the two High findings and two related Concerns identified by
`audits/audit-2026-05-25-0414-reconciled.md` §10, all of which describe
the same underlying gap: Tasks 3.9–3.12 built the meeting machinery and
the budgeted-LLM-client adapter as correct, isolated, well-tested
components — but no production entry-point actually wires them
together. The public CLI (`scripts/run_game.py`,
`scripts/run_tournament.py`, `eval/balance_eval.py`) constructs
`HeadlessGame` without a `meeting_runner=` kwarg, so the engine's
`MEETING` phase falls through to the legacy `MEETING_PHASE_REACHED`
outcome. A reconstructed 100-game tournament at the post-3.12 HEAD
produced `meeting_entries=0` across 100 replay files: meetings do not
fire from any public path. Separately, `BudgetedLLMClient` exists with
20 unit tests but `grep -rn "BudgetedLLMClient" orchestrator/ meetings/
agents/strategic/ scripts/ eval/balance_eval.py` returns only two
docstring references — production never constructs one, so the
`≤ $0.30/game` merge criterion can only be measured post-hoc from
replay logs, not enforced at call time.

This task closes:

- **R-1 [High]** — public CLI / tournament harness still pauses at
  `MEETING_PHASE_REACHED`.
- **R-2 [High]** — `BudgetedLLMClient` + `GameBudget` not wired into
  the orchestrator / meeting / strategic-reasoner production paths.
- **R-5 [Concern]** — no end-to-end test routes through the canonical
  `llm.fake_provider.FakeProvider`. Folds into R-1 for free by using
  `FakeProvider` as the default provider during the wire-up.
- **R-6 [Concern]** — no helper for per-game cost aggregation from a
  replay log. ~5-LOC helper the real-provider 50-game eval will need
  immediately after this task lands.

**Explicitly out of scope:**

- **R-3 [Concern]** (per-call `prompt_version` on `LLMCallRecord`).
  Defer to the real-provider eval owner — meeting-level mapping is
  currently functionally sufficient.
- **R-4 [Concern]** (`StrategicReasoner` defined but unused;
  defense-in-depth scanner bypassed in production meeting flow).
  Primary leak protection (observation packet scanning) is intact and
  passed the 100-log live tournament scan with zero violations.
  Reasoner consolidation is a significant refactor and warrants its
  own task if pursued; this task does not unify the meeting flow
  through `StrategicReasoner`.

**Wire-up shape: option (b) from the reconciled audit's recommended
action.** Make the meeting runner the production default; quarantine
the legacy `MEETING_PHASE_REACHED` outcome behind an explicit opt-out
that only Phase 2 byte-identity tests (`tests/orchestrator/test_game.py`
and similar) use. The public CLI never reaches `MEETING_PHASE_REACHED`.
This is cleaner than option (a) (a `--enable-meetings` flag defaulting
on) because it removes a backward-compat surface that exists only to
keep the pre-Task-3.12 legacy path runnable, and the byte-identity
tests already have a reason to opt out — they want engine-only replay,
not LLM-driven replay.

**Files in scope:**
- scripts/run_game.py
- scripts/run_tournament.py
- eval/balance_eval.py
- orchestrator/game.py
- orchestrator/replay.py
- tests/orchestrator/test_meeting_integration.py
- tests/eval/test_balance_eval.py
- tests/llm/test_budgeted_client.py

**Files NOT in scope:**
- engine/
- observation/
- agents/tactical/
- agents/perception.py
- agents/memory/
- agents/runtime.py
- agents/base.py
- agents/strategic/reasoner.py
- agents/strategic/prompts/
- agents/strategic/output_schemas.py
- meetings/manager.py
- meetings/schemas.py
- meetings/transcript.py
- meetings/voting.py
- llm/client.py
- llm/provider.py
- llm/fake_provider.py
- llm/cache.py
- llm/budget.py
- llm/budgeted_client.py
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
- tests/observation/
- tests/meetings/
- tests/llm/test_client.py
- tests/llm/test_budget.py
- tests/engine/
- tests/eval/test_leak.py
- tests/orchestrator/test_action_ordering.py
- tests/orchestrator/test_boundary.py
- tests/orchestrator/test_game.py
- tests/orchestrator/test_replay.py
- tests/orchestrator/test_replay_meetings.py
- tests/orchestrator/test_seeder.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **R-1 — `HeadlessGame` meeting runner is the production default.** `scripts/run_game.py`, `scripts/run_tournament.py`, and `eval/balance_eval.py::run_balance_eval` all construct `HeadlessGame` with a `meeting_runner=` kwarg by default. The constructed runner is `DefaultMeetingRunner` wrapping the canonical `llm.fake_provider.FakeProvider` (R-5 closure: this is the canonical fake provider used through the orchestrator path). Construct one runner + one `GameBudget` per game; do not share runners or budgets across games in a tournament.
- [ ] **R-2 — `BudgetedLLMClient` wraps every production LLM call.** `orchestrator/game.py::DefaultMeetingRunner.__init__` (or an equivalent factory in the wire-up surface) accepts an optional `budget: GameBudget | None = None` kwarg. When `budget` is provided, the runner wraps `llm_client` in `BudgetedLLMClient(inner=llm_client, budget=budget)` before passing it through `_RecordingLLMClient` to `MeetingManager`. The three public entry-points always construct a `GameBudget` and pass it to the runner; the cost cap is enforced at call time, not post-hoc.
- [ ] **`MEETING_PHASE_REACHED` quarantined behind opt-out.** `HeadlessGame.run` continues to return `MEETING_PHASE_REACHED` when `meeting_runner=None`, but the three public entry-points never construct that path. The branch is reachable only by tests that explicitly pass `meeting_runner=None` (e.g. Phase 2 byte-identity tests that want engine-only behavior). Add a comment at the no-runner branch in `orchestrator/game.py` naming this contract: "engine-only opt-out for Phase 2 byte-identity tests; production paths always pass a runner."
- [ ] **R-6 — `compute_cost_usd(path)` helper.** `orchestrator/replay.py` exposes a helper `compute_cost_usd(path: Path) -> float` that walks the replay log and sums `LLMCallRecord.cost_usd` across all `MeetingReplayEntry` rows. ~5–15 LOC. Document the function as the canonical reduction for per-game cost; future eval code (including the real-provider 50-game eval) consumes it.
- [ ] **`eval/balance_eval.py` reframes `MEETING_PHASE_REACHED` bucket.** Since meetings now fire end-to-end from the public tournament path, `MEETING_PHASE_REACHED` should no longer appear as a normal non-decisive outcome bucket. Either: (a) remove the bucket and treat any `MEETING_PHASE_REACHED` in this path as a defect (raise), OR (b) keep the bucket but document that it should be zero after this task lands. Pick one and document in `## Decisions`.
- [ ] **End-to-end CI regression: meetings fire from the public CLI.** `tests/orchestrator/test_meeting_integration.py` adds a regression test that constructs `HeadlessGame` via the same factory path used by `scripts/run_game.py`, runs to completion, and asserts: (a) the replay log contains at least one `MeetingReplayEntry`, (b) the game outcome is NOT `MEETING_PHASE_REACHED`. Use the canonical `FakeProvider`; do not introduce a new inline stub. The test must fail against an implementation that reverts the runner wire-up.
- [ ] **End-to-end CI regression: budget cap propagates from production wire-up.** `tests/llm/test_budgeted_client.py` (or a new file in `tests/orchestrator/`) adds a regression that constructs the production wire-up with a tight `GameBudget` cap (e.g. `$0.01` per game) and runs a single game expected to fire at least one meeting. Assert `BudgetExceededError` propagates from the run-meeting flow, NOT silent truncation, NOT after the underlying client was called more than budget-cap times. The test must fail against an implementation that constructs `MeetingManager` without `BudgetedLLMClient` wrapping.
- [ ] **Tournament smoke after wire-up.** Run `uv run python scripts/run_tournament.py --num-games 10 --start-seed 0 --output-dir /tmp/task-3-13-smoke --max-ticks 1000`. Walk the resulting replay JSONLs (excluding `*.audit.jsonl`) and confirm at least one `MeetingReplayEntry` per game that reached the MEETING phase (most games will). Record the bucket counts, decisive split, and `meeting_entries` total in `## Decisions`.
- [ ] **Per-game cost aggregation works.** Use the new `compute_cost_usd(path)` helper on at least three of the 10 smoke games. Confirm the returned values are non-negative finite floats. Fake-provider costs are zero or near-zero; the helper must still return a sensible number (not crash on empty `LLMCallRecord` lists).
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] No Anthropic-specific concepts leak through the production wire-up. `git grep -nE "anthropic\|cache_control\|extended_thinking" orchestrator/ scripts/ eval/balance_eval.py` returns empty.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The four script edits are sibling shapes: each constructs a runner + budget + budgeted client + `HeadlessGame`. A factory helper in `orchestrator/game.py` (or `scripts/_meeting_factory.py` if you prefer to keep `orchestrator/` minimal) is the cleanest way to avoid duplication. Suggested shape:

```python
# orchestrator/game.py — illustrative; pick exact naming consistent with existing API
def build_default_meeting_runner(
    *,
    llm_client: LLMClient | None = None,
    budget: GameBudget | None = None,
) -> DefaultMeetingRunner:
    """Construct the production default meeting runner.

    If ``llm_client`` is None, the canonical ``FakeProvider`` is used.
    If ``budget`` is provided, wraps the LLM client in
    ``BudgetedLLMClient`` so the cap is enforced at call time.

    Production callers (``scripts/run_game.py``,
    ``scripts/run_tournament.py``, ``eval/balance_eval.py``) always pass
    a fresh ``GameBudget`` per game.
    """
    inner: LLMClient = llm_client or FakeProvider()
    client: LLMClient = (
        BudgetedLLMClient(inner=inner, budget=budget) if budget else inner
    )
    return DefaultMeetingRunner(
        llm_client=client,
        # ... existing kwargs unchanged
    )
```

Then each script becomes:

```python
# scripts/run_game.py — illustrative
runner = build_default_meeting_runner(budget=GameBudget(cost_usd_cap=0.30))
game = HeadlessGame(
    seed=args.seed,
    game_map=load_canonical_map(),
    replay_path=Path(args.replay_path),
    meeting_runner=runner,
    max_ticks=args.max_ticks,
)
```

`scripts/run_tournament.py` and `eval/balance_eval.py::run_balance_eval` follow the same pattern, but construct a NEW runner + budget per game (do not share across games in a tournament — the budget must reset, and the recording LLM client may carry per-game state).

## Public types this task introduces
- `orchestrator.game.build_default_meeting_runner` (or wherever the factory lands)`
- `orchestrator.replay.compute_cost_usd`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-3-public-meeting-wireup` with a title like `task 3.13: production meeting wire-up (close r-1 + r-2 from the pre-phase-4 reconciled audit)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
