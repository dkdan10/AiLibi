# AiLibi Pre-Phase-3 Checkpoint Audit — Reconciled

- **Date:** 2026-05-15 02:25 local
- **Audited HEAD:** `0610b72 Merge pull request #29 from dkdan10/claude/headless-tournament-harness-HEXY6` on `main`
- **Regression baseline:** `014cca5 Merge pull request #24 from dkdan10/claude/phase-2-impostor-fsm-UVpdd`
- **Inputs reconciled:** `audits/audit-2026-05-15-0115-claude.md`, `audits/audit-2026-05-15-0124-codex.md`
- **Prior baseline reference:** `audits/audit-2026-05-10-0721.md`
- **Scope:** read-only adjudication through Task 2.9; no fixes attempted
- **Forbidden input note:** `audits/prompts/pre-phase-3-audit-prompt.md` was not read

---

## 1. Executive Summary

**Verdict: Not ready for Phase 3.** Static gates are green at current `HEAD`: `bash scripts/check.sh` passed with 279 tests, import-linter kept the agent/engine firewall, task docs validated, prompts were in sync, mypy strict passed, and ruff/format checks were clean. The blocking failures are behavioral, not static: the required six-seed sweep produced zero decisive outcomes, and the 100-game tournament produced `crew_wins=0`, `impostor_wins=2`, `tick_budget_reached=75`, and `meeting_phase_reached=23`. The reconciliation table contains **2 Critical, 2 High, 2 Medium, 2 Low, and 6 Concern** active findings, plus one dropped duplicate row.

The most important root cause is the tactical endgame: seed 0 reproduces an impostor loop that alternates `ENGINEERING ↔ REACTOR` after killing `p-4`, while `_scored_targets` keeps stale sightings without any dead-player or staleness filter. A second root cause remains a rule/contract ambiguity: in the checked seeds, the game stops at `2/3` tasks with the incomplete task owned by a dead crewmate, so crew wins become unreachable after an early kill unless the task rule or the merge criterion is clarified.

The old role-bearing id grep finding is real but not Critical in this reconciled report. The literal grep hits are deliberate planted negative-test fixtures inside leak-scanner self-tests, not live packet leaks; however, the Task 2.8.5 `tests/` grep DoD still cannot pass, so the finding remains High.

The Phase 3.3 memory-store gap is demoted to Concern. `agents/memory/store.py` is absent, but Task 3.3 explicitly introduces it and its DoD; this is an unresolved contract to implement early in Phase 3, not evidence that Phase 3 cannot start because that file already should exist.

## 2. Verdict

**Not ready.** Both source audits reached this verdict. The decisive-outcome and tournament balance gates in `tasks/phase-2.md:784` and `tasks/phase-2.md:957-960` fail at current `HEAD`, so Phase 3 should wait for a focused pre-Phase-3 repair task.

## 3. Commands Run and Evidence Sources

All commands ran from `/Users/danielkeinan/projects/AiLibi`.

| Command | Result / evidence |
|---|---|
| `pwd` | `/Users/danielkeinan/projects/AiLibi` |
| `git status --short --branch` | `## main...origin/main`, source audit files and `audits/prompts/` were untracked before this report |
| `git rev-parse --short HEAD`; `git log -1 --oneline` | `0610b72`; merge commit for Task 2.9 |
| `date '+%Y-%m-%d-%H%M'` | `2026-05-15-0220`, then `2026-05-15-0225` before writing |
| `wc -l audits/audit-2026-05-15-0115-claude.md`; `wc -l audits/audit-2026-05-15-0124-codex.md`; `wc -l audits/audit-2026-05-10-0721.md` | Source lengths: 731, 282, and 730 lines |
| `sed -n ...` reads of `DESIGN.md`, `AGENT_IMPLEMENTATION.md`, both source audits, and the prior audit | Read allowed inputs and governing docs; did not read the forbidden prompt |
| `bash scripts/check.sh` | Passed: import-linter kept 1 contract, task docs/prompts green, mypy clean, `279 passed in 3.00s` |
| `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" tests/` | One hit: `tests/eval/test_balance_eval.py:258` |
| `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" eval/ tests/` | Hits at `eval/leak_test.py:181`, `eval/leak_test.py:228`, `tests/eval/test_balance_eval.py:258` |
| `uv run python scripts/run_game.py --seed {0,1,2,7,42,100} ... --max-ticks 1000` | Seeds `0,1,2,7,42` -> `TICK_BUDGET_REACHED`; seed `100` -> `MEETING_PHASE_REACHED`; zero decisive outcomes |
| `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/reconciled-tournament-0220 --max-ticks 1000` | `crew_wins=0`, `impostor_wins=2`, `tick_budget_reached=75`, `meeting_phase_reached=23`, decisive split `0.00%/100.00% of 2` |
| Tournament audit-log scanner over `/tmp/reconciled-tournament-0220/*.audit.jsonl` | `audit_logs=100 packets=226229 scanner=PASS` |
| Direct `HeadlessGame` final-state probe for seeds `0,1,2,7,42,100` | Every checked seed ended at `tasks=2/3`; the incomplete task owner was dead |
| Replay action probe over `/tmp/reconciled-r-0.jsonl` | Seed 0 kill at tick 4 by `p-3` targeting `p-4`; `p-3` alternates `ENGINEERING` and `REACTOR` for ticks 970-999 |
| `git show --stat --oneline --no-renames e3b2a60`; `git show --stat --oneline --no-renames ce44eaa` | Verified Task 2.8.5 scope drift and Task 2.9 scope discipline |
| `git diff --name-only 014cca5..HEAD -- ...` baseline groups | No source diffs for engine core, observation, replay/boundary/action ordering, or most agent modules; expected diffs in crewmate policy, eval/tests/fixtures |
| `rg`, `nl -ba`, `sed -n` source reads for cited files | Read task docs, policy code, replay code, memory modules, tests, and DESIGN sections cited below |

Key files read for evidence: `tasks/phase-2.md`, `tasks/phase-3.md`, `agent_prompts/task-3-3-memory-rendering.md`, `orchestrator/game.py`, `orchestrator/replay.py`, `orchestrator/seeder.py`, `engine/win_conditions.py`, `agents/tactical/impostor_policy.py`, `agents/tactical/crewmate_policy.py`, `agents/memory/{episodic,working,beliefs}.py`, `eval/leak_test.py`, `eval/balance_eval.py`, `scripts/run_tournament.py`, `tests/eval/test_balance_eval.py`, `tests/engine/test_tick_properties.py`, `tests/observation/test_service.py`, and `tests/orchestrator/test_game.py`.

## 4. Regression Baseline

Procedure: for prior-Pass items from `audit-2026-05-10-0721.md`, I checked `git diff --name-only 014cca5..HEAD -- <paths>`. No diff means Still Pass; changed rows were re-verified through the full check gate and targeted reads.

| Prior item | Module diff vs `014cca5` | Reconciled status |
|---|---|---|
| Phase 0 repo skeleton, CI, import lint, check scripts | none | **Still Pass (no diff)** |
| 1.1 static map data | none in `engine/world.py` or `engine/maps/` | **Still Pass (no diff)** |
| 1.2 state model | no source diff; tests renamed ids | **Still Pass (re-verified)** |
| 1.3 action types | no source diff; action tests renamed ids | **Still Pass (re-verified)** |
| 1.3.5 engine contract hardening | no source diff | **Still Pass (no diff)** |
| 1.4 rules and win conditions | no source diff | **Still Pass at unit level**; live balance failure is new integration evidence |
| 1.5 `advance_tick` | no source diff; tick tests renamed ids | **Still Pass (re-verified)** |
| 1.6 visibility | no source diff; body-discovery tests added | **Still Pass (re-verified)** |
| 1.7 ObservationService | no source diff | **Still Pass for packets**; scanner passed scripted, seed, and tournament logs |
| 1.8 Replay log | no diff in `orchestrator/replay.py` | **Still Pass for Phase 2**, with Phase 3 replay concerns in R-9 |
| 1.B1 scripted fixtures | three fixtures renamed to `p-N` ids | **Still Pass (re-verified)** via leak/determinism in `check.sh` |
| 1.B2 leak test | `eval/leak_test.py` hardened with value scanner | **Still Pass (hardened)**; grep conflict tracked in R-4 |
| 2.1 boundary contracts | no source diff | **Still Pass (re-verified)** |
| 2.2 agent base/runtime | no code diff in `agents/base.py`/`agents/runtime.py` | **Still Pass (no diff plus tests)** |
| 2.3 memory scaffolding | no diff in existing memory modules | **Still Pass**, with Task 3.3 composite renderer tracked in R-6 |
| 2.4 perception ingestion | no source diff; enum-coupling test added | **Still Pass (re-verified)** |
| 2.5 pathing | no diff | **Still Pass (no diff plus tests)** |
| 2.6 crewmate FSM | source changed in 2.7.5/2.8.5 | **Still Pass at unit level**; live decisive-outcome gates fail |
| 2.7 impostor FSM | no source diff | **Still Pass at unit level**, but integration stale-target bug is R-3 |
| I-1 through I-12 | orchestrator/eval layer added | **Reconciled in §7** |

## 5. Prior Audit Follow-Through

| Prior finding | Status | Evidence |
|---|---|---|
| M-1: Task 2.4 scope omitted `agents/runtime.py` | **Resolved** | `tasks/phase-2.md:225-228` now lists `agents/runtime.py`; validators pass |
| L-1: no agent-driven replay-determinism test | **Resolved for Phase 2** | `tests/orchestrator/test_game.py:139-155` compares two default-agent `HeadlessGame` replays byte-for-byte |
| L-2: crewmate `find_path` errors not guarded | **Resolved** | `agents/tactical/crewmate_policy.py:251-254` catches `ValueError` and waits |
| L-3: own-room-only `KILL_WITNESSED` undocumented | **Resolved** | `tasks/phase-2.md:371-376` records the deliberate narrower trigger |
| L-4: audible event allow-list unpinned | **Resolved** | `tests/agents/test_perception.py:389-397` checks all `AudibleEvent.kind` literals |
| L-5: body-after-discovery filter test absent | **Resolved** | Unit pin at `tests/observation/test_service.py:351-385`; orchestrator pin at `tests/orchestrator/test_game.py:457-516` |
| Property-test action vocabulary narrow | **Still open** | `tests/engine/test_tick_properties.py:6-10` says the property vocabulary is intentionally `move`/`wait`; tracked as R-12 |
| Audit-log append-mode regression absent | **Still open** | `ObservationAuditLog.record_packet` appends at `observation/audit.py:20-23`, but no multi-instance append test exists; tracked as R-13 |
| Leak/determinism bypassed orchestrator | **Resolved for leak and replay** | `HeadlessGame` determinism test and tournament audit scans now exercise real agent paths |

## 6. Task-by-Task DoD Audit

### Task 2.7.5 — Post-2.7 Audit Repair

| DoD area | Verdict | Evidence |
|---|---|---|
| Task 2.4 scope corrected | Pass | `tasks/phase-2.md:225-228` |
| Task 2.6 own-room kill-witness choice documented | Pass | `tasks/phase-2.md:371-376` |
| Crewmate pathing guard added | Pass | `agents/tactical/crewmate_policy.py:251-254` |
| Disconnected-goal, audible-kind, and body-discovery regressions added | Pass | Covered by full `check.sh` and cited tests in §5 |
| PR-description/prompt regeneration docs | Pass | Validators and prompt sync passed |
| Scope discipline | Pass | Source audits agree; no contradictory evidence found |

**Task 2.7.5 verdict:** Pass.

### Task 2.8 — Headless Game Orchestrator

| DoD area | Verdict | Evidence |
|---|---|---|
| Seeded game loop exists | Pass | `orchestrator/game.py:120-173`; live seed runs executed |
| Observations -> agents -> intents -> engine actions -> replay | Pass | `orchestrator/game.py:150-160`, `202-210` |
| Meeting/game-over/tick-budget outcomes | Pass | `orchestrator/game.py:142-172`; seed 100 reproduced meeting pause |
| Orchestrator owns engine imports; agents stay engine-free | Pass | `check.sh` import-linter kept contract; orchestrator imports engine at `game.py:26-40` |
| Replay determinism through default agents | Pass | `tests/orchestrator/test_game.py:139-155` |
| Scope discipline | Pass | Source audits agree; no contradictory evidence found |

**Task 2.8 verdict:** Pass.

### Task 2.8.5 — Critical Leak Repair and Tactical Termination

| DoD area | Verdict | Evidence |
|---|---|---|
| Seeder and fixtures use role-neutral `p-N` ids | Pass | `orchestrator/seeder.py`, fixture tests, and grep clean in fixtures |
| Recursive packet value scanner exists | Pass | `eval/leak_test.py:175-199`; scanner passed 100 tournament audit logs |
| Crewmate policy emits task work in unit tests | Pass | `tests/agents/test_crewmate_policy.py` passed under `check.sh` |
| Post-fix old-id grep over `tests/` must be empty | **Fail** | `tests/eval/test_balance_eval.py:258` remains; adjudicated as R-4 |
| Six-seed sweep must reach at least one decisive outcome | **Fail** | Re-run produced zero `CREWMATES`/`IMPOSTORS`; R-2 |
| Scope discipline | **Fail** | `git show e3b2a60 --stat` includes unlisted files; R-7 |

**Task 2.8.5 verdict:** Partial. Leak repair is real; tactical termination and contract hygiene are not complete.

### Task 2.9 — Headless Tournament Harness

| DoD area | Verdict | Evidence |
|---|---|---|
| Multiple orchestrated games run | Pass | 100-game tournament completed without crash |
| Buckets include non-decisive outcomes | Pass | `eval/balance_eval.py:38-71`, `124-130`; `scripts/run_tournament.py:71-90` |
| Leak test across tournament logs | Pass | 100 logs / 226,229 packets scanned clean |
| Both sides win threshold | **Fail** | 100-game run had crew `0/2` decisive; R-1 |
| DoD wording matches merge criteria | **Fail / conflict** | `tasks/phase-2.md:927` says “games”; `:959` says “decisive games”; R-8 |
| Scope discipline | Pass | `git show ce44eaa --stat` touched only three in-scope files |

**Task 2.9 verdict:** Partial. Harness mechanics pass; balance/criterion readiness fails.

## 7. Architectural Invariant Audit

| Invariant | Verdict | Evidence |
|---|---|---|
| I-1/I-2 `advance_tick` pure and deterministic | Pass | No engine tick/source diff; full tests pass |
| I-3 replay determinism | Pass for Phase 2 | Default-agent 20-tick byte-identity test passes; R-9 covers Phase 3 replay sufficiency |
| I-4 engine state remains engine-owned | Pass | Engine source unchanged; orchestrator owns engine imports |
| I-5 `agents/` does not import `engine/` | Pass | `bash scripts/check.sh` import-linter kept the contract |
| I-6 agents receive only packet/public map | Pass | `orchestrator/game.py:202-210` passes `ObservationPacket` and `PublicMapView` |
| I-7 agents emit only `ActionIntent` | Pass | `translate_action_intents_for_tick` receives policy intents at `game.py:155-156` |
| I-8 observation firewall strips hidden information | Pass for packets | 100 tournament audit logs scanned clean; R-10 covers prompt/render surfaces |
| I-9 invalid inputs raise | Pass | Seeder and balance report invariants are tested and green |
| I-10 Pydantic v2 at boundary | Pass | Boundary schemas unchanged and tests pass |
| I-11 engine state immutability | Pass | No engine model source diff; tests pass |
| I-12 orchestrator duplicate-actor rejection | Pass | Boundary/action-ordering tests pass |
| Multi-agent live harness | **Partial** | Determinism/firewall pass; outcome health fails through R-1/R-2 |

## 8. Specific Questions

1. **Is the determinism boundary clean enough for Phase 3 LLM debugging?** Partially. The Phase 2 tick boundary is deterministic and replayed as actions plus `state_hash` (`orchestrator/replay.py:16-24`, `43-49`), but DESIGN §11.4 requires meeting transcripts, prompt versions, LLM outputs, and cost metadata for LLM-layer replay (`DESIGN.md:805-809`). This is R-9.

2. **Does `agents/memory/` expose the shape Phase 3.3 needs?** Not yet as a concrete file, but this is expected staging. `agents/memory/store.py` is absent, while Task 3.3 explicitly introduces it and its DoD (`tasks/phase-3.md:96-129`). Existing episodic, working, and belief modules expose the raw pieces. This is R-6, a Concern rather than a High blocker.

3. **Does the orchestrator expose a clean meeting interpose point?** Yes. `orchestrator/game.py:162-167` is a single meeting pause branch returning `MEETING_PHASE_REACHED`.

4. **Is leak testing strong enough for Phase 3 LLM prompt leaks?** Strong for `ObservationPacket`s, not yet for rendered memory or prompts. Packet scanners are reusable; Phase 3.3/3.9 should run them over `render_for_prompt` output and strategic prompt inputs. This is R-10.

5. **What must happen before Phase 3 begins?** Fix the live outcome failure (R-1/R-2/R-3), decide the dead-task rule or criterion interpretation (R-5), and clean task-doc/test guard conflicts (R-4/R-7/R-8). R-6/R-9/R-10 should be made explicit early Phase 3 requirements rather than left implicit.

## 9. Test Quality and Coverage Gaps

- R-11: no automated CI guard currently enforces the six-seed decisive sweep or 100-game merge criterion.
- R-3 includes a missing stale-target regression: unit tests cover `ImpostorPolicy` branches, but not a dead/stale sighting loop.
- R-12: property tests still cover only `move` and `wait`, by explicit test comment.
- R-13: audit-log append semantics are not pinned across multiple audit-log instances.
- R-9: default-agent replay byte identity is pinned only for a short 20-tick run, not a long-horizon or tournament-level run.
- R-10: packet leak scanning is strong, but rendered memory and strategic prompt strings do not exist yet and therefore are not scanned.
- R-14: observation unit-test helpers still normalize role-bearing ids such as `"crew-2"` and `"impostor"` outside the current value-scanner harness.
- Dropped duplicate R-15: the separate “tournament determinism coverage” and “duplicated leak scanner helper” comments are handled by R-9/R-4/R-10 and are not separate active defects.

## 10. Defects and Risks

### R-1 [Critical] Fix 100-game tournament balance before Phase 3

- **Status:** Fail.
- **Evidence:** `tasks/phase-2.md:957-960` requires a 100-game tournament, both decisive sides over 20% of decisive games, leak scan across all games, and no agent-engine imports. Re-run: `crew_wins=0`, `impostor_wins=2`, `tick_budget_reached=75`, `meeting_phase_reached=23`, decisive split `CREWMATES=0.00% IMPOSTORS=100.00% of 2 decisive`.
- **Why it matters:** The Phase 2 merge criterion is unmet. Phase 3 meeting quality cannot be evaluated on a tactical substrate where 98% of games are non-decisive and crew never wins.
- **Recommended action:** Fix default-game termination/balance, rerun the exact 100-game tournament, and record the passing counts.

### R-2 [Critical] Make the Task 2.8.5 seed sweep produce a decisive outcome

- **Status:** Fail.
- **Evidence:** `tasks/phase-2.md:784` requires at least one seed in `{0,1,2,7,42,100}` to reach `CREWMATES` or `IMPOSTORS`. Re-run at max 1000 ticks: five `TICK_BUDGET_REACHED`, one `MEETING_PHASE_REACHED`, zero decisive.
- **Why it matters:** This is the explicit acceptance gate for the tactical termination repair.
- **Recommended action:** Add a default-agent seed-sweep regression after the tactical fix and keep the output in the repair PR.

### R-3 [High] Stop the impostor stale-target chase loop

- **Status:** Fail.
- **Evidence:** Seed 0 replay: `p-3` kills `p-4` at tick 4, then at ticks 970-999 alternates `ENGINEERING` and `REACTOR`. `_scored_targets` in `agents/tactical/impostor_policy.py:219-265` keeps latest `saw_player` sightings and scores them without a dead-player or staleness filter.
- **Why it matters:** The impostor can keep chasing a corpse or stale sighting forever, preventing parity and driving R-1/R-2.
- **Recommended action:** Add a staleness/dead-target pruning rule and pin it with a unit test plus at least one default-agent integration seed.

### R-4 [High; demoted from Codex Critical] Clean the old-id grep guard without weakening negative tests

- **Status:** Fail by DoD letter; not a live packet leak.
- **Evidence:** `git grep ... tests/` returns `tests/eval/test_balance_eval.py:258`; `git grep ... eval/ tests/` also finds `eval/leak_test.py:181` and `eval/leak_test.py:228`. The surrounding functions at `eval/leak_test.py:221-236` and `tests/eval/test_balance_eval.py:254-263` are planted scanner self-tests that expect an assertion.
- **Why it matters:** The mechanical guard from `tasks/phase-2.md:780` cannot be used as written. Future real old-id regressions would be mixed with intended negative fixtures.
- **Recommended action:** Keep negative tests, but change planted strings or formalize a narrow allow-list so the exact guard has an unambiguous expected result.

### R-5 [Concern] Decide the dead-crewmate task rule or adjust the merge criterion

- **Status:** Concern / design-rule ambiguity.
- **Evidence:** Direct final-state probe: seeds `0,1,2,7,42,100` all end at `tasks=2/3`; the incomplete task owner is dead. `engine/win_conditions.py:19-22` requires all tasks, regardless of owner aliveness, to be complete for crew victory. `orchestrator/seeder.py:155-176` assigns one task per crewmate.
- **Why it matters:** If a killed crewmate’s task remains required and no ghost/reassignment rule exists, crew wins may be structurally unreachable after an early kill.
- **Recommended action:** Choose one rule: dead tasks are dropped, reassigned, ghost-completable, or intentionally still required. Then align tests and merge criteria.

### R-6 [Concern; demoted from Codex High] Treat `agents/memory/store.py` as Task 3.3 work

- **Status:** Expected missing surface.
- **Evidence:** `agents/memory/store.py` is absent; `tasks/phase-3.md:96-129` explicitly lists `agents/memory/store.py` and `render_for_prompt` as Task 3.3 scope and DoD. Existing memory modules note prompt rendering ships in Phase 3 (`agents/memory/episodic.py:8`, `working.py:7-9`).
- **Why it matters:** Phase 3.3 must not invent this informally or omit beliefs/contradictions, but the absence is not a current Phase 2 defect.
- **Recommended action:** Keep Task 3.3 first-class and add leak-scanned golden render tests.

### R-7 [Medium] Repair Task 2.8.5 file-scope drift

- **Status:** Fail.
- **Evidence:** Task scope at `tasks/phase-2.md:727-748` omits files changed by `e3b2a60`, including `eval/determinism_test.py`, `tests/engine/test_actions.py`, `tests/engine/test_events.py`, `tests/engine/test_world_state.py`, `tests/orchestrator/test_seeder.py`, and the Task 2.9 prompt.
- **Why it matters:** AGENTS.md makes file-scope discipline part of done. The rename was mechanical, but the contract did not say so.
- **Recommended action:** Add a historical scope note or amend Task 2.8.5 scope/prompt to record the accepted rename fallout.

### R-8 [Medium] Align Task 2.9 DoD with the Phase 2 merge criterion

- **Status:** Document conflict.
- **Evidence:** `tasks/phase-2.md:927` says “Both sides win > 20% of games”; `tasks/phase-2.md:959` says “Both decisive sides win > 20% of decisive games” and excludes `TICK_BUDGET_REACHED`. Code/reporting follows decisive split (`eval/balance_eval.py:9-15`, `scripts/run_tournament.py:79-87`).
- **Why it matters:** The difference matters exactly when most games are non-decisive.
- **Recommended action:** Make the DoD wording match the merge criterion and add a documented local check.

### R-9 [Concern] Expand replay/debug evidence before LLM nondeterminism arrives

- **Status:** Concern.
- **Evidence:** `ReplayEntry` stores only `game_id`, `tick`, `actions`, and `state_hash` (`orchestrator/replay.py:16-24`). DESIGN §11.4 requires meeting transcripts, prompt versions, LLM outputs, cost metadata, and structured metric inputs (`DESIGN.md:805-809`). Default-agent byte identity is currently pinned at only 20 ticks (`tests/orchestrator/test_game.py:139-155`).
- **Why it matters:** Once Phase 3 adds meetings and LLM calls, a state-hash mismatch alone will not localize the divergence.
- **Recommended action:** Treat Task 3.12 replay expansion as non-negotiable and add at least one longer deterministic baseline before LLM calls enter.

### R-10 [Concern] Extend leak scanning to rendered memory and strategic prompts

- **Status:** Concern.
- **Evidence:** Packet scanners exist in `eval/leak_test.py:175-199` and passed 100 tournament audit logs. No rendered-memory or strategic prompt surface exists yet; `llm/` and `meetings/` are placeholders, and `agents/memory/store.py` is absent.
- **Why it matters:** Phase 3 can leak information after packet construction, during memory rendering or prompt assembly.
- **Recommended action:** Reuse the packet field/value scanners against `render_for_prompt` golden outputs and strategic prompt inputs.

### R-11 [Concern] Add automated gates for the behavioral merge criteria

- **Status:** Coverage gap.
- **Evidence:** `tests/eval/test_balance_eval.py` covers bucket accounting, small leak scans, replay files, and reuse of `HeadlessGame`, but no test runs the six-seed decisive sweep or 100-game balance criterion.
- **Why it matters:** The repository is green while the required live acceptance gates fail.
- **Recommended action:** Add a practical CI-sized guard, such as one known decisive seed plus a separate documented local 100-game check.

### R-12 [Low] Broaden property-test action vocabulary beyond move/wait

- **Status:** Low, still open.
- **Evidence:** `tests/engine/test_tick_properties.py:6-10` explicitly scopes the property strategy to `move` and `wait`.
- **Why it matters:** Kill/vent/report interleavings remain covered by unit tests but not property exploration.
- **Recommended action:** Add a second property strategy for role-valid kill/report/vent batches when the tactical loop stabilizes.

### R-13 [Low] Add an audit-log append-mode regression

- **Status:** Low, still open.
- **Evidence:** `ObservationAuditLog.record_packet` opens with `"a"` at `observation/audit.py:20-23`; no test reopens the same path with a second instance and asserts previous lines remain.
- **Why it matters:** A future accidental `"w"` change could pass current single-instance tests.
- **Recommended action:** Add a small two-instance append test.

### R-14 [Concern] Stop normalizing role-bearing ids in observation helpers

- **Status:** Concern.
- **Evidence:** `tests/observation/test_service.py:49-58` uses `"crew-2"` and `"impostor"` as helper player ids outside the value-scanner harness.
- **Why it matters:** These helper ids are not default seeder ids and do not prove a live leak, but they make role-bearing ids look normal in tests.
- **Recommended action:** Rename helper ids to `p-N` or add a targeted scanner over observation test packet dumps.

## 11. Document Conflicts

1. **Task 2.8.5 grep DoD vs scanner self-tests.** The DoD says the post-fix grep under `tests/` must be empty, but negative tests deliberately plant `"impostor-1"`.
2. **Task 2.8.5 file scope vs implementation.** The task required a broad rename but did not list every file the rename touched.
3. **Task 2.9 DoD vs merge criteria.** One says “games”; the other says “decisive games.”
4. **Phase 2 merge criteria vs dead-owner task rule.** Current task completion rules can make crew victory unreachable after a kill unless a ghost/reassignment/drop rule exists.
5. **DESIGN replay/debug requirements vs Phase 2 replay.** This is expected phase staging, but it must be closed in Phase 3 replay work.

## 12. Readiness for Phase 3

**Not ready.** The architecture is still sound: firewall enforcement passes, packet leak scanning is strong, default-agent replay determinism exists, and the meeting pause point is localized. But the Phase 2 behavioral substrate is not healthy enough to support Phase 3 strategic reasoning: the required seed sweep has zero decisive outcomes, the tournament fails its merge criterion, and the likely root causes are concrete enough to fix before adding LLM nondeterminism.

Recommended pre-Phase-3 repair order: fix R-3, decide R-5, rerun R-2/R-1, then clean the contract conflicts R-4/R-7/R-8. Keep R-6/R-9/R-10 as explicit early Phase 3 acceptance gates.

## 13. Reconciliation

### 13.1 Comparison Table

| ID | Title | Claude says | Codex says | Verified | Final severity | Disposition |
|---|---|---|---|---|---|---|
| R-1 | Fix 100-game tournament balance before Phase 3 | Critical: merge criterion fails, 0 crew wins | Critical: tournament criterion fails | yes: rerun matched `0/2/75/23` | Critical | Confirmed |
| R-2 | Make the six-seed sweep produce a decisive outcome | Critical: zero decisive outcomes | High: 2.8.5 sweep unmet | yes: rerun matched 5 tick budgets + 1 meeting | Critical | Confirmed |
| R-3 | Stop the impostor stale-target chase loop | High: `_scored_targets` chases dead player | — | yes: seed 0 trace and policy code reproduce | High | Unique-but-verified |
| R-4 | Clean the old-id grep guard without weakening negative tests | High: DoD letter fails; possible downgrade | Critical: any old-id hit in tests/eval | yes: grep hits; surrounding tests are planted negatives | High | Demoted: Codex Critical rejected because evidence is not a live packet leak |
| R-5 | Decide the dead-crewmate task rule or adjust the criterion | Concern: task fix insufficient / dead owner blocks crew win | Concern/root cause in probes and gaps | yes: all checked seeds stop at `2/3` with dead owner | Concern | Confirmed |
| R-6 | Treat `agents/memory/store.py` as Task 3.3 work | Says sufficient / no discrete defect | High: memory-store surface absent | yes: file absent and Task 3.3 owns it | Concern | Demoted: absence is expected staged work, not a preexisting blocker |
| R-7 | Repair Task 2.8.5 file-scope drift | Medium: unlisted files touched | Medium: unlisted files touched | yes: `git show e3b2a60 --stat` | Medium | Confirmed |
| R-8 | Align Task 2.9 DoD with merge criterion | — | Medium: “games” vs “decisive games” | yes: `tasks/phase-2.md:927` vs `:959` | Medium | Unique-but-verified |
| R-9 | Expand replay/debug evidence before LLM nondeterminism | Concern: short horizon / missing events | Concern: replay lacks future LLM artifacts | yes: replay schema and 20-tick test read | Concern | Confirmed |
| R-10 | Extend leak scanning to rendered memory and prompts | Concern in Phase 3 readiness | Concern: prompt/render surfaces unscanned | yes: packet scanner exists; render/prompt surfaces absent | Concern | Confirmed |
| R-11 | Add automated gates for behavioral merge criteria | Gap: no decisive-outcome integration guard | Gap: no CI guard for sweep/tournament | yes: tests cover buckets, not required live gates | Concern | Confirmed |
| R-12 | Broaden property-test action vocabulary | Low unresolved from prior audit | — | yes: property test comment scopes to move/wait | Low | Unique-but-verified |
| R-13 | Add audit-log append-mode regression | Low unresolved from prior audit | — | yes: append implementation exists; no reopen test found | Low | Unique-but-verified |
| R-14 | Stop normalizing role-bearing ids in observation helpers | — | Gap: helpers use role-bearing ids | yes: `tests/observation/test_service.py:49-58` | Concern | Unique-but-verified |
| R-15 | Split tournament determinism and leak-helper duplication as separate defects | Concern/gap variants | Concern/gap variants | partial: claims overlap active rows | dropped | Dropped: duplicates R-4, R-9, and R-10 |

### 13.2 Disagreements and Resolutions

**R-3:** Codex did not name the impostor stale-target loop as a discrete finding. Claude’s High grading is accepted because seed 0 reproduces the tick-970-999 oscillation and `agents/tactical/impostor_policy.py:219-265` has no dead-player or staleness filter.

**R-4:** Codex’s Critical grading is rejected. The grep evidence reproduces, but the matching lines are deliberately planted scanner self-tests (`eval/leak_test.py:221-236`, `tests/eval/test_balance_eval.py:254-263`) rather than production packet leaks. Claude’s lower severity is closer to the evidence, but the finding remains High because the literal Task 2.8.5 grep DoD cannot pass.

**R-6:** Codex’s High grading is rejected. `agents/memory/store.py` is absent, but `tasks/phase-3.md:96-129` explicitly introduces that file and `render_for_prompt`; Claude’s “no shape gap” answer is too soft because the contract still needs to be honored, so the reconciled severity is Concern.

**R-8:** Claude did not list the Task 2.9 “games” vs “decisive games” wording conflict. Codex’s Medium finding is accepted because `tasks/phase-2.md:927` and `tasks/phase-2.md:959` contradict each other in a way that affects the current failing tournament.

**R-12:** Codex did not carry forward the property-test vocabulary gap as a discrete finding. Claude’s Low finding is accepted because `tests/engine/test_tick_properties.py:6-10` explicitly limits property actions to `move`/`wait`.

**R-13:** Codex did not list the audit-log append-mode regression as a discrete finding. Claude’s Low finding is accepted because `observation/audit.py:20-23` uses append mode but no test reopens the same file with a second logger.

**R-14:** Claude did not list the observation-helper id issue. Codex’s Concern is accepted because the helper ids are visible at `tests/observation/test_service.py:49-58`; the severity stays Concern because this is test hygiene, not a live seeder leak.

**R-15:** Both audits had overlapping test-gap variants around tournament determinism, scanner duplication, and planted literal handling. They are dropped as separate findings because R-4, R-9, and R-10 already carry the actionable work.

### 13.3 Verdict Reconciliation

Both source audits said **Not ready** for Phase 3. The reconciled verdict adopts that shared conclusion because the independently rerun seed sweep and tournament reproduce the Phase 2 acceptance failures.
