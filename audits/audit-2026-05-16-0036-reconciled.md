# AiLibi Pre-Phase-3 Checkpoint Audit — Reconciled

- **Date:** 2026-05-16 00:36 local
- **Audited HEAD:** `5988e66 update audit prompts for re-audit` on `main`
- **Regression baseline:** `0610b72 Merge pull request #29 from dkdan10/claude/headless-tournament-harness-HEXY6` (HEAD at the May-15 reconciled audit)
- **Inputs reconciled:** `audits/audit-2026-05-16-0024-claude.md`, `audits/audit-2026-05-16-0023-codex.md`
- **Prior baseline reference:** `audits/audit-2026-05-15-0225-reconciled.md`
- **Scope:** read-only adjudication; no fixes attempted; the reconciliation prompt was read as the IDE selection but the audit prompt was not read
- **Forbidden input note:** `audits/prompts/pre-phase-3-audit-prompt.md` was not read

---

## 1. Executive Summary

**Verdict: Ready with fixes.** Static gates are green at current `HEAD`: `bash scripts/check.sh` passed with 289 tests, import-linter kept the agent/engine firewall, task docs and prompts are in sync, mypy strict passed, and ruff/format checks were clean. The Phase 2 behavioral gates pass live: the required six-seed sweep produced five `CREWMATES` and one `IMPOSTORS` outcome (all six decisive, all under 12 ticks), and a fresh 100-game tournament reproduced `crew_wins=68 / impostor_wins=25 / tick_budget_reached=0 / meeting_phase_reached=7` with decisive split `CREWMATES=73.12% / IMPOSTORS=26.88%` of 93 decisive — both sides comfortably above the 20% merge criterion. Same-seed determinism is preserved: a seed-0 replay at 200 ticks is byte-identical across two runs. The tournament leak scan walked all 100 audit logs with zero violations.

The reconciliation table contains **0 Critical, 0 High, 1 Medium, 2 Low, and 4 Concern** active findings. The single Medium is a documentation drift: `DESIGN.md` §3.5 paragraph names `tasks_per_crewmate` as a parameter on `orchestrator.seeder.seed_initial_state` and claims a "Current canonical default" of `tasks_per_crewmate=1`, but the seeder signature has no such parameter and `_build_tasks` hardcodes one task per crewmate. The Lows are a missing same-tick crew-win pin and a missing missing-payload pin on the temporary body-id parsing bridge. The four Concerns are forward-looking risks that are either scheduled for retirement in Phase 3 or test-hygiene-only.

Both source audits agreed the prior reconciled audit's R-1..R-14 are closed or correctly wired into Phase 3 task DoDs. The reconciled verdict is one notch more conservative than the Claude verdict because the Medium drift is concrete enough that a Phase 3 implementing agent reading DESIGN.md §3.5 for balance levers would follow it into a parameter that does not exist. Fixing M-1 is a one-line documentation edit and does not block Phase 3 start; the two Low test gaps are worth landing soon but block nothing.

## 2. Verdict

**Ready with fixes.** No Critical or High finding is open against current `main`. The single Medium is a doc-vs-code drift in DESIGN.md §3.5 that affects Phase 2 balance documentation; the two Lows are regression-test hardening items. None of these block Phase 3 implementation work from starting. Recommend landing M-1 (a one-line DESIGN.md edit) before Phase 3 agents rely on the balancing docs, and landing L-1/L-2 opportunistically.

## 3. Commands Run and Evidence Sources

All commands ran from `/Users/danielkeinan/projects/AiLibi`. Exit codes are zero except where noted; `git grep` exits `1` when no match is found (the desired result for the post-2.11 guards).

| Command | Result / evidence |
|---|---|
| `git rev-parse HEAD`; `git log -1 --oneline` | `5988e66ff40d17e063fb9c2cb6bb3ab07e61951a`; `5988e66 update audit prompts for re-audit` |
| `date '+%Y-%m-%d-%H%M'` | `2026-05-16-0036` |
| `wc -l audits/audit-2026-05-16-0024-claude.md audits/audit-2026-05-16-0023-codex.md audits/audit-2026-05-15-0225-reconciled.md` | 268, 259, 344 lines |
| `bash scripts/check.sh` | `Contracts: 1 kept, 0 broken. Task docs validation passed: 61 tasks and 61 prompts. All 61 prompts are in sync. Success: no issues found in 77 source files. 289 passed in 3.46s` (exit 0) |
| `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/rec-r-$seed.jsonl --max-ticks 1000; done` | seed 0 → CREWMATES tick 11; seed 1 → CREWMATES tick 9; seed 2 → CREWMATES tick 7; seed 7 → CREWMATES tick 7; seed 42 → CREWMATES tick 8; seed 100 → IMPOSTORS tick 10. All six decisive. |
| `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/rec-tournament --max-ticks 1000` | `games:100 crew_wins:68 impostor_wins:25 tick_budget_reached:0 meeting_phase_reached:7 decisive_split: CREWMATES=73.12% IMPOSTORS=26.88% of 93 decisive` |
| Tournament leak scanner over `/tmp/rec-tournament/*.audit.jsonl` (recursive hidden-fields + role-bearing-values; one packet per line) | `audit_logs=100 packets=3275 scanner=PASS (violations=0)`. (Both source audits report `packets=6550`; that count appears to count walked sub-dicts, not top-level packet entries. The substantive result — zero violations — reproduces.) |
| `uv run python scripts/run_game.py --seed 0 --replay-path /tmp/rec-r0{a,b}.jsonl --max-ticks 200`; `cmp` | `BYTE_IDENTITY=PASS` |
| `grep -n "tasks_per_crewmate" DESIGN.md` | One hit at `DESIGN.md:291` |
| `grep -n "tasks_per_crewmate" orchestrator/seeder.py` | empty (parameter does not exist) |
| Read of `orchestrator/seeder.py:29-35` (signature) and `:155-176` (`_build_tasks`) | Signature is `seed, game_map, num_players, num_impostors`; one task per crewmate via `for index, crewmate_id in enumerate(crewmate_ids)` |
| `grep -n "same tick\|last incomplete\|removes the last\|kill.*crew win\|CREWMATE_TASKS.*kill\|same_tick" tests/engine/test_tick.py` | Only `test_repair_prevents_same_tick_sabotage_timeout_when_completed` at line 507 (sabotage, not kill-last-task) |
| Read of `tests/engine/test_tick.py:911-988` (R-5 test) | Test completes the surviving alive-owned task on a follow-up tick; the same-tick win path (kill removes only incomplete task) is not exercised |
| Read of `agents/tactical/impostor_policy.py:80-94, 244-336` | `_STALENESS_THRESHOLD: Final[int] = 30`; `_BODY_ID_VICTIM_PATTERN = re.compile(r"^body-(.+)-\d+$")`; `_confirmed_dead_from_bodies` raises `ValueError` when `body_id` is not a string |
| `grep -n "f\"body-" engine/rules.py` | `engine/rules.py:69: body_id = f"body-{target.id}-{state.tick}"` |
| Read of `tests/agents/test_impostor_policy.py:510-602` | Four cases cover stale, matching body, alive-target fallback, and one malformed-string body id; no test plants a missing or non-string `body_id` payload, leaving the `raise ValueError` branch at `impostor_policy.py:260-263` uncovered |
| `grep -n "victim-body" tests/observation/test_service.py` | Hits at lines 343 and 358 (body id string, not player id) |
| `git grep -nE "['\"](player\|impostor)-[0-9]+['\"]" eval/ tests/` | empty (exit 1 — desired post-2.11) |
| `git grep -nE "['\"](player\|impostor\|victim\|observer\|crew-[0-9]+)['\"]" tests/observation/test_service.py` | empty (exit 1 — desired post-2.11) |
| `grep -n "_assert_no_recursive_hidden_fields\|_assert_no_role_bearing_values" tasks/phase-3.md` | Hits at `tasks/phase-3.md:124` (rendered memory) and `:335` (strategic prompts); both name the helpers explicitly but hedge "or their canonical Phase 3 successors" |
| Read of `tests/orchestrator/test_game.py:139-155` | Phase 2 byte-identity test pins at 20 ticks; Phase 3.12 R-9 acceptance gate at `tasks/phase-3.md:444` requires ≥ 200 ticks |
| `git diff --stat 0610b72..HEAD` | 32 files changed, 4562 insertions, 75 deletions; only 7 source files changed (`AGENTS.md`, `DESIGN.md`, `agents/tactical/impostor_policy.py`, `engine/maps/canonical_1.yaml`, `engine/tick.py`, `engine/win_conditions.py`, `eval/leak_test.py`); the rest are tasks/tests/audit prompts |
| `git diff --name-only 0610b72..HEAD` over all baseline-row paths | No relevant source diffs for boundary contracts, base/runtime, perception, pathing, crewmate FSM, memory scaffolding, ObservationService, replay, visibility, state model, action types, or contract hardening |

Key files read for evidence: `audits/audit-2026-05-16-0024-claude.md`, `audits/audit-2026-05-16-0023-codex.md`, `audits/audit-2026-05-15-0225-reconciled.md`, `DESIGN.md`, `tasks/phase-2.md`, `tasks/phase-3.md`, `orchestrator/seeder.py`, `agents/tactical/impostor_policy.py`, `engine/rules.py`, `engine/tick.py`, `engine/win_conditions.py`, `engine/maps/canonical_1.yaml`, `observation/audit.py`, `tests/engine/test_tick.py`, `tests/agents/test_impostor_policy.py`, `tests/orchestrator/test_game.py`, `tests/observation/test_service.py`, and `tests/eval/test_balance_eval.py`.

## 4. Regression Baseline

Procedure: for every prior-Pass row in `audit-2026-05-15-0225-reconciled.md` §4, I checked `git diff --name-only 0610b72..HEAD -- <paths>` and re-verified through `bash scripts/check.sh`. "No diff" ⇒ Still Pass; "diff exists" ⇒ re-verified by source read.

| Prior Pass item | Window diff vs `0610b72` | Reconciled status |
|---|---|---|
| Phase 0 repo skeleton, CI, import lint, check scripts | None of substance; `AGENTS.md` gained GitHub-operation guidance | **Still Pass (no relevant diff)**; `check.sh`, lint-imports, docs validation all green |
| 1.1 static map data | `engine/maps/canonical_1.yaml` cooldown `10 → 4` only | **Pass (re-verified)**; pinned at `tests/engine/test_map_loader.py:200-205` |
| 1.2 state model | No source diff | **Still Pass (no diff)** |
| 1.3 action types | No source diff | **Still Pass (no diff)** |
| 1.3.5 engine contract hardening | No source diff | **Still Pass (no diff)** |
| 1.4 rules and win conditions | `engine/win_conditions.py` gained the §3.5 dropped-rule anchor comment; `engine/rules.py` no diff | **Pass (re-verified)** |
| 1.5 `advance_tick` | `engine/tick.py::_apply_kill` adds dead-task drop + `last_action` clear (R-5) | **Pass (re-verified)**; purity preserved; byte-identity test still passes |
| 1.6 visibility | No source diff | **Still Pass (no diff)** |
| 1.7 ObservationService | No source diff in `observation/service.py`/`packet.py`; only test changes | **Still Pass (re-verified)**; 100-log/3,275-packet scan clean |
| 1.8 Replay log | No source diff in `orchestrator/replay.py` | **Still Pass for Phase 2**; Phase 3 replay expansion is wired into Task 3.12 |
| 1.B1 scripted fixtures | No fixture diff in window | **Still Pass** |
| 1.B2 leak test | `eval/leak_test.py` sentinel cleanup (`impostor-1` → `crew_role_leak_fixture`) | **Pass (re-verified)** |
| 2.1 boundary contracts | No source diff | **Still Pass (no diff)** |
| 2.2 agent base/runtime | No code diff | **Still Pass (no diff)** |
| 2.3 memory scaffolding | No diff in `agents/memory/{episodic,working,beliefs}.py`; `agents/memory/store.py` still absent by design | **Still Pass**; Task 3.3 owns the composite surface |
| 2.4 perception ingestion | No source diff | **Still Pass (no diff)** |
| 2.5 pathing | No source diff | **Still Pass (no diff)** |
| 2.6 crewmate FSM | No diff in `agents/tactical/crewmate_policy.py` | **Still Pass (no diff)** |
| 2.7 impostor FSM | Diff: `agents/tactical/impostor_policy.py` gained R-3 staleness + confirmed-dead pruning | **Pass (re-verified)**; tests cover stale window, confirmed-dead, malformed body id, and alive-target fallback |
| 2.8 headless orchestrator | No diff in `orchestrator/game.py` | **Still Pass (no diff)**; meeting interpose point at `orchestrator/game.py:162-167` is still a single branch |
| 2.8.5 leak repair + tactical termination | Covered above by 1.B2 and impostor policy R-3 closure | **Re-verified** |
| 2.9 tournament harness | DoD wording aligned with merge criterion at `tasks/phase-2.md:932-938` ≡ `:1589-1593` | **Re-verified**; live 100-game run meets the criterion |
| 2.10 pre-Phase-3 tactical repair | New task | See §6.1 |
| 2.10.5 Phase 2 tournament balance | New task | See §6.2 |
| 2.11 contract hygiene and test-guard cleanup | New task | See §6.3 |
| 2.12 behavioral CI gates and remaining test hygiene | New task | See §6.4 |
| I-1 .. I-12 + multi-agent block | See §7 | **Re-verified** |

Both source audits agreed cell-by-cell on every regression-baseline row. No reconciliation needed within §4.

## 5. Prior Audit Follow-Through

Both source audits re-checked the May-15 reconciled audit's R-1..R-14 and agreed on the closure status of every row. I adopt their reconciled view; no disagreements surfaced.

| Prior finding | Status | Evidence |
|---|---|---|
| **R-1** [Critical] 100-game tournament balance | **Resolved** | PR #31 (`1ae5fe8`) set `kill_cooldown_ticks: 4` at `engine/maps/canonical_1.yaml:34`. Live re-run: 68/25/0/7 → 73.12%/26.88% of 93 decisive. Pinning canary: `tests/eval/test_balance_eval.py:278-298`. |
| **R-2** [Critical] Six-seed decisive sweep | **Resolved** | PR #30 + PR #31. Live sweep: 5 CREWMATES + 1 IMPOSTORS, all decisive, all under 12 ticks. CI floor: `tests/eval/test_balance_eval.py:341-381`. |
| **R-3** [High] Impostor stale-target chase loop | **Resolved** | `agents/tactical/impostor_policy.py:86, 94, 270-336` adds `_STALENESS_THRESHOLD=30`, `_BODY_ID_VICTIM_PATTERN`, and the two filters in `_scored_targets`. Pin: `tests/agents/test_impostor_policy.py:510-602`; integration: `tests/orchestrator/test_game.py:457-540`. |
| **R-4** [High] Old-id grep guard cleanup | **Resolved** | PR #33 replaced planted strings with `crew_role_leak_fixture`. `git grep -nE "['\"](player\|impostor)-[0-9]+['\"]" eval/ tests/` returns empty. |
| **R-5** [Concern] Dead-crewmate task rule | **Resolved** | `engine/tick.py:247-265` drops victim's incomplete tasks; `engine/win_conditions.py:17-25` documents the rule; `tests/engine/test_tick.py:911-988` pins the case. Same-tick consequence is documented but unpinned (L-1 below). |
| **R-6** [Concern] `agents/memory/store.py` for Phase 3.3 | **Wired into Task 3.3** | `tasks/phase-3.md:123` adds the R-6 acceptance gate naming the composite (episodic + working + beliefs) memory surface and `render_for_prompt`. `agents/memory/store.py` correctly remains absent in Phase 2. |
| **R-7** [Medium] Task 2.8.5 file-scope drift | **Resolved** | `tasks/phase-2.md:865-873` enumerates the six unlisted files. |
| **R-8** [Medium] Task 2.9 DoD vs merge criterion | **Resolved** | `tasks/phase-2.md:932-938` matches `tasks/phase-2.md:1589-1593` verbatim. |
| **R-9** [Concern] Replay/debug expansion before LLM nondeterminism | **Wired into Task 3.12** | `tasks/phase-3.md:444` adds the R-9 gate (meeting transcripts, prompt versions, LLM outputs, cost metadata; ≥ 200-tick byte-identical replay test). |
| **R-10** [Concern] Leak scanning for rendered memory and strategic prompts | **Wired into Tasks 3.3 + 3.9** | `tasks/phase-3.md:124, 335` name the helpers and require planted negative tests; "or their canonical Phase 3 successors" hedge tracked as C-3 below. |
| **R-11** [Concern] Automated guard for behavioral merge criteria | **Resolved** | `tests/eval/test_balance_eval.py:341-381` (decisive-outcome CI floor) + `tests/eval/test_balance_eval.py:278-298` (10-game canary). |
| **R-12** [Low] Property-test vocabulary | **Resolved** | `tests/engine/test_tick_properties.py:162-243` adds `_role_aware_actions` strategy covering kill / vent / report / wait. |
| **R-13** [Low] Audit-log append-mode regression | **Resolved** | `tests/observation/test_service.py:388-412` pins two-instance append behavior. |
| **R-14** [Concern] Role-bearing helper ids in observation tests | **Resolved** | Helper ids renamed to `p-1`..`p-4`. The `victim-body` body-id string remains acceptable per PR #33 Decisions (tracked as C-4 below — test hygiene only). |

## 6. Task-by-Task DoD Audit

### 6.1 Task 2.10 — Pre-Phase-3 Tactical Repair (PR #30, `30725b0`, merged `36177ea`)

| DoD bullet | Verdict | Evidence |
|---|---|---|
| R-5 dropped rule pinned in DESIGN.md + `win_conditions` anchor | Pass | `DESIGN.md:287-289`; `engine/win_conditions.py:17-25` |
| R-5 implementation and regression test | Pass | `engine/tick.py:247-265`; `tests/engine/test_tick.py:911-988` covers (a) incomplete-dropped, (b) completed-retained, (c) post-kill alive-owned task reaches CREWMATE_TASKS |
| R-3 staleness/dead-target pruning unit test | Pass | `tests/agents/test_impostor_policy.py:510-602` (4 cases) |
| R-3 pruning implementation | Pass | `agents/tactical/impostor_policy.py:80-95, 244-336` |
| R-3 default-agent integration regression | Pass | `tests/orchestrator/test_game.py:457-540` (seed-0 oscillation guard) |
| R-2 six-seed decisive sweep | Pass at HEAD | Live re-run: 5 CREWMATES + 1 IMPOSTORS, all decisive |
| R-1 100-game tournament | Pass via PR #31 | Live re-run: 68/25/0/7; 73.12%/26.88% |
| Static gates (mypy, ruff, lint-imports, generate_prompts --check, check.sh) | Pass | §3 |
| File-scope discipline | Pass | `30725b0` touched only the six in-scope files |

**Verdict:** Pass.

### 6.2 Task 2.10.5 — Phase 2 Tournament Balance (PR #31, `1ae5fe8`, merged `d278829`)

| DoD bullet | Verdict | Evidence |
|---|---|---|
| Path A search space documented | Pass with M-1 doc drift | `DESIGN.md:291`; `tasks_per_crewmate` parameter claim is inaccurate — see §10 R-1 |
| Path A acceptance criterion | Pass | Live 100-game run reproduces PR #31 baseline |
| Path A committed config | Pass | `engine/maps/canonical_1.yaml:34` reads `kill_cooldown_ticks: 4` |
| Path A regression test | Pass | `tests/eval/test_balance_eval.py:278-298` (10-game canary) |
| Path D Phase 2 amendment | N/A | Path A succeeded at step 1 (cooldown only); Path D not triggered |
| Dropped-rule consequence documented | Pass | `DESIGN.md:289` documents the same-tick crew-win consequence (unpinned — see §10 R-2) |
| Determinism preserved | Pass | `tests/orchestrator/test_game.py:139-155` and `eval/determinism_test.py` pass; live byte-identity re-verified |
| Test cascades resolved | Pass with documented deviation | `tests/engine/test_map_loader.py:200-205` and `tests/engine/test_tick.py:108-117` updated; `tests/engine/test_tick.py` was outside the original scope, but PR #33's optional historical note at `tasks/phase-2.md:1311-1320` records this retroactively |
| Static gates | Pass | §3 |
| File-scope discipline | Pass with documented deviation | See above |

**Verdict:** Pass.

### 6.3 Task 2.11 — Contract Hygiene and Test-Guard Cleanup (PR #33, `9c27a30`, merged `ed56e6f`)

| DoD bullet | Verdict | Evidence |
|---|---|---|
| R-4 old-id grep guard cleared | Pass | Required grep over `eval/ tests/` returns empty; scanner self-tests still trip on `crew_role_leak_fixture` |
| R-7 Task 2.8.5 file-scope drift recorded | Pass | `tasks/phase-2.md:865-873` |
| Optional Task 2.10.5 historical note | Pass | `tasks/phase-2.md:1311-1320` |
| R-8 Task 2.9 DoD wording aligned | Pass | `tasks/phase-2.md:932-938` ≡ `:1589-1593` |
| R-14 observation helper id rename | Pass | `tests/observation/test_service.py:43-59` uses `p-1`..`p-4`; required grep returns empty |
| `generate_prompts.py` after task-doc edit | Pass | PR #33 Decisions document three mechanical prompt updates |
| Static gates | Pass | §3 |
| File-scope discipline | Pass with documented prompt fallout | PR #33 Decisions justify the three regenerated agent_prompts |

**Verdict:** Pass.

### 6.4 Task 2.12 — Behavioral Merge-Criteria CI Gates and Remaining Test Hygiene (PR #34, `d92da83`, merged `5f15af9`)

| DoD bullet | Verdict | Evidence |
|---|---|---|
| R-11 decisive-outcome CI guard | Pass, narrow by design | `tests/eval/test_balance_eval.py:341-381`; catches zero-decisive but not full balance regression. Adjacent 10-game canary `test_canonical_balance_keeps_both_sides_alive` catches the cooldown-10 regression. |
| R-13 audit-log append regression | Pass | `tests/observation/test_service.py:388-412` |
| R-12 broadened property-test vocabulary | Pass | `tests/engine/test_tick_properties.py:181-243` |
| Static gates | Pass | §3 |
| File-scope discipline | Pass | `d92da83` touched exactly the three in-scope files |

**Verdict:** Pass.

## 7. Architectural Invariant Audit

| Invariant | Verdict | Evidence |
|---|---|---|
| I-1 / I-2 `advance_tick` pure + deterministic | Pass | `engine/tick.py:422-492` unchanged in signature; `_apply_kill` rewrite is pure state-in/state-out; byte-identity at HEAD: PASS |
| I-3 replay determinism (Phase 2) | Pass | `tests/orchestrator/test_game.py:139-155`; live seed-0 byte-identity at 200 ticks PASS |
| I-4 engine state remains engine-owned | Pass | `engine/win_conditions.py:17-40` reads only engine fields; no agent imports |
| I-5 `agents/` does not import `engine/` | Pass | `lint-imports` KEPT; `grep -RIn "from engine\|import engine" agents` empty |
| I-6 agents receive only packet + public map | Pass | `orchestrator/game.py:202-211` |
| I-7 agents emit only `ActionIntent` | Pass | `orchestrator/game.py:150-160` |
| I-8 observation firewall strips hidden info | Pass | 100 tournament audit logs / 3,275 top-level packets scanned clean (zero violations) |
| I-9 invalid inputs raise | Pass | Boundary and seeder invariant tests pass |
| I-10 Pydantic v2 boundary | Pass | Boundary schemas unchanged; tests pass |
| I-11 engine state immutability | Pass | World-state tests pass; `_apply_kill` constructs new state via `replace` |
| I-12 orchestrator duplicate-actor rejection | Pass | `tests/orchestrator/test_action_ordering.py` passes |
| Multi-agent live harness | Pass | Six-seed sweep all decisive; 100-game tournament meets criterion; tournament audit logs leak-clean |

Both source audits Pass every invariant; no reconciliation needed within §7. The new `_BODY_ID_VICTIM_PATTERN` is a string coupling on the engine body-id format but does not violate I-5 (no `from engine` import); tracked as C-1 below.

## 8. Specific Questions for the Post-2.12 Layer

1. **Is the determinism boundary clean enough for Phase 3 LLM debugging?** Yes for Phase 2. `tests/orchestrator/test_game.py:139-155` pins same-seed default-agent byte identity at 20 ticks, and a fresh seed-0 byte-identity check at 200 ticks reproduces. `orchestrator/replay.py:16-24` still records only `game_id`, `tick`, `actions`, and `state_hash`, which is correct for Phase 2 but insufficient for LLM-layer bisecting. That gap is correctly wired into Task 3.12 at `tasks/phase-3.md:444` (transcripts, prompt versions, LLM outputs, cost metadata; ≥ 200-tick byte identity).

2. **Does `agents/memory/` expose the shape Phase 3.3 needs?** The boundary is concrete. `agents/memory/store.py` is absent by design; Task 3.3 at `tasks/phase-3.md:117-126` requires aggregating the existing episodic, working, and belief components into a composite surface with `render_for_prompt`. `git ls-files` confirms `agents/memory/store.py` is still absent, as expected for Phase 3.3 scope.

3. **Does the orchestrator expose a clean meeting interpose point?** Yes. `orchestrator/game.py:162-167` is a single clean branch that returns `MEETING_PHASE_REACHED` when the engine transitions to `phase == "MEETING"`. Phase 3.12 can replace this branch with a `MeetingManager` dispatch + `apply_meeting_result` call without surgery elsewhere in `HeadlessGame.run`.

4. **Is leak testing strong enough for Phase 3?** Strong for `ObservationPacket`s (100-log/3,275-packet clean scan at HEAD). The R-10 addenda at `tasks/phase-3.md:124` (rendered memory) and `:335` (strategic prompts) name the existing helpers and require planted-negative regression tests. The "or their canonical Phase 3 successors" hedge in both rows is a minor risk (C-3 below).

5. **Do the DESIGN.md balance levers match the seeder?** No — `DESIGN.md:291` describes `tasks_per_crewmate` as "a parameter on `orchestrator.seeder.seed_initial_state`" and claims a "Current canonical default: `tasks_per_crewmate=1`", but the seeder signature at `orchestrator/seeder.py:29-35` has no such parameter and `_build_tasks` hardcodes one task per crewmate at `:155-176`. This is R-1 below.

6. **New Critical or High findings introduced by this audit window?** None. The reconciliation table has 0 Critical, 0 High, 1 Medium, 2 Low, and 4 Concern active rows.

## 9. Test Quality and Coverage Gaps

- **R-11 CI floor false-positive risk.** Low. Inverting `kill_cooldown_ticks` to 10 in `engine/maps/canonical_1.yaml` would reproduce the prior-audit failure mode (all five seeds → `TICK_BUDGET_REACHED` at `max_ticks=200`); `test_default_agent_sweep_reaches_at_least_one_decisive_outcome` asserts `decisive >= 1` and would fail. The adjacent 10-game canary `test_canonical_balance_keeps_both_sides_alive` would also catch a cooldown-10 regression (`crew_wins=10 impostor_wins=0` per Codex's temporary probe).

- **R-12 property-test reject-path coverage.** Genuine, not just no-op. In `_initial_state`, `p-3` is the impostor with `cooldown=0`, so the first drawn `kill` succeeds; subsequent kill draws hit `ActionRejectedError("kill is on cooldown")`; vent draws hit "cannot enter vent from another room" (CAFETERIA has no vent); report draws on `missing-body` hit "unknown body id". All four verbs reach engine rejection branches.

- **R-13 append-mode mutation resistance.** Strong. `observation/audit.py:20-23` opens with `mode="a"` per call; a `"w"` mutation would truncate at the second open, breaking both `len(lines) == 2` and the order assertions in `tests/observation/test_service.py:388-412`.

- **L-1: Same-tick crew-win edge unpinned.** `DESIGN.md:289` documents that an impostor kill removing the last incomplete task triggers `GameOver(winner=CREWMATES, reason=CREWMATE_TASKS)` on the same tick. The R-5 test at `tests/engine/test_tick.py:911-988` only exercises the follow-up-tick path. `grep -n "same tick\|last incomplete\|removes the last\|kill.*crew win\|CREWMATE_TASKS.*kill" tests/engine/test_tick.py` returns only an unrelated sabotage test.

- **L-2: Body-id missing-payload uncovered.** `agents/tactical/impostor_policy.py:260-263` raises `ValueError` if `body_id` is not a string. `tests/agents/test_impostor_policy.py:510-602` covers matching body ids, the alive-target fallback, and one malformed string body id (`"malformed"`, regex non-match) — but no test plants a missing or non-string `body_id` payload, so the `raise ValueError` branch is uncovered.

- **C-1: `_BODY_ID_VICTIM_PATTERN` engine-format coupling.** If `engine/rules.py:69` ever changes the body-id format (currently `f"body-{target.id}-{state.tick}"`) without updating `_BODY_ID_VICTIM_PATTERN` (`^body-(.+)-\d+$`), no test would detect the silent loss of the R-3 dead-target filter — the agent would just lose confirmed-dead pruning and the impostor stale-target loop could partially regress (only the 30-tick staleness threshold would still bound it).

- **C-2: Long-horizon byte identity unpinned.** Phase 2 byte identity is pinned at 20 ticks. Phase 3.12 R-9 at `tasks/phase-3.md:444` requires ≥ 200 ticks (or one meeting cycle). Not a current defect — wired forward.

## 10. Defects and Risks

### R-1 [Medium] `DESIGN.md` §3.5 names `tasks_per_crewmate` as a `seed_initial_state` parameter that does not exist

- **Status:** Open. (Source severity: Claude Medium, Codex Medium — Confirmed.)
- **Evidence:** `DESIGN.md:291` reads: *"(2) `tasks_per_crewmate ∈ {2, 3}` (a parameter on `orchestrator.seeder.seed_initial_state`) paired with `kill_cooldown_ticks ∈ {6, 4}`"* and *"Current canonical default: `kill_cooldown_ticks=4`, `tasks_per_crewmate=1`, `sabotages.lights.duration_ticks=90`."* But `grep -n "tasks_per_crewmate" orchestrator/seeder.py` returns no results; `seed_initial_state` at `orchestrator/seeder.py:29-35` has parameters `seed`, `game_map`, `num_players`, `num_impostors` only. `_build_tasks` at `orchestrator/seeder.py:155-176` hardcodes one task per crewmate via the `for index, crewmate_id in enumerate(crewmate_ids)` loop. PR #31 Decisions also state "No seeder change required (cooldown-only fix)."
- **Why it matters:** Phase 2 audit prompt §6.4 specifically asks whether DESIGN.md's tuning levers match the seeder. A Phase 3 implementing agent reading §3.5 will look for a parameter that does not exist, or may assume the "current default `tasks_per_crewmate=1`" is configurable today. AGENTS.md explicitly says not to guess around drift like this.
- **Recommended action:** One-line DESIGN.md edit. Either (a) remove the "(a parameter on `orchestrator.seeder.seed_initial_state`)" parenthetical and the `tasks_per_crewmate=1` from the "Current canonical default" line, replacing it with a one-line note that `tasks_per_crewmate` was in the Path A search space but not committed because cooldown-only sufficed; or (b) keep the lever but rephrase to *"`tasks_per_crewmate ∈ {2, 3}` (would require parameterizing `orchestrator.seeder.seed_initial_state`; currently hardcoded to one task per crewmate by `_build_tasks`)"*.

### R-2 [Low] DESIGN.md §3.5 same-tick crew-win consequence is documented but unpinned

- **Status:** Open. (Source severity: Claude Low, Codex Low — Confirmed.)
- **Evidence:** `DESIGN.md:289` documents the same-tick consequence: *"an impostor kill which removes the last incomplete task from `state.tasks` triggers the crew win condition on that same tick. This is intended behavior, not an engine bug."* `engine/tick.py:437-479` (`advance_tick`) runs `resolve_win_conditions` after `_apply_kill` within the same tick, and `_apply_kill` at `engine/tick.py:261-265` removes `{owner == target AND not completed}` tasks. But no test asserts a same-tick `GameOver(winner=CREWMATES, reason=CREWMATE_TASKS)` event when the kill is the last-task trigger; `tests/engine/test_tick.py:911-988` only exercises the surviving alive-owned task on a follow-up tick. `grep -n "same tick\|last incomplete\|removes the last\|kill.*crew win\|CREWMATE_TASKS.*kill" tests/engine/test_tick.py` confirms no direct pin.
- **Why it matters:** Latent failure mode. A future refactor that moves `resolve_win_conditions` to a different step or short-circuits when an action-induced delta is "small enough" could regress the documented behavior silently. Severity stays Low because the current `advance_tick` loop is the natural place for the check.
- **Recommended action:** Add a single regression (~20 lines) to `tests/engine/test_tick.py`: construct a state with one incomplete task owned by the victim and zero completed tasks total; advance through a kill action; assert the returned `events` list contains a `GameOverEvent` with `winner == "CREWMATES"` and `reason == "CREWMATE_TASKS"`.

### R-3 [Low] Body-id victim-parsing bridge lacks missing-payload coverage

- **Status:** Open. (Source severity: Codex Low only; unique to Codex — Unique-but-verified.)
- **Evidence:** `agents/tactical/impostor_policy.py:259-263` raises `ValueError("saw_body event missing string 'body_id': ...")` when the `body_id` payload field is missing or not a string. Tests at `tests/agents/test_impostor_policy.py:510-602` cover (a) matching body ids `body-victim-{tick}`, (b) the alive-target fallback when one of two candidates is confirmed dead, (c) a stale-window case, and (d) one malformed STRING body id (`"malformed"`, regex non-match) — but no test plants a missing or non-string `body_id`. The `_saw_body_event` helper at `tests/agents/test_impostor_policy.py:101-106` enforces `body_id: str` at the helper signature, which means the test surface never reaches the missing-payload branch.
- **Why it matters:** The `raise ValueError` branch is the type-safety guard for a temporary Phase-2 inference bridge. The current behavior is probably correct, but a malformed-memory-event path is not pinned and could regress silently if the boundary changes (e.g., `body_id` becomes `Optional[str]`).
- **Recommended action:** Add one unit test (~10 lines) that constructs a `saw_body` `EpisodicEvent` with `payload={}` (or `{"body_id": None, "room": "MEDBAY"}`) and asserts `_confirmed_dead_from_bodies` raises `ValueError`. Pair with R-4 retirement in Phase 3.

### R-4 [Concern] `_BODY_ID_VICTIM_PATTERN` is an agent→engine string coupling on body-id format

- **Status:** Open; scheduled for Phase 3 retirement. (Source severity: Claude Concern only; related to Codex L-2 but framed as architectural risk rather than coverage gap — Unique-but-verified.)
- **Evidence:** `agents/tactical/impostor_policy.py:88-94` documents the pattern as a Phase-2 inference to be retired by a typed `BodyView.victim_id` field. The pattern is `re.compile(r"^body-(.+)-\d+$")`; `engine/rules.py:69` emits `body_id = f"body-{target.id}-{state.tick}"`. The two are coupled by format only — no shared constant — so a refactor of either side that does not also update the other will silently break the R-3 confirmed-dead filter. The `match is None: continue` branch at `agents/tactical/impostor_policy.py:265-266` makes the failure mode a silent loss of pruning, not a crash.
- **Why it matters:** Two coupled places that must change together. If `engine/rules.py:69` ever changes (e.g., to `f"body-{state.tick}-{target.id}"` for sortability), the agent silently loses dead-target pruning and the impostor stale-target loop could partially regress (only the 30-tick staleness threshold would still bound it).
- **Recommended action:** Already addressed by Phase 3 task wiring. No code change needed in Phase 2. Worth a note in the Phase 3.x task that introduces `BodyView.victim_id`: include a regression test that asserts the engine and agent agree on the victim id, and remove the regex once the boundary field lands.

### R-5 [Concern] Phase 2 long-horizon byte identity is not pinned (carryover R-9)

- **Status:** Wired into Task 3.12. (Source severity: Claude Concern only — Unique-but-verified. Codex covered the same gap in §8 question 1 but did not raise it as a discrete finding.)
- **Evidence:** `tests/orchestrator/test_game.py:139-155` pins same-seed default-agent byte identity at 20 ticks. `eval/determinism_test.py` covers scripted fixtures. No test covers a long-horizon (≥ 200 tick) default-agent byte-identity run. The R-9 acceptance gate at `tasks/phase-3.md:444` requires ≥ 200 ticks (or one full meeting cycle) at Phase 3.12.
- **Why it matters:** Phase 3 LLM nondeterminism debugging will need a longer baseline so a hash divergence can be bisected. Wired R-9 gate requires this in Phase 3.12; nothing more is owed in Phase 2.
- **Recommended action:** None in Phase 2. Phase 3.12 reviewer: enforce the ≥ 200-tick byte-identical assertion at task close.

### R-6 [Concern] Phase 3 R-10 leak-scanner reuse hedge

- **Status:** Wired into Tasks 3.3 and 3.9. (Source severity: Claude Concern only — Unique-but-verified.)
- **Evidence:** `tasks/phase-3.md:124` (rendered memory) and `:335` (strategic prompts) both name the helpers `_assert_no_recursive_hidden_fields` and `_assert_no_role_bearing_values` *"or their canonical Phase 3 successors"*. The "or successors" hedge is the only soft spot — if Phase 3.3 or 3.9 chooses to re-implement instead of importing from `eval/leak_test.py`, the scanner discipline may drift.
- **Why it matters:** Minor risk of duplicated/divergent scanners across the leak surface. Severity stays Concern because the addendum names the canonical helpers and a Phase 3 reviewer can enforce re-use.
- **Recommended action:** None in Phase 2. Phase 3 reviewers: when reviewing 3.3 and 3.9, verify the prompt/render leak tests import from `eval/leak_test.py` rather than re-implementing.

### R-7 [Concern] `tests/observation/test_service.py:343, 358` retains the `"victim-body"` synthetic body-id string

- **Status:** Acceptable per PR #33 `## Decisions`; flagged for the next hygiene pass. (Source severity: Claude Concern only — Unique-but-verified.)
- **Evidence:** The two occurrences are the `BodyState.id` value used in the body-discovery filter test. The string does not match the post-2.11 grep `['"](player|impostor|victim|observer|crew-[0-9]+)['"]` because `victim` is followed by `-` rather than a closing quote (`git grep ... tests/observation/test_service.py` returns empty, exit 1). Engine-generated body ids in production read `body-{victim_id}-{tick}` (e.g. `body-p-1-0` per `engine/rules.py:69`); the test's `"victim-body"` is a synthetic shorter form. Semantically a body id, not a player id; does not leak role.
- **Why it matters:** Test-hygiene-only. The string does not appear in any observation packet under default seeder ids; it is internal test scaffolding.
- **Recommended action:** Optional cleanup later — rename to `"body-p-1-0"` or `"body-victim-0"` to match the engine's actual format. Not a Phase 3 blocker.

## 11. Document Conflicts

1. **DESIGN.md §3.5 tuning-lever paragraph vs `orchestrator/seeder.py`** — R-1 above. `tasks_per_crewmate` is described as a `seed_initial_state` parameter and as the "current canonical default = 1," but no such parameter exists; one-task-per-crewmate is hardcoded by `_build_tasks`.
2. **No regressions** of the May-15 reconciled audit's resolved conflicts. The "games" vs "decisive games" wording is now identical at `tasks/phase-2.md:932-938` and `:1589-1593`; the Task 2.8.5 file-scope-drift contract gap is closed by the historical note at `:865-873`; the Task 2.10.5 deviation is recorded at `:1311-1320`.
3. **Phase 3 merge criteria carryover.** `tasks/phase-3.md:464-469` lists 50-game eval, impostor win rate `[25%, 65%]`, cost, transcript readability, and replay/eval-record completeness. Path D fallback (which would have added the Phase 2 100-game criterion to Phase 3) was not taken because Path A succeeded. No contradiction — Phase 3 inherits its own criteria, and Phase 2's criterion is now met on `main`.

## 12. Readiness for Phase 3

**Ready with fixes.** The architecture is sound and the Phase 2 substrate is healthy enough to carry Phase 3 strategic reasoning:

- **Determinism boundary for LLM debugging.** Same-seed default-agent byte identity reproduces at 200 ticks at HEAD. The current replay format records only `game_id`, `tick`, `actions`, and `state_hash`, which is correct for Phase 2 but insufficient for Phase 3 LLM bisecting. The R-9 acceptance gate at `tasks/phase-3.md:444` requires `ReplayEntry`'s successor to add meeting transcripts, prompt versions, LLM outputs, and cost metadata, plus a ≥ 200-tick byte-identical test. With R-5's `_apply_kill` rewrite landed, the Phase 2 tick boundary is deterministic enough that LLM nondeterminism introduced in Phase 3 will localize cleanly to the LLM call — provided the R-9 successor lands as specified.

- **`agents/memory/` shape for Phase 3.3.** `agents/memory/store.py` is absent by design. Task 3.3's R-6 acceptance gate at `tasks/phase-3.md:117-126` names the three components (`episodic.py`, `working.py`, `beliefs.py`) and requires `render_for_prompt` to read from all three. Concrete enough that the Phase 3.3 agent will not need to invent the boundary.

- **Orchestrator meeting interpose point.** `orchestrator/game.py:162-167` is a single clean branch that returns `MEETING_PHASE_REACHED` when `state.phase == "MEETING"`. Phase 3.12 can replace this branch with a `MeetingManager` dispatch + `apply_meeting_result(state, result)` call without surgery elsewhere in `HeadlessGame.run`. The DoD at `tasks/phase-3.md:439-440` already names the new engine function for the post-meeting handoff.

- **Leak-scanner extension to rendered memory and strategic prompts.** Packet scanning is strong (100-log/3,275-packet clean scan at HEAD). The R-10 addenda at `tasks/phase-3.md:124, 335` name the existing helpers and require planted-negative regression tests mirroring `test_role_bearing_value_scanner_trips_on_planted_visible_player_id`. Tight enough that Phase 3.3 and 3.9 will inherit the discipline — subject to R-6 above (Phase 3 reviewers must enforce re-use rather than re-implementation under the "or successors" hedge).

- **Tuning-lever doc-vs-code drift.** R-1 (Medium). DESIGN.md §3.5 still names `tasks_per_crewmate` as a `seed_initial_state` parameter. One-line DESIGN.md edit; does not block Phase 3 start, but should land before Phase 3 agents rely on the balancing docs.

- **New Critical or High findings introduced by this audit window.** None. The 1 Medium (R-1) is a doc drift; the 2 Lows (R-2 same-tick win pin, R-3 body-id missing-payload pin) are test-hygiene. The 4 Concerns are forward-looking and either already wired into Phase 3 tasks (R-4 retirement, R-5 long-horizon determinism, R-6 scanner reuse) or test-hygiene-only (R-7).

The recommended Phase 3 start order: address R-1 as a single one-line DESIGN.md edit (no task needed); land R-2 and R-3 opportunistically; then Tasks 3.1 → 3.2 → 3.3 (closes R-6 and R-10/render carryovers) → 3.4 onward, with R-9 / R-10/strategic-prompts arriving at 3.9 and 3.12 respectively.

## 13. Reconciliation

### 13.1 Comparison Table

| ID | Title | Claude says | Codex says | Verified | Final severity | Disposition |
|---|---|---|---|---|---|---|
| R-1 | DESIGN.md §3.5 names `tasks_per_crewmate` as a nonexistent seeder parameter | Medium (F-1): doc-vs-code drift | Medium (M-1): doc-vs-code drift | yes: DESIGN.md:291 says parameter exists; `grep tasks_per_crewmate orchestrator/seeder.py` returns empty; `_build_tasks` hardcodes 1/crewmate | Medium | Confirmed |
| R-2 | Same-tick crew-win consequence from `dropped` rule is documented but unpinned | Low (F-2): no same-tick pin | Low (L-1): no same-tick pin | yes: R-5 test exercises follow-up tick only; same-tick grep returns no pin | Low | Confirmed |
| R-3 | `_confirmed_dead_from_bodies` missing-payload `ValueError` branch uncovered | — | Low (L-2): no missing/non-string body_id test | yes: only matching + one malformed string covered; `_saw_body_event` helper signature forbids non-string | Low | Unique-but-verified |
| R-4 | `_BODY_ID_VICTIM_PATTERN` is an agent→engine string coupling on body-id format | Concern (C-1): coupling, retire in Phase 3 | Implied by L-2 recommended action but not raised as a discrete finding | yes: regex at impostor_policy.py:94 vs engine emit at engine/rules.py:69; no shared constant | Concern | Unique-but-verified |
| R-5 | Phase 2 long-horizon byte identity not pinned | Concern (C-2): wired into Task 3.12 | Same gap mentioned in §8 Q1, not as discrete finding | yes: 20-tick pin only; ≥ 200-tick gate at tasks/phase-3.md:444 | Concern | Unique-but-verified |
| R-6 | Phase 3 R-10 scanner-reuse "or successors" hedge | Concern (C-3): reviewer must enforce reuse | — | yes: tasks/phase-3.md:124, 335 contain the hedge | Concern | Unique-but-verified |
| R-7 | `"victim-body"` string retained in observation tests | Concern (C-4): test hygiene only | Acknowledged as acceptable per PR #33 Decisions, not raised as finding | yes: lines 343, 358; post-2.11 grep still empty because format doesn't match | Concern | Unique-but-verified |

Disagreement hotspots (surfaced by the table): R-3 / R-4 / R-5 / R-6 / R-7 — every Concern and the Codex-only Low. R-1 and R-2 are both Confirmed (both auditors cite, both agree on severity and substance).

### 13.2 Disagreements and Resolutions

**R-3.** Claude did not raise the body-id missing-payload coverage gap as a discrete finding (it folded the surface-level concern into the C-1 architectural framing). Codex's Low grading is accepted because the `raise ValueError` branch at `agents/tactical/impostor_policy.py:260-263` is genuinely uncovered: the test helper `_saw_body_event` at `tests/agents/test_impostor_policy.py:101-106` types `body_id: str` and so cannot exercise the missing-payload branch; no other call site in the test suite constructs a `saw_body` event with a missing or non-string `body_id`. The fix is bounded (~10 lines).

**R-4.** Codex did not raise the body-id format coupling as a discrete finding (it folded the architectural concern into the L-2 recommended action, which suggests adding a missing-payload test "and one explicit engine-format-change sentinel"). Claude's Concern grading is accepted because the regex at `agents/tactical/impostor_policy.py:94` (`^body-(.+)-\d+$`) and the engine emit at `engine/rules.py:69` (`f"body-{target.id}-{state.tick}"`) are coupled by format only, with no shared constant. The failure mode is silent (`match is None: continue`) rather than a crash, which makes a missing format-sentinel test the architectural risk it is. R-3 and R-4 are kept as distinct rows because the recommended actions are different (R-3 = add a missing-payload test in Phase 2; R-4 = retire the regex in Phase 3 via `BodyView.victim_id`).

**R-5.** Codex covered the same long-horizon byte-identity gap in §8 question 1 but did not raise it as a discrete finding because it is already wired into Phase 3.12 by name. Claude's Concern grading is accepted because the gap exists as a tracked carryover (R-9 from May-15) — keeping it on the radar through Phase 3.12 has audit-trail value. No action owed in Phase 2.

**R-6.** Codex did not raise the "or canonical Phase 3 successors" hedge in `tasks/phase-3.md:124, 335` as a discrete finding. Claude's Concern grading is accepted because the hedge is the only soft spot in an otherwise well-specified Phase 3 R-10 acceptance gate; flagging it preserves the audit trail for Phase 3.3 and 3.9 reviewers. No action owed in Phase 2.

**R-7.** Codex acknowledged the `"victim-body"` retention but accepted it as documented in PR #33 Decisions and did not raise it as a finding. Claude's Concern grading is accepted as test-hygiene-only — the string does not match the post-2.11 role-bearing grep and is internal test scaffolding. Flagging it ensures the next hygiene pass picks it up; no action owed in Phase 2.

**Why no Critical/High findings were raised.** Both audits independently verified that R-1..R-4 from the May-15 reconciled audit are closed and that R-6, R-9, R-10 are correctly wired into Phase 3 task DoDs. The six-seed sweep, 100-game tournament, leak scan, byte-identity check, and full `check.sh` gate all pass at HEAD. No active behavioral or architectural blocker survives the verification.

### 13.3 Verdict Reconciliation

The two source verdicts differed: Claude said **Ready for Phase 3**, Codex said **Ready with fixes**. The reconciled verdict adopts **Ready with fixes** per the prompt's tie-breaker rule (more conservative reading on disagreement), with the substantive justification that R-1 (DESIGN.md `tasks_per_crewmate` drift) is a concrete enough doc-vs-code conflict that a Phase 3 implementing agent reading §3.5 for balance levers would follow it into a parameter that does not exist — exactly the failure mode AGENTS.md warns against. The fix is bounded (one DESIGN.md edit) and does not block Phase 3 start; the distinction between the two verdicts is whether to call the one Medium a fix-before-Phase-3 hygiene item or an opportunistic follow-up. The conservative reading wins because the cost of landing the fix is small and the cost of misleading a Phase 3 agent is non-trivial.
