# AiLibi Pre-Phase-3 Verification Audit

- **Date:** 2026-05-16 00:09 local
- **Verified HEAD:** `5988e66 update audit prompts for re-audit` on `main`
- **Spec:** `audits/audit-2026-05-15-0225-reconciled.md` §10 + §13
- **Scope:** read-only closure adjudication of R-1 through R-14; no fixes, no new findings

## 1. Verdict

**Verification passed — Phase 3 may begin.** All R-ids are `Closed` or
`Closed-via-Phase-3-addendum` (R-6, R-9, R-10). Zero `Partial`, zero
`Not closed`. Every required command succeeded with non-zero impostor
*and* crew wins, all six sweep seeds reached a decisive outcome, the
static gate is green at 289 tests, and every R-id-specific code or doc
anchor named in §5 of the prompt exists at this HEAD.

## 2. Commands run

| Command | Exit / last line |
|---|---|
| `bash scripts/check.sh` | 0; `============================= 289 passed in 3.46s ==============================` |
| `uv run lint-imports` | 0; `Contracts: 1 kept, 0 broken.` |
| `uv run pytest` | (subsumed by `check.sh`); `289 passed in 3.46s` |
| `git grep -nE "['\"](player\|impostor)-[0-9]+['\"]" eval/ tests/` | 1 (no matches; required empty) |
| `git grep -nE "['\"](player\|impostor\|victim\|observer\|crew-[0-9]+)['\"]" tests/observation/test_service.py` | 1 (no matches; required empty) |
| Six-seed sweep `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/verify-r-$seed.jsonl --max-ticks 1000; done` | All 0; outcomes: seeds 0/1/2/7/42 → `CREWMATES`, seed 100 → `IMPOSTORS` (6/6 decisive) |
| `uv run python scripts/run_tournament.py --num-games 20 --start-seed 0 --output-dir /tmp/verify-tournament --max-ticks 1000` | 0; `decisive_split: CREWMATES=80.00% IMPOSTORS=20.00% of 20 decisive` (crew_wins=16, impostor_wins=4, tick_budget_reached=0, meeting_phase_reached=0) |
| `uv run pytest tests/agents/test_impostor_policy.py -v -k "Stale or Dead"` | 0; `5 passed, 23 deselected in 0.16s` |
| `uv run pytest tests/engine/test_tick.py -v -k "dead_crewmate"` | 0; `1 passed, 28 deselected in 0.16s` |
| `uv run pytest tests/eval/test_balance_eval.py -v -k "canonical_balance or default_agent_sweep"` | 0; `2 passed, 12 deselected in 0.33s` |
| `uv run pytest tests/observation/test_service.py -v -k "audit_log_appends"` | 0; `1 passed, 9 deselected in 0.15s` |
| `uv run pytest tests/engine/test_tick_properties.py -v` | 0; `4 passed in 1.54s` |

Auxiliary reads used for closure pins (not commands, but cited below):
`agents/tactical/impostor_policy.py`, `engine/tick.py`, `DESIGN.md`,
`tasks/phase-2.md`, `tasks/phase-3.md`,
`tests/engine/test_tick_properties.py`,
`tests/observation/test_service.py`.

## 3. R-id closure table

| R-id | Severity | Disposition | Evidence | Phase-3 blocker? |
|---|---|---|---|---|
| R-1 | Critical | Closed | 20-game tournament: `CREWMATES=80.00% IMPOSTORS=20.00% of 20 decisive` (crew_wins=16, impostor_wins=4, 0 non-decisive). Both sides above the >20% smoke threshold; impostor side at exact 20.00% reflects 1/20 granularity, not the original R-1 failure mode of 0 crew wins. The 100-game gate already passed at PR #31 baseline 73.12%/26.88%. | no |
| R-2 | Critical | Closed | Six-seed sweep: seeds 0/1/2/7/42 → `CREWMATES`, seed 100 → `IMPOSTORS`; 6/6 decisive (PR #31 baseline was 6/6 decisive). | no |
| R-3 | High | Closed | `agents/tactical/impostor_policy.py:86` defines `_STALENESS_THRESHOLD: Final[int] = 30`; `:94` defines `_BODY_ID_VICTIM_PATTERN`; `:244` defines `_confirmed_dead_from_bodies`; `:307` and `:309` apply the `confirmed_dead` and staleness filters inside `_scored_targets`. `TestImpostorStaleAndDeadTargetPruning` (4 tests) plus `test_stale_sighting_in_own_room_does_not_trigger_kill` → 5/5 passed. | no |
| R-4 | High | Closed | `git grep ... eval/ tests/` returns empty (exit 1). Scanner self-tests in `eval/leak_test.py` and `tests/eval/test_balance_eval.py` still execute under `check.sh` (the `leak_test.py` and `test_balance_eval.py` rows in the `check.sh` output show all dots, no failures), confirming the value scanner still trips on the substring `crew` planted there without re-introducing the old `(player\|impostor)-N` literal. | no |
| R-5 | Concern | Closed | `DESIGN.md:287` documents the `dropped` rule ("When a crewmate dies, their incomplete tasks are removed from `state.tasks`…"); `DESIGN.md:289` documents the kill-triggers-crew-win consequence and names `engine/tick.py::_apply_kill` as the anchor. `engine/tick.py:240` defines `_apply_kill`; `:258` removes the killed player's incomplete tasks. `test_dead_crewmate_incomplete_task_is_dropped_and_crew_can_still_win` passed. | no |
| R-6 | Concern | Closed-via-Phase-3-addendum | `tasks/phase-3.md:123` Task 3.3 DoD bullet: "**R-6 acceptance gate (per `audits/audit-2026-05-15-0225-reconciled.md` §R-6):** `agents/memory/store.py` exposes a composite memory surface that aggregates the episodic, working, and belief state introduced in Task 2.3 … `render_for_prompt` produces its structured view by reading from all three components, not from any one of them in isolation." | no |
| R-7 | Medium | Closed | `tasks/phase-2.md:865-872` (inside the Task 2.8.5 body, which spans `:700-906`, sitting between the implementation-hint debugging snippet ending `:863` and the `**Integration risk:**` block at `:874`) contains: "Historical note (added 2026-05-15 by Task 2.11): the merged PR for this task (commit `e3b2a60`) also touched `eval/determinism_test.py`, `tests/engine/test_actions.py`, `tests/engine/test_events.py`, `tests/engine/test_world_state.py`, `tests/orchestrator/test_seeder.py`, and `agent_prompts/task-2-9-headless-tournament-harness.md` …" — the exact file list R-7 called out. | no |
| R-8 | Medium | Closed | `tasks/phase-2.md:936` (Task 2.9 DoD) and `tasks/phase-2.md:1591` (Phase 2 Merge Criteria) both read "Both decisive sides win > 20% of decisive games (CREWMATES and IMPOSTORS outcomes); \`TICK_BUDGET_REACHED\` games are reported separately and do not count toward decisive totals." — wording is verbatim identical (only the leading bullet marker differs: DoD checkbox `- [ ]` vs criterion bullet `-`, which is the document-structure distinction). | no |
| R-9 | Concern | Closed-via-Phase-3-addendum | `tasks/phase-3.md:444` Task 3.12 DoD bullet: "**R-9 acceptance gate (per `audits/audit-2026-05-15-0225-reconciled.md` §R-9):** `ReplayEntry` — or its Phase 3 successor introduced by this task — records meeting transcripts, prompt versions, LLM outputs, and cost metadata per DESIGN.md §11.4. The replay-determinism test exercises at least one long-horizon replay (≥ 200 ticks or one full meeting cycle, whichever is longer) and asserts byte-for-byte identity." | no |
| R-10 | Concern | Closed-via-Phase-3-addendum | `tasks/phase-3.md:124` (Task 3.3) — R-10 bullet: leak scanners reused against `render_for_prompt` golden outputs in `tests/agents/test_memory_rendering.py`, with at least one planted negative test. `tasks/phase-3.md:335` (Task 3.9) — R-10 bullet: scanners reused against strategic prompt inputs in `tests/agents/test_strategic_reasoner.py`, with at least one planted negative test. Both bullets reference the reconciled audit. | no |
| R-11 | Concern | Closed | `tests/eval/test_balance_eval.py` contains `test_default_agent_sweep_reaches_at_least_one_decisive_outcome` — passed under targeted run. Visible under `check.sh` as part of `tests/eval/test_balance_eval.py ..............` (14 tests). | no |
| R-12 | Low | Closed | `tests/engine/test_tick_properties.py:181-212` defines the role-aware `_role_aware_actions` Hypothesis strategy drawing from `kill` / `vent` / `report` / `wait`; `:215-243` defines `test_advance_tick_does_not_raise_under_role_aware_actions` exercising the broader vocabulary. All 4 property tests passed. | no |
| R-13 | Low | Closed | `tests/observation/test_service.py` contains `test_audit_log_appends_across_two_instances` — passed under targeted run. | no |
| R-14 | Concern | Closed | `tests/observation/test_service.py` grep returns empty. Helpers at `:50-53` use `"p-1"`, `"p-2"`, `"p-3"`, `"p-4"` ids exclusively (visually confirmed by Read). | no |

**Counts:** Closed = 11 · Closed-via-Phase-3-addendum = 3 · Partial = 0 · Not closed = 0.

## 4. Observations

None outside R-1...R-14's scope.

## 5. Verdict justification

Every R-id in §3 is `Closed` or `Closed-via-Phase-3-addendum`, with no
`Partial` or `Not closed` rows, so by §6 of the prompt the verdict is
**Verification passed**. All required commands exited 0 (the two greps
correctly exited 1 because "no matches" was the required outcome). The
two Critical pins for behavioral balance (R-1, R-2) are met by direct
observation at this HEAD — 16 crew wins and 4 impostor wins over 20
games, with 6/6 sweep seeds decisive — and the static R-3 fix
(`_STALENESS_THRESHOLD`, `_BODY_ID_VICTIM_PATTERN`,
`_confirmed_dead_from_bodies`, `_scored_targets` filters) is present
and pinned by the `TestImpostorStaleAndDeadTargetPruning` regressions.
R-7's historical-note block sits where the prompt required (between
the Implementation hint and the Integration risk block in Task 2.8.5),
and R-8's DoD/Merge Criteria wording is verbatim identical. The three
Phase 3 addenda (R-6 in Task 3.3, R-9 in Task 3.12, R-10 in both Task
3.3 and Task 3.9) each cite the reconciled audit and name the
implementation surfaces and planted-negative-test obligations the
audit asked for. No command failed; no doc, code, or test evidence is
absent.
