# AiLibi Pre-Phase-4 Checkpoint Audit — Reconciled

- **Date:** 2026-05-25 04:14 local
- **Audited HEAD:** `639debc3a2b0dc912a95ff5f417d02b878957279` on `main`
- **Audit window:** `45e664f..HEAD` (Tasks 3.9, 3.10, 3.11, 3.12, plus post-3.8 audit + task-regeneration commit `b7cd6fd`)
- **Source audits reconciled:**
  - [audits/audit-2026-05-25-0357-claude.md](audit-2026-05-25-0357-claude.md) — verdict: *Ready for Phase 4 (pending real-provider eval), with one High finding*
  - [audits/audit-2026-05-25-0402-codex.md](audit-2026-05-25-0402-codex.md) — verdict: *Not ready*
- **Regression baseline:** [audits/audit-2026-05-16-0036-reconciled.md](audit-2026-05-16-0036-reconciled.md) (the prompt cites `audit-2026-05-15-0225-reconciled.md`; the 0036 file supersedes it for post-3.8 follow-through tracking and is read for that purpose only).
- **Scope:** read-only adjudication; no source/test edits; the two audit prompts that produced the source reports were intentionally not read. Live-LLM eval ($/game band, transcript readability, win-rate band) is **out of scope** per the source audits' framing — that stage belongs to `audits/prompts/pre-phase-4-real-provider-eval-prompt.md`.
- **Tool:** independent reconciler (no memory of either auditor's intent).

---

## 1. Executive Summary

**Verdict: Ready with fixes.** Two High-severity gaps must close before Phase 3 merge criteria can be evaluated and before the real-provider 50-game eval can safely run; Phase 4 *dispatch* (FastAPI scaffolding, WebSocket broadcast, React frontend) does not depend on those fixes and can begin in parallel. Static gates are green at `HEAD`: `bash scripts/check.sh` runs **663 passed + 1 deliberately-skipped** test, `uv run lint-imports` keeps the agent/engine firewall, `uv run mypy --strict agents observation orchestrator engine llm meetings` succeeds across 53 source files, `uv run ruff check .` + `ruff format --check .` are clean across 104 files, `validate_task_docs.py` confirms 63 tasks + 63 prompts in sync. All four required guard greps return empty: role-bearing literal ids in `eval/`/`tests/`, `anthropic|cache_control|extended_thinking` in `agents/`/`meetings/`/`orchestrator/`, `_BODY_ID_VICTIM_PATTERN` in `agents/`, and `from engine|import engine` under `agents/`/`llm/`/`meetings/`. The Phase 2 substrate is byte-for-byte unchanged: a fresh 100-game tournament returns `crew_wins=58 / impostor_wins=35 / tick_budget_reached=0 / meeting_phase_reached=7 → 62.37% / 37.63%` of 93 decisive games, identical to post-3.8.

Two findings are open as High. **R-1** is the public CLI/tournament path (`scripts/run_game.py`, `scripts/run_tournament.py`, `eval.balance_eval.run_balance_eval`): all three construct `HeadlessGame` without a `meeting_runner=` kwarg, so when the engine enters `MEETING` they return the legacy `MEETING_PHASE_REACHED` outcome. A fresh 100-game tournament reconstruction at `HEAD` confirms zero `MeetingReplayEntry` records were written across 100 replay files. The Phase 3 merge criterion *“50-game eval: full-LLM games complete end-to-end using fake-provider tests in CI”* cannot be exercised from any public entry-point today; the only full-meeting CI test is the single-game R-9 byte-identity gate at [tests/orchestrator/test_replay_meetings.py:389](tests/orchestrator/test_replay_meetings.py#L389), which uses an explicitly-constructed `DefaultMeetingRunner` and a `_DeterministicLLMClient` stub. **R-2** is the budget integration carry-over: `grep -rn "BudgetedLLMClient\|GameBudget" orchestrator/ meetings/ agents/strategic/` returns only two docstring references in `agents/strategic/reasoner.py`. The adapter exists at [llm/budgeted_client.py:93](llm/budgeted_client.py#L93) and is exhaustively unit-tested (20 cases), but no production path constructs one; the `≤ $0.30 / game` merge criterion can only be measured post-hoc from replay logs, not enforced at call time.

Both Low findings carried over from post-3.8 (`_COST_USD_CAP_SLACK` boundary, `last_seen` confirmed-dead suffix) **closed** by Task 3.9 DoD pins. The schema half of R-9 closed by `MeetingReplayEntry` + `LLMCallRecord`; the determinism gate is closed in CI (one-game with one meeting) but not exercised by the public harness because of R-1. The Concerns: (R-3) `LLMCallRecord` carries no per-call `prompt_version` or parsed output — those live at meeting level / inside transcript; (R-4) `StrategicReasoner` is defined but no production caller routes through it, so its prompt-input leak scanner is defense-in-depth that doesn't protect the meeting flow; (R-5) no end-to-end test uses `llm.fake_provider.FakeProvider` through the full orchestrator path; (R-6) no helper aggregates per-game cost from a replay file.

Total active findings: **0 Critical, 2 High, 0 Medium, 0 Low, 4 Concern.**

## 2. Verdict

**Ready with fixes.** Phase 4 dispatch (FastAPI scaffolding 4.1, WebSocket game broadcast 4.2, React frontend 4.3+) builds on the replay format, the orchestrator/runner protocol, and the engine boundary — all of which are correct on current `HEAD`. The two High findings block Phase 3 *closure* (R-1 prevents the merge criteria from being evaluated, R-2 prevents the cost cap from being enforced at call time) and the downstream real-provider eval, but they do not block Phase 4 work from starting in parallel. The two source audits' verdicts diverged here; see §13.3 for the reconciliation.

## 3. Commands Run and Evidence Sources

All commands ran from `/Users/danielkeinan/projects/AiLibi`. Exit code zero unless noted; `git grep` exits `1` on empty match — that is the desired result for the must-be-empty guards.

| Command | Result / evidence |
|---|---|
| `git rev-parse HEAD` | `639debc3a2b0dc912a95ff5f417d02b878957279` |
| `git log 45e664f..HEAD --oneline` | 12 commits in window (4 PR-merge commits + 7 task/review commits + post-3.8 task-regen commit `b7cd6fd`). |
| `git diff --name-only 45e664f..HEAD` | 25 changed files; `engine/`, `observation/`, `agents/tactical/`, `agents/perception.py`, `agents/memory/`, `llm/{client,budget,fake_provider}.py`, `meetings/{manager,schemas}.py`, `eval/balance_eval.py`, `scripts/run_*.py` — **none changed**. |
| `bash scripts/check.sh` | `663 passed, 1 skipped in 4.33s`; `Contracts: 1 kept, 0 broken.`; `Task docs validation passed: 63 tasks and 63 prompts.`; `All 63 prompts are in sync.` |
| `uv run pytest tests/orchestrator/test_replay_meetings.py::TestReplayRecordsMeetingArtifacts::test_byte_identical_long_horizon_meeting_replay -v` | `1 passed in 0.50s` (R-9 long-horizon byte-identity test passes with the runner explicitly configured). |
| `uv run python scripts/run_game.py --seed 0 --replay-path /tmp/recon-byte.jsonl --max-ticks 500` | `outcome: CREWMATES`, `final_tick: 11`. Replay walk: `tick_entries=12 meeting_entries=0`. Seed 0 game terminates before any meeting fires; the public harness's 500-tick byte-identity check is engine-only. |
| `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/recon-tournament --max-ticks 1000` | `games:100 crew_wins:58 impostor_wins:35 tick_budget_reached:0 meeting_phase_reached:7 decisive_split: CREWMATES=62.37% IMPOSTORS=37.63% of 93 decisive` — **byte-identical to post-3.8**. |
| Inline replay walk over the 100 tournament `*.jsonl` files (excluding `*.audit.jsonl`) | `replay_logs=100 tick_entries=964 meeting_entries=0` — **confirms R-1: public tournament writes zero meeting records.** |
| Inline leak scan via `_assert_no_recursive_hidden_fields` + `_assert_no_role_bearing_values` over the 100 `*.audit.jsonl` files | `audit_logs=100 packets=3275 victim_id_seen=True violations=0` (the two source audits counted observations differently and reported 6,550 packets — same finding either way: zero violations). |
| `grep -rn "BudgetedLLMClient\|GameBudget" orchestrator/ meetings/ agents/strategic/ scripts/ eval/balance_eval.py` (excluding tests) | 2 docstring references in `agents/strategic/reasoner.py`; no constructor / call site. **Confirms R-2.** |
| `grep -rn "StrategicReasoner" orchestrator/ meetings/ scripts/ eval/balance_eval.py` (excluding tests) | empty. **Confirms R-4.** |
| `git grep -nE "_BODY_ID_VICTIM_PATTERN" agents/` | empty (desired). |
| `git grep -nE "['\"](player\|impostor)-[0-9]+['\"]" eval/ tests/` | empty (desired). |
| `git grep -nE "anthropic\|cache_control\|extended_thinking" agents/ meetings/ orchestrator/` | empty (desired). |
| `grep -rn "from engine\|import engine" agents/ llm/ meetings/` | empty (desired). |

Key files read for adjudication: [tasks/phase-3.md §3.12 + Merge Criteria](tasks/phase-3.md), [orchestrator/game.py](orchestrator/game.py) (645-651 no-runner branch + 124-176 runner protocol + 240-297 `DefaultMeetingRunner` + 392-520 `apply_meeting_result`), [orchestrator/replay.py](orchestrator/replay.py) (51-72 `LLMCallRecord` + 86-116 `MeetingReplayEntry`), [scripts/run_game.py:71-80](scripts/run_game.py#L71), [eval/balance_eval.py:112-120](eval/balance_eval.py#L112), [meetings/manager.py](meetings/manager.py), [meetings/voting.py](meetings/voting.py), [meetings/transcript.py](meetings/transcript.py), [agents/strategic/reasoner.py:172-258](agents/strategic/reasoner.py#L172), [agents/strategic/prompts/loader.py:57](agents/strategic/prompts/loader.py#L57), [llm/budgeted_client.py:93](llm/budgeted_client.py#L93), [tests/orchestrator/test_replay_meetings.py:389](tests/orchestrator/test_replay_meetings.py#L389), [tests/orchestrator/test_meeting_integration.py:425-444](tests/orchestrator/test_meeting_integration.py#L425), [tests/llm/test_budget.py:270](tests/llm/test_budget.py#L270), [tests/agents/test_memory_rendering.py:706](tests/agents/test_memory_rendering.py#L706).

## 4. Regression Baseline

Procedure: for every prior-Pass row in the most recent post-3.8 audit baseline, `git diff --name-only 45e664f..HEAD -- <paths>` was used to confirm "no diff" rows, and re-running the relevant gate at `HEAD` was used to confirm "in-window diff" rows. Both source audits used `audit-2026-05-16-2239-claude.md` as their baseline; that table is adopted here with cells reconciled where the two audits disagreed.

| Prior-Pass item | Diff in window? | Status at HEAD |
|---|---|---|
| Phase 0 / CI / import lint / check scripts | No | **Still Pass (no diff)** |
| 1.1–1.7 engine + observation + visibility | No | **Still Pass (no diff)**; 100-game tournament numbers byte-identical to post-3.8. |
| 1.8 replay log (Phase 2 surface) | Yes (`orchestrator/replay.py`) | **Pass — Phase 2 surface preserved**; pre-Task-3.12 entries parse as `ReplayEntry` via the `kind = raw_entry.get("kind", "tick")` default at [orchestrator/replay.py:257](orchestrator/replay.py#L257); Phase 3 expansion (`MeetingReplayEntry` + `LLMCallRecord`) is additive and tested. |
| 1.B1 scripted fixtures, 1.B2 leak test | No | **Still Pass (no diff)**; 100-log / 3,275-packet leak scan confirms zero violations on the live tournament artifacts. |
| 2.1–2.7 boundary / agent base / memory / perception / pathing / tactical FSMs | No | **Still Pass (no diff)**. |
| 2.8 headless orchestrator (Phase 2 surface) | Yes (`orchestrator/game.py`) | **Pass — Phase 2 surface preserved**; the no-runner branch at [orchestrator/game.py:645-651](orchestrator/game.py#L645) preserves `MEETING_PHASE_REACHED` verbatim and the 100-game tournament reproduces post-3.8 byte-for-byte. *Note: this preservation is what makes R-1 a live finding — see §10.* |
| 2.9 tournament harness (`eval/balance_eval.py`) | No | **Still Pass (no diff)** for the Phase 2 contract, but does not satisfy the Phase 3 merge-criteria reading — see R-1. |
| 2.10–2.14 tasks | No | **Still Pass (no diff)**. |
| 3.1 LLM client + budget + fake provider | No to `llm/{client,budget,fake_provider}.py`; tests changed | **Pass**; L-1 boundary pin added and full `tests/llm` suite (87 passed + 1 skipped `real_provider`) green. |
| 3.2 shared schemas + `BodyView.victim_id` | No | **Still Pass (no diff)**. |
| 3.3 memory rendering | No to `agents/memory/`; tests changed | **Pass**; L-2 confirmed-dead suffix pin added. |
| 3.4–3.7 prompt templates | No to `.j2` files | **Still Pass (no diff)**; wrapped without modification by the new `agents/strategic/prompts/loader.py`. |
| 3.8 meeting state machine | No to `meetings/{manager,schemas}.py`; `meetings/transcript.py` extended for 3.11 | **Pass**; `MeetingManager._tally` semantics unchanged (Task 3.10 created a public `meetings/voting.py` module rather than refactoring the manager). |
| I-1 .. I-12 + multi-agent block | See §7 | **Static invariants Pass; multi-agent live-harness Partial — see §7.** |

## 5. Prior Audit Follow-Through

The two source audits both re-checked the post-3.8 baseline's findings. Where they agree, the adopted status is below; where they disagreed (R-9, C-5), the row is re-verified and decided.

| Prior finding | Status | Evidence |
|---|---|---|
| **L-1** Budget `_COST_USD_CAP_SLACK` size unpinned | **Closed** | [tests/llm/test_budget.py:270 TestSlackBoundary](tests/llm/test_budget.py#L270) — `cap=0.30, charge=0.30 + 1e-3` raises; `cap=0.30, charge=0.30 + 1e-9` does not raise. Constant remains `1e-6` at [llm/budget.py:42](llm/budget.py#L42); a constant-rename regression surfaces in the docstring assertion. |
| **L-2** `last_seen` suffix on confirmed-dead unpinned | **Closed** | [tests/agents/test_memory_rendering.py:706](tests/agents/test_memory_rendering.py#L706) records a `saw_player` + `saw_body` pair for the same player, renders, and asserts the `(last seen in MEDBAY at tick 10)` suffix appears on the dead player's belief line. |
| **C-1 (post-3.8)** R-10 leak-scanner reuse hedge | **Closed for the reasoner; not active for production meeting flow** | [agents/strategic/reasoner.py:224-228](agents/strategic/reasoner.py#L224) imports `_assert_no_recursive_hidden_fields` + `_assert_no_role_bearing_values` directly from `eval.leak_test`; the [TestR10LeakScannerAcceptanceGate](tests/agents/test_strategic_reasoner.py#L612) plants 7 leak vectors and asserts each trips. The function-local import keeps `import agents.strategic.reasoner` from transitively pulling engine code. **Caveat**: the production meeting flow does not route through `StrategicReasoner` — captured separately as **R-4**. The primary leak surface (observation packets) is still protected by `eval/leak_test.py` and the 100-game live scan returns zero violations. |
| **C-2 (post-3.8)** `render_for_prompt` overflow path | **Closed (documentation)** | [DESIGN.md §6.6 non-elastic carve-out](DESIGN.md) (the only DESIGN.md diff in the audit window) documents that role + tasks-completed + beliefs + contradictions are always retained; only observations are elastic. The reasoner docstring at [agents/strategic/reasoner.py:41-53](agents/strategic/reasoner.py#L41) restates the contract. |
| **C-4 (post-3.8)** No Python loader for the four `.j2` templates | **Closed** | [agents/strategic/prompts/loader.py:57](agents/strategic/prompts/loader.py#L57) constructs `jinja2.Environment(autoescape=False, undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)`. 24 per-template smoke tests pin StrictUndefined, environment settings, version-marker presence, missing-kwarg raise, and FakeProvider-response-parses-into-schema for each of the four templates. |
| **C-5 (post-3.8)** No `GameBudget` integration with `MeetingManager` | **Not closed — promoted to R-2** | The adapter exists and is tested at the unit level. No production code constructs a `BudgetedLLMClient`. See §10 R-2. |
| **R-9 (post-3.8 addendum)** `ReplayEntry` extension for meetings | **Closed (schema + CI test); blocked on public harness** | [orchestrator/replay.py:86 MeetingReplayEntry](orchestrator/replay.py#L86) carries transcript + ballots + contradictions + `tuple[LLMCallRecord, ...]` + `prompt_versions` + before/after state hashes; the long-horizon byte-identity gate at [tests/orchestrator/test_replay_meetings.py:389](tests/orchestrator/test_replay_meetings.py#L389) drives one 250-tick game with one full meeting cycle (16 LLM calls = 4 reports + 8 statements + 4 ballots) twice on seed 2026 and asserts byte-identical JSONL. **The schema and the determinism gate are both closed**; the gap is that the public harness never exercises the determinism gate because it doesn't dispatch through a runner — that gap is **R-1**, not an R-9 reopen. |

## 6. Task-by-Task DoD Audit

### 6.1 Task 3.9 — Strategic reasoner + sub-phase C integration substrate (PR #45, merged `d2e27c8`)

| DoD bullet | Verdict | Evidence |
|---|---|---|
| Strategic reasoner exposes the documented pipeline (`render_for_prompt → leak-scan → template → llm.complete → parse → identity-override`). | **Pass** | [agents/strategic/reasoner.py:279](agents/strategic/reasoner.py#L279); `produce_report` / `produce_statement` / `produce_vote` at lines 355 / 410 / 464. |
| C-4 — Jinja loader with StrictUndefined. | **Pass** | [agents/strategic/prompts/loader.py:57](agents/strategic/prompts/loader.py#L57). |
| C-4 — Per-template smoke tests with Pydantic round-trips. | **Pass** | [tests/agents/test_strategic_prompts.py](tests/agents/test_strategic_prompts.py) — 24 cases; each template has a non-empty + version-marker + missing-kwarg raise + `FakeProvider().complete(schema=…)` parse-into-schema gate. |
| C-5 — `BudgetedLLMClient` adapter. | **Pass at the adapter level** | [llm/budgeted_client.py:93](llm/budgeted_client.py#L93); preflight + reserve under `asyncio.Lock`, provider call runs outside the lock, charge-on-success / release-on-failure. |
| C-5 — Meeting-ceiling budget integration. | **Partial / Fail in production** | [tests/llm/test_budgeted_client.py:352](tests/llm/test_budgeted_client.py#L352) drives cumulative cost into a cap and asserts the `BudgetExceededError` propagates from preflight. **No orchestrator / meeting / strategic-reasoner production code constructs a `BudgetedLLMClient`** — see R-2. |
| C-2 — Reasoner respects DESIGN.md §6.6 non-elastic carve-out. | **Pass** | Reasoner docstring + DESIGN.md §6.6 reconciled. |
| L-1 + L-2 pins. | **Pass** | See §5. |
| R-10 acceptance gate for strategic prompt inputs. | **Pass for the reasoner** | [TestR10LeakScannerAcceptanceGate](tests/agents/test_strategic_reasoner.py#L612) — 7 planted leak vectors + 1 clean negative; matches the canonical scanner contract. The gate protects callers that route through the reasoner; the meeting flow does not (R-4). |
| Strategic calls only at meetings or specified triggers. | **Pass** | `_VALIDATE_TRIGGER_FOR_METHOD` allowlists at [agents/strategic/reasoner.py:135-141](agents/strategic/reasoner.py#L135); `_validate_trigger_for_method` fail-loud. |
| Tests use `llm.fake_provider` and make no network calls. | **Pass** | 53 `FakeProvider` hits in `tests/agents/test_strategic_reasoner.py`; no real-provider calls (`real_provider` test deliberately skipped). |
| No imports from `engine/` under `agents/`. | **Pass** | `lint-imports` KEPT; function-local import in `_scan_prompt_inputs` defers the engine-transitive pull. |
| No LLM calls in `agents/tactical/`. | **Pass** | `git grep` for `LLMClient` / `complete(` under `agents/tactical/` empty. |
| `mypy --strict` + `ruff` + `lint-imports` + `check.sh`. | **Pass** | §3. |

**Verdict:** Pass on every documented DoD bullet. The reasoner is a complete, well-tested pipeline. Two integration-level observations are captured as findings against the *next* task (R-2 / R-4 / R-5) rather than as Task-3.9 DoD failures, because Task 3.9's scope was the reasoner + adapter + loader, not their orchestrator wire-up.

### 6.2 Task 3.10 — Voting (PR #46, merged `d951caf`)

| DoD bullet | Verdict | Evidence |
|---|---|---|
| Voting tally + uncertainty-aware skip matches DESIGN.md §5.5. | **Pass** | [meetings/voting.py:120 tally_ballots](meetings/voting.py#L120); five resolution rules at lines 139-166. |
| `VoteBallot` structured output parsed and tallied. | **Pass** | [meetings/voting.py:83 normalize_ballot_target](meetings/voting.py#L83) defensively rewrites hallucinated targets to SKIP with the `INVALID_VOTE_TARGET_MARKER`. |
| Ballots publicly logged in `MeetingResult`. | **Pass** | `MeetingResult.ballots: tuple[VoteBallot, ...]` at [meetings/schemas.py:259](meetings/schemas.py#L259); persisted into [MeetingReplayEntry.ballots](orchestrator/replay.py#L176). |
| Relevant voting tests pass. | **Pass** | [tests/meetings/test_voting.py](tests/meetings/test_voting.py) — 30 cases covering empty / all-skip / strict plurality / skip-tied / two-way + three-way ties / below-threshold / max-confidence threshold / inclusive-at-cutoff / defensive normalisation / bad threshold rejection. |
| Static checks. | **Pass** | §3. |

**Verdict:** Pass. The module docstring at [meetings/voting.py:38-48](meetings/voting.py#L38) acknowledges deliberate duplication with `MeetingManager._tally` and frames consolidation as future work; both implementations agree byte-for-byte on every documented input.

### 6.3 Task 3.11 — Contradiction detection (PR #47, merged `918284b`)

| DoD bullet | Verdict | Evidence |
|---|---|---|
| Flags incompatible alibi and saw-player claims. | **Pass** | [meetings/transcript.py:97 detect_contradictions](meetings/transcript.py#L97); two detectors: `_detect_alibi_conflicts` (alibi-vs-alibi) at line 195; `_detect_alibi_vs_sightings` at line 220. |
| Flags are information, not verdicts. | **Pass** | Docstring at line 116-120; detector returns `tuple[ContradictionRef, ...]` and never mutates votes. |
| Detected contradictions are representable in shared schemas and surfaceable in rendered memory. | **Pass** | `ContradictionRef` at [meetings/schemas.py:190](meetings/schemas.py#L190) carries `contradiction_id`, `kind: Literal["alibi_conflict","alibi_vs_sighting"]`, `event_a_id`, `event_b_id`, `subjects`, `description`; the accusation-round and vote-ballot templates already iterate `contradictions` / `contradiction_flags`. |
| Relevant tests pass. | **Pass** | [tests/meetings/test_contradictions.py](tests/meetings/test_contradictions.py) — 21 cases including 9 false-negative coverage scenarios, 7 true-positive scenarios, 5 determinism cases (sort-by-id, idempotence, iteration-order independence). |
| Static checks. | **Pass** | §3. |

**Verdict:** Pass. The detector relies on the producer-guaranteed canonical order from Task 3.8 (does not re-sort by side effect) and the sort-by-`contradiction_id` finalizer is the determinism guarantee that lets the flags land in a replay-stable rendered memory view.

### 6.4 Task 3.12 — Meeting/orchestrator integration (PR #48, merged `639debc`)

| DoD bullet | Verdict | Evidence |
|---|---|---|
| Orchestrator applies `MeetingResult` ejection/skip to engine-owned world state. | **Pass** | [orchestrator/game.py:392 apply_meeting_result](orchestrator/game.py#L392); EJECTED clears `alive`, resets `last_action`, drops the ejected player's incomplete tasks (DESIGN.md §3.5 dead-crewmate-task rule), removes cooldown entry; SKIPPED no player mutation; win conditions re-evaluated; triggering body consumed from `state.bodies`. |
| Gameplay resumes after meetings with tick/cooldown behaviour matching DESIGN.md §3.1 and §5.1. | **Pass when runner configured; legacy MEETING_PHASE_REACHED preserved when no runner** | `apply_meeting_result` returns `(state, events)` with `phase="PLAY"`, `tick=tick+1`, rng advanced one step ([:513-520](orchestrator/game.py#L513)); cooldown / sabotage / emergency counters frozen during the meeting tick per DESIGN.md §5.1. The legacy no-runner branch is preserved as backward-compat at [orchestrator/game.py:645-651](orchestrator/game.py#L645) and explicitly pinned by [test_meeting_phase_reached_when_no_runner_configured](tests/orchestrator/test_meeting_integration.py#L425) — *this is the substrate that makes R-1 a live finding even though the DoD bullet passes.* |
| Replay records meeting transcripts, ballots, contradiction flags, prompt versions, and LLM cost metadata. | **Pass at the schema level; not exercised by the public harness** | [orchestrator/replay.py:150 record_meeting](orchestrator/replay.py#L150) builds `MeetingReplayEntry` from runner-returned `MeetingArtifacts`; all five categories are on the entry. Fresh 100-game tournament reconstruction at HEAD walks 100 replay files and finds **zero** `MeetingReplayEntry` records — see R-1. |
| Engine remains pure; `MeetingManager` does not mutate engine state directly. | **Pass** | `MeetingManager.run` returns a `MeetingResult` DTO; engine-state application happens in `apply_meeting_result` called by the orchestrator. The `MeetingRunner` Protocol docstring forbids mutation ([orchestrator/game.py:124-176](orchestrator/game.py#L124)); pinned by [TestMeetingFirewallContract](tests/orchestrator/test_meeting_integration.py#L1212). |
| **R-9 long-horizon byte-identity gate.** | **Pass** | [tests/orchestrator/test_replay_meetings.py:389](tests/orchestrator/test_replay_meetings.py#L389) drives a 250-tick game with one full meeting cycle (16 LLM calls = 4 reports + 8 statements + 4 ballots) twice on seed 2026 and asserts byte-identical JSONL. Re-ran during reconciliation: `1 passed in 0.50s`. The short-horizon Phase 2 byte-identity is preserved at `:490`. |
| Relevant integration tests pass with fake LLM outputs. | **Pass** | `tests/orchestrator` = 58 passed in 1.29s; meeting-integration and replay-meetings suites both green. **Coverage gap**: the canonical `llm.fake_provider.FakeProvider` is not exercised through `HeadlessGame + DefaultMeetingRunner + MeetingManager`; the inline stubs `_ScriptedLLMClient` and `_DeterministicLLMClient` cover the protocol. Captured as R-5. |
| `mypy --strict engine observation agents meetings orchestrator llm` + `ruff`. | **Pass** | §3. |

**Verdict:** **Pass on every documented DoD bullet, with two architectural observations.** Task 3.12's *Files in scope* explicitly lists `orchestrator/game.py`, `orchestrator/replay.py`, and the two test files; `scripts/run_*.py` and `eval/balance_eval.py` are **not** in scope. The DoD bullets are evaluated against the runner-configured path and they all pass. R-1 is therefore not a Task-3.12 DoD violation; it is a Phase-3 *merge-criteria* gap (the criterion *“50-game eval: full-LLM games complete end-to-end using fake-provider tests in CI”* at [tasks/phase-3.md:956](tasks/phase-3.md#L956) cannot be exercised from any public entry-point today, even though the runner-configured CI test exists).

## 7. Architectural Invariant Audit

| Invariant | Verdict | Evidence |
|---|---|---|
| I-1 / I-2 `advance_tick` pure + deterministic | **Pass** | No `engine/tick.py` diff in window; 500-tick byte-identity at HEAD. |
| I-3 replay determinism | **Pass for runner-configured path; not exercised on the public harness path (R-1)** | Tick-replay byte-identity passes at HEAD; meeting-replay determinism passes [test_replay_meetings.py:389](tests/orchestrator/test_replay_meetings.py#L389). Public harness emits no meetings, so its determinism is engine-only. |
| I-4 engine state remains engine-owned | **Pass** | `apply_meeting_result` lives in `orchestrator/`, not `engine/`; `MeetingManager` does not import `engine/`. |
| I-5 `agents/` does not import `engine/` | **Pass** | `lint-imports` KEPT; direct grep empty; function-local import in `_scan_prompt_inputs` defers the transitive chain. |
| I-6 agents receive only packet + public map | **Pass** | No diff to the agent-call path; orchestrator unchanged outside the meeting boundary. |
| I-7 agents emit only `ActionIntent` | **Pass** | No diff to action-emission paths. |
| I-8 observation firewall strips hidden info | **Pass** | 100-log / 3,275-packet leak scan returns zero violations; `_BODY_ID_VICTIM_PATTERN` grep empty under `agents/`. |
| I-9 invalid inputs raise | **Pass** | Strategic reasoner trigger-validation + constructor validators; voting threshold range check; `BudgetedLLMClient` negative-rate rejection; orchestrator `_validate_runner_result` rejects trigger-field drift; `apply_meeting_result` rejects non-MEETING phase / unknown player / already-dead / SKIPPED-with-ejected. |
| I-10 Pydantic v2 boundary | **Pass** | `LLMCallRecord`, `MeetingReplayEntry`, `ReplayEntry`, meeting DTOs all `frozen=True, extra="forbid"`. |
| I-11 engine state immutability | **Pass** | No engine diff. |
| I-12 orchestrator duplicate-actor rejection | **Pass** | No orchestrator boundary diff outside the meeting interpose; `_build_participants` adds duplicate-id guard via `state.players`. |
| Firewall `llm/` → no `agents`/`meetings` | **Pass** | `grep` empty. |
| Firewall `meetings/` → no `agents`/`engine`/`orchestrator` | **Pass** | `grep` empty. |
| Multi-agent live harness | **Partial — see R-1** | Six-seed sweep + 100-game tournament reproduce post-3.8 byte-identical numbers. The "live harness" exercises only the no-runner branch in production; the runner-configured branch lives only in CI integration tests. |
| Cross-provider portability outside `llm/` | **Pass** | `anthropic|cache_control|extended_thinking` grep empty under `agents/`, `meetings/`, `orchestrator/`. `BudgetedLLMClient` public surface uses USD-per-token rates, not provider-named tiers. |

## 8. Specific Questions for the Phase 4 Layer

1. **Is the replay format ready for the eval harness?** **Schema yes; coverage from the public harness no.** `MeetingReplayEntry` at [orchestrator/replay.py:86](orchestrator/replay.py#L86) carries everything a spectator UI or eval-metric reducer needs: transcript (reports + statements in canonical order), ballots, contradictions, per-call `LLMCallRecord` telemetry, `prompt_versions` (entry-level mapping — see R-3), and `state_hash_before` / `state_hash_after`. Per-game cost is reconstructable as `sum(call.cost_usd for entry in read_meeting_entries(path) for call in entry.llm_calls)`. **Coverage limitation**: replays written by `scripts/run_game.py` or `scripts/run_tournament.py` contain **zero** `MeetingReplayEntry` records today; the eval harness cannot drive 50 fake-provider games to completion through the public CLI without first wiring a default runner (R-1).

2. **Does the meeting interpose point allow Phase 4's WebSocket broadcasts?** **Yes, with the same shape both auditors identified.** `MeetingRunner.run_meeting()` is one opaque async block returning `MeetingArtifacts` after the meeting resolves; intermediate states (report submitted, round started, vote cast) are not directly observable from the orchestrator's loop. The natural Phase 4.2 integration is a `_BroadcastingMeetingRunner` decorator analogous to `DefaultMeetingRunner`'s `_RecordingLLMClient` wrapper — the substrate supports this without a Phase 3 refactor.

3. **Anthropic-specific assumptions in `reasoner.py` or `manager.py`?** **None.** `grep -nE "anthropic\|cache_control\|extended_thinking" agents/ meetings/ orchestrator/ llm/budgeted_client.py` empty. `BudgetedLLMClient` uses USD-per-token rates (defaults `6e-6` input / `30e-6` output at [llm/budgeted_client.py:69-70](llm/budgeted_client.py#L69)).

4. **Does the cost-tracking machinery support the ≤ $0.30 / game merge criterion?** **Extraction yes; enforcement no.** Per-call cost is on `LLMCallRecord.cost_usd`; per-meeting cost is `sum(...)`; per-game cost is `sum(...)` over all meeting entries. *Missing*: (a) no production code constructs a `BudgetedLLMClient` so there is no preflight cap enforcement during the run (R-2); (b) no helper aggregates per-game cost from a replay file (R-6). The merge-criterion check is achievable post-hoc only on replays that contain meeting entries — which today excludes every public-CLI run.

5. **Did Phase 3 introduce new Phase 2 risks?** **No.** 100-game tournament byte-identical to post-3.8 (58 / 35 / 0 / 7); 500-tick seed-0 byte-identity PASS; leak scanner walks 100 audit logs with zero violations. The orchestrator diff preserves the `meeting_runner=None` path verbatim — that preservation is the seed of R-1 but is not a Phase 2 regression.

6. **New Critical / High findings introduced by this audit window?** **Two High (R-1 + R-2).** No Critical. R-1 is the public-harness wire-up gap; R-2 is the budget adapter wire-up gap.

7. **Is the substrate ready for Phase 4 dispatch after the gaps close?** **Yes.** Phase 4.1 (FastAPI scaffolding) builds on the existing orchestrator + replay surface; Phase 4.2 (WebSocket game broadcast) builds on a `MeetingRunner` wrapper as in Q2; Phase 4.3+ (React frontend) consumes WebSocket events. None of the three depend on R-1 or R-2 being closed first — they only depend on the *capability* (`MeetingRunner` Protocol + `MeetingReplayEntry` schema), which is already present.

## 9. Test Quality and Coverage Gaps

Union of both audits' lists, deduplicated and re-verified.

- **The strategic-reasoner test suite is genuine, not a false-positive surface.** 35 cases organised by behavioural axis (construction validation, three `produce_*` pipelines, suspicion-graph forwarding, determinism, R-10 leak scanner, budget propagation, trigger validation, forwarded inputs). The R-10 acceptance gate plants 7 different leak vectors and asserts each trips; a regression that silently suppresses the scanner would fail every one.
- **The four prompt-loader templates have schema-round-trip coverage via `FakeProvider`.** Each template has a `test_fake_provider_response_parses_into_schema` case that renders the prompt, feeds the result through `FakeProvider().complete(schema=…)`, and asserts the response parses into the corresponding Pydantic schema. StrictUndefined / `autoescape=False` / `trim_blocks=True` / `lstrip_blocks=True` are pinned by direct attribute reads on the loader's environment.
- **Voting tests are exhaustive on the documented branches.** 30 cases over the 5 resolution rules × multiple input shapes each, plus the defensive normaliser surface. The "inclusive at cutoff" semantics at [meetings/voting.py:202](meetings/voting.py#L202) is the off-by-epsilon trap that's pinned explicitly.
- **Contradiction tests pin both true positives and false negatives.** 21 cases including 9 false-negative coverage scenarios, 7 true-positive scenarios, and 5 determinism scenarios. The boundary-overlap case (alibis covering ticks 10-15 and 15-20) is the off-by-one trap that's pinned explicitly.
- **The R-9 long-horizon byte-identity test is the strongest gate added in this window.** [tests/orchestrator/test_replay_meetings.py:389](tests/orchestrator/test_replay_meetings.py#L389) drives a 250-tick game with one full meeting cycle, runs it twice, asserts byte-identical JSONL. This exercises the engine tick loop, meeting dispatch, LLM-call recording, meeting-replay serialization, post-meeting state application, and rng-advance in one gate.
- **Coverage gap: no end-to-end test routes through `llm.fake_provider.FakeProvider`** (R-5). Orchestrator integration tests use `_ScriptedLLMClient` and `_DeterministicLLMClient` — both conform to the protocol, but a regression in `FakeProvider` that breaks its production-shape responses would not be caught by any end-to-end test. The risk is bounded because `FakeProvider`'s response builder is deterministic by construction.
- **Coverage gap: no end-to-end test routes through `BudgetedLLMClient`** (subsumed by R-2). The adapter is well-tested in isolation; there is no test that constructs a `DefaultMeetingRunner` with a budgeted client and asserts the cap is enforced through the meeting flow.
- **Coverage gap: no integration test pins that the public CLI / tournament harness drives at least one meeting end-to-end** (subsumed by R-1). Two existing tests *preserve* the legacy MEETING_PHASE_REACHED outcome ([tests/orchestrator/test_game.py:220-230](tests/orchestrator/test_game.py#L220); [tests/orchestrator/test_meeting_integration.py:424-444](tests/orchestrator/test_meeting_integration.py#L424)), which lets `pytest` and `check.sh` go green while the public harness can't reach a meeting.

## 10. Defects and Risks

### R-1 [High] Public CLI / tournament harness still pauses at `MEETING_PHASE_REACHED`

- **Status:** Open. **Demoted from Codex Critical; promoted from Claude Medium M-1.** Both source audits cited the same evidence; severity reconciled in §13.2.
- **Evidence:** `HeadlessGame.run` returns `MEETING_PHASE_REACHED` when `state.phase == "MEETING"` and `_meeting_runner is None` at [orchestrator/game.py:645-651](orchestrator/game.py#L645). [scripts/run_game.py:71-80](scripts/run_game.py#L71), [scripts/run_tournament.py](scripts/run_tournament.py), and [eval/balance_eval.py:112-120](eval/balance_eval.py#L112) all construct `HeadlessGame` without a `meeting_runner=` kwarg. A fresh 100-game tournament reconstruction at `HEAD` (`/tmp/recon-tournament/`) walks all 100 replay files and finds `tick_entries=964 meeting_entries=0`; the harness reports `meeting_phase_reached:7` of 100, identical to post-3.8.
- **Why it matters:** The Phase 3 merge criterion *“50-game eval: full-LLM games complete end-to-end using fake-provider tests in CI”* at [tasks/phase-3.md:956](tasks/phase-3.md#L956) cannot be exercised from any public entry-point today. The merge criteria *“Impostor win rate in [25%, 65%] band”* and *“Cost per game ≤ $0.30”* are unmeasurable from a public CLI run because the harness never gets past `MEETING_PHASE_REACHED`. The only CI evidence that the full meeting pipeline works end-to-end is the single-game runner-configured test at [tests/orchestrator/test_replay_meetings.py:389](tests/orchestrator/test_replay_meetings.py#L389), which is sufficient to prove the *capability* but not the *merge-criteria gate*.
- **Why this is High and not Critical:** Phase 4 dispatch (FastAPI 4.1, WebSocket 4.2, React 4.3+) consumes the orchestrator's `MeetingRunner` Protocol and the `MeetingReplayEntry` schema — both correct on `HEAD`. None of Phase 4's first three tasks need a 50-game tournament to be runnable from the public CLI before they can start. Phase 3 *closure* and the real-provider eval both block on this; Phase 4 *dispatch* does not. Task 3.12's "Files in scope" explicitly excludes `scripts/` and `eval/balance_eval.py`, so this is not a Task-3.12 DoD violation — it is a Phase-3-merge-criteria gap that should be closed alongside the budget wiring (R-2).
- **Recommended action:** Wire a default fake-provider `DefaultMeetingRunner` through the public path. Two natural shapes: (a) a `--enable-meetings` CLI flag on `scripts/run_game.py` and `scripts/run_tournament.py` that constructs a `FakeProvider`-backed `DefaultMeetingRunner` + `GameBudget` + `BudgetedLLMClient` (this folds R-1 + R-2 + R-5 into one fix), or (b) make the runner the default and quarantine `MEETING_PHASE_REACHED` behind an opt-out for the Phase 2 byte-identity tests. Add at least one CI test that runs the public harness end-to-end through one meeting and asserts no `MEETING_PHASE_REACHED` outcome.

### R-2 [High] `BudgetedLLMClient` + `GameBudget` not wired into orchestrator / meeting / strategic-reasoner production paths

- **Status:** Open. **Both source audits cited as High** — Claude H-1, Codex H-1. Confirmed.
- **Evidence:** `grep -rn "BudgetedLLMClient\|GameBudget" orchestrator/ meetings/ agents/strategic/ scripts/ eval/balance_eval.py` (excluding tests) returns only two docstring references in `agents/strategic/reasoner.py`. The adapter exists at [llm/budgeted_client.py:93](llm/budgeted_client.py#L93) with 20 unit tests including the meeting-ceiling preflight + concurrent-preflight pins. `DefaultMeetingRunner.__init__` at [orchestrator/game.py:240](orchestrator/game.py#L240) accepts `llm_client: LLMClient`, wraps it in `_RecordingLLMClient` for replay capture, and passes that into `MeetingManager(llm_client=…)` — no `GameBudget`, no preflight enforcement.
- **Why it matters:** The Phase 3 merge criterion *“Cost per game ≤ $0.30 or provider equivalent”* at [tasks/phase-3.md:958](tasks/phase-3.md#L958) is unenforceable at call time. A runaway meeting that issues a long prompt could blow the cap and be detected only after-the-fact in replay cost analysis. The C-5 task-bullet contract from Task 3.9 was that consumers — explicitly including `MeetingManager` — accept the adapter; the adapter conforms transparently, but production wiring never happened.
- **Recommended action:** Add an optional `budget: GameBudget | None = None` kwarg to `DefaultMeetingRunner.__init__`; when present, wrap `llm_client` in `BudgetedLLMClient(inner=llm_client, budget=budget)` before passing it through `_RecordingLLMClient`. Construct one `GameBudget` per game at the orchestrator entry-point (the natural call site is `HeadlessGame.run`). Add one regression test that drives a meeting with a tight-cap budget and asserts `BudgetExceededError` propagates from `run_meeting()`. ~30 LOC + 1 test. The fix should land **before** the real-provider eval runs. Folding R-1 + R-2 into one PR is natural — the runner-injection and the budget-wiring are sibling wires.

### R-3 [Concern] `LLMCallRecord` lacks per-call `prompt_version` / parsed-output fields

- **Status:** Open. **Unique-but-verified from Codex.** Claude did not flag this; the evidence reproduces.
- **Evidence:** `LLMCallRecord` fields at [orchestrator/replay.py:51-72](orchestrator/replay.py#L51) are `call_kind`, `model`, `prompt`, `response_text`, `input_tokens`, `output_tokens`, `cost_usd`. `prompt_versions` is a meeting-level mapping on the parent `MeetingReplayEntry` at [orchestrator/replay.py:113-114](orchestrator/replay.py#L113); parsed outputs live in `transcript.reports`, `transcript.statements`, `ballots`, and `outcome` on the meeting entry.
- **Why it matters:** Correlating a particular raw LLM response to a prompt template version requires inferring from prompt text or call order rather than reading a field. For a five-meeting game with four template versions, the meeting-level mapping is functionally sufficient and is the more compact shape; for a multi-version A/B replay corpus that asks "which calls used vote_ballot.j2 v1 vs v2?" the per-call shape would be cleaner.
- **Recommended action:** Either add per-call `prompt_id` + `prompt_version` (~6 LOC + a serializer pin) when R-1/R-2 are fixed, or explicitly document the meeting-level mapping as the supported replay contract in DESIGN.md §11.4. Defer until the real-provider eval owner has a concrete need.

### R-4 [Concern] `StrategicReasoner` is defined but unused in production meeting flow (R-10 scanner gate not active in production)

- **Status:** Open. **Both source audits flagged this**; Codex bundled it into H-1, Claude isolated it as C-2 Concern. Reconciled as Concern — see §13.2.
- **Evidence:** `grep -rn "StrategicReasoner" orchestrator/ meetings/ scripts/ eval/balance_eval.py` (excluding tests / docs) returns empty. `DefaultMeetingRunner` constructs `MeetingManager` directly with the four prompt callables from `agents/strategic/prompts/`, bypassing the reasoner. `MeetingManager._collect_report` / `_collect_statement` / `_collect_vote` call `self._llm_client.complete(...)` directly at [meetings/manager.py:512-528](meetings/manager.py#L512), `:560-579`, `:644-662`. The reasoner's `_scan_prompt_inputs` defense-in-depth scanner at [agents/strategic/reasoner.py:172-258](agents/strategic/reasoner.py#L172) does not run in the production meeting flow.
- **Why it matters:** The reasoner's R-10 leak scanner protects prompt-time inputs (rendered memory + auxiliary text like `meeting_trigger`) against role-bearing strings and recursive hidden fields. The production meeting flow consumes the same rendered memory through the same templates, so a leak in rendered memory would still be caught by `eval/leak_test.py` packet scanning (100-log / 3,275-packet live tournament scan returns zero violations). The bypass is a defense-in-depth gap, not a primary leak risk. `MeetingManager` already has identity-override logic on the parsed-result side ([meetings/manager.py:594-601](meetings/manager.py#L594)), so the parallel-implementations risk is bounded.
- **Recommended action:** Either consolidate the meeting flow through `StrategicReasoner` (the cleaner architecture), or lift `_scan_prompt_inputs` into a shared helper that `MeetingManager` also calls (the cheaper hygiene fix). Neither is a Phase 4 blocker. Consider as part of the R-1 / R-2 wire-up PR.

### R-5 [Concern] No end-to-end test routes through `llm.fake_provider.FakeProvider`

- **Status:** Open. **Unique-but-verified from Claude (C-1).** Codex noted the gap in §9 but did not list as a defect.
- **Evidence:** Orchestrator integration tests use `_ScriptedLLMClient` and `_DeterministicLLMClient` (both conform to the `LLMClient` Protocol but are inline stubs); the canonical `FakeProvider` is exercised at three levels (meeting-manager unit, reasoner unit, per-template smoke) but never through the full `HeadlessGame` + `DefaultMeetingRunner` + `MeetingManager` path.
- **Why it matters:** A regression in `FakeProvider` that breaks its production-shape responses (e.g. introduces a non-deterministic field) would not be caught by any end-to-end test. The risk is bounded — `FakeProvider`'s response builder is deterministic by construction — but the coverage gap exists.
- **Recommended action:** Fold into the R-1 fix: when wiring a default fake-provider runner into `scripts/run_game.py`, use the canonical `FakeProvider` rather than an inline stub. The end-to-end coverage falls out of the wire-up.

### R-6 [Concern] No helper for per-game cost aggregation from a replay log

- **Status:** Open. **Unique-but-verified from Claude (C-4).**
- **Evidence:** `orchestrator/replay.py` exposes `read_all_entries`, `read_meeting_entries`, `read_replay_entries`. Per-game cost is `sum(call.cost_usd for entry in read_meeting_entries(path) for call in entry.llm_calls)` — three lines, but no helper packages it.
- **Why it matters:** The real-provider 50-game eval will compute per-game cost across 50 replays and check the `≤ $0.30` band. Inline reductions risk drift (e.g. someone forgets that `read_meeting_entries` returns only meetings).
- **Recommended action:** Defer to the real-provider eval owner. Add `compute_cost_usd(path)` (~5 LOC) to `eval/` or `orchestrator/replay.py` as part of the eval scaffolding.

## 11. Document Conflicts

- **Task 3.12 DoD vs `HeadlessGame` no-runner path.** `tasks/phase-3.md:932` says "Gameplay resumes after meetings with tick/cooldown behavior matching DESIGN.md §3.1 and §5.1." On the runner-configured path this is true ([orchestrator/game.py:513-520](orchestrator/game.py#L513)). On the no-runner path the loop returns `MEETING_PHASE_REACHED` and does not "resume gameplay." The Task 3.12 "Files in scope" excludes `scripts/` and `eval/balance_eval.py`, so the DoD bullet is technically satisfied for the in-scope surface; the broader merge-criteria gap is R-1.
- **Phase 3 Merge Criteria vs tournament harness.** `tasks/phase-3.md:956` requires fake-provider full-LLM games to complete end-to-end in CI. `eval/balance_eval.py:9-15` still treats `MEETING_PHASE_REACHED` as a normal non-decisive bucket and `:112-120` does not pass a meeting runner; reconstruction at HEAD produces `meeting_phase_reached:7` / `meeting_entries:0`. Conflict captured by R-1.
- **Task 3.9 C-5 wording vs production wiring.** `tasks/phase-3.md` line range 686-687 states that `BudgetedLLMClient` should wrap calls and consumers including `MeetingManager` accept it; production `MeetingManager` construction in `DefaultMeetingRunner` receives raw `LLMClient`. Conflict captured by R-2.
- **DESIGN.md §6.6 non-elastic carve-out vs renderer behaviour.** Added in `b7cd6fd` ahead of Task 3.9 dispatch; reasoner docstring at [agents/strategic/reasoner.py:41-53](agents/strategic/reasoner.py#L41) restates the contract. No source change to `agents/memory/store.py` was needed because the renderer's existing elasticity policy already preserved the non-elastic block. **No conflict on current `HEAD`.**

## 12. Readiness for Phase 4

**Ready for Phase 4 dispatch in parallel with closing R-1 + R-2.** The substrate Phase 4 needs is correct on `HEAD`:

- The orchestrator dispatches through a `MeetingRunner` Protocol when one is configured ([orchestrator/game.py:645-669](orchestrator/game.py#L645)); the protocol is documented and the firewall (`MeetingManager` doesn't mutate engine state; the orchestrator does via `apply_meeting_result`) is pinned by `TestMeetingFirewallContract`.
- The replay format carries everything a spectator UI or eval reducer needs: transcript, ballots, contradictions, per-call LLM telemetry, prompt-version mapping, state hashes ([orchestrator/replay.py:86-116](orchestrator/replay.py#L86)).
- The four `.j2` templates have a `StrictUndefined` Jinja loader plus per-template schema-round-trip smoke tests; a template typo or schema-template drift fails CI rather than the first live-provider call.
- `MeetingManager` is unchanged; voting and contradiction detection are public modules with 30 + 21 cases respectively.
- The strategic reasoner exists as a complete pipeline with 35 cases; not yet integrated into production (R-4) but the contract is stable.
- The `BudgetedLLMClient` adapter exists with 20 unit tests; not yet wired into production (R-2) but the adapter conforms transparently.
- Phase 2 substrate is byte-identical to post-3.8: 100-game tournament `58/35/0/7`, six-seed sweep `11/9/7/7/8/10`, 500-tick byte-identity PASS, leak scan 100 logs / 3,275 packets / zero violations.

**The most important thing to fix before Phase 3 closes and the real-provider eval runs:** **R-1 and R-2 together.** Wire `DefaultMeetingRunner` + `GameBudget` + `BudgetedLLMClient` into `scripts/run_game.py` and `eval/balance_eval.py` so the public CLI exercises the full meeting flow end-to-end with cap enforcement. This closes both High findings, satisfies the *“50-game eval: full-LLM games complete end-to-end using fake-provider tests in CI”* and *“Cost per game ≤ $0.30”* merge criteria in one PR, and incidentally folds in R-5 (canonical FakeProvider through the orchestrator) by virtue of using `FakeProvider` as the default provider. Estimated ~80-120 LOC + 2-3 regression tests.

## 13. Reconciliation

### 13.1 Comparison table

Disposition column abbreviations: **C** = Confirmed (both audits cited it, evidence reproduces); **U** = Unique-but-verified (one audit cited it, evidence reproduces); **P** = Promoted (severity raised); **D** = Demoted (severity lowered); **X** = Dropped (subsumed / non-reproducing); **N** = New (surfaced during reconciliation).

| ID | Title | Claude says | Codex says | Verified | Final severity | Disposition |
|---|---|---|---|---|---|---|
| R-1 | Public CLI / tournament harness pauses at `MEETING_PHASE_REACHED`; zero meeting replay entries | Medium (M-1) | **Critical (C-1)** — *blocks real-provider eval and Phase 4* | yes (reconstructed 100-game tournament → `meeting_entries=0`) | **High** | D (Codex Critical → High; also note Claude Medium → High) |
| R-2 | `BudgetedLLMClient` + `GameBudget` not wired into orchestrator / meeting / strategic-reasoner production paths | **High (H-1)** | **High (H-1)** *(bundled with reasoner bypass)* | yes (grep returns 2 docstring refs only) | **High** | C |
| R-3 | `LLMCallRecord` lacks per-call `prompt_version` / parsed-output fields | — | Concern (R-1) | yes | Concern | U |
| R-4 | `StrategicReasoner` defined but unused in production; R-10 scanner bypass on meeting flow | Concern (C-2) | High *(bundled into H-1)* | yes | **Concern** | D (Codex implicit High → Concern; Claude Concern Confirmed) |
| R-5 | No end-to-end test routes through canonical `llm.fake_provider.FakeProvider` | Concern (C-1) | (noted in §9, not a defect) | yes | Concern | U |
| R-6 | No helper for per-game cost aggregation from a replay log | Concern (C-4) | — | yes | Concern | U |
| (R-7) | `MEETING_PHASE_REACHED` literal preserved as backward-compat outcome | Concern (C-3) | (subsumed in Critical C-1) | yes | — | X (subsumed by R-1) |
| L-1 | Budget `_COST_USD_CAP_SLACK` boundary unpinned | Closed | Closed | yes | n/a | C (closed, no row in §10) |
| L-2 | `last_seen` confirmed-dead suffix unpinned | Closed | Closed | yes | n/a | C (closed, no row in §10) |

### 13.2 Disagreements and resolutions

**R-1 — severity (Codex Critical → reconciler High; Claude Medium → reconciler High).** Both audits cite the same evidence — three public entry-points (`scripts/run_game.py`, `scripts/run_tournament.py`, `eval/balance_eval.py`) construct `HeadlessGame` without a `meeting_runner=` kwarg, and a 100-game tournament reconstruction confirms zero `MeetingReplayEntry` records. The disagreement is severity interpretation, not evidence. Codex grades Critical on the reading that the Phase 3 merge criterion *“50-game eval: full-LLM games complete end-to-end using fake-provider tests in CI”* is a strict gate for Phase 4 entry. Claude grades Medium on the reading that Task 3.12 DoD does not name `scripts/` or `eval/balance_eval.py` in "Files in scope" and the substrate (runner Protocol + replay schema) is correct, so this is a wire-up discipline issue. Re-verified the Task 3.12 DoD at [tasks/phase-3.md:916-928](tasks/phase-3.md#L916) — `scripts/` and `eval/balance_eval.py` are explicitly excluded from "Files in scope" and the merge criteria at [tasks/phase-3.md:955-960](tasks/phase-3.md#L955) live at the *Phase 3* level, not at any individual task. Codex's Critical depends on the interpretation that "Phase 4 cannot begin until Phase 3 merge criteria can be evaluated"; that interpretation is plausible but the rubric does not actually require it (per tie-breaker rule 2(b)). Conversely, Claude's Medium under-weighs that the merge criteria *cannot even be measured* from the public CLI today — that is structurally more than a discipline issue. Resolved at **High** as the severity that matches both the unmeasurable-merge-criteria evidence (against Claude's Medium) and the non-blocking-of-Phase-4-dispatch reality (against Codex's Critical).

**R-4 — severity (Codex implicit High bundle → reconciler Concern; Claude Concern Confirmed).** Codex bundles the reasoner bypass into H-1 ("budgeted client *and reasoner checks* are bypassed by the actual meeting flow"). Claude isolates it as C-2 Concern. Re-verified: the reasoner's `_scan_prompt_inputs` is defense-in-depth at prompt-input time; the primary leak surface is observation packets, and the 100-game live leak scan returns `audit_logs=100 packets=3275 victim_id_seen=True violations=0`. The bypass is a hygiene gap, not a leak risk. Codex's High framing on this specific axis depends on treating defense-in-depth equivalently to primary leak protection; that conflates two distinct surfaces. Resolved at Concern with Claude's grading. The budget-wiring half of Codex's H-1 stands separately as R-2 High.

**R-3 — presence (Codex unique).** Claude marked R-9 closed; Codex flagged a Concern that `LLMCallRecord` lacks per-call `prompt_version` / parsed-output fields, with the prompt-version mapping living on the parent `MeetingReplayEntry`. Re-verified: the meeting-level mapping is the actual shape; the four template versions don't vary across calls within a meeting, so the per-call duplication would be redundant data. For Phase 5 A/B replay analysis it would be cleaner per-call, but for the current `≤ $0.30 / game` and transcript-readability reductions the meeting-level mapping is functionally sufficient. Concern is the right grading; carried forward as a small documentation-or-schema decision for the real-provider eval owner.

**R-5 — presence (Claude unique).** Codex noted the gap in §9 but did not list it as a defect. Re-verified: orchestrator integration tests use `_ScriptedLLMClient` and `_DeterministicLLMClient` — both conform to the `LLMClient` Protocol but are inline stubs. Concern is the right grading; folds naturally into the R-1 fix.

**R-6 — presence (Claude unique).** Codex did not flag this; Claude's C-4 is a small forward-looking helper request. Re-verified: no `compute_cost_usd(path)` helper exists; the inline three-line reduction is trivial. Concern.

**R-7 dropped — subsumed by R-1.** Claude listed `MEETING_PHASE_REACHED` as a Concern about backward-compat literal preservation. Codex bundled it into Critical C-1. Both readings are about the same underlying surface; the wire-up that closes R-1 either deletes the literal or makes the no-runner path an opt-out for the Phase 2 byte-identity tests. Carrying it as a separate Concern would be double-counting.

### 13.3 Verdict reconciliation

The two source audits' verdicts diverged: Claude wrote *“Ready for Phase 4 (pending real-provider eval), with one High finding”* and Codex wrote *“Not ready.”* Per the prompt's discipline (do not soften the verdict to split the difference, and choose the more conservative reading when the two diverge): the conservative reading is **“Ready with fixes.”** Claude's verdict effectively communicates "Ready with fixes" with a different framing (the parenthetical "pending real-provider eval" *is* a fix). Codex's "Not ready" is too strong because Phase 4 dispatch (FastAPI scaffolding, WebSocket broadcast, React frontend) genuinely does not depend on R-1 or R-2 being closed first — the substrate they consume (runner Protocol + replay schema + engine-state firewall) is correct on `HEAD`. The reconciled verdict captures both realities: Phase 4 work can begin, and the two High findings must close before Phase 3 closes and the real-provider eval runs. The "Ready" half answers Phase 4 dispatch; the "with fixes" half answers Phase 3 closure and the eval pipeline.

---

**Counts:** 0 Critical, 2 High, 0 Medium, 0 Low, 4 Concern.
**Verdict:** Ready with fixes.
