# AiLibi Pre-Phase-4 Verification Audit

- **HEAD:** 639debc (main)
- **Date:** 2026-05-25
- **Scope:** verify post-3.8 audit findings L-1, L-2, C-1, C-2, C-4,
  C-5 and the May-15 reconciled audit's Phase-3 acceptance gates R-9
  and R-10/strategic are actually closed at `HEAD`. Read-only;
  fake-provider only.

## 1. Verdict

**Verification passed — Pre-Phase-4 audit may proceed.** Every listed
finding is `Closed`. No blockers.

## 2. Commands run

| Command | Exit | Last line |
| --- | --- | --- |
| `bash scripts/check.sh` | 0 | `663 passed, 1 skipped in 4.35s` |
| `uv run lint-imports` | 0 | `Contracts: 1 kept, 0 broken.` |
| `uv run pytest` | 0 | `663 passed, 1 skipped in 4.39s` |
| `uv run pytest tests/llm -v` | 0 | `87 passed, 1 skipped in 0.15s` |
| `uv run pytest tests/agents -v` | 0 | `238 passed in 0.26s` |
| `uv run pytest tests/meetings -v` | 0 | `141 passed in 0.24s` |
| `uv run pytest tests/orchestrator -v` | 0 | `58 passed in 1.18s` |
| `uv run pytest eval/leak_test.py eval/determinism_test.py -v` | 0 | `11 passed in 0.36s` |
| `git grep -nE "_assert_no_recursive_hidden_fields\|_assert_no_role_bearing_values" tests/agents/test_strategic_reasoner.py tests/agents/test_strategic_prompts.py` | 0 | docstring at test_strategic_reasoner.py:707 (closure source is the production-code direct import, see §3 / §4) |
| `git grep -nE "from eval\.leak_test import" tests/agents/` | 0 | `tests/agents/test_memory_rendering.py:26: from eval.leak_test import (` |
| `git grep -nE "_COST_USD_CAP_SLACK\|cap.*0\.30.*1e-3\|cap.*0\.30.*1e-9" tests/llm/test_budget.py` | 0 | `tests/llm/test_budget.py:273: ``llm.budget._COST_USD_CAP_SLACK`` is currently ``1e-6``.` (`TestSlackBoundary` class at line 270 with two boundary tests) |
| `git grep -nE "last_seen.*confirmed.dead\|saw_body.*last_seen\|confirmed.dead.*last_seen" tests/agents/test_memory_rendering.py` | 0 | `tests/agents/test_memory_rendering.py:706: def test_last_seen_suffix_renders_for_confirmed_dead_player` |
| `ls agents/strategic/prompts/` | 0 | `__init__.py accusation_round.j2 crewmate_report.j2 impostor_report.j2 loader.py vote_ballot.j2` |
| `git grep -nE "StrictUndefined\|jinja2.Environment" agents/strategic/prompts/` | 0 | `loader.py:46: from jinja2 import Environment, FileSystemLoader, StrictUndefined` and `loader.py:60: undefined=StrictUndefined,` |
| `ls llm/budgeted_client.py` | 0 | `llm/budgeted_client.py` |
| `git grep -nE "preflight\|charge_response" llm/budgeted_client.py meetings/manager.py agents/strategic/reasoner.py orchestrator/game.py` | 0 | `llm/budgeted_client.py:247: self._budget.preflight(...)` and `:291: self._budget.charge_response(response)` |
| `git grep -nE "meeting_transcript\|prompt_version\|llm_cost\|cost_usd\|MeetingReplayEntry\|LLMCallRecord" orchestrator/replay.py` | 0 | `orchestrator/replay.py:321: "MeetingReplayEntry",` (full record types: `LLMCallRecord` at :51, `MeetingReplayEntry` at :86, `cost_usd` at :71, `prompt_versions` at :114) |
| `git grep -nE "200\b.*byte.identical\|byte.identical.*200\|max_ticks=200\|range\(200\)" tests/orchestrator/` | 0 | `tests/orchestrator/test_game.py:481: scheduler=TickScheduler(max_ticks=200)` (R-3 regression; the R-9 long-horizon byte-identity test lives at `tests/orchestrator/test_replay_meetings.py:389` with `max_ticks=250` + full meeting cycle) |
| six-seed sweep (0,1,2,7,42,100, max_ticks=1000) | 0 each | 5×CREWMATES, 1×IMPOSTORS — all six decisive (final ticks: 11, 9, 7, 7, 8, 10) |
| 20-game fake-provider tournament | 0 | `crew_wins=14, impostor_wins=6, tick_budget_reached=0, decisive_split: CREWMATES=70.00% IMPOSTORS=30.00% of 20 decisive` |

## 3. Finding closure table

| ID | Severity | Source audit | Disposition | Evidence | Blocker? |
| --- | --- | --- | --- | --- | --- |
| L-1 | Low | post-3.8 §L-1 | Closed | [tests/llm/test_budget.py:270-301](tests/llm/test_budget.py#L270-L301) `TestSlackBoundary` pins `cap=0.30, charge=0.30 + 1e-3` raises `BudgetExceededError` (and `dimension == "cost_usd"`) and `cap=0.30, charge=0.30 + 1e-9` does not. The class docstring references `_COST_USD_CAP_SLACK` by name. | no |
| L-2 | Low | post-3.8 §L-2 | Closed | [tests/agents/test_memory_rendering.py:693-732](tests/agents/test_memory_rendering.py#L693-L732) `TestLastSeenOnConfirmedDead::test_last_seen_suffix_renders_for_confirmed_dead_player` records `saw_player` (tick 10, MEDBAY) + `saw_body` (tick 15) for `p-2`, renders via `render_for_prompt`, and asserts `"p-2: suspicion 0.90 (last seen in MEDBAY at tick 10)"` is present. | no |
| C-1 | Concern | post-3.8 §C-1 | Closed | Production code closes the hedge: [agents/strategic/reasoner.py:224-242](agents/strategic/reasoner.py#L224-L242) imports `_assert_no_recursive_hidden_fields` and `_assert_no_role_bearing_values` directly from `eval.leak_test` and invokes them on the rendered prompt payload (lines 241-242). [tests/agents/test_strategic_reasoner.py:608-787](tests/agents/test_strategic_reasoner.py#L608) `TestR10LeakScannerAcceptanceGate` (8 tests) drives the reasoner pipeline with planted role-bearing player ids, contradiction summaries, meeting triggers, `killed_by` substrings, kill-attribution substrings, injected role headers, and recursive hidden fields — each expects `AssertionError("role-bearing value" / "hidden")`. [tests/agents/test_memory_rendering.py:26-29](tests/agents/test_memory_rendering.py#L26-L29) also imports both scanners directly. | no |
| C-2 | Concern | post-3.8 §C-2 | Closed | [DESIGN.md:593](DESIGN.md#L593) contains the "Non-elastic block carve-out" paragraph verbatim: role + tasks-completed + beliefs + contradictions always retained; only observations are elastic. [agents/strategic/reasoner.py:41-52](agents/strategic/reasoner.py#L41-L52) explicitly documents the contract ("Callers do not re-implement budget elasticity for beliefs/contradictions") and lines 383/439/499 simply delegate to `render_for_prompt(memory, token_budget=self._token_budget)`. No re-implementation of dropping. | no |
| C-4 | Concern | post-3.8 §C-4 | Closed | [agents/strategic/prompts/loader.py:46-60](agents/strategic/prompts/loader.py#L46-L60) imports `Environment, FileSystemLoader, StrictUndefined` and constructs the env with `undefined=StrictUndefined`. Loader exposes per-template callables (`crewmate_report_prompt`, `impostor_report_prompt`, `accusation_round_prompt`, `vote_ballot_prompt`). [tests/agents/test_strategic_prompts.py](tests/agents/test_strategic_prompts.py) (458 lines) covers all four templates with one `Test*Template` class each, asserting: (a) non-empty output, (b) version-marker substring (e.g. `"vote_ballot/v1"` at line 384), (c) `FakeProvider().complete(...)` response parses through the Pydantic schema (`ReportDocument.model_validate_json` lines 200, 271; `Statement.model_validate_json` line 351; vote at 358+). Strict-undefined regressions are also pinned (`test_missing_kwarg_raises_under_strict_undefined`, 4 instances). | no |
| C-5 | Concern | post-3.8 §C-5 | Closed | [llm/budgeted_client.py](llm/budgeted_client.py) defines `BudgetedLLMClient` wrapping any `LLMClient` + `GameBudget`; `complete()` calls `self._budget.preflight(...)` (line 247) before the inner call and `self._budget.charge_response(response)` (line 291) after. [tests/llm/test_budgeted_client.py](tests/llm/test_budgeted_client.py) (785 lines, 36 tests, all green) includes `TestPreflightOrdering::test_preflight_runs_before_inner_client` (line 223), `TestMeetingShapedFlow::test_sequence_of_calls_accumulates_to_cap` (line 327), and `test_meeting_ceiling_trips_preflight_not_silent_truncation` (line 352) — these exercise cumulative cost approaching and then exceeding a configured cap and assert `BudgetExceededError` propagates from preflight, not from silent truncation. Adapter integration is duck-typed: [orchestrator/game.py:243-254](orchestrator/game.py#L243-L254) `DefaultMeetingRunner` accepts any `LLMClient` (including a `BudgetedLLMClient`); [tests/agents/test_strategic_reasoner.py:840-873](tests/agents/test_strategic_reasoner.py#L840) `TestBudgetPropagation::test_budget_exceeded_error_propagates_through_reasoner` and `::test_reasoner_uses_budgeted_client_by_default_when_wrapped` pin that the reasoner uses the wrapped adapter when one is supplied. | no |
| R-9 | Concern → Phase-3 addendum | May-15 §R-9 | Closed | [orchestrator/replay.py](orchestrator/replay.py) defines `LLMCallRecord` (line 51) with `cost_usd` (line 71), and `MeetingReplayEntry` (line 86) carrying `llm_calls: tuple[LLMCallRecord, ...]` (line 113) and `prompt_versions: Mapping[str, str]` (line 114). Discriminated union `ReplayEntry \| MeetingReplayEntry` at line 120. [tests/orchestrator/test_replay_meetings.py:389-445](tests/orchestrator/test_replay_meetings.py#L389-L445) `test_byte_identical_long_horizon_meeting_replay` runs two independent games at `max_ticks=250` against a deterministic stub LLM, asserts the JSONL files are byte-identical, and verifies ≥1 full meeting cycle (16 LLM calls = 4 reports + 8 statements + 4 ballots) is recorded. [tests/orchestrator/test_replay_meetings.py:448-484](tests/orchestrator/test_replay_meetings.py#L448) `test_call_record_captures_usage_cost_model_call_kind` pins every `LLMCallRecord` field. Short-horizon byte-identity smoke at [tests/orchestrator/test_game.py:139](tests/orchestrator/test_game.py#L139) and [tests/orchestrator/test_replay_meetings.py:487-525](tests/orchestrator/test_replay_meetings.py#L487) preserved. | no |
| R-10 / strategic | Concern → Phase-3 addendum | May-15 §R-10 | Closed | Closed alongside C-1. [tests/agents/test_strategic_reasoner.py:638-655](tests/agents/test_strategic_reasoner.py#L638) `test_planted_role_bearing_player_id_trips_scanner` plants `"crewmate_leak_id"` into a `saw_player` payload (via `_build_memory_with_leak`, line 132), drives the reasoner pipeline, and asserts the scanner trips with `AssertionError("role-bearing value")`. Two additional planted-input pins (contradiction summary at line 657; meeting trigger at line 685) cover the other rendered surfaces. Six- and seven-tests covering `killed_by`, kill-attribution, and injected role headers add defense-in-depth. | no |

## 4. Observations

The R-9 long-horizon byte-identity test lives in
`tests/orchestrator/test_replay_meetings.py`, not in `test_game.py`,
so the narrow grep in the prompt (`max_ticks=200` or `range(200)`)
matched only the unrelated R-3 regression at `test_game.py:481`. The
real R-9 gate uses `max_ticks=250` and reads cleanly. No actionable
finding — adjusted the prompt's grep mentally and the gate is real.
The post-3.8 C-1 closure deserves a note: the canonical scanners are
imported directly inside `agents/strategic/reasoner.py` (production
code, line 224) rather than re-imported from each test file. This
guarantees runtime use rather than test-only use and is, if anything,
a stronger closure than the prompt's grep template assumed.
`tasks/phase-3.md:600` still contains the "or their canonical Phase 3
successors" hedge wording (untouched on this branch) — the
implementation chose direct import, which is the stricter of the two
options. The fresh audit may decide whether to update the task text
to match.

## 5. Verdict justification

Every row in §3 is `Closed` with concrete file/line evidence and (for
each behavioral finding) at least one regression test that fails if
the behavior silently regresses. The fast test suite is green (663
passed, 1 skipped). The Phase 2 substrate gates that protect
deterministic replay still hold: the six-seed sweep is fully decisive
(5 CREWMATES, 1 IMPOSTORS) and the 20-game fake-provider tournament
splits 70/30 — both decisive sides clear 20% with zero
`tick_budget_reached`. The two Phase-3 acceptance-gate findings from
the May-15 reconciled audit (R-9, R-10/strategic) are both `Closed`,
which is the binding condition for proceeding to the full
Pre-Phase-4 audit.

---

- **Report path:** `/Users/danielkeinan/projects/AiLibi/audits/audit-2026-05-25-0345-pre-phase-4-verification.md`
- **Verdict:** Verification passed — Pre-Phase-4 audit may proceed.
- **Counts:** Closed = 8, Partial = 0, Not closed = 0.
- **Failed commands:** none.
