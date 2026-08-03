# Agent Prompt — 19.19 The retirements + the dead-code sweep (consumer-verified)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.19 — The retirements + the dead-code sweep (consumer-verified), anchored to audits/audit-phase-19-triage.md §7 item 19 (retire set) + singleton 31 + claude §4 item 16 [S-Claude/S-Codex; consumer checks mandatory] + locked decision 2; training/realpath.py (4,470 LOC; the one-shot campaign ops surface) + tests/training/test_realpath.py (4,601 LOC; wall-clock asserts :288/:320-322/:3307-3309); training/surrogate/runner.py:383 (`load_surrogate_runner_factory`) — VERIFIED LIVE CONSUMERS: training/composed_runner.py:266 (the sha/staleness verification fence) and training/bakeoff/harness.py:159/:1763/:2072, with AST call-site pins at tests/training/test_bakeoff_harness.py:1742-1772 — so the factory and class STAY and only a surrogate-ONLY runner exposure proven consumer-free may retire; training/env.py:1037-1056 (`first_meeting` — production callers all pass `full_game`: crew/scorer.py:946, bakeoff/harness.py:722, coevo/rollout.py:214); scripts/run_tournament.py:102-105 (the stale crew-dir CLI advertisement); llm/cache.py (192 LOC; sole importer tests/llm/test_client.py:12); scripts/record_meeting_gate_probe.py (zero references); frontend/src/ui/SectionLabel.tsx (dead); the five unreferenced bake-off prompt-set dirs (cydonia_24b, glm_4_32b, qwen3_30b_a3b, qwen3_32b, qwen3_32b_thinking — delete ONLY those grep-proven unreferenced by committed stamps and tests). NOTE: eval/determinism_test.py is NOT retired — the planning session verified pytest collects it (`*_test.py`) and README cites it as the engine-purity proof; the source audit's "exercised by nothing" is REFUTED.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-retirements`
**Depends on:** 19.6, 19.18
**Section refs:** audits/audit-phase-19-triage.md §7 item 19 (retire set) + singleton 31 + claude §4 item 16 [S-Claude/S-Codex; consumer checks mandatory] + locked decision 2; training/realpath.py (4,470 LOC; the one-shot campaign ops surface) + tests/training/test_realpath.py (4,601 LOC; wall-clock asserts :288/:320-322/:3307-3309); training/surrogate/runner.py:383 (`load_surrogate_runner_factory`) — VERIFIED LIVE CONSUMERS: training/composed_runner.py:266 (the sha/staleness verification fence) and training/bakeoff/harness.py:159/:1763/:2072, with AST call-site pins at tests/training/test_bakeoff_harness.py:1742-1772 — so the factory and class STAY and only a surrogate-ONLY runner exposure proven consumer-free may retire; training/env.py:1037-1056 (`first_meeting` — production callers all pass `full_game`: crew/scorer.py:946, bakeoff/harness.py:722, coevo/rollout.py:214); scripts/run_tournament.py:102-105 (the stale crew-dir CLI advertisement); llm/cache.py (192 LOC; sole importer tests/llm/test_client.py:12); scripts/record_meeting_gate_probe.py (zero references); frontend/src/ui/SectionLabel.tsx (dead); the five unreferenced bake-off prompt-set dirs (cydonia_24b, glm_4_32b, qwen3_30b_a3b, qwen3_32b, qwen3_32b_thinking — delete ONLY those grep-proven unreferenced by committed stamps and tests). NOTE: eval/determinism_test.py is NOT retired — the planning session verified pytest collects it (`*_test.py`) and README cites it as the engine-purity proof; the source audit's "exercised by nothing" is REFUTED.
**Complexity:** Integration

Implement the tier map's RETIRE column plus the verified dead-code list, one deletion at
a time, each with a grep-proven consumer check recorded in the PR. Retire:
`training/realpath.py` + its test file (the ranking-row schema doc and committed rankings
survive — the map records where); the surrogate-ONLY meeting-runner exposure — with the
verified boundary respected: `load_surrogate_runner_factory` and
`SurrogateMeetingRunner` STAY (the composed runner's verification fence at
`composed_runner.py:266` and the harness at `:159/:1763/:2072` consume them, AST-pinned)
— the retire candidate is any config/CLI arm that runs the surrogate ALONE as a meeting
runner, and if the consumer grep proves no such consumer-free exposure exists, the
outcome is a recorded no-op for this item, not a forced deletion; the `first_meeting` episode
boundary (env + rollout plumbing; tests-only consumer); the stale crew-dir CLI
advertisement in run_tournament (the honest fail-loud behavior stays; the advertisement
of a stampless directory goes); `llm/cache.py` (+ its import in test_client);
`scripts/record_meeting_gate_probe.py`; `frontend/src/ui/SectionLabel.tsx`; and any of
the five bake-off prompt-set directories that a grep over committed replay stamps,
loader references, and tests proves unreferenced — a set that fails the grep is labeled
bake-off-archive instead, never deleted on hope. Every deletion is recoverable from git
history; the PR lists each with its consumer-check output.

**Files in scope:**
- training/realpath.py; (deleted)
- tests/training/test_realpath.py; (deleted)
- training/surrogate/runner.py; (the surrogate-only exposure, if the grep frees one)
- training/surrogate/; (ripple from the arm removal)
- training/bakeoff/harness.py; (only if a retired exposure ripples — record if touched)
- tests/training/test_bakeoff_harness.py; (the AST pins, only on ripple)
- tests/training/test_goodhart_probe.py; (only on ripple)
- tests/training/test_composed_runner.py; (only on ripple)
- tests/eval/test_balance_eval_meeting_runner.py; (only on ripple)
- training/env.py
- training/rollout.py
- tests/training/test_rollout.py
- tests/training/test_surrogate_runner.py
- tests/training/test_coevo_driver.py; (only if the realpath removal ripples — record if touched)
- scripts/run_tournament.py
- tests/scripts/test_run_tournament.py
- scripts/record_meeting_gate_probe.py; (deleted)
- llm/cache.py; (deleted)
- tests/llm/test_client.py; (the cache import removed)
- frontend/src/ui/SectionLabel.tsx; (deleted)
- agents/strategic/prompts/; (unreferenced bake-off set dirs only; loader.py is NOT edited — a set needing a loader edit is skipped and recorded)

**Files NOT in scope:**
- eval/determinism_test.py (NOT dead — see Section refs; it stays)
- agents/strategic/prompts/loader.py (19.6's file; any set requiring a loader edit is skipped)
- training/composed_runner.py + the conviction/compact-inference surfaces (KEEP column)
- frontend/src/api/ (dead client methods are backlog — they collide with 19.13/19.24)

**Definition of done:**
- [ ] Every deletion carries its consumer-check grep output in the PR; every skipped candidate (failed grep) is named with the blocking consumer.
- [ ] The surrogate boundary is proven: `load_surrogate_runner_factory`/`SurrogateMeetingRunner` and every verified consumer (composed runner fence, harness, the AST pins) are untouched and green; the surrogate-only exposure is either retired with its consumer grep quoted or recorded as no-consumer-free-exposure (a documented no-op), never force-deleted.
- [ ] `first_meeting` is gone from env/rollout with the three production call sites unchanged (`full_game` explicit) and their tests green.
- [ ] The full gate is green after all deletions; the gate-runtime delta is quoted in the PR.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Order the deletions leaf-first (cache → gate probe → SectionLabel → first_meeting →
standalone arm → realpath) so each gate run isolates one removal. For the prompt sets,
the consumer surfaces are: `prompt_set`/set-name strings in committed replay stamps
(grep the JSONL), `loader.py` set references, tests, and the byte-golden's coverage —
run all four greps per set and paste the outputs.

## Integration risk

Deletions across five packages in one branch. The guards: leaf-first commit ordering with
the suite green at each step, the consumer-check discipline (nothing deleted on an
audit's say-so alone — the audits themselves got `eval/determinism_test.py` wrong, which
is why the check is mandatory), and the composed-runner dependency boundary pinned by its
existing tests before the standalone arm is removed.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-19-retirements` with a title like `task 19.19: the retirements + the dead-code sweep (consumer-verified)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 19 (retire set) + singleton 31 + claude §4 item 16 [S-Claude/S-Codex; consumer checks mandatory] + locked decision 2; training/realpath.py (4,470 LOC; the one-shot campaign ops surface) + tests/training/test_realpath.py (4,601 LOC; wall-clock asserts :288/:320-322/:3307-3309); training/surrogate/runner.py:383 (`load_surrogate_runner_factory`) — VERIFIED LIVE CONSUMERS: training/composed_runner.py:266 (the sha/staleness verification fence) and training/bakeoff/harness.py:159/:1763/:2072, with AST call-site pins at tests/training/test_bakeoff_harness.py:1742-1772 — so the factory and class STAY and only a surrogate-ONLY runner exposure proven consumer-free may retire; training/env.py:1037-1056 (`first_meeting` — production callers all pass `full_game`: crew/scorer.py:946, bakeoff/harness.py:722, coevo/rollout.py:214); scripts/run_tournament.py:102-105 (the stale crew-dir CLI advertisement); llm/cache.py (192 LOC; sole importer tests/llm/test_client.py:12); scripts/record_meeting_gate_probe.py (zero references); frontend/src/ui/SectionLabel.tsx (dead); the five unreferenced bake-off prompt-set dirs (cydonia_24b, glm_4_32b, qwen3_30b_a3b, qwen3_32b, qwen3_32b_thinking — delete ONLY those grep-proven unreferenced by committed stamps and tests). NOTE: eval/determinism_test.py is NOT retired — the planning session verified pytest collects it (`*_test.py`) and README cites it as the engine-purity proof; the source audit's "exercised by nothing" is REFUTED.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
