# Agent Prompt — 5.9 Performance pass

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.9 — Performance pass, anchored to DESIGN.md §9. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-performance-pass`
**Depends on:** 5.7 merged, 5.8 merged
**Section refs:** DESIGN.md §9
**Complexity:** Medium

Hit the DESIGN.md §9 Phase 5 target: ≥ 1 headless game per minute on a laptop.
Measure the current rate, profile to find the real bottlenecks, apply targeted
fixes to the hot paths, and prove no behavior change. This is the final Phase 5
task and pure polish — the dashboard (5.7) and regression suite (5.8) already
ship at the current rate.

**Benchmark on the FAKE provider.** The rate must be measured deterministically
and network-free, so the benchmark runs headless games with
`AILIBI_LLM_PROVIDER=fake` (instant LLM stubs). That means the measured cost is
ENGINE + serialization throughput per tick — NOT LLM latency. The confirmed hot
paths (cited, not guessed):

- **Per-tick full-state hash** — `orchestrator.replay._state_hash`
  (`orchestrator/replay.py:546`) sha256s the entire serialized `WorldState`
  every tick.
- **Per-tick replay JSONL write** — `ReplayLog.record_tick`
  (`orchestrator/replay.py:244`) serializes via `_stable_json`
  (`json.dumps(sort_keys=True…)`, `orchestrator/replay.py:585`) and writes one
  line per tick.
- **Per-agent-per-tick observation packet construction** —
  `ObservationService.build_packet` (`observation/service.py:36`).

LLM-call concurrency (`orchestrator/`) is a REAL-run lever only — it does not
show up in a fake-provider benchmark (the fake is instant) — so it is secondary
here and any change to it must not alter determinism or the recorded replay.

**Files in scope:**
- engine/ (hot paths only; no rule/behavior change)
- orchestrator/ (per-tick serialization / hash / write-cadence hot paths; concurrency tuning is secondary and determinism-preserving)
- observation/ (packet-construction hot path, if it appears in the profile)
- eval/benchmark.py (a small reusable throughput harness, if one is wanted; else inline in the test)
- tests/eval/test_performance.py (records the benchmark; skipped by default — see DoD)
- scripts/run_tournament.py (only if perf surfaces a tuning knob worth a CLI flag)

**Files NOT in scope:**
- agents/ behavior (FSM or strategic prompt changes)
- llm/ provider behavior
- meetings/ behavior (cap raises etc. are Phase 3 territory)
- api/, frontend/ (the spectator UI is read-only; perf is engine + orchestrator)
- eval/ metric modules, report_schema.py, meeting_quality.py (perf must not change metric values)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] BEFORE rate recorded (games/min on the target laptop, fake provider) in the PR's `## Decisions`, with the exact command and hardware noted.
- [ ] Bottlenecks identified via profiling (`cProfile` or `py-spy`); the profile output (top cumulative-time frames) captured in `## Decisions`. Only paths that actually appear in the profile are optimized — no speculative changes.
- [ ] Targeted fixes applied with NO behavior change. The proof is byte-identity: for a fixed seed, the AFTER `replay-seed-{seed}.jsonl` is byte-identical to BEFORE, and `eval/determinism_test.py` (the three scripted games) still passes byte-identically. Any change to `_state_hash` / `_stable_json` serialization is forbidden unless provably output-identical, since the state hash IS the determinism contract.
- [ ] AFTER rate recorded; meets or exceeds ≥ 1 game/min on the target laptop (documented alongside BEFORE).
- [ ] A benchmark harness is committed that times N headless fake-provider games and reports games/min (e.g. via `time.perf_counter` over `HeadlessGame`/`run_balance_eval`; no `pytest-benchmark` dependency — it is not in `pyproject.toml`). It lives in `tests/eval/test_performance.py` and is **skipped by default** (behind an env-gate or marker) so it never flakes CI on hardware variance; running it is opt-in. Decision recorded: record-only vs a generous non-flaky floor — bias toward record-only (or a floor far below the target, e.g. a smoke assertion that the rate is finite/positive), with the real ≥ 1 game/min target verified manually and documented, never asserted as a tight CI threshold.
- [ ] No regression in any existing test, including `eval/determinism_test.py` and `eval/leak_test.py` (byte-identity + leak firewall both still hold).
- [ ] `uv run mypy .` passes; `uv run ruff check .` and `uv run ruff format --check .` pass; `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes; `bash scripts/check.sh` passes locally.

## Implementation hint

First action is to record a baseline — do NOT optimize before measuring. Time a
small batch of fake-provider games (e.g. `AILIBI_LLM_PROVIDER=fake` over a seed
range that reaches meetings, so the meeting path is exercised) with
`time.perf_counter`, and profile the same batch with `cProfile`
(`python -m cProfile -s cumtime`). Then target only the frames the profile
surfaces — the three cited hot paths are the likely candidates, but let the
profile decide.

When optimizing the per-tick hash/write: the determinism contract is that the
recorded replay is byte-identical from a seed. So you may make `_state_hash` /
`_stable_json` faster ONLY if the bytes are unchanged (e.g. caching, avoiding
redundant re-serialization), never by changing the serialization format. Re-run
a tournament for a fixed seed before and after and `diff` the replay files —
they must be identical. `eval/determinism_test.py` is the automated guard.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.prompt_regression"`
- `uv run python -c "import eval.balance_eval"`
- `uv run python -c "import eval.meeting_quality"`
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
Open a PR from branch `phase-5-performance-pass` with a title like `task 5.9: performance pass`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §9), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
