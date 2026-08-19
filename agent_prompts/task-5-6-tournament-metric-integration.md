# Agent Prompt — 5.6 Tournament metric integration

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.6 — Tournament metric integration, anchored to DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-tournament-metric-integration`
**Depends on:** 5.2 merged, 5.3 merged, 5.4 merged, 5.5 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Integration

The convergence point for Phase 5. Four things, in order:

1. **Build the JSONL→`TournamentReport` loader** (deferred from Task 5.1, does
   not exist yet). A tournament run already writes one
   `replay-seed-{seed}.jsonl` per seed (`eval.balance_eval.run_balance_eval`)
   and `orchestrator.replay.read_all_entries(path)` parses each back into the
   typed record union (`ReplayEntry` / `MeetingReplayEntry` /
   `GameEndReplayEntry` / `FailedCallReplayEntry`). The loader folds those
   records into a `GameReport` per seed and collects them into a
   `TournamentReport`. The `MeetingReplayEntry` → `MeetingReport` mapping is
   near 1:1 (same `meeting_id`/`tick`/`triggered_by`/`outcome`/
   `ejected_player_id`/`transcript`/`ballots`/`contradictions`/`llm_calls`).
   `GameEndReplayEntry` gives `winner`/`reason`/`final_tick`;
   `FailedCallReplayEntry` rows become `GameReport.failed_calls`.
2. **Populate `GameReport.roles` from the seeded game setup** — the single
   report field with no replay-JSONL source (roles are kept out of replay by
   the leak firewall, `report_schema.py:28-29`). `HeadlessGame.run()` returns a
   `HeadlessGameResult` whose `final_state: WorldState` carries
   `players[id].role` (`engine.world.WorldState.players` →
   `engine.entities.PlayerState.role`). Capture roles from that in-memory
   result during the run — NOT by re-parsing the replay file. An empty `roles`
   map is fail-loud: tasks 5.2–5.4 silently score zero impostor ejections /
   all-unresolved targets without it.
3. **Run the four metrics and wrap.** Call the merged public analyzers —
   `eval.vote_correctness.compute_vote_correctness`,
   `eval.accusation_calibration.compute_accusation_calibration`,
   `eval.alibi_fabrication.compute_alibi_fabrication_rate`,
   `eval.cost_dashboard.compute_cost_dashboard` — over the `TournamentReport`,
   and wrap report + the four results into a new frozen `TournamentEvalReport`
   model. Because `TournamentReport` is frozen + `extra="forbid"`, the metric
   outputs CANNOT be added as fields on it; they live on the new wrapper, which
   is the single typed shape Task 5.7 (dashboard) and Task 5.8 (regression
   suite) consume.
4. **Emit + supersede.** `scripts/run_tournament.py` emits the
   `TournamentEvalReport` as JSON. This supersedes `eval.balance_eval.BalanceReport`
   as the tournament artifact per Task 5.1's `## Decisions` (Task 5.1 deferred
   the migration here).

**Files in scope:**
- eval/meeting_quality.py
- eval/balance_eval.py
- scripts/run_tournament.py
- tests/eval/test_tournament_report.py
- tests/eval/test_balance_eval.py (only if the `run_balance_eval` refactor in the migration decision perturbs its existing assertions; leave untouched otherwise)

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- meetings/ (import its schemas; do not modify)
- orchestrator/ (import `read_all_entries`, `compute_cost_usd`, `HeadlessGame`; do not modify)
- eval/report_schema.py (the frozen 5.1 hub — import `TournamentReport`/`GameReport`/`MeetingReport`/`GameCostSummary`; do NOT edit it. The metric-output wrapper is a NEW model in eval/meeting_quality.py, not a field added here.)
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] A loader builds a `eval.report_schema.TournamentReport` from a tournament run: one `GameReport` per seed assembled from that seed's replay records (via `orchestrator.replay.read_all_entries`), with `meetings` from `MeetingReplayEntry`, `winner`/`reason`/`final_tick` from `GameEndReplayEntry`, and `failed_calls` from `FailedCallReplayEntry`.
- [ ] `GameReport.roles` is populated from the seeded game setup (`HeadlessGameResult.final_state.players[id].role`), NOT the replay JSONL. An empty/missing `roles` for a finished game is a fail-loud error.
- [ ] `GameReport.cost` (`GameCostSummary`) is built so `total_cost_usd` equals `orchestrator.replay.compute_cost_usd(path)` — the canonical reducer, which ALREADY folds in `failed_calls` cost. `total_input_tokens` / `total_output_tokens` / `by_model` are summed across the same records (meeting `llm_calls` plus `failed_calls`) in one pass. The dashboard (5.5) must NOT add failed-call cost again — this loader is the single place that spend is counted (the no-double-count invariant).
- [ ] A new frozen, `extra="forbid"` wrapper model in `eval/meeting_quality.py` (e.g. `TournamentEvalReport`) holds the immutable `TournamentReport` plus the four metric result models (`VoteCorrectnessReport`, `AccusationCalibrationReport`, `AlibiFabricationReport`, `CostDashboard`) as named fields. A builder (e.g. `build_tournament_eval_report`) calls the four `compute_*` analyzers and assembles it; it consumes their public APIs and duplicates no metric logic.
- [ ] `scripts/run_tournament.py` emits the `TournamentEvalReport` as JSON (validated round-trip: `model_validate_json(model_dump_json(...))`). `python scripts/run_tournament.py --num-games 200 --output-dir <dir>` (the merge criteria's "--N=200") produces a JSON report carrying all four Phase 5 metrics over a 200-game run.
- [ ] The `BalanceReport` migration decision (below) is executed: the `TournamentReport`/`TournamentEvalReport` supersedes `BalanceReport` as the emitted artifact, with crew/impostor/tick-budget buckets recoverable from `GameReport.winner` (`CREWMATES`/`IMPOSTORS`/`None`) and `seeds_used` — no information loss (already proven by `tests/eval/test_report_schema.py`).
- [ ] Partial-run robustness: a seed whose game crashed before a `game_over` record yields a `GameReport` with `winner=None`, `final_tick=None`, and whatever meetings were recorded — the loader does not raise on a missing `game_over` (it still fails loud on a doubled/corrupted file via `read_all_entries`'s `CorruptedFileError`).
- [ ] `tests/eval/test_tournament_report.py` runs a small tournament with the FAKE provider (no network), and asserts: every `GameReport.roles` is non-empty with key set == the game's players and exactly `num_impostors` entries `== "IMPOSTOR"`; the emitted JSON validates against the schema; all four metric blocks are present; and per-game `cost.total_cost_usd` equals `compute_cost_usd` for that seed (no double-count).
- [ ] All four `compute_*` are invoked via their public module entry points; no metric math is reimplemented in this task.
- [ ] `uv run mypy --strict eval` passes (and `scripts` if covered by mypy config).
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes (the firewall: `eval/` may import `engine`/`orchestrator`/`meetings`; none of those import back).
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes (including the untouched `test_balance_eval.py`, unless the migration decision intentionally edits it).
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Loader recipe, per seed:

```python
entries = read_all_entries(output_dir / f"replay-seed-{seed}.jsonl")
meetings = tuple(MeetingReport(...) for e in entries if isinstance(e, MeetingReplayEntry))
failed   = tuple(e for e in entries if isinstance(e, FailedCallReplayEntry))
end      = next((e for e in entries if isinstance(e, GameEndReplayEntry)), None)
roles    = {pid: ps.role for pid, ps in result.final_state.players.items()}  # from HeadlessGameResult
cost     = _game_cost_summary(entries)  # total via compute_cost_usd; tokens + by_model summed in-pass
game = GameReport(game_id=..., seed=seed, winner=end.winner if end else None,
                  reason=end.reason if end else "...", final_tick=end.tick if end else None,
                  roles=roles, replay_ref=f"replay-seed-{seed}.jsonl",
                  meetings=meetings, failed_calls=failed, prompt_versions=..., cost=cost)
```

Recommended structure: add `run_tournament_eval(...) -> TournamentReport` to
`eval/balance_eval.py` doing the run + roles capture + assembly, and reduce the
existing `run_balance_eval(...) -> BalanceReport` to a thin wrapper over it
(so `test_balance_eval.py` stays green and there is one game-running path).
`prompt_versions` collapses from the per-meeting `MeetingReplayEntry.prompt_versions`
(constant within a run); for a game with no meetings, leave it empty (the cost
dashboard handles empty). The wrapper + builder live in `eval/meeting_quality.py`.
Use the FAKE provider in tests — never call a real model in CI.

## Public types this task introduces
- `eval.meeting_quality.TournamentEvalReport`
- `eval.meeting_quality.build_tournament_eval_report`
- `eval.balance_eval.run_tournament_eval`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Convergence point for Phase 5 — Tasks 5.7 and 5.8 build on the `TournamentEvalReport` shape this task defines.

- **`roles` population is the silent-zero trap.** If the loader is built purely from replay files (the obvious reading of "fold metrics into the report"), `roles` is empty and vote-correctness / accusation-calibration / alibi-fabrication all silently report zero impostor signal. Roles MUST come from the in-memory seeded result, and the test asserts non-empty coverage.
- **No double-counting cost.** `compute_cost_usd` already includes failed-call spend; the loader populates `total_cost_usd` via it and the 5.5 dashboard never re-adds `failed_calls`. Building `total_cost_usd` any other way risks drift.
- **Do not edit the frozen hub or the metric modules.** `report_schema.py` and the four `eval/*` metric files are import-only. A schema change here means 5.1 was wrong — stop and report.
- **Determinism / no network.** Integration tests run the fake provider on a few seeds; the 200-game JSON check is a local/manual gate, not CI.
- **BalanceReport migration must not break out-of-scope tests.** `test_balance_eval.py` asserts `isinstance(report, BalanceReport)`; the thin-reducer approach preserves that. Full retirement requires pulling that test into scope deliberately.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.cost_dashboard"`
- `uv run python -c "import eval.report_schema"`
- `uv run python -c "import orchestrator.replay.ReplayLog"`
- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`
- `uv run python -c "import eval.alibi_fabrication"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.vote_correctness"`

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
Open a PR from branch `phase-5-tournament-metric-integration` with a title like `task 5.6: tournament metric integration`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
